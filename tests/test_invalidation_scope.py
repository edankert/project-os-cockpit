"""Only a feature check is re-opened by a change (ADR-0039 decision 2).

A feature check asserts *the system does X* — a standing claim about current
behaviour, which a later change can falsify. A regression check asserts *this
defect was fixed* — a claim about a past event, and **nothing a later change
does can falsify it**. So "never re-checked" is a property of what the check
asserts rather than a policy imposed on it, which is the whole reason ADR-0039
could derive the sections instead of declaring them.

**Zero checks in the fleet carry an invalidation today** — measured 2026-08-20
across `your-trainer` (581), `project-os-cockpit` (34) and `your-sudoku` (56).
So no corpus assertion can distinguish a working implementation from one that
ignores the section entirely, and every case here is constructed. `test_the_
mutant_is_caught` is what proves the rest are load-bearing.

This is the clause carrying the risk, and it is written down so it can be
argued with: nothing re-opens a settled regression check automatically. A bug
that recurs files a new issue, and a bug anybody expected to recur should have
had a `command:`.
"""

from __future__ import annotations

import pytest

from project_os_cockpit import acceptance


def _check(*, covers, verdict="2026-01-01", invalid="2026-06-01", command="", kind=None):
    fm = {
        "id": "TST-0001",
        "title": "a check",
        "level": "acceptance",
        "mark": "done",
        "verdict_date": verdict,
        "covers": covers,
        "command": command,
        "invalidated_by": {"change": "TASK-0001", "reason": "moved", "date": invalid},
    }
    if kind is not None:
        fm["kind"] = kind
    item = acceptance.item_from_note(fm, rel="docs/tests/acceptance/TST-0001-A.md")
    assert item is not None
    return item


def test_a_feature_check_overtaken_by_a_change_is_stale() -> None:
    """The case the mechanism exists for, unchanged."""
    item = _check(covers=["[[FEAT-0001]]"])
    assert acceptance.kind_of(item) == acceptance.KIND_FEATURE
    assert item.stale is True


def test_a_regression_check_is_not_re_opened_by_a_change() -> None:
    """Same note, same dates, same invalidation — only what it covers differs.

    Nothing a change does can falsify *this defect was fixed on that date*.
    """
    item = _check(covers=["[[ISS-0001]]"])
    assert acceptance.kind_of(item) == acceptance.KIND_REGRESSION
    assert item.stale is False


def test_an_automated_check_is_not_re_opened_either() -> None:
    """CI is current by construction; there is nothing for a clock to grade."""
    item = _check(covers=["[[FEAT-0001]]"], command="pytest tests/x.py")
    assert acceptance.kind_of(item) == acceptance.KIND_AUTOMATED
    assert item.stale is False


def test_a_check_that_declares_kind_feature_is_re_opened_despite_its_issue() -> None:
    """`kind: feature` wins over the `ISS-*` in `covers:` ([[ISS-0316]]).

    your-trainer's TST-0642 covers ISS-0387 and asserts that the FIT file the
    app writes today imports into Garmin Connect. A change to those bytes must
    reopen it, and the issue stays in `covers:` as the record of the defect.
    """
    item = _check(covers=["[[ISS-0001]]"], kind="feature")
    assert acceptance.kind_of(item) == acceptance.KIND_FEATURE
    assert item.stale is True


def test_a_declared_regression_kind_is_honoured_without_an_issue() -> None:
    item = _check(covers=["[[FEAT-0001]]"], kind="Regression")
    assert acceptance.kind_of(item) == acceptance.KIND_REGRESSION
    assert item.stale is False


def test_a_command_still_wins_over_a_declared_kind() -> None:
    """The validator refuses the pair (CHECK-KIND); the reader still answers
    the way the precedence says, so a note that slips through reads as automated."""
    item = _check(covers=["[[ISS-0001]]"], kind="feature", command="pytest tests/x.py")
    assert acceptance.kind_of(item) == acceptance.KIND_AUTOMATED


def test_an_unknown_declared_kind_falls_back_to_covers() -> None:
    item = _check(covers=["[[ISS-0001]]"], kind="feture")
    assert acceptance.kind_of(item) == acceptance.KIND_REGRESSION


def test_a_verdict_after_the_change_answers_it() -> None:
    """TASK-0466's arithmetic, still live for feature checks."""
    item = _check(covers=["[[FEAT-0001]]"], verdict="2026-07-01", invalid="2026-06-01")
    assert item.stale is False


def test_an_explicit_rerun_still_re_opens_a_regression_check() -> None:
    """A person saying so is not a change overtaking it.

    `mark: rerun` is read separately from `stale`, and narrowing invalidation
    must not take away the one lever that re-opens a settled check when the
    defect genuinely returns.
    """
    fm = {
        "id": "TST-0002", "title": "b", "level": "acceptance",
        "mark": "rerun", "covers": ["[[ISS-0001]]"],
    }
    item = acceptance.item_from_note(fm, rel="docs/tests/acceptance/TST-0002-B.md")
    assert item is not None
    assert acceptance.kind_of(item) == acceptance.KIND_REGRESSION
    assert item.needs_rerun is True
    assert item.settled is False, "an explicit re-check must still be owed"


def test_the_mutant_is_caught() -> None:
    """Would anything above fail if the section were ignored?

    Asserted directly, because the corpus holds no invalidated check at all
    and every assertion here would survive that mutation if the constructed
    cases were wrong.
    """
    regression = _check(covers=["[[ISS-0001]]"])
    real = acceptance.kind_of
    try:
        acceptance.kind_of = lambda item: acceptance.KIND_FEATURE  # the mutant
        assert regression.stale is True, (
            "the mutant did not change behaviour — these tests prove nothing")
    finally:
        acceptance.kind_of = real
    assert regression.stale is False
