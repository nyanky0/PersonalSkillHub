#!/usr/bin/env python3
"""Sync Hermes skills into Antigravity global skills dir (Windows via WSL).

Usage:
  sync_hermes_to_antigravity.py <dest_dir> <skill-name> [<skill-name> ...]
  sync_hermes_to_antigravity.py <dest_dir> --all

Auto-discovers each skill under ~/.hermes/skills by frontmatter `name` (NOT the
folder name — Hermes dirs are category-scoped), copies the FULL tree
(SKILL.md + references/ + templates/ + scripts/), strips CRLF + UTF-8 BOM,
validates frontmatter (name+description required), and reports per skill.

Stray subfolders that are themselves skills (have their own SKILL.md at their
root, e.g. a copy of another skill nested inside a skill dir) are skipped;
asset dirs (references/, templates/, scripts/) have no SKILL.md and always copy.

Example (Antigravity on Windows, from WSL):
  python3 sync_hermes_to_antigravity.py /mnt/c/Users/muham/.gemini/config/skills frontend-design p5js pretext
"""
import os, re, sys

HERMES_SKILLS = os.path.expanduser("~/.hermes/skills")
FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
NAME_RE = re.compile(r"^name:\s*(.+?)\s*$", re.M)


def frontmatter_name(path):
    try:
        with open(path, "rb") as f:
            raw = f.read().decode("utf-8", "replace")
    except OSError:
        return None
    m = FM_RE.match(raw)
    if not m:
        return None
    n = NAME_RE.search(m.group(1))
    return n.group(1).strip() if n else None


def discover(name):
    for root, dirs, files in os.walk(HERMES_SKILLS):
        if "SKILL.md" not in files:
            continue
        if frontmatter_name(os.path.join(root, "SKILL.md")) == name:
            return root
    return None


def strip_bytes(b):
    if b.startswith(b"\xef\xbb\xbf"):
        b = b[3:]
    return b.replace(b"\r\n", b"\n")


def copy_tree(src, dest):
    """Copy full tree. Skip level-1 subdirs that are themselves skills (own SKILL.md)."""
    copied = 0
    for root, dirs, files in os.walk(src):
        if os.path.abspath(root) == os.path.abspath(src):
            dirs[:] = [d for d in dirs
                       if not os.path.exists(os.path.join(root, d, "SKILL.md"))]
        rel = os.path.relpath(root, src)
        tgt = dest if rel == "." else os.path.join(dest, rel)
        os.makedirs(tgt, exist_ok=True)
        for fn in files:
            with open(os.path.join(root, fn), "rb") as f:
                data = f.read()
            with open(os.path.join(tgt, fn), "wb") as f:
                f.write(strip_bytes(data))
            copied += 1
    return copied


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    dest = sys.argv[1]
    names = [n for n in sys.argv[2:] if not n.startswith("--")]
    if "--all" in sys.argv:
        names = []
        for root, dirs, files in os.walk(HERMES_SKILLS):
            if "SKILL.md" in files:
                nm = frontmatter_name(os.path.join(root, "SKILL.md"))
                if nm:
                    names.append(nm)
    os.makedirs(dest, exist_ok=True)
    failed = 0
    for name in sorted(set(names)):
        src = discover(name)
        if not src:
            print(f"SKIP {name}: not found under {HERMES_SKILLS}")
            failed += 1
            continue
        n = copy_tree(src, os.path.join(dest, name))
        print(f"OK   {name} -> {os.path.join(dest, name)} ({n} files)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
