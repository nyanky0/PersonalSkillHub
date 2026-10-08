# ytmusic

# YouTube Music via ytmusicapi

Create playlists, search songs, add items on the user's YouTube Music account. Requires the user's browser login once (headers paste flow).

## Setup

```bash
python3 -m venv ~/.venvs/ytmusic
~/.venvs/ytmusic/bin/pip install ytmusicapi   # v1.12.x current
```

## Auth — pick the right flow (pitfall: names are misleading)

Three functions, only ONE usable without Google Cloud setup:

| Function | What it actually does | Works out of the box? |
|---|---|---|
| `setup(filepath)` | Prompts to paste request headers (interactive stdin, Ctrl-D/EOF to finish) | YES — this is the main path |
| `setup_browser(filepath)` | SAME headers-paste flow. Despite the name it does NOT extract from browser. Just tolerates Chromium "Copy as cURL" paste formats | YES (same as setup) |
| `setup_oauth(client_id, client_secret, filepath, open_browser=False)` | True OAuth device flow, prints URL + code | NO — requires Google Cloud OAuth client_id/secret (YouTube Data API v3 enabled). Skip unless user already has one |

Do NOT start with `setup_oauth` — it crashes with TypeError (missing creds) and wastes a cycle. Run `setup()` / `setup_browser()`; when it prints "Please paste the request headers..." you are in the headers flow, which is the goal.

### Headers paste flow — user steps

1. Open https://music.youtube.com in Chrome/Edge, logged in.
2. F12 → Network tab → refresh (F5).
3. Click any request (e.g. "browse"), right-click → Copy → Copy request headers.
4. Paste the block into the chat (agent writes it to a file), or feed via heredoc.

Required lines: `cookie:` and `x-goog-authuser:`. The pasted block must be the raw "Name: value" format; Chromium's separate-lines format is also tolerated.

### Headers → usable session

```bash
~/.venvs/ytmusic/bin/python - <<'EOF'
from ytmusicapi import setup
setup("headers_auth.json", headers_raw=open("/tmp/headers.txt").read())
from ytmusicapi import YTMusic
yt = YTMusic("headers_auth.json")   # or YTMusic(auth="headers_auth.json") in newer API
print(yt.get_library_playlists())
EOF
```

`setup_browser(filepath, headers_raw=...)` accepts the same `headers_raw` kwarg.

## Playlist creation

```python
pid = yt.create_playlist("Chill Vibes", "desc", privacy_status="PRIVATE")  # returns playlist id
songs = ["artist - title", ...]
video_ids = []
for q in songs:
    r = yt.search(q, filter="songs", limit=1)   # or limit=3, pick by resultType=="song" + matching title/artist
    if r:
        video_ids.append(r[0]["videoId"])
# create_playlist can also take videoIds directly:
yt.add_playlist_items(pid, videoIds=video_ids)
```

Search pitfalls:
- Filter `filter="songs"` — without it you get videos/albums mixed in.
- Verify match: compare `result["title"]` and `result["artists"][0]["name"]` loosely against query; first hit is usually right but covers/remixes slip in.
- Some tracks are unavailable (region/VEVO) — `add_playlist_items` may partially fail; check response for non-200 results and report which songs failed.

## Verification

- `yt.get_playlist(pid)` → check `tracks` count matches.
- Give user the playlist URL: `https://music.youtube.com/playlist?list={pid}`.

## Gotchas

- ytmusicapi 1.12.1: `YTMusic("headers_auth.json")` positional auth still works; newer versions prefer `YTMusic(auth=...)`.
- Headers go stale (cookie expiry). Re-run the paste flow if requests start failing with 401/403.
- Python 3.14 + venv: pip not on PATH globally — always use `~/.venvs/ytmusic/bin/python` / `.../bin/pip`.
