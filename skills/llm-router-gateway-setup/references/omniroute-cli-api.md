# OmniRoute admin API & CLI (3.8.x)

Data dir: `%USERPROFILE%\.omniroute` (Windows) / `~/.omniroute` — contains `storage.sqlite`
(SQLite, ~130 tables), `.env`, `logs/application/app.log`, `db_backups/`. Server default port 20128.

## Credentials

- **Admin routes** → header `x-omniroute-cli-token: <token>`, machine-derived:
  ```bash
  node -e "import('C:/Users/<u>/AppData/Roaming/npm/node_modules/omniroute/bin/cli/utils/cliToken.mjs').then(async m=>console.log(await m.getCliToken()))"
  ```
  Await it — a bare call prints `[object Promise]`. Works for `/api/provider-nodes`, `/api/providers`,
  `/api/combos`, `/api/keys`, `/api/settings`.
- **Client routes** → `Authorization: Bearer sk-...` from `POST /api/keys`. Required for `/v1/*`.

## Routes / commands used

| Purpose | Call |
|---|---|
| Create a custom node | `POST /api/provider-nodes` `{type:"openai-compatible", name, prefix, apiType:"chat", baseUrl}` → 201 `{node:{id,…}}` — **no apiKey in this body**; `prefix` must not equal a built-in provider id/alias (`400 … is a reserved provider prefix`) |
| List custom nodes | `GET /api/provider-nodes` → `{nodes:[{id,type,name,prefix,apiType,baseUrl,chatPath,modelsPath,customHeaders}], total}` — shows how existing custom providers were built |
| Park a connection | `PATCH /api/providers/<id>` `{"isActive":false}` → 200 |
| Assign credential + default model | `POST /api/providers` `{provider: nodeId, apiKey, name, defaultModel}` |
| Build combo | `POST /api/combos` (schema `createComboSchema`) or `omniroute combo create <name> --strategy priority --models "p/m,p/m"` |
| Suggest combo entries | `omniroute combo suggest` |
| Test a provider | `omniroute providers test <providerId>` — **unsupported for vendor-catalog types**; verify those with a real `/v1/chat/completions` on `prefix/model` |
| Add a vendor-catalog provider | `omniroute providers add <vendorId> --name "…" --credential-stdin --default-model <vendor-model-id> --yes < keyfile` (credential is the only required datum) |
| Extend an existing combo | `PUT /api/combos/<uuid>` body `{name, models:[…], strategy, config}` — full array, replaces; 200 = applied |
| Client key | `POST /api/keys` `{"name":"..."}` → raw value once |
| Rotate key | `POST /api/keys/<id>/regenerate` → new value; old value dead |
| Health | `GET /api/health` → `{"status":"ok"}` |
| Catalog | `GET /v1/models` (client key) → `data[].id` = `prefix/model` |

Combo entry shape (both `POST` and `PUT /api/combos`):
`{id: '<combo>-model-N-<slug>', kind: 'model', model: 'prefix/model', providerId: 'prefix', weight: 0}`.
`PUT` replaces the whole `models` array, so GET first, splice, then re-GET to confirm the count and the
first few ids — the id strings embed an index and are not renumbered for you. Vendor-catalog providers
(`gemini`, `groq`, …) are defined in `src/shared/constants/providers/apikey/*.ts` as a display entry only
(id/alias/name/icon/website/`hasFree`/`serviceKinds`) — endpoint and auth live in code, which is why the
credential alone installs them.

### Custom-node flow, and the errors it throws

```bash
# 1) node first — carries the endpoint, holds no credential
POST /api/provider-nodes {"type":"openai-compatible","name":"ZAI Platform","prefix":"zaiplat","apiType":"chat","baseUrl":"https://api.z.ai/api/paas/v4"}
# → 201 {"node":{"id":"openai-compatible-chat-<uuid>", …}}
# 2) connection bound to that exact node id
POST /api/providers {"provider":"openai-compatible-chat-<uuid>","name":"…","apiKey":"<key>","defaultModel":"<upstream-model-id>"}
# → 201 {"connection":{"id":"<uuid>","isActive":true, …}}
```

- `404 {"error":"OpenAI Compatible node not found"}` = step 2 ran before step 1, or the node id was
  invented instead of taken from step 1's response.
- `400 … is a reserved provider prefix — choose a different prefix` = the prefix collides with a
  built-in id/alias (`zai`, `glm`, `gemini`, …). Built-ins own `<prefix>/model`, so use `<vendor><role>`.
- A custom node has **no live model catalog**: any `<prefix>/<id>` passes the gateway and the upstream
  decides. Probe each candidate id against the upstream directly before putting it in a combo — same key
  and endpoint, z.ai's general platform answers `200` for the free Flash ids and
  `429 {"code":"1113","message":"Insufficient balance or no resource package"}` for the paid ones.
- Route discovery: unknown `/api/*` paths 404 while page routes fall through to the dashboard SPA HTML
  (hundreds of KB) — read the response body, not just the status code.

The dashboard modal `AddCompatibleProviderModal.tsx` mirrors the provider-node body — fetch the route
file from the repo when a field name is unclear (`curl -g` for paths with spaces).

## Reconciling model counts (aggregate in code, never by eye)

```bash
curl -s -H "Authorization: Bearer $OMNI_KEY" http://127.0.0.1:20128/v1/models -o v1.json
python -c "import json,collections;d=json.load(open('v1.json'))['data'];c=collections.Counter(m['id'].split('/')[0] for m in d);print(len(d),dict(c))"
```

Compare per prefix against the arrays dumped from each upstream `<baseUrl>/models` with the upstream's
own key. Synthetic additions look like `<prefix>/auto` and `<prefix>/<model>-low|-medium|-high|-xhigh`.

## Which combo entry actually served

```bash
grep -E '"tag":"(COMBO|ROUTING)"' ~/.omniroute/logs/application/app.log | tail -n 20
```

Line shapes worth grepping: `Combo "<name>" [priority] with N models`, `Trying model 1/N: <prefix>/<model>`,
`Model <m> succeeded (1913ms, 0 fallbacks)`, `Model <m> returned 200 but failed quality check:
reasoning consumed 1024/1024`.

```bash
node -e "const D=require('<pkgDir>/node_modules/better-sqlite3');const db=new D(process.env.USERPROFILE+'/.omniroute/storage.sqlite',{readonly:true});console.log(db.prepare('select id,combo_name,model_str,provider,used_at from session_model_history order by id desc limit 5').all())"
```

Notes: `session_key=... has no available affinity target` repeats once per combo entry and floods the
log — filter it out. Extra combo entries are the normal state, not an error.

## Local execution timeout (the rate-limit queue's wait cap)

The queue bounds how long a request may WAIT before dispatch at `maxWaitMs` — default **15000 ms**
(`src/lib/resilience/settings.ts`, env **`RATE_LIMIT_MAX_WAIT_MS`**). An upstream that answers in ~20 s
is therefore counted as a failure at the gateway (504) while the same call succeeds in ~20 s with
`curl`. Raise the cap in the data-dir `.env` and restart:

```bash
printf '\nRATE_LIMIT_MAX_WAIT_MS=120000\n' >> ~/.omniroute/.env
omniroute restart   # may outlive a foreground timeout; it still completes in the background
```

Proof: the combo returns 200 with a `time_total` LARGER than the previous cap (that is what shows the new
env value took effect, not just that the upstream woke up). After a restart the port is briefly unowned —
check `GET /api/health` plus `~/.omniroute/supervisor/.pid` rather than re-issuing the command.
