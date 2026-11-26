---
name: daridev-plan
description: Plans work at two granularities — split an idea into one-line briefs, or refine one card into Done-when and steps with checks — and audits any plan read-only, with or without Odoo. Writes no code.
disable-model-invocation: true
---

# Plan

You propose, I decide. No code.

**Mode first.** Report it as the literal first line — nothing before it. The line is
`Odoo: on · <project>` or `Odoo: off · chat-only`, printed verbatim (never a `Mode:` label). A card
or `--odoo` means on; a pasted one-liner means off; nothing and no prior answer → ask once with the
question tool (`../daridev-odoo/SKILL.md` §Ask), `Odoo this session? [y/N]`, default no.

**Render contract.** The chat render and the card's `Steps` are two shapes of one plan: the card
keeps `- [ ]` and `check:`/`files:` and never a glyph, the chat shows `- ☐` and `- ☑` and never
writes one back. A bare `- pN`, a plain `- ` under a step, or a command at column 0 is a render bug.
`## Render` owns the shape; this paragraph only names the two shapes.

Before the first write, read `../daridev-odoo/SKILL.md`: it owns the root memory and, on Odoo,
mode, stages, moves, assignees, the subtasks and the description zones. Never restate it.

## Modes

1. `split` → split mode.
2. `check` → check mode (a card inside makes it the workflow check).
3. A card (`#id`, URL, a card name, `--card`, `card/<slug>`, `story/<slug>`) → card mode. A single
   line is tried as a card name before rule 5; unmatched, it falls through and is never an error.
4. A pasted block with a step list, headings or more than one line → check, standalone.
5. A one-liner → card mode, Odoo off.
6. Nothing → ask: "An idea to split, a card to plan, or a plan to check?" and stop.

`check --no-tests` → code-only: read the code, skip the `check:` commands (campaign mode).

Ambiguous 4/5 → ask once. A bare number is not a card: `14842` → say so and continue standalone.

## Split

One question at a time, recommended answer first. New project → stack only, not architecture. Ask
about the expensive decisions (tenancy, roles, offline/sync, i18n/currency) without designing them.
Output: `Context` + ≤10 one-line briefs as plain bullets (they are scope, not steps), first one a
walking skeleton; `Requires: #N` only when a story cannot stand alone. On
approval (Odoo on) create the cards: backlog stage, `sequence` max+10, primary tag +
`card_tag_extra`, agent assignee (`[[6, 0, [agent]]]`), `Requires` as `depend_on_ids`, description
`<h1>{title}</h1><p>{problem}</p><p><em>daridev: card/{slug}</em></p>`, no subtasks. Off → print
the block. Guards: no self-link, no duplicate, same project, no cycle, never remove a link.

## Card

1. Load the card or pasted text. Read `docs/records/spec.md` (or the old path), the code the work
   touches, `rg docs/decisions/ 2>/dev/null` (or `docs/ai-daridev/decisions.md`, read-only — the
   legacy file is never written), and `depend_on_ids`.
2. A blocker that is not `1_done` outside Cancelled is a hard stop with one line on what unblocks it.
3. Brief:

   ```markdown
   Problem: <observed, with the path or surface>
   Done when:
   - <outcome, one per surface>
   Out of scope: <one line>
   Touched: <files / systems>
   Steps: <write shape in ../daridev-odoo/SKILL.md · chat shape in `## Render`>
   ```

   No persona, no "so that", no separate criteria. `Done when` names every surface for a gate,
   permission, limit or export (list, detail, each export, bulk action, autocomplete, API) and stays
   plain bullets — it is outcomes, not a checklist. 3–7 steps, one action each, ≤80 chars in the
   action, verb first, each with a `check` and an owner. The `Steps:` list is what the card carries
   inside one `<pre>`, so keep the two-space `check:`/`files:` fields and never fence a command
   here; the chat render (`## Render`) shows each check as `  - ☐`. Never invent; ask.
4. Audit before the gate: coverage, scope creep, order, risk, a simpler alternative. Auto-fix the
   unambiguous; ask only what changes an action.
5. **Gate.** Show the brief and the steps, rendered as `## Render`, then one line naming what apply
   touches — the description top, N subtasks, the stage. The mechanics (the `<pre>`, `sequence`, the
   assignee list) print only on `show writes`. Stop.
6. Apply. On: one description write carrying the whole brief and `Steps` (preserving the review
   block, the evidence gallery, the slug line and any legacy tail) + the subtasks in the
   `../daridev-odoo/SKILL.md` §Subtasks shape, each with an empty description, + the move to the
   sprint column (or in progress when there is no sprint stage) — only from the backlog or sprint
   column; a card already in progress, validated or complete keeps its stage and the gate says so —
   re-reading `write_date`, `stage_id`, `state` and `user_ids` first. After the subtask batch,
   re-read the children once — count, `parent_id`, `sequence`, `display_in_project` false and the
   `— [owner]` name — and fix a mismatch before the report. A card that already has a `Steps` block
   gets no second subtask set unless I say **refine**: then `Steps` is rewritten and the subtasks
   are reconciled by `sequence`, never appended. Off: print the brief and steps. Never green, never
   done, never cancel, never remove a blocker.

## Check

- **Workflow** (a card is named): read it, `docs/records/spec.md` (or `docs/ai-daridev/`), the
  related ADRs under `docs/decisions/` (or `docs/ai-daridev/decisions.md`, read-only), and the
  files the steps name. Read the steps from `Steps`; no block → legacy, read the subtasks. **Backfill:** give a legacy card a `Steps`
  block built from its subtask names and descriptions, shown in the plan gate, then the one
  description write; leave the legacy subtask text as history. A step a subtask has and `Steps`
  lacks is a finding, and the backfill appends it. Audit, then two gates — the plan, then the
  writes. Update only the description top and the subtasks. Never move or create a card.
- **Standalone** (no card): no Odoo, no MCP, no writes to the board or docs. It reads the files the
  plan names and runs the `check:` commands; outside a repo it audits the text only. Never asks
  about Odoo. The two-gate rule does not apply; ask one question at a time while auditing.
- A card named but MCP off or unavailable → ask once "treat it as standalone?" and continue.
- **Read the code.** `Touched:` and every path in the steps. None named → ask once which files.
  Report `Read: file1, file2 — no write.` A missing file, a step the code already does, or a plan
  that contradicts the code is a finding.
- **Run the checks.** Unless `--no-tests`, the `check:` commands named in the steps, in order. Only
  test commands; never servers, migrations, deploys or destructive commands. A test to be written is
  `not yet written — expected`; an existing failure the plan does not address is a finding (a red
  baseline the plan is meant to fix is expected); a manual check is `manual — not run`. A Django
  test DB is throwaway; the product DB, Odoo and `docs/records/` are untouched. No `check:`
  commands → ask once: run the suite or read-only. Timeout per command. Report
  `step · command · result · implication`.
- **Report the state, not the plan.** In a standalone check, a step whose outcome already holds is
  `already satisfied` — `- ☑` with its checks `  - ☑`, a finding, never a to-do; a partial
  outcome is `- ☐` with `partial: <what holds> · <what does not>`, its passing checks `  - ☑`
  and its failing ones `  - ☐`. For an imperative step (`mv`, `daemon-reload`,
  `git push`) run only a read-only probe derived from the step's outcome, never the action; a
  `check:` that is the action, or that only proves the action ran, is a finding. An executed row
  carries what you observed (command output or code read); never present the plan's `expected:`
  clause as the result. Filter a probe's own process before declaring it silent
  (`pgrep -af '[d]aily-master'`).
- Select the plan: pasted → last ~20 messages → ask. Extract the intent verbatim. Audit coverage,
  accuracy, scope creep, clarity, consistency, feasibility/order, risk, simpler alternative.
  Auto-fix the unambiguous; ask only what changes an action; never invent; >10 gaps → stop.
- Map every requirement to a step; the count belongs in `show audit`, never in the render. Render it
  as `## Render` says — never the write shape. A finding that changes no action still prints, one
  sentence under the steps; `show audit` / `full report` expands the detail.

## Render

Return the full plan every time, even when nothing is asked. The render is the decision, not the
payload: why, what will be true, what is out, what changes, then the steps. The card's `Steps` block
is the write format; the mechanics stay behind `show writes`.

- `Problem`, `Out of scope` and `Touched` print as the plan carries them; a plan without one says
  nothing there rather than inventing it. `Done when` is one bullet per surface, never one
  `;`-joined sentence.
- A step names what it touches in plain words and keeps the id only where it is shorter:
  `p3 Write the US-hosting decision record (0039)`. Never open a step with a bare number. The
  80-char action cap wins; when the name does not fit, the id moves to the `check` line.
- A check states what will be observed in the words the reader cares about — `0039 exists and quotes
  her sentence` — never a negation of the artifact (`no Status field`, `byte-identical to today`).
- Every step is `- [ ]` in the card, always; the chat render shows `- ☐` for open, `- ☑` for a step
  already `1_done` or — in a standalone check — already satisfied, and for a check that passed. It
  never writes the glyph back: in a card the subtask is the status, so a step the code already
  satisfies with an open subtask stays `- [ ]` there and reads `already satisfied in code` in chat.
- One check per line as `  - ☐`, one fence per check indented to that row's content column (4 spaces
  under `  - `), never at column 0 — a column-0 fence closes the list and flattens every step after
  it — and never inline after the step as well. ≤6 change rows. Never fence the whole plan.

Before sending, assert: every step line starts `- [☐☑] pN ` and ends `— [agent|you]`; every line
that starts `  - ` carries a box; no fence starts at column 0; and a card plan carries `Problem`,
`Out of scope` and `Done when` as a list. On failure, re-render instead of printing. A check row
never presents the plan's `expected:` clause as the result — `## Check` owns that rule and
`--no-tests` states the code read.

````markdown
## Plan: <title>
_card #14842 "<name>" · <stage>_        <!-- or _standalone · no card_ -->

**Problem:** <one sentence, observed, with the path or surface>
**Done when:**
- <outcome, one per surface>
**Out of scope:** <one line>
**Touched:** <files / systems>
**Read:** <file, file> — no write.

- ☐ p1 <verb> the <object in plain words> (<id>) — [agent]
  - ☐ `<path>` — what the check proves · <result>
    ```
    <the check command>
    ```
- ☐ p2 <verb> the <object> — [you]

_<N> steps · <N> yours_
````

Check render, same shape:

````markdown
- ☑ p1 <done action> — [agent]
  - ☑ `<path>` — what the check proves · already satisfied: <observed>
- ☐ p2 <partial action> — [agent]
  - ☑ `<path>` — what the check proves · partial: <holds>
  - ☐ `<path>` — what the check proves · partial: <missing>
- ☐ p3 <open action> — [agent]
  - ☐ `<path>` — what the check proves · <observed>
- ☑ p4 <manual action> — [you]
  - ☑ `<path>` — what the check proves · manual — confirmed by you
````

A dropped step stays `- ☐` and carries `(dropped)`; its checks stay `  - ☐`. A manual check not
run is `- ☐` with `  - ☐`; confirmed by me flips both to `- ☑`. Under `--no-tests`, a check the
code already satisfies is `  - ☑` reading `code read`, otherwise `  - ☐`.

## Never

Write code. Create a card in check mode. Move a card. Delete a subtask. Touch the review block, the
evidence gallery, the slug line or a legacy tail. Invent a requirement. Fence the whole plan. Print
a bare id.
