"""`FEATURE-UNCOVERED` — a finished feature that nothing verifies ([[TASK-0523]]).

Built on constructed corpora rather than on this repo's, because the live
number (88) is exactly the kind of figure that drifts under every commit — and
a guard that pins it would be edited, not obeyed.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "scripts" / "validate-docs.py"
BUNDLED = ROOT / "src" / "project_os_cockpit" / "validate_docs_bundled.py"


def _repo(tmp: Path, *, suite: bool, status: str, exception: str = "") -> Path:
    """A minimal repo: one feature, and optionally one acceptance check."""
    docs = tmp / "docs"
    (docs / "features" / "f").mkdir(parents=True)
    (tmp / "SNAPSHOT.yaml").write_text(
        'version: 1\nproject:\n  name: "t"\n  repo_root: "."\n'
        "counters:\n  FEAT: 1\n  TST: 1\nitems: {}\n", encoding="utf-8")
    extra = f'acceptance_exception: "{exception}"\n' if exception else ""
    (docs / "features" / "f" / "FEAT-0001-Thing.md").write_text(
        f'---\ntype: "[[feature]]"\nid: FEAT-0001\ntitle: "Thing"\n'
        f'status: {status}\n{extra}---\n\n# Thing\n', encoding="utf-8")
    if suite:
        (docs / "tests" / "acceptance").mkdir(parents=True)
        (docs / "tests" / "acceptance" / "TST-0001-C.md").write_text(
            '---\ntype: "[[test]]"\nid: TST-0001\ntitle: "C"\n'
            'level: acceptance\nstatus: active\narea: "A"\nmark: todo\n'
            'covers: []\n---\n\n# C\n', encoding="utf-8")
    return tmp


def _findings(repo: Path) -> int:
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(repo)],
        capture_output=True, text=True).stdout
    return out.count("FEATURE-UNCOVERED")


def test_it_fires_on_a_done_feature_nothing_covers(tmp_path: Path) -> None:
    assert _findings(_repo(tmp_path, suite=True, status="done")) == 1


def test_it_is_silent_while_the_feature_is_unfinished(tmp_path: Path) -> None:
    """The subject is *shipped and unverified*, not *not yet verified*."""
    assert _findings(_repo(tmp_path, suite=True, status="doing")) == 0


def test_an_exception_silences_it(tmp_path: Path) -> None:
    """**The escape is what makes the rule honest.** Without a way to say once,
    in the note, that a feature can never have a check — an engine with no
    rider-facing surface, a phase of work — this is a rule people disable
    rather than satisfy.
    """
    repo = _repo(tmp_path, suite=True, status="done",
                 exception="engine with no rider-facing surface")
    assert _findings(repo) == 0


def test_it_says_nothing_in_a_repo_with_no_suite(tmp_path: Path) -> None:
    """Nine of the twelve fleet repos hold no acceptance check at all. Firing
    there would scold them for not using a mechanism they never adopted —
    236 findings fleet-wide against 147 in the three that have a suite.
    """
    assert _findings(_repo(tmp_path, suite=False, status="done")) == 0


def test_it_warns_and_never_errors(tmp_path: Path) -> None:
    """**Undated, deliberately** ([[ADR-0011]] clause 3). The debt is 147 in
    suite-bearing repos, 88 of them in this one. A date would either fail every
    build on arrival or be moved when it did, and a promotion nobody intends to
    honour teaches people to ignore the table.
    """
    repo = _repo(tmp_path, suite=True, status="done")
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(repo)],
        capture_output=True, text=True)
    assert "WARN  [FEATURE-UNCOVERED]" in out.stdout, out.stdout[-400:]
    assert "ERROR [FEATURE-UNCOVERED]" not in out.stdout
    #: And it is not in the promotions table, which is what a date would mean.
    src = VALIDATOR.read_text(encoding="utf-8")
    table = src[src.index("PROMOTIONS = {"):]
    table = table[:table.index("}")]
    assert "FEATURE-UNCOVERED" not in table, (
        "the rule has been dated; 147 outstanding findings is not a promise"
    )


def test_the_two_validator_copies_stay_identical() -> None:
    """`tools/scripts/validate-docs.py` ships downstream and
    `validate_docs_bundled.py` is the package's copy. They are **byte-identical
    at HEAD**, and adding this rule to only one of them is exactly what
    happened first: the rule was written, measured 88 in the corpus, and
    reported **zero** — because `validate-docs.sh` runs the other file.

    Nothing in the suite caught that. This does.
    """
    assert BUNDLED.read_bytes() == VALIDATOR.read_bytes(), (
        "the two validator copies have diverged — a rule added to one of them "
        "silently does not run in the other, and `validate-docs.sh` runs "
        "`tools/scripts/validate-docs.py`"
    )
