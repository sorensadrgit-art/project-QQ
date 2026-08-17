# Execution Order

## Recommended linear sequence

1. `prompts/01_foundation_and_repo_governance.md`
2. `prompts/02_agent_browser_installation_and_mcp.md`
3. `prompts/03_qdrant_knowledge_platform_and_github_sync.md`
4. `prompts/04_hermes_integration_and_operating_rules.md`
5. `prompts/05_knowledge_ingestion_and_update_workflow.md`

This linear order minimizes operational ambiguity.

## Dependency graph

```text
01 Foundation
├── 02 Agent Browser
└── 03 Qdrant + Gateway + GitHub Sync
    └── 05 Knowledge Ingestion

02 + 03
└── 04 Hermes Integration
```

## Safe parallelization

After Prompt 01 passes:

- **Prompt 02** can run on the Agent Browser/Hermes host.
- **Prompt 03** can run on the VPS.

They can run in parallel because Prompt 02 owns `infra/agent-browser/` and Prompt 03 owns Qdrant/indexer/gateway/sync paths.

After Prompt 03 passes, **Prompt 05** can run without waiting for Prompt 04. Prompt 04 requires both Prompt 02 and Prompt 03.

## File-ownership collision check

| Path family | Owner |
|---|---|
| repo governance/manifests/root validation | 01 |
| `infra/agent-browser/**`, Agent Browser MCP test | 02 |
| `infra/qdrant/**`, `services/knowledge-indexer/**`, `services/knowledge-gateway/**`, knowledge publish workflow | 03 |
| `integrations/hermes/**` | 04 |
| `tools/knowledge-ingestion/**`, knowledge ingestion playbook/validators | 05 |

Later phases may update only their explicitly identified shared manifest/CI/document files and must preserve unrelated fields. No two prompts own the same service implementation.

## Handoff contract

Every prompt leaves a Markdown report in the platform repository:

```text
docs/handoffs/01-foundation.md
docs/handoffs/02-agent-browser.md
docs/handoffs/03-qdrant-knowledge-platform.md
docs/handoffs/04-hermes-integration.md
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

A downstream agent reads the handoff as evidence but still verifies prerequisites directly.

## Stop conditions

An execution agent may finish with `PARTIAL_ENVIRONMENT_BLOCKER` only when an external condition genuinely prevents a hard-evidence check, such as:

- no permission to create GitHub secrets/deploy keys;
- no access to the real VPS;
- Hermes Desktop is not installed/launchable on that host;
- insufficient VPS RAM/disk;
- official package/release source is unreachable and no verified pinned compatible version exists.

The agent still completes all safe source/config/test work available locally and states exactly which acceptance test remains unverified. It must never convert an external blocker into a guessed PASS.
