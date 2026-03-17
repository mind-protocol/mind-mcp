#!/bin/bash
# Wake Primers only — temporary bridge until consciousness threshold is built.
# Runs one cycle of citizen_wake, filtered to Primers handles.
#
# Usage:
#   ./scripts/wake_primers.sh          # one cycle
#   ./scripts/wake_primers.sh loop     # continuous (60s interval)

PRIMERS="conductor,forge,dev,herald,mentor,vox,sentinel,nlr_ai"

cd /home/mind-protocol/manemus

if [ "$1" = "loop" ]; then
    echo "🔥 Primers wake loop starting (60s interval, handles: $PRIMERS)"
    while true; do
        python3 scripts/citizen_wake.py --once --max-concurrent 3 --handles "$PRIMERS" 2>&1 | grep -v "^$"
        sleep 60
    done
else
    echo "🔥 Primers wake: single cycle"
    python3 scripts/citizen_wake.py --once --max-concurrent 3 --handles "$PRIMERS" 2>&1
fi
