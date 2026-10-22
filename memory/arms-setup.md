# ARMS setup

Source plan: RoboNuggets "ARMS Agentic OS v2" guide. Visual home: https://claude.ai/artifact/K1bST6pzovpqEHGeQ52Ck6

| Level | Status | Where |
|---|---|---|
| M1 Long-term memory | built | `AGENTS.md` (shared with Codex), `CLAUDE.md`, `MEMORY.md`, department router files, `/business-data` |
| Brand | chosen | Direction A "Sapphire Steady" in `brand/brand-book.html` |
| S1 Skill types | built | `/tone` + `/wildcard` (database), `/brand` (artifact), `/clean-up` (self-triggered, `os/server.py`) |
| S2 Model routing | built | `os/router/route.py`, `os/ask`, dashboard auto option; pins in skill frontmatter; router on Claude plan, Jev or OpenAI; optional Codex target |
| S3 Self-improving skills | built | `/teach` (feedback → principle → skill, after a yes), `CHANGELOG.md` per skill, `os/skills/usage.py` + dashboard skills table; first skill: `/tone` |
| All other levels | not started | |

Model pins: /grammar, /wildcard, /clean-up, /business-data → haiku, low effort. /tone, /brand → sonnet. Everything else → the router in `os/router/config.json` picks (provider `claude` default, `jev` or `openai` optional; `use_codex` adds Codex on the ChatGPT plan).

Suggested next: R1 passive routines.
