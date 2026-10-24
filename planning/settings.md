# Planning settings

`/plan` reads this before every plan. Change a line here, not in the skill.

- **Week starts:** Monday (ISO weeks, e.g. 2026-W45)
- **Working days and hours:** Monday to Friday, 08:30 to 17:30 (default, not confirmed by Issam yet)
- **Priorities:** 3 per day, 5 per week, 3 outcomes per month. Everything else is a list, not a priority
- **Calendar:** not connected yet. Once `/connect` adds one to `os/apps/apps.json`, `/plan` reads meetings from it (read-only, never writes)
- **Scope:** business projects. Personal projects only when Issam adds one with area `life`; their details never go into business files or artifacts
- **Morning plan:** weekdays 07:30 (routine `morning-plan`). **Weekly review:** Friday 16:00 (`weekly-review`). **Month plan:** the 1st at 08:00 (`monthly-plan`)
