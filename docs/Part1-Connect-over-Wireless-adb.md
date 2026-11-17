# Part 1: Connecting the Mac to the watch over wireless adb

Goal: a Mac terminal that can run `adb shell` on the watch, with no cable and no app installed on the watch.

## What you need

- Galaxy Watch 4 (any Wear OS 3+ watch works the same way) and a Mac.
- Android platform-tools: `brew install android-platform-tools`
- The Mac and the watch on **the same Wi-Fi network**.

## Steps

1. **Turn on Developer options on the watch.** Settings → About watch → Software information → tap *Software version* 5 times.
2. **Turn on ADB debugging and Wireless debugging.** Settings → Developer options. Wireless debugging shows an IP address and port.
3. **Pair once.** In Wireless debugging tap *Pair new device*. The watch shows a pairing code and a *pairing* port (different from the connect port).

   ```bash
   adb pair <watch-ip>:<pairing-port>      # type the code shown on the watch
   ```

4. **Connect.** Use the port shown on the Wireless debugging screen (not the pairing port):

   ```bash
   adb connect <watch-ip>:<port>
   export WATCH=<watch-ip>:<port>
   adb -s "$WATCH" shell getprop ro.product.model     # should print the model, e.g. SM-R870
   ```

5. **Find the port again later without looking at the watch.** The port changes after every reboot or network change. The watch advertises itself over mDNS:

   ```bash
   dns-sd -B _adb-tls-connect._tcp local.               # lists the service name
   dns-sd -L "<service name>" _adb-tls-connect._tcp local.   # prints the host and port
   ```

## The gotchas that cost me time

- **Phone hotspot must be 2.4 GHz only.** The watch only speaks 2.4 GHz. When my phone's hotspot ran both bands, the Mac sat on 5 GHz, the watch on 2.4 GHz, and the hotspot didn't bridge them: they couldn't see each other. Forcing the hotspot to 2.4 GHz fixed it.
- **Crowded networks break discovery.** On a network where dozens of other devices advertise adb, adb's built-in mDNS crashed every 7–10 minutes. Use `dns-sd` (above) for the port and keep commands short.
- **The adb serial can contain a space,** e.g. `adb-XXXX (2)._adb-tls-connect._tcp`. When parsing `adb devices`, split on the tab, not on whitespace.
- **Wireless debugging turns itself off** after a reboot and when Wi-Fi sleeps. Off the charger, the watch's Wi-Fi sleeps in doze and adb goes offline. Work with the watch on its charger.
- Pairing survives reboots; only the port changes.

## Security: do this every time you finish

- **Turn Wireless debugging off** on the watch. While it's on, it listens on the network and drains the battery.
- Never tick *Always allow on this network* on a shared hotspot. Pair only on a private network.
- Leave *Disable adb authorization timeout* off, so authorisations expire on their own.
- `~/.android/adbkey` on your Mac is the credential: whoever has it gets a full shell on the watch (installs, taps, notification text including one-time codes). Keep it out of cloud sync. If the Mac is lost, use *Revoke USB debugging authorizations* on the watch.
- Never use `adb tcpip 5555`: it's the old, unencrypted way.

Next: [Part 2: Measure before you change anything](Part2-Measure-Before-You-Change.md)
