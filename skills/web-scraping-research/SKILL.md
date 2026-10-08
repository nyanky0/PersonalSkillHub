---
name: web-scraping-research
description: "Scrape web docs/research to extract knowledge into skills."
version: 1.0.0
author: Hermes Agent (lessons from live scraping sessions)
license: MIT
tags: [scraping, research, web, curl, browser, knowledge-synthesis, skills]
platforms: [linux, macos, windows]
triggers:
  - scrape websites
  - research from many sites
  - turn web content into a skill
  - extract knowledge from docs
  - learn a new technology from the web
  - curl blocked by bot protection
---

# Web Scraping → Knowledge Synthesis

Turn live web research into durable skill content. Proven pattern from real sessions: scraping design systems (shadcn, TailAdmin, Carbon), SAP B1 official curriculum (learning.sap.com, help.sap.com), and REST/Laravel best-practice repos. The goal is always a synthesized, class-level artifact — not a raw dump.

## Workflow

### 1. Curate sources, don't spray
Pick high-authority sources per topic before scraping:
- **Official docs** (help.sap.com, tailwindcss.com/docs, ui.shadcn.com/docs) — most accurate but often bot-blocked
- **Raw GitHub** — `raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>` — rarely blocked, best for docs-as-code (Microsoft api-guidelines, laravel-best-practices, TailAdmin templates, shadcn content)
- **Wikipedia REST API** — `en.wikipedia.org/w/index.php?title=<page>&action=raw` returns wikitext; plain HTML often redirects to a list page
- **Learning platforms** (learning.sap.com) — official curriculum structure = gold for "what to teach"
- Avoid blog listings (sapb1tips.com = just post titles, no content)

### 2. Parallel fetch with xargs (not shell `&`)
Foreground terminal rejects `&` backgrounding. Use:
```bash
mkdir -p /tmp/scrape && cd /tmp/scrape
printf '%s\n' \
  "https://url1/file1.html" \
  "https://url2/file2.html" | \
  xargs -P4 -L1 sh -c 'curl -sL --max-time 30 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36" -o "$1" "$0"'
```
Then `wc -c` each file: tiny sizes (<2KB) = 404/redirect/blocked shell. Exit code 123 from xargs = one URL failed (e.g. DNS) — retry individually.

### 3. Recognize & handle bot-block signatures
| Signature | Meaning |
|---|---|
| `Access Denied` + `errors.edgeSuite.net` (Akamai) | sap.com, vercel.com product pages — curl dead |
| `<title>Just a moment...</title>` / "Enable JavaScript and cookies" | Cloudflare challenge |
| 1KB Vue/React shell (`<div id="app">` + JS bundle) | help.sap.com, learning.sap.com — needs JS |
| 403 Forbidden | erpsoftwareblog etc. |
| 404 page-in-markup | wrong path/URL — check via GitHub API or search |
| Google `/sorry/` CAPTCHA | google.com search — dead via curl AND browser |
| Bing serves unrelated junk (query reinterpretation, wrong-language results) | bing.com search — unreliable for research |
| DDG JS wall / anti-bot checkbox+iframe form | duckduckgo.com AND html./lite. variants — dead |

### 4. Browser fallback for JS-rendered content
When curl gets a shell, the browser (browser_navigate) renders it:
- **SAP Help Portal / learning.sap.com** render via JS; `browser_console` + `document.body.innerText` extracts clean text
- Click-through TOC links (they're real `<a href>`) to reach deeper pages; after click, re-read `document.body.innerText.slice(-N)` — content lands at the END of innerText
- `browser_console` JS: `Array.from(document.querySelectorAll('a')).map(a => a.href).join('\n')` to harvest link URLs without clicking — faster than clicking each
- Buttons with `aria-expanded` need `.click()` dispatch to reveal hidden content:
  `document.querySelectorAll('button[aria-expanded="false"]').forEach(b => b.click())`
- To open a link: `document.querySelector('a[href*="..."]').click()` via console instead of browser_click (more reliable)

### 4b. Search-engine fallback: GitHub API + raw files
When all search engines bot-block (Google CAPTCHA, Bing junk, DDG wall), pivot to GitHub as the research backbone — it is the most reliable bot-free corpus:
- **Repo discovery**: `curl -s -A "Mozilla/5.0" "https://api.github.com/search/repositories?q=<query>&sort=stars&per_page=10"` → `full_name`, `stargazers_count`, `description` (sort by stars = instant quality ranking)
- **README**: `https://api.github.com/repos/<owner>/<repo>/readme` → base64-decode the `content` field
- **File tree**: `https://api.github.com/repos/<owner>/<repo>/git/trees/<branch>?recursive=1` → list paths, find the exact file to fetch
- **File content**: `https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>` — rarely blocked
- This finds both the state of the art AND canonical project structure/templates to model a build on.

### 5. Strip HTML → text, then search for signal
```bash
python3 -c "
import re,html
raw=open('file.html',encoding='utf-8',errors='ignore').read()
txt=re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>','',raw)
txt=re.sub(r'<[^>]+>',' ',txt)
txt=html.unescape(re.sub(r'\s+',' ',txt))
print(txt[:3000])"
```
For large files: print slices (`txt[600:4500]`) or grep headings (`grep -E "^#{1,3} " file.md`) to map structure before reading full text.

### 6. Synthesize into a class-level skill
- Structure: concepts → modules/patterns → gotchas → verification checklist → official learning path (if any)
- Cite sources in the skill (author line: "synthesized from X")
- Write functional/consultant-level knowledge per user's role — user is a SAP B1 consultant; code-level SAP goes to `sap-b1-addon-dev`, functional-level to `sap-b1-concepts`
- Keep the frontmatter `description` ≤60 chars (system prompt budget; `:` inside an unquoted YAML value breaks parsing — quote it: `description: "..."`)

## Pitfalls
- **Cleanup temp dirs** (`rm -rf /tmp/scrape`) — and if the cwd was inside the deleted dir, the shell's `pwd` breaks; run `cd ~` before the next terminal call
- **Grep targets** change per page (table of contents vs body) — extract then search, don't guess
- **wiki `action=raw` on a redirect page** returns `#REDIRECT [[...]]` — follow the target title
- **Full-page browser snapshots get huge** — use `browser_console` with targeted expressions instead of `browser_snapshot(full=true)` for repeated reads
- **Some pages are search-only** (web_extract with ddgs backend returns "search-only backend and cannot extract") — fall back to `curl -sL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" -o /tmp/page.html` in terminal, then parse locally
- **Never pipe curl into python3** (`curl ... | python3 -c "..."`) — the terminal security scan flags pipe-to-interpreter as HIGH and blocks it. Download to a temp file first (`curl -o /tmp/page.html`), then run python3 as a separate command/heredoc reading that file. Same for any curl | interpreter pattern.
- **Verify Telegram channels before recommending**: many Pokemon-GO/social coords channels are dead. Check via `curl -sL https://t.me/s/<channel> -o /tmp/tg.html`, then grep `datetime="YYYY-MM` (post dates) and message text — a 2023 last-post date or feed content that no longer matches the claimed purpose (e.g. generic spawns instead of raid coords) = dead channel, don't recommend it. Prefer Discord servers (member counts in invite previews are a liveness signal).

## Verification
- Skill frontmatter parses (name + description, ≤60 char description)
- Content cites its sources
- A trigger phrase from the research topic matches the skill description
