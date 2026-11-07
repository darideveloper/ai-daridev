# Preflight — the configuration contract

Every skill runs `ai-daridev preflight` before doing anything. It is the only place where names
are resolved, and the only failure mode: **if it exits non-zero, the skill prints its errors and
stops**. No asking, no guessing, no reading `AGENTS.md` by hand.

```bash
ai-daridev preflight        # JSON on stdout, one-line summary on stderr
ai-daridev doctor           # same, plus `engram doctor` and install checks
```

## Inputs

1. `AGENTS.md` in the repository that holds `.engram/config.json`, block between
   `<!-- ai-daridev:start -->` and `<!-- ai-daridev:end -->`.
2. `.engram/config.json` — the memory project.
3. `~/.config/ai-daridev/repos/<repo>.json` — your personal `odoo_uid`.
4. `~/.config/odoo-mcp.env` — Odoo credentials (optional).

## Output

```json
{
  "ok": true,
  "repo": "/path/to/repo",
  "config": {"path": ".../AGENTS.md", "version": 1},
  "project": {"id": 138, "name": "acme-app"},
  "stages": {"backlog": 526, "active": [527, 528], "done": 529, "cancelled": 531},
  "tags": {"frontend": 24, "backend": 65, "script": 79, "workflow": 80},
  "uid": 2,
  "engram": {"project": "acme-app", "match": true, "version": "engram 3.6.1"},
  "listing": {"limit": 20, "mine_only": false},
  "plan_steps": {"min": 5, "max": 20},
  "markers": {"min": 2, "max": 4},
  "assignees": false,
  "errors": [],
  "warnings": []
}
```

## Errors vs degradations

| Kind | Examples | Behaviour |
|---|---|---|
| **Error** (exit 1) | block missing/malformed, unknown key, `version` ≠ 1, project 0 or 2+ matches, a stage name not in the project, a tag missing, `engram_project` ≠ `.engram/config.json`, not the repo holding it, Engram not runnable, credentials present but rejected, malformed uid | the skill stops and prints the message |
| **Degradation** (exit 0 + warning) | no `~/.config/odoo-mcp.env`, Odoo timeout/unreachable, no personal uid | the skill continues; card writes use the manual handout, "mine" is not marked |

The distinction is deliberate: Odoo is optional, so an absent credential file cannot block a
teammate; a *wrong* password is a broken machine and must stop.

## What it reads

Only `project.project`, `project.task.type` and `project.tags` — the same project models the global
rules allow. It never reads `res.users`, and it never prints credentials.

`plan_steps` is the plan granularity (5–20 steps). `markers` is the deprecated pre-plan key:
preflight still emits it so blocks written before the plan existed keep validating, but every skill
reads `plan_steps`.

## Schema

See [`AGENTS.template.md`](../AGENTS.template.md). `odoo_uid` is rejected in the block on purpose:
identity is personal and stored outside the repository.

## Fixing it

```bash
ai-daridev init --project "acme-app" --uid 2   # owner, once per repo
ai-daridev uid 2                                # teammate, personal only
ai-daridev doctor                               # what is wrong, in one screen
```
