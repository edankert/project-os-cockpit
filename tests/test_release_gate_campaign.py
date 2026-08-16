"""The release gate stays ONE obligation, never sixty (TST-0028).

**Trimmed by FEAT-0107.** Four tests here asserted the `release-gate`
NAVIGATOR GROUP — its label, its rows, its section anchors. That group is
deleted: the suite already lived in the Tests view and now also has the
release page, and a third home was the ISS-0068 duplication this codebase
cites throughout. What survives is the part that was never about the
navigator — the gate is one obligation while a release is preparing, and
zero otherwise.

The gate is the reason PHASE-034 exists, and it is the thing most likely to be
rebuilt into the wall it replaced. Both halves are pinned here: it must
**state** 60, and it must never **sum** to 60.

The first proposal admitted every unchecked Tier 1/2 row to the registry, and
Edwin refused it — *"I am also afraid that this could overwhelm my attention"*.
The registry's own charter agreed: ADR-0027 excludes staleness because
*"counting it is a badge that re-arms itself forever"*, and acceptance rows
re-arm **in bulk**, by the suite's own rule 3.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from project_os_cockpit import acceptance, cockpit, obligations
from project_os_cockpit.index import Index

SUITE = """\
# Tier 1 — Feature Tests

## 1.1 Trainer Compatibility (FEAT-0001)
- [ ] **A:** do a thing.
- [ ] **B:** do another.
- [x] **C:** already walked.

## 1.2 Monetization (FEAT-0002)
- [ ] **D:** a third.

# Tier 2 — Regression Tests

## 2.1 A regression (ISS-0001)
- [~] **E:** settled by decision.

# Tier 3 — Verification Tests

## 3.1 Temporary (FEAT-0001)
- [ ] **F:** does not gate.
"""


def _docs(tmp_path: Path, *, suite: str | None = SUITE,
          release: tuple[str, str, str] | None = None) -> Path:
    d = tmp_path / "docs"
    (d / "tests").mkdir(parents=True)
    if suite is not None:
        (d / "tests" / "ACCEPTANCE_TESTS.md").write_text(suite, encoding="utf-8")
    if release:
        rid, status, version = release
        (d / "releases").mkdir(parents=True, exist_ok=True)
        # `preparing:` on a draft — FEAT-0105 split "open" from "prepared
        # for ship", and only the second gates. A draft alone accumulates.
        prep = 'preparing: "2026-08-16"\n' if status == "draft" else ""
        (d / "releases" / f"{rid}-R.md").write_text(
            f'---\ntype: "[[release]]"\nid: {rid}\ntitle: "R"\n'
            f'status: {status}\nversion: "{version}"\n{prep}---\n',
            encoding="utf-8",
        )
    return d


# ---- 1-4: one obligation, never sixty ------------------------------------


def test_a_draft_release_with_unchecked_checks_owes_exactly_one(
    tmp_path: Path,
) -> None:
    docs = _docs(tmp_path, release=("REL-0001", "draft", "1.0.0"))
    rows = obligations.owed_items(Index.build(docs))["publication"]
    gate = [r for r in rows if r["type"] == obligations.GATE_OBLIGATION_KIND]
    assert len(gate) == 1, "the CAMPAIGN is the obligation, not the checkbox"
    assert gate[0]["verb"] == "Walk"
    assert "3" in gate[0]["title"], gate[0]["title"]


def test_a_released_release_owes_nothing(tmp_path: Path) -> None:
    """With none in preparation, an unchecked suite is the resting state of a
    checklist that unchecks itself whenever code changes — not a debt."""
    docs = _docs(tmp_path, release=("REL-0001", "released", "1.0.0"))
    rows = obligations.owed_items(Index.build(docs))["publication"]
    assert [r for r in rows if r["type"] == obligations.GATE_OBLIGATION_KIND] == []


def test_the_badge_rises_by_at_most_one(tmp_path: Path) -> None:
    """The guard against this feature's own worst outcome.

    A **bound**, not a spot value: the first proposal would have taken
    `your-trainer`'s card from 64 to 124 in answer to a complaint about noise,
    and asserting equality against today's number would not bite if someone
    later routed the rows individually.
    """
    quiet = _docs(tmp_path / "a", release=("REL-0001", "released", "1.0.0"))
    loud = _docs(tmp_path / "b", release=("REL-0001", "draft", "1.0.0"))
    before = obligations.counts(Index.build(quiet))["publication"]
    after = obligations.counts(Index.build(loud))["publication"]
    assert after - before <= 1, (before, after)


# ---- 5-8: what the surface says ------------------------------------------


def test_tier_three_is_shown_and_does_not_gate(tmp_path: Path) -> None:
    docs = _docs(tmp_path, release=("REL-0001", "draft", "1.0.0"))
    gate = acceptance.gate_payload(docs)
    assert all(b["tier"] in (1, 2) for b in gate["blocking"])
    assert acceptance.load(docs).tier(3), "tier 3 exists…"
    assert "Temporary" not in {b["area"] for b in gate["blocking"]}


def test_a_reconciled_row_is_counted_and_never_folded_into_checked(
    tmp_path: Path,
) -> None:
    """ISS-0141's rule. The denominator is what the document holds, and a
    check settled by decision is named rather than quietly removed from both
    halves of the fraction."""
    docs = _docs(tmp_path, release=("REL-0001", "draft", "1.0.0"))
    tier2 = next(t for t in acceptance.payload(docs)["tiers"] if t["tier"] == 2)
    assert tier2["total"] == 1
    assert tier2["checked"] == 0
    assert tier2["reconciled"] == 1
    assert acceptance.gate_payload(docs)["counts"]["tier2"]["unchecked"] == 0


def test_no_suite_says_never_instantiated_not_nothing_blocking(
    tmp_path: Path,
) -> None:
    """Every repo had no suite until 2026-08-10, and conflating the two is
    what made the gate look like it worked for the years it could not fire."""
    docs = _docs(tmp_path, suite=None, release=("REL-0001", "draft", "1.0.0"))
    gate = acceptance.gate_payload(docs)
    assert gate["exists"] is False
    assert gate["blocked"] is False
    rows = obligations.owed_items(Index.build(docs))["publication"]
    assert [r for r in rows if r["type"] == obligations.GATE_OBLIGATION_KIND] == []


def test_the_rule_sentence_is_the_contracts_words(tmp_path: Path) -> None:
    """Quoted verbatim from TESTING.md, with the local reconciliation clause
    BESIDE it rather than folded in — a gate that quotes one rule while
    implementing another is drift wearing the quote as cover."""
    gate = acceptance.gate_payload(_docs(tmp_path))
    assert gate["rule"].startswith("A release is blocked while any Tier 1/Tier 2")
    assert "reconciliation" in gate["local_rule"]
    assert "reconcil" not in gate["rule"], "the contract's sentence is untouched"


# ---- 9: ISS-0173 makes the rows nameable --------------------------------


def test_a_blocking_row_names_its_subject(tmp_path: Path) -> None:
    """The link a scoped gate needs, and it is written bare in every suite in
    the fleet (ISS-0173)."""
    gate = acceptance.gate_payload(_docs(tmp_path))
    assert gate["blocking"], "fixture must block"
    assert all(row["refs"] for row in gate["blocking"]), gate["blocking"]
    assert gate["blocking"][0]["refs"] == ["FEAT-0001"]


@pytest.mark.skipif(
    not (Path.home() / "Dev/repos/your-trainer/docs").is_dir(),
    reason="your-trainer not present",
)
def test_the_measured_repo_still_reports_what_this_phase_measured() -> None:
    """The numbers PHASE-034 stands on, re-taken rather than re-asserted."""
    docs = Path.home() / "Dev/repos/your-trainer/docs"
    gate = acceptance.gate_payload(docs)
    assert gate["exists"] and gate["blocked"]
    assert len(gate["blocking"]) >= 40, len(gate["blocking"])
    assert all(row["refs"] for row in gate["blocking"]), \
        "every blocking row names a subject — 0 of 60 did before ISS-0173"
