---
name: live-vps-deploy
description: "Deploy fixed app versions to live production VPS safely."
version: 1.0.0
platforms: [linux, wsl]
metadata:
  hermes:
    tags: [deploy, production, vps, docker, compose, laravel, rollback]
    category: devops
    requires_toolsets: [terminal]
---

# Live VPS Deploy

Fix an app running on a production VPS (Docker Compose stack, live transactional DB), build a new version, and replace the running one safely.

## When to Use

- User reports a bug in a system deployed on a VPS and wants a fixed version deployed, replacing the old one
- Any task combining SSH access to a production box + Docker Compose + "don't touch the database"

## Hard rules (non-negotiable)

1. **Live DB is read-only** during diagnosis: `SELECT` only. Never `migrate`, never `seed`, never schema changes without explicit user confirmation in-session.
2. **Backup before replace**: tag old image as rollback (`docker tag app:vN app:vN-backup-<date>`), and dump the DB if the user permits.
3. **Confirm deploy timing** if the system serves live users — prefer off-peak windows.
4. Never run `docker compose down -v` or `docker system prune --volumes` on a production box.

## Procedure

### 1. Recon the VPS (batch over one SSH session)

```bash
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
find /opt /srv /root -maxdepth 3 -name "docker-compose*.y*ml" 2>/dev/null
cat /opt/<project>/docker-compose.yml
```

Copy the SSH key to `~/.ssh/` + `chmod 600` first (keys arrive as Windows paths like `C:\SSH\x.pem` → `/mnt/c/SSH/x.pem`).

### 2. Verify DB safety

- `docker inspect <db-container> --format "{{json .Mounts}}"` — DB data must be in a named volume or bind mount OUTSIDE the app image. If it is, replacing the app image leaves data intact.
- If DB data lives inside the app container/image: STOP and tell the user before anything else.

### 3. Audit the image entrypoint (critical pitfall)

```bash
docker exec <app> cat /usr/local/bin/docker-entrypoint.sh
```

Laravel images built for dev convenience often run on EVERY container start:
- `php artisan migrate --force`
- `php artisan db:seed --force`

On a live DB this re-runs seeders (duplicate users!) and applies new migrations without review. Fix in the NEW image: gate behind an env var defaulting OFF (e.g. `RUN_MIGRATIONS=0`), or strip entirely and keep only: wait-for-db, `config:cache`/`route:cache`/`view:cache`, storage link.

### 4. Note what lives outside the image

Check `docker inspect <app> --format "{{json .Mounts}}"` and the compose file for:
- `.env` bind-mounted from host → new image must be compatible with existing env
- `public/` bind-mounted for nginx → static assets must be re-synced at deploy, new image alone is NOT enough
- `storage/` volume → uploaded files persist across deploys

### 5. Sandbox-test the new logic against a DB copy (before touching prod code paths)

1. `docker exec <db> sh -c 'mysqldump -u<user> -p<pass> <db>' | gzip > /tmp/dump.sql.gz` on the VPS.
2. Create `<db>_test` + GRANT as ROOT (the app DB user usually lacks CREATE privileges — CREATE DATABASE via app user fails with `ERROR 1044`).
3. Restore the dump into the sandbox, then run a standalone PHP/python script INSIDE the app container (`docker cp` + `docker exec php /tmp/script.php`) that replicates the new logic with the same queries. No framework, no writes to live.
4. Assert against ground truth (the owner's manual Excel re-computed in openpyxl). Compare worker-by-worker, not just totals.
5. Clean up: `DROP DATABASE <db>_test`, revoke, delete dump + scripts from /tmp.

### 6. Fix, build, deploy

1. Get source (git clone or copy from user's Windows machine via `/mnt/c/`).
2. Reproduce + fix locally.
3. Build + tag versioned image (`app:vN+1`, never just `latest`), push to registry. In WSL with no docker CLI: drive `docker.exe` on Windows via `/mnt/c/Windows/System32/cmd.exe /c "docker build ..."`.
4. **Verify image contents before push**: `docker run --rm --entrypoint grep <image> -c <PATTERN> /path/in/image`. (Plain `docker run <image> sh -c "..."` executes the ENTRYPOINT first — a wait-for-DB entrypoint hangs forever.)
5. On VPS: `docker tag app:vN app:backup-vN` → sed the compose image tag → `docker compose pull <app>` → `docker compose up -d <app-service>` (app service only — never restart the DB service).
6. Sync `public/` ONLY if the frontend actually references built assets — grep the Blade view for `@vite`/asset URLs. A fully-CDN frontend (Vue via unpkg, Tailwind via CDN script) needs NO host asset sync; the stale `public/build` mismatch is harmless.
7. Schema changes on live: apply `ALTER TABLE` manually via `docker exec mysql`. MySQL 8.0 does NOT support `ADD COLUMN IF NOT EXISTS` — check `information_schema.COLUMNS` first. Still ship the migration file so fresh installs converge.

### 6. Verify + rollback plan

- `docker ps` (app Up), `docker logs --tail 50 <app>` (entrypoint clean, no migrate ran), `curl` the public URL, exercise the fixed flow.
- Rollback = revert compose tag to old image + `docker compose up -d <app>`. Volume data unaffected.

## Diagnosis pattern: system output ≠ user's manual numbers

When the bug is "system calculation doesn't match the owner's manual spreadsheet":

1. **Read the spreadsheet BOTH ways** (`data_only=False` for formulas, `data_only=True` for values) — the business rule lives in the formulas, the expectations live in the values.
2. **Verify inputs before blaming logic**: query the live DB (read-only) for the raw facts (per-day unit counts, attendance) and diff them against the manual sheet. If inputs match, the bug is purely in the calculation/distribution code — say so precisely; it shrinks the fix scope enormously.
3. **Check the pool total, then the distribution separately.** Often the aggregate is correct and only the per-person split rule differs (monthly-proportional vs daily-equal-split are the classic mismatched pair).
4. Manual sheets also encode post-processing the system lacks: rounding conventions (e.g. round UP to nearest 10k) and per-person manual adjustments by the owner (look for totals that overshoot any rounding rule — ask the user, don't guess). Encode these as explicit columns/fields (`manual_adjustment`), never hardcode.
5. Root-cause in numbers, in a side-by-side table, BEFORE proposing the fix — the user must confirm rule changes (role treatment, rounding, new settings) before you rewrite business logic.
6. **Attribute the residual gap to named sources before fixing.** After the code is correct, the remaining system-vs-spreadsheet delta should decompose into explicit buckets (owner manual overrides on specific days, rounding-order differences, missing feature flags). Present the buckets with totals (e.g. "-206,667 = manual override day 9 ÷ 9 attendees; -33,333 = rounding-order"). If a bucket can't be named, keep digging — don't hand-wave "small differences".
8. **"Anomaly" ≠ "error" — the sheet may be right and the DB incomplete.** When a day's manual number overshoots the formula, don't just flag it as an owner override. Check the live DB for that day by `payment_status`: pending/unpaid transactions (e.g. a washed car never closed out in POS) explain part of the gap, and the remainder may be genuinely real cash paid out (owner confirmed by re-computing manually — the user's word is ground truth for the business rule). Only the truly unexplainable remainder is a candidate for `manual_adjustment`; the missing-transaction part suggests an operational fix (close/cancel the stale pending ticket), not a payroll patch.
9. **Audit the sheet's OWN internal consistency before granting it ground truth.** Recompute every derived column against its own inputs, per day (e.g. "dibagikan" vs `mobil×rate + motor×rate`). If 30 of 31 days match the formula and exactly one day overshoots with a value that matches NO derivable formula from that day's inputs, suspect a manual calculation error in the sheet — the DB may be the correct side. Cross-check the sheet's count columns against its own distribution cells too: a "9 karyawan" count column next to 11 people receiving money that day is a typo inside the sheet, and the per-person amounts reveal which number was actually used. Internal inconsistency = sheet error; only externally-confirmed sheets win over the DB.
10. **A user's first confirmation can be wrong too.** In this engagement the user first said "I re-counted manually, the sheet is right", then with fuller evidence (unit counts, pending rows, the no-derivable-source math) reversed: "kesalahan dari sisi excel". Don't stop at the first verbal confirmation when the data contradicts it — present the arithmetic decomposition and let them re-confirm. But also don't relitigate after the SECOND confirmation with full evidence in hand; that's the settled answer.
11. **Stuck pending tickets: soft-cancel, don't DELETE.** `UPDATE transactions SET payment_status='cancelled'` keeps the audit trail (invoice, plate, cashier, timestamp), keeps the row reversible if a payment surfaces later, and excludes it from any `paid`-filtered report. Batch-check ALL stuck pendings in the period (`GROUP BY DATE(created_at)`), not just the one that surfaced — the pattern usually repeats across days.
8. **Ask "what does this anomaly mean" before asserting it.** A claim like "the owner overrode this number" can be wrong; the owner may have counted real cars the POS missed. Present the evidence (unit counts, pending rows), state both hypotheses, and let the user pick. Being corrected by the user ("itu setelah gw hitung manual ulang") after asserting the wrong cause costs more trust than asking first.

## Pitfalls

| Pitfall | Consequence | Prevention |
|---|---|---|
| Entrypoint auto-migrate on start | Live DB touched on every deploy/restart | Audit entrypoint (step 3); gate with env var |
| Auto `db:seed` on start | Duplicate default users each restart | Same gate |
| `docker compose up -d` (all services) | DB container restarted, brief outage | Target only the app service |
| Forgetting bind-mounted `public/` | New build looks unchanged (stale JS/CSS) | Re-sync host public dir |
| Replacing `latest` tag only | No rollback path | Always version tags + backup tag |
| Reading Excel values without formulas | Missed business rules (overrides, rounding) | Read BOTH passes: `data_only=False` + `data_only=True` |
| Feature-gated code deployed, gate setting row missing | New behavior silently inactive (e.g. rounding off) — output looks "still wrong" | After deploy, `SELECT` the settings table and INSERT any new flag rows the code reads, before declaring done |
| Re-deriving totals with own SQL filter | Wrong units (e.g. `business_type='motor'` when rows are keyed by `vehicle_type` Mobil/Motor/Warung) → totals that don't match anything | Before trusting an ad-hoc diff, `SHOW COLUMNS` + GROUP BY the actual discriminator columns; reconcile unit counts against the ground truth first |
| Schema ALTER applied without asking | User trust broken even though data untouched | Additive columns still need explicit in-session confirmation — "read-only" includes `information_schema` writes, so ask BEFORE the ALTER |
| Attribute spreadsheet-vs-DB anomaly to "owner override" | Wrong diagnosis: user re-counted manually and the sheet is right; real cause is missing/pending transactions in POS + real cash | Before labeling an override, check per-day DB by `payment_status` (pending rows) and unit counts vs sheet; present hypotheses, let the user confirm which is real |
| Claiming a feature doesn't exist after grepping ONE keyword | Wrong claim to user ("no cancel feature") when the app has a void button — keyword was `void`, not `cancel` | Grep all synonyms (cancel/void/batal/refund/nullify) across routes AND views before asserting absence; or ask the user "does the app have X?" |
| Rounding convention assumed (always-up) without asking | Business-rule mismatch: owner wanted nearest-10k (5k-10k range both directions) | Confirm rounding DIRECTION (up/nearest/down) explicitly before implementing; a one-word spec gap ships wrong business logic |
| Shell quoting mangled through SSH + docker exec + mysql -e | Silent empty output, exit 1, repeated retries | Batch SQL into a local file → `scp` → `docker exec -i mysql < file`; for inline `-e`, use double quotes inside single-quoted SSH command; run `SHOW COLUMNS` first (column-name guess `total_amount` vs actual `total` fails cleanly anyway) |
| `INSERT INTO settings (key, value) ...` on MySQL | `key` is a reserved word → ERROR 1064/exit 1 mid-batch (earlier statements in the same `-e` still ran!) | Backtick the column: `` INSERT INTO t (`key`, value) ... `` — and after any partial multi-statement batch failure, re-SELECT to see which statements actually landed before re-running |
| Report endpoints filter workflow status but not payment status | Cancelled/voided transactions still inflate daily revenue reports; after a soft-cancel cleanup the system's daily numbers DROP below the owner's historical records | Audit every revenue/report query: exclude `payment_status='cancelled'` (or include only `paid`) in the SAME pass as `status != 'Process'`. Also means the owner's previously-recorded "system" figures were snapshots that included pending — re-baseline expectations after cleanup |
| Period-picker default = start-of-month → today | Calculating a closed month from the UI on/after the 1st silently produces start→today (e.g. Aug 1→Sep 1), one day off or wrong month entirely | Default end date = last day of the START month (`new Date(y, m+1, 0)`), not `today` |
| Reconciling "manual cash count vs system revenue" on totals only | Chase a phantom number for hours; per-method per-day diffs expose the real buckets | Diff per payment method (Cash/QRIS separately) per day, and READ the owner's notes/keterangan column first — residuals are usually operational (off-POS product sales like perfume, tips, cash↔QRIS swaps by the cashier) |
| Running Windows `docker.exe` from WSL with a `/mnt/c/...` path as build context | `unable to prepare context: path "/mnt/c/..." not found` | `cd /mnt/c/<project> && docker.exe build -t img .` (cwd resolves; path arg doesn't). Same for `php.exe -l`: pass Windows-style path `C:\laragon\...`, not `/mnt/c/...` ("Could not open input file") |
| Deploying a business-rule change (e.g. rounding direction) with no before/after table | User sees total move vs old Excel and calls it a bug; re-litigation | Present the per-person before/after delta table AT DEPLOY TIME ("8 workers -10k each = total -70k, this is the rule you asked for") — set the expectation before they open the UI |
| Report needs per-row detail (e.g. daily breakdown) but only aggregates are stored in the DB | Tempting schema migration on a live DB for display-only data | Recompute the breakdown ON THE FLY in the GET endpoint from the source tables (transactions, attendance) using the same settings/formula as the original calculation; verify `sum(daily) ≈ stored aggregate` (small rounding diff is display-only). Zero schema change |
| Patching a block INTO THE MIDDLE of a fat controller function | `php -l` passes but runtime "Undefined variable" — the new block references a variable defined LATER in the same function (or a later duplicate query silently shadows it) | After inserting code above existing logic, trace every variable the new block uses back to its definition ABOVE the insertion point; remove now-dead duplicate queries below. `php -l` catches syntax only — use LSP diagnostics (intelephense) for use-before-assign |
| Testing endpoints with hardcoded record IDs from a previous session | `ModelNotFoundException` — user deletes and re-creates records (payroll recomputed: id 6 → id 8) | Resolve IDs at test time (`SELECT id ... ORDER BY id DESC LIMIT 1` or by period), never reuse old IDs; note the response shape (JSON often nested under a top-level key like `slip`) and that Blade rendering may require a flag (`?print=1`) while default returns JSON; confirm the real path via `route:list` (prefix like `/api` is easy to miss) |
| `new Date().toISOString().split('T')[0]` used as a local date string (browser app, UTC+N timezone) | Off-by-one DAY on any local time 00:00–07:00 in UTC+7: month-boundary defaults render as previous month's last day ("end of last month → today" dashboards); build/lint both pass | Never derive date strings from `toISOString()` in a local-timezone app. Add a `localISO(d)` helper (`y-m-d` from `getFullYear/getMonth/getDate`) and bulk-replace every `toISOString().split('T')[0]` / `.slice(0,10)` occurrence; wrap date-arithmetic sites (`+86400000`, `setDate(1)`) with it too. Grep `toISOString` after the sweep — target zero |
| Bulk-editing a mixed-CRLF/LF file via Python `str.replace` | Anchor strings containing `\r\n` fail silently on LF lines — "AssertionError anchor" with edits half-applied on retry | Inspect real line bytes first (`cat -A` / `repr()` around the anchor); run replace pairs for BOTH endings, or build the anchor from the file's own bytes. Verify post-edit by grepping that zero old-pattern occurrences remain |
| `docker.exe build` from WSL fails: "The process cannot access ... meta.json ... used by another process" | Looks like a broken build; actually a transient Windows-side Docker context lock | `sleep 10` and re-run the exact same command — retry succeeded. Don't restructure the command on first failure |
| User reports a just-shipped UI feature "not changed" | Fix landed in only ONE of several rendering surfaces | Same data often renders in MULTIPLE places: printable Blade view (`?print=1`), in-app SweetAlert modal built from JS template strings, export files. Before declaring done, enumerate every surface that displays the feature and patch all of them; verify each by grepping the LIVE html (e.g. `curl the page \| grep` for the new markup / JS var) |

## References

- `references/washpro-adr-steam.md` — active engagement: SP IKG carwash ERP, stack layout, entrypoint findings, manual payroll logic decoded from Excel, revenue-reconciliation method, UTC date-string bug class (v77–v80 session log).
