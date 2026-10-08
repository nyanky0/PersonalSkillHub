---
name: windows-hardware-tuning
description: "Master Windows OS, APU/iGPU Dev Tuning, Power Management, WSL administration, and UI diagnosis."
version: 2.0.0
author: Hermes Agent & Antigravity
metadata:
  hermes:
    tags: [windows, wsl, optimization, battery, apu]
---

# Windows Hardware Tuning



## Sub-Module: windows

## Credential Management

- Never hardcode passwords in scripts — use Windows Credential Manager:
  ```powershell
  # Store
  cmdkey /generic:"MyService" /user:"admin" /pass:"secret"
  # Retrieve in script
  $cred = Get-StoredCredential -Target "MyService"
  ```
- For scripts, use `Get-Credential` and export securely:
  ```powershell
  $cred | Export-Clixml -Path "cred.xml"  # Encrypted to current user/machine
  $cred = Import-Clixml -Path "cred.xml"
  ```

## Silent Failures

- Windows Defender silently quarantines downloaded scripts/executables — check quarantine if script disappears
- Group Policy overrides local settings silently — `gpresult /r` to see what's actually applied
- Antivirus real-time scanning blocks file operations intermittently — add exclusions for build/automation folders
- PowerShell `-ErrorAction SilentlyContinue` hides problems — use `Stop` and handle explicitly

## Symbolic Links

- Creating symlinks requires admin OR SeCreateSymbolicLinkPrivilege — regular users fail silently
- Enable Developer Mode for symlinks without admin: Settings → For Developers → Developer Mode
- `mklink` is CMD-only, PowerShell uses `New-Item -ItemType SymbolicLink`

## Script Signing

- Unsigned scripts fail on restricted machines with confusing errors — sign for production:
  ```powershell
  $cert = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert
  Set-AuthenticodeSignature -FilePath script.ps1 -Certificate $cert
  ```
- AllSigned policy requires ALL scripts signed including profile.ps1

## Operational Safety

- Always `-WhatIf` first on destructive operations — `Remove-Item -Recurse -WhatIf`
- `Start-Transcript` for audit trail — forgotten until incident investigation
- NTFS permissions: `icacls` for CLI, but inheritance rules are non-obvious — test changes on copy first

## WinRM Remoting

- Enable correctly: `Enable-PSRemoting -Force` isn't enough on workgroups
- Workgroup machines need TrustedHosts: `Set-Item WSMan:\localhost\Client\TrustedHosts -Value "server1,server2"`
- HTTPS remoting needs certificate setup — HTTP sends credentials readable on network

## Event Logging

- Scripts should log to Windows Event Log for centralized monitoring:
  ```powershell
  New-EventLog -LogName Application -Source "MyScript" -ErrorAction SilentlyContinue
  Write-EventLog -LogName Application -Source "MyScript" -EventId 1000 -Message "Started"
  ```
- Custom event sources require admin to create — create during install, not runtime

## File Locking

- Windows locks files aggressively — test file access before operations:
  ```powershell
  try { [IO.File]::OpenWrite($path).Close(); $true } catch { $false }
  ```
- Scheduled tasks writing to same file as user → conflicts. Use unique temp files and atomic rename

## Temp File Hygiene

- `$env:TEMP` fills silently — scripts should cleanup with `try/finally`:
  ```powershell
  $tmp = New-TemporaryFile
  try { ... } finally { Remove-Item $tmp -Force }
  ```
- Orphaned temp files accumulate across reboots — unlike Linux /tmp

## Service Account Gotchas

- Services run in different user context — `$env:USERPROFILE` points to system profile, not user's
- Network access from SYSTEM account uses machine credentials — may fail where user succeeds
- Mapped drives don't exist for services — use UNC paths `\\server\share`

---

## Sub-Module: battery-runtime-profiling

# Battery Runtime Profiling & Power Plan Management

## Use when
Need to analyze laptop battery runtime estimates, create custom Windows power plans for battery optimization, or switch between performance/battery-saver profiles on a Lenovo laptop (or any Windows laptop with powercfg).

## Overview
This skill covers reading battery health and runtime estimates from Windows via WSL, creating custom power plans with specific CPU/display thresholds, and managing GUID-based plan switches. It addresses the gotcha where average drain rates include suspend and AC-connected time, leading to misleading runtime estimates.

## Steps

### 1. Export Windows Battery Report
```powershell
powercfg /batteryreport /output C:\battery_report.xml /xml
```
Then read from `/mnt/c/battery_report.xml` in WSL.

### 2. Parse Runtime Estimates (XML structure)
```xml
<RuntimeEstimates>
  <DesignCapacity>
    <Capacity>60000</Capacity>
    <ActiveRuntime>PT2H22M43S</ActiveRuntime>
  </DesignCapacity>
  <FullChargeCapacity>
    <Capacity>57090</Capacity>
    <ActiveRuntime>PT2H15M48S</ActiveRuntime>
  </FullChargeCapacity>
</RuntimeEstimates>
```

### 3. Calculate Realistic Drain (filter off-charger only)
**Just run `scripts/battery_runtime.py`** — it prints battery health + expected runtime + real battery-only drain rates in one shot. Recreate the report first with step 1, then `python3 battery_runtime.py`.

Manual path: usage entries live in `<RecentUsage><UsageEntry>` (NOT `<EnergyDrains><Drain>` as older versions had). Filter entries where Ac="0" and EntryType="Active", compute mWh gap / duration between consecutive entries:
```
drain_rate_mW = (prev_capacity - curr_capacity) / ((ts_now - ts_prev) / 3600)
```
Capacity values in the XML are **mWh** directly (`<DesignCapacity>60000</DesignCapacity>` = 60 Wh).

**Pitfall**: Average drain includes AC-connected and suspend time. This inflates estimates massively. Always filter for battery-only active usage.

### Actual XML structure (Windows 11 batteryreport /xml)
The elements carry data as **nested text, NOT attributes**:
```xml
<RuntimeEstimates>
  <DesignCapacity><Capacity>60000</Capacity><ActiveRuntime>PT2H17M46S</ActiveRuntime></DesignCapacity>
  <FullChargeCapacity><Capacity>56230</Capacity><ActiveRuntime>PT2H9M7S</ActiveRuntime>...</FullChargeCapacity>
</RuntimeEstimates>
<Batteries><Battery>
  <DesignCapacity>60000</DesignCapacity>
  <FullChargeCapacity>56230</FullChargeCapacity>
  <CycleCount>148</CycleCount>
</Battery></Batteries>
<RecentUsage>
  <UsageEntry Timestamp="2026-09-03T08:25:02Z" Ac="0" EntryType="Active" ChargeCapacity="43060" .../>
  <UsageEntry Ac="1" EntryType="ChargerConnected" .../>
</RecentUsage>
```
Gotchas:
- **RecentUsage entry key is `Timestamp`** (capital T), not `TimeStamp`.
- **Timestamp format is inconsistent** — some entries end `Z`, some don't. Use a robust parser (try `replace('Z','+00:00')`, fall back to bare `fromisoformat`).
- **Battery** lives under `<Batteries><Battery>` with text child elements, not a bare attribute-carrying node.

### PowerShell XML Parsing Pattern
```powershell
[xml]$xml = Get-Content "C:\battery_report.xml"
$namespace = $xml.DocumentElement.NamespaceURI
$ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
$ns.AddNamespace("br", $namespace)
# Use br: prefix for all Find calls
```

### Python XML Parsing Pattern (WSL)
```python
import xml.etree.ElementTree as ET
ns = {'br': 'http://schemas.microsoft.com/battery/2012'}
root = ET.parse('/mnt/c/battery_report.xml')
drains = root.findall('.//br:Drain', ns)
for d in drains:
    ac = d.get('Ac', '1')  # 0 = on battery
    drained = int(d.get('StartChargeCapacity')) - int(d.get('EndChargeCapacity'))
```

### 4. Create Custom Power Plans
```powershell
# Duplicate Balanced as template
$output = powercfg /duplicatescheme 381b4222-f694-41f0-9685-ff5bb260df2e
# Extract GUID from output: "Power Scheme GUID: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
if ($output -match 'Power Scheme GUID: ([0-9a-fA-F\-]+)') {
    $plan = $matches[1]
}

# Battery-saver: throttle CPU, lower brightness
powercfg /setdcvalueindex $plan SUB_PROCESSOR PROCTHROTTLEMIN 5
powercfg /setdcvalueindex $plan SUB_PROCESSOR PROCTHROTTLEMAX 30
powercfg /setdcvalueindex $plan SUB_VIDEO DISPLAY_BRIGHTNESS 30

# Activate plan
powercfg /setactive $plan

# Export for portability
powercfg /export C:\power_plans\my_plan.pow $plan
```

### 5. Switch Plans
```powershell
powercfg /setactive <GUID>
```

### Common GUIDs (Lenovo LOQ 16" Intel)
- **Balanced**: `381b4222-f694-41f0-9685-ff5bb260df2e`
- **Ultimate Performance**: `79bce170-4242-404a-97ba-20dcfb9e5e7a`

### Expected Runtime Estimates (Lenovo LOQ 16" Intel)
| Plan | CPU Max (battery) | Brightness | Est. Runtime |
|------|-------------------|------------|-------------|
| Ultimate Performance | 100% | 80% | ~1.5 hr |
| Balanced | 50-80% | 50% | ~2-3 hr |
| Battery Saver 5hr | 30% | 30% | ~4-5 hr |

### "Power plan saver tapi masih boros" — diagnose the REAL idle consumers

A power plan throttles CPU + brightness ONLY. If the user reports the battery
still drains fast on the saver plan, check these in order (each is a bigger
lever than any plan setting):

1. **dGPU idle**: gaming laptops keep the dGPU awake even at 0% util. Check
   `nvidia-smi --query-gpu=utilization.gpu,power.draw,temperature.gpu --format=csv`
   (via a `.ps1` file — inline WSL `-Command` mangles `&` and `$_`). RTX 4050
   idles ~4W doing nothing. Fix is per-app GPU assignment (Settings → Display →
   Graphics → "Power saving"/iGPU), NOT a powercfg setting — there is none for dGPU.
2. **WSL/Docker VM**: `vmmemWSL` eats GBs of RAM + CPU while WSL host is up.
   Query via `Get-Process vmmemWSL`. If the user doesn't need WSL on battery,
   `wsl --shutdown` (optionally automated by the auto-switcher) is a big win.
3. **RAM full / memory compression**: `TotalPhysicalMemory/1GB` vs
   `FreePhysicalMemory/1MB` — compression + swap keeps CPU busy. Cause is usually
   browser tab count (Chrome/Edge + edgewebview2 stacks).
4. **Brightness/refresh** last — already covered by the plan, verify with
   `WmiMonitorBrightness.CurrentBrightness` + `Win32_VideoController.CurrentRefreshRate`.

Set expectations: runtime math is `capacity / current_drain`. Saver plan at 11W
gives 5h only if the consumers above are actually off; a busy browser + dGPU idle
alone can sit at 20-30W → 2h no matter the plan.

### Pitfalls
- **Hardcoding GUIDs fails**: `powercfg /duplicatescheme` returns a dynamic GUID. Always parse from output.
- **XML namespace prefix required**: ElementTree/SelectSingleNode needs namespace manager on Windows battery XML.
- **Drain rate misleading**: Including AC/suspend entries gives 45W average (implies 100+ day runtime). Filter `Ac="0"` and `EntryType="Active"` for real estimates.
- **CSV via WSL**: Windows `powercfg /batteryreport /output report.csv` uses `\r\n` — strip carriage returns or parse as text.

## WSL boundary & the batterai switcher

When driving Windows power/battery from WSL, the split matters (full detail in
`references/wsl-vs-windows-battery-control.md`):

- `powercfg` (query + `/setactive`) runs fine from WSL — wrap it in a bash alias
  (e.g. `~/.local/bin/batterai`) for one-word plan switching (`batterai saver|hemat|perf`).
- **Changing refresh rate/brightness/monitor mode does NOT work from WSL** —
  `ChangeDisplaySettings` fails cross-session. Write a reversible `.bat` to the
  Windows Desktop (60Hz ↔ 144Hz) and have the user double-click it.
- Reading GPU/refresh is via `Get-CimInstance Win32_VideoController` from a `.ps1`
  file, not inline `-Command` (WSL strips `$_`).
- If you attempt the `user32` refresh-rate route anyway, `references/refresh-rate-and-display-control.md`
  has the full PowerShell DEVMODE P/Invoke gotchas (hardcode `dmSize=220`, use
  `[uint16]` not `[ushort]`, `deviceName` must be `""`) — and why on gaming panels
  you usually end up telling the user to use Display Settings instead.

## Auto power-plan switcher (plug/unplug watcher)

Windows has no native "switch plan on AC connect/disconnect". Build a hidden PowerShell watcher loop instead. Full working script + launcher + pitfalls in `references/power-plan-auto-switcher.md`.

Core loop:
```powershell
while ($true) {
    $b = Get-CimInstance Win32_Battery
    $onAC = ($b.BatteryStatus -eq 2)   # 2 = plugged, 1 = discharging
    $target = if ($onAC) { $AC_GUID } else { $BAT_GUID }
    if ($target -ne $last) { powercfg /setactive $target; $last = $target; log }
    Start-Sleep -Seconds 15
}
```
- Switch ONLY when plan changed — no powercfg spam every tick.
- Log every switch to `Desktop\PowerWatcher\log.txt` for verification.
- **Autostart without flash**: copy a `.vbs` containing
  `CreateObject("Wscript.Shell").Run "powershell.exe ... -WindowStyle Hidden -File ""...power-watcher.ps1""", 0, False`
  into `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\`. `-WindowStyle Hidden` alone still flashes briefly; VBS `0` window mode is the no-flash trick.
- **Hardcode the log path** (`C:\Users\<name>\...`). `$env:USERPROFILE` under a service/odd-context PowerShell can resolve to a different user and silently log nowhere.

### WSL launch pitfalls (all hit in practice)
- **`cmd.exe /c 'start ...'` from a WSL cwd under `/mnt/...` (UNC `\\wsl.localhost\...`) HANGS** — cmd can't handle UNC cwd, waits forever. Don't `cd /mnt/...` then cmd; launch via `powershell.exe -Command "wscript.exe 'C:\...\start-hidden.vbs'"` instead (no UNC path involved).
- Inline `-Command "..."` strips `$_` when invoked from WSL (bash eats it). Any script using `$_`/`$()` logic must live in a `.ps1` file run with `-File`, not inline. (Same rule already noted for Win32_VideoController.)
- Verify a background watcher via its log file, not process list: `tail Desktop\PowerWatcher\log.txt` shows the last switch; a fresh entry = loop alive.

## Verification
```powershell
powercfg /list
powercfg /query <GUID>
```

---

## Sub-Module: windhawk-mod-dev

# Windhawk Mod Development Skill

Windhawk adalah **marketplace kustomisasi native untuk Windows** (by ramensoftware / Michael Maltsev a.k.a. `m417z`), footprint ~1 MB RAM. Sebuah **mod = satu file C++ (`.wh.cpp`)** yang dikompilasi jadi DLL, lalu di-inject engine Windhawk ke dalam **proses target** (mis. `explorer.exe`). Mod jalan di dalam konteks proses target, bisa hook fungsi, manipulasi memory, inject XAML, dst.

Skill ini ngumpulin: anatomi mod, referensi API lengkap, pola hooking, toolchain, dan alur komunitas/publishing. Sumber canonical: wiki `github.com/ramensoftware/windhawk/wiki` + repo `windhawk-mods` (592 mod resmi) + repo utama `windhawk`.

## When to Use

- User minta bikin mod Windhawk baru / modifikasi mod existing
- Kustomisasi Windows 11 (taskbar, start menu, explorer, dsb.) via Windhawk
- Debug mod yang gagal compile / nggak jalan / crash
- Baca/pahami source code mod orang lain buat referensi
- Don't use for: kustomisasi via ExplorerPatcher/StartAllBack (beda tool), atau tweak registry sederhana tanpa hooking

## Prerequisites

- **Windhawk app** terinstall (portable/installer) — editor bawaan punya compile + deploy mod. Download: `windhawk.net`
- **Compile offline**: Clang 20 (mingw-w64, toolchain `llvm-mingw` dari `mstorsjo`), mode **C++23** (sejak Windhawk v1.7). Flag kompilasi lengkap bisa dilihat di editor lewat **Ctrl+P → `compile_flags.txt`**.
- Header resmi buat mod: `windhawk_api.h` (API publik), `windhawk_api_internal.h`, `windhawk_utils.h` (helper). Ada di repo `windhawk-mods/.vscode/windhawk_headers_<versi>/`.
- **VS Code extension** `windhawk` (folder `src/windhawk-vscode`) untuk install/compile/list mod dari editor.
- Repo lokal (sudah di-clone di mesin user): `C:\Users\yudah\windhawk-learning\{windhawk, windhawk-mods}` — pakai `read_file`/`search_files` buat baca source 592 mod + engine.

## Anatomi Mod (struktur file)

Satu mod `.wh.cpp` berisi 4 blok opsional + kode:

```cpp
// ==WindhawkMod==           <- metadata wajib
// @id              mod-id-1      (unik; hanya 0-9 a-z "-")
// @name            My Mod        (bisa dilokalisasi: @name:fr-FR ...)
// @description     ...
// @version         1.0           (WAJIB naik tiap publish update)
// @author          Nama
// @github          https://github.com/xxx
// @include         explorer.exe  (wildcard * ? + env var %SystemRoot% ok)
// @exclude         foo.exe
// @architecture    x86-64        (x86 / amd64 / arm64 / x86-64)
// @compilerOptions -lcomctl32 -lgdi32
// ==/WindhawkMod==

// ==WindhawkModReadme==        <- markdown, img hanya i.imgur.com + raw.githubusercontent.com
/* ... */
// ==/WindhawkModReadme==

// ==WindhawkModSettings==      <- YAML
/*
- BooleanOption: true
  $name: ...
  $description: ...
- NumberOption: 1234
- StringCombobox: option1
  $options: [option1: Desc, option2: Desc]
- NestedOptions:
    - NestedNumber: 5
- ArrayOfStrings: [a, b, c]
*/
// ==/WindhawkModSettings==
```

**@include/@exclude** menentukan proses mana yang di-inject. Tanpa `@architecture` = x86 + x86-64. `@compilerOptions` nambah flag linker (`-l<lib>`).

## Mod Lifetime & Callbacks

Urutan (mod di-load sebelum proses jalan): `Wh_ModInit` → (implicit `Wh_ApplyHookOperations`) → `Wh_ModAfterInit` → tunggu event → `Wh_ModSettingsChanged` (saat setting diubah) → `Wh_ModBeforeUninit` → hooks dilepas → `Wh_ModUninit`. Kalau di-load ke proses yang sudah jalan, semua event di thread Engine.

```cpp
BOOL Wh_ModInit();                 // return TRUE = sukses; tempat pasang hook
void Wh_ModAfterInit();            // setelah hook selesai di-apply
void Wh_ModBeforeUninit();         // sebelum hook dilepas
void Wh_ModUninit();               // setelah hook dilepas
void Wh_ModSettingsChanged();      // varian 1
BOOL Wh_ModSettingsChanged(BOOL* bReload); // varian 2: return FALSE=unload, *bReload=TRUE=reload
```

## API Inti (ringkas)

Lihat `references/windhawk-api.md` untuk daftar lengkap + signature. Inti yang paling dipakai:

- **Log**: `Wh_Log(L"...", ...)` — hanya dievaluasi kalau log aktif.
- **Setting**: `Wh_GetIntSetting(L"Nama")`, `Wh_GetStringSetting(L"Nama")` (+ `Wh_FreeStringSetting`). Nama nested pakai titik: `L"Nested.Sub"`.
- **Storage lokal** (persist per mod): `Wh_GetIntValue/Wh_SetIntValue`, `Wh_GetStringValue/Wh_SetStringValue`, `Wh_GetBinaryValue/Wh_SetBinaryValue`, `Wh_DeleteValue`, `Wh_GetModStoragePath`.
- **Hook**: `Wh_SetFunctionHook(target, hook, &orig)` → `Wh_RemoveFunctionHook(target)` → `Wh_ApplyHookOperations()` (auto dipanggil setelah ModInit; hindari panggil manual, lambat).
- **Symbol**: `Wh_FindFirstSymbol(module, opts, &findData)` / `Wh_FindNextSymbol` / `Wh_FindCloseSymbol` — resolve alamat fungsi non-exported via PDB symbol server Microsoft.
- **Lainnya**: `Wh_Disasm(address, &result)`, `Wh_GetUrlContent(url, opts)` / `Wh_FreeUrlContent`.
- **Konstanta**: `WH_MOD_ID` (L"my-mod"), `WH_MOD_VERSION` (L"1.0").

## Pola Hooking (PALING penting)

Detail + contoh kode di `references/hooking-patterns.md`. Ringkasan 4 pola utama:

1. **GetProcAddress + Wh_SetFunctionHook** (paling umum, 342/592 mod) — hook fungsi yang **di-export** DLL. Contoh: block Win+V hook `RegisterHotKey` di user32.dll; shrink address bar hook `GetSystemMetricsForDpi`.
2. **Symbol hooking via `WindhawkUtils::HookSymbols`** — hook fungsi **internal/non-exported** (mis. method private TaskbarView di explorer.exe) dengan resolve nama PDB symbol dari symbol server Microsoft. Pakai struct `SYMBOL_HOOK` (list nama symbol + prototype + hook + optional flag).
3. **Window subclassing** — `WindhawkUtils::SetWindowSubclassFromAnyThread` (bisa dari thread mana pun, beda dgn `SetWindowSubclass`).
4. **XAML diagnostics injection** (teknik styler mods) — hook `InitializeXamlDiagnosticsEx` di `Windows.UI.Xaml.dll` buat manipulasi resource WinUI 3 (taskbar/start menu/notification center). Ini yang dipakai **Taskbar Styler / Start Menu Styler / Notification Center Styler** buat apply tema CSS-like.

Helper umum ada di `windhawk_utils.h` (include `<windhawk_utils.h>`): `WindhawkUtils::SetFunctionHook` (wrapper typed), `WindhawkUtils::SYMBOL_HOOK` + `HookSymbols`, `WindhawkUtils::StringSetting` (RAII string), `SetWindowSubclassFromAnyThread`.

## Toolchain & Compile

- Sejak **v1.7**: **Clang 20** (mingw-w64 / llvm-mingw), **C++23**.
- Editor Windhawk kompilasi otomatis saat save; log error tampil di output window.
- `Ctrl+P` di editor → pilih `compile_flags.txt` buat lihat flag persis.
- Engine pakai library: **MinHook** (detour), **Zydis** (disassembler), **phnt** (header native API NT), **DIA** (debug symbols).
- Arsitektur source utama (`src/windhawk/`): `app/`, `engine/` (mod.h, mods_api.h, inject_shellcode, MinHook, Zydis, phnt), `shared/`, `scripts/`. Plus `windhawk-core`, `windhawk-frontend`, `windhawk-vscode`, `windhawk-webview-ipc-contract`.

## Alur Komunitas & Publishing

- **Katalog resmi**: `windhawk.net` — mod bisa dilihat + install langsung dari app Windhawk.
- **Repo resmi**: `github.com/ramensoftware/windhawk-mods` (592 mod). Diskusi: GitHub Discussions + **Discord** (link di README repo utama).
- **Submit mod baru** = PR berisi **satu file** `mods/<mod-id>.wh.cpp`. Syarat: `@github` metadata WAJIB ada & match profile author PR; `@twitter` harus milik author & bisa diverifikasi; tanpa `@license` = MIT.
- **Submit update** = PR ubah file yang sama, `@version` WAJIB naik.
- Author utama: `m417z` (Michael Maltsev) — styler mods + guide tema di repo `ramensoftware/windows-11-taskbar-styling-guide`.
- Mod dari author lain (fork/personal): cari di GitHub `windhawk-mods` (mis. Nishanth1409, Bo0ii).

## Key Resources

- Wiki pembuatan mod: `github.com/ramensoftware/windhawk/wiki/Creating-a-new-mod`
- Wiki mod lifetime: `github.com/ramensoftware/windhawk/wiki/Mod-lifetime`
- Repo mods: `github.com/ramensoftware/windhawk-mods`
- Repo utama: `github.com/ramensoftware/windhawk`
- Guide styling taskbar: `github.com/ramensoftware/windows-11-taskbar-styling-guide`
- Thread komunitas: elevenforum.com topic "Windhawk Mods (Official Topic)"

## Pitfalls

- **`Wh_ApplyHookOperations` sangat lambat** — idealnya semua hook dipasang di `Wh_ModInit` saja, jangan panggil manual berulang.
- **`Wh_SetFunctionHook` nggak boleh** dipanggil setelah `Wh_ModBeforeUninit` return; `Wh_RemoveFunctionHook` nggak boleh sebelum `Wh_ModInit` return.
- **@version WAJIB naik** tiap publish, kalau nggak PR update ditolak.
- **@id hanya karakter `0-9`, `a-z`, `-`** — no underscore/uppercase.
- **Gambar di readme** hanya dari `i.imgur.com` + `raw.githubusercontent.com`.
- **Wildcard @include**: `*` = sequence apa pun, `?` = satu karakter; `%ProgramFiles%` selalu native, pakai `%ProgramFiles(X86)%` buat 32-bit.
- **x86-64 punya arti khusus** di ARM64 (lihat wiki @architecture) — taskbar/explorer di Windows 11 umumnya `@architecture x86-64`.
- **Mod di-load per proses target** — kalau target `*` (semua proses), mod jalan di tiap proses; hati-hati overhead.
- **Symbol hooking butuh download PDB** (symbol server Microsoft) — first-run lambat, ada cache online (`WH_HOOK_SYMBOLS_OPTIONS.onlineCacheUrl`).

## Setup & Apply Setting di Mesin Ini

Lokasi penting (tervalidasi di mesin user):
- Install: `C:\Program Files\Windhawk\` (engine version di `Engine\1.7.3`).
- Data global: `C:\ProgramData\Windhawk\` — berisi `userprofile.json` (daftar mod terinstall + flag `disabled`), `ModsSource\` (source `.wh.cpp` mod terinstall), `Engine\Mods\64\` (DLL compiled), `Engine\ModsWritable\mod-status\` (status load per proses, UTF-16 `explorer.exe|Loaded`).
- **Setting mod** disimpan di registry **HKLM**: `HKLM\Software\Windhawk\Engine\Mods\<mod-id>\Settings` (REG_SZ/REG_DWORD, nama pakai titik mis. `images.imageSource`). Flag enable/disable di key induk (`Disabled` REG_DWORD).
- Baca setting: `reg query "HKLM\Software\Windhawk\Engine\Mods\<id>\Settings" /s`.

**Cara apply setting tanpa buka UI** (untuk mod yang sudah terinstall):
1. Tulis nilai baru ke HKLM — butuh **admin** (shell biasa kena `Access is denied`). Pakai: `powershell.exe -NoProfile -Command "Start-Process reg.exe -ArgumentList 'import','C:\path\x.reg' -Verb RunAs -Wait"` (muncul UAC, user klik Yes).
2. Restart `explorer.exe` biar mod re-inject + baca setting baru: `taskkill /f /im explorer.exe` lalu `cmd.exe /c "start explorer.exe"` (taskkill butuh admin juga kalau explorer jalan; start explorer via cmd biar nggak nge-hang bash).
3. Verifikasi: cek `Engine\ModsWritable\mod-status\` ada entry `<pid-explorer>_<mod-id>` + isinya `explorer.exe|Loaded`.

Catatan: jangan edit `.wh.cpp` di `ModsSource` untuk ganti setting — itu source, bukan setting aktif. Setting aktif ada di registry.

## Verification

- Mod compile tanpa error di editor (log output bersih).
- Setelah enable, efek muncul di proses target; cek log `Wh_Log` kalau diaktifkan.
- `Wh_ModInit` return `TRUE` (kalau `FALSE`, mod langsung unload tanpa error jelas — tambah `Wh_Log` buat debug).
- Untuk baca source mod: `read_file` file `.wh.cpp` di `C:\Users\yudah\windhawk-learning\windhawk-mods\mods\`.

---

## Sub-Module: windows-pc-optimization

# Windows PC Optimization — APU/iGPU + Dev Stack + Gaming

## When to Use

User reports low FPS on APU/iGPU laptop despite hardware being "good enough", or needs Game/Work mode toggle for conflicting dev stack (SAP B1, Docker/WSL, SQL Server, PostgreSQL, Apache) vs competitive gaming. Also when sizing UMA Frame Buffer, configuring Adrenalin, or managing services.

## Core Principles

### 1. APU = Shared Thermal Budget
CPU and iGPU share same die, VRM, thermal budget. When CPU cores saturated (SAP/Tomcat/Java/SQL), GPU clock drops → linear FPS loss (200→80). Diagnosis: GPU clock <1500 MHz under load → thermal/power starvation.

### 2. iGPU Shares System RAM
UMA Frame Buffer (BIOS) controls reserved RAM as "dedicated VRAM". **4 GB optimal** for Valorant/osu! + dev stack on 32GB DDR5. 0 GB = dynamic pinning thrash (10-15% FPS loss). 8 GB = over-reserves (no FPS gain for Valorant).

### 3. Service Classification
- **DEV-CRITICAL** (never kill): SAP Service Layer (b1s50000-10), B1ServerTools, SQL Server, B1ClientAgent, Tomcat/Java
- **GAME-KILL** (kill during gaming): Docker/WSL, PostgreSQL, Laragon/Apache, browsers, WhatsApp
- **PERMANENT-OFF** (disabled by default): SAP WebClient, telemetry services

### 4. Anti-Cheat Safety
Never disable kernel features, VBS, Memory Integrity, WinDefend. Anti-Lag in Adrenalin: OFF (Vanguard false-positive risk). Safe: power plan, registry Game Mode, mouse latency, telemetry services.

## Workflow

### Step 1: Scan Current State
```powershell
Get-Service | Where-Object { $_.Status -eq 'Running' } | Select-Object Name, DisplayName, StartType
Get-Process | Sort-Object WS -Descending | Select-Object ProcessName, RAM_MB, Id
Get-CimInstance Win32_PhysicalMemory | Select-Object Capacity, Speed
```

### Step 2: Identify Service Origins (critical: don't assume process=application)
```powershell
Get-Process httpd -ErrorAction SilentlyContinue | ForEach-Object {
  $cim = Get-CimInstance Win32_Process -Filter "ProcessId = $($PSItem.Id)"
  Write-Host "PID $($PSItem.Id): $($cim.CommandLine)"
}
Get-CimInstance Win32_Service | Where-Object { $_.PathName -match 'httpd|apache|laragon' }
```

### Step 3: Create Toggle Scripts
- `-Mode Game`: Kill GAME-KILL services, set High Performance power plan
- `-Mode Work`: Start DEV-CRITICAL + GAME-KILL services, restore balanced power plan

### Step 4: One-Time Registry Tweaks
Apply `gaming-tweaks.reg` once (HPET, mouse latency, Game Mode, privacy/telemetry). Requires reboot.

### Step 5: Verify After Optimization
Check RAM available (should be 25-27 GB after Game Mode), GPU clock (should be >2000 MHz under gaming), Memory Compression (<200 MB).

## Pitfalls

### ❌ "Kill SAP to fix FPS"
**WRONG.** SAP Service Layer is dev-critical. Kill only Docker/WSL, PostgreSQL, Laragon/Apache, browsers, telemetry.

### ❌ "UMA = 0 is best (max system RAM)"
**WRONG.** Dynamic VRAM pinning adds latency. Fixed 4 GB = lower latency, stable FPS.

### ❌ "httpd = Laragon"
**WRONG.** On SAP B1 machines, httpd is SAP Service Layer Apache (11 instances). Check `Win32_Service.PathName` before killing.

### ❌ "Anti-Lag improves FPS"
**WRONG on Vanguard machines.** Anti-Lag can trigger Vanguard false positives.

### ❌ "Gaming on battery"
**CRITICAL.** Always verify user is plugged in. On battery, APU runs at ~15W → iGPU capped at ~800 MHz.

## Benchmark Reference (verified Sep 2026)

### GPU: Radeon 780M equivalents
| GPU | Aggregate Score | vs 780M |
|-----|:----:|:----:|
| Radeon 780M | **16.21** | baseline |
| GTX 1650 | 18.88 | +16% |
| RX 6400 | ~14.5 | -10% |

### Valorant FPS on 780M (1080p low)
- Stock, no background load: 200-280 FPS
- With SAP + Docker + SQL running: 80-120 FPS
- On battery: 60-80 FPS

## Templates
- `templates/Toggle-PC-Mode.ps1` — Game/Work toggle engine
- `templates/gaming-tweaks.reg` — One-time registry apply
- `templates/[GAME MODE].bat` — Wrapper
- `templates/[WORK MODE].bat` — Wrapper

---

## Sub-Module: windows-ui-diagnostics

# Windows UI Diagnostics — window tree vs what the shell shows

## When to use

User reports any of: "app-nya dobel di Alt+Tab", duplicate windows that multiply, ghost windows filling the screen, "nyangkut ya?" / "is it a stuck process?", wrong taskbar thumbnails, focus/restore weirdness, an app that looks frozen but keeps running.

Applies to any Windows desktop app (SAP B1, VS, Electron/CEF apps, Office). Do not answer from the symptom.

## Rules (always on)

1. **Prove it before naming a cause.** Collect four facts: (a) how many live processes, (b) how many *visible* top-level windows, (c) hung status, (d) the contents of the shell's Alt+Tab list. "Duplicate window", "ghost entry", "stale shell cache", and "hung process" are different diagnoses with different fixes — they are decided by these four numbers, not by how the symptom looks.
2. **Never synthesize the user's input.** To catch a transient UI event, start a background logger (`background=true`), ask the user to perform the action and reply, then read the log file. Do not send Alt+Tab / keystrokes into their live desktop.
3. **A window you did not see can still exist.** EnumWindows skips message-only windows and children of other windows: a process with zero top-level windows may still have a full UI. Say "no top-level windows", not "no UI".
4. **Fix ladder, mildest first**, and state each trade-off: shell restart / OS setting → app-side setting → vendor KB / update / support ticket. Registry hacks that remove thumbnails entirely (classic Alt+Tab) are a trade-off, not a fix — say so.
5. **Never tell the user to kill hidden helper windows** (Chromium/CEF renderers, GDI+/IME/tooltip windows, cross-process message pumps). They are normal for hybrid apps and killing them crashes the host.
6. **Report shape for this user** (Indonesian, uwu persona): short verdict first ("bukan nyangkut, dan bukan duplikat beneran"), then an evidence table (what the switcher lists vs what actually exists), then the fix ladder, then the explicit disproof ("kalau nyangkut, statusnya Not Responding — yang not-responding cuma X"). No play-by-play of your tool calls. Keep the raw evidence (HWND class names, counts) in the reply — the user checks it.

## Procedure

### 1. Snapshot the real window tree

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:/tmp/window-probe.ps1 -Pattern '^(?i)(sap|b1)'
```

(Run the skill's `scripts/window-probe.ps1`; see Pitfalls for why `C:/...` and an anchored pattern.)

Read: `Vis=True` + `Tool=False` + `Cloak=0` rows are the real windows on screen. Note `Class`, `Owner`, `Hung`, `Cloak`.

Decision point: **1 visible window + many switcher entries ⇒ shell-side ghost entries**, not duplicate windows. **N visible windows with identical titles ⇒ genuinely N windows** (common for File Explorer: `TEST`, `TEST`, `This PC` are three real windows — corroborate with the taskbar tooltip "File Explorer - 3 running windows").

### 2. Separate "hung" from "busy / hidden / cloaked"

- `tasklist /FI "STATUS eq NOT RESPONDING"` and the `Hung` column (`IsHungAppWindow`) — this is the only evidence for "stuck process".
- `Cloak` = `DwmGetWindowAttribute(hwnd, DWMWA_CLOAKED=14)`. A cloak 0→1→0 lasting ~150 ms exactly at the moment of Alt+Tab is the shell hiding/unhiding the window, **not** a duplicate.
- A process that spawns more hidden top-level windows over time is normal for hybrid/CEF apps and is what pollutes the shell's list.

### 3. Catch transient events (background logger)

Start `scripts/window-transition-logger.ps1 -Pattern '...' -Seconds 900 -OutFile C:/tmp/window-transitions.txt` with `background=true`, tell the user exactly what to do ("tekan & tahan alt, tap tab 3-4x, tahan 3 detik, baru lepas"), have them reply, then read the log. It logs `NEW` / `CHANGE` / `GONE` with pid, class, title, vis/cloak/hung so you can tell shell hiding from window creation.

### 4. Read the shell's own Alt+Tab list (decisive step)

Run `scripts/alt-tab-switcher-dump.ps1` in the background, then have the user hold Alt with the switcher visible.

How it works: on Windows 11 the switcher is an **explorer** window, class `XamlExplorerHostIslandWindow`, title `Task Switching`. It exposes UI Automation `ListItem` children whose `Name` is exactly the entry text shown to the user. Compare that list, item by item, against the real visible windows from step 1:

- entry matches a real window → real
- entry has **no matching window, often carrying an older title** (previous tenant/company/document/folder) → **stale ghost entry**

This is what turns "SAP dobel" into a proven shell-cache problem. The watcher only sees the switcher while Alt is actually held — say that in the instruction.

### 5. Report + fixes

Give: verdict, evidence table, then the ladder (e.g. restart `explorer.exe` to rebuild the list; Settings → System → Multitasking → Alt+Tab → "Open windows only"; app/vendor KB + update patch level; ticket to the vendor component). If you have not verified a fix yourself, label it as the expected effect, not as verified.

## Pitfalls

- **`$PID` is a PowerShell automatic read-only variable.** Never bind a window/process id to `$pid` — the script dies with "Cannot overwrite variable PID because it is read-only". Use `$wpid`.
- **Anchor process-name filters**: `^(?i)(sap|b1)`. Substring matching false-positives badly — `WhatsApp.Root` contains "sApp" and matches `sap`, `B1_ServiceManager` matches `b1`; both pollute the window list and the visible-window count you are about to report as evidence.
- **Pass `C:/...` forward-slash paths** to native programs (PowerShell, curl, python) from this host's bash terminal; MSYS path conversion is off, so `/c/...` is read literally as `C:\c\...`.
- **In long polling loops, rebuild the PID→process-name cache every ~15 iterations** — every iteration starves the loop, once at start misses new processes.
- Reference: `references/sap-b1-client-windows.md`

## Support files

- `scripts/window-probe.ps1` — one-shot snapshot: top-level windows + visible/hung/cloaked/owner/class/title
- `scripts/window-transition-logger.ps1` — background poll logger of NEW/CHANGE/GONE window transitions
- `scripts/alt-tab-switcher-dump.ps1` — background UIA dump of the Win11 Alt+Tab switcher's entries
- `references/sap-b1-client-windows.md` — SAP B1 10.0 client window anatomy + the Alt+Tab duplication case and its fixes

---

## Sub-Module: wsl-windows-admin

# Windows Admin Tools from WSL (C# / .NET Framework)

Build & ship Windows console utilities from WSL: detect/manage Windows services, compile to .exe, place on desktop.

## Build pipeline: compile C# .NET Framework exe from WSL

- Full-solution build (multi-project, sln): use Visual Studio MSBuild, NOT `dotnet build` (netcore MSBuild). Path: `/mnt/c/Program Files/Microsoft Visual Studio/2022/Community/MSBuild/Current/Bin/MSBuild.exe` (adjust edition: Community/Pro/Enterprise).
- **MSB4803 pitfall**: `dotnet build` on a .NET Framework project that references COM interop (e.g. `SAPbobsCOM`, `SAPbouiCOM`) fails with `error MSB4803: The task "ResolveComReference" is not supported on the .NET Core version of MSBuild`. This is a hard architectural limit — always use VS MSBuild.exe for such projects. Not fixable by CLI flags.
- Invoke from the project dir with Windows-style args once, then reuse: `MSBuild.exe "Project.csproj" /verbosity:minimal /nologo`. Success = exit 0 + trailing lines `... -> D:\...\bin\Debug\...exe`. Pre-existing warnings (CS0414 unused field etc.) are noise — grep for `error` only.
- Verify artifact: `file /mnt/c/.../exe` → `PE32 ... Mono/.Net assembly`, or check the `-> ...exe` line in build output.
- csc.exe location: `C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe` (32-bit: `Framework\v4.0.30319`). No install needed — ships with Windows.
- Always invoke via `cmd.exe /c` with WINDOWS paths as arguments (never `/mnt/c/...` inside the command string):

```
cmd.exe /c "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /nologo /target:exe /r:System.ServiceProcess.dll /win32manifest:C:\Users\muham\app\app.manifest /out:C:\Users\muham\Desktop\App.exe C:\Users\muham\app\Program.cs"
```

- Non-BCL assemblies need explicit `/r:` — `System.ServiceProcess.dll` for `ServiceController`.
- Success = exit code 0 + empty output. Verify artifact: `file /mnt/c/.../App.exe` → `PE32 executable ... Mono/.Net assembly`, plus `ls -la` for size.
- Template manifest (requireAdministrator): see `templates/app.manifest`.

## Windows service management (C#)

- List + filter: `ServiceController.GetServices()` then `Where` on ServiceName AND DisplayName with `StringComparison.OrdinalIgnoreCase` (display name often differs from service name).
- Call `s.Refresh()` before reading `s.Status` (cached otherwise).
- Stop/Start: wrap EACH service in try/catch — one failure must not abort the batch. `WaitForStatus(..., TimeSpan.FromSeconds(30))` for confirmation.
- `ServiceController` has NO API to set startup type (Automatic/Manual/Disabled). Use P/Invoke `advapi32.dll` `ChangeServiceConfig` / `QueryServiceConfig`. Working code: `references/service-starttype-pinvoke.md`.
- Set Manual does NOT stop a running service — tell the user to stop explicitly too (menu order matters).
- `Stop()` also stops dependent services — mention this in UI copy.

## Pitfalls

- **WinForms `StartPosition` set in `Load` event never applies** — window position is computed when the handle is created (before `Load` fires), so `form.StartPosition = CenterScreen` in a `Load` handler is a silent no-op. Set it in the constructor (after `InitializeComponent`) or in the Designer. Same rule for any property that affects first-show layout. Detail + verification pattern: `references/winforms-centering.md`.
- **Patch tool fuzzy-match can mangle indentation** on CRLF C# files: V4A/replace with slightly-off old_string re-indents the whole edited block (nested bodies get over-indented). After patching .cs files, re-read the edited region and check brace indentation before building; fix with a follow-up replace.
- **Locked exe on rebuild**: compile fails with `error CS0016: Could not write to output file ... being used by another process` when the exe is still running. Check `cmd.exe /c "tasklist | findstr /i <name>"`, then `cmd.exe /c "taskkill /PID <pid> /F"` — ask the user before killing an interactive process (use clarify if they might be using it).
- UAC prompt appears on launch because of the manifest — warn the user beforehand.
- Full rewrites via write_file are safer than patch for large feature additions.

## User conventions (muham, WSL)

- UI copy for user-facing Windows programs: Bahasa Indonesia (menus, labels, messages).
- Real example: `SapApacheServiceManager` — source `C:\Users\muham\sap_apache_manager\Program.cs`, exe `C:\Users\muham\Desktop\SapApacheServiceManager.exe`. Update flow: edit source → check/kill running instance → recompile to same /out path.
- Windows user dir: `/mnt/c/Users/muham/`; desktop `/mnt/c/Users/muham/Desktop/`.

---

## Sub-Module: wsl-windows-gpu-setup

# WSL2 → Windows GPU & Gaming Performance

Set up Windows-side GPU/performance from inside WSL2. User plays Valorant on the same PC where Hermes runs. Goal: **zero manual steps** — user just plays.

## Detect hardware (run first, always)

```bash
# CPU
powershell.exe -Command "Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors"

# GPU — WSL2 only sees primary display GPU. Check ALL GPU registry slots:
powershell.exe -Command "Get-ChildItem 'HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}' -ErrorAction SilentlyContinue | ForEach-Object { (Get-ItemProperty $_.PSPath).DriverDesc }"

# Win32 only reports primary. Registry check above finds ALL GPUs.

# RAM
powershell.exe -Command "Get-CimInstance Win32_PhysicalMemory | Select-Object Manufacturer, Capacity, Speed"

# Disk
powershell.exe -Command "Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | Select-Object DeviceID, @{N='FreeGB';E={[math]::Round($_.FreeSpace/1GB,1)}}"

# WSL memory
grep -E "memory|swap" ~/.wslconfig 2>/dev/null || echo "No .wslconfig"
```

## Check NVIDIA driver

```bash
# Driver version
powershell.exe -Command "Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*' -ErrorAction SilentlyContinue | Where-Object { \$_.DisplayName -and \$_.DisplayName -match 'NVIDIA Graphics Driver' } | Select-Object DisplayName, DisplayVersion"

# nvidia-smi path
powershell.exe -Command "Test-Path 'C:\Windows\System32\nvidia-smi.exe'"

# nvidia-smi from WSL — WILL FAIL on hybrid GPU laptops
/mnt/c/Windows/System32/nvidia-smi.exe 2>&1
# Exit 9 = "non-NVIDIA GPU running as primary display, NVIDIA GPU in WDDM mode"
# This is EXPECTED. nvidia-smi inside WSL2 does NOT work on Optimus laptops.
# The driver is still installed. Do NOT tell user driver is missing.
```

**Critical:** `nvidia-smi` failing from WSL2 ≠ no driver. Check the uninstall registry. If driver is listed, it's installed. WSL2 just can't query it via nvidia-smi on Optimus (hybrid) laptops.

## Check game install location

```bash
# Common locations
ls /mnt/c/Riot\ Games/ 2>/dev/null || ls /mnt/d/Games/Riot\ Games/ 2>/dev/null
# Valorant exe
find "/mnt/d/Games/Riot Games/VALORANT" -name "VALORANT.exe" -type f 2>/dev/null
```

## Power plan — set via PowerShell from WSL

```bash
# List
powershell.exe -Command "powercfg /list"
# Find Ultimate Performance GUID
powershell.exe -Command "powercfg /getactivescheme"
# Set (use GUID from powercfg /list)
powershell.exe -Command "powercfg /setactive <GUID>"
```

**Important:** Use the full command in a single `powershell.exe -Command "..."`. Don't try `sudo powershell` — sudo doesn't recognize the WSL path and fails. Plain `powershell.exe` works.

## Game Mode + GameDVR

```powershell
$reg = 'HKCU:\SYSTEM\GameConfigStore'
Set-ItemProperty -Path $reg -Name 'GameDVR_Enabled' -Value 0 -Type DWord
Set-ItemProperty -Path $reg -Name 'AutoGameModeEnabled' -Value 1 -Type DWord
Set-ItemProperty -Path $reg -Name 'GameDVR_FSEBehavior' -Value 2 -Type DWord
Set-ItemProperty -Path $reg -Name 'GameDVR_FSEBehaviorMode' -Value 2 -Type DWord
Set-ItemProperty -Path $reg -Name 'GameDVR_HonorUserFSEBehaviorMode' -Value 0 -Type DWord
```

## Force game to use discrete GPU

**Problem:** Backslash paths in registry keys break when passed through WSL→PowerShell. `D:\Games\Riot\...` becomes `D:ames\Riot...` — the backslashes get eaten.

**Solution:** Write a `.ps1` script to disk, execute it. The file itself has proper backslashes.

```powershell
# Write to /home/maulana/setup_game.ps1, then:
powershell.exe -ExecutionPolicy Bypass -File /home/maulana/setup_game.ps1
```

Script content (the path variable must be inside the .ps1, NOT in the -Command string):

```powershell
$reg = 'HKCU:\SYSTEM\GameConfigStore'
Set-ItemProperty -Path $reg -Name 'GameDVR_Enabled' -Value 0 -Type DWord
Set-ItemProperty -Path $reg -Name 'AutoGameModeEnabled' -Value 1 -Type DWord

$directXReg = 'HKCU:\SOFTWARE\Microsoft\DirectX\GraphicsSettings'
if (-not (Test-Path $directXReg)) { New-Item -Path $directXReg -Force | Out-Null }

$gamePath = 'D:\Games\Riot Games\VALORANT\live\VALORANT.exe'
$hash = [System.BitConverter]::ToString(
    [System.Security.Cryptography.SHA1]::Create().ComputeHash(
        [System.Text.Encoding]::UTF8.GetBytes($gamePath))
).Replace('-','').Substring(0,16)
$gpuRegPath = "$directXReg\$hash"
if (-not (Test-Path $gpuRegPath)) { New-Item -Path $gpuRegPath -Force | Out-Null }
Set-ItemProperty -Path $gpuRegPath -Name 'PreferGpu' -Value 'High' -Type String
```

## Kill game before setup

```bash
powershell.exe -Command "Get-Process valorant* -ErrorAction SilentlyContinue | Stop-Process -Force"
```

## FPS expectations (Valorant, RTX 4050 Laptop)

| Resolution | Settings | Expected FPS |
|---|---|---|
| 1080p | Low | 200-250 |
| 1080p | Medium | 150-200 |
| 1080p | High | 120-160 |
| 720p | Low | 250-350 |

**User expectation:** 300+ FPS at 1080p. This requires: dGPU force + Ultimate Performance + GameDVR off + Game Mode on. If still not reaching 300, check game's in-game settings (FXAA off, V-Sync off, frame limit unbounded).

## Pitfalls

1. **`sudo powershell` fails from WSL** — sudo doesn't resolve `.exe` paths in WSL. Use plain `powershell.exe` directly. If sudo is truly needed, `sudo -n` (non-interactive) or check if sudoers has NOPASSWD.
2. **`nvidia-smi` from WSL2 always fails on Optimus** — this is the expected behavior, not a driver problem. Check the uninstall registry for driver version instead.
3. **Backslash paths break in `powershell.exe -Command`** — any path with `\` gets mangled when passed through bash quoting. Always write a `.ps1` file and execute with `-File` for anything involving registry paths.
4. **WSL2 RAM limits** — check `~/.wslconfig`. If `memory=` is too low, Windows games starve for RAM. Set at least 8GB if total system RAM is 16GB+.
5. **Don't tell user to manually change resolution** — user expects zero manual steps. Set everything from WSL, tell them to just play.
6. **`Get-Process` with wildcards in WSL bash** — `valorant*` works fine. But `Get-Process *valorant*` needs quotes in the `-Command` string.
7. **Laptop hybrid GPU** — WSL2 only sees Intel UHD. RTX 4050 is in Optimus (discrete GPU). The dGPU is only active when a DirectX application (like Valorant) requests it. This is normal.

## WSL config check

```bash
# .wslconfig location
cat /mnt/c/Users/*/ /mnt/c/Users/*/AppData/Local/Microsoft/WSL/.wslconfig 2>/dev/null
# Or:
ls /mnt/c/Users/*/
```

For a 16-20GB RAM laptop, recommended `.wslconfig`:
```ini
[wsl2]
memory=8GB
swap=2GB
localhostForwarding=true
```

After changing `.wslconfig`, user must run `wsl --shutdown` from Windows PowerShell to apply.

---