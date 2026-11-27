---
name: daridev-status
description: Reports where a card stands in one screen, read-only — done, pushed, merged, deployed and whether the chat can be closed. Runs at the end of every phase close, or on its own. Never writes, never probes a Done-when, never archives.
disable-model-invocation: true
---

# Status

One screen. Read live; the conversation is never proof.

**Mode first, only when called alone.** A card, slug or flag decides; nothing → the card in the
conversation, else `card/<slug>` from the branch, else ask. The literal first line:
`Odoo: on · <project> · card #<id> "<name>"` or `Odoo: off · chat-only`.

Read `../daridev-odoo/SKILL.md` before the first read: it owns the root, mode, stages, states and
assignees. Never restate it.

## Scope

1. A card in the conversation → that card.
2. No card, and a `feat/<slug>` or legacy `story/<slug>` branch, or a `<repo>-<slug>` worktree → the
   card `card/<slug>`.
3. No match → list the active cards (not backlog, not validated), limit 20, ask once.
4. No card at all, or Odoo off → the light flow: `spec.md`, `log.md`, the commit.

No `daridev:start` block → no memory root: the code rows and `done` still print, `archived` never
applies, and `next` is `commit` or `push`, nothing later.

Never invent a card from a branch name.

## Head

`unplanned · planned · blocked · building · built · changes requested · reviewed · archived ·
cancelled`.

| Head | When | `next` |
|---|---|---|
| unplanned | no `Steps` and no subtasks | `/daridev-plan` |
| planned | steps exist, none closed | `p1 "<step>"` |
| blocked | a `depend_on_ids` card is not `1_done` | `blocked by #<id>` |
| building | some steps closed, some open | `pN "<step>"`, with `(you)` when it is yours |
| built | every step closed, no review pass | `review → archive` |
| changes requested | the review failed | `fix pN, pN` |
| reviewed | validated column, `Review` passes | `/daridev-archive` |
| archived | `1_done` | `merge`, `deploy`, or the close line |
| cancelled | cancelled | `— (cancelled)` |

A card reads its steps from `Steps`; no block → legacy, read the subtasks. No card: `planned` when
only the conversation has it, `building` while the change is uncommitted, `built` when it is
committed, `archived` when `log.md` carries the slug.

A card already `1_done` that still has an open step keeps the head `archived`: `done` shows the gap
and `next` names the step. The archive gate was missed once; the block reports it, never repairs it.

## Read

One card read: `name, stage_id, state, user_ids, date_end, write_date, description, child_ids`.
Then, read-only: `git status --porcelain`, `git log @{u}..HEAD`, `git cherry <default> <branch>` and
`git worktree list`, one GET on `deploy_url`, and the memory under the root. Read git where the
card's branch lives — the worktree when there is one — and the memory from the canonical checkout.
Never `git fetch`: behind-ness prints `N behind (stale — last fetch <when>)` unless I say fetch.
Never run a Done-when probe, capture, or write.

## Rows

```
<slug> — <head>
done      <✓|✗|—> <closed>/<total>
pushed    <✓|✗|—>
merged    <✓|✗|—>
deployed  <✓|✗|—>
next      <one act>
```

- `done` — closed steps over total; a `1_canceled` step counts closed. A light run is `✓` when the
  change is committed, with no count. `—` for `unplanned` and `cancelled`.
- `pushed` — `✗` when the tree is dirty, when local commits are not on the upstream, or when a
  branch has no upstream and carries commits; `—` when this work has no branch yet or the repo has
  no remote. *Behind* upstream does not flip it.
- `merged` — `✓` when `git cherry <default> <branch>` leaves no patch, which counts a squash merge;
  `✗` when patches remain; `—` when there is no branch.
- `deployed` — `—` without `deploy_url`, and while the branch is unmerged, since no commit of the
  card is on the deployed surface. `✓` when the probe answers 200 and its `deploy_expect` marker, or
  the sha it reports, is the commit that carries the work; `✗` otherwise. One GET, five seconds, one
  retry.

## Close

`you can close the chat` replaces `next` only when the head is `archived` and no row is `✗`.

## From a phase

When `plan` closes, `pair` closes, `review` writes its verdict, or `archive` appends the log, print
the block as the last output of the turn: no mode line, no question, nothing after it. A phase that
stopped prints none. In campaign mode, none — the journal is the report. The block reads the state
after the phase's writes, so `next` names what follows, never the phase that just ran.

## Never

Write anything (card, git, docs, screenshots), run a Done-when probe, fetch, capture, move or close a
card, restate a review verdict, count an `—` as a failure.
