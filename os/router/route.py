#!/usr/bin/env python3
"""Pick the right model and effort for a prompt (ARMS S2, model routing).

  python3 os/router/route.py "your prompt"     prints "<model> <effort>"
  python3 os/router/route.py --json "prompt"   prints the full pick as JSON
  python3 os/router/route.py on | off | status  turns routing on or off
  python3 os/router/route.py stats              summarises the log
  python3 os/router/route.py --test             one real call to check the key and API

Order of decisions:
  1. A prompt that starts with /skill uses the model pinned in that skill's
     SKILL.md (`model:` in the frontmatter). Free and instant.
  2. Otherwise the provider in config.json picks the model and effort:
     "openai": a small OpenAI model (OPENAI_API_KEY, pay-as-you-go API billing)
     "jev":    Jev from TypeSafe via OpenRouter's decisions API (OPENROUTER_API_KEY)
  3. Routing off, no key, or any error: the defaults in config.json.

Keys are read from the environment, then the repo's .env file, then
~/.config/openai/key or ~/.config/openrouter/key. They are never printed.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CONFIG = HERE / "config.json"
LOG = HERE / "log.jsonl"
SKILLS = ROOT / ".claude" / "skills"


def load_config():
    return json.loads(CONFIG.read_text())


def save_config(cfg):
    CONFIG.write_text(json.dumps(cfg, indent=2) + "\n")


KEYS = {"openai": ("OPENAI_API_KEY", "openai"), "jev": ("OPENROUTER_API_KEY", "openrouter")}


def api_key(provider):
    var, folder = KEYS[provider]
    key = os.environ.get(var, "").strip()
    if key:
        return key
    env = ROOT / ".env"
    if env.is_file():
        for line in env.read_text().splitlines():
            if line.strip().startswith(var + "="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                if key:
                    return key
    keyfile = Path.home() / ".config" / folder / "key"
    if keyfile.is_file():
        return keyfile.read_text().strip()
    return ""


def post_json(url, body, key, timeout):
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def check_pick(model, effort, cfg):
    if model not in cfg["models"]:
        raise ValueError(f"router returned an unknown model: {model}")
    if effort not in cfg["efforts"]:
        raise ValueError(f"router returned an unknown effort: {effort}")


def ask_openai(prompt, cfg, key):
    oc = cfg["openai"]
    options = "\n".join(f"- {name}: {desc}" for name, desc in cfg["models"].items())
    system = (
        "You route prompts for Claude Code, an AI work assistant. Pick the smallest model that will do "
        "the prompt well, and how much reasoning effort it needs.\nModels:\n" + options +
        "\nEfforts: " + ", ".join(cfg["efforts"]) +
        '\nReply with JSON only: {"model": "<model>", "effort": "<effort>"}'
    )
    body = {
        "model": oc["model"],
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt[:12000]}],
        "response_format": {"type": "json_object"},
        **oc.get("extra", {}),
    }
    data = post_json(oc["endpoint"], body, key, cfg["timeout_seconds"])
    pick = json.loads(data["choices"][0]["message"]["content"])
    model, effort = pick.get("model"), pick.get("effort")
    check_pick(model, effort, cfg)
    usage = data.get("usage") or {}
    cost = (usage.get("prompt_tokens", 0) * oc.get("usd_per_million_input", 0)
            + usage.get("completion_tokens", 0) * oc.get("usd_per_million_output", 0)) / 1_000_000
    return {"model": model, "effort": effort, "cost": round(cost, 8)}


def pinned(prompt, cfg):
    """Model and effort pinned in a skill's frontmatter, if the prompt calls one."""
    m = re.match(r"\s*/([a-z0-9][a-z0-9-]*)", prompt)
    if not m:
        return None
    skill = SKILLS / m.group(1) / "SKILL.md"
    if not skill.is_file():
        return None
    text = skill.read_text()
    front = text.split("---", 2)[1] if text.startswith("---") else ""
    model = re.search(r"^model:\s*(\S+)", front, re.M)
    if not model or model.group(1) not in cfg["models"]:
        return None
    effort = re.search(r"^effort:\s*(\S+)", front, re.M)
    return {"model": model.group(1), "effort": effort.group(1) if effort else "low", "skill": m.group(1)}


def ask_jev(prompt, cfg, key):
    body = {
        "model": cfg["jev"]["model"],
        "state": ["A user prompt for Claude Code, an AI coding and work assistant:", prompt[:12000]],
        "questions": {
            "model": {
                "type": "choice",
                "instructions": "Which is the smallest model that will do this prompt well?",
                "criteria": cfg["models"],
            },
            "effort": {
                "type": "score",
                "instructions": "How much reasoning effort does this prompt need?",
                "criteria": [
                    "Low: quick and direct, little thinking needed",
                    "Medium: some planning or checking needed",
                    "High: careful step-by-step reasoning needed",
                ],
            },
        },
    }
    data = post_json(cfg["jev"]["endpoint"], body, key, cfg["timeout_seconds"])
    answers = data["answers"]
    efforts = cfg["efforts"]
    idx = min(len(efforts) - 1, max(0, round(float(answers["effort"]["score"]))))
    model, effort = answers["model"]["choice"], efforts[idx]
    check_pick(model, effort, cfg)
    return {
        "model": model,
        "effort": effort,
        "confidence": answers["model"].get("confidence"),
        "cost": (data.get("usage") or {}).get("cost", 0),
    }


def route(prompt):
    cfg = load_config()
    started = time.monotonic()
    pick = {"model": cfg["default_model"], "effort": cfg["default_effort"], "source": "default", "cost": 0}
    pin = pinned(prompt, cfg)
    if pin:
        pick.update(pin, source="pinned")
    elif not cfg.get("enabled", True):
        pick["source"] = "off"
    else:
        provider = cfg.get("provider", "openai")
        key = api_key(provider)
        if not key:
            pick["source"] = "no-key"
        else:
            ask = ask_openai if provider == "openai" else ask_jev
            try:
                pick.update(ask(prompt, cfg, key), source=provider)
            except (urllib.error.URLError, TimeoutError, KeyError, IndexError, ValueError, TypeError) as e:
                pick.update(source="error", error=type(e).__name__ + ": " + str(e)[:200])
    pick["ms"] = round((time.monotonic() - started) * 1000)
    if cfg.get("log", True):
        entry = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "chars": len(prompt), **pick}
        with open(LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
    return pick


def stats():
    if not LOG.is_file():
        return {"calls": 0}
    rows = [json.loads(l) for l in LOG.read_text().splitlines() if l.strip()]
    jev = [r for r in rows if r.get("source") in KEYS]
    by_model = {}
    for r in rows:
        by_model[r["model"]] = by_model.get(r["model"], 0) + 1
    return {
        "calls": len(rows),
        "router_calls": len(jev),
        "avg_router_ms": round(sum(r["ms"] for r in jev) / len(jev)) if jev else None,
        "total_cost_usd": round(sum(r.get("cost") or 0 for r in rows), 6),
        "by_model": by_model,
        "by_source": {s: sum(1 for r in rows if r.get("source") == s) for s in sorted({r.get("source") for r in rows})},
    }


def main(argv):
    if not argv:
        print(__doc__.strip())
        return 1
    cmd = argv[0]
    if cmd in ("on", "off"):
        cfg = load_config()
        cfg["enabled"] = cmd == "on"
        save_config(cfg)
        print(f"Routing is {cmd}.")
        return 0
    if cmd == "status":
        cfg = load_config()
        provider = cfg.get("provider", "openai")
        print(f"Routing is {'on' if cfg.get('enabled', True) else 'off'}; provider {provider}; "
              f"key {'found' if api_key(provider) else 'not found'}.")
        return 0
    if cmd == "stats":
        print(json.dumps(stats(), indent=2))
        return 0
    if cmd == "--test":
        pick = route("Fix the spelling in this sentence: Teh data is redy.")
        print(json.dumps(pick, indent=2))
        return 0 if pick["source"] in KEYS else 2
    as_json = cmd == "--json"
    prompt = " ".join(argv[1:] if as_json else argv)
    pick = route(prompt)
    print(json.dumps(pick) if as_json else f"{pick['model']} {pick['effort']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
