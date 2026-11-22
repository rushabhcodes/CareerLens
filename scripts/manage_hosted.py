"""Run Django management commands with a separately downloaded hosting environment."""

import os
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values

root = Path(__file__).resolve().parent.parent
target = root / ".env.production"
if not target.exists():
    raise SystemExit(
        "First run: vercel env pull .env.production --environment production"
    )
target.chmod(0o600)
values = {
    key: value for key, value in dotenv_values(target).items() if value is not None
}
if not values.get("DATABASE_URL") or not values.get("DJANGO_SECRET_KEY"):
    raise SystemExit(
        "The hosting environment needs DATABASE_URL and DJANGO_SECRET_KEY."
    )
if not sys.argv[1:]:
    raise SystemExit(
        "Usage: python scripts/manage_hosted.py <Django management command>"
    )
environment = os.environ.copy()
environment.update(values)
if sys.argv[1] in {"migrate", "test"} and values.get("DATABASE_URL_UNPOOLED"):
    environment["DATABASE_URL"] = values["DATABASE_URL_UNPOOLED"]
raise SystemExit(
    subprocess.run(
        [sys.executable, str(root / "backend/manage.py"), *sys.argv[1:]],
        cwd=root,
        env=environment,
    ).returncode
)
