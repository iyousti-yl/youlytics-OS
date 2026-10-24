---
name: plan
description: Make or review Issam's day, week or month plan from the active projects, the level above and the calendar. Use for "/plan day", "/plan week", "/plan month", "plan my day/week/month" or "weekly review".
model: sonnet
effort: medium
---

# /plan day | week | month

Plans live in `planning/` (router: `planning/planning.md`). Each level reads the one above it and the active projects in `projects/`. Keep plans short: a plan Issam can read in one minute gets used.

## Every time
1. Read `planning/settings.md` (working hours, calendar, how many priorities, scope).
2. Run `python3 os/planner/plans.py` to see today's, this week's and this month's plan and the active projects.
3. Read each active `projects/<name>/project.md`: goal, open milestones with due dates, next actions.
4. Calendar: if `os/apps/apps.json` has a calendar entry, read that period's meetings with it (read-only). If there is none, leave Meetings empty and say once at the end: "No calendar connected yet: `/connect` your calendar to fill meetings."

## /plan day
1. Make the file: `python3 os/planner/plans.py new day` (prints the path; it never overwrites). If it already has a top 3, update it instead of starting over.
2. Read this week's plan and yesterday's day plan (`planning/day/`, the last weekday before today).
3. **Carried over:** every unticked item from yesterday's Top 3 and Also today, as plain bullets (not tasks), so nothing is lost silently.
4. **Top 3:** pick from this week's Top 5, the project next actions, milestones due within 7 days, and what was carried over. Each one is a single action that fits today and ends with its project in brackets, e.g. `- [ ] Send the BW/4HANA migration outline (Client X)`. Exactly 3 or fewer, never more.
5. **Meetings:** from the calendar, `- 09:00 to 10:00 Title`. **Time blocks:** put the top 3 into free time inside working hours, hardest one first.
6. **Also today:** small tasks only (under 30 minutes each), at most 5.
7. Fill the Focus line in one short phrase. Leave the Log for the evening.

## /plan week (run on Friday for the next week, or on Monday for this week)
1. Pick the week: on Friday, Saturday or Sunday plan next week; otherwise this week. Make the file with `python3 os/planner/plans.py new week <a date in that week>`.
2. **Review of last week:** read the week's plan and its day plans. Done: the top 5 items ticked and anything big from the day logs. Slipped, and why: one line each, using the day logs. Lesson: one line, or none.
3. Update each active project: tick milestones and next actions that the week finished, add a dated line to its Log, and add the next action if it has none.
4. **Top 5:** from the month's 3 outcomes, milestones due within 14 days and what slipped. Each names its project in brackets. Exactly 5 or fewer.
5. **By day:** one focus per working day; meetings that shape the day from the calendar.
6. **Not this week:** what you deliberately left out, so Issam sees the trade-off.

## /plan month (run on the 1st, or when asked)
1. Make the file with `python3 os/planner/plans.py new month`.
2. **Review of last month:** read last month's plan and its week reviews. Outcomes reached, missed and why, one lesson.
3. **3 outcomes:** results, not activities ("Client X signs the phase 2 offer", not "work on Client X"), each with its project and how Issam will know it's done. Exactly 3 or fewer.
4. **Project status:** one row per project that isn't done: status, next milestone, due date.
5. **Dates that matter:** deadlines, travel and holidays from the calendar and the projects.

## Rules
- Write only in `planning/` and in the Log, Milestones and Next actions of `projects/<name>/project.md`. Never change a project's goal or status without Issam.
- Never invent meetings, dates or tasks. If something is unknown, leave it empty and ask in one line.
- Projects with `area: life` may appear in plans, but never copy their details into `business/` or `artifacts/`.
- When Issam corrects a plan, offer `/teach plan` in one line.
- Unattended (a routine): write the file, then reply with one headline (`Today: <top 1>, <top 2>, <top 3>`) and the path. Interactive: show the draft in chat first and save after a yes.
