# ARMS setup

Source plan: RoboNuggets "ARMS Agentic OS v2" guide. Visual home: https://claude.ai/artifact/K1bST6pzovpqEHGeQ52Ck6

| Level | Status | Where |
|---|---|---|
| M1 Long-term memory | built | `AGENTS.md` (shared with Codex), `CLAUDE.md`, `MEMORY.md`, department router files, `/business-data` |
| Brand | chosen | Direction A "Sapphire Steady" in `brand/brand-book.html` |
| S1 Skill types | built | `/tone` + `/wildcard` (database), `/brand` (artifact), `/clean-up` (self-triggered, `os/server.py`) |
| S2 Model routing | built | `os/router/route.py`, `os/ask`, dashboard auto option; pins in skill frontmatter; router on Claude plan, Jev or OpenAI; optional Codex target |
| S3 Self-improving skills | built | `/teach` (feedback → principle → skill, after a yes), `CHANGELOG.md` per skill, `os/skills/usage.py` + dashboard skills table; first skill: `/tone` |
| R1 Active vs passive routines | built | `os/routines/run.py` + `routines.json`, inbox `os/inbox.jsonl` in the dashboard, `/routines-review`; passive routines reply NOTHING_TO_FLAG when quiet |
| R2 Capped routines | built | `cap_usd_week` per routine, passed as `--max-budget-usd`; `run.py costs`; `/cap-routine` |
| R3 Routines that suggest routines | built | `weekly-recos` routine (Fri 08:00) runs `/suggest-routines`; `os/recos/collect.py`; page `/recos` with a copy-back cart; memory cards cover M3's "suggested fixes" |
| M2 Short-term memory | built | compact rules in `CLAUDE.md`; `os/memory/cache.py` report (prices in `os/memory/prices.json`); `os/memory/keepwarm.py` off until the report says it pays |
| M3 Self-evolving memory | built | `/note` (haiku) with `NOTES.md` per skill or app, `/note apply`; `/calibrate` (sonnet); rule in `CLAUDE.md`; Recos memory cards |
| A1 Connect anything | built | `/connect`, `os/apps/apps.json` (GitHub via gh, Gmail via claude.ai connector), `os/apps/check.py` |
| A2 Mods | built | status line `.claude/statusline.py` via `.claude/settings.json`; Chrome clipper `os/chrome-clipper/` → `/api/clip` → `knowledge/reading/`. The job (saving articles) was Claude's pick; Issam can swap it |
| A3 Micro apps | built | `os/ui/` parts + gallery; `/app/<name>` hosting with `/api/data/<name>` storage; Review app `os/review/`; `/micro-app`. Review was Claude's pick (no chat history yet); swap it when a real weekly review shows up |

Model pins: /grammar, /wildcard, /clean-up, /business-data, /note → haiku, low effort. /tone, /brand, /teach, /routines-review, /cap-routine, /suggest-routines, /calibrate, /connect, /micro-app → sonnet. Everything else → the router in `os/router/config.json` picks (provider `claude` default, `jev` or `openai` optional; `use_codex` adds Codex on the ChatGPT plan).

All twelve levels are built. Next: Issam tests end to end (guide: `docs/test-guide.md`), then real use feeds /teach, /note and the Friday recos.
