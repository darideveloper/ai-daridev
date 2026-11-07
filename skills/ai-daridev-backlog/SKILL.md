---
name: ai-daridev-backlog
description: Turns a software idea or a discussed feature into a backlog of short, vertical user stories. No acceptance criteria or implementation; that's /ai-daridev-story's job.
disable-model-invocation: true
---

# Backlog

Your job is to help me split what I tell you into user stories. I bring the requirements; you order and slice them.

## Requirement

This workflow needs **Engram**, the memory MCP. If its tools are not available, stop and tell me to
install Engram and restart the agent. Do not continue without memory.

## Conversation

1. Listen to the idea or feature. If something is unclear, ask. One question at a time, with your suggested answer.
2. If it's a new project, let's discuss the stack. Only the stack, not the architecture or implementation.
3. Ask whether any of these expensive-to-change decisions apply. Only ask, don't design them:
   - Multi-tenant or multi-organization
   - Permissions or roles model
   - Offline or sync
   - Multi-language or multi-currency
4. Propose the backlog. I adjust it.

## Rules

- **Don't invent requirements.** Only split what I told you. If you see a gap, ask me; don't fill it.
- **Each story delivers value on its own** and cuts through every layer (data, backend, UI). Never split by layer.
- **No technical stories.** The actor is never the developer or the system. "Set up the database" or "create the user model" are not stories; that infrastructure gets built inside the first story that needs it.
- **Few stories.** 10–15 max. I'd rather add than cut.
- **One line per story.** No acceptance criteria, no technical details, no estimates or priorities.
- The first story is the smallest one usable end to end (walking skeleton).

## Output format

```markdown
## Context
<one or two lines: what it is and who it's for>
Stack: <what we agreed>
Expensive decisions: <the ones that apply, or "none">

## Backlog
1. As a <actor>, I want <action>, so that <benefit>.
2. As a <actor>, I want <action>, so that <benefit>. Requires: #1
```

Add `Requires: #N` only when a story makes no sense without another.

## No plan, no subtasks

A backlog card is just the story. The plan is 5–20 steps and belongs to `/ai-daridev-story`, which
creates one hidden Odoo subtask per step. Do not create subtasks or a `Markers:` line here: two
skills writing the same checklist is how cards drift.

When done, offer to save the context and stack in `AGENTS.md`. The stories go to my tracker; don't save them to files unless I ask.

## Projection (only if the tools are available)

**Preflight.** Run `ai-daridev preflight` in the repo root and use its JSON (`project`, `stages`,
`tags`, `uid`, `listing`, `plan_steps`, `assignees`). If the command is missing, stop and say: run
`./scripts/setup.sh` from the ai-daridev repo. If it exits non-zero, print its `errors` and stop —
do not ask, do not guess, do not read `AGENTS.md` yourself. Print its `warnings` once, then continue.

**Tool names.** OpenCode: `odoo_odoo_search_read`, `engram_mem_save` — inside Code Mode
(`execute`) as `tools.odoo.odoo_search_read`, `tools.engram.mem_save`. Claude Code:
`mcp__odoo__*`, `mcp__engram__*`.

**Tags** are one of `frontend` / `backend` / `script` / `workflow`. `card_tag` in `AGENTS.md` is the
**default** for this repo; pick another per story only when the work clearly belongs to it, and say
which one you picked.

**Odoo** — the project-management MCP tools (`odoo_search_read`, `odoo_create`):

1. Use the project id, first stage and tags resolved in the preflight — do not resolve them twice.
2. Read the current `max(sequence)` among that project's tasks.
3. For each story: slug = kebab-case of the title, ≤40 chars, unique within the project. Skip it
   if a card's description already contains `engram: story/<slug>`.
4. Create the cards in one contiguous batch: `sequence` = max + 10, +20, +30…, `stage_id` = the
   first stage, `description` per the card body below, exactly one tag of
   frontend / backend / script / workflow (default `card_tag`), and `date_deadline` only if I gave
   one (UTC, `YYYY-MM-DD 00:00:00`). Write `user_ids: [[6,0,[]]]` explicitly — Odoo assigns the
   creator by default — and do not write `state`.
5. Create no subtasks. `/ai-daridev-story` turns the approved plan into steps and subtasks.
6. Report a table: id · name · stage · tag. If I deny an approval mid-batch, stop and list what
   already exists so a re-run resumes without duplicates.

Card body at creation (`/ai-daridev-story` later adds criteria, plan, tests and the review block;
the `engram:` key stays):

```html
<h1>{story title}</h1>
<p>{As a …, I want …, so that …}</p>
<p><em>engram: story/{slug}</em></p>
```

**Engram** — the memory MCP (`mem_save`; `engram_mem_save` in OpenCode, `mcp__engram__mem_save`
in Claude Code). One memory:

- `title`: `backlog <engram_project>` (short, searchable).
- `topic_key`: `backlog/<engram_project>` — it upserts, so a re-run updates the same record.
- `type`: `architecture`.
- `content`: the approved block + the task ids, in `**What** / **Why** / **Where** / **Learned**`.

If the answer carries `judgment_required`, ask me once about the conflict and resolve it with
`mem_judge_many` (`candidates[].judgment_id`). Never drop the memory silently.

**Export the memory.** After saving, run `engram sync` in the repo root and commit only that:

- if it reports nothing new, stop here;
- `git add .engram/`;
- if `git diff --cached --name-only` lists anything outside `.engram/`, unstage it and stop;
- if HEAD is detached, report and stop;
- `git commit -m "chore: memory — backlog <engram_project>"`, and never push.

**Without Odoo** — print the full checklist and stop: each card's title, the HTML description to
paste, and a reminder that the first column is where a new card goes. No subtasks.`

Engram is required — if the memory tools are missing, stop before doing anything.
