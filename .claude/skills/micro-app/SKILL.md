---
name: micro-app
description: Find the review Issam repeats most in chat and give it its own small local app built from the UI parts library, with a copy-back button and work saved to a file. Use for "/micro-app" or "give this job its own app".
model: sonnet
effort: medium
---

# /micro-app

ARMS A3. Once a job is routine, ask whether a chat window is still the best place for it.

1. **Find the job.** Run `python3 os/recos/collect.py --days 30` and read `os/recos/week-prompts.json`. Look for the review Issam repeats every week: approving drafts, checking reports, picking options, giving the same kind of feedback. Check `os/<name>/app.json` files first: `os/review/` (artifacts and reports) and `os/recos/` already exist. Propose the top one in two lines and wait for a yes.
2. **Parts first.** Read `os/ui/README.md`. Build only from `os/ui/parts.css` and `os/ui/parts.js`. If the app needs a part that doesn't exist, add it to the library (and to `os/ui/gallery.html`) first, so the next app can reuse it.
3. **Build the smallest app that does that one job.** `os/<name>/index.html` plus `os/<name>/app.json`. It is served at `/app/<name>` and listed on the dashboard. Read inputs from files in the workspace; if it needs a new read endpoint, add it to `os/server.py` next to `review_items`.
4. **Save the work to a file** through `/api/data/<name>` (`UI.save`), so nothing is lost on restart.
5. **Accessible and quick.** Call `UI.nav("<Name>")` first (add the page to `PAGES` in `parts.js` if it belongs in the top bar). Follow the rules at the end of `docs/ui-audit.md`: answer first, never colour alone, named buttons, `UI.say()` for changes, focus kept, works at 375px and in dark mode, 0 axe issues.
6. **Copy back.** One button that copies Issam's comments or picks back to Claude as clear instructions (`UI.cart` + `UI.copyBack`).
7. **Walk through one real use** with Issam before calling it done: open it, review one real item, copy back, and act on what comes back.
