# Knowledge Ingestion Checklist

Use this every time new data is added.

- [ ] Place new raw text/Markdown/PDF-derived text under `sources/{domain}/...`; do not overwrite the normalized version.
- [ ] Record or verify the source URL, source type, stable source ID, language, rights class, and SHA-256 checksum.
- [ ] Scan the source for secrets, credentials, cookies, tokens, personal data, and accidental private project material.
- [ ] Run the normalizer against only the changed/new source set.
- [ ] Review any quarantine output; quarantined sources do not proceed.
- [ ] Confirm exact product/API/control names were preserved.
- [ ] Confirm filler, duplicated transcript text, and irrelevant intros/outros were removed.
- [ ] Confirm visible-only facts were not invented from transcript text.
- [ ] Validate normalized frontmatter and required sections.
- [ ] Run chunk validation: semantic boundaries, code-block integrity, size limits, deterministic IDs.
- [ ] Run duplicate detection against the current source manifest.
- [ ] For an update, confirm the old source ID is retained unless it is intentionally a new source.
- [ ] For a deletion, confirm the source manifest deletion is intentional and covered by a retrieval regression test when high-value.
- [ ] Add or update retrieval test cases for important new concepts, exact names, and common phrasing variants.
- [ ] Run repository validation and retrieval tests locally.
- [ ] Inspect the generated ingestion report: sources accepted, quarantined, unchanged, updated, deleted, chunk counts, warnings.
- [ ] Commit raw permitted text, normalized Markdown, source manifest, and tests together.
- [ ] Push through the protected main-branch workflow.
- [ ] Confirm the VPS publish report points to the pushed Git commit.
- [ ] Confirm `knowledge_current` now resolves to the new verified collection.
- [ ] Query at least one new item through the MCP gateway and verify provenance.
- [ ] Query at least one previously known item to catch regression.
- [ ] Confirm the previous healthy Qdrant build remains available for rollback.
