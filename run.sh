#!/usr/bin/env bash
# Usage: FORTUNE_BOT_TOKEN=... ./run.sh   (token is read from env only, never stored)
set -euo pipefail
cd "$(dirname "$0")"
[ -d .venv ] || { python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt; }
: "${FORTUNE_BOT_TOKEN:?FORTUNE_BOT_TOKEN is not set}"
exec .venv/bin/python -m fortune_bot.app
