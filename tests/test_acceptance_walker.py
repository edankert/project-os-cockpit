"""The walker ticks what it walked and nothing else (TST-0029 / FEAT-0103).

A walker that writes the wrong row is worse than one that writes nothing, and
a walker that ticks on failure manufactures the claim the suite exists to make.
Both fail silently. This pins the write.

The dangerous one is `test_editing_a_row_above_does_not_move_the_target`: a
global-index implementation passes every other assertion here and fails only
that one — against a real corpus, quietly, on someone else's afternoon.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from project_os_cockpit import acceptance, cockpit, note_writes, publication
from project_os_cockpit.index import Index

SUITE = """\
# Tier 1 — Feature Tests

## 1.1 Trainer Compatibility (FEAT-0001)
- [ ] **Alpha:** plug in the trainer and pedal.
- [ ] **Beta:** feel the resistance change.
- [x] **Gamma:** already walked.

## 1.2 Monetization (FEAT-0002)
- [ ] **Delta:** buy the thing.
- [~] **Epsilon:** settled by decision.

# Tier 3 — Verification Tests

## 3.1 Temporary (FEAT-0001)
- [ ] **Zeta:** does not gate.
"""


def _docs(tmp_path: Path, suite: str = SUITE) -> Path:
    d = tmp_path / "docs"
    (d / "tests").mkdir(parents=True)
    (d / "tests" / "ACCEPTANCE_TESTS.md").write_text(suite, encoding="utf-8")
    return d


def _suite_text(docs: Path) -> str:
    return (docs / "tests" / "ACCEPTANCE_TESTS.md").read_text(encoding="utf-8")


def _unchecked(docs: Path) -> int:
    s = acceptance.load(docs)
    return sum(1 for i in s.items if i.tier in (1, 2) and not i.settled)


# ---- 1-3: what each outcome writes --------------------------------------


def test_a_pass_ticks_the_row_and_names_who_walked_it(tmp_path: Path) -> None:
    """REQ-0028: *"`- [x]` says something was ticked; `accepted in cockpit
    run, user:edwin` says who stood behind it."*"""
    docs = _docs(tmp_path)
    note_writes.walk_check(
        docs, "1.1.1", name="Alpha", outcome="pass", actor="user:edwin",
    )
    line = [l for l in _suite_text(docs).splitlines() if "Alpha" in l][0]
    assert line.startswith("- [x]")
    assert "walked" in line and "user:edwin" in line


def test_a_fail_leaves_the_row_unticked_and_says_what_went_wrong(
    tmp_path: Path,
) -> None:
    """A failed walk is evidence of a DEFECT, not of progress. Ticking on
    failure would manufacture the claim the suite exists to make."""
    docs = _docs(tmp_path)
    note_writes.walk_check(
        docs, "1.1.1", name="Alpha", outcome="fail",
        evidence="resistance never changed", actor="user:edwin",
    )
    line = [l for l in _suite_text(docs).splitlines() if "Alpha" in l][0]
    assert line.startswith("- [ ]"), line
    assert "FAILED" in line and "resistance never changed" in line
    assert _unchecked(docs) == 3, "a failure does not reduce what is blocking"


def test_a_skip_writes_nothing_at_all(tmp_path: Path) -> None:
    """A check nobody performed leaves no trace, because a trace is a claim."""
    docs = _docs(tmp_path)
    before = _suite_text(docs)
    result = note_writes.walk_check(docs, "1.1.1", name="Alpha", outcome="skip")
    assert result["written"] is False
    assert _suite_text(docs) == before


# ---- 4-5: the address ---------------------------------------------------


def test_editing_a_row_above_does_not_move_the_target(tmp_path: Path) -> None:
    """**The assertion a global-index walker fails and nothing else catches.**

    `check-toggle` addresses a checkbox by its ordinal within the whole file.
    The real suite has 542 of them, so any edit above a row shifts every index
    below it and the walker writes to whichever row now sits there.
    """
    docs = _docs(tmp_path, SUITE.replace(
        "## 1.1 Trainer Compatibility (FEAT-0001)\n",
        "## 1.1 Trainer Compatibility (FEAT-0001)\n- [ ] **Inserted:** new first check.\n",
    ))
    note_writes.walk_check(docs, "1.1.3", name="Beta", outcome="pass")
    lines = _suite_text(docs).splitlines()
    assert [l for l in lines if "Beta" in l][0].startswith("- [x]")
    assert [l for l in lines if "Inserted" in l][0].startswith("- [ ]"), \
        "the inserted row must be untouched"


def test_a_name_that_no_longer_matches_is_refused(tmp_path: Path) -> None:
    """The caller acts on what it last read; the file may have moved."""
    docs = _docs(tmp_path)
    with pytest.raises(note_writes.WriteError) as err:
        note_writes.walk_check(docs, "1.1.1", name="Not Alpha", outcome="pass")
    assert "moved underneath" in str(err.value)
    assert _unchecked(docs) == 3


def test_an_unresolvable_address_is_refused(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    with pytest.raises(note_writes.WriteError):
        note_writes.walk_check(docs, "9.9.9", name="Alpha", outcome="pass")


# ---- 6-7: the two refusals that protect meaning -------------------------


def test_a_reconciled_row_is_refused(tmp_path: Path) -> None:
    """`- [~]` means settled by a decision recorded on its own line
    (ISS-0141). Walking one would erase the distinction the mark makes."""
    docs = _docs(tmp_path)
    with pytest.raises(note_writes.WriteError) as err:
        note_writes.walk_check(docs, "1.2.2", name="Epsilon", outcome="pass")
    assert "reconciled" in str(err.value)
    assert "- [~]" in _suite_text(docs)


def test_a_stale_write_is_refused(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    with pytest.raises(note_writes.WriteError):
        note_writes.walk_check(
            docs, "1.1.1", name="Alpha", outcome="pass", mtime=1.0,
        )


def test_an_unknown_outcome_is_refused(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    with pytest.raises(note_writes.WriteError):
        note_writes.walk_check(docs, "1.1.1", name="Alpha", outcome="maybe")


# ---- 8: the round trip --------------------------------------------------


def test_walking_a_check_moves_the_count_by_exactly_one(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    assert _unchecked(docs) == 3
    note_writes.walk_check(docs, "1.1.1", name="Alpha", outcome="pass")
    assert _unchecked(docs) == 2
    note_writes.walk_check(docs, "1.2.1", name="Delta", outcome="pass")
    assert _unchecked(docs) == 1


# ---- 9: declaring a release ---------------------------------------------


def _release(docs: Path, rid: str, status: str, version: str) -> None:
    d = docs / "releases"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{rid}-R.md").write_text(
        f'---\ntype: "[[release]]"\nid: {rid}\ntitle: "R"\n'
        f'status: {status}\nversion: "{version}"\n---\n', encoding="utf-8",
    )


def test_declaring_a_release_creates_a_draft(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    _release(docs, "REL-0001", "released", "1.0.0")
    index = Index.build(docs)
    result = note_writes.create_release(index, docs, title="v1.1.0", version="1.1.0")
    assert result["id"] == "REL-0002"
    fresh = Index.build(docs)
    prep = publication.preparing(fresh)
    assert prep and prep["version"] == "1.1.0" and prep["status"] == "draft"


def test_a_version_at_or_below_the_newest_released_is_refused(
    tmp_path: Path,
) -> None:
    """That is the overtaken-draft state FEAT-0102 already works around;
    creating one by hand manufactures it."""
    docs = _docs(tmp_path)
    _release(docs, "REL-0001", "released", "2.1.6")
    index = Index.build(docs)
    with pytest.raises(note_writes.WriteError) as err:
        note_writes.create_release(index, docs, title="v2.0.2", version="2.0.2")
    assert "at or below" in str(err.value)


def test_a_second_release_in_preparation_is_refused(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    _release(docs, "REL-0001", "draft", "1.1.0")
    index = Index.build(docs)
    with pytest.raises(note_writes.WriteError) as err:
        note_writes.create_release(index, docs, title="v1.2.0", version="1.2.0")
    assert "already in preparation" in str(err.value)


def test_a_bad_version_is_refused(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    with pytest.raises(note_writes.WriteError):
        note_writes.create_release(Index.build(docs), docs, title="next", version="next")


# ---- 10-12: the gate lists what it counts -------------------------------


def _gate_group(docs: Path) -> dict | None:
    groups = cockpit.nav_payload(
        Index.build(docs), "publication", project_root=docs.parent,
    )["groups"]
    return next((g for g in groups if g["key"] == "release-gate"), None)


def test_the_gate_lists_individual_checks_not_area_counts(
    tmp_path: Path,
) -> None:
    """Edwin, after the count shipped: *"I still don't seem to be able to see
    … the current set."*"""
    group = _gate_group(_docs(tmp_path))
    assert [i["id"] for i in group["items"]] == ["1.1.1", "1.1.2", "1.2.1"]
    assert [i["title"] for i in group["items"]] == ["Alpha", "Beta", "Delta"]


def test_the_stated_number_equals_the_rows_listed(tmp_path: Path) -> None:
    group = _gate_group(_docs(tmp_path))
    assert "3 unchecked" in group["label"]
    assert len(group["items"]) == 3


def test_a_row_links_to_its_own_section(tmp_path: Path) -> None:
    """The anchors have existed since the suite was first rendered and nothing
    used one, so every row opened a 1082-line file at the top."""
    group = _gate_group(_docs(tmp_path))
    url = group["items"][0]["url"]
    assert "#" in url, url
    assert url.endswith("#11-trainer-compatibility-feat-0001"), url


def test_the_gate_still_contributes_one_obligation_never_sixty(
    tmp_path: Path,
) -> None:
    """Listing the checks is a RENDERING decision. It must not put them back
    on a badge — ADR-0028, and the bound TST-0028 asserts."""
    from project_os_cockpit import obligations

    docs = _docs(tmp_path)
    _release(docs, "REL-0001", "draft", "1.0.0")
    index = Index.build(docs)
    rows = obligations.owed_items(index)["publication"]
    gate = [r for r in rows if r["type"] == obligations.GATE_OBLIGATION_KIND]
    assert len(gate) == 1


def test_the_controls_live_where_their_subject_is(tmp_path: Path) -> None:
    """**Rewritten.** Both controls used to sit on the gate's header, and
    Edwin said the walk button *"looks totally out of place there"*.

    A header is the name of a set, not a place to act on one of its members.
    `Walk` is the action on the gate's OBLIGATION and rides that row in
    `Needs you`; `Prepare release…` belongs to the rung that holds the
    releases, because its subject is the release list.
    """
    docs = _docs(tmp_path)
    groups = {
        g["key"]: g for g in cockpit.nav_payload(
            Index.build(docs), "publication", project_root=docs.parent,
        )["groups"]
    }
    assert "walk" not in groups["release-gate"]
    assert "prepare_release" not in groups["release-gate"]
    # Nothing in preparation, and no release rung at all in this fixture —
    # so the control has nowhere to live yet, which is correct.
    _release(docs, "REL-0001", "released", "1.0.0")
    groups = {
        g["key"]: g for g in cockpit.nav_payload(
            Index.build(docs), "publication", project_root=docs.parent,
        )["groups"]
    }
    assert groups["rung-release"]["prepare_release"] is True


def test_the_walk_routes_are_loopback_guarded() -> None:
    src = (
        Path(__file__).resolve().parents[1]
        / "src" / "project_os_cockpit" / "server.py"
    ).read_text(encoding="utf-8")
    for handler in ("_serve_walk_check", "_serve_release_prepare"):
        body = src.split(f"def {handler}(")[1].split("\n        def ")[0]
        assert "_require_loopback" in body, handler
