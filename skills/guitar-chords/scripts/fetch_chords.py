#!/usr/bin/env python3
"""Fetch guitar chords for a song list, trying multiple chord sites.

Edit SONGS: (title, artist, [candidate URLs in priority order]).
Output: raw/NN_<title>.txt files (header comments + chord/lyric text).
Stdlib only — run with plain python3.
"""
import re, html, os, json, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

def extract_pre(html_text):
    m = re.search(r"<pre[^>]*>(.*?)</pre>", html_text, re.S)
    if not m:
        return None
    t = html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))
    return re.sub(r"\n{3,}", "\n\n", t).strip()

SONGS = [
    # (title, artist, [candidate URLs in priority order])
    ("Kangen", "Dewa 19", [
        "https://chordtela.web.id/chord/dewa-19/dewa-19-kangen",
    ]),
    ("Separuh Aku", "Noah", [
        "https://chordtela.web.id/chord/noah/noah-separuh-aku",
        "https://www.chordindonesia.com/chord-noah-separuh-aku",
    ]),
    ("Akad", "Payung Teduh", [
        "https://chordtela.web.id/chord/payung-teduh/payung-teduh-akad-menikahlah",
        "https://www.chordindonesia.com/payung-teduh-akad",
    ]),
    ("Kenangan Terindah", "Samsons", [
        "https://chordtela.web.id/chord/samsons/samsons-kenangan-terindah",
        "https://www.chordindonesia.com/chord-samsons-kenangan-terindah",
        "https://www.chordindonesia.com/samsons-kenangan-terindah",
    ]),
    ("Tak Bisakah", "Peterpan", [
        "https://chordtela.web.id/chord/peterpan/peterpan-tak-bisakah",
        "https://www.chordindonesia.com/chord-peterpan-tak-bisakah",
        "https://www.chordindonesia.com/peterpan-tak-bisakah",
    ]),
    ("Wonderwall", "Oasis", [
        "https://chordtela.web.id/chord/oasis/oasis-wonderwall",
        "https://www.chordindonesia.com/oasis-wonderwall",
    ]),
    ("Let Her Go", "Passenger", [
        "https://chordtela.web.id/chord/passenger/passenger-let-her-go",
    ]),
    ("Perfect", "Ed Sheeran", [
        "https://chordtela.web.id/chord/ed-sheeran/ed-sheeran-perfect",
        "https://www.chordindonesia.com/ed-sheeran-perfect",
        "https://www.chordindonesia.com/chord-ed-sheeran-perfect",
    ]),
    ("I'm Yours", "Jason Mraz", [
        "https://chordtela.web.id/chord/jason-mraz/jason-mraz-im-yours",
        "https://www.chordindonesia.com/jason-mraz-im-yours",
        "https://www.chordindonesia.com/chord-jason-mraz-im-yours",
    ]),
    ("Riptide", "Vance Joy", [
        "https://chordtela.web.id/chord/vance-joy/vance-joy-riptide",
        "https://www.chordindonesia.com/vance-joy-riptide",
        "https://www.chordfylan.com/2020/01/riptide-vance-joy.html",
    ]),
]

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")
os.makedirs(OUT, exist_ok=True)
results = []

for idx, (title, artist, urls) in enumerate(SONGS, 1):
    found = None
    for url in urls:
        try:
            page = fetch(url)
            pre = extract_pre(page)
            if pre and len(pre) > 300:  # ads-only pages extract too short
                found = (url, pre)
                break
        except Exception as e:
            print(f"  [skip] {url}: {e}")
    if found:
        url, pre = found
        safe = title.lower().replace(" ", "_").replace("'", "")
        with open(os.path.join(OUT, f"{idx:02d}_{safe}.txt"), "w", encoding="utf-8") as f:
            f.write(f"# {title} — {artist}\n# Sumber: {url}\n\n{pre}\n")
        results.append((title, artist, "OK", url))
        print(f"OK  [{idx}] {title} — {artist} ({url})")
    else:
        results.append((title, artist, "FAIL", ""))
        print(f"FAIL[{idx}] {title} — {artist}")

with open(os.path.join(OUT, "_status.json"), "w") as f:
    json.dump(results, f, indent=1)
print("\nDone:", sum(1 for r in results if r[2] == "OK"), "/", len(results))
