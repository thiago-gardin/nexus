---
name: nexus-install-mcp
description: Install or repair the local Nexus MCP server in Codex. Use when an agent needs to add the Nexus MCP entry to Codex, verify `codex mcp get nexus`, validate the stdio server, recover from a broken Python interpreter or `.venv`, or document the installation without changing Nexus specs/runtime.
---

# Nexus MCP Installer

## Scope

Install the local Nexus MCP server as a Codex MCP entry named `nexus`.

Do not modify `system/00_specs/`. Do not change Nexus runtime code unless the server itself is broken and the user explicitly asks for a runtime fix.

## Workflow

1. Read `AGENTS.md` and `WORKSPACE_CONTRACT.md` if working inside the Nexus repo.
2. Locate the repo root and MCP server:
   - repo root: current Nexus workspace, normally `C:\Dev\nexus`
   - server module: `system.runtime.mcp.server`
   - default DB: `.nexus\nexus.db`
3. Inspect the Codex config:
   - Windows default: `%USERPROFILE%\.codex\config.toml`
   - check for an existing `[mcp_servers.nexus]` entry before adding a new one
4. Validate the Python interpreter before writing config:
   - it must import `yaml`, `mcp`, and `system.runtime.mcp.server`
   - if repo `.venv` fails, prefer the Python interpreter that successfully runs the Nexus test suite
5. Back up `config.toml` before editing.
6. Add or update the `[mcp_servers.nexus]` entry.
7. Validate:
   - parse `config.toml` with Python `tomllib`
   - run `codex mcp get nexus`
   - start a real MCP stdio client and list tools
8. Record a short operational log under `agent/ops/` with the config path, backup path, command used, validation result, and any environment caveat.

## Reference

For the exact Windows config pattern and validation snippets, read `references/codex-mcp-config.md`.

If the skill must be auto-discovered outside this repo, copy the whole `agent/skills/nexus-install-mcp` folder into `$CODEX_HOME/skills` or `%USERPROFILE%\.codex\skills`. Keep the repo copy as the authoritative Nexus reference.

## Expected Tools

The installed server must expose exactly these normative Nexus MCP tools:

- `get_domain`
- `get_entity`
- `get_relation`
- `get_payload`
- `search_objects`
- `get_projection`
- `create_proposal`
- `get_decision_queue`
- `explain_object`

If the tool list differs, do not declare the install complete. Report the mismatch and inspect `system/runtime/mcp/server.py`.
