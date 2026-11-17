---
name: daridev-plan
description: Plans work at two granularities — split an idea into one-line briefs, or refine one card into Done-when and steps with checks — and audits any plan read-only, with or without Odoo. Writes no code.
disable-model-invocation: true
---

# Plan

You propose, I decide. No code.

**Mode first.** Report it as the literal first line — nothing before it. The line is
`Odoo: on · <project>` or `Odoo: off · chat-only`. A card or `--odoo` means on; a pasted one-liner
means off; nothing and no prior answer → ask once `Odoo this session? [y/N]`, default no.

On Odoo, read `../daridev-odoo/SKILL.md` before the first write: it owns mode, stages, moves,
assignees and the description zones. Never restate it.

## Modes

1. `split` → split mode.
2. `check` → check mode (a card inside makes it the workflow check).
3. A card (`#id`, URL, `--card`, `story/<slug>`) → card mode.
4. A pasted block with a step list, headings or more than one line → check, standalone.
5. A one-liner → card mode, Odoo off.
6. Nothing → ask: "An idea to split, a card to plan, or a plan to check?" and stop.

Ambiguous 4/5 → ask once. A bare number is not a card: `14842` → say so and continue standalone.

## Split

One question at a time, recommended answer first. New project → stack only, not architecture. Ask
about the expensive decisions (tenancy, roles, offline/sync, i18n/currency) without designing them.
Output: `Context` + ≤10 one-line briefs, first one a walking skeleton; `Requires: #N` only when a
story cannot stand alone. On approval (Odoo on) create the cards: backlog stage, `sequence` max+10,
primary tag + `card_tag_extra`, agent assignee, `Requires` as `depend_on_ids`, description
`<h1>{title}</h1><p>{problem}</p><p><em>daridev: card/{slug}</em></p>`, no subtasks. Off → print
the block. Guards: no self-link, no duplicate, same project, no cycle, never remove a link.

## Card

1. Load the card or pasted text. Read `docs/records/spec.md` (or the old path), the code the work
   touches, `rg docs/decisions/`, and `depend_on_ids`.
2. A blocker that is not `1_done` outside Cancelled is a hard stop with one line on what unblocks it.
3. Brief:

   ```markdown
   Problem: <observed, with the path or surface>
   Done when:
   - <outcome, one per surface>
   Out of scope: <one line>
   Touched: <files / systems>
   Steps:
   - p1 <one action> — [agent] — check: <command or test>
   ```

   No persona, no "so that", no separate criteria. `Done when` names every surface for a gate,
   permission, limit or export (list, detail, each export, bulk action, autocomplete, API). 3–7
   steps, one action each, ≤80 chars, verb first, each with a `check`, each with an owner. Never
   invent; ask.
4. Audit before the gate: coverage, scope creep, order, risk, a simpler alternative. Auto-fix the
   unambiguous; ask only what changes an action.
5. **Gate.** Show the brief, the steps and the exact writes (description, N subtasks, stage/state,
   assignees). Stop.
6. Apply. On: one description write (preserving the review block, the evidence gallery, the slug
   line and any legacy tail) + the subtasks + the move to the sprint column (or in progress when
   there is no sprint stage), re-reading `write_date` first. Off: print the brief and steps.
   Never green, never done, never cancel, never remove a blocker.

## Check

- **Workflow** (a card is named): read it, `docs/records/spec.md`, the related ADRs and the files
  the steps name. Audit, then two gates — the plan, then the writes. Update only the description
  top and the subtasks. Never move or create a card.
- **Standalone** (no card): no Odoo, no MCP, no writes to the board or docs. It reads the files the
  plan names and runs the `check:` commands; outside a repo it audits the text only. Never asks
  about Odoo. The two-gate rule does not apply; ask one question at a time while auditing.
- **Read the code.** `Touched:` and every path in the steps. None named → ask once which files.
  Report `Read: file1, file2 — no write.` A missing file, a step the code already does, or a plan
  that contradicts the code is a finding.
- **Run the checks.** The `check:` commands named in the steps, in order. Only test commands; never
  servers, migrations, deploys or destructive commands. A test to be written is
  `not yet written — expected`; an existing failure the plan does not address is a finding (a red
  baseline the plan is meant to fix is expected); a manual check is `manual — not run`. A Django
  test DB is throwaway; the product DB, Odoo and `docs/records/` are untouched. No `check:`
  commands → ask once: run the suite or read-only. Timeout per command. Report
  `step · command · result · implication`.
- Select the plan: pasted → last ~20 messages → ask. Extract the intent verbatim. Audit coverage,
  accuracy, scope creep, clarity, consistency, feasibility/order, risk, simpler alternative.
  Auto-fix the unambiguous; ask only what changes an action; never invent; >10 gaps → stop.
- Map every requirement to a step; print the count. Render the full plan: owner and check per step,
  ≤6 change rows, commands in fenced blocks indented to the bullet, never fence the whole plan.
  `show audit` / `full report` expands the detail.

## Never

Write code. Create a card in check mode. Move a card. Delete a subtask. Touch the review block, the
evidence gallery, the slug line or a legacy tail. Invent a requirement. Fence the whole plan. Print
a bare id.
