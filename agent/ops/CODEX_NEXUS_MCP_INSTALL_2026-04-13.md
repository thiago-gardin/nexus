# Codex Nexus MCP Install

Date: 2026-04-13
Status: installed

## Change

Installed the local Nexus MCP server in the user Codex configuration.

Codex config file:

- `C:\Users\gardi\.codex\config.toml`

Backup created before editing:

- `C:\Users\gardi\.codex\config.toml.bak-nexus-mcp-20260413-031832`

## MCP Entry

Server name:

- `nexus`

Transport:

- `stdio`

Command:

- `C:\Users\gardi\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe`

Launcher behavior:

- Adds `C:\Dev\nexus` to `sys.path`.
- Sets `NEXUS_DB_PATH` to `C:\Dev\nexus\.nexus\nexus.db` if not already set.
- Runs `system.runtime.mcp.server.main()`.

## Validation

- Parsed `C:\Users\gardi\.codex\config.toml` with Python `tomllib`.
- `codex mcp list` shows `nexus` as `enabled`.
- `codex mcp get nexus` shows `transport: stdio`.
- Direct MCP stdio client initialized the server and listed the expected normative tools:
  - `get_domain`
  - `get_entity`
  - `get_relation`
  - `get_payload`
  - `search_objects`
  - `get_projection`
  - `create_proposal`
  - `get_decision_queue`
  - `explain_object`

## Notes

The repo `.venv` was not used for the Codex MCP entry because it currently fails MCP import validation due to local environment issues. The Python interpreter already used successfully by the Nexus test suite was used instead.

No `system/00_specs/` files were modified.
