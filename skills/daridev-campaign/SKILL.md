---
name: daridev-campaign
description: Runs the daridev flow unattended over a batch of cards — one worktree per card, plan, pair, integrate to main, wait for the deploy, review, archive, and park what needs me. Never skips review or waives evidence.
disable-model-invocation: true
---

# Campaign

You are the scheduler. You never implement and never review: subagents do, and one closer
serializes main. One invocation authorizes every write in §2 — that is the point, so the gate is
printed once and then it runs.

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
  `limit`/`offset`. Exclude archived (`1_done`), hidden subtasks (`display_in_project=False`), the
  backlog stage and the validated column.
- A card whose next open step is `[you]` is a handoff: list it and skip. A card with no subtasks
  and no brief is not planned: list it with "run `/daridev-plan`" and skip. Never invent steps.
- Ready = every `depend_on_ids` blocker is `1_done` outside Cancelled. Otherwise print
  `Blocked by #<id> "<name>" — <stage> · <state>`.
- `--parallel N` (default 4), `--max N` (default 10). `--dry-run` prints the batch, the gate and
  every write, then stops with no Odoo write, branch, worktree or journal.
- `fresh` refuses when a selected slug already has a sibling worktree.
- Missing `deploy_url` at pre-flight → ask once
  (`deploy_url for <repo>? [<app root> / skip]`), use the answer for the run and print the block
  line to add; `skip` means no deploy wait and the app root is probed.

## 2. The gate

One table — card, next open step, owner, blockers, branch, worktree — then one question. Print the
`deploy_url` (or `skip`) the run will use. Authorized, and nothing else:

- move each card to the in-progress column (`stage_id` + `state=01_in_progress`);
- apply the plan check's description and subtask updates;
- flip steps to `1_done`, attach screenshots to the step's subtask and append the evidence gallery,
  create the hidden park step, reconcile `user_ids`;
- commit on the card's branch, push it, fetch, rebase, run the suite, `merge --ff-only` into main,
  `git revert` a landed card, push main;
- wait for the deploy (100s + `deploy_url` ×4) and run review's probes on prod;
- let review write green + the validated move;
- archive each green card (`state=1_done`, `date_end` when empty), then commit and push `log.md`;
- remove the card's worktree after a successful archive.

**Never**: `1_canceled` on a visible card, waivers, `archive anyway`, skip review, a destructive
non-code step, `rm -rf` a worktree, a force-push, a card from another project. Park instead.

## 3. Journal

`/tmp/opencode/campaign/<repo>-<YYYYMMDD-HHMM>/` — `journal.jsonl` plus one `<slug>.json` per card.
Per card: state, id, slug, branch `feat/<slug>`, worktree path, last integrated sha, deploy
attempts, revert loop, strikes, park reason. Last line `closed <iso> <archived>/<parked>`; without
it the journal is live. Only the scheduler writes it; never in the repo, never committed.

## 4. Card loop

One worktree per card, `--parallel` in flight, one closer. The card's own skills still decide what a
step means.

1. **Implementer** (up to the ready set): `worktree_create <repo>-<slug>` with an explicit name
   (shell `git worktree add` only for a specific base, sibling only), `session_move` in, branch
   `feat/<slug>`, run `/daridev-plan check --no-tests` on every card (code-only, no gate; the
   campaign gate authorizes) then `/daridev-pair`. A plan change is applied under the gate; a
   decision parks the card. It returns `complete`, `blocked` or `partial`, the steps it flipped, the
   local evidence, the spec/decision lines and the branch head. Anything but `complete` is parked,
   never integrated. A `[you]` step mid-card parks on that step, no new one.
2. **Integrate** (the scheduler): fetch, rebase onto `origin/main`, install only when needed, run
   the full suite. Conflict or red → park, main untouched. Then `merge --ff-only` and push.
3. **Wait for the deploy:** 100s, then the `deploy_url` asked at pre-flight (HTTP 200, plus
   `deploy_expect` when declared); `skip` → no wait, probe the app root. Four attempts, ~400s.
   Exhausted → park that card only.
4. **Review:** a fresh subagent runs `/daridev-review` in campaign mode — probe prod, never ask —
   and its probes run on prod. Approved → it writes green + the validated move. Changes requested →
   `git revert` the landed commit first, push, wait for the deploy, reset the worktree, hand the
   findings back. Three loops, then park.
5. **Archive:** `/daridev-archive` on the card, then `docs: archive <slug>` on main and push.
   Never archive drift; park it.
6. **Clean up:** stop any dev server, `git worktree remove`, `prune`, `branch -d` (merged only),
   `fetch -p`. Parked cards keep their worktree.
7. **Recompute the ready set** — the archive freed dependents — and continue until nothing is
   ready, `--max` is reached, or three parks happen in a row.

## 5. Deviations from the single-card skills

| Skill | Single card | Campaign |
|---|---|---|
| pair | one gate per phase, waits for me | the gate is §2; the plan is always re-checked against the current code, never asks |
| pair close | green only when I say yes | never green; review is the only green authority |
| review | moves only with my approval | its write is the §2 authorization |
| archive | waits for my yes | automatic when green and proven; drift parks |
| all | never commit | branch commits, the merge, the revert and `log.md` belong here |
| all | moves only when I ask | the invocation is the turn |

Everything else — evidence shape, assignees, step states, one write per move, no bare ids, the root
— is unchanged and owned by the phases and the contract.

## 6. Rules

- **One campaign per repo.** A journal without its `closed` line → refuse in one line.
- **Pre-flight main.** Default branch, clean, `pull --ff-only`-able, or stop before any work.
- **Park** = one `[you]` step `pN Decide <blocker> — [you]`, detail = what blocked it and how to
  unblock, `sequence = index × 10`, `state=01_in_progress`, `display_in_project=False`, plus the
  assignee handoff — one write. If the next open step is already `[you]`, create nothing and only
  reconcile the assignees. Every park is reported.
- **Loops:** three reverts per card, 45 minutes per card, ten cards per run, three consecutive
  parks stop the run.
- **Resume:** read the journal; archived cards are skipped, a parked card whose `[you]` step is now
  `1_done` re-enters, an existing worktree is reused, a missing one is recreated. `fresh` ignores
  it.
- Never write a card's description, never touch cards the run did not select, never write above the
  root.

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
