#!/usr/bin/env python3
"""Audit biaya token setup skill + file aturan pasif.

Laporan:
  - ukuran file aturan pasif (di- inject ke prompt tiap sesi)
  - jumlah skill per agent (hermes / cline-agy / gemini / hub)
  - 10 SKILL.md terbesar (kandidat pemangkasan)
  - estimasi token daftar skill per giliran untuk Hermes

Pakai: python token_audit.py
"""
from pathlib import Path

HOME = Path.home()
HERE = Path(__file__).resolve().parent.parent
PASSIVE = [
    Path("E:/HERMES/SOUL.md"),
    HOME / ".agents/AGENTS.md",
    HOME / ".gemini/config/AGENTS.md",
    HOME / ".gemini/GEMINI.md",
]
ROOTS = {
    "hermes": Path("E:/HERMES/skills"),
    "cline/agy": HOME / ".agents/skills",
    "gemini": HOME / ".gemini/config/skills",
    "hub": Path("D:/SkillHub/skills"),
}
DESC_LIMIT = 60  # SKILL_PROMPT_DESC_LIMIT di agent/skill_utils.py


def desc_of(skill_md: Path) -> str:
    try:
        for line in skill_md.read_text(encoding="utf-8", errors="ignore").splitlines()[:20]:
            s = line.strip()
            if s.lower().startswith("description:"):
                return s.split(":", 1)[1].strip().strip('\"\'')
    except OSError:
        pass
    return ""


def main() -> None:
    print("== File aturan pasif (token input tiap sesi) ==")
    total = 0
    for p in PASSIVE:
        n = p.stat().st_size if p.exists() else 0
        total += n
        print(f"  {n:>7,} char  {'ada' if p.exists() else 'BELUM ADA':<9} {p}")
    print(f"  {total:>7,} char  TOTAL  (~{total // 4:,} token/giliran)\n")

    print("== Jumlah skill per agent ==")
    for label, root in ROOTS.items():
        n = len({p.parent for p in root.rglob("SKILL.md")}) if root.exists() else 0
        print(f"  {n:>5}  {label:<9} {root}")
    print()

    herm = ROOTS["hermes"]
    mds = sorted(herm.rglob("SKILL.md"), key=lambda p: p.stat().st_size, reverse=True) if herm.exists() else []
    print("== 10 SKILL.md terbesar di Hermes (kandidat pemangkasan) ==")
    for p in mds[:10]:
        print(f"  {p.stat().st_size:>8,} char  {p.parent.name}")
    print()

    # Estimasi daftar skill di system prompt Hermes: 1 baris per skill,
    # '  - nama: deskripsi(<=60)' + label kategori.
    names = [p.parent.name for p in mds]
    line_chars = sum(len(n) + min(len(desc_of(p)), DESC_LIMIT) + 6 for n, p in zip(names, mds))
    print(f"== Daftar skill Hermes: {len(names)} skill, ~{line_chars:,} char (~{line_chars // 4:,} token) per giliran ==")
    print("   Tip: `agent.coding_context: focus` menurunkan kategori non-coding jadi nama-saja.")
    print("   Tip: pangkas/hapus skill yang tak pernah dipanggil, bukan yang sering dipakai.")
    print(f"\n(Skill ini: {HERE})")


if __name__ == "__main__":
    main()
