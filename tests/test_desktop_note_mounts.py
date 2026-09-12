"""Two rules about how the desktop window shows a note (ISS-0294, ISS-0295).

Source-level guards on `desktop/src/renderer/renderer.ts`, like the others in
this suite that read it: the renderer is a plain script with no module
boundary, so its wiring can only be asserted from its text. The behaviour was
seen in the running window through the debugging port on 2026-09-10; these
keep the wiring from being lost.
"""

from __future__ import annotations

import re
from pathlib import Path

from conftest import js_function_body

REPO_ROOT = Path(__file__).resolve().parents[1]
RENDERER = REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts"


def _src() -> str:
    return RENDERER.read_text(encoding="utf-8")


def test_every_note_mount_points_its_images_at_the_sidecar() -> None:
    """The sidecar writes `<img src="/docs/…">`. The window's page is
    `file://`, so without the rewrite every image in every note resolved to
    `file:///docs/…` and was a broken icon (ISS-0294).

    Counted rather than named: a fourth place that mounts a note and forgets
    the rewrite fails here."""
    src = _src()
    mounts = [m.start() for m in re.finditer(r"\.innerHTML = [^;\n]*data\.html;", src)]
    assert len(mounts) >= 3, "the three note mounts moved; re-read this test"
    for at in mounts:
        next_line = src[at:].split("\n", 2)[1]
        assert "pointImagesAtSidecar(" in next_line, (
            f"the note mount at offset {at} does not rewrite its images on the next line")


def test_the_rewrite_leaves_a_protocol_relative_src_alone() -> None:
    body = js_function_body(_src(), "function pointImagesAtSidecar(")
    assert "img[src^=\"/\"]" in body
    assert "startsWith('//')" in body, "`//host/x` names its own host and must not be prefixed"


def test_a_file_change_refreshes_the_list_without_landing() -> None:
    """A soft reload called `loadWsNav()`, which also lands the mode on its
    page. In Design mode that replaced the open note with `~design` on every
    file write in the project (ISS-0295)."""
    src = _src()
    reload = js_function_body(src, "function scheduleSoftReload(")
    assert "loadWsNav({ land: false })" in reload
    assert "loadWsNav()" not in reload, "a bare call would land again"
