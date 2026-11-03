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
   Markers: button component · input field · form organism
2. As a <actor>, I want <action>, so that <benefit>. Requires: #1
```

Add `Requires: #N` only when a story makes no sense without another.

## Markers

Every story may carry **2–4 tracking markers**: component-sized names, no description, no dates.
They are how the implementer follows progress inside the card.

- Optional: a story with no natural breakdown gets none.
- Names only, chosen with me during the approval pass (I can edit your proposal).
- They become Odoo subtasks, hidden inside the card, and are echoed in the card description on a
  `Markers:` line so someone without Odoo access can recreate them.
- States: `01_in_progress` working · `1_done` validated · `02_changes_requested` rejected.
  Never `03_approved` on a marker: the card closes at `03_approved`, the markers use `1_done`.

When done, offer to save the context and stack in `AGENTS.md`. The stories go to my tracker; don't save them to files unless I ask.

## Projection (only if the tools are available)

Read the workflow config from `AGENTS.md` (`odoo_project`, `engram_project`, `card_tag`). If the
section is missing, ask me once for the Odoo project name and offer to add the section.

Memory resolves its project from the working directory. If it resolves anything other than
`engram_project`, stop and tell me to reopen the agent in the directory that holds
`.engram/config.json`. Never write memory into the wrong project, and never guess.

**Odoo** — the project-management MCP tools (`odoo_search_read`, `odoo_create`; they appear as
`odoo_odoo_*` in OpenCode and `mcp__odoo__*` in Claude Code):

1. Resolve the project by `odoo_project`, then its first stage (`project.task.type` where
   `project_ids` contains the project, ordered by `sequence`, limit 1).
2. Read the current `max(sequence)` among that project's tasks.
3. For each story: slug = kebab-case of the title, ≤40 chars, unique within the project. Skip it
   if a card's description already contains `engram: story/<slug>`.
4. Create the cards in one contiguous batch: `sequence` = max + 10, +20, +30…, `stage_id` = the
   first stage, `description` per the card body below, exactly one tag of
   frontend / backend / script / workflow (default backend), and `date_deadline` only if I gave
   one (UTC, `YYYY-MM-DD 00:00:00`). Do not write `state`.
5. For each card, create its markers as subtasks: `name` (normalized for comparison),
   `parent_id`, `project_id`, `state=01_in_progress`. No `description`, no `stage_id`, no dates.
   Skip a marker whose normalized name already exists among the card's children.
6. Report a table: id · name · stage · tag · markers. If I deny an approval mid-batch, stop and
   list what already exists so a re-run resumes without duplicates.

Card body at creation (`/ai-daridev-story` later adds criteria, tests and the review block; the
`Markers:` line and the `engram:` key stay):

```html
<h1>{story title}</h1>
<p>{As a …, I want …, so that …}</p>
<p>Markers: {marker 1} · {marker 2}</p>
<p><em>engram: story/{slug}</em></p>
```

When a marker is added or removed later, the `Markers:` line is rewritten to match — it is the only
way someone without Odoo access knows the list.

**Engram** — the memory MCP (`mem_save`; `engram_mem_save` in OpenCode, `mcp__engram__mem_save`
in Claude Code): one memory, `topic_key backlog/<engram_project>`, type `architecture`, content =
the approved block + the task ids.

**Without Odoo** — print the full checklist and stop: each card's title, the HTML description to
paste, the markers to create (names), their state (`01_in_progress`), and a reminder that the
first column is where a new card goes.

Engram is required — if the memory tools are missing, stop before doing anything.
