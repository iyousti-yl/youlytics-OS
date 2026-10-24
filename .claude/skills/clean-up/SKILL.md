---
name: clean-up
description: Check the computer for space hogs and slow apps and write a short report. Runs headless from the dashboard button.
model: haiku
effort: low
---

# /clean-up

Self-triggered skill, run with `claude -p` from `os/server.py`. It reports; it never deletes.

1. Disk: free space on the main disk, then the 10 biggest folders in the home directory (`du -sh ~/* ~/.cache 2>/dev/null | sort -h | tail -10`), and files over 1 GB not opened in 90 days.
2. Caches and trash: size of the trash, `~/Library/Caches` (macOS) or `~/.cache` (Linux), and Downloads older than 60 days.
3. Apps: the 10 processes using the most CPU and memory right now (`ps aux` sorted), and anything that starts at login.
4. Write the report to `os/reports/clean-up-YYYY-MM-DD-HHMM.md`: a 3-line summary at the top, then each section as a short table, then up to 5 suggested actions with the space each would free.
On Windows (Claude Code's Bash is Git Bash): disk with `df -h /c`; caches are `$LOCALAPPDATA/Temp` and the browsers' cache folders under `$LOCALAPPDATA`; processes with `tasklist //fo csv //nh`, ranked by memory (Windows doesn't give CPU there, so say so); login items with `reg query 'HKCU\Software\Microsoft\Windows\CurrentVersion\Run'`.
5. Don't delete or move anything. Suggested actions are for Issam to approve in a normal chat.
