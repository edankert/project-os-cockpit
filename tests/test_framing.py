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

import re
from pathlib import Path

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
