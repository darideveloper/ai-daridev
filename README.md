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
/backlog  →  /story  →  /pair  →  /archive
  what       what exactly   how        what happened
```

| Skill | What it does | What it never does |
|---|---|---|
| [`/backlog`](skills/backlog/SKILL.md) | Turns an idea into a short backlog of vertical, one-line user stories. | Invent requirements, technical stories, estimates. |
| [`/story`](skills/story/SKILL.md) | Takes **one** story, adds 2–3 Given/When/Then acceptance criteria and a mini plan (≤5 bullets) for your approval. | Write code. If it needs more than 3 criteria, it proposes splitting the story. |
| [`/pair`](skills/pair/SKILL.md) | Pair programming: the AI drives, you navigate. One test → red → minimum code → green, then it stops and waits. For non-code work it investigates, proposes a numbered plan, and executes it one step at a time. | Commit, edit tests to make them pass, add things you didn't ask for, move tracker columns. |
| [`/archive`](skills/archive/SKILL.md) | Closes a story or a sprint: reconciles the tracker card with the recorded decisions and prints the retro. | Move cards, mark work done, invent a retro with no records. |

Each skill's output is the next one's input, as blocks ready to paste into your tracker.

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
./scripts/install.sh          # Linux / macOS
# .\scripts\install.ps1       # Windows (junctions, falls back to copies)
```

The script installs **Engram** into `~/.local/bin` (and aborts if it cannot), removes any old
copied skills that would shadow the new ones, links the four skills into `~/.agents/skills` and every
agent directory that exists, and copies the OpenCode commands. It never edits your agent configs —
it prints the MCP snippets instead.

Supported agents: OpenCode, Claude Code, Codex, Gemini CLI, Continue, Windsurf.

> After `git pull`, re-run the installer so the copied commands stay in sync.

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

Each repository declares where things go in its `AGENTS.md`:

```md
## Workflow config
- odoo_project: acme-app
- odoo_stages: Backlog, Sprint Backlog, Sprint in Progress, Sprint Complete, Old Completed Sprint, Cancelled
- engram_project: acme-app
- decisions_dir: docs/decisions
- card_tag: one of frontend | backend | script | workflow
```

Open the agent **in the directory that holds `.engram/config.json`** — Engram resolves the project
from the working directory, and the skills stop rather than write into the wrong one.

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

## Install without the script

Copy the skill folders into your agent's skills directory:

```bash
cp -r skills/* ~/.claude/skills/          # Claude Code
cp -r skills/* ~/.agents/skills/          # Codex / OpenCode compatible layout
```

The skills are only invoked manually, never automatically.

---

By Hola Mundo. Fork maintained by Dari Developer.
