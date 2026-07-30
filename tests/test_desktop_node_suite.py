"""Run the desktop's behavioural node suite from pytest (FEAT-0028 / TASK-0248).

Every other desktop guard in this repo reads TypeScript *source* and
asserts that a string appears in it. Both design-bench reviewers walked
through one of those independently (ISS-0055's closing observation): a
rename, or a hoist, and the guard still passes while the behaviour it
names is gone.

`desktop/tests/*.test.mjs` runs the built module against real HTTP
servers instead, so it fails when the behaviour breaks rather than when
a literal moves. This wrapper keeps the repo at one test command —
`pytest` — rather than two, so a suite nobody remembers to run cannot
quietly rot.

Uses `node --test`, which is stdlib since Node 18. No new dependency:
adding a JS test framework to a Python project to check four hundred
lines of TypeScript would cost more than it returns.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DESKTOP = REPO_ROOT / "desktop"
NODE_TESTS = DESKTOP / "tests"
BUILT = DESKTOP / "dist" / "ipc" / "fleet-health.js"


def test_desktop_node_suite_passes() -> None:
    """The desktop's node suite is green.

    Skipped without node or without a build — a fresh clone has neither,
    and there is nothing shipped to be wrong about. The suite itself
    fails loudly if the build is missing once it does run, so a
    half-built tree cannot pass by accident.
    """
    node = shutil.which("node")
    if node is None:
        pytest.skip("node not on PATH")
    if not BUILT.is_file():
        pytest.skip("desktop not built (no dist/ipc/fleet-health.js) — run `npm run build`")

    files = sorted(str(p) for p in NODE_TESTS.glob("*.test.mjs"))
    assert files, "desktop/tests/ has no *.test.mjs — the suite was removed or renamed"

    proc = subprocess.run(
        [node, "--test-timeout", "20000", "--test", *files],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=str(DESKTOP),
    )
    assert proc.returncode == 0, (
        "desktop node suite failed:\n"
        + (proc.stdout or "")[-6000:]
        + "\n--- stderr ---\n"
        + (proc.stderr or "")[-2000:]
    )
