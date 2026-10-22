---
name: calibrate
description: Save a lesson Issam taught so it sticks: write it to memory, link it to related memories, and fix the skill it belongs to. Use when Issam corrects the same thing twice, states a lasting preference or rule, or says "calibrate".
model: sonnet
---

# /calibrate

ARMS M3. If Issam has to correct Claude on the same thing twice, the memory missed it. Don't leave important lessons to chance or to automatic memory.

1. **Name the lesson.** One rule, written so it applies next time without this chat: what to do, when, and why (Issam's reason, or ask for it in one line). Example: "Invoices for Belgian clients are in Dutch. Why: their finance teams process Dutch only."
2. **Find what it touches.** Read `MEMORY.md` (the catalog) and open only the memory files whose line is related. Check the department router (`knowledge/`, `business/`, `life/`) and any skill the lesson belongs to. Anything about Issam's personal life stays in `life/` and out of business memories.
3. **Write the memory.** One file per subject in `memory/` (e.g. `memory/invoicing.md`): add the rule to the existing subject file if there is one, else create it with a `# Title` and one line per rule. Replace a rule that the lesson contradicts instead of adding a second one.
4. **Link it.** Add or update the file's one line in `MEMORY.md`. In the memory file, add a `Related:` line linking related memory files and router files, and add the back-link in each of those.
5. **Fix the skill.** If the lesson belongs to a skill, fold it in the /teach way: the smallest change to `SKILL.md` or its `references/`, rewriting an existing line rather than stacking a new rule. Close any matching open `/note` in its `NOTES.md`.
6. **Show everything first.** One diff covering memory, catalog, links and skill. Change nothing until Issam approves. On yes, save, and log one line at the top of the skill's `CHANGELOG.md`: `YYYY-MM-DD: calibrated: <the rule>.`
