#!/usr/bin/env python3
"""Keep idle Claude Code chats warm with a tiny ping (ARMS M2). Off by default.

  python3 os/memory/keepwarm.py status     on or off, chats it would ping now, recent pings
  python3 os/memory/keepwarm.py on | off   switch it (run cache.py first: only turn it on if it pays)
  python3 os/memory/keepwarm.py tick       ping every chat that is due (the scheduler calls this)
  python3 os/memory/keepwarm.py install    show how to run `tick` every 10 minutes (--write sets it up on a Mac)

A prompt cache belongs to one chat on one model, so the ping resumes that chat on the same
model. It runs as a fork (`--fork-session`) so the chat itself gets no extra message, and the
fork's transcript is deleted after the ping. A chat is pinged when it has been idle for
`ping_every_minutes`, for up to `warm_for_hours`, and only if it holds at least
`min_context_tokens`. Each ping is checked: if it had to write the chat to the cache instead
of reading it, the ping missed, so that chat is not pinged again and the miss is logged.
"""
import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cache  # noqa: E402

HERE = cache.HERE
CONFIG = HERE / "config.json"
STATE = HERE / "keepwarm-state.json"
PINGS = HERE / "pings.jsonl"


def read_state():
    try:
        return json.loads(STATE.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def due(cfg, now):
    """Chats idle long enough to ping, and not pinged within the interval."""
    every = timedelta(minutes=cfg["ping_every_minutes"])
    window = timedelta(hours=cfg["warm_for_hours"])
    state = read_state()
    out = []
    for path, cwd, msgs in cache.sessions(now - window - every):
        last = msgs[-1]
        sid = path.stem
        idle = now - last["ts"]
        s = state.get(sid, {})
        last_ping = datetime.fromisoformat(s["last_ping"]) if s.get("last_ping") else None
        since = now - max(last["ts"], last_ping) if last_ping else idle
        if (cache.context_tokens(last) >= cfg["min_context_tokens"] and every <= idle <= window
                and since >= every - timedelta(minutes=5) and not s.get("missed") and cwd):
            out.append({"session": sid, "path": path, "cwd": cwd, "model": last["model"],
                        "context": cache.context_tokens(last), "idle_minutes": int(idle.total_seconds() // 60)})
    return out


def ping(chat, cfg):
    cmd = [shutil.which("claude") or "claude", "-p", cfg["ping_prompt"], "--resume", chat["session"], "--fork-session",
           "--model", chat["model"], "--output-format", "json", "--max-turns", "1"]
    try:
        out = subprocess.run(cmd, cwd=chat["cwd"], capture_output=True, text=True, timeout=120,
                             stdin=subprocess.DEVNULL, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        data = json.loads(out.stdout)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"[:200]}
    fork = data.get("session_id")
    if fork and fork != chat["session"]:  # drop the fork's transcript; the original chat is untouched
        try:
            (chat["path"].parent / f"{fork}.jsonl").unlink()
        except OSError:
            pass
    u = data.get("usage") or {}
    read, write = u.get("cache_read_input_tokens") or 0, u.get("cache_creation_input_tokens") or 0
    return {"ok": not data.get("is_error"), "read": read, "write": write,
            "cost": data.get("total_cost_usd", 0), "missed": write > read}


def tick():
    cfg = json.loads(CONFIG.read_text())
    if not cfg.get("keep_warm"):
        return []
    now = datetime.now(timezone.utc)
    state, results = read_state(), []
    for chat in due(cfg, now):
        r = ping(chat, cfg)
        s = state.setdefault(chat["session"], {})
        s["last_ping"] = now.isoformat()
        if r.get("missed"):
            s["missed"] = True  # the ping wrote instead of read: pinging this chat only costs
        row = {"ts": now.astimezone().isoformat(timespec="seconds"), "session": chat["session"][:8],
               "model": chat["model"], "idle_minutes": chat["idle_minutes"], **r}
        with open(PINGS, "a") as f:
            f.write(json.dumps(row) + "\n")
        results.append(row)
    STATE.write_text(json.dumps(state, indent=2))
    return results


def main(argv):
    cmd = argv[0] if argv else "status"
    cfg = json.loads(CONFIG.read_text())
    if cmd in ("on", "off"):
        cfg["keep_warm"] = cmd == "on"
        CONFIG.write_text(json.dumps(cfg, indent=2) + "\n")
        print(f"Keep-warm is {cmd}." + (" Schedule `tick` with: python3 os/memory/keepwarm.py install" if cmd == "on" else ""))
        return 0
    if cmd == "tick":
        for row in tick():
            print(json.dumps(row))
        return 0
    if cmd == "status":
        print(f"Keep-warm is {'on' if cfg.get('keep_warm') else 'off'}: a ping every {cfg['ping_every_minutes']} min "
              f"for up to {cfg['warm_for_hours']} h, chats of {cfg['min_context_tokens']:,}+ tokens.")
        for c in due(cfg, datetime.now(timezone.utc)):
            print(f"  due: {c['session'][:8]} {c['model']} idle {c['idle_minutes']} min, {c['context']:,} tokens")
        rows = PINGS.read_text().splitlines()[-5:] if PINGS.is_file() else []
        for line in rows:
            r = json.loads(line)
            print(f"  pinged {r['ts']} {r['session']} " + ("missed the cache" if r.get("missed") else
                                                          f"read {r.get('read', 0):,} tokens, ${r.get('cost', 0):.4f}"))
        return 0
    if cmd == "install":
        sys.path.insert(0, str(HERE.parent / "routines"))
        import schedule
        return schedule.install("com.youlytics.keepwarm", Path(__file__).resolve(), "tick", 10,
                                HERE / "keepwarm.log", "--write" in argv)
    print(__doc__.strip())
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
