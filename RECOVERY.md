# Recovery Runbook

## Recovery principle

The canonical recovery path is **Git → rebuild → verify → alias**, not “restore an opaque database and hope it is current.”

Qdrant snapshots are acceleration/rollback artifacts. They are not the sole backup.

## Scenario A — Qdrant container/data lost, Git intact

1. Restore `hermes-platform` from Git.
2. Restore `hermes-knowledge` from Git.
3. Run Prompt 03’s infrastructure bootstrap in recovery mode.
4. Generate new Qdrant credentials; do not reuse a leaked key.
5. Start empty Qdrant and the knowledge gateway.
6. Run the full index build against the exact protected `main` Git commit.
7. Run deterministic retrieval/provenance tests.
8. Create `knowledge_current` alias only after tests pass.
9. Generate a fresh snapshot.
10. Run Hermes retrieval verification.

**Expected data loss:** none for canonical knowledge content committed to Git.

## Scenario B — Bad knowledge publish

1. Read current and retained alias targets.
2. Select most recent known-good retained collection from publish reports.
3. Run retrieval smoke tests directly against that collection.
4. Atomically switch `knowledge_current` to it.
5. Mark the bad Git commit/publish as failed in the platform operations log.
6. Fix knowledge data in Git; do not mutate the bad collection by hand.
7. Republish.

## Scenario C — Knowledge repository lost locally

Clone the private remote repository and run its validation workflow. Qdrant should not be used to reconstruct source files because normalized source/provenance detail may not be sufficient for an exact Git history reconstruction.

## Scenario D — Platform repository lost locally

Clone `hermes-platform`, read `SYSTEM_MANIFEST.yaml`, run the recovery verification script, and reapply services from source. Secrets must be restored from the chosen secret manager or regenerated.

## Scenario E — Agent Browser authentication state lost

1. Reinstall Agent Browser from the pinned/resolved version policy.
2. Recreate the encrypted restore-state directories and, only where required, any dedicated persistent-profile directory.
3. Generate a new state encryption key.
4. Perform interactive logins again in headed mode for each stable service/account restore session.
5. Re-run encrypted restore and MCP verification.
6. Do not restore browser cookies/profile data from Git; they must never be there.

## Scenario F — GitHub push trigger broken

The VPS reconciliation timer compares remote main with the active published commit. Run the reconciliation service manually and inspect its logs. Fix the GitHub trigger independently; do not bypass validation by writing directly to Qdrant.

## Mandatory recovery drill

At least once after initial setup and after any schema/embedding change:

- start from empty Qdrant storage;
- rebuild from Git;
- publish;
- run the retrieval regression suite;
- verify Hermes retrieval;
- record elapsed build time, corpus size, point count, active Git commit, and collection name.

A recovery procedure is not considered verified until this drill has succeeded.
