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
- `os/` holds the local dashboard, the model router (`os/router/`) and `os/ask`.

## Working rules
- Find things through the map and the router files. Don't search the whole workspace unless the map has no answer, and if it doesn't, add the missing line to the right router.
- Keep files plain text (Markdown, HTML, JSON). No vector database.
- Every image gets a text description: save the prompt that made it next to it as `<image>.txt`.
- Never ask for API keys in chat. Keys live in `.env` (gitignored).
- Keep anything from `life/` out of business files and artifacts unless Issam asks.
