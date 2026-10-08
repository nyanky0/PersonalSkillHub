# AI-Slop Audit Report Template
Use this structure for consistent audit reporting.

---

## EXECUTIVE SUMMARY
[1-2 sentences: app type, main findings, overall quality]

Example: "Enterprise B2B internal tool. No AI-slop markers found. Issues were developer stub residue, not AI-generated content."

---

## FINDINGS & FIXES

### [PRIORITY] Issue Title
**Location:** `file/path.jsx:line`
**Issue:** [What's wrong]
**Fix:** [What was done]
**Status:** ✅ RESOLVED | ⚠️ ACCEPTABLE | 🔄 PENDING

---

## REMAINING ITEMS (Intentional, Not Slop)

| File | Line | Type | Justification |
|------|------|------|---------------|
| `Component.jsx` | 123 | console.error | Legitimate error handler |
| `Layout.jsx` | 456 | conditional debug | Guarded by feature flag |

---

## CODE QUALITY ASSESSMENT

### ✅ Strengths
- [List what's good]

### ⚠️ Areas for Improvement
- [List optional improvements]

### ✅ Anti-Slop Indicators
- [Evidence of human-crafted content]

---

## FILES MODIFIED
1. `path/to/file1.jsx` — [what changed]
2. `path/to/file2.jsx` — [what changed]

---

## VERIFICATION
```bash
# Commands run to verify fixes
grep -rn "pattern" resources/js/
npm run build
```

---

## CONCLUSION
[1 paragraph: overall assessment, readiness for production]

---

## NEXT STEPS (Optional)
1. [Future improvement 1]
2. [Future improvement 2]