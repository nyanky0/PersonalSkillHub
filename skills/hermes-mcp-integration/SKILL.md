---
name: hermes-mcp-integration
description: "Use when adding MCP servers to Hermes. Verify health."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [hermes, mcp, integrations, providers, plugins]
---

# Hermes MCP integrations

## Procedure

1. Confirm scope: Hermes MCP connection is distinct from a vendor plugin for another host. Do not resume unrelated tasks while adding integration.
2. Load `autonomous-ai-agents/hermes-agent` and `references/native-mcp.md`; consult live Hermes docs.
3. Inspect `hermes mcp --help`, `hermes mcp add --help`, `hermes config get mcp_servers --json`, and current model config before changes.
4. Research upstream provider installation docs and exact command, runtime, transport, persistence requirements, and whether setup triggers login, telemetry, or paid services. Do not assume `npx <package> mcp` initializes its backend.
5. Install only required prerequisites via official sources, verify versions, and distinguish package/CLI installation from host plugin and worker setup.
6. Add with `hermes mcp add` where possible. If interactive tool selection blocks it, use Hermes config CLI only after verifying supported schema; don't invent an MCP tools allowlist.
7. Verify `hermes mcp test <name>` AND actual backend behavior/persistence; MCP handshake/tool discovery alone is not proof of a healthy memory store.
8. Preserve requested model/provider; use only user-approved fallback. Never redirect API/model independently to troubleshoot another integration.
9. Report config, connection/tool discovery, backend health, and read/write persistence verification separately. Do not claim complete installation when any layer is unverified.

See `references/claude-mem.md` for Claude-Mem setup specifics.