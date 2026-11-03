# AGENTS.md template

Copy this block into the `AGENTS.md` of the repository (or subproject) that uses the skills.
The skills read it on every run; without it they ask once and offer to add it.

```md
## Workflow config

- odoo_project: <project name exactly as it appears in Odoo>
- odoo_stages: Backlog, Sprint Backlog, Sprint in Progress, Sprint Complete, Old Completed Sprint, Cancelled
- odoo_uid: <your numeric Odoo user id>
- engram_project: <project name used by `engram init`>
- decisions_dir: docs/decisions
- card_tag: backend
```

## Notes

- `odoo_project` is a **name**, never an ID. The preflight resolves it by exact match (limit 2) and
  stops when there is no match or more than one, so a typo never writes into another project.
- `odoo_stages` must list the project's stages **exactly**. Every run validates them before writing
  anything; a renamed or missing stage stops the skill and prints the real list.
- `odoo_uid` is your numeric Odoo user id (the value in `project.task.user_ids`). It is read from
  here, never looked up in `res.users`, so the agent must not read that model. It marks which cards
  are yours and assigns work only when you ask for it in the same run.
- `engram_project` must match `.engram/config.json`. The skill stops rather than writing memory into
  a different project.
- The agent must be opened in the directory that holds `.engram/config.json`.
- `decisions_dir` is where ADRs go, and only for decisions that are project-wide, hard to reverse,
  or affect a shared/ops contract.
- `card_tag` is the **default** tag for this repo: `frontend`, `backend`, `script` or `workflow`
  (`workflow` = automation/workflow files, `script` = isolated scripts). The agent may pick another
  one per story when the work clearly belongs to it, and says which it picked.
- **Markers** are component-sized tracking items: Odoo subtasks with a name and a state only, and a
  matching `Markers:` line in the card description. `/ai-daridev-backlog` creates them;
  `/ai-daridev-pair` flips them when validated; `/ai-daridev-review` adjusts them.
- The `<h2>Review (ai-daridev)</h2>` block in a card belongs to `/ai-daridev-review`. Other skills
  preserve it verbatim and re-insert it between the tests and the `Markers:` line.

## Rules worth repeating in the repo

```md
- Never move cards between columns; that is the owner's job. The only exception is an explicit
  "move it" confirmation, one card at a time.
- Never mark a **card** done or cancelled; `state=Approved` + `date_end` is the agent's only claim
  on it. Markers are the exception: they are validated with `1_done`.
- Never write `user_ids`: cards are created unassigned. Assign only when explicitly asked, in that
  same run.
- Markers carry no detail: name + state only. Detail goes in the card's Review block.
- `engram sync` runs where `.engram/config.json` lives. `/ai-daridev-pair` and
  `/ai-daridev-archive` commit, and only `.engram/`.
- `.engram/engram.db*` and `.engram/tmp/` stay gitignored; only `config.json`, `manifest.json` and
  `chunks/` are committed.
```
