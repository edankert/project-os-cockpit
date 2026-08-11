"""Every nav url is routable — the sweep, not another one-off fix (ISS-0135).

The renderer resolves a nav target through `extractRel`, which accepts exactly
two shapes and **deliberately** discards everything else::

    /docs/<rel>   -> <rel>            a note under docs/
    ~<something>  -> ~<something>     a virtual page
    anything else -> null             no data-rel, and the delegated click
                                      handler keys entirely off data-rel

That third line is the trap. A url of ``/README.md`` looks correct, serialises
correctly, renders a row that looks correct — and the row is a dead click, with
no error anywhere. `extractRel` refuses it on purpose: ``/README.md`` and
``/docs/README.md`` both reduce to ``README.md``, so routing the bare form
would collapse two distinct files onto one fetch (ISS-0037).

**This has now happened twice.** ISS-0037 was the Library's top-level rows;
it was fixed there. ISS-0135 was the eight standing documents, where the whole
point of the view is reaching them, and every one was unclickable. Both were
one builder emitting a shape another layer silently drops.

So the guard is a sweep rather than a third assertion about a specific group:
walk every mode, every group, every subgroup, every item, and require the shape.
A new builder is covered the day it is written, without anyone remembering this.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Iterator

import pytest

from project_os_cockpit.cockpit import NAV_MODES, nav_payload
from project_os_cockpit.index import Index


FIXTURE = Path(__file__).parent / "fixtures" / "index_basic"
REPO = Path(__file__).resolve().parent.parent


@pytest.fixture()
def index(tmp_path: Path) -> Index:
    target = tmp_path / "docs"
    shutil.copytree(FIXTURE, target)
    return Index.build(target)


def _walk(groups: list[dict[str, Any]], trail: str = "") -> Iterator[tuple[str, Any]]:
    """Yield ``(where, url)`` for every group and item, however nested."""
    for group in groups:
        where = f"{trail}/{group.get('key') or group.get('label') or '?'}"
        yield f"group {where}", group.get("url")
        for item in group.get("items") or []:
            ident = item.get("id") or item.get("title") or "?"
            yield f"item {where} -> {ident}", item.get("url")
            # Items nest: a feature carries its requirements, plan and tasks.
            for child in item.get("children") or []:
                cid = child.get("id") or child.get("title") or "?"
                yield f"child {where} -> {ident} -> {cid}", child.get("url")
        yield from _walk(group.get("subgroups") or [], where)


def _is_routable(url: Any) -> bool:
    """The renderer's `extractRel` contract, restated as a predicate."""
    if url is None or url == "":
        return True                      # a row with no target is legitimate
    if not isinstance(url, str):
        return False
    return url.startswith("/docs/") or url.startswith("~")


def test_every_nav_url_is_routable_by_extract_rel(index: Index) -> None:
    seen = 0
    bad: list[str] = []
    for mode in NAV_MODES:
        payload = nav_payload(index, mode=mode)
        for where, url in _walk(payload.get("groups") or []):
            if url in (None, ""):
                continue
            seen += 1
            if not _is_routable(url):
                bad.append(f"{mode}: {where} -> {url!r}")
    assert not bad, (
        "nav urls the renderer will silently drop, producing dead clicks:\n  "
        + "\n  ".join(bad)
    )
    # A sweep that swept nothing passes for the wrong reason. The fixture is
    # small, so this floor is deliberately low — it catches an empty walk (a
    # renamed key, a payload shape change), not a thin fixture.
    assert seen >= 10, f"sweep examined only {seen} urls — it is not reaching the payload"


def test_standing_documents_are_routable(index: Index) -> None:
    """The specific regression, kept alongside the sweep.

    The sweep would catch it, but only while the Intent mode happens to build
    a standing group. This says the thing ISS-0135 was about: the view whose
    entire landing is these documents can open them.
    """
    groups = nav_payload(index, mode="intent").get("groups") or []
    standing = next((g for g in groups if g.get("key") == "standing"), None)
    assert standing is not None, "the Intent mode no longer lands on the standing set"
    items = standing.get("items") or []
    assert items, "the standing group is empty"
    present = [it for it in items if it.get("url")]
    assert present, "every standing document row is targetless — all dead clicks"
    for item in present:
        assert str(item["url"]).startswith("/docs/"), (
            f"standing document {item.get('id')!r} has url {item['url']!r}; "
            "the bare form is dropped by extractRel (ISS-0135/ISS-0037)"
        )


# ---------------------------------------------------------------------------
# TASK-0385 — the view is called Intent, and the old id still answers
# ---------------------------------------------------------------------------


def test_intent_is_the_mode_and_design_still_answers(index: Index) -> None:
    """A renamed mode must not fall back silently.

    `nav_payload` maps an unknown mode to `DEFAULT_MODE` without complaint.
    That is the behaviour which, on 2026-08-11, made the Tests view look
    broken for 33 hours: a client asked for `tests`, a server that predated
    the mode answered with the features tree, and nothing anywhere said the
    request had not been understood.

    Renaming `design` to `intent` sets up exactly that failure for every
    stored preference and bookmark still saying `design` — so the old id is
    aliased, and this asserts the alias rather than trusting it.
    """
    from project_os_cockpit.cockpit import NAV_MODES as SERVER_MODES

    assert "intent" in SERVER_MODES and "design" not in SERVER_MODES

    intent = nav_payload(index, mode="intent")
    assert intent["mode"] == "intent"

    aliased = nav_payload(index, mode="design")
    assert aliased["mode"] == "intent", (
        "`design` fell through to the default instead of aliasing to `intent` — "
        "the silent-fallback trap, on every bookmark that still says design"
    )
    assert [g.get("key") for g in aliased["groups"]] == [
        g.get("key") for g in intent["groups"]
    ], "the alias answers with different content than the mode it aliases to"

    # A genuinely unknown mode must STILL fall back — the alias is a rename,
    # not a licence for anything to resolve.
    assert nav_payload(index, mode="not-a-mode")["mode"] == "features"


def test_the_renderer_and_the_server_agree_the_mode_is_intent() -> None:
    """Both front doors, and the icon key that is easy to forget.

    The button icon is looked up by `data-mode`. When the id moved and the
    icon map's key did not, the lookup fell through to `TYPE_ICONS._default`
    and the button lost its compass without any error — found while writing
    this task, which is why it is asserted rather than remembered.
    """
    ts = (REPO / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    html = (REPO / "desktop" / "src" / "renderer" / "index.html").read_text(encoding="utf-8")

    assert 'data-mode="intent"' in html, "the button still declares the old mode id"
    assert 'data-mode="design"' not in html
    assert 'aria-label="Intent"' in html, "the accessible name still says Design"

    assert "'overview', 'intent', 'features'" in ts, "renderer NAV_MODES not renamed"
    assert "intent:   '<circle" in ts, (
        "the mode icon map is keyed by data-mode; without an `intent` key the "
        "button falls back to the default glyph and loses its compass"
    )
    assert "design: 'intent'," in ts, (
        "a stored `cockpit:nav-mode` of `design` no longer migrates, so anyone "
        "carrying the old preference lands in the features fallback"
    )
    assert "intent: 'intent'," in ts, (
        "MODE_FOR_VIEW still translates the registry's `intent` to `design`, so "
        "the badge would attach to a button that no longer exists"
    )
