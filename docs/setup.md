# Setup

Requirements: `bash` and `git`. Python, Node and Engram are not needed. Odoo is optional.
`playwright-cli` is used for browser evidence; ImageMagick `convert` is optional for the screenshot
cap.

## Install

```bash
git clone git@github.com:darideveloper/ai-daridev.git
cd ai-daridev
./scripts/install.sh
./scripts/install.sh --check
```

`install.sh` is idempotent and does exactly this:

1. symlinks `skills/*` into `~/.agents/skills` and into every installed agent that has a home
   (`~/.claude`, `~/.codex`, `~/.gemini`, `~/.continue`, `~/.codeium/windsurf`, `~/.kiro`,
   `~/.config/devin`);
2. removes `~/.config/opencode/skills/ai-daridev-*` copies, because OpenCode gives that directory
   precedence and a stale copy would shadow the link;
3. symlinks `commands/*.md` into `~/.config/opencode/commands`;
4. replaces the old `<!-- ai-daridev -->` block in the global instruction files with the current
   one, keeping a timestamped backup;
5. prints the Odoo MCP snippet.

It never installs packages, never edits JSON/TOML, never touches credentials. `--check` verifies the
links, the commands and the global block, and lists what is missing.

A `git pull` is enough after the first install: skills and commands are symlinks.

## Repo block

Add the block to the `AGENTS.md` of the repo (or subproject) that uses the workflow:

```md
<!-- ai-daridev:start -->
- odoo_project: acme-app
- odoo_stage_done: Sprint Complete
- card_tag: backend
<!-- ai-daridev:end -->
```

- The block is also the anchor: the nearest one wins. `n8n-automations/ourlivesapp` inherits
  `n8n-automations`, unless `ourlivesapp/AGENTS.md` declares its own block — then it gets its own
  `docs/ai-daridev/` and its own Odoo project.
- A block with no keys (just the two markers) is valid for a files-only repo.
- `odoo_project` must be the **exact** name in Odoo. Zero or two matches → the skill stops and lists
  the real ones.
- `odoo_stage_done` is the validated column: review moves an approved card there with the green dot,
  and archive only closes cards already there and green. Pair unblocks on `1_done`, not on the
  column. It must match the exact stage name. Archived cards (`1_done`) are hidden by the default
  board filter; enable `Closed Tasks` to see them.
- Existing 3.x blocks work unchanged; unknown keys are ignored.

## Odoo MCP

The agent talks to Odoo through an MCP server. Any server that exposes `project.task` works. Keep
credentials in one 600 file and register a wrapper, so nothing secret lives in an agent config:

```bash
# ~/.config/odoo-mcp.env   (chmod 600)
ODOO_URL=https://odoo.example.com
ODOO_DB=odoo_db
ODOO_USER=...
ODOO_PASSWORD=...
```

```bash
#!/usr/bin/env bash
set -eu
set -a; . "$HOME/.config/odoo-mcp.env"; set +a
exec <your-odoo-mcp-command> "$@"
```

Register it:

- **OpenCode** — `~/.config/opencode/opencode.json`, under `mcp.servers`:
  `"odoo": { "type": "local", "command": ["<path>/mcp.sh"], "disabled": false }`.
  Inside Code Mode the tools are `tools.odoo.odoo_create`, `tools.odoo.odoo_search_read`…
- **Claude Code** — `claude mcp add --scope user odoo -- <path>/mcp.sh`.
- **Codex** — `~/.codex/config.toml`: `[mcp_servers.odoo]` with `command = "<path>/mcp.sh"`.
- **Gemini, Continue, Windsurf, Kiro, Devin** — register the same command in their MCP settings.

Verify by calling a read tool in a **new session**, not by listing servers.

The agent's Odoo allowlist must include `ir.attachment` (read/create only, scoped to `project.task`
attachments) so pair can attach evidence.

## Permissions

A story creates one card and up to seven subtasks, so a per-call `ask` policy means up to eight
prompts. If that is noise, allow `odoo_create` in your agent's permissions and keep `odoo_update`,
`odoo_delete` and `odoo_unlink` on `ask`. Archive adds one `odoo_update` for the done state; the gate
is the approval, but the client may still prompt. Evidence adds one `ir.attachment` create and one
`odoo_update` per step; caps: screenshot ≤500 KB, inline output ≤40 lines / 4 KB, file ≤2 MB. Redact
secrets and mask client data
before upload. The skills never delete or bulk-update.

## Windows

Use WSL and run `./scripts/install.sh`. Without WSL, copy `skills/*` into your agent's skills
directory and `commands/*.md` into `~/.config/opencode/commands` by hand; the skills have no
dependencies.

## Teammates

1. Clone the installer repo and run `./scripts/install.sh`.
2. Clone the project. Its `AGENTS.md` block is committed, so nothing to configure.
3. No Engram, no uid file, no preflight. Open the agent in the repo and use a command.

Without Odoo credentials the skills print the manual checklist and still write the three files.

## First run in an existing repo

If the repo has `docs/decisions/*.md` or an `openspec/` folder and no `docs/ai-daridev/`, the first
skill that writes asks once: fold the old decisions and specs into `decisions.md` and `spec.md`
(originals untouched) or skip. It never asks again.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `/ai-daridev-pair` missing in OpenCode | run `./scripts/install.sh`; commands live in `~/.config/opencode/commands` |
| Two entries for the same command in Claude Code | you have both a skill and `~/.claude/commands/<name>.md`; delete the command file |
| The agent says the Odoo project has 0 or 2 matches | make `odoo_project` match exactly one project |
| No cards are created | the repo block has no `odoo_project`, or the Odoo MCP is not registered |
| Files land in the wrong repo | a parent `AGENTS.md` has the block; add one where you want the root |
