# Cross-Phase Contracts

This file is a concise interface registry. The full rationale and failure behavior live in `PLAN.md`, `ARCHITECTURE.md`, and the numbered prompts.

## Repository ownership

| Repository | Canonical responsibility |
|---|---|
| `hermes-platform` | infrastructure, services, integrations, CI, operational/recovery documentation |
| `hermes-knowledge` | source text/provenance, normalized Markdown, source manifest, retrieval regressions |

Git is authoritative. Qdrant is derived.

## Runtime endpoints

| Component | Default bind | Agent access |
|---|---|---|
| Qdrant REST/dashboard | `127.0.0.1:6333` on VPS | never direct general-agent access |
| Knowledge MCP Gateway | `127.0.0.1:8790` on VPS | private mesh / TLS / SSH tunnel |
| SSH tunnel fallback | Hermes `127.0.0.1:18790` → VPS `127.0.0.1:8790` | Hermes remote MCP |
| Agent Browser | local process | MCP stdio wrapper |

Bindings may use a pre-existing private interface instead of loopback only when security remains equivalent and the decision is documented.

## Qdrant naming

```text
Stable alias: knowledge_current
Build collection: knowledge_v1_YYYYMMDDTHHMMSSZ_GIT12
Retain: current + two previous healthy builds
```

## Retrieval schema

Dense:

```text
model: BAAI/bge-small-en-v1.5
dimension: 384
distance: cosine
```

Sparse:

```text
model: Qdrant/bm25
idf: enabled as required by resolved Qdrant/FastEmbed version
```

Fusion:

```text
RRF
default top_k: 8
hard top_k: 12
query max: 4000 chars
response content budget: 60000 chars
```

Chunking/embedding budget:

```text
target normalized content: 350 model tokens
soft minimum: 80
hard normalized content ceiling: 420
hard complete prefixed embedding input ceiling: 500
maximum overlap: 60
document prefix: passage:
query prefix: query:
```

## Knowledge MCP tools

### `knowledge_search`

Input:

```json
{
  "query": "string 2..4000",
  "top_k": 8,
  "domains": [],
  "source_types": [],
  "rights": [],
  "language": null,
  "schema_version": 1
}
```

Output includes active collection, active Git commit, and bounded hits with content + provenance.

### `knowledge_get`

Input is a 64-character SHA-256 `chunk_id`. Output is the complete v1 chunk plus active build metadata, or a structured not-found result.

### `knowledge_domains`

No required input. Returns active domains and bounded point/source counts.

### `knowledge_health`

Returns status, active collection, active repository commit, knowledge schema, models, point count, and checked time. Never returns secrets.

## Knowledge chunk payload

Required:

```text
schema_version = 1
chunk_id
content_hash
domain
source_id
source_type
title
section_path[]
content
source_path
source_url|null
language
tags[]
rights
repo_commit
published_at
```

Enums:

```text
source_type:
  official_doc
  official_tutorial
  community_pattern
  internal

rights:
  owned
  permitted
  public_reference
  restricted_summary_only
```

## Publication state machine

```text
VALIDATE_GIT
→ CAPACITY_CHECK
→ CREATE_STAGING_COLLECTION
→ CREATE_PAYLOAD_INDEXES
→ EMBED_AND_UPSERT
→ POINT_COUNT_CHECK
→ RETRIEVAL_REGRESSIONS
→ WRITE_BUILD_METADATA
→ ATOMIC_ALIAS_SWITCH
→ POST_SWITCH_VERIFY
→ SNAPSHOT
→ RETENTION_CLEANUP
→ COMPLETE
```

Any failure before alias switch leaves production unchanged. Any correctness failure immediately after switch must switch back to the previously known-good alias target.

## Browser state boundary

- default profile is dedicated to agent automation;
- saved state encrypted;
- encryption key host-local only;
- per-task sessions isolated;
- no cookie/storage/profile material in Git;
- page content is untrusted;
- destructive/financial/security/account-changing actions require explicit authorization from the invoking task.

## Handoff files

```text
docs/handoffs/01-foundation.md
docs/handoffs/02-agent-browser.md
docs/handoffs/03-qdrant-knowledge-platform.md
docs/handoffs/04-hermes-integration.md
docs/handoffs/05-knowledge-ingestion.md
```

Handoffs contain observed facts and verification evidence, never secret values.
