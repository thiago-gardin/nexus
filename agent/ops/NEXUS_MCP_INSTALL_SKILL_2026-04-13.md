# Nexus MCP Install Skill

Date: 2026-04-13
Status: created

## Change

Created a repo-local Codex skill for installing the Nexus MCP server:

- `agent/skills/nexus-install-mcp/SKILL.md`
- `agent/skills/nexus-install-mcp/references/codex-mcp-config.md`
- `agent/skills/nexus-install-mcp/agents/openai.yaml`

Updated `README.md` to point agents to the skill.

## Purpose

Allow any future agent to install or repair the local Nexus MCP server in Codex without rediscovering:

- the MCP server module;
- the expected Codex `config.toml` format;
- the need to back up the config before editing;
- the correct stdio validation path;
- the expected nine normative Nexus MCP tools.

## Scope Boundaries

- No changes to `system/00_specs/`.
- No runtime changes.
- No dependency changes.
- No direct edit to `CURRENT_STATE.md`.
