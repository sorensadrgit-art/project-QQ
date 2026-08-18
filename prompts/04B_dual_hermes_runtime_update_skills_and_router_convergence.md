# Prompt 04B — Dual Hermes Runtime Update, Skills, Router, and MCP Convergence

You are a senior Hermes runtime engineer, endpoint-operations engineer, MCP integration engineer, security engineer, and agent-systems verifier. Your task is to converge **both** Hermes installations in this project — the operator's Desktop Hermes runtime and the VPS Hermes runtime — onto a current, healthy, role-correct state after Prompt 04 has created the source-controlled Hermes integration and skills.

Do not ask the operator questions. Inspect the real hosts, repositories, Hermes install types, versions, configs, and available access. Choose the safest supported engineering path, record assumptions, and complete everything possible. Never fabricate access, credentials, versions, update success, skill routing, MCP connectivity, or runtime test results.

This is a **mandatory convergence gate**. Prompt 05 must not treat the platform as fully operational until this prompt passes or records a precise environmental blocker.

## Fixed project context

Three Git repositories/roles exist conceptually:

1. `project-QQ` — project-control documentation and execution prompts.
2. `hermes-platform` — executable infrastructure, Hermes integrations, source-controlled project skills, CI, operations, and recovery.
3. `hermes-knowledge` — canonical technical knowledge corpus and retrieval tests.

Read before changing either runtime:

```text
project-QQ/HERMES_RUNTIME_BASELINE.md
project-QQ/ARCHITECTURE.md
project-QQ/CONTRACTS.md
project-QQ/DECISIONS.md
hermes-platform/docs/handoffs/01-foundation.md
hermes-platform/docs/handoffs/02-agent-browser.md
hermes-platform/docs/handoffs/03-qdrant-knowledge-platform.md
hermes-platform/docs/handoffs/04-hermes-integration.md
hermes-platform/SYSTEM_MANIFEST.yaml
hermes-platform/SECURITY.md
```

If a listed artifact does not exist, determine whether the producing phase actually ran. Do not synthesize a fake handoff. Continue only with work whose prerequisites are real and record the missing dependency.

## Prerequisites

Prompt 04 must have created the operational Hermes integration and project-skill directory. Both real Hermes hosts must be reachable through already-authorized local or SSH access, and the Phase 02/03 services assigned to each role must have real handoffs. A missing host, handoff, or credential is an explicit environment blocker; it is never permission to fabricate convergence evidence.

The canonical bootstrap policy skill must be readable from `project-QQ/skills/skill-router/SKILL.md`. Prompt 04B promotes that reviewed file into the operational platform skill directory and verifies its hash before registering it on either host.

## Objective

Bring the two Hermes runtimes to this end state:

### Desktop Hermes

- updated through the current official supported Hermes update path;
- config migrated and `hermes doctor` clean for project-relevant checks;
- Hermes Desktop uses the same updated local runtime that was verified from CLI;
- bundled skills synchronized;
- installed Hub skills checked, safely updated, and security-audited;
- source-controlled project skills loaded from `hermes-platform`;
- `skill-router`, `knowledge-retrieval`, and `agent-browser-routing` visible and routable;
- native Hermes skill router proven by both explicit and natural-language routing tests;
- Knowledge MCP healthy;
- Agent Browser MCP healthy;
- no secrets committed or logged.

### VPS Hermes

- updated through the current official supported Hermes update path;
- config migrated and `hermes doctor` clean for project-relevant checks;
- running Hermes gateway/service, if present, is restarted onto the updated runtime;
- bundled skills synchronized;
- installed Hub skills checked, safely updated, and security-audited;
- source-controlled project skills loaded from `hermes-platform`;
- `skill-router` and `knowledge-retrieval` visible and routable;
- native Hermes skill router proven by both explicit and natural-language routing tests;
- Knowledge MCP healthy through localhost/private networking;
- Qdrant remains internal and is not registered as a general agent tool;
- no secrets committed or logged.

## Scope boundary

### Build / modify

You may create or modify only these source-controlled surfaces unless the existing repository has an equivalent established path:

```text
hermes-platform/integrations/hermes/
├── skill-policy.yaml
├── skills/
│   └── skill-router/
│       └── SKILL.md
├── runtime-baseline/
│   ├── README.md
│   ├── reconcile-runtime.sh
│   ├── verify-runtime.sh
│   └── compare-runtimes.sh
└── docs or examples that do not contain secrets

hermes-platform/docs/handoffs/
└── 04B-dual-hermes-runtime-convergence.md
```

You may modify each host's real Hermes configuration/state through supported Hermes commands and narrowly-scoped config merges.

### Do not

- do not fork or patch Hermes core;
- do not copy Desktop auth/session databases to the VPS or vice versa;
- do not install every optional/community skill blindly;
- do not add a third-party skill router merely because the word "router" appears in this prompt;
- do not expose Qdrant to agents/public networking;
- do not overwrite local skill edits with `--force` without reviewing the diff and recording why replacement is safe;
- do not synchronize provider/API secrets across hosts unless an explicit existing operator secret-management contract requires that credential on both;
- do not claim the Desktop GUI is using the updated runtime without checking its real backend/runtime resolution;
- do not use floating `latest` container tags or guessed Hermes versions.

## Native Hermes skill-router decision

Use Hermes's **native skill system/router** as the default and required routing layer. Current Hermes exposes skills through its skill index, `skills_list`, `skill_view`, slash commands, project/external directories, and prompt-time routing. Treat the router as part of the runtime, not as a standalone network service.

The repository explicitly depends on the reviewed procedural policy skill at `project-QQ/skills/skill-router/SKILL.md`. Promote that exact content into `hermes-platform/integrations/hermes/skills/skill-router/SKILL.md`, record both SHA-256 hashes, and require them to match. This custom skill supplements—never replaces—the native Hermes skill-selection mechanism.

A separate community semantic skill-router plugin remains out of scope. Do not install a second competing router.

## Required role policy

Create or reconcile:

```text
hermes-platform/integrations/hermes/skill-policy.yaml
```

with this machine-valid contract:

```yaml
schema_version: 1
bundled:
  sync_all: true
hub:
  check_updates: true
  update_outdated: true
  audit_installed: true
project_skills:
  source_dir: integrations/hermes/skills
roles:
  desktop:
    required_project_skills:
      - skill-router
      - knowledge-retrieval
      - agent-browser-routing
    required_mcp_servers:
      - knowledge
      - agent_browser
  vps:
    required_project_skills:
      - skill-router
      - knowledge-retrieval
    required_mcp_servers:
      - knowledge
```

If Prompt 04 produced additional reviewed project skills, add them to the correct role(s) rather than deleting them. Do not add a skill to both roles merely for symmetry when its required tool does not exist on both hosts.

## Host discovery

Identify both targets from existing handoffs/config. Prefer:

- Desktop: current/local host if this agent runs there;
- VPS: the already-configured operator SSH target from the platform handoffs, deployment config, or existing authorized SSH config.

Do not invent a hostname/IP. Do not place a hostname containing private information into public docs unless it already exists there by design.

Create a non-secret host matrix in the handoff:

```text
ROLE | OS | ARCH | HERMES_PATH | INSTALL_TYPE | VERSION_BEFORE | ACCESS_MODE
```

If the current execution environment can reach only one runtime, still implement the reusable reconciliation scripts and fully verify the reachable host. Mark the unreachable host as `PARTIAL_ENVIRONMENT_BLOCKER` with the missing access requirement. Do not call the overall phase PASS.

## Pre-update backups

Before updating each host, use Hermes's supported full backup/update-backup path. Prefer:

```bash
hermes update --backup
```

when performing the update, and use `hermes backup` as an additional migration/recovery artifact if the installed version's official documentation recommends it for that host.

Record only backup path, timestamp, and non-secret metadata. Never commit the backup archive.

Also back up the active `~/.hermes/config.yaml` atomically to a mode-0600 host-local backup directory before any manual config merge.

## Hermes update procedure — both hosts

For each host, inspect first:

```bash
set -Eeuo pipefail
command -v hermes
hermes version || hermes --version
hermes update --check || true
hermes --help
hermes config --help || true
hermes skills --help || true
hermes mcp --help || true
hermes gateway --help || true
```

Determine install type from real evidence: managed installer/source checkout/PyPI/other officially supported path. Do not assume both hosts use the same channel.

Then update using the installed version's **official supported updater**. For standard current Hermes this is expected to be:

```bash
hermes update --backup
```

The update must complete dependency refresh, bundled-skill synchronization, config migration hooks, and gateway/backend restart behavior supported by the current release.

After update run:

```bash
hermes update --check
hermes config check
hermes doctor
hermes version || hermes --version
```

If `hermes config check` reports missing options, run the installed version's supported migration path (normally `hermes config migrate`) and select safe defaults from official schema/docs when no environment-specific secret is required. Record every non-default decision in the handoff. If a required secret/value cannot be inferred safely, preserve the old working configuration, mark the exact blocker, and do not invent a value.

### Update success requirement

A host passes update only when:

- update command exited successfully;
- `hermes update --check` reports no pending update for the selected channel;
- config check is clean;
- `hermes doctor` has no unresolved error relevant to this system;
- exact post-update version/commit is recorded;
- any active Hermes gateway/backend has been restarted and is using the updated runtime.

### Channel/version convergence

Compare the post-update versions/channels.

Preferred state: both runtimes use the same supported stable channel and exact Hermes release/commit.

If platform-specific official packaging makes exact equality inappropriate, accept different package identifiers only when their underlying Hermes capability level is demonstrably compatible with:

- external/project skills;
- `skills_list`/`skill_view`;
- HTTP and stdio MCP client support;
- required config migration behavior;
- the same Knowledge MCP contract.

Record the difference and reason. Do not force unsupported installation layouts merely to make version strings match.

## Desktop runtime identity verification

Hermes Desktop may launch/reuse a local Hermes runtime. Prove the GUI's backend resolves to the runtime you just updated.

Use the current official Desktop diagnostics/settings/logs or supported launch command. Compare backend executable/root/version with the CLI runtime. If the GUI uses a remote Hermes backend instead of the local runtime, record that topology and apply this prompt's Desktop role checks to the actual backend it uses.

Do not call `DESKTOP_RUNTIME_MATCH=PASS` merely because `hermes` on PATH was updated.

## VPS gateway/service verification

If VPS Hermes runs a gateway/service:

```bash
hermes gateway status
```

or the installed version's equivalent must show the service healthy after update. Inspect the service command/executable path and ensure it points to the updated runtime/profile.

A stale long-running gateway process using the pre-update interpreter fails this phase even if `hermes version` in a new shell is current.

## Bundled and Hub skill maintenance — both hosts

On each host run the current official equivalents of:

```bash
hermes skills list
hermes skills check
hermes skills update
hermes skills audit
```

Rules:

1. `hermes update` is expected to synchronize the bundled skills shipped with that Hermes release. Verify the bundled manifest/state rather than assuming it happened.
2. `hermes skills check` must report whether Hub-installed skills have upstream changes.
3. `hermes skills update` may update only safely updatable Hub skills.
4. If a skill has local edits and Hermes skips it, diff/review it. Preserve intentional local changes or migrate them explicitly. Never use blanket `--force`.
5. Any required skill quarantined by the security scanner is a blocker until its content is reviewed/fixed/replaced with a trusted equivalent.
6. Do not install unrelated optional skills simply to increase the skill count.

Capture names, sources, versions/hashes when available — never secrets.

## Project skills source and host-local registration

Project skills must remain source controlled at:

```text
hermes-platform/integrations/hermes/skills/
```

Promote and verify the bootstrap router before host registration. Use real absolute repository paths; this Python operation is deterministic and fails if the copies differ:

```bash
PROJECT_QQ_REPO=/absolute/path/to/project-QQ
PLATFORM_REPO=/absolute/path/to/hermes-platform
export PROJECT_QQ_REPO PLATFORM_REPO
python3 - <<'PY'
import hashlib
import os
import shutil
from pathlib import Path

source = Path(os.environ["PROJECT_QQ_REPO"]) / "skills/skill-router/SKILL.md"
target = Path(os.environ["PLATFORM_REPO"]) / "integrations/hermes/skills/skill-router/SKILL.md"
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(source, target)
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
target_hash = hashlib.sha256(target.read_bytes()).hexdigest()
if source_hash != target_hash:
    raise SystemExit("skill-router promotion hash mismatch")
print(f"SKILL_ROUTER_SHA256={target_hash}")
PY
```

Ensure each host has an authenticated/readable clone or deployment copy of `hermes-platform` at a stable path. Do not use a transient `/tmp` checkout as the configured skill source. The operational skill directory should be read-only to the Hermes service/runtime identity when host permissions permit, because `skills.external_dirs` is a discovery mechanism rather than a write-protection boundary.

Merge the platform skills path into Hermes's current supported external-skill configuration. On current Hermes this is expected to be:

```yaml
skills:
  external_dirs:
    - /absolute/stable/path/to/hermes-platform/integrations/hermes/skills
```

Preserve all unrelated `skills` settings and existing external directories.

Do not copy the skill files into Basic Memory or the permanent system prompt.

### Required skills by role

Desktop must expose:

```text
skill-router
knowledge-retrieval
agent-browser-routing
```

VPS must expose:

```text
skill-router
knowledge-retrieval
```

If source control contains additional role-required skills declared in `skill-policy.yaml`, enforce them too.

After changing skill paths, start a **fresh Hermes session** (or use the current official cache invalidation mechanism). A stale pre-change session is not valid evidence.

## MCP reconciliation

### Desktop

Verify:

```bash
hermes mcp list
hermes mcp test knowledge
hermes mcp test agent_browser
```

or exact current equivalents.

Pass criteria:

- Knowledge server authenticates and exposes only approved tools;
- Agent Browser server starts/connects through its local stdio wrapper;
- representative harmless calls work;
- no secret value appears in command output/logs.

### VPS

Verify:

```bash
hermes mcp list
hermes mcp test knowledge
```

The VPS Knowledge MCP should use localhost/private connectivity where possible. Ensure Qdrant itself is **not** registered as a general-purpose Hermes MCP server/tool.

If an Agent Browser server happens to exist on the VPS from a separate reviewed deployment, do not remove it, but do not make it a required baseline unless `skill-policy.yaml` explicitly assigns it to the VPS role.

## Native skill-router verification — hard evidence required

For each host, perform **two** skill loading tests for each role-required project skill.

### Test 1 — explicit load

Use the installed Hermes surface to invoke the skill explicitly by slash command or exact skill name.

Pass only if the runtime loads the real source-controlled skill and the trace/session identifies the expected skill.

### Test 2 — natural-language routing

Start a new session. Do **not** mention the skill name.

#### Desktop knowledge routing case

Ask a deterministic technical question whose answer is present in the Phase 03 fixture knowledge corpus and instruct only that Hermes should use the project's indexed technical knowledge if relevant.

Pass only if the runtime trace shows:

1. the native router/index selected/loaded `knowledge-retrieval` (for example through `skill_view` or the strongest official trace available);
2. Hermes then used the Knowledge MCP;
3. answer/provenance matches the fixture.

#### Desktop browser routing case

Ask Hermes to interact with `https://example.com` using the project's persistent interactive browser capability, without naming the skill.

Pass only if the trace shows:

1. `agent-browser-routing` loaded automatically;
2. Agent Browser MCP was actually called;
3. page state was observed and verified.

#### VPS knowledge routing case

Ask the same deterministic knowledge fixture question without naming the skill.

Pass only if:

1. `knowledge-retrieval` is automatically selected/loaded;
2. Knowledge MCP is called locally/privately;
3. fixture truth and provenance are correct.

### Router evidence rule

The model saying "I used the knowledge skill" is not evidence. Accept evidence from the official tool trace, `skill_view` call, debug/session logs, or equivalent current Hermes runtime instrumentation.

If the installed release offers no way to observe routing, use the strongest available behavioral evidence and record `ROUTER_TRACE_LIMITATION=<exact limitation>`. Do not silently upgrade a behavioral inference to a trace-proven PASS.

## Reusable scripts

Create:

```text
hermes-platform/integrations/hermes/runtime-baseline/reconcile-runtime.sh
hermes-platform/integrations/hermes/runtime-baseline/verify-runtime.sh
hermes-platform/integrations/hermes/runtime-baseline/compare-runtimes.sh
```

### `reconcile-runtime.sh`

Requirements:

```text
--role desktop|vps
--platform-root ABSOLUTE_PATH
--non-interactive-safe
```

It must:

- use `set -Eeuo pipefail`;
- refuse an unknown role;
- never print secrets;
- verify the platform skill directory exists;
- safely merge the external skill directory into the current Hermes config using the installed schema;
- preserve existing unrelated config;
- run config validation;
- verify role-required skills exist;
- return non-zero if a required role skill is absent/quarantined.

It must **not** install/update Hermes itself; update remains an explicit operator/auditable action in this prompt.

### `verify-runtime.sh`

Requirements:

```text
--role desktop|vps
--platform-root ABSOLUTE_PATH
```

It must produce a redacted machine-readable summary containing:

```text
role
hermes_version
update_check
config_check
doctor
skills_required
skills_visible
skill_audit
mcp_required
mcp_status
gateway_status when applicable
```

Never emit bearer tokens, provider keys, browser state, auth JSON, cookies, or entire `.env` contents.

### `compare-runtimes.sh`

Accept two redacted verification summaries and fail if:

- either runtime failed a required check;
- either runtime lacks required project skills;
- either runtime has a failed required MCP;
- versions/capabilities are incompatible;
- a required router test is missing.

Version-string inequality alone is a warning, not an automatic failure, when official platform packaging differs but capability compatibility was verified.

## Security checks

On both hosts verify:

- `~/.hermes` permissions are no broader than required by the supported runtime;
- `~/.hermes/.env` is outside Git and not group/world-readable;
- no secrets were introduced into `config.yaml` when environment substitution is supported;
- project skills contain no credentials or copied browser state;
- git repos have no populated `.env` files or private keys;
- skill audit has no unresolved dangerous verdict for a required skill;
- Qdrant remains private/internal;
- Desktop browser state remains local to the browser host;
- VPS does not receive Desktop cookies/profile state.

## Failure and rollback

If updating one host fails:

1. preserve the other host's verified state;
2. inspect `~/.hermes/logs/update.log` or current official update log;
3. use the pre-update snapshot/full backup and official rollback path;
4. re-run `hermes doctor` and required runtime checks;
5. record the failure and exact recovery action.

Do not roll both runtimes back unless cross-version incompatibility is demonstrated.

If a required skill update introduces a security or behavior regression, restore the prior reviewed skill version/source commit and document the pin.

## Source-control updates

Commit only non-secret scripts, policy, docs, and handoff evidence to `hermes-platform`.

Update `SYSTEM_MANIFEST.yaml` with observed non-secret fields such as:

```yaml
hermes:
  desktop:
    version: <observed>
    install_channel: <observed>
    runtime_verified: true|false
  vps:
    version: <observed>
    install_channel: <observed>
    runtime_verified: true|false
  skill_policy: integrations/hermes/skill-policy.yaml
  router: native
```

Preserve unrelated manifest fields.

## Acceptance criteria

- [ ] Both real Hermes runtimes were discovered; missing access is explicitly blocked rather than guessed.
- [ ] Both runtimes have pre-update backups.
- [ ] Both runtimes were updated using their official supported Hermes update mechanism.
- [ ] `hermes update --check` is clean on both selected update channels.
- [ ] Config check/migration is clean on both.
- [ ] `hermes doctor` passes project-relevant checks on both.
- [ ] Exact post-update Hermes version/commit/channel is recorded for both.
- [ ] Hermes Desktop is proven to use the updated Desktop runtime/backend.
- [ ] VPS gateway/service, if used, is proven to run the updated VPS runtime.
- [ ] Bundled skills are synchronized on both.
- [ ] Installed Hub skills were checked for updates and safely updated where appropriate.
- [ ] Installed skills were security-audited on both.
- [ ] `skill-policy.yaml` exists and validates.
- [ ] Desktop sees `knowledge-retrieval` and `agent-browser-routing`.
- [ ] VPS sees `knowledge-retrieval`.
- [ ] External/project skill directories are configured through supported Hermes config on both hosts.
- [ ] Explicit skill load tests pass.
- [ ] Natural-language skill-router tests pass with real trace/behavior evidence.
- [ ] Desktop Knowledge MCP test passes.
- [ ] Desktop Agent Browser MCP test passes.
- [ ] VPS Knowledge MCP test passes.
- [ ] Qdrant is not exposed as a general Hermes tool.
- [ ] Secrets/browser state were not copied between hosts or committed.
- [ ] Reusable reconciliation/verification/compare scripts exist and pass shell/static validation.
- [ ] `docs/handoffs/04B-dual-hermes-runtime-convergence.md` contains the full redacted verification matrix.

## Required handoff

Write:

```text
hermes-platform/docs/handoffs/04B-dual-hermes-runtime-convergence.md
```

Include:

```text
PHASE_04B_STATUS=PASS or PARTIAL_ENVIRONMENT_BLOCKER or FAIL

DESKTOP_HERMES_VERSION=<observed>
DESKTOP_INSTALL_CHANNEL=<observed>
DESKTOP_UPDATE_CHECK=PASS|FAIL
DESKTOP_DOCTOR=PASS|FAIL
DESKTOP_RUNTIME_MATCH=PASS|FAIL|NOT_AVAILABLE
DESKTOP_SKILLS=PASS|FAIL
DESKTOP_SKILL_ROUTER=PASS|FAIL|TRACE_LIMITED
DESKTOP_KNOWLEDGE_MCP=PASS|FAIL
DESKTOP_AGENT_BROWSER_MCP=PASS|FAIL

VPS_HERMES_VERSION=<observed>
VPS_INSTALL_CHANNEL=<observed>
VPS_UPDATE_CHECK=PASS|FAIL
VPS_DOCTOR=PASS|FAIL
VPS_GATEWAY_RUNTIME=PASS|FAIL|NOT_USED
VPS_SKILLS=PASS|FAIL
VPS_SKILL_ROUTER=PASS|FAIL|TRACE_LIMITED
VPS_KNOWLEDGE_MCP=PASS|FAIL

CROSS_RUNTIME_COMPATIBILITY=PASS|FAIL
SKILL_POLICY=integrations/hermes/skill-policy.yaml
```

Never include secret values, cookies, auth databases, browser-state payloads, private keys, or full `.env` contents.

Before reporting completion, re-read `HERMES_RUNTIME_BASELINE.md` and this prompt line-by-line, verify every required cell with fresh evidence, fix anything safe to fix, and only then report PASS.
