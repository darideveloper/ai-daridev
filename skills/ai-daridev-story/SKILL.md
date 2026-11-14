---
name: ai-daridev-story
description: Refines ONE user story into acceptance criteria and a step checklist on its card when the session is on Odoo, with one hidden subtask per step, and moves it to the sprint column. Writes no code; implementation is /ai-daridev-pair's job.
disable-model-invocation: true
---

# Story

Refine one story right before building it. You propose, I decide. No code.

**Mode first.** This phase can open the session. When the turn does not already say it (`--odoo`,
`--no-odoo`, or my words) and the session has not answered yet, ask once: `Odoo this session? [y/N]` —
default no. Keep it for the session and report it in the first line, `Odoo: on · <project>` or
`Odoo: off · chat-only`. A card named in the invocation answers it: on.

## Steps

1. **Load the story** by slug, card or pasted text. Read `docs/ai-daridev/spec.md` if it exists, the
   code the story touches, `rg` `docs/ai-daridev/decisions.md` for that area, and the card's
   `depend_on_ids` (id, name, stage).
2. **Blocked by** — show the blockers in the proposal. When I name one, resolve it by `#id`, task
   URL or `story/<slug>` (0 or 2+ matches → stop and list) and propose the append in the same gate:
   `depend_on_ids: [[4, <id>]]`. Same project, no self-link, no cycle; never remove a link.
3. **Acceptance criteria** — one or more, Given/When/Then, user-visible only, never implementation.
4. **Checklist** — as many steps as the story needs: verb-first, ≤80 chars, one verifiable action
   each. Add a detail sub-bullet (file, command, rollback) only when you already read the code. Mark
   every step `[agent]` or `[you]`; a `[you]` step is one I must do myself. A step already done on
   the card is `- [x]`, not `- [ ]`. A command block in a detail is indented to that bullet's
   content column (4 spaces under `  - `), never at column 0 — a column-0 fence closes the list.
5. **Wait for my approval.**

## Rules

- Don't invent requirements; ask.
- No count cap: as many criteria and steps as the story needs. Do not split for the count; split
  only if it is genuinely more than one story.
- The simplest thing that meets the criteria. No abstractions, layers or configuration "for the
  future".
- Suggest a pattern only when the code already shows the signal; put it under Suggestions.
- Never write code.

## Output

````markdown
## Story
As a <actor>, I want <action>, so that <benefit>.

## Blocked by                 <!-- only when the card has blockers -->
- #<id> <name> — <stage>

## Acceptance criteria
- [ ] Given …, when …, then ….

## Checklist
- [ ] p1 <step> — [agent]
  - <detail, only if you read the code>
    ```
    <command block, indented to this bullet's content column>
    ```
- [ ] p2 <step> — [you]

## Out of scope
- <what this story leaves out>

## Suggestions (your call)
- <optional>
````

## The card

Odoo off → skip this section: print the description, the step list and where to paste them, and write
nothing. On Odoo, write only after the checklist is approved. One gate: show the card, its checklist,
its assignees, the column move and the exact writes. Slug = kebab-case of the title, ≤40 chars; reuse
the slug of the card you found.

- **Move to the sprint column: default, in the gate.** Resolve the single stage inside the project
  whose name matches `sprint backlog` (case-insensitive); 0 or 2+ → ask once which stage and use that
  answer for the run. In the same `odoo_update` as the description: `stage_id=<stage>,
  state=01_in_progress`, no `date_end`. Move only from the backlog stage, on an open card
  (`state=01_in_progress`): already in the sprint column → skip and report; any other stage, or any
  other state → leave it and report "refined in place". Say "keep it in Backlog" in the turn to opt
  out. No stage resolved → the card stays put, reported in one line.
- Find the card by `ai-daridev: story/<slug>` (or legacy `engram: story/<slug>`). Not found → ask
  "create it in the sprint column?" and create it with `/ai-daridev-backlog`'s card rules, except
  `stage_id` = that stage and `state=01_in_progress`: the create is the move.
- A blocker is one of the exact writes: `odoo_update` with `depend_on_ids: [[4, <id>]]`, in the same
  gate. Never regenerate the description to carry it.
- **Regenerate the description** (never append), escaping `<`, `>` and `&`, in this order:
  `<h1>{the card's CURRENT name, read it first}</h1>`, `<p>{goal}</p>`,
  `<h2>Acceptance criteria</h2>`, `<h2>Checklist</h2>` (step name, its `[agent]`/`[you]` owner
  and optional detail, **no status**), any existing `<h2>Review (ai-daridev)</h2>` section copied
  **verbatim**, `<p><em>ai-daridev: story/{slug}</em></p>`, and finally the `Evidence` tail when the
  description has one.
- **The Evidence tail is not yours.** Everything from `<h2>Evidence (ai-daridev)</h2>` to the end of
  the description is copied byte-for-byte, after the slug line. No heading → nothing to copy. Never
  regenerate, reorder, trim or move it.
- Re-read the description right before writing. If `write_date` changed since your first read, show
  what changed and ask once.
- **Assignees, one write with the description.** `user_ids: [[6,0,[<agent>]]]`, plus
  `odoo_assignee_manual_uid` in the same array when the first step is `[you]`; a create sends the
  same full set. Both uids resolve per the Odoo contract. Derived from the checklist, so it is shown in
  the gate rather than asked again.
- **Subtasks: one per step.** `name` = `<step> — [agent|you]`, `description` = `<p>{detail}</p>`
  (no key prefix), `parent_id`, `sequence` = index × 10, `state=01_in_progress`,
  `user_ids: [[6,0,[<id>]]]` — the agent user for a `[agent]` step and the
  `odoo_assignee_manual_uid` for a `[you]` step; no manual uid → omit it on the `[you]` steps. If I
  name an assignee for a step, resolve the exact `res.users` name or login and use that id instead.
  `display_in_project=False`. Never write the subtask's `project_id` or `stage_id`. Read one back: if
  `display_in_project` is not false, stop and report.
- Match existing children by exact name, ignoring a trailing ` — [agent]`/`— [you]`: update the ones
  that changed (rewriting the name in the new form), create the missing ones, never delete. On a
  legacy child, keep everything from a `<h3>Evidence</h3>` onward byte-for-byte and replace only the
  detail above it. List extras and leave them alone; a rename asks once.
- No file writes.

Odoo off: print the description HTML with the `Evidence` heading at the end, the step list with
owners, and where to paste them. No card is created and nothing moves.

## Always

- **Root.** Walk up from the current directory to the nearest `AGENTS.md` that holds
  `<!-- ai-daridev:start -->`. That directory is the root: read and write `docs/ai-daridev/` there
  and write nothing outside it. No block → ask once: create it here, use the git root, or chat-only.
- **Mode.** Cards only when this session is on Odoo, and the first line says which. Resolve it once
  and keep it: an explicit `--odoo`/`--no-odoo` or my words beat everything; a named card means on;
  this skill can open the session, so with no signal it asks once (default no).
- **Odoo contract.** On → read `../ai-daridev-odoo/SKILL.md` and follow it for every Odoo rule:
  config, project and stages, moves, assignees, who writes what and the evidence upload. Off → print
  what it would write and write no card. Never restate those rules here.
- **One approval gate per phase.** Structure asks once; state changes are reported, not asked.
- **Decisions** → one append to `docs/ai-daridev/decisions.md`, only when project-wide, hard to
  reverse or a shared/ops contract. Everything else stays in the conversation.
- **Fold-in.** If `docs/ai-daridev/` is missing and `docs/decisions/*.md` or `openspec/` exists, ask
  once to fold them into `decisions.md` and `spec.md`; the originals stay as frozen history.
- **Never commit.** Never write secrets or client data into the three files.
