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
| `/ai-daridev-story` | Adds Given/When/Then criteria and a step checklist to **one** card, one hidden subtask per step, and moves it to the sprint column. | Write code. |
| `/ai-daridev-pair` | Drives: one test → red → minimum code → green, stops after every step and embeds a screenshot of the shipped UI per step in the card description. Plan-and-execute for non-code work. | Commit, edit tests to pass, add what you didn't ask for, move a card without your yes (starting the pair is the yes), start a blocked card. |
| `/ai-daridev-review` | Grades someone else's card against its criteria, steps and evidence, then writes the verdict and the move on approval. | Move a card without approval, invent a verdict, mark work done. |
| `/ai-daridev-archive` | Gates on the validated column and the green dot, marks the card done so Odoo frees its dependents, then appends the retro to `docs/ai-daridev/log.md`. | Move cards, cancel, create cards, invent a retro, turn a card green. |
| `/ai-daridev-check-plan` | Audits any plan in detail, fixes the gaps one question at a time and renders an ordered checklist. Outside the flow; with a named card it also updates the card checklist, its subtasks and the derived assignees. | Invent requirements, write files, move cards. |
| `/ai-daridev-campaign` | Runs the whole flow over a batch, unattended: one worktree per card, pair → integrate → deploy → review → archive, one gate at the start, parks what needs you. Outside the flow. | Waive evidence, archive a drifted card, cancel a card, run destructive non-code steps. |

Each phase ends waiting for your approval — except a campaign, which takes its one approval at the
start and then runs. Moves are proposed, never silent: a card changes column only when you ask or
approve it, in the same write as its state, and archive is the only phase that marks a card done. A
story's gate and the start of a pair are that ask: the card lands in the sprint column when its
checklist is approved, and in progress when the pair starts. Assignees are derived from the
checklist — the card follows whose step is next — so they are written with the step and reported,
not asked.

## What the agent writes

**In Odoo (optional):** one card per story — backlog cards at `backlog`, refined cards in the sprint
column, criteria and checklist in the description, one hidden subtask per step
(`display_in_project=False`) with its `[agent]`/`[you]` assignee, real **Blocked By** links for
`Requires: #N`, one dated **Evidence** section at the end of the card description — one entry per
step, keyed `pN "<step>"`, with the final UI screenshot inline and on prod — `state=03_approved` +
`date_end` when a story closes, and `state=1_done` at archive, which frees its dependents. `stage_id`
is written only when you ask or approve a move (approving the story checklist lands it in the sprint
column, starting pair in the in-progress column), always together with its state. The card's
assignees follow the checklist: agent user always, plus you while the next open step is yours.

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

`install.sh` symlinks every skill in `skills/` into `~/.agents/skills` and every installed agent, links the
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
- odoo_assignee_manual_uid: 2
<!-- ai-daridev:end -->
```

- `odoo_project` omitted → no cards, no board; stories live in the conversation and only the three
  files are written.
- Backlog stage = the project's first stage by sequence. `odoo_stage_done` is the validated column:
  review moves an approved card there with the green dot, and archive refuses to close a card that is
  not green in that column. Pair unblocks on `1_done`, not on the column. `odoo_stage_done` resolves
  inside that project's stages; a name shared with other projects is not a match.
- Archived cards (`1_done`) are hidden by the default board filter; enable `Closed Tasks` to see
  them.
- Evidence attachments use `ir.attachment` with read/create only; the agent's Odoo allowlist must
  include it. They are created on the **card** (`res_id` = the card, never a subtask) and embedded in
  the description with `/web/image/<id>`. Browser screenshots come from `playwright-cli`.
- Tags are `frontend`, `backend`, `infrastructure`, `script`, `workflow`; `card_tag` is the repo
  default. When the block declares `card_tag_extra`, every card carries that tag too.
- **Two users, one card.** The card carries the agent user — the MCP connection user, or
  `odoo_assignee_uid` when the block pins a different account — and carries
  `odoo_assignee_manual_uid` (you) only while the next open step is a `[you]` step. `[you]`
  subtasks are assigned to you from creation; the card is the signal that it is your turn. It is a
  derived write, diff-style (`[[4, uid]]` / `[[3, uid]]`), so it never wipes a person you added by
  hand. No manual uid → no handoff, and the first skill that needs one asks for the key.
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
