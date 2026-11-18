---
name: daridev-pair
description: Executes an approved plan one step at a time — check red, minimum code, check green, screenshot on the card — and stops on anything unplanned. Never reviews, never archives, never commits.
disable-model-invocation: true
---

# Pair

You drive, I navigate. One step at a time; stop only when the plan runs out.

**Mode first.** The literal first line, nothing before it:
`Odoo: on · <project> · card #<id> "<name>"` or `Odoo: off · chat-only`.
A card, slug or flag decides; with nothing it is off and you do not ask.

Before the first write, read `../daridev-odoo/SKILL.md`: it owns the root memory and, on Odoo,
mode, stages, moves, assignees and the evidence upload. Never restate it.

## Open

- Card via MCP, or the brief pasted, or the plan already approved in this conversation. No plan →
  propose one with `/daridev-plan`'s rules, one gate, continue.
- Worktree: in the canonical checkout, ask `Worktree or current branch? [worktree]` before p1 and
  follow the `AGENTS.md` worktree block — it owns when to ask and what follows.
- On: read `depend_on_ids` first. A blocker not `1_done` outside Cancelled stops the run with one
  line and what unblocks it. Then move the card to the in-progress column (one write, reported, not
  asked; skip when already there, in the validated column, Cancelled or `1_done`). Checklist = the
  `Steps` block of the description; the subtasks supply only `state`, by `sequence`, and the block's
  `check:` line is what step 1 runs. No `Steps` block → legacy card: read the subtask names and
  descriptions, and say so once.
- Off: the checklist is the approved steps in the conversation.

## Per step — no stop

1. Write the check named in the plan.
2. Show it fail.
3. Minimum code to pass.
4. Show it pass.
5. Visual step → before the first one, ask once
   `Screenshots from prod, staging or local? [prod]` (default prod when deployed, local when not)
   and keep it. Capture on that surface at 1600×1000, mask client data, save under
   `docs/records/evidence/<date>-<slug>/pN-<step>.png`. With MCP: attach it to the card, append the
   gallery entry to `Evidence (daridev)` (create the heading only when missing, after `Review` and
   before the slug), and verify the attachment row on the card and the gallery entry before
   flipping. Without MCP: print the handoff label and the upload instruction (see Close).
   Non-visual → one `<code>` line under the label.
6. Flip the subtask to `1_done` (on) and report.
7. `Plan 4/7 · next p5 "<step>" ([agent|you])`.

Stop immediately on: a design decision not in the plan; adding something not asked; a change that
needs a test changed, skipped or deleted; two attempts without green; >50 lines or >3 files. A
missing or wrong check is a plan change — stop and ask.

## Close (only when every step is green and I say yes)

- List open steps: flip, leave the card open, or drop (`1_canceled` + ` (dropped)`, never deleted).
- Propose one sentence for `docs/records/spec.md` under `## <domain>` when behaviour changed.
- Print the handoff: what shipped, the spec line, the card state, the step summary,
  `worktree: removed|kept <path>`, and the commit message for me to run.
- **No MCP:** print one block per step, in order, each with its local path and label, plus the
  upload instruction:

  ```
  Open the screenshot and confirm it shows the step. If it does, open the card in Odoo,
  add each label under Evidence (daridev), and paste its image under it. If you cannot
  edit the card, send the files to the reviewer.

  p5 "<step>" — [agent] · local — not deployed
     docs/records/evidence/<date>-<slug>/p5-<step>.png
  ```

  A non-visual step prints the same label and the `<code>` line to paste.

## Never

Review yourself, archive, mark green, commit, write `log.md`, rewrite the description, write a
subtask description, add what the plan does not name. Never print a bare id.
