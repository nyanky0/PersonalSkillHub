#!/usr/bin/env python3
"""Hermes memory bridge to Mnemosyne.

Replace the old MEMORY.md/USER.md single-file approach with
real-time recall via the Mnemosyne Python SDK.

Usage:
    python3 mnemosyne_bridge.py recall "query..."
    python3 mnemosyne_bridge.py remember "fact text"
    python3 mnemosyne_bridge.py forget "query..."
"""
import os
import sys
from pathlib import Path

# Ensure mnemosyne venv packages are importable
MNEMOSYNE_VENV = os.path.expanduser("~/.venvs/mnemosyne/lib/python3.14/site-packages")
if MNEMOSYNE_VENV not in sys.path:
    sys.path.insert(0, MNEMOSYNE_VENV)

# Set explicit DB path to avoid default location confusion
DB_DIR = Path.home() / ".hermes" / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MNEMOSYNE_DB_PATH", str(DB_DIR / "mnemosyne.db"))

from mnemosyne import remember, recall, forget

# ---- config ----
LEGACY_DIR = Path.home() / ".hermes" / "memories"
LEGACY_FILES = [LEGACY_DIR / "MEMORY.md", LEGACY_DIR / "USER.md"]
MIGRATED_MARKER = DB_DIR / ".migrated"


# ---- migration (run once) ----
def migrate_legacy():
    if MIGRATED_MARKER.exists():
        return
    for f in LEGACY_FILES:
        if f.exists():
            txt = f.read_text()
            chunks = [p.strip() for p in txt.split("\u00a7") if p.strip()]
            bank = "user_context" if "USER" in f.name else "working_memory"
            source = "user_profile" if "USER" in f.name else "working_memory"
            for chunk_text in chunks:
                remember(chunk_text, source=source, scope="global", bank=bank)
    MIGRATED_MARKER.touch()


# ---- public API ----
def load_memory(query: str = "preferences user context", top_k: int = 15) -> str:
    """Return a compact text block suitable for injection into prompt."""
    migrate_legacy()
    results = recall(query, top_k=top_k)
    if not results:
        return ""
    lines = []
    for r in results:
        content = r.get("content", "").strip()
        if len(content) < 2000:
            lines.append(f"- {content}")
    return "\n".join(lines)


def save_memory(fact: str, source: str = "conversation", importance: float = 0.5) -> None:
    """Store a single fact into Mnemosyne."""
    remember(fact, source=source, importance=importance, scope="session")


def forget_memory(query: str) -> int:
    """Best-effort: forget top recall hits. Returns count forgotten."""
    results = recall(query, top_k=5)
    count = 0
    for r in results:
        try:
            forget(r["id"])
            count += 1
        except Exception:
            pass
    return count


# ---- CLI ----
if __name__ == "__main__":
    migrate_legacy()
    if len(sys.argv) < 2:
        print("usage: mnemosyne_bridge.py [recall|remember|forget] ...")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "recall":
        q = " ".join(sys.argv[2:]) or "preferences user context"
        print(load_memory(q))
    elif cmd == "remember":
        fact = " ".join(sys.argv[2:])
        if not fact:
            print("fact required", file=sys.stderr)
            sys.exit(2)
        save_memory(fact)
        print("stored")
    elif cmd == "forget":
        q = " ".join(sys.argv[2:])
        n = forget_memory(q)
        print(f"forgot {n}")
