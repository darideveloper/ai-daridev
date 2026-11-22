---
name: daridev-campaign
description: Runs the daridev flow unattended over a batch of cards — one worktree per card, plan, pair, integrate to main, wait for the deploy, review, archive, and park what needs me. Never skips review or waives evidence.
disable-model-invocation: true
---

# Campaign

You are the scheduler. You never implement and never review: subagents do, and one closer
serializes main. One invocation authorizes every write in §2 and the local actions §4 names — that
is the point, so the gate is printed once and then it runs.

**Mode first.** The literal first line: `Odoo: on · <project>`. A campaign is always on; no
`odoo_project` → stop in one line.

## 1. Inputs and selection

```
/daridev-campaign                          # everything in the in-progress column
/daridev-campaign tags:Shell,Terminals
/daridev-campaign cards:#14842 "#14850"
/daridev-campaign fresh                     # ignore the journal
/daridev-campaign --dry-run cards:#<id>
```

- Default selection = every card in the in-progress column of `odoo_project`, paged with
  `limit`/`offset`. Exclude archived (`1_done`), canceled (`1_canceled`), hidden subtasks
  (`display_in_project=False`), the backlog stage and the validated column — except a parked card
  whose `[you]` step is now `1_done`, which re-enters from any column.
- A card whose next open step is `[you]` is a handoff: list it and skip. A card with subtasks but no
  `Steps` is legacy: backfill it from them (§2). A card with a brief and neither is planned in
  pre-flight. A card with nothing to plan from — no `Steps`, no subtasks, no Problem/Done-when —
  parks (§6) as `- [ ] p1 Decide needs brief — [you]`; never a silent skip, never an invented step.
- Ready = every `depend_on_ids` blocker is `1_done` outside Cancelled. Otherwise print
  `Blocked by #<id> "<name>" — <stage> · <state>`.
- `--parallel N` (default 4), `--max N` (default 10). `--dry-run` prints the pre-flight questions
  with their defaults, the batch, the gate those defaults build and every write, then stops with no
  Odoo write, branch, worktree or journal.
- `fresh` refuses when a selected slug already has a sibling worktree.

### Pre-flight — one round, then silence

Ask everything once, in one message, before the gate; after the answer the run asks nothing until
the report. Every question carries its default and an unanswered question takes it. Ask only what
the root block and the selection do not already answer:

| Question | Default when unanswered |
|---|---|
| the resolved batch: ids and names | the selection as chosen |
| surface: `prod`, `staging` or `local` | `prod` when the `deploy_url` answer is not `skip`, else `local` |
| `deploy_url` and `deploy_expect` for `<repo>` | `skip` |
| manual uid for the handoff, when `odoo_assignee_manual_uid` is empty | none — parks carry no assignee and the report is the handoff |

`surface` is one surface for the whole card — the captures and review's probes both run on it;
review's verdict records it (`pass · <surface>`, `pass · local — prod unproven` when nothing was
deployed) and the gate prints it. The default follows the `deploy_url` answer: a `skip` run has
nothing to deploy, so the app root is probed and the surface is recorded unproven. Every answer
worth keeping is printed as its root block line.

Each card with a brief and neither `Steps` nor subtasks is planned by a subagent running
`/daridev-plan` card mode up to its gate — text only, no write — against the pre-flight main
checkout, since no worktree exists yet (§4.1). The gate prints those briefs; once it is answered the
same subagent applies them — description, `Steps`, subtasks — and never the stage or state (§2). A
card with nothing to plan from is a park (§6), never an invented plan.

## 2. The gate

One table — card, next open step with the brief of a card planned in pre-flight, owner, blockers,
branch, worktree, and a park reason with no branch for a card that will be parked — then one
question. Print the surface and the `deploy_url` (or `skip`) the run will use. Authorized: the
writes below, plus every local action §4 names — worktree create and remove, session move, install,
dev-server stop, worktree reset, prune, `branch -d`, `fetch -p` — and nothing else:

- move each card to the in-progress column (`stage_id` + `state=01_in_progress`); a card already at
  `03_approved` keeps that state, and one re-entering from the validated column keeps its column;
- the planner applies each plan generated in pre-flight — description, `Steps`, subtasks — once the
  gate is answered; the column move is this gate's, never the plan's; the plan check applies its
  description and subtask updates, including a legacy card's `Steps` backfill;
- flip steps to `1_done`, attach screenshots to the card and append or re-capture the evidence
  gallery, create the hidden park step and mirror its line into `Steps`, reconcile `user_ids`;
- commit the worktree on the card's branch, push it, fetch, rebase, run the suite, `merge --ff-only`
  into main, `git revert` a landed card, push main;
- wait for the deploy (100s, then up to four probes of `deploy_url`, ~400s), re-capture each visual
  step on that surface, and run review's probes on it;
- write the green dot in place at pair's close — green means built, awaiting validation — then let
  review add `date_end` + the validated move; review's fail is the only `03→02` write, on the card
  and its failing steps, and the park keeps it;
- archive each green card (`state=1_done`, `date_end` when empty), then commit and push `log.md`;
- remove the card's worktree after a successful archive.

**Never**: `1_canceled` on a visible card, waivers, `archive anyway`, skip review, a destructive
non-code step, `rm -rf` a worktree, a force-push, a card from another project. Park instead.

## 3. Journal

`/tmp/opencode/campaign/<repo>-<YYYYMMDD-HHMM>/` — `journal.jsonl` plus one `<slug>.json` per card.
Per card: state, id, slug, branch `feat/<slug>`, worktree path, last integrated sha, deploy
attempts, revert count (carried across re-entries), strikes, park reason. Last line
`closed <iso> <archived>/<parked>`; without
it the journal is live. Only the scheduler writes it; never in the repo, never committed.

## 4. Card loop

One worktree per card, `--parallel` in flight, one closer. The card's own skills still decide what a
step means. Where the loop starts is the card's entry: `03_approved` in the in-progress column → 4;
parked at archive in the validated column → 5; anything else → 1.

1. **Implementer** (up to the ready set): `worktree_create <repo>-<slug>` with an explicit name
   (shell `git worktree add` only for a specific base, sibling only), `session_move` in, branch
   `feat/<slug>`, run `/daridev-plan check --no-tests` on every card (code-only, no gate; the
   campaign gate authorizes) then `/daridev-pair`. A card planned in pre-flight already carries the
   `Steps` the gate printed: the check re-reads the plan, the implementer never plans. A plan change
   parks the card, naming the change the next run's plan check applies (§2); a decision parks the
   card. It returns `complete`, `blocked` or `partial`, the steps it flipped, the evidence, the
   spec/decision lines and the worktree — clean or dirty, never committed. Anything but `complete`
   is parked, never integrated. A `[you]` step mid-card parks on that step, no new one.
2. **Integrate** (the scheduler): commit the worktree on `feat/<slug>`, fetch, rebase onto
   `origin/main`, install only when needed, run the full suite. Conflict or red → park, main
   untouched. Then `merge --ff-only` and push.
3. **Wait for the deploy, then re-capture:** 100s, then the `deploy_url` asked at pre-flight
   (HTTP 200, plus `deploy_expect` when declared); `skip` → no wait, probe the app root, no
   re-capture. Four attempts, ~400s; exhausted → park that card only. Green → a capture subagent
   re-runs each visual step on that surface at 1600×1000, masked, under
   `flock /tmp/opencode/playwright.lock`, and replaces that step's `Evidence (daridev)` entry
   (`../daridev-odoo/SKILL.md`: a re-capture replaces it, the old attachment stays as history). A
   capture that fails or cannot reproduce the step parks the card — the capture is the proof, not a
   label.
4. **Review:** a fresh subagent runs `/daridev-review` in campaign mode — it probes the surface and
   never asks; `skip` probes the app root and takes review's not-deployed branch (`surface: local —
   prod unproven`, never a FAIL for a missing deploy) — with the gallery already re-captured unless
   the run is `skip`; review never captures. Approved → it adds `date_end` + the validated move.
   Changes requested → the scheduler reverts the landed commit, pushes, waits for the deploy to
   prove the revert is live (`skip` → no wait), then `git reset --hard origin/main` on `feat/<slug>`
   so the next attempt cannot re-merge it; the implementer re-enters with the findings. Three
   reverts, then park.
5. **Archive:** `/daridev-archive` on the card from the canonical checkout, never the card's
   worktree — its `log.md` append belongs to the repo root; then `docs: archive <slug>` on main and
   push. The worktree is removed only after a successful archive.
   Never archive drift; park it. A lasting decision found while implementing parks the card on that
   step; found at archive, it parks the card before it closes — green kept, a hidden `[you]` step
   naming the decision. The re-entry closes it, and the answered step is the ADR approval, so
   archive writes it. Campaign never writes an ADR on its own.
6. **Clean up:** stop any dev server, `git worktree remove`, `prune`, `branch -d` (merged only),
   `fetch -p`. Parked cards keep their worktree.
7. **Recompute the ready set** — the archive freed dependents — and continue until nothing is
   ready, `--max` is reached, or three cards in a row end parked.

## 5. Deviations from the single-card skills

| Skill | Single card | Campaign |
|---|---|---|
| pair | one gate per phase, waits for me, asks the capture surface | the gate is §2 and pre-flight fixed the surface; the plan is re-checked against the code; never asks — answers `run` without asking, and a `[you]` step returns partial and parks |
| pair close | green only when I say yes, column untouched | green at close = built, awaiting validation; the §2 gate is the yes and the `Review` block is the proof |
| review | moves only with my approval | its write is the §2 authorization; it probes the pre-flight surface, not its campaign default of prod |
| archive | waits for my yes, asks about the decision | automatic when green and proven; drift parks; the answered park step is the answer, so it asks nothing and writes the ADR that step names |
| all | never commit | branch commits, the merge, the revert and `log.md` belong here |
| all | moves only when I ask | the invocation is the turn |

Everything else — evidence shape, assignees, step states, one write per move, no bare ids, the root
— is unchanged and owned by the phases and the contract.

## 6. Rules

- **One campaign per repo.** A journal without its `closed` line → refuse in one line.
- **Pre-flight main, before the questions.** Default branch, clean, `pull --ff-only`-able, or stop
  before any work.
- **Park** = one `[you]` step `- [ ] pN Decide <blocker> — [you]`, its line in `Steps` carrying what
  blocked it and how to unblock, `sequence = index × 10`, `display_in_project=False`, plus the
  assignee handoff when a manual uid exists — one write; with none, the report is the handoff. A
  card review failed keeps its `02_changes_requested`, and one
  parked at archive keeps its `03_approved`: for those two the park adds the step and writes no
  state. Any other card parks at `01_in_progress`. If the next open step is already `[you]`, create
  nothing and only reconcile the assignees. Every park is reported.
- **Limits:** three reverts per card, counted across re-entries and kept in the journal; 45 minutes
  of work per card, after which it parks, the deploy wait and the capture pass excluded; `--max`
  cards per run; three cards in a row ending parked stop the run, and a card that does not park
  resets the count.
- **Resume:** read the last closed journal of this repo; archived cards are skipped, a parked card
  whose `[you]` step is now `1_done` re-enters — its `02_changes_requested` is cleared by the gate's
  move to the in-progress column (§2) and pair fixes the yellow steps, while one re-entering from
  the validated column goes straight to archive (§4) — an existing worktree is reused, a missing one
  is recreated. `fresh` ignores it.
- Never write a card's description beyond the plan check's block, a plan generated in pre-flight,
  the evidence gallery and a park's line (all covered by §2), never touch cards the run did not
  select, never write above the root.

## 7. Report

```
Campaign <repo> · <start> → <end> · <n>/<m> archived · <k> parked
| card | result | merge | deploy | evidence | worktree |
|---|---|---|---|---|---|
| #14842 "retry upload" | archived 1_done | a1b2c3d | ok 1/4 | p1..p4 | removed |
| #14850 "billing export" | parked [you] p5 | — | — | — | kept |
Next: flip the [you] steps above; archive <n> cards to unblock <list>.
```

## Always

- **Root.** Nearest `AGENTS.md` with `<!-- daridev:start -->`; `docs/records/` is relative to it.
- **Mode.** Always on: no `odoo_project` → stop in one line.
- **Contract.** Read `../daridev-odoo/SKILL.md` and follow it; never restate it.
- **Odoo unavailable** → print the plan and every write, then stop.
- UI is validated with `playwright-cli`, every capture under `flock /tmp/opencode/playwright.lock`.
