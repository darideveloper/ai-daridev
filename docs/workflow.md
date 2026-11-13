# Workflow

Five phases, one story at a time. Each phase ends waiting for your approval. A card changes column
only when you ask or approve it, and always in one write that keeps the column and the state in sync.

## The rules that apply everywhere

- **Root.** The repo root is the nearest `AGENTS.md` holding `<!-- ai-daridev:start -->`, walking up
  from the current directory. `docs/ai-daridev/` is always relative to it; nothing is written above.
  No block → the skill asks once (create it here, use the git root, or chat-only).
- **Odoo is optional.** Without an `odoo_project` key there are no cards: stories live in the
  conversation and only the three files are written.
- **Moves and assignees are proposed, not assumed.** Move a card only when you ask in this turn,
  when the phase gate lists it and you say yes, or when the column and the state already disagree
  and you approve the repair. Show the exact write in the gate; never move silently.
- **A move is one write.** `stage_id`, `state` and `date_end` go in the same `odoo_update`:
  → `odoo_stage_done` = `03_approved` + `date_end`; → an active stage = `01_in_progress`; → the
  backlog stage = `01_in_progress` (explicit reopen only); → the Cancelled stage = `1_canceled`
  (you confirm first; dependents stay blocked). Never move a subtask or an archived (`1_done`)
  card, and never into `odoo_stage_done` unless every step is `1_done`/`1_canceled` and it turns
  green in the same write.
- **Assignees need a name.** Write `user_ids` only when you name the person; resolve the exact
  `res.users` name or login, 0 or 2+ matches → stop and list. Cards are created unassigned.
- **Who writes what.** Archive is the only skill that sets a **card** `1_done`, after its gate; no
  skill sets `1_canceled` on a visible card unless you ask or approve it, and dependents stay
  blocked. The agent writes the description (story), its `Evidence` tail (pair), subtask states,
  `state=03_approved` + `date_end` (close), `state=02_changes_requested` (review) and
  `state=1_done` (archive, on the card).
- **One gate per phase.** Structure changes, a column move and archive's done write ask once; the
  other state changes are reported.
- **Evidence.** Every `1_done` step has an entry in the card's `Evidence` section: a screenshot by
  default, one code line only when the proof is invisible in a browser, a waiver when there is
  nothing to show. Pair writes it and review refuses a step without it; archive names it as drift and
  archives anyway on your word. A file in the attachment list is not evidence.
- **Decisions only when they last.** Project-wide, hard to reverse or a shared/ops contract goes to
  `decisions.md`; everything else stays in the conversation.

## 1. Backlog

`/ai-daridev-backlog` splits the idea into ≤10 one-line stories:

```
1. As a visitor, I want to retry an upload, so that a flaky network doesn't lose my file.
2. As an operator, I want to see failed uploads, so that I can follow up. Requires: #1
```

Each story delivers value on its own and cuts through every layer. No technical stories, no
estimates. The first one is the walking skeleton. On approval the cards are created in the backlog
stage, unassigned unless you name someone, one tag each, no subtasks. A backward `Requires: #N` is
written as a real Odoo **Blocked By** link (`depend_on_ids`) in the create call itself, and a second
pass covers forward references; the clause never stays in the name or description.

## 2. Story

`/ai-daridev-story` refines exactly one story. It reads `spec.md`, the code the story touches and
the related decisions, then proposes:

```
## Acceptance criteria
- [ ] Given a 500 from storage, when I retry, then exactly one record exists.

## Checklist
- [ ] p1 Reproduce a retry twice — [agent]
  - tests/test_upload.py; run `pytest -k retry`
- [ ] p2 Make the write idempotent — [agent]
- [ ] p3 Run the staging check — [you]
```

As many criteria and steps as the story needs; no count cap. One gate, then the card description is
regenerated (`<h2>Acceptance criteria</h2>`, `<h2>Checklist</h2>`, no status) and one hidden subtask
per step is created. Anything from `<h2>Evidence (ai-daridev)</h2>` to the end is copied
byte-for-byte. Existing children are matched by name, updated, never deleted.

## 3. Pair

`/ai-daridev-pair <slug>` loads the card and its checklist.

Before anything else it reads the card's blockers. Only `1_done`, outside the Cancelled column,
frees a dependent; anything else is a hard stop: no override, no test list. A canceled blocker keeps
blocking and needs re-planning.

1. **Test list first**, names only: `retry keeps one record — tests/test_upload.py — covers p1 "<step>"`.
   Manual criteria are marked as such. One approval; the list lives in the conversation.
2. **One step per stop**: write the test, show it red, write the minimum code, show it green,
   embed the evidence in the card, flip that subtask to `1_done`, print `Plan 4/9 · next p5 "<step>"`.
3. **Stop immediately** on an unplanned design decision, an unrequested addition, a test that would
   have to change, two failed attempts, or a step over ~50 lines / 3 files.
4. **Non-code** (n8n, server, infra): read-only investigation, numbered plan, one approval, execute
   one step at a time showing command, output, state and rollback. Destructive steps ask again. The
   command and state stay in the conversation; the card gets the screenshot, same contract.

**Never print a bare id.** A step is `p4 "<step>"`, a card is `#14842 "<name>"`; a test-list mapping
is `covers p4 "<step>"`.

Each step appends one dated entry to `<h2>Evidence (ai-daridev)</h2>` at the end of the card
description, keyed `p4 "<step>"`: the final UI screenshot from prod via `playwright-cli`, or one code
line when the proof is invisible in a browser. Attachments live on the card and render inline via
`/web/image/<id>`; a file in the attachment list alone is not evidence. Redact secrets and mask client
data. No entry → a waiver, never a silent done. Upload or embed failure stops the flip.

At close: open steps are listed and decided (a step left open keeps the card gray), every closed step
already has its entry in the card's `Evidence` section, the card gets `state=03_approved` + `date_end`,
and one sentence is added or replaced in `spec.md` when behavior changed. The same gate offers the
column move to `odoo_stage_done` as one write with the green dot, default no, so a self-reviewed card
can land validated for archive. The agent prints the commit message for **you** to run. It never
commits.

## 4. Review

`/ai-daridev-review <card>` is for work someone else built. It reads the card, asks for a diff or a
screenshot only when the card does not settle it, and prints a verdict table: each criterion
pass/fail/manual and each step pass/fail/not reached, with one evidence line.

Each completed step must have an entry in the card's `Evidence` section, or a waiver; a `1_done` step
without one fails, even when the test passed. The `<h2>Review (ai-daridev)</h2>` section stays above
the slug line, outside the tail.

- **Approved** → one write turns the card green (`03_approved` + `date_end`) and moves it to
  `odoo_stage_done`, so it lands validated and not archived. A step that is not
  `1_done`/`1_canceled` blocks the green dot. The move is part of the gate: you can drop it and
  move the card yourself.
- **Changes requested** → the failing steps and the card go to `02_changes_requested`, and the
  `<h2>Review (ai-daridev)</h2>` section is replaced with the dated findings. If the card is in
  `odoo_stage_done`, the same write moves it back to the active stage; from a later stage, stop and
  report. Missing work becomes new steps, in the same gate.

## 5. Archive

`/ai-daridev-archive <slug>` marks the card done and appends its retro to `log.md`. The gate stops
unless the card is in `odoo_stage_done`, is **green** (`03_approved`) or already done (not gray,
yellow, waiting or canceled), and every step is closed. A step with no entry in the card's `Evidence`
tail is drift, not a stop: the gate lists it and continues only on `archive anyway`, and the retro's
`Drift:` line names it. It
then shows the dependents it frees and waits for your yes. A gray card in the validated column is
listed with one line: review it, or ask for the green dot. Archive never turns a card green.

```
## retry-safe-upload — shipped 2026-11-07
Shipped: uploads survive retries, exactly one record.
Decisions: 2026-11-07 — dedupe by hash, not a unique index (see decisions.md)
Follow-ups: backfill dedupe for legacy rows
Plan: 4/4 steps · dropped 0 · open 0
Card: task 14842 · state 1_done · end 2026-11-07 10:12:00
Drift: none
```

Odoo clears the blocked-by badge of the dependents when the card turns `1_done`. Bare
`/ai-daridev-archive` lists ready cards in the done stage that are not in `log.md` and asks one, all
or cancel; not-ready cards are listed with the reason. Follow-ups are listed, never turned into
cards.

## The card

```
<h1>{current card name}</h1>
<p>{one-line goal}</p>
<h2>Acceptance criteria</h2>
<ul><li>Given …, when …, then …</li></ul>
<h2>Checklist</h2>
<ol><li><b>p1</b> {step} — [agent]<ul><li>{detail}</li></ul></li></ol>
<h2>Review (ai-daridev)</h2>            <!-- owned by review, above the slug line, preserved by story -->
<p><b>{date}</b> — changes requested</p>
<p><em>ai-daridev: story/{slug}</em></p>  <!-- idempotency key -->
<h2>Evidence (ai-daridev)</h2>            <!-- owned by pair, always last, append-only -->
<h3>{YYYY-MM-DD HH:MM UTC} · p4 "{step}" · [agent]</h3>
<p><img src="/web/image/{id}" alt="p4 {step} — final UI" style="max-width:100%"/></p>
<p>{one line: what the screenshot proves}</p>
```

Subtask description (story and check-plan own the detail; pair never writes it):

```html
<p>{detail}</p>
```

- Subtasks: `name` = `<step> — [agent|you]` (the owner lives here, so it survives a restart;
  legacy names without the suffix still match), `description` = the detail, `parent_id`,
  `sequence = index × 10`, `state=01_in_progress`, `display_in_project=False`, never `project_id`
  or `stage_id`.
- Evidence: one dated entry per attempt, keyed `pN "<step>"`, on the card; never overwrite an
  attempt; a step without one is not `1_done`. A file in the attachment list is not evidence.
- Step states: `01_in_progress` open · `1_done` done · `02_changes_requested` rejected ·
  `1_canceled` dropped. Only open steps can be dropped; validated steps are never cancelled.
- The card closes at `03_approved` (green), archive marks it `1_done`, and the column move to
  `odoo_stage_done` is one write with the green dot — proposed in the gate, never silent. No skill
  sets `1_canceled` on a visible card without your say-so.

## The three files

```
docs/ai-daridev/
├── spec.md        # what the product does now
├── decisions.md   # why it is built this way (append-only)
└── log.md         # what shipped (append-only)
```

Query them with `rg`, or let the agent read them at the start of a story. `spec.md` is edited by
section; `decisions.md` and `log.md` only grow. No secrets or client data: they are committed.

First run in a repo that already has `docs/decisions/*.md` or an `openspec/` folder: one gate, then
they are folded into these three files and the originals stay as frozen history.

## Outside the flow

`/ai-daridev-check-plan` audits any plan in detail — pasted, from the conversation, or a card's
current checklist — fixes the gaps, asks one question at a time and renders it as an ordered
`p1..pN` checklist in the same format as a card. Standalone it writes nothing. If you name a card (`#14842`, a task URL,
`--card`, `story/<slug>`), it also updates that card's `<h2>Checklist</h2>` and its subtasks after
two gates (the plan, then the exact writes). It never creates a card, never deletes a subtask and
never drops a `1_done` step.

## Without Odoo

Every phase still works. Backlog and story print the card, the subtask list and the `Evidence`
heading to paste; pair loads the story from what you pasted, keeps the checklist in the conversation
and prints each evidence entry to paste; review takes the card as text; archive requires a slug or a
pasted story. Only the three files are written, and the printed close checklist tells you what to
update by hand.
