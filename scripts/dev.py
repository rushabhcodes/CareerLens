"""Start or stop only CareerLens development servers, preserving their logs."""

from pathlib import Path
import json
import os
import signal
import subprocess
import sys
import time
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parent.parent
RUNTIME = ROOT / ".runtime"
STATE = RUNTIME / "dev-processes.json"
SERVERS = {
    "backend": (
        [
            str(ROOT / ".venv/bin/python"),
            "manage.py",
            "runserver",
            "127.0.0.1:8000",
            "--noreload",
        ],
        ROOT / "backend",
        "http://127.0.0.1:8000/api/auth/me/",
    ),
    "frontend": (["npm", "run", "dev"], ROOT / "frontend", "http://127.0.0.1:5173/"),
}


def ready(url):
    try:
        with urllib.request.urlopen(url, timeout=1) as response:
            return response.status == 200
    except urllib.error.HTTPError as error:
        return error.code == 401
    except (urllib.error.URLError, TimeoutError):
        return False


def start():
    RUNTIME.mkdir(mode=0o700, exist_ok=True)
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    for name, (command, cwd, url) in SERVERS.items():
        if ready(url):
            print(f"{name} is already responding at {url}")
            continue
        with (RUNTIME / f"{name}.log").open("ab") as log:
            process = subprocess.Popen(
                command, cwd=cwd, stdout=log, stderr=log, start_new_session=True
            )
        state[name] = process.pid
        STATE.write_text(json.dumps(state))
        for _ in range(80):
            if ready(url):
                break
            if process.poll() is not None:
                raise SystemExit(f"{name} failed. Read .runtime/{name}.log.")
            time.sleep(0.2)
        else:
            raise SystemExit(f"{name} did not become ready. Read its log.")
        print(f"{name} ready: {url}")
    print("Open http://127.0.0.1:5173/ in your browser.")


def stop():
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    for name, pid in state.items():
        proc = Path(f"/proc/{pid}/cwd")
        if proc.exists() and str(proc.resolve()).startswith(str(ROOT)):
            os.killpg(pid, signal.SIGTERM)
            print(f"Stopped {name}.")
    STATE.unlink(missing_ok=True)


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"start", "stop"}:
        raise SystemExit("Usage: .venv/bin/python scripts/dev.py start|stop")
    globals()[sys.argv[1]]()
