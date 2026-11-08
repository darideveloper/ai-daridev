---
name: ai-daridev-archive
description: Closes a finished story or sprint. Gates on the validated column, marks the card done (`1_done`) so Odoo frees its dependents, and appends the retro to docs/ai-daridev/log.md. Never moves cards, never cancels.
disable-model-invocation: true
---

# Archive

Close work that is already finished. The card and the files are the record; never invent a retro.

## Inputs

- `/ai-daridev-archive <slug>` → that story. It must be in `odoo_stage_done`; the gate stops if it
  is not.
- Bare → cards in `odoo_stage_done` that are not yet in `docs/ai-daridev/log.md`; ask one, all, or
  cancel. Never assume "all". No `odoo_stage_done` → bare mode needs a slug or a pasted story; with
  a slug, the gate asks once for the validated column. No Odoo → require a slug or a pasted story.

## Steps

1. **Load and gate.** Read the card (`name`, `stage_id`, `state`, children, `depend_on_ids`,
   `dependent_ids`, `date_end`, `write_date`), `docs/ai-daridev/spec.md` and `decisions.md`. Also
   flag, without fixing: a decision that contradicts the description (quote both) and a behavior
   change with no spec entry. Stop and list what is wrong when the stage is not `odoo_stage_done`
   (no key → ask once which column means validated, use it for the session), the state is
   `02_changes_requested`, `04_waiting_normal` or `1_canceled`, or a child is not
   `1_done`/`1_canceled`. Read each `1_done` child's description and `attachment_ids`: a valid
   attempt has an artifact `<li>` or a `waiver` with reason, who and date; `screenshot`/`file` ids
   must resolve. A child with neither stops the archive and is listed; a `1_canceled` child
   (dropped) needs no evidence. Accept `03_approved` (green) and `01_in_progress` (gray) as
   validated; a `1_done` card in `odoo_stage_done` skips the write and only logs.
2. **Show the gate.** List the exact writes (`state=1_done`, `date_end` only if empty), the
   dependents this frees and the ones still blocked by another card, and the reminder to run it only
   after the commit is on the main branch. Wait for my yes.
3. **Apply.** Set `state=1_done` (and `date_end` if empty), re-read, and confirm; if it fails, stop
   before the log.
4. **Print the retro**:

```
## <slug> — shipped <date>
Shipped: <one or two lines>
Decisions: <dated, each with its Why>
Follow-ups: <or "none">
Plan: <done>/<total> steps · dropped <n> · open 0
Card: task <id> · state 1_done · end <date_end or date_last_stage_update>
Drift: <or "none">
```

5. **Append** the block to `docs/ai-daridev/log.md` unless the slug is already there. Create the file
   with `# Log` if needed. If the slug is already there, append nothing; the state write from the
   apply step has already run, and any drift is reported.
6. Follow-ups are listed, never turned into cards.

## Rules

- Never move a card, never write `stage_id`, never set `1_canceled`. Archive is the only skill that
  writes a **card** `1_done`, and only after the gate.
- Read `docs/ai-daridev/spec.md` and `decisions.md` first; the retro quotes them, it does not
  reinvent them.

## Always

- **Root.** Walk up from the current directory to the nearest `AGENTS.md` that holds
  `<!-- ai-daridev:start -->`. That directory is the root: read and write `docs/ai-daridev/` there
  and write nothing outside it. No block → ask once: create it here, use the git root, or chat-only.
- **Config.** Read `odoo_project`, `odoo_stage_done` and `card_tag` from the block. No
  `odoo_project` → Odoo is off. Resolve the project, the tags and the stages by exact name; 0 or 2+
  matches → stop and list the real ones. Backlog stage = lowest `sequence`. Default tag `backend`.
- **Never move a card** between stages, never set a card `1_canceled`, never assign. Archive writes
  `state=1_done` and `date_end` (only when empty); the description, subtask states,
  `state=03_approved` and `state=02_changes_requested` belong to the other skills.
- **One approval gate per phase.** The done write and the log are one gate; nothing else asks.
- **Odoo unavailable** → print the close checklist (`1_done`, the date, the dependents it would
  free) and write only the files; I set done by hand.
- **Decisions** → one append to `docs/ai-daridev/decisions.md`, only when project-wide, hard to
  reverse or a shared/ops contract. Everything else stays in the conversation.
- **Fold-in.** If `docs/ai-daridev/` is missing and `docs/decisions/*.md` or `openspec/` exists, ask
  once to fold them into `decisions.md` and `spec.md`; the originals stay as frozen history.
- **Never commit.** Never write secrets or client data into the three files.
- **Cards** are found by `<p><em>ai-daridev: story/<slug></em></p>`; the legacy
  `engram: story/<slug>` is accepted on read.
