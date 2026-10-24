# Planning router

Day, week and month plans, all plain Markdown. Every plan pulls from the active projects in [projects/](../projects/projects.md); reviews feed back into them.

| Folder or file | What goes there |
|---|---|
| `settings.md` | Working days and hours, the calendar, how many priorities per level. `/plan` reads it first |
| `month/YYYY-MM.md` | Month plan: review of last month, 3 outcomes, project status, dates that matter |
| `week/YYYY-Www.md` | Week plan (ISO week, Monday start): review of last week, top 5, a focus per day |
| `day/YYYY-MM-DD.md` | Day plan: top 3, meetings, time blocks, carried over, and a log at the end of the day |
| `templates/` | The fixed shape of each plan and of a project. `python3 os/planner/plans.py new day` makes today's file from it |

Make and fill plans with `/plan day`, `/plan week` or `/plan month`. Tick things off in the Planner (http://127.0.0.1:8765/app/planner) or in the file itself: `- [x]`.
