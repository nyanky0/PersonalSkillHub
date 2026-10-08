#!/usr/bin/env python3
"""
SkillHub Sync — pusat sinkronisasi AGENT SKILLS

Folder master: D:\\SkillHub\\skills\
  Tiap subfolder = 1 skill (SKILL.md + semua file pendukungnya), FLAT.
  Agent baru cukup mengarahkan folder skills-nya ke sini (atau copy) untuk
  mendapatkan SEMUA skill yang sama persis.

Subcommand:
  collect        Kumpulkan skill terbaru dari semua source (hermes, cline,
                 gemini) ke hub. merge: file yang sudah ada & lebih baru tidak
                 ditimpa; skill baru/info baru ditambahkan.
  push <target>  Dorong semacam skill dari hub ke satu target agent.
                 target: hermes | cline | gemini | /path/apa/saja
  pushall        Dorong ke hermes + cline + gemini sekaligus.
  list           Tampilkan daftar skill di hub.
  manifest       Regenerate MANIFEST.md + MANIFEST.json (daftar skill + sumber).

Contoh:
  python sync_skills.py collect
  python sync_skills.py push cline
  python sync_skills.py pushall
"""
import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ----------------------------------------------------------------------------
# Konfigurasi lokasi (sesuaikan bila perlu)
# ----------------------------------------------------------------------------
HOME = Path.home()
LOCALAPPDATA = Path(os.environ.get("LOCALAPPDATA", HOME / "AppData/Local"))
GEMMA_I = HOME / ".gemini/config"

def _detect_hermes_home() -> Path:
    """HERMES_HOME env wins; kalau tidak diset, probe lokasi umum.
    (install lama ada di %LOCALAPPDATA%\\hermes, sekarang default E:\\HERMES)."""
    env = os.environ.get("HERMES_HOME")
    if env:
        return Path(env)
    for cand in (Path("E:/HERMES"), HOME / ".hermes", LOCALAPPDATA / "hermes"):
        if (cand / "skills").is_dir():
            return cand
    return LOCALAPPDATA / "hermes"


HERMES_HOME = _detect_hermes_home()

SOURCE_ROOTS = {
    "hermes": HERMES_HOME / "skills",
    "cline":  HOME / ".agents/skills",
    "gemini": GEMMA_I / "skills",
}

# Target untuk push
TARGET_ROOTS = {
    "hermes": HERMES_HOME / "skills",
    "cline":  HOME / ".agents/skills",
    "gemini": GEMMA_I / "skills",
}

HUB = Path("D:/SkillHub/skills")
DOCS = Path("D:/SkillHub/docs")


# ----------------------------------------------------------------------------
# Util
# ----------------------------------------------------------------------------
def skip_hidden(path: Path) -> bool:
    return path.name.startswith(".")


def find_skill_dirs(root: Path) -> list:
    """Kembalikan daftar folder skill (folder yang berisi SKILL.md) di root.
    recursive untuk mendukung struktur kategori hermes (cat/skill) dan flat."""
    results = []
    if not root.exists():
        return results
    for skill_md in root.rglob("SKILL.md"):
        if skip_hidden(skill_md):
            continue
        # folder berisi SKILL.md itu skill-nya
        d = skill_md.parent
        # lewati kalau ternyata makelar folder category yang tidak berisi SKILL.md langsung
        results.append(d)
    return results


def skill_name_of(dirpath: Path) -> str:
    return dirpath.name


def copy_skill(src_dir: Path, dst_dir: Path) -> tuple:
    """Salin skill. Menggabungkan (merge): file di tujuan yang LEBIH BARU tidak ditimpa.
    Return (added_files, skipped_newer_files)."""
    added, skipped = 0, 0
    if not dst_dir.exists():
        dst_dir.mkdir(parents=True)
    for src_path in src_dir.rglob("*"):
        if any(part.startswith(".") for part in src_path.relative_to(src_dir).parts):
            continue
        rel = src_path.relative_to(src_dir)
        dst_path = dst_dir / rel
        if src_path.is_dir():
            dst_path.mkdir(parents=True, exist_ok=True)
            continue
        # file
        if dst_path.exists():
            if dst_path.stat().st_mtime >= src_path.stat().st_mtime:
                skipped += 1
                continue
        try:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            added += 1
        except Exception as e:  # permission dsb
            print(f"    ! gagal salin {rel}: {e}")
    return added, skipped


# ----------------------------------------------------------------------------
# collect
# ----------------------------------------------------------------------------
def cmd_collect(args):
    print(f"Hub: {HUB}")
    HUB.mkdir(parents=True, exist_ok=True)
    seen = {}
    grand_added = 0
    for source, root in SOURCE_ROOTS.items():
        skills = find_skill_dirs(root)
        print(f"\n[{source}] {root} -> {len(skills)} skill ditemukan")
        for sd in skills:
            name = skill_name_of(sd)
            # cukup proses sekali per nama per pass ini (role terakhir selesai)
            if name in seen:
                print(f"  ~ {name}: dup (sudah dari {seen[name]}), skip")
                continue
            seen[name] = source
            added, skipped = copy_skill(sd, HUB / name)
            grand_added += added
    print(f"\nSelesai collect. {grand_added} file baru ditambahkan, sisanya sudah sinkron.")


# ----------------------------------------------------------------------------
# push
# ----------------------------------------------------------------------------
def cmd_push(args):
    target = args.target
    if target in TARGET_ROOTS:
        root = TARGET_ROOTS[target]
        label = f"agent: {target}"
    else:
        root = Path(target)
        label = f"custom path: {root}"
    print(f"Push hub -> {label}")
    root.mkdir(parents=True, exist_ok=True)
    if not HUB.exists():
        print("! Hub kosong/tidak ada. Jalankan collect dulu.")
        return
    total_added = 0
    for skill_dir in sorted([p for p in HUB.iterdir() if p.is_dir()]):
        name = skill_dir.name
        added, _ = copy_skill(skill_dir, root / name)
        if added:
            total_added += added
            print(f"  + {name} ({added} file)")
    print(f"Selesai push ke {label}. {total_added} file baru; sisanya sudah sinkron.")


# ----------------------------------------------------------------------------
# list
# ----------------------------------------------------------------------------
def cmd_list(args):
    if not HUB.exists():
        print("Hub kosong.")
        return
    names = sorted([p.name for p in HUB.iterdir() if p.is_dir()])
    print(f"Jumlah skill di hub: {len(names)}\n")
    for n in names:
        print(f"  - {n}")
    print("\nTotal:", len(names))


# ----------------------------------------------------------------------------
# manifest
# ----------------------------------------------------------------------------
def cmd_manifest(args):
    if not HUB.exists():
        print("! Hub tidak ada. Jalankan collect dulu.")
        return
    skills = []
    for skill_dir in sorted([p for p in HUB.iterdir() if p.is_dir()]):
        sk = skill_dir / "SKILL.md"
        desc = ""
        if sk.exists():
            text = sk.read_text(encoding="utf-8", errors="ignore")
            # ambil baris description dari frontmatter
            for line in text.splitlines():
                line = line.strip()
                if line.lower().startswith("description:"):
                    desc = line.split(":", 1)[1].strip().strip("\"'")
                    break
        mtime = datetime.fromtimestamp(skill_dir.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        skills.append({"name": skill_dir.name, "description": desc, "changed": mtime})

    DOCS.mkdir(parents=True, exist_ok=True)
    total = len(skills)

    # MANIFEST.json
    jdata = {
        "hub": str(HUB),
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "count": total,
        "skills": skills,
    }
    (DOCS / "MANIFEST.json").write_text(
        json.dumps(jdata, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # MANIFEST.md
    lines = [
        "# SkillHub — MANIFEST Skill",
        "",
        f"Total skill: **{total}**  ·  Di-generate: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "| Skill | Deskripsi | Terakhir diubah |",
        "|---|---|---|",
    ]
    for s in skills:
        d = (s["description"] or "-").replace("\n", " ").replace("|", "/")
        lines.append(f"| {s['name']} | {d} | {s['changed']} |")
    lines.append("")
    (DOCS / "MANIFEST.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Manifest dibuat: {DOCS/'MANIFEST.md'} & {DOCS/'MANIFEST.json'} ({total} skill)")


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="SkillHub sync")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("collect")
    p = sub.add_parser("push")
    p.add_argument("target", help="hermes|cline|gemini|/custom/path")
    sub.add_parser("pushall")
    sub.add_parser("list")
    sub.add_parser("manifest")
    args = parser.parse_args()

    if args.cmd == "collect":
        cmd_collect(args)
    elif args.cmd == "push":
        cmd_push(args)
    elif args.cmd == "pushall":
        for t in ["hermes", "cline", "gemini"]:
            args.target = t
            cmd_push(args)
    elif args.cmd == "list":
        cmd_list(args)
    elif args.cmd == "manifest":
        cmd_manifest(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()