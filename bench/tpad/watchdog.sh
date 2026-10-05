#!/bin/sh
# Keeps the TPAD runner alive: restarts `bench run SPEC` if it exits before every planned run has a result.
# Usage: nohup sh bench/tpad/watchdog.sh bench/tpad/pilot-stage1.yaml 104 > bench/tpad/watchdog.log 2>&1 &
SPEC="$1"; PLANNED="$2"; OUT=bench/tpad/runs-pilot/results.jsonl
while true; do
  DONE=$(.venv/bin/python -c "
import json
rows=[json.loads(l) for l in open('$OUT') if l.strip()] if __import__('os').path.exists('$OUT') else []
print(len({r['key'] for r in rows if not r.get('error')}))")
  if [ "$DONE" -ge "$PLANNED" ]; then echo "$(date -u +%FT%T) all $PLANNED runs done"; exit 0; fi
  if ! pgrep -f "bench run $SPEC" > /dev/null; then
    echo "$(date -u +%FT%T) runner not running ($DONE/$PLANNED done); restarting"
    pkill -f researchforge.mcp_server; pkill -f "_npx.*dsh"
    nohup .venv/bin/researchforge bench run "$SPEC" --workers 2 >> bench/tpad/stage1.log 2>&1 &
  fi
  sleep 120
done
