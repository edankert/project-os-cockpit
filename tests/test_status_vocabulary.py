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

import hashlib
import json
import pathlib
import re
from pathlib import Path

import pytest

from project_os_cockpit import statuses
from project_os_cockpit.cockpit import (
    _ACTIVE_DONE,
    DONE_BY_TYPE,
    TASK_STATUS_ORDER,
    is_done_status,
    stats_payload,
)
from project_os_cockpit.index import Index
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


def test_delivered_band_is_retired() -> None:
    """The delivered band is gone, and nothing may quietly reintroduce it.

    ISS-0023 created it for work shipped but not signed off. ADR-0007 made its
    founding member `implemented` terminal, leaving `staged` and `monitoring`;
    upstream ADR-0008 then deleted both, having measured **zero** writes of
    either across 5,890 fleet status writes. A band no status can enter is not
    a distinction the system makes, so ADR-0006 retired it.

    This asserts the retirement rather than deleting the guard: re-adding the
    band without re-deciding it should fail here.
    """
    assert "delivered" not in statuses.BANDS
    assert "delivered" not in statuses.BAND_TOKEN
    assert statuses.DELIVERED_STATUSES == frozenset()
    for gone in ("staged", "monitoring"):
        assert gone not in statuses.VOCABULARY, f"{gone} was deleted by ADR-0008"

def test_task_status_order_covers_the_vocabulary() -> None:
    missing = statuses.VOCABULARY - set(TASK_STATUS_ORDER)
    assert not missing, f"unranked in the tasks pane: {sorted(missing)}"


def test_status_rank_covers_the_vocabulary() -> None:
    missing = statuses.VOCABULARY - set(STATUS_RANK)
    assert not missing, f"unranked on index pages: {sorted(missing)}"


def test_pending_ranks_below_done() -> None:
    """Ordering invariant that survives the delivered band's retirement.

    With no intermediate band left, every pending status must still rank ahead
    of every done status on index pages.
    """
    pending = max(STATUS_RANK[s] for s in statuses.BANDS["pending"])
    done = min(STATUS_RANK[s] for s in statuses.BANDS["done"])
    assert pending < done

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


def test_superseded_reads_as_done_for_every_type_that_allows_it() -> None:
    """`superseded` is terminal; every per-type vocabulary must say so.

    The test above only checks the *negative* direction — that no done
    vocabulary claims a delivered status. Nothing asserted the positive one,
    so the ISS-0023 / ISS-0024 failure mode recurred verbatim for a different
    status: ADR-0008 added `superseded` to `task` and `phase`, `DONE_FEAT` and
    `DONE_REQ` were updated, and `DONE_TASK` and `"phase"` were not. The
    module comment above them claimed "Terminal-resolved statuses
    (superseded/retired/cancelled) count done" while the data disagreed.

    Concretely: `your-trainer` carries 72 superseded tasks and a superseded
    PHASE-012 (the frozen iOS-launch line, re-cut as PHASE-019). Every one of
    them rendered as outstanding work — reported by a rider-facing user, not
    caught here.

    `statuses.COMPLETED_STATUSES` is the source of truth: it is
    `BANDS["done"] | BANDS["archived"]`, and `superseded` lives in
    `archived`.
    """
    assert "superseded" in statuses.COMPLETED_STATUSES
    for note_type in ("task", "phase", "feature", "requirement"):
        assert is_done_status(note_type, "superseded"), (
            f"{note_type!r} does not count `superseded` as done, but ADR-0008 "
            f"makes it terminal for that type"
        )

    # The general form of the same rule: no per-type vocabulary may omit a
    # terminal status it is reachable by. `cancelled` is the sibling case.
    for note_type in ("task", "feature"):
        assert is_done_status(note_type, "cancelled")


def test_overview_mix_buckets_stay_in_the_sidecar(tmp_path: Path) -> None:
    """The overview's mix-bars must not re-derive the vocabulary in JS.

    TASK-0200's first cut classified statuses into done/doing/attention/
    backlog inside `renderer.ts` — a ninth surface restating the
    vocabulary, which is precisely the ISS-0023 failure mode. The
    bucketing moved into `stats_payload` (`status_buckets`, computed from
    `is_done_status` + `statuses.band_of`); this test fails if the
    renderer grows its own per-type done table again.
    """
    src = DESKTOP_TS.read_text(encoding="utf-8")
    # A per-type done vocabulary in the renderer is the thing being banned.
    assert "DONE_STATUSES_BY_MIX_TYPE" not in src, (
        "renderer.ts is restating a per-type done vocabulary — "
        "the sidecar owns bucketing (status_buckets); see ISS-0023"
    )
    assert "status_buckets" in src, (
        "renderer.ts should consume the sidecar's status_buckets"
    )


def test_status_buckets_agree_with_the_canonical_vocabulary(tmp_path: Path) -> None:
    """Every status the payload buckets lands where statuses.py says.

    Guards the specific confusions the bands exist to prevent:
    `implemented` is done (ADR-0007), `ready` is *not* in flight
    (ADR-0006/ADR-0008 — defined but never executed), `failing` needs
    attention, and a plain `open` issue is attention while an `open`
    requirement is merely backlog.
    """
    docs = tmp_path / "docs"

    def note(rel: str, fm: dict) -> None:
        path = docs / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = ["---"]
        for key, value in fm.items():
            lines.append(f"{key}: {json.dumps(value)}")
        lines.append("---")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    note("requirements/REQ-0001-A.md", {
        "type": "[[requirement]]", "id": "REQ-0001", "title": "A",
        "status": "implemented",
    })
    note("requirements/REQ-0002-B.md", {
        "type": "[[requirement]]", "id": "REQ-0002", "title": "B",
        "status": "open",
    })
    note("tests/TST-0001-P.md", {
        "type": "[[test]]", "id": "TST-0001", "title": "P", "status": "passing",
    })
    note("tests/TST-0002-R.md", {
        "type": "[[test]]", "id": "TST-0002", "title": "R", "status": "ready",
    })
    note("tests/TST-0003-F.md", {
        "type": "[[test]]", "id": "TST-0003", "title": "F", "status": "failing",
    })
    note("issues/ISS-0001-O.md", {
        "type": "[[issue]]", "id": "ISS-0001", "title": "O", "status": "open",
    })
    note("issues/ISS-0002-D.md", {
        "type": "[[issue]]", "id": "ISS-0002", "title": "D", "status": "doing",
    })

    payload = stats_payload(Index.build(docs))
    assert payload is not None
    buckets = payload["status_buckets"]

    # `implemented` is terminal (ADR-0007); a plain `open` requirement is not
    # attention-worthy, just unstarted.
    assert buckets["requirements"] == {
        "done": 1, "doing": 0, "attention": 0, "backlog": 1,
    }
    # `ready` is "defined, never executed" — pending, NOT in flight.
    assert buckets["tests"] == {
        "done": 1, "doing": 0, "attention": 1, "backlog": 1,
    }
    # An open issue *is* attention; a doing issue is in flight.
    assert buckets["issues"] == {
        "done": 0, "doing": 1, "attention": 1, "backlog": 0,
    }
    # Bucket totals must account for every note, or a status fell through.
    for kind, counts in buckets.items():
        assert sum(counts.values()) == sum(payload["status_mix"][kind].values()), (
            f"{kind}: bucket total disagrees with the raw status mix"
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


# ------------------------------------------------- shipped desktop artifact

DESKTOP_DIST = (
    pathlib.Path(statuses.__file__).resolve().parent.parent.parent
    / "desktop" / "dist" / "renderer" / "renderer.js"
)


def test_desktop_build_is_not_stale() -> None:
    """The Electron app loads `dist/`, not `src/` — a stale build ships old rules.

    Every other test here reads TypeScript source, so the suite stayed green
    while the running app was on a build predating the ADR-0007 status work:
    `dist/renderer/renderer.js` had zero occurrences of `implemented` while the
    source had six, and Hide-completed therefore kept showing implemented
    requirements. Guard the artifact, not just its source.

    Skipped when `dist/` is absent (fresh clone, CI without a build step) —
    there is nothing shipped to be stale.
    """
    if not DESKTOP_DIST.is_file():
        pytest.skip("desktop not built (no dist/renderer/renderer.js)")
    built = DESKTOP_DIST.read_text(encoding="utf-8", errors="replace")
    for status in sorted(statuses.COMPLETED_STATUSES):
        assert f"'{status}'" in built or f'"{status}"' in built, (
            f"desktop build is stale: {status!r} is in the canonical completed set "
            f"but absent from dist/renderer/renderer.js — run `npm run build` in desktop/"
        )
    _assert_build_matches_source()


def _desktop_source_digest() -> str:
    """The same digest `copy-assets.mjs` writes: every .ts under src/,
    path then bytes, in sorted order. Kept in step by this test failing
    if the two ever disagree."""
    src = DESKTOP_TS.parents[1]           # desktop/src
    digest = hashlib.sha256()
    for path in sorted(src.rglob("*.ts")):
        digest.update(str(path.relative_to(src.parent)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _assert_build_matches_source() -> None:
    """The build corresponds to the current source — by CONTENT, not mtime.

    ISS-0055 §4: the mtime comparison this replaces fired twice during
    review on a no-op touch. `renderer.ts` was restored byte-identical
    after a mutation run, its mtime moved past the build's, and the test
    went red with nothing actually stale.

    A hash written at build time is the honest version of the question:
    "was this artifact produced from this source", which mtime only ever
    approximated. `scripts/copy-assets.mjs` writes `dist/renderer/
    .source-hash`; a build predating that file falls back to mtime, so
    an older tree still gets the weaker check rather than none.
    """
    stamp = DESKTOP_DIST.parent / ".source-hash"
    if stamp.is_file():
        expected = _desktop_source_digest()
        recorded = stamp.read_text(encoding="utf-8").strip()
        assert recorded == expected, (
            "dist/ was built from a different renderer.ts than the one on disk — "
            "run `npm run build` in desktop/"
        )
        return
    assert DESKTOP_DIST.stat().st_mtime >= DESKTOP_TS.stat().st_mtime, (
        "dist/renderer/renderer.js is older than src/renderer/renderer.ts — "
        "run `npm run build` in desktop/ (no .source-hash present; this is the "
        "mtime fallback, which ISS-0055 §4 records as prone to false alarms)"
    )
