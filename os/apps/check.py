#!/usr/bin/env python3
"""Check that each connected app still answers (ARMS A1).

  python3 os/apps/check.py          run every app's test (one real read) and show the result
  python3 os/apps/check.py github   only one app
  python3 os/apps/check.py --json   the same as JSON (the dashboard uses this)

Apps live in os/apps/apps.json, added by /connect. A test is one short read-only command.
Keys come from the repo's .env (gitignored) and are passed to the test, never printed.
Apps reached through a Claude connector or MCP have no shell test; their `test_in_claude`
prompt is the check to run inside Claude Code.
"""
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def env_with_keys():
    env = dict(os.environ)
    f = ROOT / ".env"
    if f.is_file():
        for line in f.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                env.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    return env


def check(app, env):
    if app.get("key_env") and not env.get(app["key_env"]):
        return {"id": app["id"], "ok": False, "detail": f"{app['key_env']} is not in .env"}
    if not app.get("test"):
        return {"id": app["id"], "ok": None, "detail": "check inside Claude Code: " + (app.get("test_in_claude") or "-")}
    try:
        out = subprocess.run(shlex.split(app["test"]), cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
        ok = out.returncode == 0
        detail = (out.stdout if ok else out.stderr or out.stdout).strip().splitlines()
        return {"id": app["id"], "ok": ok, "detail": (detail[0] if detail else "")[:160]}
    except FileNotFoundError:
        return {"id": app["id"], "ok": False, "detail": f"{shlex.split(app['test'])[0]} is not installed"}
    except subprocess.TimeoutExpired:
        return {"id": app["id"], "ok": False, "detail": "no answer within 60 s"}


def main(argv):
    apps = json.loads((HERE / "apps.json").read_text(encoding="utf-8"))["apps"]
    only = [a for a in argv if not a.startswith("--")]
    env = env_with_keys()
    rows = [{**check(a, env), "name": a["name"], "way_in": a["way_in"]} for a in apps if not only or a["id"] in only]
    if "--json" in argv:
        print(json.dumps(rows))
        return 0
    for r in rows:
        mark = {True: "ok  ", False: "FAIL", None: "--  "}[r["ok"]]
        print(f"{mark} {r['name']:<14} {r['way_in']:<10} {r['detail']}")
    return 0 if all(r["ok"] is not False for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
