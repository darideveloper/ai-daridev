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
    `limit` from preflight, paginate with `offset`) that have no `retro/<slug>` memory. Mark the ones
    assigned to `uid` as yours.
  - Without Odoo: `story/*` memories that have no `retro/*` memory.

## Steps

1. **Preflight.** Run `ai-daridev preflight` in the repo root and use its JSON (`project`, `stages`,
`tags`, `uid`, `listing`, `plan_steps`, `assignees`). If the command is missing, stop and say: run
`./scripts/setup.sh` from the ai-daridev repo. If it exits non-zero, print its `errors` and stop —
do not ask, do not guess, do not read `AGENTS.md` yourself. Print its `warnings` once, then continue.

2. Memory is already imported by the preflight (step 1). Do not run `engram sync --import` again.
3. Story mode: load `story/<slug>`, `plan/<slug>`, its `decision` memories, any `review/<slug>`
   record, and the Odoo card.
   Sprint mode: read the cards in the **done stage** (`stages.done`) (`name`, `description`, `state`, `date_end`,
   `date_last_stage_update`), extract `engram: story/<slug>` from each description, and skip the
   ones that already have a `retro/<slug>` memory.
4. Reconcile and **flag** drift, without fixing it:
   - card exists and neither `story/*` nor `review/*` exists → "no agent record"
   - memory says shipped, card is not in Sprint Complete → "card not moved"
   - approved means any of: `state = 03_approved`, stage is "Sprint Complete", or a `review/*`
     record — only when none of them applies is it "not approved"
   - a step is still not `1_done` while the card sits in "Sprint Complete" → "step still open:
     <name>"; list them, never flip them here
   - `plan/<slug>` still has `pending_sync` → "plan not synced to the tracker"
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
   - `git add .engram/`; detached HEAD, merge/rebase in progress or `.engram/` conflicts → report
     and skip the commit (the sync already happened);
   - `git commit --only -m "chore: memory — <slug>" -- .engram/`, leaving anything else staged
     untouched; never `--no-verify`, never `git push`;
   - nothing to export → say so and continue.

## Format

```
## <slug> — shipped <date>
Shipped: ...
Decisions: <dated, each with its Why>
Deviations: ...
Follow-ups: ...
Plan: <done>/<total> steps · dropped <n> · open <n>
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
