# Claude-Mem via Hermes MCP

Use when recalling, searching, or storing session memories via the local Claude-Mem worker.

Claude-Mem upstream (Apache-2.0) exposes an MCP server and its memory search/store tools. Hermes loads it for this profile from `mcp-servers.json`; setup/update is managed separately under `C:/Users/yudah/AppData/Local/claude-mem`.

## Available tools
- `search(query)` to find relevant memories; filter matches before fetching detail.
- `timeline(anchor=ID)` for nearby context.
- `get_observations(ids=[...])` for selected full observations.
- `get_tool_uses(ids=[...])` only when needed to inspect original tool input/output.
- Store memory with the upstream tool and mark the appropriate platform/source when supported.

Do not dump all observations. Avoid placing credentials or other secrets into memory. Hermes built-in MEMORY.md remains available alongside this provider.
