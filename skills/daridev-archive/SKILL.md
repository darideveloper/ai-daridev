---
name: daridev-archive
description: Closes a finished card — green and validated, or self-verified with an explicit skip — appends a 4-line log, and proposes an ADR for a lasting decision. Never sets the green dot, never cancels, never invents a retro.
disable-model-invocation: true
---

# Archive

Close work that is already finished. The card and the files are the record.

**Mode first.** A card/slug means on; `--no-odoo` beats it; bare archive lists green cards in the
validated column, so on; off needs a slug or a pasted brief. Report it as the literal first line,
nothing before it: `Odoo: on · <project> · card #<id> "<name>"` or `Odoo: off · chat-only`.

Before the first write, read `../daridev-odoo/SKILL.md`: it owns the root memory and, on Odoo,
mode, stages, moves, assignees and the close variants. Never restate it.

## Steps

1. Load the card (`name`, `stage_id`, `state`, `user_ids`, children, `depend_on_ids`,
   `dependent_ids`, `date_end`, `write_date`) or the pasted brief. Read `docs/records/spec.md` (or
   `docs/ai-daridev/`) and the related ADRs (`rg docs/decisions/ 2>/dev/null`, or the legacy
   `docs/ai-daridev/decisions.md`, read-only).
2. **Gate.** Every step must be `1_done`/`1_canceled`. Then:
   - card in `odoo_stage_done` and green → `state=1_done`, `date_end` if empty, agent-only
     assignees;
   - card in an active column, all steps closed, and I say **skip review** → one write:
     `stage_id=odoo_stage_done`, `state=1_done`, `date_end`, agent-only assignees. **No green dot.**
     Skip review only when the Done-when were probed on the accepted surface. A card proven only
     locally goes through review, which greens it and records `surface: local — prod unproven`.

   Refuse an open step, a cancelled card, an archived card, another project. List what frees and
   what stays blocked.
3. Drift: a behaviour change with no spec sentence is listed; continue only on "archive anyway".
4. **Decision.** Ask once `Lasting decision on this card? [y/N]`. Yes → propose the ADR at the
   close, before the log: `docs/decisions/NNNN-<slug>.md` (next = highest existing + 1, `0001` when
   none), ≤15 lines: `# <title>`, `Decided: <date>`, `Because:`, `Alternatives:`, `Consequence:`.
   On approval write it; on refusal the log gets no `Decided:` line. Never append to a legacy
   `decisions.md` — freeze it per `../daridev-odoo/SKILL.md` first.
5. **Log** — create the log in the memory root (`docs/records/log.md`, or `docs/ai-daridev/log.md`
   when that is the memory) with a `# Log` header when missing, then append 4 lines max:

   ```markdown
   ## <slug> — <date>
   Shipped: <one line, plus the proof when review was skipped>.
   Decided: <docs/decisions/NNNN-<slug>.md — only when written this run or already covering the card>.
   Follow-up: <only when a card exists — #id>.
   ```

   A slug already in the log was reopened: append `— re-shipped <date>`, never a duplicate and
   never a silent skip. A block that moved with a repo migration moves with it.
6. A follow-up that matters becomes a card now or is dropped; no prose backlog.

Off: no card, no stage, no evidence gate — the log, the spec sentence and step 4 only.

## Never

Set the green dot, set `1_canceled`, create a card silently, write above the root, append to a
legacy `decisions.md`, archive a card with an open step, invent a retro.
