"""`~checks` groups by screen, with a dialog under the screen it opens from.

[[TASK-0625]]; upstream ADR-0044. The page grouped by the `area:` string until
2026-09-14, so the groups sorted by whatever the string happened to be —
`your-trainer`'s "HR-zone interval sheet" nowhere near the "Workout editor" it
opens from. A reader walking a release walks screens, and the dialogs they
open are part of that screen's walk.

**The parent lookup is the bundled walk module's**, not a second reading of
`parent:`. That is the property the last test here asserts, and it is the one
that keeps this page and `walk-sheet.py` from coming to disagree about which
screen a dialog belongs to.
"""

from __future__ import annotations

from pathlib import Path

from project_os_cockpit import acceptance, cockpit
from project_os_cockpit.index import Index


def _surface(docs: Path, sid: str, title: str, *, parent: str = "",
             kind: str = "screen") -> None:
    (docs / "surfaces").mkdir(parents=True, exist_ok=True)
    extra = f'parent: "{parent}"\n' if parent else ""
    (docs / "surfaces" / f"{sid}.md").write_text(
        f'---\ntype: "[[surface]]"\nid: {sid}\ntitle: "{title}"\n'
        f'status: active\nkind: {kind}\n{extra}---\n\n# {title}\n',
        encoding="utf-8")


def _check(docs: Path, tid: str, area: str) -> None:
    (docs / "tests" / "acceptance").mkdir(parents=True, exist_ok=True)
    (docs / "tests" / "acceptance" / f"{tid}.md").write_text(
        f'---\ntype: "[[test]]"\nid: {tid}\ntitle: "{tid}"\n'
        f'level: acceptance\nstatus: active\narea: "{area}"\nmark: todo\n'
        f"---\n\n# {tid}\n\n## Steps\n1. Do it.\n\n## Expect\n- It happens.\n",
        encoding="utf-8")


def _corpus(tmp_path: Path) -> Path:
    """A parent screen, a child dialog under it, a subsystem, and an orphan."""
    docs = tmp_path / "docs"
    _surface(docs, "SUR-0001", "Workout editor")
    _surface(docs, "SUR-0002", "HR-zone interval sheet", parent="SUR-0001")
    _surface(docs, "SUR-0003", "Sync", kind="subsystem")
    _check(docs, "TST-0001", "Workout editor")
    _check(docs, "TST-0002", "HR-zone interval sheet")
    _check(docs, "TST-0003", "Sync")
    #: An `area:` naming no surface note at all. It must stay visible
    #: ([[ISS-0250]]): a check filed under a name nobody kept is a check
    #: somebody still has to walk.
    _check(docs, "TST-0004", "Nowhere in particular")
    return docs


def _areas(docs: Path) -> list[dict]:
    view = acceptance.view_payload(docs, Index.build(docs))
    return [a for tier in view["tiers"] for a in tier["areas"]]


# ---------------------------------------------------- a dialog under its screen

def test_a_dialogs_checks_sit_under_the_screen_it_opens_from(
        tmp_path: Path) -> None:
    docs = _corpus(tmp_path)
    areas = _areas(docs)
    #: The screen first, then the dialog that opens from it, then the
    #: surfaces that are not screens, then the area naming no surface.
    assert [a["area"] for a in areas] == [
        "Workout editor", "HR-zone interval sheet", "Sync",
        "Nowhere in particular",
    ]
    child = next(a for a in areas if a["area"] == "HR-zone interval sheet")
    assert child["parent"] == "Workout editor"
    assert child["screen"] == "Workout editor"


def test_a_screen_and_its_child_report_the_same_screen(tmp_path: Path) -> None:
    """What the renderer indents on. Both name the top-level screen, and only
    the child names a parent — so a page can draw the nesting without asking
    which of the two it is looking at."""
    docs = _corpus(tmp_path)
    by_area = {a["area"]: a for a in _areas(docs)}
    assert by_area["Workout editor"]["screen"] == "Workout editor"
    assert by_area["Workout editor"]["parent"] == ""
    assert by_area["HR-zone interval sheet"]["screen"] == "Workout editor"
    assert by_area["HR-zone interval sheet"]["parent"] == "Workout editor"


def test_a_subsystem_is_its_own_group_after_the_screens(tmp_path: Path) -> None:
    """`subsystem` and `surface-less` are surfaces without being places, so
    they cannot sit under a screen and they come after every one that is."""
    docs = _corpus(tmp_path)
    areas = _areas(docs)
    order = [a["area"] for a in areas]
    assert order.index("Sync") > order.index("HR-zone interval sheet")
    sync = next(a for a in areas if a["area"] == "Sync")
    assert sync["kind"] == "subsystem"
    assert sync["parent"] == ""


def test_an_area_naming_no_surface_is_still_drawn(tmp_path: Path) -> None:
    """[[ISS-0250]]: a surface rename silently orphans its checks. The group
    must still be on the page — last, and marked as resolving to nothing —
    rather than folded into a screen it has no claim on."""
    docs = _corpus(tmp_path)
    areas = _areas(docs)
    orphan = next(a for a in areas if a["area"] == "Nowhere in particular")
    assert orphan["unresolved"] is True
    assert orphan["surface"] == ""
    assert areas[-1] is orphan
    assert [r["id"] for r in orphan["items"]] == ["TST-0004"]


def test_every_check_is_still_on_the_page_exactly_once(tmp_path: Path) -> None:
    """Grouping moves rows; it must not lose or duplicate one."""
    docs = _corpus(tmp_path)
    rows = [r["id"] for a in _areas(docs) for r in a["items"]]
    assert sorted(rows) == ["TST-0001", "TST-0002", "TST-0003", "TST-0004"]


def test_the_grouping_does_not_move_between_renders(tmp_path: Path) -> None:
    """A list that reorders itself is one you lose your place in
    ([[TASK-0556]]). The sort is total, so two renders agree."""
    docs = _corpus(tmp_path)
    assert [a["area"] for a in _areas(docs)] == [a["area"] for a in _areas(docs)]


# -------------------------------------------------- one parent lookup, not two

def test_the_page_and_the_walk_sheet_resolve_the_same_parent(
        tmp_path: Path) -> None:
    """The DoD's second box, asserted rather than assumed.

    `parent:` is written three ways across the fleet — a bare id, a wikilink,
    and the parent's title. The bundled module resolves all three; a second
    implementation here would have to as well, and the first one to miss a
    spelling is where the two surfaces start disagreeing.
    """
    docs = tmp_path / "docs"
    _surface(docs, "SUR-0001", "Workout editor")
    _surface(docs, "SUR-0002", "By id", parent="SUR-0001")
    _surface(docs, "SUR-0003", "By wikilink", parent="[[SUR-0001]]")
    _surface(docs, "SUR-0004", "By title", parent="Workout editor")
    for i, area in enumerate(["By id", "By wikilink", "By title"], start=1):
        _check(docs, f"TST-000{i}", area)

    index = Index.build(docs)
    by_area = {a["area"]: a for a in _areas(docs)}
    walk = acceptance._walk_module()
    surfaces, _titles, _kinds = acceptance._surface_map(index)
    for area, sid in [("By id", "SUR-0002"), ("By wikilink", "SUR-0003"),
                      ("By title", "SUR-0004")]:
        assert by_area[area]["screen"] == "Workout editor"
        #: The same answer the sheet gets, from the same function.
        assert walk.top_screen(sid, surfaces) == "SUR-0001"


# --------------------------------------------- the design view counts screens

def test_the_design_view_counts_top_level_screens(tmp_path: Path) -> None:
    """FEAT-0130's 12 to 15 target is about screens (Edwin, 2026-09-14).

    The child and the subsystem are on the list and neither counts toward it:
    a repo that named its dialogs properly was reading three times its real
    number of places.
    """
    docs = _corpus(tmp_path)
    index = Index.build(docs)
    groups = {str(g.get("key")): g
              for g in cockpit.nav_payload(index, "design")["groups"]}
    assert groups["surfaces"]["label"] == "Surfaces · 1 screen · 1 child"
    #: And the child is listed under its parent, not sorted away from it.
    assert [i["id"] for i in groups["surfaces"]["items"]] == [
        "SUR-0001", "SUR-0002", "SUR-0003",
    ]


def test_a_surface_with_no_checks_still_appears(tmp_path: Path) -> None:
    """[[FEAT-0130]]'s whole reason for the type: a place in the product that
    nothing checks is invisible until surfaces are notes. Grouping `~checks`
    by screen must not have taken that row away."""
    docs = _corpus(tmp_path)
    _surface(docs, "SUR-0005", "Nobody checks this")
    index = Index.build(docs)
    groups = {str(g.get("key")): g
              for g in cockpit.nav_payload(index, "design")["groups"]}
    assert "SUR-0005" in [i["id"] for i in groups["surfaces"]["items"]]
    assert "1 with no checks" in groups["surfaces"]["label"]


# ------------------------------------------------------- what the page draws

def _renderer() -> str:
    return (Path(__file__).resolve().parents[1] / "desktop" / "src"
            / "renderer" / "renderer.ts").read_text(encoding="utf-8")


def test_the_page_indents_a_child_group_and_names_its_screen() -> None:
    """A source guard, and a weak one by this repo's own rule ([[ISS-0055]]).

    The grouping itself — which screen a dialog belongs to, and in what order
    the groups come out — is decided in `view_payload` and asserted above
    against real payloads. What is left for the page is an indent and a label,
    and the checks page has no DOM harness to draw it in. So this pins the two
    values reaching the DOM rather than the words around them, and the payload
    tests carry the property.
    """
    src = _renderer()
    block = src[src.index("function paintCheckList"):]
    block = block[:block.index("\nfunction buildCheckRow")]
    assert "area.parent ? 'checks-area is-child' : 'checks-area'" in block
    assert "`in ${area.parent}`" in block
    #: And the orphan says so rather than reading like every other group.
    assert "area.unresolved" in block and "no surface note" in block
