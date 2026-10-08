# Windows Chromium cookie extraction from WSL (for ytmusicapi)

Goal: get a fresh logged-in `cookie` string for youtube.com from a Windows browser/Electron app, without asking the user to copy-paste headers.

## Key facts
- Chromium cookie DB = SQLite table `cookies`. Values encrypted AES-256-GCM with prefix `v10` (or `v20` on recent Chrome).
- Key chain for v10: `Local State` JSON → `os_crypt.encrypted_key` (base64) → strip leading `b"DPAPI"` → DPAPI-unprotect → 32-byte AES key.
- DPAPI from WSL (works when WSL user == Windows user):
  ```
  powershell.exe -NoProfile -Command 'Add-Type -AssemblyName System.Security; [Convert]::ToBase64String([System.Security.Cryptography.ProtectedData]::Unprotect([Convert]::FromBase64String("<b64>"), $null, [System.Security.Cryptography.DataProtectionScope]::CurrentUser))'
  ```
- v10 decrypt layout: `encrypted_value` = `b"v10"` (3) + nonce (12) + ciphertext + tag (16). Slice: nonce=enc[3:15], ct=enc[15:-16], tag=enc[-16:]. Use pycryptodome `AES.new(key, AES.MODE_GCM, nonce=nonce).decrypt_and_verify(ct, tag)`.
- **Chrome locks the Cookies DB exclusively while running** → `cp` fails with Permission denied. User closing windows is NOT enough (background processes linger): `taskkill.exe /F /IM chrome.exe`.
- Firefox `cookies.sqlite` is NOT exclusively locked (WAL readers allowed), but the master key (key4.db) decryption is DPAPI + PBKDF2 — not yet implemented here; check cookie NAMES first to see if the user is even logged in.
- **Chrome v20 cookies (`b"v20"` prefix) use an app-bound key** from `os_crypt.app_bound_encrypted_key` (header `b"APPB\x01\x00\x00\x00"`). DPAPI-unprotect attempts (skip 3/4/5 bytes, with/without entropy `app_bound_encrypted_key` / `app-bound-encryption-key`) ALL failed on a 2026 Chrome build. Do not rely on Chrome; prefer another logged-in source.
- Electron apps: cookies live in the app's own userData. If the app uses Chromium partitions, the DB is at `<userData>/Partitions/<partition>/Network/Cookies`, encrypted with THAT app's own `Local State` key (NOT Chrome's).

## YouTube Music Desktop App (ytmdesktop) specifics
- userData: `/mnt/c/Users/<u>/AppData/Roaming/YouTube Music Desktop App`
- Partition cookie DB: `Partitions/ytmview/Network/Cookies` (~20 cookies incl. SID, SAPISID, HSID, SSID, APISID, LOGIN_INFO when logged in).
- **QUIRK: every decrypted plaintext carries a fixed 31-byte prefix** — the real cookie value = `plaintext[31:]`. GCM MAC verifies with the app key, so the prefix is part of the stored format; strip it, don't debug the key.
- App must be closed to read the DB (Windows lock, same as Chrome).
- **Session freshness**: check Cookies DB mtime. Months-old mtime = dead session → user must re-login in the app and actually play something before cookies refresh; merely launching the app may write zero bytes (verified: launch without network activity leaves mtime untouched).
- **Broken install symptom**: app dir contains only `squirrel.exe` + `v8_context_snapshot.bin` (real files deleted by a failed update) and `logs/main.log` shows nothing new. Fix: reinstall from `https://github.com/ytmdesktop/ytmdesktop/releases` — `YouTube.Music.Desktop.App-<v>.Setup.exe /S` (silent squirrel install; auto-launches after install).

## Decisive auth tests
- `requests.get("https://www.youtube.com/account", headers={"cookie": c}, allow_redirects=False, timeout=30)`:
  - `303` → `accounts.google.com/ServiceLogin` = LOGGED OUT
  - `200` = logged in
- ytmusicapi: `create_playlist()` → `401 Unauthorized: You must be signed in` = logged out.

## Working script pattern (from 2026-07 session)
venv `~/.venvs/ytmusic` (ytmusicapi + pycryptodome). Full working example: `~/ytm/build_playlist.py` — decrypt ytmview DB → strip 31B prefix → write `headers_auth.json` with `cookie` + `x-goog-authuser` + `authorization` (`get_authorization(SAPISID + " https://music.youtube.com")`) → `YTMusic(path)` → create_playlist → search(filter="songs") → add_playlist_items → get_playlist to verify.
