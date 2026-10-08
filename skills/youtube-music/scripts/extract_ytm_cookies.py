#!/usr/bin/env python3
"""Extract YouTube cookies from ytmdesktop partition -> ytmusicapi headers_auth.json.

Usage:
    ~/.venvs/ytmusic/bin/python extract_ytm_cookies.py [output.json]

Requires: ytmusicapi + pycryptodome in the venv, powershell.exe interop (WSL).
Target app (YouTube Music Desktop) must be CLOSED — Windows locks cookie DBs.
"""
import base64, json, os, sqlite3, subprocess, sys

BASE = "/mnt/c/Users/muham/AppData/Roaming/YouTube Music Desktop App"
HOME = os.path.expanduser("~")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HOME, "ytm", "headers_auth.json")


def dpapi_unprotect(blob_b64: str) -> bytes:
    ps = ('Add-Type -AssemblyName System.Security; '
          '[Convert]::ToBase64String([System.Security.Cryptography.ProtectedData]::Unprotect('
          f'[Convert]::FromBase64String("{blob_b64}"), $null, '
          '[System.Security.Cryptography.DataProtectionScope]::CurrentUser))')
    out = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps],
                         capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise RuntimeError("DPAPI failed: " + out.stderr[:300])
    return base64.b64decode(out.stdout.strip())


def main():
    ls = json.load(open(os.path.join(BASE, "Local State"), encoding="utf-8"))
    ek = base64.b64decode(ls["os_crypt"]["encrypted_key"])
    assert ek[:5] == b"DPAPI", ek[:5]
    key = dpapi_unprotect(base64.b64encode(ek[5:]).decode())
    print("AES key len:", len(key))

    from Crypto.Cipher import AES
    db = os.path.join(BASE, "Partitions", "ytmview", "Network", "Cookies")
    con = sqlite3.connect(db)
    rows = con.execute(
        "SELECT name, encrypted_value, value FROM cookies "
        "WHERE host_key LIKE '%youtube%'").fetchall()
    cookies = {}
    for name, enc, plain in rows:
        val = None
        if enc and len(enc) > 28:
            try:
                pt = AES.new(key, AES.MODE_GCM, nonce=enc[3:15]).decrypt_and_verify(
                    enc[15:-16], enc[-16:])
                # ytmdesktop wraps plaintext with a FIXED 31-byte prefix; strip it.
                # Other apps: pt = pt (no strip) or check prefix bytes first.
                val = pt[31:].decode()
            except Exception:
                val = None
        else:
            val = plain
        if val:
            cookies.setdefault(name, val)

    need = ("SAPISID", "SID", "HSID", "SSID", "APISID", "LOGIN_INFO")
    missing = [n for n in need if n not in cookies]
    if missing:
        print("missing login cookies:", missing,
              "| got:", sorted(cookies))
        print("=> app not logged in, or session expired (open app to refresh, then retry)")
        sys.exit(2)
    print("login cookies OK:", len(cookies))

    from ytmusicapi.auth.browser import get_authorization
    cookie_str = "; ".join(f"{n}={v}" for n, v in cookies.items())
    headers = {
        "cookie": cookie_str,
        "x-goog-authuser": "0",
        # CRITICAL: get_authorization expects "SAPISID Origin" joined by space
        "authorization": get_authorization(cookies["SAPISID"] + " https://music.youtube.com"),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(headers, open(OUT, "w"))
    print("wrote", OUT)

    import requests  # optional login sanity check
    r = requests.get("https://www.youtube.com/account",
                     headers={"cookie": cookie_str}, allow_redirects=False, timeout=30)
    if r.status_code == 200:
        print("session: ALIVE")
    else:
        print(f"session: DEAD ({r.status_code} -> {r.headers.get('location','')[:60]})")


if __name__ == "__main__":
    main()
