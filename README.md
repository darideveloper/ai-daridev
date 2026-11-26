# daridev

Agent skills for building software in vertical slices without letting go of the wheel: small
briefs, a plan you approve, test-first, and a close you can read in ten seconds.

The agent proposes and writes code in small steps. You decide.

- [Workflow](docs/workflow.md) · [Setup](docs/setup.md)

## The flow

```
/daridev-plan → /daridev-pair → /daridev-review → /daridev-archive
 brief + steps    at your          probes the        closes the card
 + one gate       pace             Done-when         + 4-line log
```

| Command | Does | Never does |
|---|---|---|
| `/daridev-plan` | Splits an idea into ≤10 one-line briefs, or refines one card into `Problem` / `Done when` / 3–7 steps with checks. Audits any plan read-only. | Write code, move a card in check mode, invent a requirement. |
| `/daridev-pair` | Executes the approved steps: check red → minimum code → green → screenshot in the card gallery, then the green dot in place when you accept the close. Asks once for the pace — step by step, straight through or manual steps batched — and never implements a `[you]` step without your `do it`. Stops on anything unplanned. | Review itself, archive, move the card, set `1_done`, commit without your yes. |
| `/daridev-review` | Runs the `Done when` probes as the lowest-privilege actor and writes one `Review` block. | Capture evidence, archive, invent a verdict. |
| `/daridev-archive` | Closes a green validated card, or a self-verified one you explicitly release, and appends a 4-line log. | Set the green dot, cancel a card, invent a retro. |
| `/daridev-campaign` | Runs the flow over a batch: one worktree per card, plan → pair → integrate → deploy → review → archive. | Skip review, waive evidence, archive drift. |

Each phase ends waiting for your approval — two gates per work item: the plan and the close.
Everything else (a step passing, a card moving to in-progress, a subtask flipping) is reported, not
asked. `step` pace adds one gate per step, only when you ask for it.

## Size decides how much you run

- **Light, no card** — `/daridev-plan` on a one-liner, `/daridev-pair`, `/daridev-archive`. No
  review, no Odoo, the log is the record.
- **Carded, no review** — plan the card, pair, then archive with “skip review”. The card closes
  without a review pass.
- **Full** — plan → pair → review → archive, for delegated or risky work.

## What the agent writes

**Odoo (only when the session is on):** one card per brief; the whole plan in the description — a
`Problem` / `Done when` brief and a `Steps` markdown checklist with every owner, check and file, so
a teammate without MCP can copy it whole; one hidden subtask per step for tracking only, its
description empty; a screenshot in the card's `Evidence` gallery, attached to the card; one
`Review` block written by review; the green dot at pair's close, in place; validated column +
`date_end` on a review pass; `1_done` at archive. `stage_id` and `state` travel in the same write,
except pair's close, which writes `state` alone. Assignees are replaced each write — the agent, plus
you while the next open step is `[you]` — and whoever it dropped is named.
Archived cards are hidden by the default board filter.

**In the repo:** `docs/records/spec.md` (one sentence per behaviour), `docs/records/log.md`
(4 lines per card), `docs/records/evidence/` (untracked), and `docs/decisions/NNNN-<slug>.md` for
ADRs. The root is the nearest `AGENTS.md` holding `<!-- daridev:start -->`; nothing is written above
it. Files are committed with your code: a phase that writes offers the commit once, and it lands
only on your yes.

## Install

```bash
git clone git@github.com:darideveloper/ai-daridev.git
cd ai-daridev
./scripts/install.sh
./scripts/install.sh --check
```

`install.sh` symlinks every skill in `skills/` into `~/.agents/skills` and every installed agent,
links the OpenCode commands, removes the old `ai-daridev-*` links, and migrates the global
instruction block. It installs nothing else and never edits MCP or JSON config.

| Agent | Reads | Invoke with |
|---|---|---|
| OpenCode | `~/.agents/skills` | `/daridev-plan` (command file) |
| Claude Code | `~/.claude/skills` | `/daridev-plan` (the skill) |
| Codex | `~/.agents/skills`, `~/.codex/skills` | `$daridev-plan` |
| Gemini, Continue, Windsurf, Kiro, Devin | linked when the agent exists | ask the agent to use the skill |

A `git pull` updates everything: skills and commands are symlinks.

## Odoo is per session

Declare the project in the repo’s `AGENTS.md`:

```md
<!-- daridev:start -->
- odoo_project: acme-app
- odoo_stage_done: Sprint Complete
- card_tag: backend
<!-- daridev:end -->
```

The block supplies the parameters, never the switch. `--odoo` / `--no-odoo`, your words, or a card
reference decide the session; `plan` with a one-liner is off without asking. Every phase prints the
mode first, so it is never a guess. With Odoo off, no cards are written and only the files are.

Identity is per developer, never in the block: your agent is your MCP account, and `.daridev.local`
beside `AGENTS.md` (untracked) carries your own uid and name. Every on session prints
`Identity: agent 17 · you Dari (2, local)` as its second line.

## Principles

- **Don't invent.** Missing information gets asked, not filled in.
- **The simplest thing that works.** No abstractions for the future.
- **Slice vertically and small.** One brief = one session, ≤3 files; 3–7 steps.
- **Two gates.** The plan and the close; everything else is a report.
- **Proof, not paperwork.** A probe per Done-when; screenshots only for visual work.
- **Suggest, don't decide.** Patterns and refactors are your call; a commit is offered once and lands
  only on your yes.

By Hola Mundo. Fork maintained by Dari Developer.
