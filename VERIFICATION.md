# Verification Report

## Scope

This report separates **artifact/package verification** from **live deployment verification**. The authoring environment had shell/Python/web access and could create/test this package, but it did not have the user's real VPS, Hermes installation, GitHub repositories, browser accounts, or corpus. Therefore no live infrastructure deployment is claimed here.

## Hard evidence produced in the authoring environment

The package-level verifier was executed after the final prompt-contract changes:

```text
PACKAGE_VERIFICATION=PASS checks=144 prompts=5 prompt_sha256=a424f64ee32403a24b01d938474337f2c38f7906f6567f05987f00517f4dc10b
```

The verifier checks, among other invariants:

- all required package files and exactly five numbered standalone prompts;
- required cold-start prompt sections, verification steps, acceptance criteria, and handoffs;
- balanced Markdown code fences;
- exact shared Knowledge Schema v1 and retrieval contracts across prompts;
- no stale unsafe contracts or secret-like literal material in the prompt library;
- locked Phase 01 YAML validation environment;
- Agent Browser default MCP `core`-only least-privilege surface and encrypted restore-session contract;
- canonical Phase 03 chunk planner and Phase 05 delegation;
- stable chunk identity and English-only schema-v1 publication gate;
- Qdrant build sidecar plus atomic alias contract;
- Hermes native `.env` secret handling, secure token-transfer modes, external skills, and four-tool Knowledge MCP allowlist;
- intentional cross-phase shared-file ownership rather than competing overwrites;
- exact ordered `MASTER_PROMPT_LIBRARY.md` concatenation.

Additional authoring scans passed after correcting the scan invocations themselves:

```text
STALE_SCAN=PASS
PLACEHOLDER_VALUE_SCAN=PASS
SECRET_SCAN=PASS
CONFLICT_SCAN=PASS
```

`AUDIT.md` then records the final cross-phase specification review as having zero unresolved blocker or major findings. This is evidence from contract/spec tracing, not evidence that runtime services are deployed.

## Official-source verification

The architecture was checked against current official documentation for Agent Browser, Hermes Agent, Qdrant, the Model Context Protocol Python SDK, and GitHub. Exact references are listed in `REFERENCES.md`. Execution prompts explicitly require implementing agents to re-check current official releases/configuration before installation and then pin resolved versions/digests.

## Live/runtime evidence intentionally deferred to execution agents

The following cannot be verified in this authoring environment and must not be treated as already complete:

- Qdrant bound/authenticated on the user's actual VPS;
- real snapshots, restore drills, GitHub push triggers, and reconciliation timer;
- real Agent Browser installation, browser binary, authenticated sessions, and MCP discovery on the target host;
- Hermes Desktop/CLI configuration and real MCP tool invocation;
- real VPS-to-Hermes gateway-token transfer;
- real corpus indexing/retrieval quality;
- real GitHub branch protection, deploy keys, or Actions permissions.

Each execution prompt contains hard-evidence gates and an explicit environment-blocker state so an agent cannot legitimately report PASS when host/account access is missing.

## Delivery archive integrity

`MANIFEST.sha256` is generated immediately before packaging and excludes itself and `.git`. The final delivery workflow verifies the ZIP with `unzip -t`, extracts it into a clean temporary directory, runs `sha256sum -c MANIFEST.sha256`, and executes `scripts/verify_package.py` against the extracted copy. The final chat delivery report states the observed results from that post-package run.
