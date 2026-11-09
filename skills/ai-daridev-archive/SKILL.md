---
name: ai-daridev-archive
description: Closes a finished story or sprint. Gates on the validated column and the green dot, marks the card done (`1_done`) so Odoo frees its dependents, and appends the retro to docs/ai-daridev/log.md. Never moves cards, never turns one green.
disable-model-invocation: true
---

# Archive

Close work that is already finished. The card and the files are the record; never invent a retro.

## Inputs

- `/ai-daridev-archive <slug>` → that story. It must be in `odoo_stage_done` and green
  (`03_approved`); the gate stops if it is not.
- Bare → green cards in `odoo_stage_done` that are not yet in `docs/ai-daridev/log.md`; ask one,
  all, or cancel. "All" means every green card; a gray card is listed with the reason and skipped.
  Never assume "all". No `odoo_stage_done` → bare mode needs a slug or a pasted story; with a slug,
  the gate asks once for the validated column. No Odoo → require a slug or a pasted story.

## Steps

1. **Load and gate.** Read the card (`name`, `stage_id`, `state`, children, `depend_on_ids`,
   `dependent_ids`, `date_end`, `write_date`), `docs/ai-daridev/spec.md` and `decisions.md`. Also
   flag, without fixing: a decision that contradicts the description (quote both) and a behavior
   change with no spec entry. Stop and list what is wrong when the stage is not `odoo_stage_done`
   (no key → ask once which column means validated, use it for the session), the state is not
   `03_approved` or `1_done`, or a child is not `1_done`/`1_canceled`. A gray card (`01_in_progress`)
   in the validated column gets one line: review it, or ask me for the green dot — archive never
   turns a card green. Read the latest dated attempt in each `1_done` child's description and its
   `attachment_ids`: `screenshot`/`file` ids must resolve to an `ir.attachment` with
   `res_model=project.task`, `res_id=<child>`, a non-empty `mimetype` and `file_size > 0`; a `code`
   `<li>` needs a non-empty `<pre><code>`; a `waiver` needs the reason, who and date. A child with
   neither is drift, not a stop: list it for the gate and archive continues on my yes. A `1_canceled`
   child (dropped) needs no evidence. A `1_done` card in `odoo_stage_done` skips the write and only
   logs.
2. **Show the gate.** List the exact writes (`state=1_done`, `date_end` only if empty), the
   dependents this frees and the ones still blocked by another card, and the reminder to run it only
   after the commit is on the main branch. With drift, add one line per unproven `1_done` child:
   what it needs (screenshot, code, file or waiver) and the two routes — record it first, or cancel it
   by hand if it never happened; archive does neither. When the card was self-closed and never
   reviewed, recommend `/ai-daridev-review` before archiving. Wait for my yes; with drift only
   `archive anyway` counts, and that yes is the waiver for the retro.
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
Drift: <decision and spec drift, then "no evidence on <ids>", or "none">
```

5. **Append** the block to `docs/ai-daridev/log.md` unless the slug is already there. Create the file
   with `# Log` if needed. If the slug is already there, append nothing; the state write from the
   apply step has already run, and any drift is reported.
6. Follow-ups are listed, never turned into cards.

## Rules

- Archive never writes `stage_id`: the card is already green in `odoo_stage_done`. Never set
  `1_canceled`. Archive is the only skill that writes a **card** `1_done`, and only after the gate.
- **Evidence is mandatory in pair and review, advisory here.** Archive never refuses a `1_done` step
  for a missing artifact and never fixes it — descriptions, waivers and drops belong to pair and
  review; it only names the step in the gate and in the retro.
- Read `docs/ai-daridev/spec.md` and `decisions.md` first; the retro quotes them, it does not
  reinvent them.

## Always

- **Root.** Walk up from the current directory to the nearest `AGENTS.md` that holds
  `<!-- ai-daridev:start -->`. That directory is the root: read and write `docs/ai-daridev/` there
  and write nothing outside it. No block → ask once: create it here, use the git root, or chat-only.
- **Config.** Read `odoo_project`, `odoo_stage_done` and `card_tag` from the block. No
  `odoo_project` → Odoo is off. Resolve the project, the tags and the stages by exact name; 0 or 2+
  matches → stop and list the real ones. Backlog stage = lowest `sequence`. Default tag `backend`.
- **Moves and assignees are proposed, not assumed.** Move a card only when I ask in this turn, when
  the phase gate lists it and I say yes, or when the column and the state already disagree and I
  approve the repair. Show the exact write in the gate; never move silently.
- **A move is one write.** `stage_id`, `state` and `date_end` in the same `odoo_update`:
  → `odoo_stage_done` = `03_approved` + `date_end`; → an active stage = `01_in_progress`; → the
  backlog stage = `01_in_progress` (explicit reopen only); → the Cancelled stage = `1_canceled`
  (I confirm; dependents stay blocked). Never move a subtask or an archived (`1_done`) card.
- **Assignees need a name.** `user_ids` only when I name the person; resolve the exact `res.users`
  name or login, 0 or 2+ matches → stop and list.
- **Agents write:** archive writes `state=1_done` and `date_end` (only when empty); the description,
  subtask states, `state=03_approved` and `state=02_changes_requested` belong to the other skills.
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
