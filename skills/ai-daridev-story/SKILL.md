---
name: ai-daridev-story
description: Refines ONE user story into 1-3 acceptance criteria and a 3-7 step checklist on its Odoo card, with one hidden subtask per step. Writes no code; implementation is /ai-daridev-pair's job.
disable-model-invocation: true
---

# Story

Refine one story right before building it. You propose, I decide. No code.

## Steps

1. **Load the story** by slug, card or pasted text. Read `docs/ai-daridev/spec.md` if it exists, the
   code the story touches, and `rg` `docs/ai-daridev/decisions.md` for that area.
2. **Acceptance criteria** — 1–3, Given/When/Then, user-visible only, never implementation.
3. **More than 3 criteria → split.** Print the new stories in backlog format and continue with the
   first one.
4. **Checklist** — 3–7 steps: verb-first, ≤80 chars, one verifiable action each. Add a detail
   sub-bullet (file, command, rollback) only when you already read the code. Mark every step
   `[agent]` or `[you]`; a `[you]` step is one I must do myself. More than 7 steps is a story to
   split.
5. **Wait for my approval.**

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
- **Regenerate the description** (never append), escaping `<`, `>` and `&`, in this order:
  `<h1>{the card's CURRENT name, read it first}</h1>`, `<p>{goal}</p>`,
  `<h2>Acceptance criteria</h2>`, `<h2>Checklist</h2>` (step name plus optional detail, **no
  status**), any existing `<h2>Review (ai-daridev)</h2>` section copied **verbatim**, and finally
  `<p><em>ai-daridev: story/{slug}</em></p>`.
- Re-read the description right before writing. If `write_date` changed since your first read, show
  what changed and ask once.
- **Subtasks: one per step.** `name` = the step, `description` = `<p>{detail}</p>` (no key prefix),
  `parent_id`, `sequence` = index × 10, `state=01_in_progress`, `user_ids=[]`,
  `display_in_project=False`. Never write `project_id` or `stage_id`. Read one back: if
  `display_in_project` is not false, stop and report.
- Match existing children by exact name: update the ones that changed, create the missing ones,
  never delete. List extras and leave them alone; a rename asks once.
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
