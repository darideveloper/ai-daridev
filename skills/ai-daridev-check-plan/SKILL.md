---
name: ai-daridev-check-plan
description: Audit and polish a plain-text plan pasted in chat outside openspec projects. Use whenever user says check plan, review plan, validate plan, polish plan, is this plan solid, or pastes steps for review. Also use when user says show audit, expand review, or full report to expand a previous lean result. Auto-fixes gaps, searches alternatives, asks only on architecture decisions, returns a lean plan with an owner-grouped checklist. Do not use for openspec changes, proposal.md/design.md/specs/tasks.md — use openspec-check-proposal instead.
disable-model-invocation: true
license: MIT
compatibility: No dependencies, chat-only. No openspec CLI, no file I/O required.
metadata:
  author: daridev
  version: "2.0"
---

Audit a plain-text plan from chat against the user's intent, then fix and verify it. This is **audit → fix → verify**: identify what's wrong, auto-fix everything possible, ask only on relevant architecture decisions or gaps, and return a final working polished plan.

**Output is lean by default.** One change table, one plan. No duplicated facts, no auditor worksheet unless asked.

**Input**: Chat text only. By default, use the plan from recent chat history (last ~20 messages). If the slash/command is invoked with a pasted plan in the same message, prefer that. Only if no plan exists in recent context, prompt for paste. Never read openspec artifacts. Never require files.

---

## Workflow Overview

1. **Audit** — extract intent, analyze plan, classify issues internally.
2. **Fix** — auto-fix all fixable items; ask via question tool only on architecture/gaps.
3. **Verify** — requirement traceability until certain, no CLI.
4. Loop audit→fix→verify up to 3 iterations, then escalate remaining issues.
5. **Output** — change table + lean plan (§4 and §7).

---

## Steps

### 1. Select the plan

- **By default, scan recent chat history (last ~20 messages) and use the most recent plan found.** If `/ai-daridev-check-plan` was invoked with a plan argument in the same message, prefer the argument.
- If multiple candidate plans exist in the window, ask which one to check via the question tool.
- Only if no plan exists in recent history, ask the user to paste it.
- Do not infer files, do not run `openspec` commands.

### 2. Extract the user's intent from conversation context

Review history to identify:
- **Original goal**: What the user wants to achieve
- **Explicit requirements**: Behaviors, constraints, features mentioned
- **Scope boundaries**: What is in or out of scope
- **Pain points**: What they want to avoid
- **Preferences**: Tech choices, patterns, conventions expressed

Quote the user's own words. Do not relabel them as "the card" or "the ticket".

### 3. Analyze the plan against intent

Compare across these dimensions:

| Dimension | What to check |
|-----------|--------------|
| **Coverage** | Are all stated requirements addressed? Any missing steps? |
| **Accuracy** | Does the plan reflect intent, or misinterpret it? |
| **Scope creep** | Does the plan add things never requested? |
| **Clarity** | Ambiguous steps that could be executed wrong? |
| **Consistency** | Do steps contradict each other or the goal? |
| **Feasibility** | Will the steps actually work in order given? Technical concerns? |
| **Risks** | Missing, understated, or misidentified risks? |
| **Alternatives** | Is there a simpler, more robust, or standard way to achieve the same? |

Classify each issue internally. You do not print these labels — they only decide **where the issue surfaces in the output**:

| Severity | Meaning | Surfaces as |
|----------|---------|-------------|
| **MISSING** | A requirement has no corresponding step | Change row (or an open decision if it is a scope choice) |
| **MISALIGNED** | Plan contradicts what the user asked | Open decision (prose) |
| **SCOPE_CREEP** | Included but never requested | Open decision (prose) |
| **CONTRADICTION** | Two steps disagree | Change row + one note line |
| **AMBIGUOUS** | Too vague to execute | Change row (or open decision if unresolvable) |
| **RISK** | Risk missing/understated | Change row, or a line under Risks in the plan |

**CONTRADICTION reclassification rule**: If two steps contradict, check either side against user intent. One side matches → AUTO-FIX the other. Neither matches → reclassify as **MISALIGNED** → NEEDS-DECISION.

**AMBIGUOUS rule**: Can the meaning be confidently inferred from stated intent? Yes → AUTO-FIX by clarifying wording. No → NEEDS-DECISION.

**Alternatives method**: Use reasoning first from your own knowledge to propose simpler or more robust options. Use websearch only if the plan involves a library, API, or version-specific choice where docs may have changed.

### 4. Output part 1 — the change table

Every auto-fix becomes one row. Do not narrate what you fixed.

```
### What changed
| Was | Now |
|---|---|
| revoke → paste replacement | paste → test → revoke |
| no proof the key is dead | curl expecting 401 |
| "full-tree scan" | `ourlivesapp/` + `git ls-files` |
```

Rules:
- **≤6 rows.** Merge related fixes into one row. If you need more than 6, the plan was too vague — say so in one line instead of listing.
- **Was** = the plan's original step, quoted or paraphrased. **Now** = the replacement, imperative.
- **One italic note line per reorder or contradiction**, naming the requirement or user statement that decided it:
  `_Reordered revoke after cutover: criterion 2 requires production on the replacement first._`
- Risks that change behavior and are not visible as a row get one line each under `### Risks` in the plan — not here.
- **Only NEEDS-DECISION items get prose.** Use a compact block, not a 4-line issue report:

```
### Open decision
**D1 — <question in one line>.** A: <option> (recommended, <why>). B: <option>. Affects <the action> only.
```

- No Summary table (`Coverage / Accuracy / Scope / Consistency…`). The footer line in §7 replaces it.
- Never repeat a fact: alternatives appear only in the plan's `### Risks`; decisions appear only in `### Open decision`.

### 5. Fix plan and apply

1. **Auto-fix everything possible** without asking: MISSING steps with obvious content, CONTRADICTION where intent is clear, AMBIGUOUS with clear meaning, all RISK additions, wording polish. Each one becomes a change-table row.
2. **Ask only on relevant architecture decisions or gaps** using the question tool. For each NEEDS-DECISION:
   - **MISSING with scope choice**: ask whether to add, and at what detail level. If no, dismiss as "acknowledged out of scope".
   - **MISALIGNED**: ask which version reflects intent — plan's or original statement.
   - **SCOPE_CREEP**: ask remove or keep-and-justify. If keep, add one-line justification to final plan.
   - **AMBIGUOUS unresolvable**: ask what they meant.
   - Label decisions `D1`, `D2`, `D3` (max 3) so the user can answer by number.
3. **Apply the rewrite** in-memory to produce the polished plan. No file edits unless explicitly requested.

### 6. Verify

1. **Requirement traceability matrix** (internal): map every user requirement from Step 2 to a step in the final plan:

   | User requirement | Action | Confidence |
   |------------------|--------|------------|
   | Req 1 | <checkbox action> | certain/uncertain |

   - Traced only if the checkbox exists and states the action.
   - Mark **uncertain** when the link is loose — don't fabricate confidence.
   - Any untraced requirement = gap → return to the fix loop or ask the user. Never invent requirements.
2. **Render the matrix only when a mapping is uncertain.** If every requirement traces with certain confidence, the footer line alone carries it. Never assert `N/N traced, certain` you cannot show.
3. **Loop**: repeat audit→fix→verify until all requirements trace with certain confidence.
4. **Iteration guard**: cap at **3 fix-verify rounds**. If issues remain, stop and present them for manual resolution.

### 7. Output part 2 — the plan

Always return the full plan in the same invocation after verify, even if no NEEDS-DECISION was asked. No second prompt needed.

Use this skeleton. It is a shape, not a script: **omit any section that has nothing to say** (no `Open decision: None` lines, no empty `Risks`).

```
## Plan: <title>

**Goal.** One sentence, ≤25 words.

**Start here** → <owner>: <the single blocking action>.   [omit if no human step]

**Touched:** `file`, `file`, `new file`, `external system` — not: <what stays untouched>.

### What changed
| Was | Now |
|---|---|
| ... | ... |

_<one note line per reorder/contradiction>_

### Steps

**Me**
- [ ] <one action, imperative verb first>
  - <detail: files, patterns, command block>
- [ ] ...

**You**
- [ ] <one action>
- [ ] ...

**Close**
- [ ] ...

### Open decision
**D1 — ...**

### Risks
- <risk and its guard>

_<N>/<N> requirements traced, certain · <N> auto-fixes · <N> open decisions_
```

Rules:
- **≤40 words per checkbox.** One action per line; details as sub-bullets.
- Group by **who acts**: `Me` / `You` / `Close`. Omit an empty group. If the plan has no human steps, drop `Start here` and the `You` group.
- Checkboxes carry no numbers: reference an action by its name (`the gate step`), never by index — in `Start here`, in open decisions, and in the traceability table.
- Commands go in a **fenced code block in the output**, copy-pasteable, with the expected result in a trailing comment. Inside this skill file the skeleton uses a `[command block]` placeholder — never nest fences.
- **Never wrap the whole plan in a fence** — it must render as markdown. Only commands are fenced.
- No `### Task list`: the checkbox steps are the task list. One list, paste-ready.
- Alternatives live in `### Risks` as one-line decisions (`used X, not Y: <why>`), never in a separate section.
- `Open decision` is the only place a question appears; max 3.

When a plan is rewritten, the plan itself is the deliverable: never leave a named card behind. If
the sync was skipped because no card was named, say so in one line so it is a choice, not an
oversight.

**If asked to expand the audit after the fact** (user says *show audit*, *expand review*, *full report*): render the detailed per-issue format below from the current conversation, without re-auditing.

```
### Issues Found

**[SEVERITY] <one-line title>**
  User asked: "..."
  Plan says: "..."
  Why it's wrong: ...
  Action: AUTO-FIX / NEEDS-DECISION
```


### 8. Sync to the card (only when a card or slug is named)

Skip this whole section unless the invocation or the conversation carries an **explicit** signal:
`#14842`, an Odoo task URL, `card 14842`, a `story/<slug>`, or a `--card <id>` argument. A bare
number never counts — it could be a year, an amount or a PR. A generic plan stays chat-only.

**Resolve.** Run `ai-daridev preflight` in the repo root. If the command is missing, fails, or
resolves no Odoo project: write nothing to Odoo, print the step diff as a handout, and — only when
Engram is available and a slug is known — upsert `plan/<slug>` with
`pending_sync: <YYYY-MM-DD>`.

**Read.** Find the card by `engram: story/<slug>` (or the id I gave). Read `name`, `description`,
`write_date` and its children (`name`, `description`, `state`, `sequence`). Index the children by
the key in `description` (`ai-daridev: plan/<slug>#pN`); a legacy child has only a name.

**Diff.** Compare the polished plan with the card:

| Case | Behaviour |
|---|---|
| step exists, same key | rename only if content changed |
| new step | propose `pN` = next free key, `sequence` = index × 10 |
| removed step | propose `1_canceled` + `(dropped)`; never delete. Only open/blocked steps can be dropped |
| reordered | propose new `sequence` values |
| memory and Odoo disagree | show both and ask; write the answer to the losing side |
| keyed child missing | a human deleted it: ask restore or drop |
| unkeyed child | never touch; list once and ask adopt or ignore, then remember the answer |
| legacy card (`Markers:` and no `Plan:`) | ask once: convert markers into steps (default) or start fresh |
| `write_date` changed after the read | re-read and re-diff before writing |

**Gate.** Structure changes need one approval with a `Was | Now` table and the exact writes.
State is untouched here. Apply: new steps → states → sequences → description (with the rebuilt
`Plan:` line) → read back `display_in_project=False`.

**Persist.** Upsert `plan/<slug>` (steps with keys, owner, state, detail; clear `pending_sync` when
Odoo applied). `engram sync`, `git add .engram/`, `git commit --only -m "chore: memory — plan <slug>"
-- .engram/` (skip on detached HEAD, merge/rebase or `.engram/` conflicts; never `--no-verify`).

**Render.** Always print the plan after this section, with or without Odoo, in the shared format
(full list whenever the plan changed, including a state flip):
ordered checklist `pN · step · owner · state`, counts footer, and `next:`.

```
Plan · <slug> · 4/9 done · 1 dropped · synced
- [x] p1 Re-export live automations — agent — done
- [x] p2 Charge in one statement — agent — done
- [ ] p3 409 response — agent — changes requested
- [ ] p4 Drop project join — agent — dropped
- [ ] p5 Staging test with a 1-use code — you — open

next: p5 (you)
```

---

## Graceful Degradation

- If plan is 1-3 lines: check coverage and clarity only; skip the change table if there are no fixes.
- If plan has no explicit goal: infer goal, mark uncertain, confirm in output.
- If no plan found in recent history: ask for it and stop.

---

## Stance

- **Thorough, not pedantic** — catch real gaps, don't nitpick wording
- **Specific, not vague** — every issue ties to what the user said
- **Actionable** — each issue is a concrete rewrite or a clear question
- **Auditor-then-editor** — every change maps to an identified issue
- **Honest about certainty** — distinguish proven traceability from best-effort inference
- **Lean, not lossy** — compress the report, never the reasoning

## Guardrails

- **Chat-only by default** — never touch openspec artifacts, never run openspec CLI. Odoo and
  `plan/<slug>` are written only through §8, and only when a card or slug was named
- **Disambiguation** — do not use for openspec changes, proposal.md/design.md/specs/tasks.md; defer to openspec-check-proposal there
- **Never implement code** — stop at the plan; implementation is separate
- **Never create files** unless explicitly requested — return plan in chat
- **Auto-fix by default** — ask only on architecture decisions or relevant gaps
- **Only apply identified issues** — no invented steps, no unapproved scope
- **Always reference the conversation** — ground issues in user statements, quoting their words
- **Don't invent requirements** — compare only against stated intent
- **Don't claim 100% on false matches** — mark loose mappings uncertain, show the matrix
- **Respect the iteration guard** — escalate after 3 rounds
- **Fact budget** — ≤6 change rows, ≤3 open decisions, one action per step, every fact appears once
- **Omit empty sections** — a section with nothing to say is removed, not filled with "None"
