#!/usr/bin/env python3
"""Gather the past week of Issam's prompts for /suggest-routines (ARMS R3).

  python3 os/recos/collect.py              last 7 days, writes os/recos/week-prompts.json
  python3 os/recos/collect.py --days 14    a longer window

It reads Claude Code's local session transcripts (~/.claude/projects/*/*.jsonl) and keeps
only what Issam typed: no tool results, no headless runs (routines, the router, the
dashboard) and no subagent chats. The output file is gitignored and never leaves the
computer. It also lists the routines and skills that already exist, so nothing is
suggested twice.
"""
import json
import re
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = HERE / "week-prompts.json"
TRANSCRIPTS = Path.home() / ".claude" / "projects"
COMMAND = re.compile(r"<command-name>/?([a-z0-9][a-z0-9:-]*)</command-name>")
ARGS = re.compile(r"<command-args>(.*?)</command-args>", re.S)
NOISE = re.compile(r"<(system-reminder|local-command-stdout|local-command-stderr|command-message|task-notification)>.*?</\1>", re.S)
HEADLESS = ("sdk-cli", "sdk-py", "sdk-ts")
ROUTER_PREFIX = "You route prompts for an AI work assistant"


def prompt_text(entry):
    """What Issam typed in one transcript entry, or None if it isn't a typed prompt."""
    if entry.get("type") != "user" or entry.get("isMeta") or entry.get("isSidechain"):
        return None
    if entry.get("entrypoint") in HEADLESS:
        return None
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, list):
        if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
            return None
        content = " ".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    if not isinstance(content, str):
        return None
    cmd = COMMAND.search(content)
    if cmd:
        args = ARGS.search(content)
        content = f"/{cmd.group(1)} {args.group(1).strip() if args else ''}"
    text = NOISE.sub("", content).strip()
    if not text or text.startswith(ROUTER_PREFIX) or text.startswith("Caveat:"):
        return None
    return text


def existing():
    routines = json.loads((ROOT / "os" / "routines" / "routines.json").read_text(encoding="utf-8"))["routines"]
    skills = sorted(p.parent.name for p in (ROOT / ".claude" / "skills").glob("*/SKILL.md"))
    return {"routines": [{"id": r["id"], "name": r["name"], "schedule": r["schedule"], "prompt": r["prompt"]}
                         for r in routines],
            "skills": skills}


def collect(days):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    routine_prompts = {r["prompt"] for r in existing()["routines"]}
    prompts, sessions, commands, seen = [], set(), Counter(), set()
    for path in TRANSCRIPTS.glob("*/*.jsonl"):
        try:
            lines = path.read_text(errors="replace", encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            try:
                entry = json.loads(line)
                when = datetime.fromisoformat(entry.get("timestamp", "").replace("Z", "+00:00"))
            except (json.JSONDecodeError, ValueError):
                continue
            if when < since:
                continue
            text = prompt_text(entry)
            key = (entry.get("sessionId"), text)
            if not text or text in routine_prompts or key in seen:
                continue
            seen.add(key)
            if text.startswith("/"):
                commands[text.split()[0]] += 1
            sessions.add(entry.get("sessionId", path.stem))
            prompts.append({"ts": when.astimezone().strftime("%a %Y-%m-%d %H:%M"),
                            "project": Path(entry.get("cwd") or path.parent.name).name,
                            "session": entry.get("sessionId", path.stem)[:8], "text": text[:600]})
    prompts.sort(key=lambda p: p["ts"][4:])
    return {"days": days, "collected": datetime.now().isoformat(timespec="minutes"),
            "sessions": len(sessions), "prompt_count": len(prompts), "commands": dict(commands.most_common()),
            "existing": existing(), "prompts": prompts[-1500:]}


def main(argv):
    days = int(argv[argv.index("--days") + 1]) if "--days" in argv else 7
    data = collect(days)
    OUT.write_text(json.dumps(data, indent=1), encoding="utf-8")
    print(f"{data['prompt_count']} prompts from {data['sessions']} sessions in the last {days} days "
          f"-> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
