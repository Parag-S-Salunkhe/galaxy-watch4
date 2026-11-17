#!/bin/bash
# Measure CPU of the active watch face with the screen on. Usage: WATCH=<ip:port> scripts/face_cpu.sh <label> [seconds]
# Keeps the screen awake on the watch face (WAKEUP + HOME every 3 s). Changes no settings.
set -u
mkdir -p "$(cd "$(dirname "$0")/.." && pwd)/speed"
LABEL="${1:?label}"; S="${WATCH:?set WATCH=<ip:port> (the port changes, see docs/Part1)}"; SECS="${2:-30}"
sh() { adb -s "$S" shell "$@"; }
sh true >/dev/null 2>&1 || { adb connect "$S" >/dev/null 2>&1; sh true >/dev/null 2>&1 || { echo "watch $S not reachable" >&2; exit 1; }; }
FACE=$(sh dumpsys wallpaper | awk -F'[{}/]' '/mWallpaperComponent=/{print $2; exit}')
sh input keyevent KEYCODE_WAKEUP; sh input keyevent KEYCODE_HOME; sleep 5
fpid=$(sh pidof "$FACE" | awk '{print $1}'); spid=$(sh pidof surfaceflinger | awk '{print $1}')
ticks() { sh cat /proc/"$1"/stat 2>/dev/null | awk '{print $14+$15}'; }
cpu_total() { sh head -1 /proc/stat | awk '{t=0; for(i=2;i<=NF;i++) t+=$i; print t, $5+$6}'; }
f0=$(ticks "$fpid"); s0=$(ticks "$spid"); read t0 i0 < <(cpu_total)
end=$((SECONDS+SECS)); while [ $SECONDS -lt $end ]; do sh input keyevent KEYCODE_WAKEUP; sleep 3; done
f1=$(ticks "$fpid"); s1=$(ticks "$spid"); read t1 i1 < <(cpu_total)
awk -v l="$LABEL" -v face="$FACE" -v f="$((f1-f0))" -v s="$((s1-s0))" -v dt="$((t1-t0))" -v di="$((i1-i0))" -v secs="$SECS" 'BEGIN{
  printf "%s | %s | face %.1f%% | surfaceflinger %.1f%% | whole watch busy %.1f%% (of 2 cores)\n", l, face, f/secs, s/secs, (dt-di)*100/dt }' \
  | tee -a "$(cd "$(dirname "$0")/.." && pwd)/speed/face_cpu.txt"
