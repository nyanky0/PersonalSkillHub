# Android SDK headless install (no sudo, WSL/Linux)

When `sudo` is unavailable or prompts for a password (background tasks can't authenticate), install the Android SDK + JDK manually into the user's home dir. This is the exact recipe used to build a Capacitor APK on a fresh WSL without root.

## Why
- `apt-get install default-jdk-headless` needs `sudo` and a TTY — fails in background.
- `java`/`sdkmanager` are not preinstalled on WSL/Ubuntu cloud images.
- APK build needs: JDK (17+), cmdline-tools, platform-tools, a `platforms;android-XX`, and `build-tools;XX.0.0`.

## Recipe (all in /home/maulana/, no root)

```bash
cd /home/maulana && mkdir -p android-tools && cd android-tools

# 1. JDK 21 (Temurin, GitHub release — no apt, no sudo)
curl -sL -o jdk.tar.gz "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.5%2B11/OpenJDK21U-jdk_x64_linux_hotspot_21.0.5_11.tar.gz"
mkdir -p jdk && tar -xzf jdk.tar.gz -C jdk --strip-components=1

# 2. Android cmdline-tools (Google direct download)
curl -sL -o cmdtools.zip "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip"
# unzip may not exist -> use python
python3 -c "import zipfile; zipfile.ZipFile('cmdtools.zip').extractall('cmdline-tools')"
mkdir -p cmdline-tools/latest && mv cmdline-tools/cmdline-tools/* cmdline-tools/latest/ 2>/dev/null
chmod +x cmdline-tools/latest/bin/*   # sdkmanager ships non-executable on extract

# 3. Export env (must be set for EVERY sdkmanager / gradlew / cap call)
export JAVA_HOME=/home/maulana/android-tools/jdk
export ANDROID_HOME=/home/maulana/android-tools/sdk
export PATH=$JAVA_HOME/bin:$PATH

# 4. Accept licenses — `yes |` FAILS with "tcsetattr: Inappropriate ioctl"
#    because sdkmanager needs no TTY but `yes` fights the terminal. Use:
mkdir -p $ANDROID_HOME
yes 2>/dev/null | cmdline-tools/latest/bin/sdkmanager --sdk_root=$ANDROID_HOME --licenses >/dev/null 2>&1
# (the 2>/dev/null hides the harmless tcsetattr warning; exit 0 = accepted)

# 5. Install packages
cmdline-tools/latest/bin/sdkmanager --sdk_root=$ANDROID_HOME \
  "platform-tools" "platforms;android-34" "build-tools;34.0.0"
```

## Build the APK (no Android Studio)

```bash
cd /home/maulana/gdb-app
export JAVA_HOME=/home/maulana/android-tools/jdk
export ANDROID_HOME=/home/maulana/android-tools/sdk
export PATH=$JAVA_HOME/bin:$PATH
npm run build              # web assets FIRST
npx cap sync              # copy dist -> android/app/src/main/assets/public
cd android && chmod +x gradlew
./gradlew assembleDebug   # ~1-2 min first run (downloads Gradle deps)
# APK: app/build/outputs/apk/debug/app-debug.apk  (~12 MB)
```

## Verify APK without unzip (unzip often missing)
```bash
python3 -c "import zipfile; z=zipfile.ZipFile('app/build/outputs/apk/debug/app-debug.apk'); n=z.namelist(); print('dex', any(x.endswith('classes.dex') for x in n)); print('manifest', 'AndroidManifest.xml' in n)"
```

## Pitfalls
- **tcsetattr error** on `yes | sdkmanager` → pipe `yes 2>/dev/null` or redirect `</dev/null`. The error is non-fatal but noisy; check `$ANDROID_HOME/licenses` was created to confirm acceptance.
- **sdkmanager Permission denied** after unzip → `chmod +x cmdline-tools/latest/bin/*` (extracted archives often drop the exec bit).
- **`npx cap add android` → "Missing appId"** → `capacitor.config.js` is being read; convert to JSON via `npx cap init "GDB" com.gdb.app --web-dir dist` (arg order: appName THEN appId). Delete the `.js` first — `cap init` refuses a non-JSON config file.
- **JDK version**: Capacitor 6 builds fine on JDK 17 or 21. cmdline-tools needs JDK 17+.
- Reuse same `$JAVA_HOME`/`$ANDROID_HOME` across all three stages; they don't persist between terminal() calls unless re-exported.
