# agentops-mcp

[![tests](https://github.com/Ludoonus/agentops-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/Ludoonus/agentops-mcp/actions/workflows/test.yml)

An **MCP server** that exposes AI-coding-agent operations analytics as tools any MCP
client can call. Ask your assistant "how much did I spend on Claude Code this week?",
"what dangerous commands did my agent attempt?", or "where are my tokens wasted?" —
answered from the transcripts Claude Code already writes locally. Read-only, no telemetry.

## Tools

| Tool | Returns |
|------|---------|
| `cost_summary` | tokens, cache hit rate, est. dollars, top projects & tools |
| `audit_summary` | commands run, file writes, errors, sensitive-path access |
| `safety_report` | dangerous actions the agent *attempted* (force-push, rm -rf, curl\|sh) |
| `efficiency_report` | re-read waste, cache misses, concrete fixes |

Each takes `days` (default 30) and an optional `project` filter.

## Install

```bash
pipx install git+https://github.com/Ludoonus/agentops-mcp
# or: uvx --from git+https://github.com/Ludoonus/agentops-mcp agentops-mcp
```

## Use with Claude Desktop (or any MCP client)

Add to your MCP config:

```json
{
  "mcpServers": {
    "agentops": { "command": "agentops-mcp" }
  }
}
```

Then ask your assistant about your Claude Code cost, audit trail, safety, or efficiency.

## How it works

Reads `~/.claude/projects/*.jsonl` (the transcripts Claude Code writes), parses the
API-reported usage and tool calls, and serves the analysis over MCP (stdio). Nothing
leaves your machine; the server only reads.

## Companion projects

- [Operator](https://github.com/Ludoonus/operator) — the same analytics as a CLI/TUI console.
- [cc-powerpack](https://github.com/Ludoonus/cc-powerpack) — guardrail hooks that *prevent*
  the dangerous actions this server reports.


## Go deeper

These tools are the practical layer; [**The Claude Code Operator's Handbook**](https://ludoonus.github.io/cc-powerpack/handbook/) is the full playbook — 18 chapters on running AI coding agents safely and efficiently (threat model, guardrails, cost, workflows, recovery, scaling). $29, with a free 3-chapter sample.

## License

MIT.
