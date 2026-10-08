# prd-authoring

# PRD Authoring & Agent Pack Generation

Convert raw product ideas → structured PRD → agent-ready project docs. Working tool: `/home/maulana/prd-studio/prd-studio.html` (single-file HTML+JS, OpenAI-compatible API, localStorage history).

## References
- `references/prd-frameworks.md` — research notes: Atlassian 8-section PRD, prd-creator 11-field input + 6-section output, ai-prd-generator ideas (clarification loop, verification), prompt engineering + Gemini endpoint.

## PRD structure (11 sections — synthesis of Atlassian + prd-creator + ai-prd-generator)
1. Ringkasan Eksekutif (produk, audiens, masalah, solusi, kenapa sekarang)
2. Latar Belakang & Problem Statement (konteks, dampak, kenapa layak)
3. Target Audiens & Persona (segmen utama/sekunder + 2-3 persona: profil, goals, frustrations)
4. Tujuan & Metrik Sukses (SMART KPI + target angka)
5. Fitur & Requirements — MVP per fitur: nama, deskripsi, prioritas P0/P1/P2, acceptance criteria; user stories "Sebagai [peran], saya ingin [aksi], agar [manfaat]" 2-3 per fitur; fitur post-MVP + alasan tunda
6. Persyaratan Teknis (stack + alasan, arsitektur/alur data, integrasi pihak ketiga)
7. Non-Fungsional (performa, keamanan, privasi, availability, usability)
8. Out of Scope (+ alasan)
9. Risiko & Open Questions (risiko + mitigasi, pertanyaan belum terjawab)
10. Roadmap (MVP → v1.1 → v1.2, estimasi kasar)
+ header meta: Versi | Status | Tanggal

## Agent pack (4 files)
- `PRD.md` — spesifikasi lengkap, dokumen acuan
- `AGENTS.md` — taruh di root project. Dibaca OTOMATIS oleh Hermes, Gemini CLI/Antigravity, VS Code Copilot/Codex. Isi: ringkasan project, tech stack, link PRD.md, aturan kerja (jangan scope creep, update tasks.md), checklist. Satu file nge-cover semua agent sekaligus.
- `tasks.md` — epic → story → acceptance criteria → sub-task teknis, urutan pengerjaan + dependensi
- `SKILL.md` — skill permanen. YAML frontmatter: `name` (lowercase, dash) + `description` (≤60 char, tanpa colon). Install:
  - Hermes: `~/.hermes/skills/<name>/SKILL.md` → auto-detect
  - Antigravity: `/mnt/c/Users/<winuser>/.gemini/config/skills/<name>/SKILL.md` → register `/name` setelah reload window
  - WSL user ≠ Windows user (maulana ↔ muham) — cek `/mnt/c/Users/` dulu

## Generation approach
- **Streaming** (default ON, toggle `optStream`): fetch dengan `stream: true`, parse SSE `data: ` lines, akumulasi `full` string, panggil `onChunk(full)` callback per delta. Real-time render ke pane. Tab yang streaming punya dot animasi hijau (`stream-dot` class). Auto-fallback: kalo stream gagal (API ga support / ReadableStream unavailable), fallback ke non-stream `callLLM` tanpa user action. Pattern: `callSmart(messages, onChunk)` — try stream first, catch → non-stream.
- **Parallel generate**: PRD harus selesai dulu (others depend on its content). Setelah itu AGENTS + tasks + skill jalan `Promise.all` bareng. Masing-masing streaming independent ke pane masing-masing. Progress bar: 0→30% (PRD) → 100% (parallel batch selesai).
- **Edit mode**: toggle `✏️ Edit` per tab → jadi `<textarea class="edit-area">`, input ke `LAST_RESULT[key]` via `onInput`. Switch tab atau klik Preview auto-save textarea content ke LAST_RESULT. Edit state reset pas regenerate.
- Jawaban klarifikasi user (scope MVP, persona, metrik sukses, batasan) di-inject ke prompt sebagai konteks tambahan
- Bahasa output ikut preferensi user (Indonesia default)
- Rekomendasi API: OpenAI-compatible endpoint (Gemini `/v1beta/openai/`, OpenRouter, proxy lokal). Key + base URL disimpan localStorage browser, gak pernah ke server lain.

## Pitfalls
- Async generate() WAJIB try/catch/finally — tanpa itu error API mati senyap di console, UI gak ngasih feedback, tombol stuck disabled.
- Double `style` attribute dalam satu tag HTML invalid — browser cuma pakai attribute pertama, jadi `display:none` di attribute kedua diabaikan → elemen selalu visible. Gabung jadi satu style attribute.
- SKILL.md description: cap ~60 char, tanpa colon (YAML parse error). Sama dengan gotcha skill_manage.
- AGENTS.md cukup 20-40 baris — jangan over-engineer. Agent baca file ini tiap kali mulai kerja di folder, terlalu panjang = dilompatin.
- Download banyak file sekaligus: tiap file butuh `<a download>` sendiri + `URL.revokeObjectURL` delayed (jangan langsung, file kedua bisa gagal).
- **SSE streaming**: `data: [DONE]` = stream selesai. Buffer partial lines — SSE chunks bisa split di tengah line. Pattern: split `\n`, `buf = lines.pop()`, proses `lines` yang complete. Kalo ga, chunk terakhir kepotong dan JSON.parse gagal diam-diam.
- **Parallel generate timing**: SKILL.md prompt butuh `tasks` content, tapi tasks jalan parallel dengan skill. Solusi: inject `out.tasks` (partial/streaming content) ke SKILL prompt — skill generate mulai setelah tasks punya content awal. Kalo tasks belum kelar, skill tetap jalan dengan partial tasks. Akzeptabel karena skill cuma butuh ringkasan epic, bukan full detail.
- **Edit mode state leak**: pas user switch tab saat lagi edit, HARUS save textarea content ke `LAST_RESULT` dulu sebelum render pane baru. Tanpa itu, edit hilang.

## Hermes integration bridge (browser → agent auto-run)

Browser JS CANNOT spawn `hermes` CLI (sandbox blocks terminal). Bridge that gap with a
zero-dependency Python stdlib companion server that (a) serves the single-file HTML and
(b) exposes a `/send` route. One click from PRD Studio → server writes the agent pack +
optionally spawns `hermes chat` in the project folder.

- **Server** `prd-studio-server.py` beside the HTML. `GET /` serves the page; `POST /send`
  accepts `{name, files:{PRD.md,AGENTS.md,tasks.md,SKILL.md}, auto_run}` and writes them to
  `~/prd-outbox/<slug>/`.
- **Why it's real integration**: `AGENTS.md` written to that folder is auto-read by Hermes
  when you `hermes chat` from there — agent gets full PRD context without re-explaining.
- **Auto-run** (opt-in toggle): `subprocess.Popen(f"{HERMES} chat -q \"...\"", cwd=proj)`.
  Redirect `stdout`/`stderr` to `run.log` (NOT DEVNULL — or the agent runs with zero trace).
  Save PID to `.run.pid`; guard against double-spawn by checking `/proc/<pid>` exists → return
  `already:true` instead of spawning again.
- **Live progress in browser (no `tail -f`)**: add `GET /run?name=X` returning a server-rendered
  HTML page that reads `run.log` + PID status and uses `<meta http-equiv="refresh" content="2">`
  (no JS, avoids empty-paren pitfalls). Also `GET /log?name=X` → JSON `{running, lines}`.
  Return a clickable `/run` link in the send-status ALWAYS (every branch: started / already /
  not-started / auto-run-off), not only in one branch.
- **File naming**: write exact-case names (`PRD.md`, `AGENTS.md`, `tasks.md`, `SKILL.md`) —
  don't `.lower` the basename; Hermes looks for `AGENTS.md` case-sensitively. Keep filenames in an
  allowlist (`{prd.md, agents.md, tasks.md, skill.md}`).
- **Model separation** (make clear to user): the PRD Studio dropdown picks the GENERATE model;
  the spawned `hermes chat` runs on Hermes' own configured model (not the generate model). Expose
  an override if the user wants them aligned.

## Inspecting a spawned agent (forensics)

When the user asks "is that PRD still generating?" / "cek di hermes sekarang lagi running apa",
do NOT guess — reconstruct actual state from the process table + `~/.hermes/logs/agent.log`.
Recurring source of user confusion: the PRD Studio web server (port 8678) stays alive forever,
so "something is running" is usually just the idle server, NOT an active generate job.

1. **Find agent processes**: `pgrep -af "hermes"`. Three distinct things show up:
   - `hermes_cli.main gateway run` — the always-on gateway (not a generate job)
   - `.../hermes` (foreground PTY) — an interactive CLI session (PID ≠ agent, this is a live chat)
   - `hermes chat -q ...` — a SPAWNED agent (this is the generate job). If absent, no generate is running.
   - Newer spawns may show as `hermes chat` under a PTY instead — check `ps --ppid <pid>` for children.
2. **Check `.run.pid`**: `cat ~/prd-outbox/<slug>/.run.pid` then `ps -o pid,etime,cmd -p <pid>`.
   PID absent/dead = the agent already finished (the project output lives in the folder; run.log is the trace).
3. **Reconstruct WHAT it did/is doing** from `~/.hermes/logs/agent.log` — every session has a
   stable ID like `20260823_171204_1c5b73`. `grep "<session_id>" agent.log | tail -40` reveals the
   full turn sequence: the user's message (`msg='...'`), each `agent.conversation_loop` API call,
   and each `agent.tool_executor` tool result. This IDs the exact task (e.g. "BrewVerse Coffee
   Landing Page") and whether it's mid-work or finished.
4. **Separate concurrent sessions**: Telegram-vs-CLI-vs-spawned agents all interleave in agent.log
   under different session IDs. The user may be running a manual CLI session (attach file, "ada
   disini...") while also chatting with you — don't conflate them. Grep by session_id, not by keyword.
5. **Stuck vs slow**: a huge `latency=` on one API call (e.g. 1000+ s) is a stream stall, not a hang —
   the agent usually resumes. `reason=interrupted_during_api_call` in the turn-ended line = the user
   Ctrl-C'd it.

## Previewing generated output

PRD Studio writes agent packs to `~/prd-outbox/<slug>/`. When the output includes web/HTML files the user wants to see live:

```bash
cd ~/prd-outbox/<slug> && python3 -m http.server 8680
# Open: http://localhost:8680
# From WSL: cmd.exe /c start http://localhost:8680
```

Use `terminal(background=true)` for the server (it's long-lived). Check port conflict first: `lsof -i :8680 || ss -tlnp | grep 8680`. If port busy, kill old process or pick another port.

Browser tools (`browser_navigate`) can load `http://localhost:8680` for DOM inspection. `browser_vision` may not return visual data on all models — rely on `browser_snapshot` for structure.

## Verify
- Buka via `file://` di browser (browser_navigate works on file paths).
- Tanpa API key: mock `window.callLLM` di console (`window.callLLM = async (msgs)=>{...}`) → `await generate()` → cek LAST_RESULT, tabs, panes. Restore `window.callLLM = window.__origCall` setelahnya.
- Tes path: tabs render + switch, download/copy, history save/load/delete, clarify questions, error path (API gagal → status err tampil, tombol balik aktif).
- `browser_console` expression untuk state check; `browser_vision` gak selalu bisa baca screenshot kalau model tanpa vision — andalkan DOM snapshot.

## Related
- antigravity-ide-skills: detail sync SKILL.md Hermes → Antigravity, pitfalls CRLF, skip antigravity-* skill.
