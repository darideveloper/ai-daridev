---
name: daridev-review
description: Reviews someone else's card by running the Done-when probes as the lowest-privilege actor, writes one Review block and applies the verdict after one gate. Never captures evidence.
disable-model-invocation: true
---

# Review

You review work someone else built. Evidence, then a verdict; I decide.

**Mode first.** A card means on; `--no-odoo` or my words beat it; bare review lists cards, so on;
off needs a pasted card. Report it as the literal first line, nothing before it:
`Odoo: on · <project> · card #<id> "<name>"` or `Odoo: off · chat-only`.

On Odoo, read `../daridev-odoo/SKILL.md` before the first write: it owns mode, stages, moves,
assignees and the description zones. Never restate it.

## Steps

1. Load the card by id or name; no argument → list active cards (not backlog, not validated),
   limit 20, ask. Off → ask for the paste.
2. Read the brief, the steps and their states, `write_date`. No `Done when` → say so and ask what
   correct means; never invent a verdict.
3. **Surface.** Ask once: `Probe against prod or local? [prod]`. Prod → the probes are the prod
   proof. Local or not deployed → record `surface: local — prod unproven`; the verdict may still
   pass and green the card, and the block names the surface. Never FAIL for a missing deploy.
   Invoked by a campaign → prod, never ask.
4. **Probe** every `Done when` line as the lowest-privilege actor it names. For a gate, permission,
   limit or export, enumerate the sibling surfaces (each export, bulk action, list, detail,
   autocomplete, API). Record actor + probe + result. A claim you cannot prove is FAIL, never PASS,
   except the not-deployed case above.
5. **Gallery.** Each visual step has a label that matches a subtask (`pN "<step>"`) and an image
   that resolves (`/web/image/{id}` plus the attachment on the card or the subtask, `image/*`,
   `file_size > 0`). A missing or mismatched entry is a finding; never upload or capture.
6. Verdict table: each Done-when pass/fail/manual, each step pass/fail/not reached, one evidence
   line each. Screenshots are not graded; the probe is.
7. **Gate.** Show the verdict and the exact writes.
   - Pass → flip every step that passed to `1_done` (one update), then one card update
     (`03_approved`, `date_end`, validated column, assignee diff) plus the `Review` block. A step
     that is not `1_done`/`1_canceled` blocks the green dot: list it instead of approving.
   - Fail → one card update (`state=02_changes_requested` + move to **In Progress** from Backlog,
     Sprint Backlog, In Progress or Sprint Complete); stop from a later stage. Then the `Review`
     block, the failing steps to `02_changes_requested`, and missing work as new subtasks created
     with `state=02_changes_requested` (yellow).
8. Apply, then print the verdict and the checklist states. Stop: archiving is my next move.

Self mode is allowed; the block says `self-reviewed`.

## Review block

```html
<h2>Review (daridev)</h2>
<p><b>2026-11-17</b> — pass · prod</p>
<ul>
  <li><b>{area}</b>: {actor} {probe} → {result}</li>
</ul>
```

Replace the whole section; insert it before the slug line; never touch the rest. When the probe ran
locally, the line reads `pass · local — prod unproven`; the green dot is set and the surface is
recorded.

## Never

Capture a screenshot, upload, write outside its section, create a card, archive, write `log.md`,
invent a verdict, grade an attachment.
