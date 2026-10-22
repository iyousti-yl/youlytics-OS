#!/usr/bin/env python3
"""Local dashboard for self-triggered skills, routines and the inbox.

Run from the repo root:  python3 os/server.py   then open http://127.0.0.1:8765
Each button runs one skill in the background with `claude -p` (no chat window).
Only skills listed in os/buttons.json can be run, with the tools listed there.
Routines come from os/routines/routines.json and run through os/routines/run.py.
"""
import json
import subprocess
import sys
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OS_DIR = ROOT / "os"
REPORTS = OS_DIR / "reports"
HOST, PORT = "127.0.0.1", 8765
MODELS = {"haiku", "sonnet", "opus", "codex", "auto"}
EFFORTS = {"low", "medium", "high", "xhigh", "max", "auto"}
ROUTER = OS_DIR / "router"
ROUTINES = OS_DIR / "routines"
INBOX = OS_DIR / "inbox.jsonl"
RECOS = OS_DIR / "recos"
PAGES = {"/recos": RECOS / "index.html"}  # local micro apps, each built from os/ui/
TYPES = {".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".json": "application/json"}

runs = {}  # skill -> {"state", "started", "finished", "model", "effort", "log"}
lock = threading.Lock()


def load_buttons():
    return json.loads((OS_DIR / "buttons.json").read_text())


def routed(prompt):
    """Ask the router (os/router/route.py) for a model and effort."""
    out = subprocess.run([sys.executable, str(ROUTER / "route.py"), "--json", prompt],
                         cwd=ROOT, capture_output=True, text=True, timeout=30)
    pick = json.loads(out.stdout)
    return pick["model"], pick["effort"], pick["source"]


def run_skill(skill, cfg, model, effort):
    REPORTS.mkdir(exist_ok=True)
    if model == "auto" or effort == "auto":
        r_model, r_effort, source = routed(cfg["prompt"])
        model = r_model if model == "auto" else model
        effort = r_effort if effort == "auto" else effort
        with lock:
            runs[skill].update(model=model, effort=effort, routed=source)
    stamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    log = REPORTS / f"{skill}-{stamp}.log"
    if model == "codex":  # Codex CLI on the ChatGPT plan, allowed to write only inside this workspace
        cmd = ["codex", "exec", "-c", f"model_reasoning_effort={effort}", "--sandbox", "workspace-write", cfg["prompt"]]
    else:
        cmd = ["claude", "-p", cfg["prompt"], "--model", model, "--effort", effort,
               "--allowedTools", *cfg.get("allowed_tools", [])]
    started = time.time()
    with open(log, "w") as out:
        try:
            code = subprocess.run(cmd, cwd=ROOT, stdout=out, stderr=subprocess.STDOUT, timeout=1800).returncode
        except FileNotFoundError:
            out.write(f"The {cmd[0]} command wasn't found. Install it and try again.\n")
            code = 127
        except subprocess.TimeoutExpired:
            out.write("Stopped after 30 minutes.\n")
            code = 124
    with lock:
        runs[skill].update(state="done" if code == 0 else "failed", finished=time.time(),
                           seconds=round(time.time() - started), log=log.name)


_skills_cache = {"at": 0, "data": {}}


def skill_usage():
    """Skill runs and tokens from os/skills/usage.py, refreshed at most once a minute."""
    if time.time() - _skills_cache["at"] > 60:
        out = subprocess.run([sys.executable, str(OS_DIR / "skills" / "usage.py"), "--json"],
                             cwd=ROOT, capture_output=True, text=True)
        try:
            _skills_cache.update(at=time.time(), data=json.loads(out.stdout))
        except json.JSONDecodeError:
            _skills_cache.update(at=time.time(), data={})
    return _skills_cache["data"]


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


routine_runs = {}  # routine id -> "running" while the dashboard runs it


def routines_state():
    """Each routine with its week cost against its cap and its last run."""
    out = subprocess.run([sys.executable, str(ROUTINES / "run.py"), "costs", "--json"],
                         cwd=ROOT, capture_output=True, text=True)
    try:
        rows = json.loads(out.stdout)
    except json.JSONDecodeError:
        return []
    config = {r["id"]: r for r in json.loads((ROUTINES / "routines.json").read_text())["routines"]}
    last = {}
    for run in read_jsonl(ROUTINES / "runs.jsonl"):
        last[run["id"]] = run
    for row in rows:
        row["last"] = last.get(row["id"])
        row["setup_note"] = config.get(row["id"], {}).get("setup_note")
        row["running"] = routine_runs.get(row["id"]) == "running"
    return rows


def run_routine(rid):
    subprocess.run([sys.executable, str(ROUTINES / "run.py"), "run", rid], cwd=ROOT, capture_output=True)
    with lock:
        routine_runs.pop(rid, None)


def inbox(limit=30):
    rows = read_jsonl(INBOX)
    rows.reverse()
    return {"unread": sum(1 for r in rows if not r.get("read")), "items": rows[:limit]}


def mark_read(key):
    """Mark one inbox item (by its ts and id) or all items (key None) as read."""
    rows = read_jsonl(INBOX)
    for r in rows:
        if key is None or (r.get("ts"), r.get("id")) == key:
            r["read"] = True
    INBOX.write_text("".join(json.dumps(r) + "\n" for r in rows))


_cache_cache = {"at": 0, "data": {}}


def cache_report():
    """Cold-cache numbers from os/memory/cache.py, refreshed at most every 10 minutes."""
    if time.time() - _cache_cache["at"] > 600:
        out = subprocess.run([sys.executable, str(OS_DIR / "memory" / "cache.py"), "--json"],
                             cwd=ROOT, capture_output=True, text=True)
        try:
            _cache_cache.update(at=time.time(), data=json.loads(out.stdout))
        except json.JSONDecodeError:
            _cache_cache.update(at=time.time(), data={})
    return _cache_cache["data"]


_apps_cache = {"at": 0, "data": []}


def apps_state():
    """Each app from os/apps/apps.json with its last check, refreshed at most every 10 minutes."""
    if time.time() - _apps_cache["at"] > 600:
        out = subprocess.run([sys.executable, str(OS_DIR / "apps" / "check.py"), "--json"],
                             cwd=ROOT, capture_output=True, text=True)
        try:
            _apps_cache.update(at=time.time(), data=json.loads(out.stdout))
        except json.JSONDecodeError:
            _apps_cache.update(at=time.time(), data=[])
    return _apps_cache["data"]


def latest_reports(limit=10):
    files = sorted(REPORTS.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    return [{"name": p.name, "modified": datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")} for p in files]


POSTS = ("/api/run", "/api/router", "/api/routines/run", "/api/inbox/read")


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _same_origin(self):
        origin = self.headers.get("Origin")
        return origin in (None, f"http://{HOST}:{PORT}", f"http://localhost:{PORT}")

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self._send(200, (OS_DIR / "dashboard.html").read_bytes(), "text/html; charset=utf-8")
        if self.path == "/api/state":
            with lock:
                state = {k: dict(v) for k, v in runs.items()}
            buttons = {k: {kk: v[kk] for kk in ("label", "default_model", "default_effort")} for k, v in load_buttons().items()}
            router = json.loads((ROUTER / "config.json").read_text())
            stats = json.loads(subprocess.run([sys.executable, str(ROUTER / "route.py"), "stats"],
                                              cwd=ROOT, capture_output=True, text=True).stdout or "{}")
            return self._send(200, {"buttons": buttons, "runs": state, "reports": latest_reports(),
                                    "router": {"enabled": router.get("enabled", True), "stats": stats},
                                    "skills": skill_usage(), "routines": routines_state(),
                                    "inbox": inbox(), "cache": cache_report(), "apps": apps_state()})
        path, _, query = self.path.partition("?")
        if path in PAGES:
            return self._send(200, PAGES[path].read_bytes(), TYPES[".html"])
        if path.startswith("/ui/"):
            f = OS_DIR / "ui" / Path(path).name
            if f.suffix in TYPES and f.is_file():
                return self._send(200, f.read_bytes(), TYPES[f.suffix])
        if path == "/api/recos":
            f = RECOS / ("recos.example.json" if query == "example" else "recos.json")
            return self._send(200, f.read_bytes() if f.is_file() else b"{}")
        if self.path.startswith("/reports/"):
            rel = self.path[len("/reports/"):]
            sub = REPORTS / "routines" if rel.startswith("routines/") else REPORTS
            f = sub / Path(rel).name
            if f.suffix in (".md", ".log") and f.is_file():
                return self._send(200, f.read_bytes(), "text/plain; charset=utf-8")
        self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path not in POSTS or not self._same_origin():
            return self._send(403, {"error": "not allowed"})
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except json.JSONDecodeError:
            return self._send(400, {"error": "bad request"})
        if self.path == "/api/router":
            subprocess.run([sys.executable, str(ROUTER / "route.py"), "on" if req.get("enabled") else "off"],
                           cwd=ROOT, capture_output=True)
            return self._send(200, {"ok": True})
        if self.path == "/api/routines/run":
            ids = {r["id"] for r in json.loads((ROUTINES / "routines.json").read_text())["routines"]}
            rid = req.get("id")
            if rid not in ids:
                return self._send(400, {"error": "unknown routine"})
            with lock:
                if routine_runs.get(rid) == "running":
                    return self._send(409, {"error": "already running"})
                routine_runs[rid] = "running"
            threading.Thread(target=run_routine, args=(rid,), daemon=True).start()
            return self._send(202, {"ok": True})
        if self.path == "/api/inbox/read":
            with lock:
                mark_read(None if req.get("all") else (req.get("ts"), req.get("id")))
            return self._send(200, {"ok": True})
        buttons = load_buttons()
        skill, model, effort = req.get("skill"), req.get("model"), req.get("effort")
        if skill not in buttons or model not in MODELS or effort not in EFFORTS:
            return self._send(400, {"error": "unknown skill, model or effort"})
        with lock:
            if runs.get(skill, {}).get("state") == "running":
                return self._send(409, {"error": "already running"})
            runs[skill] = {"state": "running", "started": time.time(), "model": model, "effort": effort}
        threading.Thread(target=run_skill, args=(skill, buttons[skill], model, effort), daemon=True).start()
        self._send(202, {"ok": True})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print(f"Dashboard on http://{HOST}:{PORT}  (Ctrl+C to stop)")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
