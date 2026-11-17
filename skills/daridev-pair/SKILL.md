---
name: daridev-pair
description: Executes an approved plan one step at a time — check red, minimum code, check green, screenshot on the step's subtask — and stops on anything unplanned. Never reviews, never archives, never commits.
disable-model-invocation: true
---

# Pair

You drive, I navigate. One step at a time; stop only when the plan runs out.

**Mode first.** The literal first line, nothing before it:
`Odoo: on · <project> · card #<id> "<name>"` or `Odoo: off · chat-only`.
A card, slug or flag decides; with nothing it is off and you do not ask.

On Odoo, read `../daridev-odoo/SKILL.md` before the first write: it owns mode, stages, moves,
assignees and the evidence upload. Never restate it.

## Open

- Card via MCP, or the brief pasted, or the plan already approved in this conversation. No plan →
  propose one with `/daridev-plan`'s rules, one gate, continue.
- On: read `depend_on_ids` first. A blocker not `1_done` outside Cancelled stops the run with one
  line and what unblocks it. Then move the card to the in-progress column (one write, reported, not
  asked; skip when already there, in the validated column, Cancelled or `1_done`). Checklist = the
  subtasks by `sequence`, fallback to the brief's `Steps:`.
- Off: the checklist is the approved steps in the conversation.

## Per step — no stop

1. Write the check named in the plan.
2. Show it fail.
3. Minimum code to pass.
4. Show it pass.
5. Visual step → screenshot the shipped surface, resize 1600×1000, mask client data, local copy
   under `docs/records/evidence/<date>-<slug>/pN-<step>.png`, attach it to that step's subtask.
   Non-visual → nothing extra.
6. Flip the subtask to `1_done` (on) and report.
7. `Plan 4/7 · next p5 "<step>" ([agent|you])`.

Stop immediately on: a design decision not in the plan; adding something not asked; a change that
needs a test changed, skipped or deleted; two attempts without green; >50 lines or >3 files. A
missing or wrong check is a plan change — stop and ask.

## Close (only when every step is green and I say yes)

- List open steps: flip, leave the card open, or drop (`1_canceled` + ` (dropped)`, never deleted).
- Propose one sentence for `docs/records/spec.md` under `## <domain>` when behaviour changed.
- Print the handoff: what shipped, the spec line, the card state, the step summary, and the commit
  message for me to run.

## Never

Review yourself, archive, mark green, commit, write `log.md`, rewrite the description, change a
subtask description after creation, add what the plan does not name. Never print a bare id.
