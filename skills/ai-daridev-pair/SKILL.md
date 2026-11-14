---
name: ai-daridev-pair
description: Pairs on one refined story. The agent drives in small test-driven steps (one test, minimum code, green) or plan-and-execute for non-code work, stops after every step, embeds a final-UI screenshot per step in the card's Evidence section, and never commits.
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
  another later stage → propose moving it back or finishing it; earlier → finish it, then archive it.
  A `1_canceled` blocker also says the dependency needs re-planning. A blocker in another project, or
  one that is a hidden subtask, stops and reports (a subtask as its parent card). No Odoo → say
  dependencies cannot be verified and continue.
- Checklist = the card's subtasks by `sequence`; fall back to `<h2>Checklist</h2>` in the description.
  A subtask name ends with `— [agent]` or `— [you]`: that is the step's owner. A legacy subtask
  without the suffix takes its owner from the checklist line; if that is missing too, ask once and
  assume nothing. If neither exists, propose the steps and get one approval before starting.
- If a step was renamed or a child disappeared, show the difference and ask once. Never recreate silently.

## 2. Mode

- Code plus a test runner in this repo → TDD (§3–§5).
- Only config/JSON/YAML or no test runner → non-code (§6).
- Both signals or neither → ask me once.

## 3. Test list

From the criteria, propose **the test list: names only**. Say where each runs and which step it
covers: `test name — where — covers p3 "<step>"`. Mark criteria that cannot be tested (visual ones) as
**manual verification**. Prefer the highest practical level. Wait for my approval; the list is the
spec. It lives in this conversation only — if the session resumes, propose it again.

## 4. Cycle

1. Write the test.
2. Run it; show that it fails (red).
3. Write the minimum code that makes it pass.
4. Run it; show that it passes (green).

One step per stop. "Do N" means N full cycles, never "N tests and then the code". After green,
embed the evidence in the card's `Evidence` section and verify it from the card before flipping.
Then send:

```
✅ Passes "<test>". <one line> (<file:line>)
Evidence: p3 entry in #<card> "<name>" · /web/image/{id} · <KB>
Plan: p3 "<step>" → done (agent) · 4/9 done · next p4 "<step>" ([agent|you])
Card: #<card> "<name>" · assignees agent + you | agent alone
Decided: <judgment call, if any>
Anything to change, or continue with "<next test>"?
```

Flip the step to `1_done` only when every test covering it is green **and** its entry is in the card's
`Evidence` section and verified. A `[you]` step flips only when I say so and its entry or waiver is
recorded. If it is unclear which step a test completes, ask.

### Evidence

One surface: the main card description. Every step's proof is a screenshot embedded in
`<h2>Evidence (ai-daridev)</h2>` at the end of that description. A file in the attachment list is not
evidence, and a subtask description is never written again.

Default artifact: a screenshot of the shipped surface, taken on the prod host after the deploy, with
`playwright-cli resize 1600 1000` then `playwright-cli screenshot`. Code, a diff or a curl is the
exception — only when the step's proof is invisible in a browser — and it is one `<code>` line, never
a `.txt` link as the only proof. A step that cannot be captured on prod because nothing is deployed
yet is captioned `local — not deployed`; that does not block the flip. Redact tokens, cookies,
passwords and keys; mask emails, names and ids unless the step is about them; prefer a test account.
Captures live in `/tmp/opencode/evidence/<slug>/<sanitized-step>/` and are deleted after the re-read;
never in the repo.

Convert to ≤500 KB with `convert` when it is available; ask me only when it is not. Upload each image
to `ir.attachment` (`name`, base64 `datas`, `res_model=project.task`, `res_id=<main card>`,
`mimetype`), then read the card's `description`, `write_date` and `user_ids`, and write it back with
one entry appended and the assignee set reconciled for the new next open step — never regenerate
it, and never touch the text above the heading. The `<h2>` goes in only when the card has none;
otherwise append from the `<h3>` down. If `write_date` changed between the read and the write,
re-read and append to the new text.

```html
<h2>Evidence (ai-daridev)</h2>                <!-- add it, at the very end, only when it is missing -->
<h3>{YYYY-MM-DD HH:MM UTC} · p4 "{step}" · [agent]</h3>
<p><img src="/web/image/{id}" alt="p4 {step} — final UI" style="max-width:100%"/></p>
<p>{one line: what the screenshot proves}</p>
```

The `<h3>` is the join to the subtask: `pN "<step>"` is the same vocabulary as the plan line and the
review verdict. One entry per attempt, chronological; a later attempt appends, it never replaces.
Extra images repeat the `<p><img/>` line. A `[you]` step gets its entry when I hand you the capture,
labelled `[you]`. Escape `<`, `>` and `&`.

Verify from the card before flipping: the description contains `/web/image/{id}` **and** the
attachment row is `project.task` on this card, `image/*`, `file_size > 0`. A heading, or an id in
`attachment_ids`, is not proof. If the upload or the embed failed, or the id is missing from the
description, print `EVIDENCE FAILED: <what>` and stop — the step stays open. No attachment-only
evidence, and no waiver unless I grant one in this turn: record
`<p><b>waiver</b> — {reason} — {who}, {UTC}</p>` inside the entry. On retry create a new attachment,
leave the orphan, never delete it. Without Odoo, print the entry and where it goes.

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

When the list is green: verify the manual criteria with me. A manual criterion checked here does not
move the card — I am already here; the handoff follows `[you]` steps only. Suggest that I run my
agent's code review; do not review yourself. Suggest a refactor only when something repeats — I
decide. Refactor only with tests green and never mixed with new functionality.

## 6. Non-code stories (n8n, server, infra, config)

1. Investigate read-only. No changes.
2. Propose a numbered plan, each step `[agent]` or `[you]`.
3. One approval of the whole list.
4. Execute `[agent]` steps one at a time. After each: the exact command, its output, the resulting
   state (diff, `systemctl status`, `docker ps`, curl) and a one-line rollback. Stop if anything
   differs from the plan. The command and its state stay in the conversation; the card gets a
   screenshot — the terminal output when the proof is a command, the UI when the step changed
   something visible (§4 Evidence, same contract).
5. Flip the step only when the state shown proves it and its entry is in the card's `Evidence`
   section and verified; `[you]` steps flip when I say so, with their entry or waiver recorded.
6. Destructive steps (`rm`, `drop`, restart, delete, migration) ask again on their own.
7. Then §7.

## 7. Close (only when the work is done and I say yes)

1. List every step that is not `1_done` and ask: flip it, leave the card open, or drop it
   (`1_canceled` + `(dropped)`, never deleted). Every closed step already has its entry in the card's
   `Evidence` section; the close only summarises it. If a step stays open, print the close block but
   keep the card gray and skip the move.
2. Card (Odoo): `state = 03_approved` and `date_end = <UTC now, YYYY-MM-DD HH:MM:SS>`, plus
   `stage_id = odoo_stage_done` when I say yes to the move — all in the same `odoo_update`. The gate
   lists the move with the default "no": the card can stay in its column for review, or land green in
   the validated column for archive. Never move it from a later stage, the Cancelled stage or an
   archived (`1_done`) card. Never mark the card done or cancelled. Reconcile the card's assignees in
   the close write from the next open step, exactly as every flip does — no open step left means the
   card stays on the agent alone. Write `user_ids` for a person I name only when I name one in this
   turn.
3. `docs/ai-daridev/spec.md`: if the behavior changed, add or replace **one sentence** in the right
   domain section (`## <domain>`), creating the file with `# <project> spec` if needed. Show the line
   in the close block.
4. Print what shipped, the decisions saved, the spec line, the card `#<id> "<name>"` and state, the
   step summary, and the commit message I should use. **Never commit.**

Never write the description above the `Evidence` heading; it belongs to `/ai-daridev-story` and
`/ai-daridev-review`. You own the `<h2>Evidence (ai-daridev)</h2>` tail at the very end of the card
description: append one entry per attempt, never rewrite it, never move it, and never repeat the step
detail there.

Without Odoo: print the close checklist (state, date, steps to flip, the `Evidence` tail, the spec
line) and write only the files.

## Always

- **Root.** Walk up from the current directory to the nearest `AGENTS.md` that holds
  `<!-- ai-daridev:start -->`. That directory is the root: read and write `docs/ai-daridev/` there
  and write nothing outside it. Evidence captures are the one exception: `/tmp/opencode/evidence/`
  outside the root, deleted after upload. No block → ask once: create it here, use the git root, or
  chat-only.
- **Config.** Read `odoo_project`, `odoo_stage_done`, `card_tag`, `card_tag_extra`,
  `odoo_assignee_uid` and `odoo_assignee_manual_uid` from the block. No `odoo_project` → Odoo is off.
  Resolve the project and the tags by exact name; 0 or 2+ matches → stop and list the real ones.
  Resolve the stages **inside that project** (`project.task.type` whose `project_ids` contains it);
  a stage name that also exists in other projects is not a match and must not stop the run.
  Backlog stage = lowest `sequence`. Default tag `backend`.
- **Moves and assignees are proposed, not assumed.** Move a card only when I ask in this turn, when
  the phase gate lists it and I say yes, or when the column and the state already disagree and I
  approve the repair. Show the exact write in the gate; never move silently. The assignee reconcile
  is the one exception: it only mirrors the checklist owner, so it rides the step's own write and is
  reported.
- **A move is one write.** `stage_id`, `state` and `date_end` in the same `odoo_update`:
  → `odoo_stage_done` = `03_approved` + `date_end`; → an active stage = `01_in_progress`; → the
  backlog stage = `01_in_progress` (explicit reopen only); → the Cancelled stage = `1_canceled`
  (I confirm; dependents stay blocked). Never move a subtask or an archived (`1_done`) card.
- **Two users, one card.** The card always carries the agent user — `odoo_assignee_uid` when the
  block declares it, else the MCP connection uid (`odoo_connection_info` → `uid`) — and carries
  `odoo_assignee_manual_uid` only while the **next open step** is `[you]`. Next open = the lowest
  `sequence` child whose state is not `1_done`/`1_canceled`; `02_changes_requested` is open, for its
  own owner. A legacy card with no children takes the owner from its `<h2>Checklist</h2>` line; a
  card with neither is left alone. Creates send the full set; updates diff with
  `[[4, uid]]`/`[[3, uid]]`, never `[[6,0,[…]]]`, and add the agent when it is missing. Derived from
  the checklist, so it is reported, not asked. No manual uid → no handoff: ask once and
  offer to add `odoo_assignee_manual_uid` to the block, then one line in the output. A person I
  name still resolves the exact `res.users` name or login, 0 or 2+ matches → stop.
- **Never print a bare id.** A step is `p4 "<step>"`, a card is `#14842 "<name>"`; a test-list
  mapping is `covers p4 "<step>"`. Tables keep a name column instead of quoted names.
- **Agents write:** the description (story), its `Evidence` tail (pair), subtask states,
  `state=03_approved` + `date_end` (close), `state=02_changes_requested` (review) and the derived
  `user_ids` diff (every phase). Never write `depend_on_ids`; only backlog and story add links, and
  nothing removes one.
- **One approval gate per phase.** Structure, a move and the close ask once; state changes are
  reported, not asked.
- **Odoo unavailable** → print the handout and continue; the files are still written.
- **Decisions** → one append to `docs/ai-daridev/decisions.md`, only when project-wide, hard to
  reverse or a shared/ops contract. Everything else stays in the conversation.
- **Fold-in.** If `docs/ai-daridev/` is missing and `docs/decisions/*.md` or `openspec/` exists, ask
  once to fold them into `decisions.md` and `spec.md`; the originals stay as frozen history.
- **Never commit.** Never write secrets or client data into the three files.
- **Cards** are found by `<p><em>ai-daridev: story/<slug></em></p>`; the legacy
  `engram: story/<slug>` is accepted on read.
