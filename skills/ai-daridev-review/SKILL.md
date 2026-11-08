---
name: ai-daridev-review
description: Reviews someone else's card against its acceptance criteria and checklist, proposes the writes, and applies them after one gate. Never moves a card.
disable-model-invocation: true
---

# Review

You review work someone else built. You produce a verdict with evidence and propose the writes; I
decide. One card per run unless I ask for a batch.

## Steps

1. **Load the card** by id or name. No argument → list the active-stage cards (not the backlog
   stage, not `odoo_stage_done`), limit 20, and ask which one. Without Odoo, ask me to paste it.
2. **Read it:** name, description sections, `state`, children, `write_date`. No acceptance criteria
   in the description → say so and ask me what "correct" means; never invent a verdict.
3. **Evidence only when the card does not settle it.** Ask for a diff, PR, screenshot or paste, and
   state what you could not verify.
4. **Verdict table:** every criterion (pass / fail / manual) and every step (pass / fail / not
   reached), one evidence line each. A step passes only when every test covering it is green or the
   verification is shown.
5. **Propose the writes**, then one gate:
   - Approved → print the column move as **my** action (`<current> → <odoo_stage_done>`) and list
     any step that is not `1_done`. Never write `stage_id`.
   - Changes requested → the failing steps and the card to `state=02_changes_requested`, plus the
     review block. If work is missing, propose new steps (name, detail) and create them as hidden
     subtasks like `/ai-daridev-story` does, in the same gate.
6. **Apply** after the gate: new steps → states (one `odoo_update` with all the ids) → the review
   section. Re-read `write_date` first; if it changed, show the difference and re-apply.
7. Print the verdict and the checklist with the review states.

## Review block

Owned by this skill. Replace the whole `<h2>Review (ai-daridev)</h2>` section; never append, never
touch anything else in the description.

```html
<h2>Review (ai-daridev)</h2>
<p><b><date></b> — changes requested</p>
<ul>
  <li><b>p3 · <step name></b>: <what is wrong></li>
</ul>
```

## Rules

- **Never move a card**, never write `stage_id`, never create cards, never mark work done or
  cancelled. The column is mine.
- Re-review only the yellow steps; proposing to flip the fixed ones is part of the gate.
- No plan mirror, no `Plan:` line.

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
