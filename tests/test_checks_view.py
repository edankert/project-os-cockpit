"""The suite is a view, and it is the same list (FEAT-0114 / TASK-0464, TASK-0465).

Edwin's contract is verbatim and is the thing to hold: *"We can then present
them still as the same list with the same tick options for me to go through
before a release."* So the assertions are about **continuity** — the shape a
reader knew, the marks they knew — and about the one property four rounds of
work were spent buying on the old surface (ISS-0187..0189): a repaint that does
not move the reader.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from project_os_cockpit import acceptance
from project_os_cockpit.index import Index

REPO_ROOT = Path(__file__).resolve().parent.parent
REPO_DOCS = REPO_ROOT / "docs"
RENDERER = REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts"


@pytest.fixture(scope="module")
def view() -> dict:
    return acceptance.view_payload(REPO_DOCS, Index.build(REPO_DOCS))


def _renderer() -> str:
    return RENDERER.read_text(encoding="utf-8")


# ------------------------------------------------------- the same list

def test_the_view_holds_every_check_in_suite_order(view: dict) -> None:
    """A reader who knew the document finds nothing missing.

    Counted against the loader's own total rather than a literal: the corpus is
    alive, and a guard that pins 34 becomes a guard about a number rather than
    about completeness the first time somebody adds a check.
    """
    rows = [row for tier in view["tiers"]
            for area in tier["areas"] for row in area["items"]]
    assert len(rows) == view["total"] == len(
        acceptance.load(REPO_DOCS).items)
    # Tier, then section, then ordinal — the order the document had. A view
    # that reordered itself between renders is a view nobody can walk.
    seen = [(t["tier"], a["section"], r["number"]) for t in view["tiers"]
            for a in t["areas"] for r in a["items"]]
    assert seen == sorted(seen, key=lambda s: (
        s[0], [int(p) for p in s[1].split(".")], s[2]))


def test_the_counts_name_reconciliation_separately(view: dict) -> None:
    """`26/27 · 1 reconciled`, never `26/26` (ISS-0141).

    The denominator is what the suite holds. A check settled by decision is
    named rather than quietly removed from both halves of the fraction —
    rounding the bar up is the exact defect that issue exists for.
    """
    tier1 = next(t for t in view["tiers"] if t["tier"] == 1)
    assert tier1["checked"] + tier1["reconciled"] + tier1["excepted"] \
        + tier1["unsettled"] == tier1["total"]


def test_every_row_can_draw_its_own_mark(view: dict) -> None:
    """The control needs the character back, which the parse used to drop."""
    for tier in view["tiers"]:
        for area in tier["areas"]:
            for row in area["items"]:
                assert row["mark"], row
                assert row["id"].startswith(("TST-", "CHK-")), row
                assert row["rel"].endswith(".md"), row


def test_the_rules_preamble_is_one_click_away_not_republished(view: dict) -> None:
    """The README holds the document's own words; the view points at it.

    Re-rendering the preamble into the header would make this surface a second
    publisher of a record — the dual-source trap, arriving as a nicety.
    """
    assert view["readme"].endswith("README.md")
    assert (REPO_DOCS / view["readme"]).exists()


# ------------------------------------------------------------ the facets

def test_every_filter_comes_from_a_field_and_none_from_prose(view: dict) -> None:
    """The concrete thing the migration bought.

    The old suite could be filtered only by whatever a section heading happened
    to say — and `missing_issue_refs` reported **158 of 158** because it could
    not read the form the headings were written in (ISS-0173). Each facet here
    is a frontmatter field, so the filter and the record cannot disagree.
    """
    facets = view["facets"]
    assert set(facets) == {"marks", "tiers", "areas", "covers", "automation"}
    suite = acceptance.load(REPO_DOCS)
    assert sum(f["count"] for f in facets["marks"]) == len(suite.items)
    assert {f["value"] for f in facets["areas"]} == {
        i.area for i in suite.items if i.area}
    # `covers:` resolves through the index — the whole point of ISS-0173's fix
    # surviving the migration as a field rather than as a heading heuristic.
    index = Index.build(REPO_DOCS)
    for facet in facets["covers"]:
        assert index.by_id(facet["value"]) is not None, facet


def test_a_facet_with_one_value_is_not_offered() -> None:
    """A filter that can only return everything costs a click and buys nothing.

    Asserted on the client, where the decision is made: a payload listing every
    axis and a view that hides the useless ones is the split that keeps the
    server free of layout opinions.
    """
    src = _renderer()
    block = src[src.index("function buildCheckFilters"):]
    block = block[:block.index("\n}")]
    assert "values.length < 2" in block


# ---------------------------------------------------- the reader's place

def test_marking_from_the_view_holds_the_readers_position() -> None:
    """The property four rounds were spent on, held from day one here.

    ISS-0187 held the scroll around a repaint, ISS-0188 moved it inside the
    animation frame because layout lands a frame late, ISS-0189 found the
    watcher re-navigating underneath both. The new surface inherits the answer
    instead of re-earning it: position held twice, once synchronously and once
    in the frame.
    """
    src = _renderer()
    block = src[src.index("async function walkOneCheck"):]
    block = block[:block.index("\n}\n")]
    assert "const held = docView.scrollTop" in block
    assert "requestAnimationFrame" in block
    assert block.count("docView.scrollTop = held") == 2


def test_one_walk_layer_serves_both_surfaces() -> None:
    """TASK-0465: the gate row and the view row write through one function.

    Not a style preference — the copies drifted twice already. ISS-0187's
    unhandled rejection existed in one copy and not the other, and ISS-0188's
    scroll fix had to be applied twice, one frame too early the first time.
    """
    src = _renderer()
    for caller in ("async function markGateRow", "async function markCheckRow"):
        block = src[src.index(caller):]
        block = block[:block.index("\n}")]
        assert "walkOneCheck" in block, caller
        # …and nothing else. A caller that still posts for itself is a second
        # copy wearing a call to the first.
        assert "postJson" not in block, caller
    assert src.count("'/api/notes/mark-check'") == 1, (
        "**one write path, full stop** (ISS-0192). It was two while a repo "
        "could still store its suite as a document; that surface is gone, and "
        "a second call site now would be a second copy of the refusal "
        "handling — which is how the first two came to disagree."
    )


def test_cancelling_writes_nothing() -> None:
    """A dialog dismissed must not repaint, let alone write."""
    src = _renderer()
    block = src[src.index("async function walkOneCheck"):]
    block = block[:block.index("\n}\n")]
    body = block[:block.index("try {")]
    assert "if (chosen === null) return;" in body


# ------------------------------------------------------ what it says empty

def test_an_absent_suite_does_not_read_as_a_clear_gate() -> None:
    """Absent is not passing — the sentence `acceptance.load` exists to protect.

    A repo that never instantiated the contract has nothing blocking BECAUSE it
    has nothing, and that is the state that made the gate look like it worked
    for months across twelve repos.
    """
    src = _renderer()
    block = src[src.index("function buildChecksPage"):]
    block = block[:block.index("\nfunction buildCheckFilters")]
    assert "if (!v.exists)" in block
    assert "not a " in block and "clear gate" in block


def test_a_filtered_empty_list_names_what_is_hiding_the_rows() -> None:
    """`No results` is the one empty state a reader cannot act on (TASK-0318)."""
    src = _renderer()
    block = src[src.index("function paintCheckList"):]
    block = block[:block.index("\nfunction buildCheckRow")]
    assert "Clear one to see more" in block


def test_the_suite_route_is_a_page_not_a_ninth_nav_mode() -> None:
    """One corpus, one home. A ninth mode would put the suite in two places,
    which is ISS-0068's defect and one this project has already paid for."""
    src = _renderer()
    assert "normalised === '~checks'" in src
    modes = src[src.index("const QUICK_CORPUS_MODES"):]
    modes = modes[:modes.index("] as const")]
    assert "checks" not in modes


def test_the_tier_heads_open_the_view_not_a_directory() -> None:
    """`/docs/` on a directory is a 404 wearing a path.

    The head used to open the suite file; once the suite is notes there is no
    file, and the honest destination is the surface where the marks can be
    written.
    """
    from project_os_cockpit import cockpit

    index = Index.build(REPO_DOCS)
    groups = {g["key"]: g for g in
              cockpit.nav_payload(index, mode="tests")["groups"]}
    tiers = [g for k, g in groups.items() if k.startswith("tier")]
    assert tiers, "the migrated suite renders no tier groups at all"
    for group in tiers:
        assert group["url"] == cockpit.CHECKS_VIEW_ROUTE, group["url"]
        for row in group["items"]:
            # …and the ROW opens the check itself, which is the difference the
            # migration buys a reader over a link into a 1082-line document.
            assert re.fullmatch(r"/docs/tests/acceptance/(TST|CHK)-\d+-.*\.md",
                                row["url"]), row


# ---- the automation path (REQ-0039 / ADR-0031) ---------------------------


def test_a_passing_covering_test_settles_the_check(tmp_path) -> None:
    """The return on the whole merge, asserted end to end on real notes.

    Before ADR-0031 this could not happen at all: `automation:` and
    `covered_by:` were read by one facet and one release stat, and by nothing
    that could discharge anything. 15 of the 60 checks blocking `your-trainer`
    said in their own bodies that a machine already covered them, and blocked
    the release anyway.
    """
    from project_os_cockpit import acceptance
    from project_os_cockpit.index import Index

    docs = tmp_path / "docs"
    (docs / "tests" / "acceptance").mkdir(parents=True)
    (docs / "tests").joinpath("TST-0900-Covering.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0900\ntitle: "The covering test"\n'
        'status: passing\nkind: automated\nlevel: integration\n'
        'command: "pytest -q"\nlast_run: "2026-08-18"\ncovers: []\n---\n\nbody\n',
        encoding="utf-8")
    check = docs / "tests" / "acceptance" / "TST-0901-Covered.md"

    def write(covered_by: str, mark: str = " ") -> None:
        check.write_text(
            '---\ntype: "[[test]]"\nid: TST-0901\ntitle: "A covered check"\n'
            f'status: active\nlevel: acceptance\nkind: manual\ntier: 1\n'
            f'mark: "{mark}"\narea: "Area"\nsection: "1.1"\nordinal: 10\n'
            f'automation: full\ncovered_by: {covered_by}\ncovers: []\n---\n\nwalk it\n',
            encoding="utf-8")

    # Unwalked and uncovered: it blocks, which is the baseline the rest means
    # nothing without.
    write("[]")
    suite = acceptance.load(docs, Index.build(docs))
    assert len(suite.blocking()) == 1

    # Unwalked, but a PASSING test covers it: settled, with no human mark.
    write('["[[TST-0900-Covering]]"]')
    suite = acceptance.load(docs, Index.build(docs))
    assert suite.blocking() == [], "a passing covering test must settle the check"
    assert suite.items[0].mark == " ", "settling must not write a mark"

    # The covering test fails: the check re-enters the gate. Decided in
    # ADR-0031 rather than discovered -- this is what puts a machine-driven
    # population into the release gate.
    covering = docs / "tests" / "TST-0900-Covering.md"
    covering.write_text(covering.read_text().replace("status: passing", "status: failing"), "utf-8")
    suite = acceptance.load(docs, Index.build(docs))
    assert len(suite.blocking()) == 1, "a failing covering test must un-settle the check"

    # `ready` is not "not failing": a covering test that has never run settles
    # nothing, which is the whole difference between coverage and a promise.
    covering.write_text(covering.read_text().replace("status: failing", "status: ready"), "utf-8")
    suite = acceptance.load(docs, Index.build(docs))
    assert len(suite.blocking()) == 1, "an unrun covering test must not settle anything"


def test_coverage_cannot_settle_without_an_index() -> None:
    """A directory read cannot resolve an id, so it must under-settle.

    The safe direction, and stated as a property rather than left to chance: a
    reader that guessed `passing` for an unresolvable reference would clear a
    release gate on a claim nobody checked.
    """
    from project_os_cockpit.acceptance import Item

    item = Item(tier=1, section="1.1", area="Area", name="x", text="x",
                checked=False, mark=" ",
                covered_by=("[[TST-0900]]",), covered_by_status=())
    assert item.settled is False


def test_coverage_is_all_covers_not_any(tmp_path) -> None:
    """Two covers, one failing: the check is NOT settled.

    `any()` settled it, which contradicts the sentence every note about this
    feature carries — *a failing covering test un-settles the check*. Found by
    independent review, and the shape of the defect is why the guard exists:
    the single-cover case, which every other test here uses, passes either way.
    """
    from project_os_cockpit import acceptance
    from project_os_cockpit.index import Index

    docs = tmp_path / "docs"
    (docs / "tests" / "acceptance").mkdir(parents=True)
    for tid, status in (("TST-0900", "passing"), ("TST-0901", "failing")):
        (docs / "tests" / f"{tid}-C.md").write_text(
            f'---\ntype: "[[test]]"\nid: {tid}\ntitle: "c"\nstatus: {status}\n'
            f'kind: automated\nlevel: unit\ncommand: "pytest -q"\n'
            f'last_run: "2026-08-18"\ncovers: []\n---\n\nb\n', encoding="utf-8")
    (docs / "tests" / "acceptance" / "TST-0902-Covered.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0902\ntitle: "covered"\nstatus: active\n'
        'level: acceptance\nkind: manual\ntier: 1\nmark: " "\narea: "A"\n'
        'section: "1.1"\nordinal: 10\nautomation: full\n'
        'covered_by: ["[[TST-0900-C]]", "[[TST-0901-C]]"]\ncovers: []\n---\n\nwalk\n',
        encoding="utf-8")
    suite = acceptance.load(docs, Index.build(docs))
    assert len(suite.blocking()) == 1, "one failing cover must keep the check in the gate"


def test_a_manual_covering_test_is_not_coverage(tmp_path) -> None:
    """A hand-walked test at `passing` must not discharge another check.

    Coverage means a MACHINE answers it. Accepting a manual `passing` would let
    one walk launder itself into another's automation — the opposite of what
    REQ-0039 buys, and reachable today because every migrated acceptance note
    carries `kind: manual`.
    """
    from project_os_cockpit import acceptance
    from project_os_cockpit.index import Index

    docs = tmp_path / "docs"
    (docs / "tests" / "acceptance").mkdir(parents=True)
    (docs / "tests" / "TST-0900-Manual.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0900\ntitle: "m"\nstatus: passing\n'
        'kind: manual\nlevel: system\nlast_verified: "2026-08-18"\ncovers: []\n---\n\nsteps\n',
        encoding="utf-8")
    (docs / "tests" / "acceptance" / "TST-0902-Covered.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0902\ntitle: "covered"\nstatus: active\n'
        'level: acceptance\nkind: manual\ntier: 1\nmark: " "\narea: "A"\n'
        'section: "1.1"\nordinal: 10\nautomation: full\n'
        'covered_by: ["[[TST-0900-Manual]]"]\ncovers: []\n---\n\nwalk\n', encoding="utf-8")
    suite = acceptance.load(docs, Index.build(docs))
    assert len(suite.blocking()) == 1, "a manual covering test must not settle anything"
