# daridev

Agent skills for building software in vertical slices without letting go of the wheel: small
briefs, a plan you approve, test-first, and a close you can read in ten seconds.

The agent proposes and writes code in small steps. You decide.

- [Workflow](docs/workflow.md) · [Setup](docs/setup.md)

## The flow

```
/daridev-plan → /daridev-pair → /daridev-review → /daridev-archive
 brief + steps    one step at      probes the        closes the card
 + one gate       a time           Done-when         + 4-line log
```

| Command | Does | Never does |
|---|---|---|
| `/daridev-plan` | Splits an idea into ≤10 one-line briefs, or refines one card into `Problem` / `Done when` / 3–7 steps with checks. Audits any plan read-only. | Write code, move a card in check mode, invent a requirement. |
| `/daridev-pair` | Executes the approved steps: check red → minimum code → green → screenshot on the step's subtask. Stops on anything unplanned. | Review itself, archive, mark green, commit. |
| `/daridev-review` | Runs the `Done when` probes as the lowest-privilege actor and writes one `Review` block. | Capture evidence, archive, invent a verdict. |
| `/daridev-archive` | Closes a green validated card, or a self-verified one you explicitly release, and appends a 4-line log. | Set the green dot, cancel a card, invent a retro. |
| `/daridev-campaign` | Runs the flow over a batch: one worktree per card, plan → pair → integrate → deploy → review → archive. | Skip review, waive evidence, archive drift. |

Each phase ends waiting for your approval — two gates per work item: the plan and the close.
Everything else (a step passing, a card moving to in-progress, a subtask flipping) is reported, not
asked.

## Size decides how much you run

- **Light, no card** — `/daridev-plan` on a one-liner, `/daridev-pair`, `/daridev-archive`. No
  review, no Odoo, the log is the record.
- **Carded, no review** — plan the card, pair, then archive with “skip review”. The card closes
  without the green dot.
- **Full** — plan → pair → review → archive, for delegated or risky work.

## What the agent writes

**Odoo (only when the session is on):** one card per brief; `Problem` / `Done when` in the
description; one hidden subtask per step with its owner; a screenshot attached to the step for
visual work; one `Review` block written by review; green + validated column on a pass; `1_done` at
archive. `stage_id` and `state` always travel in the same write. Assignees follow the next open
step. Archived cards are hidden by the default board filter.

**In the repo:** `docs/records/spec.md` (one sentence per behaviour), `docs/records/log.md`
(4 lines per card), `docs/records/evidence/` (untracked), and `docs/decisions/` for ADRs. The root
is the nearest `AGENTS.md` holding `<!-- daridev:start -->`; nothing is written above it. Files are
committed with your code, by you.

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
- odoo_assignee_manual_uid: 2
<!-- daridev:end -->
```

The block supplies the parameters, never the switch. `--odoo` / `--no-odoo`, your words, or a card
reference decide the session; `plan` with a one-liner is off without asking. Every phase prints the
mode first, so it is never a guess. With Odoo off, no cards are written and only the files are.

## Principles

- **Don't invent.** Missing information gets asked, not filled in.
- **The simplest thing that works.** No abstractions for the future.
- **Slice vertically and small.** One brief = one session, ≤3 files; 3–7 steps.
- **Two gates.** The plan and the close; everything else is a report.
- **Proof, not paperwork.** A probe per Done-when; screenshots only for visual work.
- **Suggest, don't decide.** Patterns, refactors and commits are your call.

By Hola Mundo. Fork maintained by Dari Developer.
