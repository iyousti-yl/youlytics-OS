# UI and UX audit (2026-10-22)

Goal: every local page is accessible (keyboard, screen reader, contrast, phone, dark mode) and still quick to use: the answer first, then the detail.

Pages checked: Dashboard `/`, Brain `/app/brain`, Recos `/recos`, Review `/app/review`, UI gallery `/ui/gallery.html`, Chrome clipper popup.

How: axe-core 4.10 (WCAG 2.0 A, 2.1 AA, 2.2 AA and best practice) on every page in light and dark at 1280px and 375px wide; a keyboard-only pass; a manual read of each page for clarity and effort.

**Result: 0 axe issues on every page, both themes, both widths, and no sideways scrolling on a phone.**

## What was found and fixed

| # | Page | Finding | Severity | Fix |
|---|---|---|---|---|
| 1 | Dashboard | Built separately from the shared parts: no dark mode, mono font for prose, its own colours | High | Rebuilt on `os/ui/parts.css` and `parts.js`, so it matches every other page and follows light/dark |
| 2 | Dashboard | Polling every 3s rebuilt the whole page: keyboard focus and screen-reader position were lost | High | Each section re-renders only when its data changed and puts focus back; polling pauses when the tab is hidden |
| 3 | Dashboard | Wide tables scrolled the whole page sideways on a phone; one table header was empty | High | Routines, inbox and apps are lists that wrap; the skills table scrolls inside its card and every column has a header |
| 4 | Dashboard | No answer at a glance: you had to read every section to know if anything needed you | Medium | Four tiles on top: inbox unread, routine spend against caps, apps working, prompt cache. Each links to its section; the one that needs you is marked |
| 5 | Dashboard | "Over cap" shown by red only | Medium | Said in words next to the cost, with the meter as extra |
| 6 | Dashboard | Ten "Run now" and "Mark read" buttons with the same name for a screen reader | Medium | Each carries the routine or item name (hidden text) |
| 7 | Dashboard | Nothing announced when a run starts or finishes | Medium | Status line with `role=status`, and `UI.say()` announces start and result |
| 8 | Dashboard | 14 skill rows of zeros | Low | Shows used skills first, "Show all" toggle (with `aria-expanded`) for the rest |
| 9 | Dashboard | Routine said "OFF" and "active" in the same row | Low | Plain words: "Off until set up", "quiet unless it finds something" or "always reports" |
| 10 | All | No shared way between pages, no skip link | Medium | `UI.nav()` top bar (Dashboard, Brain, Recos, Review) with the current page marked, plus a "Skip to content" link |
| 11 | All | Focus ring missing or faint on some controls | Medium | One `:focus-visible` ring for every link, button and field |
| 12 | All | Small touch targets (Mark read, quiet buttons) | Low | Buttons at least 36px tall, quiet ones 32px |
| 13 | All | Native selects and checkboxes stayed light in dark mode | Low | `color-scheme: light dark` |
| 14 | All | Motion for people who turned it off | Low | `prefers-reduced-motion` stops transitions; Brain draws the settled graph without animating |
| 15 | Review | Long report text in a scroll box that a keyboard can't reach | Medium | The box is focusable and labelled; verdict buttons are grouped and announce the choice |
| 16 | Recos | Every card had a button called "Add to cart" | Medium | Each says which card; focus stays on it after adding; the cart announces the count |
| 17 | Brain | Side panel re-read aloud on every change | Low | Panel labelled instead; picking a file announces one short line ("points to 5, pointed to by 3") |
| 18 | Brain | A canvas graph is mouse-only | Medium | List view with every file as a button, search, and arrow-key pan and zoom on the canvas |
| 19 | Gallery | Headings jumped from h1 to h3 | Low | h2, and the gallery now shows the new parts (nav, stats, rows, status) |
| 20 | Clipper | Note box had no label; save result not announced | Medium | Visible label, `role=status` on the result, focus ring |

## Rules for every new page (checked by `/micro-app`)

1. Build only from `os/ui/` parts and call `UI.nav("<Page>")` first.
2. Answer first: the one thing that needs Issam goes at the top, details below.
3. Never colour alone: every status has a word.
4. Buttons that repeat get the item's name in hidden text.
5. Anything that changes without a click is announced with `UI.say()`; anything that re-renders keeps focus.
6. Works at 375px wide with no sideways scroll, and in dark mode.
7. Before shipping, run axe in light and dark at 1280px and 375px: 0 issues.
