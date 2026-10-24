# youlytics clipper (Chrome extension)

ARMS A2. One job: save the page you're reading to `knowledge/reading/` so Claude can read it later. It runs as plain code, so it costs no tokens.

- Toolbar button: saves the page with an optional note on why it's worth keeping.
- Right-click: "Save page to youlytics" or "Save selection to youlytics".

Each clip becomes `knowledge/reading/YYYY-MM-DD-<title>.md` (source link at the top, your note, the selection, then the page text) and gets a line in `knowledge/reading/index.md`. Ask Claude to summarise it whenever you like.

## Load it
1. Start the dashboard: `python3 os/server.py` (the clipper sends to http://127.0.0.1:8765, nothing leaves your computer).
2. Open `chrome://extensions`, turn on **Developer mode** (top right).
3. Click **Load unpacked** and pick this folder, `os/chrome-clipper`.
4. Pin it from the puzzle-piece menu. After you edit a file here, click the reload arrow on its card.
