"""An exclusion says why, and the page says what it cost ([[TASK-0576]]).

[[FEAT-0142]] criterion 4, the last of its seven. Six were already met — five
delivered under [[FEAT-0129]]'s tasks and one (`chronic`) found true and
guarded by `test_a_deselected_check_stops_blocking_but_keeps_being_counted`.

**Why the reason matters more than the count.** A gate that fell from 59 to 23
because somebody held six features back, rendered as *"23 blocking"* with
nothing beside it, is [[ISS-0241]] (*"89 executed by CI"*, derived from no
observed run) and [[ISS-0243]] (*"90% complete"* over checks with no recorded
result) in a new place: **a number with no recorded cause.** [[ADR-0040]] chose
subtraction over division so the gate would stay conservative; this is the
other half of that argument, which is that the subtraction must be *visible*.

Constructed fixtures throughout: no repo holds a release that names its own
contents yet, so the corpus cannot exercise any of this.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from project_os_cockpit import note_writes, publication
from project_os_cockpit.index import Index

RENDERER = (Path(__file__).resolve().parents[1]
            / "desktop" / "src" / "renderer" / "renderer.ts")


def _repo(tmp: Path, *, features: str = "[]", status: str = "draft",
          held_back: str = "") -> Path:
    """Two done features, one blocking check each, and one open release."""
    docs = tmp / "docs"
    (docs / "releases").mkdir(parents=True)
    (docs / "features" / "f").mkdir(parents=True)
    (docs / "tests" / "acceptance").mkdir(parents=True)
    for fid in ("FEAT-0001", "FEAT-0002"):
        (docs / "features" / "f" / f"{fid}-T.md").write_text(
            f'---\ntype: "[[feature]]"\nid: {fid}\ntitle: "Thing {fid[-1]}"\n'
            f'status: done\n---\n\n# T\n', encoding="utf-8")
        (docs / "tests" / "acceptance" / f"TST-{fid[-4:]}-C.md").write_text(
            f'---\ntype: "[[test]]"\nid: TST-{fid[-4:]}\ntitle: "C {fid}"\n'
            f'level: acceptance\nstatus: active\narea: "A"\nmark: todo\n'
            f'covers: ["[[{fid}]]"]\n---\n\n# C\n', encoding="utf-8")
    (docs / "releases" / "REL-0001-R.md").write_text(
        f'---\ntype: "[[release]]"\nid: REL-0001\ntitle: "R"\n'
        f'status: {status}\nversion: "1.1.0"\nplatform: ""\npreparing: true\n'
        f'features: {features}\n{held_back}updated: "2026-01-01"\n'
        f'---\n\n# R\n', encoding="utf-8")
    return docs


def _fm(docs: Path) -> dict:
    raw = (docs / "releases" / "REL-0001-R.md").read_text(encoding="utf-8")
    return yaml.safe_load(raw.split("---", 2)[1]) or {}


# ---- the refusal ----------------------------------------------------------

def test_a_removal_with_no_reason_is_refused(tmp_path: Path) -> None:
    """**The front door is not where this is enforced.** A rule enforced in
    the renderer is a rule the other front door does not get ([[ISS-0230]]),
    so the refusal lives in `note_writes` and the prompt is a convenience.
    """
    docs = _repo(tmp_path, features='["[[FEAT-0001]]", "[[FEAT-0002]]"]')
    for empty in ("", "   ", "\n"):
        with pytest.raises(note_writes.WriteError) as exc:
            note_writes.release_contents(
                Index.build(docs), "REL-0001", action="remove",
                feature_id="FEAT-0002", reason=empty)
        assert exc.value.status == 400
        assert "reason" in exc.value.message


def test_adding_needs_no_reason(tmp_path: Path) -> None:
    """Only the subtraction has to explain itself. Putting a feature IN a
    release is the default the derived set already expresses."""
    docs = _repo(tmp_path)
    out = note_writes.release_contents(
        Index.build(docs), "REL-0001", action="add", feature_id="FEAT-0001")
    assert out["features"] == ["[[FEAT-0001-T]]"]


# ---- where the reason lives ----------------------------------------------

def test_the_reason_lands_beside_the_selection(tmp_path: Path) -> None:
    """`held_back:` sits in the release note's own frontmatter, next to
    `features:` — one file, one diff. [[ADR-0009]]: notes are the authored
    source of state."""
    docs = _repo(tmp_path, features='["[[FEAT-0001]]", "[[FEAT-0002]]"]')
    note_writes.release_contents(
        Index.build(docs), "REL-0001", action="remove", feature_id="FEAT-0002",
        reason="depends on a backend change that is not deployed")
    fm = _fm(docs)
    assert [f for f in fm["features"]] == ["[[FEAT-0001]]"]
    assert fm["held_back"] == [{
        "id": "FEAT-0002",
        "reason": "depends on a backend change that is not deployed",
        "date": fm["held_back"][0]["date"],
    }]
    assert fm["held_back"][0]["date"], "an exclusion with no date cannot age"


def test_re_adding_a_feature_retires_its_exclusion(tmp_path: Path) -> None:
    """`held_back:` answers *"why is this not in the release"*. A feature that
    IS in the release has no answer to give, so the entry goes rather than
    accumulating a history the field was never asked for. Git holds that."""
    docs = _repo(tmp_path, features='["[[FEAT-0001]]", "[[FEAT-0002]]"]')
    note_writes.release_contents(
        Index.build(docs), "REL-0001", action="remove", feature_id="FEAT-0002",
        reason="slipping a cycle")
    assert len(_fm(docs)["held_back"]) == 1
    note_writes.release_contents(
        Index.build(docs), "REL-0001", action="add", feature_id="FEAT-0002")
    fm = _fm(docs)
    assert fm["held_back"] == [], fm["held_back"]


def test_the_last_exclusion_leaves_an_empty_list_not_a_null(
        tmp_path: Path) -> None:
    """A bare `held_back:` parses as `None`, which every reader would then
    have to special-case. `_set_field` cannot write it — it refuses a key
    whose next line is indented, which is exactly the block being replaced."""
    docs = _repo(tmp_path, features='["[[FEAT-0001]]", "[[FEAT-0002]]"]')
    note_writes.release_contents(
        Index.build(docs), "REL-0001", action="remove", feature_id="FEAT-0002",
        reason="slipping a cycle")
    note_writes.release_contents(
        Index.build(docs), "REL-0001", action="add", feature_id="FEAT-0002")
    raw = (docs / "releases" / "REL-0001-R.md").read_text(encoding="utf-8")
    assert "held_back: []" in raw, raw[:500]
    assert _fm(docs)["held_back"] is not None


def test_a_phase_records_a_reason_per_feature_it_contributed(
        tmp_path: Path) -> None:
    """A phase contributes features and is not stored ([[REQ-0048]] criterion
    2), so holding a phase back holds each of its features back — and each one
    carries the reason, because each one is what a check's `covers:` names."""
    docs = _repo(tmp_path, features='["[[FEAT-0001]]", "[[FEAT-0002]]"]')
    (docs / "phases").mkdir(parents=True, exist_ok=True)
    (docs / "phases" / "PHASE-0001-P.md").write_text(
        '---\ntype: "[[phase]]"\nid: PHASE-0001\ntitle: "P"\nstatus: active\n'
        'order: 1\nfeatures: ["[[FEAT-0001]]", "[[FEAT-0002]]"]\n'
        '---\n\n# P\n', encoding="utf-8")
    note_writes.release_contents(
        Index.build(docs), "REL-0001", action="remove", feature_id="PHASE-0001",
        reason="the whole phase slips")
    assert [r["id"] for r in _fm(docs)["held_back"]] == ["FEAT-0001", "FEAT-0002"]
    assert all(r["reason"] == "the whole phase slips"
               for r in _fm(docs)["held_back"])


# ---- what the page reads --------------------------------------------------

def test_the_page_says_how_many_were_held_back_and_what_it_cost(
        tmp_path: Path) -> None:
    """**The two numbers arrive together or not at all.** Either one alone is
    the shape this phase spent itself removing."""
    docs = _repo(tmp_path, features='["[[FEAT-0001]]"]')
    d = publication.release_payload(tmp_path, Index.build(docs), "REL-0001")
    held = d["contents"]["held_back"]
    assert [r["id"] for r in held] == ["FEAT-0002"]
    assert held[0]["title"] == "Thing 2", "the row is resolved, not a raw id"
    #: One check covered only FEAT-0002, so exactly one stopped gating.
    assert d["gate"]["deselection"] == {"features": 1, "checks": 1}
    assert len(d["gate"]["blocking"]) == 1


def test_the_cost_is_the_size_of_the_subtraction_not_a_second_count(
        tmp_path: Path) -> None:
    """Measured against the same suite the gate reports, so the two can never
    disagree. A second traversal is how two surfaces come to disagree."""
    from project_os_cockpit import acceptance

    docs = _repo(tmp_path, features='["[[FEAT-0001]]"]')
    #: **A third check, so no two of the numbers can coincide.** With two
    #: checks the subtraction (1), the survivors (1) and the cost (1) are all
    #: the same integer, and a `checks: len(blocking)` mutant passes. Three
    #: makes them 1, 2 and 3 — measured, not assumed: the mutant was
    #: constructed and only this shape caught it.
    (docs / "tests" / "acceptance" / "TST-0003-C.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0003\ntitle: "C nobody"\n'
        'level: acceptance\nstatus: active\narea: "A"\nmark: todo\n'
        'covers: []\n---\n\n# C\n', encoding="utf-8")
    index = Index.build(docs)
    suite = acceptance.load(docs, index=index)
    full = len(suite.blocking())
    d = publication.release_payload(tmp_path, index, "REL-0001")
    assert full == 3 and len(d["gate"]["blocking"]) == 2
    assert d["gate"]["deselection"]["checks"] == full - len(d["gate"]["blocking"])
    assert d["gate"]["deselection"]["checks"] == 1


def test_nothing_held_back_reports_no_cost(tmp_path: Path) -> None:
    """A release naming nothing deselects nothing — the invariant eleven
    historical releases depend on — and it must not draw a line about it."""
    docs = _repo(tmp_path)
    d = publication.release_payload(tmp_path, Index.build(docs), "REL-0001")
    assert d["contents"]["held_back"] == []
    assert d["gate"]["deselection"] == {"features": 0, "checks": 0}


def test_a_hand_edited_exclusion_says_it_has_no_reason(tmp_path: Path) -> None:
    """**Reported, not filled in.** `features:` edited by hand produces a
    held-back feature with no entry in `held_back:`, and inventing a plausible
    sentence for it would be the overclaiming this phase exists to remove.
    """
    docs = _repo(tmp_path, features='["[[FEAT-0001]]"]')
    d = publication.release_payload(tmp_path, Index.build(docs), "REL-0001")
    assert d["contents"]["held_back"][0]["reason"] == ""


def test_the_seal_keeps_the_exclusions(tmp_path: Path) -> None:
    """What a release held back is part of what it was measured against: a
    shipped release whose gate was smaller than the repo's must still say what
    made it smaller ([[ADR-0035]] — the record is a fact about the past, and
    that includes the subtraction)."""
    docs = _repo(
        tmp_path, status="released", features='["[[FEAT-0001]]"]',
        held_back=('held_back:\n  - id: "FEAT-0002"\n'
                   '    reason: "no hardware to verify it"\n'
                   '    date: "2026-08-21"\n'))
    d = publication.release_payload(tmp_path, Index.build(docs), "REL-0001")
    assert d["contents"]["kind"] == "frozen"
    assert [r["id"] for r in d["contents"]["held_back"]] == ["FEAT-0002"]
    assert d["contents"]["held_back"][0]["reason"] == "no hardware to verify it"


# ---- the kind, and the control it unlocks --------------------------------

def test_naming_contents_makes_them_chosen_rather_than_derived(
        tmp_path: Path) -> None:
    """**The renderer has always known there were three kinds.** `Remove` is
    guarded on `c.kind !== 'derived'` and a test pins that guard — but nothing
    ever emitted a third kind, so the control was unreachable and a feature
    added through the front door could never be taken back out through it.

    Naming one feature is the semantic jump the compose warning announces;
    this is that jump arriving in the payload.
    """
    docs = _repo(tmp_path)
    d = publication.release_payload(tmp_path, Index.build(docs), "REL-0001")
    assert d["contents"]["kind"] == "derived"
    assert d["contents"]["count"] == 2

    docs = _repo(tmp_path / "b", features='["[[FEAT-0001]]"]')
    d = publication.release_payload(tmp_path / "b", Index.build(docs), "REL-0001")
    assert d["contents"]["kind"] == "chosen"
    assert [r["id"] for r in d["contents"]["rows"]] == ["FEAT-0001"]
    assert d["contents"]["rows"][0]["title"] == "Thing 1"


def test_next_reads_the_selection_of_the_release_it_resolved(
        tmp_path: Path) -> None:
    """`~release/next` is the page a person actually opens, and
    `index.by_id("next")` is `None` — so reading the caller's ARGUMENT left
    the selection empty and the subtraction silently off for the one release
    anybody is preparing.

    The same class as the defect `test_the_held_back_set_is_read_from_the_note`
    guards: a rule that cannot fire, passing every test that does not
    construct the positive case.
    """
    docs = _repo(tmp_path, features='["[[FEAT-0001]]"]')
    d = publication.release_payload(tmp_path, Index.build(docs), "next")
    assert d["id"] == "REL-0001"
    assert d["contents"]["kind"] == "chosen"
    assert [r["id"] for r in d["contents"]["held_back"]] == ["FEAT-0002"]
    assert d["gate"]["deselection"]["checks"] == 1


# ---- the page ------------------------------------------------------------

def test_the_page_never_shows_a_smaller_number_alone() -> None:
    """The count and its cost are one sentence. Two numbers on separate lines
    is how a reader comes to believe one of them explains the other."""
    src = RENDERER.read_text(encoding="utf-8")
    i = src.index("const heldBack = c.held_back")
    block = src[i:i + 900]
    assert "held back" in block and "no longer gating" in block, block[:400]
    assert "deselection?.checks" in block, (
        "the cost is not read from the gate, so the page could report a "
        "number the gate never computed"
    )


def test_an_exclusion_with_no_reason_is_drawn_as_such() -> None:
    src = RENDERER.read_text(encoding="utf-8")
    i = src.index("const heldBack = c.held_back")
    block = src[i:i + 2600]
    assert "no reason recorded" in block, block[-600:]


def test_the_remove_control_asks_why() -> None:
    """And the ask is a convenience, not the rule: `holdFeatureBack` prompts,
    `release_contents` refuses. A caller that skips the prompt gets the same
    answer."""
    src = RENDERER.read_text(encoding="utf-8")
    j = src.index("drop.textContent = 'Remove'")
    assert "holdFeatureBack(" in src[j:j + 500]
    i = src.index("async function holdFeatureBack(")
    body = src[i:i + 900]
    assert "askForText(" in body
    assert "if (reason === null || !reason.trim()) return;" in body, (
        "an empty reason is posted, and the server's refusal becomes an "
        "error toast where nothing needed to happen"
    )


def _code_only(text: str) -> str:
    """`text` with comments removed.

    **The guard fired on a comment the first time it was widened**, and the
    comment was one recording that `markGateRow` had been *deleted* — so the
    note explaining that a write path is gone read as a write path. Stripping
    comments is what makes *"no verdict control on a release surface"* a claim
    about code.
    """
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"^\s*//.*$", "", text, flags=re.M)


def test_a_release_row_does_not_call_a_manual_check_automated() -> None:
    """**The first repair for the control was a different lie.**

    `manual` and `controls` were one parameter, so taking the buttons away
    also took the `is-automated` branch — and all 34 of this repo's checks are
    manual, so 67 rows on `~release/<id>/<ITEM-ID>` printed the word
    `automated` under checks no machine runs. That is [[ISS-0241]] exactly,
    and the row's own fallback comment says so: *"it must not be a claim about
    CI."*

    `manual` comes from the item; `controls` comes from the surface.
    """
    src = RENDERER.read_text(encoding="utf-8")
    sig = re.search(r"function buildCheckRow\(([^)]*)\)", src)
    assert sig, "buildCheckRow moved"
    params = [p.split(":")[0].strip() for p in sig.group(1).split(",")]
    assert params == ["item", "manual", "controls"], params

    #: The two facts must not be read as one: the automated styling keys on
    #: `manual` alone and the buttons on both.
    body = src[sig.start():src.index("\nfunction ", sig.start())]
    assert "if (!manual) row.classList.add('is-automated');" in body
    assert body.count("if (manual && controls) {") == 2, body[:400]

    #: And the release surface derives `manual` from the ITEM — **checked
    #: inside the release region**, not as a whole-file substring. A
    #: whole-file `in src` is satisfied by any comment quoting the string, and
    #: `renderer.ts` already carries a comment quoting the previous round's
    #: assertion; the seventh pass reinstated the round-five defect with one
    #: such comment above it and both tests stayed green.
    decls = [(m.start(), m.group(1))
             for m in re.finditer(r"^(?:async )?function (\w+)", src, re.M)]
    region = ""
    for n, (start, name) in enumerate(decls):
        if name == "buildReleaseItemPage":
            end = decls[n + 1][0] if n + 1 < len(decls) else len(src)
            region = _code_only(src[start:end])
    assert region, "buildReleaseItemPage moved"
    assert "buildCheckRow(item, !item.command, false)" in region


def test_no_write_path_to_a_check_appears_on_the_release_page() -> None:
    """[[ADR-0035]] unweakened — [[TASK-0576]]'s fourth criterion.

    **Scoped to the whole release-page region, not to a window.** The first
    version read `src[i:i + 2600]` and `renderer.ts` runs 469,293 characters
    past that anchor — independent review put a live `askForMark` call at
    anchor + 2621 and the test passed. A universal claim measured over 0.5% of
    the file is the shape this phase exists to remove.

    The region is every release-page render function, bounded by the next
    top-level declaration rather than by a character count.
    """
    src = RENDERER.read_text(encoding="utf-8")
    decls = [(m.start(), m.group(1))
             for m in re.finditer(r"^(?:async )?function (\w+)", src, re.M)]
    #: **Every function that builds or renders a release surface**, bounded by
    #: the next top-level declaration. Named rather than pattern-matched, so
    #: renaming one into existence outside this list is a visible edit here.
    #: **Discovered, not enumerated.** A fixed list catches a function
    #: DISAPPEARING and never one appearing: independent review added
    #: `buildReleaseChecksPanel` calling `askForMark` and the test passed.
    #: Every top-level function whose name mentions a release is in scope, and
    #: the discovered set is asserted against the recorded one — so a **tenth**
    #: is a deliberate edit here rather than a silent widening of the page.
    #: (There are nine. The comment said "a ninth" while the list already held
    #: nine, which is the enumerated version's sentence surviving the rewrite.)
    named = {"mountReleaseGate", "buildGateSection", "composeRelease",
             "holdFeatureBack"}
    subjects = {n for _, n in decls if "elease" in n} | named
    expected = {"renderReleasePage", "renderReleaseItemPage",
                "buildReleasePage", "buildReleaseItemPage",
                "mountReleaseGate", "buildGateSection", "composeRelease",
                "holdFeatureBack", "fillUnreleasedCard"}
    assert subjects == expected, (
        "the set of release surfaces changed: %s appeared, %s went"
        % (sorted(subjects - expected), sorted(expected - subjects))
    )
    #: And the block this task added is inside one of them, checked rather
    #: than assumed — the first version of this test scanned a 2600-character
    #: window that did not even contain the enclosing function.
    anchor = src.index("const heldBack = c.held_back")

    #: **An enumeration, and it must be maintained.** It is not a property:
    #: the seventh pass planted `checkMark(item)` on a release surface, and it
    #: typechecked and left all 18 tests green while the list still named
    #: `markGateRow(`, which is deleted. Every live route to a check write is
    #: named here now, and [[ISS-0254]] owns the durable form — a rule over
    #: the call graph rather than over spellings.
    forbidden = ("askForMark", "walkOneCheck", "/api/notes/mark-check",
                 "/api/notes/retire-check",
                 "gateMark(", "markGateRow(", "retireCheckRow(",
                 "checkMark(", "markCheckRow(", "paintCheckList(")
    covered = False
    for n, (start, name) in enumerate(decls):
        if name not in subjects:
            continue
        end = decls[n + 1][0] if n + 1 < len(decls) else len(src)
        region = _code_only(src[start:end])
        if start <= anchor < end:
            covered = True
        for word in forbidden:
            assert word not in region, (
                "%s appears inside %s() — a release page reports, it does not "
                "record (ADR-0035)" % (word, name)
            )
    assert covered, "the held-back block is not inside any release function"

    #: **The row builder is checked on its ARGUMENT, not on its spelling.**
    #: Listing `buildCheckRow(item)` as a forbidden string caught one call and
    #: nothing else: `buildCheckRow(item, true)`, `(item, manual)` and `(c)`
    #: all passed, and the last is the original defect with one letter
    #: changed. Every call inside a release surface must pass `controls` as a
    #: literal `false`.
    #:
    #: **That covers this helper and not the general case.** The `forbidden`
    #: list above is still an enumeration; [[ISS-0254]] carries the repro and
    #: the durable form.
    calls = 0
    for n, (start, name) in enumerate(decls):
        if name not in subjects:
            continue
        end = decls[n + 1][0] if n + 1 < len(decls) else len(src)
        for call in re.finditer(r"buildCheckRow\(([^;]*?)\)",
                                _code_only(src[start:end])):
            calls += 1
            args = [a.strip() for a in call.group(1).split(",")]
            assert len(args) == 3 and args[2] == "false", (
                "%s() renders a check row with controls — buildCheckRow(%s) "
                "(ADR-0035)" % (name, call.group(1))
            )
    assert calls == 1, (
        "expected exactly one check-row call on a release surface, found %d"
        % calls
    )

    #: And the two deletions are file-wide, which is the stronger claim: a
    #: live-looking helper is how the next caller re-acquires the behaviour a
    #: decision just removed.
    assert "function gateMark" not in src
    assert "function markGateRow" not in src
