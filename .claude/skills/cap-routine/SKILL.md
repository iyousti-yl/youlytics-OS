---
name: cap-routine
description: Find the routine that costs the most, trim it until it fits a weekly cap, and show the cost before and after. Use when a routine hits its cap or for a monthly cost check.
model: sonnet
---

# /cap-routine

ARMS R2. Every routine costs plan usage or API credits; know what each one costs and cap the expensive ones.

1. Run `python3 os/routines/run.py costs` and read the last runs of each routine in `os/routines/runs.jsonl` (tokens, cost, seconds, model).
2. Rank them, most expensive first, with tokens per week and API-equivalent cost per week.
3. For the top one, cut the fat. In order of usual payoff:
   - a smaller model or lower effort (most routines are fixed-step: haiku, low)
   - a narrower prompt: one job, a clear stopping point, no "and also"
   - fewer tools, and no web fetches it doesn't need
   - a less frequent schedule
   - passive instead of active
4. Ask Issam for the cap if they haven't set one (a typical cap is $4 a week). Show the cost before and after, as an estimate, and what the routine still does.
5. Don't drop anything Issam relies on without asking, and change nothing until Issam says yes. Then edit `os/routines/routines.json` and run the routine once to measure the new cost.
