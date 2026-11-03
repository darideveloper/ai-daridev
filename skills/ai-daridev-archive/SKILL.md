---
name: ai-daridev-archive
description: Closes a finished story or sprint. Reconciles the Odoo card with the decisions and work already recorded in memory and produces the retro. Reads and summarises; never moves cards, never marks work done.
disable-model-invocation: true
---

# Archive

You are closing work that is already finished. You do not decide what shipped: the card and the
memories do. Never invent a retro for a story with no record; report the gap instead.

## Requirement

This workflow needs **Engram**, the memory MCP. If its tools are not available, stop and tell me to
install Engram and restart the agent. Do not continue without memory.

## Inputs

- `/ai-daridev-archive <slug>` → that story.
- `/ai-daridev-archive` → list the candidates and **ask**: one of them, all, or cancel. Never
  assume "all".
  - With Odoo: cards in "Sprint Complete" of the configured project (`project_id` + `stage_id`,
    `limit 20`, paginate with `offset`) that have no `retro/<slug>` memory. Mark the ones assigned
    to `odoo_uid` as yours.
  - Without Odoo: `story/*` memories that have no `retro/*` memory.

## Steps

1. Read the workflow config from `AGENTS.md` (`odoo_project`, `odoo_stages`, `engram_project`,
   `decisions_dir`, `odoo_uid`). If it is missing, ask me once. If memory resolves a project other
   than `engram_project`, stop and tell me to reopen the agent where `.engram/config.json` lives.
   Preflight, read-only: resolve `project.project` by exact name (`limit 2`, stop on 0 or more than
   one) and check that every name in `odoo_stages` exists. A missing stage stops the run and prints
   the real list.
2. Refresh memory: `engram sync --import` in the directory holding `.engram/config.json`. Warn and
   continue if it fails.
3. Story mode: load `story/<slug>`, its `decision` memories, any `review/<slug>` record, and the
   Odoo card.
   Sprint mode: read the cards in "Sprint Complete" (`name`, `description`, `state`, `date_end`,
   `date_last_stage_update`), extract `engram: story/<slug>` from each description, and skip the
   ones that already have a `retro/<slug>` memory.
4. Reconcile and **flag** drift, without fixing it:
   - card exists and neither `story/*` nor `review/*` exists → "no agent record"
   - memory says shipped, card is not in Sprint Complete → "card not moved"
   - approved means any of: `state = 03_approved`, stage is "Sprint Complete", or a `review/*`
     record — only when none of them applies is it "not approved"
   - a marker is still not `1_done` while the card sits in "Sprint Complete" → "marker still open:
     <name>"; list them, never flip them here
   - a decision contradicts the description → quote both
5. Output the retro (format below). Offer follow-ups as a list; don't create cards.
6. Save one memory `retro/<slug>` (type `learning`) with the retro body: `title` = `retro <slug>`,
   `content` in `**What** / **Why** / **Where** / **Learned**`. Sprint mode saves
   `retro/sprint-<YYYY-MM-DD>` and adds totals, cross-story decisions and all follow-ups. If the
   answer carries `judgment_required`, ask me once and resolve it with `mem_judge_many`
   (`candidates[].judgment_id`).
7. Write `docs/decisions/<slug>.md` **only if** the story produced a decision that is
   project-wide, hard to reverse, or affects a shared/ops contract. Otherwise create no file.
8. **Export and commit the memory** (this skill may commit — the only one that may):
   - run `engram sync` in the directory holding `.engram/config.json`;
   - commit **only if** that directory (or its git root) contains `.engram/config.json`;
   - stage only `.engram/`; if `git diff --cached --name-only` shows anything outside `.engram/`,
     do not commit — list the staged files and stop;
   - message: `chore: memory — <slug>`;
   - never `git push`. If there is nothing to export or nothing staged, say so and continue.

## Format

```
## <slug> — shipped <date>
Shipped: ...
Decisions: <dated, each with its Why>
Deviations: ...
Follow-ups: ...
Card: task <id> · state <state> · end <date_end or date_last_stage_update>
Drift: <or "none">
```

Sprint mode groups the same blocks and adds: total shipped, cross-story decisions, the full
follow-up list, and all drift.

## Rules

- Never move a card, never write `stage_id`, never set `state` to done or canceled.
- If I ask to move or close a card, do it as a separate explicit request, one card at a time.
- No file writes outside `docs/decisions/`. The commit in step 8 is the only git write this skill
  makes, and it touches `.engram/` only.
- Missing tools: Engram is required — stop if memory is unavailable. If Odoo is unavailable, still
  produce the retro from memory and say what could not be checked.
