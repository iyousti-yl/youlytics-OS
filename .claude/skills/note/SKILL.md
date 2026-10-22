---
name: note
description: Park feedback for a skill or app in its own NOTES.md without stopping the current job; with "apply", work through the parked notes. Use for "/note <skill> <feedback>" or "/note apply".
model: haiku
effort: low
---

# /note

ARMS M3, the fix backlog. Noting a fix must not break Issam's flow.

## Park a note: `/note [skill or app] <feedback>`
1. Find the target: the skill or app named, else the last skill used in this chat. A skill's file is `.claude/skills/<name>/NOTES.md`; an app's is `os/<app>/NOTES.md` (e.g. `os/recos/NOTES.md`). If you can't tell, ask in one line.
2. Append one line under `## Open` (create the file with `# Notes for <name>`, `## Open` and `## Applied` if missing):
   `- [ ] YYYY-MM-DD: <the feedback in Issam's words> (context: <what was being made, 10 words max>)`
3. Reply with one line, "Parked for /<name>.", and go straight back to the job. Don't fix anything now.

## Apply: `/note apply [skill or app]`
Only when Issam says apply. Run this on the smallest model that can do it (this skill is pinned to haiku).
1. List every open note (or only the named target's) and count them.
2. For each note, make the smallest edit to that skill's `SKILL.md` (or the app's file) that does what the note asks. Merge notes that say the same thing.
3. A note that needs judgement (it conflicts with an existing rule, or it's a lasting lesson rather than a fix) is not applied here: mark it "needs /teach" or "needs /calibrate" and leave it open.
4. Show all edits as one diff and wait for a yes. On yes, save, tick each applied note (`- [x]`), move it under `## Applied` with the date, and add one line per skill at the top of its `CHANGELOG.md`: `YYYY-MM-DD: applied N notes: <short list>.`
