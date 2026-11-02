# AMATERASU Example: Debugging

## Input
```
ERROR: jwt.exceptions.DecodeError: Signature verification failed
Stack: auth_middleware.py line 47, verify_token(token)
Tried: reinstall PyJWT, check token format
```

## AMATERASU Output

◈ TL;DR: Bukan bug library — secret key mismatch antara token issuer dan verifier. Fix: pastikan SECRET_KEY sama di kedua sisi, atau token sudah expired/tampered.

---

**ACQUIRE**
```
TASK   : Debug JWT signature verification failure
CONTEXT: Python, PyJWT, auth middleware
TRIED  : reinstall lib, format check
```

**ANALYZE**
```
ROOT_CAUSE_CANDIDATES (ordered by probability):
1. [HIGH] SECRET_KEY beda di env issuer vs verifier
2. [HIGH] Token dari env berbeda (dev token di prod verifier)  
3. [MED]  Algorithm mismatch (HS256 vs RS256)
4. [LOW]  Token tampered / corrupted in transit
5. [LOW]  PyJWT version mismatch (decode API berubah di v2.x)
```

**SEC-SCAN**
```
⚠ SEC-03: Jangan log SECRET_KEY saat debug
⚠ SEC-02: Jangan expose detail error ke client (hanya "Invalid token")
⚠ SEC-01: Validate token format sebelum decode
```

**EXECUTE — Diagnostic Script**
```python
import jwt, os

def diagnose_jwt(token: str) -> None:
    secret = os.environ.get("JWT_SECRET_KEY")
    if not secret:
        print("❌ JWT_SECRET_KEY tidak ada di environment!")
        return

    # Step 1: decode tanpa verify (lihat header & payload)
    try:
        header = jwt.get_unverified_header(token)
        payload = jwt.decode(token, options={"verify_signature": False})
        print(f"✓ Header : {header}")
        print(f"✓ Payload: {payload}")
        print(f"✓ Algo   : {header.get('alg')}")
    except Exception as e:
        print(f"❌ Token malformed: {e}")
        return

    # Step 2: verify dengan secret yang ada
    try:
        jwt.decode(token, secret, algorithms=["HS256"])
        print("✓ Token valid! (masalah bukan di sini)")
    except jwt.ExpiredSignatureError:
        print("❌ Token expired — issue token baru")
    except jwt.InvalidSignatureError:
        print("❌ SECRET_KEY mismatch — cek .env di kedua service")
    except jwt.DecodeError as e:
        print(f"❌ Decode error: {e}")

# Jalankan:
# diagnose_jwt(request.headers.get("Authorization", "").removeprefix("Bearer "))
```

**REVIEW**
```
☑ Root cause identified (key mismatch most probable)
☑ Diagnostic tool provided — run first before guessing
☑ SEC-02: error detail tidak leak ke client
☑ SEC-03: SECRET_KEY dari env, tidak hardcoded
```

**NEXT**
1. Jalankan diagnostic script dengan token yang gagal
2. Jika "SECRET_KEY mismatch" → sync `.env` di semua service
3. Jika "Token expired" → fix refresh token flow
4. Production: set `JWT_SECRET_KEY` via secret manager, bukan `.env`
