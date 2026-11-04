#!/usr/bin/env python3
"""
Backup Agent Mindset & Instructions Script for SkillHub
Backs up SOUL.md, GEMINI.md, AGENTS.md, MEMORY.md, and USER.md across:
- Antigravity 2 / Gemini CLI
- Antigravity IDE / Cline
- Hermes Agent
Also updates git-tracked D:/SkillHub/agent_mindsets directory.
"""

import shutil
from datetime import datetime
from pathlib import Path

SKILLHUB = Path("D:/SkillHub")
MINDSET_BACKUP_DIR = SKILLHUB / "agent_mindset_backups"
GIT_TRACKED_DIR = SKILLHUB / "agent_mindsets"

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
    "configs_gemini_mcp.json": Path("C:/Users/yudah/.gemini/config/mcp_config.json"),
    "configs_antigravity_mcp.json": Path("C:/Users/yudah/.gemini/antigravity/mcp_config.json"),
}

GIT_STRUCTURED_SOURCES = {
    "gemini/GEMINI.md": Path("C:/Users/yudah/.gemini/GEMINI.md"),
    "gemini/SOUL.md": Path("C:/Users/yudah/.gemini/memories/SOUL.md"),
    "gemini/USER.md": Path("C:/Users/yudah/.gemini/memories/USER.md"),
    "antigravity/GEMINI.md": Path("C:/Users/yudah/.gemini/antigravity/GEMINI.md"),
    "antigravity/mcp_config.json": Path("C:/Users/yudah/.gemini/antigravity/mcp_config.json"),
    "cline_agents/AGENTS.md": Path("C:/Users/yudah/.agents/AGENTS.md"),
    "cline_agents/SOUL.md": Path("C:/Users/yudah/.agents/memories/SOUL.md"),
    "cline_agents/USER.md": Path("C:/Users/yudah/.agents/memories/USER.md"),
    "hermes/SOUL.md": Path("E:/HERMES/SOUL.md"),
    "hermes/USER.md": Path("E:/HERMES/memories/USER.md"),
    "configs/gemini_mcp_config.json": Path("C:/Users/yudah/.gemini/config/mcp_config.json"),
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

    # Also sync to git-tracked agent_mindsets
    print("\n=== SYNCING TO GIT-TRACKED agent_mindsets ===")
    GIT_TRACKED_DIR.mkdir(parents=True, exist_ok=True)
    for rel_path, src_path in GIT_STRUCTURED_SOURCES.items():
        if src_path.exists():
            dst = GIT_TRACKED_DIR / rel_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst)
            print(f"Synced git-tracked: {rel_path}")
    print("Git-tracked agent_mindsets updated successfully.")


def main():
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_mindset(timestamp_str)


if __name__ == "__main__":
    main()
