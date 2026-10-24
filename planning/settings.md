# Planning settings

`/plan` reads this before every plan. Change a line here, not in the skill. Answers from Issam, 2026-10-24.

- **Week starts:** Monday (ISO weeks, e.g. 2026-W45)
- **Day job:** Monday to Friday, 09:00 to 17:00 (SAP consultancy). A fixed block: never plan in it, and never read or connect client calendars or client mail
- **Hours for youlytics and personal projects:** weekdays 19:00 to 21:00 (2 hours), Saturday and Sunday 08:00 to 12:00 (4 hours). 18 hours a week
- **Priorities:** at most 2 per weekday, 3 per weekend day, 5 per week, 3 outcomes per month. Everything else is a list, not a priority
- **Scope:** business and personal life together. Personal projects have `area: life`; they show up in plans, but their details never go into `business/` or `artifacts/`
- **Tasks:** the plan files are the only task list. Quick captures land in `inbox.md` (from the Planner) and `/plan` sorts them
- **Calendar:** Google Calendar on Issam's Gmail account, with a calendar called "youlytics" for this work and the day job as one recurring block. Not connected yet: see "Connect the calendar" below. Read-only, never writes
- **Schedules:** day plan every day at 07:30 (routine `morning-plan`), weekly review Friday 18:30 (`weekly-review`, ready for the 19:00 slot), month plan on the 1st at 08:00 (`monthly-plan`)

## Connect the calendar
1. In Google Calendar (same Google account as the Gmail Claude already reads), add a calendar called "youlytics". Add the day job as a repeating event, Monday to Friday 09:00 to 17:00. Personal and youlytics appointments go in this calendar or the main one; client meetings stay in the client's calendar.
2. In claude.ai, Settings > Connectors: connect Google Calendar with that account.
3. In Claude Code in this folder, run `/connect google calendar`. It checks that Claude can read this week's events, adds the calendar to `os/apps/apps.json`, and adds its tool name to the three planning routines.
