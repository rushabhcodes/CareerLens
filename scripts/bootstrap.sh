#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
uv venv --python 3.12 .venv --allow-existing
uv pip sync --python .venv/bin/python backend/requirements.lock
.venv/bin/python scripts/create_env.py
if [[ "${1:-}" == "--local-mysql" ]]; then
  bash scripts/install_local_mysql.sh
fi
.venv/bin/python backend/manage.py migrate --noinput
.venv/bin/python backend/manage.py seed_catalog
npm --prefix frontend ci
.venv/bin/python backend/manage.py check
printf '%s\n' 'Setup complete. Start with: .venv/bin/python scripts/dev.py start'
