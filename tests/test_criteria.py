"""The runner walks exactly what the validator counts (TASK-0287).

`criteria.py` restates `count_acceptance_boxes` rather than importing it — the
validator is a standalone script with no package imports so CI can run it from
a bare checkout, and importing it into the package would invert that.

A restatement is only worth having if it is proven, so the identity is asserted
**over the whole live corpus**, requirement by requirement, rather than over a
handful of hand-written cases. If they ever diverge, a person could complete an
acceptance run and still be refused at close-out by REQ-BOXES — or tick past a
criterion the gate never saw.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from project_os_cockpit import criteria
from project_os_cockpit.index import Index

REPO = Path(__file__).resolve().parent.parent
REPO_DOCS = REPO / "docs"


def _validator():
    """The real `validate-docs.py`, loaded as a module."""
    spec = importlib.util.spec_from_file_location(
        "validate_docs_under_test", REPO / "tools" / "scripts" / "validate-docs.py",
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def index() -> Index:
    return Index.build(REPO_DOCS)


def test_the_parse_is_identical_to_req_boxes_across_the_corpus(index: Index) -> None:
    """Every requirement, both parses, same three numbers."""
    validator = _validator()
    checked = 0
    mismatches: list[str] = []
    for record in index.notes_by_type("requirement"):
        if record.rel_path.startswith("__templates__/"):
            continue
        theirs = validator.count_acceptance_boxes(record.path, with_reconciled=True)
        parsed = criteria.parse_criteria(record.path.read_text(encoding="utf-8"))
        mine = (
            sum(1 for c in parsed if c["state"] == "open"),
            sum(1 for c in parsed if c["state"] == "ticked"),
            sum(1 for c in parsed if c["state"] == "reconciled"),
        )
        checked += 1
        if theirs != mine:
            mismatches.append(f"{record.note_id}: validator={theirs} runner={mine}")
    assert checked >= 20, f"only {checked} requirements examined; the corpus should have more"
    assert not mismatches, (
        "the runner and REQ-BOXES disagree about what a criterion is:\n  "
        + "\n  ".join(mismatches)
    )


def test_a_fence_hides_a_checkbox_from_both(tmp_path: Path) -> None:
    """The fence rule, which is the subtle half of the shared parse."""
    note = tmp_path / "REQ-9001-Fenced.md"
    note.write_text(
        '---\ntype: "[[requirement]]"\nid: REQ-9001\n---\n\n'
        "## Acceptance\n\n"
        "- [ ] a real criterion\n\n"
        "```\n- [ ] an example inside a fence\n```\n\n"
        "- [x] another real one — evidence here\n",
        encoding="utf-8",
    )
    parsed = criteria.parse_criteria(note.read_text(encoding="utf-8"))
    assert [c["state"] for c in parsed] == ["open", "ticked"], parsed
    assert _validator().count_acceptance_boxes(note, with_reconciled=True) == (1, 1, 0)


def test_the_three_states_are_all_read(tmp_path: Path) -> None:
    """`- [~]` is a first-class answer, not a typo.

    STATUSES.md defines the gate as "ticked-with-evidence OR reconciled". A
    runner offering only pass/fail would have no way to record the honest third
    answer, and would push people to tick things they did not do.
    """
    note = tmp_path / "REQ-9002-Three.md"
    note.write_text(
        '---\ntype: "[[requirement]]"\nid: REQ-9002\n---\n\n'
        "## Acceptance\n\n"
        "- [ ] owed\n- [x] delivered — with evidence\n- [~] cut — and here is why\n",
        encoding="utf-8",
    )
    states = [c["state"] for c in criteria.parse_criteria(note.read_text(encoding="utf-8"))]
    assert states == ["open", "ticked", "reconciled"]


def test_evidence_splits_on_the_last_dash_not_the_first(tmp_path: Path) -> None:
    """Criteria routinely contain an em dash mid-sentence.

    Splitting on the first would file half the criterion as its own evidence,
    which reads as plausible and is wrong — the failure mode worth a test.
    """
    note = tmp_path / "REQ-9003-Dash.md"
    note.write_text(
        '---\ntype: "[[requirement]]"\nid: REQ-9003\n---\n\n'
        "## Acceptance\n\n"
        "- [x] the cockpit — which a person drives — refuses a LAN write — 10 of 10 got 403\n",
        encoding="utf-8",
    )
    c = criteria.parse_criteria(note.read_text(encoding="utf-8"))[0]
    assert c["evidence"] == "10 of 10 got 403"
    assert c["text"].startswith("the cockpit")
    assert "403" not in c["text"]


def test_an_open_criterion_carries_no_evidence(tmp_path: Path) -> None:
    """An em dash on an unticked box is punctuation, not proof."""
    note = tmp_path / "REQ-9004-Open.md"
    note.write_text(
        '---\ntype: "[[requirement]]"\nid: REQ-9004\n---\n\n'
        "## Acceptance\n\n- [ ] something — with a clause\n",
        encoding="utf-8",
    )
    c = criteria.parse_criteria(note.read_text(encoding="utf-8"))[0]
    assert c["state"] == "open"
    assert c["evidence"] == ""


def test_the_payload_gathers_a_features_requirements(index: Index) -> None:
    """FEAT-0059 owns two requirements; both must appear with their criteria."""
    payload = criteria.payload(index, "FEAT-0059")
    assert "error" not in payload
    ids = [r["id"] for r in payload["requirements"]]
    assert "REQ-0026" in ids and "REQ-0027" in ids, ids
    assert payload["total"] == sum(payload["totals"].values())
    assert payload["total"] > 0 and payload["nothing_to_accept"] is False


def test_a_feature_with_no_criteria_says_so_rather_than_erroring(index: Index) -> None:
    """`nothing_to_accept` is a real answer — FEAT-0065 counts it as debt."""
    payload = criteria.payload(index, "FEAT-0073")
    assert "error" not in payload
    assert payload["nothing_to_accept"] is (payload["total"] == 0)


def test_an_unknown_feature_is_an_error_not_an_empty_run(index: Index) -> None:
    """An empty runner screen for a typo'd id would look like a clean feature."""
    assert "error" in criteria.payload(index, "FEAT-9999")
