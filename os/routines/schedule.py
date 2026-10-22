"""Run a command every N minutes on Issam's computer: launchd on macOS, cron on Linux,
Task Scheduler on Windows. Used by `run.py install` and `keepwarm.py install`.

On macOS a LaunchAgent runs inside the logged-in session, so `claude` can reach its
sign-in in the Keychain (cron often can't).
"""
import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def plist(label, args, minutes, log):
    items = "".join(f"\n    <string>{a}</string>" for a in args)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>{label}</string>
  <key>ProgramArguments</key>
  <array>{items}
  </array>
  <key>WorkingDirectory</key><string>{ROOT}</string>
  <key>EnvironmentVariables</key>
  <dict><key>PATH</key><string>{os.environ.get('PATH', '/usr/bin:/bin')}</string></dict>
  <key>StartInterval</key><integer>{minutes * 60}</integer>
  <key>StandardOutPath</key><string>{log}</string>
  <key>StandardErrorPath</key><string>{log}</string>
</dict>
</plist>
"""


def install(label, script, arg, minutes, log, write):
    """Print (or with write=True, set up) a schedule that runs `python script arg` every `minutes`."""
    args = [sys.executable, str(script), arg]
    system = platform.system()
    if system == "Darwin":
        path = Path.home() / "Library" / "LaunchAgents" / f"{label}.plist"
        if not write:
            print(f"Runs `{arg}` every {minutes} minutes with launchd. To set it up, run this again with --write.")
            print(f"It writes {path} and loads it. Undo with: launchctl unload {path} && rm {path}")
            return 0
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(plist(label, args, minutes, log))
        subprocess.run(["launchctl", "unload", str(path)], capture_output=True)
        subprocess.run(["launchctl", "load", str(path)], check=False)
        print(f"Scheduled: {path} (every {minutes} minutes). Log: {log}")
        return 0
    if system == "Windows":
        print(f'schtasks /Create /SC MINUTE /MO {minutes} /TN {label} /TR "\\"{args[0]}\\" \\"{args[1]}\\" {arg}"')
        return 0
    print("Add this line with `crontab -e`:")
    print(f"*/{minutes} * * * * cd {ROOT} && PATH={os.environ.get('PATH', '/usr/bin:/bin')} "
          f"{args[0]} {args[1]} {arg} >> {log} 2>&1")
    return 0
