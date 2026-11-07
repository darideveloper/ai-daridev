# AGENTS.md template

Copy this block into the `AGENTS.md` of the repository (or subproject) that uses the skills.
Prefer generating it with `ai-daridev init` — it detects the stages, tags and Engram project for you.

```md
<!-- ai-daridev:start -->
## Workflow config
- version: 1
- odoo_project: <exact project name as it appears in Odoo>
- odoo_stage_backlog: Backlog
- odoo_stage_active: Sprint Backlog, Sprint in Progress
- odoo_stage_done: Sprint Complete
- odoo_stage_cancelled: Cancelled
- odoo_assignees: false
- card_tag: backend
- card_tags: frontend, backend, script, workflow
- engram_project: <the name used by engram init>
- decisions_dir: docs/decisions
- plan_steps: 5-20
- listing_limit: 20
<!-- ai-daridev:end -->
```

## What each key means

| Key | Meaning |
|---|---|
| `version` | schema version, currently `1` |
| `odoo_project` | **exact** name; preflight fails on 0 or 2+ matches. Omit the key to disable Odoo for this repo |
| `odoo_stage_*` | **roles**, not IDs. `active` is a list. Every name must exist in that project or preflight stops |
| `odoo_assignees` | `false` keeps new cards unassigned; `true` mirrors the personal uid (rare) |
| `card_tag` | default tag for the repo; must be one of `card_tags` |
| `card_tags` | the vocabulary the skills may use |
| `engram_project` | must equal `.engram/config.json` |
| `decisions_dir` | where ADRs go |
| `plan_steps` | `min-max` plan steps per card (each becomes a hidden subtask) |
| `listing_limit` | page size for every listing |

## Personal, never committed

`odoo_uid` is **not** in the block. It lives in `~/.config/ai-daridev/repos/<repo>.json` and is set
with:

```bash
ai-daridev uid <n>
```

It marks "mine" in listings. Cards are created unassigned unless you ask for an assignee in the
same run.

## Memory

- The store is **global** (`~/.engram/engram.db`); the repo only carries exported chunks.
- `ai-daridev preflight` imports pending chunks before every skill — nothing to remember after a pull.
- Every skill that writes memory exports and commits: `engram sync` → `git add .engram/` →
  `git commit -m "chore: memory — <kind> <id>"`. Only `.engram/`, never a push.
- Never hand-edit a chunk. On a manifest conflict, take either side and run `engram sync --import`.

## Rules worth repeating in the repo

```md
- Run `ai-daridev preflight` before any write; if it fails, print its errors and stop.
- Never move cards between columns; that is the owner's job, one card at a time.
- Never mark a card done or cancelled; `state=Approved` + `date_end` is the agent's only claim.
- Plan steps are the exception: they are validated with `1_done` (dropped steps use `1_canceled`).
- Plan steps are subtasks with `display_in_project=False`: that flag is what keeps them out of the
  board. Never write `project_id` (Odoo computes it from the parent) or `stage_id` on a step.
- Every step carries a key in its description: `ai-daridev: plan/<slug>#pN`. The key is the
  identity; names may change, keys never do.
- Structure changes to the plan (add/rename/remove/reorder) ask once before writing to Odoo;
  state changes are reported, not asked.
- `engram sync` runs where `.engram/config.json` lives. Checkpoints commit with
  `git commit --only -- .engram/`, so your staged files are never touched; never push.
```
