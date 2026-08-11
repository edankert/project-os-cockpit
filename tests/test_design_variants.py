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
