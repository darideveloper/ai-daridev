---
name: ai-daridev-story
description: Takes ONE user story from the backlog, adds 2-3 acceptance criteria and proposes a mini implementation plan for approval. Writes no code; implementation is /ai-daridev-pair's job.
disable-model-invocation: true
---

# Story

We refine a single story, right before building it. You propose and I decide.

## Requirement

This workflow needs **Engram**, the memory MCP. If its tools are not available, stop and tell me to
install Engram and restart the agent. Do not continue without memory.

## Steps

1. **Read the story** I give you (pasted text, GitHub issue, Jira ticket, etc.) and review the current code and `AGENTS.md` to understand the context.
2. **Acceptance criteria.** Propose 2–3 in Given/When/Then format. They only describe *what* the user sees or gets, never *how* it's implemented.
3. **If it needs more than 3 criteria, don't bloat it: propose splitting it.** Deliver the new stories in backlog format (`As a…, I want…, so that…`) for me to add to the tracker, and we continue with the first one.
4. **Mini plan.** 5 bullets max, no code or file names. How it cuts through the layers, with the minimum that meets the criteria.
5. **Wait for my approval.** We adjust until I say yes.

## Rules

- **Don't invent requirements.** If information is missing, ask me.
- **The simplest thing that meets the criteria.** No abstractions, layers, configuration or patterns "for the future".
- **Suggest, don't decide.** If a pattern could help (Atomic Design, middleware composition, extracting a component…), mention it under "Suggestions" with its why. Only suggest it if there's a concrete signal in the code (for example, something that already repeats), not in advance.
- **Don't write code.**

## Output format

A block ready to paste into the issue. `/ai-daridev-pair` uses it as input.

```markdown
## Story
As a <actor>, I want <action>, so that <benefit>.

## Acceptance criteria
- [ ] Given <context>, when <action>, then <result>.
- [ ] ...

## Plan
- ...

## Out of scope
- <what's left out of this story, so it doesn't sneak in>

## Suggestions (your call)
- <optional>
```

## Projection (only if the tools are available)

Slug = kebab-case of the story title, ≤40 chars. If a card already carries
`engram: story/<slug>`, reuse that slug.

**Tool names.** OpenCode: `odoo_odoo_search_read`, `engram_mem_save` — inside Code Mode
(`execute`) as `tools.odoo.odoo_search_read`, `tools.engram.mem_save`. Claude Code:
`mcp__odoo__*`, `mcp__engram__*`.

**Preflight.** Run `ai-daridev preflight` in the repo root and use its JSON (`project`, `stages`,
`tags`, `uid`, `listing`, `markers`, `assignees`). If the command is missing, stop and say: run
`./scripts/setup.sh` from the ai-daridev repo. If it exits non-zero, print its `errors` and stop —
do not ask, do not guess, do not read `AGENTS.md` yourself. Print its `warnings` once, then continue.

**Odoo** — the project-management MCP tools (`odoo_search_read`, `odoo_update`, `odoo_create`):

- Find the card by `project_id = <resolved id>` and `description ilike "engram: story/<slug>"`.
- Found → update `description` only. Never touch `stage_id`, `state`, `sequence` or tags.
- Not found → ask me "create it in Backlog?" before writing anything. If I say yes, create it in
  the project's first stage with one tag, `sequence`, and `user_ids: [[6,0,[]]]` (Odoo assigns the
  creator by default) — same rules as `/ai-daridev-backlog`.
- **Markers** — read them from the card's children, or from the `Markers:` line in its
  description. Never invent a different set. If the card has none and Odoo is available, propose
  2–4 for my approval before creating them as subtasks: `name`, `parent_id`, `state=01_in_progress`,
  `user_ids=[]`, and **`display_in_project=False`** (that flag is what hides it from the board;
  `project_id` is computed from the parent and must not be written), no `stage_id`. They are
  validated to `1_done` later by `/ai-daridev-pair` or `/ai-daridev-review`. Read one back: if
  `display_in_project` is not false, stop and report.
- Missing tools → if Odoo is unavailable, continue and print the handout below. Engram is
  required: if the memory tools are missing, stop before doing anything.

**Engram** — the memory MCP (`mem_save`). Upsert:

- `title`: the story title (≤10 words).
- `topic_key`: `story/<slug>` — it upserts, so refining again updates the same record.
- `type`: `architecture`.
- `content`: acceptance criteria + plan + out of scope + markers + `odoo_task_id`, in
  `**What** / **Why** / **Where** / **Learned**`.

If the answer carries `judgment_required`, ask me once and resolve it with `mem_judge_many`
(`candidates[].judgment_id`). Never drop the memory silently.

**Export the memory.** After saving, run `engram sync` in the repo root and commit only that:

- if it reports nothing new, stop here;
- `git add .engram/`;
- if `git diff --cached --name-only` lists anything outside `.engram/`, unstage it and stop;
- if HEAD is detached, report and stop;
- `git commit -m "chore: memory — story <slug>"`, and never push.

## Card body (HTML)

Regenerate the whole `description` — never append. Escape `<`, `>`, `&`. Keep this order, and keep
the `Markers:` line and the `engram:` key:

```html
<h1>{the card's CURRENT name, read it first}</h1>
<p>{one-line goal}</p>
<h2>Acceptance criteria</h2>
<ul><li>Given …, when …, then …</li></ul>
<h2>Tests</h2>
<ol><li>{test name} — {where it runs}</li></ol>
<p>Markers: {marker 1} · {marker 2}</p>
<p><em>engram: story/{slug}</em></p>
```

**Preserve the review block.** If the description already has a `<h2>Review (ai-daridev)</h2>`
section, copy it verbatim and re-insert it between the tests and the `Markers:` line. It runs from
that heading to the `engram:` line (exclusive) and belongs to `/ai-daridev-review`.

When a marker is added or removed, rewrite the `Markers:` line so it matches the subtasks.

## Without Odoo

Print a copy-paste handout and write nothing:

- the card title and the state to set,
- the full HTML description above (with the `Markers:` line and the key),
- the markers to create manually (names only) and their state (`01_in_progress`),
- where to paste it and the reminder that the column belongs to the owner.

The H1 uses the live task name, so renaming the card in Odoo is not reverted on the next update.
No `<pre>` for prose; monospace only for code.
