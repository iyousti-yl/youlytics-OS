---
name: brand
description: Build any deck, infographic, one-pager or PDF in Issam's brand. Use for every visual artifact.
model: sonnet
---

# /brand

1. Read `brand/brand-book.html`. Use only its colour tokens, fonts (IBM Plex Sans + Plex Mono), spacing scale, logo rules and voice.
2. Build the artifact as one self-contained HTML file first. Copy the `:root` tokens from the brand book.
3. Save it to `artifacts/YYYY-MM-DD-short-name/index.html` (plus any images, each with a `.txt` description).
4. Add an entry at the top of the `ENTRIES` list in `artifacts/index.html`: date, title, type, path, one-line summary. Newest first.
5. Export to PDF or images only at the end, and only when asked. With Chrome installed:
   `google-chrome --headless --print-to-pdf=artifacts/<folder>/export.pdf artifacts/<folder>/index.html`
6. Logos: use `brand/logo-mark.svg` on light grounds and `brand/logo-mark-reversed.svg` on sapphire. Never redraw them.
7. One amber highlight per view, ruby only for risks. Check text contrast before saving.
