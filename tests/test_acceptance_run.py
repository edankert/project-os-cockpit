"""What a completed acceptance run leaves behind (TASK-0289 / REQ-0028).

*"The difference between acceptance and a checkbox: `- [x]` says something was
ticked; `accepted in cockpit run, user:edwin, 2026-08-03` says who stood behind
it. PHASE-022 ran twelve acceptance rounds whose only witness record is a chat
transcript — this requirement is why that cannot recur."*

Each of REQ-0028's four criteria gets a test, and the two that are easy to
implement *almost* correctly get the most attention:

* an **incomplete** run must stamp nothing — a partial walk is evidence of
  progress, not of acceptance;
* a feature that **never requested** acceptance must be refused — stamping
  `accepted_by` on a feature nobody asked about manufactures a judgment.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from project_os_cockpit import note_writes
from project_os_cockpit.index import Index


def _feature(docs: Path, fid: str, *, acceptance: str = "requested") -> Path:
    d = docs / "features" / fid.lower()
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{fid}-Thing.md"
    p.write_text(
        f'---\ntype: "[[feature]]"\nid: {fid}\naliases: ["{fid}"]\n'
        f'title: "A thing"\nstatus: doing\nacceptance: {acceptance}\n'
        f"updated: 2026-01-01\n---\n\n# A thing\n\n## Goal\n\nSomething.\n",
        encoding="utf-8",
    )
    return p


@pytest.fixture()
def docs(tmp_path: Path) -> Path:
    d = tmp_path / "docs"
    d.mkdir()
    return d


def test_a_completed_run_names_its_witness_and_totals(docs: Path) -> None:
    """Criteria 1 and 2: who, when, and the same numbers in both places."""
    path = _feature(docs, "FEAT-9001")
    result = note_writes.stamp_acceptance_run(
        Index.build(docs), "FEAT-9001",
        passed=5, failed=1, skipped=2, issues=["ISS-9001"], actor="user:edwin",
    )
    text = path.read_text(encoding="utf-8")

    assert "## Acceptance runs" in text
    assert "user:edwin" in text
    assert "5 passed · 1 failed → ISS-9001 · 2 skipped" in text, text
    # `_set_field` renders quoted values, as every other stamped field is.
    assert f'accepted_by: "{result["witness"]}"' in text
    assert f'accepted_date: "{result["date"]}"' in text
    assert 'acceptance: "accepted"' in text, (
        "the feature still reads `requested` after being accepted, so it would "
        "keep appearing on the acceptance queue it has just left"
    )
    # The log line and the frontmatter must name the SAME witness — one
    # composed line is why they cannot disagree.
    assert result["witness"] == "user:edwin"


def test_an_incomplete_run_logs_but_stamps_nothing(docs: Path) -> None:
    """Criterion 3, and the one most easily got wrong.

    A partial walk is evidence of progress. Stamping `accepted_by` for it
    would let an abandoned run read as an acceptance.
    """
    path = _feature(docs, "FEAT-9002")
    result = note_writes.stamp_acceptance_run(
        Index.build(docs), "FEAT-9002",
        passed=2, failed=0, skipped=0, complete=False, actor="user:edwin",
    )
    text = path.read_text(encoding="utf-8")

    assert "INCOMPLETE" in text
    assert "accepted_by" not in text, "an unfinished run stamped acceptance"
    assert "accepted_date" not in text
    assert result["accepted"] is False


def test_a_feature_that_never_asked_is_refused(docs: Path) -> None:
    """Stamping a feature nobody asked about manufactures a judgment."""
    _feature(docs, "FEAT-9003", acceptance="")
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.stamp_acceptance_run(
            Index.build(docs), "FEAT-9003",
            passed=1, failed=0, skipped=0, actor="user:edwin",
        )
    assert "not requested acceptance" in exc.value.message


def test_an_incomplete_run_may_log_against_a_feature_that_did_not_ask(docs: Path) -> None:
    """The refusal is on the STAMP, not on the log.

    Recording that somebody walked criteria is harmless and useful; claiming
    they accepted is not. Splitting the guard this way keeps a partial walk
    possible on any feature.
    """
    path = _feature(docs, "FEAT-9004", acceptance="")
    note_writes.stamp_acceptance_run(
        Index.build(docs), "FEAT-9004",
        passed=1, failed=0, skipped=0, complete=False, actor="user:edwin",
    )
    assert "## Acceptance runs" in path.read_text(encoding="utf-8")


def test_runs_accumulate_newest_last(docs: Path) -> None:
    """The section is a chronological log, like `## Runs` — so "has this ever
    passed, and when did it start failing" is answered by scrolling."""
    path = _feature(docs, "FEAT-9005")
    index = Index.build(docs)
    note_writes.stamp_acceptance_run(
        index, "FEAT-9005", passed=1, failed=1, skipped=0,
        complete=False, actor="a",
    )
    note_writes.stamp_acceptance_run(
        Index.build(docs), "FEAT-9005", passed=2, failed=0, skipped=0, actor="b",
    )
    text = path.read_text(encoding="utf-8")
    assert text.count("### ") == 2
    assert text.index("1 passed") < text.index("2 passed"), "runs are not chronological"


def test_a_run_cannot_be_recorded_on_a_non_feature(docs: Path) -> None:
    """Acceptance is a feature-level judgment; a task has no criteria to walk."""
    (docs / "issues").mkdir(parents=True, exist_ok=True)
    (docs / "issues" / "ISS-9001-X.md").write_text(
        '---\ntype: "[[issue]]"\nid: ISS-9001\naliases: ["ISS-9001"]\n'
        'title: "X"\nstatus: triage\n---\n\n# X\n', encoding="utf-8",
    )
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.stamp_acceptance_run(
            Index.build(docs), "ISS-9001", passed=1, failed=0, skipped=0,
        )
    assert "recorded on features" in exc.value.message


def test_a_stale_run_is_refused_by_the_mtime_guard(docs: Path) -> None:
    """Every write path carries it; a run walked against an older note must
    not silently apply to a newer one."""
    _feature(docs, "FEAT-9006")
    with pytest.raises(note_writes.WriteError):
        note_writes.stamp_acceptance_run(
            Index.build(docs), "FEAT-9006", passed=1, failed=0, skipped=0,
            mtime=1.0,
        )


def test_the_run_endpoint_is_in_the_guarded_write_set() -> None:
    """REQ-0028 criterion 4 rests on the loopback guard, so it is asserted.

    `test_every_note_mutating_endpoint_requires_loopback` enumerates the POST
    table and would catch a missing guard; this asserts the route exists at
    all, so the enumeration has something to find.
    """
    src = (
        Path(__file__).resolve().parents[1]
        / "src" / "project_os_cockpit" / "server.py"
    ).read_text(encoding="utf-8")
    assert '"/api/notes/acceptance-run"' in src
    handler = src.split("def _serve_acceptance_run")[1].split("\n        def ")[0]
    assert "_require_loopback" in handler, (
        "the acceptance-run endpoint writes to notes without a peer check"
    )
