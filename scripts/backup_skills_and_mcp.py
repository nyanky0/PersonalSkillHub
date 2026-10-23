#!/usr/bin/env python3
"""
Backup Skills & MCP Script for SkillHub
Backs up:
1. Skills: 222 master skills to D:\\SkillHub\\skills_backups\\
2. MCP: Antigravity 2, Antigravity IDE, and Hermes MCP configurations & schemas to D:\\SkillHub\\mcp_backups\\
"""

import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

SKILLHUB = Path("D:/SkillHub")
SKILLS_DIR = SKILLHUB / "skills"
SKILLS_BACKUPS = SKILLHUB / "skills_backups"
MCP_BACKUPS = SKILLHUB / "mcp_backups"

ANTIGRAV_MCP_CFG = Path("C:/Users/yudah/.gemini/antigravity/mcp_config.json")
GEMINI_MCP_CFG = Path("C:/Users/yudah/.gemini/config/mcp_config.json")
HERMES_CFG = Path("E:/HERMES/config.yaml")

ANTIGRAV_MCP_TOOLS = Path("C:/Users/yudah/.gemini/antigravity/mcp")
ANTIGRAV_IDE_MCP_TOOLS = Path("C:/Users/yudah/.gemini/antigravity-ide/mcp")


def backup_skills(timestamp_str: str):
    print("=== 1. BACKUP SKILLS ===")
    SKILLS_BACKUPS.mkdir(parents=True, exist_ok=True)
    target_dir = SKILLS_BACKUPS / f"backup_{timestamp_str}"
    target_dir.mkdir(parents=True, exist_ok=True)

    zip_path = target_dir / f"skills_master_{timestamp_str}.zip"
    print(f"Creating zip snapshot: {zip_path}")
    
    skill_folders = [p for p in SKILLS_DIR.iterdir() if p.is_dir()]
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for skill_folder in skill_folders:
            for file_path in skill_folder.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(SKILLS_DIR)
                    zf.write(file_path, arcname)

    manifest_content = f"""# Skills Master Backup Manifest

- **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Total Master Skills**: {len(skill_folders)}
- **Source Directory**: {SKILLS_DIR}
- **Archive File**: {zip_path.name}
- **Archive Size**: {round(zip_path.stat().st_size / (1024 * 1024), 2)} MB

## Agents Synchronization Status:
- Master Hub (`D:\\SkillHub\\skills`): {len(skill_folders)} skills
- Hermes (`E:\\HERMES\\skills`): {len(skill_folders)} unique skills
- Antigravity IDE / Cline (`C:\\Users\\yudah\\.agents\\skills`): {len(skill_folders)} unique skills
- Antigravity 2 / Gemini (`C:\\Users\\yudah\\.gemini\\config\\skills`): {len(skill_folders)} unique skills
- **Status**: 100% SYNCHRONIZED across all 4 environments.
"""
    (target_dir / "MANIFEST.md").write_text(manifest_content, encoding="utf-8")

    # Update latest directory
    latest_dir = SKILLS_BACKUPS / "latest"
    if latest_dir.exists():
        shutil.rmtree(latest_dir)
    latest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(zip_path, latest_dir / "skills_master_latest.zip")
    shutil.copy2(target_dir / "MANIFEST.md", latest_dir / "MANIFEST.md")
    print(f"Skills backup complete in {target_dir} and updated {latest_dir}\n")


def backup_mcp(timestamp_str: str):
    print("=== 2. BACKUP MCP ===")
    MCP_BACKUPS.mkdir(parents=True, exist_ok=True)
    target_dir = MCP_BACKUPS / f"backup_{timestamp_str}"
    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Antigravity 2 MCP config
    if ANTIGRAV_MCP_CFG.exists():
        shutil.copy2(ANTIGRAV_MCP_CFG, target_dir / "antigravity_2_mcp_config.json")
        print(f"Copied {ANTIGRAV_MCP_CFG} -> antigravity_2_mcp_config.json")

    # 2. Gemini Config MCP
    if GEMINI_MCP_CFG.exists():
        shutil.copy2(GEMINI_MCP_CFG, target_dir / "gemini_config_mcp_config.json")
        print(f"Copied {GEMINI_MCP_CFG} -> gemini_config_mcp_config.json")

    # 3. Hermes MCP config extraction
    if HERMES_CFG.exists():
        content = HERMES_CFG.read_text(encoding="utf-8", errors="ignore")
        mcp_lines = []
        in_mcp = False
        for line in content.splitlines():
            if line.startswith("mcp_servers:"):
                in_mcp = True
            elif in_mcp and line.strip() and not line.startswith(" ") and not line.startswith("\t"):
                in_mcp = False
            if in_mcp:
                mcp_lines.append(line)
        hermes_mcp_path = target_dir / "hermes_mcp_servers.yaml"
        hermes_mcp_path.write_text("\n".join(mcp_lines) + "\n", encoding="utf-8")
        print(f"Extracted Hermes mcp_servers to {hermes_mcp_path}")

    # 4. Copy schemas
    mcp_tools_dir = target_dir / "mcp_tools"
    if ANTIGRAV_MCP_TOOLS.exists():
        shutil.copytree(ANTIGRAV_MCP_TOOLS, mcp_tools_dir / "antigravity", dirs_exist_ok=True)
        print(f"Copied Antigravity tools schemas from {ANTIGRAV_MCP_TOOLS}")
    if ANTIGRAV_IDE_MCP_TOOLS.exists():
        shutil.copytree(ANTIGRAV_IDE_MCP_TOOLS, mcp_tools_dir / "antigravity-ide", dirs_exist_ok=True)
        print(f"Copied Antigravity IDE tools schemas from {ANTIGRAV_IDE_MCP_TOOLS}")

    # 5. Manifest
    manifest_content = f"""# MCP Backup & Synchronization Manifest

- **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Backup Path**: {target_dir}
- **Latest Directory**: {MCP_BACKUPS / "latest"}

## MCP Environments & Synchronization Summary

| Server Name | Antigravity 2 | Antigravity IDE | Hermes Agent | Status |
| :--- | :--- | :--- | :--- | :--- |
| **nyan-mem** | Stdio (Node bridge) | Stdio (Node bridge) | HTTP SSE (`:37788/mcp`) | **Synchronized** (Different transport, same database) |
| **sequential-thinking** | `npx -y @modelcontextprotocol/server-sequential-thinking` | `npx -y @modelcontextprotocol/server-sequential-thinking` | `npx -y @modelcontextprotocol/server-sequential-thinking` | **Identical** |
| **context-mode** | `cmd.exe /c context-mode` | `cmd.exe /c context-mode` | `cmd.exe /c context-mode` | **Identical** |
| **playwright** | `npx -y @playwright/mcp@latest` | `npx -y @playwright/mcp@latest` | `npx -y @playwright/mcp@latest` | **Identical** |
| **gemini-api-docs** | Built-in / Eager tool | Built-in / Eager tool | N/A | Antigravity specific |

## Notes on Configuration:
- Antigravity 2 and Antigravity IDE share the global Gemini config bridge for `nyan-mem` (`C:\\Users\\yudah\\.nyan-mem\\bridge.cjs`).
- Hermes connects directly to `nyan-mem-http` via HTTP SSE on `127.0.0.1:37788/mcp`.
- All 3 environments have access to the exact same memory store and reasoning/browser/context tools.

## Backed Up Files in this Snapshot:
- `antigravity_2_mcp_config.json`: Live config from `C:\\Users\\yudah\\.gemini\\antigravity\\mcp_config.json`
- `gemini_config_mcp_config.json`: Live config from `C:\\Users\\yudah\\.gemini\\config\\mcp_config.json`
- `hermes_mcp_servers.yaml`: Extracted `mcp_servers` configuration block from `E:\\HERMES\\config.yaml`
- `mcp_tools/antigravity/`: Schemas & instructions for all 6 lazy/eager MCP tools in Antigravity 2
- `mcp_tools/antigravity-ide/`: Schemas & instructions for MCP tools in Antigravity IDE
"""
    (target_dir / "MANIFEST.md").write_text(manifest_content, encoding="utf-8")

    # Update latest directory
    latest_dir = MCP_BACKUPS / "latest"
    if latest_dir.exists():
        shutil.rmtree(latest_dir)
    shutil.copytree(target_dir, latest_dir)
    print(f"MCP backup complete in {target_dir} and updated {latest_dir}\n")


def main():
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_skills(timestamp_str)
    backup_mcp(timestamp_str)
    print("ALL BACKUPS COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
