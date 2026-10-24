#!/usr/bin/env python3
"""youlytics status line for Claude Code (ARMS A2, a mod that costs no tokens).

Shows: model and effort · context used · 5-hour and 7-day limits · prompt cache warm or cold,
with minutes left and what a cold reload would cost · session cost · git branch.
Claude Code passes the session as JSON on stdin; .claude/settings.json runs this every 30 s.
"""
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

AMBER, RUBY, DIM, RESET = "\033[38;2;217;150;43m", "\033[38;2;224;122;140m", "\033[2m", "\033[0m"


def last_reply_age(transcript):
    """Seconds since the last assistant reply, read from the end of the transcript."""
    try:
        with open(transcript, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 200_000))
            lines = f.read().decode(errors="replace").splitlines()
        for line in reversed(lines):
            if '"assistant"' in line:
                ts = json.loads(line).get("timestamp")
                if ts:
                    return time.time() - datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except (OSError, ValueError):
        pass
    return None


def reload_cost(root, model, tokens):
    try:
        prices = json.loads((Path(root) / "os" / "memory" / "prices.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    models = prices["models"]
    p = next((models[k] for k in sorted(models, key=len, reverse=True) if model.startswith(k)),
             models[prices["fallback_model"]])
    return tokens * p["input"] * prices["write_multiplier"]["1h"] / 1e6


def cache_part(d, root):
    pc = d.get("prompt_cache") or {}
    ctx = (d.get("context_window") or {}).get("total_input_tokens") or 0
    tokens = pc.get("recache_tokens_if_cold") or ctx
    if pc.get("expires_at"):
        left = pc["expires_at"] - time.time()
        warm = pc.get("warm", left > 0)
    else:  # older Claude Code: estimate from the last reply and the 1-hour cache
        age = last_reply_age(d.get("transcript_path") or "")
        if age is None:
            return None
        left, warm = 3600 - age, age < 3600
    cost = reload_cost(root, (d.get("model") or {}).get("id", ""), tokens)
    price = f", ${cost:.2f}" if cost else ""
    if not warm or left <= 0:
        return f"{RUBY}cache cold: next message reloads {tokens / 1000:.0f}k{price}{RESET}"
    mins = int(left // 60)
    text = f"cache warm {mins}m"
    return f"{AMBER}{text} (reload {tokens / 1000:.0f}k{price}){RESET}" if mins < 10 else text


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # Windows pipes default to cp1252; Claude Code reads UTF-8
    try:
        d = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace"))
    except json.JSONDecodeError:
        print("youlytics")
        return
    root = (d.get("workspace") or {}).get("project_dir") or d.get("cwd") or "."
    parts = []
    model = (d.get("model") or {}).get("display_name") or "Claude"
    effort = (d.get("effort") or {}).get("level")
    parts.append(f"{model}{' · ' + effort if effort else ''}")
    pct = (d.get("context_window") or {}).get("used_percentage")
    if pct is not None:
        parts.append(f"ctx {pct:.0f}%")
    rl = d.get("rate_limits") or {}
    limits = [f"{label} {rl[k]['used_percentage']:.0f}%" for k, label in (("five_hour", "5h"), ("seven_day", "7d"))
              if (rl.get(k) or {}).get("used_percentage") is not None]
    if limits:
        parts.append(" ".join(limits))
    cache = cache_part(d, root)
    if cache:
        parts.append(cache)
    cost = (d.get("cost") or {}).get("total_cost_usd")
    if cost:
        parts.append(f"${cost:.2f}")
    try:
        branch = subprocess.run(["git", "branch", "--show-current"], cwd=d.get("cwd") or root,
                                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=2).stdout.strip()
        if branch:
            parts.append(f"{DIM}{branch}{RESET}")
    except (OSError, subprocess.SubprocessError):
        pass
    print(" · ".join(parts))


if __name__ == "__main__":
    main()
