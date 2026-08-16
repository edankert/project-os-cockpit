"""The exception mark, so far as it is built (TST-0031 / FEAT-0104).

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
- [!] **D:** not done, shipping anyway.
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


def test_the_check_map_carries_addresses_and_no_dom_index() -> None:
    """ISS-0175: `your-trainer` parses 579 checks and renders 542 inputs, so
    the Nth-box-is-the-Nth-line assumption is false by 37 and everything after
    the first divergence is attributed to the wrong row. The map therefore
    carries addresses only, until that is fixed."""
    rows = acceptance.check_map(SUITE)
    assert [r["number"] for r in rows] == ["1.1.1", "1.1.2", "1.1.3", "1.1.4"]
    assert [r["mark"] for r in rows] == [" ", "x", "~", "!"]
    assert all("index" not in r for r in rows), \
        "a DOM index here would be a correspondence that does not hold"


def test_rewriting_to_an_exception_keeps_the_name_check(tmp_path: Path) -> None:
    out = acceptance.rewrite_check(
        SUITE, "1.1.1", name="A", mark="!", note="_(exception)_",
    )
    assert "- [!] **A:**" in out
    assert acceptance.parse(out)[0].excepted is True
