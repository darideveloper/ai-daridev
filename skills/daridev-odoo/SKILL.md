---
name: daridev-odoo
description: The Odoo rules every daridev phase shares — per-session mode, project and stage lookup, one write per move, assignees, the description zones, subtasks and the evidence upload. A contract, not a phase.
disable-model-invocation: true
---

# Odoo

Read **Root memory** and **Mode** first, even when the session may end up off. When it is on, read
the rest before the first write. This file is the only copy of these rules; the phases never
restate them.

## Root memory

The root is the nearest `AGENTS.md` holding `<!-- daridev:start -->` (or the legacy
`<!-- ai-daridev:start -->`). Its memory is `docs/records/`; if only `docs/ai-daridev/` exists, it
is the memory: read **and write** it in place (`spec.md`, `log.md`, `evidence/`) and print the
`git mv docs/ai-daridev docs/records` hint. Never create `docs/records/` beside it. If both exist,
use `docs/records/` and report the stale one. Nothing is written above the root.

`decisions.md` is retired: read it, never append. Lasting decisions are ADRs under
`docs/decisions/`, one per file, named `NNNN-<slug>.md` — zero-padded from `0001`, next = highest
existing + 1, slug kebab-case, numbered per repo, never reused. A `decisions.md` still in the
memory root is frozen by the first ADR: `mkdir -p docs/decisions` and `git mv` it to
`docs/decisions/legacy-decisions.md` unless that file is already there.

Memory is created by the write that needs it, never as empty stubs: in the memory root
(`docs/records/`, or the legacy `docs/ai-daridev/` in place) `pair` creates the folder, `spec.md`
and `evidence/.gitignore` (`*`, `!.gitignore`); `archive` creates `log.md` with a `# Log` header;
`docs/decisions/` exists once an ADR is written.

## Mode (per session)

| Signal | Mode | Ask |
|---|---|---|
| `--odoo` / `--no-odoo`, or I say it | that | never |
| A card: `#14842`, a task URL, a card name, `card/<slug>` or `story/<slug>` | on | never |
| `plan` with pasted text or a one-liner | off | never |
| `plan` with nothing, no prior answer | — | once, default no |
| `pair` with nothing | off | never |
| `review` / `archive` bare | on, they list cards | off needs a pasted card/brief |
| `campaign` | on | never; no `odoo_project` → stop |

- `--no-odoo` beats a card: off, and the card is ignored in one line.
- First line of every phase: `Odoo: on · <project> · card #<id> "<name>"` or `Odoo: off · chat-only`.
- On with no `odoo_project` → ask for the exact project and offer the block line.
- MCP unavailable → print what it would write, continue in chat, never guess an id.

## Config

Read `odoo_project`, `odoo_stage_done`, `card_tag`, `card_tag_extra`, `odoo_assignee_uid`,
`odoo_assignee_manual_uid`, `deploy_url`, `deploy_expect` from the root block.

Resolve the project and tags by exact name; 0 or 2+ → stop and list. Resolve stages inside that
project (`project.task.type` whose `project_ids` contains it). Backlog = lowest `sequence`;
sprint = name matches `sprint backlog`; in progress = `in progress` (case-insensitive);
validated = `odoo_stage_done`. Cards are found by `<p><em>daridev: card/<slug></em></p>`; legacy
`story/`, `ai-daridev: story/` and `engram: story/` are accepted on read. No `#id`, no slug, no
match inside `odoo_project`, and the reference is still unclear → `odoo_search_read project.task`
with `name ilike` on its longest word, `limit 20`; report the project the card came from; 2+ → list
`#<id> "<name>" · <project>`, never guess.

## Moves

A move is one write: `stage_id` + `state` (+ `date_end`) together.
→ validated = `03_approved` + `date_end` (review) or `1_done` + `date_end` (archive skip-review);
→ an active stage = `01_in_progress`; → backlog = explicit reopen only; → Cancelled = `1_canceled`
with my approval. Never move a subtask or an archived card. Never enter validated without review
unless it is archive's skip-review close.

## Assignees

The card carries the agent (`odoo_assignee_uid` or the MCP uid) and the manual user only while the
next open step is `[you]`. Next open = lowest `sequence` child not `1_done`/`1_canceled`;
`02_changes_requested` is open, for its own owner. Creates send the full set; updates diff with
`[[4, uid]]`/`[[3, uid]]`, never `[[6,0,…]]`; add the agent when missing. Derived, reported, not
asked. No manual uid → no handoff; ask once and offer the key. A named person resolves exactly.

## Description — four zones

```
[plan]      <h1>, Problem, Done when, Out of scope, Touched, Steps
[review]    <h2>Review (daridev)</h2> ...        (above the slug line)
[evidence]  <h2>Evidence (daridev)</h2> ...      (pair-owned, append-only)
[frozen]    <p><em>daridev: card/<slug></em></p>
[legacy]    <h2>Evidence (ai-daridev)</h2> ...   (old cards; byte-for-byte)
```

The description is the whole plan: a teammate without Odoo MCP copies it and has every step, owner,
check and file. The subtasks are a checklist, never a document.

`Steps` is one `<pre>` block of markdown so a copy keeps its shape. Every box stays `[ ]` — the
subtask `state` is the status — and `<`, `>`, `&` are escaped:

```html
<p><b>Steps</b></p>
<pre>- [ ] p1 Add a hidden status region — [agent]
  check: npx playwright test tests/e2e/scan-report.spec.ts
  files: src/layouts/Layout.astro, tests/e2e/scan-report.spec.ts
- [ ] p2 Run the mobile suites — [agent]
  check: npx playwright test --project="local: mobile-chrome"
</pre>
```

`plan` writes the first zone, rewrites the slug line to `card/<slug>`, and preserves everything
after it (or after an existing `Review` heading) byte-for-byte, including the evidence gallery. A
legacy tail may be collapsed to one attachment pointer only with approval. `review` replaces only
its section, inserting it before the slug, and mirrors a new or refused step into `Steps`.
`campaign`'s park line is the only other write inside `Steps`. `pair` appends the evidence gallery.
Nobody else writes the description. Cap: the brief above `Steps` is 10 lines; `Steps` is 3–7.

## Subtasks = tracking

`name` = `pN <step> — [agent|you]`, `description` empty, `parent_id`,
`sequence = index × 10`, `state=01_in_progress`, owner uid, `display_in_project=False`. Never write
the subtask's `project_id`, `stage_id` or description; the name mirrors its line in `Steps` and the
detail stays there. A subtask never carries information the description does not: every step,
rename, drop and park is mirrored into `Steps` in the same write. A card with no `Steps` block is
legacy — read the steps from its subtasks. On a legacy card, new steps start at `max+10`; open
legacy steps superseded by a new plan become `1_canceled` + ` (superseded)` with approval; a
`1_done` step is never renamed or dropped. Review-created missing-work steps use
`state=02_changes_requested` (yellow). States: `01_in_progress` · `1_done` ·
`02_changes_requested` · `1_canceled`. Never delete a subtask.

## Evidence

The card shows the screenshots in `Evidence (daridev)`, one entry per step, labelled
`pN "<step>" — [owner] · <surface>` (`prod`, `staging — not deployed`, `local — not deployed`).

- The image is attached to **the card** (`ir.attachment`, `res_model=project.task`,
  `res_id=<card>`, `image/*`, > 0 bytes), named `pN-<step>.png`; the card renders
  `<p><img src="/web/image/{id}" …/></p>` under the label. A legacy attachment on a subtask is
  accepted on read.
- A teammate without MCP pastes the image into `Evidence (daridev)`; Odoo attaches it to the card
  the same way.
- One entry per step; a re-capture replaces it; old attachments stay as history.
- A non-visual step gets one `<code>` line under the label instead of an image; the text must be
  non-empty and the label must match a step in `Steps` and its subtask.
- `pair` creates `Evidence (daridev)` only when missing, after the `Review` block and before the
  slug line; it appends one entry per step, replacing that step's entry on a re-capture.
- Local copy always: `docs/records/evidence/<YYYY-MM-DD>-<slug>/pN-<step>.png` in the memory root
  (`docs/ai-daridev/evidence/` in a legacy repo), untracked.
- Verify before flipping: the image resolves and the attachment row is on the card, `image/*`,
  `file_size > 0`; for a code line, the text is non-empty. Never a
  `.txt` link as the only proof; never delete an orphan. The probe block in `Review` is what proves
  the Done-when.

## Who writes what

| Write | Owner |
|---|---|
| description top: the brief and `Steps` | plan; review for a new or refused step; campaign for a park |
| subtasks create/rename/sequence | plan; review for new steps, with their `Steps` line |
| subtask state | plan (open), pair (done/drop), review (changes and new steps) |
| attachment on the card | pair, or the teammate without MCP |
| `Evidence (daridev)` gallery | pair, or the teammate without MCP |
| `stage_id` + `state` | plan (sprint), pair (in progress), review, archive (skip-review) |
| `Review` block | review |
| `spec.md`, `evidence/`, `docs/records/` | pair |
| `docs/decisions/NNNN-<slug>.md` | archive, on approval |
| `1_done`, `docs/records/log.md` | archive |
| `user_ids` diff | plan, pair, review; archive closes agent-only |

Never print a bare id: `p4 "<step>"`, `#14842 "<name>"`, `covers p4 "<step>"`.
