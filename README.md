# Hermes AI Infrastructure & Knowledge System v1

This repository is the **project-control and execution-prompt repository** for the Hermes + Agent Browser + Qdrant knowledge system.

It contains the architecture, contracts, operating/recovery rules, and standalone prompts that can be handed to separate agents. It does **not** store runtime secrets, browser sessions, Qdrant data, or the future technical knowledge corpus itself.

## Start here

1. Read `REPO_MAP.md` to see exactly what belongs in this repository, on the VPS, on the Desktop Hermes host, and in the future `hermes-platform` / `hermes-knowledge` repositories.
2. Read `EXECUTION_ORDER.md`.
3. Read `HERMES_RUNTIME_BASELINE.md` — this is the mandatory contract for keeping **both** Desktop Hermes and VPS Hermes updated, skill-complete, router-verified, and connected.
4. Give `prompts/01_foundation_and_repo_governance.md` to the first implementation agent.
5. Continue through the sequence including the mandatory Prompt 04B convergence gate.

## Execution sequence

```text
01 Foundation & Repository Governance
        ├── 02 Agent Browser Installation & MCP
        └── 03 Qdrant Knowledge Platform & GitHub Sync

02 + 03
        └── 04 Hermes Desktop Integration
                └── 04B Dual Hermes Runtime Update / Skills / Router Convergence
                        └── 05 Knowledge Ingestion & Update Workflow
```

Prompts 02 and 03 may run in parallel after Prompt 01. A linear `01 → 02 → 03 → 04 → 04B → 05` run is the simplest operational sequence.

**Prompt 04B is mandatory.** It updates and verifies both real Hermes runtimes, reconciles their role-specific skills, verifies the native Hermes skill router, confirms Hermes Desktop is using the updated backend, confirms the VPS gateway is using the updated runtime, and re-tests Knowledge/Agent Browser MCP connectivity after the update.

## Files intentionally stored here

- `.gitattributes` — forces stable LF text bytes across operating systems, including the checksummed patch artifact.
- `.gitignore` — excludes local Python/tool caches and operating-system noise.
- `README.md` — entry point for the project.
- `REPO_MAP.md` — where every component/file belongs and where each prompt runs.
- `PLAN.md` — final production architecture and phase contracts.
- `ARCHITECTURE.md` — runtime topology and data/control flows.
- `CONTRACTS.md` — shared schemas, endpoints, security boundaries, and handoffs.
- `DECISIONS.md` — engineering assumptions and rationale.
- `EXECUTION_ORDER.md` — prompt dependencies and safe parallelization.
- `HERMES_RUNTIME_BASELINE.md` — required Desktop/VPS Hermes update, skills, router, and MCP baseline.
- `SKILL_POLICY.md` — durable capability-selection and skill-router policy.
- `KNOWLEDGE_STANDARDS.md` — durable source cleaning/chunking/provenance standard.
- `INGESTION_CHECKLIST.md` — repeatable checklist for future data.
- `RECOVERY.md` — rebuild and disaster-recovery rules.
- `REFERENCES.md` — authoritative product/documentation references.
- `VERIFICATION.md` — current control-repository checks, evidence, and runtime limitations.
- `skills/skill-router/SKILL.md` — reviewed bootstrap routing policy promoted into the operational platform repository.
- `patches/hermes-desktop-managed-ssh.patch` and `patches/README.md` — exact-base emergency Windows SSH compatibility artifact and its provenance/application gate.
- `scripts/validate_project.py` — fail-closed control-repository validator.
- `scripts/verify_process.py` — one-command local validation, regression-test, and whitespace gate.
- `tests/test_project_contracts.py` — regression tests for cross-phase contracts and patch applicability.
- `.github/workflows/validate-project.yml` — least-privilege, SHA-pinned CI gate.
- `prompts/` — the six implementation prompts, including mandatory Prompt 04B.

The original downloadable archive also contained authoring/package-only artifacts such as the concatenated master prompt file, archive checksum manifest, package verifier, and Superpowers authoring documents. Those are useful for archival/audit purposes but are **not required for operating this GitHub project**, so they are intentionally not duplicated here.

## Validate this control repository

From a clean clone, run the one-command gate. Supplying the exact clean Hermes checkout proves the compatibility patch still applies; omitting it runs every control-repository check except that external apply test.

```bash
python scripts/verify_process.py \
  --root . \
  --hermes-source /absolute/path/to/hermes-agent-at-declared-base
```

The validator and regression suite can also be run separately:

```bash
python scripts/validate_project.py --root .
python -m unittest discover -s tests -v
```

CI repeats the full sequence against the exact pinned Hermes base. A passing control-repository gate proves these documents and artifacts agree mechanically; it does not substitute for the live-host handoffs required by each phase.

## What this repository is not

This repository is not the long-term technical corpus and is not a secret store.

Prompt 01 creates or normalizes the two operational source-of-truth repositories used by the implemented system:

```text
hermes-platform   → infrastructure, services, integrations, CI, runbooks
hermes-knowledge  → Spline/GSAP/React/WebGL/etc source + normalized knowledge
```

Once those exist, new Spline docs, tutorials, community-pattern abstractions, GSAP docs, React docs, WebGL material, and future knowledge go into `hermes-knowledge` through the ingestion workflow—not into this project-control repo root.

## Hermes runtime policy

There are two first-class Hermes runtimes:

```text
Desktop Hermes → desktop/CLI runtime + Agent Browser MCP + Knowledge MCP
VPS Hermes     → VPS agent/gateway runtime + Knowledge MCP
```

Both must stay updated through Hermes's official supported update path. Both must synchronize the bundled skills from the selected Hermes release, check/update installed Hub skills safely, audit installed skills, load the source-controlled role-required project skills, and prove the **native Hermes skill router** works in a fresh natural-language routing test.

The native skill router is part of Hermes's skill system; it is not a separate network service. Do not install an unrelated third-party router unless the platform explicitly adopts one in a reviewed future change.

Role baseline:

```text
Both:    bundled Hermes skills + safe Hub updates/audit + skill-router + knowledge-retrieval
Desktop: + agent-browser-routing
VPS:     no Desktop browser skill unless Agent Browser is intentionally deployed there
```

See `HERMES_RUNTIME_BASELINE.md` for the full contract.

## Never commit these

Do not place any of the following in this repository or any other Git repository:

- browser cookies, storage state, or Chrome profiles;
- `AGENT_BROWSER_ENCRYPTION_KEY` values;
- Qdrant API/admin keys;
- `KNOWLEDGE_MCP_BEARER_TOKEN` values;
- SSH private keys;
- populated `.env` secret files;
- Hermes `~/.hermes/.env`;
- Hermes auth/session databases;
- passwords, 2FA recovery codes, session tokens, or authenticated screenshots containing secrets.

## Core architecture

- **Hermes Agent / Hermes Desktop** is the primary agent runtime.
- **Agent Browser** provides interactive browser automation over MCP stdio on the Desktop/browser host.
- **Qdrant** is a private, disposable/rebuildable retrieval index.
- **Git** is authoritative for knowledge and infrastructure definitions.
- **Knowledge Gateway** exposes bounded authenticated retrieval to both Hermes runtimes and other agents; general agents do not talk directly to Qdrant.
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

Runtime software versions are resolved from current official stable releases during execution and then pinned/recorded exactly by the implementing agent where the distribution supports that model.

## Completion standard

The project is not considered deployed merely because these prompts exist. Runtime completion requires hard evidence from the actual hosts: Agent Browser functional/MCP tests, private/authenticated Qdrant, atomic fixture publication and rollback, GitHub synchronization, **both Hermes runtimes current and healthy**, required skill sets present/audited, native skill-router tests passing, Hermes MCP discovery, grounded retrieval on Desktop and VPS, browser execution on Desktop, and a clean rebuild from Git.
