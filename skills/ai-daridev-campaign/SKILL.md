---
name: ai-daridev-campaign
description: Runs the ai-daridev flow unattended over a batch of cards — one worktree per card, pair, integrate to main, wait for the deploy, review, archive, and park the cards that need me. Use when asked to finish a column or a batch of cards in one run.
disable-model-invocation: true
---

# Campaign

You are the scheduler. You never implement and never review: subagents do, and one closer serializes
main. One invocation is the authorization for every write in §2 — that is the whole point, so the gate
is printed once and then it runs.

## 1. Inputs and selection

```
/ai-daridev-campaign                          # everything in the in-progress column
/ai-daridev-campaign tags:Shell,Terminals
/ai-daridev-campaign cards:#14842 "#14850"    # the ids you name, in that order
/ai-daridev-campaign fresh                     # ignore the journal, start a new run
/ai-daridev-campaign --dry-run cards:#<id> "<name>"
```

- **Default selection** = every card in the in-progress column of `odoo_project`, paged with
  `limit`/`offset`; never an unbounded query. The project, the column and the tags come from the repo
  block exactly as the other skills resolve them (0 or 2+ matches → ask once, never guess).
- Exclude archived (`1_done`) cards, hidden subtasks (`display_in_project=False`), the backlog stage
  and `odoo_stage_done`.
- **Threshold:** a card whose next open step is `[you]` is a handoff, not unfinished automation —
  list it and skip it. A card with no subtasks and no `<h2>Checklist</h2>` is not refined: list it
  with "run `/ai-daridev-story`" and skip it. Never invent steps to fill a card.
- **Ready set:** a card enters the queue only when every `depend_on_ids` blocker is `1_done` outside
  the Cancelled stage. Skipped cards print `Blocked by #<id> "<name>" — <stage> · <state>`.
- `--parallel N` (default 4) and `--max N` (default 10). There is no fixed parallel cap: it starts as
  many cards as the ready set allows, bounded by `--max`; the single closer is what bounds throughput.
- `--dry-run` prints the batch, the ready set, the gate and every write it would make, then stops. No
  Odoo write, no branch, no worktree, no journal.
- `fresh` refuses when a selected slug already has a sibling worktree: the folder name is the card's
  identity, so remove it first instead of letting two runs collide on one path.

## 2. The gate

One table, then one question. Columns: card, next open step, owner, blockers, branch, worktree.

Authorized by this invocation, and nothing else:

- move each card to the in-progress column (`stage_id` + `state=01_in_progress`, one write);
- flip steps to `1_done`, append entries to the card's `Evidence` tail, create the hidden park step,
  reconcile `user_ids` from the next open step;
- commit on the card's own branch, push that branch, fetch, rebase, run the suite, `merge --ff-only`
  into main, `git revert` a landed card, push main;
- wait for the deploy (100s, then validation, four attempts) and re-capture prod evidence;
- let review write green + the move to `odoo_stage_done`;
- archive each green card by invoking `/ai-daridev-archive` — that skill writes `state=1_done` (+
  `date_end` when empty); the campaign then commits `log.md` and pushes it;
- remove the card's worktree after a successful archive.

**Never**, not even on a retry: `1_canceled` on a visible card, evidence waivers, `archive anyway`, a
destructive non-code step, `rm -rf` of a worktree, a force-push, a rewrite of published history, a
card from another project. A card that needs any of those is parked (§6).

## 3. Journal

`/tmp/opencode/campaign/<repo>-<YYYYMMDD-HHMM>/` — `journal.jsonl` plus one `<slug>.json` per card.
Per card: state, card id, slug, branch `feat/<slug>`, worktree path, last integrated sha, deploy
attempts, revert loop, strikes and the park reason. The run's last line is
`closed <iso> <archived>/<parked>`; a journal without that line is **live**. Only the scheduler writes
it; a subagent reports back in one block. Never inside the repo, never committed. It is the resume
key, not documentation.

## 4. Card loop

One worktree per card, `--parallel` in flight, one closer. The card's own skills still decide what a
step means; §5 is the only place this skill departs from them.

1. **Spawn the implementer** (up to the ready set, `--parallel` at a time): `worktree_create
   <repo>-<slug>` with an explicit name — the shell `git worktree add ../<repo>-<slug>` only when the
   card needs a specific base commit, and it must stay a sibling — then `session_move` into it, create
   the branch `feat/<slug>`, and run `/ai-daridev-pair` on the card. It returns `complete`, `blocked`
   or `partial`, the test list, the steps it flipped, the local evidence it recorded, the spec/decision
   lines and the branch's last commit. **Anything but `complete` is parked, never integrated.**
   The plan audit inside it follows the check-plan rules without asking: one action per step, verb
   first, ≤40 words, an owner on every line, auto-fix the unambiguous and stop rather than invent a
   requirement. **A `[you]` step mid-card** stops the implementer: the campaign parks on that existing
   step — no new step — reconciles the assignees and reports it.
2. **Integrate** (the scheduler is the closer; one card at a time, `complete` reports only):
   `git -C <worktree> fetch`, rebase onto `origin/main`,
   install only when needed, run the full suite on the rebased tree. Conflict or red → park, main
   untouched. Then `git -C <main> merge --ff-only <branch>` and push.
3. **Wait for the deploy:** 100s, then a validation of `deploy_url` from the block (HTTP 200, plus the
   expected commit marker when the block declares one); no `deploy_url` → the app root. Four attempts,
   ~400s. **Exhausted → park that card only** and continue with the next one; never halt the run.
4. **Evidence refresh:** for every `1_done` step whose entry is a `local — not deployed` screenshot,
   capture the same surface on prod with `playwright-cli` — every capture under
   `flock /tmp/opencode/playwright.lock` — and append a **new** entry for that step, keyed
   `pN "<step>"`. Code lines and waivers are left alone. Never rewrite, never replace.
5. **Review:** a fresh subagent with no memory of the implementation reviews the card
   (`/ai-daridev-review`). Approved → it writes green + the move to `odoo_stage_done` in its own gate.
   Changes requested → **revert first**: `git -C <main> revert <sha>`, push, deploy wait, reset the
   worktree onto `origin/main`, hand the findings back to the implementer. Three loops, then park.
6. **Archive:** `/ai-daridev-archive` on the card, then `docs: archive <slug>` on main and push — a
   docs-only diff, so no deploy wait. Never archive a card with drift; park it.
7. **Clean up:** stop any dev server, `git worktree remove <path>`, `git worktree prune`,
   `git branch -d <branch>` (merged only), `git fetch -p`. Parked cards keep their worktree.
8. **Recompute the ready set** — the archive just freed its dependents — and continue until nothing is
   ready, `--max` is reached, or three card-level parks happen in a row.

## 5. Deviations from the single-card skills

| Skill | Single card | Campaign |
|---|---|---|
| pair | one gate per phase, waits for me | the gate is §2; the test list is audited in-session with check-plan rules and never asks |
| pair | evidence is a prod capture after the deploy | flips on a `local — not deployed` capture; UI steps are refreshed in §4.4 |
| pair close | green only when I say yes | never green here; review is the only green authority |
| review | moves only with my approval | its approve/reject write is the §2 authorization |
| archive | waits for my yes, `archive anyway` on drift | automatic when green and proven; drift always parks |
| all | never commit | branch commits, the merge, the revert and `log.md` belong to the campaign |
| all | moves only when I ask in this turn | the invocation is the turn |

Everything else — evidence shape, assignees, step states, one write per move, no bare ids, the root and
the config — is unchanged and owned by the six programs.

## 6. Rules

- **One campaign per repo.** A journal in `/tmp/opencode/campaign/` without its `closed` line → refuse
  with one line. Two schedulers would break the single-writer rule the whole design rests on; a closed
  journal is just history.
- **Pre-flight main.** It must be on the default branch, clean, and `pull --ff-only`-able, or the run
  stops with one line — before any work, not during the first merge.
- **Park** = a `[you]` step `pN Decide <blocker> — [you]`, detail = what blocked it and how to
  unblock, `sequence = index × 10`, `state=01_in_progress`, `display_in_project=False`, plus the
  assignee diff that hands the card to `odoo_assignee_manual_uid` — all in one write. When the card's
  own next open step is already `[you]`, create nothing and only reconcile the assignees. Every park
  is reported; none is silent.
- **Loops:** three revert cycles per card, 45 minutes of implementation per card, ten cards per run,
  and three consecutive parks stop the run. Recovered loops do not count as strikes; the 45 minutes
  run from the implementer's spawn to its report.
- **Resume:** read the journal. Archived cards are skipped, a parked card whose `[you]` step is now
  `1_done` re-enters the queue, an existing worktree is reused and a missing one is recreated. `fresh`
  ignores all of it.
- **Deploy validation failure is per card** — the run continues, and the report says so loudly.
- Never write a card's description outside the `Evidence` tail, never touch cards the run did not
  select, never write above the repo root.

## 7. Report

```
Campaign <repo> · <start> → <end> · <n>/<m> archived · <k> parked · <s> skills
| card | result | merge | deploy | evidence | worktree |
|---|---|---|---|---|---|
| #14842 "retry upload" | archived 1_done | a1b2c3d | ok 1/4 | p1..p4 prod | removed |
| #14850 "billing export" | parked [you] p5 | — | — | local only | kept |
Next: flip the [you] steps above; archive <n> cards to unblock <list>.
```

## Always

- **Root and config** follow the six single-card skills: the nearest `AGENTS.md` with the block, exact
  project and tag names, stages resolved inside the project, `odoo_assignee_uid`/`odoo_assignee_manual_uid`.
- **Odoo unavailable** → print the plan and every write it would make, and stop; a campaign cannot run
  blind.
- **Never print a bare id.** A step is `p4 "<step>"`, a card is `#14842 "<name>"`.
- **UI is validated with `playwright-cli`, never by eye**; every capture takes
  `flock /tmp/opencode/playwright.lock`, so parallel implementers queue instead of colliding.
