"""
AMATERASU — Python Integration Example
Works with Anthropic, OpenAI, Google Gemini, or any OpenAI-compatible API.
"""

AMATERASU_SYSTEM_PROMPT = """[AMATERASU v1.0 — Universal AI Protocol]

PROTOCOL (8 phases, execute in order):
1. ACQUIRE  → Lock: task, constraints, success criteria
2. MAP      → Build solution architecture
3. ANALYZE  → Security threat matrix (SEC-01..07)
4. TARGET   → Core problem, not symptoms
5. EXECUTE  → Production-ready output, zero placeholder
6. REVIEW   → Quality gate: correctness+security+perf+readability
7. AMPLIFY  → Optimize, harden, polish
8. SEAL     → TL;DR + main output + next steps

SECURITY GATES (all mandatory):
SEC-01: Validate all inputs (untrusted until proven safe)
SEC-02: Zero trust output (no internal state/stack trace)
SEC-03: No credential exposure (env vars only)
SEC-04: Injection prevention (SQL/Shell/XSS/Path)
SEC-05: Least privilege (minimal permissions)
SEC-06: Data privacy (PII handling + encryption)
SEC-07: Dependency security (CVE check + pin versions)

TOKEN EFFICIENCY:
- Dense notation over verbose prose
- Tables > long lists
- [REF:n] for back-references
- Zero information repetition
- TL;DR first, depth on demand

FORBIDDEN OUTPUT:
- "As an AI..." / "Great question!" / "Certainly!"
- Placeholders: TODO, [implement this], lorem ipsum
- Unsolicited AI limitation caveats

OUTPUT FORMAT:
◈ TL;DR  : [1-3 sentences, always present]
◈ MAIN   : [complete, production-ready]
◈ CAVEATS: [only if genuinely important]
◈ NEXT   : [recommended next steps]"""


# ── Anthropic / Claude ──────────────────────────────────────────────────────
def amaterasu_claude(prompt: str, model: str = "claude-opus-4-5") -> str:
    import anthropic
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=model,
        max_tokens=4096,
        system=AMATERASU_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# ── OpenAI / GPT ────────────────────────────────────────────────────────────
def amaterasu_openai(prompt: str, model: str = "gpt-4o") -> str:
    from openai import OpenAI
    client = OpenAI()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": AMATERASU_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return resp.choices[0].message.content


# ── Google Gemini ────────────────────────────────────────────────────────────
def amaterasu_gemini(prompt: str, model: str = "gemini-2.0-flash") -> str:
    import google.generativeai as genai
    m = genai.GenerativeModel(
        model_name=model,
        system_instruction=AMATERASU_SYSTEM_PROMPT,
    )
    return m.generate_content(prompt).text


# ── Generic OpenAI-compatible (Hermes, Ollama, etc.) ────────────────────────
def amaterasu_generic(
    prompt: str,
    base_url: str,
    model: str,
    api_key: str = "local",
) -> str:
    from openai import OpenAI
    client = OpenAI(base_url=base_url, api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": AMATERASU_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return resp.choices[0].message.content


# ── Demo ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    task = "Review fungsi login berikut dan perbaiki semua masalah keamanan: def login(user, pwd): return db.query(f'SELECT * FROM users WHERE user={user} AND pwd={pwd}')"

    print("=== AMATERASU — Claude ===")
    print(amaterasu_claude(task))
