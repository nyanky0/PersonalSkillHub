---
name: hermes-skill-auto-sync
description: "Sync any new Hermes skill to Cline, Gemini, and SkillHub."
version: 1.0.0
author: Hermes Agent (Miku)
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [skills, sync, cline, gemini, antigravity, agy, workflow]
    related_skills: [agent-skill-sync, agent-skills-install]
---

# Hermes Skill Auto-Sync — tiap skill baru → semua agent

## When to Use (Kapan skill ini dipakai — TRIGGER WAJIB)

Pakai skill ini **setiap kali** terjadi salah satu dari ini di sesi Hermes:
- User menambahkan/install skill baru (dari `npx skills`, clone GitHub, atau buatan sendiri)
- User bikin skill baru lewat `skill_manage(action='create')` atau nulis SKILL.md manual
- User bilang "ada skill baru", "jangan lupa sync skill", "push skill ke agent lain"
- Selesai pakai `agent-skills-install` atau `writing-skills` → lanjutkan dengan skill ini

**Aturan inti: 1 skill baru = 4 lokasi + 1 otomatis.** Skill baru WAJIB ada di:

| # | Lokasi | Path |
|---|--------|------|
| 1 | Hermes | `E:\HERMES\skills\<name>\` (env `HERMES_HOME`; install lama di `%LOCALAPPDATA%\hermes\skills\`) |
| 2 | Cline / Antigravity IDE | `C:\Users\yudah\.agents\skills\<name>\` |
| 3 | Gemini CLI (Agent AI) | `C:\Users\yudah\.gemini\config\skills\<name>\` |
| 4 | Master hub | `D:\SkillHub\skills\<name>\` |
| — | Antigravity CLI (`agy`) | **otomatis** — agy baca dari `C:\Users\yudah\.agents\skills\` (folder yang SAMA dengan Cline), jadi begitu #2 ke-push, agy ikut dapat. Tidak ada path terpisah. |

> Catatan penting: Antigravity CLI (`agy.exe` di `C:\Users\yudah\AppData\Local\agy\bin\`) memang punya fitur "skill expansion" (slash-command skills), dan binary-nya mereferensi `.agents/skills/` + `AGENTS.md` — artinya agy memakai library skills global yang sama dengan Cline. Tidak perlu push tambahan untuk agy.

## Langkah (3 perintah, urut)

Jalankan dari folder mana pun (script pakai absolute path):

```bash
# 1. Tarik skill baru dari hermes (dan agent lain) ke hub
python D:/SkillHub/scripts/sync_skills.py collect

# 2. Sebarkan hub → hermes + cline + gemini sekaligus
#    (cline = folder .agents/skills → otomatis juga buat Antigravity CLI/agy)
python D:/SkillHub/scripts/sync_skills.py pushall

# 3. Refresh manifest (docs/MANIFEST.md + MANIFEST.json)
python D:/SkillHub/scripts/sync_skills.py manifest
```

Kalau cuma mau push ke satu target: `python D:/SkillHub/scripts/sync_skills.py push <target>` dengan target = `hermes|cline|gemini|<path kustom>`.

## Kasus khusus: install lewat `npx skills add ... -g -y`

`npx skills add` otomatis menulis ke `~/.agents/skills/` (Cline → agy ikut) + symlink ke Hermes, **TAPI TIDAK ke Gemini**. Setelah `add`, wajib:

```bash
for s in <nama-skill>; do cp -r "$HOME/.agents/skills/$s" "$HOME/.gemini/config/skills/$s"; done
```

lalu tetap jalankan `collect` + `pushall` + `manifest` di atas biar hub ikut update.

## Verifikasi (WAJIB sebelum bilang "beres")

Cek skill baru ada di 4 lokasi:

```bash
for loc in "E:/HERMES/skills" "C:/Users/yudah/.agents/skills" "C:/Users/yudah/.gemini/config/skills" "D:/SkillHub/skills"; do
  if [ -d "$loc/<nama-skill>" ]; then echo "OK: $loc/<nama-skill>"; else echo "MISSING: $loc/<nama-skill>"; fi
done
```

Semua harus `OK`. Kalau ada `MISSING`, ulangi `pushall` (atau `push gemini` kalau cuma Gemini yang kurang). Untuk agy: cukup cek folder `~/.agents/skills/<nama-skill>` (point #2) — agy otomatis kebaca.

## Pitfalls

- **Jangan cuma copy ke 1-2 lokasi** — aturannya 4 lokasi, Gemini paling sering kelewat.
- **agy TIDAK punya path skills sendiri** — jangan cari `~/.antigravity/skills` atau `~/.config/agy/skills`; agy pakai `.agents/skills` bersama Cline (sudah diverifikasi dari strings binary agy v1.1.26 yang mereferensi `.agents/skills/` dan `AGENTS.md`).
- **`sync_skills.py` itu idempotent** — aman dijalankan ulang; file yang sama/lebih baru tidak ditimpa.
- **MSYS path** — di git-bash, argumen program native (python/curl/uv) pakai path `C:/...` atau `D:/...`, jangan `/c/...` (bisa ke-mangle jadi `C:\c\...`).
- **Duplicate skill di hermes** — kalau hermes punya skill di top-level DAN di subfolder kategori (mis. `github/github-pr-workflow`), sync script menangani flattening otomatis; jangan hapus salah satunya manual tanpa cek.
- **Verifikasi count** — setelah push besar, cek konsistensi: jumlah folder = jumlah SKILL.md di target.

## Related
- `agent-skill-sync` — detail lengkap tentang master hub D:\SkillHub & perintah sync_skills.py.
- `agent-skills-install` — cara install skill dari ekosistem `npx skills` (GitHub/skills.sh).
- Skill ini melengkapi keduanya: fokus pada **refleks otomatis** setiap kali skill baru muncul di Hermes.