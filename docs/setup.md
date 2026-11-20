# Setup

Requirements: `bash` and `git`. Python, Node and Engram are not needed. Odoo is optional and
chosen per session. `playwright-cli` is used for browser evidence; ImageMagick `convert` is
optional for the screenshot cap.

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
2. removes the old `ai-daridev-*` skill links and command links, so only one command set exists;
3. removes `~/.config/opencode/skills/daridev-*` copies, because OpenCode gives that directory
   precedence and a stale copy would shadow the link;
4. symlinks `commands/*.md` into `~/.config/opencode/commands`;
5. replaces the global instruction block (`<!-- ai-daridev -->` or `<!-- daridev -->`) with the
   current one, keeping a timestamped backup;
6. prints the Odoo MCP snippet.

It never installs packages, never edits JSON/TOML, never touches credentials. `--check` verifies
the links, the commands, the absence of the old names and the global block.

A `git pull` is enough after the first install: skills and commands are symlinks.

## Repo block

Add the block to the `AGENTS.md` of the repo (or subproject) that uses the workflow. It supplies
the project and its parameters; whether a session writes cards is decided per session.

```md
<!-- daridev:start -->
- odoo_project: acme-app
- odoo_stage_done: Sprint Complete
- card_tag: backend
- odoo_assignee_manual_uid: 2
- deploy_url: https://acme.example.com/health
<!-- daridev:end -->
```

- **Memory follows the code.** Each repo that owns code gets its own block and its own
  `docs/records/`. A product spanning repos keeps one spec per repo; the Odoo board is the
  cross-repo view.
- **The switch is per session, not the block.** `--odoo`/`--no-odoo` or your words decide it, a
  card reference decides it, `plan` with a one-liner is off without asking, and `plan` with
  nothing asks once (`Odoo this session? [y/N]`, default no). Every phase prints the mode first.
- The block is also the anchor: the nearest one wins. A subproject with its own block gets its own
  `docs/records/` and its own Odoo project.
- A block with no keys (just the two markers) is valid for a files-only repo.
- `odoo_project` must be the **exact** name in Odoo. Zero or two matches → the skill stops and
  lists the real ones.
- `card_tag` is the primary tag; `card_tag_extra` adds a second one to every card.
- **Two users, one card.** The agent user is the MCP connection user; declare `odoo_assignee_uid`
  only to pin a different account. `odoo_assignee_manual_uid` is **you**: the card carries that
  user only while the next open step is a `[you]` step. No manual uid → no handoff; the first skill
  that needs one asks once.
- `odoo_stage_done` is the validated column. Review moves an approved card there and stamps
  `date_end`; `pair`'s close sets the green dot without moving the card; archive closes a green card
  there, or closes a self-verified card you explicitly release (which lands there **without** the
  green dot). It must match exactly one stage inside the project. Archived cards (`1_done`) are
  hidden by the default board filter.
- The **sprint column** and the **in-progress column** need no key: they are the stages whose names
  match `Sprint Backlog` and `In Progress` (case-insensitive). Zero or two matches → the skill asks
  once.
- `deploy_url` is the campaign’s deploy signal: after pushing main it waits 100s and requests that
  URL four times. `deploy_expect` optionally names a commit marker the response must contain. If
  the key is missing, the campaign asks once at pre-flight and prints the line to add; `skip` means
  no deploy wait and the app root is probed.
- Existing `ai-daridev` blocks are read unchanged; unknown keys are ignored.

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
  Inside Code Mode the tools are `tools.odoo.odoo_search_read` (there is no `odoo_search`),
  `odoo_search_count`, `odoo_get_fields`, `odoo_create`, `odoo_update`, `odoo_delete`. Servers
  name these differently, so verify before the first call.
- **Claude Code** — `claude mcp add --scope user odoo -- <path>/mcp.sh`.
- **Codex** — `~/.codex/config.toml`: `[mcp_servers.odoo]` with `command = "<path>/mcp.sh"`.
- **Gemini, Continue, Windsurf, Kiro, Devin** — register the same command in their MCP settings.

Verify by calling a read tool in a **new session**, not by listing servers.

The agent’s Odoo allowlist must include `ir.attachment` (read/create only, scoped to
`project.task` attachments) so pair can attach the step screenshot. Attachments are created on the
**card**, and `Evidence (daridev)` renders them by `/web/image/{id}`.

## Permissions

A plan creates one card and up to seven subtasks, so a per-call `ask` policy means up to eight
prompts. If that is noise, allow `odoo_create` and keep `odoo_update` and `odoo_delete` on `ask`.
The per-phase gate is already the approval, but the client may still prompt. Evidence adds one
`ir.attachment` create and one `odoo_update` call per visual step — the gallery on the card plus
the step's state — so with `odoo_update` on `ask` plan for two prompts per step. Cap: screenshot
≤500 KB. Redact secrets and mask client data before upload. The skills never delete or
bulk-update.

`/daridev-campaign` cannot wait on a prompt, so it needs `odoo_create` and `odoo_update` on
`allow`; keep `odoo_delete` and `odoo_execute` on `ask`, the campaign never uses them.

## Windows

Use WSL and run `./scripts/install.sh`. Without WSL, copy `skills/*` into your agent’s skills
directory and `commands/*.md` into `~/.config/opencode/commands` by hand; the skills have no
dependencies.

## Teammates

1. Clone the installer repo and run `./scripts/install.sh`.
2. Clone the project. Its `AGENTS.md` block is committed, so nothing to configure.
3. No Engram, no uid file, no preflight. Open the agent in the repo and use a command.

Without Odoo credentials the skills print the manual checklist and still write the files; captures
land in `docs/records/evidence/` instead of an attachment. A teammate with MCP reads the card
directly; without MCP, they paste the card text and the skill works on that. Without MCP they also
paste the screenshots into the card’s `Evidence (daridev)` section — the label is printed by
`pair` — or send the files to the reviewer if they cannot edit the card.

## Existing repos

- `docs/ai-daridev/` is read in place and the skill prints a one-line hint:
  `git mv docs/ai-daridev docs/records`. If `docs/records/` already exists, stop and ask; never
  merge two memories.
- Old blocks (`ai-daridev:start`), old slugs (`ai-daridev: story/<slug>`, `engram:`) and old
  `Review (ai-daridev)` headings are read; new writes use the new names.
- `decisions.md` is retired and read-only. The first ADR freezes it: `mkdir -p docs/decisions` and
  `git mv` it to `docs/decisions/legacy-decisions.md` (skip when that file already exists).
- ADRs are `docs/decisions/NNNN-<slug>.md`, numbered per repo from `0001`, next = highest existing
  + 1; `archive` writes one only when you approve it at the close gate.
- The first skill that writes asks once about folding an existing `openspec/` into the memory;
  the originals stay as history. `docs/decisions/` is already the home for decisions and is never
  folded.
- The memory is created by the write that needs it: `pair` creates `docs/records/`, `spec.md` and
  `evidence/.gitignore`; `archive` creates `log.md`. No empty stubs.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `/daridev-plan` missing in OpenCode | run `./scripts/install.sh`; commands live in `~/.config/opencode/commands` |
| Two command sets after upgrading | re-run `./scripts/install.sh`; it removes `ai-daridev-*` links |
| The agent says the Odoo project has 0 or 2 matches | make `odoo_project` match exactly one project |
| No cards are created | the session is off — say `--odoo`; or the block has no `odoo_project`, or MCP is not registered |
| Evidence is not on the step | the session was chat-only, or the upload failed; the file is under `docs/records/evidence/`, and a no-MCP teammate pastes it into the card gallery |
| `docs/records/evidence/` shows in `git status` | commit its `.gitignore` (`*` and `!.gitignore`); the images stay untracked |
| `spec.md` or `log.md` missing | the write that needs it creates it: `pair` for the spec and the evidence folder, `archive` for the log |
| A refined card stays in Backlog | the project has no `Sprint Backlog` stage, or the card was not in the backlog stage |
| Files land in the wrong repo | a parent `AGENTS.md` has the block; add one where you want the root |
