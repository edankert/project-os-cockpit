"""Every test the machine considers automated must say how to run it (ISS-0130).

The release-verification gate exists to catch **stale evidence**: a test that
passed in May against code that changed in August. Its step 7 re-runs a note's
entrypoint and moves the verdict from STALE back to CURRENT. A note with no
entrypoint can never make that trip, so its `status: passing` is a claim the
machine cannot refresh and nobody can check without first reverse-engineering
which module verifies it.

Measured on 2026-08-13, before this guard existed: **1 of 24** test notes carried
a `command:`. Eleven declared `kind: automated` and no way to run; ten more
declared their module in `path:` or in prose, which `run-tests.py` does not read.
Every one of them passed. That is the point — nothing here was broken, and the
record could not demonstrate it.

The guard is deliberately keyed to `cockpit._is_manual_test`, the same predicate
the Tests view uses to decide who runs a test, rather than to a second reading of
`kind:`. A note that the product calls automated and the runner cannot execute is
exactly the disagreement worth failing on; asking a fresh question here would let
the two drift apart in the usual way.
"""

from __future__ import annotations

import shlex
from pathlib import Path

import pytest

from project_os_cockpit.cockpit import _is_manual_test
from project_os_cockpit.index import Index

REPO_ROOT = Path(__file__).resolve().parent.parent


#: A test whose subject no longer exists is not going to be re-run, and the
#: entrypoint rule is about re-runnability. `superseded` is terminal-without-
#: the-thing-having-been-done, and FEAT-0107 produced the first two: the
#: acceptance stepper they guarded was deleted, and the notes are kept as the
#: record of what it proved rather than removed (this project does not delete
#: completed notes).
#:
#: Narrow deliberately — only `superseded`. A `passing` test with no
#: entrypoint is exactly the ISS-0130 defect this file exists to catch, and
#: widening this set is how that guard would be satisfied by relabelling.
_NOT_RERUNNABLE = frozenset({"superseded"})


def _test_notes():
    index = Index.build(REPO_ROOT / "docs")
    notes = [
        record
        for path in index.paths()
        if (record := index.get(path)) is not None and record.note_type == "test"
        and str(record.status or "").strip().lower() not in _NOT_RERUNNABLE
    ]
    assert notes, "the corpus has no test notes; the walk is wrong, not the corpus"
    return sorted(notes, key=lambda r: str(r.frontmatter.get("id") or ""))


def _note_id(record) -> str:
    return str(record.frontmatter.get("id") or "")


def _command(record) -> str:
    return str(record.frontmatter.get("command") or "").strip()


def test_no_test_can_be_automated_without_a_way_to_run_it():
    """The state this guard was written for is now unreachable (ADR-0034).

    It caught *"the corpus treats this as automated and it declares no way to
    run"* — a real hole while `kind: automated` could say so with no `command:`.
    `_is_manual_test` is now `not command`, so a note without one is a person's
    job by construction and the hole closes rather than being policed.

    Kept, inverted, because the property still matters and the guard going green
    forever is the wrong way for it to end: this asserts the classifier cannot
    produce the state, so re-adding any second declaration fails here.

    Measured when it flipped: `your-sudoku`'s TST-0013 was in exactly the old
    hole — `kind: automated`, no `command:` — and is now correctly owed to a
    person until somebody gives it one.
    """
    for record in _test_notes():
        if _command(record):
            continue
        assert _is_manual_test(record), (
            "%s has no command: and is not classified as human-walked; some "
            "field other than `command:` is deciding who runs a test again"
            % _note_id(record)
        )

def test_every_declared_entrypoint_names_files_that_exist():
    """A command: that resolves to nothing is worse than none — it looks runnable."""
    broken = []
    for record in _test_notes():
        command = _command(record)
        if not command:
            continue
        for token in shlex.split(command):
            if token.endswith(".py") and "/" in token:
                if not (REPO_ROOT / token).is_file():
                    broken.append("%s -> %s" % (_note_id(record), token))
    assert not broken, "entrypoints naming files that do not exist: %s" % ", ".join(broken)


def test_nothing_declares_who_runs_a_test_except_the_command():
    """`command:` is the only answer to who runs a test (ADR-0034 decision 4).

    This asserted that an exempt note must *say* it is manual — a real guard
    while `kind:` existed, because before 2026-08-13 a note declaring nothing
    was read as automated and still had no entrypoint. **ADR-0034 deletes
    `kind:` instead of constraining it**, so the ambiguity is gone with the
    field that created it: absence of a `command:` IS the declaration, and
    there is no longer such a thing as being exempt by accident.

    What still needs guarding is that a second declaration does not come back.
    Two fields answering one question is how the reader and the registry came
    to disagree about 8 of 788 tests, and re-adding one would be silent.
    """
    # `automation:` is NOT banned as a field — it answers "does a machine cover
    # this check", which is a real and different question. What is banned is any
    # field OTHER than `command:` being read as who-runs-this, which is asserted
    # separately below.
    banned = ("kind", "mode", "method")
    offenders = [
        "%s carries %s:" % (_note_id(record), key)
        for record in _test_notes()
        for key in banned
        if str(record.frontmatter.get(key) or "").strip()
    ]
    assert not offenders, (
        "a second who-runs-this field is back, and it will drift from `command:` "
        "the way `kind:` did: %s" % ", ".join(offenders)
    )


@pytest.mark.parametrize("note_id", ["TST-0011", "TST-0024"])
def test_the_known_manual_tests_stay_exempt(note_id):
    """Both are procedures a person walks, and neither should sprout a command:.

    TST-0011 is the manual UI checklist; TST-0024 is PHASE-033's remote-SSH walk,
    which cannot be automated because the thing it walks is not built. Naming them
    means a future sweep that hands them a fake entrypoint fails here.
    """
    record = next((r for r in _test_notes() if _note_id(r) == note_id), None)
    assert record is not None, "%s has gone missing" % note_id
    assert _is_manual_test(record), "%s stopped reading as manual" % note_id
    assert not _command(record), "%s gained an entrypoint it cannot honour" % note_id


def test_an_executable_test_reports_its_run_not_an_older_typed_date():
    """The ISS-0130 sweep's second-order effect, caught before it could bite.

    Making 22 notes executable left every one of them carrying a `last_verified`
    from weeks earlier. The freshness rule read that field first, so a test that
    had run green minutes ago displayed a date up to 39 days old and was on its
    way to reading STALE while passing daily.
    """
    from project_os_cockpit.cockpit import _test_last_verified

    lagging = []
    for record in _test_notes():
        fm = record.frontmatter
        if not _command(record):
            continue
        run = str(fm.get("last_run") or "").strip()
        if not run:
            continue
        shown = _test_last_verified(fm)
        if shown[:10] != run[:10]:
            lagging.append("%s shows %s, ran %s" % (_note_id(record), shown[:10], run[:10]))
    assert not lagging, (
        "executable tests reporting a date other than their run: %s" % "; ".join(lagging)
    )


def test_a_manual_test_still_reports_its_typed_date():
    """The other half of the same rule — nothing runs a manual test, so the date is it."""
    from project_os_cockpit.cockpit import _test_last_verified

    fm = {"last_verified": "2026-07-27", "last_run": "2026-08-13T18:28Z"}
    assert _test_last_verified(fm) == "2026-07-27"
    fm_exec = dict(fm, command=".venv/bin/pytest tests/test_index.py -q")
    assert _test_last_verified(fm_exec).startswith("2026-08-13")


def test_only_the_command_answers_who_runs_a_test():
    """`_is_manual_test` must read `command:` and nothing that means something else.

    Deleting `kind:` while `_is_manual_test` still read `automation:` would have
    MOVED the ambiguity rather than removed it: `automation:` is set on 671 of
    788 fleet notes and reads `manual` on 466, so it was silently the second
    who-runs-this field the moment the first one went. Found by independent
    review.

    `automation:` answers *does a machine cover this check* — `full`/`partial`/
    `manual`, beside `covered_by:` — which is a claim about coverage, not about
    who performs the walk.
    """
    import inspect

    source = inspect.getsource(_is_manual_test)
    body = source[source.index('"""', source.index('"""') + 3):]
    assert '"automation"' not in body, (
        "_is_manual_test reads `automation:` again; it is a coverage claim, not "
        "a declaration of who runs the test, and it is set on most of the fleet"
    )
    assert '"kind"' not in body, "`kind:` is deleted (ADR-0034 decision 4)"
    assert '"command"' in body, "the one field that does answer this must be read"
