# 🧠 Agent Core Mindsets, Personas & System Instructions

Repository pusat instruksi dasar, persona, memori jangka panjang, dan konfigurasi MCP untuk seluruh ekosistem AI Agent.

---

## 📂 Struktur Direktori

| Direktori | Target Runtime | File Kunci | Deskripsi |
| :--- | :--- | :--- | :--- |
| **gemini/** | Gemini CLI / Antigravity 2 | GEMINI.md, SOUL.md, MEMORY.md, USER.md | Instruksi sistem global, persona Miku-chan, memori jangka panjang, dan profil dev. |
| **ntigravity/** | Antigravity Engine | GEMINI.md, mcp_config.json | Konfigurasi runtime Antigravity dan schema MCP server. |
| **cline_agents/** | Cline & Antigravity IDE | AGENTS.md, SOUL.md, MEMORY.md, USER.md | SSOT instruksi agent universal untuk ekstensi VS Code dan IDE. |
| **hermes/** | Hermes Agent | SOUL.md, MEMORY.md, USER.md | Karpathy engineering guidelines, token efficiency protocol, dan persona Miku-chan. |
| **configs/** | Global Configs | gemini_mcp_config.json | Konfigurasi MCP server terpusat. |

---

## 🔄 Pembaruan Otomatis

Untuk memperbarui file-file ini secara otomatis dari environment lokal, jalankan:
`ash
python D:/SkillHub/scripts/backup_agent_mindset.py
`
