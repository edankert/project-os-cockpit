"""TASK-0369 — the obligation registry, enumerated by note type.

The point of these is that the **corpus supplies the checklist**. A list of
obligation kinds written by hand was wrong three times in one day; a list
checked against the types the notes actually use cannot be.
"""

from __future__ import annotations

from pathlib import Path

from project_os_cockpit import obligations, statuses
from project_os_cockpit.index import Index

REPO = Path(__file__).resolve().parents[1]


def _corpus_types() -> set[str]:
    index = Index.build(REPO / "docs")
    return {
        r.note_type for p in index.paths()
        if (r := index.get(p)) and r.note_type
        and not r.rel_path.startswith("__templates__/")
    }


def test_every_type_in_the_corpus_is_declared() -> None:
    """**The completeness guarantee.**

    This is what would have caught `change`, `release`, `risk`, `workflow` and
    `phase` without anyone asking. A type present in the notes with no entry
    is a failure here rather than something somebody has to notice.
    """
    undeclared = _corpus_types() - obligations.declared_types()
    assert not undeclared, (
        f"types in the corpus with no obligation declaration: {sorted(undeclared)}"
    )


def test_every_none_carries_its_reason() -> None:
    """An unexplained absence is exactly what an omission looks like.

    `task` (381 notes) and `plan` (52) owe nothing, correctly — and that is
    indistinguishable from a forgotten entry unless the reason is written.
    """
    for note_type, ob in obligations.OBLIGATIONS.items():
        if ob.owed:
            continue
        assert ob.reason.strip(), f"{note_type} declares `none` without a reason"
        assert len(ob.reason) > 40, (
            f"{note_type}'s reason is too thin to be checkable: {ob.reason!r}"
        )


def test_every_owed_kind_names_one_view_and_a_verb() -> None:
    """One type, one owning view — otherwise the badges count it twice."""
    for note_type, ob in obligations.owed_kinds().items():
        assert ob.view in obligations.VIEWS, f"{note_type} names view {ob.view!r}"
        assert ob.verb, f"{note_type} owes something with no verb a human can read"
        assert ob.states or ob.predicate, (
            f"{note_type} owes something but says nothing about when"
        )


def test_no_state_is_outside_the_status_vocabulary() -> None:
    """The ISS-0023 rule, applied to a third table."""
    for note_type, ob in obligations.OBLIGATIONS.items():
        for state in ob.states:
            assert state in statuses.VOCABULARY, (
                f"{note_type} is owed at {state!r}, which is not a status"
            )


def test_no_close_out_status_makes_something_owed() -> None:
    """A terminal note owes nobody anything, by construction."""
    for note_type, ob in obligations.OBLIGATIONS.items():
        for state in ob.states:
            assert not statuses.is_completed(state), (
                f"{note_type} is owed at the terminal status {state!r}"
            )


def test_the_four_ISS_0128_answers_are_recorded() -> None:
    """Each was a decision a test could not make, so the test asserts they
    were made — and that the reasoning survived, not just the verdict."""
    reg = obligations.OBLIGATIONS
    assert not reg["risk"].owed and reg["risk"].view == obligations.VIEW_INTENT
    assert "resting state" in reg["risk"].reason
    assert not reg["workflow"].owed and "TOOLING" in reg["workflow"].reason
    assert not reg["phase"].owed and "PROCEDURE" in reg["phase"].reason
    for note_type in ("risk", "workflow", "phase"):
        assert "ISS-0128" in reg[note_type].reason, (
            f"{note_type}'s reason does not cite where it was decided"
        )


def test_the_payload_carries_no_vocabulary_a_renderer_must_restate() -> None:
    p = obligations.payload()
    assert p["kinds"] and p["none"]
    for kind in p["kinds"]:
        assert kind["verb"] and kind["view"]
    for none in p["none"]:
        assert none["reason"]


def test_removing_a_kind_removes_it_from_every_view() -> None:
    """Nothing downstream keeps its own list."""
    before = set(obligations.views_owed()["issues"])
    assert "issue" in before
    saved = obligations.OBLIGATIONS["issue"]
    try:
        obligations.OBLIGATIONS["issue"] = obligations.NONE(
            "temporarily removed by a test to prove nothing else remembers it",
            obligations.VIEW_ISSUES,
        )
        assert "issue" not in obligations.views_owed()["issues"]
        assert "issue" not in obligations.owed_kinds()
    finally:
        obligations.OBLIGATIONS["issue"] = saved
