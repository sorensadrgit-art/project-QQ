from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

PROMPTS = [
    "prompts/01_foundation_and_repo_governance.md",
    "prompts/02_agent_browser_installation_and_mcp.md",
    "prompts/03_qdrant_knowledge_platform_and_github_sync.md",
    "prompts/04_hermes_integration_and_operating_rules.md",
    "prompts/04B_dual_hermes_runtime_update_skills_and_router_convergence.md",
    "prompts/05_knowledge_ingestion_and_update_workflow.md",
]
HANDOFFS = [
    "docs/handoffs/01-foundation.md",
    "docs/handoffs/02-agent-browser.md",
    "docs/handoffs/03-qdrant-knowledge-platform.md",
    "docs/handoffs/04-hermes-integration.md",
    "docs/handoffs/04B-dual-hermes-runtime-convergence.md",
    "docs/handoffs/05-knowledge-ingestion.md",
]

REQUIRED = {
    ".gitattributes",
    ".gitignore",
    "README.md",
    "REPO_MAP.md",
    "PLAN.md",
    "ARCHITECTURE.md",
    "CONTRACTS.md",
    "DECISIONS.md",
    "EXECUTION_ORDER.md",
    "HERMES_RUNTIME_BASELINE.md",
    "KNOWLEDGE_STANDARDS.md",
    "INGESTION_CHECKLIST.md",
    "RECOVERY.md",
    "REFERENCES.md",
    "SKILL_POLICY.md",
    "VERIFICATION.md",
    "patches/README.md",
    "patches/hermes-desktop-managed-ssh.patch",
    "skills/skill-router/SKILL.md",
    "scripts/validate_project.py",
    "scripts/verify_process.py",
    "tests/test_project_contracts.py",
    ".github/workflows/validate-project.yml",
    *PROMPTS,
}
IDENTITY_MARKERS = [
    '"schema=1"',
    'f"domain={domain}"',
    'f"source_id={source_id}"',
    "f\"section={' > '.join(section_path)}\"",
    'f"content_hash={content_hash}"',
    'f"occurrence={occurrence}"',
]

SECRET_NAMES = {
    ".env",
    ".npmrc",
    ".pypirc",
    "agent-browser.env",
    "credentials.json",
    "qdrant.env",
    "gateway.env",
    "service-account.json",
    "sync.env",
    "cookies.json",
    "storage-state.json",
    "id_rsa",
    "id_ed25519",
}


def command(args: list[str], cwd: Path, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def tracked_files(root: Path) -> list[Path]:
    result = command(["git", "ls-files", "-z"], root)
    if result.returncode == 0:
        return [root / value for value in result.stdout.split("\0") if value]
    return sorted(path for path in root.rglob("*") if path.is_file() and ".git" not in path.parts)


def candidate_text_files(root: Path) -> list[Path]:
    suffixes = {
        ".cfg",
        ".ini",
        ".json",
        ".md",
        ".patch",
        ".ps1",
        ".py",
        ".sh",
        ".toml",
        ".txt",
        ".yaml",
        ".yml",
    }
    names = {".gitattributes", ".gitignore"}
    files = {
        path
        for path in root.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and "__pycache__" not in path.parts
        and (
            path.suffix.lower() in suffixes
            or path.name in names
            or path.name.endswith(".example")
        )
    }
    return sorted(files)


def load_text(path: Path, errors: list[str]) -> str:
    try:
        raw = path.read_bytes()
        if b"\x00" in raw:
            errors.append(f"NUL byte in tracked text file: {path}")
        return raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"Cannot read UTF-8 file {path}: {exc}")
        return ""


def validate_required(root: Path, errors: list[str]) -> None:
    for relative in sorted(REQUIRED):
        if not (root / relative).is_file():
            errors.append(f"Missing required file: {relative}")


def validate_prompts(root: Path, errors: list[str]) -> None:
    order = load_text(root / "EXECUTION_ORDER.md", errors)
    positions: list[int] = []
    for relative in PROMPTS:
        text = load_text(root / relative, errors)
        for section in ("Objective", "Acceptance criteria", "Handoff"):
            if not re.search(rf"(?im)^##+\s+.*{re.escape(section)}", text):
                errors.append(f"{relative}: missing section matching {section!r}")
        for section in ("Prerequisite", "Scope", "Verification"):
            if not re.search(rf"(?im)^##+\s+.*{re.escape(section)}", text):
                errors.append(f"{relative}: missing section matching {section!r}")
        if len(re.findall(r"(?m)^```", text)) % 2:
            errors.append(f"{relative}: unbalanced Markdown code fences")
        marker = f"`{relative}`"
        if marker not in order:
            errors.append(f"EXECUTION_ORDER.md: missing {marker}")
        else:
            positions.append(order.index(marker))
    if positions != sorted(positions):
        errors.append("EXECUTION_ORDER.md: prompt order is not canonical")


def role_requires(text: str, role: str, skill: str) -> bool:
    pattern = re.compile(
        rf"(?ms)^  {re.escape(role)}:\n(?P<body>.*?)(?=^  [a-z][a-z0-9_-]*:\n|^```|\Z)"
    )
    for match in pattern.finditer(text):
        body = match.group("body")
        if "required_project_skills:" in body and f"- {skill}" in body:
            return True
    return False


def validate_contracts(root: Path, errors: list[str]) -> None:
    contracts = load_text(root / "CONTRACTS.md", errors)
    for handoff in HANDOFFS:
        if handoff not in contracts:
            errors.append(f"CONTRACTS.md: missing handoff {handoff}")

    phase_one = load_text(root / PROMPTS[0], errors)
    if "uv run uv run" in phase_one:
        errors.append("Prompt 01 contains nested 'uv run uv run'")
    if "uv sync --frozen" not in phase_one:
        errors.append("Prompt 01 verification does not use the committed lockfile")
    if "uv run python scripts/validate_repository.py" not in phase_one:
        errors.append("Prompt 01 verification does not execute through uv")
    if "|TODO|TBD|FIXME" in phase_one:
        errors.append("Prompt 01 contains a self-matching broad placeholder grep")

    phase_two = load_text(root / PROMPTS[1], errors)
    secure_generation = (
        "printf 'AGENT_BROWSER_ENCRYPTION_KEY='" in phase_two
        and "openssl rand -hex 32" in phase_two
        and '} >"$tmp"' in phase_two
    )
    if not secure_generation:
        errors.append("Prompt 02 does not redirect browser-key generation to a protected file")
    for marker in ("mktemp", ">\"$tmp\"", "chmod 0600", "mv -f"):
        if marker not in phase_two:
            errors.append(f"Prompt 02 atomic secret creation missing {marker!r}")

    decisions = load_text(root / "DECISIONS.md", errors)
    if "this five-prompt scope" in decisions:
        errors.append("DECISIONS.md still describes the current process as five prompts")

    for relative in (
        "KNOWLEDGE_STANDARDS.md",
        "PLAN.md",
        PROMPTS[2],
        PROMPTS[5],
    ):
        text = load_text(root / relative, errors)
        if 'canonical_identity = "\\n".join(' not in text:
            errors.append(f"{relative}: missing exact canonical chunk identity construction")
        for marker in IDENTITY_MARKERS:
            if marker not in text:
                errors.append(f"{relative}: missing chunk identity marker {marker}")


def validate_patch(root: Path, hermes_source: Path | None, errors: list[str]) -> None:
    patch_path = root / "patches/hermes-desktop-managed-ssh.patch"
    patch = load_text(patch_path, errors)
    base = re.search(r"(?m)^# Base commit: ([0-9a-f]{40})$", patch)
    target = re.search(r"(?m)^# Target path: (\S+)$", patch)
    if base is None:
        errors.append("Managed SSH patch has no exact Base commit metadata")
    if target is None:
        errors.append("Managed SSH patch has no Target path metadata")
    if re.search(r"(?m)^@@$", patch):
        errors.append("Managed SSH patch contains a bare invalid hunk header")
    if not re.search(r"(?m)^@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@", patch):
        errors.append("Managed SSH patch contains no valid unified-diff hunk")

    parsed = command(["git", "apply", "--numstat", str(patch_path)], root)
    if parsed.returncode != 0:
        errors.append(f"Managed SSH patch is not parseable: {parsed.stderr.strip()}")
    elif target is not None and target.group(1) not in parsed.stdout:
        errors.append("Managed SSH patch changes an unexpected target")

    for marker in (
        "function desktopSshExecutable()",
        "function spawnDesktopSsh(command, args, options)",
        "spawnFn: spawnDesktopSsh",
        "desktopSshExecutable(),",
        "System32', 'OpenSSH', 'ssh.exe'",
    ):
        if marker not in patch:
            errors.append(f"Managed SSH patch missing required behavior: {marker}")
    if patch.count("spawnFn: spawnDesktopSsh") < 3:
        errors.append("Managed SSH patch does not cover all SSH spawn boundaries")

    readme = load_text(root / "patches/README.md", errors)
    readme_base = re.search(r"(?m)^Base commit: `([0-9a-f]{40})`$", readme)
    readme_hash = re.search(r"(?m)^Patch SHA-256: `([0-9a-f]{64})`$", readme)
    if base is not None and (readme_base is None or readme_base.group(1) != base.group(1)):
        errors.append("Patch README base commit does not match patch metadata")
    digest = hashlib.sha256(patch_path.read_bytes()).hexdigest()
    if readme_hash is None or readme_hash.group(1) != digest:
        errors.append("Patch README SHA-256 does not match patch bytes")

    if hermes_source is None or base is None or target is None:
        return
    source_status = command(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        hermes_source,
    )
    if source_status.returncode != 0:
        errors.append(f"Cannot inspect Hermes source status: {source_status.stderr.strip()}")
        return
    if source_status.stdout.strip():
        errors.append("Hermes source checkout is not clean")
        return
    observed = command(["git", "rev-parse", "HEAD"], hermes_source)
    if observed.returncode != 0:
        errors.append(f"Cannot inspect Hermes source: {observed.stderr.strip()}")
        return
    if observed.stdout.strip() != base.group(1):
        errors.append(
            f"Hermes source HEAD {observed.stdout.strip()} does not match declared patch base {base.group(1)}"
        )
    if not (hermes_source / target.group(1)).is_file():
        errors.append(f"Hermes patch target missing: {target.group(1)}")
    applied = command(
        ["git", "apply", "--check", "--whitespace=error-all", str(patch_path)],
        hermes_source,
    )
    if applied.returncode != 0:
        errors.append(f"Managed SSH patch does not apply: {applied.stderr.strip()}")


def validate_architecture(root: Path, errors: list[str]) -> None:
    text = load_text(root / "ARCHITECTURE.md", errors)
    required = (
        "knowledge_v1_YYYYMMDDTHHMMSSZ_GIT12",
        '"query": "string, 2..4000 characters"',
        '"top_k": 8',
        '"domains": []',
        '"source_types": []',
        '"rights": []',
        '"language": null',
        '"schema_version": 1',
        '"active_collection"',
        '"active_repo_commit"',
        '"source_id"',
        '"rights"',
        "top_k > 12 is rejected",
        "verified_staging",
        "failed_post_switch",
        "canonical Phase 03 indexer planner",
    )
    for marker in required:
        if marker not in text:
            errors.append(f"ARCHITECTURE.md: missing contract marker {marker!r}")
    if "knowledge_v1_4f39c21a" in text:
        errors.append("ARCHITECTURE.md: stale versioned collection example")
    if '"include_content"' in text:
        errors.append("ARCHITECTURE.md: unsupported knowledge_search include_content field")
    if "clamped to 1..12" in text:
        errors.append("ARCHITECTURE.md: top_k must be rejected, not clamped")


def validate_skill_policy(root: Path, errors: list[str]) -> None:
    for relative in (
        "HERMES_RUNTIME_BASELINE.md",
        PROMPTS[4],
    ):
        text = load_text(root / relative, errors)
        for role in ("desktop", "vps"):
            if not role_requires(text, role, "skill-router"):
                errors.append(f"{relative}: {role} role does not require skill-router")

    phase_four = load_text(root / PROMPTS[3], errors)
    phase_four_b = load_text(root / PROMPTS[4], errors)
    operational = "hermes-platform/integrations/hermes/skills/skill-router/SKILL.md"
    bootstrap = "project-QQ/skills/skill-router/SKILL.md"
    for relative, text in ((PROMPTS[3], phase_four), (PROMPTS[4], phase_four_b)):
        if operational not in text:
            errors.append(f"{relative}: missing operational skill-router path")
        if bootstrap not in text:
            errors.append(f"{relative}: missing bootstrap skill-router path")
    if "SHA-256" not in phase_four or "byte-identical" not in phase_four:
        errors.append("Prompt 04 does not require deterministic skill-router promotion")
    if "source_hash != target_hash" not in phase_four_b:
        errors.append("Prompt 04B does not verify skill-router promotion hashes")

    skill = load_text(root / "skills/skill-router/SKILL.md", errors)
    if not skill.startswith("---\n"):
        errors.append("skill-router SKILL.md must begin with YAML frontmatter")
    for marker in ("name: skill-router", "version:", "platforms:"):
        if marker not in skill:
            errors.append(f"skill-router SKILL.md missing {marker!r}")
    description = re.search(r'(?m)^description:\s*"([^"]+)"$', skill)
    if description is None:
        errors.append("skill-router SKILL.md has no quoted description")
    elif len(description.group(1)) > 120:
        errors.append("skill-router description exceeds 120 characters")


def validate_inventory(root: Path, errors: list[str]) -> None:
    required_mentions = (
        ".gitattributes",
        ".gitignore",
        "SKILL_POLICY.md",
        "skills/skill-router/SKILL.md",
        "patches/hermes-desktop-managed-ssh.patch",
        "patches/README.md",
        "scripts/validate_project.py",
        "scripts/verify_process.py",
        ".github/workflows/validate-project.yml",
    )
    for relative in ("README.md", "REPO_MAP.md"):
        text = load_text(root / relative, errors)
        for marker in required_mentions:
            if marker not in text:
                errors.append(f"{relative}: inventory missing {marker}")

    verification = load_text(root / "VERIFICATION.md", errors)
    for marker in (
        "python scripts/validate_project.py",
        "python -m unittest discover -s tests -v",
        "python scripts/verify_process.py",
    ):
        if marker not in verification:
            errors.append(f"VERIFICATION.md: missing current command {marker!r}")


def validate_markdown(root: Path, errors: list[str]) -> None:
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for path in sorted(root.rglob("*.md")):
        if ".git" in path.parts:
            continue
        relative = path.relative_to(root).as_posix()
        text = load_text(path, errors)
        if "\ufffd" in text:
            errors.append(f"{relative}: contains Unicode replacement characters")
        if len(re.findall(r"(?m)^```", text)) % 2:
            errors.append(f"{relative}: unbalanced Markdown code fences")
        for target in link_pattern.findall(text):
            clean = target.split("#", 1)[0].strip()
            if not clean or clean.startswith(("http://", "https://", "mailto:", "#")):
                continue
            resolved = (path.parent / clean).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                errors.append(f"{relative}: local link escapes repository: {target}")
                continue
            if not resolved.exists():
                errors.append(f"{relative}: broken local Markdown link: {target}")


def validate_text_safety(root: Path, errors: list[str]) -> None:
    conflict = re.compile(r"(?m)^(<<<<<<<|=======|>>>>>>>)")
    populated_secret = re.compile(
        r"(?im)(?:^|\bexport\s+|[\"'])(?:AGENT_BROWSER_ENCRYPTION_KEY|"
        r"KNOWLEDGE_MCP_BEARER_TOKEN|QDRANT_API_KEY|QDRANT_ADMIN_KEY)"
        r"(?:[\"'])?\s*[:=]\s*(?:[\"'])?"
        r"(?:[0-9a-f]{32,}|[A-Za-z0-9+/_-]{40,}={0,2})"
        r"(?:[\"'])?"
    )
    private_material = re.compile(
        r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----\s*\n"
        r"[A-Za-z0-9+/=]{32,}"
    )
    for path in candidate_text_files(root):
        relative = path.relative_to(root).as_posix()
        text = load_text(path, errors)
        if path.suffix.lower() != ".patch":
            for line_number, line in enumerate(text.splitlines(), start=1):
                if line.endswith((" ", "\t")):
                    errors.append(f"{relative}:{line_number}: trailing whitespace")
        if conflict.search(text):
            errors.append(f"{relative}: unresolved merge conflict marker")
        if populated_secret.search(text):
            errors.append(f"{relative}: populated secret assignment detected")
        if private_material.search(text):
            errors.append(f"{relative}: private key material detected")

    for path in tracked_files(root):
        relative = path.relative_to(root).as_posix()
        secret_name = path.name in SECRET_NAMES or (
            path.name.endswith(".env") and not path.name.endswith(".env.example")
        )
        if secret_name:
            errors.append(f"Tracked secret-class filename: {relative}")
        if path.suffix.lower() in {".pem", ".p12", ".pfx"}:
            errors.append(f"Tracked credential file extension: {relative}")
        if "__pycache__" in path.parts or path.suffix.lower() in {".pyc", ".pyo"}:
            errors.append(f"Tracked Python cache artifact: {relative}")


def validate_workflow(root: Path, errors: list[str]) -> None:
    text = load_text(root / ".github/workflows/validate-project.yml", errors)
    if not re.search(r"(?m)^permissions:\s*\n\s+contents:\s*read\s*$", text):
        errors.append("Validation workflow must grant only contents: read")
    if "timeout-minutes:" not in text:
        errors.append("Validation workflow has no job timeout")
    if "persist-credentials: false" not in text:
        errors.append("Validation workflow must disable persisted checkout credentials")
    if "7cae03b8c02542ca2a9b95d7cd3c02b71010f796" not in text:
        errors.append("Validation workflow does not pin the Hermes patch base")
    uses = re.findall(r"(?m)^\s*-?\s*uses:\s*([^\s#]+)", text)
    if not uses:
        errors.append("Validation workflow contains no action steps")
    for action in uses:
        if action.startswith("./"):
            continue
        if "@" not in action or not re.fullmatch(r"[0-9a-f]{40}", action.rsplit("@", 1)[1]):
            errors.append(f"Validation workflow action is not full-SHA pinned: {action}")


def validate_project(root: Path, hermes_source: Path | None = None) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    validate_required(root, errors)
    if errors:
        return sorted(set(errors))
    validate_prompts(root, errors)
    validate_contracts(root, errors)
    validate_architecture(root, errors)
    validate_skill_policy(root, errors)
    validate_patch(root, hermes_source, errors)
    validate_inventory(root, errors)
    validate_markdown(root, errors)
    validate_text_safety(root, errors)
    validate_workflow(root, errors)
    return sorted(set(errors))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the project-QQ control repository")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--hermes-source",
        type=Path,
        default=Path(os.environ["HERMES_SOURCE"]) if os.environ.get("HERMES_SOURCE") else None,
        help="Clean Hermes checkout at the exact patch base commit",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    hermes_source = args.hermes_source.resolve() if args.hermes_source else None
    if not root.is_dir():
        print(f"ERROR: repository root does not exist: {root}", file=sys.stderr)
        return 2
    if hermes_source is not None and not hermes_source.is_dir():
        print(f"ERROR: Hermes source does not exist: {hermes_source}", file=sys.stderr)
        return 2
    try:
        errors = validate_project(root, hermes_source)
    except subprocess.TimeoutExpired as exc:
        print(f"ERROR: validation command timed out: {exc.cmd}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"PROJECT_QQ_VALIDATION=FAIL issues={len(errors)}", file=sys.stderr)
        return 1
    print("PROJECT_QQ_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
