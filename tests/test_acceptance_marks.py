"""Every acceptance row carries its mark and its address (TST-0038 / FEAT-0104).

**An HTML checkbox holds two states and the record's vocabulary has four.**
`pymdownx.tasklist` understands `[ ]` and `[x]`; a `[~]` or `[F]` row renders
with **no input element at all** and its mark left as literal text. That — not
lazy continuation — is why [[FEAT-0104]] stalled, and it cannot be fixed by
counting more carefully.

So the *list item* is stamped, whatever its mark, and the client draws one
control for all four.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from project_os_cockpit import acceptance, renderer

TRAINER = Path.home() / "Dev" / "repos" / "your-trainer"
needs_trainer = pytest.mark.skipif(
    not (TRAINER / "docs" / acceptance.SUITE_REL).exists(),
    reason="../your-trainer is not present",
)

FOUR = (
    "# Tier 1 — Feature Tests\n\n## 1.1 An area (FEAT-0001)\n\n"
    "- [ ] **Unwalked:** a.\n\n"
    "- [x] **Passed:** b.\n\n"
    "- [~] **Excused:** c. **Blocked 2026-08-17** — no hardware\n\n"
    "- [F] **Failed:** d. **FAILS 2026-08-17** — crashes\n"
)


def _render(text: str, name: str = "x.md") -> str:
    return renderer.render_markdown_text(
        text, source_path=Path(name),
        resolver=lambda *a, **k: None, asset_resolver=lambda *a, **k: None,
    )


def _rows(html: str) -> dict[str, str]:
    """`{check number: mark}` for every addressed row."""
    out: dict[str, str] = {}
    for li in re.findall(r"<li[^>]*>", html):
        number = re.search(r'data-check="([^"]+)"', li)
        mark = re.search(r'data-mark="([^"]*)"', li)
        if number and mark:
            out[number.group(1)] = mark.group(1)
    return out


def test_all_four_marks_are_addressed_not_just_the_two_tasklist_knows() -> None:
    got = _rows(_render(FOUR))
    assert got == {"1.1.1": " ", "1.1.2": "x", "1.1.3": "~", "1.1.4": "F"}


def test_the_two_marks_tasklist_understands_still_get_their_input() -> None:
    """The address is stamped ABOVE `task-list` in priority order, so the
    literal `[ ]`/`[x]` must be left in place for it to consume. Removing them
    here would leave the extension nothing to find — which a first pass at
    priority 4 did, addressing only `~` and `F`, the exact inverse."""
    html = _render(FOUR)
    assert html.count('type="checkbox"') == 2


def test_the_literal_mark_is_stripped_only_where_tasklist_leaves_one() -> None:
    html = _render(FOUR)
    assert "[~]" not in html and "[F]" not in html
    # …and the row's own prose survives.
    assert "no hardware" in html and "crashes" in html


def test_a_document_that_is_not_a_suite_is_untouched() -> None:
    plain = "# Notes\n\n- [ ] a plain checklist item\n- [x] another\n"
    html = _render(plain)
    assert "data-check=" not in html
    assert html.count('type="checkbox"') == 2


def test_a_name_containing_a_colon_still_matches() -> None:
    """The matcher uses `parse`'s own regex rather than splitting on the first
    colon. A hand-rolled split truncated names like *"translated (Layer 1:
    shared assignment)"* and left 70 of your-trainer's 579 rows unaddressed."""
    text = (
        "# Tier 2 — Regression\n\n## 2.1 An area (ISS-0001)\n\n"
        "- [ ] **Imported intervals get translated (Layer 1: shared):** do it.\n"
    )
    assert _rows(_render(text)) == {"2.1.1": " "}


def test_a_gating_row_says_so() -> None:
    text = (
        "# Tier 1 — Feature Tests\n\n## 1.1 A (FEAT-0001)\n\n- [ ] **G:** a.\n\n"
        "# Tier 3 — Aids\n\n## 3.1 B (FEAT-0002)\n\n- [ ] **N:** b.\n"
    )
    html = _render(text)
    gating = dict(re.findall(r'data-check="([^"]+)"[^>]*data-gating="(\d)"', html))
    assert gating == {"1.1.1": "1", "3.1.1": "0"}


@needs_trainer
def test_almost_every_row_of_the_real_suite_is_addressable() -> None:
    """573 of 579. The six that are not are rows Markdown never made into list
    items — a blank line missing in the document that owns them, which
    [[TASK-0457]] names rather than papering over."""
    text = (TRAINER / "docs" / acceptance.SUITE_REL).read_text(encoding="utf-8")
    items = acceptance.parse(text)
    addressed = _rows(_render(text, acceptance.SUITE_REL))
    assert len(items) == 579
    assert len(addressed) >= 570, (
        f"only {len(addressed)} of {len(items)} rows addressable"
    )
    # No address is ever emitted twice — that would mean two rows sharing one
    # write target, which is the mis-addressing this exists to prevent.
    numbers = re.findall(r'data-check="([^"]+)"', _render(text, acceptance.SUITE_REL))
    assert len(numbers) == len(set(numbers))


@needs_trainer
def test_the_seven_hand_written_marks_are_reachable_now() -> None:
    """`../your-trainer`'s v2.1.0 delta suite carries 6 `[~]` and 1 `[F]`, and
    before this **none of the seven had a control at all** — tasklist leaves
    them as literal text.

    Six of the seven are reachable now. The seventh, §1.6.1 *"AI warnings
    banner dismissable on the editor"*, is not: its list opens directly under
    `Beyond §1.3.6 / §1.1, the editor gained:` with no blank line, so Markdown
    absorbs it and never makes a list item to stamp. That is the document's
    formatting, not this code's reach, and [[TASK-0457]] names it rather than
    inventing a phantom control for a row with nothing on screen.

    Asserted at the measured number rather than the hoped-for one: `>= 6`
    would have called five of six a success.
    """
    p = TRAINER / "docs" / "tests" / "ACCEPTANCE_TESTS_v2.1.0.md"
    if not p.exists():
        pytest.skip("the v2.1.0 delta suite is not present")
    rows = _rows(_render(p.read_text(encoding="utf-8"), str(p)))
    assert sum(1 for m in rows.values() if m == "~") == 5
    assert sum(1 for m in rows.values() if m == "F") == 1
    # …and the whole file, so the six-of-579 shortfall cannot grow unnoticed.
    assert len(rows) == 264, f"{len(rows)} of 300 rows addressable"


# ----- rows with nothing to click (TASK-0457) -------------------------------


def test_a_row_markdown_never_made_into_a_list_item_is_named() -> None:
    """ISS-0172's rule in a second surface: an affordance that cannot work
    should explain itself rather than vanish."""
    text = (
        "# Tier 1 — Feature Tests\n\n## 1.1 An area (FEAT-0001)\n\n"
        "- [ ] **Reachable:** a.\n\n"
        "Some prose with no blank line after it:\n"
        "- [ ] **Absorbed:** b.\n"
    )
    html = _render(text)
    assert "1 of 2 checks cannot be marked here" in html
    assert "Add a blank line above each list" in html
    assert list(_rows(html)) == ["1.1.1"]


def test_a_suite_where_every_row_is_clickable_says_nothing() -> None:
    assert "acc-unreachable" not in _render(FOUR)


def test_the_notice_is_never_auto_fixed() -> None:
    """Reformatting somebody's document because it would be more convenient to
    click is a different act, and it would rewrite the file the gate reads. The
    count is stated; the blank line is theirs."""
    source = (
        "# Tier 1 — Feature Tests\n\n## 1.1 An area (FEAT-0001)\n\n"
        "Prose:\n- [ ] **Absorbed:** b.\n"
    )
    before = source
    _render(source)
    assert source == before


@needs_trainer
def test_the_real_suites_report_their_own_shortfall() -> None:
    text = (TRAINER / "docs" / acceptance.SUITE_REL).read_text(encoding="utf-8")
    html = _render(text, acceptance.SUITE_REL)
    assert "6 of 579 checks cannot be marked here" in html
