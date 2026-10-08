#!/usr/bin/env python3
"""Sebar blok Token Efficiency Protocol ke file aturan pasif semua agent.

Idempotent: blok ditulis di antara marker <!-- TOKEN-EFFICIENCY:BEGIN --> dan
<!-- TOKEN-EFFICIENCY:END -->. Jalankan ulang = memperbarui blok, bukan menumpuk.

Pakai:
  python install_passive_rules.py            # pasang/refresh di semua target
  python install_passive_rules.py --remove   # cabut blok dari semua target
  python install_passive_rules.py --check    # hanya lapor status
"""
import sys
from pathlib import Path

HOME = Path.home()
SKILL_DIR = Path(__file__).resolve().parent.parent
RULES = SKILL_DIR / "references" / "passive-rules.md"

BEGIN = "<!-- TOKEN-EFFICIENCY:BEGIN -->"
END = "<!-- TOKEN-EFFICIENCY:END -->"

TARGETS = [
    Path("E:/HERMES/SOUL.md"),                                   # Hermes: selalu dimuat
    HOME / ".agents/AGENTS.md",                                 # Antigravity IDE / Cline / agy
    HOME / ".gemini/config/AGENTS.md",                          # Gemini (agent Antigravity)
    HOME / ".gemini/GEMINI.md",                                 # Gemini CLI
]


def block() -> str:
    text = RULES.read_text(encoding="utf-8")
    _, _, rest = text.partition(BEGIN)
    body, _, _ = rest.partition(END)
    return BEGIN + body + END


def apply(path: Path, new_block: str | None) -> str:
    old = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
    if BEGIN in old and END in old:
        head, _, rest = old.partition(BEGIN)
        _, _, tail = rest.partition(END)
        base = (head.rstrip() + "\n") if head.strip() else ""
        tail = tail.lstrip("\n")
    else:
        base = old.rstrip() + "\n" if old.strip() else ""
        tail = ""
    if new_block is None:
        new = base + ("\n" + tail if tail else "")
    else:
        new = base + ("\n" if base else "") + new_block + "\n" + ("\n" + tail if tail else "")
    new = new.rstrip() + "\n"
    if new == old:
        return "unchanged"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(new, encoding="utf-8")
    return "updated" if new_block else "removed"


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "--check":
        for t in TARGETS:
            has = t.exists() and BEGIN in t.read_text(encoding="utf-8", errors="ignore")
            print(f"{'OK  ' if has else 'MISS'} {t}")
        return 0
    want = None if mode == "--remove" else block()
    for t in TARGETS:
        print(f"{apply(t, want):9} {t}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
