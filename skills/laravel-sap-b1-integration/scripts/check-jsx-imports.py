"""Cek komponen JSX yang DIPAKAI tapi TIDAK di-import.

`vite build` tetap sukses walau ada identifier JSX yang belum di-import, sehingga errornya baru muncul
saat halaman dibuka sebagai `ReferenceError: <Nama> is not defined` (halaman blank). Skrip ini
menemukannya sebelum build.

Pakai:
    python scripts/check-jsx-imports.py $(find resources/js -name "*.jsx")
    python scripts/check-jsx-imports.py resources/js/Pages/Settings/SapConfig.jsx
    python scripts/check-jsx-imports.py            # default: resources/js

Keluaran:
    [OK] resources/js/Pages/Settings/SapConfig.jsx
    [MISSING] resources/js/Layouts/AppLayout.jsx
              TIDAK di-import -> Ban
Exit code 1 bila ada yang bermasalah, jadi bisa dipakai sebagai gate.
"""

import glob
import re
import sys

DEFAULT_GLOBS = [
    "resources/js/**/*.jsx",
    "resources/js/**/*.tsx",
]


def files_from_args(argv):
    if argv:
        return argv
    found = set()
    for pattern in DEFAULT_GLOBS:
        found.update(glob.glob(pattern, recursive=True))
    return sorted(found)


def defined_names(src):
    """Nama yang tersedia di scope modul: import, deklarasi lokal, destructuring parameter."""
    names = set()

    # 1. import default + named (termasuk `as`)
    for m in re.finditer(r"import\s+([^;]+?)\s+from\s+['\"][^'\"]+['\"]", src, re.S):
        clause = m.group(1)
        for brace in re.finditer(r"\{([^}]*)\}", clause, re.S):
            for part in brace.group(1).split(","):
                name = part.strip().split(" as ")[-1].strip()
                if re.match(r"^[A-Za-z_$][\w$]*$", name):
                    names.add(name)
        head = re.sub(r"\{[^}]*\}", "", clause, flags=re.S).strip().rstrip(",").strip()
        if re.match(r"^[A-Za-z_$][\w$]*$", head):
            names.add(head)

    # 2. deklarasi lokal (const/let/var/function/class)
    for m in re.finditer(r"\b(?:const|let|var|function|class)\s+([A-Z][\w$]*)", src):
        names.add(m.group(1))

    # 3. destructuring di parameter fungsi, mis. setup({ el, App, props })
    for m in re.finditer(r"\(\s*\{([^}]*)\}\s*\)", src, re.S):
        for part in m.group(1).split(","):
            name = part.strip().split(":")[0].split("=")[0].strip()
            if re.match(r"^[A-Za-z_$][\w$]*$", name):
                names.add(name)

    return names


def main():
    paths = files_from_args(sys.argv[1:])
    if not paths:
        print("Tidak ada berkas JSX/TSX yang ditemukan.")
        return 0

    broken = 0
    for path in paths:
        try:
            src = open(path, encoding="utf-8").read()
        except OSError:
            print("SKIP (tidak bisa dibaca): " + path)
            continue

        used = set(re.findall(r"<\s*([A-Z][\w$]*)", src)) | set(
            re.findall(r"</\s*([A-Z][\w$]*)", src)
        )
        missing = sorted(used - defined_names(src))

        if missing:
            broken += 1
            print("[MISSING] " + path)
            print("        TIDAK di-import -> " + ", ".join(missing))
        else:
            print("[OK] " + path)

    print("\n%d berkas diperiksa, %d bermasalah." % (len(paths), broken))
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
