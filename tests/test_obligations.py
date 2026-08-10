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


# ---- the badges (TASK-0370) -------------------------------------------


def test_the_badges_sum_to_the_registry_total() -> None:
    """ADR-0020 decision 3: the badges must cover **every** kind.

    A total that disagrees with the sum is exactly how a kind goes missing
    without anyone noticing — which is the defect this whole feature exists
    to remove, so it is asserted rather than assumed.
    """
    index = Index.build(REPO / "docs")
    payload = obligations.badges_payload(index)
    assert payload["total"] == sum(payload["views"].values())


def test_every_owed_note_lands_in_exactly_one_view() -> None:
    """One type, one view. Counting a note twice is as wrong as missing it."""
    index = Index.build(REPO / "docs")
    seen: dict[str, str] = {}
    for path in index.paths():
        record = index.get(path)
        if record is None or not record.note_type:
            continue
        if record.rel_path.startswith("__templates__/"):
            continue
        ob = obligations.for_type(record.note_type)
        if ob is None or not obligations._is_owed(record, ob):
            continue
        key = record.note_id or record.rel_path
        assert key not in seen, f"{key} counted in two views"
        seen[key] = ob.view


def test_nothing_owed_by_a_type_declaring_none() -> None:
    """The `none` entries must not leak into a count through the predicate."""
    index = Index.build(REPO / "docs")
    for path in index.paths():
        record = index.get(path)
        if record is None or not record.note_type:
            continue
        ob = obligations.for_type(record.note_type)
        if ob is not None and not ob.owed:
            assert not obligations._is_owed(record, ob), (
                f"{record.note_id} owes something despite {record.note_type} "
                "declaring none"
            )


def test_the_renderer_reads_the_count_and_declares_no_kinds() -> None:
    """No vocabulary in TypeScript — the badge draws what it is sent.

    And it must not clamp: the change badge reads 81 in this corpus, which is
    real debt with a deadline. Hiding it in the renderer would be a display
    lying about a gate (ADR-0020 leaves the cutoff open as a parameter).
    """
    src = (
        REPO / "desktop" / "src" / "renderer" / "renderer.ts"
    ).read_text(encoding="utf-8")
    body = src[src.index("async function refreshObligationBadges"):]
    body = body[:body.index("\nfunction ")]
    assert "/api/cockpit/obligations" in body
    assert "n <= 0) return" in body, "the badge renders a zero"
    for clamp in ("Math.min(", "> 99", "'99+'"):
        assert clamp not in body, f"the badge clamps the count with {clamp}"
    for kind in ("triage", "draft", "proposed", "changes-requested"):
        assert f"'{kind}'" not in body, f"the renderer names the state {kind!r}"
