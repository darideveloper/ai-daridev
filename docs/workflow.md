# Workflow

Five phases, one story at a time. Each phase ends waiting for your approval, and the agent never
moves a card between stages.

## The rules that apply everywhere

- **Root.** The repo root is the nearest `AGENTS.md` holding `<!-- ai-daridev:start -->`, walking up
  from the current directory. `docs/ai-daridev/` is always relative to it; nothing is written above.
  No block → the skill asks once (create it here, use the git root, or chat-only).
- **Odoo is optional.** Without an `odoo_project` key there are no cards: stories live in the
  conversation and only the three files are written.
- **The board is yours.** No skill writes `stage_id`, sets a card `1_done`/`1_canceled` or assigns
  anyone. The agent writes the description (story), subtask states, `state=03_approved` + `date_end`
  (close) and `state=02_changes_requested` (review).
- **One gate per phase.** Structure changes ask once; state changes are reported.
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
stage, unassigned, one tag each, no subtasks.

## 2. Story

`/ai-daridev-story` refines exactly one story. It reads `spec.md`, the code the story touches and
the related decisions, then proposes:

```
## Acceptance criteria
- [ ] Given a 500 from storage, when I retry, then exactly one record exists.

## Checklist
- p1 Reproduce a retry twice — [agent]
  - tests/test_upload.py; run `pytest -k retry`
- p2 Make the write idempotent — [agent]
- p3 Run the staging check — [you]
```

1–3 criteria, 3–7 steps. More than that is a story to split. One gate, then the card description is
regenerated (`<h2>Acceptance criteria</h2>`, `<h2>Checklist</h2>`, no status) and one hidden subtask
per step is created. Existing children are matched by name, updated, never deleted.

## 3. Pair

`/ai-daridev-pair <slug>` loads the card and its checklist.

1. **Test list first**, names only: `retry keeps one record — tests/test_upload.py — covers p1`.
   Manual criteria are marked as such. One approval; the list lives in the conversation.
2. **One step per stop**: write the test, show it red, write the minimum code, show it green, flip
   that subtask to `1_done`, print `Plan 4/9 · next p5`.
3. **Stop immediately** on an unplanned design decision, an unrequested addition, a test that would
   have to change, two failed attempts, or a step over ~50 lines / 3 files.
4. **Non-code** (n8n, server, infra): read-only investigation, numbered plan, one approval, execute
   one step at a time showing command, output, state and rollback. Destructive steps ask again.

At close: open steps are listed and decided, the card gets `state=03_approved` + `date_end`, one
sentence is added or replaced in `spec.md` when behavior changed, and the agent prints the commit
message for **you** to run. It never commits.

## 4. Review

`/ai-daridev-review <card>` is for work someone else built. It reads the card, asks for a diff or a
screenshot only when the card does not settle it, and prints a verdict table: each criterion
pass/fail/manual and each step pass/fail/not reached, with one evidence line.

- **Approved** → it proposes the column move as *your* action and lists any step still open. It never
  writes `stage_id`.
- **Changes requested** → the failing steps and the card go to `02_changes_requested`, and the
  `<h2>Review (ai-daridev)</h2>` section is replaced with the dated findings. Missing work becomes
  new steps, in the same gate.

## 5. Archive

`/ai-daridev-archive <slug>` reconciles the card, its steps and the decisions, prints the retro and
appends it to `log.md`:

```
## retry-safe-upload — shipped 2026-11-07
Shipped: uploads survive retries, exactly one record.
Decisions: 2026-11-07 — dedupe by hash, not a unique index (see decisions.md)
Follow-ups: backfill dedupe for legacy rows
Plan: 4/4 steps · dropped 0 · open 0
Card: task 14842 · state 03_approved · end 2026-11-07 10:12:00
Drift: none
```

Bare `/ai-daridev-archive` lists cards in the done stage that are not in `log.md` and asks one, all or
cancel. Follow-ups are listed, never turned into cards.

## The card

```
<h1>{current card name}</h1>
<p>{one-line goal}</p>
<h2>Acceptance criteria</h2>
<ul><li>Given …, when …, then …</li></ul>
<h2>Checklist</h2>
<ol><li><b>p1</b> {step} — [agent]<ul><li>{detail}</li></ul></li></ol>
<h2>Review (ai-daridev)</h2>            <!-- owned by review, preserved verbatim by story -->
<p><b>{date}</b> — changes requested</p>
<p><em>ai-daridev: story/{slug}</em></p>  <!-- idempotency key, always last -->
```

- Subtasks: `name` = `<step> — [agent|you]` (the owner lives here, so it survives a restart;
  legacy names without the suffix still match), `description` = the detail, `parent_id`,
  `sequence = index × 10`, `state=01_in_progress`, `display_in_project=False`, never `project_id`
  or `stage_id`.
- Step states: `01_in_progress` open · `1_done` validated · `02_changes_requested` rejected ·
  `1_canceled` dropped. Only open steps can be dropped; validated steps are never cancelled.
- The card itself never uses `1_done`/`1_canceled`; it closes at `03_approved` and the column move is
  yours.

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
current checklist — fixes the gaps, asks one question at a time and renders the corrected plan in
the same lean format. Standalone it writes nothing. If you name a card (`#14842`, a task URL,
`--card`, `story/<slug>`), it also updates that card's `<h2>Checklist</h2>` and its subtasks after
two gates (the plan, then the exact writes). It never creates a card, never deletes a subtask and
never drops a `1_done` step.

## Without Odoo

Every phase still works. Backlog and story print the card and the subtask list to paste; pair loads
the story from what you pasted and keeps the checklist in the conversation; review takes the card as
text; archive requires a slug or a pasted story. Only the three files are written, and the printed
close checklist tells you what to update by hand.
