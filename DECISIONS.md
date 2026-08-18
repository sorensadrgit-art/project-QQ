# Decisions

This file records assumptions made autonomously because the requested workflow explicitly disallowed clarification questions.

## D-001 — Greenfield package

**Decision:** Treat the work as a greenfield infrastructure specification and prompt library.

**Reason:** No user project repository, attachment, or source tree was mounted in the authoring environment. Only the conversational plan was available.

**If this changes:** Prompt 01 instructs the execution agent to inspect and preserve an existing repository rather than overwrite it.

## D-002 — Two repositories instead of one

**Decision:** Separate `hermes-platform` from `hermes-knowledge`.

**Reason:** Infrastructure code, secrets policy, CI, and runtime integrations have a different lifecycle and permission surface from technical corpus content. A split also makes Qdrant rebuild/recovery clearer.

**If this changes:** A monorepo can preserve the same boundaries under `/platform` and `/knowledge`; the contracts do not otherwise change.

## D-003 — Git is authoritative; Qdrant is derived

**Decision:** Never treat Qdrant as canonical storage.

**Reason:** The user explicitly wants the project recoverable if derived data is lost. A Git-backed corpus plus deterministic index build satisfies that requirement.

**If this changes:** None recommended. Making Qdrant canonical would reduce recoverability.

## D-004 — Qdrant stays private

**Decision:** Qdrant does not listen on a publicly reachable host port.

**Reason:** Self-hosted Qdrant is not secure by default, and general-purpose agents do not need database-admin APIs. An MCP gateway provides a smaller, auditable surface.

**If this changes:** Public Qdrant exposure requires TLS, API-key/JWT RBAC, firewall restrictions, and a documented threat model.

## D-005 — Use an MCP gateway for knowledge retrieval

**Decision:** Expose search through a small Streamable HTTP MCP server.

**Reason:** Hermes supports remote MCP servers, and MCP is reusable by other agents. It decouples agent clients from Qdrant schema and embedding implementation.

**If this changes:** A REST API can be added, but the MCP tools remain the agent-facing contract.

## D-006 — Use Agent Browser MCP rather than patch Hermes

**Decision:** Register `agent-browser mcp` with Hermes.

**Reason:** Agent Browser has an MCP stdio server, and Hermes can consume MCP servers. This is upgrade-safe and reusable by other MCP-capable agents.

**If this changes:** A Hermes plugin is justified only if a capability cannot be represented cleanly through Agent Browser MCP.

## D-007 — Hybrid retrieval

**Decision:** Use dense `BAAI/bge-small-en-v1.5` plus sparse `Qdrant/bm25`, fused with RRF.

**Reason:** Technical corpora need both semantic recall and exact symbol/setting/API-name matching. Both models can run locally without an external embedding API.

**If this changes:** Changing the dense model creates embedding schema v2 and requires a new collection build before alias switch.

## D-008 — One collection schema, domains in payload

**Decision:** Use one physical collection per published knowledge build, with `domain` as indexed payload metadata.

**Reason:** All planned technologies share the same text embedding schema. Qdrant recommends payload partitioning rather than proliferating collections in such cases.

**If this changes:** Create separate collection families only for materially different vector/payload schemas or isolation/scaling needs.

## D-009 — Blue/green index publication

**Decision:** Build a full versioned staging collection and atomically switch the `knowledge_current` alias.

**Reason:** It is simpler to verify and roll back than partially mutating the live index. Content-hash embedding caches control rebuild cost.

**If this changes:** Extremely large corpora may graduate to incremental generation-aware publication after equivalent atomicity and rollback tests exist.

## D-010 — Push trigger plus reconciliation

**Decision:** GitHub Actions triggers a restricted VPS command, and a systemd timer independently reconciles state.

**Reason:** Webhook/runner/network failures should not leave the system permanently stale. The VPS pulls using its own read-only deploy credential.

**If this changes:** A signed webhook service can replace SSH, but it must retain reconciliation and publish locking.

## D-011 — Version policy

**Decision:** Execution agents resolve current stable versions from official sources, then pin exact versions/digests in lock/config files and record them.

**Reason:** This prompt library is intended to remain useful beyond its authoring date. Hard-coding “latest” as of one day is not reproducible later; never pinning is also not reproducible.

**If this changes:** A centrally approved version matrix can replace runtime resolution.

## D-012 — Browser authentication

**Decision:** Use encrypted Agent Browser restore sessions as the default authenticated persistence, with one stable session per service/account. Use a full persistent Chrome profile only when a site needs browser state that restore sessions do not preserve. Never automatically reuse the user's everyday Chrome profile.

**Reason:** Agent Browser encrypts saved restore state with `AGENT_BROWSER_ENCRYPTION_KEY`, while a full Chrome profile contains broader sensitive state and is not made fully encrypted merely by setting that key. Stable service sessions also make the concurrency boundary explicit.

**If this changes:** Reusing/importing a personal Chrome profile must be explicit and documented as a risk acceptance; concurrent access to any shared authenticated session/profile must remain serialized.

## D-013 — Knowledge rights and provenance

**Decision:** Every source must retain URL/path, source type, provenance, checksum, and rights/license notes. Raw video is not committed.

**Reason:** Community projects and tutorial transcripts may have redistribution restrictions. The system should preserve technique/provenance without turning the repository into an uncontrolled asset mirror.

**If this changes:** Organization-specific licensing policy can tighten these rules.


## D-014 — Single-node Qdrant v1, recoverability over high availability

**Decision:** The first deployment is a hardened single-VPS Qdrant instance, not a multi-node HA cluster.

**Reason:** The stated use is a personal/multi-agent technical knowledge service. Git-backed rebuild, snapshots, atomic publication, and explicit outage behavior provide a strong v1 without introducing distributed-cluster operations prematurely.

**If this changes:** Move to a supported multi-node/managed Qdrant architecture and redesign capacity, backup, rolling upgrade, quorum, and disaster-recovery tests before claiming HA.

## D-015 — Secure client connectivity is selected from the real environment

**Decision:** Hermes reaches the Knowledge Gateway through an existing private mesh when available, otherwise an existing TLS reverse proxy, otherwise a restricted SSH tunnel. Public plaintext HTTP is forbidden.

**Reason:** The authoring environment does not know the user's VPS networking/domain topology. This deterministic decision tree is safer than inventing a hostname or requiring a new public service.

**If this changes:** Record the new network trust boundary and equivalent encryption/authentication controls.

## D-016 — No hidden LLM dependency in ingestion v1

**Decision:** The deterministic ingestion tooling validates/extracts/plans but does not silently call a specific LLM API. The execution agent performs semantic cleanup under repository standards.

**Reason:** No model provider/API credential was specified, and hard-wiring one would create a new secret/cost/vendor dependency. Deterministic validators still make future “ingest this” work reproducible.

**If this changes:** Add an explicit model-provider abstraction, locked prompt/version, cost limits, redaction policy, evals, and human/agent review gates before automated semantic rewriting can publish.

## D-017 — Headed browser visibility is host capability, not VPS requirement

**Decision:** Agent Browser is installed on the machine where browser automation should run. A visible browser is verified only when that host has a display.

**Reason:** Installing a full GUI on a headless VPS only to watch automation increases attack surface and operational complexity.

**If this changes:** Use an authorized remote desktop/display stack and add its security/patching/identity requirements to the platform plan.

## D-018 — Use Hermes-native secret loading for MCP bearer authentication

**Decision:** Store the Knowledge MCP bearer token in `~/.hermes/.env` and reference it from `mcp_servers.*.headers` through Hermes runtime `${ENV_VAR}` substitution.

**Reason:** Hermes documents `.env` as its secret store and supports environment substitution in MCP headers. This avoids inventing a second secret-loading mechanism and keeps populated credentials out of `config.yaml` and Git.

**If this changes:** Use a future Hermes-supported OS keychain/credential-store feature only if it provides equal or stronger isolation and the MCP integration verification is updated.

## D-019 — Least-privilege Agent Browser MCP surface

**Decision:** The default general-agent MCP wrapper exposes only Agent Browser `core`, not `all` and not the broader `state`, `network`, `debug`, `tabs`, `react`, or `mobile` profiles.

**Reason:** Agent Browser's current MCP documentation describes `debug` as including plugin/command capabilities and `state` as exposing cookies/storage/auth/profile operations. Hermes only needs ordinary navigation, inspection, interaction, screenshots, tabs/frames, and React inspection for the planned Spline workflow.

**If this changes:** Add a separately named trusted wrapper for the minimum additional profile and keep the default general-agent surface unchanged.

## D-020 — Stable chunk identity excludes source revision/path

**Decision:** Compute `chunk_id` from schema version, domain, stable source ID, semantic section, content hash, and deterministic duplicate occurrence only. Keep source checksum/path/commit as provenance, not identity.

**Rationale:** Unrelated source edits and repository refactors must not churn every unchanged point ID or destroy embedding/cache stability.

**What changes this:** A future identity scheme migration must increment the knowledge schema/identity version and rebuild atomically.

## D-021 — Knowledge Schema v1 is English-only

**Decision:** Publish only `language=en` under schema v1. Record but quarantine non-English sources until a multilingual dense+sparse model pair and regression corpus are explicitly adopted.

**Rationale:** The selected BGE dense model and BM25 configuration are English-oriented; silently indexing other languages would claim a quality contract we have not validated.

**What changes this:** A tested schema migration can adopt multilingual dense and sparse retrieval and republish the corpus.

## D-022 — Build metadata is an atomic sidecar, not a Qdrant knowledge point

**Decision:** Store per-build metadata under `/var/lib/hermes-kb/builds/<collection>.json` and validate it against the active alias.

**Rationale:** Synthetic metadata points would violate the uniform KnowledgeChunk payload contract and distort point counts/retrieval assumptions.

**What changes this:** A future dedicated metadata collection/service with its own explicit schema could replace sidecars.

## D-023 — Repository validation uses a locked PyYAML environment

**Decision:** The platform repo owns a minimal `pyproject.toml` + `uv.lock`; repository validation runs through `uv` and imports locked PyYAML rather than pretending YAML can be fully parsed with the standard library.

**Rationale:** One deterministic local/CI parser avoids divergent manifest validation and partial-parser bugs.

**What changes this:** A future repository-wide tooling environment may absorb the validator if it preserves a locked YAML parser and the same CLI contract.

## D-024 — Memory provider installation is outside this six-prompt scope

**Decision:** Phase 04 defines the routing boundary for durable user/project memory but does not install or migrate Basic Memory, Graphify, or another memory provider. It preserves and uses the Hermes host's existing supported memory capability.

**Rationale:** The technical knowledge platform must not be coupled to a particular personal-memory implementation, and no current repository/host evidence establishes which memory provider is already installed.

**What changes this:** Add a separate audited integration phase if a specific memory provider must be installed, migrated, or synchronized.

## D-025 — The control repository is executable and fail-closed

**Decision:** Keep a standard-library repository validator, regression suite, one-command verification wrapper, and least-privilege SHA-pinned GitHub Actions workflow inside `project-QQ`.

**Rationale:** A prompt library can drift while remaining readable. The control repository now rejects missing artifacts, cross-phase contract mismatches, malformed patches, unsafe secret examples, role-policy drift, broken Markdown, tracked secret classes, and unpinned Actions before changes reach `main`.

**What changes this:** A replacement verifier is acceptable only if it remains dependency-minimal, deterministic, fail-closed, runnable from a clean clone, and covers every current invariant plus deliberate negative tests.

## D-026 — Managed SSH remains an exact-base compatibility patch

**Decision:** Keep `patches/hermes-desktop-managed-ssh.patch` as an emergency, exact-base compatibility artifact rather than a standing Hermes fork or a normal Phase 04 modification.

**Rationale:** Current Hermes Desktop has multiple Windows SSH launch boundaries. The compatibility artifact must cover all of them, prefer the Hermes-managed Git OpenSSH executable, preserve System OpenSSH fallback, record its exact upstream base and SHA-256, and pass upstream typecheck/lint plus clean `git apply --check` evidence. It is not applied when upstream already provides equivalent behavior or when the selected revision differs from the recorded base.

**What changes this:** Remove the patch after an official upstream release provides and verifies equivalent managed-SSH selection. Rebase only from fresh upstream source with new base, checksum, typecheck, lint, and apply evidence.

## D-027 — The reviewed router policy is promoted, not independently rewritten

**Decision:** Treat `project-QQ/skills/skill-router/SKILL.md` as the bootstrap reviewed copy, then promote it byte-for-byte into `hermes-platform/integrations/hermes/skills/skill-router/SKILL.md` and verify matching SHA-256 values.

**Rationale:** Both Hermes roles need the same procedural capability-routing policy, while Hermes's native skill index remains the actual selection mechanism. Hash-verified promotion prevents Desktop/VPS policy drift without creating a competing router daemon or Hermes-core fork.

**What changes this:** A future reviewed version may replace the skill when both repositories update atomically, the role policy references the new version, and both host runtimes pass explicit and natural-language routing verification.
