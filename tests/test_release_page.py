"""The release page, and the guard that would have caught ISS-0176 (TST-0033).

The page exists because a left-pane row popping a dialog is the wrong shape —
the navigator navigates, the centre pane acts. It also removes the dialog,
which matters more than it sounds: `window.prompt` is not implemented in
Electron and had been dead in **five** places across four shipped features.

Every one of those features had tests on its payload, its write path and its
endpoint. None pressed the button. `test_the_renderer_never_calls_window_prompt`
is the assertion that was missing.
"""

from __future__ import annotations

import inspect
import re
from pathlib import Path

import pytest

from project_os_cockpit import cockpit, publication
from project_os_cockpit.index import Index

RENDERER = (
    Path(__file__).resolve().parents[1]
    / "desktop" / "src" / "renderer" / "renderer.ts"
)
SUITE = (
    "# Tier 1 — Feature Tests\n\n## 1.1 Area (FEAT-0001)\n"
    "- [ ] **A:** do it.\n- [x] **B:** done.\n"
)


def _docs(tmp_path: Path, *, suite: bool = True) -> Path:
    d = tmp_path / "docs"
    (d / "tests").mkdir(parents=True)
    if suite:
        (d / "tests" / "ACCEPTANCE_TESTS.md").write_text(SUITE, encoding="utf-8")
    (d / "features" / "f").mkdir(parents=True)
    (d / "features" / "f" / "FEAT-0001-F.md").write_text(
        '---\ntype: "[[feature]]"\nid: FEAT-0001\ntitle: "A feature"\n'
        "status: done\n---\n", encoding="utf-8",
    )
    return d


def _rel(docs: Path, rid: str, status: str, version: str,
         preparing: str = "", features: str = "[]") -> None:
    d = docs / "releases"
    d.mkdir(parents=True, exist_ok=True)
    body = (
        f'---\ntype: "[[release]]"\nid: {rid}\ntitle: "R"\n'
        f'status: {status}\nversion: "{version}"\nfeatures: {features}\n'
    )
    if preparing:
        body += f'preparing: "{preparing}"\n'
    (d / f"{rid}-R.md").write_text(body + "---\n", encoding="utf-8")


# ---- the payload ---------------------------------------------------------


def test_next_answers_even_with_no_release_note(tmp_path: Path) -> None:
    """The ordinary case: the open release is derived and nothing is written
    until a person declares one."""
    docs = _docs(tmp_path)
    d = publication.release_payload(docs.parent, Index.build(docs), "next")
    assert d["exists"] is False
    assert d["preparing"] is False
    assert d["contents"]["kind"] == "derived"
    assert d["contents"]["count"] == 1


def test_contents_come_from_the_existing_computation(tmp_path: Path) -> None:
    """`unreleased_payload`'s own keys — `items` and `since` — read rather
    than near-missed. A second vocabulary for one computation is how two
    surfaces come to disagree, and the first draft of this invented `rows`
    and `latest` and silently reported nothing."""
    docs = _docs(tmp_path)
    _rel(docs, "REL-0001", "released", "1.0.0")
    d = publication.release_payload(docs.parent, Index.build(docs), "next")
    assert d["contents"]["since"] == "REL-0001"
    assert [r["id"] for r in d["contents"]["rows"]] == ["FEAT-0001"]


def test_a_shipped_release_reports_what_it_named(tmp_path: Path) -> None:
    """The frozen list is the record. Recomputing it would make a shipped
    release's contents drift as the project moved on."""
    docs = _docs(tmp_path)
    _rel(docs, "REL-0001", "released", "1.0.0", features='["[[FEAT-0001]]"]')
    d = publication.release_payload(docs.parent, Index.build(docs), "REL-0001")
    assert d["contents"]["kind"] == "frozen"
    assert d["contents"]["count"] == 1


def test_the_gate_rides_the_page(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    d = publication.release_payload(docs.parent, Index.build(docs), "next")
    assert d["gate"]["exists"] is True
    assert [b["name"] for b in d["gate"]["blocking"]] == ["A"]


def test_no_suite_is_reported_rather_than_read_as_clear(tmp_path: Path) -> None:
    docs = _docs(tmp_path, suite=False)
    d = publication.release_payload(docs.parent, Index.build(docs), "next")
    assert d["gate"]["exists"] is False
    assert d["gate"]["blocked"] is False


def test_the_row_navigates_to_the_page(tmp_path: Path) -> None:
    """Edwin: *"I would have expected that if I selected the Next Release
    item that this would bring up a virtual page."* It used to carry an action
    that popped a dialog — the wrong shape, and dead besides."""
    docs = _docs(tmp_path)
    groups = {
        g["key"]: g for g in cockpit.nav_payload(
            Index.build(docs), "publication", project_root=docs.parent,
        )["groups"]
    }
    nxt = groups["release-next"]
    assert nxt["url"] == "~release/next"
    assert nxt["type"] == "release"


# ---- ISS-0176 ------------------------------------------------------------


def test_the_renderer_never_calls_window_prompt() -> None:
    """**The assertion that was missing for four features.**

    Electron removed `window.prompt` in v3 and this app is on 32. Five call
    sites were dead in the desktop shell — drafting a release, reconciling a
    criterion, filing an issue from a failure, annotating a design, and
    preparing a release — and every one worked in the browser cockpit, which
    is why it went unnoticed for months.

    A comment saying "do not use prompt" would not have caught it. This does.
    """
    src = RENDERER.read_text(encoding="utf-8")
    code = [
        line for line in src.splitlines()
        if "window.prompt" in line
        and not line.lstrip().startswith(("//", "*", "/*"))
    ]
    assert code == [], code


def test_the_replacement_exists_and_is_shared() -> None:
    """One input, not five. The next call site cannot be written the broken
    way by copying a neighbour, because no neighbour does it that way."""
    src = RENDERER.read_text(encoding="utf-8")
    assert "function askForText(" in src
    # Four, not five: `promptPrepareRelease` was deleted by FEAT-0107 — the
    # version field on the release page is the only way to start one now.
    assert src.count("await askForText(") >= 4, src.count("await askForText(")


# ---- ISS-0190: the errand comes before the inventory ----------------------


def _body_of(src: str, signature: str) -> str:
    """The source of one function, bounded by its OWN end.

    Bounding a slice on a distant landmark is how an earlier edit in this
    phase removed 5315 lines of `renderer.ts` in a single replacement — the
    typechecker caught it, and the rule since is that the boundary is
    computed. Brace-counted from the opening `{` of the signature.
    """
    start = src.index(signature)
    depth = 0
    for i in range(src.index("{", start), len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[start:i + 1]
    raise AssertionError(f"{signature} never closes")


def test_the_gate_is_built_before_what_is_in_the_release() -> None:
    """Edwin: *"move the acceptance tests section to the top ... since this
    needs to be completed (the features/issues are things that simply ship
    with this release)"*.

    Asserted on the ORDER OF THE APPENDS inside `buildReleasePage`, which is
    what puts one section above another — not on the order the sections are
    declared, and not on either name appearing in the file.
    """
    body = _body_of(
        RENDERER.read_text(encoding="utf-8"), "function buildReleasePage(",
    )
    gate = body.index("wrap.appendChild(gateSection)")
    # The features list — the section that used to be first.
    contents = body.index("section.appendChild(list);")
    assert gate < contents, (
        "the gate section is appended after the release's contents, so it "
        "renders below them"
    )
    # And it is genuinely the first thing after the header/version controls:
    # nothing else may be appended between them.
    between = body[body.index("wrap.append(start, err);"):gate]
    assert "wrap.append" not in between.replace("wrap.append(start, err);", ""), (
        f"something is appended between the header and the gate: {between!r}"
    )


def test_a_gate_row_wears_the_documents_control_and_no_buttons() -> None:
    """Edwin: *"remove the buttons on the right, if you want you can have the
    checkbox on the left as long as the check box functionality is the same as
    in the .md file."*

    `Pass · Partial · Fail` was a second vocabulary — three verbs against the
    document's six marks — for one act on one check.
    """
    src = RENDERER.read_text(encoding="utf-8")
    assert "function verdictControls(" not in src, (
        "the three verdict buttons are back"
    )
    body = _body_of(src, "function gateGroup(")
    #: **The checkbox half of this is SUPERSEDED, by the same person**
    #: ([[ISS-0244]], 2026-08-20). The instruction above was permissive — *"if
    #: you want you can have the checkbox on the left"* — and the later one is
    #: not: *"it shows the outstanding tests but it shows them with the check
    #: marks, just show them as a list of tst links like the features below."*
    #:
    #: So the two assertions that required a mark token, and required it first,
    #: are gone rather than relaxed. What they were protecting — that a mark,
    #: IF present, is the row's left-hand column and not an afterthought — has
    #: no subject any more: `gateMark` is deleted and the four unsettled lists
    #: drew the same glyph on every row.
    #:
    #: **The half that is not superseded stays, and is the reason this test
    #: exists**: no second vocabulary, and no button on the row. That is
    #: [[ADR-0035]], which nothing here revisits.
    assert "review-btn" not in body, "a button crept back onto the row"
    assert "createElement('button')" not in body, (
        "a control is back on a gate row — a release page reports the gate "
        "and records nothing (ADR-0035)"
    )
    #: The row still reads as a row: a typed id, a title, and a click that
    #: opens the check. Asserted so "no controls" cannot be met by inertness.
    assert "'scoped-row-id mono ov-typed'" in body, (
        "the gate row's id lost the features row's treatment — the shape "
        "Edwin asked for was 'a list of tst links like the features below'"
    )
    assert "navigateTo(item.rel" in body, "the row no longer opens its check"


def test_the_walk_layer_still_writes_through_the_documents_own_path() -> None:
    """*"the same as in the .md file"* means the same dialog and the same
    endpoint, not a lookalike. Both are asserted as USED — the value reaching
    the call — rather than as names appearing somewhere in the function.

    **The gate-row half of this guard is gone, and deliberately** (ADR-0035).
    It asserted that `markGateRow` delegated to `walkOneCheck`; a release page
    no longer writes a check at all, so there is nothing to delegate. That the
    helper stays deleted is asserted in `test_acceptance_marks.py` — here it
    would read as an absence, which is the weakest possible form of the claim.

    What survives is the whole of the original property for the surface that
    *does* write: `~checks` and the check's own note.
    """
    src = RENDERER.read_text(encoding="utf-8")
    body = _body_of(src, "async function walkOneCheck(")
    assert "await askForMark({" in body, body
    assert "'/api/notes/mark-check'" in body, body
    # The reason and the verdict the dialog returned are what is sent. A
    # mutation posting a fixed verdict would pass a name-only check.
    assert "verdict: chosen.verdict" in body and "reason: chosen.reason" in body
    # A refusal is caught and shown. `postJson` THROWS; an `if (!res.ok)`
    # branch here would be unreachable (ISS-0187, on the other caller).
    assert "catch" in body and "showStatus(" in body


def test_the_walk_holds_the_readers_place() -> None:
    """A repaint that moves the reader is the defect ISS-0187/0188/0189 were
    three rounds of.

    Pinned on the ORDER (read, repaint, restore) and on the restore happening
    inside an animation frame as well, because ISS-0188's fix did exactly this
    one frame too early and a source-shape guard could not see it.

    **The `renderReleasePage(releaseId)` assertion is gone** (ADR-0035): it
    pinned the repaint the release page passed in, and the release page no
    longer marks anything. The scroll property itself belongs to
    `walkOneCheck` and is unchanged — it is what `~checks` still relies on.
    """
    src = RENDERER.read_text(encoding="utf-8")
    body = _body_of(src, "async function walkOneCheck(")

    def at(needle: str) -> int:
        # `str.index` raises ValueError when the thing is simply GONE, which
        # is the most likely regression here and the one that would report as
        # a crashed test rather than a failed assertion.
        assert needle in body, f"{needle!r} is not in markGateRow:\n{body}"
        return body.index(needle)

    read = at("const held = docView.scrollTop;")
    repaint = at("await repaint()")
    restore = at("docView.scrollTop = held;")
    frame = at("requestAnimationFrame(")
    assert read < repaint < restore, body[read:]
    assert repaint < frame, "the frame-deferred restore runs before the repaint"
    assert "docView.scrollTop = held" in body[frame:], (
        "the animation frame does not restore the position, so the "
        "synchronous restore is alone and lands before layout"
    )


def test_the_suite_opens_from_a_row_and_not_a_button() -> None:
    """Edwin: *"remove the open the acceptance tests button, just show this as
    a file link instead, similar to how the requirements are shown on that
    page."* Every other file on this page is a row you click."""
    src = RENDERER.read_text(encoding="utf-8")
    # Code lines only. The comment above the replacement quotes the button it
    # replaced, and a guard that a neighbouring sentence can satisfy is the
    # third failure mode this control has produced (ISS-0187).
    live = [
        line for line in src.splitlines()
        if "Open the acceptance tests" in line
        and not line.lstrip().startswith(("//", "*", "/*"))
    ]
    assert live == [], live
    body = _body_of(src, "function buildGateSection(")
    assert "scoped-rowlist" in body, "the suite has no file row"
    assert "fileRow.addEventListener('click'" in body
    assert "navigateTo(`/docs/${gate.rel}`)" in body
    # …and no primary button survives in the section.
    assert "is-primary" not in body, body


def _calls(src: str, opener: str) -> list[str]:
    """Every `opener…)` argument block, brace/paren-counted to its own close."""
    out: list[str] = []
    at = src.find(opener)
    while at != -1:
        depth = 0
        for i in range(at + len(opener) - 1, len(src)):
            if src[i] in "({":
                depth += 1
            elif src[i] in ")}":
                depth -= 1
                if depth == 0:
                    out.append(src[at:i + 1])
                    break
        at = src.find(opener, at + 1)
    return out


def test_no_gate_group_says_nothing_when_it_is_empty() -> None:
    """`None.` is on TASK-0318's contentless list, and an empty gate group is
    usually the *good news* on the page — it should be able to say so.

    Every group that renders a heading is checked, so a fourth group added
    next month is covered without this test being edited. The two collapsed
    groups are exempt by construction: their `<details>` only exists when they
    have rows, so their empty branch is unreachable.
    """
    body = _body_of(
        RENDERER.read_text(encoding="utf-8"), "function buildGateSection(",
    )
    headed = [c for c in _calls(body, "gateGroup({") if "heading" in c]
    assert len(headed) >= 2, f"the sweep found {len(headed)} headed groups"
    mute = [c for c in headed if not re.search(r"\bempty\b", c)]
    assert mute == [], mute


def test_the_gate_breakdown_is_lossless_and_sums_to_its_list() -> None:
    """[[TASK-0503]]: *"Replace the sixty-row blocking wall with a breakdown by
    area… Lossless: the full list stays reachable through the links, and the
    count in the heading must equal the number of rows behind them."*

    Measured on `your-trainer`'s **working tree** on 2026-08-20 (not `HEAD`, where that repo carries zero
    command-bearing checks and no automated section at all — corrected after
    independent review): **59 blocking rows across 17
    areas**, and the shape is what makes the tally worth drawing —
    `Trainer Compatibility Verification` holds 20 and `Monetization &
    Licensing` 11, so two areas are more than half the gate.

    The property asserted here is the one that can silently break: the parts
    must add up. A breakdown that drops a row is indistinguishable from a
    shorter gate, which is the direction a release page must never be wrong in.
    """
    src = RENDERER.read_text(encoding="utf-8")
    body = _body_of(src, "function gateAreaBreakdown(")

    #: **Every row is counted exactly once**, and the guard is on the loop's
    #: SHAPE rather than a list of forbidden words (independent review,
    #: 2026-08-20: `if (!item.area) continue;` slipped straight past the word
    #: list and the suite stayed green).
    #:
    #: The loop body must be a single unconditional accumulation. Anything
    #: that can skip an iteration — `continue`, an early `return`, a `break`,
    #: or a slice/filter on the collection — makes the parts stop summing to
    #: the list, and a breakdown that drops rows is indistinguishable from a
    #: shorter gate.
    loop = re.search(r"for \(const item of ([^)]*)\) \{(.*?)\n  \}", body, re.S)
    assert loop, "the tally is no longer a plain for-of over every item"
    assert loop.group(1).strip() == "items", (
        f"the tally iterates something other than the full list: "
        f"{loop.group(1)!r}"
    )
    inner = loop.group(2)
    for escape in ("continue", "return", "break"):
        assert not re.search(r"\b%s\b" % escape, inner), (
            f"`{escape}` inside the tally loop — an iteration that can be "
            f"skipped is a row that can vanish from the breakdown: {inner!r}"
        )
    #: Exactly one place increments, so there is no second path to miscount.
    assert inner.count("byArea.set(") == 1, inner
    #: **And the increment is UNCONDITIONAL** (re-review 2026-08-20).
    #: `if (area) byArea.set(...)` has no escape keyword, iterates every item
    #: and holds exactly one `set(` — and drops the five no-area rows on
    #: `your-trainer`'s `New` group. Forbidding the escapes was never the
    #: property; running for every row is.
    assert not re.search(r"^(?!\s*(?://|\*)).*\bif\b", inner, re.M), (
        "a branch inside the tally loop — the accumulation must run for every "
        f"row, not most of them: {inner!r}"
    )
    #: And the list itself is still rendered: the tally goes in FRONT of it.
    gg = _body_of(src, "function gateGroup(")
    assert "gateAreaBreakdown(items)" in gg
    assert gg.index("gateAreaBreakdown(items)") < gg.index("gate-rowlist"), (
        "the breakdown is rendered after the rows, so it is a summary of "
        "something already scrolled past"
    )
    #: Each part addresses the rows it counted, and the filter is in the URL —
    #: a click-only filter cannot be linked to or reopened (ISS-0203).
    assert "~checks/area/${encodeURIComponent(area)}" in body


def test_the_area_filter_lives_in_the_address() -> None:
    """The `~checks/area/<area>` route, and the reason it is a route
    ([[TASK-0503]], on [[ISS-0203]]'s rule).

    Also: the filter is assigned **unconditionally**. Setting it only when
    non-empty would leave the previous page's area applied to a bare
    `~checks` — the sticky filter ISS-0203 took off the tier axis.
    """
    src = RENDERER.read_text(encoding="utf-8")
    assert "~checks\\/area\\/(.+)$" in src or "~checks\\/area" in src, (
        "no area route — the breakdown's links have nowhere to go"
    )
    i = src.index("checkFilters.areas = area")
    line = src[i:src.index("\n", i)]
    assert "new Set()" in line, (
        f"the area filter is not cleared on a bare ~checks: {line!r}"
    )


def test_the_breakdown_chip_opens_rows_that_exist() -> None:
    """A part that counts rows and then opens nothing is worse than no part at
    all (independent review, 2026-08-20).

    `gateAreaBreakdown` keyed an absent area under an em-dash and navigated to
    `~checks/area/%E2%80%94`, while `checkMatches` compares
    `f.areas.has(item.area || '')`. Five rows on `your-trainer`'s `New` group
    sat behind a chip that matched **zero** of them — on the one surface whose
    whole promise is that each part opens exactly what it counted.

    The em-dash is a label applied at render; the key is the raw value, so the
    two sides of the round trip cannot disagree.
    """
    src = RENDERER.read_text(encoding="utf-8")
    body = _body_of(src, "function gateAreaBreakdown(")
    tally = re.search(r"const area = \(item\.area \|\| ''\)\.trim\(\)(.*)?;", body)
    assert tally, body[:400]
    assert "\\u2014" not in (tally.group(1) or ""), (
        "the tally KEY still falls back to an em-dash, so the chip's filter "
        "will not match the rows it counted"
    )
    #: The label may show one; the address must carry the raw key.
    assert "name.textContent = area || '\\u2014'" in body, (
        "the empty area has no visible label"
    )
    assert "~checks/area/${encodeURIComponent(area)}" in body

    #: And the round trip is asserted against the filter's own comparison, so
    #: this fails if either side changes independently.
    m = re.search(r"f\.areas\.has\(item\.area \|\| ''\)", src)
    assert m, (
        "checkMatches no longer compares `item.area || ''` — the breakdown's "
        "key and the filter's key have drifted apart"
    )


def test_the_release_shows_the_tests_owed_for_its_own_contents() -> None:
    """[[TASK-0504]]. Edwin: *"these should either show a list of open tsts or
    suggest something else."*

    **The predicate is settledness, not `status:`** — and that is the whole
    difficulty. An acceptance check sits at `status: active` for its entire
    life, because the verdict lives in `mark:` and the ledger ([[ADR-0037]]).
    Filtering on status returns every check covering a release feature,
    settled or not. Measured on `your-trainer`'s working tree, 2026-08-20:
    **94 by status, 3 by settledness.** The first is an inventory; only the
    second is work, and shipping the first would have been a 94-row wall
    beside a gate that says 59.
    """
    from project_os_cockpit import publication

    src = inspect.getsource(publication._open_tests_for_contents)
    assert "if item.settled:" in src and "continue" in src, (
        "the open-tests list no longer filters on settledness — a status "
        "filter returns settled checks too, because an acceptance check is "
        "`active` for life"
    )
    #: Scoped to the release's contents, or it is just the gate again.
    assert "content_ids" in src and "FEAT-" in src

    #: And the rendered rows are links, not marks (ADR-0035 / ISS-0244).
    #: Located by its own first line rather than by a containing function:
    #: the block lives in `renderReleaseItemPage`, and anchoring on
    #: `renderReleasePage` matched a DIFFERENT, earlier function whose body
    #: ends well above it — a guard that would have failed for a reason with
    #: nothing to do with the feature.
    rsrc = RENDERER.read_text(encoding="utf-8")
    i = rsrc.index("const openTests = d.open_tests")
    block = rsrc[i:i + 2600]
    assert "'scoped-row-id mono ov-typed'" in block, "the id is not a typed link"
    for control in ("acc-mark", "gate-mark", "MARK_GLYPH", "createElement('button')"):
        assert control not in block, (
            f"`{control}` on the open-tests rows — a release page reports and "
            "records nothing (ADR-0035)"
        )
    #: It must say how it differs from the gate: 3 beside 59 reads as a bug
    #: unless the page explains which population each counts.
    assert "every unsettled check in the repo" in block, (
        "the section does not distinguish itself from the gate's count"
    )
