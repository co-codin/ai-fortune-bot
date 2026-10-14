#!/usr/bin/env bash
# Background run without systemd: FORTUNE_BOT_TOKEN=... ./run-nohup.sh ; stop: kill $(cat bot.pid)
cd "$(dirname "$0")"
: "${FORTUNE_BOT_TOKEN:?FORTUNE_BOT_TOKEN is not set}"
setsid nohup ./run.sh >> bot.log 2>&1 < /dev/null &
echo $! > bot.pid; echo "started pid $(cat bot.pid), log: bot.log"
