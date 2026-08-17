# Authoritative References

These sources were checked while hardening the plan. Execution agents must re-check current official documentation before installing or upgrading software.

## Agent Browser — Vercel Labs

- Repository: `https://github.com/vercel-labs/agent-browser`
- The official README documents global installation, `agent-browser install`, `upgrade`, `doctor`, accessibility-tree snapshots, persistent profiles, session restore, AES-256-GCM state encryption, authentication vault, content boundaries, action policy, and `agent-browser mcp`.
- The MCP server supports selectable tool profiles such as `core`, `state`, `network`, `debug`, `tabs`, `react`, and `mobile`.

## Hermes Agent — Nous Research

- Repository: `https://github.com/NousResearch/hermes-agent`
- MCP documentation: `https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/mcp.md`
- Skills documentation: `https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/skills.md`
- Hermes supports stdio and remote HTTP MCP servers through `~/.hermes/config.yaml`.
- External source-controlled skill directories are supported through `skills.external_dirs`.

## Qdrant

- Security: `https://qdrant.tech/documentation/security/`
- Installation: `https://qdrant.tech/documentation/installation/`
- Collections/aliases: `https://qdrant.tech/documentation/manage-data/collections/`
- Multitenancy: `https://qdrant.tech/documentation/tutorials/multiple-partitions/`
- Hybrid search: `https://qdrant.tech/documentation/search/text-search/hybrid-search/`
- FastEmbed: `https://qdrant.tech/documentation/fastembed/`
- Snapshots: `https://qdrant.tech/documentation/operations/snapshots/`
- Web UI: `https://qdrant.tech/documentation/web-ui/`
- Qdrant documents that self-hosted instances are insecure by default, recommends authentication/network binding/TLS, recommends payload partitioning over large numbers of small collections, and supports atomic alias changes for blue/green collection switching.

## Model Context Protocol

- Python SDK: `https://github.com/modelcontextprotocol/python-sdk`
- The official SDK recommends Streamable HTTP for deployed servers and supports stateless JSON-response FastMCP servers.

## GitHub

- Deploy keys: `https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys`
- Actions secure use: `https://docs.github.com/en/actions/reference/security/secure-use`
- GitHub recommends least-privilege secrets and immutable full commit SHA pinning for third-party Actions.
