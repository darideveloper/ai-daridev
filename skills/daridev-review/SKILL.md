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

Before the first write, read `../daridev-odoo/SKILL.md`: it owns the root memory and, on Odoo,
mode, stages, moves, assignees, the subtasks and the description zones. Never restate it.

## Steps

1. Load the card by id or name; no argument → list active cards (not backlog, not validated),
   limit 20, ask. Off → ask for the paste.
2. Read the brief, its `Steps`, and the subtask states, `write_date`. No `Steps` → legacy card:
   read the subtask names and descriptions. No `Done when` → say so and ask what correct means;
   never invent a verdict.
3. **Surface.** Ask once with the question tool (`../daridev-odoo/SKILL.md` §Ask):
   `Probe against prod or local? [prod]`. Prod → the probes are the prod
   proof. Local or not deployed → record `surface: local — prod unproven`; the verdict may still
   pass and green the card, and the block names the surface. Never FAIL for a missing deploy.
   Invoked by a campaign → the surface the campaign fixed, never ask.
4. **Probe** every `Done when` line as the lowest-privilege actor it names. For a gate, permission,
   limit or export, enumerate the sibling surfaces (each export, bulk action, list, detail,
   autocomplete, API). Record actor + probe + result. A claim you cannot prove is FAIL, never PASS,
   except the not-deployed case above.
5. **Gallery.** Each visual step has a label matching its step in `Steps` and its subtask
   (`pN "<step>"`); the subtask is only the tracker, the image lives on the card. The image
   resolves (`/web/image/{id}` with an `ir.attachment` on the card, `image/*`, `file_size > 0`; a
   legacy attachment on the subtask is accepted). A missing or mismatched entry is a finding; never
   upload or capture.
6. Verdict table: each Done-when pass/fail/manual, each step pass/fail/not reached, one evidence
   line each. Screenshots are not graded; the probe is.
7. **Gate.** Show the verdict and the exact writes.
   - Pass → flip every step that passed to `1_done` (one update), then one card update
     (`03_approved`, `date_end`, validated column, assignee set) plus the `Review` block. A step
     that is not `1_done`/`1_canceled` blocks the green dot: list it instead of approving.
   - Fail → one card update (`state=02_changes_requested` + move to **In Progress** from Backlog,
     Sprint Backlog, In Progress or Sprint Complete); stop from a later stage. Then the `Review`
     block, the failing steps to `02_changes_requested`, and missing work appended to `Steps` **and**
     created as new subtasks with `state=02_changes_requested` (yellow).
8. Apply, then print the verdict and the checklist states: `- ☑ pN "<step>" — [agent|you]` for a
   passed/`1_done` step and `- ☐ pN "<step>" — [agent|you]` for a failed or not-reached one, each
   with the probe that proves it (its `check:` line or the Done-when probe) as `  - ☑`/`  - ☐`
   and the observed result. The verdict table stays a table. Stop: archiving is my next move.

Self mode is allowed; the block says `self-reviewed`.

## Review block

```html
<h2>Review (daridev)</h2>
<p><b>2026-11-17</b> — pass · prod</p>
<ul>
  <li><b>{area}</b>: {actor} {probe} → {result}</li>
</ul>
```

Replace the whole section; insert it before the slug line; never touch the rest. If the card carries
`Review (ai-daridev)`, replace that heading with `Review (daridev)` instead of adding a second
section. When the probe ran locally, the line reads `pass · local — prod unproven`; the green dot is
set and the surface is recorded.

## Never

Capture a screenshot, upload, write outside its section (except a step's line in `Steps`), create a
card, archive, write `log.md`, invent a verdict, grade an attachment.
