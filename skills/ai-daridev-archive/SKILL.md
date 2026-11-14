---
name: ai-daridev-archive
description: Closes a finished story or sprint. With Odoo on it gates on the validated column and the green dot, marks the card done (`1_done`) so Odoo frees its dependents, and appends the retro to docs/ai-daridev/log.md; with Odoo off it appends the retro from the session. Never moves cards, never turns one green.
disable-model-invocation: true
---

# Archive

Close work that is already finished. The card and the files are the record; never invent a retro.

## Inputs

- `/ai-daridev-archive <slug>` → that story. On Odoo it must be in `odoo_stage_done` and green
  (`03_approved`); the gate stops if it is not.
- Bare → green cards in `odoo_stage_done` that are not yet in `docs/ai-daridev/log.md`; ask one,
  all, or cancel. "All" means every green card; a gray card is listed with the reason and skipped.
  Never assume "all". No `odoo_stage_done` → bare mode needs a slug or a pasted story; with a slug,
  the gate asks once for the validated column.
- **Odoo off** → a slug or the story pasted in this turn is enough. There is no card and no column to
  gate, so the retro is built from the session and step 2 collapses to showing the block.

## Steps

1. **Load and gate.** On Odoo, read the card (`name`, `stage_id`, `state`, children, `depend_on_ids`,
   `dependent_ids`, `date_end`, `write_date`); off, there is no card and the story comes from this
   session. Read `docs/ai-daridev/spec.md` and `decisions.md` either way. Also
   flag, without fixing: a decision that contradicts the description (quote both) and a behavior
   change with no spec entry. On Odoo, stop and list what is wrong when the stage is not
   `odoo_stage_done`
   (no key → ask once which column means validated, use it for the session), the state is not
   `03_approved` or `1_done`, or a child is not `1_done`/`1_canceled`. A gray card (`01_in_progress`)
   in the validated column gets one line: review it, or ask me for the green dot — archive never
   turns a card green. Read each `1_done` step's entry in the card's `<h2>Evidence (ai-daridev)</h2>`
   — match `pN "<step>"` — and resolve every `<img src="/web/image/{id}">` id to an `ir.attachment`
   with `res_model=project.task`, `res_id=<card>`, `mimetype=image/*` when labelled a screenshot, and
   `file_size > 0`; a `code` line needs non-empty text; a `waiver` needs the reason, who and date. A
   card with no tail at all (legacy) falls back to the child description and the child's
   `attachment_ids`. A step with neither is drift, not a stop: list it for the gate and archive
   continues on my yes. A `1_canceled` child (dropped) needs no evidence. A `1_done` card in
   `odoo_stage_done` skips the write and only logs.
2. **Show the gate.** List the exact writes (`state=1_done`, `date_end` only if empty), the
   dependents this frees and the ones still blocked by another card, and the reminder to run it only
   after the commit is on the main branch. With drift, add one line per unproven `1_done` step:
   what it needs (an embedded screenshot, a code line or a waiver) and the two routes — record it
   first, or cancel it by hand if it never happened; archive does neither. When the card was
   self-closed and never reviewed, recommend `/ai-daridev-review` before archiving. Wait for my yes;
   with drift only
   `archive anyway` counts, and that yes is the waiver for the retro. With no card, show the retro
   block and skip the writes — there is nothing to gate.
3. **Apply.** On Odoo, set `state=1_done` (and `date_end` if empty), re-read, and confirm; if it fails,
   stop before the log. With no card, skip to the retro.
4. **Print the retro**:

```
## <slug> — shipped <date>
Shipped: <one or two lines>
Decisions: <dated, each with its Why>
Follow-ups: <or "none">
Plan: <done>/<total> steps · dropped <n> · open 0
Card: task <id> · state 1_done · end <date_end or date_last_stage_update>
Card: none (chat-only)          <!-- Odoo off: replaces the line above -->
Drift: <decision and spec drift, then "no evidence on p4", or "none">
```

5. **Append** the block to `docs/ai-daridev/log.md` unless the slug is already there. Create the file
   with `# Log` if needed. If the slug is already there, append nothing; the state write from the
   apply step has already run, and any drift is reported.
6. Follow-ups are listed, never turned into cards.

## Rules

- Archive never writes `stage_id`: the card is already green in `odoo_stage_done`. Never set
  `1_canceled`. Archive is the only skill that writes a **card** `1_done` or `log.md`, and only
  after the gate.
- **Evidence is mandatory in pair and review, advisory here.** Archive never refuses a `1_done` step
  for a missing entry and never fixes it — the card's `Evidence` tail, waivers and drops belong to
  pair and review; it only names the step in the gate and in the retro.
- **A cardless run gates nothing.** Odoo off → no stage, no evidence check, no dependents: the retro
  is the record and `log.md` is the only write.
- Read `docs/ai-daridev/spec.md` and `decisions.md` first; the retro quotes them, it does not
  reinvent them.

## Always

- **Root.** Walk up from the current directory to the nearest `AGENTS.md` that holds
  `<!-- ai-daridev:start -->`. That directory is the root: read and write `docs/ai-daridev/` there
  and write nothing outside it. No block → ask once: create it here, use the git root, or chat-only.
- **Mode.** Cards only when this session is on Odoo, and the first line says which. A card in the
  invocation means on; `--odoo`/`--no-odoo` or my words beat that; bare archive lists cards, so it is
  on, and off needs a slug or a pasted story.
- **Odoo contract.** On → read `../ai-daridev-odoo/SKILL.md` and follow it for every Odoo rule:
  config, project and stages, moves, assignees, who writes what and the evidence upload. Never restate
  those rules here.
- **One approval gate per phase.** The done write and the log are one gate; nothing else asks.
- **Decisions** → one append to `docs/ai-daridev/decisions.md`, only when project-wide, hard to
  reverse or a shared/ops contract. Everything else stays in the conversation.
- **Fold-in.** If `docs/ai-daridev/` is missing and `docs/decisions/*.md` or `openspec/` exists, ask
  once to fold them into `decisions.md` and `spec.md`; the originals stay as frozen history.
- **Never commit.** Never write secrets or client data into the three files.
