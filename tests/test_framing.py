"""ADR-0042 / RISK-0008 — the sandbox is the only boundary a framed file has.

Since ADR-0042 the cockpit will frame any file inside a workspace's `docs/`.
That is defensible because `/docs/<rel>` already served every one of those
files by path, with no allowlist and no authentication, on a socket that binds
`0.0.0.0` by design — so framing widened no read access.

What it did do is leave **one attribute** between a framed document and the
cockpit: the frame is sandboxed without `allow-same-origin`, which gives it an
opaque origin and no way to read the sidecar API. `allow-scripts` sits right
beside it. Nothing in the code said so, and a boundary nobody names is one a
refactor removes; this is the test RISK-0008 closes on.
"""

from __future__ import annotations

import inspect
import re
from pathlib import Path

from conftest import js_function_body

REPO_ROOT = Path(__file__).resolve().parent.parent
RENDERER = REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts"

#: `sandbox` set on any element, however the value is spelled.
SANDBOX_SET = re.compile(r"setAttribute\(\s*'sandbox'\s*,\s*([^)]*)\)")


def test_no_frame_is_ever_given_allow_same_origin() -> None:
    """The whole of RISK-0008 in one assertion. With `allow-same-origin` the
    framed document shares this window's origin and can read every endpoint
    the cockpit can — including, since ADR-0042, one that serves any file
    under `docs/`."""
    src = RENDERER.read_text(encoding="utf-8")
    sets = SANDBOX_SET.findall(src)
    assert sets, "no sandbox attribute is set anywhere; a frame lost its boundary"
    for value in sets:
        assert "allow-same-origin" not in value, (
            "a frame was given allow-same-origin: since ADR-0042 the cockpit "
            "frames any file under docs/, and this attribute is the only thing "
            "keeping a framed document out of the sidecar API (RISK-0008)"
        )


def test_the_reason_is_written_where_the_attribute_is() -> None:
    """A boundary nobody names is one a refactor removes. The sentence has to
    sit at the attribute, not only in a note somebody may never open."""
    src = RENDERER.read_text(encoding="utf-8")
    i = src.index("frame.setAttribute('sandbox', 'allow-scripts');")
    preceding = src[max(0, i - 1200):i]
    # "same-origin", not the full flag: `test_design_bench.py` refuses the
    # literal anywhere in renderer.ts, so the comment spells it without its
    # prefix. Two guards, one rule.
    assert "same-origin" in preceding and "RISK-0008" in preceding, (
        "the frame no longer says why allow-same-origin is absent"
    )


# ---- the viewer (FEAT-0148 / REQ-0064) ------------------------------------


def test_one_handler_serves_both_route_names() -> None:
    """`/framed/<rel>` is the name that survives; `/design-asset/<rel>` is the
    name it had when only a design could be framed, kept until the bench goes.
    Both reach one handler, so the two cannot drift while both exist."""
    from project_os_cockpit import server as server_mod

    src = inspect.getsource(server_mod)
    assert 'if path.startswith("/framed/"):' in src
    assert src.count("self._serve_framed_file(") == 2, (
        "the two route names no longer share a handler"
    )


def test_the_viewer_frames_a_file_and_not_a_design() -> None:
    """The point of FEAT-0148: the surface knows about files, not designs. If
    it asked the design register for anything, it would inherit the bench's
    limit — that a file must be claimed by a design note to be shown."""
    src = RENDERER.read_text(encoding="utf-8")
    body = js_function_body(src, "async function renderViewerPage(")
    assert "fetchDesignRegister" not in body and "designRegister" not in body, (
        "the viewer consults the design register; it must frame any file"
    )
    assert "/framed/" in body, "the viewer no longer uses the framing route"
    assert "theme=" in body, (
        "the theme stopped travelling in the URL -- the frame has an opaque "
        "origin and cannot read the app's, so one style-guide page would stop "
        "following six projects (TASK-0231)"
    )
    assert "referrerpolicy" in body


def test_the_viewer_page_is_routed_before_the_bench() -> None:
    """`~view/` and `~design/` both exist until TASK-0615 removes the bench.
    Order matters while they do: whichever is tested first wins a prefix."""
    src = RENDERER.read_text(encoding="utf-8")
    nav = js_function_body(src, "async function navigateToInner(")
    assert "normalised.startsWith('~view/')" in nav, "the viewer has no route"
    assert nav.index("normalised.startsWith('~view/')") < nav.index("normalised === '~design'")


def test_the_viewer_reaches_another_workspaces_sidecar() -> None:
    """Cross-repo framing is allowed (Edwin, 2026-09-12), and it works by
    asking THAT workspace's sidecar — each one still bounds its own `docs/`,
    so nothing here can read another repo's files by path."""
    src = RENDERER.read_text(encoding="utf-8")
    body = js_function_body(src, "function viewerTarget(")
    assert "sidecarUrls.get(" in body, (
        "cross-repo framing no longer addresses the other workspace's sidecar"
    )
    assert "projectId" in body


def test_the_way_back_is_recorded_on_the_way_in() -> None:
    """`currentRel` is the viewer itself by the time the viewer renders, so
    the note that sent the reader there has to be captured before navigating —
    a button computed afterwards points at the page it sits on."""
    src = RENDERER.read_text(encoding="utf-8")
    outer = js_function_body(src, "async function navigateTo(")
    assert "viewerCameFrom = currentRel" in outer
    assert outer.index("viewerCameFrom") < outer.index("await navigateToInner(")
