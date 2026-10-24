---
name: project
description: Add a project to the OS or update one, so plans can pull from it. Use for "/project new <name>", "/project <name> <update>", "/project list" or "add a project".
model: haiku
effort: low
---

# /project

Every project is one file, `projects/<name>/project.md` (router: `projects/projects.md`). `/plan` pulls from every project whose status is `active`.

## /project new <name>
1. Ask Issam, in one message, only what isn't given yet:
   - the goal in one sentence (what's true when it's done),
   - business or life,
   - up to 3 milestones with a due date each,
   - the very next action.
2. Run `python3 os/planner/plans.py new project "<Name>" "<goal>"`. It makes the file from `planning/templates/project.md` and adds a row to `projects/projects.md`.
3. Fill in the answers: `area:` and `due:` in the front matter (due = the last milestone's date), the milestones as `- [ ] <milestone> (due YYYY-MM-DD)`, and the next action. If the area is `life`, also change the row's Area in `projects/projects.md`.
4. Show the file and say: "It's in the next `/plan`."

## /project <name> <update>
Change only what Issam says: status (`active`, `paused`, `done`), a milestone, a next action, or a note. Add a dated line to the Log, e.g. `- 2026-11-03: paused until the client signs`. Keep the row in `projects/projects.md` in step with the status.

## /project list
Run `python3 os/planner/plans.py` and show the projects as a short table: name, status, next action.

## Rules
- One folder per project, named in lowercase with dashes. Files the project needs go next to `project.md`.
- A `life` project's details never go into `business/` or `artifacts/`.
