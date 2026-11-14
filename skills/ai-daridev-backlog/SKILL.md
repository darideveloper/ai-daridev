---
name: ai-daridev-backlog
description: Turns an idea into a short backlog of vertical one-line user stories and creates the cards when the session is on Odoo. No acceptance criteria, no plan; that is /ai-daridev-story's job.
disable-model-invocation: true
---

# Backlog

Split what I tell you into vertical user stories. I bring the requirements; you order and slice them.

**Mode first.** This phase opens the session, so when the turn does not already say it (`--odoo`,
`--no-odoo`, or my words), ask once: `Odoo this session? [y/N]` — default no. Keep the answer for the
session and report it in the first line, `Odoo: on · <project>` or `Odoo: off · chat-only`.

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

## Cards (Odoo on)

Odoo off → skip this section: print the block and the descriptions to paste, and write no cards. On
Odoo, on approval, create the cards in one ordered batch, story 1 first. Slug = kebab-case of the
title, ≤40 chars; skip a story whose card already carries `ai-daridev: story/<slug>` (or the legacy
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

Odoo off: print the same block, the description to paste, and a reminder that the first column
is where a new card goes; `Requires: #N` stays in the list as text. Write no files.

## Always

- **Root.** Walk up from the current directory to the nearest `AGENTS.md` that holds
  `<!-- ai-daridev:start -->`. That directory is the root: read and write `docs/ai-daridev/` there
  and write nothing outside it. No block → ask once: create it here, use the git root, or chat-only.
- **Mode.** Cards only when this session is on Odoo, and the first line says which. Resolve it once
  and keep it: an explicit `--odoo`/`--no-odoo` or my words beat everything; a card reference means
  on; this skill opens the session, so with no signal it asks once (default no).
- **Odoo contract.** On → read `../ai-daridev-odoo/SKILL.md` and follow it for every Odoo rule:
  config, project and stages, moves, assignees, who writes what and the evidence upload. Off → print
  what it would write and write no card. Never restate those rules here.
- **One approval gate per phase.** Structure asks once; state changes are reported, not asked.
- **Decisions** → one append to `docs/ai-daridev/decisions.md`, only when project-wide, hard to
  reverse or a shared/ops contract. Everything else stays in the conversation.
- **Fold-in.** If `docs/ai-daridev/` is missing and `docs/decisions/*.md` or `openspec/` exists, ask
  once to fold them into `decisions.md` and `spec.md`; the originals stay as frozen history.
- **Never commit.** Never write secrets or client data into the three files.
