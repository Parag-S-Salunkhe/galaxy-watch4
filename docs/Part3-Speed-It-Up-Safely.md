# Part 3: Speed it up safely: every command with its undo

**The method rule:** only `pm disable-user --user 0 <package>` (undo: `pm enable <package>`). Never `pm uninstall` and never `pm clear`. A disabled app comes back with one command; an uninstalled system app may not.

Before each change: take a baseline (`pm list packages -d`, `settings get ...`). After each change: verify it applied. Then write a changelog row with the command and its undo. If a `settings get` returns `null`, the undo is `settings delete`, not `settings put ... 0`.

All commands run as `adb -s "$WATCH" shell <command>`.

## Round 1: obvious background apps + animation speed

| # | Command | Undo |
|---|---|---|
| 1 | `pm disable-user --user 0 com.google.android.wearable.assistant` | `pm enable com.google.android.wearable.assistant` |
| 2 | `pm disable-user --user 0 com.google.android.apps.maps` | `pm enable com.google.android.apps.maps` |
| 3 | `pm disable-user --user 0 com.google.android.apps.messaging` | `pm enable com.google.android.apps.messaging` |
| 4 | `pm disable-user --user 0 com.samsung.android.watch.weather` | `pm enable com.samsung.android.watch.weather` |
| 5 | `pm disable-user --user 0 com.samsung.android.watch.worldclock` | `pm enable com.samsung.android.watch.worldclock` |
| 6–8 | `settings put global window_animation_scale 0.25` (same for `transition_animation_scale`, `animator_duration_scale`) | put back the old value (mine was 0.5) |

Side effect: the Weather and World Clock tiles and watch-face slots go blank. Only disable what you don't use.

## Round 2: restart, and the Assistant that came back

| # | Command | Undo |
|---|---|---|
| 9 | `reboot` (first restart in 32 days) | n/a |
| 10 | `cmd role remove-role-holder android.app.role.ASSISTANT com.google.android.wearable.assistant` | `cmd role add-role-holder android.app.role.ASSISTANT com.google.android.wearable.assistant` |
| 11 | `pm disable-user --user 0 com.google.android.wearable.assistant` | `pm enable ...` (then undo row 10) |

**Surprise:** after the reboot, the system re-enabled the Assistant by itself (`lastDisabledCaller: android`) and it went straight back to using the microphone. It holds the system *assistant role*, so Android brings it back at boot. Removing it from the role first, then disabling it, made it stick. Check after the next reboot:

```bash
pm list packages -d | grep assistant
cmd role get-role-holders android.app.role.ASSISTANT
```

## Round 3: background and voice apps

I don't use voice at all, so the voice apps went too. **Before disabling them, test voice typing** (keyboard → microphone). On my watch it kept working, because the speech engine is `com.google.android.tts`, which I kept.

| # | Package | What it is |
|---|---|---|
| 12 | `com.sec.android.easyMover` | Smart Switch (170 wake-ups, resident) |
| 13 | `com.samsung.android.watch.runestone.app` | keep-alive service (~1,500 alarms) |
| 14 | `com.samsung.android.samsungpay.gear` | Samsung Wallet (only if you never pay with the watch) |
| 15–16 | `com.samsung.android.bixby.agent`, `com.samsung.android.bixby.wakeup` | Bixby |
| 17 | `com.samsung.android.intellivoiceservice` | Samsung voice service |
| 18 | `com.samsung.android.wear.voicerecorder` | Voice recorder |

Command: `pm disable-user --user 0 <package>`. Undo: `pm enable <package>`.

Side effect: if the Home key long-press was set to Bixby, it does nothing now. Change it in Settings → Advanced features → Customize keys.

## Round 4: settings with a real effect

| # | Command | Undo |
|---|---|---|
| 19 | `settings put system accessibility_reduce_transparency 1` (= Accessibility → Vision enhancements → Reduce transparency and blur) | `settings delete system accessibility_reduce_transparency` |
| 34 | `settings put global wifi_scan_always_enabled 0` and `settings put global ble_scan_always_enabled 0` | `settings put global wifi_scan_always_enabled 1` and `settings delete global ble_scan_always_enabled` |

Row 34 only stops background location scans while Wi-Fi or Bluetooth is off. The phone connection is unaffected.

Left off on purpose: *Remove animations*. Full animation removal can break progress indicators.

## Never disable these

Update and security path: `com.wssyncmldm`, `com.sec.android.soagent`, `com.samsung.android.wearable.setupwizard.fota`, `com.google.android.gms`, Knox Manage.

Also keep:
- `com.sec.android.diagmonagent`: if you disable it, other services relaunch it every second, which makes things slower.
- `com.samsung.android.mobileservice`: the Samsung account Samsung Health needs.
- `com.samsung.android.app.routines`: Modes and Bedtime.
- Alarm and Timer, Camera Controller, the media controller, Gallery.

## Results

| | Before | Right after | A day later |
|---|---|---|---|
| Free memory | ~225 MB | ~345 MB | ~230 MB |
| Swap in use | ~685 MB | ~323 MB | ~570 MB |
| Assistant idle CPU | ~21% | 0 | 0 |

So the lasting wins were the Assistant's CPU, a dozen fewer apps running, and a **weekly restart** (I set it up with a Samsung Mode/Routine).

Next: [Part 4: Build a watch face](Part4-Build-a-Watch-Face.md)
