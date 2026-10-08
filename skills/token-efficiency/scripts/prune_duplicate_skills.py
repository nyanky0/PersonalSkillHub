#!/usr/bin/env python3
"""Pangkas SKILL.md duplikat di pohon skill Hermes.

Daftar skill di system prompt memuat SETIAP SKILL.md yang ditemukan. Kalau skill yang sama
ada di top-level DAN di subfolder kategori, prompt membayar dua kali — dan `skill_view`
menggagalkan nama itu ("Ambiguous skill name ... Refusing to guess").

Pengelompokan pakai **name: di frontmatter**, BUKAN nama folder: folder `lazy-dev` yang
isinya `name: ponytail` tetap tabrakan dengan skill `ponytail`.

Pemenang: salinan yang byte-identik dengan hub (`D:/SkillHub/skills/<name>/SKILL.md`) —
hub = himpunan kanonis yang dipakai semua agent, jadi Hermes tidak boleh menyimpang. Kalau
tidak ada yang cocok dengan hub, ambil yang paling dangkal. Sisanya dipindah ke karantina
di luar pohon skill → 100% reversibel. Default = dry-run.

Dikecualikan: bundel plugin vendored (`*/plugin/skills/*`, mis. skill api-gateway milik
provider Claude) — memindahkannya berisiko merusak manifest plugin.

Pakai:
  python prune_duplicate_skills.py              # dry-run, tampilkan rencana
  python prune_duplicate_skills.py --apply      # pindahkan ke karantina
  python prune_duplicate_skills.py --restore E:/HERMES/.skill-quarantine/<ts>   # balikkan
"""
import collections
import hashlib
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path("E:/HERMES/skills")
HUB = Path("D:/SkillHub/skills")
QUAR = Path("E:/HERMES/.skill-quarantine")
NAME_RE = re.compile(r'^name:\s*["\']?([A-Za-z0-9._-]+)', re.M)


def depth(p: Path) -> int:
    return len(p.parent.relative_to(ROOT).parts) - 1


def declared_name(smd: Path) -> str:
    try:
        head = smd.read_text(encoding="utf-8", errors="ignore")[:800]
    except OSError:
        return smd.parent.name
    m = NAME_RE.search(head)
    return m.group(1) if m else smd.parent.name


def is_vendored_plugin(p: Path) -> bool:
    return "plugin/skills" in str(p.parent.relative_to(ROOT)).replace("\\", "/")


def pick_keep(name: str, paths: list[Path]) -> Path:
    """Kandidat pemenang berurutan: (1) folder-nya bernama sama dengan `name` DAN identik
    dengan hub, (2) identik dengan hub, (3) folder bernama sama, (4) paling dangkal.
    Tanpa langkah "folder bernama sama", `lazy-dev/` (frontmatter `name: ponytail`) bisa
    menang atas `ponytail/` hanya karena urutan abjad lalu menabrak lagi tiap sync."""
    hub = HUB / name / "SKILL.md"
    hub_hash = hashlib.md5(hub.read_bytes()).hexdigest() if hub.exists() else None
    named = [p for p in paths if p.parent.name == name]
    for pool in (named, paths):
        if hub_hash is not None:
            same = [p for p in pool if hashlib.md5(p.read_bytes()).hexdigest() == hub_hash]
            if same:
                return min(same, key=lambda p: (depth(p), str(p)))
    if named:
        return min(named, key=lambda p: (depth(p), str(p)))
    return min(paths, key=lambda p: (depth(p), str(p)))


def main() -> int:
    argv = sys.argv[1:]
    apply = "--apply" in argv
    if "--restore" in argv:
        src = Path(argv[argv.index("--restore") + 1])
        n = 0
        for item in src.iterdir():
            dest = ROOT / item.relative_to(src)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(item), str(dest))
            n += 1
        print(f"restored {n} item dari {src}")
        return 0

    groups: dict[str, list[Path]] = collections.defaultdict(list)
    for smd in ROOT.rglob("SKILL.md"):
        groups[declared_name(smd)].append(smd)

    victims: list[Path] = []
    mangled = 0
    protected: list[str] = []
    for name, paths in sorted(groups.items()):
        if len(paths) < 2:
            continue
        keep = pick_keep(name, paths)
        losers = [p for p in paths if p != keep]
        for p in losers:
            if is_vendored_plugin(p):
                protected.append(f"{name} ({p.parent.relative_to(ROOT)})")
                continue
            if hashlib.md5(p.read_bytes()).hexdigest() != hashlib.md5(keep.read_bytes()).hexdigest():
                mangled += 1
            victims.append(p)

    total = sum(len(v) for v in groups.values())
    print(f"entri SKILL.md sekarang    : {total}")
    print(f"nama unik                  : {len(groups)}")
    print(f"tabrakan nama              : {sum(1 for v in groups.values() if len(v) > 1)}")
    print(f"salinan dipindah           : {len(victims)}  (isi beda dari pemenang: {mangled})")
    print(f"entri setelah prune        : {total - len(victims)}")
    saved_chars = sum(len(p.parent.name) + 70 for p in victims)
    print(f"estimasi hemat prompt      : ~{saved_chars:,} char (~{saved_chars // 4:,} token) tiap giliran")
    if protected:
        print("dibiarkan (bundel plugin)  : " + ", ".join(protected))
    print()
    for p in victims[:30]:
        print(f"  - {p.parent.relative_to(ROOT)}")
    if len(victims) > 30:
        print(f"  ... +{len(victims) - 30} lagi")

    if not apply:
        print("\n(dry-run — jalankan ulang dengan --apply untuk pindah ke karantina)")
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest_root = QUAR / stamp
    for p in victims:
        d = dest_root / p.parent.relative_to(ROOT)
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(p.parent), str(d))
    print(f"\nOK: {len(victims)} folder skill dipindah ke {dest_root}")
    print("Balikkan: python prune_duplicate_skills.py --restore " + str(dest_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
