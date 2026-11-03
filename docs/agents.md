# Agents

The same five skills, one clone, symlinked everywhere. **Engram is required** — the skills stop if
its MCP is missing. **Odoo is optional** — without it they remember decisions but create no cards.

| Agent | Skills read from | Slash commands | Notes |
|---|---|---|---|
| OpenCode | `~/.agents/skills` (and `~/.config/opencode/skills`) | `~/.config/opencode/commands/*.md` | skills are **not** commands, the pointer files are |
| Claude Code | `~/.claude/skills` | skills already appear as `/skill-name` | `AGENTS.md` needs Claude Code ≥ 2.1.277 |
| Codex | `~/.agents/skills` | none (prompts deprecated); invoke `$skill` | `agents/openai.yaml` controls auto-invocation |
| Gemini CLI | `~/.gemini/skills` | — | register the Engram MCP for memory |
| Continue | `~/.continue/skills` | — | register the Engram MCP for memory |
| Windsurf | `~/.codeium/windsurf/skills` | — | register the Engram MCP for memory |

`scripts/install.sh` links into `~/.agents/skills` and into every agent directory that exists.

## OpenCode

Skills and commands are separate namespaces. The command body loads the skill explicitly:

```md
---
description: Pair on a story: TDD for code, plan-and-execute for non-code
---
Load the skill `ai-daridev-pair` with the skill tool and follow it exactly. My input: $ARGUMENTS
```

Every skill and command is namespaced `ai-daridev-*`, so `/ai-daridev-review` never collides
with OpenCode's built-in `/review`.

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

Skills are invoked as `$backlog`, not `/ai-daridev-backlog`. Auto-invocation is controlled per skill:

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
3. new session → the tracker tool responds (only if you use Odoo)
4. a skill loads (`skill` tool, or `/ai-daridev-story` as a command)
5. remove the Engram MCP entry, restart, run `/ai-daridev-pair` → it must **stop** and ask you to install Engram
6. remove the Odoo MCP entry, restart, run `/ai-daridev-pair` → it must run normally and say that no card was created
