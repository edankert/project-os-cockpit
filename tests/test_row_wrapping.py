"""A hard-wrapped row keeps every word (ISS-0216).

`_ITEM_RE` matches one PHYSICAL line, and for the whole life of the parser
every line it did not match was discarded with no warning, no count and no
entry in the migration's `problems` list. A bullet wrapped across four lines
parsed as its first line.

**The damage is in the corpus and it is not hypothetical.**
`../your-trainer/docs/tests/acceptance/TST-0596-Chrome-Reachable-From-Every-Pre-Ride.md`
is titled *"Chrome reachable from every pre-ride screen"* and its entire body
is the word `From` — the last word of the first physical line. Five siblings
are truncated the same way. The full text survived only because the migration
also copied the source document's prose verbatim into the directory README,
which is luck rather than design: the README is prose for humans, and no tool
can reunite it with the note.

The fixture below is that row, byte for byte from
`../your-trainer/docs/tests/acceptance/README.md`, which is the only surviving
copy — the pre-migration file was uncommitted at the cut, so git does not have
it either.

**Every guard here is about a line the parser must NOT swallow**, as much as
about the one it must. Widening one axis of a silent-drop bug and leaving the
other is how ISS-0141 came back twice, and the pre-migration corpus puts real
non-continuation lines in exactly the position a naive fix would eat.
"""

from __future__ import annotations

import pytest

from project_os_cockpit import acceptance


#: Verbatim from `your-trainer`'s checks README — the surviving copy of the
#: rows that produced `TST-0592`..`TST-0597`. Six-space continuations, aligning
#: under the `**`, which is what the suite's own hard wrap looks like.
WRAPPED = """# Tier 3 — Verification Tests (temporary)

## 3.5 Moved from Tier 1 / Tier 2 — Fully Automated

- [ ] **Chrome reachable from every pre-ride screen (ISS-0361 / ISS-0362).** From
      Workouts and from History: the Riders/Workouts/History switcher is in the
      title slot and peer-swaps without growing the stack; the rider chip and gear
      both open Settings; both badges turn green when the respective device
      connects and grey on a drop.
- [x] **A one-liner.** Nothing wrapped here.
"""


def test_a_wrapped_row_keeps_every_word() -> None:
    """The exact note whose body is currently the word `From`."""
    rows = acceptance.parse(WRAPPED)
    assert len(rows) == 2, "wrapping must not split one row into several"

    first = rows[0]
    assert first.name == (
        "Chrome reachable from every pre-ride screen (ISS-0361 / ISS-0362)."
    )
    # The bug, stated as the assertion that would have caught it.
    assert first.text != "From"
    for tail in ("peer-swaps without growing the stack",
                 "both open Settings",
                 "grey on a drop."):
        assert tail in first.text, f"lost the continuation carrying {tail!r}"
    # Joined as prose, not as lines: the row is one sentence in every surface
    # that renders it, and a newline inside a YAML scalar or a table cell is a
    # different bug in a different place.
    assert "\n" not in first.text


def test_an_unwrapped_row_is_untouched() -> None:
    """The 665 rows that do not wrap must parse exactly as before."""
    rows = acceptance.parse(WRAPPED)
    assert rows[1].name == "A one-liner."
    assert rows[1].text == "Nothing wrapped here."
    assert rows[1].checked is True


def test_a_following_bullet_is_not_swallowed() -> None:
    """`- *… moved to §3.5*` is a separate annotation, not the row's text.

    Measured in the pre-migration file: **23 of these sit directly under a
    checkbox.** A fix that accepted Markdown's *lazy* (unindented) continuation
    would have folded all 23 into the check above them, inventing a procedure
    step out of a cross-reference. That is why the continuation must be
    indented — the rule is measured against the corpus, not assumed.
    """
    suite = """# Tier 3 — Verification

## 3.5 Moved

- [ ] **A check.** Its own text.
- *Favorites Independence moved to §3.5 Sprint 2 — covered by `FavouritesTest`*
- [x] **Another check.** Also its own.
"""
    rows = acceptance.parse(suite)
    assert len(rows) == 2
    assert rows[0].text == "Its own text."
    assert "Favorites" not in rows[0].text
    assert rows[1].name == "Another check."


def test_a_nested_checkbox_is_its_own_row() -> None:
    """An indented `- [ ]` is a check, and `_ITEM_RE` claims it first."""
    suite = """# Tier 1 — Feature Tests

## 1.1 A surface

- [ ] **Parent.** Parent text.
  - [ ] **Nested.** Nested text.
"""
    rows = acceptance.parse(suite)
    assert len(rows) == 2
    assert rows[0].text == "Parent text."
    assert rows[1].name == "Nested."


def test_a_blank_line_closes_the_row() -> None:
    """Prose after a blank line belongs to the section, not to the last row."""
    suite = """# Tier 1 — Feature Tests

## 1.1 A surface

- [ ] **A check.** Its text.

      An indented paragraph after a blank line. Not part of the check.
"""
    rows = acceptance.parse(suite)
    assert len(rows) == 1
    assert rows[0].text == "Its text."


def test_a_heading_closes_the_row() -> None:
    suite = """# Tier 1 — Feature Tests

## 1.1 First

- [ ] **A check.** Its text.
## 1.2 Second

- [ ] **Another.** Other text.
"""
    rows = acceptance.parse(suite)
    assert len(rows) == 2
    assert rows[0].text == "Its text."
    assert rows[0].section == "1.1"
    assert rows[1].section == "1.2"


def test_a_fence_closes_the_row() -> None:
    """A code block under a row is not the row's prose."""
    suite = """# Tier 1 — Feature Tests

## 1.1 A surface

- [ ] **A check.** Its text.
```
  not a continuation
```
"""
    rows = acceptance.parse(suite)
    assert len(rows) == 1
    assert rows[0].text == "Its text."
    assert "not a continuation" not in rows[0].text


def test_a_wrapped_bold_name_still_yields_a_name() -> None:
    """Why the join happens BEFORE `_NAME_RE`, not after.

    A fix that appended continuations to the already-parsed `detail` would
    leave this row nameless, because `**…**` never closes on the first physical
    line. Joining first costs nothing and removes the whole class.
    """
    suite = """# Tier 1 — Feature Tests

## 1.1 A surface

- [ ] **A name that wraps across
      two physical lines.** And then the detail.
"""
    rows = acceptance.parse(suite)
    assert len(rows) == 1
    assert rows[0].name == "A name that wraps across two physical lines."
    assert rows[0].text == "And then the detail."


def test_a_rerun_annotation_on_a_continuation_is_found() -> None:
    """`RE-RUN (…)` is searched in the row's text, which is now the whole row.

    Before the fix an annotation on a continuation line was invisible, so a
    check whose evidence had been overtaken read as a clean pass.
    """
    suite = """# Tier 1 — Feature Tests

## 1.1 A surface

- [x] **A check.** Walked on the 3rd.
      RE-RUN (TASK-0776: the dialog moved)
"""
    rows = acceptance.parse(suite)
    assert len(rows) == 1
    assert rows[0].invalidated.change == "TASK-0776"
    assert rows[0].invalidated.reason == "the dialog moved"


def test_a_lazy_wrap_is_reported_rather_than_dropped() -> None:
    """The one ambiguous shape, surfaced instead of guessed at.

    Markdown would read an unindented line under a bullet as that bullet's
    text. This parser will not, because the corpus puts real separate content
    there — so the line is *named in a report* rather than silently discarded
    or silently absorbed. The migration surfaces the count; a person decides.
    """
    suite = """# Tier 1 — Feature Tests

## 1.1 A surface

- [ ] **A check.** Its text.
this line is unindented and is not a bullet
"""
    report: list[str] = []
    rows = acceptance.parse(suite, report=report)
    assert rows[0].text == "Its text."
    assert len(report) == 1
    assert "unindented" in report[0]
    assert "this line is unindented" in report[0]


def test_ordinary_prose_between_rows_is_not_reported() -> None:
    """A report nobody can act on is one people learn to skip.

    Section prose is not a lost continuation — it is a document doing what
    documents do — so it must not appear in a report whose whole purpose is to
    say *look at this line*.
    """
    suite = """# Tier 1 — Feature Tests

## 1.1 A surface

Some ordinary prose introducing the section.

- [ ] **A check.** Its text.

More ordinary prose after it.
"""
    report: list[str] = []
    acceptance.parse(suite, report=report)
    assert report == []


# ================= what independent review found, 2026-08-19 =================


def test_a_fence_closes_the_row_before_its_contents(  # finding 3
) -> None:
    """`test_a_fence_closes_the_row` passed with the fence's `close_row()`
    deleted, because the row was closed later by a different mechanism.

    A test that passes when the thing it names is removed is not guarding it.
    This is the distinguishing input: an **indented** line after the closing
    fence, which reaches the continuation branch and would be appended to a
    row that should have ended three lines earlier.
    """
    suite = """# Tier 1 — Feature Tests

## 1.1 A surface

- [ ] **A check.** Its text.
```
  fenced
```
      an indented line after the fence
"""
    rows = acceptance.parse(suite)
    assert len(rows) == 1
    assert rows[0].text == "Its text.", (
        "the fence ends the row; nothing after it belongs to the row")


def test_a_tier_heading_closes_the_row_before_its_contents() -> None:  # finding 3
    suite = """# Tier 1 — Feature Tests

## 1.1 A surface

- [ ] **A check.** Its text.
# Tier 2 — Regression Tests
      an indented line under the new tier
"""
    rows = acceptance.parse(suite)
    assert len(rows) == 1
    assert rows[0].text == "Its text."
    assert rows[0].tier == 1


def test_a_section_heading_closes_the_row_before_its_contents() -> None:  # 3
    suite = """# Tier 1 — Feature Tests

## 1.1 First

- [ ] **A check.** Its text.
## 1.2 Second
      an indented line under the new section
"""
    rows = acceptance.parse(suite)
    assert len(rows) == 1
    assert rows[0].text == "Its text."
    assert rows[0].section == "1.1"


@pytest.mark.parametrize("line,label", [
    ("  1. Open the app.", "an ordered-list step"),
    ("  | col | col |", "a table row"),
    ("  ## A heading", "a heading"),
    ("  > A quote", "a block quote"),
])
def test_indented_structure_is_not_folded_into_the_row(  # finding 4
    line: str, label: str,
) -> None:
    """The exclusion is five shapes, not one.

    The first version excluded `-*+` alone, and every one of these folded into
    the row's detail — *"| col | col |"* read as part of a sentence. The
    docstring's own argument against nested bullets applies verbatim: folding
    structure into prose invents a sentence nobody wrote.

    Unreachable in any committed suite, and reachable the moment
    [[TASK-0531]]'s migration runs, which is the parser it runs through.
    """
    suite = f"""# Tier 1 — Feature Tests

## 1.1 A surface

- [ ] **A check.** Its text.
{line}
"""
    rows = acceptance.parse(suite)
    assert rows[0].text == "Its text.", f"{label} was folded into the row"
