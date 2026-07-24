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

import pathlib
import re
from pathlib import Path

from project_os_cockpit import statuses
from project_os_cockpit.cockpit import _ACTIVE_DONE, DONE_BY_TYPE, TASK_STATUS_ORDER, is_done_status
from project_os_cockpit.templates import COLLAPSED_BY_DEFAULT, STATUS_RANK

STATIC = Path(statuses.__file__).parent / "static"
COCKPIT_JS = STATIC / "cockpit.js"
BASE_CSS = STATIC / "base.css"
COCKPIT_CSS = STATIC / "cockpit.css"
DESKTOP_TS = (
    pathlib.Path(statuses.__file__).resolve().parent.parent.parent
    / "desktop" / "src" / "renderer" / "renderer.ts"
)


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
    """The crux of ISS-0023 — delivered-but-unsigned-off work stays visible.

    `implemented` was the founding member of this band; ADR-0007 retired the
    requirement `verified` status and made `implemented` terminal, so it moved
    to `done`. The band still holds `staged` (release ready, not live) and
    `monitoring` (risk mitigated, still watched), which remain non-terminal.
    """
    assert not (statuses.DELIVERED_STATUSES & statuses.COMPLETED_STATUSES)
    assert "staged" in statuses.DELIVERED_STATUSES
    assert not statuses.is_completed("staged")
    assert statuses.is_completed("implemented")   # terminal since ADR-0007
    assert statuses.band_of("STAGED") == "delivered"
    assert statuses.band_of("implemented") == "done"
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
    assert "staged" not in COLLAPSED_BY_DEFAULT      # delivered, not terminal
    assert "implemented" in COLLAPSED_BY_DEFAULT     # terminal since ADR-0007


def test_done_by_type_recognises_terminal_requirement_status() -> None:
    """`DONE_BY_TYPE` is a seventh surface the original parity test missed.

    It drifted exactly the way ISS-0023 described: after ADR-0007 made
    `implemented` the terminal requirement status, `DONE_REQ` still keyed on
    the retired `verified` and omitted `implemented`, so the cockpit's own
    progress boxes counted every migrated requirement as unfinished. Found by
    independent review, not by this suite — hence this test.
    """
    assert is_done_status("requirement", "implemented")
    assert not is_done_status("requirement", "staged")   # delivered, not terminal
    # No per-type done vocabulary may treat a delivered (non-terminal) status
    # as done — that is the ISS-0023 failure mode expressed per type.
    for members in DONE_BY_TYPE.values():
        assert not (set(members) & statuses.DELIVERED_STATUSES), (
            f"a done vocabulary claims a delivered status: {set(members) & statuses.DELIVERED_STATUSES}"
        )


def test_active_done_is_the_completed_set() -> None:
    """The Active-mode done set derives from the canonical vocabulary."""
    assert _ACTIVE_DONE == statuses.COMPLETED_STATUSES
    assert "implemented" in _ACTIVE_DONE
    assert not (_ACTIVE_DONE & statuses.DELIVERED_STATUSES)


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

def _css_status_rules(path: Path, selector: str) -> list[tuple[list[str], str]]:
    """Every `[data-status=…]` rule for `selector`, in source order.

    Source order matters: CSS resolves same-specificity conflicts last-wins,
    so a later rule silently overrides an earlier one. The parser must see
    *all* rules, not only the ones that happen to use a token (ISS-0024 §2).
    """
    src = path.read_text(encoding="utf-8")
    rules: list[tuple[list[str], str]] = []
    for selectors, block in re.findall(
        rf"((?:\.{selector}\[data-status=\"[a-z-]+\"\],?\s*)+)\{{([^}}]*)\}}", src
    ):
        rules.append((re.findall(r'data-status="([a-z-]+)"', selectors), block))
    return rules


def _css_status_map(path: Path, selector: str) -> dict[str, str]:
    """Map data-status value -> the --status-* token its rule resolves to.

    Last-wins, mirroring the cascade.
    """
    out: dict[str, str] = {}
    for statuses_in_rule, block in _css_status_rules(path, selector):
        token = re.search(r"var\((--status-[a-z-]+)\)", block)
        if not token:
            continue
        for status in statuses_in_rule:
            out[status] = token.group(1)
    return out


# A `color:` on a status selector must resolve through a palette token. A raw
# literal renders a colour the parity map cannot see — the first ISS-0024 §2
# blind spot, where appending one red rule left the whole suite green.
_COLOUR_DECL_RE = re.compile(r"(?<![-\w])color\s*:\s*([^;}]+)")


def _literal_colour_rules(path: Path, selector: str) -> list[tuple[list[str], str]]:
    bad = []
    for statuses_in_rule, block in _css_status_rules(path, selector):
        for decl in _COLOUR_DECL_RE.findall(block):
            value = decl.strip()
            if not re.fullmatch(r"var\(--status-[a-z-]+\)", value):
                bad.append((statuses_in_rule, value))
    return bad


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
    """REQ-0012: every semantic hue is ≤60% saturation.

    Accepts both `hsl(H S% L%)` and legacy `hsl(H, S%, L%)`, and asserts each
    token was actually matched. The comma form used to slip past the regex
    entirely, so a 90%-saturated token passed by matching nothing at all —
    the second ISS-0024 §2 blind spot.
    """
    src = BASE_CSS.read_text(encoding="utf-8")
    for token in statuses.BAND_TOKEN.values():
        decls = re.findall(rf"{token}\s*:\s*([^;}}]+)", src)
        assert decls, f"{token} is not defined in base.css"
        for value in decls:
            m = re.search(r"hsl\(\s*[\d.]+\s*,?\s+([\d.]+)%", value)
            assert m, f"{token} is not a parseable hsl() value: {value.strip()!r}"
            assert float(m.group(1)) <= 60, f"{token} is {m.group(1)}% saturated"


def test_no_literal_colour_on_status_selectors() -> None:
    """Every status rule paints through a palette token, never a raw literal."""
    for path, selector in ((BASE_CSS, "status-chip"), (COCKPIT_CSS, "group-icon")):
        bad = _literal_colour_rules(path, selector)
        assert not bad, (
            f"{path.name}: status rules set a non-token colour — "
            + "; ".join(f"{s} -> {v!r}" for s, v in bad)
        )


def test_bundled_validator_matches_the_canonical_one() -> None:
    """`validate_docs_bundled.py` is a verbatim copy — drift ships a stale taxonomy.

    It fell behind ADR-0007 (still allowing requirement `verified` after the
    canonical validator dropped it), which is how a repo validating through the
    cockpit's fallback path would have accepted a retired status. The
    CHG-20260717 follow-up asked for a sync check; this is it.
    """
    import pathlib
    root = pathlib.Path(__file__).resolve().parent.parent
    canonical = (root / "tools" / "scripts" / "validate-docs.py").read_text(encoding="utf-8")
    bundled = (root / "src" / "project_os_cockpit" / "validate_docs_bundled.py").read_text(encoding="utf-8")
    assert bundled == canonical, (
        "validate_docs_bundled.py has drifted from tools/scripts/validate-docs.py; "
        "re-copy it (it is a verbatim bundle, not a fork)"
    )


# ----------------------------------------------------- desktop (mode 3) surface

def _ts_set(name: str) -> set[str]:
    """Extract a `const NAME = new Set([...])` literal from the desktop renderer."""
    src = DESKTOP_TS.read_text(encoding="utf-8")
    m = re.search(rf"const {name} = new Set\(\[(.*?)\]\)", src, re.DOTALL)
    assert m, f"{name} literal not found in renderer.ts"
    body = re.sub(r"//[^\n]*", "", m.group(1))
    return set(re.findall(r"'([a-z][a-z-]*)'", body))


def test_desktop_completed_set_matches_python() -> None:
    """The Electron renderer keeps its own Hide-completed vocabulary.

    It is a third copy (after statuses.py and cockpit.js) and nothing guarded
    it until ADR-0007 — it still had `verified` and no `implemented`, so on the
    desktop every migrated requirement stayed visible as unfinished work.
    """
    assert _ts_set("COMPLETED_STATUSES") >= set(statuses.COMPLETED_STATUSES), (
        "desktop COMPLETED_STATUSES is missing: "
        f"{set(statuses.COMPLETED_STATUSES) - _ts_set('COMPLETED_STATUSES')}"
    )
    assert not (_ts_set("COMPLETED_STATUSES") & statuses.DELIVERED_STATUSES)


def test_desktop_done_statuses_cover_the_done_band() -> None:
    """Session progress views use a separate DONE_STATUSES set."""
    done = _ts_set("DONE_STATUSES")
    assert "implemented" in done
    assert not (done & statuses.DELIVERED_STATUSES)


def test_desktop_status_colours_agree_with_the_bands() -> None:
    """`STATUS_COLOR_BY_KEY` must not colour a status into the wrong band."""
    src = DESKTOP_TS.read_text(encoding="utf-8")
    m = re.search(r"const STATUS_COLOR_BY_KEY: Record<string, string> = \{(.*?)\n\};", src, re.DOTALL)
    assert m, "STATUS_COLOR_BY_KEY literal not found"
    body = re.sub(r"//[^\n]*", "", m.group(1))
    mapped = dict(re.findall(r"'?([a-z][a-z_-]*)'?\s*:\s*'var\((--status-[a-z-]+)\)'", body))
    for status, token in mapped.items():
        band = statuses.STATUS_BAND.get(status)
        if band is None:
            continue          # desktop-only aliases (in_progress, …) are fine
        assert token == statuses.BAND_TOKEN[band], (
            f"desktop colours {status} as {token}, band says {statuses.BAND_TOKEN[band]}"
        )
    assert mapped.get("implemented") == "--status-done"
