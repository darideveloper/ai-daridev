---
name: archive
description: Closes a finished story or sprint. Reconciles the Odoo card with the decisions and work already recorded in memory and produces the retro. Reads and summarises; never moves cards, never marks work done.
disable-model-invocation: true
---

# Archive

You are closing work that is already finished. You do not decide what shipped: the card and the
memories do. Never invent a retro for a story with no record; report the gap instead.

## Inputs

- `/archive <slug>` → one story.
- `/archive` → every card in the project's "Sprint Complete" stage that has no `retro/<slug>`
  memory yet. No time window: the absence of a retro is the filter.

## Steps

1. Read the workflow config from `AGENTS.md` (`odoo_project`, `odoo_stages`, `engram_project`,
   `decisions_dir`). If it is missing, ask me once. If memory resolves a project other than
   `engram_project`, stop and tell me to reopen the agent where `.engram/config.json` lives.
2. Story mode: load `story/<slug>`, its `decision` memories, and the Odoo card.
   Sprint mode: read the cards in "Sprint Complete" (`name`, `description`, `state`, `date_end`),
   extract `engram: story/<slug>` from each description, and skip the ones that already have a
   `retro/<slug>` memory.
3. Reconcile and **flag** drift, without fixing it:
   - card exists, no memory → "no agent record"
   - memory says shipped, card is not in Sprint Complete → "card not moved"
   - card `state` is not Approved → "not approved"
   - a decision contradicts the description → quote both
4. Output the retro (format below). Offer follow-ups as a list; don't create cards.
5. Save one memory `retro/<slug>` (type `learning`) with the retro body. Sprint mode saves
   `retro/sprint-<YYYY-MM-DD>` and adds totals, cross-story decisions and all follow-ups.
6. Write `docs/decisions/<slug>.md` **only if** the story produced a decision that is
   project-wide, hard to reverse, or affects a shared/ops contract. Otherwise create no file.

## Format

```
## <slug> — shipped <date>
Shipped: ...
Decisions: <dated, each with its Why>
Deviations: ...
Follow-ups: ...
Card: task <id> · state <state> · date_end <date>
Drift: <or "none">
```

Sprint mode groups the same blocks and adds: total shipped, cross-story decisions, the full
follow-up list, and all drift.

## Rules

- Never move a card, never write `stage_id`, never set `state` to done or canceled.
- If I ask to move or close a card, do it as a separate explicit request, one card at a time.
- No file writes outside `docs/decisions/`. No commits.
- Missing tools: say in one line what was skipped, and still produce the retro from whatever is
  available.
