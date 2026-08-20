"""The `SUR-*` note type ([[TASK-0514]]).

*"A surface is a note, not a string retyped on every check."* Measured on
`your-trainer` 2026-08-20 (working tree): **94 distinct `area:` strings across
581 checks** — every one of them typed by hand, on every check that touches it.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "scripts" / "validate-docs.py"
BUNDLED = ROOT / "src" / "project_os_cockpit" / "validate_docs_bundled.py"
UPSTREAM = Path.home() / "Dev" / "repos" / "project-os"


def test_the_type_is_wired_into_the_validator() -> None:
    from project_os_cockpit import validate_docs_bundled as vd

    assert "SUR" in vd.ID_PREFIXES, "a SUR-* id resolves to nothing"
    assert vd.COLLECTION_TYPE.get("surfaces") == {"surface"}
    #: **A surface is not *done*.** It exists until the product stops having
    #: it, so its terminal states are `retired` (the place is gone) and
    #: `superseded` (another surface took it over) — no new vocabulary, because
    #: ADR-0008 collapsed 64 status values to 53 and a type is not a reason to
    #: reopen that.
    assert vd.ALLOWED_STATUS.get("surface") == {"active", "retired", "superseded"}
    for wrong in ("done", "fixed", "passing", "draft"):
        assert wrong not in vd.ALLOWED_STATUS["surface"], wrong


def test_a_surface_note_validates(tmp_path: Path) -> None:
    docs = tmp_path / "docs" / "surfaces"
    docs.mkdir(parents=True)
    (tmp_path / "SNAPSHOT.yaml").write_text(
        'version: 1\nproject:\n  name: "t"\n  repo_root: "."\n'
        "counters:\n  SUR: 1\nitems: {}\n", encoding="utf-8")
    (docs / "SUR-0001-A-Screen.md").write_text(
        '---\ntype: "[[surface]]"\nid: SUR-0001\ntitle: "A screen"\n'
        'status: active\nkind: screen\nplatforms: []\n---\n\n# A screen\n',
        encoding="utf-8")
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(tmp_path)],
        capture_output=True, text=True).stdout
    assert "SUR-0001" not in out or "ERROR" not in out, out[-500:]


def test_an_illegal_surface_status_is_refused(tmp_path: Path) -> None:
    """`done` is the value somebody will reach for, and it is the one that is
    wrong: a surface is not finished, it is *there*."""
    docs = tmp_path / "docs" / "surfaces"
    docs.mkdir(parents=True)
    (tmp_path / "SNAPSHOT.yaml").write_text(
        'version: 1\nproject:\n  name: "t"\n  repo_root: "."\n'
        "counters:\n  SUR: 1\nitems: {}\n", encoding="utf-8")
    (docs / "SUR-0001-A-Screen.md").write_text(
        '---\ntype: "[[surface]]"\nid: SUR-0001\ntitle: "A screen"\n'
        'status: done\nkind: screen\n---\n\n# A screen\n', encoding="utf-8")
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(tmp_path)],
        capture_output=True, text=True).stdout
    assert "NOTE-STATUS" in out and "SUR-0001" in out, out[-500:]


def test_the_template_is_template_owned_and_identical_upstream() -> None:
    """*"Template-owned, so it lands upstream in `project-os` FIRST and syncs
    down — the lesson of the `kind:` removal, which took three passes because
    six repos held the edit on disk and in no commit."*
    """
    here = ROOT / "docs" / "__templates__" / "surface.md"
    there = UPSTREAM / "docs" / "__templates__" / "surface.md"
    assert here.is_file(), "no surface template downstream"
    if not there.is_file():                       # pragma: no cover
        raise AssertionError("the template did not land upstream first")
    assert here.read_bytes() == there.read_bytes(), (
        "the surface template has drifted from upstream — the edit must land "
        "there and sync down, not the other way round"
    )


def test_the_template_refuses_to_list_its_own_coverage() -> None:
    """A second, hand-maintained copy of a relationship is what [[ADR-0032]]
    spent a decision removing. The checks covering a surface are derived from
    `area:`, so the template says so rather than leaving a tempting list."""
    text = (ROOT / "docs" / "__templates__" / "surface.md").read_text(encoding="utf-8")
    assert "DERIVED" in text and "do not list them here" in text
    assert "checks:" not in text, "the template invites a second encoding"


def test_the_two_validator_copies_still_match() -> None:
    assert BUNDLED.read_bytes() == VALIDATOR.read_bytes()


# ---- surfaces on the design view (TASK-0516) ------------------------------

def _design_groups(docs: Path) -> dict[str, dict]:
    from project_os_cockpit import cockpit
    from project_os_cockpit.index import Index

    return {str(g.get("key")): g
            for g in cockpit.nav_payload(Index.build(docs), "design")["groups"]}


def test_surfaces_have_a_home_on_the_design_view() -> None:
    """Edwin: *"where should they be visible, probably in the design?"* — and
    the answer holds for the reason that group exists: the design view carries
    what **bounds** the project, and a surface is a place the product has,
    permanent and project-level, exactly like a decision or a risk.

    A group in the constraints loop rather than a fetch of its own is also what
    makes surfaces **findable** — the quick corpus is built from nav modes, so
    one entry answers the palette and the navigator at once. That is the gap
    [[TASK-0514]] recorded in `KNOWN_ABSENT`.
    """
    groups = _design_groups(ROOT / "docs")
    assert "surfaces" in groups, sorted(groups)
    assert [i["id"] for i in groups["surfaces"]["items"]] == ["SUR-0001"]


def test_a_surface_with_no_checks_is_visible_as_such() -> None:
    """*"A surface with no coverage is the row this whole type exists to make
    possible."*

    **On the head, not on the row**, and the first attempt is why. It went into
    `subtitle`, which `buildNavRow` documents as **deliberately not rendered** —
    [[ISS-0225]]'s defect exactly, sent and never drawn, reintroduced inside the
    phase that removed it. The other drawn candidate, `progress`, is worse: it
    paints a *completion* bar, and an uncovered surface has no unfinished work,
    it has no work at all.
    """
    from project_os_cockpit import cockpit
    from project_os_cockpit.index import Index

    index = Index.build(ROOT / "docs")
    assert cockpit.surface_coverage(index) == {"SUR-0001": 0}
    head = str(_design_groups(ROOT / "docs")["surfaces"]["label"])
    assert head == "Surfaces · 1 with no checks", head


def test_the_count_is_not_sent_on_a_field_no_renderer_draws() -> None:
    """[[ISS-0225]], asserted against the thing that nearly happened: the row
    must not gain a coverage field, because the two places it could go are
    undrawn (`subtitle`) or wrong (`progress`).
    """
    rows = _design_groups(ROOT / "docs")["surfaces"]["items"]
    for row in rows:
        assert "coverage" not in row and "checks" not in row, sorted(row)
        #: `progress` would render a completion bar over checks that do not
        #: exist — 0% of nothing, read as unfinished work.
        assert "progress" not in row, (
            "a surface row carries `progress`, which paints a completion bar "
            "for work that does not exist"
        )


def test_a_covered_surface_drops_off_the_head_count(tmp_path: Path) -> None:
    """The head names only the uncovered ones, so the count moves when the
    corpus does — constructed, because this repo has exactly one surface and
    it covers nothing.
    """
    from project_os_cockpit import cockpit
    from project_os_cockpit.index import Index

    docs = tmp_path / "docs"
    (docs / "surfaces").mkdir(parents=True)
    (docs / "tests" / "acceptance").mkdir(parents=True)
    (docs / "surfaces" / "SUR-0001-Ride.md").write_text(
        '---\ntype: "[[surface]]"\nid: SUR-0001\ntitle: "Ride"\n'
        'status: active\nkind: screen\n---\n\n# Ride\n', encoding="utf-8")
    (docs / "tests" / "acceptance" / "TST-0001-C.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0001\ntitle: "C"\nlevel: acceptance\n'
        'status: active\narea: "Ride"\nmark: todo\ncovers: []\n---\n\n# C\n',
        encoding="utf-8")
    index = Index.build(docs)
    assert cockpit.surface_coverage(index) == {"SUR-0001": 1}
    groups = {str(g.get("key")): g
              for g in cockpit.nav_payload(index, "design")["groups"]}
    assert str(groups["surfaces"]["label"]) == "Surfaces", (
        "a covered surface is still counted as bare"
    )
