"""`## Variant <name>` sections as live, sandboxed fragments (FEAT-0067).

**Convention over machinery.** A variant is a markdown section carrying a
fenced html block, so an agent or a human authors one with what they already
have — no new note type, no editor, no upload. The bench renders it.

The security shape is the part worth testing: a variant is sandboxed **without**
`allow-scripts` unless the note opts in. The artifact frame allows scripts
because DES-0001 carries a theme toggle; a fragment fenced inside a note has
not earned that by default.
"""

from __future__ import annotations

from pathlib import Path

from project_os_cockpit.cockpit import design_variants

REPO = Path(__file__).resolve().parent.parent
RENDERER = REPO / "desktop" / "src" / "renderer" / "renderer.ts"


def test_a_variant_is_a_section_plus_a_fence() -> None:
    text = (
        "# D\n\n## Variant Compact\n\n```html\n<div>a</div>\n```\n\n"
        "## Variant Roomy\n\n```html\n<div>b</div>\n```\n"
    )
    got = design_variants(text)
    assert [(v["name"], v["html"]) for v in got] == [
        ("Compact", "<div>a</div>"), ("Roomy", "<div>b</div>"),
    ]


def test_prose_after_the_variants_is_not_swallowed() -> None:
    """A `##` of any kind ends the section — otherwise the last variant eats
    the rest of the note."""
    text = (
        "## Variant A\n\n```html\n<p>a</p>\n```\n\n"
        "## Notes\n\nprose\n\n```html\n<p>not a variant</p>\n```\n"
    )
    got = design_variants(text)
    assert len(got) == 1 and got[0]["html"] == "<p>a</p>", got


def test_a_variant_section_with_no_fence_is_skipped() -> None:
    """A heading alone is a plan to write one, not a variant."""
    assert design_variants("## Variant Later\n\nnot written yet\n") == []


def test_only_the_first_fence_in_a_section_counts() -> None:
    """A variant is ONE shape. A section with two fences has not decided, and
    rendering both under one name would misreport which was chosen."""
    text = "## Variant A\n\n```html\n<p>one</p>\n```\n\n```html\n<p>two</p>\n```\n"
    got = design_variants(text)
    assert len(got) == 1 and got[0]["html"] == "<p>one</p>"


def test_a_note_with_no_variants_yields_none() -> None:
    assert design_variants("# Just a design\n\nprose only.\n") == []


def test_variants_are_sandboxed_without_scripts_unless_opted_in() -> None:
    """The security shape, asserted in the renderer.

    A mockup that can run code is a mockup that can reach the cockpit. The
    default must be the restrictive one, and the opt-in must be explicit.
    """
    src = RENDERER.read_text(encoding="utf-8")
    body = src.split("function buildVariantStrip")[1].split("\nfunction ")[0]
    assert "allowScripts ? 'allow-scripts' : ''" in body, (
        "variants no longer default to a script-free sandbox"
    )
    assert "referrerpolicy" in body


def test_the_opt_in_comes_from_the_note_not_the_renderer() -> None:
    """`scripts: true` in frontmatter — a per-note decision recorded in the
    record, not a renderer-side allowance."""
    src = (REPO / "src" / "project_os_cockpit" / "cockpit.py").read_text(encoding="utf-8")
    assert '"variant_scripts": str(fm.get("scripts")' in src


def test_stylesheets_are_injected_so_mockups_wear_real_tokens() -> None:
    src = RENDERER.read_text(encoding="utf-8")
    body = src.split("function buildVariantStrip")[1].split("\nfunction ")[0]
    assert "/design-asset/" in body, "variants render without the design system"


# ---------------------------------------------------------------------------
# TASK-0302 — choosing a shape, which is not accepting a design
# ---------------------------------------------------------------------------


def test_choosing_records_the_shape_and_does_not_accept(tmp_path: Path) -> None:
    """The distinction this task exists to hold.

    Choosing a shape and accepting a design are two judgments. Collapsing them
    would let a click on a thumbnail carry an acceptance nobody made — and
    acceptance is pinned to the revision it judged (ISS-0056), which a click
    on a variant knows nothing about.
    """
    from project_os_cockpit import note_writes
    from project_os_cockpit.index import Index

    docs = tmp_path / "docs" / "designs"
    docs.mkdir(parents=True)
    note = docs / "DES-9001-Shape.md"
    note.write_text(
        '---\ntype: "[[design]]"\nid: DES-9001\naliases: ["DES-9001"]\n'
        'title: "Shape"\nstatus: proposed\n---\n\n'
        "## Variant Compact\n\n```html\n<p>a</p>\n```\n\n"
        "## Variant Roomy\n\n```html\n<p>b</p>\n```\n",
        encoding="utf-8",
    )
    result = note_writes.stamp_chosen_variant(
        Index.build(tmp_path / "docs"), "DES-9001", variant="Roomy", actor="user:edwin",
    )
    text = note.read_text(encoding="utf-8")
    assert 'chosen_variant: "Roomy"' in text
    assert "status: proposed" in text, "choosing a variant changed the design's status"
    assert result["accepted"] is False


def test_a_variant_that_was_never_written_cannot_be_chosen(tmp_path: Path) -> None:
    """`chosen_variant` naming a section nobody wrote is a record of a decision
    about nothing."""
    from project_os_cockpit import note_writes
    from project_os_cockpit.index import Index

    docs = tmp_path / "docs" / "designs"
    docs.mkdir(parents=True)
    (docs / "DES-9002-Shape.md").write_text(
        '---\ntype: "[[design]]"\nid: DES-9002\naliases: ["DES-9002"]\n'
        'title: "Shape"\nstatus: proposed\n---\n\n'
        "## Variant Only\n\n```html\n<p>a</p>\n```\n",
        encoding="utf-8",
    )
    import pytest as _pytest
    with _pytest.raises(note_writes.WriteError) as exc:
        note_writes.stamp_chosen_variant(
            Index.build(tmp_path / "docs"), "DES-9002", variant="Imaginary",
        )
    assert "no variant named" in exc.value.message


def test_the_adr_offer_is_a_dispatch_and_arrives_proposed() -> None:
    """The reasoning is the part that matters, and the cockpit does not have it.

    So the ADR is dispatched rather than written, and `proposed` rather than
    accepted — nothing here auto-accepts.
    """
    src = RENDERER.read_text(encoding="utf-8")
    body = src.split("function offerVariantAdr")[1].split("\ninterface ")[0]
    assert "dispatchToAgent" in body, "the ADR is generated rather than dispatched"
    assert "status: proposed" in body
    assert "never accepted" in body
