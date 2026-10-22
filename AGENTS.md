# youlytics-OS: shared rules for every agent

Claude Code and Codex both work in this workspace. Rules that apply to both live here; `CLAUDE.md` imports this file.

## Map
Start from the department router, then open only the file you need.

| Department | Router | What it covers |
|---|---|---|
| Knowledge | [knowledge/knowledge.md](knowledge/knowledge.md) | Notes, reading, references, ideas |
| Business | [business/business.md](business/business.md) | Clients, offers, content, finance, operations |
| Life | [life/life.md](life/life.md) | Health, home, goals, personal admin |

- `MEMORY.md` is the memory catalog (one line per file in `memory/`). Check it before searching.
- `artifacts/` holds every deck, infographic and PDF, with `artifacts/index.html` as the inbox (newest first).
- `brand/brand-book.html` holds the youlytics brand. Everything visual is built from it.
- `.claude/skills/<name>/SKILL.md` holds each skill's steps. Agents other than Claude Code can follow them as plain instructions.
- `os/` holds the local dashboard (`python3 os/server.py`, http://127.0.0.1:8765) and the machinery behind it:
  - `os/router/` and `os/ask`: model routing
  - `os/routines/`: scheduled routines, their caps and run log; results go to the dashboard inbox
  - `os/recos/`: Friday suggestions; `os/review/`: the review micro app; `os/ui/`: UI parts every micro app is built from; `os/brain/`: the Brain map of every file and how they link
  - `os/memory/`: cold-cache report and keep-warm pings
  - `os/apps/apps.json`: how each outside app is reached; `os/chrome-clipper/`: the browser extension
  - `os/skills/usage.py`: skill usage ranking

## Working rules
- Find things through the map and the router files. Don't search the whole workspace unless the map has no answer, and if it doesn't, add the missing line to the right router.
- Keep files plain text (Markdown, HTML, JSON). No vector database.
- Every image gets a text description: save the prompt that made it next to it as `<image>.txt`.
- Never ask for API keys in chat. Keys live in `.env` (gitignored).
- Keep anything from `life/` out of business files and artifacts unless Issam asks.
