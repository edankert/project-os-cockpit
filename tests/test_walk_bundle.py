"""The walk module is a bundle, not a fork ([[TASK-0618]]).

The ordering, placement and survey rules are stated once upstream
(project-os-dev FEAT-0029, `tools/instructions/TESTING.md` "The walk"). This
repo ships the implementation twice — `tools/scripts/walk-sheet.py` for a
person generating a markdown sheet, and `src/project_os_cockpit/
walk_sheet_bundled.py` for the sidecar — and the two must be the same file.

Why it matters more here than for the validator: the walk page and the
generated sheet answer the same question for the same release, side by side. A
sheet that ordered its sittings differently from the page would not fail
anything; it would just be a second opinion nobody asked for.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANONICAL = ROOT / "tools" / "scripts" / "walk-sheet.py"
BUNDLED = ROOT / "src" / "project_os_cockpit" / "walk_sheet_bundled.py"


def test_the_bundled_walk_module_is_byte_identical_to_upstreams() -> None:
    """Re-copy it after a template sync; never patch it here.

    The adaptation the sidecar needs — pointing the module's validator loader
    at `validate_docs_bundled.py` — is done by seeding its global in
    `acceptance._walk_module`, precisely so this assertion can stay exact.
    """
    assert BUNDLED.read_bytes() == CANONICAL.read_bytes(), (
        "walk_sheet_bundled.py has drifted from tools/scripts/walk-sheet.py; "
        "re-copy it (it is a verbatim bundle, not a fork)"
    )


def test_the_sync_script_carries_the_walk_module() -> None:
    """`sync-project-os.sh` is what refreshes the canonical copy. If it stopped
    copying `tools/scripts/`, the bundle would be verified identical to a file
    that had itself gone stale — green, and both wrong."""
    sync = (ROOT / "tools" / "scripts" / "sync-project-os.sh").read_text(
        encoding="utf-8")
    assert "tools/scripts" in sync


def test_the_bundle_finds_a_validator_without_its_upstream_neighbour() -> None:
    """Upstream loads `validate-docs.py` from its own directory. In the package
    that directory holds `validate_docs_bundled.py` instead, so an unseeded
    import would raise the first time a survey resolved a change note."""
    from project_os_cockpit import acceptance
    module = acceptance._walk_module()
    assert module._VD is not None
    assert hasattr(module._VD, "parse_frontmatter")
    assert hasattr(module._VD, "note_type")
    assert hasattr(module._VD, "build_note_index")


def test_the_template_ships_a_walk_order_to_copy() -> None:
    """The page points a repo with no walk order at this file. A dead link
    there would be the blank button CLAUDE.md warns about, one layer down."""
    template = ROOT / "docs" / "__templates__" / "walk.md"
    assert template.is_file()
    text = template.read_text(encoding="utf-8")
    #: The syntax the parser reads, and the only one it reads.
    assert "```yaml" in text
    assert "surfaces:" in text
