---
name: ai-daridev-pair
description: Pairs on one refined story. The agent drives in small test-driven steps (one test, minimum code, green) or plan-and-execute for non-code work, stops after every step, captures a final-UI screenshot per step into the card's Evidence section or the local evidence folder, and never commits.
disable-model-invocation: true
---

# Pair

You drive, I navigate. One story per session, one step at a time, and you stop after each step.

**Mode first.** The first line reports it: `Odoo: on · <project> · card #<id> "<name>"` or
`Odoo: off · chat-only`. A card in the invocation, a resolved slug or `--odoo`/`--no-odoo` decides it,
unless this session already answered — that answer holds. An explicit flag beats the card. With
nothing, it is off and you do not ask.

## 1. Open the story

- `/ai-daridev-pair <slug>` → the card carrying `ai-daridev: story/<slug>` (legacy `engram: story/<slug>` is accepted). Mode unknown and no card found → one question: `No card for story/<slug> — chat-only, or create it in the sprint column?` Chat-only continues from the story I paste; create turns the session on and creates the card with `/ai-daridev-story`'s rules.
- No slug → the mode is on: list cards in the active stages (not the backlog stage, not `odoo_stage_done`), limit 20, and ask which one. Mode off: ask me for the one-liner or the story; never list, never ask about Odoo.
- No story at all → treat it as new: propose criteria and a checklist, one gate, then continue.
- **Blocked by (Odoo).** Read `depend_on_ids` before anything else. A blocker is satisfied only when
  its `state=1_done` and its stage is not the Cancelled stage; anything else blocks. Print
  `Blocked by #<id> "<name>" — <stage> · <state>.` and stop before §2 or a test list.
  Then say what unblocks it: in `odoo_stage_done` → archive it; in the Cancelled stage → re-plan; in
  another later stage → propose moving it back or finishing it; earlier → finish it, then archive it.
  That guidance is about the blocker, never the card you are pairing.
  A `1_canceled` blocker also says the dependency needs re-planning. A blocker in another project, or
  one that is a hidden subtask, stops and reports (a subtask as its parent card). Odoo off → say
  dependencies cannot be verified and continue.
- **To in progress (Odoo on).** Starting the pair is the ask for this one move, and it happens before
  §2. Resolve the in-progress column: the single stage inside the project whose name matches
  `in progress` (case-insensitive). 0 or 2+ matches → ask once which stage and use that answer for
  the session; never guess. Then one `odoo_update`: `stage_id=<stage>, state=01_in_progress`, no
  `date_end`. Skip and report when the stage is already the target **and** `state=01_in_progress`,
  or when the card is in `odoo_stage_done`, the Cancelled stage or `1_done`. A failed write is
  reported and does not stop the session. Print
  `Card #<id> "<name>" — <from> → <to> · 01_in_progress`. With no slug, this happens after I pick
  the card.
- Checklist = the card's subtasks by `sequence`; fall back to `<h2>Checklist</h2>` in the description.
  A subtask name ends with `— [agent]` or `— [you]`: that is the step's owner. A legacy subtask
  without the suffix takes its owner from the checklist line; if that is missing too, ask once and
  assume nothing. If neither exists, propose the steps and get one approval before starting.
- If a step was renamed or a child disappeared, show the difference and ask once. Never recreate silently.

## 2. TDD or non-code

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

One step per stop. "Do N" means N full cycles, never "N tests and then the code". After green, run the
evidence sequence below — capture, store, embed, verify — before flipping. Then send:

```
✅ Passes "<test>". <one line> (<file:line>)
Evidence: p3 "<step>" · #<card> "<name>" · /web/image/{id} · <KB>
Plan: p3 "<step>" → done (agent) · 4/9 done · next p4 "<step>" ([agent|you])
Card: #<card> "<name>" · assignees agent + you | agent alone
Decided: <judgment call, if any>
Anything to change, or continue with "<next test>"?
```

Odoo off, the same block with two changes: the evidence line names the local path,
`docs/ai-daridev/evidence/<date>-<slug>/p3-<step>.png`, and the card line reads
`Card: none (chat-only) · <n>/<total> steps`.

Flip the step to `1_done` only when every test covering it is green **and** its entry is in the card's
`Evidence` section and verified. A `[you]` step flips only when I say so and its entry or waiver is
recorded. If it is unclear which step a test completes, ask.

### Evidence

One surface: the main card description when Odoo is on, `docs/ai-daridev/evidence/` when it is off.
Every step's proof is a screenshot of the shipped surface; a file in the attachment list is not
evidence, and a subtask description is never written again.

1. **Capture.** Take it yourself — ask me only for a `[you]` step, or when the surface needs a login
   you do not hold. Default artifact: the shipped surface on the prod host after the deploy, with
   `playwright-cli resize 1600 1000` then `playwright-cli screenshot`. Code, a diff or a curl is the
   exception — only when the step's proof is invisible in a browser — and it is one `<code>` line,
   never a `.txt` link as the only proof. A step that cannot be captured on prod because nothing is
   deployed yet is captioned `local — not deployed`; that does not block the flip. Redact tokens,
   cookies, passwords and keys; mask emails, names and ids unless the step is about them; prefer a
   test account. Navigate read-only: never click a control that writes.
2. **Store.** `docs/ai-daridev/evidence/<YYYY-MM-DD>-<slug>/pN-<sanitized-step>.png`, at ≤500 KB with
   `convert` when it is available; ask me only when it is not. Keep the file after the upload — it is
   the copy I can open later. On the first capture in a repo, create
   `docs/ai-daridev/evidence/.gitignore` holding `*` and `!.gitignore` and leave it for me to commit:
   a skill never commits, and no capture is ever written to `/tmp`.
3. **Embed.** Odoo on → upload to `ir.attachment`, append one entry and reconcile the assignees, per
   the Odoo contract. Odoo off → print the entry, its folder path and one line of caption; nothing
   else is written. The `<h2>` goes in only when the card has none; otherwise append from the `<h3>`
   down.
4. **Verify before flipping.** On Odoo, the description contains `/web/image/{id}` **and** the
   attachment row is `project.task` on this card, `image/*`, `file_size > 0`; a heading, or an id in
   `attachment_ids`, is not proof. Off, the file exists, is non-empty, and its path is the one you
   print. If the capture, the upload or the embed failed, print `EVIDENCE FAILED: <what>`: on a card
   the step stays open, and chat-only continues with the failure named in the close. No
   attachment-only evidence, and no waiver unless I grant one in this turn: record
   `<p><b>waiver</b> — {reason} — {who}, {UTC}</p>` inside the entry. On retry create a new
   attachment, leave the orphan, never delete it.

The entry, exactly:

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

1. On Odoo, list every step that is not `1_done` and ask: flip it, leave the card open, or drop it
   (`1_canceled` + `(dropped)`, never deleted). Off Odoo, the checklist in this conversation is the
   record: `- [x]` means done, so treat the rest as open and ask the same question. Every closed step
   already has its entry in the card's `Evidence` section, or its file under `docs/ai-daridev/evidence/`;
   the close only summarises it. If a step stays open, print the close block but keep the card gray
   and skip the move.
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
4. Print the handoff summary: what shipped, the decisions saved, the spec line, the card
   `#<id> "<name>"` and state — or `none (chat-only)` — the step summary, and the commit message I
   should use. It is conversation-only — never copy it into `docs/ai-daridev/log.md`; `/ai-daridev-archive`
   writes the retro. **Never commit.**

Never write the description above the `Evidence` heading; it belongs to `/ai-daridev-story` and
`/ai-daridev-review`. You own the `<h2>Evidence (ai-daridev)</h2>` tail at the very end of the card
description: append one entry per attempt, never rewrite it, never move it, and never repeat the step
detail there.

Odoo off: print the close checklist (the steps, the evidence paths, the spec line) and write only the
files. The retro belongs to `/ai-daridev-archive`, as always.

## Always

- **Root.** Walk up from the current directory to the nearest `AGENTS.md` that holds
  `<!-- ai-daridev:start -->`. That directory is the root: read and write `docs/ai-daridev/` there
  and write nothing outside it. No block → ask once: create it here, use the git root, or chat-only.
- **Mode.** Cards only when this session is on Odoo, and the first line says which. A card, a
  resolved slug or an explicit `--odoo`/`--no-odoo` decides it; with nothing it is off, and you never
  ask.
- **Odoo contract.** On → read `../ai-daridev-odoo/SKILL.md` and follow it for every Odoo rule:
  config, project and stages, moves, assignees, who writes what and the evidence upload. Off → print
  what it would write and write no card. Never restate those rules here.
- **Never print a bare id.** A step is `p4 "<step>"`, a card is `#14842 "<name>"`; a test-list
  mapping is `covers p4 "<step>"`. Tables keep a name column instead of quoted names.
- **One approval gate per phase.** Structure, a move and the close ask once; state changes are
  reported, not asked.
- **Decisions** → one append to `docs/ai-daridev/decisions.md`, only when project-wide, hard to
  reverse or a shared/ops contract. Everything else stays in the conversation.
- **Fold-in.** If `docs/ai-daridev/` is missing and `docs/decisions/*.md` or `openspec/` exists, ask
  once to fold them into `decisions.md` and `spec.md`; the originals stay as frozen history.
- **Never commit.** Never write secrets or client data into the three files.
