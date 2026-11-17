# Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `adb connect` times out | Mac and watch on different bands or networks | Force the hotspot to 2.4 GHz; check both are on the same network |
| adb worked, now `offline` | Watch Wi-Fi sleeps in doze off the charger | Put the watch on its charger; reconnect |
| Port changed | Wireless debugging port changes after a reboot or network change | `dns-sd -L "<service>" _adb-tls-connect._tcp local.` |
| Wireless debugging is off again | It turns off after a reboot or Wi-Fi sleep | Turn it on again; pairing is kept |
| adb discovery crashes every few minutes | Many devices advertising adb on the same network | Use `dns-sd` for the port, use a private hotspot, keep sessions short |
| A script splits the serial wrongly | The mDNS serial contains a space, e.g. `... (2)` | Split `adb devices` output on the tab |
| `VERSION_DOWNGRADE` on install | Older version code than the one installed | Rebuild with a higher version code |
| `Watch face package is not installed` when setting a stock face | Stock faces need the full component name | Use `<package>/<service class>` as `watchFaceId` |
| Validator fails on an `HH` format | WFF's time format pattern doesn't accept `HH` | Use `hh` with `hourFormat` 24 |
| Blank AOD, or AOD drawn by the CPU | Some element reads time data | Part 5: date via complications, am/pm via BitmapFont words |
| Animation doesn't play | Transform animation didn't run on this watch | Use frame images (`PartAnimatedImage`) |
| Text sits off-centre or outside its box | Whitespace or newlines inside the text element | Keep labels inline; measure with `scripts/text_extents.py` |
| Assistant is back after a reboot | It holds the assistant role | Part 3, rows 10–11 |
| Weather tile is blank | Weather app is disabled | Expected; `pm enable com.samsung.android.watch.weather` |
| `sleep` in a script on the watch never ends | The CPU is suspended in doze | Run timing loops from the Mac, with the watch on the charger |
