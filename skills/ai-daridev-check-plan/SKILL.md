---
name: ai-daridev-check-plan
description: Audits a plan in detail (pasted or from the conversation), fixes the gaps, asks one at a time, and renders the final plan. Use when asked to check, review, validate or polish a plan, or when a plan is pasted for review. Works standalone; with a named card it also updates the checklist and the subtasks after approval.
disable-model-invocation: true
---

# Check plan

Audit a plan against what I actually asked for, fix it, and return the corrected plan. Deep analysis,
lean output.

## Modes

- **Workflow** when the invocation or the message names a card: `#14842`, a task URL, `--card <id>`,
  or `story/<slug>`. Read that card and, read-only, `docs/ai-daridev/spec.md` and the related
  decisions.
- **Standalone** otherwise: any plan in the conversation or pasted. No repo, no files, no Odoo.

A bare number is never a card: if the invocation looks like one (`14842`), say "bare `14842` is not a
card; use `#14842` or `--card 14842`" and continue standalone. A named slug with no matching card →
ask "treat it as standalone?" and wait.

## 1. Select the plan

1. A plan pasted in this message.
2. The most recent plan in the last ~20 messages.
3. Workflow mode with nothing pasted → the card's current `<h2>Checklist</h2>` and its subtasks.
4. Nothing → ask me to paste one and stop. Never invent a plan.

Several candidates → ask which one.

## 2. Extract the intent

In my words, quote: the goal, the explicit requirements, the constraints, the scope boundaries, the
pain points, the preferences. Do not relabel them as "the card" or "the ticket".

## 3. Analyze

Check the plan on: coverage, accuracy, scope creep, clarity, consistency, feasibility and order,
risks, and a simpler or more standard alternative. Classify each issue internally; the labels never
reach the output.

Also check the checklist contract: one verifiable action per step (a compound "remove X and the Y
lines" is split), verb first, ≤40 words, an owner on every step, no duplicate step. When a card is
named, any number of steps; one action each.

Resolution:

- **Auto-fix** everything unambiguous: a contradiction where one side matches my intent, an ambiguity
  the intent settles, an obvious missing step, wording.
- **Ask** only when the answer changes an action: scope creep, a real disagreement with my intent, an
  ambiguity nothing settles, an architecture fork.
- **Never invent a requirement.** A gap with no basis becomes a question or is dropped as out of
  scope.

## 4. Ask one at a time

Ask a single question, with the recommended answer first and the alternatives after it. Wait for the
answer, update the working plan, and check again. Repeat until no gap remains.

- Use a question tool only if the agent has one; otherwise ask in prose.
- Do not batch questions.
- More than 10 gaps → stop: the plan is too vague to audit, ask me to rewrite it.

## 5. Verify

Map every requirement from step 2 to a step in the plan. An untraced requirement is a gap: go back to
step 4. Print only the footer count; show the mapping only if a requirement is uncertain.

## 6. Render

Always return the full plan, even when no question was asked. This is the shape; omit empty sections.

````markdown
## Plan: <title>
_standalone · no card_        <!-- or: _card #14842 · checklist will update_ -->

**Goal.** One sentence, ≤25 words.

**Start here** → [agent]: <the single blocking action>.

**Touched:** `file`, `file`, `new file`, `external system` — not: <what stays untouched>.

### What changed
| Was | Now |
|---|---|
| ... | ... |

_<one note line per reorder or contradiction>_

### Checklist
- [ ] p1 <one action, imperative verb first> — [agent]
  - <detail: files, patterns, command>
    ```
    <command block, indented to this bullet's content column>
    ```
- [ ] p2 <one action> — [you]

### Open decision
**D1 — ...**

### Risks
- <risk and its guard>

_5 steps · 3 agent · 2 you · <N>/<N> requirements traced · <N> auto-fixes · <N> answers_
````

Rules: ≤6 change rows (more means the plan was too vague — say so); one action per step, ≤40 words,
verb first, owner on every line; every step starts with `- [ ]` (`- [x]` when it is already
`1_done`), never a bare `- pN` — the card's `<ol>` is the write format, not the render format; no
group headings; commands in a fenced block indented to that bullet's content column (4 spaces under
`  - `, 2 spaces directly under the step), never at column 0 — a column-0 fence closes the list and
flattens every step after it;
**never fence the whole plan**. **Never print a bare id.** A step is `p4 "<step>"`, a card is
`#14842 "<name>"`; a test-list mapping is `covers p4 "<step>"`. `show audit` or `full report`
expands the per-issue detail from this conversation without re-auditing.

## 7. Workflow: update the card (only when a card is named)

Two gates. Never write before Gate 2.

**Gate 1 — the plan.** Show the render above. If I change something, go back to step 4.

**Gate 2 — the writes.** List exactly what will change on the card:

- `checklist: <N> steps` (the `<h2>Checklist</h2>` section, replaced whole),
- `+<N> subtasks`, `~<N> renamed`, `<N> dropped`, `sequence: pN…`.

Re-read the card's `write_date` first; if it changed since step 1, re-read, re-diff and show the new
writes. If nothing differs, say "the card already matches" and write nothing. The rendered checklist
is exactly what gets written: same `pN` order, same owners, same marks.

Apply in this order, then read one created subtask back:

1. Replace **only** `<h2>Checklist</h2>`. Keep the title, goal, criteria, review block, the
   `ai-daridev: story/<slug>` line and the whole `<h2>Evidence (ai-daridev)</h2>` tail byte-for-byte.
   No Checklist → replace `<h2>Plan</h2>` if it exists, otherwise insert before the review heading,
   else before the key line. Delete any old `Plan:` id line.
2. Create a hidden subtask for every missing step: `name` = `<step> — [agent|you]`,
   `description` = `<p>{detail}</p>`, `parent_id`, `sequence` = index × 10, `state=01_in_progress`,
   `user_ids: [[6,0,[<id>]]]` — the `odoo_assignee_uid` for a `[agent]` step and the
   `odoo_assignee_manual_uid` for a `[you]` step when the block declares them; with no key, omit
   `user_ids` —, `display_in_project=False`. Never `project_id`, never `stage_id`.
3. Rename changed steps (update `name`; on legacy cards, keep everything from a `<h3>Evidence</h3>`
   onward byte-for-byte and replace only the detail above it). Match names ignoring a trailing
   ` — [agent]`/`— [you]`: a legacy step without the suffix matches and is rewritten in the new
   form. Exactly one step removed and one added → ask "rename or replace?"; never guess.
4. Drop a removed step with `state=1_canceled` and ` (dropped)` appended to the name; the
   description, including any legacy Evidence block, is untouched. **Never drop a `1_done` step**: it
   stays in the checklist, marked done.
5. Update `sequence` only for the steps whose index changed.
6. Read one created subtask back: `display_in_project` must be false, else stop and report.

A second run with no changes produces zero writes.

### Never

- Create a card. No card exists → render the plan and end with "run `/ai-daridev-story`".
- Delete a subtask, touch a `1_done` state, or re-open a dropped step.
- Touch the card `state`, `stage_id`, tags or assignees.
- Regenerate anything outside the checklist section; the `Evidence` tail stays byte-for-byte.
- Write files. `spec.md` and `decisions.md` belong to `/ai-daridev-pair`.
- Invent a requirement, a step or an acceptance criterion.

## Context

- Root: nearest `AGENTS.md` with `<!-- ai-daridev:start -->`. Only needed in workflow mode.
- Config: `odoo_project`, `odoo_stage_done`, `card_tag`, `card_tag_extra`, `odoo_assignee_uid`,
  `odoo_assignee_manual_uid`; project by exact name, 0 or 2+ → stop.
- Never move a card between stages, never mark it done or cancelled, never write the card's
  `user_ids` (subtasks take their owner from the step).
- Odoo unavailable → stay standalone and say so in one line.
