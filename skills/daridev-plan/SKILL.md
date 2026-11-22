---
name: daridev-plan
description: Plans work at two granularities — split an idea into one-line briefs, or refine one card into Done-when and steps with checks — and audits any plan read-only, with or without Odoo. Writes no code.
disable-model-invocation: true
---

# Plan

You propose, I decide. No code.

**Mode first.** Report it as the literal first line — nothing before it. The line is
`Odoo: on · <project>` or `Odoo: off · chat-only`, printed verbatim (never a `Mode:` label). A card
or `--odoo` means on; a pasted one-liner means off; nothing and no prior answer → ask once
`Odoo this session? [y/N]`, default no.

**Render contract.** Every step renders as `- [ ] pN` and every check under it as `  - [ ]`; `- [x]`
only in chat, for a step already `1_done`, or — in a standalone check — already satisfied, and for a
check that passed. In a card the subtask is the status: a code-satisfied step with an open subtask
stays `- [ ]` and says `already satisfied in code`. A bare `- pN`, a plain `- ` under a step, or a
command at column 0 is a render bug — `## Render` owns the shape.

Before the first write, read `../daridev-odoo/SKILL.md`: it owns the root memory and, on Odoo,
mode, stages, moves, assignees and the description zones. Never restate it.

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
Output: `Context` + ≤10 one-line briefs as plain bullets (not checkboxes: they are scope, not
steps), first one a walking skeleton; `Requires: #N` only when a story cannot stand alone. On
approval (Odoo on) create the cards: backlog stage, `sequence` max+10, primary tag +
`card_tag_extra`, agent assignee, `Requires` as `depend_on_ids`, description
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
   here; the chat render (`## Render`) shows each check as `  - [ ]`. Never invent; ask.
4. Audit before the gate: coverage, scope creep, order, risk, a simpler alternative. Auto-fix the
   unambiguous; ask only what changes an action.
5. **Gate.** Show the brief and the steps, rendered as `## Render`, plus the exact writes
   (description with `Steps`, N subtasks with an empty description, stage/state, assignees). Stop.
6. Apply. On: one description write carrying the whole brief and `Steps` (preserving the review
   block, the evidence gallery, the slug line and any legacy tail) + the subtasks, each with an
   empty description, + the move to the sprint column (or in progress when there is no sprint
   stage), re-reading `write_date` first. Off: print the brief and steps.
   Never green, never done, never cancel, never remove a blocker.

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
  `already satisfied` — `- [x]` with its checks `  - [x]`, a finding, never a to-do; a partial
  outcome is `- [ ]` with `partial: <what holds> · <what does not>`, its passing checks `  - [x]`
  and its failing ones `  - [ ]`. For an imperative step (`mv`, `daemon-reload`,
  `git push`) run only a read-only probe derived from the step's outcome, never the action; a
  `check:` that is the action, or that only proves the action ran, is a finding. An executed row
  carries what you observed (command output or code read); never present the plan's `expected:`
  clause as the result. Filter a probe's own process before declaring it silent
  (`pgrep -af '[d]aily-master'`).
- Select the plan: pasted → last ~20 messages → ask. Extract the intent verbatim. Audit coverage,
  accuracy, scope creep, clarity, consistency, feasibility/order, risk, simpler alternative.
  Auto-fix the unambiguous; ask only what changes an action; never invent; >10 gaps → stop.
- Map every requirement to a step; print the count. Render it as `## Render` says — never the write
  shape. `show audit` / `full report` expands the detail.

## Render

Return the full plan every time, even when nothing is asked. Every step is `- [ ]` in the card,
always; the chat render shows `- [x]` for a step already `1_done`, or — in a standalone check —
already satisfied, and for a check that passed; it never writes `[x]` back — in a card the subtask
is the status. Never a bare `- pN`: the card's `Steps` block is the write format, not the render.
One check per line as `  - [ ]`, one fence per check indented to that row's content column (4 spaces
under `  - `), never at column 0 — a column-0 fence closes the list and flattens every step after
it — and never inline after the step as well. ≤6 change rows. Never fence the whole plan.

Before sending, assert: every step line matches `^- \[[ x]\] p[0-9]+ .*— \[(agent|you)\]`, every
check line matches `^  - \[[ x]\] `, no line matches `^- p[0-9]+ .*— \[(agent|you)\]` without a
checkbox, no line under a step matches `^  - (?!\[[ x]\] )`, no check command starts at column 0,
and no check row presents the plan's `expected:` clause as the result — a check states what it
observed, a plan gate states the outcome it will prove, and `--no-tests` states the code read. On
failure, re-render instead of printing.

````markdown
## Plan: <title>
_standalone · no card_        <!-- or _card #14842 "<name>"_ -->

**Done when:** <outcome, one per surface>

**Read:** <file, file> — no write.

- [ ] p1 <one action> — [agent]
  - [ ] `<path>` — what the check proves · <result>
    ```
    <the check command>
    ```
- [ ] p2 <one action> — [you]

_<N> steps · <N> agent · <N> you · <N>/<N> requirements traced · <N> findings · <N> answers_
````

Check render, same shape:

````markdown
- [x] p1 <done action> — [agent]
  - [x] `<path>` — what the check proves · already satisfied: <observed>
- [ ] p2 <partial action> — [agent]
  - [x] `<path>` — what the check proves · partial: <holds>
  - [ ] `<path>` — what the check proves · partial: <missing>
- [ ] p3 <open action> — [agent]
  - [ ] `<path>` — what the check proves · <observed>
- [x] p4 <manual action> — [you]
  - [x] `<path>` — what the check proves · manual — confirmed by you
````

A dropped step stays `- [ ]` and carries `(dropped)`; its checks stay `  - [ ]`. A manual check not
run is `- [ ]` with `  - [ ]`; confirmed by me flips both to `- [x]`. Under `--no-tests`, a check the
code already satisfies is `  - [x]` reading `code read`, otherwise `  - [ ]`.

## Never

Write code. Create a card in check mode. Move a card. Delete a subtask. Touch the review block, the
evidence gallery, the slug line or a legacy tail. Invent a requirement. Fence the whole plan. Print
a bare id.
