---
name: youtube-music
description: Use when managing YouTube Music playlists (ytmusicapi).
---

# YouTube Music (ytmusicapi)

Create playlists, add songs, read library on user's YouTube Music account via `ytmusicapi`.

## Install (WSL, PEP 668 — no system pip)

```
python3 -m venv ~/.venvs/ytmusic
~/.venvs/ytmusic/bin/pip install ytmusicapi pycryptodome
```

## Auth — ranked options

1. **Browser cookie extraction (best, zero user friction)** — read cookies from Windows browser/app profile via WSL. See `references/windows-browser-cookie-extraction.md` + `scripts/extract_ytm_cookies.py`.
2. **`setup_oauth()`** — needs Google Cloud OAuth client_id/client_secret (YouTube Data API enabled). ~10 min console work. Only if cookies impossible.
3. **`setup()` / headers paste** — user copies request headers from DevTools. AVOID: users repeatedly paste wrong things (image URLs, avatar cURLs). Only as last resort; demand the "Fetch/XHR" filter + Copy as cURL of a `youtubei/v1/...` request.

## Headers file for ytmusicapi 1.12.1+

File must contain ALL three keys, or auth type detection misfires:

```json
{
  "cookie": "SAPISID=...; SID=...; HSID=...; ...",
  "x-goog-authuser": "0",
  "authorization": "SAPISIDHASH <ts>_<sha1hex>"
}
```

- `get_authorization(SAPISID + " https://music.youtube.com")` — **CRITICAL**: it expects `"SAPISID Origin"` concatenated with a space, NOT just the SAPISID. Wrong input → valid-looking request, but server treats you as logged out.
- Missing `authorization` → `YTMusicUserError: "oauth JSON provided via auth argument, but oauth_credentials not provided"` (determine_auth_type defaults to OAUTH_CUSTOM_CLIENT). Fix = add the SAPISIDHASH header, not OAuth setup.
- **ytmusicapi 1.12+ `origin` key REQUIRED**: ctor does `self.origin = base_headers.get("origin")` then builds `authorization = get_authorization(sapisid + " " + origin)`. If the file lacks `"origin"`, you get `"SAPISID None"` → valid-looking SAPISIDHASH that the server REJECTS → 401 "You must be signed in" EVEN WITH PERFECT COOKIES. headers_auth.json MUST contain `"origin": "https://music.youtube.com"`.
- **Origin/Referer/UA headers required for playlist/create** (2025+): raw requests.post with only cookie+authorization → 401; adding `User-Agent` (Chrome UA) + `Origin: https://music.youtube.com` + `Referer: https://music.youtube.com/` → 200. Pass a `requests.Session` with those headers into `YTMusic(requests_session=sess)` — the session merge survives `headers=self.headers` overrides.
- **CDP Linux Chrome route (best auth fallback, bypasses Chrome v20 ABE)**: install google-chrome .deb in WSL (`dpkg -i` + `apt-get install -f`), launch `google-chrome --remote-debugging-port=9222 --remote-allow-origins=http://127.0.0.1:9222 --user-data-dir=~/.config/hermes-chrome` (window shows on Windows desktop via WSLg; user logs in manually there). Cookies are PLAINTEXT: `Network.getAllCookies` over websocket → build headers_auth.json. Chrome 151+ rejects websocket without `--remote-allow-origins`.

## Core flow

```python
from ytmusicapi import YTMusic
yt = YTMusic("headers_auth.json")
yt.get_account_info()            # auth sanity check (may fail on shape, see pitfalls)
pid = yt.create_playlist(title, desc, privacy_status="PUBLIC")
res = yt.search("artist song", filter="songs", limit=1)  # [{"videoId": ...}]
yt.add_playlist_items(pid, [r["videoId"] for r in results])
print("https://music.youtube.com/playlist?list=" + pid)
```

## Pitfalls

- **Fresh chrome launch → `StopIteration` in `cdp._ws()`** (observed 2026-08): port 9222 answers `/json/version`, but `/json` may list no `"type": "page"` tab yet, so `next(t for t in tabs if t["type"] == "page")` raises `StopIteration` and `build_headers_cdp.py` dies before finishing. Fix BEFORE `get_cookies`: ensure a page tab exists — `curl -X PUT "http://127.0.0.1:9222/json/new?url=https://music.youtube.com"` then re-run `build_headers_cdp.py` (chrome may need a couple seconds to register the tab). Keep chrome running; don't relaunch.
- **401 "You must be signed in"** on create_playlist = session cookies EXPIRED. Fix: user opens the YouTube Music Desktop App (or browser) ~10s so YouTube issues fresh cookies, closes it, then re-extract. Do NOT re-decrypt — cookies, not key, are stale.
  - After reopen+extract, compare SAPISID value against previous headers_auth.json. If UNCHANGED and create_playlist still 401 → session is dead server-side; app shows login page and only writes non-login cookies. Requires MANUAL user re-login in the app. get_home/get_library OK is NOT proof of login (home works as guest; library check is local, not server-side). Definitive auth tests: create+delete a PRIVATE playlist, or the www.youtube.com/account 303 check.
- **get_account_info may raise** `Unable to find 'header' ... 'activeAccountHeaderRenderer'` even when logged in (menu response shape varies). Not proof of logout. Verify auth with a real write endpoint (create/delete a PRIVATE test playlist) or `GET https://www.youtube.com/account` → 303 to ServiceLogin = logged out.
- Windows cookie DBs are **exclusively locked while the browser/app runs**. Chrome keeps background processes after windows close — `taskkill.exe /F /IM chrome.exe` (interop from WSL). Extraction requires the app closed.
- Cookies for `music.youtube.com` may live in an **Electron partition** (`Partitions/<name>/Network/Cookies`), not the app root.
- Recent Chrome (2025) "v20" cookies use App-Bound Encryption — DPAPI blob `APPB\x01...`; offsets 3/4/5 + entropy variants failed to decrypt in this environment. Don't burn time; use the ytmdesktop partition or refresh-cookie route instead.
- After extraction, values may carry a fixed app-specific plaintext prefix (ytmdesktop = 31 bytes) — strip it; MAC verifies with the app's own key.

## Support files

- `references/windows-browser-cookie-extraction.md` — full WSL↔Windows cookie extraction recipe (paths, DPAPI, v10/v20, quirks).
- `scripts/extract_ytm_cookies.py` — extracts ytmdesktop cookies, writes `headers_auth.json` ready for YTMusic.
