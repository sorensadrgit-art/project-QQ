# Hermes Desktop Managed SSH Compatibility Patch

Base commit: `7cae03b8c02542ca2a9b95d7cd3c02b71010f796`

Patch SHA-256: `969c57a9d59be2df80914510795c8a3843746801b33005ddb5876d5da98255a9`

Target repository: `https://github.com/NousResearch/hermes-agent`

Target path: `apps/desktop/electron/main.ts`

## Purpose

On Windows, prefer the SSH executable installed with the Hermes-managed Git runtime at `<HERMES_HOME>/git/usr/bin/ssh.exe`. Preserve Windows System OpenSSH as the fallback when the managed executable is absent.

The patch covers every Desktop SSH launch path present at the recorded base:

- effective SSH configuration fingerprinting;
- pooled `SshConnection` commands;
- connection-test and profile-inventory probes;
- SSH config resolution;
- interactive remote terminal spawning.

## Application gate

This is a compatibility patch, not a permanent Hermes fork and not part of the normal Phase 04/04B path. Before applying:

1. update or fetch the official Hermes repository;
2. check whether upstream already selects the managed Windows SSH executable;
3. use a clean isolated worktree at the recorded base commit;
4. run `git apply --check` and stop if any hunk no longer applies;
5. apply the patch only after its recorded SHA-256 matches;
6. run the upstream Desktop typecheck and focused linter before integration.

```bash
BASE=7cae03b8c02542ca2a9b95d7cd3c02b71010f796
PATCH=/absolute/path/to/project-QQ/patches/hermes-desktop-managed-ssh.patch

[ "$(git rev-parse HEAD)" = "$BASE" ]
printf '%s  %s\n' \
  969c57a9d59be2df80914510795c8a3843746801b33005ddb5876d5da98255a9 \
  "$PATCH" | sha256sum --check
git apply --check --whitespace=error-all "$PATCH"
git apply "$PATCH"
npm ci --ignore-scripts --no-audit --no-fund
npm --prefix apps/desktop run typecheck
(
  cd apps/desktop
  ../../node_modules/.bin/eslint electron/main.ts
)
```

If the selected Hermes revision differs from the recorded base, do not force the patch. Rebase it from fresh upstream source, rerun the same checks, and update both the base and checksum evidence.

### Windows PowerShell equivalent

Run from a clean Hermes checkout at the recorded base:

```powershell
$ErrorActionPreference = 'Stop'
$Base = '7cae03b8c02542ca2a9b95d7cd3c02b71010f796'
$ExpectedHash = '969c57a9d59be2df80914510795c8a3843746801b33005ddb5876d5da98255a9'
$Patch = (Resolve-Path 'C:\absolute\path\to\project-QQ\patches\hermes-desktop-managed-ssh.patch').Path

if ((git rev-parse HEAD).Trim() -ne $Base) {
  throw 'Hermes checkout does not match the recorded patch base.'
}
$ObservedHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Patch).Hash.ToLowerInvariant()
if ($ObservedHash -ne $ExpectedHash) {
  throw 'Managed-SSH patch checksum mismatch.'
}

git apply --check --whitespace=error-all -- $Patch
if ($LASTEXITCODE -ne 0) { throw 'Patch apply check failed.' }
git apply -- $Patch
if ($LASTEXITCODE -ne 0) { throw 'Patch application failed.' }

npm.cmd ci --ignore-scripts --no-audit --no-fund
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
npm.cmd --prefix apps\desktop run typecheck
if ($LASTEXITCODE -ne 0) { throw 'Desktop typecheck failed.' }
Push-Location apps\desktop
try {
  & ..\..\node_modules\.bin\eslint.cmd electron\main.ts
  if ($LASTEXITCODE -ne 0) { throw 'Focused Desktop lint failed.' }
} finally {
  Pop-Location
}
```
