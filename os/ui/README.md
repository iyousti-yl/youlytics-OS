# UI parts library

ARMS A3. Every local micro app links `/ui/parts.css` and `/ui/parts.js` (served by `os/server.py`), so Claude doesn't rebuild pieces from scratch and every app looks the same. Colours come from `brand/brand-book.html`. See them all at http://127.0.0.1:8765/ui/gallery.html.

| Part | Use |
|---|---|
| `UI.nav(current)` | The shared top bar with a skip link; call it first on every page |
| `.ui-page`, `.ui-header`, `.ui-grid`, `.ui-row`, `.ui-check` | Page layout; a checkbox with its label |
| `.ui-stats` / `.ui-stat` | At-a-glance numbers at the top, each linking to its section (`.attention`, `.alert`) |
| `.ui-rows`, `.ui-status`, `.ui-num` | Lists that wrap on a phone; a status dot that always has a word; aligned numbers |
| `.ui-scroll` + `.ui-table` | A table that scrolls inside its card, never the page |
| `.ui-card`, `.ui-facts`, `.ui-tag`, `.ui-badge`, `.ui-btn` | Building blocks |
| `UI.reviewCard({...})` | One item to approve, change (with a comment) or skip |
| `UI.commentBox({...})` | A comment field |
| `UI.cart({...})` + `UI.copyBack(...)` + `UI.copy(text)` | Bottom bar that copies picks or comments back to Claude |
| `UI.save(url, data)`, `UI.store(key, fallback)` | Save to a file through the server; small per-browser settings |
| `UI.toast(msg)`, `UI.say(msg)`, `UI.esc(text)` | Feedback; tell screen-reader users what changed; safe HTML |
| `.sr-only` | Text only screen readers hear, e.g. which item a repeated button acts on |

## A new micro app
1. Make `os/<name>/index.html` from these parts and `os/<name>/app.json` (`{"title": ..., "desc": ...}`).
2. It's served at `/app/<name>` and listed on the dashboard. Its work saves to `os/<name>/data.json` through `GET`/`POST /api/data/<name>` (gitignored), so nothing is lost on restart.
3. Follow the rules at the end of [docs/ui-audit.md](../../docs/ui-audit.md) (0 axe issues in light and dark, phone and desktop).
4. Give it a button that copies the result back to Claude (`UI.cart` + `UI.copyBack`).
