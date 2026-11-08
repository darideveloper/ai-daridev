---
name: ai-daridev-story
description: Refines ONE user story into 1-3 acceptance criteria and a 3-7 step checklist on its Odoo card, with one hidden subtask per step. Writes no code; implementation is /ai-daridev-pair's job.
disable-model-invocation: true
---

# Story

Refine one story right before building it. You propose, I decide. No code.

## Steps

1. **Load the story** by slug, card or pasted text. Read `docs/ai-daridev/spec.md` if it exists, the
   code the story touches, `rg` `docs/ai-daridev/decisions.md` for that area, and the card's
   `depend_on_ids` (id, name, stage).
2. **Blocked by** — show the blockers in the proposal. When I name one, resolve it by `#id`, task
   URL or `story/<slug>` (0 or 2+ matches → stop and list) and propose the append in the same gate:
   `depend_on_ids: [[4, <id>]]`. Same project, no self-link, no cycle; never remove a link.
3. **Acceptance criteria** — 1–3, Given/When/Then, user-visible only, never implementation.
4. **More than 3 criteria → split.** Print the new stories in backlog format and continue with the
   first one. If the card has blockers or dependents, ask in the same gate whether the links stay on
   the original (the first slice) or are left untouched for me to fix; the other slices get theirs
   when they become cards.
5. **Checklist** — 3–7 steps: verb-first, ≤80 chars, one verifiable action each. Add a detail
   sub-bullet (file, command, rollback) only when you already read the code. Mark every step
   `[agent]` or `[you]`; a `[you]` step is one I must do myself. More than 7 steps is a story to
   split.
6. **Wait for my approval.**

## Rules

- Don't invent requirements; ask.
- The simplest thing that meets the criteria. No abstractions, layers or configuration "for the
  future".
- Suggest a pattern only when the code already shows the signal; put it under Suggestions.
- Never write code.

## Output

```markdown
## Story
As a <actor>, I want <action>, so that <benefit>.

## Blocked by                 <!-- only when the card has blockers -->
- #<id> <name> — <stage>

## Acceptance criteria
- [ ] Given …, when …, then ….

## Checklist
- p1 <step> — [agent]
  - <detail, only if you read the code>
- p2 <step> — [you]

## Out of scope
- <what this story leaves out>

## Suggestions (your call)
- <optional>
```

## The card

Write only after the checklist is approved. One gate: show the card, its checklist and the exact
writes. Slug = kebab-case of the title, ≤40 chars; reuse the slug of the card you found.

- Find the card by `ai-daridev: story/<slug>` (or legacy `engram: story/<slug>`). Not found → ask
  "create it in the backlog stage?" and create it with `/ai-daridev-backlog`'s card rules.
- A blocker is one of the exact writes: `odoo_update` with `depend_on_ids: [[4, <id>]]`, in the same
  gate. Never regenerate the description to carry it.
- **Regenerate the description** (never append), escaping `<`, `>` and `&`, in this order:
  `<h1>{the card's CURRENT name, read it first}</h1>`, `<p>{goal}</p>`,
  `<h2>Acceptance criteria</h2>`, `<h2>Checklist</h2>` (step name, its `[agent]`/`[you]` owner
  and optional detail, **no status**), any existing `<h2>Review (ai-daridev)</h2>` section copied
  **verbatim**, and finally
  `<p><em>ai-daridev: story/{slug}</em></p>`.
- Re-read the description right before writing. If `write_date` changed since your first read, show
  what changed and ask once.
- **Subtasks: one per step.** `name` = `<step> — [agent|you]`, `description` = `<p>{detail}</p>`
  (no key prefix), `parent_id`, `sequence` = index × 10, `state=01_in_progress`, `user_ids=[]`,
  `display_in_project=False`. Never write `project_id` or `stage_id`. Read one back: if
  `display_in_project` is not false, stop and report.
- Match existing children by exact name, ignoring a trailing ` — [agent]`/`— [you]` on legacy
  cards: update the ones that changed (rewriting the name in the new form; for `description`, keep
  everything from `<h3>Evidence</h3>` onward byte-for-byte and replace only the detail above it),
  create the missing ones, never delete. List extras and leave them alone; a rename asks once.
- No file writes.

Without Odoo: print the description HTML, the step list with owners, and where to paste them.

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
