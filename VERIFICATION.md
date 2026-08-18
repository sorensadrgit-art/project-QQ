# Verification Report

## Current control-repository verification

The GitHub control repository now carries its own executable validator, regression tests, and SHA-pinned CI workflow. The current checks validate all six prompts, shared handoff and chunk-identity contracts, the managed-SSH patch format/applicability, Markdown fence balance, bounded skill metadata, and tracked-secret indicators.

Run the full local gate from a clean clone:

```bash
python scripts/verify_process.py \
  --root . \
  --hermes-source /absolute/path/to/clean-hermes-checkout-at-the-declared-base
```

The underlying checks can also be run independently:

```bash
python scripts/validate_project.py --root .
python -m unittest discover -s tests -v
```

For the managed-SSH regression, check out the declared Hermes base commit and pass it through `--hermes-source` or `HERMES_SOURCE`. Historical package evidence below remains historical and is not used as proof for current `main`.

### Fresh audit evidence — 2026-08-18

The 2026-08-18 repair was verified against a clean Hermes checkout at exact upstream commit `7cae03b8c02542ca2a9b95d7cd3c02b71010f796`.

```text
PROJECT_QQ_VALIDATION=PASS
UNIT_TESTS=PASS 24/24
PYTHON_COMPILEALL=PASS
WORKFLOW_YAML_PARSE=PASS
PROJECT_QQ_PROCESS_VERIFICATION=PASS
PATCH_APPLY_CHECK=PASS
HERMES_DESKTOP_TYPECHECK=PASS
HERMES_DESKTOP_FOCUSED_ESLINT=PASS
```

The managed-SSH artifact has SHA-256 `969c57a9d59be2df80914510795c8a3843746801b33005ddb5876d5da98255a9`. The real Desktop host also confirmed that the Hermes-managed Git OpenSSH executable exists and can resolve effective SSH configuration, while Windows System OpenSSH remains available as fallback.

Negative regressions deliberately changed the `knowledge_search` minimum query length, removed a required contract file, inserted populated secrets into JSON, exported shell variables, and `*.env.example` files, added a tracked `.env`, introduced trailing whitespace, and dirtied the exact-base Hermes checkout. Every corrupted state made `scripts/validate_project.py` exit non-zero. This demonstrates that the validator enforces contracts, source provenance, and secret boundaries rather than merely printing a success marker.

These results verify the control repository and compatibility artifact. They do not replace Phase 02–05 live-service handoffs or claim that the entire distributed platform is currently deployed.

## Scope

This report separates **artifact/package verification**, **GitHub project-control verification**, and **live deployment verification**.

The original authoring environment had shell/Python/web access and could create/test the initial package, but it did not have the user's real VPS, Hermes installation, browser accounts, or corpus. During the 2026-08-18 repair, the real Windows Desktop host and its Hermes-managed SSH runtime were inspected, and the exact upstream Hermes source was compiled and linted; the VPS command relay was intermittently available earlier but was offline during final branch verification. Partial host inspection and a writable control repository do not prove Phase 02–05 runtime completion, so no live Hermes update, skill-router pass, or MCP runtime pass is claimed here until the required host handoffs exist.

## Original package hard evidence

Before the GitHub control-repo extension for dual-runtime convergence, the original five-prompt delivery package passed its package verifier:

```text
PACKAGE_VERIFICATION=PASS checks=144 prompts=5 prompt_sha256=a424f64ee32403a24b01d938474337f2c38f7906f6567f05987f00517f4dc10b
```

That evidence applies to the delivered archive at that point in time. It must **not** be misrepresented as verification of the later Prompt 04B addition.

The original verifier checked, among other invariants:

- required cold-start prompt sections, verification steps, acceptance criteria, and handoffs;
- balanced Markdown code fences;
- shared Knowledge Schema v1 and retrieval contracts;
- no stale unsafe contracts or secret-like literal material in the original prompt library;
- locked Phase 01 YAML validation environment;
- Agent Browser least-privilege MCP and encrypted restore-session contract;
- canonical Phase 03 chunk planner and Phase 05 delegation;
- stable chunk identity and English-only schema-v1 publication gate;
- Qdrant build sidecar plus atomic alias contract;
- Hermes native `.env` secret handling, secure token-transfer modes, external skills, and bounded Knowledge MCP allowlist;
- intentional cross-phase shared-file ownership.

Additional original authoring scans passed:

```text
STALE_SCAN=PASS
PLACEHOLDER_VALUE_SCAN=PASS
SECRET_SCAN=PASS
CONFLICT_SCAN=PASS
```

## GitHub control-repo extension: dual Hermes runtime convergence

The control repo now adds these mandatory artifacts:

```text
HERMES_RUNTIME_BASELINE.md
prompts/04B_dual_hermes_runtime_update_skills_and_router_convergence.md
```

and updates:

```text
README.md
REPO_MAP.md
EXECUTION_ORDER.md
PLAN.md
VERIFICATION.md
```

The new gate closes a runtime coverage gap: the earlier design could fully integrate Desktop Hermes while leaving VPS Hermes version/skills/router state under-specified.

The updated architecture now requires:

- official supported Hermes update + backup on Desktop and VPS;
- clean `hermes update --check`, config validation/migration, and `hermes doctor` on both;
- proof the Desktop GUI uses the updated runtime;
- proof any VPS Hermes gateway uses the updated runtime;
- bundled-skill synchronization on both;
- safe check/update of already-installed Hub skills;
- Hermes skill security audit on both;
- role-specific project skills loaded from source control;
- native Hermes skill-router verification in a fresh session using real trace/behavior evidence;
- Knowledge MCP on both hosts;
- Agent Browser MCP on Desktop;
- no copying of Desktop browser/auth/session state to VPS.

### GitHub-side evidence

The repository API was used to confirm the relevant files exist on `main` after mutation. This proves the control documents/prompts are present in GitHub; it does **not** prove any runtime action has occurred.

## Official-source verification for the new runtime gate

The dual-runtime requirements were checked against current official Hermes documentation at the time of the repo update. Current Hermes documentation confirms the following capabilities used by Prompt 04B:

- `hermes update` is the supported update path and includes dependency refresh, config migration checks, bundled-skill synchronization, and running-gateway restart behavior;
- `hermes update --check` provides a non-mutating behind/current check;
- `hermes update --backup` provides a full pre-update backup path;
- recommended post-update validation includes `hermes doctor`, version inspection, and gateway status when used;
- bundled skills synchronize during Hermes update;
- installed Hub skills support `hermes skills check`, `hermes skills update`, and `hermes skills audit`;
- external skill directories are supported through `skills.external_dirs` and appear in the skill index, `skills_list`, `skill_view`, and slash commands;
- Hermes supports stdio and HTTP MCP client configuration and MCP connection testing.

Prompt 04B requires the execution agent to re-read the installed version's actual help/schema before mutation because these interfaces can evolve.

## Live/runtime evidence intentionally deferred to execution agents

The following cannot be verified from this GitHub/control environment and must not be treated as already complete:

- actual Desktop Hermes update/version state;
- actual VPS Hermes update/version state;
- actual Desktop GUI backend identity;
- actual VPS Hermes gateway executable/runtime identity;
- real `hermes doctor` output on either host;
- real bundled/Hub skill state or security-audit results;
- real native skill-router selection traces;
- real Agent Browser installation/authenticated session/MCP behavior on the Desktop host;
- real Knowledge MCP connectivity from Desktop and VPS;
- Qdrant bound/authenticated on the user's actual VPS;
- real snapshots, restore drills, GitHub push triggers, and reconciliation timer;
- real corpus indexing/retrieval quality.

Prompt 04B has explicit `PASS`, `FAIL`, and `PARTIAL_ENVIRONMENT_BLOCKER` outcomes so an agent cannot legitimately report full convergence without reaching both real runtimes and gathering fresh evidence.

## Runtime completion rule

Do not declare the platform runtime-complete until the real handoff exists at:

```text
hermes-platform/docs/handoffs/04B-dual-hermes-runtime-convergence.md
```

and every required Desktop/VPS cell in `HERMES_RUNTIME_BASELINE.md` is evidenced as PASS (or an intentionally non-applicable role cell is marked N/A with rationale).

## Delivery archive note

The original downloadable ZIP predates the GitHub-only Prompt 04B extension unless a new archive is explicitly regenerated later. The GitHub `main` branch is now the authoritative control-repo version for execution order and Hermes dual-runtime convergence.
