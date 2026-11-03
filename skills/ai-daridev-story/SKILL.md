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

Read the workflow config from `AGENTS.md` (`odoo_project`, `engram_project`, `decisions_dir`).
Slug = kebab-case of the story title, ≤40 chars. If a card already carries
`engram: story/<slug>`, reuse that slug.

Memory resolves its project from the working directory. If it resolves anything other than
`engram_project`, stop and tell me to reopen the agent in the directory that holds
`.engram/config.json`. Never write memory into the wrong project, and never guess.

**Odoo** — the project-management MCP tools (`odoo_search_read`, `odoo_update`, `odoo_create`):

- Find the card by `description ilike "engram: story/<slug>"`.
- Found → update `description` only. Never touch `stage_id`, `state`, `sequence` or tags.
- Not found → ask me "create it in Backlog?" before writing anything. If I say yes, create it in
  the project's first stage (same rules as `/ai-daridev-backlog`).
- Missing tools → if Odoo is unavailable, continue and say in one line what was skipped. Engram is
  required: if the memory tools are missing, stop before doing anything.

**Engram** — the memory MCP (`mem_save`): upsert `topic_key story/<slug>`, type `architecture`,
content = acceptance criteria + plan + out of scope + `odoo_task_id`.

## Card body (HTML)

Regenerate the whole `description` — never append. Escape `<`, `>`, `&`.

```html
<h1>{the card's CURRENT name, read it first}</h1>
<p>{one-line goal}</p>
<h2>Acceptance criteria</h2>
<ul><li>Given …, when …, then …</li></ul>
<h2>Tests</h2>
<ol><li>{test name} — {where it runs}</li></ol>
<p><em>engram: story/{slug}</em></p>
```

The H1 uses the live task name, so renaming the card in Odoo is not reverted on the next update.
No `<pre>` for prose; monospace only for code.
