# Prompt 03 — Qdrant Knowledge Platform, MCP Gateway, Atomic Publishing, and GitHub Sync

You are a senior retrieval engineer, Python backend engineer, security engineer, Linux/SRE engineer, and GitHub CI architect. Execute this prompt on the VPS that will host the knowledge system, with access to the canonical repositories created in Phase 01. Work autonomously, do not ask questions, and do not expose Qdrant merely to make connectivity easier.


## Fixed project context

You are working on a reusable personal AI infrastructure platform with two canonical Git repositories:

1. `hermes-platform` — infrastructure, services, agent integrations, CI, operations, and recovery.
2. `hermes-knowledge` — raw permitted text, normalized retrieval documents, source manifests, retrieval regressions, and knowledge-governance documents.

**System invariants**

- Git is the source of truth. Qdrant is derived and must be rebuildable.
- Qdrant must never be exposed directly to general-purpose agents or the public internet.
- Agents retrieve through an authenticated MCP knowledge gateway.
- Agent Browser is exposed to agents through its official MCP stdio server; do not fork or patch Hermes core to integrate it.
- Browser cookies/state/tokens, Qdrant keys, MCP tokens, SSH keys, and populated local configs are secrets and must never be committed.
- All source-derived knowledge must retain provenance and a rights classification.
- A production knowledge publish builds a new versioned Qdrant collection, verifies it, then atomically switches the `knowledge_current` alias.
- The supported knowledge schema is v1 until an explicit migration creates a new schema version.
- Do not invent URLs, credentials, version numbers, UI labels, or successful tool results.
- Prefer existing host/package-manager conventions when safe, but preserve these architecture contracts.

**Version policy**

For software whose stable release can change, query the project's official release/package source at execution time, select the current stable non-prerelease release compatible with the host, install it, then pin the exact resolved version in lockfiles/config/manifests. For container images, record and use the immutable digest. Never deploy floating `latest` tags. If official version resolution is unavailable, preserve an already-installed compatible pinned version and record the inability to verify currency rather than guessing.

**Implementation quality**

- Complete implementations only: no `TODO`, `TBD`, `FIXME`, pseudocode, commented-out fake implementations, or placeholder secrets.
- Preserve unrelated existing behavior and conventions.
- Any generated secret must be cryptographically random and written only to the documented host-local secret path with restrictive permissions.
- Shell scripts: `set -Eeuo pipefail`, quote expansions, use `mktemp`, trap cleanup, return non-zero on verification failure.
- Python: Python 3.12 where available; type annotations; Pydantic v2 for boundary models; pytest; Ruff; mypy strict for service code. Use `uv` with a committed lockfile when introducing a new Python service unless the repo already has an equivalent locked Python toolchain.
- Containers: Docker Engine + Compose v2 unless the real repository already standardizes on a compatible alternative. Health checks are mandatory.
- YAML/JSON must be machine-validated.
- Logs must not print secrets or browser storage.
- Network calls need explicit connect/read timeouts; retry only transient/idempotent operations with capped exponential backoff and jitter.
- Every long or unbounded input has a hard size/count limit.
- Custom human-facing UI is out of scope for v1. If you create any UI despite an existing repository requirement, it must be keyboard-operable, semantically labeled, focus-safe, and honor reduced motion.

**Required knowledge schema v1**

Every indexed chunk must expose this payload contract:

```text
schema_version: integer, exactly 1
chunk_id: lowercase 64-character SHA-256 hex
content_hash: lowercase 64-character SHA-256 hex
domain: lowercase slug
source_id: stable non-empty string
source_type: one of official_doc | official_tutorial | community_pattern | internal
title: non-empty string
section_path: array of strings
content: normalized Markdown string
source_path: repository-relative POSIX path
source_url: HTTPS URL or null
language: exactly `en` for Knowledge Schema v1
tags: deduplicated array of lowercase slugs
rights: one of owned | permitted | public_reference | restricted_summary_only
repo_commit: lowercase 40- or 64-character hexadecimal Git object ID
published_at: RFC3339 UTC timestamp
```

**Retrieval contract**

- Dense vector: `BAAI/bge-small-en-v1.5`, 384 dimensions, cosine distance.
- Sparse vector: `Qdrant/bm25` with IDF enabled as required by Qdrant.
- Fusion: reciprocal-rank fusion.
- `top_k`: default 8, minimum 1, hard maximum 12.
- Supported filters: `domain`, `source_type`, `rights`, `language`, `schema_version`.
- Every returned hit includes `score`, `content`, `title`, `source_id`, `source_path`, `source_url`, `domain`, `section_path`, `rights`, `repo_commit`.


## Objective

Deploy a production-hardened single-node Qdrant knowledge backend on the VPS, implement a deterministic hybrid indexer, expose only bounded retrieval operations through an authenticated MCP Streamable HTTP gateway, implement atomic blue/green knowledge publication, and synchronize `hermes-knowledge/main` to the VPS through a least-privilege GitHub trigger plus periodic reconciliation.

This is a **single-node recoverable v1**, not a high-availability cluster. Host failure may interrupt retrieval, but Git plus documented secrets/backups must be sufficient to rebuild.

## Prerequisite state

Locate and read:

```text
hermes-platform/SYSTEM_MANIFEST.yaml
hermes-platform/SECURITY.md
hermes-platform/AGENTS.md
hermes-platform/docs/handoffs/01-foundation.md
hermes-knowledge/KNOWLEDGE_MANIFEST.yaml
hermes-knowledge/KNOWLEDGE_STANDARDS.md
```

Verify both repositories are clean before source changes. Inspect existing Docker/systemd/firewall/reverse-proxy conventions and preserve compatible ones.

Capture in `hermes-platform/docs/handoffs/03-qdrant-knowledge-platform.md`:

```bash
uname -a
id
df -h
free -h || true
docker --version || true
docker compose version || true
systemctl --version || true
git --version
python3 --version || true
ss -lntp || true
```

Record VPS memory, free disk, filesystem used for persistent data, existing firewall, and whether the host already has Tailscale/private networking/reverse proxy. Do not alter remote-access architecture in this phase; Phase 04 chooses the client path.

## Scope boundary

**Build**

- private Qdrant container and persistent volumes;
- API authentication even though host binding is local/private;
- Python `knowledge-indexer`;
- Python MCP `knowledge-gateway`;
- exact v1 data models and tool contracts;
- hybrid dense+sparse indexing and retrieval;
- atomic versioned publish/alias rollback;
- snapshots and clean rebuild tooling;
- health checks/structured logs;
- GitHub push trigger with restricted SSH command;
- VPS reconciliation service/timer;
- verification fixture and e2e tests.

**Do not build**

- do not configure Hermes;
- do not expose Qdrant on `0.0.0.0`;
- do not put a Qdrant admin key in GitHub Actions;
- do not use Qdrant dashboard as the ingestion interface;
- do not ingest the full real corpus in this phase; use a deterministic fixture corpus;
- do not create a public HTTPS hostname unless one already exists as host infrastructure;
- do not make Qdrant snapshots the canonical source of knowledge.

## Capacity gate

Before installation, require:

- at least 2 GiB total RAM for a small personal corpus, with sufficient currently available memory to run Qdrant plus Python services;
- at least 10 GiB free persistent disk **and** free space >= 2.5x the expected current corpus/index footprint for blue/green build plus snapshots;
- a filesystem suitable for persistent container volumes.

If the host cannot meet these minimums, do not install a fragile deployment. Finish source code/config/tests that can be validated locally, record `ENVIRONMENT_BLOCKER_INSUFFICIENT_CAPACITY`, and do not claim runtime PASS.

## Version resolution and pinning

From official sources at execution time resolve and record exact stable versions for:

- Qdrant server;
- Qdrant Python client;
- FastEmbed;
- official Python MCP SDK;
- Pydantic;
- FastAPI/ASGI stack only if required by the current MCP SDK deployment pattern;
- Python base image if containers are used.

Pin exact Python dependencies in `uv.lock`. Pin Qdrant and service container images by immutable digest in production Compose. Update `SYSTEM_MANIFEST.yaml` only after successfully running the resolved versions.

## Host filesystem and secrets

Use:

```text
/opt/hermes-platform/                    platform deployment checkout
/var/lib/hermes-kb/
├── qdrant/
├── snapshots/
├── embedding-cache/
├── builds/
└── work/
/etc/hermes-kb/
├── qdrant.env                           0600 root/service-readable
├── gateway.env                          0600 root/service-readable
└── sync.env                             0600 root/service-readable
/var/log/hermes-kb/                      service-managed logs if journald is not used
```

Prefer system users without interactive shells:

- `hermes-kb` owns service data;
- `knowledge-sync` owns the read-only knowledge checkout and may execute only the restricted sync workflow.

Generate independent random credentials with `umask 077` and shell tracing disabled:

- Qdrant admin/API key;
- knowledge gateway bearer token: exactly 32 random bytes encoded as 64 lowercase hexadecimal characters, stored only as `KNOWLEDGE_MCP_BEARER_TOKEN=<value>` in `/etc/hermes-kb/gateway.env`;
- any restricted SSH trigger key pair.

Use a command such as `openssl rand -hex 32` only with stdout redirected directly into a permission-restricted construction step/file; do not let the secret appear in terminal/tool output or logs. Validate the gateway token format without printing it. Never print secret values. Never reuse one credential for two trust boundaries.

## Source-controlled ownership

This prompt owns these paths:

```text
hermes-platform/
├── infra/qdrant/
│   ├── README.md
│   ├── compose.yaml
│   ├── qdrant-config.yaml
│   ├── deploy.sh
│   ├── backup.sh
│   ├── restore-test.sh
│   ├── publish-knowledge.sh
│   ├── rollback.sh
│   ├── reconcile.sh
│   ├── forced-command.sh
│   ├── systemd/
│   │   ├── hermes-knowledge-reconcile.service
│   │   └── hermes-knowledge-reconcile.timer
│   └── env.example
├── services/knowledge-indexer/
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── README.md
│   ├── src/hermes_kb_indexer/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── loaders.py
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   ├── qdrant_store.py
│   │   ├── publish.py
│   │   └── cli.py
│   └── tests/
├── services/knowledge-gateway/
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── README.md
│   ├── src/hermes_kb_gateway/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── auth.py
│   │   ├── retrieval.py
│   │   └── server.py
│   └── tests/
└── tests/
    ├── fixtures/knowledge/
    └── e2e/
        ├── test_publish_rollback.py
        └── test_gateway_mcp.py

hermes-knowledge/
└── .github/workflows/
    └── publish-knowledge.yml
```

Phase 05 owns `tools/knowledge-ingestion/` and the real corpus normalization workflow. Do not implement that directory here.

## Qdrant deployment contract

`compose.yaml` must:

- use an immutable Qdrant image digest;
- restart unless stopped;
- persist `/qdrant/storage`;
- mount explicit config read-only;
- expose port 6333 on **host loopback only**, e.g. `127.0.0.1:6333:6333`, so the dashboard/API can be accessed locally or through an SSH tunnel;
- never publish Qdrant on `0.0.0.0`;
- put Qdrant and the gateway on a private Compose network;
- define health checks;
- apply sensible log rotation;
- run services with least privilege supported by their images;
- not embed secrets in YAML.

The gateway may be host-loopback bound at `127.0.0.1:8790` in v1. Phase 04 may reach it through an existing private mesh, an existing TLS reverse proxy, or an SSH tunnel. If an existing private mesh is already configured and binding there is demonstrably safer, document the deviation.

Qdrant must require its API key even on loopback/private networking.

## Qdrant collection contract

Each publish creates:

Use the collection-name grammar `knowledge_v1_YYYYMMDDTHHMMSSZ_GIT12`, where the timestamp is UTC and `GIT12` is the first 12 lowercase characters of the source Git commit SHA. For example, the implementation must construct this from real runtime values rather than a hard-coded sample.

Allowed characters must satisfy Qdrant naming rules. The stable alias is:

```text
knowledge_current
```

The collection must contain named vectors:

- dense named vector: size 384, cosine distance;
- sparse named vector: configured for `Qdrant/bm25` and IDF behavior required by the resolved Qdrant/FastEmbed versions.

Create payload indexes before bulk load for fields used in filters:

```text
schema_version
domain
source_id
source_type
language
rights
repo_commit
```

Store all Knowledge Schema v1 payload fields.

## Indexer boundary models

Implement Pydantic v2 models equivalent to these contracts; field names/types/enums are fixed.

```python
from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator

Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
GitOid = Annotated[str, Field(pattern=r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")]
Slug = Annotated[str, Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")]

class SourceType(StrEnum):
    OFFICIAL_DOC = "official_doc"
    OFFICIAL_TUTORIAL = "official_tutorial"
    COMMUNITY_PATTERN = "community_pattern"
    INTERNAL = "internal"

class Rights(StrEnum):
    OWNED = "owned"
    PERMITTED = "permitted"
    PUBLIC_REFERENCE = "public_reference"
    RESTRICTED_SUMMARY_ONLY = "restricted_summary_only"

class KnowledgeChunk(BaseModel):
    schema_version: Literal[1]
    chunk_id: Sha256
    content_hash: Sha256
    domain: Slug
    source_id: str = Field(min_length=1, max_length=240)
    source_type: SourceType
    title: str = Field(min_length=1, max_length=500)
    section_path: list[str] = Field(max_length=32)
    content: str = Field(min_length=1, max_length=200_000)
    source_path: str = Field(min_length=1, max_length=1200)
    source_url: HttpUrl | None
    language: Literal["en"] = "en"
    tags: list[Slug] = Field(default_factory=list, max_length=64)
    rights: Rights
    repo_commit: GitOid
    published_at: datetime

    @field_validator("section_path")
    @classmethod
    def nonempty_section_items(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            raise ValueError("section_path entries must be non-empty")
        return value
```

You may strengthen validation without changing field semantics.

## Canonical chunk construction and deterministic point identity

`hermes-kb-index` is the **single executable owner of chunk planning**. Normalized Markdown does not contain `chunk_id`; the indexer derives chunks deterministically from the normalized files at the requested Git object ID. Phase 05's ingestion tooling must call/delegate to this planner rather than maintaining a second chunking implementation.

Implement `src/hermes_kb_indexer/chunking.py` with pure deterministic functions and tests. The planner must:

1. parse validated normalized Markdown frontmatter/body;
2. split on semantic heading/procedure boundaries before token limits;
3. target ~350 normalized-content tokens, soft minimum 80, hard normalized-content ceiling 420;
4. enforce a hard ≤500-token complete document embedding input after adding the exact `passage:`/title/domain/section prefix;
5. allow at most 60 tokens overlap;
6. keep ordered dependent procedures together where possible;
7. split oversized fenced code blocks only at safe blank-line/function/statement boundaries, re-fence fragments, and add deterministic part context; never rely on tokenizer truncation;
8. normalize chunk-content line endings to LF and strip trailing whitespace per line before hashing;
9. compute `content_hash = sha256(normalized_chunk_content_utf8)`;
10. for identical `content_hash` values repeated in the same semantic section, assign `occurrence` as the zero-based count of prior identical chunks in document order;
11. compute `chunk_id` from this exact canonical identity:

```python
canonical_identity = "\n".join(
    [
        "schema=1",
        f"domain={domain}",
        f"source_id={source_id}",
        f"section={' > '.join(section_path)}",
        f"content_hash={content_hash}",
        f"occurrence={occurrence}",
    ]
)
chunk_id = hashlib.sha256(canonical_identity.encode("utf-8")).hexdigest()
```

Do not include source checksum, repository path, publication commit, or global ordinal in `chunk_id`. Those remain provenance. An unchanged chunk under the same stable source ID and semantic section therefore keeps identity across unrelated source edits/path refactors.

Expose these exact CLI operations from `hermes-kb-index`:

```text
hermes-kb-index validate --repo PATH --commit GIT_OID
hermes-kb-index plan --repo PATH --commit GIT_OID --output CHUNKS_JSONL
hermes-kb-index publish --repo PATH --commit GIT_OID
hermes-kb-index rollback --to COLLECTION_NAME
```

`plan` is read-only: it emits one fully validated `KnowledgeChunk` JSON object per line in deterministic source/section/chunk order and performs no Qdrant writes. Running it twice at the same commit must produce byte-identical output.

Qdrant point IDs must be deterministic UUIDs derived from `chunk_id`, using UUIDv5 under one fixed namespace constant committed in the indexer. Never use random UUIDs for corpus points.

## Embedding pipeline

Use FastEmbed locally:

- dense model exactly `BAAI/bge-small-en-v1.5`;
- sparse model exactly `Qdrant/bm25`;
- cache embeddings by `(embedding_schema_version, content_hash)` under `/var/lib/hermes-kb/embedding-cache`;
- validate the complete prefixed embedding text is ≤500 tokens with the locked model tokenizer before embedding;
- validate generated dense vector length equals 384;
- reject NaN/inf vectors;
- reject any publishable schema-v1 chunk whose `language` is not exactly `en`; the locked v1 dense/sparse models are English-only in this architecture, so multilingual support requires a schema/model migration rather than silent degraded indexing;
- batch embeddings/upserts with bounded batch sizes determined by a tested configuration default, starting at 64;
- do not log raw document bodies at info level.

Construct embedding input exactly with:

```python
embedding_text = (
    f"passage: Title: {chunk.title}\n"
    f"Domain: {chunk.domain}\n"
    f"Section: {' > '.join(chunk.section_path)}\n\n"
    f"{chunk.content}"
)
```

The string must literally begin with `passage: `. Only this embedding input includes the retrieval prefix/context. The canonical payload `content` remains unchanged.

## Publication algorithm

Implement `hermes-kb-index publish --repo PATH --commit GIT_OID`.

Required sequence:

1. obtain an exclusive `flock`/process lock;
2. verify the knowledge checkout is clean and exactly at the requested commit;
3. validate `KNOWLEDGE_MANIFEST.yaml`;
4. call the same pure planner used by `hermes-kb-index plan` to load normalized docs and construct chunks;
5. fail before Qdrant mutation if any schema/provenance/rights/duplicate validation fails;
6. calculate capacity estimate and ensure the blue/green build has sufficient disk headroom;
7. create a new versioned staging collection with vector/payload indexes;
8. embed/cache and upsert all chunks;
9. assert point count equals the planned chunk count;
10. execute fixture + repository retrieval regression cases;
11. atomically write `/var/lib/hermes-kb/builds/<collection>.json` with `collection`, full `repo_commit`, `knowledge_schema_version`, dense/sparse model identifiers, created time, chunk/source counts, and state `verified_staging`; do **not** insert a synthetic metadata point into the knowledge collection;
12. perform a single atomic alias change that points `knowledge_current` at staging;
13. verify the alias resolves to the new collection and health loads the matching sidecar record and reports the intended full commit; then atomically update that sidecar state to `active`;
14. create a Qdrant snapshot of the now-active collection;
15. retain the active build plus the two immediately previous healthy builds and their sidecars; delete older versioned builds/sidecars only after snapshot success and never delete a collection targeted by an alias;
16. emit a machine-readable publish report.

If anything fails before step 12, production stays unchanged, the staging collection is deleted after diagnostics are captured, and its sidecar is marked `failed_pre_switch` or removed after the report captures it. If a failure occurs after alias switch but before final postchecks/snapshot, automatically switch the alias back to the previously active healthy collection, verify rollback, restore that prior sidecar to `active`, mark the failed sidecar `failed_post_switch`, and mark the publish failed. Sidecar writes must use temp-file + `fsync` + atomic rename semantics on the same filesystem.

Never partially update `knowledge_current`.

## Rollback contract

Implement:

```text
hermes-kb-index rollback --to COLLECTION_NAME
```

It may target only a known healthy collection with matching schema version 1. It performs an atomic alias switch and verifies the active commit. It never deletes the failed collection automatically; cleanup is a separate operation after diagnosis.

## MCP knowledge gateway

Use the official Python MCP SDK with Streamable HTTP transport in the currently recommended production configuration. The gateway is stateless regarding user sessions and reads only from the `knowledge_current` alias using a **read/search-capable Qdrant credential**, never the administrative deployment credential when the resolved Qdrant authorization model permits separation.

Require bearer authentication at the gateway boundary. Use constant-time token comparison or standards-compliant middleware. Reject missing/invalid tokens with no information leak.

### Tool 1 — `knowledge_search`

Input:

```python
class KnowledgeSearchInput(BaseModel):
    query: str = Field(min_length=2, max_length=4000)
    top_k: int = Field(default=8, ge=1, le=12)
    domains: list[Slug] = Field(default_factory=list, max_length=16)
    source_types: list[SourceType] = Field(default_factory=list, max_length=8)
    rights: list[Rights] = Field(default_factory=list, max_length=8)
    language: Literal["en"] | None = None
    schema_version: Literal[1] = 1
```

Output:

```python
class SearchHit(BaseModel):
    score: float
    content: str
    title: str
    source_id: str
    source_path: str
    source_url: HttpUrl | None
    domain: Slug
    section_path: list[str]
    rights: Rights
    repo_commit: GitOid

class KnowledgeSearchOutput(BaseModel):
    query: str
    active_collection: str
    active_repo_commit: GitOid
    hits: list[SearchHit]
```

Behavior:

- construct the dense query embedding input as `query: ` followed by the user's query, and reject it if the locked tokenizer exceeds the model budget;
- embed the query dense+sparse;
- query only `knowledge_current`;
- apply supplied payload filters;
- fuse dense+sparse via RRF;
- return maximum 12 hits;
- enforce a total response content budget of 60,000 characters; truncate individual content at semantic boundaries if needed and expose an explicit `content_truncated: bool` field if you implement truncation;
- 10-second end-to-end retrieval deadline by default;
- retry one time only for a clearly transient Qdrant connection failure.

### Tool 2 — `knowledge_get`

Input:

```python
class KnowledgeGetInput(BaseModel):
    chunk_id: Sha256
```

Output is one full `KnowledgeChunk` plus active build metadata loaded from the active collection's validated sidecar, or a structured not-found result. Do not expose arbitrary Qdrant query syntax.

### Tool 3 — `knowledge_domains`

No input beyond the MCP call. Return distinct indexed domain slugs and per-domain point/source counts for the active build. Bound response size.

### Tool 4 — `knowledge_health`

Return:

```python
class KnowledgeHealthOutput(BaseModel):
    status: Literal["ok", "degraded"]
    active_collection: str | None
    active_repo_commit: GitOid | None
    knowledge_schema_version: int | None
    dense_model: str | None
    sparse_model: str | None
    point_count: int | None
    checked_at: datetime
```

Never return keys, credentials, filesystem paths, or raw Qdrant configuration.

Do not expose generic “execute Qdrant query”, collection creation, delete, snapshot, or admin tools through MCP.

## Gateway failure behavior

- no active alias → health degraded; search/get return structured service-unavailable error;
- Qdrant timeout → bounded service-unavailable response, no fabricated hits;
- invalid request → validation error without stack trace;
- auth failure → generic unauthorized;
- one corrupt payload → log chunk id/source id, omit only if safe, and mark health degraded; never crash-loop silently.

## GitHub synchronization

### Read path

The VPS should pull `hermes-knowledge` using a repository-scoped **read-only deploy key** owned by `knowledge-sync`. The private key remains on the VPS.

If authenticated GitHub access is available, create/register the deploy key automatically. If not, generate the key, print only the public key, write the exact GitHub CLI registration command to the handoff, and continue with local verification. Do not ask the operator for the private key.

### Push trigger

Create a separate SSH key pair for the GitHub Actions trigger. The GitHub secret contains only the trigger private key. On the VPS, the corresponding public key in `knowledge-sync`'s `authorized_keys` must be restricted with a forced command and no port/agent/X11 forwarding.

The forced command must ignore any client-supplied command and execute exactly the source-controlled sync trigger.

The trigger must:

1. acquire the same publication lock;
2. fetch `origin main`;
3. fast-forward the local deployment checkout to the target remote commit;
4. run repository validation;
5. invoke the indexer publish for that exact commit;
6. exit non-zero on failure;
7. log commit and publish report but no secret.

### Workflow

`hermes-knowledge/.github/workflows/publish-knowledge.yml`:

- triggers on push to `main`;
- has minimum repository permissions (`contents: read`);
- uses no Qdrant credentials;
- verifies the VPS SSH host key from a secret/variable;
- invokes only the restricted SSH trigger;
- pins every third-party Action to a full commit SHA.

If GitHub secrets cannot be written by the current authenticated account, document the exact secret names and generated public/host values required. Never paste a generated private key into the handoff.

### Reconciliation timer

Install:

- `hermes-knowledge-reconcile.service`
- `hermes-knowledge-reconcile.timer`

Run every 15 minutes with randomized delay up to 2 minutes. The service:

1. fetches `origin/main`;
2. asks gateway/index metadata for the active repo commit;
3. does nothing if equal;
4. if remote is newer and local checkout can fast-forward, runs the same serialized publish path;
5. if history diverges/rewinds, does **not** publish automatically; logs a high-severity event and exits non-zero so an operator can review intentional history rewrite.

Enable at boot.

## Backup/recovery

`backup.sh` must create a Qdrant snapshot for the active collection and copy the matching `/var/lib/hermes-kb/builds/<collection>.json` sidecar plus manifests. Snapshots are supplementary; Git remains canonical.

`restore-test.sh` must use an isolated temporary Docker Compose project/ports/volumes to prove one of:

1. a selected snapshot restores and health checks pass; and
2. a completely empty Qdrant can be rebuilt from the pinned fixture/knowledge Git commit.

Never perform a destructive restore test against the live volume.

## Observability

Use journald or structured JSON logs. Every publish/search log entry may include:

- timestamp;
- operation;
- request id;
- active collection;
- repo commit;
- duration;
- counts;
- success/error code.

Never log query document bodies by default, tokens, keys, browser data, or SSH private material.

Expose service health to Docker/systemd. Document disk-space checks and snapshot cleanup.

## Security tests

Prove:

1. `ss -lntp` shows Qdrant only on loopback/private interface, never `0.0.0.0:6333`;
2. Qdrant API without key is denied;
3. Qdrant with the service credential succeeds only for its intended operations;
4. gateway without/with bad bearer token is denied;
5. gateway with correct local token can call the four tools;
6. no Git tracked file contains populated secret values;
7. the GitHub trigger key is forced-command/restricted;
8. the GitHub workflow contains no database secret;
9. all third-party GitHub Actions are SHA-pinned.

## Performance tests

Using a fixture large enough to exercise batching (at least 500 synthetic/non-copyright fixture chunks):

- cold gateway health response < 2 seconds after service is healthy;
- warmed fixture `knowledge_search` p95 < 2 seconds over 30 sequential queries on the actual VPS, unless hardware makes that impossible; if impossible, record measured p95 and capacity bottleneck rather than falsifying PASS;
- search output never exceeds 60,000 content characters;
- top_k > 12 is rejected;
- indexer memory stays bounded by batching rather than loading vectors for the entire corpus at once.

Performance targets are v1 service objectives, not excuses to skip correctness.

## Verification sequence

Run all relevant unit/static checks:

```bash
cd "$PLATFORM_REPO/services/knowledge-indexer"
uv sync --frozen
uv run ruff check .
uv run mypy src
uv run pytest -q

cd "$PLATFORM_REPO/services/knowledge-gateway"
uv sync --frozen
uv run ruff check .
uv run mypy src
uv run pytest -q
```

Then deployment/e2e:

```bash
cd "$PLATFORM_REPO/infra/qdrant"
docker compose config --quiet
bash deploy.sh
docker compose ps
bash publish-knowledge.sh --fixture
uv run pytest "$PLATFORM_REPO/tests/e2e/test_publish_rollback.py" -q
uv run pytest "$PLATFORM_REPO/tests/e2e/test_gateway_mcp.py" -q
bash restore-test.sh
systemctl status hermes-knowledge-reconcile.timer --no-pager
ss -lntp
```

Also simulate a failed publish before alias switch and assert `knowledge_current` remains unchanged. Simulate a post-switch validation failure in the isolated fixture environment and assert automatic alias rollback.

Fix failures and re-run. Never report PASS when any blocker/major acceptance test remains unexecuted on a host that should support it.

## Acceptance criteria

- [ ] Qdrant version and immutable image digest are recorded.
- [ ] Qdrant persists data and is reachable only on loopback/private networking.
- [ ] Qdrant rejects unauthenticated API calls.
- [ ] `hermes-kb-index plan` produces byte-identical JSONL across two runs at the same commit, enforces the shared chunk identity/budgets, and source checksum/path-only changes do not churn unaffected chunk IDs.
- [ ] Dense+sparse fixture indexing produces valid 384-dim dense vectors and sparse vectors.
- [ ] `knowledge_current` points to a verified versioned collection and its active build sidecar matches the alias target and full source Git object ID.
- [ ] The Qdrant collection contains only Knowledge Schema v1 chunks; build metadata is not stored as a synthetic knowledge point.
- [ ] A failed pre-switch publish leaves the current alias untouched.
- [ ] A failed post-switch verification automatically rolls back.
- [ ] Current + two previous healthy builds are retained without deleting active alias targets.
- [ ] Snapshot and isolated restore/rebuild test passes.
- [ ] MCP gateway exposes only the four approved knowledge tools.
- [ ] Gateway auth, limits, timeouts, filters, and provenance behavior pass tests; the bearer token exists only in the permission-restricted gateway secret file and never appears in reports/logs/Git.
- [ ] GitHub trigger has no Qdrant admin secret and uses a restricted forced SSH command.
- [ ] Reconciliation timer is enabled and repairs a deliberately simulated missed trigger.
- [ ] Active knowledge Git commit is observable in gateway health.
- [ ] GitHub Action third-party dependencies are full-SHA pinned.
- [ ] `docs/handoffs/03-qdrant-knowledge-platform.md` records versions, image digests, service URLs without credentials, collection/alias state, commit SHAs, tests/results, and any environment blocker.

## Handoff

End with real observed values, never secrets:

```text
PHASE_03_STATUS=PASS
QDRANT_VERSION=exact observed version
QDRANT_IMAGE_DIGEST=exact observed sha256 digest
QDRANT_BIND=observed loopback/private bind
KNOWLEDGE_ALIAS=knowledge_current
ACTIVE_COLLECTION=observed collection name
ACTIVE_REPO_COMMIT=observed full 40- or 64-character Git object ID
GATEWAY_MCP_URL=observed local/private URL
GATEWAY_TOKEN_FILE=/etc/hermes-kb/gateway.env
RECONCILIATION_TIMER=ENABLED
RESTORE_TEST=PASS
```
