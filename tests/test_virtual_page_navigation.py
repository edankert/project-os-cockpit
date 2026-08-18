"""ISS-0193 / ISS-0194 — reaching a virtual page, and being told which one.

Two defects on the surface PHASE-035 built, both found by Edwin from use on
2026-08-18 and both in the renderer rather than in the record: `~checks` was
reachable and correct, and the two ways of *getting there* were wrong.

Source assertions rather than behavioural ones, deliberately. Both defects are
about a line that is missing or a call that happens in the wrong order, and
neither has a payload to inspect — the first paints a page and then paints over
it, and the second leaves a CSS class on the wrong element.
"""

from __future__ import annotations

import re
from pathlib import Path

RENDERER = Path(__file__).resolve().parent.parent / "desktop" / "src" / "renderer" / "renderer.ts"


def test_the_checks_page_suppresses_the_arriving_view_landing() -> None:
    """ISS-0193: `~checks` must not be painted over by the `~tests` landing.

    `renderChecksPage` switches the navigator to Tests, and `loadWsNav` lands
    that view on `~tests` because `currentRel` is not `~checks` yet — the branch
    assigns it only after this function resolves. **Not a race**: everything
    after the `setNavMode` call is synchronous, so the landing always starts
    second and always finishes last.

    Asserted on the suppression being armed **before** the mode switch, because
    that ordering is the entire fix: armed afterwards, `loadWsNav` has already
    read the flag and lands anyway.
    """
    src = RENDERER.read_text(encoding="utf-8")
    block = src[src.index("async function renderChecksPage"):]
    block = block[:block.index("function buildChecksPage")]
    assert "suppressLandingOnce = true;" in block, (
        "renderChecksPage no longer suppresses the arriving Tests landing (ISS-0193)"
    )
    assert block.index("suppressLandingOnce = true;") < block.index("setNavMode('tests')"), (
        "the suppression must be armed BEFORE setNavMode, or loadWsNav lands first"
    )


def test_every_virtual_page_refreshes_the_nav_highlight() -> None:
    """ISS-0194: no `~page` may commit its rel without refreshing the highlight.

    The defect was seven copies of the same five lines with one line —
    `refreshActiveNavRow()` — missing from every copy, so the left pane went on
    highlighting the note you had left. Not an absent selection: a **wrong** one,
    shown confidently.

    So the fix is that there is now one copy, and this asserts the shape rather
    than the behaviour: any branch that assigns `currentRel` and pushes history
    by hand is a copy, and a copy is what loses the line again.
    """
    src = RENDERER.read_text(encoding="utf-8")
    assert "function commitVirtualPage(" in src
    body = src[src.index("function commitVirtualPage("):]
    body = body[:body.index("\n}")]
    assert "refreshActiveNavRow()" in body, "the helper must refresh the highlight"

    hand_rolled = re.findall(
        r"currentRel = normalised;\s*\n\s*currentDispatchHistory = null;", src)
    assert not hand_rolled, (
        f"{len(hand_rolled)} virtual-page branch(es) still commit by hand; "
        "they will lose refreshActiveNavRow() the way the first seven did"
    )


def test_the_tier_heads_still_carry_the_address_the_highlight_matches_on() -> None:
    """The other half of ISS-0194, and the half that was never broken.

    `refreshActiveNavRow` matches `summary[data-rel]` against `currentRel`, and
    the tier heads have carried `data-rel` since ISS-0132. Asserted because the
    fix depends on it: if the head stopped carrying the address, the highlight
    would go quiet again and the helper above would still look correct.
    """
    src = RENDERER.read_text(encoding="utf-8")
    assert "summary.dataset.rel = groupRel;" in src
    assert "summary[data-rel]" in src


# ---- FEAT-0123: the surfaces say one thing --------------------------------


def test_each_tier_head_addresses_its_own_tier() -> None:
    """ISS-0203: the label differed and the destination did not.

    Every tier head carried the identical `~checks`, so selecting Tier 2
    rendered what Tier 1 had. Swept across seven nav modes on both sidecars,
    these were the **only** sibling groups in the navigator sharing a url.

    Asserted on the payload rather than the renderer, because the address is
    what makes the fix work: a filter in the url is also what lets back/forward
    move between tiers and what the release page can link to.
    """
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
    from project_os_cockpit.cockpit import nav_payload
    from project_os_cockpit.index import Index

    index = Index.build(Path(__file__).resolve().parent.parent / "docs")
    tiers = {
        g["key"]: g.get("url")
        for g in nav_payload(index, mode="tests")["groups"]
        if str(g["key"]).startswith("tier")
    }
    assert len(tiers) >= 2, "this repo no longer has two tiers to distinguish"
    assert len(set(tiers.values())) == len(tiers), (
        f"tier heads share a destination again: {tiers}"
    )
    for key, url in tiers.items():
        assert url.endswith("/tier/" + key.removeprefix("tier")), (key, url)


def test_the_checks_route_parses_a_tier_out_of_the_address() -> None:
    """The other half: an address carrying a tier has to be routed.

    A payload that emits `~checks/tier/2` against a renderer that only matches
    `~checks` exactly is a dead click — which is [[ISS-0142]]'s defect, and
    the reason this asserts the route rather than trusting the payload.
    """
    src = RENDERER.read_text(encoding="utf-8")
    assert "normalised.startsWith('~checks/')" in src, (
        "the checks route matches only the bare address; every tier head is a "
        "dead click"
    )
    assert "~checks\\/tier\\/(\\d+)" in src or "~checks\\\\/tier" in src


def test_no_filter_axis_renders_a_chip_per_corpus_item() -> None:
    """ISS-0204: 164 chips came before the first check.

    `areas` (76) and `covers` (80) scale with the corpus, so the surface
    degraded exactly as the suite became more useful — and the ratio was worse
    in the small repo, 1.9 chips per check against 0.28.
    """
    src = RENDERER.read_text(encoding="utf-8")
    assert "const CHIP_CAP" in src, "the filter bar has no cap again"
    block = src[src.index("function buildCheckFilters"):]
    block = block[:block.index("\n}")]
    assert "values.length > CHIP_CAP" in block
    assert "'details'" in block, "a wide axis must collapse, not disappear"
    assert "selected" in block, (
        "a collapsed axis must show its own selection, or a filter can hide "
        "inside a fold and quietly shorten the list"
    )
