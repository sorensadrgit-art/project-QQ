# Prompt 02 — Agent Browser Installation, Security, and MCP Capability

You are a senior browser-automation, endpoint-security, and agent-infrastructure engineer. Execute this prompt on the machine that will actually host interactive browser automation for Hermes and other agents. Do not assume this is the Qdrant VPS. Do not ask questions; inspect the real host, choose the safest compatible installation path, and document deviations.


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

Install or safely upgrade Vercel Labs `agent-browser`, provision its browser runtime, establish encrypted session-restore as the default authentication persistence mechanism, define a stricter optional persistent-profile mode for sites that need full Chrome state, expose a least-privilege official `agent-browser mcp` stdio server, and leave reusable verification and operating documentation for any MCP-capable agent.

## Prerequisite state

Phase 01 must already exist. Before changing anything:

1. locate `hermes-platform`;
2. read `SYSTEM_MANIFEST.yaml`, `AGENTS.md`, `SECURITY.md`, and `docs/handoffs/01-foundation.md`;
3. verify the platform repository is clean or identify pre-existing uncommitted changes and do not overwrite them;
4. confirm the `infra/agent-browser/` directory belongs to this phase.

If Phase 01 artifacts are absent, reconstruct only the missing foundation files required by this prompt from the fixed contracts above, record that repair in `DECISIONS.md`, then continue. Do not silently create a divergent structure.

## Scope boundary

**Build**

- Agent Browser CLI/browser runtime;
- exact pinned version record;
- host-local browser profile and encrypted state secret;
- source-controlled wrappers/configuration/operational docs;
- MCP stdio startup wrapper;
- CLI + MCP + session verification;
- upgrade/rollback instructions.

**Do not build**

- do not configure Hermes yet;
- do not install Qdrant;
- do not store login credentials/cookies in Git;
- do not reuse the user's everyday Chrome profile by default;
- do not automate a real financial, destructive, messaging, or account-security action during verification.

## Inspect the host

Capture evidence in `docs/handoffs/02-agent-browser.md`:

```bash
set -Eeuo pipefail
uname -a || true
command -v agent-browser || true
agent-browser --version || true
command -v node || true
node --version || true
command -v npm || true
npm --version || true
command -v chromium || command -v chromium-browser || command -v google-chrome || true
printf 'DISPLAY=%s\n' "${DISPLAY-}"
```

Also inspect the official Agent Browser installation/release source at execution time. Resolve the current stable non-prerelease version and record the source and exact version. If an existing installed version is newer than the verified stable line, do not downgrade blindly; record the discrepancy and verify compatibility.

## Installation

Prefer the official installation path supported by the host. For the normal npm path:

For the normal npm path, resolve the stable package version from npm and reject prereleases before installing:

```bash
AGENT_BROWSER_VERSION="$(npm view agent-browser version)"
case "$AGENT_BROWSER_VERSION" in
  *-*) echo "Refusing prerelease version: $AGENT_BROWSER_VERSION" >&2; exit 1 ;;
esac
npm install -g "agent-browser@$AGENT_BROWSER_VERSION"
agent-browser install
```

Cross-check that npm version against the official Agent Browser repository/release documentation and record both evidence sources.

On Linux, if browser system libraries are missing and the official CLI supports it:

```bash
agent-browser install --with-deps
```

After installation:

```bash
agent-browser --version
agent-browser doctor
```

If an existing installation is being upgraded, back up only source-controlled integration scripts/config first; browser secrets/state remain outside Git. Use the product's supported upgrade path when it preserves the desired exact version, otherwise use the package manager with the exact pin. Re-run `doctor`.

Update `SYSTEM_MANIFEST.yaml` with the observed exact version, package source, and the host identifier. Never write a floating `latest`.

## Host-local security layout

On Unix, use:

```text
$HOME/.config/hermes-platform/
├── agent-browser.env        mode 0600
├── agent-browser/
│   ├── profile/             mode 0700
│   ├── states/              mode 0700
│   └── logs/                mode 0700
```

Create the directories with `umask 077`.

Generate a 32-byte state encryption key:

```bash
umask 077
mkdir -p "$HOME/.config/hermes-platform/agent-browser/"{profile,states,logs}
openssl rand -hex 32
```

Write `AGENT_BROWSER_ENCRYPTION_KEY=` followed immediately by the generated 64-hex value into the host-local `agent-browser.env`. The produced file contains the real value; it must never enter Git or the handoff report. Set mode 0600. The source-controlled `env.example` leaves this value empty. If Agent Browser's currently documented environment-variable name differs, use the official current name and update the local wrapper plus documentation; do not invent compatibility aliases.

### Authentication persistence modes

**Default — encrypted restore session**

Use Agent Browser's stable session + `--restore --restore-save auto` workflow for authenticated continuity. Saved cookies/localStorage are encrypted at rest through `AGENT_BROWSER_ENCRYPTION_KEY`. Derive one stable session name per service/account, not one global session for every site. Example naming policy: `auth-spline-primary`, `auth-github-primary`.

Authenticated commands sharing one stable restore session must be **serialized**; do not run two independent tasks concurrently against the same session because their commands/tabs can interleave.

**Optional — full persistent Chrome profile**

Use `$HOME/.config/hermes-platform/agent-browser/profile/<service-account-slug>` only if the site demonstrably needs IndexedDB, service workers, extensions, or other state not preserved by restore sessions.

Important: `AGENT_BROWSER_ENCRYPTION_KEY` encrypts Agent Browser saved state files; it does **not** mean an entire Chrome profile directory is encrypted by Agent Browser. Treat a persistent profile as sensitive host-local browser data, mode 0700, rely on OS/full-disk encryption where appropriate, serialize access to a given profile, and never commit/copy it into Git.

Do not import the everyday personal Chrome profile automatically.

### Authentication policy

- Interactive sign-in and 2FA happen in headed mode when required.
- Prefer a dedicated account/session for automation where the service permits it.
- Prefer encrypted restore sessions over full persistent profiles.
- Never paste credentials into a shell command, Markdown, issue, log, screenshot, or source file.
- If the current Agent Browser release offers an auth vault, use it for credentials rather than plaintext scripting.
- If a site invalidates restored cookies/device state, perform a normal interactive sign-in instead of weakening browser security.

## Source-controlled files

Own only these paths in this phase:

```text
infra/agent-browser/
├── README.md
├── install.sh
├── verify.sh
├── mcp-wrapper.sh
├── env.example
└── action-policy.json
tests/e2e/
└── verify_agent_browser_mcp.py
docs/handoffs/
└── 02-agent-browser.md
```

Do not modify `integrations/hermes/`; Phase 04 owns it.

### `env.example`

It documents variable names and safe non-secret paths only. It must not contain real keys/cookies.

### `install.sh`

Make it idempotent:

- resolve or accept an exact pinned version from `SYSTEM_MANIFEST.yaml`;
- fail if the manifest still lacks a version and no explicit exact version was supplied;
- install/verify runtime;
- never print secret values;
- do not remove an existing profile.

### `mcp-wrapper.sh`

The wrapper must:

1. `set -Eeuo pipefail`;
2. set `umask 077`;
3. load `$HOME/.config/hermes-platform/agent-browser.env` without echoing it;
4. expose only the host-local encryption key/state namespace needed by the CLI; do not force one global `AGENT_BROWSER_SESSION` because callers need per-task or per-service isolation;
5. `exec agent-browser mcp --tools core`;
6. write no protocol text to stdout other than what the MCP server itself emits; diagnostics go to stderr.

Do **not** expose `state`, `network`, `debug`, `tabs`, `react`, `mobile`, or `all` in the default general-agent MCP. The official `core` profile already covers navigation, snapshots, interaction, waits, reads, screenshots, JavaScript evaluation, close, and basic tab operations, so broader profiles are not justified by the v1 requirements. Current Agent Browser documentation notes that `debug` includes powerful plugin/command capabilities, while `state` exposes cookies/auth/profile operations. If a future workflow truly needs one of these profiles, create a separately named, explicitly trusted MCP wrapper with its own risk review rather than expanding the default surface silently.

### Action policy

The action-policy schema is versioned product behavior. Inspect the installed release's current official CLI help/skill documentation and generate a syntactically valid `action-policy.json` for that exact release. The policy semantics must enforce:

- safe navigation, reads, snapshots, screenshots, scrolling, and ordinary form filling;
- block or require explicit task authorization for purchases, subscription changes, sending/posting messages, deleting data, password/security-setting changes, account recovery, uploading secret-bearing files, downloading executables, and granting browser permissions;
- deny access to host-local secret directories/files;
- restrict file upload roots to explicitly task-authorized directories;
- use domain allowlisting for fresh public/untrusted browsing sessions when supported;
- recognize that Agent Browser cannot apply the same launch-time `allowedDomains` containment to some pre-existing/profile/restore modes; authenticated restore/profile workflows therefore rely on explicit destination checks, content boundaries, action policy, and restricted upload/filesystem access instead of pretending an allowlist is active;
- keep page-derived content inside Agent Browser content boundaries so page text cannot redefine agent policy;
- cap output size.

If the installed release no longer supports an action-policy file, do not fabricate one. Replace it with the release's supported equivalent, update `README.md`, and record the decision.

## MCP verification client

Implement `tests/e2e/verify_agent_browser_mcp.py` as a real test client using the official Python MCP SDK locked in the platform dev environment.

It must:

1. spawn `infra/agent-browser/mcp-wrapper.sh` as an stdio MCP server;
2. initialize the MCP session with a 20-second connection timeout;
3. list tools;
4. assert that core browser capabilities required for navigation, snapshot/inspection, interaction, and close are discoverable;
5. close cleanly;
6. return non-zero on protocol stderr/stdout contamination, timeout, or missing tools.

Do not hard-code tool names that differ across the installed Agent Browser release without first inspecting the real tool list. Persist the observed required tool names in the handoff.

## Functional verification

Use a non-sensitive public test page such as `https://example.com`.

Run a clean session that proves:

1. open;
2. snapshot;
3. read the H1/title;
4. create a second tab or isolated session;
5. screenshot to a temporary directory;
6. close;
7. no browser state or secret was written inside the Git repository.

Also prove session isolation with two distinct session names. Verify that a new session does not see tabs from the other.

### Encrypted restore round-trip

Create a harmless stable test session with the encryption key loaded and `--restore --restore-save auto`, write a benign test cookie/localStorage marker on a local/public test origin, close the session so state is saved, then inspect the saved-state bytes only enough to prove the plaintext marker is absent. Re-open the same stable session with restore enabled and verify the benign marker was restored. Delete the temporary restore state after the test.

Also verify that two different session names remain isolated. If the installed release provides restore validation flags such as URL/text/function checks, use them so a failed restore cannot overwrite the previous known-good state.

If you test optional persistent-profile mode, document separately that its directory is sensitive but not protected by the saved-state encryption key.

### Headed/headless behavior

- If the host has a working display, run one headed smoke test and confirm a visible browser window.
- If no display exists, run the headless test and document that visibility requires a GUI/remote-desktop/display server; do not install an unnecessary GUI stack merely to satisfy this test.
- A headed login is not a CI requirement.

## Security verification

Run:

```bash
test "$(stat -c '%a' "$HOME/.config/hermes-platform/agent-browser.env")" = "600"
git -C "$PLATFORM_REPO" status --short
git -C "$PLATFORM_REPO" grep -nE 'AGENT_BROWSER_ENCRYPTION_KEY=.+' -- . ':!infra/agent-browser/env.example' && exit 1 || true
```

Adapt the `stat` command on non-GNU systems while preserving the same permission requirement.

Confirm no process arguments expose the encryption key.

## Upgrade and rollback documentation

`infra/agent-browser/README.md` must explain:

- how to inspect current version;
- how to resolve and pin a new stable version;
- how to run `doctor` and the full verification suite before accepting an upgrade;
- how to roll back to the previous exact package version;
- why browser profiles/states are backed up separately and never copied into Git;
- how any MCP-capable future agent launches `mcp-wrapper.sh`;
- how a human performs a one-time headed authentication without sharing a password with an agent.

## Tests and verification

At minimum, run and capture results:

```bash
agent-browser --version
agent-browser doctor
bash infra/agent-browser/verify.sh
uv run python tests/e2e/verify_agent_browser_mcp.py
git status --short
```

`verify.sh` must orchestrate the harmless functional tests and fail on the first broken assertion.

If a test fails, diagnose and fix the installation/config/scripts, then re-run until it passes. Do not report PASS based on package installation alone.

## Acceptance criteria

- [ ] Exact stable Agent Browser version is installed and recorded.
- [ ] `agent-browser doctor` passes.
- [ ] Encrypted restore-state directories exist outside Git with restrictive permissions; optional persistent profiles, if used, are separately documented as sensitive host-local data.
- [ ] State encryption is configured and a harmless encrypted restore round-trip is proven.
- [ ] No secret/browser state exists in Git history or current tracked files.
- [ ] Functional open/snapshot/read/screenshot/session-isolation/close test passes.
- [ ] MCP stdio initialize + tool discovery test passes.
- [ ] Action policy/current-release equivalent is valid and enforces the required risk semantics.
- [ ] Generic-agent MCP usage and upgrade/rollback are documented.
- [ ] Hermes configuration was not modified.
- [ ] `docs/handoffs/02-agent-browser.md` contains version, paths excluding secret values, verification output, and environment-specific limitations.

## Handoff

Finish with observed values:

```text
PHASE_02_STATUS=PASS
AGENT_BROWSER_VERSION=the exact observed version
AGENT_BROWSER_MCP_WRAPPER=the absolute path to mcp-wrapper.sh
AGENT_BROWSER_AUTH_MODE=RESTORE_SESSION_DEFAULT or PERSISTENT_PROFILE_REQUIRED_FOR_SPECIFIC_SITE
HEADED_TEST=PASS or NOT_AVAILABLE_NO_DISPLAY
MCP_DISCOVERY=PASS
```

Never include the encryption key, cookies, or login details in the handoff.
