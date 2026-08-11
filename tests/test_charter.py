"""The intent charter, and delegated acceptance under it (FEAT-0077).

Acceptance asks *is this what I asked for?* — so a delegate needs **the asking
written down**. Without it a delegated acceptance is a model guessing at taste
from a diff, which is the failure twelve PHASE-022 corrections demonstrated a
human catching.

REQ-0029 states the property these tests exist to hold: *delegation without
distinguishability is impersonation.*
"""

from __future__ import annotations

from pathlib import Path

import pytest

from project_os_cockpit import charter, note_writes
from project_os_cockpit.index import Index

APPROVED = (
    "---\nstatus: approved\n---\n\n"
    "## What this is for\n\nGoverning a project you did not write.\n\n"
    "## What it must never become\n\nA tool that says something false without saying so.\n"
)


def test_an_absent_charter_is_not_usable(tmp_path: Path) -> None:
    got = charter.load(tmp_path)
    assert got["usable"] is False and "no INTENT.md" in got["why"]


def test_a_draft_charter_is_no_charter(tmp_path: Path) -> None:
    """Same gate as the delegation policy: an agent that could write the intent
    it is judged against is judging itself."""
    (tmp_path / charter.CHARTER_REL).write_text(
        APPROVED.replace("status: approved", "status: draft"), encoding="utf-8",
    )
    got = charter.load(tmp_path)
    assert got["usable"] is False and "draft charter is no charter" in got["why"]


def test_an_incomplete_charter_is_refused_with_the_missing_section_named(tmp_path: Path) -> None:
    """"Partially useful" is not a state a standard can be in — a delegate
    reading half a charter has no way to know which half."""
    (tmp_path / charter.CHARTER_REL).write_text(
        "---\nstatus: approved\n---\n\n## What this is for\n\nx\n", encoding="utf-8",
    )
    got = charter.load(tmp_path)
    assert got["usable"] is False
    assert "What it must never become" in got["why"]


def test_an_approved_complete_charter_is_usable_and_pinned(tmp_path: Path) -> None:
    (tmp_path / charter.CHARTER_REL).write_text(APPROVED, encoding="utf-8")
    got = charter.load(tmp_path)
    assert got["usable"] is True and len(got["sha"]) == 64


def test_any_edit_changes_the_sha(tmp_path: Path) -> None:
    """The sha covers the whole note deliberately: a change anywhere is a
    change to the standard, and pinning only the sections would let the
    surrounding prose drift under a judgment already made."""
    path = tmp_path / charter.CHARTER_REL
    path.write_text(APPROVED, encoding="utf-8")
    before = charter.load(tmp_path)["sha"]
    path.write_text(APPROVED + "\nOne more sentence.\n", encoding="utf-8")
    assert charter.load(tmp_path)["sha"] != before


def test_a_delegate_witness_is_distinguishable_from_a_person(tmp_path: Path) -> None:
    """REQ-0029's own test — at a glance, not by lookup."""
    w = charter.witness("c" * 64, "p" * 40)
    assert charter.is_delegate_witness(w) is True
    for human in ("user:edwin", "edwin", "", "agent:principal"):
        assert charter.is_delegate_witness(human) is False, human


# ---- TASK-0334: the guard on the write path -------------------------------


def _feature(docs: Path) -> Index:
    d = docs / "features" / "x"
    d.mkdir(parents=True)
    (d / "FEAT-9001-X.md").write_text(
        '---\ntype: "[[feature]]"\nid: FEAT-9001\naliases: ["FEAT-9001"]\n'
        'title: "X"\nstatus: doing\nacceptance: requested\nupdated: 2026-01-01\n'
        "---\n\n# X\n", encoding="utf-8",
    )
    return Index.build(docs)


def test_a_bare_agent_witness_is_refused(tmp_path: Path) -> None:
    """`agent:principal` alone is not enough.

    An attribution that could be confused with a person's is the whole failure
    REQ-0029 names, so a delegate that cannot say *under what authority* is
    refused rather than silently recorded as if a human stood behind it.
    """
    index = _feature(tmp_path / "docs")
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.stamp_acceptance_run(
            index, "FEAT-9001", passed=1, failed=0, skipped=0, actor="agent:principal",
        )
    assert "names no charter" in exc.value.message


def test_a_delegate_naming_its_charter_may_accept(tmp_path: Path) -> None:
    index = _feature(tmp_path / "docs")
    result = note_writes.stamp_acceptance_run(
        index, "FEAT-9001", passed=2, failed=0, skipped=0,
        actor=charter.witness("c" * 64, "p" * 40),
    )
    assert result["accepted"] is True
    assert charter.is_delegate_witness(result["witness"]) is True


def test_a_human_run_is_unaffected(tmp_path: Path) -> None:
    """The guard must not make a person carry a charter they are not acting
    under — a human accepts on their own authority."""
    index = _feature(tmp_path / "docs")
    result = note_writes.stamp_acceptance_run(
        index, "FEAT-9001", passed=1, failed=0, skipped=0, actor="user:edwin",
    )
    assert result["accepted"] is True
    assert charter.is_delegate_witness(result["witness"]) is False
