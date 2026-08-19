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


# ============ ISS-0220, closed by ADR-0037 decision 9a ============

def _release_note(tmp_path: Path, rows: list[dict]) -> None:
    (tmp_path / "docs" / "tests").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "tests" / "TST-0001-A.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0001\nstatus: active\n'
        'level: acceptance\n---\n\n# A\n')
    (tmp_path / "docs" / "releases").mkdir(parents=True, exist_ok=True)
    ledgers = "\n".join(
        f'  - file: "{r["file"]}"\n    sha: "{r["sha"]}"' for r in rows) or "  []"
    (tmp_path / "docs" / "releases" / "REL-0001-A.md").write_text(
        '---\ntype: "[[release]]"\nid: REL-0001\nstatus: released\n'
        f'version: "v1"\nledgers:\n{ledgers}\n---\n\n# A\n')


def _blob(text: str) -> str:
    import hashlib
    raw = text.encode("utf-8")
    return hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest()


SEALED = {"platform": "macos", "release": "REL-0001", "version": "v1",
          "sealed": "2026-08-19", "entries": [GOOD], "evidence": []}


def test_a_sealed_ledger_edited_after_committing_is_caught(
    tmp_path: Path,
) -> None:
    """**The gap ISS-0220 named, closed.**

    The old rule diffed the working tree against `HEAD`, so an edit that was
    *committed* passed forever — and *was release R walked?* had an answer
    that could still change, which is the one property immutability exists to
    give. The release note now records the ledger's blob hash, so the check is
    against the **bytes**: caught committed, uncommitted, rebased, or restored
    from a backup, because none of those changes what the content hashes to.
    """
    text = json.dumps(SEALED)
    _release_note(tmp_path, [{"file": "REL-0001-macos.json",
                              "sha": _blob(text)}])
    assert _run(tmp_path, SEALED, name="REL-0001-macos.json") == []

    tampered = json.loads(text)
    tampered["entries"][0]["mark"] = "na"
    tampered["entries"][0]["reason"] = "rewriting history"
    lines = _run(tmp_path, tampered, name="REL-0001-macos.json")
    assert "LEDGER-SEALED" in _codes(lines), lines
    assert "no longer hashes" in lines[0]


def test_a_sealed_ledger_nobody_vouches_for_is_caught(tmp_path: Path) -> None:
    """An unvouched seal is exactly the state the old check could not tell
    from a good one."""
    _release_note(tmp_path, [])
    lines = _run(tmp_path, SEALED, name="REL-0001-macos.json")
    assert "LEDGER-SEALED" in _codes(lines)
    assert "no release note vouches for it" in lines[0]


def test_a_working_ledger_needs_no_voucher(tmp_path: Path) -> None:
    """Only a sealed ledger is a record. The open one is still being written."""
    assert _run(tmp_path, {"platform": "macos", "entries": [GOOD],
                           "evidence": []}) == []
