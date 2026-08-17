# Hermes AI Infrastructure & Knowledge System v1

This package is the production-hardened execution plan and prompt library for building a reusable AI-agent platform around:

- **Hermes Agent / Hermes Desktop** as the primary agent runtime.
- **Vercel Labs Agent Browser** as an external browser-automation capability.
- **Qdrant** as a private derived retrieval index.
- **A source-controlled knowledge repository** as the canonical knowledge source.
- **A remote MCP knowledge gateway** as the stable interface used by Hermes and other agents.
- **A repeatable ingestion pipeline** that accepts future raw documentation/tutorial data, normalizes it, validates it, versions it, and publishes it to Qdrant without manual database editing.

The package assumes a greenfield setup because no user project repository or attachment was mounted in the environment where this plan was authored. That assumption and the recovery implications are recorded in `DECISIONS.md`.

## What changed from the original conversational plan

The original direction was sound but had several production risks. The hardened design makes these corrections:

1. **Qdrant is never the source of truth.** Git is. Qdrant is disposable and rebuildable.
2. **Qdrant is not directly exposed to Hermes Desktop over the public internet.** Agents use an authenticated MCP retrieval gateway.
3. **Knowledge domains are payload metadata, not one Qdrant collection per technology.** A single logical collection/alias is used while the embedding schema is shared.
4. **Knowledge publishes are atomic.** A new versioned collection is built and verified, then the `knowledge_current` alias is switched atomically.
5. **Agent Browser is integrated without modifying Hermes core.** Hermes supports MCP servers, and Agent Browser provides an MCP stdio server.
6. **Browser authentication state is treated as a secret.** Agent Browser saved restore-state is encrypted and never committed; optional full Chrome profiles remain sensitive host-local state and are not claimed encrypted by that key.
7. **Repository structure, operational rules, recovery, and ingestion standards are established before services are installed.**
8. **GitHub push-to-VPS synchronization uses least privilege and a reconciliation timer.** A failed webhook/action cannot permanently desynchronize the index.
9. **Every execution prompt is standalone.** A new agent can run any prompt without this conversation.

## Package contents

- `PLAN.md` — final corrected plan and phase contracts.
- `AUDIT.md` — concrete findings, severities, fixes, and re-verification result.
- `DECISIONS.md` — assumptions and engineering decisions.
- `ARCHITECTURE.md` — component topology and data/control flows.
- `CONTRACTS.md` — concise cross-phase interfaces, endpoints, schemas, and ownership.
- `KNOWLEDGE_STANDARDS.md` — canonical normalization, chunking, metadata, and provenance rules.
- `INGESTION_CHECKLIST.md` — operator checklist for future data.
- `RECOVERY.md` — rebuild and disaster-recovery runbook.
- `EXECUTION_ORDER.md` — exact prompt sequence and dependencies.
- `REFERENCES.md` — authoritative sources used to harden this design.
- `VERIFICATION.md` — authoring-time evidence, package checks, and explicit runtime limitations.
- `MANIFEST.sha256` — package file checksums generated immediately before delivery.
- `prompts/` — five standalone execution prompts.
- `MASTER_PROMPT_LIBRARY.md` — all five prompts concatenated for easy archival/search.
- `docs/superpowers/specs/` — design spec produced through the Superpowers workflow.
- `docs/superpowers/plans/` — implementation-plan form of the same architecture.

## Recommended execution

Run the prompts in numeric order. Prompts 02 and 03 can run in parallel after Prompt 01, but a linear run is safest.

```text
01 Foundation & Repository Governance
        ├── 02 Agent Browser Installation & MCP
        └── 03 Qdrant Knowledge Platform & GitHub Sync
                    ├── 04 Hermes Integration  (also requires 02)
                    └── 05 Knowledge Ingestion & Update Workflow
```

Each agent must inspect the real environment first, preserve existing conventions when a repository already exists, execute verification commands, repair failures, and leave a handoff report.

## Default architecture contracts

These defaults are intentional and are not secrets:

- Dense embedding: `BAAI/bge-small-en-v1.5` — 384 dimensions.
- Sparse retrieval: `Qdrant/bm25`.
- Fusion: reciprocal rank fusion (RRF).
- Canonical Qdrant alias: `knowledge_current`.
- Default retrieval limit: 8, hard maximum 12.
- Knowledge schema version: 1.
- Knowledge Schema v1 language: English only (`en`); multilingual indexing requires a schema/model migration.
- Chunk target: 350 content tokens; full prefixed embedding input hard cap: 500 model tokens.
- Normalized content: Markdown, UTF-8.
- Qdrant network posture: private/internal only.
- External agent interface: MCP Streamable HTTP knowledge gateway.
- Browser interface for Hermes: Agent Browser MCP stdio server.
- Git repositories: one platform repository and one knowledge repository.

Runtime package versions are resolved from official stable releases at execution time and then pinned immutably by the implementing agent. This avoids shipping a stale “latest” version in a long-lived infrastructure prompt while still producing reproducible deployments.

## Definition of complete

The system is complete only when:

- both repositories are committed and recoverable;
- Agent Browser passes `doctor` plus a real open/snapshot/interact/screenshot/close test;
- Qdrant is persistent, authenticated, private, and restart-safe;
- a fixture corpus can be built into a staging collection and atomically published to `knowledge_current`;
- the knowledge MCP gateway passes unit, integration, and MCP protocol checks;
- GitHub push synchronization and the VPS fallback reconciliation path both work;
- Hermes discovers both MCP integrations and can complete one browser task and one grounded knowledge lookup;
- a new raw knowledge source can be ingested from source file through Git commit, publish, retrieval, provenance, and deletion/update behavior;
- a clean-machine recovery drill can rebuild the derived knowledge index from Git without relying on a Qdrant backup.
