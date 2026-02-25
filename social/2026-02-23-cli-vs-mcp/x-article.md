# I Made MCP 94% Cheaper (And It Only Took One Command)

Every AI agent using MCP is quietly overpaying. Not on the API calls themselves - those are fine. The tax is on the instruction manual.

Before your agent can do anything useful, it needs to know what tools are available. MCP's answer is to dump the entire tool catalog into the conversation as JSON Schema. Every tool, every parameter, every option.

> CLI does the same job but cheaper.

## Same tools, different packaging

I took an MCP server and generated a CLI from it using CLIHub. Same tools, same OAuth, same API underneath. Two things change: what loads at session start, and how the agent calls a tool.

The numbers below assume a typical setup: 6 MCP servers, 14 tools each, 84 tools total.

### 1. Session start

MCP dumps every tool schema into the conversation upfront. CLI uses a lightweight skill listing - just names and locations. The agent discovers details when it needs them.

[IMAGE: comparison_session_start.png]

### 2. Tool call

Once the agent knows what's available, it still needs to call a tool.

[IMAGE: comparison_tool_call.png]

MCP's call is cheaper because definitions are pre-loaded. CLI pays at discovery time - --help returns the full command reference (~600 tokens for 14 tools), then the agent knows what to execute.

[IMAGE: table_mcp_vs_cli.png]

> CLI uses ~94% fewer tokens overall.

## Anthropic's Tool Search

Anthropic launched Tool Search which loads a search index instead of every schema then uses fetch tools on demand. It typically drops token usage by 85%.

Same idea as CLI's lazy loading. But when Tool Search fetches a tool, it still pulls the full JSON Schema.

[IMAGE: table_mcp_vs_ts_vs_cli.png]

Tool Search is more expensive, and it's Anthropic-only. CLI is cheaper and works with any model.

## CLIHub

I struggled finding CLIs for many tools so built CLIHub a directory of CLIs for agent use.

Open sourced the converter - one command to create CLIs from MCPs. https://github.com/thellimist/clihub

---

1. I like using formatting of OpenClaw's available_skills block for CLI. It can be modified to other formats.

2. Tool Search: ~500 session start + ~3K per search (loads 3-5 tools) + ~30 per call. Assumes 1 search for 1-10 calls, 3 searches for 100.
