---
name: capacitor-mobile-app
description: "Build Capacitor + Vue 3 + SQLite mobile apps (Android APK)."
version: 1.0.0
author: curator
tags: [capacitor, vue, sqlite, android, mobile, pwa]
---

# Capacitor Mobile App

Build offline-first Android apps using Capacitor + Vue 3 + Tailwind + SQLite.

## When to Use

- User wants an Android app with local storage (no server)
- Converting a web app to mobile APK
- Building offline-first finance/tracking apps
- Need Share Target API for receiving shared text from other apps

## Architecture Decision: PWA vs Capacitor

| Approach | Pros | Cons |
|----------|------|------|
| PWA + IndexedDB | Fast, no native build | Data lost on browser clear, not "real app" |
| Capacitor + SQLite | Real APK, safe data, native APIs | More setup, needs Android SDK |

Choose based on user need. If user says "convert ke apps HP" → Capacitor.

## Project Setup (Linux filesystem only)

**CRITICAL**: Never scaffold/run `npm install` on `/mnt/c/` (Windows mount). WSL permission errors (EACCES on rename/symlink) will block installs. Always use `/home/maulana/` for new projects.

```bash
# 1. Scaffold Vue 3 + Vite (plain JS — avoid TS unless you add tsconfig + vue-tsc)
npm create vite@latest gdb-app -- --template vue
cd gdb-app

# 2. Install deps
npm install
npm install -D tailwindcss @tailwindcss/vite
npm install @capacitor/core @capacitor/cli
npx cap init "GDB" "com.gdb.app" --web-dir dist
npm install @capacitor/android @capacitor/app @capacitor/haptics @capacitor/status-bar @capacitor/share
# Version pinning — verify on npm before install (these drift):
#   @capacitor-community/sqlite v6.x matches Capacitor core v6.x (v8 needs core v8 — mismatch breaks build)
#   jeep-sqlite latest is 2.x, NOT 3.x (^3.0.2 404s)
npm install @capacitor-community/sqlite@^6.0.2 jeep-sqlite@^2.8.0

# 3. Tailwind setup (v4): in vite.config.js add tailwindcss() to plugins; main CSS: @import "tailwindcss";

# 4. Build web asset FIRST, then add Android
npm run build
npx cap add android
npx cap sync
```

**capacitor.config.js** — use PLAIN JS, not `.ts`. TS syntax (`import type`, type annotations) throws `SyntaxError` when loaded as `.js` without a tsconfig.
```js
const config = { appId: 'com.gdb.app', appName: 'GDB', webDir: 'dist' }
export default config
```

**Routing** — use `createWebHashHistory()` + `base: './'` in vite.config. Hash history works for both web preview and Capacitor hybrid without server rewrites.
```js
// src/router/index.js — router lives in src/router/, so imports are ../views/, NOT ./views/
import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '../views/Home.vue'
```

**jeep-sqlite (web testing)** — must add `<jeep-sqlite></jeep-sqlite>` to index.html body AND call `await sqlite.init()` via `new m.default()` before `createConnection`. On native, swap to `@capacitor-community/sqlite` (CapacitorSQLite) — see `src/db/index.js` pattern.

## SQLite Schema Pattern

Use `@capacitor-community/sqlite` for local storage. Initialize on app mount.

**CRITICAL — v6 API call shapes (most common breakage):** the plugin uses POSITIONAL args, not options objects, on the connection. Wrong: `conn.run({statement, values})` or `conn.query(sql, params)` returning rows directly. Right:
```js
import { SQLiteConnection } from '@capacitor-community/sqlite'
const sqlite = new SQLiteConnection(CapacitorSQLite)
await sqlite.createConnection(DB_NAME, false, 'no-encryption', 1, false)   // (db, encrypted, mode, version, readonly)
const conn = await sqlite.retrieveConnection(DB_NAME, false)
await conn.open()
await conn.execute(SCHEMA, false)                 // execute(statements, transaction?)
await conn.run('INSERT ...', [v1, v2], false)    // run(statement, values[], transaction?)
const res = await conn.query('SELECT ...', [])    // query(statement, values[]) -> { values: [...] }
// WEB ONLY (jeep-sqlite): call BEFORE createConnection:  await sqlite.initWebStore()
```
Full working `src/db/index.js` with web/native branching: see `references/sqlite-v6-api.md`.

Key tables for finance app:
- `transactions` (id, type, amount, category_id, note, date, source, user, sumber_dana, is_bekal, created_at)
- `categories` (id, name, type, icon, color)
- `goals` (id, name, target, current)
- `recurring` (id, nama_tagihan, jumlah, tanggal_tagihan, sumber_dana) — auto-debet tagihan
- `settings` (key, value) — flexible key-value: payday, budget, limit_kopi, emergency_target, target_pensiun, whatsapp_number
- `emergency_fund` is NOT a separate table — tracked as a goal named "Dana Darurat" + emergency_target setting

## Share Target API (receive text from other apps)

**KEY CORRECTION — PWA `share_target` does NOT work inside a Capacitor APK.** `share_target` in `manifest.webmanifest` only fires when the app is installed as a PWA from Chrome. In a native APK, sharing from another app will NOT launch your app via that manifest entry. Two separate mechanisms:

1. **PWA mode only** (installed from browser): `share_target` in manifest, action must be `./#/share` (hash router), handle via `route.query.text`.
2. **Native APK (the real one)**: add an Android intent filter to `android/app/src/main/AndroidManifest.xml` inside `<activity>`:
   ```xml
   <intent-filter>
       <action android:name="android.intent.action.SEND" />
       <category android:name="android.intent.category.DEFAULT" />
       <data android:mimeType="text/plain" />
   </intent-filter>
   ```
   Then handle in `MainActivity.java` via `onNewIntent()` — see "Native share-into-app (ACTION_SEND)" pitfall below. `App.addListener('appUrlOpen')` does NOT fire for `ACTION_SEND`.

### Parsing shared text into transactions

Typical bank/e-wallet notification formats (Indonesia):
```
Anda menerima transfer Rp150.000 dari Budi. Saldo: Rp500.000
Pembayaran GOFOOD Rp45.000 ke Resto ABC berhasil. Saldo Rp255.000
```

Parse strategy:
1. Extract amount: regex `Rp[\d.,]+` or `[\d.,]+` near keywords like "transfer", "pembayaran", "bayar"
2. Determine type: keyword matching — "terima"/"masuk" → income, "bayar"/"pembayaran"/"beli" → expense
3. Extract description: text between amount and source/destination
4. Default date: today

## Pitfalls

### Loop Guard — CRITICAL
**NEVER call the same tool with the same or near-identical arguments more than 3 times in a row.** If a tool call fails or returns the same result, STOP and:
1. Re-read the file or re-examine the situation
2. Try a different approach or different arguments
3. If stuck after 3 attempts, ask the user

This applies to: `todo`, `skill_view`, `memory`, `patch`, `write_file`, and ALL other tools. The most common loop patterns are:
- Calling `todo` repeatedly with near-identical content (shuffle wording but same items)
- Calling `skill_view` on the same skill multiple times hoping for different output
- Retrying `memory` add when at capacity without consolidating first

If you feel "I should try one more time with slightly different wording" → STOP. That is the loop. Do something different instead.

### WSL + Windows filesystem
- `npm install` on `/mnt/c/` WILL fail with EACCES (rename/symlink permission denied)
- Solution: work in `/home/maulana/` for new projects
- If project must live on Windows side, run npm from Windows CMD/PowerShell instead

### Capacitor + SQLite
- Must build web assets (`npm run build`) BEFORE `npx cap sync`
- `@capacitor-community/sqlite` requires `jeep-sqlite` for web testing
- Without SDK, can still develop web layer and test in browser

### Android SDK install WITHOUT sudo (fresh WSL / no root)
`apt-get install default-jdk-headless` + `sudo` both fail in background tasks (TTY prompt). Install JDK 21 + cmdline-tools manually into `$HOME` and build the APK with `gradlew`. Full recipe + pitfalls (tcsetattr on `yes`, sdkmanager exec bit after unzip, `cap init` arg order): see `references/android-sdk-headless-install.md`.
Quick version:
```bash
# in /home/maulana/android-tools: download Temurin JDK 21 tarball + cmdline-tools zip; python-unzip the zip; chmod +x cmdline-tools/latest/bin/*
export JAVA_HOME=.../jdk ANDROID_HOME=.../sdk PATH=$JAVA_HOME/bin:$PATH
yes 2>/dev/null | sdkmanager --sdk_root=$ANDROID_HOME --licenses >/dev/null 2>&1   # tcsetattr warning is harmless
sdkmanager --sdk_root=$ANDROID_HOME "platform-tools" "platforms;android-34" "build-tools;34.0.0"
cd gdb-app && npm run build && npx cap sync && cd android && ./gradlew assembleDebug
# APK: app/build/outputs/apk/debug/app-debug.apk (~12 MB)
```

### npm install failures
- If `@capacitor-community/sqlite` gives 404, try `@capacitor-community/sqlite@latest` or check npm registry status
- Some Capacitor plugins have name changes between versions — verify on npmjs.com

### Version pinning — ALWAYS verify on npm before install
- `@capacitor-community/sqlite` v6.x pairs with Capacitor core v6.x. v8 of the plugin needs core v8 — mixing core v6 + sqlite v8 breaks `npx cap sync`/build.
- `jeep-sqlite` latest is 2.x. `^3.0.2` 404s. Use `jeep-sqlite@^2.8.0`.
- If `npm install` errors `EINVALIDPACKAGENAME` → you wrote `@capacitor/community/sqlite` (slash) instead of `@capacitor-community/sqlite` (hyphen).
- If `npm install` errors `ETARGET No matching version` → the version constraint doesn't exist. Run `npm view <pkg> version` to get the real latest, or `npm view <pkg>@6 version` to list a major's releases.

### capacitor.config — use .js, not .ts
- Without a tsconfig + vue-tsc, a `capacitor.config.ts` with `import type { CapacitorConfig }` throws `SyntaxError: Unexpected token '{'`. Write it as plain `export default { appId, appName, webDir }`.

### Router path bug (build failure)
- Router file lives in `src/router/index.js`. Imports to views MUST be `../views/X.vue`, not `./views/X.vue`. Wrong path → `Could not resolve "./views/Home.vue"` and build fails.

### Schema migration for existing apps (adding columns/tables without data loss)

When upgrading an existing app's schema, `CREATE TABLE IF NOT EXISTS` only creates new tables — it does NOT add columns to existing ones. Use a migration pattern:

```js
// In db/index.js ensureConn(), AFTER conn.execute(SCHEMA, false):
// 1. ALTER TABLE for new columns (wrap in try/catch — column may already exist)
const MIGRATIONS = [
  "ALTER TABLE transactions ADD COLUMN user TEXT DEFAULT 'Maulana'",
  "ALTER TABLE transactions ADD COLUMN sumber_dana TEXT DEFAULT 'tunai'",
  "ALTER TABLE transactions ADD COLUMN is_bekal INTEGER DEFAULT 0",
  "ALTER TABLE transactions ADD COLUMN created_at TEXT DEFAULT (datetime('now','localtime'))",
  "ALTER TABLE categories ADD COLUMN icon TEXT DEFAULT ''",
]
for (const sql of MIGRATIONS) {
  try { await conn.run(sql, [], false) } catch (e) { /* column exists — skip */ }
}
```

New tables use `CREATE TABLE IF NOT EXISTS` in SCHEMA. New seed rows use `INSERT OR IGNORE`. Settings keys use `INSERT OR IGNORE INTO settings`.

**CRITICAL**: SQLite ALTER TABLE only supports `ADD COLUMN` — cannot drop/rename columns. Plan schema carefully.

### db.init() helper pattern

Views call `await db.init()` before queries. The init method wraps `ensureConn()`:
```js
const db = {
  async init() { await ensureConn() },
  async run(sql, params = []) { ... },
  async all(sql, params = []) { ... },
  async get(sql, params = []) { ... },
}
```
Without `init()`, the first `db.all()` call in a view may fire before the connection is ready → empty results.

### Vue `<script setup>` import ordering

In Vue `<script setup>`, ALL imports must appear before any code that uses them — same as regular JS. The compiler does NOT hoist named imports. If you write:

```js
const total = computed(() => items.value.reduce(...))  // used here
import { computed } from 'vue'                         // imported after — ReferenceError
```

This crashes at runtime. Always group all imports at the top of `<script setup>`. Linters don't always catch this in SFC files.

### Chart.js + vue-chartjs in Capacitor apps

Finance/tracking apps commonly need charts. Install and register:
```bash
npm install chart.js vue-chartjs
```

```js
// In the Vue component that uses charts:
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement,
  Title, Tooltip, Legend
} from 'chart.js'
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)
```

Use `<Bar :data="chartData" :options="chartOptions" />` in template. Wrap in a fixed-height container (`<div class="h-40">`) — `maintainAspectRatio: false` needed for responsive sizing.

### Feature parity workflow (web → mobile)

When converting a web app to mobile or ensuring parity:
1. Read both codebases — list every view/page and feature on each side
2. Build a gap table: Web has X, App has/missing Y
3. Identify what to skip (e.g., auth if app is offline-only)
4. Upgrade schema first (add columns, tables, settings)
5. Add npm deps (chart libs, etc.)
6. Rewrite views one at a time, most complex first (Home/Dashboard)
7. Build + verify before moving to next view

### Build verification
- After scaffolding, immediately run `npm run build`. A green build (✓ built) is your only proof the wiring is correct before moving to `npx cap add android`.
- Re-runnable probe: `scripts/verify-android-build.sh` checks web build + `db/index.js` syntax + APK validity + SEND intent present + nav tab count.

### Payday holiday adjustment (gajian mundur)

If payday falls on Sunday (or a national holiday), the actual payday shifts earlier. User's rule: "tanggal 25 libur otomatis jadi tanggal 24". Implement `effectivePayday()`:

```js
function effectivePayday(payday, year, month) {
  const dim = new Date(year, month + 1, 0).getDate()
  let day = Math.min(payday, dim)
  const d = new Date(year, month, day)
  // Sunday (0) → shift back 1 day. Saturday is OK for Indonesian banks.
  if (d.getDay() === 0) day = Math.max(1, day - 1)
  return day
}
```

Use this in `cycleRange` for both start and end dates, and in `daysLeft` calculation.

### Batas Harian (daily allowance) — correct formula

**Common bug**: `daysLeft = payday - today.getDate()` gives 1 the day before payday, so `batas harian = sisa budget / 1 = sisa budget` — which looks wrong to the user ("batas harian masih = sisa budget").

Correct logic (matches web reference `btracker-web`):
1. `daysRemaining = diffInDays(today, cycleEndDate) + 1` — include today in the count
2. `batasHarian = sisaUang / max(1, daysRemaining)` — use `balance` (sisa uang), NOT `budgetRemain`

```js
const daysLeft = computed(() => {
  const { end } = cycleRange.value
  const endDate = new Date(end + 'T23:59:59')
  const diff = Math.ceil((endDate - today) / (1000 * 60 * 60 * 24))
  return Math.max(1, diff + 1)  // +1 to include today
})
const dailyAllowance = computed(() => {
  if (settings.value.budget <= 0) return 0
  return Math.max(0, balance.value / daysLeft.value)  // balance, not budgetRemain
})
```

`balance` = opening (budget or totalIncome) - expenses - bekal. `budgetRemain` = budget - expenses only (ignores bekal and income). Always use `balance` for daily allowance.

### Bottom-nav reachability (UX trap)
- When scaffolding multi-page apps, EVERY route must be reachable from the bottom nav. In the GDB build, Kategori & Pengaturan were left out of the 4-tab nav → features existed but were hidden. Put all primary routes as tab buttons (5 tabs fit fine on mobile).

### Native notification auto-capture (NotificationListenerService)

To auto-capture bank/e-wallet notifications without manual sharing, build a custom Android NotificationListenerService registered as a Capacitor plugin. Full recipe: `references/native-notification-listener.md`.

Key steps:
1. Create `GDBNotificationListener.java` extending `NotificationListenerService` — filter by package name, extract text, fire Capacitor event
2. Create `GDBNotifPlugin.java` extending `Plugin` with `@PluginMethod` for `checkPermission`, `openSettings`, `startListening`
3. Register plugin in `MainActivity.java` via `registerPlugin(GDBNotifPlugin.class)` BEFORE `super.onCreate()`
4. Add `<service>` to AndroidManifest with `android:permission="android.permission.BIND_NOTIFICATION_LISTENER_SERVICE"`
5. JS bridge uses `registerPlugin('GDBNotif')` + `addListener('notifCaptured', ...)` → parseTransaction → db.run

**Critical**: `BIND_NOTIFICATION_LISTENER_SERVICE` is a SERVICE-level permission on the `<service>` element, NOT a `<uses-permission>`. Adding it as `<uses-permission>` causes install failure.

User must grant permission manually via Settings → Notification access. Plugin's `openSettings()` launches the correct page.

### Native share-into-app (ACTION_SEND)
- Do NOT rely on `manifest.webmanifest` `share_target` for the APK — it's PWA-only.
- **`App.addListener('appUrlOpen')` does NOT fire for `ACTION_SEND` intents.** Capacitor only routes deep links (custom URL schemes) via that listener, not standard share intents.
- **Correct approach**: Override `onNewIntent()` in `MainActivity.java` to catch share intents, extract `EXTRA_TEXT`, and dispatch to JS via `bridge.eval()`:
  ```java
  // MainActivity.java
  @Override
  protected void onNewIntent(Intent intent) {
      super.onNewIntent(intent);
      setIntent(intent);
      checkShareIntent(intent);
  }

  private void checkShareIntent(Intent intent) {
      if (intent == null) return;
      if (Intent.ACTION_SEND.equals(intent.getAction()) && "text/plain".equals(intent.getType())) {
          String text = intent.getStringExtra(Intent.EXTRA_TEXT);
          if (text != null && !text.isEmpty()) {
              intent.setAction(null);  // prevent re-processing
              runOnUiThread(() -> {
                  getBridge().eval("window.dispatchEvent(new CustomEvent('gdbShare',{detail:" +
                      org.json.JSONObject.quote(text) + "})), null);
              });
          }
      }
  }
  ```
- JS side: `window.addEventListener('gdbShare', e => router.push({path:'/share', query:{text:e.detail}}))`
- Also call `checkShareIntent(getIntent())` in `onCreate()` after `super.onCreate()` to handle cold-start shares.
- **Pitfall**: `BridgeActivity.onResume()` is `final` — you CANNOT override it. Use `onNewIntent()` only.
- **Pitfall**: Must `setIntent(intent)` in `onNewIntent()` so `getIntent()` stays current.
- **Pitfall**: Must clear intent action (`intent.setAction(null)`) after processing, or every `onNewIntent` call re-processes the same share.
- **Pitfall — bridge null on cold-start**: When app is launched via share intent (not already running), `onCreate()` fires before the Capacitor bridge is ready. `getBridge()` or `getBridge().getWebView()` returns null. Fix: store the shared text in a `pendingShareText` field, then retry `dispatchShareToJS()` with a `Handler(Looper.getMainLooper()).postDelayed()` loop (up to 10 retries × 500ms). Once bridge is non-null, `eval()` the custom event and clear the pending text.

### Java regex patching via `patch` tool — NEVER do it

The `patch` tool double-escapes backslashes in `.java` files. A Java regex like `\\d{3}` becomes `\\\\d{3}` after patching, breaking the pattern at runtime. This is especially dangerous for `Pattern.compile()` strings.

**Rule**: When a `.java` file contains regex (`Pattern.compile`, `String.replaceAll`, etc.), always use `write_file` to rewrite the entire file. Never use `patch` on regex-containing Java code.

### Custom Capacitor plugin registration
- `registerPlugin(MyPlugin.class)` in `MainActivity.java` must be called BEFORE `super.onCreate()`. After `super.onCreate()`, the bridge is already initialized and plugin registration is silently ignored.
- `GDBNotifPlugin` singleton pattern: the NotificationListenerService needs a reference back to the plugin to call `notifyListeners()`. Store `instance = this` in constructor. Static `getInstance()` used by service to call `onNotificationCaptured()`. This is simpler than the `handle` field pattern and works across app lifecycle.
- **`BridgeActivity.onResume()` is `final`** — you CANNOT override it. Use `onNewIntent()` for intent handling instead.

### Budget = Saldo Awal (user correction)

Finance apps for single-income users: **Budget IS the opening balance**. The user sets "Budget 3jt" meaning "I have 3jt to spend this cycle". Saldo = Budget - Expenses. If you calculate Saldo = totalIncome - Expenses, it starts at 0 before any income transaction is recorded — the user sees "Saldo: Rp0" despite setting a budget, which is confusing.

Correct pattern:
```js
const balance = computed(() => {
  const opening = settings.value.budget > 0 ? settings.value.budget : totalIncome.value
  return opening - totalExpense.value - totalBekal.value
})
```
If budget is set → use it as opening. If not → fallback to sum of income transactions. Display label should show "Budget" or "Masuk" accordingly.

### Cycle-based filtering (not all-time)

All saldo/budget/kopi calculations MUST be filtered to the active pay cycle (payday to next payday), NOT all-time. Without this filter, historical transactions from previous months inflate totals and the numbers are meaningless.

Pattern: compute `cycleRange` from `payday` setting + `cycleOffset` (0 = current, -1 = last month, etc.), then `tx.filter(t => t.date >= start && t.date <= end)`. Load ALL transactions once, filter in computed properties.

### OCR Receipt Scanner (Tesseract.js + Capacitor Camera)

To let users photograph receipts/struk and auto-parse into transactions:

1. Install deps: `npm install @capacitor/camera tesseract.js --legacy-peer-deps` (legacy-peer-deps needed — capacitor-camera has peer dep conflicts with Capacitor 6)
2. Create `src/utils/ocrScanner.js` — wraps Camera API + Tesseract worker:
   - `captureAndScan()`: open camera → get base64 → run Tesseract OCR → return raw text
   - `parseReceiptText(text)`: regex extract amounts, dates, merchant names from OCR output
   - Tesseract worker options: `logger: false` (suppress verbose progress), `tessedit_pageseg_mode: 6` (assume uniform block of text — receipts)
3. Create `src/views/Scan.vue` — camera button → OCR progress → parsed result preview → edit → save
4. Add camera + storage permissions to AndroidManifest:
   ```xml
   <uses-permission android:name="android.permission.CAMERA" />
   <uses-feature android:name="android.hardware.camera" android:required="false" />
   <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
   <uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
   ```
5. Add route `/scan` + nav button (center elevated FAB in bottom nav works well)

**Pitfall**: Tesseract.js downloads ~4MB traineddata on first run. On slow connections this can take 10-30s. Show a loading indicator with progress. The `eng` language pack is usually sufficient for Indonesian receipts (mixed Indonesian/English).

**Pitfall**: OCR accuracy on receipts is ~60-80%. Always show the parsed result for user confirmation before saving — never auto-save OCR output blindly.

**Pitfall**: Do NOT top-level `import Tesseract from 'tesseract.js'`. This bundles the entire Tesseract worker (~4MB) into the main chunk, slowing app startup even if the user never scans. Use dynamic import: `const Tesseract = await import('tesseract.js')` inside the `scanReceipt()` function.

**Pitfall — account numbers vs amounts**: OCR text from bank transfer screenshots contains both the transfer amount AND the destination account number (8-16 bare digits). A naive "pick the largest number" strategy will select the account number (e.g., `1234567890` = 1.2B) instead of the actual amount (`2.000.000` = 2M). Fix:
1. Regex must **require** either an `Rp` prefix or a thousands-separator pattern (`\d{1,3}(?:[.,]\d{3})+`). Do NOT match bare digit sequences of 8+ characters.
2. Add `isAccountNumber(raw)` guard: if the raw match has no separator dots AND is 8+ digits, skip it.
3. Prefer Rp-prefixed amounts over unprefixed ones when multiple candidates exist.
4. Apply the same guard in ALL parsers: `ocrScanner.js`, `shareParser.js`, AND `GDBNotifPlugin.java` (the native notification parser).

Example of correct regex (JS):
```js
const re = /(?:Rp\.?\s*)(\d{1,3}(?:[.,]\d{3})+(?:[.,]\d{1,2})?)|(?:^|\s)(\d{1,3}(?:[.,]\d{3})+(?:[.,]\d{1,2})?)(?:\s|$)/gm
```

Example of correct regex (Java):
```java
Pattern re = Pattern.compile(
    "(?:Rp\\\\.?\\\\s*)(\\\\d{1,3}(?:\\\\.\\\\d{3})+(?:,\\\\d{1,2})?)|" +
    "(\\\\d{1,3}(?:\\\\.\\\\d{3})+(?:,\\\\d{1,2})?)"
);
```

Account number guard:
```js
function isAccountNumber(raw) {
  const cleaned = raw.replace(/[\s.,]/g, '')
  return /^\d{8,}$/.test(cleaned)
}
```

Full implementation pattern: `references/ocr-receipt-scanner.md`.

### Gradle/AGP upgrade chain (capacitor-camera 8.x)

Adding `@capacitor/camera@8.x` to a Capacitor 6 project triggers a dependency chain that requires upgrading the entire Android build toolchain. The error manifests as `checkDebugAarMetadata` failure: `androidx.core:core:1.17.0` requires compileSdk 36.

Upgrade chain (all must be done together):
```
compileSdkVersion: 34 → 36
targetSdkVersion:  34 → 36
minSdkVersion:    22 → 24    (capacitor-camera's ioncameralib needs minSdk 24)
AGP:              8.2.1 → 8.9.1
Gradle wrapper:   8.2.1 → 8.11.1
```

Also need `platforms;android-36` + `build-tools;36.0.0` installed via sdkmanager:
```bash
/home/maulana/android-tools/cmdline-tools/latest/bin/sdkmanager --sdk_root=$ANDROID_HOME \
  "platforms;android-36" "build-tools;36.0.0"
```

**Pitfall**: Gradle cache corruption (`bcprov-jdk18on-1.79.jar.lock.lock` with 0-byte jar). Fix: `rm -rf ~/.gradle/caches/jars-9/` + `./gradlew --stop` before rebuild. The lock file prevents jar creation even after cache clear — must stop daemon first.

**Pitfall**: After upgrading AGP/Gradle, first build downloads ~200MB of new dependencies. Budget 3-5 minutes.

### NotificationListenerService permission

### Safe-area inset for bottom nav (Android gesture nav)

Android 10+ uses gesture navigation with a system bar at the bottom. A fixed bottom nav `<nav class="fixed bottom-0">` will overlap with the system bar, making buttons un-tappable. Fix both the nav AND the content area above it:

```html
<!-- Content area — push up so content isn't hidden behind nav -->
<div style="padding-bottom: calc(4.5rem + env(safe-area-inset-bottom, 0px))">
  <router-view />
</div>

<!-- Nav bar — extra padding at bottom for system bar -->
<nav class="fixed bottom-0 left-0 right-0" style="padding-bottom: env(safe-area-inset-bottom, 0px)">
```

**Prerequisite**: `index.html` must have `<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />`. Without `viewport-fit=cover`, `env(safe-area-inset-bottom)` always returns 0.

**Pitfall**: Tailwind's `pb-20` or any fixed `padding-bottom` does NOT account for the safe area. Use `calc()` with `env(safe-area-inset-bottom)` instead.

## References

- `references/share-target-parser.md` — Regex patterns for parsing Indonesian bank/e-wallet notifications into transaction data
- `references/android-sdk-headless-install.md` — Install JDK + Android SDK + build APK without sudo (fresh WSL)
- `references/sqlite-v6-api.md` — Correct v6 SQLite call shapes + web/native branching (positional args, `.values`, `initWebStore`)
- `references/native-notification-listener.md` — Build native Android NotificationListenerService as a Capacitor plugin for auto-capturing bank/e-wallet notifications
- `references/gdb-finance-app-features.md` — Feature map (web vs mobile) for GDB finance app, parity checklist, intentionally skipped features
- `references/ocr-receipt-scanner.md` — Camera-based receipt OCR (Tesseract.js + Capacitor Camera): deps, permissions, build toolchain impact, parse patterns, UX flow
- `scripts/verify-android-build.sh` — Ad-hoc verify probe: web build + db syntax + APK validity + SEND intent + nav tab count
