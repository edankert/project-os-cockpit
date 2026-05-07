"""Verify ``tools/scripts/release-to-project-os.sh`` against a temp dir.

Covers the guards (dirty tree refusal) and the happy-path file set + stamps.
The real script targets ``~/Dev/repos/project-os/`` by default, but exposes
``PROJECT_OS_ROOT`` as an env override — these tests use that to point at a
controlled temp dir.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "scripts" / "release-to-project-os.sh"


def _make_fake_project_os(tmp_path: Path) -> Path:
    """A minimal git repo standing in for project-os."""
    root = tmp_path / "project-os"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)
    (root / "README.md").write_text("# fake project-os\n")
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=root, check=True)
    return root


def _run_release(project_os_root: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PROJECT_OS_ROOT"] = str(project_os_root)
    return subprocess.run(
        [str(SCRIPT)],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )


@pytest.mark.skipif(
    not SCRIPT.is_file(), reason="release script not installed"
)
def test_release_refuses_dirty_canonical_tree(tmp_path: Path) -> None:
    """The script must refuse to run when the canonical repo is dirty.

    Quickest way to provoke a "dirty canonical tree" without actually
    dirtying the dev tree: write a temp file inside REPO_ROOT and revert
    after the test. We use a sentinel path that the test cleans up.
    """
    project_os = _make_fake_project_os(tmp_path)
    sentinel = REPO_ROOT / ".release-test-dirty-sentinel"
    sentinel.write_text("temp")
    try:
        result = _run_release(project_os)
        assert result.returncode != 0, (
            "expected dirty-tree refusal, got success.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "not clean" in result.stderr.lower()
    finally:
        sentinel.unlink(missing_ok=True)


@pytest.mark.skipif(
    not SCRIPT.is_file(), reason="release script not installed"
)
def test_release_happy_path_writes_expected_files(tmp_path: Path) -> None:
    """A clean canonical tree + clean destination yields the deployable set.

    Skipped when the canonical repo is itself dirty (CI, dev with WIP) —
    the script's guard would refuse, and that's the previous test's job
    anyway. We only assert the *content* expectations under clean conditions.
    """
    canon_clean = subprocess.run(
        ["git", "diff", "--quiet"], cwd=REPO_ROOT
    ).returncode == 0
    canon_staged_clean = subprocess.run(
        ["git", "diff", "--cached", "--quiet"], cwd=REPO_ROOT
    ).returncode == 0
    if not (canon_clean and canon_staged_clean):
        pytest.skip("canonical tree dirty — happy-path test requires clean tree")

    project_os = _make_fake_project_os(tmp_path)
    result = _run_release(project_os)
    assert result.returncode == 0, (
        f"sync failed unexpectedly.\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )

    dest = project_os / "tools" / "cockpit"
    assert (dest / "src" / "project_os_cockpit" / "__init__.py").is_file()
    assert (dest / "pyproject.toml").is_file()
    assert (dest / "README.md").is_file()
    assert (dest / "CANONICAL_SHA").is_file()
    assert (dest / "CANONICAL_DATE").is_file()
    # tests/ is a dev-only artefact and must NOT ship to project-os.
    assert not (dest / "tests").exists(), (
        "tests/ leaked into the synced copy — delivery artefacts shouldn't "
        "carry the test suite; that lives in the canonical repo."
    )

    # Provenance stamps look right.
    sha = (dest / "CANONICAL_SHA").read_text().strip()
    assert len(sha) == 40, f"expected git SHA, got {sha!r}"
    date = (dest / "CANONICAL_DATE").read_text().strip()
    assert len(date) == 10 and date[4] == "-" and date[7] == "-", (
        f"expected ISO date, got {date!r}"
    )

    # No __pycache__ leakage from the canonical tree.
    for p in dest.rglob("__pycache__"):
        pytest.fail(f"__pycache__ slipped into the sync: {p}")
