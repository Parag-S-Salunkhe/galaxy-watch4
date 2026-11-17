# Part 2: Measure before you change anything

The internet has a hundred "speed up your Galaxy Watch" tips. Most are myths (see [Do's and Don'ts](Dos-and-Donts.md)). Instead of guessing, we measured the watch first, so every change could be judged by numbers.

## The snapshot script

```bash
export WATCH=<watch-ip>:<port>
scripts/speed_snapshot.sh before
```

It is read-only. The only side effect is that it wakes the screen and opens and closes a few simple apps to time cold starts. It saves to `speed/<label>-<date>/`:

| File | What it tells you |
|---|---|
| `summary.txt` | uptime, process count, MemAvailable, swap, top CPU users, frame stats, app launch times |
| `proc_meminfo.txt` | raw `/proc/meminfo` |
| `meminfo.txt` | `dumpsys meminfo`: memory per process, zram (compressed swap) |
| `cpuinfo.txt` / `top.txt` | which processes use the CPU |
| `gfx_sysui.txt` | frame stats of the system UI: total frames, janky frames, 90th percentile |

Two more tests:

```bash
scripts/jank_test.sh before      # swipes Tiles / quick panel / app list 3 times, then reads frame stats
scripts/face_cpu.sh before 30    # CPU of the active watch face with the screen on, over 30 s
```

## What we found on my watch

1. **32 days without a restart.**
2. **Google Assistant used ~21% CPU while idle.** It held the microphone, listening for "Hey Google". I never use voice.
3. **Memory pressure was the real cause of the lag:** ~225 MB free, ~685 MB pushed into compressed swap (zram), thousands of major page faults. It was not the GPU, not the animations and not just "old hardware".
4. **About a dozen apps woke up in the background for no reason.** Smart Switch: 170 wake-ups. A Samsung keep-alive service: ~1,500 alarms.
5. **The stock watch face was the biggest CPU user with the screen on** (~20%, plus ~17% for the screen compositor).
6. The firmware already had the One UI 8 Watch lag fix, so there was no update to wait for.

## Useful one-liners (all read-only)

```bash
adb -s "$WATCH" shell uptime
adb -s "$WATCH" shell "grep -E 'MemAvailable|SwapTotal|SwapFree' /proc/meminfo"
adb -s "$WATCH" shell dumpsys cpuinfo | head -20
adb -s "$WATCH" shell dumpsys alarm | grep -c "<package>"        # how often an app sets alarms
adb -s "$WATCH" shell pm list packages -d                        # what is already disabled (your baseline)
adb -s "$WATCH" shell settings list global > settings_before.txt # diff this after toggling something on the watch
```

**Tip:** to find which setting a toggle on the watch changes, dump `settings list global/system/secure` before you tap it, dump again after, and diff the two. That gives you the exact key and value, so you can log a precise undo.

Next: [Part 3: Speed it up safely](Part3-Speed-It-Up-Safely.md)
