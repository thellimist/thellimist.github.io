---
layout: default
title: "Coding Agents Are at Stage 5 Everything Else Is Stuck at Stage 1"
date: 2026-02-19
image: "/assets/posts/five_stages.png"
---

# Coding Agents Are at Stage 5 Everything Else Is Stuck at Stage 1

> Coding agents feel magical. You describe a task, walk away, and come back to a working pull request.
>
> Other AI agents (GTM, Marketing, Ops) hand you a to-do list and wish you luck.


The models aren't the problem. GPT, Claude, Gemini can all reason well enough. The problem is that most agents can't actually *do* anything.

I built a multi-agent orchestration for SEO to test this. Goal-setting, task management, QA, parallel execution, specialized agents. The result? D-level work. The AI wasn't dumb. It just **couldn't do the job**.

I studied why some agent workflows work, and some do not. I found five stages that every agent workflow needs. Each one is a visible jump in what the agent can actually pull off.

## The Five Stages

| Stage | Name | What It Means | Examples |
|-------|------|---------------|----------|
| 1 | **Tool Access** | The agent can read, write, and execute everything it needs | Bash, browser, CMS write access |
| 2 | **Planning** | Breaks work into steps, tackles them sequentially | Task lists, dependency ordering, step-by-step execution |
| 3 | **Verification** | Tests its own output, catches mistakes, iterates | Running tests, confirming action succeeded |
| 4 | **Personalization** | Follows your specific conventions, style, constraints | SOUL.md, SKILL.md, AGENTS.md |
| 5 | **Memory & Orchestration** | Manages context, delegates to other agents, works in parallel | Sub-agents, Planner, Orchestrator, Worker, QA agents. Parallel task execution |

I grade agent output E through A. Each stage roughly moves the agent up one grade.

| Grade | What It Looks Like |
|-------|-------------------|
| **E** | Can barely start the task |
| **D** | Understands the problem but can't execute |
| **C** | Usable with heavy hand-holding |
| **B** | Works with light review |
| **A** | You trust it and walk away |

## Coding Agents Proved the Model

The history of coding agents maps perfectly to these stages.

| System | Year | Stage | Grade | What Changed |
|--------|------|-------|-------|--------------|
| **OpenAI** | 2022 | 0 | E | Glorified search engine. You copy paste everything from GPT to your editor. AI never touches your codebase. |
| **Cursor** | 2023 | 1 | D | Tool access. It could read and write files. Understands your codebase, and updates. No need to copy paste code. The result was still low quality code. Needed constant audits. |
| **Claude Code** | 2025 | 1–4 | B | Bash access allowing it to run scripts, step-by-step planning, running tests to check its own work, reading your project conventions via AGENTS.md. It disrupted the market almost overnight. |
| **Future Systems** | 2026 | 5 | A | Codex/Claude are now working on stage 5. Spawn custom agents with a lead to review and QA to test. Each agent personalized, memory/context refreshed per task. [GSD](https://github.com/gsd-build/get-shit-done/), [VBW](https://github.com/yidakee/vibe-better-with-claude-code-vbw) like orchestrators successfully take the flow to Stage 5. |

## Everything Else Is Stuck at Stage 1

I built a multi-agent SEO system with stages 2 through 5 - planning, verification, QA agents, specialized skills, parallel execution. Then I actually ran it. It did not work.

The agent had no access to Google Analytics, Search Console and ahrefs. Once I fixed that, it analyzed everything and produced a solid action list. Then it couldn't execute any of it - no write access to the CMS. It did not work.

I gave it access. It started updating the website, fixing technical audits, writing and publishing blogs. Real output. It worked?

Then it hit the next wall: Product Hunt launches, G2, PR campaigns, backlink creation. Fifteen more tools needed before the list was done.

Each time I unblocked it, it performed. That's the pattern. To make it useful, needs to add many many tools accesses. 

Here's what this gap looks like across different workflows:

| Workflow | What Coding Agents Have | What Others Need |
|----------|------------------------|----------------------|
| **Coding** | Bash, file read/write | *(Solved)* |
| **SEO** | — | GA4, Search Console, Ahrefs, CMS write access, Lighthouse, G2, Social accounts, Wiki, Youtube, Email.. |
| **Sales** | — | CRM read/write, email send, calendar, enrichment APIs, email verification, analytics.. |
| **Marketing** | — | Ad platforms, analytics, social scheduling, design tools, video tools, social accounts.. |

Same wall, every time. The AI can think. It can plan. It can check its own work. It just can't touch anything.

## The Industry Has It Backwards

Most AI agent startups are building better planning, better orchestration, better multi-agent frameworks. Stages 2 through 5.

> Until a non-coding agent can access its tools as easily as Claude Code runs `bash`, the output stays at D grade regardless of how smart the orchestration is.

MCP, Skills are the main attempts to solve agent access. So are tool-use platforms and API aggregators. They only partially work. We're still early. There is no consistent way to access dozens of tools reliably.

Coding had it easy: bash is the universal tool, one interface to everything. Every other domain needs dozens of specialized integrations, each with its own auth, rate limits, and data quirks.

## What Happens Next

Coding agents will keep polishing stage 5. Better memory, smarter delegation, more parallel work. 2026 we'll see coding orchestration going mainstream.

The big jumps are elsewhere. The first sales agent or accounting agent that fully solves stage 1 will feel like Claude Code did when people first used it. That moment where you stop watching the agent and start trusting it.

<a href="/2026/03/14/from-0-to-1000-skills" class="blog-link-card">
<span class="blog-link-card-title">Read more on how to make "Stage 4: Personalization" work for more than 1,000 skills</span>
<span class="blog-link-card-arrow">↗</span>
</a>

If you need help building vertical AI agents that actually work, reach out: [kan.yilmaz.me@gmail.com](mailto:kan.yilmaz.me@gmail.com)
