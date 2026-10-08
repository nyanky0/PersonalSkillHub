# Stock media API endpoints (verified working)

All requests below are plain GET, no API key, JSON responses. Verified during a
digital-wedding-invitation build (video bg + gallery).

## Wikimedia Commons (best for small, license-clean video + any image)

Base: `https://commons.wikimedia.org/w/api.php`

Search video files:
```
action=query&list=search&srsearch=wedding%20couple%20filetype:video&srnamespace=6&format=json&srlimit=15
```
- `srnamespace=6` = File namespace only. `filetype:video` filters to videos.

Direct URL + size + dimensions + duration for a file:
```
action=query&titles=File:White%20wedding.webm&prop=imageinfo&iiprop=url|size|mime|duration&format=json
```
Response: `query.pages[].imageinfo[0]` → `url`, `size` (bytes), `width`,
`height`, `mime`, `duration`.
- **Strip the `?utm_source=...&utm_campaign=...` query from `url`** before use.
- Formats: `.webm`/`.ogv` dominate; few `.mp4`. WebM needs Safari 14.1+.
- Real example: `File:White wedding.webm` → 3.1MB, 28s, 528x944 (portrait),
  `https://upload.wikimedia.org/wikipedia/commons/d/da/White_wedding.webm`

## archive.org (large footage; often too big for web bg)

Search items:
```
https://archive.org/advancedsearch.php?q=title:(wedding)%20AND%20mediatype:(movies)&fl[]=identifier&fl[]=title&rows=20&output=json
```
List files in an item:
```
https://archive.org/metadata/<identifier>
```
→ `files[]` with `name`, `format`, `size`. Direct download:
`https://archive.org/download/<identifier>/<filename>`
- Derived MPEG4/h.264 files typically 50–225MB — too heavy for a hero
  background; fine for local download/re-encode. Quality/content very mixed
  (often amateur footage) — prefer Wikimedia for web use.

## Unsplash (stable direct image URLs)

Pattern: `https://images.unsplash.com/photo-<id>?w=<width>`
- `?w=` controls served width. Always HEAD-check; old IDs can 404.

### Search by keyword (official API, no key) — NEW, verified 2026-08

```
https://unsplash.com/napi/search/photos?query=<url-encoded>&per_page=3
```
- Returns JSON: `results[]` with `id`, `urls.raw`, `alt_description`.
  ⚠️ The `id` field is a SHORT slug (e.g. `5Zwpg2QJq7g`), NOT the numeric
  `photo-<id>`. NEVER build a URL from `id` directly — it 404s. Always extract
  the real segment from `urls.raw` with a regex:
  `(photo-\d+[-\w]*|premium_photo-\d+[-\w]*)`.
- **Host matters (caused a false-negative in a real session):**
  `photo-*` lives on `images.unsplash.com`; `premium_photo-*` lives on
  `plus.unsplash.com`. A premium image checked against
  `images.unsplash.com/photo-<premium_id>` returns 404 even though the image is
  fine. Read the host from the extracted `urls.raw` path, then HEAD-check that
  exact `<host>/<segment>?w=<w>` URL. Do NOT assume `images.unsplash.com/photo-`
  for everything and report a 404 as a "broken image" — verify against the
  correct host first.
- Verified working queries this session: "car wash", "coffee cup cafe",
  "perfume bottle", "gulai curry indonesian food" — returned valid 200 IDs
  (e.g. `photo-1633014041037-f5446fb4ce99` car foam, `photo-1572656631137-7935297eff55` curry bowl).
- This replaces blind ID guessing: search → extract id → HEAD-check → use.

- Known-good wedding photo IDs (all returned 200 with `?w=100`):
  - `1519741497674-611481863552` — couple, classic
  - `1465495976277-4387d4b0b4c6` — wedding ceremony
  - `1511285560929-80b456fea0bc` — bride/groom
  - `1522673607200-164d1b6ce486` — wedding couple
  - `1583939003579-730e3918a45a` — rings
  - `1591604466107-ec97de577aff` — couple

## Verification pattern

Batch HEAD-check (no download):
```bash
for u in "URL1" "URL2"; do code=$(curl -s -o /dev/null -w "%{http_code}" -L "$u"); echo "$code $u"; done
```
Drop non-200. Prefer smallest video that fits the design (< 10MB).
