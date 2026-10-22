---
name: suggest-routines
description: Read the past week of Issam's sessions, find jobs done by hand 3 or more times, and write suggestion cards (routines, skills, memory fixes) to the recos page. Runs every Friday as a routine; also on request.
model: sonnet
effort: medium
---

# /suggest-routines

ARMS R3 (routines that suggest routines) and the memory section of M3. Change nothing except `os/recos/recos.json`.

1. Run `python3 os/recos/collect.py`, then read `os/recos/week-prompts.json`. It has Issam's typed prompts from the last 7 days, the slash commands used, and the routines and skills that already exist.
2. Find **jobs done by hand 3 or more times**: the same kind of request on different days or in different sessions, even when worded differently (e.g. "check the SAP release notes", "anything new in BW/4HANA?"). Ignore one-off work and anything an existing routine or skill already does.
3. Write one card per job, at most 8 cards, best first:
   - `routine` when it can run unattended on a schedule. Say passive or active, the flag rule if passive, the schedule, the tools it needs and a weekly cap (start at $1; haiku and low effort for fixed steps).
   - `skill` when Issam starts it by hand but the steps repeat.
   - `memory` when Issam corrected Claude on the same thing twice or more, or re-explained the same context: what to save and where (`memory/`, a router file, or a skill).
4. Each card is short: what it does, when, what it saves (minutes a week, or usage), and the evidence (how many times, which days, one example quote of 12 words or fewer).
5. Write `os/recos/recos.json` in exactly this shape (replace the whole file):

```json
{
  "week": "2026-W43",
  "made": "2026-10-23 08:00",
  "summary": "One line on the week: prompts read and what stood out.",
  "cards": [
    {
      "id": "short-kebab-id",
      "section": "routine",
      "title": "SAP release-note watch",
      "what": "Checks SAP's BW/4HANA and Datasphere notes every Monday and flags anything that affects a client.",
      "when": "weekly mon 08:00",
      "saves": "About 30 minutes a week",
      "evidence": "4 times (Mon, Tue, Thu, Fri): \"anything new in datasphere this week?\"",
      "mode": "passive",
      "cap_usd_week": 1.0,
      "setup": "Add a passive routine 'sap-release-watch' to os/routines/routines.json: weekly mon 08:00, haiku, low effort, tools Read + WebSearch + WebFetch, cap $1. Flag only notes that change BW/4HANA, Datasphere or SAC behaviour for a client in business/clients/."
    }
  ]
}
```

   `mode` and `cap_usd_week` are for routine cards only. `setup` is the exact instruction Claude needs to set the card up later, written so it works on its own.
6. If nothing qualifies, write the file with an empty `cards` list and say so in `summary`.
7. Reply with one headline line: how many cards, and "Open http://127.0.0.1:8765/recos to pick." Issam picks cards into a cart on that page and pastes the cart back; only then set up the picked ones, one at a time, and run each new routine once to check it.
