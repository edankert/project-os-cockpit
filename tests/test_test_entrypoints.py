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


def _test_notes():
    index = Index.build(REPO_ROOT / "docs")
    notes = [
        record
        for path in index.paths()
        if (record := index.get(path)) is not None and record.note_type == "test"
    ]
    assert notes, "the corpus has no test notes; the walk is wrong, not the corpus"
    return sorted(notes, key=lambda r: str(r.frontmatter.get("id") or ""))


def _note_id(record) -> str:
    return str(record.frontmatter.get("id") or "")


def _command(record) -> str:
    return str(record.frontmatter.get("command") or "").strip()


def test_every_automated_test_declares_an_entrypoint():
    """The ISS-0130 defect itself: automated by the product's own rule, unrunnable."""
    orphans = [
        _note_id(r) for r in _test_notes()
        if not _is_manual_test(r) and not _command(r)
    ]
    assert not orphans, (
        "these tests are automated by cockpit._is_manual_test but declare no "
        "command:, so release verification cannot re-run them and their status "
        "cannot be refreshed by machine: %s" % ", ".join(orphans)
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


def test_a_manual_test_is_left_manual():
    """The exemption has to stay narrow, or the first guard is satisfied by relabelling.

    A note may only be exempt by *saying* it is manual, never by omission — which
    was the pre-2026-08-13 state, where a note that declared nothing at all was
    read as automated and still had no entrypoint.
    """
    for record in _test_notes():
        if _command(record):
            continue
        declared = " ".join(
            str(record.frontmatter.get(key) or "")
            for key in ("automation", "kind", "mode", "method")
        ).lower()
        assert "manual" in declared, (
            "%s has no command: and does not declare itself manual; it is exempt "
            "from the entrypoint rule by accident rather than by intent"
            % _note_id(record)
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
