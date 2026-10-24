---
name: routines-review
description: Sort Issam's scheduled routines into active and passive, turn the ones that don't need review every run into passive ones, and suggest new passive routines. Use for a routines check-up.
model: sonnet
---

# /routines-review

ARMS R1. Most routines should only speak up when something is worth flagging.

1. Run `python3 os/routines/run.py list` and read `os/routines/routines.json`.
2. Sort every routine:
   - **active**: hands Issam an output to review every run (a digest, a report Issam reads).
   - **passive**: runs quietly and only reaches the inbox when it finds something worth flagging.
3. For each active routine whose output Issam doesn't need every time, propose it as passive and write the flag rule: exactly what counts as worth flagging.
4. Suggest 3 new passive routines for youlytics (SAP analytics consultancy, moving into apps and AI tools), each with name, schedule, flag rule, tools and a weekly cap. Good shapes: a watch (brand, competitor, client news), a scout (domains, tenders, SAP release notes), machine care.
5. Show it all as one short table and change nothing until Issam picks. Then edit `routines.json` for the picks only, and run each new routine once with `run.py run <id>` to check it.
