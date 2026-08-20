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


# ---- wired end to end (FEAT-0129) -----------------------------------------

def test_a_release_that_names_contents_subtracts_from_its_own_gate(
        tmp_path: Path) -> None:
    """[[FEAT-0129]]: *"with contents named, the gate reports what blocks THIS
    release"* — and [[ADR-0040]] says how: **selection subtracts.**

    A release that names contents has, by naming them, held back every derived
    feature it did not name. `blocking_minus` then drops a check only when
    **every** feature it covers was held back.

    Built as a fixture rather than measured on the corpus, but the wiring was
    proved against `your-trainer` in both directions: holding back 29 features
    that carry no blocking checks changes nothing (59 → 59), and holding back
    the one feature that carries a blocking check drops exactly it (59 → 58).
    """
    from project_os_cockpit import publication
    from project_os_cockpit.index import Index

    docs = tmp_path / "docs"
    (docs / "releases").mkdir(parents=True)
    (docs / "features" / "f").mkdir(parents=True)
    (docs / "tests" / "acceptance").mkdir(parents=True)
    for fid in ("FEAT-0001", "FEAT-0002"):
        (docs / "features" / "f" / f"{fid}-T.md").write_text(
            f'---\ntype: "[[feature]]"\nid: {fid}\ntitle: "T"\n'
            f'status: done\n---\n\n# T\n', encoding="utf-8")
        (docs / "tests" / "acceptance" / f"TST-{fid[-4:]}-C.md").write_text(
            f'---\ntype: "[[test]]"\nid: TST-{fid[-4:]}\ntitle: "C {fid}"\n'
            f'level: acceptance\nstatus: active\narea: "A"\nmark: todo\n'
            f'covers: ["[[{fid}]]"]\n---\n\n# C\n', encoding="utf-8")

    def gate(features: str) -> int:
        (docs / "releases" / "REL-0001-R.md").write_text(
            f'---\ntype: "[[release]]"\nid: REL-0001\ntitle: "R"\n'
            f'status: draft\nversion: "1.1.0"\nplatform: ""\npreparing: true\n'
            f'features: {features}\n---\n\n# R\n', encoding="utf-8")
        payload = publication.release_payload(
            tmp_path, Index.build(docs), "REL-0001")
        return len(payload["gate"].get("blocking") or [])

    #: Naming nothing keeps the whole-suite gate — the invariant eleven
    #: historical releases depend on.
    assert gate("[]") == 2
    #: Naming one holds the other back, and only its check drops.
    assert gate('["[[FEAT-0001]]"]') == 1
    #: Naming both holds nothing back.
    assert gate('["[[FEAT-0001]]", "[[FEAT-0002]]"]') == 2


def test_the_held_back_set_is_read_from_the_note(tmp_path: Path) -> None:
    """`_releases()` builds id/title/status/version/date/platform and **no
    `features` key**, so the first wiring read `held.get("features")`, got
    `None` every time, and the subtraction could never fire.

    The invariant test passed either way — it is the **positive** case that
    caught it. Asserted on the source so the shortcut cannot come back.
    """
    import inspect

    from project_os_cockpit import publication

    src = inspect.getsource(publication.release_payload)
    #: **Narrowed to the block it is about.** A blanket
    #: `'held.get("features")' not in src` fails, and correctly: the FROZEN
    #: branch reads exactly that, because a shipped release's contents are its
    #: own hand-written list. Fifth over-broad text match this session — a
    #: claim has to name the code it is a claim about.
    start = src.index("named = {")
    block = src[start:src.index("}", start) + 1]
    assert "_rel_rec.frontmatter" in block, (
        f"the held-back set is not read from the release NOTE: {block!r}"
    )
    assert "held.get(" not in block, (
        "the held-back set reads the `_releases()` dict, which carries no "
        "`features` key — so the subtraction can never fire"
    )


def test_a_deselected_check_stops_blocking_but_keeps_being_counted(tmp_path: Path) -> None:
    """[[FEAT-0142]] criterion 5: *"`chronic` still counts an excluded check.
    It stops blocking; it does not stop being counted."*

    **True today by call-ordering, guarded by nothing until now.** `delta()`
    computes `blocking = current.blocking()` — the *full* list — while the gate
    reports `blocking_minus(deselected)`. So the two answer different questions
    and a held-back check keeps appearing in the delta's buckets.

    That is correct and fragile. Someone tidying `delta()` to "use the same
    list as the gate" would make the chronic bucket shrink whenever a feature
    is held back — silently, and in the direction that flatters. [[ADR-0028]]'s
    chronic count exists precisely so a row that stops blocking does not also
    stop being *visible*, and `blocking_minus`'s own docstring names emptying
    it as the reason ADR-0040 rejected the divide reading.

    Asserted on the mechanism rather than on a rendered number: `delta` must
    take its rows from the unsubtracted suite.
    """
    import inspect

    src = inspect.getsource(acceptance.delta)
    assert "current.blocking()" in src, (
        "delta() no longer reads the full blocking list; if it now uses "
        "blocking_minus, every held-back check silently leaves the chronic "
        "bucket and long-carried debt stops being counted (FEAT-0142 c5)"
    )
    assert "blocking_minus" not in src, (
        "delta() is subtracting; chronic must count what the gate excludes"
    )

    #: And behaviourally: the same suite, deselected, still yields the row.
    s = _suite(tmp_path, [("TST-0001", ["FEAT-0001"]), ("TST-0002", ["FEAT-0002"])])
    assert len(s.blocking_minus({"FEAT-0001"})) == 1, "the gate should drop it"
    split = acceptance.delta(s, None)
    counted = {i.note_id for i in split["chronic"]}
    assert "TST-0001" in counted, (
        f"the held-back check left the chronic bucket: {sorted(counted)}"
    )
    assert len(counted) == 2, counted
