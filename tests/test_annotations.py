"""Annotations anchored to a place, never to a coordinate (FEAT-0069).

`append_design_comment` already learned this once: *"the anchor is a region id,
never a coordinate. Pixel pins die on the next revision, and the founding
artifact went through six in one session."* This is that lesson applied to a
richer anchor — a variant, a path within it, and the quoted text.

The quote is the load-bearing part. It is what lets a moved anchor be
**re-found** rather than guessed at, and what lets a lost one **say so**: a
comment silently re-attached to different content is worse than one that admits
it is lost, because the reader trusts it and it is about something else.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from project_os_cockpit import review

DESIGN = (
    "# D\n\n"
    "## Variant Compact\n\n```html\n<p>the header sits tight</p>\n```\n\n"
    "## Variant Roomy\n\n```html\n<p>the header breathes</p>\n```\n"
)


def test_annotation_is_a_kind_the_queue_understands() -> None:
    assert "annotation" in review.KINDS


def test_a_coordinate_cannot_be_smuggled_into_an_anchor() -> None:
    """The schema is an allow-list precisely so `{x, y}` cannot be persisted
    under any name and quietly become a pixel pin."""
    got = review.normalise_anchor(
        {"x": 10, "y": 20, "top": 5, "variant": "Compact", "quote": "the header"},
    )
    assert got == {"quote": "the header", "variant": "Compact"}
    assert "x" not in got and "y" not in got and "top" not in got


def test_a_non_dict_anchor_is_dropped_rather_than_crashing() -> None:
    assert review.normalise_anchor("top-left") == {}
    assert review.normalise_anchor(None) == {}


def test_a_surviving_quote_resolves_by_quote() -> None:
    """The strongest evidence the commented thing survived, and independent of
    any structure."""
    got = review.resolve_anchor(
        {"quote": "the header sits tight", "variant": "Compact"}, DESIGN,
    )
    assert got["state"] == "found" and got["by"] == "quote"


def test_a_gone_quote_in_a_surviving_variant_reports_moved() -> None:
    """Not "found" — the exact spot is gone and saying otherwise would put the
    comment somewhere it does not belong."""
    got = review.resolve_anchor({"quote": "deleted words", "variant": "Compact"}, DESIGN)
    assert got["state"] == "moved"
    assert "still exists" in str(got["detail"])


def test_an_anchor_whose_variant_is_gone_is_lost_not_floated() -> None:
    """TASK-0308's rule: never floats to the wrong spot."""
    got = review.resolve_anchor({"quote": "deleted", "variant": "Deleted"}, DESIGN)
    assert got["state"] == "lost"


def test_resolution_prefers_the_quote_over_the_variant() -> None:
    """Order is weakest-claim-last. A quote that survived in a *renamed*
    variant is still evidence the content survived."""
    moved = DESIGN.replace("## Variant Compact", "## Variant Tight")
    got = review.resolve_anchor(
        {"quote": "the header sits tight", "variant": "Compact"}, moved,
    )
    assert got["state"] == "found", got


def test_an_annotation_round_trips_through_the_store(tmp_path: Path) -> None:
    store = review.ReviewStore(tmp_path)
    store.add(
        kind="annotation",
        title="the header is tight",
        body="two steps smaller than the rest",
        items=["DES-9001"],
        subject="DES-9001",
        anchor={"variant": "Compact", "quote": "the header sits tight", "x": 4},
    )
    reloaded = review.ReviewStore(tmp_path)
    entries = [r for r in reloaded.open_requests() if r.get("kind") == "annotation"]
    assert len(entries) == 1, entries
    anchor = entries[0]["anchor"]
    assert anchor == {"quote": "the header sits tight", "variant": "Compact"}


def test_an_unknown_kind_is_still_refused(tmp_path: Path) -> None:
    """Widening KINDS must not have widened it to anything."""
    store = review.ReviewStore(tmp_path)
    with pytest.raises(ValueError):
        store.add(kind="scribble", title="x", body="y", items=[])


# ---------------------------------------------------------------------------
# TASK-0307 / TASK-0308 — the affordance and the listing
# ---------------------------------------------------------------------------

RENDERER = Path(__file__).resolve().parent.parent / "desktop" / "src" / "renderer" / "renderer.ts"
SERVER = Path(__file__).resolve().parent.parent / "src" / "project_os_cockpit" / "server.py"


def test_the_affordance_anchors_to_a_quote_never_to_coordinates() -> None:
    """The lesson `append_design_comment` already learned, asserted where it
    would be easiest to undo."""
    body = RENDERER.read_text(encoding="utf-8").split("function annotationFromSelection")[1]
    body = body.split("\nfunction ")[0]
    assert "quote:" in body
    for coord in ("clientX", "clientY", "offsetX", "pageX", "getBoundingClientRect"):
        assert coord not in body, f"the annotation anchor reads {coord}"


def test_escape_costs_nothing() -> None:
    """The selection is read at click time, so dismissing writes nothing."""
    body = RENDERER.read_text(encoding="utf-8").split("function annotationFromSelection")[1]
    body = body.split("\nfunction ")[0]
    assert "if (text === null) return;" in body


def test_the_endpoint_reads_the_stores_vocabulary_not_its_own_list() -> None:
    """A literal `("review", "question")` here would have silently refused
    `annotation` — the two-lists failure ISS-0023 is about."""
    src = SERVER.read_text(encoding="utf-8")
    assert "if kind not in review.KINDS:" in src
    assert 'if kind not in ("review", "question"):' not in src
