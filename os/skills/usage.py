#!/usr/bin/env python3
"""Rank skills by how often they run and how many tokens they use (ARMS S2 and S3).

  python3 os/skills/usage.py              table of this workspace's skills, most used first
  python3 os/skills/usage.py --days 30    only the last 30 days (default 90)
  python3 os/skills/usage.py --all        every skill seen, not only this workspace's
  python3 os/skills/usage.py --json       the same data as JSON (the dashboard uses this)

It reads Claude Code's local session transcripts (~/.claude/projects/*/*.jsonl).
A skill counts as used when Issam types /name or Claude calls the Skill tool.
Tokens are the input, cache and output tokens of the assistant replies in the
same turn as the skill, so they show roughly what a skill costs to run.
Nothing leaves the computer.
"""
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS = ROOT / ".claude" / "skills"
TRANSCRIPTS = Path.home() / ".claude" / "projects"
COMMAND = re.compile(r"<command-name>/?([a-z0-9][a-z0-9:-]*)</command-name>")


def own_skills():
    return sorted(p.parent.name for p in SKILLS.glob("*/SKILL.md"))


def open_notes(name):
    """Parked /note feedback still waiting in the skill's NOTES.md."""
    f = SKILLS / name / "NOTES.md"
    return f.read_text(encoding="utf-8").count("- [ ]") if f.is_file() else 0


def turn_tokens(usage):
    return sum(usage.get(k) or 0 for k in
               ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens"))


def skills_in(entry):
    """Skill names invoked by one transcript entry."""
    msg = entry.get("message") or {}
    content = msg.get("content")
    found = []
    if entry.get("type") == "user":
        text = content if isinstance(content, str) else json.dumps(content)
        found += COMMAND.findall(text)
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "Skill":
                name = (block.get("input") or {}).get("skill")
                if name:
                    found.append(name)
    return [f.split(":")[-1] for f in found]


def is_new_prompt(entry):
    """A real prompt from Issam starts a new turn; tool results and meta entries don't."""
    if entry.get("type") != "user" or entry.get("isMeta"):
        return False
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, list):
        return not any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content)
    return True


def collect(days):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    stats = defaultdict(lambda: {"runs": 0, "tokens": 0, "last": ""})
    for path in TRANSCRIPTS.glob("*/*.jsonl"):
        active = set()
        try:
            lines = path.read_text(errors="replace", encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = entry.get("timestamp", "")
            try:
                when = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                continue
            if when < since:
                continue
            if is_new_prompt(entry):
                active = set()
            for name in skills_in(entry):
                active.add(name)
                stats[name]["runs"] += 1
                stats[name]["last"] = max(stats[name]["last"], ts[:10])
            if entry.get("type") == "assistant" and active:
                tokens = turn_tokens((entry.get("message") or {}).get("usage") or {})
                for name in active:
                    stats[name]["tokens"] += tokens
    return stats


def main(argv):
    days = int(argv[argv.index("--days") + 1]) if "--days" in argv else 90
    stats = collect(days)
    names = set(stats) if "--all" in argv else set(own_skills())
    rows = [{"skill": n, **stats.get(n, {"runs": 0, "tokens": 0, "last": ""}), "notes": open_notes(n)} for n in names]
    rows.sort(key=lambda r: (-r["runs"], -r["tokens"], r["skill"]))
    if "--json" in argv:
        print(json.dumps({"days": days, "skills": rows}))
        return 0
    print(f"Skills used in the last {days} days, most used first\n")
    print(f"{'skill':<26}{'runs':>6}{'tokens':>14}{'notes':>7}  last used")
    for r in rows:
        print(f"/{r['skill']:<25}{r['runs']:>6}{r['tokens']:>14,}{r['notes']:>7}  {r['last'] or '-'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
