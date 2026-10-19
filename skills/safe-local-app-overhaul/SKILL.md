---
name: safe-local-app-overhaul
description: Use for safe local app overhauls.
---

# Safe Local-App Overhaul

## Procedure

1. Read the plan and current schema/API/UI before editing. Separate code changes from deployment, restart, and data-restoration actions.
2. Copy the active database to a temporary QA directory and point all write tests at that copy. Never run destructive or synthetic tests against the active database.
3. Implement schema changes transactionally and idempotently. Add provenance/link tables with foreign keys and cleanup paths before adding merge or promotion endpoints.
4. For review workflows, keep candidate states explicit (`new`, `approved`, `trash`), treat duplicate detection as a candidate rather than a fact, preserve the selected target, and move merge sources to restorable Trash instead of deleting them.
5. Use optimistic concurrency for edits and merges: return the current record on conflict and require the caller to send the record timestamp/version it observed.
6. Keep project scope explicit. Reject cross-project merges; require explicit confirmation before approving global promotions created from multiple projects.
7. Add API tests for status filtering, project/global scope, invalid IDs, cross-project rejection, provenance persistence, Trash restore/purge, and concurrent-edit conflicts. Add a migration self-check against a copied legacy database.
8. Verify UI separately from API: extract inline scripts and run `node --check`; execute a small DOM fixture for render functions; use browser inspection when available. Do not claim browser/live-service verification from API tests alone.
9. After tests, re-open the active database read-only and verify row counts, active project/work state, and `PRAGMA integrity_check`. Do not restore ambiguous or mixed backups automatically; identify their contents and request a restoration decision.
10. Report completion as a checklist: changed files/behavior, fresh verification output, active-data verification, and explicit remaining live/browser/deployment blockers.

## Standing rules

- Keep the diff minimal; do not refactor unrelated code while fixing lifecycle or schema behavior.
- Treat backup restoration as a data operation requiring an explicit source/scope decision, not as a test cleanup step.
- A passing isolated suite proves isolated behavior only; it does not prove the running service loaded the new code or that a browser rendered the UI.
- Do not restart a live MCP/dashboard service or change its port as part of implementation unless the user explicitly authorizes that maintenance action. If restart is authorized, inspect the exact listener PID, verify the process identity, stop only that PID/tree, relaunch using the service's documented command/environment, then verify port ownership, health endpoint, MCP initialize/tools/list/ping, dashboard route, and active DB integrity before claiming success.

## References

- See `references/verification-matrix.md` for the compact acceptance matrix and command sequence.