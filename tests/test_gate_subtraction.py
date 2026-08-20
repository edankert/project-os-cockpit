"""`blocking_minus` — selection subtracts, it never divides ([[TASK-0512]] under
[[ADR-0040]]).

Constructed input throughout. No release names contents yet — the picker is
[[TASK-0511]]/[[TASK-0558]] — so the corpus cannot exercise the rule at all,
and a guard built on it would be a guard that never fires.
"""

from __future__ import annotations

from pathlib import Path

from project_os_cockpit import acceptance
from project_os_cockpit.index import Index


def _suite(tmp: Path, rows: list[tuple[str, list[str]]]) -> acceptance.Suite:
    """`rows` is (id, covers). Every check is unwalked, so all of them block."""
    docs = tmp / "docs"
    (docs / "tests" / "acceptance").mkdir(parents=True)
    for n, (tid, covers) in enumerate(rows, start=1):
        refs = ", ".join(f'"[[{c}]]"' for c in covers)
        (docs / "tests" / "acceptance" / f"{tid}.md").write_text(
            f'---\ntype: "[[test]]"\nid: {tid}\ntitle: "Check {n}"\n'
            f'level: acceptance\nstatus: active\narea: "Area"\nmark: todo\n'
            f'covers: [{refs}]\n---\n\n# Check {n}\n', encoding="utf-8")
    return acceptance.load(docs, index=Index.build(docs))


def test_nothing_held_back_moves_no_gate(tmp_path: Path) -> None:
    """**The invariant the task states**: *"must not widen or narrow any
    existing release's gate: absence of named contents keeps the whole-suite
    gate."* Eleven historical releases depend on it.
    """
    s = _suite(tmp_path, [("TST-0001", ["FEAT-0001"]), ("TST-0002", [])])
    assert len(s.blocking_minus(None)) == len(s.blocking())
    assert len(s.blocking_minus(set())) == len(s.blocking())


def test_a_check_covering_only_held_back_features_drops(tmp_path: Path) -> None:
    s = _suite(tmp_path, [("TST-0001", ["FEAT-0001"]), ("TST-0002", ["FEAT-0002"])])
    kept = {i.note_id for i in s.blocking_minus({"FEAT-0001"})}
    assert kept == {"TST-0002"}


def test_the_mixed_cell_still_gates(tmp_path: Path) -> None:
    """**The cell a subtraction rule gets wrong.** A check covering one held-back
    feature and one carried one still gates — any selected subject is enough.

    Written before the rule, and it is the reason the rule reads
    `not feats <= deselected` rather than testing intersection.
    """
    s = _suite(tmp_path, [("TST-0001", ["FEAT-0001", "FEAT-0002"])])
    assert len(s.blocking_minus({"FEAT-0001"})) == 1, (
        "a check covering a carried feature was dropped because it ALSO "
        "covers a held-back one"
    )
    #: …and it drops only when EVERY feature it names is held back.
    assert len(s.blocking_minus({"FEAT-0001", "FEAT-0002"})) == 0


def test_a_check_with_no_subject_always_gates(tmp_path: Path) -> None:
    """The fail-closed clause `blocking_for` already carries: a check nobody
    can attribute cannot be discharged by holding anything back, so it gates
    the last item there is.
    """
    s = _suite(tmp_path, [("TST-0001", [])])
    assert len(s.blocking_minus({"FEAT-0001"})) == 1


def test_selection_cannot_reach_a_non_feature_subject(tmp_path: Path) -> None:
    """A check covering an `ISS-*`, `REQ-*` or `PHASE-*` is untouched — no
    feature list speaks for it. **20 of `your-trainer`'s 59 blocking rows are
    in that class** (18 covering only ISS/PHASE, 2 with no `covers:` at all),
    so this is most of what a naive rule would have thrown away.
    """
    s = _suite(tmp_path, [
        ("TST-0001", ["ISS-0001"]),
        ("TST-0002", ["PHASE-0001"]),
        ("TST-0003", ["FEAT-0001", "ISS-0002"]),
    ])
    #: Even holding back every feature named anywhere here.
    kept = {i.note_id for i in s.blocking_minus({"FEAT-0001"})}
    assert kept == {"TST-0001", "TST-0002", "TST-0003"}, kept
