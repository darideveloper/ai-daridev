---
name: ai-daridev-odoo
description: The Odoo rules the ai-daridev phases share — mode resolution, project and stage lookup, moves, assignees, write ownership and the evidence upload. A contract, not a phase; the phase skills read it when the session is on Odoo.
disable-model-invocation: true
---

# Odoo

Every phase reads the **Mode** section below before anything else, even when the session may end up
off — it is the only switch. When the session is on, read the rest of this file too, before the first
write. It is the only copy of these rules: never restate them in a phase file, and never follow a
phase file over this one.

## Mode (per session)

Cards are written only when the session is on. Resolve it once and keep the answer for the session:

| Signal | Mode | Ask |
|---|---|---|
| `--odoo` / `--no-odoo`, or I say it in the turn | that | never |
| A card reference: `#14842`, a task URL, a card name, a resolved `story/<slug>` | on | never |
| `backlog` or `story` opening the session, no signal | — | once: `Odoo this session? [y/N]` |
| `pair` with nothing | off | never |
| `campaign` | on | never; no `odoo_project` → stop in one line |
| `review` / `archive` bare | on, it lists cards | off needs a slug or a pasted story |

An explicit flag beats every other signal: `--no-odoo` with a card named means off, and the card is
ignored in one line. Print the resolved mode as the first line of the phase:
`Odoo: on · <project> · card #<id> "<name>"` or `Odoo: off · chat-only`.

On with no `odoo_project` → ask for the exact project name and offer the block line. A card that lives
in another project stops the run: say its project and the `odoo_project` line to change.

## Config

Read `odoo_project`, `odoo_stage_done`, `card_tag`, `card_tag_extra`, `odoo_assignee_uid` and
`odoo_assignee_manual_uid` from the repo block. Resolve the project and the tags by exact name; 0 or
2+ matches → stop and list the real ones. Resolve the stages **inside that project**
(`project.task.type` whose `project_ids` contains it); a stage name that also exists in other projects
is not a match and must not stop the run. Backlog stage = lowest `sequence`; sprint column = the stage
whose name matches `sprint backlog` (case-insensitive); in-progress column = `in progress`
(case-insensitive); validated column = `odoo_stage_done`. Default tag `backend`. Cards are found by
`<p><em>ai-daridev: story/<slug></em></p>`; the legacy `engram: story/<slug>` is accepted on read.

## Moves and assignees are proposed, not assumed

Move a card only when I ask in this turn, when the phase gate lists it and I say yes, or when the
column and the state already disagree and I approve the repair. Show the exact write in the gate; never
move silently. Two exceptions, both owned by their phase: approving a story checklist approves the move
to the sprint column, and starting a pair approves the move to the in-progress column.

**A move is one write.** `stage_id`, `state` and `date_end` in the same `odoo_update`:
→ `odoo_stage_done` = `03_approved` + `date_end`; → an active stage = `01_in_progress`; → the backlog
stage = `01_in_progress` (explicit reopen only); → the Cancelled stage = `1_canceled` (I confirm;
dependents stay blocked). Never move a subtask or an archived (`1_done`) card, and never into
`odoo_stage_done` unless every step is `1_done`/`1_canceled` and it turns green in the same write.

## Two users, one card

The card always carries the agent user — `odoo_assignee_uid` when the block declares it, else the MCP
connection uid (`odoo_connection_info` → `uid`) — and carries `odoo_assignee_manual_uid` only while the
**next open step** is `[you]`. Next open = the lowest `sequence` child whose state is not
`1_done`/`1_canceled`; `02_changes_requested` is open, for its own owner. A legacy card with no
children takes the owner from its `<h2>Checklist</h2>` line; a card with neither is left alone. Creates
send the full set; updates diff with `[[4, uid]]`/`[[3, uid]]`, never `[[6,0,[…]]]`, and add the agent
when it is missing. Derived from the checklist, so it is reported, not asked. No manual uid → no
handoff: ask once and offer to add `odoo_assignee_manual_uid` to the block. A person I name still
resolves the exact `res.users` name or login, 0 or 2+ matches → stop.

## Who writes what

The agent writes the description (story), its `Evidence` tail (pair), subtask states, `stage_id` to the
sprint column (story) and to the in-progress column (pair's start), `state=03_approved` + `date_end`
(close), `state=02_changes_requested` (review) and the derived `user_ids` diff (every phase except
archive). `/ai-daridev-archive` alone sets a card `1_done` and writes `docs/ai-daridev/log.md`. No skill
sets `1_canceled` on a visible card unless I ask or approve it; the hidden dropped-step marker is the
exception. Never write `depend_on_ids`: only backlog and story add links, and nothing removes one.

## Evidence upload

Pair captures and stores the image first, under `docs/ai-daridev/evidence/`; review never captures.
Upload each image to `ir.attachment` (`name`, base64 `datas`, `res_model=project.task`,
`res_id=<main card>`, `mimetype`), then read the card's `description`, `write_date` and `user_ids`, and
write it back with one entry appended and the assignee set reconciled for the new next open step —
never regenerate the description, never touch the text above the `<h2>Evidence (ai-daridev)</h2>`
heading. If `write_date` changed between the read and the write, re-read and append to the new text.
Verify before flipping: the description contains `/web/image/{id}` **and** the attachment row is
`project.task` on this card, `image/*`, `file_size > 0`; a heading or an id in `attachment_ids` is not
proof. If the upload or the embed failed, print `EVIDENCE FAILED: <what>` and stop the flip on a card;
in chat-only mode report it and continue. On retry create a new attachment, leave the orphan, never
delete.

## Odoo unavailable

Print what it would have written and continue; the files are still written. Never guess a project, a
stage or a user id.
