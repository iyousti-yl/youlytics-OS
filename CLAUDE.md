# youlytics-OS: map for Claude Code

The map and the rules shared with Codex: @AGENTS.md
The memory catalog: @MEMORY.md

## Claude Code only
- Skills: `/tone`, `/wildcard`, `/brand`, `/clean-up`, `/business-data`, `/grammar`, `/teach`, `/routines-review`, `/cap-routine`, `/suggest-routines`, `/note`, `/calibrate`, `/connect` in `.claude/skills/`.
- Never correct the same thing twice. When Issam gives feedback on a skill or app mid-job, offer `/note` so it's parked without breaking the flow. When you notice a lesson worth keeping (a repeat correction, a lasting preference or rule), offer `/calibrate` in one line instead of saving it quietly. Open notes live in each skill's `NOTES.md`; `/note apply` works through them.
- Skills improve from feedback. When Issam corrects or rates a skill's output, offer `/teach` in one line; never change a skill silently. Each skill keeps a `CHANGELOG.md`.
- `python3 os/skills/usage.py` ranks skills by runs and tokens from local sessions. Improve the most-used skill first.
- Every new fixed-step skill gets `model: haiku` and `effort: low` in its frontmatter. Use sonnet or opus only when the skill needs judgement.
- `os/router/` picks the agent, model and effort for each new prompt: pinned skills first, then the router set in `os/router/config.json` (Claude Haiku on the Claude plan, or Jev). With `use_codex` on, self-contained coding work can go to Codex on Issam's ChatGPT plan. `os/ask "prompt"` starts the chat on the pick.
- `os/server.py` runs the local dashboard; skills write their reports to `os/reports/`.
- Routines live in `os/routines/routines.json` and run with `python3 os/routines/run.py`. Prefer passive routines (they only reach `os/inbox.jsonl` when something is worth flagging); every routine has a weekly cap in USD. A new routine gets a flag rule, the fewest tools it needs, and a cap.

- Long chats: when a chat gets long, suggest `/compact keep <what matters>` rather than letting it compact on its own. `python3 os/memory/cache.py` shows how often a cold cache (idle over an hour) made a chat reload and what it cost; `os/memory/keepwarm.py` pings idle chats to keep them warm, and stays off unless those numbers say it pays. Show the numbers before changing anything.

- Apps: `os/apps/apps.json` lists how Claude reaches each app. To add one, use `/connect`: lightest way in first (maker's tools, CLI, API, then MCP), keys only in `.env`, one real read as the test.

- Mods: `.claude/statusline.py` is the status line (model, context, 5h/7d limits, cache warm or cold with the reload cost, branch). `os/chrome-clipper/` is a Chrome extension that saves pages to `knowledge/reading/` through the dashboard server. Clips are raw: summarise one when Issam asks.

## When a chat compacts, always keep
- Decisions made and the reason for each
- Templates and formats agreed with Issam
- Open tasks and who owns them
