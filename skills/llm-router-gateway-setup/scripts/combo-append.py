#!/usr/bin/env python3
"""Append model ids to a live OmniRoute combo, idempotently, through the admin API.

usage:  python combo-append.py <combo-name> <prefix/model> [more ids...] [--dry-run]

Why this exists: `PUT /api/combos/<id>` REPLACES the whole models array, so a partial hand-written
body silently drops entries, and combo entry ids embed an index that nothing renumbers for you.
This script GETs, splices at the tail (entry 1 and the existing order survive), PUTs the full object
and re-GETs to prove the result.

Env (all optional): OMNI_BASE_URL (default http://127.0.0.1:20128), OMNI_PKG_DIR (omniroute package
root if it is not in the global npm prefix), OMNI_API_KEY (client key, only used by --test).
"""
import json
import os
import shutil
import subprocess
import sys
import urllib.request

BASE = os.environ.get("OMNI_BASE_URL", "http://127.0.0.1:20128")


def pkg_dir() -> str:
    if os.environ.get("OMNI_PKG_DIR"):
        return os.environ["OMNI_PKG_DIR"]
    npm = shutil.which("npm") or "npm"
    try:
        root = subprocess.run([npm, "root", "-g"], capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception:
        root = ""
    for cand in (os.path.join(root, "omniroute"),
                 os.path.join(os.environ.get("APPDATA", ""), "npm", "node_modules", "omniroute"),
                 os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Roaming", "npm", "node_modules", "omniroute")):
        if cand and os.path.isdir(cand):
            return cand
    raise SystemExit("omniroute package not found — set OMNI_PKG_DIR")


def cli_token() -> str:
    """Admin routes want x-omniroute-cli-token; a client key gets 403 'Invalid management token'.
    The token is HMAC-derived from the machine id by the package's own module."""
    js = ("import('%s').then(async m=>console.log(await m.getCliToken()))"
          % os.path.join(pkg_dir(), "bin/cli/utils/cliToken.mjs").replace("\\", "/"))
    out = subprocess.run([shutil.which("node") or "node", "-e", js],
                         capture_output=True, text=True, timeout=120).stdout.strip().splitlines()
    tok = out[-1].strip() if out else ""
    if not tok or tok == "[object Promise]":
        raise SystemExit("could not derive CLI token (await getCliToken())")
    return tok


def call(method: str, path: str, tok: str, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("content-type", "application/json")
    req.add_header("x-omniroute-cli-token", tok)
    with urllib.request.urlopen(req, timeout=90) as r:
        raw = r.read().decode()
    return json.loads(raw) if raw.strip()[:1] in "{[" else raw


def combo_list(payload):
    return payload if isinstance(payload, list) else payload.get("combos") or payload.get("data") or []


def entry_id(combo: str, n: int, model: str) -> str:
    slug = model.replace("/", "-").replace(".", "-").replace("_", "-").lower()
    return "%s-model-%d-%s" % (combo, n, slug)


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    dry = "--dry-run" in sys.argv
    if len(args) < 2:
        raise SystemExit(__doc__)
    name, models = args[0], args[1:]
    tok = cli_token()
    combo = next((c for c in combo_list(call("GET", "/api/combos", tok)) if c.get("name") == name), None)
    if combo is None:
        raise SystemExit("combo %r not found" % name)
    cur = [m["model"] for m in combo["models"]]
    have = set(cur)
    added = []
    for mid in models:
        if mid in have:
            print("skip (already present):", mid)
            continue
        have.add(mid)
        added.append(mid)
        combo["models"].append({"id": entry_id(name, len(combo["models"]) + 1, mid),
                                "kind": "model", "model": mid,
                                "providerId": mid.split("/")[0], "weight": 0})
    print("combo=%s %d -> %d entry | entry1=%s | added=%s"
          % (name, len(cur), len(cur) + len(added), cur[0] if cur else None, added or "(none)"))
    if dry or not added:
        return
    call("PUT", "/api/combos/" + str(combo.get("id") or combo.get("_id") or name), tok, combo)
    after = next(c for c in combo_list(call("GET", "/api/combos", tok)) if c.get("name") == name)
    ids = [m["model"] for m in after["models"]]
    print("VERIFY total=%d | entry1=%s" % (len(ids), ids[0] if ids else None))
    missing = [m for m in added if m not in ids]
    print("missing after PUT:", missing or "none")


if __name__ == "__main__":
    main()
