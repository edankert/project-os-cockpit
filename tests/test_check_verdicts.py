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
from project_os_cockpit.index import Index

TRAINER = Path.home() / "Dev" / "repos" / "your-trainer"
#: **Keyed on the SUITE, in either shape** (ADR-0030). This read
#: `(TRAINER / "docs" / acceptance.SUITE_REL).exists()` and reported
#: *"../your-trainer is not present"* — and the moment that repo migrated, the
#: repo was present, its suite was 579 notes, and eleven tests went quiet
#: saying the corpus was missing. Six of them were the release-gate delta,
#: which is exactly what the migration had to be checked against.
#:
#: A skip condition that names one storage shape is a guard that expires when
#: the storage changes, and it expires **silently and with a false reason** —
#: which is worse than failing, because a red test gets read.
needs_trainer = pytest.mark.skipif(
    not acceptance.load(TRAINER / "docs").exists,
    reason="../your-trainer has no acceptance suite in either shape",
)

CHECK = """---
type: "[[check]]"
id: CHK-0001
aliases: ["CHK-0001"]
title: "Walk me"
status: active
owner: user:edwin
created: 2026-08-01
updated: 2026-08-01
tier: 1
area: "An area"
section: "1.1"
ordinal: 10
mark: " "
verdict_date: ""
verdict_reason: ""
invalidated_by: {}
automation: manual
covered_by: []
covers: ["[[FEAT-0001]]"]
burden: []
evidence: []
migrated_from: ""
related: []
---

# Walk me

Open the thing and look.
"""

ISSUE = """---
type: "[[issue]]"
id: {id}
aliases: ["{id}"]
title: "A tracked failure"
status: open
owner: user:edwin
created: 2026-08-01
updated: 2026-08-01
---

# A tracked failure
"""


def _corpus(tmp_path: Path) -> Index:
    """A repo holding one check and two issues its reasons may cite."""
    docs = tmp_path / "docs"
    (docs / acceptance.CHECKS_REL).mkdir(parents=True)
    (docs / acceptance.CHECKS_REL / "CHK-0001-Walk-Me.md").write_text(
        CHECK, encoding="utf-8")
    (docs / "issues").mkdir(parents=True)
    for issue_id in ("ISS-0277", "ISS-0285"):
        (docs / "issues" / f"{issue_id}-A.md").write_text(
            ISSUE.format(id=issue_id), encoding="utf-8")
    return Index.build(docs)


def _check(index: Index) -> acceptance.Item:
    return next(i for i in acceptance.load(index.docs_root).items
                if i.note_id == "CHK-0001")


# ----- what a verdict may be, and what it must carry ------------------------


@pytest.mark.parametrize(("verdict", "mark"), [
    ("pass", "x"), ("partial", "/"), ("excused", "-"),
    ("failed", "!"), ("question", "?"),
])
def test_each_verdict_writes_its_mark_and_reads_back(
    tmp_path: Path, verdict: str, mark: str,
) -> None:
    """The mark round-trips through the note, not through row grammar.

    `verdict_note`/`rewrite_check` wrote `**FAILS 2026-06-07** — …` onto a line
    in a document and were deleted with that document (ISS-0192). What the
    grammar carried is now three fields, which is the whole inversion:
    `mark:` is the verdict, `verdict_date:` and `verdict_reason:` are beside
    it, and no surface has to parse a sentence to know what a check says.
    """
    index = _corpus(tmp_path)
    note_writes.mark_check(index, check_id="CHK-0001", verdict=verdict,
                           reason="saw 69 bpm")
    item = _check(Index.build(index.docs_root))
    assert item.mark == mark
    assert item.verdict_reason == "saw 69 bpm"
    assert item.verdict_date  # dated, always — staleness is arithmetic


def test_a_pass_may_carry_no_witness(tmp_path: Path) -> None:
    index = _corpus(tmp_path)
    note_writes.mark_check(index, check_id="CHK-0001", verdict="pass")
    item = _check(Index.build(index.docs_root))
    assert item.mark == "x" and item.verdict_reason == ""


@pytest.mark.parametrize("reason", [
    "a **bold** run",
    "line one\nline two",
    "a | pipe that would open a table cell",
    "an unmatched ] bracket",
    "a `backtick` span",
    'a "quoted" phrase that would end the scalar',
])
def test_a_reason_cannot_escape_the_field_it_lands_in(
    tmp_path: Path, reason: str,
) -> None:
    """The same property as before, one container along.

    It used to be *a reason must not escape the ROW* — a newline ended the list
    item, an unbalanced `**` swallowed the rest of the line. It is now *a
    reason must not escape the SCALAR*: a newline or a bare quote would end the
    YAML value and the frontmatter after it becomes body text, which is a
    corrupted note rather than a corrupted line.
    """
    index = _corpus(tmp_path)
    note_writes.mark_check(index, check_id="CHK-0001", verdict="partial",
                           reason=reason)
    # It parses at all — a broken scalar makes the whole note unreadable.
    item = _check(Index.build(index.docs_root))
    assert item.mark == "/"
    assert item.verdict_reason, "the reason vanished"
    assert "\n" not in item.verdict_reason


@pytest.mark.parametrize("verdict", ["partial", "excused", "failed", "question"])
def test_a_verdict_that_needs_a_reason_is_refused_without_one(
    tmp_path: Path, verdict: str,
) -> None:
    """The whole difference between these and the `[!]` this repo minted:
    that one shipped its permissive half with no way to ask why (ISS-0177)."""
    index = _corpus(tmp_path)
    with pytest.raises(note_writes.WriteError) as caught:
        note_writes.mark_check(index, check_id="CHK-0001", verdict=verdict)
    assert "reason" in caught.value.message
    assert _check(index).mark == " ", "the note was written despite the refusal"


def test_a_reason_citing_a_note_that_does_not_exist_is_refused(
    tmp_path: Path,
) -> None:
    """A justification pointing at a non-existent issue is worse than none:
    it reads as tracked and is not."""
    index = _corpus(tmp_path)
    with pytest.raises(note_writes.WriteError) as caught:
        note_writes.mark_check(index, check_id="CHK-0001", verdict="failed",
                               reason="tracked as ISS-9999")
    assert "ISS-9999" in caught.value.message
    # …and one that does exist is accepted.
    note_writes.mark_check(index, check_id="CHK-0001", verdict="failed",
                           reason="tracked as ISS-0285")
    assert _check(Index.build(index.docs_root)).mark == "!"


def test_an_unknown_verdict_is_refused(tmp_path: Path) -> None:
    index = _corpus(tmp_path)
    with pytest.raises(note_writes.WriteError):
        note_writes.mark_check(index, check_id="CHK-0001", verdict="probably")


def test_clearing_a_mark_clears_the_reason_it_was_carrying(
    tmp_path: Path,
) -> None:
    """A check cannot claim both that nobody walked it and that somebody
    decided why it could not be walked."""
    index = _corpus(tmp_path)
    note_writes.mark_check(index, check_id="CHK-0001", verdict="excused",
                           reason="no hardware")
    index = Index.build(index.docs_root)
    note_writes.mark_check(index, check_id="CHK-0001", verdict="clear")
    item = _check(Index.build(index.docs_root))
    assert item.mark == " "
    assert item.verdict_reason == "" and item.verdict_date == ""


def test_a_verdict_replaces_the_previous_one_rather_than_stacking_it(
    tmp_path: Path,
) -> None:
    """Fields replace by construction, which is a thing the grammar had to
    work for: `strip_verdict` existed so cycling `~` -> `F` did not leave a
    row carrying two dated verdicts that contradicted each other."""
    index = _corpus(tmp_path)
    note_writes.mark_check(index, check_id="CHK-0001", verdict="partial",
                           reason="de-DE only")
    index = Index.build(index.docs_root)
    note_writes.mark_check(index, check_id="CHK-0001", verdict="failed",
                           reason="crashes on launch")
    item = _check(Index.build(index.docs_root))
    assert item.mark == "!" and item.verdict_reason == "crashes on launch"
    assert "de-DE" not in (index.docs_root / item.rel).read_text(encoding="utf-8")


def test_a_verdict_on_something_that_is_not_a_check_is_refused(
    tmp_path: Path,
) -> None:
    """The address used to be a position in one known file, so it could not
    name the wrong KIND of thing. An id can, so the type is checked."""
    index = _corpus(tmp_path)
    with pytest.raises(note_writes.WriteError) as caught:
        note_writes.mark_check(index, check_id="ISS-0285", verdict="pass")
    assert "not an acceptance check" in caught.value.message


def test_a_verdict_without_an_id_is_refused(tmp_path: Path) -> None:
    """The document address (`1.25.3`) is gone and says so (ISS-0192).

    A caller still sending `number`+`name` gets a refusal that names the
    replacement, rather than a silent no-op or a write to nothing.
    """
    index = _corpus(tmp_path)
    with pytest.raises(note_writes.WriteError) as caught:
        note_writes.mark_check(index, check_id="", verdict="pass")
    assert "CHK-" in caught.value.message


def test_a_note_edited_underneath_the_walk_is_refused(tmp_path: Path) -> None:
    """The caller is acting on what it last read."""
    index = _corpus(tmp_path)
    with pytest.raises(note_writes.WriteError) as caught:
        note_writes.mark_check(index, check_id="CHK-0001", verdict="pass",
                               mtime=1.0)
    assert "changed on disk" in caught.value.message


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


# ----- what went with the document surface (ISS-0192) -----------------------
#
# Deleted here, deliberately and with the list written down, because a guard
# for a mechanism that no longer exists reads as coverage:
#
#   test_the_cycle_replaces_a_verdict_rather_than_stacking_it
#   test_every_verdict_form_in_the_corpus_can_be_stripped
#   test_a_row_with_no_verdict_is_left_exactly_alone
#   test_a_decided_row_is_protected_from_the_walker
#   test_the_write_returns_the_row_it_just_rendered
#   test_a_row_that_cannot_be_re_found_yields_an_empty_string_not_a_crash
#
# Every one guarded `verdict_note` / `strip_verdict` / `rewrite_check` /
# `_rendered_row` — the row-grammar writers, which existed because a check was
# a line in a document addressed by its position. **Four of the six properties
# they held survive above, re-pointed at the note**: a verdict replaces rather
# than stacks (fields do that by construction), clearing takes the reason with
# it, a decided check is not silently overwritten by the wrong caller, and a
# write that cannot find its subject refuses rather than crashing.
#
# The two that did NOT survive are named rather than quietly dropped:
#
# 1. **Linkification.** `_escape_reason` turned `ISS-0285` in a reason into
#    `[[ISS-0285]]` so the rendered row linked it. A `verdict_reason:` field is
#    text, not markdown, so it does not link. The id is still *validated* —
#    a reason citing a note that does not exist is refused above — so nothing
#    about traceability was lost, only the anchor.
# 2. **`_rendered_row`.** The client patched one `<li>` from server-rendered
#    HTML so a mark did not cost a re-navigation. `~checks` repaints itself and
#    holds the reader's position twice (test_checks_view.py), so there is no
#    row to patch and no HTML to send.
