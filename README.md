# youlytics-OS

Issam's Agentic OS: a plain-text workspace that Claude Code runs on, organised with the ARMS framework (Apps, Routines, Memory, Skills). Visual home and progress: https://claude.ai/artifact/K1bST6pzovpqEHGeQ52Ck6

## Use it
1. Clone this repo and open Claude Code in the folder. Claude reads `CLAUDE.md` (the map) and `MEMORY.md` (the catalog) at the start of every chat.
2. Save things where the department routers say: `knowledge/`, `business/`, `life/`.
3. Skills live in `.claude/skills/`. Call them by name, e.g. `/tone`, `/brand`.
4. For self-triggered skills, run `python3 os/server.py` and open http://127.0.0.1:8765.
5. Model routing: copy `.env.example` to `.env` and add your OpenRouter key. Then `os/ask "your prompt"` opens Claude Code on the model and effort Jev picks. `python3 os/router/route.py --test` checks the key, `on`/`off` switches routing, and `stats` shows picks, speed and cost.

## What's built
| Level | What |
|---|---|
| M1 Long-term memory | `CLAUDE.md` map, `MEMORY.md` catalog, router files per department, `/business-data` router skill |
| S2 Model routing | Fixed-step skills pinned to haiku; Jev (TypeSafe, via OpenRouter) picks model and effort for the rest; every pick logged with time and cost; on/off switch |
| S1 Skill types | `/tone` database skill with `/wildcard` (8 of 10 follow references, 2 wildcards), `/brand` artifact skill with `brand/brand-book.html` and `artifacts/index.html`, `/clean-up` self-triggered skill with the local dashboard |
