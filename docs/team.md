# Team

One person owns the board and the memory; everybody can work on the cards.

## Roles

| Role | Needs | Does |
|---|---|---|
| Owner | Engram, skills, Odoo | `/backlog`, `/story`, `/pair`, `/archive`, moves columns, validates work |
| Teammate | Engram, skills (Odoo optional) | picks a card, pastes it into their agent, submits the change |

The owner is the only one who moves cards and the only one who marks work done. That is what keeps
the board honest.

## The loop

```mermaid
sequenceDiagram
    autonumber
    actor Owner
    participant O as Odoo
    participant R as Repo
    actor T as Teammate
    participant TE as Teammate Engram

    Owner->>O: /backlog creates cards
    T->>O: reads the card, copies it
    T->>T: works with their own agent
    T->>R: commit / pull request
    Owner->>R: reviews the change in detail
    Owner->>O: validates, moves the column
    Owner->>Owner: /pair close if it was a tracked story
    Note over Owner,O: state=Approved + date_end, never a column move
    Owner->>R: engram sync + commit chunks
    T->>R: git pull
    T->>TE: engram sync --import
    TE-->>T: decisions become searchable
```

## What a teammate needs

```bash
git clone <this-repo>
cd ai-daridev
./scripts/install.sh        # Linux / macOS
# .\scripts\install.ps1     # Windows
```

That is enough for `/backlog`, `/story`, `/pair`, `/archive` to run: the installer brings Engram
with it. Odoo is optional, so a teammate without it still remembers decisions and just creates no
cards.

## Card hand-off

Cards are written to be self-sufficient, because a teammate may never see Engram:

```html
<h1>Retry-safe upload</h1>
<p>Uploads must survive retries without duplicating records.</p>
<h2>Acceptance criteria</h2>
<ul><li>Retrying never creates a second record</li></ul>
<h2>Tests</h2>
<ol><li>retry twice → exactly one record</li></ol>
<p><em>engram: story/retry-safe-upload</em></p>
```

The title, the criteria and the tests are the whole contract. The `engram:` line is for the agent,
not for the reader.

## Shared memory

```bash
# after pulling
engram sync --import

# before pushing
engram sync && git add .engram/ && git commit -m "chore: memory — <story>"
```

- Every sync writes a **new** chunk; nobody edits a chunk somebody else created.
- The manifest is the only shared file and merges by keeping both entries.
- `scope: personal` is **not** private: everything in an enrolled project is exported.
- Never put secrets, credentials or client data in memory.
