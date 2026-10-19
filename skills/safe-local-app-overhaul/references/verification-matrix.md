# Verification matrix

| Layer | Check | Evidence required |
|---|---|---|
| Syntax | `node --check` for server/test files; extract inline scripts and check them | exit 0 |
| API | isolated integration suite | zero failures, including status/scope/conflict cases |
| Lifecycle | Trash restore, expiry, purge, merge provenance | explicit PASS output |
| Migration | copied legacy DB migration and FTS insert/search | old data preserved; self-check PASS |
| UI | DOM fixture plus browser when available | render self-check PASS; browser state separately reported |
| Active data | read-only DB query | counts, active project/work state, `integrity_check: ok` |
| Deployment | live health endpoint after authorized restart | fresh health response and version/code-path check |

Never collapse these layers into one claim. State the missing layer explicitly.