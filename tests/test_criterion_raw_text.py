"""A criterion carrying inline markup can be ticked (ISS-0137).

The bug: the renderer recovered the criterion from the *rendered* DOM with
`textContent`, and `note_writes.stamp_tick` matches the *source* line
exactly. Markdown eats inline markup on the way out, so the two strings
differed for every criterion containing a code span, a wikilink, bold or a
link — measured at **26 of this corpus's 53 open criteria**. The tick prompt
took the evidence and then the write was refused.

**The assertion that would have passed while this was broken** is the
tempting one: call `stamp_tick` with the raw string from the file and
watch it work. It always worked. The defect lived in what the *caller* sent.

So this drives the seam instead: render the note the way the server renders
it, take the criterion text off the rendered checkbox exactly as the client
now does, and feed *that* to the writer. A regression puts the rendered text
back on the wire and this fails.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from project_os_cockpit import note_writes
from project_os_cockpit.index import Index
from project_os_cockpit.renderer import render_markdown_body

#: `data-raw="…"` on a rendered checkbox, in document order.
_DATA_RAW_RE = re.compile(r'<input[^>]*\bdata-raw="([^"]*)"')

MARKED_UP = """# A note

## Acceptance

- [ ] Mode 1 exposes the overview, rendering the same `/api/cockpit/stats` payload as the shell
- [ ] [[RISK-0001]] is re-scanned and updated with what this changed
- [ ] The **desk** retires and its route stays served
- [ ] A plain criterion with no markup at all
"""


def _render_and_read_back(md: str) -> list[str]:
    """What the client now puts on the wire, for each checkbox in order."""
    import html as _html

    html = render_markdown_body_from_text(md)
    return [_html.unescape(m) for m in _DATA_RAW_RE.findall(html)]


def render_markdown_body_from_text(md: str, tmp: Path | None = None) -> str:
    """`render_markdown_body` takes a path; give it one."""
    target = (tmp or Path(_TMP.name)) / "note.md"
    target.write_text(md, encoding="utf-8")
    return render_markdown_body(target)


import tempfile  # noqa: E402  (used by the helper above)

_TMP = tempfile.TemporaryDirectory()


def test_every_checkbox_carries_its_source_line() -> None:
    """The rendered box knows the prose the file actually contains."""
    raws = _render_and_read_back(MARKED_UP)
    assert raws == [
        "Mode 1 exposes the overview, rendering the same `/api/cockpit/stats` payload as the shell",
        "[[RISK-0001]] is re-scanned and updated with what this changed",
        "The **desk** retires and its route stays served",
        "A plain criterion with no markup at all",
    ], "data-raw must be the SOURCE prose, markup and all"


def test_the_rendered_text_still_differs_so_the_bug_was_real() -> None:
    """Guard the premise, not just the fix.

    If Markdown ever stopped consuming this markup, the fix would be
    unnecessary and this test would be measuring nothing. Assert the gap
    exists, so the fix is never quietly pointless.
    """
    html = render_markdown_body_from_text(MARKED_UP)
    assert "<code>/api/cockpit/stats</code>" in html
    assert "`/api/cockpit/stats`" not in re.sub(r"data-raw=\"[^\"]*\"", "", html), (
        "outside data-raw the backticks are gone — which is exactly why "
        "reading textContent produced a string the source does not contain"
    )


@pytest.mark.parametrize("which", [0, 1, 2, 3])
def test_a_marked_up_criterion_ticks_end_to_end(tmp_path: Path, which: int) -> None:
    """Render → read the box → write. The whole seam, per criterion.

    Parametrised over all four so the plain one is a control: if the plain
    case passed and the marked-up ones failed, that is precisely the bug.
    """
    docs = tmp_path / "docs"
    (docs / "issues").mkdir(parents=True)
    note = docs / "issues" / "ISS-9001-Probe.md"
    note.write_text(
        '---\ntype: "[[issue]]"\nid: ISS-9001\nstatus: open\n---\n\n' + MARKED_UP,
        encoding="utf-8",
    )

    raws = _render_and_read_back(MARKED_UP)
    criterion = raws[which]

    index = Index.build(docs)
    result = note_writes.stamp_tick(
        index, "ISS-9001",
        criterion=criterion,
        evidence="driven through the render seam",
        actor="user:edwin",
    )
    assert result.get("form") == "ticked"
    assert result.get("criterion") == criterion

    body = note.read_text(encoding="utf-8")
    line = next(ln for ln in body.splitlines() if ln.startswith("- [x]"))
    assert criterion in line, "the criterion must survive the rewrite verbatim"
    assert "— evidence: driven through the render seam (user:edwin," in line
    assert body.count("- [x]") == 1, "exactly one box moves"
    assert body.count("- [ ]") == 3
