# Architecture

## System boundary

The platform is split into two Git repositories because infrastructure lifecycle and knowledge-content lifecycle are different.

### `hermes-platform`

Owns executable infrastructure and operational contracts:

```text
hermes-platform/
├── README.md
├── AGENTS.md
├── DECISIONS.md
├── CHANGELOG.md
├── SECURITY.md
├── SYSTEM_MANIFEST.yaml
├── docs/
│   ├── architecture.md
│   ├── operations.md
│   ├── recovery.md
│   └── runbooks/
├── infra/
│   ├── agent-browser/
│   │   ├── install.sh
│   │   ├── verify.sh
│   │   ├── action-policy.json
│   │   └── env.example
│   └── qdrant/
│       ├── compose.yaml
│       ├── qdrant-config.yaml
│       ├── backup.sh
│       ├── restore-test.sh
│       └── sync-trigger.sh
├── services/
│   ├── knowledge-gateway/
│   └── knowledge-indexer/
├── integrations/
│   └── hermes/
│       ├── README.md
│       ├── install.sh
│       ├── verify.sh
│       ├── bin/
│       └── skills/
├── tests/
│   ├── e2e/
│   └── fixtures/
└── .github/workflows/
    └── platform-ci.yml
```

### `hermes-knowledge`

Owns canonical source material and normalized retrieval documents:

```text
hermes-knowledge/
├── README.md
├── AGENTS.md
├── KNOWLEDGE_STANDARDS.md
├── CONTRIBUTING.md
├── KNOWLEDGE_MANIFEST.yaml
├── sources/
│   ├── spline/
│   ├── gsap/
│   ├── react/
│   └── webgl/
├── normalized/
│   ├── spline/
│   ├── gsap/
│   ├── react/
│   └── webgl/
├── manifests/
│   └── sources.jsonl
├── tests/
│   └── retrieval_cases.yaml
└── .github/workflows/
    └── validate-knowledge.yml
```

Raw binary video is not committed. Store transcript text, permitted document source material, source URLs, checksums, provenance, and normalized knowledge. Respect source licenses and do not redistribute content where rights do not permit it.

## Runtime topology

```text
                    ┌───────────────────────────────┐
                    │       GitHub (private)        │
                    │                               │
                    │ hermes-platform               │
                    │ hermes-knowledge              │
                    └──────────────┬────────────────┘
                                   │ push
                                   ▼
                         GitHub Actions trigger
                                   │
                      restricted SSH command only
                                   │
                                   ▼
┌──────────────────────────────── VPS ────────────────────────────────┐
│                                                                    │
│  knowledge repo checkout ──► knowledge-indexer                     │
│                                │                                   │
│                                │ hybrid vectors                    │
│                                ▼                                   │
│                      ┌────────────────────┐                         │
│                      │ Qdrant            │                         │
│                      │ private network   │                         │
│                      │ versioned builds  │                         │
│                      │ alias:            │                         │
│                      │ knowledge_current │                         │
│                      └─────────┬──────────┘                         │
│                                │ internal API + key                 │
│                                ▼                                   │
│                      ┌────────────────────┐                         │
│                      │ Knowledge Gateway │                         │
│                      │ MCP Streamable    │                         │
│                      │ HTTP              │                         │
│                      └─────────┬──────────┘                         │
│                                │ localhost/private network          │
└────────────────────────────────┼────────────────────────────────────┘
                                 │ secure path
                                 │ (private mesh, TLS proxy, or SSH)
                                 ▼
                    ┌────────────────────────┐
                    │ Hermes Desktop / CLI   │
                    │                        │
                    │ mcp_knowledge_*        │
                    │ mcp_agent_browser_*    │
                    │ Hermes memory/skills   │
                    └──────────┬─────────────┘
                               │ stdio
                               ▼
                    ┌────────────────────────┐
                    │ Vercel Agent Browser   │
                    │ encrypted auth state   │
                    │ isolated sessions      │
                    └────────────────────────┘
```

## Retrieval data model

Every physical Qdrant collection uses the canonical runtime-generated grammar:

```text
knowledge_v1_YYYYMMDDTHHMMSSZ_GIT12
```

The timestamp is UTC and `GIT12` is the first 12 lowercase characters of the exact source Git object ID. Implementations construct the real name at publish time; this string is the grammar, not a hard-coded collection name.

The stable alias is always:

```text
knowledge_current
```

All consumers query the alias, never a versioned collection name.

Each point has two vectors:

- `dense`: 384-dimensional cosine vector generated by `BAAI/bge-small-en-v1.5`.
- `sparse`: BM25 sparse vector generated using `Qdrant/bm25`.

Domains such as `spline`, `gsap`, `react`, and `webgl` are payload values and indexed filter fields, not separate collections. A separate collection is justified only when the vector schema, payload schema, isolation requirement, or scaling profile materially differs.

## Publish flow

1. Acquire the VPS-side publication lock.
2. Verify the knowledge checkout is clean and exactly at the requested Git object ID.
3. Validate repository schema, provenance, rights, and manifests.
4. Call the canonical Phase 03 indexer planner on normalized Markdown.
5. Estimate disk headroom, then reuse cached embeddings by content hash where valid.
6. Create a new versioned staging collection and all required payload indexes.
7. Embed and upload bounded batches; assert point count equals the deterministic plan.
8. Run fixture and repository retrieval regressions plus provenance checks.
9. Atomically write the staging build sidecar with state `verified_staging`.
10. Perform one atomic alias change for `knowledge_current`.
11. Verify the alias and sidecar agree on the full source commit, then mark the sidecar `active`.
12. Snapshot the active collection.
13. Retain the active build plus the two immediately previous healthy builds.
14. Emit the machine-readable publish report and release the lock.

A pre-switch failure deletes the staging collection and leaves production untouched. A post-switch verification or snapshot failure atomically restores the previous healthy alias target and marks the failed build `failed_post_switch`.

## GitHub synchronization

GitHub does not write directly to Qdrant.

- The VPS has a **read-only repository deploy key** for `hermes-knowledge`.
- A GitHub Actions workflow uses a separate least-privilege SSH credential to call one restricted server-side sync command after a validated push to the protected main branch.
- `authorized_keys` restricts that credential to the sync command.
- The sync command itself performs the Git fetch and publish.
- A systemd reconciliation timer periodically compares the active published Git commit with the remote main commit and self-heals missed triggers.
- Concurrent publishes are blocked with `flock`.

This design prevents a GitHub workflow from receiving the Qdrant administrator key.

## MCP knowledge contract

The gateway exposes only these tools:

### `knowledge_search`

Input:

```json
{
  "query": "string, 2..4000 characters",
  "top_k": 8,
  "domains": [],
  "source_types": [],
  "rights": [],
  "language": null,
  "schema_version": 1
}
```

Rules:

- `top_k` defaults to 8; values below 1 or above 12 are validation errors, so `top_k > 12 is rejected` rather than silently clamped.
- `domains`, `source_types`, `rights`, `language`, and `schema_version` are exact allowlisted payload filters.
- The dense query input begins with `query: `; dense and BM25 results are fused with reciprocal-rank fusion.
- Retrieval has a 10-second default end-to-end deadline and at most one retry for a clearly transient Qdrant connection failure.
- Returned vectors and generic Qdrant syntax are never exposed.
- Total returned content is bounded to 60,000 characters.

Output:

```json
{
  "query": "original query",
  "active_collection": "knowledge_v1_...",
  "active_repo_commit": "40-or-64-character git object ID",
  "hits": [
    {
      "score": 0.0,
      "content": "markdown",
      "title": "string",
      "source_id": "stable-source-id",
      "source_path": "normalized/spline/...",
      "source_url": "https URL or null",
      "domain": "spline",
      "section_path": ["Animation", "States"],
      "rights": "public_reference",
      "repo_commit": "40-or-64-character git object ID"
    }
  ]
}
```

### `knowledge_get`

Input: `chunk_id`.

Output: one chunk with the same provenance fields. Never performs arbitrary filesystem reads.

### `knowledge_domains`

Returns indexed domains and point counts.

### `knowledge_health`

Returns gateway version, active Qdrant alias target, knowledge Git commit, embedding schema version, and readiness state. It returns no secrets or internal credentials.

## Browser integration contract

Agent Browser is installed on the machine where the browser actually runs. Hermes consumes it through the official Agent Browser MCP stdio server.

Browser state policy:

- encrypted stable restore sessions are the default authenticated persistence; full persistent profiles are per-site exceptions and remain sensitive host-local data;
- the user’s default Chrome profile is never reused automatically;
- encryption key stored outside Git with file permissions limited to the user;
- saved state and cookies never written to a repository;
- different agents/tasks use distinct session names;
- authenticated state uses encryption;
- content-boundary output protection enabled;
- high-risk actions are gated by the Agent Browser action policy;
- interactive login/2FA is performed in headed mode when human action is required.

Hermes does not need a fork or custom core tool for this integration.

## Memory versus knowledge

- **Hermes memory** stores small durable user/project facts and preferences.
- **Hermes skills** store reusable procedures and routing rules.
- **Qdrant knowledge** stores large retrievable technical corpora.
- **Git repositories** store the canonical definitions for both procedures and knowledge.

Do not copy large technical documentation into basic memory.
