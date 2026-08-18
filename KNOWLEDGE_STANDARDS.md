# Knowledge Standards v1

## Purpose

Turn raw official documentation, tutorial transcripts, and reusable community techniques into compact, attributable, high-retrieval-quality Markdown. This standard applies before Qdrant indexing.

## Source classes

### `official_doc`

Primary vendor documentation or reference material.

Preserve exact names for controls, APIs, settings, state names, event names, commands, parameters, and constraints.

### `official_tutorial`

Official video/tutorial content.

The transcript alone is not enough when meaning depends on visible UI actions. When frames/screenshots are available and permitted, extract the visible control names and state transitions into the normalized procedure. Never invent unseen settings.

### `community_pattern`

A reusable technique abstracted from a public community design/project.

Store the reusable mechanism, not a wholesale clone. Record the original public reference. Do not store private/remixed assets, credentials, or redistributed project files unless rights clearly allow it.

### `internal`

Original notes, patterns, and project procedures owned by the user/team.

## Raw-source rules

1. Keep raw text separate from normalized output.
2. Do not modify raw files in place.
3. Do not commit raw binary video.
4. Every source needs a stable `source_id`.
5. Compute a SHA-256 checksum before transformation.
6. Record a URL when one exists.
7. Record a rights classification.
8. If rights are unclear and the content is not owned, normalize only a technique/summary and mark `restricted_summary_only`.
9. Secrets, cookies, tokens, personal data, and credentials are rejected before commit.

## Cleaning rules

Remove:

- filler and false starts that add no meaning;
- sponsor/intro/outro material unrelated to the technique;
- repeated transcript fragments;
- timestamps when they do not carry procedural meaning;
- speech-to-text artifacts;
- navigation chrome that is unrelated to the documented operation.

Preserve:

- exact product terminology;
- prerequisites;
- order-dependent actions;
- parameter values;
- units;
- keyboard modifiers;
- state/event relationships;
- code;
- warnings;
- exceptions;
- limitations;
- version-specific behavior;
- visible UI labels that were actually observed.

Do not “improve” uncertain facts. Mark uncertainty in source notes and quarantine the item from publication if the uncertainty affects correctness.

## Normalized document structure

Every normalized Markdown document starts with YAML frontmatter:

```yaml
schema_version: 1
source_id: spline-doc-states
domain: spline
source_type: official_doc
title: States
source_url: null
language: en
rights: public_reference
tags:
  - animation
  - states
source_checksum_sha256: 4f5cbb650336a651a7d4b9f9169b56b67793419449e26763a7fab3f9f80ee147
```

The checksum above is a schema-format example only. Actual normalized documents must use the SHA-256 of their real source revision. When no source URL exists, use `null`; never fabricate a source URL.

Body structure:

```markdown
# Title

## Purpose
One compact explanation of what the concept does and when it is used.

## Prerequisites
Only real prerequisites.

## Core concepts
Precise definitions.

## Procedure
Ordered implementation steps where the source is procedural.

## Settings and parameters
Exact controls and their effects.

## Failure modes and gotchas
Specific failures, symptoms, causes, and fixes.

## Reusable patterns
Generalizable combinations or recipes.

## Source notes
Version/date/context limitations that affect interpretation.
```

Omit body sections that truly do not apply; do not create empty headings.

## Transcript transformation

For tutorial transcripts:

1. reconstruct topic boundaries;
2. combine repeated explanations;
3. convert narration into imperative procedure only when the source actually demonstrates a procedure;
4. retain why a step is performed when the source explains it;
5. explicitly distinguish “speaker preference” from “product requirement”;
6. when UI visuals are available, merge confirmed UI labels/actions into the step;
7. never infer a numeric setting solely from a visual unless it is readable.

## Community-technique extraction

Capture:

- visual/mechanical goal;
- objects/features involved;
- state machine or event flow;
- animation timing/trigger relationships;
- reusable construction sequence;
- constraints;
- what is project-specific and intentionally excluded;
- original public reference;
- rights/provenance classification.

Do not describe a screenshot as proof of hidden scene structure. Hidden object/state/event structure must come from inspectable public project data or be labeled as an inference and excluded from authoritative procedural chunks.

## Chunking contract

Chunk after normalization.

- semantic/heading boundaries first;
- target normalized content around 350 model tokens;
- 80-token soft minimum when the concept can stand alone;
- 420-token hard normalized-content ceiling;
- the complete dense embedding input, including the `passage:` + title/domain/section prefix, must never exceed 500 model tokens;
- maximum 60-token overlap;
- avoid splitting a numbered sequence where later steps depend on earlier steps;
- if a fenced code block exceeds the dynamic token budget, split it at safe blank-line/function/statement boundaries, re-fence each fragment, and add deterministic part context; never rely on tokenizer truncation;
- prepend `passage:` + title + section path + domain only to document embedding text;
- prepend `query:` to query embedding text;
- canonical chunk payload stores clean Markdown without artificial repetition.

## Chunk identity

```python
canonical_identity = "\n".join(
    [
        "schema=1",
        f"domain={domain}",
        f"source_id={source_id}",
        f"section={' > '.join(section_path)}",
        f"content_hash={content_hash}",
        f"occurrence={occurrence}",
    ]
)
chunk_id = hashlib.sha256(canonical_identity.encode("utf-8")).hexdigest()
```

The algorithm is deterministic and deliberately excludes source checksum and repository path. An unchanged chunk under the same `source_id` and section keeps its ID across source revisions and path refactors. If identical canonical content appears more than once in the same section, assign a zero-based occurrence index in document order so identities remain unique and deterministic. Moving a chunk to a different semantic section or changing its canonical content creates a new ID; the next full blue/green publish removes the old point.

## Metadata validation

Reject publication when:

- required field missing;
- slug contains uppercase or spaces;
- checksum malformed;
- source URL uses a non-HTTPS scheme except `null`;
- `rights` is not an allowed enum;
- an indexable schema-v1 normalized document has `language` other than `en`; non-English material must be quarantined or wait for a schema/model migration;
- content is empty;
- a chunk exceeds the hard maximum without an indivisible-block exception;
- a referenced source file does not exist;
- source manifest and normalized frontmatter disagree.

## Quality rubric

A normalized source passes only when all are true:

- technically faithful;
- one concept/procedure per major section;
- exact nouns preserved;
- no transcript filler;
- no invented steps/settings;
- provenance present;
- rights class present;
- duplicate detection complete;
- chunk boundaries coherent;
- retrieval regression case exists for a high-value source;
- generated report lists warnings and transformations.
