---
name: ai-daridev-review
description: Reviews a card produced by someone else against its acceptance criteria and markers, proposes the Odoo writes, and applies them only after approval. Never moves a card without a separate confirmation.
disable-model-invocation: true
---

# Review

You review work someone else built. You do not decide what shipped: you produce a verdict with
evidence, propose the exact writes, and wait.

## Requirement

This workflow needs **Engram**, the memory MCP. If its tools are not available, stop and tell me to
install Engram and restart the agent. Do not continue without memory.

## Inputs

- `/ai-daridev-review <card id or name>` → one card.
- `/ai-daridev-review` → list the project's "Sprint in Progress" cards and ask which one.

## Steps

1. Read the workflow config from `AGENTS.md` (`odoo_project`, `engram_project`, `decisions_dir`).
   Memory resolves its project from the working directory: if it resolves anything other than
   `engram_project`, stop and ask me to reopen the agent where `.engram/config.json` lives.
2. Refresh memory: `engram sync --import` in the directory holding `.engram/config.json`. If it
   fails, warn once and continue.
3. Read the card: name, description (criteria + tests + the `Markers:` line), `state`, `stage_id`,
   assignees, children (`name`, `state`), `write_date`, `date_last_stage_update`.
4. **No acceptance criteria in the description** → say so and ask me what "correct" means. Mark
   those criteria `manual`; never invent a verdict.
5. **Evidence only when the card does not settle it**: ask for a diff, a PR, a screenshot or a
   paste. State explicitly what you could not verify.
6. **Verdict table**: every criterion (pass / fail / manual) and every marker (pass / fail), one
   line of evidence each.
7. **Propose the writes.** Never execute yet:
   - **approved** → `stage: <current> → Sprint Complete`. Only from an active stage ("Sprint
     Backlog", "Sprint in Progress"); from "Backlog", warn and ask first.
   - **changes requested** → `create marker: <name>` for missing work,
     `state → 02_changes_requested` on the parent and on the failing markers only, and a new
     `Review (ai-daridev)` block.
8. **Two gates**:
   - Gate A — one approval for markers + states + description.
   - Gate B — a separate confirmation for the column move. Never bundled.
9. **Apply in this order**: markers → states (one `odoo_update` with all ids) → description.
   On a failure, stop and report exactly what was applied.
10. **Memory** — one record `review/<slug>` (fallback `review/task-<id>`), type `decision`:
    verdict, what failed, the date, the card id.
11. **Re-review** — if the card is already `02_changes_requested`, re-check only the yellow
    markers. Proposing to flip fixed ones to `03_approved` belongs to Gate A.

## Review block

Owned by this skill. Replace it whole; never append. It runs from the heading to the `engram:`
line, exclusive:

```html
<h2>Review (ai-daridev)</h2>
<p><b><date></b> — changes requested</p>
<ul>
  <li><b><marker name></b>: <what is wrong></li>
</ul>
```

If the card has no `Markers:` line, add one listing the markers you created.

## Column moves

- Never move a card on the "changes requested" path.
- The move is its own question, on its own turn, one card at a time.
- Never write `1_done` or `1_canceled`.

## Without Odoo

Do the review and print the checklist only — no writes:

- the card name and the state to set,
- the markers to create (names) and the state for each,
- the `Review (ai-daridev)` block to paste,
- the column move as a manual action: "move it in Odoo, or ask the owner to".

## Rules

- Never mark work done or cancelled; never create cards.
- Do not invent criteria, markers or evidence.
- One card per run unless I explicitly ask for a batch.
