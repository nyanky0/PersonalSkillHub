---
name: stock-media-sourcing
description: Find hotlink-able stock media for web demos.
---

# Stock Media Sourcing (hotlink-able)

Find images/videos that a web page can load directly via `<img src>` / `<video src>`
— no downloading, no hosting, no API keys. For landing pages, digital invitations
(wedding etc.), and throwaway HTML demos.

## Golden rules

1. **Official APIs, not page scraping.** `curl | grep` scraping of stock-site HTML
   (Pixabay pages etc.) was rejected by the user — never default to it. Use the
   documented APIs in `references/endpoints.md`, or ask the user for their own file.
2. **Verify every URL before shipping.** HEAD request must return 200. Batch-check
   several URLs in one loop and drop the failures.
3. **Watch file size.** Hero background video: prefer < 10MB (3MB is ideal) or the
   page feels heavy. Archive.org items often run 50–200MB — usually too big for a
   web background; Wikimedia Commons files are typically small enough.
4. **Format matters.** Wikimedia gives WebM/OgV mostly. WebM plays in
   Chrome/Firefox/Edge and Safari 14.1+. Always `muted autoplay loop playsinline`
   for background video.
5. **Orientation:** portrait video (e.g. 528x944) suits mobile-first invitations;
   desktop gets center-crop via `object-fit: cover` + `overflow: hidden`.
6. **Fallback plan:** a `<video>` that fails to load should leave a designed
   fallback (poster image or canvas animation) — never a blank hero.

## Quick recipes

| Need | Source | Recipe |
|---|---|---|
| Stock photo, stable hotlink | Unsplash | `https://images.unsplash.com/photo-<id>?w=<width>` — find IDs by keyword via the official search API in `references/endpoints.md` (no key, no page scraping); known-good wedding IDs also listed there |
| Stock video, small, license-clean | Wikimedia Commons | `imageinfo` API → direct `upload.wikimedia.org` URL |
| Large/niche footage | archive.org | `advancedsearch` + `metadata` API → `archive.org/download/<id>/<file>` |

## Workflow

1. Search source API for candidates (keywords + `filetype:video` on Commons).
2. Pull direct URLs + size + dimensions from the metadata API.
3. HEAD-check each URL (batch in one script/loop).
4. Pick smallest file that fits; note orientation.
5. Wire into HTML with poster/fallback. Verify in browser.

## Pitfalls

- `upload.wikimedia.org` URLs from `imageinfo` carry a `?utm_source=...` query —
  strip it before using.
- Don't guess CDN URLs (Pixabay `cdn.pixabay.com/video/...` paths are not
  guessable and their page HTML is scrape-protected).
- Unsplash `?w=` param controls width — request small for thumbnails, large for
  heroes; still check status, some old IDs 404.
- Unsplash has TWO CDN hosts. Standard shots: `images.unsplash.com/photo-<id>`.
  Premium shots: `plus.unsplash.com/premium_photo-<id>`. HEAD-checking a
  `premium_photo-<id>` against `images.unsplash.com/photo-<id>` returns a false
  404 even though the image is fine — you'll wrongly "fix" working images.
  Always take BOTH the host AND the `photo-`/`premium_photo-` segment from the
  search hit's `urls.raw` field. NEVER rebuild a CDN URL from the hit's `id`
  field (that `id` is a short slug like `5Zwpg2QJq7g`, not the CDN filename).
- **HTTP 200 only proves the image EXISTS, not that it MATCHES the slot.** For a
  semantic slot ("drinks", "gulai", "parfum") you must also read the hit's
  `alt_description`/subject, not just the status code. Classic real failure:
  `photo-1503376780353-7e6692767b70` is a very famous Porsche photo — returns
  200 but is dead wrong for a "Minuman Lainnya" card. Verify status AND alt text
  for every image wired into a named/described slot.
- If the user denies a fetch command, switch to a different official source —
  don't re-attempt the same scrape.

## Files

- `references/endpoints.md` — exact API requests, response shapes, and known-good
  verified URLs (Unsplash wedding photo IDs, Wikimedia wedding video).
