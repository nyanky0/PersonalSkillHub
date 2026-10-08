# Wiring Hermes to a local router gateway

A gateway on `http://127.0.0.1:20128/v1` becomes a **named custom provider** in the client's config
(`providers.<slug>` in `config.yaml`), never the legacy top-level `model.base_url` — that key belongs
to one upstream endpoint and reusing it conflates the router with a single vendor.

## Recipe (all writes through `hermes config set`; never hand-edit config.yaml)

```bash
HERMES=/e/HERMES                      # $HERMES_HOME
K=$(cat ~/.omniroute/omniroute-api-key.txt)   # never echo this value

# 1. secret -> $HERMES_HOME/.env, idempotent and line-ending preserving
python -c "
import sys; p=r'E:/HERMES/.env'; k=sys.argv[1].strip()
raw=open(p,'rb').read().decode('utf-8'); lines=raw.split('\r\n')
lines=[l for l in lines if not l.startswith('HERMES_CUSTOM_OMNIROUTE_API_KEY=')]
if lines and lines[-1]=='': lines=lines[:-1]
lines.append('HERMES_CUSTOM_OMNIROUTE_API_KEY='+k)
open(p,'wb').write(('\r\n'.join(lines)+'\r\n').encode('utf-8'))" "$K"

# 2. provider (dotted paths create the nested keys)
hermes config set providers.omniroute.name "OmniRoute (local)"
hermes config set providers.omniroute.base_url "http://127.0.0.1:20128/v1"
hermes config set providers.omniroute.model "combo-utama"      # gateway's combo name = the default
hermes config set providers.omniroute.discover_models true
hermes config set providers.omniroute.key_env "HERMES_CUSTOM_OMNIROUTE_API_KEY"

# 3. pinned models — ONE call, JSON map value (see pitfall on dotted model ids)
hermes config set providers.omniroute.models '{"combo-utama":{},"bdb/auto":{},"deepseek-v4.1-flash":{}}'

# 4. optional shorthand for /model
hermes config set model.aliases.omni omniroute/combo-utama
```

Mirror the client's existing naming convention for the key variable — the client may already carry
`HERMES_CUSTOM_<SLUG>_API_KEY` entries from earlier providers; matching the pattern keeps resolution
predictable. Write the secret from a file/script, so it never lands in shell history or the transcript.

## Verification (real runs; config echo proves nothing)

```bash
export PATH="$PATH:/e/HERMES/hermes-agent/venv/Scripts"
hermes chat -Q --provider omniroute -m combo-utama -q "Balas satu kata: SUKSES"   # combo path
hermes chat -Q --provider omniroute -q "Balas satu kata: NGAWI"                   # provider default model
hermes chat -Q --provider omniroute -m "bdb/kimi-k3" -q "Balas satu kata: K3"     # id outside allowlist
```

- Non-TTY stdio makes `-q` a one-shot; `-Q` suppresses banner/spinner. A `session_id:` line plus the
  answer is the pass signal.
- Test #2 is the one that proves `providers.<slug>.model` resolves; test #3 proves pinned lists are
  only a picker concern.
- What the desktop/ACP picker will list (internal, may move between versions — if the import fails,
  grep the install for `_named_custom_provider_catalogs`):

```bash
export HERMES_HOME="E:/HERMES"
/e/HERMES/hermes-agent/venv/Scripts/python -c "
import sys; sys.path.insert(0,'E:/HERMES/hermes-agent')
from acp_adapter.model_catalog import _named_custom_provider_catalogs
for slug,label,models in _named_custom_provider_catalogs(): print(slug,'|',label,'|',len(models))"
```

- Sanity-check the secret landed intact by comparing lengths/equality against the source file in
  Python — never by printing the value.

## Quirks that cost time

- **A dot inside a key becomes a path separator.** `hermes config set providers.x.models.deepseek-v4.1-flash '{}'`
  writes `deepseek-v4: {1-flash: {}}`. Set the whole map in one call with a JSON/YAML literal value;
  `config set` parses those into real structures (a quoted `'{}'` per key stays a dict too).
- **A declared `models:` map behaves as an allowlist**, not a label list: it suppresses live discovery
  for the picker while explicit `-m <id>` still resolves anything the gateway serves.
- **Pickers cap listed models per provider** (`ACP_MAX_MODELS_PER_PROVIDER = 200` in
  `acp_adapter/model_catalog.py`). A gateway exposing hundreds of ids should get a curated handful
  pinned; dumping discovery output into the picker is unusable.
- **The one-shot prompt goes through `-q/--query`.** A trailing positional prompt is rejected
  (`error: unrecognized arguments: …`) even though the help text hints at a positional form; always
  `hermes chat -Q --provider <slug> -m <id> -q "<prompt>"`.
- **Pinned `models` may hold pass-through ids with a foreign prefix** (`gemini/gemini-3.5-flash-lite`
  alongside the combo name) when the gateway fronts several vendors — they resolve because the gateway
  rewrites `prefix/model`; pin only the handful the user actually picks from.
- **The open session keeps its model.** The new provider shows up in a new chat, or immediately via
  `/model <alias>`.
- **Localhost provider = localhost dependency.** If the gateway is not running, every turn through it
  fails; check `/api/health` before blaming the client config, and don't silently make it the client's
  default — offer the switch (`model.provider`, `model.default`, and re-point `model.base_url`) plus
  the gateway's autostart, and let the user choose.
- Extra slugs can appear in the picker catalog from auxiliary entries (e.g. a vision/tool config with
  its own `base_url`); they are not evidence of a duplicate provider you created.
