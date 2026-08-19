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
    # **Tier, then id** (ISS-0224). This read `tier, section, ordinal` — the
    # order the *document* had, and the document exists in no migrated repo.
    # `(tier, id)` was measured byte-identical to the old key in all three
    # repos before the fields were removed, so the order a reader walks did
    # not move; only the thing that expresses it did.
    #
    # A view that reorders itself between renders is still a view nobody can
    # walk, which is what this guards.
    seen = [(t["tier"], r["number"]) for t in view["tiers"]
            for a in t["areas"] for r in a["items"]]
    assert seen == sorted(seen)
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
def test_one_walk_layer_and_now_exactly_one_surface() -> None:
    """TASK-0465: the write goes through one function. ADR-0035: one caller.
    This asserted that **both** `markGateRow` and `markCheckRow` delegated to
    `walkOneCheck`, because the two copies had drifted twice — ISS-0187's
    unhandled rejection existed in one and not the other, and ISS-0188's
    scroll fix had to be applied twice.
    `markGateRow` is now deleted: a release page reports the gate and records
    nothing. The convergence this guarded is therefore complete rather than
    abandoned — one write path, and now one caller of it — so the assertion
    narrows to the surviving surface and the endpoint count below carries the
    rest.
    """
    src = _renderer()
    block = src[src.index("async function markCheckRow"):]
    block = block[:block.index("\n}")]
    assert "walkOneCheck" in block
    # …and nothing else. A caller that still posts for itself is a second
    # copy wearing a call to the first.
    assert "postJson" not in block
    assert "markGateRow" not in src.replace(
        "// **No `markGateRow`** (ADR-0035). It was the release page's write path —", ""), (
        "markGateRow is back — a release page must not write a check (ADR-0035)"
    )
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
        # `~checks/tier/N`, not the bare route (ISS-0203). Every head carried
        # the identical address until 2026-08-18, so the label differed and the
        # destination did not — selecting Tier 2 rendered what Tier 1 had.
        assert group["url"].startswith(cockpit.CHECKS_VIEW_ROUTE + "/tier/"), group["url"]
        assert group["url"].endswith("/" + group["key"].removeprefix("tier")), group["url"]
        for row in group["items"]:
            # …and the ROW opens the check itself, which is the difference the
            # migration buys a reader over a link into a 1082-line document.
                # …and the ROW is a **surface** (ISS-0222), so it opens
                # the generated page at its tier rather than one check's
                # note. This asserted a note url, from when the nav
                # listed 579 individual checks.
                if str(row.get("id") or "").upper().startswith("TST-"):
                    # A non-acceptance test merged into this section
                    # (ADR-0039) opens its own note: it IS one check, so the
                    # generated page has nothing extra to show for it.
                    assert row["url"].endswith(".md"), row["url"]
                else:
                    assert row["url"].startswith("~checks/tier/"), row["url"]
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
    assert suite.items[0].mark == "todo", "settling must not write a mark"
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
                checked=False, mark="todo",
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
        'level: acceptance\nkind: manual\ntier: 1\nmark: "todo"\narea: "A"\n'
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
        'level: acceptance\nkind: manual\ntier: 1\nmark: "todo"\narea: "A"\n'
        'section: "1.1"\nordinal: 10\nautomation: full\n'
        'covered_by: ["[[TST-0900-Manual]]"]\ncovers: []\n---\n\nwalk\n', encoding="utf-8")
    suite = acceptance.load(docs, Index.build(docs))
    assert len(suite.blocking()) == 1, "a manual covering test must not settle anything"
# ---- the write path (TASK-0483 / TASK-0484) -------------------------------
def _write_repo(tmp_path):
    """A repo with one acceptance check and three candidate covering tests."""
    from project_os_cockpit.index import Index
    docs = tmp_path / "docs"
    (docs / "tests" / "acceptance").mkdir(parents=True)
    (docs / "tests" / "TST-0900-Executable.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0900\ntitle: "runnable"\nstatus: passing\n'
        'kind: automated\nlevel: unit\ncommand: "pytest -q"\nlast_run: "2026-08-18"\n'
        'covers: []\n---\n\nb\n', encoding="utf-8")
    (docs / "tests" / "TST-0901-Manual.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0901\ntitle: "hand-walked"\nstatus: passing\n'
        'kind: manual\nlevel: system\nlast_verified: "2026-08-18"\ncovers: []\n---\n\nb\n',
        encoding="utf-8")
    (docs / "features").mkdir()
    (docs / "features" / "FEAT-0001-Thing.md").write_text(
        '---\ntype: "[[feature]]"\nid: FEAT-0001\ntitle: "t"\nstatus: done\n---\n\nb\n',
        encoding="utf-8")
    (docs / "tests" / "acceptance" / "TST-0902-Covered.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0902\ntitle: "a check"\nstatus: active\n'
        'level: acceptance\nkind: manual\ntier: 2\nmark: "done"\nverdict_date: "2026-08-01"\n'
        'verdict_reason: ""\narea: "A"\nsection: "1.1"\nordinal: 10\n'
        'automation: manual\ncovered_by: []\ncovers: []\n---\n\nwalk\n', encoding="utf-8")
    return docs, Index.build(docs)
def test_covered_by_is_refused_unless_the_test_can_actually_run(tmp_path) -> None:
    """The refusal that makes the field mean something.
    `_resolve_coverage` accepts only an executable test, so a link to a manual
    one would look like coverage on every surface and settle nothing — a claim
    written into the exact field the gate reads, that the gate is built to
    ignore. Refusing at the write is the only place it can be caught.
    """
    from project_os_cockpit import note_writes
    docs, index = _write_repo(tmp_path)
    with pytest.raises(note_writes.WriteError) as manual:
        note_writes.cover_check(index, check_id="TST-0902", covered_by="TST-0901")
    assert "declares no command" in str(manual.value)
    with pytest.raises(note_writes.WriteError) as missing:
        note_writes.cover_check(index, check_id="TST-0902", covered_by="TST-9999")
    assert "not in the record" in str(missing.value)
    with pytest.raises(note_writes.WriteError) as wrong_type:
        note_writes.cover_check(index, check_id="TST-0902", covered_by="FEAT-0001")
    assert "not a test" in str(wrong_type.value)
    with pytest.raises(note_writes.WriteError) as partial:
        note_writes.cover_check(index, check_id="TST-0902",
                                covered_by="TST-0900", automation="partial")
    assert "which part is automated" in str(partial.value)
def test_covered_by_writes_the_link_the_gate_reads(tmp_path) -> None:
    """And the round trip: written here, read by `settled` there."""
    from project_os_cockpit import acceptance, note_writes
    from project_os_cockpit.index import Index
    docs, index = _write_repo(tmp_path)
    out = note_writes.cover_check(index, check_id="TST-0902", covered_by="TST-0900")
    assert out["automation"] == "full"
    suite = acceptance.load(docs, Index.build(docs))
    item = suite.items[0]
    assert item.covered_by, "the field the gate reads must be populated"
    assert item.covered_by_passing, "a passing executable cover must discharge it"
def test_promotion_is_refused_without_coverage_and_retirement_keeps_the_verdict(tmp_path) -> None:
    """Tier 3 is where a check goes when a machine took it over.
    Promoting one that nothing covers is moving it out of the gating tiers on
    no evidence — which is the escape hatch, not the lifecycle. And retiring
    must not erase the mark: a retired check is the record that a behaviour was
    once walked, which is exactly what somebody wants when the automated test
    is later deleted as redundant.
    """
    from project_os_cockpit import note_writes
    from project_os_cockpit.index import Index
    docs, index = _write_repo(tmp_path)
    with pytest.raises(note_writes.WriteError) as bare:
        note_writes.retire_check(index, check_id="TST-0902", reason="", promote=True)
    assert "must say why" in str(bare.value)
    with pytest.raises(note_writes.WriteError) as uncovered:
        note_writes.retire_check(index, check_id="TST-0902",
                                 reason="covered now", promote=True)
    assert "covered_by" in str(uncovered.value)
    note_writes.cover_check(index, check_id="TST-0902", covered_by="TST-0900")
    index = Index.build(docs)
    note_writes.retire_check(index, check_id="TST-0902",
                             reason="TST-0900 covers it", promote=True)
    # Read as frontmatter, not as a string: whether a scalar is quoted is a
    # writer's habit, and asserting on it would fail on a cosmetic change while
    # passing on a semantic one.
    import frontmatter as _fm
    note = _fm.loads((docs / "tests" / "acceptance" / "TST-0902-Covered.md").read_text())
    assert str(note["tier"]) == "3"
    assert note["mark"] == "done", "promotion must not erase the verdict"
    note_writes.retire_check(Index.build(docs), check_id="TST-0902",
                             reason="shipped in v2; TST-0900 owns it")
    note = _fm.loads((docs / "tests" / "acceptance" / "TST-0902-Covered.md").read_text())
    assert note["status"] == "retired"
    assert note["mark"] == "done", "retiring is deprecation, not erasure"
    assert str(note["verdict_date"]) == "2026-08-01", "the walk's date survives it"
# ----- surface grouping and the progress bar (TASK-0520) --------------------
def test_the_page_groups_by_surface_and_not_as_one_flat_list() -> None:
    """TASK-0520, restoring what TASK-0513 removed.
    `area:` IS the surface — Tier 1's values in `your-trainer` are *Profile
    Management*, *Hardware Connectivity*, *Workout Execution*. TASK-0513
    flattened these headings away while answering a request that was about the
    LEFT PANE's tier sections, which is the specific mistake this guards.
    """
    src = _renderer()
    body = src[src.index("function paintCheckList("):]
    body = body[:body.index("\n}\n") + 3]
    assert "checks-area" in body, (
        "the surface heading is gone again — `area:` is where a check sits in "
        "the application, and a flat list of 579 rows answers no question"
    )
    assert "for (const area of areas)" in body
    #: **A percentage on a surface, a bar on a tier** (ISS-0223). A bar
    #: answers what SHAPE a set has, worth four segments on a card being
    #: SCANNED; this page is being WORKED, and the rows below the header
    #: already say in full what the bar summarised.
    assert "checkPercent(area.items)" in body, "a surface with no progress"
    #: **No bar on this page at all** (ISS-0234). ISS-0223 replaced the
    #: surface bar with a percentage and kept the tier's; Edwin removed both.
    #: The page is worked rather than scanned, and the heading carries the
    #: number now — so `checkProgress` went with them, as dead code.
    assert "checkProgress" not in body, "the bar came back"
def test_a_stale_tick_is_not_drawn_as_done() -> None:
    """Four segments, because three would lie.
    A stale tick stands over evidence the record says was overtaken. Counting
    it as `done` is what made `your-trainer`'s honest blocking number 113
    against a reported 60, so the bar draws it apart — and the percentage in
    the title counts only unstale ticks.
    """
    src = _renderer()
    body = src[src.index("function checkPercent("):]
    body = body[:body.index("\n}\n") + 3]
    #: The bar drew stale as its own segment; the percentage names it in
    #: the text instead, because folding it into done is what made
    #: `your-trainer`'s honest 113 read as a reported 60 (ISS-0234).
    assert "items.filter((i) => i.stale)" in body
    assert "stale} stale" in body
    # The percentage is over `done`, never over `settled`.
    assert "(done.length / total)" in body, (
        "the percentage counts stale ticks as run — the one thing this bar "
        "exists not to do"
    )
    #: **The segment-colour assertion went with the segments** (ISS-0234).
    #: It required four families because a bar HAS four bands; a percentage
    #: has none, and the one distinction that survived the compression —
    #: stale apart from done — is asserted above, in both the numerator and
    #: the text.
