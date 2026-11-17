#!/bin/bash
# Build, validate and sign a Watch Face Format face.
# Usage: tools/build.sh <version_code> <face>      e.g. tools/build.sh 17 heritageclean
#
# Needs (see docs/Part4-Build-a-Watch-Face.md):
#   - JDK 17+ (JAVA_HOME), Android build-tools 35 + platform 35 (ANDROID_HOME)
#   - Google's validator + memory-footprint jars in tools/google-watchface/ (download from github.com/google/watchface releases)
# The debug signing key is created on first run in out/ (never committed). Its password is random and stays in out/.
set -euo pipefail
VC="${1:?version code, must be higher than what is on the watch}"
NAME="${2:?face folder name: heritageclean or bluerings}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
P="$ROOT/watchfaces/$NAME"
OUT="$ROOT/out"
JAVA_HOME="${JAVA_HOME:?set JAVA_HOME to a JDK 17+}"
ANDROID_HOME="${ANDROID_HOME:?set ANDROID_HOME to your Android SDK}"
BT="$ANDROID_HOME/build-tools/35.0.0"
JAR="$ANDROID_HOME/platforms/android-35/android.jar"
GW="$ROOT/tools/google-watchface"
KS="$OUT/debug.keystore"
mkdir -p "$OUT"

[ -f "$P/res/drawable/preview.png" ] || python3 -I "$ROOT/tools/make_preview.py" "$P/res/drawable/preview.png"

echo "== validate (WFF v3)"
"$JAVA_HOME/bin/java" -jar "$GW/wff-validator.jar" 3 "$P/res/raw/watchface.xml" 2>&1 | grep -E "PASSED|FAILED|SEVERE" || true
"$JAVA_HOME/bin/java" -jar "$GW/wff-validator.jar" 3 "$P/res/raw/watchface.xml" 2>&1 | grep -q PASSED

echo "== aapt2 compile + link"
rm -f "$OUT/res.zip" "$OUT/unsigned.apk" "$OUT/aligned.apk"
"$BT/aapt2" compile --dir "$P/res" -o "$OUT/res.zip"
"$BT/aapt2" link -o "$OUT/unsigned.apk" -I "$JAR" --manifest "$P/AndroidManifest.xml" \
  --version-code "$VC" --version-name "1.0.$VC" "$OUT/res.zip"
"$BT/zipalign" -p -f 4 "$OUT/unsigned.apk" "$OUT/aligned.apk"

echo "== sign (local debug key)"
if [ ! -f "$KS" ]; then
  head -c 18 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' > "$OUT/.ks-pass"
  chmod 600 "$OUT/.ks-pass"
fi
export KS_PASS="$(cat "$OUT/.ks-pass")"
[ -f "$KS" ] || "$JAVA_HOME/bin/keytool" -genkeypair -keystore "$KS" -storepass:env KS_PASS -keypass:env KS_PASS \
  -alias wff -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=Watch face debug" >/dev/null 2>&1
"$BT/apksigner" sign --ks "$KS" --ks-pass env:KS_PASS --key-pass env:KS_PASS --out "$OUT/$NAME.apk" "$OUT/aligned.apk"
"$BT/apksigner" verify "$OUT/$NAME.apk" && echo "signed OK"

echo "== memory footprint"
"$JAVA_HOME/bin/java" -jar "$GW/memory-footprint.jar" --watch-face "$OUT/$NAME.apk" \
  --schema-version 3 --ambient-limit-mb 10 --active-limit-mb 100 --apply-v1-offload-limitations 2>&1 | tail -6
ls -la "$OUT/$NAME.apk"
echo "install: adb -s \"\$WATCH\" install -r out/$NAME.apk"
