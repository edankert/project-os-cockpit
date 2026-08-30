"""A retired check is finished work (ISS-0272).

Reported after every other surface had been cleaned: the acceptance suite, the
release page, the unreleased card, the registry, the obligations list and the
navigator in all seven modes all correctly dropped a retired check, and it went
on showing in the session work strip as something touched and never completed.

The strip resolves "finished" through `cockpit.is_done_status`, a per-type
table, and that table said only `passing` finishes a test. `statuses` — the
band predicate the rest of the app uses — has always said otherwise.

Asserted as **agreement between the two predicates**, not as a fact about
either, because the defect is that a repo has two answers to one question
(REQ-0059). A test naming only the value would pass while the other table
drifted somewhere new.
"""

from __future__ import annotations

from project_os_cockpit import cockpit, statuses


def test_a_retired_test_is_not_outstanding_work() -> None:
    assert cockpit.is_done_status("test", "retired") is True, (
        "a retired check reads as unfinished work — it will sit in the session "
        "work strip forever, which is what ISS-0272 reported"
    )


def test_the_two_finished_predicates_agree_about_a_test() -> None:
    """`statuses.is_completed` is the band; `is_done_status` is per-type.

    They may legitimately differ — a per-type table exists precisely to be
    stricter than a band. What they must not do is disagree about a value the
    band calls *archived*: terminal without the thing having been done, which
    is exactly a retired check.
    """
    for status in ("passing", "retired"):
        assert statuses.is_completed(status) is True, status
        assert cockpit.is_done_status("test", status) is True, (
            f"the band says {status!r} is completed and the per-type table "
            f"does not; one question with two answers"
        )


def test_it_did_not_widen_to_every_type() -> None:
    """Scoped on purpose. The same disagreement exists for other types and for
    `validate-docs.py`'s third opinion (ISS-0269); widening here would hide it."""
    assert cockpit.is_done_status("task", "retired") is False
    assert cockpit.is_done_status("test", "active") is False
