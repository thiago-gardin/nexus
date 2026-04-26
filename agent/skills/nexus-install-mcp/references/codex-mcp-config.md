# Codex MCP Config Reference For Nexus

Use this reference when installing the Nexus MCP server into Codex on Windows.

## Preconditions

- Work from the Nexus repo root.
- Preserve `system/00_specs/` as read-only.
- Do not edit `CURRENT_STATE.md`.
- Do not stage unrelated dirty worktree noise.

## Validate The Interpreter

Prefer the Python interpreter that can import all runtime dependencies:

```powershell
python -c "import sys; print(sys.executable); import yaml; import mcp; import system.runtime.mcp.server as s; print(','.join(s.MCP_TOOL_NAMES))"
```

If `.venv\Scripts\python.exe` fails but the default `python` passes, use the default interpreter path in `config.toml`.

## Back Up Codex Config

```powershell
$config = Join-Path $env:USERPROFILE ".codex\config.toml"
$backup = Join-Path $env:USERPROFILE (".codex\config.toml.bak-nexus-mcp-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
Copy-Item -LiteralPath $config -Destination $backup
Write-Output $backup
```

## Config Entry Pattern

Use an inline launcher so the MCP server can import the repo package even when Codex starts it outside the repo root.

```toml
[mcp_servers.nexus]
command = 'C:\Users\gardi\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe'
args = ["-c", 'import os, sys; sys.path.insert(0, r"C:\Dev\nexus"); os.environ.setdefault("NEXUS_DB_PATH", r"C:\Dev\nexus\.nexus\nexus.db"); from system.runtime.mcp.server import main; main()']
enabled = true
```

Adjust only these values when installing in another workspace:

- Python executable path
- repo root path in `sys.path.insert`
- `NEXUS_DB_PATH`

## Validate Codex Sees The Server

```powershell
codex mcp get nexus
codex mcp list
```

Expected `codex mcp get nexus` result:

- `enabled: true`
- `transport: stdio`
- command points to the validated Python interpreter
- args import `system.runtime.mcp.server`

## Validate A Real MCP Stdio Session

```powershell
@'
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command=r"C:\Users\gardi\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe",
    args=["-c", 'import os, sys; sys.path.insert(0, r"C:\\Dev\\nexus"); os.environ.setdefault("NEXUS_DB_PATH", r"C:\\Dev\\nexus\\.nexus\\nexus.db"); from system.runtime.mcp.server import main; main()'],
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(",".join(tool.name for tool in tools.tools))

asyncio.run(main())
'@ | python -
```

Expected tool list:

```text
get_domain,get_entity,get_relation,get_payload,search_objects,get_projection,create_proposal,get_decision_queue,explain_object
```

## Operational Log

After installing, create an `agent/ops/` log with:

- date;
- status;
- Codex config path;
- backup path;
- MCP server name;
- command and launcher behavior;
- validation commands and outcomes;
- caveats, especially interpreter or `.venv` issues.

Use `agent/ops/CODEX_NEXUS_MCP_INSTALL_2026-04-13.md` as the current example.
