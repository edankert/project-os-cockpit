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
    #: **Live code, not comments** ([[ISS-0244]]). This used to strip ONE known
    #: comment line by exact text and then search the rest — so the guard broke
    #: the moment a SECOND comment mentioned the name, which is what happened
    #: when `gateMark` was deleted citing the same rule. A guard that fails on
    #: a comment is a guard that gets weakened to make it pass.
    live = re.findall(r"^(?!\s*(?://|\*|/\*)).*\bmarkGateRow\b.*$", src, re.M)
    assert not live, (
        f"markGateRow is back — a release page must not write a check "
        f"(ADR-0035): {live}"
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
# ---- coverage is OBSERVED, not declared (REQ-0057 / FEAT-0138) -----------
#
# `covered_by:` and `cover_check` are GONE. The standing claim rotted silently
# -- rename, delete or disable the covering test and the note kept asserting
# coverage while the check left the run list permanently, with no signal -- and
# the field held nothing on 671 of 671 notes fleet-wide (ISS-0198), so removing
# it took nothing away.
#
# The replacement is proved in `test_observed_coverage.py`: the test declares
# the check, the run emits, and deleting the test puts the check back on the
# run list by itself.


def test_a_note_can_no_longer_declare_that_a_machine_covers_it(tmp_path) -> None:
    """[[REQ-0057]] criterion 1, asserted on the mechanism rather than on the
    corpus being clean today.

    A note carrying `covered_by:` must not settle its own check. It is refused
    by this repo's validator (`LEDGER-MOVED-FIELD` — the field is one of the
    seven ADR-0037 moved into the ledger), and the reader is gone: even if one
    were written by hand, nothing reads it.
    """
    from project_os_cockpit import acceptance
    from project_os_cockpit.index import Index

    docs = tmp_path / "docs"
    (docs / "tests" / "acceptance").mkdir(parents=True)
    (docs / "tests" / "TST-0900-Covering.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0900\ntitle: "The covering test"\n'
        'status: passing\nkind: automated\nlevel: integration\n'
        'command: "pytest -q"\nlast_run: "2026-08-18"\ncovers: []\n---\n\nbody\n',
        encoding="utf-8")
    (docs / "tests" / "acceptance" / "TST-0901-Covered.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0901\ntitle: "A check"\n'
        'status: active\nlevel: acceptance\nkind: manual\nmark: "todo"\n'
        'area: "Area"\ncovered_by: ["[[TST-0900-Covering]]"]\ncovers: []\n---\n\nwalk it\n',
        encoding="utf-8")
    suite = acceptance.load(docs, Index.build(docs))
    assert len(suite.blocking()) == 1, (
        "a hand-written `covered_by:` still settles a check — the standing "
        "claim REQ-0057 removes is back"
    )
    assert not hasattr(suite.items[0], "covered_by")


def test_the_write_path_for_the_standing_claim_is_gone() -> None:
    """[[ISS-0249]]: `cover_check` was a complete, tested write path that no
    front door reached, and the capability it offered is one [[FEAT-0138]]
    ends. [[FEAT-0131]] — *the suite is refined* — closed `done` without ever
    needing it, which was the condition the issue named for deleting it."""
    from project_os_cockpit import note_writes

    assert not hasattr(note_writes, "cover_check")


# ---- the write path that WAS kept, and is now reachable (ISS-0249) --------

def _write_repo(tmp_path):
    """A repo with one acceptance check."""
    from project_os_cockpit.index import Index
    docs = tmp_path / "docs"
    (docs / "tests" / "acceptance").mkdir(parents=True)
    (docs / "features").mkdir()
    (docs / "features" / "FEAT-0001-Thing.md").write_text(
        '---\ntype: "[[feature]]"\nid: FEAT-0001\ntitle: "t"\nstatus: done\n---\n\nb\n',
        encoding="utf-8")
    (docs / "tests" / "acceptance" / "TST-0902-Covered.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0902\ntitle: "a check"\nstatus: active\n'
        'level: acceptance\nkind: manual\nmark: "done"\nverdict_date: "2026-08-01"\n'
        'area: "A"\ncovers: []\n---\n\nwalk\n', encoding="utf-8")
    return docs, Index.build(docs)


def test_retiring_is_refused_without_a_reason(tmp_path) -> None:
    """A check that leaves the gate without a reason is indistinguishable from
    one that was quietly dropped."""
    from project_os_cockpit import note_writes

    docs, index = _write_repo(tmp_path)
    with pytest.raises(note_writes.WriteError) as bare:
        note_writes.retire_check(index, check_id="TST-0902", reason="")
    assert "must say why" in str(bare.value)


def test_retiring_keeps_the_verdict_and_records_why(tmp_path) -> None:
    """**Retiring is deprecation, not erasure.** A retired check is the record
    that a behaviour was once walked by hand — which is exactly the history
    somebody wants when the automated test is later deleted as redundant."""
    import frontmatter as _fm

    from project_os_cockpit import note_writes
    from project_os_cockpit.index import Index

    docs, index = _write_repo(tmp_path)
    out = note_writes.retire_check(
        index, check_id="TST-0902", reason="the surface it walks was removed")
    assert out["status"] == "retired"
    note = _fm.loads(
        (docs / "tests" / "acceptance" / "TST-0902-Covered.md").read_text())
    assert note["status"] == "retired"
    assert note["mark"] == "done", "retiring is deprecation, not erasure"
    assert str(note["verdict_date"]) == "2026-08-01", "the walk's date survives"
    assert "the surface it walks was removed" in note.content
    #: **The reason is in the BODY, not `verdict_reason:`.** That field is one
    #: of the seven ADR-0037 moved into the ledger and this repo's validator
    #: refuses it — so the previous version wrote a field that would have
    #: failed the commit it was part of, and nothing caught it because nothing
    #: called it.
    assert "verdict_reason" not in note.metadata

    with pytest.raises(note_writes.WriteError):
        note_writes.retire_check(Index.build(docs), check_id="TST-0902",
                                 reason="again")


def test_promotion_is_gone(tmp_path) -> None:
    """`promote` wrote `tier: 3`, and [[ADR-0039]] decided there is no Tier 3:
    `tier:` is read by no section and by no gate decision. A parameter whose
    only effect is a field nothing reads is a lever that moves nothing."""
    import inspect

    from project_os_cockpit import note_writes

    assert "promote" not in inspect.signature(note_writes.retire_check).parameters


def test_retiring_is_reachable_from_a_front_door(tmp_path) -> None:
    """[[ISS-0249]]'s whole subject: *is every write routed?* It was not.

    Asserted on the dispatch and on the control, because the defect was
    precisely that the function, its guards and its unit tests were all fine
    and nothing could call it.
    """
    src = (Path(__file__).resolve().parents[1] / "src" / "project_os_cockpit"
           / "server.py").read_text(encoding="utf-8")
    assert 'path == "/api/notes/retire-check"' in src
    i = src.index("def _serve_retire_check")
    body = src[i:i + 2200]
    assert "self._require_loopback()" in body
    assert "note_writes.retire_check(" in body

    ts = (Path(__file__).resolve().parents[1] / "desktop" / "src" / "renderer"
          / "renderer.ts").read_text(encoding="utf-8")
    assert "/api/notes/retire-check" in ts
    assert "retireCheckRow(item)" in ts


def test_no_public_write_in_note_writes_is_unreachable() -> None:
    """**The general form of [[ISS-0249]]**, so the next one is caught by a
    test rather than by somebody walking the dispatch in reverse.

    The loopback enumeration walks the DISPATCH, so a function absent from it
    is absent from that rule's domain by construction — it cannot report what
    it cannot see. This asks the other question: *is every write routed?*
    """
    import ast

    root = Path(__file__).resolve().parents[1] / "src" / "project_os_cockpit"
    tree = ast.parse((root / "note_writes.py").read_text(encoding="utf-8"))
    #: A write is a public function that calls `_write`. Reads, id allocators
    #: and helpers are excluded by that predicate rather than by a list.
    writes = set()
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef) or node.name.startswith("_"):
            continue
        for inner in ast.walk(node):
            if (isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Name)
                    and inner.func.id == "_write"):
                writes.add(node.name)
                break
    assert writes, "the predicate found no writes at all"

    callers = ""
    for name in ("server.py", "cockpit.py", "cli.py", "worker.py",
                 "agent_actions.py", "note_writes.py"):
        callers += (root / name).read_text(encoding="utf-8")
    unreachable = sorted(
        name for name in writes
        if callers.count("%s(" % name) <= 1        # its own definition
    )
    assert unreachable == [], (
        "these write paths are complete, tested and callable by nothing: %s"
        % ", ".join(unreachable)
    )


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
