"""`validate_ledgers` — the gate, tested (independent review finding 6).

142 lines, six codes, two byte-identical copies, and `grep -rn "LEDGER-" tests/`
returned nothing. Exit criterion 5 and [[REQ-0052]] criterion 4 were met by no
test at all, which is the shape of a gate people trust because it is there
rather than because it works.

Each case here is a defect the validator must catch, written as the defect.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "scripts" / "validate-docs.py"

SNAPSHOT = (
    'version: 1\nupdated: "2026-08-19"\ncounters:\n  TST: 1\n'
    'focus:\n  task: ""\nitems:\n  tests: {}\n'
)
GOOD = {"check": "TST-0001", "mark": "pass", "date": "2026-08-19",
        "by": "user:edwin", "method": "manual"}


def _run(tmp_path: Path, ledger: dict, name: str = "WORKING-macos.json"):
    (tmp_path / "docs" / "releases" / "ledgers").mkdir(parents=True,
                                                       exist_ok=True)
    (tmp_path / "SNAPSHOT.yaml").write_text(SNAPSHOT)
    (tmp_path / "docs" / "releases" / "ledgers" / name).write_text(
        json.dumps(ledger))
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(tmp_path)],
        capture_output=True, text=True)
    return [line for line in out.stdout.splitlines() if "LEDGER-" in line]


def _codes(lines: list[str]) -> set[str]:
    return {line.split("[", 1)[1].split("]", 1)[0] for line in lines}


def test_a_clean_ledger_says_nothing(tmp_path: Path) -> None:
    assert _run(tmp_path, {"platform": "macos", "entries": [GOOD],
                           "evidence": []}) == []


def test_a_repo_with_no_ledgers_says_nothing(tmp_path: Path) -> None:
    """Nine of twelve fleet repos. Absent is a real state, not a broken one."""
    (tmp_path / "docs").mkdir(parents=True)
    (tmp_path / "SNAPSHOT.yaml").write_text(SNAPSHOT)
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(tmp_path)],
        capture_output=True, text=True)
    assert "LEDGER-" not in out.stdout


@pytest.mark.parametrize("mutate,code", [
    ({"mark": "done"}, "LEDGER-MARK"),
    ({"mark": "na"}, "LEDGER-REASON"),
    ({"by": ""}, "LEDGER-ENTRY"),
    ({"method": "guess"}, "LEDGER-ENTRY"),
    ({"date": "nope"}, "LEDGER-ENTRY"),
    ({"date": "2026-13-45"}, "LEDGER-ENTRY"),
    ({"platform": "ios"}, "LEDGER-ENTRY"),
    ({"invalidated_by": "TASK-0001"}, "LEDGER-ENTRY"),
    ({"check": ""}, "LEDGER-ENTRY"),
])
def test_each_defect_in_an_entry_is_caught(
    tmp_path: Path, mutate: dict, code: str,
) -> None:
    lines = _run(tmp_path, {"platform": "macos", "entries": [{**GOOD, **mutate}],
                            "evidence": []})
    assert code in _codes(lines), f"{mutate} produced {lines}"


def test_evidence_for_a_walk_nobody_recorded_is_caught(tmp_path: Path) -> None:
    lines = _run(tmp_path, {"platform": "macos", "entries": [GOOD],
                            "evidence": [{"check": "TST-9999",
                                          "date": "2026-08-19",
                                          "ref": "x.png"}]})
    assert "LEDGER-EVIDENCE" in _codes(lines)


def test_a_ledger_that_will_not_parse_is_caught(tmp_path: Path) -> None:
    (tmp_path / "docs" / "releases" / "ledgers").mkdir(parents=True)
    (tmp_path / "SNAPSHOT.yaml").write_text(SNAPSHOT)
    (tmp_path / "docs" / "releases" / "ledgers"
     / "WORKING-macos.json").write_text("{not json")
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(tmp_path)],
        capture_output=True, text=True)
    assert "LEDGER-PARSE" in out.stdout


def test_an_entry_naming_a_check_this_repo_does_not_have_is_caught(
    tmp_path: Path,
) -> None:
    """A verdict on a check nobody can open is a verdict about nothing."""
    (tmp_path / "docs" / "tests").mkdir(parents=True)
    (tmp_path / "docs" / "tests" / "TST-0001-A.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0001\nstatus: active\n---\n\n# A\n')
    lines = _run(tmp_path, {"platform": "macos",
                            "entries": [GOOD, {**GOOD, "check": "TST-4242"}],
                            "evidence": []})
    assert any("TST-4242" in line for line in lines)
    assert not any("TST-0001 is not a note" in line for line in lines)


def test_the_bundled_copy_carries_the_same_rules() -> None:
    """Two byte-identical copies, and only one was ever exercised."""
    canonical = VALIDATOR.read_text()
    bundled = (ROOT / "src" / "project_os_cockpit"
               / "validate_docs_bundled.py").read_text()
    assert bundled == canonical
    for code in ("LEDGER-PARSE", "LEDGER-ENTRY", "LEDGER-MARK",
                 "LEDGER-REASON", "LEDGER-EVIDENCE", "LEDGER-SEALED"):
        assert code in bundled


def test_a_sealed_ledger_edited_in_the_working_tree_is_caught(
    tmp_path: Path,
) -> None:
    """`LEDGER-SEALED`, and **the limit it carries**.

    The rule diffs the working tree against `git show HEAD:<path>`, so it
    catches an uncommitted edit and **passes forever once the edit is
    committed**. That is a real hole in *"immutable once sealed"* and it is
    recorded here rather than in a summary: the honest scope of this rule is
    *"you did not edit a sealed ledger since the last commit"*, which is what
    a pre-commit gate can see and not what the ADR claims.

    Closing it needs the seal to be checked against the commit that created
    it, which needs the sealing commit recorded — [[ISS-0220]].
    """
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp_path,
                   check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path,
                   check=True)
    sealed = {"platform": "macos", "release": "REL-0001", "version": "v1",
              "sealed": "2026-08-19", "entries": [GOOD], "evidence": []}
    ledgers = tmp_path / "docs" / "releases" / "ledgers"
    ledgers.mkdir(parents=True)
    (tmp_path / "SNAPSHOT.yaml").write_text(SNAPSHOT)
    path = ledgers / "REL-0001-macos.json"
    path.write_text(json.dumps(sealed))
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "seal"], cwd=tmp_path, check=True)

    # Clean.
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(tmp_path)],
        capture_output=True, text=True)
    assert "LEDGER-SEALED" not in out.stdout

    # Edited, uncommitted — caught.
    sealed["entries"][0]["mark"] = "fail"
    sealed["entries"][0]["reason"] = "rewriting history"
    path.write_text(json.dumps(sealed))
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(tmp_path)],
        capture_output=True, text=True)
    assert "LEDGER-SEALED" in out.stdout

    # Committed — NOT caught. The limit, asserted so it cannot be forgotten.
    subprocess.run(["git", "commit", "-qam", "edit"], cwd=tmp_path, check=True)
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(tmp_path)],
        capture_output=True, text=True)
    assert "LEDGER-SEALED" not in out.stdout, (
        "if this now fails, the rule was strengthened — update ISS-0220")


def test_a_ledger_filename_that_names_no_platform_is_caught(
    tmp_path: Path,
) -> None:
    """Finding 5's other half: the reader refuses it, and so must the gate."""
    for name in ("REL-12-ios.json", "working-ios.json", "ios.json"):
        lines = _run(tmp_path, {"platform": "ios", "entries": [], "evidence": []},
                     name=name)
        assert "LEDGER-NAME" in _codes(lines), f"{name} passed"
        (tmp_path / "docs" / "releases" / "ledgers" / name).unlink()
