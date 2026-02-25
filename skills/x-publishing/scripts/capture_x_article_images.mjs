#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";

const require = createRequire(import.meta.url);

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i += 1) {
    const part = argv[i];
    if (!part.startsWith("--")) {
      throw new Error(`Unexpected argument: ${part}`);
    }
    const key = part.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith("--")) {
      args[key] = true;
      continue;
    }
    args[key] = next;
    i += 1;
  }
  return args;
}

function parseIntFlag(name, value, fallback) {
  if (value === undefined) {
    return fallback;
  }
  const parsed = Number.parseInt(String(value), 10);
  if (!Number.isFinite(parsed)) {
    throw new Error(`--${name} must be an integer`);
  }
  return parsed;
}

function usage() {
  console.log(`Usage:
  node skills/x-publishing/scripts/capture_x_article_images.mjs \\
    --url http://localhost:4000/post-slug \\
    --manifest social/YYYY-MM-DD-slug/x-image-manifest.json \\
    --out-dir assets/posts/slug/x-article

Options:
  --article <path>           Optional x-article.md file. If provided, placeholder order is enforced.
  --allow-extra              Allow manifest entries that are not referenced in the article placeholders.
  --viewport-width <int>     Default: 1440
  --viewport-height <int>    Default: 3000
  --device-scale-factor <int> Default: 2
  --wait-ms <int>            Delay after page load. Default: 1200
  --timeout-ms <int>         Timeout per selector. Default: 20000
  --chromium-path <path>     Optional Chromium executable path.
  --playwright-dir <path>    Optional install/cache directory for Playwright module.
`);
}

function extractPlaceholders(articlePath) {
  const content = fs.readFileSync(articlePath, "utf8");
  const placeholders = [];
  const seen = new Set();
  const regex = /\[IMAGE:\s*([^\]]+?)\s*\]/g;
  let match = regex.exec(content);
  while (match) {
    const value = match[1].trim();
    if (!seen.has(value)) {
      placeholders.push(value);
      seen.add(value);
    }
    match = regex.exec(content);
  }
  return placeholders;
}

function loadManifest(manifestPath) {
  const raw = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  const items = Array.isArray(raw) ? raw : raw.items;
  if (!Array.isArray(items) || items.length === 0) {
    throw new Error(`Manifest at ${manifestPath} must be a non-empty array or { \"items\": [...] }`);
  }

  return items.map((item, index) => {
    if (!item || typeof item !== "object") {
      throw new Error(`Manifest item #${index + 1} is not an object`);
    }
    const placeholder = String(item.placeholder || "").trim();
    const selector = String(item.selector || "").trim();
    if (!placeholder) {
      throw new Error(`Manifest item #${index + 1} missing \"placeholder\"`);
    }
    if (!selector) {
      throw new Error(`Manifest item #${index + 1} missing \"selector\"`);
    }
    if (placeholder.includes("..") || path.isAbsolute(placeholder)) {
      throw new Error(`Manifest item #${index + 1} has unsafe placeholder path: ${placeholder}`);
    }
    return {
      placeholder,
      selector,
      note: item.note ? String(item.note) : "",
      waitMs: item.wait_ms !== undefined ? parseIntFlag("wait_ms", item.wait_ms, 0) : 0,
      timeoutMs: item.timeout_ms !== undefined ? parseIntFlag("timeout_ms", item.timeout_ms, 0) : 0,
    };
  });
}

function validateAgainstArticle(items, placeholders, allowExtra) {
  const manifestNames = new Set(items.map((item) => item.placeholder));
  const missing = placeholders.filter((name) => !manifestNames.has(name));
  if (missing.length > 0) {
    throw new Error(`Manifest missing placeholders from article: ${missing.join(", ")}`);
  }

  if (!allowExtra) {
    const articleNames = new Set(placeholders);
    const extras = items.filter((item) => !articleNames.has(item.placeholder)).map((item) => item.placeholder);
    if (extras.length > 0) {
      throw new Error(`Manifest has entries not present in article placeholders. Use --allow-extra or remove: ${extras.join(", ")}`);
    }
  }
}

function orderItems(items, placeholders) {
  if (placeholders.length === 0) {
    return items;
  }
  const byName = new Map(items.map((item) => [item.placeholder, item]));
  return placeholders.map((name) => byName.get(name)).filter(Boolean);
}

function loadPlaywright(playwrightDirArg) {
  try {
    return require("playwright");
  } catch {
    // Continue to local cache bootstrapping path.
  }

  const baseDir =
    playwrightDirArg ||
    path.join(
      process.env.HOME || process.cwd(),
      ".cache",
      "x-publishing-playwright",
    );

  const packagePath = path.join(baseDir, "node_modules", "playwright");
  if (!fs.existsSync(packagePath)) {
    fs.mkdirSync(baseDir, { recursive: true });
    const npmArgs = [
      "install",
      "playwright@1.58.2",
      "--no-save",
      "--silent",
      "--no-audit",
      "--no-fund",
    ];
    execFileSync("npm", npmArgs, {
      cwd: baseDir,
      stdio: "inherit",
      env: {
        ...process.env,
        PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD: "1",
      },
    });
  }

  return require(packagePath);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    usage();
    process.exit(0);
  }

  const url = args.url;
  const manifestPath = args.manifest;
  const outDir = args["out-dir"];
  if (!url || !manifestPath || !outDir) {
    usage();
    throw new Error("Missing required arguments: --url, --manifest, --out-dir");
  }

  const viewportWidth = parseIntFlag("viewport-width", args["viewport-width"], 1440);
  const viewportHeight = parseIntFlag("viewport-height", args["viewport-height"], 3000);
  const deviceScaleFactor = parseIntFlag("device-scale-factor", args["device-scale-factor"], 2);
  const waitMs = parseIntFlag("wait-ms", args["wait-ms"], 1200);
  const timeoutMs = parseIntFlag("timeout-ms", args["timeout-ms"], 20000);
  const allowExtra = Boolean(args["allow-extra"]);

  const playwright = loadPlaywright(args["playwright-dir"] ? String(args["playwright-dir"]) : undefined);

  const items = loadManifest(manifestPath);
  const placeholders = args.article ? extractPlaceholders(args.article) : [];
  if (args.article) {
    validateAgainstArticle(items, placeholders, allowExtra);
  }

  const runItems = orderItems(items, placeholders);
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await playwright.chromium.launch({
    headless: true,
    executablePath: args["chromium-path"] ? String(args["chromium-path"]) : undefined,
  });

  const context = await browser.newContext({
    viewport: { width: viewportWidth, height: viewportHeight },
    deviceScaleFactor,
  });

  const page = await context.newPage();
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: timeoutMs });
  try {
    await page.waitForLoadState("networkidle", { timeout: timeoutMs });
  } catch {
    // Some pages keep background requests open. Continue after base load.
  }
  if (waitMs > 0) {
    await page.waitForTimeout(waitMs);
  }

  const failures = [];
  const captures = [];

  for (const item of runItems) {
    const itemTimeout = item.timeoutMs > 0 ? item.timeoutMs : timeoutMs;
    const outputPath = path.join(outDir, item.placeholder);
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });

    try {
      const locator = page.locator(item.selector).first();
      await locator.waitFor({ state: "visible", timeout: itemTimeout });
      await locator.scrollIntoViewIfNeeded();
      if (item.waitMs > 0) {
        await page.waitForTimeout(item.waitMs);
      }
      await locator.screenshot({
        path: outputPath,
        animations: "disabled",
        caret: "hide",
        scale: "device",
      });
      captures.push({ ...item, outputPath });
      console.log(`[ok] ${item.placeholder} <= ${item.selector}`);
    } catch (error) {
      failures.push(`${item.placeholder} (${item.selector}): ${error.message}`);
      console.error(`[failed] ${item.placeholder} <= ${item.selector}`);
    }
  }

  await browser.close();

  console.log("\nInsertion order:");
  captures.forEach((capture, index) => {
    const noteSuffix = capture.note ? ` (${capture.note})` : "";
    console.log(`${index + 1}. [IMAGE: ${capture.placeholder}] -> ${capture.outputPath}${noteSuffix}`);
  });

  if (failures.length > 0) {
    console.error("\nCapture failures:");
    failures.forEach((failure) => console.error(`- ${failure}`));
    process.exit(1);
  }
}

main().catch((error) => {
  console.error(`Error: ${error.message}`);
  process.exit(1);
});
