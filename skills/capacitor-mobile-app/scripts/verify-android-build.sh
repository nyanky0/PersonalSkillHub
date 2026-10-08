#!/usr/bin/env bash
# Verify a Capacitor+Vue GDB-style project before handing APK to user.
# Run from project root. No device needed — checks build + APK integrity + intent + nav.
set -e
echo "== 1. web build =="
npm run build > /tmp/verify-build.log 2>&1 && echo "web build: PASS" || { echo "web build: FAIL"; tail -15 /tmp/verify-build.log; exit 1; }
echo "== 2. JS syntax (DB layer is the usual culprit) =="
node --check src/db/index.js && echo "db/index.js: OK" || echo "db/index.js: SYNTAX ERR"
echo "== 3. APK exists & valid =="
APK=android/app/build/outputs/apk/debug/app-debug.apk
if [ -f "$APK" ]; then
  python3 -c "import zipfile,sys;z=zipfile.ZipFile(sys.argv[1]);n=z.namelist();print('APK valid:', 'classes.dex' in [x for x in n if x.endswith('classes.dex')] and 'AndroidManifest.xml' in n)" "$APK"
  ls -lh "$APK" | awk '{print "APK size:", $5}'
else
  echo "APK: MISSING"
fi
echo "== 4. SEND intent (native share-in) present =="
grep -q "android.intent.action.SEND" android/app/src/main/AndroidManifest.xml && echo "SEND intent: OK" || echo "SEND intent: MISSING"
echo "== 5. bottom-nav tab count (every route must be reachable) =="
grep -c "path:" src/App.vue | xargs echo "tab entries:"
