# youlytics-OS

Issam's Agentic OS: a plain-text workspace that Claude Code runs on, organised with the ARMS framework (Apps, Routines, Memory, Skills). Visual home and progress: https://claude.ai/artifact/K1bST6pzovpqEHGeQ52Ck6

## Use it
1. Clone this repo and open Claude Code in the folder. Claude reads `CLAUDE.md` (the map) and `MEMORY.md` (the catalog) at the start of every chat.
2. Save things where the department routers say: `knowledge/`, `business/`, `life/`.
3. Skills live in `.claude/skills/`. Call them by name, e.g. `/tone`, `/brand`.
4. For self-triggered skills, run `python3 os/server.py` and open http://127.0.0.1:8765.

## What's built
| Level | What |
|---|---|
| M1 Long-term memory | `CLAUDE.md` map, `MEMORY.md` catalog, router files per department, `/business-data` router skill |
| S1 Skill types | `/tone` database skill with `/wildcard` (8 of 10 follow references, 2 wildcards), `/brand` artifact skill with `brand/brand-book.html` and `artifacts/index.html`, `/clean-up` self-triggered skill with the local dashboard |
