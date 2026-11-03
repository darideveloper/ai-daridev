# Engram tool contract

The exact call shapes the skills use. This page exists because the docs drifted from the binary
once and cost a session; when in doubt, the tool schema wins.

## Resolution

The project is resolved from the **working directory** (nearest `.engram/config.json`), not from
the MCP server's startup state. `ai-daridev preflight` compares it with `engram_project` and fails
when they differ, so the skills never write into the wrong project.

## `mem_save`

| Field | Required | Notes |
|---|---|---|
| `title` | yes | ≤10 words, searchable |
| `content` | yes | `**What** / **Why** / **Where** / **Learned**` |
| `type` | yes | `decision`, `architecture`, `bugfix`, `pattern`, `config`, `discovery`, `learning` |
| `topic_key` | for upserts | max **two** levels: `story/<slug>`, `backlog/<project>`, `review/<slug>`, `retro/<slug>` |
| `project` | no | explicit override; accepted only if the project already exists |
| `scope` | no | `project` (default) or `personal` — a search filter, **not** privacy |

Same `project + scope + topic_key` upserts: the record grows, it does not duplicate.

## Sessions

| Tool | Arguments | When |
|---|---|---|
| `mem_session_start` | `id` (you generate it), optional `directory` | `/ai-daridev-pair` start |
| `mem_session_summary` | `summary` with the headings below | `/ai-daridev-pair` close |
| `mem_session_end` | `id`, optional `summary` | right after the summary |

Summary headings (six): **Goal · Instructions · Discoveries · Accomplished · Next steps · Relevant files**.

Without a session, saves land in a single growing manual session and `mem_timeline` becomes
useless for retros.

## `mem_search`

`query`, optional `type`, `project`, `scope`, `limit`. Returns compact previews plus IDs; use
`mem_get_observation` for the full body.

## Conflicts (`judgment_required`)

Some writes return `judgment_required` with candidate relations. The skills must not drop the
memory:

1. Prefer `mem_judge_many` (max 32), using `candidates[].judgment_id` — never the top-level
   `judgment_id`.
2. Ask the user only when confidence < 0.7, or when the relation is `supersedes` / `conflicts_with`
   and the type is `architecture`, `policy` or `decision`.
3. Otherwise resolve with `related`, `compatible`, `scoped` or `not_conflict`, passing the evidence.

## Keys the workflow writes

| Key | Type | Written by |
|---|---|---|
| `backlog/<project>` | `architecture` | `/ai-daridev-backlog` |
| `story/<slug>` | `architecture` | `/ai-daridev-story`, `/ai-daridev-pair` |
| `review/<slug>` or `review/task-<id>` | `decision` | `/ai-daridev-review` |
| `retro/<slug>`, `retro/sprint-<date>` | `learning` | `/ai-daridev-archive` |
| *(none)* | `decision` | `/ai-daridev-pair` (durable decisions only) |

## Versions and upgrades

The pinned version lives in `VERSION` at the repository root. `scripts/install.sh` upgrades with a
staged write (`mv`) because the old binary may be running as an MCP server. If
`engram compatibility` refuses, the upgrade **aborts** — it never silently replaces a live store.
