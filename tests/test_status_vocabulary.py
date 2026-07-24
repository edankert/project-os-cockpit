"""Status vocabulary parity across every palette surface (ISS-0023, TST-0019).

The project-os status vocabulary is consumed by six surfaces: two Python
tables, one JS object, two CSS rule blocks, and the index-page collapse set.
Before TASK-0198 they were independent literals and drifted — `implemented`
was coloured and ranked with the done family, yet missing from the
Hide-completed set and from the tasks-pane ordering, so a corpus of
delivered-but-unverified requirements looked finished but never cleared.

These tests pin `statuses.py` as the single source of membership and parse
the JS/CSS surfaces to prove they still agree with it.
"""

from __future__ import annotations

import re
from pathlib import Path

from project_os_cockpit import statuses
from project_os_cockpit.cockpit import TASK_STATUS_ORDER
from project_os_cockpit.templates import COLLAPSED_BY_DEFAULT, STATUS_RANK

STATIC = Path(statuses.__file__).parent / "static"
COCKPIT_JS = STATIC / "cockpit.js"
BASE_CSS = STATIC / "base.css"
COCKPIT_CSS = STATIC / "cockpit.css"


# ---------------------------------------------------------------- vocabulary

def test_every_status_has_exactly_one_band() -> None:
    seen: dict[str, str] = {}
    for band, members in statuses.BANDS.items():
        for status in members:
            assert status not in seen, (
                f"{status!r} is in both {seen[status]!r} and {band!r}"
            )
            seen[status] = band
    assert set(seen) == set(statuses.VOCABULARY)


def test_every_band_has_a_palette_token() -> None:
    assert set(statuses.BAND_TOKEN) == set(statuses.BANDS)


def test_delivered_is_not_completed() -> None:
    """The crux of ISS-0023 — regressing this re-hides unverified work."""
    assert not (statuses.DELIVERED_STATUSES & statuses.COMPLETED_STATUSES)
    assert "implemented" in statuses.DELIVERED_STATUSES
    assert not statuses.is_completed("implemented")
    assert statuses.is_completed("verified")
    assert statuses.band_of("IMPLEMENTED") == "delivered"
    assert statuses.band_of("nonsense") is None


# ------------------------------------------------------------ python surfaces

def test_task_status_order_covers_the_vocabulary() -> None:
    missing = statuses.VOCABULARY - set(TASK_STATUS_ORDER)
    assert not missing, f"unranked in the tasks pane: {sorted(missing)}"


def test_status_rank_covers_the_vocabulary() -> None:
    missing = statuses.VOCABULARY - set(STATUS_RANK)
    assert not missing, f"unranked on index pages: {sorted(missing)}"


def test_delivered_ranks_between_pending_and_done() -> None:
    """Delivered work is no longer to-do, but is not finished either."""
    pending = max(STATUS_RANK[s] for s in statuses.BANDS["pending"])
    delivered = [STATUS_RANK[s] for s in statuses.BANDS["delivered"]]
    done = min(STATUS_RANK[s] for s in statuses.BANDS["done"])
    assert pending < min(delivered)
    assert max(delivered) < done


def test_collapsed_by_default_is_terminal_only() -> None:
    assert COLLAPSED_BY_DEFAULT == statuses.COMPLETED_STATUSES
    assert "implemented" not in COLLAPSED_BY_DEFAULT


# ---------------------------------------------------------------- js surface

def _js_completed_statuses() -> set[str]:
    src = COCKPIT_JS.read_text(encoding="utf-8")
    match = re.search(r"var COMPLETED_STATUSES = \{(.*?)\};", src, re.DOTALL)
    assert match, "COMPLETED_STATUSES literal not found in cockpit.js"
    body = re.sub(r"//[^\n]*", "", match.group(1))
    return set(re.findall(r'["\']?([a-z][a-z-]*)["\']?\s*:\s*1', body))


def test_js_completed_set_matches_python() -> None:
    assert _js_completed_statuses() == set(statuses.COMPLETED_STATUSES)


def test_js_never_hides_delivered_work() -> None:
    assert not (_js_completed_statuses() & statuses.DELIVERED_STATUSES)


# --------------------------------------------------------------- css surfaces

def _css_status_map(path: Path, selector: str) -> dict[str, str]:
    """Map data-status value -> the --status-* token its rule resolves to."""
    src = path.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    # Rules are written as one-or-more comma-separated selectors then a block.
    for chunk in re.findall(
        rf"((?:\.{selector}\[data-status=\"[a-z-]+\"\],?\s*)+)\{{([^}}]*)\}}", src
    ):
        selectors, block = chunk
        token = re.search(r"var\((--status-[a-z-]+)\)", block)
        if not token:
            continue
        for status in re.findall(r'data-status="([a-z-]+)"', selectors):
            out[status] = token.group(1)
    return out


def test_chip_css_covers_the_vocabulary_with_the_right_tokens() -> None:
    mapped = _css_status_map(BASE_CSS, "status-chip")
    missing = statuses.VOCABULARY - set(mapped)
    assert not missing, f"no chip colour in base.css: {sorted(missing)}"
    for status, token in mapped.items():
        if status in statuses.VOCABULARY:
            expected = statuses.BAND_TOKEN[statuses.STATUS_BAND[status]]
            assert token == expected, f"{status}: {token} != {expected}"


def test_group_icon_css_covers_the_vocabulary_with_the_right_tokens() -> None:
    mapped = _css_status_map(COCKPIT_CSS, "group-icon")
    missing = statuses.VOCABULARY - set(mapped)
    assert not missing, f"no group-icon colour in cockpit.css: {sorted(missing)}"
    for status, token in mapped.items():
        if status in statuses.VOCABULARY:
            expected = statuses.BAND_TOKEN[statuses.STATUS_BAND[status]]
            assert token == expected, f"{status}: {token} != {expected}"


def test_every_band_token_is_defined_in_both_themes() -> None:
    src = BASE_CSS.read_text(encoding="utf-8")
    light = src.split('[data-theme="dark"]')[0]
    dark = src.split('[data-theme="dark"]')[1]
    for token in statuses.BAND_TOKEN.values():
        assert re.search(rf"{token}:\s*hsl\(", light), f"{token} missing (light)"
        assert re.search(rf"{token}:\s*hsl\(", dark), f"{token} missing (dark)"


def test_status_tokens_stay_muted() -> None:
    """REQ-0012: every semantic hue is ≤60% saturation."""
    src = BASE_CSS.read_text(encoding="utf-8")
    for token in statuses.BAND_TOKEN.values():
        for sat in re.findall(rf"{token}:\s*hsl\(\d+ (\d+)%", src):
            assert int(sat) <= 60, f"{token} is {sat}% saturated"
