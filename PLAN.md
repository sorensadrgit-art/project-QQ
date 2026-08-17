# Final 10/10 Plan

## 10/10 gate

A phase passes only when:

- zero blocker findings remain;
- zero major findings remain;
- all interfaces and data contracts required by downstream phases are explicit;
- failure, retry, timeout, rollback, and recovery paths are specified;
- secrets and trust boundaries are explicit;
- accessibility requirements are addressed where a human interface is involved;
- performance limits and bounded operations are defined;
- validation/tests can prove the deliverable;
- a competent engineer can implement the phase without asking for architectural decisions.

## Phase map

### Phase 1 — Foundation and repository governance

**Builds**

- canonical two-repository structure;
- manifests and schema/version policies;
- security/secret rules;
- CI baseline;
- operations, recovery, and change-control documentation;
- exact path and naming contracts used by all later phases.

**Depends on**

- Git, an execution machine, and optional authenticated GitHub CLI for remote creation.

**Hands off**

- `SYSTEM_MANIFEST.yaml`;
- `KNOWLEDGE_MANIFEST.yaml`;
- repository roots and file conventions;
- standardized verification/reporting rules.

**Pass criteria**

- repositories validate locally;
- no secrets are tracked;
- CI/static checks are defined;
- clean-clone recovery instructions exist.

### Phase 2 — Agent Browser capability

**Builds**

- current stable Agent Browser installation on each browser host;
- pinned resolved version record;
- Chrome/Chromium runtime;
- encrypted restore-session policy plus explicit high-sensitivity persistent-profile fallback;
- safe action policy and content boundaries;
- MCP stdio exposure;
- reusable verification scripts;
- generic-agent usage documentation.

**Depends on**

- Phase 1 platform repository.

**Hands off**

- working `agent-browser` binary;
- exact MCP command;
- secret-file path contract;
- verification evidence;
- routing guidance for Hermes.

**Pass criteria**

- `agent-browser doctor` succeeds;
- real open/snapshot/interact/screenshot/close workflow succeeds;
- state encryption is configured;
- secret files are untracked and permission-restricted;
- MCP initialize/tool discovery succeeds.

### Phase 3 — Qdrant knowledge platform and GitHub synchronization

**Builds**

- persistent private Qdrant service;
- hybrid index schema;
- knowledge indexer;
- atomic blue/green publication;
- MCP knowledge gateway;
- GitHub push-triggered sync;
- reconciliation timer;
- snapshots and recovery drill;
- retrieval and provenance tests.

**Depends on**

- Phase 1 repositories and manifests.

**Hands off**

- `knowledge_current` alias;
- authenticated MCP endpoint;
- stable tool schemas;
- GitHub-to-VPS sync path;
- active knowledge commit observability.

**Pass criteria**

- Qdrant is not publicly reachable;
- fixture corpus publishes and retrieves correctly;
- failed publish cannot replace production;
- alias rollback works;
- GitHub trigger and timer reconciliation both work;
- clean rebuild from Git succeeds.

### Phase 4 — Hermes integration

**Builds**

- Agent Browser MCP registration;
- Knowledge Gateway MCP registration;
- source-controlled Hermes skills for retrieval and browser routing;
- minimal durable operating instructions;
- cross-surface verification for CLI and Desktop;
- safe fallback behavior.

**Depends on**

- Phase 2 Agent Browser;
- Phase 3 Knowledge Gateway.

**Hands off**

- Hermes config integration;
- available `mcp_agent_browser_*` and `mcp_knowledge_*` tools;
- routing skills;
- verification report.

**Pass criteria**

- Hermes discovers both MCP servers;
- browser task uses Agent Browser;
- technical question retrieves Qdrant context with provenance;
- unavailable knowledge gateway degrades clearly instead of fabricating;
- large docs are not copied into memory.

### Phase 5 — Knowledge ingestion and ongoing operations

**Builds**

- future-data intake workflow;
- deterministic cleaning/normalization;
- semantic chunking;
- source manifest and deduplication;
- validation and retrieval regression cases;
- one-command ingest/publish workflow;
- update/delete behavior;
- operator checklist and report format.

**Depends on**

- Phase 1 knowledge repo;
- Phase 3 indexer/gateway.
- Hermes integration is optional for ingestion itself.

**Hands off**

- “give an agent new data and say ingest it” operational capability;
- auditable source-to-chunk lineage;
- automatic publish on accepted main-branch changes.

**Pass criteria**

- new source, update, duplicate, rename, and deletion scenarios all pass;
- source provenance is preserved;
- malformed or rights-unclear input is quarantined rather than silently indexed;
- retrieval regression tests stay green.

## Project-wide contracts

### Versioning

Runtime dependencies are resolved from official stable release sources at execution time, then pinned. Every install/publish report records:

- package/image name;
- semantic version/tag;
- immutable digest or lockfile version where supported;
- retrieval/embedding schema version;
- Git commit.

### Secrets

Never commit:

- Qdrant admin/read-only keys;
- knowledge gateway bearer tokens;
- Agent Browser encryption keys;
- browser cookies/state/profile contents;
- GitHub deployment SSH private keys;
- raw credentials.

Secret files must be outside repository roots and mode `0600` on Unix. Services receive only the credentials they need.

### Knowledge schema v1

Required payload fields:

```text
schema_version        integer = 1
chunk_id              64-char lowercase SHA-256
content_hash          64-char lowercase SHA-256
domain                lowercase slug
source_id             stable string
source_type           enum:
                      official_doc
                      official_tutorial
                      community_pattern
                      internal
title                 non-empty string
section_path          array[string]
content               non-empty Markdown
source_path           repo-relative normalized path
source_url            HTTPS URL or null
language              exactly en in Knowledge Schema v1
tags                  array[lowercase slug]
rights                 enum:
                      owned
                      permitted
                      public_reference
                      restricted_summary_only
repo_commit           full lowercase 40- or 64-char Git object ID
published_at          UTC RFC3339
```

Optional fields:

```text
author
source_published_at
source_updated_at
tool_versions
related_chunk_ids
```

### Chunking

`hermes-kb-index plan` (Phase 03) is the single executable owner of chunk planning/token counting/identity. Phase 05 normalizes sources and delegates chunk planning to it; no second chunking implementation is permitted.

- UTF-8 Markdown.
- Prefer heading/semantic boundaries and keep ordered procedures semantically complete.
- The **entire dense embedding input**, including the `passage:` prefix plus title/domain/section context, must be **≤500 model tokens**. This leaves safety below the chosen model's 512-token context.
- Target normalized content: 350 tokens.
- Soft minimum normalized content: 80 tokens when the concept can stand alone.
- Hard normalized-content ceiling: 420 tokens, but the effective ceiling is lower whenever the prefix would make the complete embedding input exceed 500.
- Maximum overlap: 60 tokens.
- Long code blocks that exceed the dynamic budget are split at safe line/function/blank-line boundaries into separately fenced fragments with explicit part context; never rely on tokenizer truncation.
- Embed `passage:` + title + heading path + domain context, but keep canonical payload `content` unchanged.
- Query embeddings use a `query:` prefix.
- Chunk identity is `sha256(schema_version + domain + source_id + semantic section path + content_hash + duplicate-occurrence index)`; it excludes source checksum, repository path, and publish commit so unchanged chunks remain stable across source revisions and path refactors.
- Exact duplicate chunks by normalized content hash are stored once per source lineage; cross-source duplicates remain separate when provenance differs.

### Retrieval

- Dense model: `BAAI/bge-small-en-v1.5`, vector size 384, cosine.
- Sparse: `Qdrant/bm25`, configured with required IDF modifier.
- Fusion: RRF.
- Default top-k: 8.
- Hard top-k: 12.
- Filterable payload indexes: `domain`, `source_type`, `rights`, `language`, `schema_version`.
- Knowledge Schema v1 indexes only `language=en` because the selected dense and sparse model contract is English; non-English material is quarantined until a multilingual schema/model migration is explicitly designed and regression-tested.
- No unbounded search/result payloads.
- Gateway returns provenance with every result.

### Publish/rollback

- Every staging build has an atomic host-local sidecar `/var/lib/hermes-kb/builds/<collection>.json` containing the full source Git object ID, schema/model versions, counts, timestamps, and lifecycle state. Build metadata is never stored as a synthetic knowledge point.
- Full new versioned collection per publish.
- Test before alias switch.
- Atomic `knowledge_current` alias switch.
- Keep current plus two previous healthy builds.
- Failed staging build never affects alias.
- Rollback means atomically switching alias to the most recent known-good retained collection.

### Accessibility

There is no custom primary human UI in v1. Where human browser interaction occurs:

- login flows must work in headed browser mode;
- scripts must not depend only on screen coordinates;
- browser automation should prefer accessibility-tree refs and semantic locators;
- verification includes an accessibility snapshot/audit when testing pages controlled by the project.

### Performance budgets

- Gateway `top_k` hard cap: 12.
- Query input hard cap: 4,000 characters.
- Returned content per tool result: bounded to 60,000 characters total.
- Publish jobs are serialized.
- Embeddings cached by model+content hash.
- Gateway never returns vectors.
- Qdrant is sized and monitored for disk headroom before blue/green publish; required free persistent disk is at least 2.5× the expected active corpus/index footprint before a blue/green publish, covering active + staging + snapshot/headroom.
