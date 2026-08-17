# Prompt 01 — Foundation and Repository Governance

You are a senior platform engineer, security engineer, and repository architect. Execute this prompt autonomously to establish the canonical foundation for the Hermes platform and knowledge repositories. Do not ask the operator questions. Inspect first, preserve legitimate existing work, choose the safest defensible option where the environment differs, and record every non-obvious choice.


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

Create or normalize the two source-of-truth repositories, define their contracts before any service is installed, add validation and security baselines, and make a clean-clone recovery path possible.

## Scope boundary

**Build in this prompt**

- repository discovery/creation;
- canonical directory trees;
- root governance documents;
- manifests and schemas;
- ignore rules and secret policy;
- repository validators;
- CI validation baseline;
- operations/recovery documentation stubs that contain complete v1 operational contracts, not placeholders;
- initial commits and, if authenticated GitHub access exists, private GitHub remotes.

**Do not build in this prompt**

- do not install Agent Browser;
- do not install/run Qdrant;
- do not create the knowledge gateway/indexer implementation;
- do not edit Hermes local configuration;
- do not ingest a real corpus;
- do not generate or store production credentials.

## Prerequisite state

No prior project repository is required. The only prerequisites are an authorized development machine with Git and permission to create local files. GitHub CLI/authentication is optional for local completion and required only for creating/pushing private remotes.

The first duty is to discover whether either canonical repository already exists and preserve it.

## Start with evidence


Run and save the meaningful output in `docs/handoffs/01-foundation.md`:

```bash
set -Eeuo pipefail
pwd
uname -a || true
git --version
python3 --version || true
docker --version || true
docker compose version || true
gh --version || true
gh auth status || true
find "$HOME" -maxdepth 3 -type d \( -name hermes-platform -o -name hermes-knowledge \) -print 2>/dev/null
```

Search the current working tree and nearby expected project directories before creating anything. If an existing repository is found, inspect:

```bash
git -C "$REPO" status --short --branch
git -C "$REPO" remote -v
git -C "$REPO" log -5 --oneline
find "$REPO" -maxdepth 3 -type f | sort | sed -n '1,240p'
```

Never overwrite uncommitted work. If incompatible existing conventions exist, preserve them and document a migration that reaches the contracts below without destructive rewriting.

Use these canonical local paths only when no existing project path is discoverable:

```bash
PLATFORM_REPO="$HOME/src/hermes-platform"
KNOWLEDGE_REPO="$HOME/src/hermes-knowledge"
```

Create parent directories as needed.

## Required `hermes-platform` tree

Ensure these paths exist and are owned by the platform repository:

```text
hermes-platform/
├── README.md
├── AGENTS.md
├── DECISIONS.md
├── CHANGELOG.md
├── SECURITY.md
├── SYSTEM_MANIFEST.yaml
├── pyproject.toml
├── uv.lock
├── .editorconfig
├── .gitignore
├── docs/
│   ├── architecture.md
│   ├── operations.md
│   ├── recovery.md
│   ├── handoffs/
│   └── runbooks/
├── infra/
│   ├── agent-browser/
│   └── qdrant/
├── services/
│   ├── knowledge-gateway/
│   └── knowledge-indexer/
├── tools/
│   └── knowledge-ingestion/
├── integrations/
│   └── hermes/
├── scripts/
│   └── validate_repository.py
├── tests/
│   ├── e2e/
│   └── fixtures/
└── .github/
    └── workflows/
        └── platform-ci.yml
```

Empty owned directories may contain `.gitkeep` in Phase 1. Later prompts replace them with real files. `SYSTEM_MANIFEST.yaml` is a shared sequential manifest: later component prompts may update only their explicitly assigned component fields, never unrelated keys.

## Required `hermes-knowledge` tree

```text
hermes-knowledge/
├── README.md
├── AGENTS.md
├── KNOWLEDGE_STANDARDS.md
├── CONTRIBUTING.md
├── INGESTION_PLAYBOOK.md
├── KNOWLEDGE_MANIFEST.yaml
├── .editorconfig
├── .gitignore
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
└── .github/
    └── workflows/
        └── validate-knowledge.yml
```

`manifests/sources.jsonl` may be a valid empty file. `tests/retrieval_cases.yaml` must start with `version: 1` and `cases: []`. Phase 05 is explicitly authorized to refine the bootstrapped knowledge standards/contributing/playbook/source-manifest/retrieval-cases/validation-workflow files while preserving the schema and publication contracts established here and in Phase 03.

## Required manifests

Create `hermes-platform/SYSTEM_MANIFEST.yaml` with this exact top-level contract:

```yaml
schema_version: 1
project: hermes-platform
runtime:
  python: ">=3.12,<3.14"
components:
  agent_browser:
    version: null
    package_source: null
    installed_on: []
  qdrant:
    version: null
    image_digest: null
  knowledge_gateway:
    version: "0.1.0"
  knowledge_indexer:
    version: "0.1.0"
  hermes:
    observed_version: null
knowledge:
  repository: hermes-knowledge
  schema_version: 1
  active_alias: knowledge_current
  dense_model: BAAI/bge-small-en-v1.5
  dense_dimensions: 384
  sparse_model: Qdrant/bm25
security:
  qdrant_publicly_exposed: false
  secrets_in_git: false
```

Null version fields in this bootstrap manifest are intentional state, not placeholders: the component-owning prompts must replace them only after they have hard evidence of the resolved installed versions.

Create `hermes-knowledge/KNOWLEDGE_MANIFEST.yaml`:

```yaml
schema_version: 1
project: hermes-knowledge
knowledge_schema_version: 1
default_language: en
domains:
  - spline
  - gsap
  - react
  - webgl
retrieval:
  dense_model: BAAI/bge-small-en-v1.5
  dense_dimensions: 384
  dense_distance: cosine
  sparse_model: Qdrant/bm25
  fusion: rrf
chunking:
  target_content_tokens: 350
  minimum_content_tokens: 80
  maximum_content_tokens: 420
  maximum_embedding_tokens: 500
  maximum_overlap_tokens: 60
rights:
  allowed:
    - owned
    - permitted
    - public_reference
    - restricted_summary_only
```

## Governance documents

Write complete, concise versions of these documents:

### `AGENTS.md`

Require every agent to:

- read `SYSTEM_MANIFEST.yaml` or `KNOWLEDGE_MANIFEST.yaml` before work;
- inspect existing files/conventions before modifying;
- keep secrets out of Git;
- avoid inventing facts or source URLs;
- use deterministic validators before commit;
- write a handoff under `docs/handoffs/` in the platform repo for infrastructure work;
- never call Qdrant the source of truth;
- never mutate the live Qdrant alias without successful staging verification.

### `SECURITY.md`

Define:

- secret classes: browser auth state, browser encryption key, Qdrant API/admin keys, MCP bearer token, SSH private keys, GitHub Actions private trigger key;
- host-local storage only;
- file mode `0600` for secret files and `0700` for secret directories on Unix;
- no secrets in logs, command-line arguments when avoidable, screenshots, Git history, test fixtures, or Markdown;
- credential rotation after suspected disclosure;
- dependency pinning and immutable container digests;
- least privilege for GitHub keys/actions.

### Knowledge governance

`KNOWLEDGE_STANDARDS.md`, `CONTRIBUTING.md`, and `INGESTION_PLAYBOOK.md` must encode:

- raw source is immutable and separate from normalized output;
- no raw binary video in Git;
- transcript/UI evidence rules;
- provenance/rights metadata;
- deterministic IDs;
- update/delete semantics;
- quarantine on uncertain or invalid items;
- validation before publish;
- retrieval regressions before alias switch.

Do not duplicate large instructions unnecessarily; cross-link within the same repo, but each document must be understandable from a clean clone.

## Repository validator

Create a minimal repository-validation Python environment at the platform repo root. `pyproject.toml` must require Python `>=3.12,<3.14` and declare only the dependencies genuinely required by the validator. Add PyYAML with `uv add PyYAML`, then commit the generated `uv.lock`; the lockfile, not a floating production install, is the exact dependency record. CI and local validation must use `uv sync --frozen` followed by `uv run`. Do not hand-write a partial YAML parser.

Implement `hermes-platform/scripts/validate_repository.py` as a real Python 3.12 script. It may use the Python standard library plus the locked PyYAML dependency and no undeclared packages. It must accept:

```text
uv run uv run python scripts/validate_repository.py --platform PATH --knowledge PATH
```

It must fail non-zero with actionable messages when:

1. required root files/directories are missing;
2. either YAML manifest cannot be parsed by the CI YAML parser;
3. manifest schema versions are not `1`;
4. dense model/dimension or active alias differ from the fixed contracts;
5. tracked filenames match common secret patterns (`*.pem`, `*.key`, `.env`, `cookies*`, `storage-state*`) except `.env.example`;
6. tracked text contains obvious private-key headers or assignment forms for configured secret names;
7. normalized Markdown files lack required frontmatter fields;
8. `sources.jsonl` contains malformed JSON lines;
9. retrieval YAML lacks `version: 1` and a list-valued `cases`.

If PyYAML is unavailable because the environment was not synchronized, fail with an actionable dependency/setup error. Do not silently fall back to a partial YAML parser.

## CI

Create both workflows.

### Platform CI

Runs on pull requests and pushes to `main`. It checks out the platform repo, checks out the knowledge repo read-only only when repository access is configured, then runs:

- Markdown/config placeholder scan;
- secret-pattern scan;
- `uv sync --frozen`;
- repository validator through `uv run`;
- Python syntax checks for scripts through the same locked environment.

If CI cannot read a separate private knowledge repo during bootstrap, split the validator into platform-only mode and document the required GitHub App/deploy credential configuration. Do not grant write permission.

### Knowledge CI

Runs on pull requests and pushes to `main` and performs:

- YAML/JSONL/frontmatter validation;
- secret scan;
- duplicate `source_id`/checksum checks;
- retrieval case schema validation;
- no binary video extensions (`.mp4`, `.mov`, `.mkv`, `.webm`) tracked.

Pin every third-party GitHub Action to a full immutable commit SHA. Record the human-readable release tag in an adjacent comment.

## GitHub behavior

If authenticated `gh` access is available and the repositories do not exist, create them as **private** and push the initial branch:

```bash
gh repo create hermes-platform --private --source "$PLATFORM_REPO" --remote origin --push
gh repo create hermes-knowledge --private --source "$KNOWLEDGE_REPO" --remote origin --push
```

If the repositories already have remotes, do not replace them. If GitHub authentication or permission is unavailable, finish the local repositories, commit them, and record the exact remaining remote command in the handoff. This is an environment blocker, not a reason to ask a question.

## Commit discipline

Use Conventional Commits. At minimum:

```bash
git commit -m "chore: establish platform governance"
git commit -m "chore: establish knowledge governance"
```

Do not commit if validators fail.

## Verification

Run all checks available in the real environment. At minimum:

```bash
python3 "$PLATFORM_REPO/scripts/validate_repository.py" \
  --platform "$PLATFORM_REPO" \
  --knowledge "$KNOWLEDGE_REPO"

git -C "$PLATFORM_REPO" status --short
git -C "$KNOWLEDGE_REPO" status --short
git -C "$PLATFORM_REPO" ls-files | sort
git -C "$KNOWLEDGE_REPO" ls-files | sort
```

Verify there are no unresolved conflict markers or forbidden placeholders:

```bash
for repo in "$PLATFORM_REPO" "$KNOWLEDGE_REPO"; do
  if git -C "$repo" grep -nE '^(<<<<<<<|=======|>>>>>>>)|TODO|TBD|FIXME'; then
    echo "Forbidden marker found" >&2
    exit 1
  fi
done
```

Run the CI-equivalent validator locally with the committed lockfile: `uv sync --frozen`, then `uv run python scripts/validate_repository.py --platform "$PLATFORM_REPO" --knowledge "$KNOWLEDGE_REPO"`. If `uv` itself is unavailable, install it using an authorized host/package-manager method, record the exact observed version, and rerun; if that is impossible, record the validation as not executable and do not label it passed.

## Acceptance criteria

- [ ] Both repositories exist locally or valid existing equivalents were normalized without destructive overwrite.
- [ ] Canonical trees and ownership boundaries are explicit.
- [ ] Both manifests validate and carry schema version 1.
- [ ] No secret or browser-state file is tracked.
- [ ] Repository validator rejects a deliberately-created temporary secret fixture and accepts the clean repositories.
- [ ] CI definitions are syntactically valid and pinned.
- [ ] Recovery documentation states how to recreate derived services from Git.
- [ ] Git histories contain an initial governance commit.
- [ ] If GitHub auth exists, both private remotes are reachable and pushed; otherwise the handoff states exactly what external permission remains.
- [ ] `docs/handoffs/01-foundation.md` contains observed tool versions, repository paths, commit SHAs, verification commands/results, deviations, and unresolved environment blockers.

## Handoff

The next agent must be able to learn everything from the repositories and `docs/handoffs/01-foundation.md`. Finish the handoff with five machine-readable `KEY=value` lines: `PHASE_01_STATUS=PASS`, followed by `PLATFORM_REPO`, `KNOWLEDGE_REPO`, `PLATFORM_COMMIT`, and `KNOWLEDGE_COMMIT`, each populated with the actual observed absolute path or full lowercase Git commit object ID. Do not use sample or fake values.
