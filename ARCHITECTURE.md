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

The physical Qdrant collection is versioned, for example:

```text
knowledge_v1_4f39c21a
```

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

1. Acquire a VPS-side publish lock.
2. Fetch the exact knowledge Git commit.
3. Validate repository schema and provenance.
4. Normalize/chunk using the pinned schema.
5. Reuse cached embeddings by content hash where safe.
6. Create a new versioned Qdrant collection.
7. Create payload indexes before bulk upload.
8. Upload all points.
9. Run count, metadata, deterministic retrieval, and provenance tests.
10. Atomically switch `knowledge_current` from the previous collection to the new collection.
11. Create a snapshot of the newly active collection.
12. Retain the previous two healthy collections plus the current collection.
13. Record the active Git commit and collection in an immutable publish report.
14. Release the lock.

If any step before the alias switch fails, delete the failed staging collection and leave production untouched.

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
  "query": "string, 1..4000 characters",
  "domains": ["optional-domain"],
  "source_types": ["official_doc"],
  "top_k": 8,
  "include_content": true
}
```

Rules:

- `top_k` defaults to 8 and is clamped to 1..12.
- `domains` and `source_types` are exact allowlisted filters.
- Search uses dense + BM25 retrieval and RRF.
- Returned vectors are never exposed.
- Returned text is wrapped/marked as untrusted retrieved content for the agent.
- Results include provenance.

Output result item:

```json
{
  "chunk_id": "sha256 hex",
  "title": "string",
  "content": "markdown",
  "domain": "spline",
  "source_type": "official_doc",
  "source_url": "https URL or null",
  "source_path": "normalized/spline/...",
  "section_path": ["Animation", "States"],
  "repo_commit": "40-char git SHA",
  "score": 0.0
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
