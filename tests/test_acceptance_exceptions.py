"""**The exception mark moved from `[!]` to `[-]`** (ADR-0029): Minimal calls
`[-]` *canceled*, and `[!]` *important*, which is now `failed` and blocks. The
CONCEPT here is unchanged — a check that will not be done and is not holding
the release keeps its field and its separate count — so this file reads the
same assertions against a different character.

The exception mark, so far as it is built (TST-0031 / FEAT-0104).

**The interaction is not built yet**, and deliberately: ISS-0175 found that
the rendered document's checkbox order does not match the suite's, so a
control wired to DOM position would write to the wrong check. What is built
and asserted here is the vocabulary and the addressing underneath it.
"""

from __future__ import annotations

from pathlib import Path

from project_os_cockpit import acceptance

SUITE = """\
# Tier 1 — Feature Tests

## 1.1 Area (FEAT-0001)
- [ ] **A:** outstanding.
- [x] **B:** walked.
- [~] **C:** retired by decision.
- [-] **D:** not done, shipping anyway.
"""


def _docs(tmp_path: Path) -> Path:
    d = tmp_path / "docs"
    (d / "tests").mkdir(parents=True)
    (d / "tests" / "ACCEPTANCE_TESTS.md").write_text(SUITE, encoding="utf-8")
    return d


def test_the_four_marks_are_distinct() -> None:
    items = {i.name: i for i in acceptance.parse(SUITE)}
    assert (items["A"].checked, items["A"].reconciled, items["A"].excepted) == (
        False, False, False)
    assert items["B"].checked and not items["B"].excepted
    assert items["C"].reconciled and not items["C"].excepted
    assert items["D"].excepted and not items["D"].reconciled


def test_an_exception_settles_without_being_walked(tmp_path: Path) -> None:
    """`[!]` does not block — it is a decision to ship. It is also not
    `checked`: nobody performed it, and the counts must keep saying so."""
    docs = _docs(tmp_path)
    gate = acceptance.gate_payload(docs)
    assert [b["name"] for b in gate["blocking"]] == ["A"]
    counts = gate["counts"]["tier1"]
    assert counts["unchecked"] == 1
    assert counts["reconciled"] == 1
    assert counts["excepted"] == 1


def test_excepted_is_never_folded_into_reconciled(tmp_path: Path) -> None:
    """Both are non-blocking and there the resemblance stops: `~` is
    permanent, `!` expires with its release. ISS-0141 is the record of what
    conflating two marks costs."""
    tier1 = acceptance.payload(_docs(tmp_path))["tiers"][0]
    assert (tier1["checked"], tier1["reconciled"], tier1["excepted"]) == (1, 1, 1)
    assert tier1["total"] == 4


def test_a_canceled_check_is_still_reached_by_id_after_the_document_went() -> None:
    """`check_map` and `rewrite_check` guarded the DOCUMENT path and went with
    it (ISS-0192): the first mapped a check to its position among rendered
    checkboxes, the second rewrote a row in place by that position.

    The property they were protecting survives and is asserted here instead —
    an excepted check is addressable and stays excepted — but by **id**, which
    is what the migration bought. A position among 542 rendered inputs was
    never a safe address for 579 parsed rows; ISS-0175 is the 37-row record of
    that, and it is now unrepresentable rather than merely worked around.
    """
    items = acceptance.parse(SUITE)
    assert [i.number for i in items] == ["1.1.1", "1.1.2", "1.1.3", "1.1.4"]
    assert [i.mark for i in items] == [" ", "x", "~", "-"]
    excepted = [i for i in items if i.excepted]
    assert len(excepted) == 1 and excepted[0].settled
