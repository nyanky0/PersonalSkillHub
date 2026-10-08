# Auto-discovering models for an OpenAI-compatible client

When a PRD generator (or any browser/CLI tool) talks to an OpenAI-compatible
endpoint, hardcoding or hand-typing the model name is a trap — a stale/wrong
name fails at generation time with `The model "X" does not exist`.

The fix is a "Load" affordance that queries the endpoint's own model list.

## The pattern

1. Add a `GET {base_url}/models` fetch (auth header only if a key is set).
2. Parse `response.data[].id`, drop empties, render as a `<datalist>` (or
   `<select>`) so the user picks a real id instead of typing one.
3. Optional inputs every OpenAI-compatible server accepts: `base_url`, `api_key`,
   `model` — leave `model` populated from the datalist after load.

Browser-side JS shape (with `esc`/`setStatusS` already in scope):

```js
async function loadModels {
  const base = document.getElementById('apiBase').value.trim.replace(/\/+$/,'') + '/';
  const key  = document.getElementById('apiKey').value.trim;
  const headers = {'Content-Type':'application/json'};
  if (key) headers['Authorization'] = 'Bearer ' + key;
  const res = await fetch(base + 'models', { method:'GET', headers });
  if (!res.ok) throw new Error('HTTP ' + res.status + ' — cek base URL & key');
  const j = await res.json;
  const ids = (j.data || []).map(m => m.id).filter(Boolean);
  document.getElementById('modelList').innerHTML =
      ids.map(id => `<option value="${esc(id)}"></option>`).join('');
}
```

## Diagnostic: 401 vs 404 on `/models`

Before wiring the Load button, probe the endpoint directly with curl to know
whether it even exists:

- **`401` (auth_error / "Invalid API key")** → the `/models` route EXISTS; it
  just needs a valid key. Wire up Load and it will return the list once a real
  key is set. Do NOT treat 401 as "endpoint missing".
- **`404`** → the endpoint does not expose `/models`; fall back to manual
  model entry and make it clear in the UI.

This single probe tells you whether the auto-load feature is even viable
before you build it.

## Pitfall: model name ≠ provider model id

`hermes config get model` may show a display label (e.g. "DeepSeek-V4-Pro(0813)")
that is NOT the wire-level `model` id the API expects (`deepseek-v4-pro-0813`
may not exist on the endpoint). Trust the `/models` list (or the provider's
model catalog), never the display name — this is exactly the failure mode that
motivates the Load button in the first place.