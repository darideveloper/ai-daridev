---
name: ai-daridev-story
description: Takes ONE user story from the backlog, adds 2-3 acceptance criteria and a 5-20 step plan (one hidden Odoo subtask per step) for approval. Writes no code; implementation is /ai-daridev-pair's job.
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
4. **Plan.** 5–20 steps, one verifiable action each: verb-first, ≤80 chars, no code in the name.
   Under each step add a detail sub-bullet with what the implementer needs (file, command, rollback)
   when you already read the code. Mark every step `[agent]` or `[you]`: who can actually do it.
   More than 20 steps is not a bigger plan, it is a story that should be split.
5. **Wait for my approval.** We adjust until I say yes.

## Rules

- **Don't invent requirements.** If information is missing, ask me.
- **The simplest thing that meets the criteria.** No abstractions, layers, configuration or patterns "for the future".
- **The plan is the checklist.** Each step becomes one hidden Odoo subtask and is flipped as work is verified. No separate "markers".
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
- p1 <step> — [agent]
  - <detail: file, command, rollback>
- p2 <step> — [you]
- ...

Each acceptance criterion is covered by at least one step. One step may carry several tests; a
step flips only when every test covering it is green.

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
`tags`, `uid`, `listing`, `plan_steps`, `assignees`). If the command is missing, stop and say: run
`./scripts/setup.sh` from the ai-daridev repo. If it exits non-zero, print its `errors` and stop —
do not ask, do not guess, do not read `AGENTS.md` yourself. Print its `warnings` once, then continue.

**Odoo** — the project-management MCP tools (`odoo_search_read`, `odoo_update`, `odoo_create`):

- Find the card by `project_id = <resolved id>` and `description ilike "engram: story/<slug>"`.
- Found → update `description` only. Never touch `stage_id`, `state`, `sequence` or tags.
- Not found → ask me "create it in Backlog?" before writing anything. If I say yes, create it in
  the project's first stage with one tag, `sequence`, and `user_ids: [[6,0,[]]]` (Odoo assigns the
  creator by default) — same rules as `/ai-daridev-backlog`.
- **Plan steps** — the plan is the checklist, and its steps are the card's subtasks. Read the
  children first and index them by the key in `description` (`ai-daridev: plan/<slug>#pN`), falling
  back to a normalized name only for legacy children. Then create/update in one batch:
  - `name`: the step (`pN` is not part of the name),
  - `description`: `<p>ai-daridev: plan/{slug}#p3</p>` followed by the detail HTML,
  - `sequence`: step index × 10,
  - `parent_id`, `state=01_in_progress`, `user_ids=[]`, **`display_in_project=False`**
    (`project_id` is computed from the parent and must not be written), no `stage_id`.
  Read one back: if `display_in_project` is not false, stop and report. Never delete a child here:
  missing/dropped steps are a conflict for `/ai-daridev-pair` to resolve.
- **Two gates.** First the plan approval (content). Then a separate write confirmation listing the
  target card, the new `description` and "N subtasks", with the ids that already exist. Only on that
  `yes` apply in this order: card → subtasks → description (with the `Plan:` id line) → read back.
  Your permission rules may still prompt once per created record; that is the MCP configuration,
  not a third decision.
- Missing tools → if Odoo is unavailable, continue and print the handout below. Engram is
  required: if the memory tools are missing, stop before doing anything.

**Engram** — the memory MCP (`mem_save`). Two records, both upserts:

- `story/<slug>` (type `architecture`): the story title, acceptance criteria, out of scope, test
  names and `odoo_task_id`. **No plan here** — the plan has its own record.
- `plan/<slug>` (type `architecture`): the ordered steps with their keys, owner and detail, plus
  `odoo_task_id`. This is the intent; the card's subtasks are its mirror. If a step list already
  exists, diff against it first: changed keys keep their key, removed steps are marked `dropped`
  (never deleted), and new steps get the next free `pN` — keys are never reused.
- When Odoo is unavailable, set `pending_sync: <YYYY-MM-DD>` in `plan/<slug>` so the next run
  offers to apply it.

If the answer carries `judgment_required`, ask me once and resolve it with `mem_judge_many`
(`candidates[].judgment_id`). Never drop the memory silently.

**Export the memory.** After saving, run `engram sync` in the repo root and commit only that:

- if it reports nothing new, stop here;
- `git add .engram/`;
- if HEAD is detached, a merge is in progress, or `.engram/` has conflicts, report and skip the
  commit — the sync already happened;
- `git commit --only -m "chore: memory — story <slug>" -- .engram/`, so anything else I staged is
  untouched; never `--no-verify`, never push.

## Card body (HTML)

Regenerate the whole `description` — never append. Escape `<`, `>`, `&`. Keep this order, and keep
the `Plan:` line and the `engram:` key:

```html
<h1>{the card's CURRENT name, read it first}</h1>
<p>{one-line goal}</p>
<h2>Acceptance criteria</h2>
<ul><li>Given …, when …, then …</li></ul>
<h2>Plan</h2>
<ol><li><b>p1</b> {step}<ul><li>{detail: files, command, rollback}</li></ul></li></ol>
<h2>Tests</h2>
<ol><li>{test name} — {where it runs} — covers p1</li></ol>
<p>Plan: p1=14843 · p2=14844</p>
<p><em>engram: story/{slug}</em></p>
```

**Preserve the review block.** If the description already has a `<h2>Review (ai-daridev)</h2>`
section, copy it verbatim and re-insert it between the tests and the `Plan:` line. It runs from that
heading to the `engram:` line (exclusive) and belongs to `/ai-daridev-review`.

The `<h2>Plan</h2>` list is the human view (name + detail, **no status**). The `Plan:` line is the
machine view: keys and Odoo ids only, rebuilt from the children after every write. It is never the
authority — if it disappears or is edited, rebuild it.

**Render the plan** after the write. Full list on any plan change, including a state flip; a
single `plan N/M · next pX` line only when nothing changed:

```
Plan · <slug> · 4/9 done · 1 dropped · synced
- [x] p1 Re-export live automations — agent — done
- [x] p2 Charge in one statement — agent — done
- [ ] p3 409 response — agent — changes requested
- [ ] p4 Drop project join — agent — dropped
- [ ] p5 Staging test with a 1-use code — you — open

next: p5 (you)
```

Without Odoo the footer says `not synced` and the state comes from `plan/<slug>`.

## Without Odoo

Print a copy-paste handout and write nothing:

- the card title and the state to set,
- the full HTML description above (with the `Plan:` line and the key),
- the steps to create manually (name, key, owner, detail) and their state (`01_in_progress`),
- where to paste it and the reminder that the column belongs to the owner.

The H1 uses the live task name, so renaming the card in Odoo is not reverted on the next update.
No `<pre>` for prose; monospace only for code.
