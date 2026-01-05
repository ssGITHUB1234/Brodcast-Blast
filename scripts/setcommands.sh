#!/usr/bin/env bash
# Usage: BOT_TOKEN=xxxxx ./scripts/setcommands.sh
if [ -z "$BOT_TOKEN" ]; then
  echo "Set BOT_TOKEN env var"
  exit 1
fi

curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setMyCommands" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      {"command":"start","description":"Start the bot"},
      {"command":"connect","description":"Connect your TON wallet"},
      {"command":"broadcast","description":"Create/send a broadcast"},
      {"command":"help","description":"Get help"}
    ]
  }'
