#!/usr/bin/env python3
"""How often a cold prompt cache made Issam pay to reload a chat (ARMS M2).

  python3 os/memory/cache.py              last 30 days: cold reloads, what they cost, what keeping warm would save
  python3 os/memory/cache.py --days 60    a different window
  python3 os/memory/cache.py --json       the same numbers as JSON
  python3 os/memory/cache.py --save       also write the report to os/reports/cache-<date>.md

Claude Code caches each chat for an hour. After an hour idle the cache is cold, and the next
message writes the whole chat to the cache again (2x the input price) instead of reading it
(0.05x to 0.1x). This reads the local transcripts (~/.claude/projects/*/*.jsonl), finds each
reload after an idle gap, and works out what a ping every `ping_every_minutes` for up to
`warm_for_hours` (os/memory/config.json) would have cost and saved. Prices are API list
prices from os/memory/prices.json; on the Claude plan they stand for usage, not money.
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
TRANSCRIPTS = Path.home() / ".claude" / "projects"
HEADLESS = ("sdk-cli", "sdk-py", "sdk-ts")
MIN_RELOAD_TOKENS = 20_000  # smaller writes are normal growth, not a reload
PING_TOKENS = {"write": 60, "output": 10}  # the ping's own prompt and its one-word reply


def load(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def price(prices, model):
    models = prices["models"]
    if model in models:
        return models[model]
    for key in sorted(models, key=len, reverse=True):  # e.g. a dated id that starts with a known one
        if model and model.startswith(key):
            return models[key]
    return models[prices["fallback_model"]]


def sessions(since):
    """Yield (path, messages) per interactive session; each message is one API reply with its usage."""
    for path in TRANSCRIPTS.glob("*/*.jsonl"):
        try:
            if datetime.fromtimestamp(path.stat().st_mtime, timezone.utc) < since:
                continue
            lines = path.read_text(errors="replace", encoding="utf-8").splitlines()
        except OSError:
            continue
        msgs, seen, headless, cwd = [], set(), False, None
        for line in lines:
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("entrypoint") in HEADLESS:
                headless = True
                break
            cwd = e.get("cwd") or cwd
            if e.get("type") != "assistant" or e.get("isSidechain"):
                continue
            m = e.get("message") or {}
            u = m.get("usage")
            if not u or m.get("id") in seen:  # one reply can span several transcript lines
                continue
            seen.add(m.get("id"))
            try:
                ts = datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00"))
            except (KeyError, ValueError):
                continue
            cc = u.get("cache_creation") or {}
            msgs.append({"ts": ts, "model": m.get("model", ""), "write": u.get("cache_creation_input_tokens") or 0,
                         "read": u.get("cache_read_input_tokens") or 0, "input": u.get("input_tokens") or 0,
                         "ttl": "5m" if cc.get("ephemeral_5m_input_tokens") and not cc.get("ephemeral_1h_input_tokens") else "1h",
                         "session": e.get("sessionId", path.stem)})
        if msgs and not headless:
            msgs.sort(key=lambda x: x["ts"])
            yield path, cwd, msgs


def context_tokens(msg):
    return msg["input"] + msg["write"] + msg["read"]


def analyse(days):
    prices, cfg = load("prices.json"), load("config.json")
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=days)
    every = timedelta(minutes=cfg["ping_every_minutes"])
    window = timedelta(hours=cfg["warm_for_hours"])
    max_pings = int(window / every)
    reloads, ping_cost, pings, saved, chats = [], 0.0, 0, 0.0, 0
    for _path, _cwd, msgs in sessions(since):
        msgs = [m for m in msgs if m["ts"] >= since]
        if not msgs:
            continue
        chats += 1
        for prev, cur in zip(msgs, msgs[1:] + [None]):
            ttl = timedelta(hours=1) if prev["ttl"] == "1h" else timedelta(minutes=5)
            gap = (cur["ts"] if cur else now) - prev["ts"]
            p = price(prices, prev["model"])
            ctx = context_tokens(prev)
            # Pings this idle gap would have sent (the tail after a chat's last message counts too).
            if ctx >= cfg["min_context_tokens"] and gap > every:
                n = min(int(gap / every), max_pings)
                pings += n
                ping_cost += n * (ctx * p["cache_read"] + PING_TOKENS["write"] * p["input"] * prices["write_multiplier"]["1h"]
                                  + PING_TOKENS["output"] * p["output"]) / 1e6
            if not cur or gap <= ttl or cur["write"] < MIN_RELOAD_TOKENS:
                continue
            pc = price(prices, cur["model"])
            mult = prices["write_multiplier"][cur["ttl"]]
            paid = cur["write"] * pc["input"] * mult / 1e6
            warm = cur["write"] * pc["cache_read"] / 1e6
            covered = ctx >= cfg["min_context_tokens"] and gap <= max_pings * every + ttl
            if covered:
                saved += paid - warm
            reloads.append({"when": cur["ts"].astimezone().strftime("%Y-%m-%d %H:%M"), "session": cur["session"][:8],
                             "model": cur["model"], "idle_hours": round(gap.total_seconds() / 3600, 1),
                             "tokens": cur["write"], "paid": round(paid, 4), "extra": round(paid - warm, 4),
                             "keep_warm_covers": covered})
    reloads.sort(key=lambda r: -r["extra"])
    return {"days": days, "chats": chats, "reloads": len(reloads),
            "reload_tokens": sum(r["tokens"] for r in reloads),
            "reload_extra_usd": round(sum(r["extra"] for r in reloads), 2),
            "keep_warm": {"every_minutes": cfg["ping_every_minutes"], "hours": cfg["warm_for_hours"],
                          "pings": pings, "ping_cost_usd": round(ping_cost, 2), "saved_usd": round(saved, 2),
                          "net_usd": round(saved - ping_cost, 2), "pays": saved - ping_cost > 0,
                          "on": cfg["keep_warm"]},
            "top": reloads[:10]}


def report(d):
    kw = d["keep_warm"]
    lines = [f"# Cache report, last {d['days']} days", "",
             f"{d['chats']} chats. {d['reloads']} times a cold cache made the next message reload the chat: "
             f"{d['reload_tokens']:,} tokens, ${d['reload_extra_usd']:.2f} more than a warm cache at API prices.", "",
             f"Keeping idle chats warm (a ping every {kw['every_minutes']} minutes, up to {kw['hours']} hours):",
             f"- {kw['pings']} pings, costing ${kw['ping_cost_usd']:.2f}",
             f"- reloads avoided worth ${kw['saved_usd']:.2f}",
             f"- net: ${kw['net_usd']:.2f}. " + ("It pays. Turn it on with `python3 os/memory/keepwarm.py on`."
                                                  if kw["pays"] else "It does not pay; leave it off."),
             "", "Biggest reloads:", "",
             "| When | Model | Idle | Tokens | Extra | Ping covers it |", "|---|---|---|---|---|---|"]
    lines += [f"| {r['when']} | {r['model']} | {r['idle_hours']} h | {r['tokens']:,} | ${r['extra']:.2f} | "
              f"{'yes' if r['keep_warm_covers'] else 'no'} |" for r in d["top"]]
    if not d["top"]:
        lines.append("| none | | | | | |")
    lines += ["", "Prices: os/memory/prices.json (API list prices; on the Claude plan they stand for usage)."]
    return "\n".join(lines) + "\n"


def main(argv):
    days = int(argv[argv.index("--days") + 1]) if "--days" in argv else 30
    d = analyse(days)
    if "--json" in argv:
        print(json.dumps(d))
        return 0
    text = report(d)
    print(text)
    if "--save" in argv:
        out = ROOT / "os" / "reports" / f"cache-{datetime.now():%Y-%m-%d}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"Saved to {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
