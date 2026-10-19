---
name: shared-local-mcp-services
description: "Use when sharing a local MCP service across agents."
metadata:
  hermes:
    tags: [mcp, local-services, shared-memory, http, sqlite, multi-agent]
---

# Shared local MCP services

Use this class workflow when one machine-local service must be shared across multiple agent clients.

## Workflow

1. **Inspect before designing.** Confirm current MCP transport, process lifecycle, listener binds, storage ownership, active-scope behavior, and actual client settings. Identify whether HTTP is already used for a dashboard/API; do not confuse that with an MCP endpoint.
2. **Design one owner.** Prefer a single long-running process and one database owner, with the user interface and MCP endpoint on one loopback listener or clearly coordinated listeners. Keep stdio available if existing users need compatibility.
3. **Make scope explicit per call.** For collaborative work, partition by stable project identity, not agent identity. Same-project agents share records; different projects remain isolated; global records remain deliberately shared. Do not use mutable process-wide “active project” as the identity for concurrent requests.
4. **Test before implementation.** Add protocol-level tests with isolated temporary storage. Prove they fail for the missing endpoint/behavior, then implement the smallest transport adapter and reuse existing tool handlers.
5. **Harden at the HTTP boundary.** Bind only to `127.0.0.1`; cap body size; validate JSON-RPC, tool parameters, types and limits; return safe errors; avoid logging payloads and permissive CORS. Test malformed input, unsupported methods, oversize requests, listener conflicts, and requests after scope changes.
6. **Verify each layer separately.** Distinguish client configuration (configured), live handshake/tool discovery (connected), and actual tool calls (used). A copied test prompt, successful config write, reload command exit code, or agent self-report alone is not proof of runtime use. After a reload, verify a fresh connection/tool discovery or observed post-reload tool call; otherwise report “reload required / not verified” with manual steps. For write verification, use one full-test prompt that creates a clearly tagged isolated temporary record, reads it back, deletes it, and verifies cleanup; surface cleanup uncertainty rather than claiming success. Run syntax checks, focused HTTP tests, existing app tests, dashboard/health checks, and read back each client configuration. Before running legacy suites against a live service, inspect their target URL, environment overrides, and fixture cleanup; isolate them on a temporary DB and port, and report the exact failing case rather than reducing results to a pass fraction.
7. **Roll out reversibly.** Preserve old stdio configuration until HTTP is verified. Update local agent settings explicitly and restart/reload those clients; do not promise cross-agent availability until each is tested.
8. **Commit and publish last.** Review staged diff and ensure no database, backups, secrets or local config enter the repo. Push only after the user-authorized verification gate, then compare the remote ref SHA with the local commit.

## Restart and deployment

Before restarting a live local service, identify its actual process, launcher/client relationship, bound endpoint, and runtime data path; config values may be stale, so inspect the process/environment or read-only live state. Create and verify a backup of the database that process actually opened before stopping it. Prefer the owning client's normal restart/reload so stdio or managed-child lifecycle remains attached. If the client does not relaunch it, use a standalone process only after confirming the registered endpoint/transport, then verify the configured MCP URL with `initialize` and `tools/list`, dashboard health, served UI, and read-only data counts/integrity. Keep the pre-restart DB path and backup available for rollback; never infer the active DB solely from a settings field or overwrite it with a test DB.

## Agent setup and user consent

Before modifying any agent configuration, detect supported clients and show a per-client status plus exact proposed diff. Require explicit user approval before writing; back up each selected config, change only approved clients, report restart/reload needs and outcomes, verify connectivity/tool discovery, and provide rollback. Never silently overwrite unknown/custom settings. Pair automated setup with a manual recovery guide for unsupported clients or failed setup. Keep these states distinct: configured does not imply connected, and connected does not imply the agent actually used memory tools.

## Durable memory and collaboration boundary

A shared memory server is a searchable durable store, not automatic recall of every conversation, a transcript mirror, or proactive agent notification. Installing/registering its MCP endpoint only makes tools available; it does not by itself prove that an agent invokes them. A connected MCP tool is not automatically invoked by a client. To make memory use the default, configure each supported agent with instructions/skills/rules/hooks or native memory integration to read the explicit project scope plus global context at task start, proactively checkpoint durable decisions/findings at meaningful milestones and task completion, and report pending review items at turn end when supported; then verify actual tool calls per client. Auto-captured high-confidence durable memories may be pending review while remaining usable; distinguish trust/review state from access. Do not automatically save transient chat, unresolved speculation, or secrets. Keep project IDs stable and explain fallback behavior when a client omits scope. Distinguish confirmed facts/decisions from transient chat, unresolved speculation, and secrets; avoid storing the latter.

## Local client setup details

See [client setup and transport notes](references/local-mcp-clients.md) before changing Hermes, Cline, Gemini/Antigravity, or other local client configurations.
