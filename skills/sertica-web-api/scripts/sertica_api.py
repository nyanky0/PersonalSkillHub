#!/usr/bin/env python3
"""Offline lookup tool for the SERTICA Web API (no network needed, reads assets/sertica-swagger.json.gz).

    python sertica_api.py stats
    python sertica_api.py search <regex>            # match method+path+summary, prints method/path/tag/summary/body
    python sertica_api.py search <regex> --tag PurchaseOrders
    python sertica_api.py show GET /PurchaseOrders/{purchaseOrderNo}
    python sertica_api.py rights <TagOrPathFragment>
    python sertica_api.py model <NameFragment>      # fields + nested refs (also matches a model referenced by ops)
    python sertica_api.py tags
    python sertica_api.py refresh                   # re-download the spec from the environment
"""
from __future__ import annotations

import gzip
import json
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SPEC_GZ = SKILL / "assets" / "sertica-swagger.json.gz"
SPEC_URL = "https://indobaruna-test.sertica.com/api/swagger/v1/swagger.json"
PAGE = (SKILL / "references" / "endpoint-index.md")
METHODS = ("get", "post", "put", "patch", "delete")
TD_PAIR = re.compile(r">([^<>]{1,60})</td>\s*<td[^>]*>([^<>]{1,60})</td>")


def load() -> dict:
    if not SPEC_GZ.exists():
        print(f"missing {SPEC_GZ}; run: python {Path(__file__).name} refresh", file=sys.stderr)
        sys.exit(2)
    with gzip.open(SPEC_GZ, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def ops(spec):
    for path, item in spec["paths"].items():
        for method, op in item.items():
            if method in METHODS:
                yield method.upper(), path, op


def clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return " ".join(text.split())


def rights(op) -> str:
    desc = (op.get("responses", {}).get("403", {}) or {}).get("description", "") or ""
    seen, out = set(), []
    for k, v in TD_PAIR.findall(desc):
        if (k, v) not in seen:
            seen.add((k, v))
            out.append(f"{k}:{v}")
    return ", ".join(out)


def model_name(node) -> str:
    if not isinstance(node, dict):
        return ""
    if "$ref" in node:
        name = node["$ref"].rsplit("/", 1)[-1]
        parts = re.sub(r"`\d+\[\[.*", "", name).split(".")
        for marker in ("SerticaWebApi", "Models"):
            if marker in parts:
                parts = parts[parts.index(marker) + 1:]
        return ".".join(parts) or name
    if node.get("type") == "array":
        return model_name(node.get("items", {}))
    return node.get("type", "")


def cmd_stats(spec):
    c = spec.get("components", {}).get("schemas", {})
    n = sum(1 for _ in ops(spec))
    tags = {op.get("tags", ["?"])[0] for _m, _p, op in ops(spec)}
    print(f"spec {spec['info']['title']} {spec['info']['version']} | openapi {spec.get('openapi')}")
    print(f"paths={len(spec['paths'])} operations={n} schemas={len(c)} tags={len(tags)}")
    print(f"server={spec['servers'][0]['url']}  spec_url={SPEC_URL}")


def cmd_search(spec, pattern, tag=None):
    rx = re.compile(pattern, re.I)
    hits = 0
    for method, path, op in sorted(ops(spec), key=lambda x: (x[1], x[0])):
        otag = (op.get("tags") or ["?"])[0]
        if tag and otag.lower() != tag.lower():
            continue
        summary = clean(op.get("summary"))
        if not (rx.search(path) or rx.search(summary) or rx.search(method)):
            continue
        hits += 1
        body = ""
        try:
            body = model_name(op["requestBody"]["content"]["application/json"]["schema"])
        except Exception:
            pass
        r = rights(op)
        print(f"{method:6} {path}  [{otag}]  {summary}" + (f"  body={body}" if body else "") + (f"  rights={r}" if r else ""))
    print(f"-- {hits} match(es)")


def cmd_show(spec, method, path):
    item = spec["paths"].get(path)
    if not item:
        near = [p for p in spec["paths"] if path.lower() in p.lower()][:10]
        print(f"no such path: {path}")
        if near:
            print("similar:", *near, sep="\n  ")
        return
    op = item.get(method.lower())
    if not op:
        print(f"{method} not defined on {path}; available: {', '.join(k.upper() for k in item if k in METHODS)}")
        return
    print(f"{method.upper()} {path}")
    print(f"  tags      : {', '.join(op.get('tags', []))}")
    print(f"  summary   : {clean(op.get('summary'))}")
    print(f"  security  : {json.dumps(op.get('security', 'inherited (Bearer)'))}")
    print(f"  rights    : {rights(op) or '(none documented)'}")
    for p in op.get("parameters", []):
        sch = p.get("schema", {})
        t = sch.get("type") or model_name(sch)
        default = f" default={sch['default']}" if "default" in sch else ""
        print(f"  param     : {p.get('in'):6} {p['name']:32} {t}{default}{' REQUIRED' if p.get('required') else ''}")
    try:
        body = op["requestBody"]["content"]["application/json"]["schema"]
        print(f"  body      : {model_name(body)}   {json.dumps(body)[:120]}")
    except Exception:
        pass
    for code, resp in sorted(op.get("responses", {}).items()):
        try:
            sch = model_name(resp["content"]["application/json"]["schema"])
        except Exception:
            sch = ""
        print(f"  {code:9} : {sch or clean(resp.get('description'))[:110]}")


def cmd_rights(spec, needle):
    rx = re.compile(needle, re.I)
    rows = []
    for method, path, op in sorted(ops(spec), key=lambda x: (x[1], x[0])):
        if not (rx.search(path) or rx.search((op.get("tags") or [""])[0])):
            continue
        rows.append((method, path, rights(op) or "-"))
    for m, p, r in rows:
        print(f"{m:6} {p}  ->  {r}")
    print(f"-- {len(rows)} op(s). Distinct rights: {', '.join(sorted({r for _m, _p, r in rows}))}")


def cmd_tags(spec):
    counts = {}
    for _m, _p, op in ops(spec):
        t = (op.get("tags") or ["?"])[0]
        counts[t] = counts.get(t, 0) + 1
    for t, n in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"{n:5} {t}")


def cmd_model(spec, needle):
    schemas = spec["components"]["schemas"]
    rx = re.compile(needle, re.I)
    names = [n for n in schemas if rx.search(n)]
    if not names:
        print("no schema matches", needle)
        return
    seen = set()
    for name in sorted(names, key=len)[:3]:
        s = schemas[name]
        if name in seen:
            continue
        seen.add(name)
        if "enum" in s:
            print(f"enum {name}: {', '.join(str(v) for v in s['enum'])}")
            continue
        props = s.get("properties", {}) or {}
        print(f"{name}  ({len(props)} fields)")
        for pn, pv in props.items():
            t = model_name(pv) if ("$ref" in pv or pv.get("type") == "array") else pv.get("type", "?")
            fmt = f":{pv['format']}" if pv.get("format") else ""
            print(f"    {pn:38} {t}{fmt}{' ?' if pv.get('nullable') else ''}")
        print()
        for pn, pv in props.items():
            ref = pv.get("$ref") or (pv.get("items", {}) or {}).get("$ref")
            if ref:
                sub = ref.rsplit("/", 1)[-1]
                inner = schemas.get(sub, {})
                if inner.get("properties"):
                    print(f"  nested {sub.split('.')[-1]}: {', '.join(list(inner['properties'])[:25])}")
                elif "enum" in inner:
                    print(f"  nested enum {sub.split('.')[-1]}: {', '.join(str(v) for v in inner['enum'])}")


def cmd_refresh():
    print(f"downloading {SPEC_URL} ...")
    with urllib.request.urlopen(SPEC_URL, timeout=120) as r:
        data = r.read()
    SPEC_GZ.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(SPEC_GZ, "wt", encoding="utf-8") as fh:
        fh.write(data.decode("utf-8"))
    spec = json.loads(data.decode("utf-8"))
    print(f"saved {SPEC_GZ} ({SPEC_GZ.stat().st_size:,} bytes) | {len(spec['paths'])} paths")
    print("now rerun: python build_references.py")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    cmd = args[0].lower()
    if cmd == "refresh":
        cmd_refresh()
        return
    spec = load()
    if cmd == "stats":
        cmd_stats(spec)
    elif cmd == "search":
        tag = args[args.index("--tag") + 1] if "--tag" in args else None
        cmd_search(spec, args[1], tag)
    elif cmd == "show":
        cmd_show(spec, args[1], args[2])
    elif cmd == "rights":
        cmd_rights(spec, args[1])
    elif cmd == "model":
        cmd_model(spec, args[1])
    elif cmd == "tags":
        cmd_tags(spec)
    elif cmd == "index":  # grep the generated flat index instead
        rx = re.compile(args[1], re.I)
        hits = [ln for ln in PAGE.read_text(encoding="utf-8").splitlines() if rx.search(ln)]
        print("\n".join(hits[:60]), f"\n-- {len(hits)} line(s)")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
