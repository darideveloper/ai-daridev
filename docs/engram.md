# Engram — durable memory

[Engram](https://github.com/Gentleman-Programming/engram) is a single Go binary with a local SQLite
database. The skills use it to remember **why**, not **what**: decisions, specs, retros.

## What it stores

| Key | Type | Written by | Content |
|---|---|---|---|
| `backlog/<project>` | `architecture` | `/ai-daridev-backlog` | the approved backlog + card ids |
| `story/<slug>` | `architecture` | `/ai-daridev-story`, `/ai-daridev-pair` | criteria, plan, test list, card id |
| *(no key)* | `decision` | `/ai-daridev-pair` | one durable decision, append-only |
| `review/<slug>` or `review/task-<id>` | `decision` | `/ai-daridev-review` | verdict, what failed, date |
| `retro/<slug>` | `learning` | `/ai-daridev-archive` | the story retro |
| `retro/sprint-<date>` | `learning` | `/ai-daridev-archive` | the sprint retro |

`topic_key` supports at most **two levels** — that is why the project is part of the key and not
another slash.

## Project binding

Engram resolves the project from the **process working directory**:

1. nearest `.engram/config.json` inside the enclosing git root → its `project_name`
2. otherwise the git `origin` remote name
3. otherwise the git root folder name
4. otherwise the folder name

So each repository (or subproject) runs `engram init <name>` once and commits `.engram/config.json`:

```bash
cd <repo>
engram init acme-app
engram sync
git add .engram/config.json && git commit -m "chore: bind engram project"
```

Rules that follow from this:

- **Open the agent in the directory that holds `.engram/config.json`.** From a monorepo root Engram
  resolves the parent project, not the subproject.
- The skills **stop** if the resolved project is not the `engram_project` declared in `AGENTS.md`.
  They never write into the wrong project.
- An explicit `project:` argument only works **after** the project has at least one memory —
  before that the store answers `unknown_project`. The first write must come from the right cwd.

## Sessions

`/ai-daridev-pair` opens a session (`mem_session_start`) and closes it at the end (`mem_session_summary`,
`mem_session_end`). Without a session, saves land in a single growing "manual save" session, which
makes `mem_timeline` useless for retros.

If the memory tools are missing, the skills stop: memory is required, not best-effort.

## Freshness

`/ai-daridev-pair`, `/ai-daridev-review` and `/ai-daridev-archive` run `engram sync --import` in the
directory holding `.engram/config.json` before using memory. A failure warns and continues — an
import problem must never block the work.

## Sharing through git

The database never leaves the machine. Decisions travel as append-only, content-hashed chunks.

```bash
# before pushing
engram sync
git add .engram/ && git commit -m "chore: memory — <story>"

# after pulling
engram sync --import
```

```
<repo>/.engram/
├── config.json      # project identity (committed)
├── manifest.json    # index of chunks (committed, append-only)
└── chunks/*.jsonl.gz  # ~2 KB per sync (committed)
```

`/ai-daridev-pair` and `/ai-daridev-archive` both commit: after exporting, they stage `.engram/`
only, refuse if anything else is staged, commit `chore: memory — <slug>`, and never push.

`engram.db*` and `tmp/` are gitignored. Every sync writes a **new** chunk, so two people never edit
the same file; the manifest is the only thing that can conflict and it merges by keeping both
entries.

## Privacy

- Prompt records are **excluded** from git export by default (`--include-prompts` to opt in).
- `scope: personal` is a **search filter, not a privacy boundary**: observations of an enrolled
  project are exported regardless of scope.
- Nothing is redacted. A pasted token or stack trace committed to `.engram/` is in git forever.
- Never store secrets, credentials or client data in memory.

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `unknown_project` | project has no memories yet, or wrong cwd | open the agent in the repo that has `.engram/config.json` |
| memory not found after a pull | chunks are present but not imported | `engram sync --import` |
| retro has no timeline | saves went to the manual session | keep `/ai-daridev-pair`'s session start/end |
| two projects in the list for one repo | repo cloned before `engram init`, or a renamed remote | `engram projects list`, then `engram projects merge --from <a> --to <b> --apply` |
