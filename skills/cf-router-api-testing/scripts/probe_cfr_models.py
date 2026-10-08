#!/usr/bin/env python3
"""Probe every model CFRouter actually serves: status, latency, token usage.

Usage:
    export CFR_KEY=sk-...
    python probe_cfr_models.py            # all models from GET /v1/models
    python probe_cfr_models.py a b c      # only the named models

Discovers the catalog instead of hardcoding ids, so a renamed or deprecated
model can never silently 404 into an empty comparison.
"""
import json
import os
import sys
import time
import urllib.request

BASE = os.environ.get("CFR_BASE", "https://api.cfrouter.my.id/v1")
KEY = os.environ["CFR_KEY"]
PROMPT = "Reply with exactly: pong"


def post(path, payload=None, timeout=30):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode() if payload else None,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def catalog():
    return sorted(m["id"] for m in post("/models")["data"])


def probe(model):
    t0 = time.time()
    try:
        d = post(
            "/chat/completions",
            {
                "model": model,
                "messages": [{"role": "user", "content": PROMPT}],
                "max_tokens": 10,
            },
        )
    except Exception as e:  # noqa: BLE001 - report and keep going
        return {
            "model": model,
            "status": f"ERR {type(e).__name__}",
            "ms": int((time.time() - t0) * 1000),
        }
    u = d.get("usage", {})
    return {
        "model": model,
        "status": "OK",
        "ms": int((time.time() - t0) * 1000),
        "served_as": d.get("model"),
        "in": u.get("prompt_tokens"),
        "out": u.get("completion_tokens"),
    }


if __name__ == "__main__":
    rows = [probe(m) for m in (sys.argv[1:] or catalog())]
    print(f"{'model':28} {'served_as':28} {'ms':>7} {'in':>6} {'out':>5} status")
    for r in rows:
        print(
            f"{r['model']:28} {str(r.get('served_as', '-')):28} {r['ms']:>7} "
            f"{str(r.get('in', '-')):>6} {str(r.get('out', '-')):>5} {r['status']}"
        )
    print(json.dumps(rows, indent=2))
