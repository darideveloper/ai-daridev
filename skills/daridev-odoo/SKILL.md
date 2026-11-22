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
- Second line of every on session, before any other output:
  `Identity: agent <uid> · you <name> (<uid>, <source>)` — `source` is `local` when the local file
  sets the uid and `block` otherwise, never inferred from which value differs; the name is read from
  either file, and the label follows the uid. `you` is omitted when there is no manual uid, and its
  name may be omitted (`you 2 (local)`). The uid alone prints on this line and in an assignee
  report, nowhere else. The agent uid is `odoo_connection_info`'s `uid`; no such tool → ask once,
  never guess, and with MCP unavailable the line is omitted.
- On with no `odoo_project` → ask for the exact project and offer the block line.
- MCP unavailable → print what it would write, continue in chat, never guess an id.

## Ask

An ask is a tool call, not a paragraph. When the harness has a question tool (OpenCode: `question`),
use it: one question per call — or one call with the batch when the phase already asks a batch —
the phase's literal prompt string as the question, the recommended option first and labelled
`(Recommended)`, and the harness's free-text escape as the way out. The backticked prompt in a phase
is that question, never text to print and then wait behind: a session that prints `Pace: …` as prose
and stops has asked nothing.

Without such a tool, print the question with its default and stop. A dismissed question takes the
default as well. A subagent has nobody to answer: take the phase's default, never a question it
cannot get.

## Config

Read `odoo_project`, `odoo_stage_done`, `card_tag`, `card_tag_extra`, `odoo_assignee_manual_uid`,
`odoo_assignee_manual_name`, `deploy_url`, `deploy_expect` from the root block, with the
per-developer override below.

A `.daridev.local` file beside that `AGENTS.md` is the per-developer layer: the same `key: value`
lines (the leading `-` is optional), never committed, and it may set only `odoo_assignee_manual_uid`,
`odoo_assignee_manual_name`, `deploy_url`, `deploy_expect` — anything else in it is ignored. Read the
block where the session is (it commits with the branch), then the local file from the canonical
checkout (`git worktree list --porcelain | sed -n '1s/^worktree //p'`, same directory), then ask
once. The block keeps its tolerance: dashed or bare keys, an optional `## Workflow config` heading,
keys alone with no prose. Agent identity is never read from either — it is the MCP uid (§Mode).

Resolve the project and tags by exact name; 0 or 2+ → stop and list. Resolve stages inside that
project (`project.task.type` whose `project_ids` contains it). Backlog = lowest `sequence`;
sprint = name matches `sprint backlog`; in progress = `in progress` (case-insensitive);
validated = `odoo_stage_done`. Cards are found by `<p><em>daridev: card/<slug></em></p>`; legacy
`story/`, `ai-daridev: story/` and `engram: story/` are accepted on read. No `#id`, no slug, no
match inside `odoo_project`, and the reference is still unclear → `odoo_search_read project.task`
with `name ilike` on its longest word, `limit 20`; report the project the card came from; 2+ → list
`#<id> "<name>" · <project>`, never guess.

## Moves

A move is one write: `stage_id` + `state` (+ `date_end`) together. The one state-only write is
`pair`'s close: `state=03_approved`, `stage_id` and `date_end` untouched, when no step is open and I
said yes (in a campaign, the §2 gate is that yes). It is the green dot in the column the card
already sits in, never the validated move.
→ validated = `03_approved` + `date_end` (review) or `1_done` + `date_end` (archive skip-review);
→ an active stage = `01_in_progress`; → backlog = explicit reopen only; → Cancelled = `1_canceled`
with my approval. Never move a subtask or an archived card. Never enter validated without review
unless it is archive's skip-review close.

One card, one session: the in-progress column is the claim, and a session that finds the card
changed under it stops and reloads instead of continuing. Two sessions never work the same card; the
second one says so in one line.

## Assignees

The card carries exactly two identities: the agent (the MCP uid) and the manual user, the second only
while the next open step is `[you]`. Next open = lowest `sequence` child not `1_done`/`1_canceled`;
`02_changes_requested` is open, for its own owner. Every assignee write replaces the set —
`[[6, 0, [agent, manual]]]`, or `[[6, 0, [agent]]]` — and reports what it dropped: a name and a uid
when the read returns them, `uid <n>` when the server returns ids only. Read `user_ids` with the
card. Re-read `stage_id`, `state` and `user_ids` immediately before the write; any change since the
load → stop in one line and reload the card. Derived, reported, not asked. No manual uid → no
handoff; ask once and offer the two `.daridev.local` lines. A named person resolves exactly.

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

`Steps` is one `<pre>` block of markdown so a copy keeps its shape. Every step line stays `- [ ]`
— the subtask `state` is the status — the `check:`/`files:` lines are two-space fields, and `<`,
`>`, `&` are escaped:

```html
<p><b>Steps</b></p>
<pre>- [ ] p1 Add a hidden status region — [agent]
  check: npx playwright test tests/e2e/scan-report.spec.ts
  files: src/layouts/Layout.astro, tests/e2e/scan-report.spec.ts
- [ ] p2 Run the mobile suites — [agent]
  check: npx playwright test --project="local: mobile-chrome"
</pre>
```

The `<pre>` block is the write shape, not a render: renders use `- ☐` for a step and `  - ☐`
for each check. `☑` is chat-only and never written to the card.

**Step rendering, every phase.** A chat step list writes `- ☐ pN` / `- ☑ pN`, with each check
under it as `  - ☐` / `  - ☑`. The card `Steps` keeps `- [ ]` and the `check:`/`files:` fields;
`☑` is chat-only and never written to the card. A step named inline (a progress line, a table cell,
an evidence label) keeps its inline form; an evidence label is never a step; a handoff's
`what/files/check/then` are fields, not checks; a summary line may omit its checks. A dropped step
stays `- ☐` and carries `(dropped)`.

`plan` writes the first zone, rewrites the slug line to `card/<slug>`, and preserves everything
after it (or after an existing `Review` heading) byte-for-byte, including the evidence gallery. A
legacy tail may be collapsed to one attachment pointer only with approval. `review` replaces only
its section, inserting it before the slug, and mirrors a new or refused step into `Steps`.
`campaign`'s park line is the only other write inside `Steps`. `pair` appends the evidence gallery.
Nobody else writes the description. Cap: the brief above `Steps` is 10 lines; `Steps` is 3–7.

## Subtasks = tracking

`name` = `pN <step> — [agent|you]`, `description` empty, `parent_id`,
`sequence = index × 10`, `state=01_in_progress`, `display_in_project=False`. Never write the
subtask's `project_id`, `stage_id`, `user_ids` or description — Odoo may default an assignee from
the create user and nothing reads it; the name mirrors its line in `Steps` and the detail stays
there. A subtask never carries information the description does not: every step,
rename, drop and park is mirrored into `Steps` in the same write. A card with no `Steps` block is
legacy — read the steps from its subtasks. On a legacy card, new steps start at `max+10`; open
legacy steps superseded by a new plan become `1_canceled` + ` (superseded)` with approval; a
`1_done` step is never renamed or dropped. Review-created missing-work steps use
`state=02_changes_requested` (yellow). States: `01_in_progress` · `1_done` ·
`02_changes_requested` · `1_canceled`. Never delete a subtask.

## Evidence

The card shows the screenshots in `Evidence (daridev)`, one entry per step, labelled
`pN "<step>" — [owner] · <surface>` (`prod`, `staging`, `local`), with ` — not deployed` appended
while that surface is not deployed.

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
- Local copy always: `docs/records/evidence/<YYYY-MM-DD>-<slug>/pN-<step>.png` under the canonical
  checkout's memory root (`docs/ai-daridev/evidence/` in a legacy repo), untracked, so removing the
  worktree cannot delete it. The folder's `.gitignore` (`*`, `!.gitignore`) is created in the root
  that receives the PNGs — the canonical memory root — when missing, and committed there.
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
| attachment on the card | pair, or the campaign's post-deploy re-capture, or the teammate without MCP |
| `Evidence (daridev)` gallery | pair, or the campaign's post-deploy re-capture, or the teammate without MCP |
| `stage_id` + `state` | plan (sprint), pair (in progress; green dot at close, state only), review, archive (skip-review) |
| `Review` block | review |
| `spec.md`, `evidence/`, `docs/records/` | pair |
| `docs/decisions/NNNN-<slug>.md` | archive, on approval |
| `1_done`, `docs/records/log.md` | archive |
| `user_ids` set | plan, pair, review; archive closes agent-only |

Never print a bare id — the uid on the identity line and a `uid <n>` in an assignee report are the
only exceptions: `p4 "<step>"`, `#14842 "<name>"`, `covers p4 "<step>"`.
