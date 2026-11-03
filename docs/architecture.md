# Architecture

The integration has three layers. You type commands; the skills decide; the MCP servers are the
only thing that touches real data.

```mermaid
flowchart TB
    subgraph HUMANS["Humans"]
        OWNER["Owner"]
        TEAM["Team"]
    end
    subgraph AGENTS["Agents"]
        OC["OpenCode"]
        CC["Claude Code"]
        CX["Codex"]
        OTH["Gemini / Continue / Windsurf"]
    end
    subgraph SKILLS["Skills — one clone, symlinked"]
        BL["backlog"]
        ST["story"]
        PR["pair"]
        AR["archive"]
    end
    subgraph MCP["MCP servers (per agent)"]
        EM["engram"]
        OM["odoo"]
    end
    subgraph STORE["State"]
        DB[("SQLite<br/>~/.engram/engram.db")]
        CH["chunks<br/>repo/.engram"]
        OD[("Odoo<br/>project.task")]
    end

    OWNER --> OC & CC & CX
    TEAM --> OTH
    OC & CC & CX & OTH --> SKILLS
    SKILLS --> EM & OM
    EM --> DB
    EM --> CH
    OM --> OD
    TEAM --> OD
    TEAM --> CH

    classDef human fill:#FFE4B5,stroke:#333,color:black
    classDef agent fill:#87CEEB,stroke:#333,color:darkblue
    classDef skill fill:#90EE90,stroke:#333,color:darkgreen
    classDef mcp fill:#E6E6FA,stroke:#333,color:darkblue
    classDef store fill:#D3D3D3,stroke:#333,color:black
    class OWNER,TEAM human
    class OC,CC,CX,OTH agent
    class BL,ST,PR,AR skill
    class EM,OM mcp
    class DB,CH,OD store
```

## Division of responsibility

| Question | Answered by | Because |
|---|---|---|
| What is the work? | Odoo card | humans need to see it |
| Where is it in the process? | Odoo stage — **moved only by a human** | automation must not lie about status |
| Why was it built this way? | Engram decisions | searchable, per project, survives sessions |
| What does a reviewer read? | `docs/decisions/<slug>.md` | a diff, in the PR |
| What did the last story change? | Engram session summary | the agent's own trail |

Odoo is deliberate, visible and slow. Engram is automatic, invisible and fast. There is no two-way
sync: Odoo is authoritative for **state**, Engram for **knowledge**.

## Lifecycle

```mermaid
flowchart TD
    IDEA([Idea]) --> BL["/backlog"]
    BL --> BLW["Writes: N cards in the first stage<br/>one tag, sequence, optional deadline<br/>memory backlog/project"]
    BLW --> OK["Backlog approved"]
    OK --> ST["/story"]
    ST --> STW["Writes: card description as HTML<br/>memory story/slug<br/>no stage move"]
    STW --> PAIR["/pair — slug or pasted card"]
    PAIR --> MODE{"Repo has code<br/>and a test runner?"}
    MODE -->|Yes| CODE["TDD: red → green → stop"]
    MODE -->|No| NOCODE["Plan → approve once<br/>→ execute step by step"]
    MODE -->|Ambiguous| ASK["Ask once"]
    ASK --> MODE
    CODE --> DEC{"Durable decision?"}
    NOCODE --> DEC
    DEC -->|Yes| MEM["memory type=decision"]
    DEC -->|No| EPH["stays in chat"]
    MEM --> CLOSE
    EPH --> CLOSE
    CLOSE["Close: state=Approved + date_end<br/>ADR if shared contract<br/>summary + engram sync"]
    CLOSE --> ARCH["/archive — slug or bare"]
    ARCH --> OUT["Retro printed, memory retro/slug<br/>ADR only if it qualified"]
```

## What gets remembered

A `Decided:` line is only saved when it will still matter next month.

```mermaid
flowchart TD
    D["A Decided: line"] --> Q1{"Project-wide?"}
    Q1 -->|Yes| Q2{"Hard to reverse<br/>or shared contract?"}
    Q1 -->|No| Q3{"Hard to reverse<br/>local choice?"}
    Q2 -->|Yes| BOTH["Engram decision + ADR file"]
    Q2 -->|No| ENG["Engram decision only"]
    Q3 -->|Yes| ENG
    Q3 -->|No| EPH["Ephemeral, stays in chat"]

    classDef yes fill:#90EE90,stroke:#333,color:darkgreen
    classDef no fill:#FFB6C1,stroke:#DC143C,color:black
    class BOTH,ENG yes
    class EPH no
```

## Fail-open

Every integration is optional. A skill that cannot reach a tool says one line and continues.

```mermaid
flowchart TD
    S["Skill needs to write"] --> Q1{"Odoo available?"}
    Q1 -->|No| N1["Skip card work<br/>say one line, continue"]
    Q1 -->|Yes| Q2{"Engram available?"}
    Q2 -->|No| N2["Write the card<br/>skip memory silently"]
    Q2 -->|Yes| N3["Write card + memory"]
    N1 --> Q3{"Engram available?"}
    Q3 -->|Yes| N4["Memory only"]
    Q3 -->|No| N5["Ephemeral: upstream behavior"]

    classDef ok fill:#90EE90,stroke:#333,color:darkgreen
    classDef warn fill:#FFE4B5,stroke:#333,color:black
    classDef none fill:#D3D3D3,stroke:#333,color:black
    class N3 ok
    class N1,N2,N4 warn
    class N5 none
```

Next: [workflow](workflow.md) · [odoo](odoo.md) · [engram](engram.md)
