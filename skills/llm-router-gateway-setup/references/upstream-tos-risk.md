# Answering "is provider X safe / bannable through a router?"

Read the gateway's own terms-risk catalog FIRST — it is the vendor's distilled reading of each
provider's ToS and beats guessing. OmniRoute ships it at `docs/reference/FREE_TIERS.md`, mirrored in
`open-sse/config/freeTierCatalog.ts`, and labels each upstream `avoid` / `caution` / ok.

Then apply these two axes — the answer almost always depends on both, so separate them explicitly:

1. **Which credential is being routed**
   - *Official API key, personal use* → not bannable. Routing through an OpenAI-compatible gateway is
     just a client; the clause the catalog usually flags is the free tier being licensed for
     "professional or business purposes" plus no-resale / no-key-sharing. That is a **caution**, not a
     ban threat.
   - *Account / OAuth-based provider driven by a third-party tool, proxy, or router* → the real ban
     risk. Those terms explicitly prohibit access through third-party software or proxies, and the
     gateway itself lists them as **avoid**. Consequence lands on the user's ACCOUNT, not just the key.
2. **Which tier**
   - *Free tier* → usage restrictions and resale prohibitions; fine for solo personal use.
   - *Cloud/enterprise service accounts (Vertex-style)* → provider terms restrict resale unless a
     reseller agreement exists: personal use ok, sharing/selling not.

## Multi-account and multi-key setups

- **Quota is per project/credential, not per person.** N accounts with their own projects = N× the free
  allotment. That is legitimate wired as **ordered fallbacks** (429 → next combo entry); spreading keys
  in **parallel** to multiply throughput is quota evasion, which is what the upstream abuse policies
  target. Recommend failover, never fan-out.
- **A consumer subscription is not an API tier.** A paid app/IDE plan does not raise API rate limits —
  the API tier is set at the billing-account level and stays Free until billing is linked. Read the
  vendor's rate-limit table that way: an allowance like `5 / 250K / 20` is usable now, `0 / 0` means
  **paid tier only** (say so, rather than letting the user think the zeros are a display bug).
- **IDE-agent quota rows are the avoid path.** When a catalog exposes an agent/IDE quota line, it belongs
  inside the vendor's own IDE; routing that quota through the gateway is the third-party-proxy clause the
  catalog marks `avoid`.
- **Prefer an official API key restricted to that one API** over an OAuth account, and if a key was pasted
  into chat, offer the rotate-and-rescrub path instead of treating it as still secret.

Answer shape the user wants: mechanism first (why it is or is not bannable), the two-axis split above,
and one actionable recommendation — "add the provider via its API key; do not route an OAuth account
through the gateway". Keep it to the verdict plus the one sentence of why, no lecture.

When the safe path is an API key, name the credential concretely (key from the provider's own console,
restricted to that API) and point at its key page rather than reciting a memorised click-path: key
types and creation UIs change, and a stale step-by-step is worse than a link. Mention only that the
durable constraints hold — free tier is licensed for personal/professional use, no resale, no sharing —
and that limit resets/quotas are per project, not per key.
