# ai-daridev

Agent skills for building software in vertical slices without letting go of the wheel. Inspired by
Extreme Programming: small user stories, acceptance criteria, test-first, pair programming, simple
design.

The agent splits, proposes and writes code in small steps. You decide.

- [Workflow](docs/workflow.md) · [Setup](docs/setup.md)

## The flow

```
/ai-daridev-backlog → /ai-daridev-story → /ai-daridev-pair → /ai-daridev-review → /ai-daridev-archive
   the idea            criteria + a        red → green,        someone else's      the retro
   as stories          step checklist       one step at a time  card, graded
```

| Command | Does | Never does |
|---|---|---|
| `/ai-daridev-backlog` | Turns an idea into ≤10 vertical, one-line stories, creates the cards and links each `Requires: #N` as Blocked By. | Invent requirements, technical stories, estimates. |
| `/ai-daridev-story` | Adds Given/When/Then criteria and a step checklist to **one** card, one hidden subtask per step. | Write code. |
| `/ai-daridev-pair` | Drives: one test → red → minimum code → green, stops after every step and attaches evidence. Plan-and-execute for non-code work. | Commit, edit tests to pass, add what you didn't ask for, move columns, start a blocked card. |
| `/ai-daridev-review` | Grades someone else's card against its criteria, steps and evidence, proposes the writes. | Move a card, invent a verdict, mark work done. |
| `/ai-daridev-archive` | Gates on the evidence, marks the card done so Odoo frees its dependents, then appends the retro to `docs/ai-daridev/log.md`. | Move cards, cancel, create cards, invent a retro. |
| `/ai-daridev-check-plan` | Audits any plan in detail, fixes the gaps one question at a time and renders an ordered checklist. Outside the flow; with a named card it also updates the card checklist. | Invent requirements, write files, move cards. |

Each phase ends waiting for your approval. The board is yours: the agent never moves a card between
stages, never cancels and never assigns; archive is the only phase that marks a card done.

## What the agent writes

**In Odoo (optional):** one card per story — backlog cards at `backlog`, criteria and checklist in
the description, one hidden subtask per step (`display_in_project=False`), real **Blocked By** links
for `Requires: #N`, a dated **Evidence** block on each completed subtask with screenshots, curl
responses or files attached, `state=03_approved` + `date_end` when a story closes, and `state=1_done`
at archive, which frees its dependents. Columns are never written.

**In the repo:** three files under `docs/ai-daridev/` at the repo root.

| File | Holds | Owner |
|---|---|---|
| `spec.md` | what the product does now, one sentence per behavior | pair (at close) |
| `decisions.md` | append-only: date, decision, why, where | pair |
| `log.md` | append-only: one ≤8-line retro per closed story | archive |

The repo root is the nearest `AGENTS.md` that holds an `ai-daridev:start` block, so a subfolder can
inherit the suite's memory or declare its own. Files are created on first write. Nothing is written
above that root. They are committed with your code, by you.

## Install

```bash
git clone git@github.com:darideveloper/ai-daridev.git
cd ai-daridev
./scripts/install.sh
./scripts/install.sh --check
```

`install.sh` symlinks the six skills into `~/.agents/skills` and every installed agent, links the
OpenCode commands, and replaces the old global instruction block (backup first). It installs
nothing else and never edits MCP or JSON config.

| Agent | Reads | Invoke with |
|---|---|---|
| OpenCode | `~/.agents/skills` | `/ai-daridev-pair` (command file) |
| Claude Code | `~/.claude/skills` | `/ai-daridev-pair` (the skill) |
| Codex | `~/.agents/skills`, `~/.codex/skills` | `$ai-daridev-pair` |
| Gemini, Continue, Windsurf, Kiro, Devin | linked when the agent exists | ask the agent to use the skill |

A `git pull` updates everything: skills and commands are symlinks.

## Odoo is optional

Declare the project in the repo's `AGENTS.md`:

```md
<!-- ai-daridev:start -->
- odoo_project: acme-app
- odoo_stage_done: Sprint Complete
- card_tag: backend
<!-- ai-daridev:end -->
```

- `odoo_project` omitted → no cards, no board; stories live in the conversation and only the three
  files are written.
- Backlog stage = the project's first stage by sequence. `odoo_stage_done` is the validated column:
  review proposes the move there, and archive refuses to mark a card done outside it. Pair unblocks
  on `1_done`, not on the column.
- Archived cards (`1_done`) are hidden by the default board filter; enable `Closed Tasks` to see
  them.
- Evidence attachments use `ir.attachment` with read/create only; the agent's Odoo allowlist must
  include it. Browser screenshots come from `playwright-cli`.
- Tags are `frontend`, `backend`, `script`, `workflow`; `card_tag` is the repo default.
- Existing blocks from 3.x keep working: unknown keys are ignored.

## Upgrading from 3.x

- The old `ai-daridev preflight` command, the CLI and the Engram dependency are gone. Re-run
  `./scripts/install.sh`; it migrates the global instruction block for you.
- Existing cards are found by `ai-daridev: story/<slug>` or the legacy `engram: story/<slug>`.
- First run in a repo with `docs/decisions/*.md` or `openspec/`: one gate, then those decisions and
  specs are folded into `docs/ai-daridev/`; the originals stay as frozen history.
- `.engram/` is no longer read or written. Delete it when you are done with Engram.

## Principles

- **Don't invent.** Missing information gets asked, not filled in.
- **The simplest thing that works.** No abstractions "for the future".
- **Slice vertically and small.** One story = one session, ≤3 files; as many criteria and steps as it needs.
- **Suggest, don't decide.** Patterns, refactors and commits are your call.
- **Explicit checkpoints.** Every phase waits for your approval.

By Hola Mundo. Fork maintained by Dari Developer.
