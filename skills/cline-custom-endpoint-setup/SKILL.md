---
name: cline-custom-endpoint-setup
description: "Configures a custom API endpoint in Cline on Windows."
version: 1.0.0
platforms: [windows]
metadata:
  hermes:
    tags: [cline, antigravity, custom-endpoint, openai-compatible, config]
---

# Cline Custom Endpoint Setup (Windows / Antigravity IDE)

Use when the user wants to point the **Cline extension** (saoudrizwan.claude-dev)
at a custom OpenAI-compatible endpoint (base URL + API key) — e.g. a proxy/gateway
like bandelbanget.xyz, cfrouter, etc. — inside Antigravity IDE (VS Code fork) or
plain VS Code.

## Where Cline 4.x stores config (verified on this machine)

| File | Role |
|---|---|
| `C:\Users\<user>\.cline\data\settings\providers.json` | Provider list + API key + baseUrl + default model (`tokenSource: migration` = migrated from old state) |
| `C:\Users\<user>\.cline\data\settings\models.json` | Per-provider model catalog for the model picker (id/name/contextWindow/maxInputTokens/capabilities) |
| `C:\Users\<user>\.cline\data\globalState.json` | **ACTIVE mode config** — `actModeApiProvider`, `planModeApiProvider`, `actModeApiModelId`, `openAiBaseUrl`, model info |
| Extension install | `C:\Users\<user>\.antigravity-ide\extensions\saoudrizwan.claude-dev-<ver>-universal` |
| Runtime log | `C:\Users\<user>\AppData\Roaming\Antigravity IDE\logs\<session>\window1\exthost\output_logging_*\N-Cline.log` |

Env: Cline extension on Antigravity uses `AppData\Roaming\Antigravity IDE\User\globalStorage\saoudrizwan.claude-dev` (cache/mcp only). The **settings live in `~/.cline/data/`** — that's the source of truth.

## Working config shapes

providers.json — one entry per configured provider, keyed by family id:
```json
{
  "version": 1,
  "lastUsedProvider": "openai-compatible",
  "providers": {
    "openai-compatible": {
      "settings": {
        "provider": "openai-compatible",
        "apiKey": "sk-...",
        "model": "deepseek-v4-flash-0731",
        "baseUrl": "https://example.xyz/v1",
        "headers": {},
        "reasoning": {"enabled": true, "effort": "medium"}
      },
      "updatedAt": "2026-09-09T02:34:40.669Z",
      "tokenSource": "migration"
    }
  }
}
```

models.json — the picker catalog (capabilities: `streaming`, `tools`, + `images` for vision models):
```json
{
  "providers": {
    "openai-compatible": {
      "provider": {"name": "OpenAI Compatible", "baseUrl": "https://example.xyz/v1", "defaultModelId": "deepseek-v4-flash-0731"},
      "models": { "deepseek-v4-flash-0731": { "id": "...", "name": "...", "contextWindow": 200000, "maxInputTokens": 128000, "capabilities": ["streaming","tools"] } }
    }
  }
}
```

globalState.json — the ACTIVE per-mode selection (this is what actually runs):
```json
"openAiBaseUrl": "https://example.xyz/v1",
"actModeApiProvider": "openai-compatible",
"planModeApiProvider": "openai-compatible",
"actModeApiModelId": "deepseek-v4-flash-0731",
"planModeApiModelId": "deepseek-v4-flash-0731",
"actModeOpenAiModelId": "deepseek-v4-flash-0731"
```

## Procedure

1. **Get the model list from the endpoint first**: `curl -s <base_url>/models -H "Authorization: Bearer <key>"` → parse `data[].id`. Use these exact ids.
2. **Verify chat works with curl** (stream too): POST `<base_url>/chat/completions` with `{"model":"<id>","messages":[{"role":"user","content":"hi"}],"stream":true}` → expect `data:` SSE chunks, HTTP 200.
3. Back up the 3 files (`*.bak`), then edit JSON with Python (never hand-edit while the IDE is open — in-memory state overwrites files on exit).
4. Update **all three files consistently**: providers.json (key/baseUrl/model), models.json (baseUrl + catalog), globalState.json (openAiBaseUrl, mode provider/model ids).
5. Ask the user to **fully quit Antigravity IDE (all windows) and reopen** — extension reloads config from disk at startup. Test with a short prompt in Cline.
6. If it still fails, read the Cline runtime log (path above) and look for `[ai-sdk] stream error` / `Agent run failed` / `send() completed: text=...`.

## Pitfalls (all seen in the field)

- **`Not found` reply from Cline = HTTP 404 from the proxy** (the proxy's error body is echoed verbatim). Cline's URL = `baseUrl + "/chat/completions"` (verified in extension.js). A typo'd baseUrl (e.g. `.../v11` instead of `.../v1`) → 404 `{"error":"Not found"}`. ALWAYS curl-test the exact baseUrl path.
- **Editing providers.json alone is NOT enough** — globalState.json's `actModeApiProvider`/`openAiBaseUrl` can still point at the old endpoint (stale migrated state). Keep all 3 files in sync.
- **Wrong model id**: a model that isn't in the proxy's list also 404s (or 400). Use ids from the endpoint's `/models`, and set both `actModeApiModelId` AND `actModeOpenAiModelId`.
- **Old models.json overrides**: if models.json's `provider.baseUrl` still points at the previous endpoint, the picker shows stale models. Replace/align it.
- **Don't edit while the IDE runs**: Cline caches config in memory; on quit it writes back and clobbers disk edits. Edit first, then full restart.
- Config files may contain a plaintext `apiKey` (tokenSource `migration`) — treat as secret.

## Verification checklist

- [ ] `curl <base_url>/models` returns the endpoint's model ids
- [ ] curl chat completions (stream) returns 200
- [ ] providers.json + models.json + globalState.json all have the SAME baseUrl and a valid model id
- [ ] User fully restarted the IDE
- [ ] Cline answers a test prompt (no "Not found")
