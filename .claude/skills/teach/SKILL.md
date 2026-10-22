---
name: teach
description: Fold Issam's feedback on a skill's output back into that skill, so it gets sharper next time. Use when Issam corrects, rates or edits what a skill made, or says "teach".
model: sonnet
---

# /teach

The teach switch for every skill (ARMS S3). One round of feedback in, one better skill out.

1. **Find the skill.** The one whose output the feedback is about, usually the last skill run in this chat. If it's unclear, ask which one in one line.
2. **Read it.** Its `SKILL.md`, its `references/` files and its `CHANGELOG.md`.
3. **Name the principle.** Ask why the output missed, not just what to change. Write the lesson as one principle that would have prevented the miss and also covers similar cases. One principle per round.
4. **Fold it in.** Put it where it belongs: steps in `SKILL.md`, knowledge and examples in `references/`. Rewrite or merge an existing line rather than adding a new rule on top. The skill should get sharper, not longer; a good update often makes it shorter.
5. **Show the change first.** Show the diff and the principle in two lines, then wait for a yes. Don't save anything before that.
6. **Log it.** On yes, save the change and add one line at the top of the skill's `CHANGELOG.md`: `YYYY-MM-DD: <what changed>. Why: <the feedback in a few words>.`
7. **Look wider.** If the lesson applies to every agent and skill, not just this one, offer to add it to `AGENTS.md` too.

Never change a skill silently. Small skills pinned to haiku stay fixed-step: if a lesson needs judgement, say the skill may need a bigger model instead of adding judgement to it.
