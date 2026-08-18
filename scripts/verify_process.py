#!/usr/bin/env python3
"""Run the complete local project-QQ verification sequence."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run(command: list[str], *, cwd: Path, env: dict[str, str]) -> None:
    print("+", subprocess.list2cmdline(command), flush=True)
    result = subprocess.run(command, cwd=cwd, env=env, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--hermes-source", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    env = os.environ.copy()
    validator = [sys.executable, "scripts/validate_project.py", "--root", str(root)]
    if args.hermes_source is not None:
        source = args.hermes_source.resolve()
        validator.extend(["--hermes-source", str(source)])
        env["HERMES_SOURCE"] = str(source)
    run(validator, cwd=root, env=env)
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=root, env=env)
    run(
        ["git", "diff", "--check", "--", ".", ":(exclude)patches/*.patch"],
        cwd=root,
        env=env,
    )
    print("PROJECT_QQ_PROCESS_VERIFICATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
