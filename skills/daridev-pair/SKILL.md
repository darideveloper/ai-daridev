---
name: daridev-pair
description: Executes an approved plan at the pace you choose — straight through, one step at a time, or manual steps batched — check red, minimum code, check green, screenshot on the card. Never implements a [you] step without your do it, never reviews, never archives, never commits.
disable-model-invocation: true
---

# Pair

You drive, I navigate. The pace is yours; a step stops only when the plan, the pace or a handoff
says so.

**Mode first.** The literal first line, nothing before it:
`Odoo: on · <project> · card #<id> "<name>"` or `Odoo: off · chat-only`.
A card, slug or flag decides; with nothing it is off and you do not ask.

Before the first write, read `../daridev-odoo/SKILL.md`: it owns the root memory and, on Odoo,
mode, stages, moves, assignees and the evidence upload. Never restate it.

## Open

- Card via MCP, or the brief pasted, or the plan already approved in this conversation. No plan →
  propose one with `/daridev-plan`'s rules, one gate, continue.
- Worktree: in the canonical checkout, ask `Worktree or current branch? [worktree]` before p1 and
  follow the `AGENTS.md` worktree block — it owns when to ask and what follows.
- On: read `depend_on_ids` first. A blocker not `1_done` outside Cancelled stops the run with one
  line and what unblocks it. Then move the card to the in-progress column (one write, reported, not
  asked; skip when already there, in the validated column, Cancelled or `1_done`). Checklist = the
  `Steps` block of the description; the subtasks supply only `state`, by `sequence`, and the block's
  `check:` line is what step 1 runs. No `Steps` block → legacy card: read the subtask names and
  descriptions, and say so once.
- Off: the checklist is the approved steps in the conversation.

## Pace

One question per session, after the worktree answer and before p1:

`Pace: step by step [step] · straight through [run] · manual steps batched [batch]`

- `run` (default) — every step in order; a `[you]` step is the handoff below, and nothing after it
  starts until I answer.
- `step` — the same run, stopped after every step for my yes: the report line first, then wait.
- `batch` — every `[agent]` step first, then the `[you]` ones as one block, but only those nothing
  later depends on; a manual step a later step needs is handed off in place and the line says why.
  When unsure, in place. Verify them in order and flip as each passes; the first red leaves it and
  everything after it open.

My words already answer it — do not ask again, and never twice in one session. No answer (a
subagent) → `run`. My words set or change the pace for the session; the card is never rewritten.
Switching pace mid-run never drops a deferred step — it still arrives as the one block.

## Handoff

A `[you]` step, in any pace:

```
p5 "<step>" — [you]
  what:  <the command, click path or value, exactly>
  files: <the step's files: line>
  check: <the step's check: line, or what to look at>
  then:  say done with its output — or "do it" and I take p5.
```

A check that is a command: run it on "done" and flip on green. Nothing runnable (a decision, an
approval, a key): observe what the step names — a URL, a value, a file — and capture it; otherwise my
word is the proof and the step's `<code>` line reads `manual — confirmed by you`, never a passing
command. Capture the result read-only on the chosen surface, asking the screenshots question first when
this is the first visual step; a proof that needs a click that writes, or a login I do not hold, is my
screenshot, labelled `[you]`. Never touch the files a `[you]`
step names while it is open. A legacy step with no `files:` or `check:` line prints what the subtask
carries, asks once for the missing check, and omits an empty line. A step the plan gave you and I run
reports `p5 done by agent (planned [you])`; the card text is never rewritten.

## Per step — no stop unless the pace or the owner says so

A `[you]` step prints the handoff above and waits: on "done" verify and flip, never implement it. In
`step` pace, stop after the report line and wait for my yes.

1. Write the check named in the plan.
2. Show it fail.
3. Minimum code to pass.
4. Show it pass.
5. Visual step → before the first one, ask once
   `Screenshots from prod, staging or local? [prod]` (default prod when deployed, local when not)
   and keep it. Capture on that surface at 1600×1000, mask client data, save under
   `docs/records/evidence/<date>-<slug>/pN-<step>.png` (the memory root: `docs/ai-daridev/evidence/`
   in a legacy repo). Create that evidence folder and its `.gitignore` (`*` and `!.gitignore`) when
   missing. With MCP: attach it to the card, append the
   gallery entry to `Evidence (daridev)` (create the heading only when missing, after `Review` and
   before the slug), and verify the attachment row on the card and the gallery entry before
   flipping. Without MCP: print the handoff label and the upload instruction (see Close).
   Non-visual → one `<code>` line under the label.
6. Flip the subtask to `1_done` (on) and report.
7. `Plan 4/7 · next p5 "<step>" ([agent|you])`.

Stop immediately on: a design decision not in the plan; adding something not asked; a change that
needs a test changed, skipped or deleted; two attempts without green; >50 lines or >3 files. A
missing or wrong check is a plan change — stop and ask.

## Close (only when every step is green and I say yes)

- List open steps: flip, leave the card open, or drop (`1_canceled` + ` (dropped)`, never deleted).
- **Green dot.** On, once no step is open and I said yes: one write `state=03_approved`, stage
  untouched, no `date_end` — green in the column it already sits in, never the validated column.
  Skip an archived, cancelled, validated or already-green card. It is not a review pass: only the
  `Review` block proves that.
- Propose one sentence for `docs/records/spec.md` under `## <domain>` when behaviour changed; on
  yes, create the file (`# Spec` header) when missing instead of only printing the line.
- Print the handoff: what shipped, the spec line, the card state, the step summary,
  `worktree: removed|kept <path>`, and the commit message for me to run.
- **No MCP:** print one block per step, in order, each with its local path and label, plus the
  upload instruction:

  ```
  Open the screenshot and confirm it shows the step. If it does, open the card in Odoo,
  add each label under Evidence (daridev), and paste its image under it. If you cannot
  edit the card, send the files to the reviewer.

  p5 "<step>" — [agent] · local — not deployed
     docs/records/evidence/<date>-<slug>/p5-<step>.png
  ```

  A non-visual step prints the same label and the `<code>` line to paste.

## Never

Implement a `[you]` step without my `do it`, review yourself, archive, move the card forward, set
`1_done` or `date_end`, green a card with an open step, commit, write `log.md`, rewrite the
description, write a subtask description, add what the plan does not name. Never print a bare id.
