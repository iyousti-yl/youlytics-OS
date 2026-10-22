# youlytics-OS

Issam's Agentic OS: a plain-text workspace that Claude Code runs on, organised with the ARMS framework (Apps, Routines, Memory, Skills). Visual home and progress: https://claude.ai/artifact/K1bST6pzovpqEHGeQ52Ck6

## Use it
1. Clone this repo and open Claude Code (or Codex) in the folder. Both read `AGENTS.md` (the shared map and rules); Claude also loads `CLAUDE.md` and `MEMORY.md`.
2. Save things where the department routers say: `knowledge/`, `business/`, `life/`.
3. Skills live in `.claude/skills/`. Call them by name, e.g. `/tone`, `/brand`.
4. For self-triggered skills, run `python3 os/server.py` and open http://127.0.0.1:8765.
5. Model routing: start chats with `os/ask "your prompt"` and the router picks the model and effort. Set the router in `os/router/config.json`:
   - `"provider": "claude"` (default): Claude Haiku on your Claude plan decides. No key; about 5 seconds per new chat.
   - `"provider": "jev"`: Jev via OpenRouter decides in under a second. Needs `OPENROUTER_API_KEY` in `.env`.
   - `"use_codex": true`: Codex on your ChatGPT plan becomes a choice for self-contained coding work. Install the Codex CLI and run `codex login` first.
   `python3 os/router/route.py --test` checks the setup, `on`/`off` switches routing, and `stats` shows picks, speed and cost.
6. Skills get better from feedback: after a skill's output, tell Claude what missed and run `/teach`. `python3 os/skills/usage.py` shows which skills you use most and what they cost in tokens.

## What's built
| Level | What |
|---|---|
| M1 Long-term memory | `CLAUDE.md` map, `MEMORY.md` catalog, router files per department, `/business-data` router skill |
| S2 Model routing | Fixed-step skills pinned to haiku; a router picks model and effort for the rest: Claude Haiku on the Claude plan by default, or Jev via OpenRouter, with Codex on the ChatGPT plan as an optional target; every pick logged with time and cost; on/off switch |
| S3 Self-improving skills | `/teach` turns feedback into one principle and folds it into the skill (shown first, saved after a yes, logged in the skill's `CHANGELOG.md`); usage ranking by runs and tokens |
| S1 Skill types | `/tone` database skill with `/wildcard` (8 of 10 follow references, 2 wildcards), `/brand` artifact skill with `brand/brand-book.html` and `artifacts/index.html`, `/clean-up` self-triggered skill with the local dashboard |
