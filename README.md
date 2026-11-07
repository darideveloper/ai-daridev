# ai-daridev

Agent skills for building software with AI **without letting go of the wheel**. Inspired by Extreme Programming: vertical user stories, acceptance criteria, test-first, pair programming, simple design.

The AI splits, proposes and writes code in small steps. You decide.

This is a fork of [hola-ai](https://github.com/nschurmann/hola-ai) that adds a **memory + tracker
layer**: decisions go to [Engram](https://github.com/Gentleman-Programming/engram), work items go to
Odoo. **Engram is required** — the skills refuse to run without it. **Odoo is optional.**

- [Architecture](docs/architecture.md) · [Workflow](docs/workflow.md) · [Odoo contract](docs/odoo.md)
- [Engram memory](docs/engram.md) · [Agents](docs/agents.md) · [Team](docs/team.md)
- [AGENTS.md template](AGENTS.template.md)

## The flow

```
/ai-daridev-backlog  →  /ai-daridev-story  →  /ai-daridev-pair  →  /ai-daridev-review  →  /ai-daridev-archive
  what       what exactly   how        is it right?        what happened
```

| Skill | What it does | What it never does |
|---|---|---|
| [`/ai-daridev-backlog`](skills/ai-daridev-backlog/SKILL.md) | Turns an idea into a short backlog of vertical, one-line user stories. | Invent requirements, technical stories, estimates. |
| [`/ai-daridev-story`](skills/ai-daridev-story/SKILL.md) | Takes **one** story, adds 2–3 Given/When/Then acceptance criteria and a 5–20 step plan (one hidden subtask per step) for your approval. | Write code. If it needs more than 3 criteria, it proposes splitting the story. |
| [`/ai-daridev-pair`](skills/ai-daridev-pair/SKILL.md) | Pair programming: the AI drives, you navigate. One test → red → minimum code → green, then it stops and waits. For non-code work it investigates, proposes a numbered plan, and executes it one step at a time. | Commit, edit tests to make them pass, add things you didn't ask for, move tracker columns. |
| [`/ai-daridev-review`](skills/ai-daridev-review/SKILL.md) | Reviews someone else's card against its criteria and plan steps, proposes the writes, and applies them after approval. | Move a card without a separate confirmation, invent a verdict, mark work done. |
| [`/ai-daridev-archive`](skills/ai-daridev-archive/SKILL.md) | Closes a story or a sprint: asks which card(s), reconciles the tracker with memory, prints the retro, and exports the memory chunk. | Move cards, mark work done, invent a retro with no records. |

Each skill's output is the next one's input, as blocks ready to paste into your tracker.

The plan is the checklist. `/ai-daridev-story` writes 5–20 steps and creates one hidden subtask per
step, keyed `ai-daridev: plan/<slug>#pN` in its description. The card shows the steps (name and
detail, no status); the subtasks carry the state. Structure changes ask once, state changes are
reported, and every change prints the plan in chat with counts and the next step.

Cards also carry a `Review (ai-daridev)` section once someone has reviewed the work.

Outside the flow, [`/ai-daridev-check-plan`](skills/ai-daridev-check-plan/SKILL.md) audits a plain-text
plan already in the chat, fixes the gaps and returns a leaner one. Chat-only: no Engram, no Odoo, no
`preflight`.

## Principles

- **Don't invent.** Missing information gets asked, not filled in.
- **The simplest thing that works.** No abstractions "for the future".
- **Slice vertically and small.** Stories cross every layer; steps are one test and ~50 lines.
- **Suggest, don't decide.** Patterns, refactors and commits are your call.
- **Explicit checkpoints.** Every phase ends waiting for your approval.

## Install

```bash
git clone git@github.com:darideveloper/ai-daridev.git
cd ai-daridev
./scripts/setup.sh            # Linux / macOS: install + MCP + instruction block
# .\scripts\install.ps1      # Windows: installs and links; MCP snippets printed
```

`setup` installs or upgrades **Engram** (version pinned in `VERSION`, staged write, aborts if
`engram compatibility` refuses), symlinks the skills and the OpenCode commands, **applies** the
MCP entries with timestamped backups (Engram always; Odoo only when a wrapper and its 600-perm env
file exist), and writes the `<!-- ai-daridev -->` block into the four agent instruction files.

`setup --dry-run` shows every write. `setup --restore` puts the latest backup back.

Supported agents: OpenCode, Claude Code, Codex, Gemini CLI, Continue, Windsurf, Kiro, Devin.

> After `git pull` there is nothing to re-run for the skills or the commands: they are links to this
> clone. Re-run the installer only to pick up a new Engram pin or a newly installed agent.

## Engram is required

Every skill reads and writes memory: the spec for a story, the decisions taken, the retro. Without
the memory MCP the skills stop and ask you to install it, instead of running half-blind.

```jsonc
// register once per agent, e.g. OpenCode
"engram": { "type": "local", "command": ["<home>/.local/bin/engram", "mcp", "--tools=agent"], "disabled": false }
```

## Odoo is optional

Without Odoo the skills still remember everything; they just create no cards. With Odoo (any MCP
server for `project.task`) they also:

- create a card in the **first stage**,
- update its `description`,
- set `state=03_approved` + `date_end` when a story closes.

They never move a card between columns and never mark it done or cancelled.

Each repository declares where things go in its `AGENTS.md`, between markers. Generate it with
`ai-daridev init` instead of writing it by hand:

```md
<!-- ai-daridev:start -->
## Workflow config
- version: 1
- odoo_project: acme-app
- odoo_stage_backlog: Backlog
- odoo_stage_active: Sprint Backlog, Sprint in Progress
- odoo_stage_done: Sprint Complete
- odoo_stage_cancelled: Cancelled
- odoo_assignees: false
- card_tag: backend
- card_tags: frontend, backend, script, workflow
- engram_project: acme-app
- decisions_dir: docs/decisions
- plan_steps: 5-20
- listing_limit: 20
<!-- ai-daridev:end -->
```

`odoo_uid` is deliberately **not** in the block: it is personal and lives in
`~/.config/ai-daridev/repos/<repo>.json`, set with `ai-daridev uid <n>`.

Open the agent **in the directory that holds `.engram/config.json`** — Engram resolves the project
from the working directory, and `ai-daridev preflight` stops rather than write into the wrong one.

## Preflight

Every skill starts with:

```bash
ai-daridev preflight     # JSON: project, stages, tags, uid, listing, plan_steps
```

If it exits non-zero, the skill prints its errors and stops. The contract is in
[docs/preflight.md](docs/preflight.md); the tool call shapes are in
[docs/engram-api.md](docs/engram-api.md).

## Sharing memory with a team

The database never leaves your machine; the decisions travel as append-only chunks.

```bash
# in the repo, first time
engram init <project-name>
engram sync && git add .engram/ && git commit -m "chore: memory"

# after every pull
engram sync --import

# before pushing
engram sync && git add .engram/ && git commit -m "chore: memory — <story>"
```

`.engram/engram.db*` is gitignored. `scope: personal` is a search filter, **not** a privacy
boundary — everything in an enrolled project is exported, so never store secrets in Engram.

`/ai-daridev-pair`, `/ai-daridev-review` and `/ai-daridev-archive` import memory at the start.
`/ai-daridev-pair` and `/ai-daridev-archive` commit it: they stage `.engram/` only, refuse if
anything else is staged, and never push.

## Install without the script

Copy the skill folders into your agent's skills directory:

```bash
cp -r skills/* ~/.claude/skills/          # Claude Code
cp -r skills/* ~/.agents/skills/          # Codex / OpenCode compatible layout
```

The skills are only invoked manually, never automatically.

---

By Hola Mundo. Fork maintained by Dari Developer.
