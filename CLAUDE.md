# youlytics-OS: map for Claude Code

The map and the rules shared with Codex: @AGENTS.md
The memory catalog: @MEMORY.md

## Claude Code only
- Skills: `/tone`, `/wildcard`, `/brand`, `/clean-up`, `/business-data`, `/grammar` in `.claude/skills/`.
- Every new fixed-step skill gets `model: haiku` and `effort: low` in its frontmatter. Use sonnet or opus only when the skill needs judgement.
- `os/router/` picks the agent, model and effort for each new prompt: pinned skills first, then the router set in `os/router/config.json` (Claude Haiku on the Claude plan, or Jev). With `use_codex` on, self-contained coding work can go to Codex on Issam's ChatGPT plan. `os/ask "prompt"` starts the chat on the pick.
- `os/server.py` runs the local dashboard; skills write their reports to `os/reports/`.

## When a chat compacts, always keep
- Decisions made and the reason for each
- Templates and formats agreed with Issam
- Open tasks and who owns them
