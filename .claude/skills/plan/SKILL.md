---
name: plan
description: Make or review Issam's day, week or month plan from the active projects, the level above and the calendar. Use for "/plan day", "/plan week", "/plan month", "plan my day/week/month" or "weekly review".
model: sonnet
effort: medium
---

# /plan day | week | month

Plans live in `planning/` (router: `planning/planning.md`). Each level reads the one above it and the active projects in `projects/`. Keep plans short: a plan Issam can read in one minute gets used.

## Every time
1. Read `planning/settings.md` (the day job, Issam's hours, how many priorities, scope, calendar). The day job is a fixed block: never plan in it.
2. Run `python3 os/planner/plans.py` to see today's, this week's and this month's plan and the active projects.
3. Read each active `projects/<name>/project.md`: goal, open milestones with due dates, next actions.
4. Calendar: if `os/apps/apps.json` has a calendar entry, read that period's events with it (read-only; Issam's own Google Calendar only, never a client's). If there is none, leave Meetings empty and say once at the end: "No calendar connected yet: see 'Connect the calendar' in planning/settings.md."
5. Inbox: read `planning/inbox.md`. Each open item is a quick capture from the Planner.

## /plan day
1. Make the file: `python3 os/planner/plans.py new day` (prints the path; it never overwrites). If it already has priorities, update it instead of starting over.
2. Read this week's plan and yesterday's day plan (`planning/day/`, the last weekday before today).
3. **Carried over:** every unticked item from yesterday's Priorities and Also today, as plain bullets (not tasks), so nothing is lost silently.
4. **Sort the inbox:** move each open inbox item to where it belongs: today's Also today, a project's Next actions, or this week's plan under Not this week if it can wait. Then delete it from `planning/inbox.md`, along with any ticked item (Issam marked it done). If you can't tell where an item goes, leave it in the inbox and ask in one line.
5. **Priorities:** at most 2 on a weekday (Issam has 2 evening hours) and 3 on a weekend day. Pick from this week's Top 5, the project next actions, milestones due within 7 days, and what was carried over. Each one is a single action that fits the time and ends with its project in brackets, e.g. `- [ ] Fix the page title on youlytics.be (youlytics website)`.
6. **Meetings:** from the calendar, `- 19:00 to 19:30 Title`, leaving out the day job block. **Time blocks:** put the priorities into Issam's hours for that day (weekdays 19:00 to 21:00, weekends 08:00 to 12:00), hardest one first.
7. **Also today:** small tasks only (under 30 minutes each), at most 3 on a weekday and 5 on a weekend day.
8. Fill the Focus line in one short phrase. Leave the Log for the evening.

## /plan week (run on Friday for the next week, or on Monday for this week)
1. Pick the week: on Friday, Saturday or Sunday plan next week; otherwise this week. Make the file with `python3 os/planner/plans.py new week <a date in that week>`.
2. **Review of last week:** read the week's plan and its day plans. Done: the top 5 items ticked and anything big from the day logs. Slipped, and why: one line each, using the day logs. Lesson: one line, or none.
3. Update each active project: tick milestones and next actions that the week finished, add a dated line to its Log, and add the next action if it has none.
4. **Top 5:** from the month's 3 outcomes, milestones due within 14 days, what slipped and anything left in the inbox. Each names its project in brackets. Exactly 5 or fewer, sized for 18 hours (2 a weekday evening, 4 a weekend morning).
5. **By day:** one focus per day, Monday to Sunday; events that shape the day from the calendar.
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
- Business and personal projects share the plans. Projects with `area: life` may appear in plans, but never copy their details into `business/` or `artifacts/`.
- Never read a client calendar or client mail; the day job is one block, nothing more.
- When Issam corrects a plan, offer `/teach plan` in one line.
- Unattended (a routine): write the file, then reply with one headline (`Today: <priority 1>, <priority 2>`) and the path. Interactive: show the draft in chat first and save after a yes.
