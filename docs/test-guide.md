# End-to-end test guide

One pass through all twelve ARMS levels on your own computer. Each step says what to do and when it passes. Plan about an hour; the routine runs cost a few cents of usage each.

## 0. Get the code
The work sits on three stacked pull requests (#2 routing, #3 self-improving skills, and the one for routines, memory and apps). The top branch has all of it:

```sh
cd youlytics-OS
git fetch origin
git checkout arms-routines-memory-apps
```

You need Claude Code signed in to your Claude plan, Python 3.9 or newer, and Chrome for step A2. Open a second terminal for the dashboard:

```sh
python3 os/server.py        # leave it running, then open http://127.0.0.1:8765
```

**Passes when** the dashboard shows Inbox, Routines, Model routing, Apps, Prompt cache, the Clean up button and the Skills table, and the top line links Recos and Review.

## Skills
**S1 Skill types.** In Claude Code in this folder, run `/brand make a one-page summary of youlytics' services`. Then press **Run /clean-up** on the dashboard.
Passes when a new folder appears in `artifacts/` in the Sapphire Steady look and is listed in `artifacts/index.html`, and the clean-up report shows under Latest reports.

**S2 Model routing.** Run `python3 os/router/route.py --test`, then `os/ask "fix the typos in: teh data is redy"`.
Passes when the test prints `"source": "claude"` and `os/ask` opens Claude Code on the model the router picked (a small fix like this should get haiku). `python3 os/router/route.py stats` shows the picks.

**S3 Self-improving skills.** Use `/tone` on a short email, tell Claude what you'd change, then run `/teach`.
Passes when Claude shows one principle and a diff before saving, and after your yes the change is in `.claude/skills/tone/CHANGELOG.md`. The dashboard Skills table counts the runs.

## Routines
**R1 Active vs passive.** On the dashboard, press **Run now** on Machine care.
Passes when the run finishes in under a minute and, only if something is worth flagging, a line appears in the Inbox (otherwise the Last run column says "quiet"). Then run `/routines-review` in Claude Code: it sorts the routines and proposes 3 new passive ones without changing anything.

**R2 Capped routines.** Run `python3 os/routines/run.py costs`, then `/cap-routine`.
Passes when each routine shows its runs, tokens and cost against its cap, and `/cap-routine` shows a before and after estimate for the most expensive one before changing anything.

Schedule them for real: `python3 os/routines/run.py install --write` (Task Scheduler on Windows, launchd on a Mac). On Windows, `schtasks /Query /TN com.youlytics.routines` shows the task. Passes when the next due routine shows a Last run time on its own, with no window popping up.

**R3 Routines that suggest routines.** Press **Run now** on Routine suggestions, then open **Recos**.
Passes when the Inbox gets a "N cards this week" line and Recos shows the cards (with little history it may say there are none; `/recos?example` shows example cards). Add two to the cart, press **Copy for Claude**, paste into Claude Code: Claude sets up only those, one at a time.

## Memory
**M1 Long-term memory.** Ask Claude Code "where would you save notes from a client call with Acme?" without naming a folder.
Passes when it answers from the map (`business/clients/acme/`) without searching the whole workspace.

**M2 Short-term memory.** Run `python3 os/memory/cache.py`.
Passes when it lists your cold-cache reloads of the last 30 days and says whether keeping chats warm would pay. Only if it says it pays: `python3 os/memory/keepwarm.py on` and `python3 os/memory/keepwarm.py install --write`, leave a big chat idle for an hour, then `keepwarm.py status` shows a ping that read the cache. Also check the status line at the bottom of Claude Code: it shows the model, context %, your 5-hour and 7-day limits and "cache warm 59m", counting down.

**M3 Self-evolving memory.** In the middle of a `/tone` job, type `/note tone always sign off with "Kind regards, Issam"`. Later, `/note apply`. Then teach something lasting with `/calibrate` (for example the language you use for invoices).
Passes when the note lands in `.claude/skills/tone/NOTES.md` without derailing the job, the dashboard shows 1 open note, `/note apply` shows a diff and ticks the note after your yes, and `/calibrate` shows the memory file, the `MEMORY.md` line, the links and the skill change before saving anything.

## Apps
**A1 Connect anything.** Run `python3 os/apps/check.py`, then `/connect` an app you use (for example your calendar or SAP Analytics Cloud).
Passes when GitHub says ok, and `/connect` tells you what it picked and why, asks you to put any key in `.env` yourself, tests with one real read and adds the app to the Apps table.

**A2 Mods.** The status line is already on (step M2). For the clipper: open `chrome://extensions`, turn on Developer mode, **Load unpacked** and pick `os/chrome-clipper`. On any article, click the youlytics icon, add a note and save; right-click a selected paragraph and choose **Save selection to youlytics**.
Passes when both clips appear in `knowledge/reading/` with the source link and a line in `knowledge/reading/index.md`.

**A3 Micro app.** Open **Review** on the dashboard. Mark the S1 artifact **Change** with a comment, approve a report, then **Copy review for Claude** and paste it into Claude Code.
Passes when Claude makes the change and shows the diff, your verdicts survive a server restart (stop and start `os/server.py`, reload the page), and reviewed items leave the list. `/ui/gallery.html` shows the parts every app is built from.

**Brain.** Open **Brain** in the top bar. Click `CLAUDE.md`, then follow a link in the side panel; search for `tone`; switch to **List** and move through it with Tab only.
Passes when the side panel shows what the file points to and what points to it, the search fades everything else, and the List view reaches every file without a mouse. `python3 os/brain/graph.py` prints the same numbers as the header.

## When something fails
Tell Claude Code what you saw, or park it with `/note <skill or app> <what went wrong>`. Small fixes go straight in; anything bigger comes back to you as a decision.
