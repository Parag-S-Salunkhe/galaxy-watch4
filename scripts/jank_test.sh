#!/bin/bash
# Repeatable UI smoothness test. Usage: WATCH=<ip:port> scripts/jank_test.sh <label>
# Resets frame stats, swipes through Tiles / quick panel / app list on a 450x450 screen, then reads frame stats.
# Side effects: wakes the screen, swipes, returns to the watch face. Changes no settings.
set -u
LABEL="${1:?label}"
S="${WATCH:?set WATCH=<ip:port> (the port changes, see docs/Part1)}"
OUT="$(cd "$(dirname "$0")/.." && pwd)/speed/jank-${LABEL}-$(date +%Y%m%d-%H%M)"
mkdir -p "$OUT"
sh() { adb -s "$S" shell "$@"; }
sh true >/dev/null 2>&1 || { echo "watch $S not reachable - check WATCH=<ip:port>" >&2; exit 1; }
PKGS="com.samsung.android.wearable.sysui com.google.android.apps.wearable.systemui com.google.wear.services"

sh input keyevent KEYCODE_WAKEUP; sh input keyevent KEYCODE_HOME; sleep 2
for p in $PKGS; do sh dumpsys gfxinfo "$p" reset >/dev/null 2>&1; done

for round in 1 2 3; do
  for i in 1 2 3 4 5; do sh input swipe 400 225 50 225 150; sleep 0.6; done   # Tiles, forward
  for i in 1 2 3 4 5; do sh input swipe 50 225 400 225 150; sleep 0.6; done   # back to face
  sh input swipe 225 5 225 400 200; sleep 0.8                                   # quick panel down
  sh input swipe 225 440 225 50 200; sleep 0.8                                  # close it
  sh input swipe 225 440 225 50 200; sleep 1                                    # app list up
  for i in 1 2 3; do sh input swipe 225 380 225 80 200; sleep 0.5; done         # scroll list
  sh input keyevent KEYCODE_HOME; sleep 1.5
done

for p in $PKGS; do
  sh dumpsys gfxinfo "$p" > "$OUT/gfx_$p.txt" 2>&1
  tot=$(grep -m1 "Total frames rendered" "$OUT/gfx_$p.txt" | awk '{print $4}')
  jank=$(grep -m1 "Janky frames:" "$OUT/gfx_$p.txt" | sed 's/.*Janky frames: //')
  p50=$(grep -m1 "50th percentile" "$OUT/gfx_$p.txt" | awk '{print $3}')
  p90=$(grep -m1 "90th percentile" "$OUT/gfx_$p.txt" | awk '{print $3}')
  p99=$(grep -m1 "99th percentile" "$OUT/gfx_$p.txt" | awk '{print $3}')
  echo "$LABEL $p: frames=${tot:-0} janky=${jank:-n/a} p50=${p50:-} p90=${p90:-} p99=${p99:-}" | tee -a "$OUT/summary.txt"
done
echo "saved: $OUT"
