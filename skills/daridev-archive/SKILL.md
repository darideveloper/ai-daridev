---
name: daridev-archive
description: Closes a finished card — green and validated, or self-verified with an explicit skip — and appends a 4-line log. Never sets the green dot, never cancels, never invents a retro.
disable-model-invocation: true
---

# Archive

Close work that is already finished. The card and the files are the record.

**Mode first.** A card/slug means on; `--no-odoo` beats it; bare archive lists green cards in the
validated column, so on; off needs a slug or a pasted brief. Report it as the literal first line,
nothing before it: `Odoo: on · <project> · card #<id> "<name>"` or `Odoo: off · chat-only`.

On Odoo, read `../daridev-odoo/SKILL.md` before the first write: it owns mode, stages, moves,
assignees and the close variants. Never restate it.

## Steps

1. Load the card (`name`, `stage_id`, `state`, children, `depend_on_ids`, `dependent_ids`,
   `date_end`, `write_date`) or the pasted brief. Read `docs/records/spec.md` and the related ADRs.
2. **Gate.** Every step must be `1_done`/`1_canceled`. Then:
   - card in `odoo_stage_done` and green → `state=1_done`, `date_end` if empty, agent-only
     assignees;
   - card in an active column, all steps closed, and I say **skip review** → one write:
     `stage_id=odoo_stage_done`, `state=1_done`, `date_end`, agent-only assignees. **No green dot.**
     Skip review only when the Done-when were probed on the accepted surface; a card proven only
     locally goes through review.

   Refuse an open step, a cancelled card, an archived card, another project. List what frees and
   what stays blocked.
3. Drift: a behaviour change with no spec sentence is listed; continue only on "archive anyway".
4. **Log** — append 4 lines max:

   ```markdown
   ## <slug> — <date>
   Shipped: <one line, plus the proof when review was skipped>.
   Decided: <only when an ADR exists — path>.
   Follow-up: <only when a card exists — #id>.
   ```

   A slug already in the log was reopened: append `— re-shipped <date>`, never a duplicate and
   never a silent skip. A block that moved with a repo migration moves with it.
5. A follow-up that matters becomes a card now or is dropped; no prose backlog.

Off: no card, no stage, no evidence gate — the log and the spec sentence only.

## Never

Set the green dot, set `1_canceled`, create a card silently, write above the root, archive a card
with an open step, invent a retro.
