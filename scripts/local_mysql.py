"""Manage this project's optional private Linux MySQL instance without sudo.

The current workstation uses the official MySQL 8.4.6 generic binary and an
extracted Arch libaio package. Other machines can use Docker Compose or an
existing MySQL 8 instance instead. This script never stops an unrelated server.
"""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
import mysql.connector
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent
RUNTIME = ROOT / ".runtime"
RUNTIME.mkdir(mode=0o700, exist_ok=True)
CONFIG = dotenv_values(ROOT / ".env")
PID = RUNTIME / "mysql.pid"


def connect_root(initial=False):
    return mysql.connector.connect(
        unix_socket=str(RUNTIME / "mysql.sock"),
        user="root",
        password="" if initial else CONFIG.get("MYSQL_ROOT_PASSWORD", ""),
        use_pure=True,
    )


def start():
    try:
        connection = connect_root()
        connection.close()
        print("Project MySQL is already running.")
        return
    except mysql.connector.Error:
        pass
    binary = RUNTIME / "mysql/bin/mysqld"
    if not binary.exists():
        raise SystemExit(
            "MySQL binary missing. Run scripts/install_local_mysql.sh or use Docker Compose. See README.md."
        )
    env = {
        **os.environ,
        "LD_LIBRARY_PATH": str(RUNTIME / "system/usr/lib")
        + ":"
        + os.environ.get("LD_LIBRARY_PATH", ""),
    }
    data_dir = RUNTIME / "mysql-data"
    initial = not (data_dir / "mysql").exists()
    if initial:
        subprocess.run(
            [
                str(binary),
                "--no-defaults",
                "--initialize-insecure",
                f"--basedir={RUNTIME / 'mysql'}",
                f"--datadir={data_dir}",
                f"--log-error={RUNTIME / 'mysql-init.log'}",
            ],
            env=env,
            check=True,
        )
    args = [
        str(binary),
        "--no-defaults",
        f"--basedir={RUNTIME / 'mysql'}",
        f"--datadir={data_dir}",
        "--bind-address=127.0.0.1",
        f"--port={CONFIG.get('MYSQL_PORT', '3307')}",
        f"--socket={RUNTIME / 'mysql.sock'}",
        f"--pid-file={PID}",
        "--mysqlx=0",
        "--skip-log-bin",
        f"--log-error={RUNTIME / 'mysql.log'}",
    ]
    with open(RUNTIME / "mysql-process.log", "ab") as log:
        process = subprocess.Popen(
            args, env=env, stdout=log, stderr=log, start_new_session=True
        )
    for _ in range(100):
        if process.poll() is not None:
            raise SystemExit("MySQL failed to start. Read .runtime/mysql.log.")
        try:
            connection = connect_root(initial)
            break
        except mysql.connector.Error:
            time.sleep(0.2)
    else:
        raise SystemExit("MySQL did not become ready. Read .runtime/mysql.log.")
    cursor = connection.cursor()
    # Database and account names are fixed for the private development instance.
    cursor.execute(
        "CREATE DATABASE IF NOT EXISTS careerlens CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci"
    )
    cursor.execute(
        "CREATE USER IF NOT EXISTS 'careerlens'@'127.0.0.1' IDENTIFIED BY %s",
        (CONFIG["MYSQL_PASSWORD"],),
    )
    cursor.execute("GRANT ALL PRIVILEGES ON careerlens.* TO 'careerlens'@'127.0.0.1'")
    cursor.execute(
        "GRANT ALL PRIVILEGES ON test_careerlens.* TO 'careerlens'@'127.0.0.1'"
    )
    if initial:
        cursor.execute(
            "ALTER USER 'root'@'localhost' IDENTIFIED BY %s",
            (CONFIG["MYSQL_ROOT_PASSWORD"],),
        )
    connection.close()
    print(
        "Project MySQL is ready on loopback port "
        + CONFIG.get("MYSQL_PORT", "3307")
        + "."
    )


def stop():
    if not PID.exists():
        print("No project MySQL PID file found.")
        return
    pid = int(PID.read_text())
    cmdline = Path(f"/proc/{pid}/cmdline")
    if not cmdline.exists() or str(RUNTIME / "mysql-data") not in cmdline.read_text():
        raise SystemExit("Refusing to stop a process outside this project.")
    os.kill(pid, signal.SIGTERM)
    for _ in range(100):
        if not cmdline.exists():
            print("Project MySQL stopped.")
            return
        time.sleep(0.1)
    print("Shutdown requested. MySQL is still flushing data.")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"start", "stop"}:
        raise SystemExit("Usage: .venv/bin/python scripts/local_mysql.py start|stop")
    globals()[sys.argv[1]]()
