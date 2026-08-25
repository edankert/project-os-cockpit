"""The console's fit parent carries no padding (ISS-0255).

`@xterm/addon-fit` computes the terminal's rows and columns from
``getComputedStyle(parent).height`` and subtracts only the *xterm element's*
own padding. Under CSS's default `content-box` that is exact. Under
`box-sizing: border-box` — which `base.css` applies to every element in both
front doors — the reported height includes the parent's padding, so any padding
on the element xterm is opened into is room the addon spends and the terminal
cannot occupy. It asks the PTY for rows and columns that fall outside the box, and
`overflow: hidden` cuts them: 6px/8px clipped the last row at 466 of 581 pane
heights and the last two columns at every width measured.

These are source assertions rather than a rendered check because the renderer
has no DOM test harness. What they pin is the *invariant* — the measured box
and the occupied box are the same box — not the pixels.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RENDERER_CSS = REPO / "desktop" / "src" / "renderer" / "renderer.css"
# Shared with mode 1 and copied into the renderer by desktop/scripts/copy-assets.mjs.
BASE_CSS = REPO / "src" / "project_os_cockpit" / "static" / "base.css"
RENDERER_TS = REPO / "desktop" / "src" / "renderer" / "renderer.ts"


def _block(css: str, selector: str) -> str:
    """The declarations of the first rule with exactly this selector."""
    match = re.search(
        r"(?:^|\})\s*" + re.escape(selector) + r"\s*\{([^}]*)\}", css, re.MULTILINE
    )
    assert match is not None, f"no rule for {selector}"
    return match.group(1)


def test_the_renderer_is_border_box() -> None:
    """The premise. If this ever stops being true the rule below is still
    safe, but the *reason* recorded beside it is not — so assert the thing
    that makes the reason true rather than trusting the comment."""
    assert "* { box-sizing: border-box; }" in BASE_CSS.read_text(encoding="utf-8")


def test_xterm_is_opened_into_the_terminal_mount() -> None:
    """Which element is the fit parent is decided in TypeScript, not CSS. The
    padding rule below is about *that* element and nothing else, so pin the
    identification instead of assuming it."""
    assert "term.open(terminalMount)" in RENDERER_TS.read_text(encoding="utf-8")


def test_the_fit_parent_carries_no_padding() -> None:
    """The invariant. Any padding here is measured by the addon and unusable
    by the terminal, and the last row is what gets cut."""
    block = _block(RENDERER_CSS.read_text(encoding="utf-8"), ".terminal-mount")
    assert "padding" not in block, (
        "padding on .terminal-mount is spent by @xterm/addon-fit and cannot be "
        "used by the terminal — it clips the last row (ISS-0255). Put the inset "
        "on .terminal-pane."
    )


def test_the_fit_parent_still_clips() -> None:
    """`overflow: hidden` is what makes a mis-fit a *visible* defect rather
    than a harmless over-count, and it is also what keeps one from spilling
    over the rest of the shell. It stays."""
    block = _block(RENDERER_CSS.read_text(encoding="utf-8"), ".terminal-mount")
    assert "overflow: hidden" in block


def test_the_inset_survived_the_move() -> None:
    """The padding was not deleted — it was moved. A terminal whose first line
    touches the header divider is what the inset was added for."""
    block = _block(RENDERER_CSS.read_text(encoding="utf-8"), ".terminal-pane")
    assert "padding: 6px 8px" in block
