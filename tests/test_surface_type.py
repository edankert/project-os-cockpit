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
