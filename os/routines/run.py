#!/usr/bin/env python3
"""Routines: tasks Claude runs on a schedule (ARMS R1, R2, R3).

  python3 os/routines/run.py list            every routine, its mode, schedule and weekly cost
  python3 os/routines/run.py run <id>        run one routine now
  python3 os/routines/run.py due             run every routine that is due (the scheduler calls this)
  python3 os/routines/run.py costs           routines ranked by cost over the last 7 days
  python3 os/routines/run.py enable <id>     switch a routine on (disable <id> switches it off)
  python3 os/routines/run.py install         show how to run `due` every 15 minutes (--write sets it up on a Mac)

Routines live in os/routines/routines.json.
- active routines always put their output in the inbox for Issam to review.
- passive routines only reach the inbox when they find something worth flagging.
- every routine has a weekly cap (API-equivalent USD). A run gets only what is left of the
  cap as its budget, and a routine over its cap is skipped with one inbox note.
Each run is logged to os/routines/runs.jsonl with its cost and tokens.
"""
import json
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CONFIG = HERE / "routines.json"
STATE = HERE / "state.json"
RUNS = HERE / "runs.jsonl"
INBOX = ROOT / "os" / "inbox.jsonl"
REPORTS = ROOT / "os" / "reports" / "routines"
ROUTER = ROOT / "os" / "router" / "route.py"
NOTHING = "NOTHING_TO_FLAG"
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

PASSIVE_RULES = (
    "This is a passive routine running unattended. Do the job, then decide whether anything is worth "
    f"Issam's attention. If nothing is, reply with exactly {NOTHING} and nothing else. If something is, "
    "reply with one headline line, then at most five short bullets with what you found and what to do."
)
ACTIVE_RULES = (
    "This is an active routine running unattended. Do the job and reply with one headline line, then "
    "the output for Issam to review. Keep it short and scannable."
)


def load():
    return json.loads(CONFIG.read_text())["routines"]


def save(routines):
    CONFIG.write_text(json.dumps({"routines": routines}, indent=2) + "\n")


def read_json(path, default):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return default


def read_jsonl(path):
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text().splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return rows


def append_jsonl(path, row):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(row) + "\n")


def last_slot(schedule, now):
    """The most recent time at or before `now` that this schedule says to run."""
    parts = schedule.lower().split()
    hh, mm = (int(x) for x in parts[-1].split(":"))
    slot = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if parts[0] == "daily":
        allowed = set(range(7))
    elif parts[0] == "weekdays":
        allowed = set(range(5))
    elif parts[0] == "weekly":
        allowed = {DAYS.index(parts[1][:3])}
    elif parts[0] == "monthly":  # e.g. "monthly 1 08:00": that day of every month
        day = int(parts[1])
        cand = slot.replace(day=day) if day <= 28 else None
        if cand and cand > now:
            prev = (slot.replace(day=1) - timedelta(days=1)).replace(day=day)
            cand = prev
        return cand
    else:
        raise ValueError(f"unknown schedule: {schedule}")
    for back in range(8):
        cand = slot - timedelta(days=back)
        if cand <= now and cand.weekday() in allowed:
            return cand
    return None


def week_cost(rid, now=None):
    since = (now or datetime.now()) - timedelta(days=7)
    return sum(r.get("cost", 0) or 0 for r in read_jsonl(RUNS)
               if r["id"] == rid and datetime.fromisoformat(r["ts"]) >= since)


def notify(title, text):
    """Best-effort desktop notification; the inbox is the record either way."""
    try:
        if platform.system() == "Darwin":
            script = f'display notification {json.dumps(text[:200])} with title {json.dumps(title)}'
            subprocess.run(["osascript", "-e", script], capture_output=True, timeout=10)
        elif shutil.which("notify-send"):
            subprocess.run(["notify-send", title, text[:200]], capture_output=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        pass


def to_inbox(r, headline, file=None, kind="output"):
    append_jsonl(INBOX, {"ts": datetime.now().isoformat(timespec="seconds"), "id": r["id"], "name": r["name"],
                         "mode": r["mode"], "kind": kind, "headline": headline, "file": file, "read": False})
    notify(f"youlytics · {r['name']}", headline)


def pick_model(r):
    model, effort = r.get("model", "auto"), r.get("effort", "auto")
    if "auto" in (model, effort):
        out = subprocess.run([sys.executable, str(ROUTER), "--json", r["prompt"]],
                             cwd=ROOT, capture_output=True, text=True, timeout=60)
        pick = json.loads(out.stdout)
        model = pick["model"] if model == "auto" else model
        effort = pick["effort"] if effort == "auto" else effort
    if model == "codex":  # routines need Claude's skills and budget cap
        model = "sonnet"
    return model, effort


def run(r):
    now = datetime.now()
    spent = week_cost(r["id"], now)
    cap = float(r.get("cap_usd_week", 1.0))
    if spent >= cap:
        state = read_json(STATE, {})
        if state.get(r["id"], {}).get("capped_week") != now.strftime("%G-%V"):
            to_inbox(r, f"Skipped: weekly cap of ${cap:.2f} reached (${spent:.2f} spent). Run /cap-routine to trim it.",
                     kind="cap")
            state.setdefault(r["id"], {})["capped_week"] = now.strftime("%G-%V")
            STATE.write_text(json.dumps(state, indent=2))
        return {"id": r["id"], "skipped": "cap"}

    model, effort = pick_model(r)
    rules = PASSIVE_RULES if r["mode"] == "passive" else ACTIVE_RULES
    cmd = ["claude", "-p", r["prompt"], "--model", model, "--effort", effort,
           "--output-format", "json", "--append-system-prompt", rules,
           "--max-budget-usd", f"{max(cap - spent, 0.01):.2f}",
           "--allowedTools", *r.get("allowed_tools", ["Read", "Glob", "Grep"])]
    started = time.monotonic()
    try:
        out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                             timeout=r.get("timeout_minutes", 20) * 60, stdin=subprocess.DEVNULL)
        data = json.loads(out.stdout)
        result, cost = (data.get("result") or "").strip(), data.get("total_cost_usd", 0) or 0
        usage = data.get("usage") or {}
        tokens = sum(usage.get(k) or 0 for k in ("input_tokens", "cache_creation_input_tokens",
                                                  "cache_read_input_tokens", "output_tokens"))
        ok = not data.get("is_error")
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as e:
        result, cost, tokens, ok = f"The routine could not run: {type(e).__name__}: {e}", 0, 0, False

    flagged = r["mode"] == "active" or not ok or result != NOTHING
    file = None
    if flagged:
        REPORTS.mkdir(parents=True, exist_ok=True)
        path = REPORTS / f"{r['id']}-{now.strftime('%Y-%m-%d-%H%M')}.md"
        path.write_text(f"# {r['name']}\n\n{now:%Y-%m-%d %H:%M} · {model}, {effort} effort · "
                        f"${cost:.4f}\n\n{result}\n")
        file = str(path.relative_to(ROOT))
        to_inbox(r, (result.splitlines() or ["(no output)"])[0][:160], file, "error" if not ok else "output")
    row = {"ts": now.isoformat(timespec="seconds"), "id": r["id"], "mode": r["mode"], "model": model,
           "effort": effort, "ok": ok, "flagged": flagged, "cost": round(cost, 6), "tokens": tokens,
           "seconds": round(time.monotonic() - started), "file": file}
    append_jsonl(RUNS, row)
    state = read_json(STATE, {})
    state.setdefault(r["id"], {})["last_run"] = row["ts"]
    STATE.write_text(json.dumps(state, indent=2))
    return row


def due(now=None):
    now = now or datetime.now()
    state = read_json(STATE, {})
    results = []
    for r in load():
        if not r.get("enabled"):
            continue
        slot = last_slot(r["schedule"], now)
        last = state.get(r["id"], {}).get("last_run")
        if slot and (not last or datetime.fromisoformat(last) < slot) and now - slot < timedelta(hours=12):
            results.append(run(r))
    return results


def costs():
    rows = []
    for r in load():
        runs = [x for x in read_jsonl(RUNS) if x["id"] == r["id"]
                and datetime.fromisoformat(x["ts"]) >= datetime.now() - timedelta(days=7)]
        rows.append({"id": r["id"], "name": r["name"], "mode": r["mode"], "enabled": r.get("enabled", False),
                     "schedule": r["schedule"], "runs": len(runs), "flags": sum(1 for x in runs if x["flagged"]),
                     "tokens": sum(x.get("tokens", 0) for x in runs), "cost": round(sum(x.get("cost", 0) for x in runs), 4),
                     "cap": r.get("cap_usd_week", 1.0)})
    return sorted(rows, key=lambda x: (-x["cost"], -x["tokens"], x["id"]))


def main(argv):
    cmd = argv[0] if argv else "list"
    routines = load()
    by_id = {r["id"]: r for r in routines}
    if cmd in ("list", "costs"):
        rows = costs()
        if "--json" in argv:
            print(json.dumps(rows))
            return 0
        print(f"{'routine':<18}{'mode':<9}{'on':<4}{'schedule':<18}{'runs':>5}{'flags':>6}{'tokens':>12}{'cost':>9}{'cap':>7}")
        for x in rows:
            print(f"{x['id']:<18}{x['mode']:<9}{'yes' if x['enabled'] else 'no':<4}{x['schedule']:<18}{x['runs']:>5}"
                  f"{x['flags']:>6}{x['tokens']:>12,}{'$%.2f' % x['cost']:>9}{'$%.2f' % x['cap']:>7}")
        return 0
    if cmd == "run" and len(argv) > 1 and argv[1] in by_id:
        print(json.dumps(run(by_id[argv[1]]), indent=2))
        return 0
    if cmd == "due":
        for row in due():
            print(json.dumps(row))
        return 0
    if cmd in ("enable", "disable") and len(argv) > 1 and argv[1] in by_id:
        by_id[argv[1]]["enabled"] = cmd == "enable"
        save(routines)
        print(f"{argv[1]} {cmd}d.")
        return 0
    if cmd == "install":
        import schedule
        return schedule.install("com.youlytics.routines", Path(__file__).resolve(), "due", 15,
                                HERE / "cron.log", "--write" in argv)
    print(__doc__.strip())
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
