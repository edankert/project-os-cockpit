"""`strip-verdict-fields.py` — the destructive half of the migration.

**This script had no test at all**, and independent review found its one
safety property could not fire: it read `item.mark` from `acceptance.load`,
which applies the ledger to every item, so the guard compared the ledger to
itself. Reproduced — three notes at `mark: done`, a ledger with **zero**
entries, exit 0, three verdicts destroyed, and the output line asserting the
property it had not checked.

The 34-note migration in this repo was safe by *timing*: the script ran three
commits before the change that broke it. The fleet migration named next in
`PLAN.md` is 581 notes carrying 513 passes.

Every test here is written from the failure, and the guard is mutation-proven
below — because a test written after a fix tends to assert what the code now
does, which is how a fixed bug comes back looking like a passing suite.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "scripts" / "strip-verdict-fields.py"

NOTE = '''---
type: "[[test]]"
id: {cid}
level: acceptance
status: active
tier: 1
area: "A surface"
mark: {mark}
verdict_date: ""
verdict_reason: ""
invalidated_by: {{}}
automation: manual
covered_by: []
evidence: []
covers: []
---

# {cid}

A procedure.
'''


def _repo(tmp_path: Path, marks: dict[str, str], entries: list[dict]) -> Path:
    (tmp_path / "docs" / "tests" / "acceptance").mkdir(parents=True)
    (tmp_path / "SNAPSHOT.yaml").write_text(
        'version: 1\nupdated: "x"\ncounters:\n  TST: 1\n'
        'focus:\n  task: ""\nitems:\n  tests: {}\n')
    for cid, mark in marks.items():
        (tmp_path / "docs" / "tests" / "acceptance" / f"{cid}-A.md").write_text(
            NOTE.format(cid=cid, mark=mark))
    led = tmp_path / "docs" / "releases" / "ledgers"
    led.mkdir(parents=True)
    (led / "WORKING-macos.json").write_text(json.dumps(
        {"platform": "macos", "entries": entries, "evidence": []}))
    return tmp_path


def _run(repo: Path, *args: str):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo),
         "--platform", "macos", *args], capture_output=True, text=True)


def _entry(cid: str) -> dict:
    return {"check": cid, "mark": "pass", "date": "2026-08-19",
            "by": "migration", "method": "migration"}


def test_a_verdict_the_ledger_does_not_carry_is_refused(tmp_path: Path) -> None:
    """**The finding.** Three `done` marks, an empty ledger, `--apply`."""
    repo = _repo(tmp_path, {"TST-0001": "done", "TST-0002": "done"}, [])
    out = _run(repo, "--apply")

    assert out.returncode == 1, out.stdout
    assert "REFUSING" in out.stdout
    for cid in ("TST-0001", "TST-0002"):
        assert cid in out.stdout, "the refusal must name every note it saved"
        note = repo / "docs" / "tests" / "acceptance" / f"{cid}-A.md"
        assert "mark: done" in note.read_text(), "a verdict was destroyed"


def test_a_partly_carried_corpus_is_refused_whole(tmp_path: Path) -> None:
    """One unbacked note stops the run. A migration that strips what it can
    and reports the rest leaves a corpus nobody can reason about."""
    repo = _repo(tmp_path, {"TST-0001": "done", "TST-0002": "done"},
                 [_entry("TST-0001")])
    out = _run(repo, "--apply")
    assert out.returncode == 1
    assert "TST-0002" in out.stdout and "TST-0001" not in out.stdout
    assert "mark: done" in (repo / "docs" / "tests" / "acceptance"
                            / "TST-0001-A.md").read_text()


def test_an_unwalked_note_needs_no_entry(tmp_path: Path) -> None:
    """`todo` records no verdict, so removing it loses none — which is why
    `your-sudoku`'s 56 unwalked checks can migrate against an empty ledger."""
    repo = _repo(tmp_path, {"TST-0001": "todo", "TST-0002": "todo"}, [])
    out = _run(repo, "--apply")
    assert out.returncode == 0, out.stdout
    assert "mark:" not in (repo / "docs" / "tests" / "acceptance"
                           / "TST-0001-A.md").read_text()


def test_a_carried_corpus_strips_all_seven_fields(tmp_path: Path) -> None:
    repo = _repo(tmp_path, {"TST-0001": "done"}, [_entry("TST-0001")])
    assert _run(repo, "--apply").returncode == 0
    text = (repo / "docs" / "tests" / "acceptance" / "TST-0001-A.md").read_text()
    for field in ("mark:", "verdict_date:", "verdict_reason:",
                  "invalidated_by:", "automation:", "covered_by:", "evidence:"):
        assert field not in text, field
    # Intent survives.
    for kept in ("tier: 1", 'area: "A surface"', "covers: []",
                 "level: acceptance"):
        assert kept in text, kept
    assert text.count("---") == 2, "frontmatter is still frontmatter"


def test_a_block_field_takes_its_continuation_lines(tmp_path: Path) -> None:
    """Dropping the key and leaving the body makes the note unparseable — a
    defect that reads as a MISSING note rather than as a bad edit."""
    import yaml

    repo = _repo(tmp_path, {"TST-0001": "done"}, [_entry("TST-0001")])
    note = repo / "docs" / "tests" / "acceptance" / "TST-0001-A.md"
    note.write_text(note.read_text().replace(
        "invalidated_by: {}",
        "invalidated_by:\n  change: TASK-0001\n  reason: a thing\n"
        "  date: 2026-08-01"))
    assert _run(repo, "--apply").returncode == 0
    text = note.read_text()
    assert "TASK-0001" not in text and "reason: a thing" not in text
    parsed = yaml.safe_load(text.split("---")[1])
    assert parsed["id"] == "TST-0001" and "invalidated_by" not in parsed


def test_a_repo_with_no_ledger_is_refused(tmp_path: Path) -> None:
    """Removing the fields with nowhere for the verdicts to go is the whole
    corpus destroyed in one command."""
    (tmp_path / "docs" / "tests" / "acceptance").mkdir(parents=True)
    (tmp_path / "SNAPSHOT.yaml").write_text(
        'version: 1\nupdated: "x"\ncounters:\n  TST: 1\n'
        'focus:\n  task: ""\nitems:\n  tests: {}\n')
    (tmp_path / "docs" / "tests" / "acceptance" / "TST-0001-A.md").write_text(
        NOTE.format(cid="TST-0001", mark="done"))
    out = _run(tmp_path, "--apply")
    assert out.returncode == 2 and "no ledger" in out.stdout


def test_a_dry_run_writes_nothing(tmp_path: Path) -> None:
    repo = _repo(tmp_path, {"TST-0001": "done"}, [_entry("TST-0001")])
    before = (repo / "docs" / "tests" / "acceptance" / "TST-0001-A.md").read_text()
    assert _run(repo).returncode == 0
    assert (repo / "docs" / "tests" / "acceptance"
            / "TST-0001-A.md").read_text() == before


def test_the_guard_reads_the_file_and_not_the_item(tmp_path: Path) -> None:
    """The regression, pinned at its cause.

    `acceptance.load` applies the ledger, so `Item.mark` is the ledger's
    answer. Anything comparing that to the ledger is comparing the ledger to
    itself and can never refuse. This asserts the guard sees a mark the
    joined `Item` cannot: `mark: done` on disk, `todo` after the join.
    """
    sys.path.insert(0, str(ROOT / "src"))
    from project_os_cockpit import acceptance as A
    from project_os_cockpit.index import Index

    repo = _repo(tmp_path, {"TST-0001": "done"}, [])
    joined = A.load(repo / "docs", Index.build(repo / "docs"))
    assert joined.items[0].mark == "todo", (
        "if this is 'done' the join stopped applying and this test is stale")
    assert _run(repo, "--apply").returncode == 1, (
        "the guard must see the file's `done`, not the join's `todo`")
