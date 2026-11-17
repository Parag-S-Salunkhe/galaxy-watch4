# Questions & Answers

Questions I had along the way, and what I found.

1. <ins>Why disable apps instead of uninstalling them?</ins>

`pm disable-user --user 0` stops an app from running but keeps it on the system partition. One command (`pm enable`) brings it back, and it survives updates. `pm uninstall --user 0` removes it for your user, and restoring a system app afterwards isn't always possible without a reset. Disable gives you the same speed benefit with a guaranteed way back.

2. <ins>What is "swap" on a watch? It has no disk swap.</ins>

Android uses **zram**: a slice of RAM where memory pages are stored compressed. When free memory is low, inactive pages get compressed into zram instead of apps being killed. It's cheaper than killing an app, but compressing and decompressing costs CPU. 685 MB in zram on a 1.5 GB watch meant it was working hard all the time, and that was the lag.

3. <ins>Why did Google Assistant re-enable itself after a reboot?</ins>

It holds the system **assistant role** (`android.app.role.ASSISTANT`). At boot, Android makes sure the role holder is enabled, so the system re-enabled it (`lastDisabledCaller: android`). Remove the role holder first (`cmd role remove-role-holder ...`), then disable it.

4. <ins>Does disabling the voice apps break voice typing?</ins>

Not on my watch. The speech engine is `com.google.android.tts`, which I kept. Test the keyboard microphone **before** disabling Bixby and Samsung's voice service, so you know which one actually powers it.

5. <ins>What is Watch Face Format, and how is it different from Watch Face Studio?</ins>

WFF is the format: XML plus images, drawn by the watch's runtime, with no app code. Watch Face Studio is Samsung's visual editor that exports WFF. Writing the XML directly gives full control (BitmapFonts, expressions, complications, user settings) and makes changes easy to diff.

6. <ins>Why does the watch refuse to install an older version?</ins>

Android blocks downgrades (`VERSION_DOWNGRADE`) so an attacker can't roll an app back to a version with known bugs. `install -r -d` only works for debuggable apps. For a watch face, rebuild the old design with a **higher** version code.

7. <ins>What is AOD offload?</ins>

On watches with a low-power display chip, the always-on display can be handed to that chip so the main processor sleeps. The face runtime checks the whole face first. If anything reads time data, the hand-off is refused and the main processor draws the AOD instead. Details in Part 5.

8. <ins>Why only 2.4 GHz Wi-Fi?</ins>

The Galaxy Watch 4 only has 2.4 GHz Wi-Fi. If your hotspot runs both bands, the Mac may join 5 GHz, and some hotspots don't route between the two bands.

9. <ins>Is wireless adb safe?</ins>

It's encrypted (TLS) and requires pairing, so yes, as long as you turn it off when you're done, pair only on private networks and protect `~/.android/adbkey`. While it's on, it advertises itself on the network.

10. <ins>Did you root the watch?</ins>

No. Everything here works on a stock watch with Developer options on.
