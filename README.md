# Hermes AI Infrastructure & Knowledge System v1

This repository is the **project-control and execution-prompt repository** for the Hermes + Agent Browser + Qdrant knowledge system.

It contains the architecture, contracts, operating/recovery rules, and the five standalone prompts that can be handed to separate agents. It does **not** store runtime secrets, browser sessions, Qdrant data, or the future technical knowledge corpus itself.

## Start here

1. Read `REPO_MAP.md` to see exactly what belongs in this repository, on the VPS, on the Hermes host, and in the future `hermes-platform` / `hermes-knowledge` repositories.
2. Read `EXECUTION_ORDER.md`.
3. Give `prompts/01_foundation_and_repo_governance.md` to the first implementation agent.
4. Continue through Prompts 02–05 according to the dependency order.

## Execution sequence

```text
01 Foundation & Repository Governance
        ├── 02 Agent Browser Installation & MCP
        └── 03 Qdrant Knowledge Platform & GitHub Sync
                    ├── 04 Hermes Integration  (also requires 02)
                    └── 05 Knowledge Ingestion & Update Workflow
```

Prompts 02 and 03 may run in parallel after Prompt 01. A linear `01 → 02 → 03 → 04 → 05` run is the simplest operational sequence.

## Files intentionally stored here

- `README.md` — entry point for the project.
- `REPO_MAP.md` — where every component/file belongs and where each prompt runs.
- `PLAN.md` — final production architecture and phase contracts.
- `ARCHITECTURE.md` — runtime topology and data/control flows.
- `CONTRACTS.md` — shared schemas, endpoints, security boundaries, and handoffs.
- `DECISIONS.md` — engineering assumptions and rationale.
- `EXECUTION_ORDER.md` — prompt dependencies and safe parallelization.
- `KNOWLEDGE_STANDARDS.md` — durable source cleaning/chunking/provenance standard.
- `INGESTION_CHECKLIST.md` — repeatable checklist for future data.
- `RECOVERY.md` — rebuild and disaster-recovery rules.
- `REFERENCES.md` — authoritative product/documentation references.
- `VERIFICATION.md` — authoring-time verification scope and runtime limitations.
- `prompts/` — the five standalone implementation prompts.

The original downloadable archive also contained authoring/package-only artifacts such as the concatenated master prompt file, archive checksum manifest, package verifier, and Superpowers authoring documents. Those are useful for archival/audit purposes but are **not required for operating this GitHub project**, so they are intentionally not duplicated here.

## What this repository is not

This repository is not the long-term technical corpus and is not a secret store.

Prompt 01 creates or normalizes the two operational source-of-truth repositories used by the implemented system:

```text
hermes-platform   → infrastructure, services, integrations, CI, runbooks
hermes-knowledge  → Spline/GSAP/React/WebGL/etc source + normalized knowledge
```

Once those exist, new Spline docs, tutorials, community-pattern abstractions, GSAP docs, React docs, WebGL material, and future knowledge go into `hermes-knowledge` through the ingestion workflow—not into this project-control repo root.

## Never commit these

Do not place any of the following in this repository or any other Git repository:

- browser cookies, storage state, or Chrome profiles;
- `AGENT_BROWSER_ENCRYPTION_KEY` values;
- Qdrant API/admin keys;
- `KNOWLEDGE_MCP_BEARER_TOKEN` values;
- SSH private keys;
- populated `.env` secret files;
- Hermes `~/.hermes/.env`;
- passwords, 2FA recovery codes, session tokens, or authenticated screenshots containing secrets.

## Core architecture

- **Hermes Agent / Hermes Desktop** is the primary agent runtime.
- **Agent Browser** provides interactive browser automation over MCP stdio.
- **Qdrant** is a private, disposable/rebuildable retrieval index.
- **Git** is authoritative for knowledge and infrastructure definitions.
- **Knowledge Gateway** exposes bounded authenticated retrieval to Hermes and other agents; general agents do not talk directly to Qdrant.
- **Knowledge publication is atomic** through versioned collections and the stable `knowledge_current` alias.
- **Future knowledge ingestion is repeatable**: source → provenance/rights → normalize → validate → Git → publish → retrieval verification.

## Default retrieval contract

```text
Dense model: BAAI/bge-small-en-v1.5
Dense dimensions: 384
Sparse model: Qdrant/bm25
Fusion: RRF
Stable alias: knowledge_current
Knowledge schema: v1
Schema-v1 language: en
Default top_k: 8
Hard top_k: 12
Full prefixed embedding input hard cap: 500 model tokens
```

Runtime software versions are resolved from current official stable releases during execution and then pinned exactly by the implementing agent.

## Completion standard

The project is not considered deployed merely because these prompts exist. Runtime completion requires hard evidence from the actual hosts: Agent Browser functional/MCP tests, private/authenticated Qdrant, atomic fixture publication and rollback, GitHub synchronization, Hermes MCP discovery, grounded retrieval, browser execution, and a clean rebuild from Git.
