# Hermes Skill Policy

This policy supplements `HERMES_RUNTIME_BASELINE.md` and is authoritative for the shared custom capability router.

## Required on both Hermes runtimes

Both Desktop Hermes and VPS Hermes must have:

- all bundled skills supplied by the selected/current Hermes release;
- safe updates for already-installed Hub skills;
- a fresh `hermes skills audit` for Hub/community skills;
- the source-controlled custom `skill-router` skill from `skills/skill-router/SKILL.md`;
- the native Hermes skill index/router functioning in a fresh session.

The custom `skill-router` is a **procedural policy skill**. It does not replace Hermes's native skill-selection mechanism. The native runtime still decides when to call `skill_view`; the custom skill tells the agent how to assess and route capabilities once selected.

## Role-specific project skills

When the later project services exist:

```text
Desktop Hermes
  skill-router
  knowledge-retrieval
  agent-browser-routing

VPS Hermes
  skill-router
  knowledge-retrieval
```

`agent-browser-routing` is Desktop-only unless Agent Browser is intentionally deployed on the VPS.

`knowledge-retrieval` must not be marked ready until the Knowledge MCP gateway exists and passes a live retrieval test.

## Source of truth

The canonical bootstrap copy of the shared router is:

```text
project-QQ/skills/skill-router/SKILL.md
```

Prompt 01/04B should copy or promote that skill into the future operational platform repository:

```text
hermes-platform/integrations/hermes/skills/skill-router/SKILL.md
```

Each host may load the operational copy through `skills.external_dirs`, or place the same reviewed content in its local Hermes skill directory when bootstrapping before `hermes-platform` exists.

## Verification

A runtime does not pass merely because `SKILL.md` exists.

Required evidence:

1. `hermes skills list` shows `skill-router` enabled.
2. The installed file hash matches the source-controlled reviewed copy.
3. An explicit preload test succeeds.
4. A fresh natural-language task that asks Hermes to choose among capabilities produces a real `skill_view("skill-router")` tool call in the session trace/export.
5. Any MCP selected by the skill is independently connection-tested.

## Security

Never put credentials, cookies, browser state, bearer tokens, SSH private keys, or Hermes auth/session databases inside a skill or Git repository.
