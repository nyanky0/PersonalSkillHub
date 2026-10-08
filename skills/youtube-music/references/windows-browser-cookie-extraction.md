# WSL → Windows browser cookie extraction (Chromium, DPAPI)

Extract YouTube/Google session cookies from Windows browser profiles while inside WSL. No user copy-paste needed.

## Why this works

- WSL can read `/mnt/c/Users/<user>/AppData/...` files directly.
- Chromium cookie values are AES-256-GCM, key = DPAPI blob in `Local State`, decrypted with `powershell.exe` interop (runs as the same Windows user → `CryptUnprotectData` works).
- No native Linux crypto needed.

## DPAPI decrypt helper (powershell.exe interop)

```python
import base64, subprocess
def dpapi_unprotect(blob_b64: str, entropy: str | None = None) -> bytes:
    ent = ',[System.Text.Encoding]::UTF8.GetBytes("' + entropy + '")' if entropy else ",$null"
    ps = ('Add-Type -AssemblyName System.Security; '
          '[Convert]::ToBase64String([System.Security.Cryptography.ProtectedData]::Unprotect('
          f'[Convert]::FromBase64String("{blob_b64}")' + ent +
          ',[System.Security.Cryptography.DataProtectionScope]::CurrentUser))')
    out = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps],
                         capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise RuntimeError("DPAPI failed: " + out.stderr[:300])
    return base64.b64decode(out.stdout.strip())
```

## Paths (this user's machine: /mnt/c/Users/muham)

| Source | Cookie DB | Key (Local State) |
|---|---|---|
| Chrome | `AppData/Local/Google/Chrome/User Data/<Profile>/Network/Cookies` | `.../User Data/Local State` → `os_crypt.encrypted_key` |
| YouTube Music Desktop App (Electron) | `AppData/Roaming/YouTube Music Desktop App/Partitions/ytmview/Network/Cookies` | `AppData/Roaming/YouTube Music Desktop App/Local State` |
| Electron app root (`Network/Cookies` without partition) | often empty/irrelevant — check `Partitions/*/Network/Cookies` first | app's own Local State |

## Steps

1. **Ensure target app is fully closed.** Windows locks cookie DBs exclusively while running. Chrome lingers in background: `taskkill.exe /F /IM chrome.exe` (verify with `tasklist.exe | grep -i chrome`). Electron apps must be closed too.
2. Copy DB + Local State to `/tmp` or `~/` (avoid reading over the C: mount mid-lock; also keeps a consistent snapshot).
3. `encrypted_key` from Local State: base64-decode, assert `[:5] == b"DPAPI"`, DPAPI-decrypt `[5:]` → 32-byte AES key.
4. SQLite: `SELECT name, value, encrypted_value FROM cookies WHERE host_key LIKE '%youtube%'`.
5. Decrypt per row (see below).
6. Build cookie header `"; ".join(f"{n}={v}")` — include SID, HSID, SSID, APISID, SAPISID, __Secure-1/3PSID(+TS,CC), LOGIN_INFO, VISITOR_INFO1_LIVE, PREF, etc.

## Value formats

- `v10`: `b"v10" + nonce(12) + ciphertext + tag(16)`, key = DPAPI key. Standard AES-GCM.
- `v20`: `b"v20" + nonce(12) + ciphertext + tag(16)` BUT key = App-Bound key from `os_crypt.app_bound_encrypted_key` (header `APPB\x01\x00\x00\x00`). Tried DPAPI at offsets 3/4/5, with/without entropy (`app_bound_encrypted_key`, `app-bound-encryption-key`) — all "The data is invalid." Recent Chrome ABE not crackable this way from WSL. **Fallback: use a different profile (ytmdesktop partition) or refresh cookies via app usage.**
- **ytmdesktop quirk**: plaintext = FIXED 31-byte prefix + real value (`<\\xb2a^...\\xefI` + value). MAC verifies with the app's own key. Strip `pt[31:]`. Identical prefix on every cookie → deterministic app wrapper, not random salt.

## Login-state checks (don't trust decryption success)

- `GET https://www.youtube.com/account` with cookie → **303 redirect to accounts.google.com/ServiceLogin** = session dead. 200 = alive.
- ytmusicapi `create_playlist` → **HTTP 401** = cookies expired. Fix: user opens the app/browser ~10s (YouTube reissues cookies on activity), closes it, re-extract. Decryption is fine — the session, not the key, went stale.
- Cookie DB may decrypt perfectly yet contain zero youtube rows (logged-out profile / app never logged in). Check `SAPISID`/`SID` presence before building headers.

## One-shot verification snippet

```python
import json, requests
h = json.load(open("headers_auth.json"))
r = requests.get("https://www.youtube.com/account",
                 headers={"cookie": h["cookie"]}, allow_redirects=False, timeout=30)
print("alive" if r.status_code == 200 else f"dead: {r.status_code} -> {r.headers.get('location','')[:60]}")
```

## Firefox alternative (untried here)

Firefox does NOT lock cookies.sqlite against reading; values encrypted with key in `key4.db` (global salt + DPAPI-protected master key). Deeper rabbit hole; only if no Chromium/Electron login exists.
