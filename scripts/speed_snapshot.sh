#!/bin/bash
# Read-only speed snapshot of the watch. Usage: WATCH=<ip:port> scripts/speed_snapshot.sh <label>
# Only side effect: wakes the screen and opens/closes a few simple apps to time cold starts.
set -u
LABEL="${1:?label, e.g. before or after}"
S="${WATCH:?set WATCH=<ip:port> (the port changes, see docs/Part1)}"
OUT="$(cd "$(dirname "$0")/.." && pwd)/speed/${LABEL}-$(date +%Y%m%d-%H%M)"
mkdir -p "$OUT"
sh() { adb -s "$S" shell "$@"; }
sh true >/dev/null 2>&1 || { echo "watch $S not reachable - check WATCH=<ip:port>" >&2; exit 1; }

echo "== $LABEL $(date) ==" | tee "$OUT/summary.txt"

sh uptime | tee -a "$OUT/summary.txt"
sh ps -A | wc -l | sed 's/^ */processes: /' | tee -a "$OUT/summary.txt"

sh cat /proc/meminfo > "$OUT/proc_meminfo.txt"
awk '/MemTotal|MemAvailable|SwapTotal|SwapFree/' "$OUT/proc_meminfo.txt" | tee -a "$OUT/summary.txt"

sh dumpsys -t 60 meminfo > "$OUT/meminfo.txt" 2>&1
grep -E "Free RAM|Used RAM|ZRAM" "$OUT/meminfo.txt" | tee -a "$OUT/summary.txt"

sh top -b -n 1 -m 15 > "$OUT/top.txt" 2>&1
sh dumpsys cpuinfo > "$OUT/cpuinfo.txt" 2>&1
echo "-- top CPU (dumpsys cpuinfo) --" | tee -a "$OUT/summary.txt"
head -16 "$OUT/cpuinfo.txt" | tee -a "$OUT/summary.txt"

sh dumpsys gfxinfo com.samsung.android.wearable.sysui > "$OUT/gfx_sysui.txt" 2>&1
grep -E "Total frames rendered|Janky frames:|90th percentile" "$OUT/gfx_sysui.txt" | head -3 | sed 's/^/sysui /' | tee -a "$OUT/summary.txt"

# Cold starts (-S force-stops first). Samsung Health is timed warm only, so a workout is never killed.
echo "-- launch times ms (3 runs) --" | tee -a "$OUT/summary.txt"
sh input keyevent KEYCODE_WAKEUP
for act in \
  com.samsung.android.watch.stopwatch/.activity.StopwatchActivity \
  com.samsung.android.watch.timer/.activity.TimerHomeActivity \
  com.samsung.android.wear.calculator/.main.CalculatorActivity \
  com.samsung.android.watch.alarm/.activity.AlarmMainActivity \
  com.samsung.android.watch.weather/.ui.WeatherActivity \
  com.google.android.apps.wearable.settings/com.samsung.android.clockwork.settings.StMainSettingsActivity; do
  t=""
  for i in 1 2 3; do
    sh input keyevent KEYCODE_WAKEUP
    v=$(sh am start -W -S -n "$act" 2>&1 | awk '/TotalTime/{print $2}')
    t="$t ${v:-?}"
    sh input keyevent KEYCODE_HOME; sleep 2
  done
  echo "cold ${act%%/*}:$t" | tee -a "$OUT/summary.txt"
done
t=""
for i in 1 2 3; do
  sh input keyevent KEYCODE_WAKEUP
  v=$(sh am start -W -n com.samsung.android.wear.shealth/.app.home.HomeActivity 2>&1 | awk '/TotalTime/{print $2}')
  t="$t ${v:-?}"
  sh input keyevent KEYCODE_HOME; sleep 2
done
echo "warm com.samsung.android.wear.shealth:$t" | tee -a "$OUT/summary.txt"
echo "saved: $OUT"
