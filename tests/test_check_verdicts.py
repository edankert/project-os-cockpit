"""The marks the record already uses (TST-0037 / FEAT-0111).

[[ISS-0181]] items 1 and 2 read as a design problem — no way to mark a check
intentionally left open, no way to attach text. Both already exist in
`../your-trainer`'s own suites, with a stable grammar:

    **FAILS 2026-06-07** — collapse state is stored globally … [[ISS-0285]]
    **Partial pass 2026-06-06**: English prompts come back in English …
    ✅ (Claude, tablet: address rotated 7F:D5:… → 73:DD:…)

This repo minted `[!]` for the same purpose in a form no suite writes, and
shipped its permissive half with no way to ask why ([[ISS-0177]]). Nothing here
needed designing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from project_os_cockpit import acceptance, note_writes

TRAINER = Path.home() / "Dev" / "repos" / "your-trainer"
needs_trainer = pytest.mark.skipif(
    not (TRAINER / "docs" / acceptance.SUITE_REL).exists(),
    reason="../your-trainer is not present",
)

SUITE = (
    "# Tier 1 — Feature Tests\n\n"
    "## 1.1 An area (FEAT-0001)\n\n"
    "- [ ] **Walk me:** open the thing and look.\n"
    "- [ ] **And me:** then close it.\n"
)


class _Idx:
    """Enough index for `mark_check`: id resolution and a docs root."""

    def __init__(self, docs_root: Path, known: set[str]) -> None:
        self.docs_root = docs_root
        self._known = known

    def by_id(self, note_id: str):          # noqa: ANN201
        return note_id if note_id in self._known else None


def _suite_at(tmp_path: Path) -> _Idx:
    docs = tmp_path / "docs"
    (docs / "tests").mkdir(parents=True)
    (docs / acceptance.SUITE_REL).write_text(SUITE, encoding="utf-8")
    return _Idx(docs, {"ISS-0277", "ISS-0285"})


# ----- the grammar ----------------------------------------------------------


def test_each_verdict_writes_the_form_the_record_uses() -> None:
    assert acceptance.verdict_note(
        "pass", date="2026-08-16", reason="saw 69 bpm",
    ) == "✅ (saw 69 bpm)"
    assert acceptance.verdict_note(
        "partial", date="2026-08-16", reason="German locale only",
    ) == "**Partial pass 2026-08-16** — German locale only"
    assert acceptance.verdict_note(
        "fail", date="2026-08-16", reason="crashes on open",
    ) == "**FAILS 2026-08-16** — crashes on open"


def test_a_pass_may_carry_no_witness_and_writes_no_empty_parenthetical() -> None:
    assert acceptance.verdict_note("pass", date="2026-08-16") == "✅"


def test_an_id_in_the_reason_is_linkified_however_it_was_typed() -> None:
    """A reason that already said `[[ISS-0285]]` and one that said `ISS-0285`
    must write the identical line — brackets are stripped first, ids are
    linkified after."""
    bare = acceptance.verdict_note(
        "fail", date="2026-08-16", reason="tracked as ISS-0285")
    linked = acceptance.verdict_note(
        "fail", date="2026-08-16", reason="tracked as [[ISS-0285]]")
    assert bare == linked == "**FAILS 2026-08-16** — tracked as [[ISS-0285]]"


@pytest.mark.parametrize("reason", [
    "a **bold** run",
    "line one\nline two",
    "a | pipe that would open a table cell",
    "an unmatched ] bracket",
    "a `backtick` span",
])
def test_a_reason_cannot_escape_the_row_it_lands_on(reason: str) -> None:
    """A newline would end the list item and orphan the rest; an unbalanced
    `**` would swallow the line into bold; a `|` would open a cell."""
    note = acceptance.verdict_note("fail", date="2026-08-16", reason=reason)
    body = note.split("** — ", 1)[1]
    assert "\n" not in note
    assert "**" not in body and "`" not in body and "|" not in body
    assert "]" not in body.replace("[[ISS-0285]]", "")


# ----- the write ------------------------------------------------------------


def test_a_partial_or_a_fail_is_refused_without_a_reason(
    tmp_path: Path,
) -> None:
    """The whole difference between these marks and `[!]`.

    The mark and its justification are one action, so a check cannot leave the
    gate without saying why — which is the gap [[ISS-0177]] records for `[!]`.
    """
    index = _suite_at(tmp_path)
    for verdict in ("partial", "fail"):
        with pytest.raises(note_writes.WriteError) as caught:
            note_writes.mark_check(
                index, number="1.1.1", name="Walk me", verdict=verdict)
        assert "needs a reason" in caught.value.message
    # …and the file is untouched.
    assert (index.docs_root / acceptance.SUITE_REL).read_text() == SUITE


def test_a_pass_needs_no_reason(tmp_path: Path) -> None:
    index = _suite_at(tmp_path)
    note_writes.mark_check(index, number="1.1.1", name="Walk me",
                           verdict="pass")
    got = (index.docs_root / acceptance.SUITE_REL).read_text()
    assert "- [x] **Walk me:** open the thing and look. ✅" in got


def test_a_reason_citing_a_note_that_does_not_exist_is_refused(
    tmp_path: Path,
) -> None:
    """A justification pointing at a non-existent issue is worse than none: it
    reads as tracked and is not."""
    index = _suite_at(tmp_path)
    with pytest.raises(note_writes.WriteError) as caught:
        note_writes.mark_check(
            index, number="1.1.1", name="Walk me", verdict="fail",
            reason="tracked as ISS-9999")
    assert "ISS-9999" in caught.value.message
    assert (index.docs_root / acceptance.SUITE_REL).read_text() == SUITE


@pytest.mark.parametrize(("verdict", "mark"), [
    ("pass", "x"), ("partial", "~"), ("fail", "F"),
])
def test_a_written_row_parses_back_to_the_mark_and_the_text(
    tmp_path: Path, verdict: str, mark: str,
) -> None:
    index = _suite_at(tmp_path)
    note_writes.mark_check(index, number="1.1.1", name="Walk me",
                           verdict=verdict, reason="because ISS-0277")
    text = (index.docs_root / acceptance.SUITE_REL).read_text()
    item = next(i for i in acceptance.parse(text) if i.name == "Walk me")
    assert {"x": item.checked, "~": item.reconciled,
            "F": item.failed}[mark] is True
    assert "[[ISS-0277]]" in item.text
    # The row below is untouched — the address is the section ordinal, not a
    # global checkbox index.
    other = next(i for i in acceptance.parse(text) if i.name == "And me")
    assert other.checked is False and other.text == "then close it."


def test_an_unknown_verdict_is_refused(tmp_path: Path) -> None:
    index = _suite_at(tmp_path)
    with pytest.raises(note_writes.WriteError) as caught:
        note_writes.mark_check(index, number="1.1.1", name="Walk me",
                               verdict="excepted", reason="x")
    assert "is not a verdict" in caught.value.message


def test_the_exception_mark_is_never_offered() -> None:
    """`[!]` stays READABLE so a suite already using it keeps working, and is
    never written — offering it would re-open [[ISS-0177]]'s gap, where a check
    leaves the gate with no justification and nothing owed."""
    assert "!" not in acceptance.VERDICTS.values()
    assert set(acceptance.VERDICTS) == {"pass", "partial", "fail"}
    # Still parsed, though.
    item = acceptance.parse(
        "# Tier 1 — T\n\n## 1.1 A (FEAT-0001)\n\n- [!] **X:** y.\n")[0]
    assert item.excepted is True


def test_a_suite_that_moved_underneath_the_walk_is_refused(
    tmp_path: Path,
) -> None:
    index = _suite_at(tmp_path)
    with pytest.raises(note_writes.WriteError) as caught:
        note_writes.mark_check(index, number="1.1.1", name="Some other check",
                               verdict="pass")
    assert "moved underneath" in caught.value.message


# ----- the existing corpus is unchanged -------------------------------------


@needs_trainer
def test_your_trainers_seven_marked_rows_still_parse_the_same() -> None:
    """Adopting `[F]` must not change what any existing row means."""
    delta = TRAINER / "docs" / "tests" / "ACCEPTANCE_TESTS_v2.1.0.md"
    if not delta.exists():
        pytest.skip("the v2.1.0 delta suite is not present")
    items = acceptance.parse(delta.read_text(encoding="utf-8"))
    assert sum(1 for i in items if i.reconciled) == 6
    assert sum(1 for i in items if i.failed) == 1
    # `[F]` does not settle. A check that failed is not a check that passed.
    assert all(not i.settled for i in items if i.failed)


@needs_trainer
def test_the_living_suite_is_unchanged_by_the_new_marks() -> None:
    suite = acceptance.load(TRAINER / "docs")
    assert len(suite.items) == 579
    assert len(suite.blocking()) == 60


# ----- ticking a post-release box (FEAT-0110 / TASK-0453) -------------------

NOTE = """---
type: "[[release]]"
id: REL-0001
title: "v1.0.0"
status: released
---

# v1.0.0

### Post-Release Actions

- [ ] Tag repo: `git tag v1.0.0`
- [ ] Watch the dashboards
"""


class _RelIdx:
    def __init__(self, docs_root: Path) -> None:
        self.docs_root = docs_root

    def by_id(self, note_id: str):          # noqa: ANN201
        path = self.docs_root / "releases" / "REL-0001-v1.0.0.md"
        return path if note_id == "REL-0001" and path.exists() else None

    def get(self, path):                    # noqa: ANN001, ANN201
        return None


def _release_at(tmp_path: Path) -> _RelIdx:
    docs = tmp_path / "docs"
    (docs / "releases").mkdir(parents=True)
    (docs / "releases" / "REL-0001-v1.0.0.md").write_text(NOTE, encoding="utf-8")
    return _RelIdx(docs)


def _line_of(index: "_RelIdx", needle: str) -> int:
    """The body-relative line of a box, read the way the payload reads it."""
    from project_os_cockpit import publication
    from project_os_cockpit.note_writes import _split_frontmatter

    raw = (index.docs_root / "releases" / "REL-0001-v1.0.0.md").read_text()
    _, body = _split_frontmatter(raw)
    box = next(b for b in publication.post_release_actions(body)
               if needle in b["text"])
    return int(box["line"])


def test_a_box_is_ticked_only_where_it_was_addressed(tmp_path: Path) -> None:
    index = _release_at(tmp_path)
    note_writes.tick_post_release_box(
        index, "REL-0001", line=_line_of(index, "Tag repo"),
        text="Tag repo: `git tag v1.0.0`")
    got = (index.docs_root / "releases" / "REL-0001-v1.0.0.md").read_text()
    assert "- [x] Tag repo: `git tag v1.0.0`" in got
    assert "- [ ] Watch the dashboards" in got, "the row below is untouched"


def test_a_note_that_moved_underneath_the_tick_is_refused(
    tmp_path: Path,
) -> None:
    """The caller is acting on what it last read. A wrong tick destroys the
    only record the obligation existed, so a mismatch is refused rather than
    written — the same comparison `rewrite_check` makes on a check's name."""
    index = _release_at(tmp_path)
    with pytest.raises(note_writes.WriteError) as caught:
        note_writes.tick_post_release_box(
            index, "REL-0001", line=_line_of(index, "Tag repo"),
            text="Something else entirely")
    assert "moved underneath" in caught.value.message
    assert "- [ ] Tag repo" in (
        index.docs_root / "releases" / "REL-0001-v1.0.0.md").read_text()


def test_a_line_that_is_not_an_unticked_box_is_refused(tmp_path: Path) -> None:
    index = _release_at(tmp_path)
    for line in (0, 8, 999):
        with pytest.raises(note_writes.WriteError):
            note_writes.tick_post_release_box(
                index, "REL-0001", line=line, text="anything")


def test_nothing_on_the_release_page_ticks_itself() -> None:
    """The one failure this surface is shaped to prevent.

    `() => void (async () => {…})()` is correct but reads like an IIFE that
    fires at bind time; if it ever became one, every provable box would tick
    itself on render. The handler is written long-hand so that a reviewer can
    see the difference, and this pins it.
    """
    src = (
        Path(__file__).resolve().parents[1]
        / "desktop" / "src" / "renderer" / "renderer.ts"
    ).read_text(encoding="utf-8")
    anchor = src.index("/api/notes/tick-owed")
    start = src.rindex("tick.addEventListener", 0, anchor)
    block = src[start:anchor + 40]
    assert "'click', () => {" in block, (
        "the tick handler must take a plain click callback, not an "
        "immediately-invoked expression"
    )
    assert "tick-owed" in block
