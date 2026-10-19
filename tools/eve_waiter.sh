#!/bin/bash
# The Mac's one trigger on a release date's eve (DECISIONS, review round 1, OPS-2 and OPS-5).
# From 19:05 ET it runs `make daily-core` every 10 minutes until the quarter's lock record is on
# origin/main, giving up at 23:30 ET. A run that refuses (a dirty tree, a failed gh call) is retried.
# Every exit code goes to .build/logs/eve-<date>.log.
# Usage: tools/eve_waiter.sh 2026Q3 2026-10-29
set -u
usage="usage: tools/eve_waiter.sh <quarter> <eve date, YYYY-MM-DD>"
q=${1:?$usage}
eve=${2:?$usage}
start="${eve}T19:05"
stop="${eve}T23:30"
mkdir -p .build/logs
log=".build/logs/eve-${eve}.log"
while :; do
  now=$(TZ=America/New_York date +%Y-%m-%dT%H:%M)
  if [[ "$now" > "$stop" ]]; then
    echo "$now no lock record on origin/main by $stop ET; stopping" >>"$log"
    exit 1
  fi
  if [[ "$now" < "$start" ]]; then
    sleep 60
    continue
  fi
  git fetch -q origin >>"$log" 2>&1
  if git cat-file -e "origin/main:results/live/${q}_lock.json" 2>/dev/null; then
    echo "$now ${q}_lock.json is on origin/main; done" >>"$log"
    exit 0
  fi
  make daily-core >>"$log" 2>&1
  echo "$now make daily-core exited $?" >>"$log"
  sleep 600
done
