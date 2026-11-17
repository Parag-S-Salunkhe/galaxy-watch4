# Part 4: Building a watch face in Watch Face Format

Watch Face Format (WFF) is Google's format for Wear OS faces: **XML plus images, no code**. The watch's own runtime draws it, so a WFF face is lighter and safer than a face app. Samsung's *Watch Face Studio* exports WFF too, but writing the XML by hand (with Claude) gave me full control.

## Toolchain (all free, no sudo)

```bash
brew install openjdk@21 android-commandlinetools
sdkmanager "build-tools;35.0.0" "platforms;android-35"
export JAVA_HOME=$(brew --prefix openjdk@21)/libexec/openjdk.jdk/Contents/Home
export ANDROID_HOME=$(brew --prefix)/share/android-commandlinetools
```

Google's tools from [github.com/google/watchface](https://github.com/google/watchface) releases. Download them, check the SHA-256 on the release page, and put them in `tools/google-watchface/`:
- `wff-validator.jar`: checks the XML against the WFF schema.
- `memory-footprint.jar`: checks the face stays under the memory limits (active and always-on).

## Anatomy of a face

```
watchfaces/heritageclean/
  AndroidManifest.xml           package name, hasCode=false, WFF version 3
  res/raw/watchface.xml         the face: scene, clocks, complications, user settings
  res/xml/watch_face_info.xml   preview + editable flag
  res/values/strings.xml        labels shown in the Customise menu
  res/drawable/*.png            dials, hands, heart and pulse frames, am/pm images
```

The PNGs are drawn by the Python scripts in `tools/` (standard library only: they write PNG bytes directly, anti-aliased by supersampling). Example:

```bash
python3 -I tools/make_analog_assets.py watchfaces/heritageclean/res/drawable
```

| Script | Draws |
|---|---|
| `make_analog_assets.py` | sword hands, seconds hand, 60-tick dial, always-on hands and dial |
| `make_v2_assets.py` | heartbeat frames, ECG trace, orange always-on hands and dial |
| `make_aod_theme_assets.py` | always-on hands and ticks in white/grey, so the accent theme can tint them |
| `make_pulse_frames.py` | the pulse sweep animation behind the heart-rate sub-dial |
| `make_aod_assets.py`, `make_heart.py` | Blue Rings' always-on hands and dial, the heart icon |
| `make_preview.py` | the preview image shown in the face picker |

## Build, install, set

```bash
tools/build.sh 17 heritageclean              # validate -> aapt2 compile/link -> zipalign -> sign -> memory check
adb -s "$WATCH" install -r out/heritageclean.apk
adb -s "$WATCH" shell am broadcast -a com.google.android.wearable.app.DEBUG_SURFACE \
  --es operation set-watchface --es watchFaceId com.parag.watchface.heritageclean
```

Or just long-press the current face on the watch and pick the new one.

**Version codes only go up.** The watch refuses to install an older `versionCode` over a newer one (`VERSION_DOWNGRADE`). To roll back a design, rebuild the old XML with a **higher** version code.

## Things I learned building the faces

- **Validate every build.** The validator catches schema mistakes before the watch silently shows a blank face.
- **Measure the face's CPU** (`scripts/face_cpu.sh`). The animated heartbeat cost ~10% CPU with the screen on (24–25% animated vs 14–15% static). I kept it because I like the look, but it's behind a *Pulse animation* toggle in Customise.
- **Transform-based animation didn't play** on this watch. A frame-by-frame image animation (`PartAnimatedImage`) did.
- **Whitespace inside text elements pushes the text out of its box.** Keep labels inline.
- **am/pm for a second time zone:** `AMPM_STRING` ignores the clock's time-zone setting, so it showed my local am/pm. It has to be worked out another way; see Part 5.
- **Check alignment with pixels, not eyes.** `scripts/text_extents.py` measures where bright pixels start and end in a screenshot (`adb exec-out screencap -p > shot.png`). That's how the date and second time zone ended up centred to within half a pixel.

Next: [Part 5: The always-on display detective story](Part5-AOD-on-the-Low-Power-Chip.md)
