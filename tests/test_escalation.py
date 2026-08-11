"""Nothing waits silently without bound (FEAT-0076).

The sharpest failure mode of a system *designed* to escalate is that one
unanswered question stalls the loop forever. The invariant is one sentence —
**everything either times out into a recorded assumption, or alarms** — and
TASK-0331 asks for it to be proven by **drill**: construct each silent-wait
candidate and show it lands somewhere visible.

So the central test here is not a case, it is an enumeration: every shape an
entry can take, asserted to reach a non-silent state.
"""

from __future__ import annotations

import datetime as dt

import pytest

from project_os_cockpit import escalation

NOW = dt.datetime(2026, 8, 11, 12, 0, tzinfo=dt.timezone.utc)


def _entry(kind: str, hours_ago: float | None) -> dict:
    ts = "" if hours_ago is None else (NOW - dt.timedelta(hours=hours_ago)).isoformat()
    return {"kind": kind, "ts": ts, "request_id": f"{kind}-{hours_ago}"}


# ---- the drill ------------------------------------------------------------


@pytest.mark.parametrize("entry", [
    _entry("question", 999),        # long past its timeout, has a default
    _entry("review", 999),          # ditto, different kind
    _entry("annotation", 999),      # no timeout at all
    _entry("mystery-kind", 999),    # no policy line
    _entry("question", None),       # no timestamp — cannot be aged
    _entry("question", 0),          # brand new
])
def test_the_drill_no_entry_waits_silently(entry: dict) -> None:
    """Every silent-wait candidate, shown to land somewhere visible.

    `waiting` counts as visible: the entry sits in the queue with its age, and
    the human sees the clock the system is on. What must never happen is a
    state that is neither actionable nor observable.
    """
    state = escalation.assess(entry, now=NOW)["state"]
    assert state in {"waiting", "late", "lapsed", "alarm"}, state


def test_a_kind_with_no_policy_alarms_rather_than_passing() -> None:
    """The judgment that makes the invariant real.

    A kind nobody wrote a timeout for is a kind nobody decided about, and the
    safe reading of an undecided kind is *ask a person* — never *proceed
    quietly*. Defaulting to silence here would hollow out the whole feature.
    """
    got = escalation.assess(_entry("delegated-acceptance", 1), now=NOW)
    assert got["state"] == "alarm"
    assert "undecided kind" in got["why"]


def test_an_entry_with_no_timestamp_alarms() -> None:
    """An un-ageable entry that stayed quiet is exactly the silent wait."""
    assert escalation.assess(_entry("question", None), now=NOW)["state"] == "alarm"


def test_a_lapse_records_the_assumption_it_proceeded_on() -> None:
    """TASK-0330: work done under an assumption carries it, so the digest can
    lift it back to a human."""
    got = escalation.assess(_entry("question", 48), now=NOW)
    assert got["state"] == "lapsed"
    assert got["assumption"], "a lapse with no recorded assumption is a silent decision"


def test_within_its_timeout_it_simply_waits() -> None:
    got = escalation.assess(_entry("question", 1), now=NOW)
    assert got["state"] == "waiting" and got["timeout_hours"] == 24


def test_a_reserved_judgment_never_lapses_and_eventually_alarms() -> None:
    """A kind that reserves judgment cannot proceed on an assumption however
    long it waits — the timeout then decides only *when it alarms*."""
    policy = {"grave": {"timeout_hours": 4, "default": None}}
    late = escalation.assess(_entry("grave", 5), now=NOW, policy=policy)
    assert late["state"] == "late", late
    alarming = escalation.assess(_entry("grave", 9), now=NOW, policy=policy)
    assert alarming["state"] == "alarm", alarming


def test_the_sweep_accounts_for_every_entry() -> None:
    """Nothing may be absent from the result — an entry the sweep dropped is
    an entry waiting silently."""
    entries = [
        _entry("question", 999), _entry("review", 1),
        _entry("annotation", 500), _entry("mystery", 3), _entry("question", None),
    ]
    got = escalation.sweep(entries, now=NOW)
    assert len(got["entries"]) == len(entries)
    assert sum(got["counts"].values()) == len(entries)
    assert got["alarming"], "the unknown kind and the timestamp-less entry did not alarm"


def test_the_reserved_set_exists_before_it_is_needed() -> None:
    """Empty today and deliberately present: the moment a delegated acceptance
    kind exists it belongs here, and a set that must be created later is a set
    somebody forgets."""
    assert hasattr(escalation, "RESERVES_JUDGMENT")
    assert isinstance(escalation.RESERVES_JUDGMENT, frozenset)
