# youlytics-OS: map

This file is a map, not a rulebook. Start here, then open only the file you need.
Check the memory catalog before searching: @MEMORY.md

## Departments
Each department has one router file that says what lives in each of its folders.

| Department | Router | What it covers |
|---|---|---|
| Knowledge | [knowledge/knowledge.md](knowledge/knowledge.md) | Notes, reading, references, ideas |
| Business | [business/business.md](business/business.md) | Clients, offers, content, finance, operations |
| Life | [life/life.md](life/life.md) | Health, home, goals, personal admin |

## Other places
- `artifacts/` holds every deck, infographic and PDF, with `artifacts/index.html` as the inbox (newest first).
- `brand/brand-book.html` holds colours, fonts, spacing and logo rules. Every artifact is built from it.
- `.claude/skills/` holds the skills. Current ones: `/tone`, `/wildcard`, `/brand`, `/clean-up`, `/business-data`.
- `os/` holds the local dashboard (`python3 os/server.py`) and the reports skills write there.
- `memory/` holds one file per memory subject. `MEMORY.md` is its one-line-per-file catalog.

## Working rules
- Find things through this map and the router files. Don't search the whole workspace unless the map has no answer, and if it doesn't, add the missing line to the right router.
- Keep files plain text (Markdown, HTML, JSON). No vector database.
- Every image gets a text description: save the prompt that made it next to it as `<image>.txt`.
- Never ask for API keys in chat. Keys live in `.env` (gitignored).

## When a chat compacts, always keep
- Decisions made and the reason for each
- Templates and formats agreed with Issam
- Open tasks and who owns them
