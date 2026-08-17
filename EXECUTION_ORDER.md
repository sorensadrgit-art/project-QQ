# Execution Order

## Recommended linear sequence

1. `prompts/01_foundation_and_repo_governance.md`
2. `prompts/02_agent_browser_installation_and_mcp.md`
3. `prompts/03_qdrant_knowledge_platform_and_github_sync.md`
4. `prompts/04_hermes_integration_and_operating_rules.md`
5. **`prompts/04B_dual_hermes_runtime_update_skills_and_router_convergence.md` — mandatory convergence gate**
6. `prompts/05_knowledge_ingestion_and_update_workflow.md`

This linear order minimizes operational ambiguity and ensures the two real Hermes runtimes are current, skill-complete, router-verified, and connected before the system is treated as operational.

## Dependency graph

```text
01 Foundation
├── 02 Agent Browser
└── 03 Qdrant + Gateway + GitHub Sync

02 + 03
└── 04 Hermes Desktop Integration
      └── 04B Dual Hermes Runtime Convergence
            └── 05 Knowledge Ingestion / Normal Operations
```

Prompt 04B is not optional. It is the phase that proves **both** Desktop Hermes and VPS Hermes are updated and healthy, synchronizes/audits required skills, verifies the native Hermes skill router, and re-tests role-specific MCP connectivity after the update.

## Safe parallelization

After Prompt 01 passes:

- **Prompt 02** can run on the Agent Browser/Desktop Hermes host.
- **Prompt 03** can run on the VPS.

They can run in parallel because Prompt 02 owns `infra/agent-browser/` and Prompt 03 owns Qdrant/indexer/gateway/sync paths.

After both Prompt 02 and Prompt 03 pass, run Prompt 04 on the Desktop Hermes host.

After Prompt 04 passes, run **Prompt 04B** with access to both the Desktop Hermes runtime and the VPS Hermes runtime. Prompt 04B must complete or explicitly report the unreachable host as an environmental blocker.

Prompt 05 may be developed after Prompt 03, but **production ingestion/publication must not be declared fully operational until Prompt 04B passes**, because 04B is the cross-runtime update/skills/router/connectivity gate.

## File-ownership collision check

| Path family | Owner |
|---|---|
| repo governance/manifests/root validation | 01 |
| `infra/agent-browser/**`, Agent Browser MCP test | 02 |
| `infra/qdrant/**`, `services/knowledge-indexer/**`, `services/knowledge-gateway/**`, knowledge publish workflow | 03 |
| `integrations/hermes/**` base integration and project routing skills | 04 |
| `integrations/hermes/runtime-baseline/**`, `integrations/hermes/skill-policy.yaml` | 04B |
| `tools/knowledge-ingestion/**`, knowledge ingestion playbook/validators | 05 |

Prompt 04B may reconcile host-local Hermes config and update only the runtime-specific fields of shared manifests/handoffs. It must preserve Prompt 04's integration implementation and project skill contents unless a verified post-update compatibility defect requires a narrowly documented fix.

Later phases may update only their explicitly identified shared manifest/CI/document files and must preserve unrelated fields. No two prompts own the same service implementation.

## Handoff contract

Every execution step leaves a Markdown report in the platform repository:

```text
docs/handoffs/01-foundation.md
docs/handoffs/02-agent-browser.md
docs/handoffs/03-qdrant-knowledge-platform.md
docs/handoffs/04-hermes-integration.md
docs/handoffs/04B-dual-hermes-runtime-convergence.md
docs/handoffs/05-knowledge-ingestion.md
```

Each report contains:

- detected host/OS;
- repository commit before work;
- files changed;
- dependency versions/digests resolved;
- commands/tests run;
- pass/fail output summary;
- secrets created by **name and storage location only**, never value;
- decisions made;
- remaining environmental blockers;
- final repository commit.

Prompt 04B additionally records a redacted Desktop/VPS matrix covering Hermes version/update state, config/doctor status, required skills, skill-router evidence, Knowledge MCP, Agent Browser MCP on Desktop, and VPS gateway runtime status.

A downstream agent reads the handoff as evidence but still verifies prerequisites directly.

## Stop conditions

An execution agent may finish with `PARTIAL_ENVIRONMENT_BLOCKER` only when an external condition genuinely prevents a hard-evidence check, such as:

- no permission to create GitHub secrets/deploy keys;
- no access to the real VPS;
- no access to the real Desktop Hermes host;
- Hermes Desktop is not installed/launchable on that host;
- insufficient VPS RAM/disk;
- official package/release source is unreachable and no verified pinned compatible version exists;
- an operator-controlled credential is required and no existing secure non-logging transfer path is available.

The agent still completes all safe source/config/test work available locally and states exactly which acceptance test remains unverified. It must never convert an external blocker into a guessed PASS.
