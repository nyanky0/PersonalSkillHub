# AMATERASU Example: Code Review

## Aktivasi
```
[AMATERASU_ACTIVE] Module: CODE_REVIEW
```

## Input
```python
def get_user(id):
    query = "SELECT * FROM users WHERE id=" + id
    return db.execute(query)
```

## AMATERASU Output

◈ TL;DR: SQL injection critical. Fix: parameterized query. 3 issues total.

---

**ACQUIRE**
- TASK: Review function keamanan & kualitas
- LANG: Python + SQL
- RISK: HIGH (user-facing, database)

**ANALYZE → SEC-04 TRIGGERED**

```
SEVERITY: CRITICAL
TYPE    : SQL Injection
LINE    : 2
VECTOR  : id parameter tidak disanitasi, dikonkat langsung ke query
EXPLOIT : id = "1 OR 1=1 --" → dump seluruh tabel users
```

**EXECUTE — Fixed Code**
```python
def get_user(user_id: int) -> dict | None:
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError(f"Invalid user_id: {user_id}")
    row = db.execute(
        "SELECT id, name, email FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    return dict(row) if row else None
```

**REVIEW — Issues Found**
```
☑ SEC-04 CRITICAL : SQL injection → FIXED (parameterized query)
☑ SEC-02 MEDIUM   : SELECT * exposes semua kolom → FIXED (explicit columns)
☑ SEC-01 MEDIUM   : No input validation → FIXED (type + range check)
☑ QUALITY LOW     : No type hints → FIXED
☑ QUALITY LOW     : No null handling → FIXED
```

**NEXT**
- Add rate limiting di layer atas fungsi ini
- Tambah logging untuk audit trail
- Test: `get_user(-1)`, `get_user("'; DROP TABLE users; --")`, `get_user(999999)`
