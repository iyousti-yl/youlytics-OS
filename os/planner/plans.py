#!/usr/bin/env python3
"""Day, week and month plans and the projects they pull from (for /plan, the Planner app and the dashboard).

  python3 os/planner/plans.py                  today's, this week's and this month's plan, and active projects
  python3 os/planner/plans.py new day|week|month [YYYY-MM-DD]
                                               make the plan file from its template if it doesn't exist; prints its path
  python3 os/planner/plans.py new project "Name" "One-line goal"
                                               make projects/<name>/project.md and add it to projects/projects.md
  python3 os/planner/plans.py capture "Call the printer about business cards"
                                               add a task to planning/inbox.md (what the Planner's capture box does)
  python3 os/planner/plans.py --json           the same summary as JSON (the dashboard serves it at /api/planner)

Plans are plain Markdown in planning/; projects in projects/<name>/project.md. Nothing else is stored.
"""
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PLANNING, PROJECTS = ROOT / "planning", ROOT / "projects"
TEMPLATES = PLANNING / "templates"
INBOX = PLANNING / "inbox.md"
INBOX_HEAD = "# Inbox\n\nQuick captures from the Planner. `/plan day` moves each one to a day, a week or a project, then deletes it here.\n\n"
TASK = re.compile(r"^(\s*)- \[( |x|X)\] (.*)$")
TOP = {"day": "Priorities", "week": "Top 5", "month": "3 outcomes"}


def week_id(d):
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def month_id(d):
    return d.strftime("%Y-%m")


def paths(d):
    return {"day": f"planning/day/{d.isoformat()}.md", "week": f"planning/week/{week_id(d)}.md",
            "month": f"planning/month/{month_id(d)}.md"}


def fill(text, values):
    return re.sub(r"\{\{(\w+)\}\}", lambda m: values.get(m.group(1), m.group(0)), text)


def values_for(d):
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    first = d.replace(day=1)
    return {"date": d.isoformat(), "weekday": d.strftime("%A"), "week": week_id(d), "month": month_id(d),
            "month_name": d.strftime("%B %Y"), "prev_week": week_id(monday - timedelta(days=7)),
            "prev_month": month_id(first - timedelta(days=1)),
            "range": f"{monday:%b} {monday.day} to {sunday:%b} {sunday.day}"}


def new_plan(kind, d):
    rel = paths(d)[kind]
    f = ROOT / rel
    if not f.exists():
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(fill((TEMPLATES / f"{kind}.md").read_text(encoding="utf-8"), values_for(d)))
    return rel


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:48] or "project"


def new_project(name, goal="", today=None):
    d = today or date.today()
    folder = PROJECTS / slug(name)
    f = folder / "project.md"
    if not f.exists():
        folder.mkdir(parents=True, exist_ok=True)
        f.write_text(fill((TEMPLATES / "project.md").read_text(encoding="utf-8"), {"date": d.isoformat(), "name": name, "goal": goal}))
        router = PROJECTS / "projects.md"
        router.write_text(router.read_text(encoding="utf-8").rstrip("\n") + f"\n| [{name}]({slug(name)}/project.md) | active | business | {goal} |\n")
    return str(f.relative_to(ROOT))


def tasks(text):
    """Every checkbox line with its section, so the Planner can tick it and count priorities."""
    out, section = [], ""
    for i, line in enumerate(text.splitlines()):
        if line.startswith("## "):
            section = line[3:].strip()
        m = TASK.match(line)
        if m and m.group(3).strip():
            out.append({"line": i, "done": m.group(2) != " ", "text": m.group(3).strip(), "section": section})
    return out


def plan(kind, d):
    rel = paths(d)[kind]
    f = ROOT / rel
    if not f.is_file():
        return {"kind": kind, "path": rel, "exists": False}
    text = f.read_text(encoding="utf-8")
    ts = tasks(text)
    top = [t for t in ts if t["section"] == TOP[kind]]
    return {"kind": kind, "path": rel, "exists": True, "text": text,
            "top": {"done": sum(t["done"] for t in top), "total": len(top)}, "tasks": ts}


def front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    meta = dict(re.findall(r"^(\w+):[ \t]*(.*)$", m.group(1), re.M)) if m else {}
    return meta, text[m.end():] if m else text


def projects():
    out = []
    for f in sorted(PROJECTS.glob("*/project.md")):
        meta, body = front_matter(f.read_text(encoding="utf-8"))
        title = re.search(r"^# (.+)$", body, re.M)
        goal = re.search(r"^## Goal\n+(.+)$", body, re.M)
        ts = tasks(body)
        nxt = [t["text"] for t in ts if t["section"] == "Next actions" and not t["done"]]
        miles = [t for t in ts if t["section"] == "Milestones"]
        out.append({"path": str(f.relative_to(ROOT)), "name": title.group(1).strip() if title else f.parent.name,
                    "status": meta.get("status", "active"), "area": meta.get("area", "business"),
                    "due": meta.get("due", ""), "goal": goal.group(1).strip() if goal and not goal.group(1).startswith("#") else "",
                    "next": nxt[:3], "milestones": {"done": sum(t["done"] for t in miles), "total": len(miles)}})
    return out


def capture(text, today=None):
    """Add one task to the inbox. Returns the line, or None if there's nothing usable."""
    text = " ".join(str(text).split())[:300].lstrip("#>-*[] ")
    if not text:
        return None
    line = f"- [ ] {text} (captured {(today or date.today()).isoformat()})"
    body = INBOX.read_text(encoding="utf-8") if INBOX.is_file() else INBOX_HEAD
    INBOX.write_text(body.rstrip("\n") + ("\n\n" if body.strip() == INBOX_HEAD.strip() else "\n") + line + "\n", encoding="utf-8")
    return line


def inbox():
    text = INBOX.read_text(encoding="utf-8") if INBOX.is_file() else ""
    return {"path": str(INBOX.relative_to(ROOT)), "items": [t for t in tasks(text) if not t["done"]],
            "tasks": tasks(text)}


def summary(d=None):
    d = d or date.today()
    return {"today": d.isoformat(), "weekday": d.strftime("%A"), "week": week_id(d), "month": month_id(d),
            "plans": {k: plan(k, d) for k in ("day", "week", "month")}, "projects": projects(), "inbox": inbox()}


def toggle(rel, line, text, done):
    """Tick or untick one checkbox in a plan or project file. Refuses anything else."""
    f = (ROOT / rel).resolve()
    if f.suffix != ".md" or not (f.is_relative_to(PLANNING) or f.is_relative_to(PROJECTS)) \
            or f.is_relative_to(TEMPLATES) or not f.is_file():
        return False
    lines = f.read_text(encoding="utf-8").split("\n")
    if not (0 <= line < len(lines)):
        return False
    m = TASK.match(lines[line])
    if not m or m.group(3).strip() != text:
        return False
    lines[line] = f"{m.group(1)}- [{'x' if done else ' '}] {m.group(3)}"
    f.write_text("\n".join(lines), encoding="utf-8")
    return True


def main(argv):
    if argv[:1] == ["capture"] and len(argv) >= 2:
        line = capture(" ".join(argv[1:]))
        print(line or "Nothing to capture.")
        return 0 if line else 1
    if argv[:1] == ["new"] and len(argv) >= 2:
        if argv[1] == "project" and len(argv) >= 3:
            print(new_project(argv[2], argv[3] if len(argv) > 3 else ""))
            return 0
        if argv[1] in TOP:
            print(new_plan(argv[1], date.fromisoformat(argv[2]) if len(argv) > 2 else date.today()))
            return 0
        print(__doc__)
        return 1
    s = summary()
    if "--json" in argv:
        print(json.dumps(s))
        return 0
    print(f"{s['weekday']} {s['today']} · {s['week']} · {s['month']}\n")
    for k, p in s["plans"].items():
        state = f"{p['top']['done']} of {p['top']['total']} {TOP[k].lower()} done" if p["exists"] else "not made yet"
        print(f"  {k:<6} {p['path']:<32} {state}")
    active = [p for p in s["projects"] if p["status"] == "active"]
    print(f"\n{len(s['inbox']['items'])} in the inbox ({s['inbox']['path']})")
    print(f"\n{len(active)} active of {len(s['projects'])} projects")
    for p in active:
        print(f"  {p['name']}: {p['next'][0] if p['next'] else 'no next action'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
