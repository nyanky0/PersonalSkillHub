# Local MCP client setup and verification

## Hermes

- Hermes config uses `mcp_servers.<name>.url` for HTTP MCP endpoints; use a loopback URL such as `http://127.0.0.1:<port>/mcp`.
- Verify with `hermes mcp list` and `hermes mcp test <name>`; test after changing transport, not just after editing YAML.
- HTTP config edits can be security-sensitive. Use Hermes-supported config tooling or ask for direct user approval; never bypass a config guard with a script/tool write.

## Other local clients

- Inspect the existing live config schema and supported transport first; fields differ between Cline/Gemini/Antigravity versions.
- Add a parallel HTTP entry and retain the old stdio entry for rollback. Avoid enabling both names at once in the same active client unless duplicate tools are intended.
- Read back the exact changed entry, restart/reload the application, and use its connection status or a harmless read-only tool to verify runtime connectivity.
- Document unsupported clients honestly rather than assuming a generic `url` field is accepted.

## Transport distinction

stdio means the client launches the MCP server process and exchanges protocol messages over stdin/stdout. HTTP MCP is a client request to a listening MCP endpoint. A dashboard HTTP listener is not MCP HTTP unless it routes MCP JSON-RPC at a specific endpoint. One process can serve both dashboard and MCP routes.

## Shared scope

Use one canonical project key across clients. Same key means shared project memory; global memory is shared separately. Avoid implicit mutable active-project defaults for concurrent agents; require explicit project arguments when correctness depends on scope.
