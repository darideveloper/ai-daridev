# Agents

The same four skills, one clone, symlinked everywhere. MCP servers are registered **per agent**;
where they are missing the skills fail open.

| Agent | Skills read from | Slash commands | Notes |
|---|---|---|---|
| OpenCode | `~/.agents/skills` (and `~/.config/opencode/skills`) | `~/.config/opencode/commands/*.md` | skills are **not** commands, the pointer files are |
| Claude Code | `~/.claude/skills` | skills already appear as `/skill-name` | `AGENTS.md` needs Claude Code ≥ 2.1.277 |
| Codex | `~/.agents/skills` | none (prompts deprecated); invoke `$skill` | `agents/openai.yaml` controls auto-invocation |
| Gemini CLI | `~/.gemini/skills` | — | skills only, no MCP required |
| Continue | `~/.continue/skills` | — | skills only |
| Windsurf | `~/.codeium/windsurf/skills` | — | skills only |

`scripts/install.sh` links into `~/.agents/skills` and into every agent directory that exists.

## OpenCode

Skills and commands are separate namespaces. The command body loads the skill explicitly:

```md
---
description: Run the hola-ai pair skill
---
Load the skill `pair` with the skill tool and follow it exactly. My input: $ARGUMENTS
```

MCP goes under `mcp.servers`:

```jsonc
"engram": {
  "type": "local",
  "command": ["<engram-path>", "mcp", "--tools=agent"],
  "disabled": false
}
```

Note: `opencode mcp list` may report no servers even when the tools work. Verify by calling a tool
in a **new session**, not by listing.

## Claude Code

- Upgrade to ≥ 2.1.277 for native `AGENTS.md` support (`claude update`).
- Register MCP at user scope so it works in every project:

```bash
claude mcp add --scope user engram -- <engram-path> mcp --tools=agent
claude mcp add --scope user odoo   -- <odoo-wrapper-path>
```

- No command files needed: a skill is already `/skill-name`. Adding `~/.claude/commands/<name>.md`
  creates a second entry with the same name.

## Codex

```toml
# ~/.codex/config.toml
[mcp_servers.engram]
command = "<engram-path>"
args = ["mcp", "--tools=agent"]

[mcp_servers.odoo]
command = "<odoo-wrapper-path>"
```

Codex expands **no** environment variables in config. Pass literal `env = { K = "V" }`, or inherit
with `env_vars = ["K"]`, or — preferred — point at a wrapper script that reads a 600 file.

Skills are invoked as `$backlog`, not `/backlog`. Auto-invocation is controlled per skill:

```yaml
# skills/<id>/agents/openai.yaml
policy:
  allow_implicit_invocation: false
```

## Credentials

Never put secrets in an agent config. One wrapper, one file:

```bash
# ~/.config/<name>.env   (chmod 600)
ODOO_URL=...
ODOO_DB=...
ODOO_USER=...
ODOO_PASSWORD=...
```

```bash
#!/usr/bin/env bash
set -eu
set -a; . "$HOME/.config/<name>.env"; set +a
exec <command> "$@"
```

Register the wrapper in every agent. It works from a GUI launch too, where shell exports do not
exist.

## Verification

1. `engram doctor`
2. new session → the memory tool responds
3. new session → the tracker tool responds
4. a skill loads (`skill` tool, or `/story` as a command)
5. remove the MCP entry, restart, run `/pair` → it must still work and say what it skipped
