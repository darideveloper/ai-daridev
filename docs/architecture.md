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
        BL["ai-daridev-backlog"]
        ST["ai-daridev-story"]
        PR["ai-daridev-pair"]
        RV["ai-daridev-review"]
        AR["ai-daridev-archive"]
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
    class BL,ST,PR,RV,AR skill
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
    IDEA([Idea]) --> BL["/ai-daridev-backlog"]
    BL --> BLW["Writes: N cards in the first stage<br/>one tag, sequence, optional deadline<br/>memory backlog/project"]
    BLW --> OK["Backlog approved<br/>cards + markers"]
    OK --> ST["/ai-daridev-story"]
    ST --> STW["Writes: card description as HTML<br/>memory story/slug<br/>no stage move"]
    STW --> PAIR["/ai-daridev-pair — slug or pasted card"]
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
    CLOSE["Close: state=Approved + date_end<br/>markers confirmed<br/>ADR if shared contract<br/>summary + engram sync"]
    CLOSE --> ARCH["/ai-daridev-archive — slug or bare"]
    ARCH --> OUT["Retro printed, memory retro/slug<br/>ADR only if it qualified"]

    TEAM([Card built by someone else]) --> RV["/ai-daridev-review"]
    RV --> VERD{"Verdict"}
    VERD -->|correct| MOVE["Propose: move to Sprint Complete<br/>(separate confirmation)"]
    VERD -->|wrong| CHG["Markers + parent yellow<br/>Review block in the card"]
    CHG --> RV
    MOVE --> ARCH
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

## When a tool is missing

**Engram is required**: without memory the skill stops and asks you to install it. **Odoo is
optional**: without it the skill says one line and continues without cards.

```mermaid
flowchart TD
    S["Skill starts"] --> M{"Engram available?"}
    M -->|No| STOP["Stop: install Engram<br/>and restart the agent"]
    M -->|Yes| Q1{"Odoo available?"}
    Q1 -->|No| N1["Memory only<br/>no cards, one line"]
    Q1 -->|Yes| N2["Memory + cards"]

    classDef stop fill:#FFB6C1,stroke:#DC143C,color:black
    classDef ok fill:#90EE90,stroke:#333,color:darkgreen
    classDef warn fill:#FFE4B5,stroke:#333,color:black
    class STOP stop
    class N2 ok
    class N1 warn
```

Next: [workflow](workflow.md) · [odoo](odoo.md) · [engram](engram.md)
