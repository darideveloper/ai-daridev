---
name: ai-daridev-pair
description: Pairs on one refined story. The agent drives in small test-driven steps (one test, minimum code, green) or plan-and-execute for non-code work, stops after every step, and never commits.
disable-model-invocation: true
---

# Pair

You drive, I navigate. One story per session, one step at a time, and you stop after each step.

## 1. Open the story

- `/ai-daridev-pair <slug>` → the card carrying `ai-daridev: story/<slug>` (legacy `engram: story/<slug>` is accepted).
- No slug → list cards in the active stages (not the backlog stage, not `odoo_stage_done`), limit 20, and ask which one. No Odoo → ask me to paste the story.
- No story at all → treat it as new: propose criteria and a checklist, one gate, then continue.
- **Blocked by (Odoo).** Read `depend_on_ids` before anything else. A blocker is satisfied only when
  its `state=1_done` and its stage is not the Cancelled stage; anything else blocks. Print
  `Blocked by #<id> "<name>" — <stage> · <state>.` and stop before proposing a mode or a test list.
  Then say what unblocks it: in `odoo_stage_done` → archive it; in the Cancelled stage → re-plan; in
  another later stage → move it back or mark it done; earlier → finish it, then archive it. A
  `1_canceled` blocker also says the dependency needs re-planning. A blocker in another project, or
  one that is a hidden subtask, stops and reports (a subtask as its parent card). No Odoo → say
  dependencies cannot be verified and continue.
- Checklist = the card's subtasks by `sequence`; fall back to `<h2>Checklist</h2>` in the description.
  A subtask name ends with `— [agent]` or `— [you]`: that is the step's owner. A legacy subtask
  without the suffix takes its owner from the checklist line; if that is missing too, ask once and
  assume nothing. If neither exists, propose 3–7 steps and get one approval before starting.
- If a step was renamed or a child disappeared, show the difference and ask once. Never recreate silently.

## 2. Mode

- Code plus a test runner in this repo → TDD (§3–§5).
- Only config/JSON/YAML or no test runner → non-code (§6).
- Both signals or neither → ask me once.

## 3. Test list

From the criteria, propose **the test list: names only**. Say where each runs and which step it
covers: `test name — where — covers p3`. Mark criteria that cannot be tested (visual ones) as
**manual verification**. Prefer the highest practical level. Wait for my approval; the list is the
spec. It lives in this conversation only — if the session resumes, propose it again.

## 4. Cycle

1. Write the test.
2. Run it; show that it fails (red).
3. Write the minimum code that makes it pass.
4. Run it; show that it passes (green).

One step per stop. "Do N" means N full cycles, never "N tests and then the code". Then send:

```
✅ Passes "<test>". <one line> (<file:line>)
Plan: p3 → done (agent) · 4/9 done · next p4
Decided: <judgment call, if any>
Anything to change, or continue with "<next test>"?
```

Flip the step to `1_done` only when every test covering it is green, and only on evidence. A `[you]`
step flips only when I say so. If it is unclear which step a test completes, ask.

### Stop immediately

- A design decision that is not in the checklist.
- Adding something I did not ask for.
- Making a test pass would need changing, skipping or deleting a test.
- Two attempts without green.
- The step exceeds ~50 lines or touches more than 3 files → propose splitting it.

### Decisions

A `Decided:` line that is project-wide, hard to reverse or a shared/ops contract → append one
section to `docs/ai-daridev/decisions.md` (create the file with `# Decisions` if needed):

```markdown
## YYYY-MM-DD — <decision>
Why: <one line>
Where: <files or systems it affects>
```

Per-step choices stay in the conversation.

## 5. Check

When the list is green: verify the manual criteria with me. Suggest that I run my agent's code
review; do not review yourself. Suggest a refactor only when something repeats — I decide. Refactor
only with tests green and never mixed with new functionality.

## 6. Non-code stories (n8n, server, infra, config)

1. Investigate read-only. No changes.
2. Propose a numbered plan, each step `[agent]` or `[you]`.
3. One approval of the whole list.
4. Execute `[agent]` steps one at a time. After each: the exact command, its output, the resulting
   state (diff, `systemctl status`, `docker ps`, curl) and a one-line rollback. Stop if anything
   differs from the plan.
5. Flip the step only when the state shown proves it; `[you]` steps flip when I say so.
6. Destructive steps (`rm`, `drop`, restart, delete, migration) ask again on their own.
7. Then §7.

## 7. Close (only when the work is done and I say yes)

1. List every step that is not `1_done` and ask: flip it, leave the card open, or drop it
   (`1_canceled` + `(dropped)`, never deleted).
2. Card (Odoo): `state = 03_approved`, `date_end = <UTC now, YYYY-MM-DD HH:MM:SS>`. Do not touch
   `stage_id` or `user_ids`. Never mark the card done or cancelled.
3. `docs/ai-daridev/spec.md`: if the behavior changed, add or replace **one sentence** in the right
   domain section (`## <domain>`), creating the file with `# <project> spec` if needed. Show the line
   in the close block.
4. Print what shipped, the decisions saved, the spec line, the card id and state, the step summary,
   and the commit message I should use. **Never commit.**

Never write the card description; it belongs to `/ai-daridev-story` and `/ai-daridev-review`.

Without Odoo: print the close checklist (state, date, steps to flip, the spec line) and write only
the files.

## Always

- **Root.** Walk up from the current directory to the nearest `AGENTS.md` that holds
  `<!-- ai-daridev:start -->`. That directory is the root: read and write `docs/ai-daridev/` there
  and write nothing outside it. No block → ask once: create it here, use the git root, or chat-only.
- **Config.** Read `odoo_project`, `odoo_stage_done` and `card_tag` from the block. No
  `odoo_project` → Odoo is off. Resolve the project, the tags and the stages by exact name; 0 or 2+
  matches → stop and list the real ones. Backlog stage = lowest `sequence`. Default tag `backend`.
- **Never move a card** between stages, never set a card `1_done`/`1_canceled`, never assign.
  Agents write: the description (story), subtask states, `state=03_approved` + `date_end` (close),
  `state=02_changes_requested` (review). Never write `depend_on_ids`; only backlog and story add
  links, and nothing removes one.
- **One approval gate per phase.** Structure asks once; state changes are reported, not asked.
- **Odoo unavailable** → print the handout and continue; the files are still written.
- **Decisions** → one append to `docs/ai-daridev/decisions.md`, only when project-wide, hard to
  reverse or a shared/ops contract. Everything else stays in the conversation.
- **Fold-in.** If `docs/ai-daridev/` is missing and `docs/decisions/*.md` or `openspec/` exists, ask
  once to fold them into `decisions.md` and `spec.md`; the originals stay as frozen history.
- **Never commit.** Never write secrets or client data into the three files.
- **Cards** are found by `<p><em>ai-daridev: story/<slug></em></p>`; the legacy
  `engram: story/<slug>` is accepted on read.
