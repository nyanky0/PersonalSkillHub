# Claude-Mem with Hermes

Claude-Mem MCP, its worker/database, host plugins, and optional observers are separate components. Installing its npm package or making `claude-mem mcp` respond does not prove persistent memory is initialized.

## Setup and verification

1. Read current upstream installation docs and repository notes; confirm the release's package entrypoint, MCP command, runtime requirements, worker setup, and data location.
2. Configure the documented local MCP command in Hermes via `hermes mcp add`; verify with `hermes config get mcp_servers --json`.
3. Run `hermes mcp test <name>` to verify launch and advertised tools; separately run the provider's doctor/status checks for worker health.
4. Verify a real search and, only if suitable, a safe write followed by read-back. A successful MCP handshake alone is not proof of durable read/write.
5. Host-specific Cursor/Grok Bot plugin installation is not required for Hermes MCP; do that only when explicitly requested.
6. Optional Claude-Mem observers may use an external LLM independently. Obtain consent before configuring them; never reuse Hermes credentials or change the selected Hermes model implicitly.

Check current runtime docs before installing or repairing worker dependencies. The MCP endpoint can start even if the background worker is not initialized.