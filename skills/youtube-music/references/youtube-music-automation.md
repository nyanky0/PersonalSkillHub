# youtube-music-automation

# YouTube Music automation (ytmusicapi)

## When to use
Create/fill YouTube Music playlists, search songs, manage library programmatically. Especially when the logged-in browser session lives on Windows and you work from WSL.

## Core flow
1. Setup: `python3 -m venv ~/.venvs/ytmusic && ~/.venvs/ytmusic/bin/pip install ytmusicapi pycryptodome`
2. Auth (pick one):
   - Headers paste: `setup_browser()` flow — user copies request headers from browser DevTools (Network tab → Fetch/XHR filter → Copy request headers / Copy as cURL). Must contain `cookie:` line. User repeatedly pastes wrong things (image URLs); insist on the Fetch/XHR filter.
   - Cookie extraction from disk: see `references/windows-chromium-cookie-extraction.md` (best for WSL→Windows, zero user copy-paste).
   - `setup_oauth()` needs Google Cloud client_id/secret — avoid (10+ min setup).
3. Headers JSON file for YTMusic:
   ```json
   {"cookie": "<name=value; ...>", "x-goog-authuser": "0", "authorization": "SAPISIDHASH ..."}
   ```
4. `yt = YTMusic(headers_path)` → `yt.create_playlist(title, description, privacy_status)` → `yt.search(q, filter="songs", limit=1)` → `yt.add_playlist_items(pid, video_ids)`.

## Pitfalls (ytmusicapi 1.12.x)
- **`authorization` header is REQUIRED.** Auth-type detection defaults to OAUTH_CUSTOM_CLIENT unless the headers contain `authorization` with `SAPISIDHASH` → then BROWSER. Missing it raises "oauth JSON provided via auth argument".
- **`get_authorization()` wants `"<SAPISID> https://music.youtube.com"`** (SAPISID + space + origin). Passing bare SAPISID yields a wrong hash → server silently treats you as logged out (menu without account header, 401 on create_playlist). The 401 is the tell.
- `get_account_info()` often fails on newer account_menu shapes ("Unable to find 'header' using path ['actions', 0, ...]") EVEN when logged in. Decisive auth tests instead: `create_playlist()` (401 = logged out) or `requests.get("https://www.youtube.com/account", allow_redirects=False)` (303→accounts.google.com/ServiceLogin = logged out).
- Stale/expired cookies → 401. Check the source DB mtime: months-old mtime = dead session. Refresh requires the user to actually open the app/browser and play something (opening alone may write nothing) or re-login.
- `parse_auth_str` URL-encodes header values (quote with safe=printable) — cookie strings survive intact (printables unencoded).

## Verification
- `create_playlist` returns playlistId; confirm with `yt.get_playlist(pid)` trackCount == number added.
- Playlist URL: `https://music.youtube.com/playlist?list=<id>`.

## References
- `references/windows-chromium-cookie-extraction.md` — full WSL→Windows Chromium/Electron cookie decryption walkthrough (DPAPI via powershell.exe, v10/v20, ytmdesktop quirks).
