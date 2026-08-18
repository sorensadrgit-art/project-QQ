from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_TIMEOUT_SECONDS = 180
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

IDENTITY_MARKERS = [
    '"schema=1"',
    'f"domain={domain}"',
    'f"source_id={source_id}"',
    "f\"section={' > '.join(section_path)}\"",
    'f"content_hash={content_hash}"',
    'f"occurrence={occurrence}"',
]
IDENTITY_FILES = [
    "KNOWLEDGE_STANDARDS.md",
    "PLAN.md",
    "prompts/03_qdrant_knowledge_platform_and_github_sync.md",
    "prompts/05_knowledge_ingestion_and_update_workflow.md",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class ProjectContractTests(unittest.TestCase):
    def test_six_prompt_files_exist_in_execution_order(self) -> None:
        order = read("EXECUTION_ORDER.md")
        positions: list[int] = []
        for prompt in PROMPTS:
            self.assertTrue((ROOT / prompt).is_file(), prompt)
            positions.append(order.index(f"`{prompt}`"))
        self.assertEqual(positions, sorted(positions))

    def test_every_prompt_has_operational_sections_and_balanced_fences(self) -> None:
        required = ("Objective", "Acceptance criteria", "Handoff")
        for prompt in PROMPTS:
            text = read(prompt)
            self.assertEqual(text.count("``` "), 0, prompt)
            self.assertEqual(
                len(re.findall(r"^```", text, re.MULTILINE)) % 2,
                0,
                prompt,
            )
            for section in required:
                self.assertRegex(
                    text,
                    rf"(?im)^##+\s+.*{re.escape(section)}",
                    f"{prompt}: {section}",
                )

    def test_phase_one_validator_command_is_not_nested(self) -> None:
        text = read("prompts/01_foundation_and_repo_governance.md")
        self.assertNotIn("uv run uv run", text)
        self.assertIn(
            "uv run python scripts/validate_repository.py --platform PATH --knowledge PATH",
            text,
        )

    def test_contracts_register_every_handoff(self) -> None:
        contracts = read("CONTRACTS.md")
        for handoff in HANDOFFS:
            self.assertIn(handoff, contracts)

    def test_chunk_identity_contract_is_exact_and_shared(self) -> None:
        for path in IDENTITY_FILES:
            text = read(path)
            for marker in IDENTITY_MARKERS:
                self.assertIn(marker, text, f"{path}: missing {marker}")
            self.assertIn(
                'canonical_identity = "\\n".join(',
                text,
                f"{path}: canonical construction missing",
            )

    def test_scope_language_matches_six_prompt_process(self) -> None:
        self.assertNotIn("this five-prompt scope", read("DECISIONS.md"))
        self.assertIn("six-prompt", read("DECISIONS.md"))

    def test_managed_ssh_patch_is_a_valid_unified_diff(self) -> None:
        patch = read("patches/hermes-desktop-managed-ssh.patch")
        self.assertRegex(patch, r"(?m)^# Base commit: [0-9a-f]{40}$")
        self.assertRegex(patch, r"(?m)^# Target path: apps/desktop/electron/main\.ts$")
        self.assertNotRegex(patch, r"(?m)^@@$")
        self.assertRegex(
            patch,
            r"(?m)^@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@",
        )

    def test_managed_ssh_patch_applies_to_declared_base_when_available(self) -> None:
        source = os.environ.get("HERMES_SOURCE")
        if not source:
            self.skipTest("HERMES_SOURCE is not set")
        result = subprocess.run(
            [
                "git",
                "-C",
                source,
                "apply",
                "--check",
                str(ROOT / "patches/hermes-desktop-managed-ssh.patch"),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_validator_rejects_dirty_hermes_patch_source(self) -> None:
        source_value = os.environ.get("HERMES_SOURCE")
        if not source_value:
            self.skipTest("HERMES_SOURCE is not set")
        source = Path(source_value)
        sentinel = source / "PROJECT_QQ_VALIDATOR_DIRTY_SENTINEL"
        self.assertFalse(sentinel.exists())
        sentinel.write_text("dirty\n", encoding="utf-8")
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/validate_project.py"),
                    "--root",
                    str(ROOT),
                    "--hermes-source",
                    str(source),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=VALIDATOR_TIMEOUT_SECONDS,
            )
        finally:
            sentinel.unlink(missing_ok=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Hermes source checkout is not clean", result.stderr)

    def test_validator_exists_and_accepts_clean_repository(self) -> None:
        validator = ROOT / "scripts/validate_project.py"
        self.assertTrue(validator.is_file(), validator)
        result = subprocess.run(
            [sys.executable, str(validator), "--root", str(ROOT)],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertIn("PROJECT_QQ_VALIDATION=PASS", result.stdout)

    def test_ci_uses_only_full_sha_pinned_actions(self) -> None:
        workflow = ROOT / ".github/workflows/validate-project.yml"
        self.assertTrue(workflow.is_file(), workflow)
        text = workflow.read_text(encoding="utf-8")
        uses = re.findall(r"(?m)^\s*-?\s*uses:\s*([^\s#]+)", text)
        self.assertGreaterEqual(len(uses), 1)
        for value in uses:
            if value.startswith("./"):
                continue
            self.assertRegex(value, r"^[^@]+@[0-9a-f]{40}$", value)
        self.assertIn(
            "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1",
            text,
        )

    def test_skill_router_frontmatter_is_bounded(self) -> None:
        text = read("skills/skill-router/SKILL.md")
        self.assertTrue(text.startswith("---\n"))
        match = re.search(r'(?m)^description:\s*"([^"]+)"$', text)
        self.assertIsNotNone(match)
        assert match is not None
        self.assertLessEqual(len(match.group(1)), 120)

    def test_patch_checkout_preserves_lf_bytes(self) -> None:
        attributes = read(".gitattributes")
        self.assertIn("*.patch text eol=lf", attributes)
        self.assertIn("*.py text eol=lf", attributes)
        self.assertIn("*.yml text eol=lf", attributes)

    def test_patch_readme_matches_patch_bytes_and_base(self) -> None:
        patch_path = ROOT / "patches/hermes-desktop-managed-ssh.patch"
        patch = patch_path.read_text(encoding="utf-8")
        readme = read("patches/README.md")
        base = re.search(r"(?m)^# Base commit: ([0-9a-f]{40})$", patch)
        documented_base = re.search(r"(?m)^Base commit: `([0-9a-f]{40})`$", readme)
        documented_hash = re.search(r"(?m)^Patch SHA-256: `([0-9a-f]{64})`$", readme)
        self.assertIsNotNone(base)
        self.assertIsNotNone(documented_base)
        self.assertIsNotNone(documented_hash)
        assert base is not None and documented_base is not None and documented_hash is not None
        self.assertEqual(base.group(1), documented_base.group(1))
        self.assertEqual(hashlib.sha256(patch_path.read_bytes()).hexdigest(), documented_hash.group(1))

    def test_knowledge_search_contract_is_exact(self) -> None:
        text = read("ARCHITECTURE.md")
        for marker in (
            '"query": "string, 2..4000 characters"',
            '"rights": []',
            '"language": null',
            '"schema_version": 1',
            "top_k > 12 is rejected",
        ):
            self.assertIn(marker, text)
        self.assertNotIn('"include_content"', text)
        self.assertNotIn("clamped to 1..12", text)

    def test_skill_router_is_required_by_both_roles(self) -> None:
        for path in (
            "HERMES_RUNTIME_BASELINE.md",
            "prompts/04B_dual_hermes_runtime_update_skills_and_router_convergence.md",
        ):
            text = read(path)
            desktop = re.search(r"(?ms)^  desktop:\n(.*?)(?=^  vps:)", text)
            vps = re.search(r"(?ms)^  vps:\n(.*?)(?=^```)", text)
            self.assertIsNotNone(desktop, path)
            self.assertIsNotNone(vps, path)
            assert desktop is not None and vps is not None
            self.assertIn("- skill-router", desktop.group(1), path)
            self.assertIn("- skill-router", vps.group(1), path)

    def test_browser_key_generation_is_redirected_and_atomic(self) -> None:
        text = read("prompts/02_agent_browser_installation_and_mcp.md")
        self.assertIn("openssl rand -hex 32", text)
        self.assertIn('} >"$tmp"', text)
        self.assertIn("mktemp", text)
        self.assertIn("chmod 0600", text)
        self.assertIn("mv -f", text)

    def test_validator_rejects_contract_drift(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-qq-validator-") as temp:
            copy = Path(temp) / "project-QQ"
            shutil.copytree(
                ROOT,
                copy,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
            )
            architecture = copy / "ARCHITECTURE.md"
            text = architecture.read_text(encoding="utf-8")
            architecture.write_text(
                text.replace(
                    '"query": "string, 2..4000 characters"',
                    '"query": "string, 1..4000 characters"',
                    1,
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(copy / "scripts/validate_project.py"), "--root", str(copy)],
                check=False,
                capture_output=True,
                text=True,
                timeout=VALIDATOR_TIMEOUT_SECONDS,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ARCHITECTURE.md", result.stderr)

    def test_validator_rejects_missing_required_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-qq-missing-") as temp:
            copy = Path(temp) / "project-QQ"
            shutil.copytree(
                ROOT,
                copy,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
            )
            (copy / "CONTRACTS.md").unlink()
            result = subprocess.run(
                [sys.executable, str(copy / "scripts/validate_project.py"), "--root", str(copy)],
                check=False,
                capture_output=True,
                text=True,
                timeout=VALIDATOR_TIMEOUT_SECONDS,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing required file: CONTRACTS.md", result.stderr)

    def test_validator_rejects_populated_secret_assignment(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-qq-secret-") as temp:
            copy = Path(temp) / "project-QQ"
            shutil.copytree(
                ROOT,
                copy,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
            )
            fixture = copy / "secret-fixture.json"
            fixture.write_text(
                '{"KNOWLEDGE_MCP_BEARER_TOKEN":"' + ("a" * 64) + '"}\n',
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(copy / "scripts/validate_project.py"), "--root", str(copy)],
                check=False,
                capture_output=True,
                text=True,
                timeout=VALIDATOR_TIMEOUT_SECONDS,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("populated secret assignment detected", result.stderr)

    def test_validator_rejects_exported_secret_assignment(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-qq-export-secret-") as temp:
            copy = Path(temp) / "project-QQ"
            shutil.copytree(
                ROOT,
                copy,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
            )
            fixture = copy / "secret-fixture.sh"
            fixture.write_text(
                "export QDRANT_ADMIN_KEY=" + ("c" * 64) + "\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(copy / "scripts/validate_project.py"), "--root", str(copy)],
                check=False,
                capture_output=True,
                text=True,
                timeout=VALIDATOR_TIMEOUT_SECONDS,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("populated secret assignment detected", result.stderr)

    def test_validator_rejects_populated_secret_in_example_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-qq-env-example-") as temp:
            copy = Path(temp) / "project-QQ"
            shutil.copytree(
                ROOT,
                copy,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
            )
            fixture = copy / "agent-browser.env.example"
            fixture.write_text(
                "AGENT_BROWSER_ENCRYPTION_KEY=" + ("b" * 64) + "\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(copy / "scripts/validate_project.py"), "--root", str(copy)],
                check=False,
                capture_output=True,
                text=True,
                timeout=VALIDATOR_TIMEOUT_SECONDS,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("populated secret assignment detected", result.stderr)

    def test_validator_rejects_secret_class_filename(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-qq-env-file-") as temp:
            copy = Path(temp) / "project-QQ"
            shutil.copytree(
                ROOT,
                copy,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
            )
            (copy / ".env").write_text("EXAMPLE_ONLY=1\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(copy / "scripts/validate_project.py"), "--root", str(copy)],
                check=False,
                capture_output=True,
                text=True,
                timeout=VALIDATOR_TIMEOUT_SECONDS,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Tracked secret-class filename", result.stderr)

    def test_validator_rejects_trailing_whitespace_in_source_text(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-qq-whitespace-") as temp:
            copy = Path(temp) / "project-QQ"
            shutil.copytree(
                ROOT,
                copy,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
            )
            readme = copy / "README.md"
            readme.write_text(
                readme.read_text(encoding="utf-8") + "bad trailing space   \n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(copy / "scripts/validate_project.py"), "--root", str(copy)],
                check=False,
                capture_output=True,
                text=True,
                timeout=VALIDATOR_TIMEOUT_SECONDS,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("trailing whitespace", result.stderr)


if __name__ == "__main__":
    unittest.main()
