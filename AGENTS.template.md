# AGENTS.md template

Copy this block into the `AGENTS.md` of the repository (or subproject) that uses the skills.
The skills read it on every run; without it they ask once and offer to add it.

```md
## Workflow config

- odoo_project: <project name as it appears in Odoo>
- odoo_stages: Backlog, Sprint Backlog, Sprint in Progress, Sprint Complete, Old Completed Sprint, Cancelled
- engram_project: <project name used by `engram init`>
- decisions_dir: docs/decisions
- card_tag: one of frontend | backend | script | workflow
  (workflow = automation/workflow files, script = isolated scripts, default backend)
```

## Notes

- `odoo_project` is a **name**, never an ID. The skill resolves the id and the first stage on every
  run, so renaming or reordering stages never breaks it.
- `engram_project` must match `.engram/config.json`. The skill stops rather than writing memory into
  a different project.
- The agent must be opened in the directory that holds `.engram/config.json`.
- `decisions_dir` is where ADRs go, and only for decisions that are project-wide, hard to reverse,
  or affect a shared/ops contract.
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
- Markers carry no detail: name + state only. Detail goes in the card's Review block.
- `engram sync` runs where `.engram/config.json` lives. `/ai-daridev-pair` and `/ai-daridev-archive`
  commit, and only `.engram/`.
```
