#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .runtime/downloads .runtime/system
chmod 700 .runtime
if [[ ! -x .runtime/mysql/bin/mysqld ]]; then
  curl -fL --retry 2 https://cdn.mysql.com/archives/mysql-8.4/mysql-8.4.6-linux-glibc2.28-x86_64-minimal.tar.xz -o .runtime/downloads/mysql.tar.xz
  tar -xJf .runtime/downloads/mysql.tar.xz -C .runtime
  mv .runtime/mysql-8.4.6-linux-glibc2.28-x86_64-minimal .runtime/mysql
fi
if ! ldconfig -p 2>/dev/null | rg -q 'libaio.so.1' && [[ ! -e .runtime/system/usr/lib/libaio.so.1 ]]; then
  if command -v pacman >/dev/null && command -v bsdtar >/dev/null; then
    package_url=$(pacman -Sp --print-format '%l' libaio | head -1)
    package_url="${package_url/http:/https:}"
    curl -fL "$package_url" -o .runtime/downloads/libaio.tar.zst
    bsdtar -xf .runtime/downloads/libaio.tar.zst -C .runtime/system
  else
    printf '%s\n' 'Install your distribution libaio package, or use Docker Compose. See README.md.'
    exit 1
  fi
fi
.venv/bin/python scripts/local_mysql.py start
