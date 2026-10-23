#!/usr/bin/env python3
"""
Backup Agent Mindset & Instructions Script for SkillHub
Backs up SOUL.md, GEMINI.md, AGENTS.md, MEMORY.md, and USER.md across:
- Antigravity 2 / Gemini CLI
- Antigravity IDE / Cline
- Hermes Agent
"""

import shutil
from datetime import datetime
from pathlib import Path

MINDSET_BACKUP_DIR = Path("D:/SkillHub/agent_mindset_backups")

SOURCES = {
    "GEMINI.md": Path("C:/Users/yudah/.gemini/GEMINI.md"),
    "ANTIGRAVITY_GEMINI.md": Path("C:/Users/yudah/.gemini/antigravity/GEMINI.md"),
    "GEMINI_memories_SOUL.md": Path("C:/Users/yudah/.gemini/memories/SOUL.md"),
    "GEMINI_MEMORY.md": Path("C:/Users/yudah/.gemini/memories/MEMORY.md"),
    "GEMINI_USER.md": Path("C:/Users/yudah/.gemini/memories/USER.md"),
    "AGENTS_agents_dir.md": Path("C:/Users/yudah/.agents/AGENTS.md"),
    "AGENTS_memories_SOUL.md": Path("C:/Users/yudah/.agents/memories/SOUL.md"),
    "AGENTS_MEMORY.md": Path("C:/Users/yudah/.agents/memories/MEMORY.md"),
    "AGENTS_USER.md": Path("C:/Users/yudah/.agents/memories/USER.md"),
    "HERMES_SOUL.md": Path("E:/HERMES/SOUL.md"),
    "HERMES_MEMORY.md": Path("E:/HERMES/memories/MEMORY.md"),
    "HERMES_USER.md": Path("E:/HERMES/memories/USER.md"),
}


def backup_mindset(timestamp_str: str):
    print("=== BACKUP AGENT MINDSET & INSTRUCTIONS ===")
    MINDSET_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    target_dir = MINDSET_BACKUP_DIR / f"backup_{timestamp_str}"
    target_dir.mkdir(parents=True, exist_ok=True)

    copied = []
    for dest_name, src_path in SOURCES.items():
        if src_path.exists():
            # Copy to timestamped folder
            dest_file = target_dir / dest_name
            shutil.copy2(src_path, dest_file)
            # Copy to latest flat file in MINDSET_BACKUP_DIR
            latest_file = MINDSET_BACKUP_DIR / f"latest_{dest_name}"
            shutil.copy2(src_path, latest_file)
            copied.append((dest_name, src_path))
            print(f"Backed up: {src_path} -> {dest_name}")
        else:
            print(f"Skipped (missing): {src_path}")

    # Write Manifest
    manifest_lines = [
        "# Agent Mindset & Persona Backup Manifest",
        f"- **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Backup Folder**: {target_dir}",
        "",
        "## Backed Up Files:",
    ]
    for dest_name, src_path in copied:
        mtime = datetime.fromtimestamp(src_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        manifest_lines.append(f"- **{dest_name}**: Source `{src_path}` (mtime: `{mtime}`)")

    manifest_content = "\n".join(manifest_lines) + "\n"
    (target_dir / "MANIFEST.md").write_text(manifest_content, encoding="utf-8")
    (MINDSET_BACKUP_DIR / "latest_MANIFEST.md").write_text(manifest_content, encoding="utf-8")
    print(f"\nMindset backup complete in {target_dir} and updated latest_* files.")


def main():
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_mindset(timestamp_str)


if __name__ == "__main__":
    main()
