# Do's and Don'ts

Before changing anything, Claude ran research agents across owner reports (Reddit, XDA), package-safety lists and adb tweak guides, then checked each claim against our own measurements. Confidence: **H** = many owners plus our own data, **M** = several owners, **L** = a few reports.

## ✅ Do (ranked)

1. **Restart it.** Mine had run 32 days. A weekly restart through a Samsung Mode/Routine keeps memory pressure down. (M, confirmed by our numbers)
2. **Turn on Reduce transparency and blur:** Accessibility → Vision enhancements. (H, about 12 owners confirmed it)
3. **Turn Always-on display off** if you don't need it. If you keep it, use a face that offloads it (Part 5). (H)
4. **Use a lighter watch face:** no seconds hand, two or fewer static complications, or your own WFF face. The stock face was the biggest CPU user with the screen on.
5. **Disable only apps your own measurements show running in the background,** one at a time, with `pm disable-user`. Use a list like UAD-ng's "Recommended" only as a reference: it isn't tested on watches.
6. **Battery, no speed effect:** background Wi-Fi/BLE scanning off; heart rate every 10 minutes instead of continuous; stress measured manually.
7. **Log every change with its undo.** If a `settings get` returns `null`, the undo is `settings delete`.
8. **Measure before and after** (Part 2). Judge the always-on display lag by feel, because the swipe test can't see it.

## ❌ Don't (myths, or harmful)

- RAM cleaner or "booster" apps.
- *Background process limit*, *Don't keep activities*, *Disable HW overlays*, *Force 4x MSAA*.
- Lowering `max_cached_processes`, `am compact`, lmkd tweaks, `am kill-all`.
- **Animations set to 0.** It can break progress indicators. 0.25 is enough.
- `pm uninstall` or `pm clear` on system apps. Disable instead.
- Factory reset on One UI 8 Watch "to speed it up": people report problems re-adding their Google account. (M–L)
- Disabling the update path (`com.wssyncmldm`, `com.sec.android.soagent`, FOTA), Google Play services or `diagmonagent` (it gets relaunched every second, which is slower).
- `adb tcpip 5555` (unencrypted) or `curl | bash` installers.
- Tools that run adb **on** the watch (Canta/Shizuku, "Local ADB" apps), or watch-face APKs from random file shares.

## 🔐 Security habits

- Wireless debugging **off** after every session.
- Pair only on a private network. Never tick *Always allow on this network* on a shared one.
- Treat `~/.android/adbkey` like a password.
- Check the SHA-256 of every tool you download.

## 🤝 Working with an AI on a real device

- Write the rules down first: no root, nothing permanent, ask before every change, log every undo.
- Let it research and measure freely (read-only). Approve each change yourself.
- Ask it to separate **measured** facts from **owner reports**. The best fixes here were boring: a restart, a few disabled apps, one accessibility toggle.
