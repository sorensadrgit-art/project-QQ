# Hermes Dual-Runtime Baseline

This document is the mandatory runtime contract for the two Hermes installations in this project:

1. **Desktop Hermes** — the Hermes Agent/CLI runtime used by Hermes Desktop on the operator workstation.
2. **VPS Hermes** — the Hermes Agent/CLI/gateway runtime installed on the knowledge/infrastructure VPS.

The project is not runtime-complete until **both** installations satisfy this baseline.

## 1. Update policy

Both runtimes must be brought to the current supported Hermes release/update state using the installed Hermes distribution's official update mechanism. Do not infer currency from an old version string.

Required sequence on each runtime:

```text
observe install type and current version
→ create a full pre-update backup
→ hermes update --check
→ hermes update --backup
→ hermes config check
→ migrate newly required config safely if needed
→ hermes doctor
→ record hermes version
→ verify gateway/service state where applicable
```

If the two hosts use different Hermes installation channels, record both channels. Prefer converging them to the same official supported stable channel and exact release/commit when that can be done without replacing a platform-supported Desktop installation with an unsupported layout.

A runtime is **not** considered updated when:

- `hermes update --check` still reports it behind;
- `hermes doctor` has unresolved errors relevant to this project;
- config migration is incomplete;
- the running gateway/backend still points at the pre-update runtime;
- the Desktop GUI is using a different Hermes backend than the one that was updated.

On Windows, respect Hermes's running-process/venv guards. Close the Desktop/backend/gateway through supported means before retrying an update; do not bypass a real lock with destructive force flags.

## 2. Skills policy

Do **not** install every optional/community skill in existence. "All skills they must have" means all skills required by the runtime's role, plus all bundled skills shipped by its selected Hermes release.

### Both Desktop and VPS

Both runtimes must have:

- the complete bundled skill set synchronized by the current Hermes update;
- all already-installed Hub skills checked for upstream updates;
- outdated Hub skills updated unless a local modification requires review;
- all installed third-party/Hub skills re-audited with Hermes's skill security scanner;
- the source-controlled `knowledge-retrieval` project skill visible to Hermes;
- the built-in Hermes skill index/router functioning in a fresh session.

### Desktop-only required project skill

Desktop Hermes additionally requires:

- `agent-browser-routing` — routes interactive/persistent web UI work to the Agent Browser MCP server.

### VPS-only runtime expectations

VPS Hermes must have:

- `knowledge-retrieval`;
- its normal bundled Hermes self/operations skills from the installed release;
- Knowledge MCP connectivity through the private/local gateway path.

VPS Hermes does **not** require the Desktop's Agent Browser skill or MCP unless Agent Browser is intentionally installed and secured on the VPS in a separately reviewed change. Do not pretend the VPS can drive the Desktop's local browser.

## 3. Source-controlled project skill policy

Project-specific Hermes skills are source controlled under:

```text
hermes-platform/integrations/hermes/skills/
```

Hermes must load that directory through its supported external-skill mechanism, normally:

```yaml
skills:
  external_dirs:
    - /absolute/path/to/hermes-platform/integrations/hermes/skills
```

The absolute path is host-local. The skill contents remain Git-controlled.

The runtime reconciliation phase must maintain a non-secret role manifest at:

```text
hermes-platform/integrations/hermes/skill-policy.yaml
```

Contract:

```yaml
schema_version: 1
bundled:
  sync_all: true
hub:
  check_updates: true
  update_outdated: true
  audit_installed: true
roles:
  desktop:
    required_project_skills:
      - knowledge-retrieval
      - agent-browser-routing
    required_mcp_servers:
      - knowledge
      - agent_browser
  vps:
    required_project_skills:
      - knowledge-retrieval
    required_mcp_servers:
      - knowledge
```

Future project skills must be added to this manifest instead of being silently installed on one machine only.

## 4. Native skill router — what "connected" means

Hermes's skill router is part of the Hermes runtime/session prompt and skill system. It is **not** a separate network daemon and must not be replaced with an unreviewed third-party router merely to satisfy the word "router."

For this project, the native router is considered connected only when all of the following are proven on each host:

1. the required skill directory is present and configured;
2. `hermes skills list` shows every role-required skill;
3. the skill security scan does not quarantine a required skill;
4. a fresh Hermes session exposes the required skill through the skill index;
5. an explicit `/skill-name` test can load the skill;
6. a natural-language task that clearly matches the skill causes Hermes to load/use that skill without the user naming it;
7. the task then invokes the correct downstream MCP capability when the skill requires one.

Evidence for item 6 must come from the strongest trace the installed Hermes version provides: tool trace showing `skill_view`, debug/session logs, or another official runtime trace. A model merely saying "I would use the skill" is not evidence.

## 5. MCP role matrix

### Desktop Hermes

Required:

```text
knowledge     → authenticated private/HTTPS/SSH-tunneled Knowledge MCP
agent_browser → local Agent Browser MCP stdio server
```

Both must pass Hermes's supported MCP connection test and a real harmless task.

### VPS Hermes

Required:

```text
knowledge → localhost/private Knowledge MCP gateway
```

Do not register Qdrant itself as an agent MCP/tool. Qdrant remains an internal derived datastore.

## 6. Required runtime commands

Use the installed version's actual help/schema, but the current supported lifecycle includes these checks:

```bash
hermes update --check
hermes update --backup
hermes config check
hermes doctor
hermes version
hermes skills list
hermes skills check
hermes skills update
hermes skills audit
hermes mcp list
hermes mcp test knowledge
```

Desktop also requires:

```bash
hermes mcp test agent_browser
```

If an installed Hub skill has local edits, do not use `--force` blindly. Diff/review the local copy versus upstream and preserve intentional local behavior or explicitly migrate it.

## 7. Fresh-session rule

Skill changes must be tested in a new Hermes session (or with the installed version's official prompt-cache invalidation mechanism). A stale session is not valid evidence that the router sees a newly installed/updated skill.

## 8. Verification matrix

The convergence handoff must contain a table equivalent to:

| Check | Desktop | VPS |
|---|---|---|
| Hermes update check clean | PASS | PASS |
| Exact version/commit recorded | PASS | PASS |
| Config check/migration clean | PASS | PASS |
| `hermes doctor` | PASS | PASS |
| Bundled skills synchronized | PASS | PASS |
| Hub skills update check | PASS | PASS |
| Skill audit | PASS | PASS |
| Required project skills visible | PASS | PASS |
| Native router natural-language test | PASS | PASS |
| Knowledge MCP | PASS | PASS |
| Agent Browser MCP | PASS | N/A unless installed |
| Running gateway/backend uses updated runtime | N/A or PASS | PASS |
| Desktop GUI uses updated runtime | PASS | N/A |

Any unverified required cell prevents a full PASS.

## 9. Secrets and state

Never copy between hosts or commit:

```text
~/.hermes/.env values
browser cookies/storage/profile state
MCP bearer-token values
SSH private keys
provider/API credentials
Hermes auth/session databases
```

Synchronize configuration structure and skill source, not secret values or personal session databases.

## 10. Recovery

Before runtime convergence, create Hermes full backups on both machines using the supported Hermes backup/update-backup path. Record backup locations by path only, never contents.

If the update breaks a runtime, restore that host independently. Do not roll both hosts backward merely because one host failed unless the failure is proven to be an incompatible cross-runtime protocol/version contract.
