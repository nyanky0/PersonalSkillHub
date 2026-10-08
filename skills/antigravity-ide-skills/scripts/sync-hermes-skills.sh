#!/usr/bin/env bash
# Sync Hermes skills -> Antigravity IDE global skills root.
# Copies every ~/.hermes/skills/**/SKILL.md, names the destination dir after the
# frontmatter `name` field, strips CRLF and UTF-8 BOM (both break YAML name parsing),
# and reports case-insensitive duplicate dir names.
#
# Usage: ./sync-hermes-skills.sh [SRC] [DEST]
#   SRC  default ~/.hermes/skills
#   DEST default /mnt/c/Users/muham/.gemini/config/skills  (Windows: C:\Users\muham\.gemini\config\skills)
set -euo pipefail

SRC="${1:-$HOME/.hermes/skills}"
DEST="${2:-/mnt/c/Users/muham/.gemini/config/skills}"

[ -d "$SRC" ] || { echo "SRC not found: $SRC"; exit 1; }
mkdir -p "$DEST"

COUNT=0
for f in "$SRC"/*/SKILL.md "$SRC"/*/*/SKILL.md; do
  [ -f "$f" ] || continue
  # name from frontmatter, CR-stripped; fall back to source dir name
  NAME=$(grep -m1 '^name:' "$f" | sed 's/^name:[[:space:]]*//' | tr -d '\r')
  [ -n "$NAME" ] || NAME=$(basename "$(dirname "$f")")
  TARGET="$DEST/$NAME/SKILL.md"
  mkdir -p "$(dirname "$TARGET")"
  # Strip both CRLF and UTF-8 BOM
  tr -d '\r' < "$f" | sed '1s/^\xef\xbb\xbf//' > "$TARGET"
  COUNT=$((COUNT+1))
done

echo "Synced $COUNT skills -> $DEST"

echo "--- CR-check (must be empty) ---"
grep -rl $'\r' "$DEST" || echo "no CR files"

echo "--- BOM-check (must be empty) ---"
find "$DEST" -name "SKILL.md" -exec sh -c 'xxd -l 3 "$1" | grep -q "efbb bf" && echo "$1"' _ {} \; || echo "no BOM files"

echo "--- case-insensitive dup dir names (must be empty) ---"
ls "$DEST" | tr 'A-Z' 'a-z' | sort | uniq -d

echo "--- frontmatter check ---"
python3 - "$DEST" <<'EOF'
import os, sys, re
root = sys.argv[1]
bad, ok = [], 0
for dp, dn, fn in os.walk(root):
    if 'SKILL.md' not in fn:
        continue
    txt = open(os.path.join(dp, 'SKILL.md'), encoding='utf-8').read()
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', txt, re.S)
    if not m:
        bad.append((dp, 'no frontmatter')); continue
    fm = m.group(1)
    if re.search(r'^name:', fm, re.M) and re.search(r'^description:', fm, re.M):
        ok += 1
    else:
        bad.append((dp, 'missing name/description'))
print(f"frontmatter OK: {ok}, BROKEN: {len(bad)}")
for p, why in bad:
    print('  ', p, '->', why)
EOF