"""The measure view (FEAT-0068) — the tool whose absence cost PHASE-022 twelve
rounds, every one beginning with hand-driven CDP measurement.

The module is TypeScript, so this asserts its **shape and its boundaries**
rather than executing it: which properties are read, that differences are
marked rather than filtered, that the markdown is differences-only, and — most
importantly — that the scope stayed at *self and artefacts*.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MEASURE = REPO / "desktop" / "src" / "renderer" / "measure.ts"
RENDERER = REPO / "desktop" / "src" / "renderer" / "renderer.ts"
INDEX = REPO / "desktop" / "src" / "renderer" / "index.html"


def test_the_module_is_loaded_before_the_renderer() -> None:
    """A plain script, like every sibling — the project has no build step for
    the renderer's modules, so load order is the dependency mechanism."""
    html = INDEX.read_text(encoding="utf-8")
    assert "./measure.js" in html
    assert html.index("./measure.js") < html.index("./renderer.js")


def test_it_measures_named_properties_not_pixels() -> None:
    """DES-0007 rejected pixel diffing: pixels diff noisily and explain
    nothing. The answer a reader needs is *the box is 4px taller*."""
    src = MEASURE.read_text(encoding="utf-8")
    for group in ("box", "type", "colour", "space"):
        assert f"['{group}'" in src, f"the {group} group is gone"
    for prop in ("font-size", "line-height", "background-color", "padding"):
        assert prop in src
    assert "canvas" not in src.lower() and "toDataURL" not in src


def test_the_box_comes_from_the_rect_not_the_style() -> None:
    """`width` reports the content box under `box-sizing: content-box`, and
    "how big is this on screen" is about the border box."""
    src = MEASURE.read_text(encoding="utf-8")
    assert "getBoundingClientRect" in src
    assert "values.width" in src and "values.height" in src


def test_every_property_is_returned_and_differences_are_marked() -> None:
    """*What is the same* is half the answer when two surfaces look different.
    A table that filtered to differences would send the reader back to the
    inspector for the rest."""
    src = MEASURE.read_text(encoding="utf-8")
    body = src.split("function diff(")[1].split("\nfunction ")[0]
    assert "differs: va !== vb" in body
    assert "if (va === vb) continue" not in body, "the diff filters instead of marking"


def test_the_markdown_is_differences_only() -> None:
    """The full table lives on screen; an issue quoting forty identical rows
    would bury its own point."""
    src = MEASURE.read_text(encoding="utf-8")
    body = src.split("function toMarkdown(")[1]
    assert "rows.filter((r) => r.differs)" in body
    assert "no differences across" in body, "an all-same comparison says nothing"


def test_the_scope_stayed_at_self_and_artefacts() -> None:
    """The feature's out-of-scope line: pointing the probe at an external app
    is its own phase with its own risk scan. Asserted so growing it there is a
    visible change rather than a quiet parameter."""
    src = MEASURE.read_text(encoding="utf-8") + RENDERER.read_text(encoding="utf-8")
    body = src.split("The measure view (FEAT-0068")[1].split("\n// ---")[0]
    for reach in ("webview", "BrowserView", "loadURL(", "fetch(`http"):
        assert reach not in body, f"the measure path reaches outside via {reach}"


def test_picking_is_a_click_and_escape_disarms() -> None:
    """Hover commits by accident, and the thing being measured is usually under
    the pointer on the way somewhere else."""
    src = RENDERER.read_text(encoding="utf-8")
    assert "function armMeasure" in src and "function disarmMeasure" in src
    assert "measurePicking && ev.key === 'Escape'" in src


def test_the_panel_does_not_take_layout_from_its_subject() -> None:
    """The subject is whatever is already on screen; reflowing it to show the
    measurements would change what is being measured."""
    css = (REPO / "desktop" / "src" / "renderer" / "renderer.css").read_text(encoding="utf-8")
    block = css.split(".measure-panel {")[1].split("}")[0]
    assert "position: fixed" in block
