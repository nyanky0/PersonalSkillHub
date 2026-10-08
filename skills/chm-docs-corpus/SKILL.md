---
name: chm-docs-corpus
description: Extract .chm docs into a queryable skill corpus.
---

# CHM Documentation → Queryable Skill Corpus

Vendor SDKs (SAP B1, MSDN-based help, etc.) ship docs as compiled HTML help (`.chm`).
These are not directly searchable by ripgrep and are painful to open page-by-page.
The reliable workflow: extract the CHM to plain HTML, build a JSON index + search helper,
and optionally wire that corpus into skills. This is the class-level procedure; the concrete
SAP B1 instance lives in the `sap-b1*` skills.

## Step 1 — Extract the CHM (Windows)

**Pitfall (proven):** `hh -decompile <outdir> <file.chm>` from a git-bash/MSYS terminal
reports exit 0 but silently produces NO files. It also eats stdout. Do not rely on it
from bash, and do not wrap it in `cmd //c ...` (MSYS mangles the command line).

**Use 7-Zip instead — it always works:**

```bash
SEVENZ="C:/Program Files/7-Zip/7z.exe"   # note: forward-slash Windows path
"$SEVENZ" x -y -o"C:/path/to/outdir" "C:/Program Files/.../vendor.chm"
```

**Pitfall (proven):** native Windows tools get MSYS path conversion DISABLED. Pass
`C:/...` (not `/c/...`) to `7z.exe`, otherwise it reports
`ERROR: The system cannot find the path specified.` and looks for `\c\Program Files...`.
This is the single most common extraction failure.

Result: plain `.html` files plus `*.hhc` (table-of-contents), `*.hhk` (index keymap),
and internal `#TOPICS`, `#URLSTR`, `#IDXHDR` metadata files.

## Step 2 — Understand the structure before indexing

- `*.hhc` is the TOC: nested `<li><object><param name="Name">` + `Local="File.htm"`.
  Grep the `Name` params to enumerate topics; list TOC entries for the doc map.
- Vendor files open with a `<table>`; the useful text is after stripping tags.
- Large SDKs explode into tens of thousands of files (SAP B1 DI = 27k). **Never
  `find` / `du -sh` the whole tree from bash** to count them — MSYS walks it file by
  file and times out (120–180s+ for 27k files). Use targeted `ls`/`ls -d`/`grep` and
  per-module counts, or let Python do the walk once during indexing.

## Step 3 — Build a JSON index + search helper

Generate an index dict once (fast, in Python) and save as JSON; then a tiny search
helper reads it so lookups are instant. See `scripts/build_chm_index.py` as a template.

Recommended pattern:
- RefDB style (one page per table): key = lowercase table name → `{name, module, path, desc}`.
- Object reference style (pages `Prefix~Object.html`): key = lowercase object → `{obj, path}`,
  excluding member pages (pages containing `~` after the object name) from the top-level index.

Search modes: exact key → hit; else starts-with then substring (cap results). Desc
extraction: strip tags, sniff `"Table Description:"` / `"Description"` text.

## Step 4 — Wire into skills

- Point the skill's SKILL.md at the search helper with absolute paths so it works from
  any skill dir / any agent (Hermes, Cline `~/.agents/skills`, Gemini `~/.gemini/config/skills`).
- Keep the extracted corpus in a STABLE writable dir (e.g. `C:/Users/<user>/.vendor-help/`),
  NOT a temp dir that gets cleaned.
- Verify enum/constant values in docs against the extracted HTML before hardcoding them
  into skill content — don't trust memory for `BoObjectTypes`, `BoFormItemTypes`, etc.
- Rebuild index (re-run the script) if the index JSON is ever missing.

## Path & tooling pitfalls (all proven this session)

- `python C:/.../script.py` from bash needs a forward-slash native path; `/c/...` to native
  Python fails with `can't open file 'C:\\c\\Users\\...'`.
- To place the produced doc inside a protected `Program Files (x86)` folder you need admin;
  a `Start-Process -Verb RunAs` UAC elevation prompt does NOT reliably surface from a
  headless/CLI session and can hang waiting — instead give the user a one-line
  run-as-administrator `copy` command to run themselves.
- `robocopy` (native) is the fast way to move a huge extracted tree; MSYS `cp -r` on 27k
  files is slow.

## Support files

- `scripts/build_chm_index.py` — template index-builder (RefDB + object-reference modes).
- `references/sap-b1-corpus.md` — concrete SAP B1 SDK 10.0 corpus layout & channels.