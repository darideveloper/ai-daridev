---
name: ai-daridev-review
description: Reviews someone else's card against its acceptance criteria and checklist, applies the verdict after one gate, and moves the card between stages only with my approval.
disable-model-invocation: true
---

# Review

You review work someone else built. You produce a verdict with evidence and propose the writes; I
decide. One card per run unless I ask for a batch.

## Steps

1. **Load the card** by id or name. No argument → list the active-stage cards (not the backlog
   stage, not `odoo_stage_done`), limit 20, and ask which one. Odoo off, ask me to paste it.
2. **Read it:** name, description sections (including the `Evidence` tail), `state`, children,
   `write_date`, `attachment_ids`. No
   acceptance criteria in the description → say so and ask me what "correct" means; never invent a
   verdict.
3. **Evidence only when the card does not settle it.** Ask me for a diff, PR, screenshot or paste, and
   state what you could not verify. Never capture it yourself.
4. **Verdict table:** every criterion (pass / fail / manual) and every step (pass / fail / not
   reached), one evidence line each. A step passes only when every test covering it is green and its
   evidence is valid. Read the step's latest entry in the card's `<h2>Evidence (ai-daridev)</h2>` —
   match `pN "<step>"` — and resolve every `<img src="/web/image/{id}">` id to an `ir.attachment` with
   `res_model=project.task`, `res_id=<this card>`, `mimetype=image/*` when it is labelled a
   screenshot, and `file_size > 0`; a `code` line needs non-empty text; a `waiver` needs the reason,
   who and date. A `1_done` step with no entry in the tail is a fail, even when the test passed. A
   card with no tail at all (legacy) falls back to the latest dated attempt in the child description
   and the child's `attachment_ids` with `res_id=<subtask>`.
5. **Propose the writes**, then one gate:
   - Approved → one `odoo_update` sets `state=03_approved` + `date_end` (the green dot) and moves
     the card `<current> → <odoo_stage_done>`, so it lands validated; archiving is a separate step I
     run later. A step that is not `1_done`/`1_canceled` blocks the green dot: list it instead of
     approving. The move is a normal part of the gate — if I say "don't move", write the green dot
     alone.
   - Changes requested → the failing steps and the card to `state=02_changes_requested`, plus the
     review block. If the card is in `odoo_stage_done`, the same write moves it back to the
     in-progress column — the single stage inside the project whose name matches `in progress`
     (case-insensitive), asked once in the gate when 0 or 2+ match — or leaves the column alone when
     I say so; from a later stage, stop and report. If work is missing, propose new steps (name,
     detail) and create them as hidden subtasks like `/ai-daridev-story` does, in the same gate. A
     criterion you cannot verify becomes a `[you]` step with its detail, never a bare verdict: the
     card is only handed over when a step stands behind it.
   - Both branches reconcile the card's assignees from the next open step in the rendered
     checklist, new steps included: `[[4, <manual>]]` or `[[3, <manual>]]`, plus `[[4, <agent>]]`
     when it is missing.
6. **Apply** after the gate: any new `[you]` step first, so the card never points at a step that is
   not there yet → the card write (one `odoo_update`: `state` + `date_end` + `stage_id` +
   the assignee diff) → the other new steps → their states (one `odoo_update` with all the ids) →
   the review section. Re-read `write_date` first; if it changed, show the difference and re-apply.
7. Print the verdict and the checklist with the review states. Stop here: archiving is my next move,
   not yours, so never prompt for it or write `docs/ai-daridev/log.md`.

## Review block

Owned by this skill. Replace the whole `<h2>Review (ai-daridev)</h2>` section; never append, never
touch anything else in the description. It lives above the slug line — replace it in place, or insert
it immediately before `<p><em>ai-daridev: story/{slug}</em></p>`; never inside or after the `Evidence`
tail.

```html
<h2>Review (ai-daridev)</h2>
<p><b><date></b> — changes requested</p>
<ul>
  <li><b>p3 "<step>"</b>: <what is wrong></li>
</ul>
```

## Rules

- **Never captures.** Review reads evidence; it never drives the browser, never takes a screenshot,
  never uploads, and never writes the `Evidence` tail. A `1_done` step with no valid entry is a fail;
  the fix is `/ai-daridev-pair` recording it, not review filling it in.
- **Move only through the gate.** The two moves in step 5 are the only `stage_id` writes, and each
  lands in the same `odoo_update` as its `state`. Never move silently, never create cards, never mark
  work done or cancelled.
- The evidence check reads the attachment record and the description; it never fetches `/web/image`.
- Re-review only the yellow steps; proposing to flip the fixed ones is part of the gate.
- No plan mirror, no `Plan:` line.

## Always

- **Root.** Walk up from the current directory to the nearest `AGENTS.md` that holds
  `<!-- ai-daridev:start -->`. That directory is the root: read and write `docs/ai-daridev/` there
  and write nothing outside it. No block → ask once: create it here, use the git root, or chat-only.
- **Mode.** The first line reports it. A card in the invocation means on; `--odoo`/`--no-odoo` or my
  words beat that; bare review lists cards, so it is on, and off needs a pasted card.
- **Odoo contract.** On → read `../ai-daridev-odoo/SKILL.md` and follow it for every Odoo rule:
  config, project and stages, moves, assignees, who writes what and the evidence upload. Never restate
  those rules here.
- **One approval gate per phase.** Structure and the card write ask once; the rest is reported, not
  asked.
- **Decisions** → one append to `docs/ai-daridev/decisions.md`, only when project-wide, hard to
  reverse or a shared/ops contract. Everything else stays in the conversation.
- **Fold-in.** If `docs/ai-daridev/` is missing and `docs/decisions/*.md` or `openspec/` exists, ask
  once to fold them into `decisions.md` and `spec.md`; the originals stay as frozen history.
- **Never commit.** Never write secrets or client data into the three files.
- Never write or offer `docs/ai-daridev/log.md`: the retro belongs to `/ai-daridev-archive`.
