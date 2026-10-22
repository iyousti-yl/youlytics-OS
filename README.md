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

7. Routines: `python3 os/routines/run.py list` shows them; `run <id>` runs one now; `install` prints the line that runs due routines every 15 minutes (cron on Mac/Linux, Task Scheduler on Windows). Results land in the dashboard inbox. `/routines-review` sorts them into active and passive, and `/cap-routine` trims the most expensive one.
8. Every Friday at 08:00 the `weekly-recos` routine runs `/suggest-routines`: it reads your week of sessions, spots jobs you did by hand 3 or more times and puts cards on http://127.0.0.1:8765/recos. Add the good ones to the cart, copy it and paste it into Claude Code. `/recos?example` shows example cards.
9. Long chats: `python3 os/memory/cache.py` shows the last 30 days of cold-cache reloads and what keeping chats warm would have saved. Only if it pays: `python3 os/memory/keepwarm.py on`, then schedule it with `keepwarm.py install`.
10. Never correct Claude twice: type `/note <skill> <feedback>` mid-job to park a fix in that skill's `NOTES.md`, then `/note apply` when you're ready (it runs on haiku). For lessons that matter, `/calibrate` saves the rule to `memory/`, links it and fixes the skill, after you approve.
11. Apps: `/connect <app>` finds the lightest way in for any app (maker's tools, then a CLI, then the API, then an MCP), tests it with one real read and adds it to `os/apps/apps.json`. If it needs a key, you add it to `.env` yourself. `python3 os/apps/check.py` re-tests them all.
12. Mods: the status line turns on by itself in this folder (`.claude/settings.json`; on Windows, change `python3` to `python` there). The Chrome clipper saves pages to `knowledge/reading/` with one click or a right-click; load it from `os/chrome-clipper/` (steps in its README).
13. Micro apps: the dashboard links them. **Review** (`/app/review`) lists the artifacts and reports Claude made in the last two weeks; approve, change with a comment, or skip, then copy your review back to Claude. Verdicts are saved to `os/review/data.json`. `/micro-app` gives the next repeated job its own app, built from the parts in `os/ui/` (see `/ui/gallery.html`).

## What's built
| Level | What |
|---|---|
| M1 Long-term memory | `CLAUDE.md` map, `MEMORY.md` catalog, router files per department, `/business-data` router skill |
| S2 Model routing | Fixed-step skills pinned to haiku; a router picks model and effort for the rest: Claude Haiku on the Claude plan by default, or Jev via OpenRouter, with Codex on the ChatGPT plan as an optional target; every pick logged with time and cost; on/off switch |
| S3 Self-improving skills | `/teach` turns feedback into one principle and folds it into the skill (shown first, saved after a yes, logged in the skill's `CHANGELOG.md`); usage ranking by runs and tokens |
| S1 Skill types | `/tone` database skill with `/wildcard` (8 of 10 follow references, 2 wildcards), `/brand` artifact skill with `brand/brand-book.html` and `artifacts/index.html`, `/clean-up` self-triggered skill with the local dashboard |
| R1 Active vs passive routines | `os/routines/` registry and runner; active routines always post to the inbox, passive ones only when they flag something; desktop notification; `/routines-review`; starter routines: machine care, brand watch, domain scout, Gmail digest (off until the connector is named) |
| R2 Capped routines | Weekly USD cap per routine, enforced as the run's budget; cost and tokens logged per run; `run.py costs` and the dashboard show week cost against cap; `/cap-routine` |
| R3 Routines that suggest routines | `os/recos/collect.py` gathers the week's typed prompts locally; `/suggest-routines` writes routine, skill and memory cards to `os/recos/recos.json`; the Recos page (built from the `os/ui/` parts) has a cart that copies the picks back to Claude |
| M2 Short-term memory | Compact rules in `CLAUDE.md`; `os/memory/cache.py` counts cold-cache reloads over 30 days and prices a keep-warm ping at API rates; `os/memory/keepwarm.py` (off by default) pings idle chats on the same model as a fork, checks each ping hit the cache, and stops pinging a chat when it misses |
| M3 Self-evolving memory | `/note` parks feedback in each skill's or app's `NOTES.md` and applies it only on `/note apply` (haiku); `/calibrate` writes the lesson to `memory/`, links related memories and fixes the skill; `CLAUDE.md` says to offer them instead of saving quietly; open notes show in the dashboard; memory cards on the Recos page are the suggested fixes |
| A1 Connect anything | `/connect` (maker's tools > CLI > API > MCP, keys in `.env`, one real read to test); registry `os/apps/apps.json` seeded with GitHub (gh) and Gmail (claude.ai connector); `os/apps/check.py`; apps table on the dashboard |
| A2 Mods | Status line `.claude/statusline.py` (model, effort, context, 5h and 7d limits, prompt cache warm/cold with minutes left and reload cost, session cost, branch; no tokens); Chrome extension `os/chrome-clipper/` saves the page or a selection with a note to `knowledge/reading/` via the dashboard server |
| A3 Micro apps | UI parts library `os/ui/` (review card, comment box, cart with copy-back, save, toast; gallery page); the server hosts any `os/<name>/` app at `/app/<name>` with file storage; first app: Review (artifacts and reports, verdicts saved, comments copied back); `/micro-app` builds the next one |
