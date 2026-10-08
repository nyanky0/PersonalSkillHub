#!/usr/bin/env python3
"""Template: build JSON indexes over an extracted CHM docs corpus.

Two common layouts:
  RefDB style      - one .htm per table, grouped by module dir   -> {table_lower: {table, mod, path, desc}}
  Object style     - pages `Prefix~Object.html`                  -> {object_lower: {obj, path}}

Adapt CORPUS / PREFIX / output names to the vendor. Proven against SAP B1 SDK 10.0
(REFDB 2,844 tables, REFDI 2,960 objects, REFUI 212 objects).
"""
import json, os, re, sys

CORPUS = r"C:/Users/<user>/.vendor-help"   # stable, NOT a temp dir
HERE = os.path.dirname(os.path.abspath(__file__))

def clean_text(path):
    """Fast readable-text extraction from a vendor HTML page."""
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            html = fh.read()
    except Exception:
        return ""
    html = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html)
    txt = re.sub(r"(?s)<[^>]+>", " ", html)
    for a, b in [("&nbsp;", " "), ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&#160;", " ")]:
        txt = txt.replace(a, b)
    return re.sub(r"\s+", " ", txt).strip()

def build_refdb(root):
    """One page per table, grouped by module subdir."""
    idx = {}
    for mod in os.listdir(root):
        modp = os.path.join(root, mod)
        if not os.path.isdir(modp):
            continue
        for fn in os.listdir(modp):
            if not fn.lower().endswith(".htm"):
                continue
            table = fn[:-4]
            desc = clean_text(os.path.join(modp, fn))[:180]
            m = re.search(r"Table Description:\s*([A-Za-z0-9 _&/()\-\.]+)", desc)
            idx[table.lower()] = {
                "table": table, "mod": mod,
                "path": os.path.join(modp, fn),
                "desc": m.group(1).strip() if m else "",
            }
    return idx

def build_objects(prefix, root):
    """Pages `Prefix~Object.html`; skip member pages (extra '~' after object name)."""
    idx = {}
    for fn in os.listdir(root):
        if not fn.startswith(prefix) or not fn.endswith(".html"):
            continue
        obj = fn[len(prefix):-5]
        if not obj or "~" in obj:
            continue
        idx[obj.lower()] = {"obj": obj, "path": os.path.join(root, fn)}
    return idx

def main():
    os.makedirs(HERE, exist_ok=True)
    # EXAMPLE: adapt per vendor
    db = build_refdb(os.path.join(CORPUS, "REFDB"))
    json.dump(db, open(os.path.join(HERE, "refdb_index.json"), "w", encoding="utf-8"))
    di = build_objects("SAPbobsCOM~", os.path.join(CORPUS, "REFDI"))
    json.dump(di, open(os.path.join(HERE, "refdi_index.json"), "w", encoding="utf-8"))
    ui = build_objects("SAPbouiCOM~", os.path.join(CORPUS, "REFUI"))
    json.dump(ui, open(os.path.join(HERE, "refui_index.json"), "w", encoding="utf-8"))
    print(f"tables={len(db)} di={len(di)} ui={len(ui)}")

if __name__ == "__main__":
    main()