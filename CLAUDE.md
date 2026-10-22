# youlytics-OS: map for Claude Code

The map and the rules shared with Codex: @AGENTS.md
The memory catalog: @MEMORY.md

## Claude Code only
- Skills: `/tone`, `/wildcard`, `/brand`, `/clean-up`, `/business-data`, `/grammar`, `/teach`, `/routines-review`, `/cap-routine` in `.claude/skills/`.
- Skills improve from feedback. When Issam corrects or rates a skill's output, offer `/teach` in one line; never change a skill silently. Each skill keeps a `CHANGELOG.md`.
- `python3 os/skills/usage.py` ranks skills by runs and tokens from local sessions. Improve the most-used skill first.
- Every new fixed-step skill gets `model: haiku` and `effort: low` in its frontmatter. Use sonnet or opus only when the skill needs judgement.
- `os/router/` picks the agent, model and effort for each new prompt: pinned skills first, then the router set in `os/router/config.json` (Claude Haiku on the Claude plan, or Jev). With `use_codex` on, self-contained coding work can go to Codex on Issam's ChatGPT plan. `os/ask "prompt"` starts the chat on the pick.
- `os/server.py` runs the local dashboard; skills write their reports to `os/reports/`.
- Routines live in `os/routines/routines.json` and run with `python3 os/routines/run.py`. Prefer passive routines (they only reach `os/inbox.jsonl` when something is worth flagging); every routine has a weekly cap in USD. A new routine gets a flag rule, the fewest tools it needs, and a cap.

## When a chat compacts, always keep
- Decisions made and the reason for each
- Templates and formats agreed with Issam
- Open tasks and who owns them
