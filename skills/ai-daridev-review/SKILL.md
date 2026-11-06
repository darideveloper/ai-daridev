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
- `/ai-daridev-review` → list the cards in the **active stages** (`project_id` + `stage_id in
  stages.active`, `limit` from preflight, never unbounded) and ask which one. Mark the ones
  assigned to `uid` as yours; do not filter by it.

## Steps

1. **Preflight.** Run `ai-daridev preflight` in the repo root and use its JSON (`project`, `stages`,
`tags`, `uid`, `listing`, `markers`, `assignees`). If the command is missing, stop and say: run
`./scripts/setup.sh` from the ai-daridev repo. If it exits non-zero, print its `errors` and stop —
do not ask, do not guess, do not read `AGENTS.md` yourself. Print its `warnings` once, then continue.

2. Refresh memory: `engram sync --import` in the directory holding `.engram/config.json`. If it
   fails, warn once and continue.
   Tool names: OpenCode `odoo_odoo_update` / `engram_mem_save`, inside Code Mode (`execute`)
   `tools.odoo.odoo_update` / `tools.engram.mem_save`. Claude Code `mcp__odoo__*`, `mcp__engram__*`.
3. Read the card: name, description (criteria + tests + the `Markers:` line), `state`, `stage_id`,
   assignees, children (`name`, `state`), `write_date`, `date_last_stage_update`.
4. **No acceptance criteria in the description** → say so and ask me what "correct" means. Mark
   those criteria `manual`; never invent a verdict.
5. **Evidence only when the card does not settle it**: ask for a diff, a PR, a screenshot or a
   paste. State explicitly what you could not verify.
6. **Verdict table**: every criterion (pass / fail / manual) and every marker (pass / fail), one
   line of evidence each.
7. **Propose the writes.** Never execute yet:
   - **approved** → list any marker that is not `1_done` and ask before proposing the move, then
     `stage: <current> → <done stage>`. Only from an active stage (`stages.active`); from the
     backlog stage, warn and ask first.
   - **changes requested** → `create marker: <name>` for missing work — subtask with `parent_id`,
     `state=02_changes_requested`, `user_ids=[]`, **`display_in_project=False`** (never write
     `project_id`; Odoo computes it from the parent) and no `stage_id` — then
     `state → 02_changes_requested` on the parent and on the failing markers only, and a new
     `Review (ai-daridev)` block. Read a created marker back: `display_in_project` must be false.
8. **Two gates**:
   - Gate A — one approval for markers + states + description.
   - Gate B — a separate confirmation for the column move. Never bundled.
9. **Apply in this order**: markers → states (one `odoo_update` with all ids) → description.
   On a failure, stop and report exactly what was applied.
10. **Memory** — one `mem_save`: `topic_key review/<slug>` (fallback `review/task-<id>`), type
    `decision`, `title` = `review <slug>`, `content` = verdict, what failed, the date, the card id,
    in `**What** / **Why** / **Where** / **Learned**`. If it answers `judgment_required`, ask me
    once and resolve it with `mem_judge_many` (`candidates[].judgment_id`).
11. **Re-review** — if the card is already `02_changes_requested`, re-check only the yellow
    markers. Proposing to flip fixed ones to `1_done` belongs to Gate A.

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
- Markers are the only things that use `1_done`. The card is never set to Done or Canceled; approval
  is a column move, nothing else.

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
