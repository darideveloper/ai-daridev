# Workflow

Investigate → plan → validate → do → verify → archive. Two approvals: the plan and the close.
Everything else is reported.

```
/daridev-plan   →   /daridev-pair   →   /daridev-review   →   /daridev-archive
brief + steps       one step at a       probes the            closes the card
+ one gate          time, no stops      Done-when             + 4-line log
```

`review` is skipped when there is no card, or when you say **skip review** at the archive gate.

## The card

```
Problem:      <observed, with the path or surface>
Done when:    <outcome, one per surface>
Steps:        p1 … · p2 … · p3 …      (subtasks when Odoo is on)
```

No persona, no separate acceptance criteria. `Done when` names every surface a gate, permission,
limit or export must hold on. The description is at most 10 lines above the review block; anything
longer belongs in the conversation or an ADR.

The description has four zones: the brief, `Review (daridev)` (the probes), `Evidence (daridev)`
(the screenshots, one entry per step, labelled `pN "<step>" · prod|local`), and the
`daridev: card/<slug>` line. Old cards keep their `Evidence (ai-daridev)` tail below it.

## Three paths

**Light — no card.**
```
/daridev-plan <one-liner>      Odoo: off, one gate
/daridev-plan check            optional; reads the code and runs the checks
/daridev-pair                  consumes the approved plan
/daridev-archive               log + spec sentence, no card
```

**Carded — small fix, no review.**
```
/daridev-plan <card>           card + subtasks
/daridev-pair                  steps, screenshots in the card gallery
/daridev-archive               "skip review" → done, not green
```

**Full — delegated or risky.**
```
/daridev-plan → /daridev-pair → /daridev-review → /daridev-archive
```

## Odoo is per session

The block supplies the project; the session decides whether cards are written. `--odoo` /
`--no-odoo`, a card reference, or your words decide it; `plan` with a pasted one-liner is off
without asking; `plan` with nothing asks once, default no. Every phase prints
`Odoo: on · <project>` or `Odoo: off · chat-only` first. With Odoo off, stories live in the
conversation and only the files are written.

Green means **reviewed**. The validated column means **finished**; a skip-review card lands there
without the green dot, so the board still shows who looked at it.

## Evidence surface

`pair` asks once `Screenshots from prod, staging or local? [prod]`; `review` asks once
`Probe against prod or local? [prod]`. A probe on local, or on a card that is not deployed, is
recorded as `surface: local — prod unproven`; it can still pass and green the card, and the block
names the surface. It is not a failure.

## Memory

```
docs/records/
├── spec.md        what the product does now, one sentence per behaviour
├── log.md         4 lines per closed card
└── evidence/      untracked screenshots (`*` + `!.gitignore`)
```

Lasting decisions are ADRs under `docs/decisions/`, referenced by path from the log. The root is
the nearest `AGENTS.md` with `<!-- daridev:start -->`; memory follows the code, so each code repo
has its own. Nothing is written above the root.

Legacy reads: the old `ai-daridev:start` marker, `docs/ai-daridev/`, `ai-daridev: story/<slug>`
and `Review (ai-daridev)` still work; new writes use the new names. An old `Evidence (ai-daridev)`
tail is preserved unless you approve collapsing it to one attachment pointer.

## Outside the flow

- `/daridev-plan check` — reads the code the plan names and runs its `check:` commands; no card,
  no Odoo, no writes.
- `/daridev-campaign` — runs the flow over a batch, unattended, one worktree per card.
- `/daridev-plan split` — one idea into ≤10 one-line briefs and cards.

## Caps

| Thing | Cap |
|---|---|
| Card above the review block | 10 lines |
| Review block | 6 lines |
| Log entry | 4 lines |
| Steps per card | 3–7 |
| Gates per work item | 2 |
