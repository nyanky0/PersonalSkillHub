# Prompt compression ("token saver" / Caveman) on a local router gateway

The gateway ships a built-in multi-engine prompt compressor: Caveman (terse-prose rewriting), `lite`
(tool-result trimming), RTK, session-dedup, headroom, codex-responses, omniglyph, and a `stacked`
pipeline that chains them. It is **off by default**; there is no working admin HTTP route to enable it
with the credentials an agent can hold, so it is enabled in the settings DB.

## Where the config lives

`<dataDir>/storage.sqlite` → table **`key_value`**, namespace **`compression`**, one row per knob, and the
`value` column is a **JSON-encoded** scalar/object (`"lite"`, `true`, `50000`, `{"enabled":true,…}`), not
a bare string. The reader merges these onto `DEFAULT_COMPRESSION_CONFIG`, ignores keys it does not know,
and caches the result in-process for ~5 s (`src/lib/db/compression.ts`) — so a write takes effect within
seconds, and a re-read immediately after the write can still show the old value.

Back up before writing: `cp storage.sqlite db_backups/pre-compression-$(date +%Y%m%d-%H%M%S).sqlite`.

## Recipe (run from the data dir; the server may stay up)

```bash
cd ~/.omniroute && python - <<'EOF'
import sqlite3, json
db = sqlite3.connect('storage.sqlite')
def setk(key, value):                      # upsert into the compression namespace
    v = json.dumps(value)
    if db.execute("update key_value set value=? where namespace='compression' and key=?", (v, key)).rowcount == 0:
        db.execute("insert into key_value(namespace,key,value) values('compression',?,?)", (key, v))
    print(' set', key, '=', v[:80])

row = db.execute("select value from key_value where namespace='compression' and key='engines'").fetchone()
eng = json.loads(row[0]) if row else {}
eng.setdefault('lite', {})['enabled'] = True    # flip the engine inside the EXISTING JSON map
setk('engines', eng)

setk('enabled', True)
setk('defaultMode', 'lite')
setk('autoTriggerMode', 'standard')
setk('autoTriggerTokens', 50000)
setk('preserveSystemPrompt', True)
setk('preserveSystemPromptMode', 'whenNoCache')
setk('cacheMinutes', 5)
setk('cavemanConfig', {"enabled": True, "compressRoles": ["user"], "skipRules": [],
                       "minMessageLength": 50, "preservePatterns": []})
db.commit()
EOF
```

Why these values for a first-time user: `defaultMode: lite` is the conservative, low-risk level (tool
results trimmed, no prose rewriting), and `autoTriggerMode: standard` only escalates once a request
exceeds `autoTriggerTokens`. `preserveSystemPrompt: whenNoCache` keeps the system prompt intact when the
upstream would not have cached it anyway. Raise to `aggressive`/`ultra` only after the user sees the
output quality they want.

## Knobs worth knowing

| key | values | effect |
|---|---|---|
| `enabled` | bool | master switch; every other key is inert while false |
| `defaultMode` | `off` `lite` `standard` `aggressive` `ultra` `rtk` `codex-responses` `omniglyph` `stacked` | mode applied to every request |
| `autoTriggerMode` / `autoTriggerTokens` | mode / int | once a request is bigger than N tokens, switch to this mode (0 = never) |
| `preserveSystemPrompt` + `preserveSystemPromptMode` | bool / mode token | the MODE row is authoritative; unknown tokens are dropped and the default survives, so re-read to confirm it parsed |
| `cavemanConfig` | `{enabled, compressRoles[], skipRules[], minMessageLength, preservePatterns[]}` | Caveman itself; `preservePatterns` defaults protect code blocks, inline code, URLs, file paths, stack lines |
| `engines` | `{<engineId>: {enabled, level?}}` | per-engine toggles for the `stacked` pipeline. Engine ids come from `open-sse/services/compression/engineCatalog.ts` (each carries `stackPriority`, `lossy`, `cacheImpact`); a set-but-unused engine costs nothing, a wrong id is ignored |
| `comboOverrides` | `{<comboId>: mode}` | per-combo mode overrides |
| `stackedPipeline` / `exclusions` / `contextBudget` / `liveZone` / `ultraEngine` | see the schemas in `src/shared/validation/compressionConfigSchemas.ts` | depth, only touch on a specific ask |

## Verifying it actually runs (don't judge by the saved %)

```bash
grep -o '"tag":"COMPRESSION"[^}]*}' ~/.omniroute/logs/application/app.log | tail -5
```

Live lines look like `Prompt compressed (stacked): 4195 -> 4195 tokens (0% saved, techniques:
whitespace,skip:no_vision)` — the line appearing at all proves the pipeline is engaged. **0% saved on a
small prompt is normal and not a failure signal**; the pipeline only has something to strip once the
request is large, and `autoTriggerTokens` decides when that is. Confirm the state itself from the stored
rows (or a re-read after the 5 s TTL), not from the savings figure.

Note the gateway's own compression is independent of the *client's* style settings — enabling it here
changes what is sent upstream, while the client's own terse/caveman personality is prompt-level only.
