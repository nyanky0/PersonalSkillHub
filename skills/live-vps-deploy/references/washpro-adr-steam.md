# Washpro / ADR Steam ERP — active engagement notes

SP IKG carwash ERP (Laravel Blade). Business: cuci steam + resto. Bug: sistem payroll ≠ manual Excel.

## VPS layout (live)

- Host: Debian `SteamADR` 103.127.139.80, user `adr-steam-debian`. SSH key already copied to `~/.ssh/adr-steam-debian.pem` on this WSL box.
- Compose: `/opt/washpro/docker-compose.yml`
  - `adr-steam-app` — image `maulsss/washpro:v76` since 2026-09-01 (was v75; old image tagged `maulsss/washpro:backup-v75` on VPS). Volumes: `washpro_storage-data` → `/var/www/html/storage`, bind `/opt/washpro/.env` → `/var/www/html/.env`
  - `adr-steam-nginx` — nginx:1.27-alpine, ports 80/443, serves bind-mounted `/opt/washpro/public`. NO asset sync needed: pos.blade.php frontend is fully CDN (Vue unpkg, Tailwind CDN script, SweetAlert2, Chart.js) — `public/build` is never referenced by the live pages. Verified by grepping rendered HTML.
  - `adr-steam-mysql` — mysql:8.0, data in volume `washpro_mysql-data`. LIVE transactional DB. User explicitly forbade touching it. Creds in compose: user `laravel` / db `adr_steam` (password in compose file); root creds also available for sandbox creation.
- Entrypoint `/usr/local/bin/docker-entrypoint.sh` NOW GATED (v76): migrate+seed only when `RUN_MIGRATIONS=1`, default OFF. Verified in container logs: "Migrations/seeders SKIPPED".

## Source code

- Local Windows: `C:\laragon\www\washpro` → `/mnt/c/laragon/www/washpro`
- All payroll logic in ONE controller: `app/Http/Controllers/PosController.php` (fat controller). `calculatePayroll()` at line ~1624; `getPayrollSlip()` ~line 1990. Models have `$guarded = []`. Routes in `routes/web.php` lines 114-123.
- Views: `resources/views/pos.blade.php` (Vue 3 inline app — payroll modal ~line 3098), `resources/views/payroll_slip.blade.php` (printable slip, 320px receipt style).
- Docker build from WSL: `/mnt/c/Windows/System32/cmd.exe /c "docker build ..."`; Docker Hub user `maulsss` (login persisted on Windows side). `node_modules` installable in WSL (node v22 at `~/.local/bin/node`) — `npm install && npm run build` works locally for verification.

## Manual payroll logic (from "Pendataan Gaji Bulan Agustus  2026.xlsx", sheet EXCEL — note DOUBLE SPACE before 2026 in filename)

- Rows 3 = header, 4-34 = days 1-31, columns C-R = 16 employees (SOFI, ANDINI, MAS JOKO, PAK ACU, PAK SAHYA, AGUNG, ALDI, ASEP, IBAY, GUSTIAN, SAPUTRA, APIT, IDRUS, IQBAL, ABDULLAH, OPICK). Row 35 = totals, row 36 = final rounded salaries.
- Per-employee per-day cells: NUMBER = share that day; `'-'` = absent. NOT checkmarks. Attendance per worker = count of non-`-` cells.
- `S` (daily car revenue) = `50000 x Z`; `Y` (bonus) = `5000 x AA`; per-employee daily = `(Sx30% + Y) / U` (U = present that day).
- Monthly (row 36) = round UP to nearest 10,000 of Sum daily, plus owner manual extras (MAS JOKO +1,000,000).
- Row 17 (day 17) all `-`: shop closed (DB also has no transactions that day).

## Deployed fix (v76, 2026-09-01)

`calculatePayroll()` rewritten: per-day loop — daily pool = mobil x 50000 x pool% + motor x 5000, split equally among present workers (ALL roles incl. kasir SOFI/ANDINI; base salary path removed). Reads `pool_percentage` from `payroll_settings`. Per-worker: `rounding_amount` (ceil to 10k when `rounding_enabled=1`), `manual_adjustment` (from request `adjustments` map — UI modal has per-worker input). Slip + POS modal + `getPayrollSlip` updated to new fields.

Schema change applied (live, via `docker exec mysql` as root): `payroll_details` gained `manual_adjustment DECIMAL(15,2) DEFAULT 0` + `rounding_amount DECIMAL(15,2) DEFAULT 0` (after `tip_included`). Migration file shipped in repo: `database/migrations/2026_09_01_000001_add_adjustment_rounding_to_payroll_details.php`.

Verification done: sandbox DB (`adr_steam_test`, created/restored as root, DROPPED after) + standalone PHP script in container → 17/17 worker match vs Python re-computation; `php -l` all changed files; `view:cache` compiles; HTTP 200; entrypoint skip confirmed; image contents grepped pre-push.

## Residual deltas — RESOLVED 2026-09-01 (final verdict: the sheet was wrong, system correct)

Payroll id=4 (Aug 2026, recalculated on v76) total 19,130,000 vs Excel 19,430,000. Gap -240,000 splits into:
1. **-206,667 = day 9 MANUAL CALCULATION ERROR IN THE EXCEL.** User initially said the sheet was right ("gw hitung manual ulang"), then with full evidence reversed: "kesalahan dari sisi excel untuk yang tanggal 9". Evidence that settled it:
   - Day 9 sheet: V=1,136,667 but formula from its OWN inputs (61 mobil × 15,000 + 3 motor × 5,000) = 930,000; the 1,136,667 matches NO derivable formula from that day's numbers.
   - ALL other 30 days match the formula exactly — day 9 is the single outlier.
   - Sheet's own count column U=9 "karyawan" while 11 employees received 103,333 that day (1,136,667 ÷ 11 = 103,333.33 exactly) — typo inside the sheet; the split used 11, matching DB attendance (11 Hadir, 5 Sakit/Izin — attendance matched DB 100% for all 16 workers, all month).
   - The pending Mobil 57,000 (INV-20260809-2669, plate B 1585 NP, cashier Sofi, workflow Selesai but never paid) was a red herring for pool math: user said those stuck pendings should be cancelled.
2. **-33,333 = rounding order** (Excel rounds sum-including-error; system rounds pure sum).
3. **rounding was silently OFF** — `rounding_enabled` row did not exist in DB. FIXED this session.

## Correct final numbers (Aug 2026, system truth)

Total 19,190,000 with rounding ON + Mas Joko adj 1,000,000. Per worker: Joko 2,430,000 / Sahya & Agung 1,230,000 / Asep 1,210,000 / Abdullah, Aldi, Pak Acu 1,160,000 / Sofi 1,150,000 / Iqbal 1,140,000 / Ibay 1,130,000 / Andini 1,120,000 / Opick 1,110,000 / Gustian 1,090,000 / Saputra 1,030,000 / Idrus 950,000 / Apit 890,000. Excel's 19,430,000 is inflated by the day-9 error. User still needs to recompute payroll in UI (delete id=4, rerun with Joko adj) to store these values.

## DB changes applied 2026-09-01 (session 2, with user authorization)

- `UPDATE transactions SET payment_status='cancelled' WHERE payment_status='pending'` — all 17 stuck pendings (Aug 4-11: 8 Warung + 8 Mobil + 1 more, total 225,000). Soft-cancel chosen over DELETE for audit trail + reversibility. No effect on payroll (queries filter `paid`).
- `INSERT INTO payroll_settings (`key`, value) VALUES ('rounding_enabled', '1')` — note backticks: `key` is a MySQL reserved word, plain insert fails with exit 1 MID-BATCH (earlier statements in the same `-e` string still executed — always re-SELECT to check what landed after a partial batch failure).

## Query pitfalls (this DB)

- Vehicle counts key on `vehicle_type` ('Mobil'/'Motor'/'Warung'), NOT `business_type` ('steam'/'combined'/'food'/'motor'). An ad-hoc filter on `business_type='motor'` returns ZERO motor units → totals silently wrong (20.99jt vs true 19.13jt). Always `GROUP BY vehicle_type` first when reconciling units.
- `payrolls` has `period`/`start_date`/`end_date` (NOT `period_start`/`period_end`).
- `transactions` has `total` (NOT `total_amount`); also `subtotal`, `cash_given`, `cash_change`.
- `SHOW COLUMNS FROM transactions LIKE '%type%'` to discover discriminators before writing ad-hoc SQL.
- SSH+docker exec+mysql quoting: inline `-e "..."` with nested quotes failed 4x (silent empty + exit 1). Reliable path: write SQL to local file → `scp` → `docker exec -i mysql < file`. Works first try.

## Excel reading pattern that worked

Two `load_workbook` passes (formulas `data_only=False` + values `data_only=True`). openpyxl lives in venv `~/.venvs/xlsx` (system python has no pip; PEP 668). Pull DB dumps to local `/tmp/*.tsv` via SSH + compare in one Python script — keeps reconciliation reproducible.

## v77 deploy (2026-09-01 session 3): rounding convention CHANGED to nearest-10k

User correction: "rounding nya rentang antara 5000 sampai dengan 10000 saja jadi cari yang terdekat" — round to NEAREST 10,000, not always-up. One-line change in `calculatePayroll()` line ~1792: `ceil($rawEarned/10000)*10000` → `round($rawEarned/10000)*10000`. `rounding_amount` can now be negative. Built v77, pushed, deployed (compose tag sed v76→v77; first `docker compose pull` from VPS timed out to Docker Hub but retry succeeded — verify with `docker images --digests` that the running digest matches the pushed digest `sha256:4115...`). Verified: `php -l` in container, `round()` present at line 1792, runtime `php -r` spot-check of three raw values, `npm run build` PASS. Aug-2026 effect: 19,210,000 (ceil) → 19,140,000 (nearest); 8 workers -10,000 each. Historical payroll id=6 was computed under the old always-up rule and stays as stored; future payrolls use nearest.

Also: user revealed the POS DOES have a void button (agent wrongly claimed no cancel feature exists after only grepping routes for 'cancel' — `void` was the actual keyword). LESSON: when asserting a feature doesn't exist, grep for ALL common synonyms (cancel/void/batal/refund/nullify) across routes AND views before claiming absence; and prefer asking the user "does the app have X?" over declaring it missing.

## Session 4 (2026-09-01, later): revenue reconciliation + open bugs

User asked about two NEW issues (beyond payroll):

1. **Payroll period default wrong**: UI modal `showCalculatePayroll()` (pos.blade.php ~line 3111) defaults `firstDay = start of CURRENT month` and `end = today`. Calculating August on Sep 1 produced Aug 1 → Sep 1. NOT YET FIXED — planned fix: end default = last day of start month (`new Date(y, m+1, 0)`).

2. **Revenue vs manual cash count (DATA KEUANGAN.xlsx)**: user said system short by 198,000 vs manual. Real findings:
   - Sheet `AGUSTUS` has per-day columns: Mobil/Motor/Cash Asli/Cash Sistem/Qris Asli/Qris Sistem/TOTAL ASLI/TOTAL SISTEM/Parfum/Keterangan. The Keterangan column explains nearly every residual (perfume sold off-POS, tips, cash↔QRIS swaps). Parfum total Aug = 945,000 (27 units × 35,000) — sold by staff, never entered in POS.
   - ASLI total 66,560,000 vs Excel-recorded SISTEM 65,977,000 (Δ 583,000, all explained by owner's own notes: off-POS perfume + tips + swaps).
   - Excel-recorded SISTEM 65,977,000 vs live DB paid now 65,749,000 (Δ 228,000 ≈ the 225,000 of soft-cancelled pendings) → **`reportSummary()` (PosController ~line 806) filters `status != 'Process'` but NOT payment_status — cancelled transactions still counted in daily reports**. The owner's recorded "system" figures were snapshots including pending. NOT YET FIXED — planned: add `->where('payment_status', '!=', 'cancelled')`. Same audit needed for `exportPDF`/`exportExcel`.
   - User's "198,000" number itself never exactly reproduced; likely a partial-view figure (cash side: DB cash 42,531,000 vs sheet ASLI cash 42,334,000 = 197,000, sheet Sistem cash 42,759,000). Presented buckets, user did not disambiguate.
   - DB paid Aug breakdown: Mobil 61,433,000 + Motor 2,958,000 + Warung 1,358,000 = 65,749,000. `food_transactions` table exists but has 0 rows Aug (warung sales live in `transactions` as vehicle_type='Warung').

## Session 5 (2026-09-01): per-day slip breakdown (v79)

User: "rubah slip gaji nya agar seperti di excel yang keliatan per harinya" — printable slip must show per-day rows (date, mobil units, motor units, pool, recipients, daily earn), like the Excel's daily columns.

Implementation pattern (NO schema change — `payroll_details` stores only aggregates):
- `getPayrollSlip()` gained an on-the-fly daily loop: query transactions (same filters as `calculatePayroll`: `status='Done'`, `business_type IN (steam,combined)`, branch, period), bucket mobil/motor per day via `substr(created_at,0,10)` + `vehicle_type`; query attendance per day for recipient counts; loop `strtotime('+1 day')` over the full period emitting one row per calendar day (absent day → `earned: null`, rendered as `-` like Excel's `-` cells). Settings (pool_percentage, mobil_flat_rate, motor_incentive_amount) re-read so breakdown matches current formula. Exposed as `slip['daily']` in the JSON.
- Slip view `payroll_slip.blade.php` gained `RINCIAN HARIAN` table (tgl d/m, 🚗, 🛵, Org, Gaji, JUMLAH row, footnote explaining rates) between absensi and komponen gaji.
- Gotchas hit this session: (a) inserted the block referencing `$transactions` BEFORE its definition — intelephense caught use-before-assign, `php -l` did NOT; (b) a later duplicate `$transactions` query in the same function removed to avoid shadowing; (c) tested with stale payroll id=6 → ModelNotFoundException (user had deleted/recreated payroll; live id now 8, period 2026-08, total 19,140,000); (d) response JSON nests under top-level `slip` key; (e) Blade renders only via `?print=1` (`$request->has('print')`), default returns JSON; (f) real URL is `/api/payroll/{id}/slip/{name}` — route prefix, `/payroll/...` without `/api` 404s.
- Verification: tinker `sum(daily)=1,429,403` vs stored `pool_share=1,429,405` (2 rupiah = per-day display rounding, acceptable); curl `?print=1` HTTP 200 with table present (31 rows + JUMLAH); php -l local + in-container; npm build PASS.
- Version sequence: v75 → v76 (payroll rewrite + gated entrypoint) → v77 (nearest rounding) → v78 (report filters + period default) → v79 (slip daily breakdown). Backup tag on VPS: `maulsss/washpro:backup-v75`.

## Session 6 (2026-09-01): dashboard period bug — `toISOString()` UTC off-by-one (v80)

User: "pada tab dashboard periode nya masih sama belum berubah" — despite v78 fixing the payroll modal period default, the DASHBOARD tab still showed "end of last month → today" (e.g. 31/08 → 01/09 on Sep 1).

**Root cause (a whole bug CLASS, not a washpro quirk):** `new Date().toISOString().split('T')[0]` converts to UTC before slicing. In UTC+7 (WIB), any local date between 00:00–07:00 shifts back one day in UTC. So `new Date(2026, 8, 1)` (Sep 1 00:00 local) → "2026-08-31" in UTC. Month boundaries silently render as the previous month's last day. `php -l` and `npm run build` both pass — it's a logic bug only visible at runtime before 7am or in month-boundary defaults.

**Fix pattern:** local-time formatter helper, used EVERYWHERE a date becomes a string:
```js
const localISO = (d) => `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
```
Injected once above `createApp({` in pos.blade.php, then bulk-replaced every `new Date().toISOString().split('T')[0]` and `.toISOString().slice(0,10)` (XLSX filenames) with `localISO(new Date())`. Date-arithmetic sites (`today.getTime() + 86400000`, `firstDay.setDate(1)`) wrapped as `localISO(new Date(...))` or rebuilt from parts (`${y}-${m}-01`).

**Scope of the sweep in pos.blade.php (10 sites):** dashboard `reportStartDate`/`reportEndDate` data() defaults; quick-filter computeds `periodStart`/`periodEnd` (Hari Ini/Minggu Ini/Bulan Ini); rekap absensi period default; history transaksi default end; getWorkerStatus + getAttendanceStatus "today" lookups (attendance status widgets showed stale state between midnight–7am!); modal absensi + tip date input defaults; XLSX export filenames (member + admin). Grep `toISOString` to find strays after the sweep — target zero.

**Mechanical-edit gotcha:** bulk-editing a mixed-line-ending Blade file (CRLF+LF) from Python — `str.replace` anchors with `\r\n` fail silently on LF lines. Detect the real bytes (`cat -A` / `repr()`) before asserting an anchor; run replace pairs for both endings or normalize the anchor first. Also: `docker.exe build` intermittently fails with "The process cannot access ... meta.json" (Windows-side context lock) — sleep 10s and retry the exact same command; second attempt succeeded.

- v80 verified live: compose tag sed v79→v80, `docker inspect` shows v80, HTTP 200, 10 `localISO` greps in container, npm build PASS. Told user to hard-refresh (Ctrl+Shift+R) since Blade output is cached by the browser.
- Version sequence: v75 → v76 (payroll rewrite + gated entrypoint) → v77 (nearest rounding) → v78 (report filters + period default) → v79 (slip daily breakdown) → v80 (UTC-safe dates dashboard-wide). Backup tag on VPS: `maulsss/washpro:backup-v75`.

## Session 7 (2026-09-01): "slip belum berubah" — multiple render surfaces (v81)

User: "kok slip gajinya belum berubah?" — after v79 shipped the daily-breakdown slip. The v79 fix WAS live and correct (verified by curl `?print=1` → RINCIAN HARIAN present), but the user was looking at the IN-APP modal, not the print page.

**Root cause:** the slip data renders on TWO independent surfaces:
1. Printable Blade view `payroll_slip.blade.php` (rendered via `?print=1`, opened by the CETAK button through `window.open('/api/payroll/{id}/slip/{name}?print=1')`).
2. In-app SweetAlert modal, built from JS template strings in `pos.blade.php` `showPayrollSlip()` (~line 3310) — it consumes the same JSON (`data.slip`) but had its OWN hand-written HTML with no daily table.

v79 patched only #1. **Lesson (now also in SKILL.md pitfalls):** when a UI feature has several rendering surfaces (print view, in-app modal, exports), patch and verify ALL of them in the same release. Verification method: `curl` the live page HTML and grep for the new markup/JS variable (e.g. `dailyTable`) — the modal markup only exists inside the JS template string, so grepping the served `pos.blade.php` output for `dailyTable` (3 hits) is the live check.

**v81 change (pos.blade.php only, no backend change):** in `showPayrollSlip()`, after `const s = data.slip`, build a `dailyTable` HTML string when `Array.isArray(s.daily)` — scrollable table (max-h-52), rows: tgl (d/m from ISO string slice), mobil, motor, recipients, per-day earn (`-` for absent like the Excel), tfoot JUMLAH = sum; inserted into the modal HTML between the Absensi block and `slipContent`. Kasir role gets no table (kasir pay isn't from the daily pool). Backend `daily` array from v79 serves both surfaces unchanged — good reason to compute the breakdown once in the API.

Also this session: user re-calculated payroll again → live id is now **10** (was 8). Confirms: ALWAYS resolve payroll id at query time (`SELECT id ... ORDER BY id DESC LIMIT 1` or by `period`), never hardcode.

- v81 verified live: compose tag sed v80→v81, `docker inspect` v81, HTTP 200, `curl /api/payroll/10/slip/...?print=1` → RINCIAN HARIAN present, served pos page → 3 `dailyTable` hits.
- Version sequence: v75 → v76 → v77 → v78 → v79 → v80 → v81. Backup tag on VPS: `maulsss/washpro:backup-v75`.

## Status

- **v81 live** (2026-09-01, session 7): in-app payroll slip modal now shows the daily table (same `daily` API as the print slip). Slip feature complete on both surfaces.
- Current payroll row: id=**10**, period 2026-08, total 19,140,000 (nearest-10k rule). User deletes/recreates payrolls freely — resolve id at query time, never reuse.
- Version sequence: v75 → v76 (payroll rewrite + gated entrypoint) → v77 (nearest rounding) → v78 (report filters + period default) → v79 (slip daily breakdown print) → v80 (UTC-safe dates dashboard-wide) → v81 (slip daily breakdown in-app modal). Backup tag on VPS: `maulsss/washpro:backup-v75`.
- Payroll investigation closed: system correct, Excel day 9 wrong (manual calc error).
- Revenue reconciliation closed: all residuals bucketed (off-POS perfume 945k, tips, cash↔QRIS swaps, +225k previously-counted pendings now excluded by v78). User's "198,000" never exactly reproduced — likely partial-view cash figure (DB cash vs sheet ASLI cash = 197,000). Advice given: enter perfume sales through POS.
- Rounding = nearest-10k since v77 (Δ-70,000 vs old always-up Excel rule, user accepted).
