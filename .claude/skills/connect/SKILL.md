---
name: connect
description: Connect Claude to any app, even one with no official connector, by finding the lightest way in (maker's tools, then a CLI, then the API, then an MCP), testing it with one real read and adding it to the apps registry. Use for "/connect <app>" or "connect Claude to ...".
model: sonnet
effort: medium
---

# /connect

ARMS A1. Every app Issam uses gets a way in, lightest first.

1. **Check what's there.** Read `os/apps/apps.json`. If the app is already in it, run `python3 os/apps/check.py <id>` and stop if it passes. Run `claude mcp list` to see the MCPs already loaded.
2. **Search for the way in, in this order**, and note each option you find with a link:
   1. The maker's own tools: an official connector (claude.ai connectors), an official CLI, or an official MCP from the maker.
   2. A community CLI. Claude types one short command and gets back just the answer, so it's the lightest on usage. Prefer well-maintained ones (recent releases, many users).
   3. The app's API, usually with an API key. Heavier, because answers come back long.
   4. A community MCP. The heaviest: every MCP's full tool list loads at the start of every chat, even unused. Keep MCPs few; suggest removing one Issam no longer uses.
3. **Pick the lightest one that works** and tell Issam what you picked and why, in two or three lines, before installing anything. Installing needs Issam's yes.
4. **Keys never go in the chat.** If it needs a key, give Issam the exact line to add to `.env` in the repo root (gitignored), like `MYFITNESSPAL_API_KEY=`, and wait until they say it's saved. Never ask them to paste a key here, and never print one. Scripts read keys from `.env`.
5. **Test it with one real read** (the smallest read-only call: a profile, the newest item) before calling it done. Show the result.
6. **Register it.** Add an entry to `os/apps/apps.json`: `id`, `name`, `way_in` (`maker` | `connector` | `cli` | `api` | `mcp`), `how` (one line, with install and sign-in steps), `key_env` (the `.env` name or null), `test` (the read-only shell command, or null), `test_in_claude` (for connectors and MCPs), `used_by`, `status`. Then run `python3 os/apps/check.py <id>`.
7. If a skill or routine should use the app, say which one in one line; don't change it unasked.
