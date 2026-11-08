---
name: ai-daridev-archive
description: Closes a finished story or sprint. Reconciles the card with the decisions already recorded and appends the retro to docs/ai-daridev/log.md. Never moves cards, never marks work done.
disable-model-invocation: true
---

# Archive

Close work that is already finished. The card and the files are the record; never invent a retro.

## Inputs

- `/ai-daridev-archive <slug>` → that story, even if the card has not been moved yet.
- Bare → cards in `odoo_stage_done` that are not yet in `docs/ai-daridev/log.md`; ask one, all, or
  cancel. Never assume "all". No `odoo_stage_done` or no Odoo → require a slug or a pasted story.

## Steps

1. **Reconcile** the card, its subtasks and the decisions. Flag drift, do not fix it: card not moved,
   steps still open, a decision that contradicts the description (quote both), a behavior change
   with no spec entry.
2. **Print the retro**:

```
## <slug> — shipped <date>
Shipped: <one or two lines>
Decisions: <dated, each with its Why>
Follow-ups: <or "none">
Plan: <done>/<total> steps · dropped <n> · open <n>
Card: task <id> · state <state> · end <date_end or date_last_stage_update>
Drift: <or "none">
```

3. **Append** the block to `docs/ai-daridev/log.md` unless the slug is already there. Create the file
   with `# Log` if needed. Nothing else is written.
4. Follow-ups are listed, never turned into cards.

## Rules

- Never move a card, never write `stage_id`, never set `state` to done or cancelled.
- Read `docs/ai-daridev/spec.md` and `decisions.md` first; the retro quotes them, it does not
  reinvent them.

## Always

- **Root.** Walk up from the current directory to the nearest `AGENTS.md` that holds
  `<!-- ai-daridev:start -->`. That directory is the root: read and write `docs/ai-daridev/` there
  and write nothing outside it. No block → ask once: create it here, use the git root, or chat-only.
- **Config.** Read `odoo_project`, `odoo_stage_done` and `card_tag` from the block. No
  `odoo_project` → Odoo is off. Resolve the project, the tags and the stages by exact name; 0 or 2+
  matches → stop and list the real ones. Backlog stage = lowest `sequence`. Default tag `backend`.
- **Never move a card** between stages, never set a card `1_done`/`1_canceled`, never assign.
  Agents write: the description (story), subtask states, `state=03_approved` + `date_end` (close),
  `state=02_changes_requested` (review).
- **One approval gate per phase.** Structure asks once; state changes are reported, not asked.
- **Odoo unavailable** → print the handout and continue; the files are still written.
- **Decisions** → one append to `docs/ai-daridev/decisions.md`, only when project-wide, hard to
  reverse or a shared/ops contract. Everything else stays in the conversation.
- **Fold-in.** If `docs/ai-daridev/` is missing and `docs/decisions/*.md` or `openspec/` exists, ask
  once to fold them into `decisions.md` and `spec.md`; the originals stay as frozen history.
- **Never commit.** Never write secrets or client data into the three files.
- **Cards** are found by `<p><em>ai-daridev: story/<slug></em></p>`; the legacy
  `engram: story/<slug>` is accepted on read.
