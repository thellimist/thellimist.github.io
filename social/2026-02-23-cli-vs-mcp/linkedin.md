I Made MCP 94% Cheaper. One command.

Every AI agent using MCP overpays before it does anything useful. The cost isn't the API calls - it's the instruction manual.

MCP dumps every tool schema into the conversation as JSON. 84 tools = 15,500 tokens before a single tool is called. Every session. Every time.

I generated CLIs from the same MCP servers. Same tools, same OAuth, same API underneath. The agent gets a lightweight list of tool names at session start. It discovers details only when needed via --help.

The result is direct. Session start drops from 15,540 tokens (MCP) to 300 (CLI), which is 98% less. After 100 tool calls, it is 18,540 vs 1,504, still 92% less.

Anthropic's Tool Search takes a similar lazy-loading approach but still pulls full JSON Schema per tool. CLI stays cheaper and works with any model.

I struggled finding CLIs for many tools, so I built CLIHub - a directory of CLIs for agent use. Open sourced the converter: one command to create CLIs from MCPs.

What's the most expensive part of your agent stack that turned out to be unnecessary?
