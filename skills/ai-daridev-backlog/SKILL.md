---
name: ai-daridev-backlog
description: Turns an idea into a short backlog of vertical one-line user stories and creates the Odoo cards. No acceptance criteria, no plan; that is /ai-daridev-story's job.
disable-model-invocation: true
---

# Backlog

Split what I tell you into vertical user stories. I bring the requirements; you order and slice them.

## Conversation

1. Listen. If something is unclear, ask — one question at a time, with your suggested answer.
2. New project → discuss the stack only, not the architecture.
3. Ask whether these expensive-to-change decisions apply; do not design them: multi-tenant,
   permissions or roles, offline or sync, multi-language or multi-currency.
4. Propose the backlog; I adjust it.

## Rules

- **Don't invent requirements.** Only split what I told you; a gap gets a question.
- **Each story delivers value on its own** and cuts through every layer. Never split by layer.
- **No technical stories.** "Set up the database" or "create the user model" are built inside the
  first story that needs them.
- **10 stories max**, one line each: no criteria, no technical details, no estimates, no priorities.
- The first story is the smallest thing usable end to end (walking skeleton).
- `Requires: #N` only when a story makes no sense without another. `N` is a position in this list,
  never a card id; a link to a card from an earlier run goes through `/ai-daridev-story`.

## Output

```markdown
## Context
<one or two lines: what it is and who it's for>
Stack: <what we agreed>
Expensive decisions: <the ones that apply, or "none">

## Backlog
1. As a <actor>, I want <action>, so that <benefit>.
2. As a <actor>, I want <action>, so that <benefit>. Requires: #1
```

## Cards (Odoo only)

On approval, create the cards in one ordered batch, story 1 first. Slug = kebab-case of the title,
≤40 chars; skip a story whose card already carries `ai-daridev: story/<slug>` (or the legacy
`engram: story/<slug>`).

- `name`: the story title, with any `Requires: #N` removed. `project_id`: resolved. `stage_id`: the
  backlog stage (lowest `sequence`).
- `sequence`: `max(sequence in project) + 10, +20, +30…`.
- `tag_ids`: one primary tag — the repo's `card_tag` unless the work clearly belongs to another of
  `frontend`, `backend`, `infrastructure`, `script` or `workflow`. When the block declares
  `card_tag_extra`, add that tag too, so the card carries both.
- `user_ids: [[6,0,[<agent>]]]`, so the card belongs to the agent user — the block's
  `odoo_assignee_uid` when declared, else the MCP connection uid; no connection uid → omit
  `user_ids` and let Odoo assign the creator. If I name an assignee,
  resolve the exact `res.users` name or login and use that id instead; 0 or 2+ matches → stop and
  list. No `state`, no deadline unless I gave one.
- Description, exactly:
  `<h1>{title}</h1><p>{As a …, I want …, so that …}</p><p><em>ai-daridev: story/{slug}</em></p>`
  — the `Requires: #N` clause is not prose and never appears here.
- No subtasks; `/ai-daridev-story` owns them.
- **Dependencies.** Put a backward `Requires: #N` (the target card already exists) in the create
  call itself: `depend_on_ids: [[4, <id>]]`. After the batch, one pass writes the remaining forward
  references and the links for cards that already existed. Append, never `[[6, 0, …]]`, so a link
  set by hand in Odoo is never wiped. A `Requires` whose target was denied or never created stops
  the batch and lists it.
- Guards: no self-link, no duplicate, same project only, and no cycle — walk the blockers' existing
  `depend_on_ids` together with the links this batch is about to add. A loop stops the batch and
  shows it. Never remove a link.
- Report a table: id · name · stage · tag · blocked by. `blocked by` holds card ids; the approved
  block above already shows the `#N` positions. If I deny an approval mid-batch, stop and list what
  already exists so a re-run resumes without duplicates.

Without Odoo: print the same block, the description to paste, and a reminder that the first column
is where a new card goes; `Requires: #N` stays in the list as text. Write no files.

## Always

- **Root.** Walk up from the current directory to the nearest `AGENTS.md` that holds
  `<!-- ai-daridev:start -->`. That directory is the root: read and write `docs/ai-daridev/` there
  and write nothing outside it. No block → ask once: create it here, use the git root, or chat-only.
- **Config.** Read `odoo_project`, `odoo_stage_done`, `card_tag`, `card_tag_extra`,
  `odoo_assignee_uid` and `odoo_assignee_manual_uid` from the block. No `odoo_project` → Odoo is off.
  Resolve the project and the tags by exact name; 0 or 2+ matches → stop and list the real ones.
  Resolve the stages **inside that project** (`project.task.type` whose `project_ids` contains it);
  a stage name that also exists in other projects is not a match and must not stop the run.
  Backlog stage = lowest `sequence`. Default tag `backend`.
- **Moves and assignees are proposed, not assumed.** Move a card only when I ask in this turn, when
  the phase gate lists it and I say yes, or when the column and the state already disagree and I
  approve the repair. Show the exact write in the gate; never move silently.
- **A move is one write.** `stage_id`, `state` and `date_end` in the same `odoo_update`:
  → `odoo_stage_done` = `03_approved` + `date_end`; → an active stage = `01_in_progress`; → the
  backlog stage = `01_in_progress` (explicit reopen only); → the Cancelled stage = `1_canceled`
  (I confirm; dependents stay blocked). Never move a subtask or an archived (`1_done`) card.
- **Two users, one card.** The card always carries the agent user — `odoo_assignee_uid` when the
  block declares it, else the MCP connection uid (`odoo_connection_info` → `uid`) — and carries
  `odoo_assignee_manual_uid` only while the **next open step** is `[you]`. Next open = the lowest
  `sequence` child whose state is not `1_done`/`1_canceled`; `02_changes_requested` is open, for its
  own owner. A legacy card with no children takes the owner from its `<h2>Checklist</h2>` line; a
  card with neither is left alone. Creates send the full set; updates diff with
  `[[4, uid]]`/`[[3, uid]]`, never `[[6,0,[…]]]`, and add the agent when it is missing. Derived from
  the checklist, so it is reported, not asked. No manual uid → no handoff: ask once and
  offer to add `odoo_assignee_manual_uid` to the block, then one line in the output. A person I
  name still resolves the exact `res.users` name or login, 0 or 2+ matches → stop.
- **Agents write:** the description (story), its `Evidence` tail (pair), subtask states,
  `state=03_approved` + `date_end` (close), `state=02_changes_requested` (review).
- **One approval gate per phase.** Structure asks once; state changes are reported, not asked.
- **Odoo unavailable** → print the handout and continue; the files are still written.
- **Decisions** → one append to `docs/ai-daridev/decisions.md`, only when project-wide, hard to
  reverse or a shared/ops contract. Everything else stays in the conversation.
- **Fold-in.** If `docs/ai-daridev/` is missing and `docs/decisions/*.md` or `openspec/` exists, ask
  once to fold them into `decisions.md` and `spec.md`; the originals stay as frozen history.
- **Never commit.** Never write secrets or client data into the three files.
- **Cards** are found by `<p><em>ai-daridev: story/<slug></em></p>`; the legacy
  `engram: story/<slug>` is accepted on read.
