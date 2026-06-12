"""agentops-mcp — an MCP server exposing AI-coding-agent operations analytics.

Lets any MCP client (Claude Desktop, etc.) ask about your Claude Code usage: cost,
what your agent did (audit), dangerous actions it attempted (safety), and where tokens
are wasted (efficiency) — all read locally from the transcripts Claude Code writes.
Read-only, nothing leaves your machine.

Run:  agentops-mcp     (stdio MCP server)
"""
from __future__ import annotations

from datetime import timedelta

from mcp.server.fastmcp import FastMCP

from .engine.audit import analyze_audit
from .engine.cost import analyze_cost, blended_dollars, by_day
from .engine.efficiency import analyze_efficiency
from .engine.safety import analyze_safety
from .engine.transcripts import load_sessions, now_utc

mcp = FastMCP("agentops")


def _sessions(days: int, project: str | None):
    return load_sessions(project_filter=project, since=now_utc() - timedelta(days=days))


@mcp.tool()
def cost_summary(days: int = 30, project: str | None = None) -> dict:
    """Token cost across Claude Code projects: output/input tokens, cache hit rate,
    estimated list-price dollars, and the top projects and tools by spend."""
    s = _sessions(days, project)
    if not s:
        return {"error": "no sessions in window"}
    c = analyze_cost(s)
    return {
        "window_days": days,
        "sessions": c.sessions,
        "turns": c.turns,
        "output_tokens": c.output_tokens,
        "input_uncached": c.input_tokens,
        "cache_read": c.cache_read_tokens,
        "cache_hit_rate": round(c.cache_hit_rate, 4),
        "est_list_price_usd": round(blended_dollars(s) or 0, 2),
        "top_projects": [{"project": p, "output_tokens": t} for p, t in c.by_project.most_common(8)],
        "top_tools_by_result_tokens": [
            {"tool": n, "tokens": t, "calls": c.by_tool_calls[n]}
            for n, t in c.by_tool_result.most_common(8)
        ],
    }


@mcp.tool()
def cost_trend(days: int = 30, project: str | None = None) -> dict:
    """Per-day Claude Code cost trend: output tokens and est. dollars by calendar day,
    so you can spot spend spikes over time."""
    s = _sessions(days, project)
    if not s:
        return {"error": "no sessions in window"}
    return {
        "window_days": days,
        "by_day": [
            {"date": d, "output_tokens": tok, "est_usd": round(dol, 2)}
            for d, tok, dol in by_day(s)
        ],
    }


@mcp.tool()
def audit_summary(days: int = 30, project: str | None = None) -> dict:
    """What the agent actually did: command count, file writes, errors,
    sensitive-path accesses, and the most common command verbs."""
    s = _sessions(days, project)
    if not s:
        return {"error": "no sessions in window"}
    a = analyze_audit(s)
    return {
        "window_days": days,
        "commands": len(a.commands),
        "file_writes": len(a.writes),
        "errors": len(a.errors),
        "sensitive_access": [{"kind": e.kind, "detail": e.detail[:160]} for e in a.sensitive_access[:25]],
        "top_command_verbs": dict(a.command_verbs.most_common(12)),
    }


@mcp.tool()
def safety_report(days: int = 30, project: str | None = None) -> dict:
    """Dangerous actions the agent ATTEMPTED (force-push, rm -rf on risky paths,
    curl|sh, chmod 777, etc.), whether or not a guardrail stopped them."""
    s = _sessions(days, project)
    if not s:
        return {"error": "no sessions in window"}
    sr = analyze_safety(s)
    return {
        "window_days": days,
        "risky_attempts": len(sr.hits),
        "critical": sr.critical,
        "by_label": dict(sr.by_label),
        "examples": [
            {"severity": h.severity, "label": h.label, "command": h.command[:160], "project": h.project}
            for h in sr.sorted_hits()[:20]
        ],
    }


@mcp.tool()
def efficiency_report(days: int = 30, project: str | None = None) -> dict:
    """Where tokens are wasted: re-read files, oversized tool output, cache hit rate,
    plus concrete recommendations to cut waste."""
    s = _sessions(days, project)
    if not s:
        return {"error": "no sessions in window"}
    e = analyze_efficiency(s)
    return {
        "window_days": days,
        "reread_waste_tokens": e.reread_waste_tokens,
        "cache_hit_rate": round(e.cache_hit_rate, 4),
        "most_reread_files": [{"file": f, "extra_reads": n} for f, n in e.reread_files.most_common(10)],
        "recommendations": [
            {"severity": r.severity, "title": r.title, "detail": r.detail} for r in e.recommendations
        ],
    }


def main():
    mcp.run()


if __name__ == "__main__":
    main()
