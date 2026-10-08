---
name: guitar-chords
description: "Guitar chords / kunci gitar / chord book PDF requests."
version: 1.0.0
author: Hermes Agent
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [music, chords, guitar, scraping, pdf]
    category: creative
---

# Guitar Chords → Chord-Book PDF

Fetch guitar chords + lyrics for a list of songs from Indonesian chord sites (curl-friendly, no API key needed), then assemble a PDF book with chord-over-lyric alignment.

## When to Use

User asks: "cari chord gitar lagu X", "buat buku chord 10 lagu", "chord lagu + PDF", "kunci gitar". Covers both Indonesian and English/Western songs — Indonesian sites carry both.

## Chord Site Landscape (as of 2026-07)

| Site | Curl-able? | Notes |
|------|-----------|-------|
| `chordtela.web.id` | Yes | New domain. URL: `/chord/<artist-slug>/<artist-slug>-<title-slug>` (two segments!). Catalog LIMITED — many classic songs 404. |
| `www.chordtela.com` | NO — HTTP 403 | Old domain, Cloudflare-blocked. Google indexes its URLs (`/YYYY/MM/<slug>.html`) but they're useless for curl. |
| `chordindonesia.com` | Yes | URL variants: `/chord-<artist>-<title>` OR `/<artist>-<title>` — try both. Full catalog, good for English songs too. |
| `chordfylan.com` | Yes | Blogspot-style, `/YYYY/MM/<slug>.html`. Good fallback for niche songs. |
| `malaykord.com` | Yes | Another fallback. |

All of them put chord+lyric content inside a single `<pre>` tag — same extraction works everywhere.

## Workflow

1. **Pick songs** (5 Indo + 5 English mix works well). Prefer songs with simple chords (Am, C, G, D, Em) for beginner value.
2. **Find page URLs**: guess slugs first, but expect 404s. Fastest reliable path: `web_search` with `site:chordtela.web.id` or plain `<song> <artist> chord` — descriptions show the chord content, confirming the song exists on that domain.
3. **Fetch + extract** (see scripts/fetch_chords.py): curl with desktop Chrome UA, regex `<pre[^>]*>(.*?)</pre>`, `html.unescape` + strip tags, collapse 3+ newlines, strip `\r`. Verify extracted text > ~300 chars before accepting (ads-only pages extract too short).
4. **Fallback chain per song**: chordtela.web.id → chordindonesia.com → chordfylan.com / malaykord.com.
5. **Build PDF** (see scripts/build_chordbook_pdf.py): reportlab, A4, `XPreformatted` + Courier 8.5pt for body (Paragraph collapses whitespace and wrecks chord alignment — never use it for chord bodies), `PageBreak` per song, cover + TOC page, source URL listed under each song title.
6. **Verify**: `pdftotext -layout` the first song page and confirm chord lines sit above lyric lines; count `NN. Title` occurrences == song count.

## Pitfalls

- chordtela.web.id artist pages (`/artis/<slug>`) show a GLOBAL song list, not the artist's — useless for slug discovery.
- New chordtela slugs include the artist prefix twice: `/chord/dewa-19/dewa-19-kangen`. Single-segment `/chord/<slug>` → HTTP 500, not 404.
- Old-domain URLs from Google results are 403 traps — don't batch-curl them.
- `web_extract` may be search-only on some configs (ddgs backend) — curl fallback is the reliable path.
- Some pages have stray "Chord Kunci Gitar Lagu X / Artist" header lines inside `<pre>` — strip duplicate title lines before PDF.
- Indonesian sites use `\r\n` — strip `\r`.
- Keep the source URL per song in the PDF; chord accuracy disputes need provenance.

## Scripts

- `scripts/fetch_chords.py` — multi-source fetcher. Edit `SONGS` list (title, artist, candidate URLs), run with plain `python3` (stdlib only).
- `scripts/build_chordbook_pdf.py` — reportlab assembly from `raw/NN_<title>.txt` files. Needs venv with reportlab (`pip install reportlab`).

## Verification

1. `pdftotext -layout -f 2 -l 2 book.pdf - | head -25` — chord alignment readable.
2. `pypdf` PdfReader page count + spot-check extract_text on a middle page.
3. If vision model unavailable (401), pdftotext layout check is sufficient proof of alignment.
