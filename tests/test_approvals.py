"""Permission prompts as durable state, not a colour (ISS-0094).

The hole this closes, in one sentence: **[[FEAT-0076]]'s alarm watches the
review queue, and a tool-permission prompt is not a queue entry** — so the most
likely way an unattended worker stops, an agent asking *"may I run this
command?"*, was precisely the way the alarm could not see it. Not idle, not
failed, not budget-exhausted: blocked, and the supervision blind.

Three properties carry the fix, and each is a way it could be worse than the
amber card it replaces.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from project_os_cockpit import escalation
from project_os_cockpit.approvals import ApprovalStore

NOW = dt.datetime(2026, 8, 11, 12, 0, tzinfo=dt.timezone.utc)


def test_a_prompt_survives_a_restart(tmp_path: Path) -> None:
    """"Detection" that evaporates on restart leaves the worker blocked and
    the record with no memory of why."""
    store = ApprovalStore(tmp_path)
    store.record(session_id="s1", tool="Bash", prompt="rm -rf build/", agent="claude")
    assert len(ApprovalStore(tmp_path).open_prompts()) == 1


def test_a_retried_prompt_does_not_become_two_obligations(tmp_path: Path) -> None:
    """Repeated hook deliveries are normal — the review store learned this when
    16 concurrent offers produced 9 indistinguishable rows."""
    store = ApprovalStore(tmp_path)
    a = store.record(session_id="s1", tool="Bash", prompt="ls", agent="claude")
    b = store.record(session_id="s1", tool="Bash", prompt="ls", agent="claude")
    assert a["approval_id"] == b["approval_id"]
    assert len(store.open_prompts()) == 1


def test_an_agent_may_not_answer_its_own_prompt(tmp_path: Path) -> None:
    """The whole point of a permission prompt is that a **different party**
    decides. An agent answering its own is the loop granting itself the
    authority the prompt exists to withhold."""
    store = ApprovalStore(tmp_path)
    entry = store.record(session_id="s1", tool="Bash", prompt="rm -rf /", agent="claude")
    for who in ("agent:worker", "agent:claude", "agent:anything"):
        with pytest.raises(ValueError) as exc:
            store.answer(entry["approval_id"], decision="granted", actor=who)
        assert "different party" in str(exc.value)
    assert store.open_prompts(), "a refused answer still closed the prompt"


def test_an_unattributed_answer_is_refused(tmp_path: Path) -> None:
    store = ApprovalStore(tmp_path)
    entry = store.record(session_id="s1", tool="Bash", prompt="x")
    with pytest.raises(ValueError):
        store.answer(entry["approval_id"], decision="granted", actor="")


def test_answering_twice_does_not_change_the_first_decision(tmp_path: Path) -> None:
    """A decision is a record of what somebody chose, not a mutable field."""
    store = ApprovalStore(tmp_path)
    entry = store.record(session_id="s1", tool="Bash", prompt="x")
    store.answer(entry["approval_id"], decision="denied", actor="user:edwin")
    again = store.answer(entry["approval_id"], decision="granted", actor="user:edwin")
    assert again["status"] == "denied", again


def test_only_granted_or_denied_are_decisions(tmp_path: Path) -> None:
    store = ApprovalStore(tmp_path)
    entry = store.record(session_id="s1", tool="Bash", prompt="x")
    with pytest.raises(ValueError):
        store.answer(entry["approval_id"], decision="maybe", actor="user:edwin")


# ---- the hole, closed -----------------------------------------------------


def test_a_stalled_prompt_alarms_rather_than_being_invisible() -> None:
    """The whole reason this issue existed.

    Without a `permission` policy line the sweep would have alarmed anyway (an
    unknown kind alarms) — but only *after* the kind reached it at all, which
    it never did, because prompts were not entries.
    """
    fresh = escalation.assess(
        {"kind": "permission", "ts": (NOW - dt.timedelta(minutes=30)).isoformat()}, now=NOW,
    )
    stalled = escalation.assess(
        {"kind": "permission", "ts": (NOW - dt.timedelta(hours=3)).isoformat()}, now=NOW,
    )
    assert fresh["state"] == "waiting"
    assert stalled["state"] == "alarm", stalled


def test_a_permission_prompt_never_lapses_into_an_assumption() -> None:
    """**No default, deliberately.** A permission request asks to take an
    action with effects outside the record: lapsing into "yes" grants authority
    nobody delegated, and lapsing into "no" silently changes what the agent did.
    """
    assert escalation.DEFAULT_POLICY["permission"]["default"] is None
    late = escalation.assess(
        {"kind": "permission", "ts": (NOW - dt.timedelta(hours=1.5)).isoformat()}, now=NOW,
    )
    assert late["state"] == "late"
    assert "assumption" not in late


def test_prompts_are_swept_with_everything_else(tmp_path: Path) -> None:
    """One clock. A second sweep for prompts would drift from the first."""
    store = ApprovalStore(tmp_path)
    store.record(session_id="s1", tool="Bash", prompt="x")
    swept = escalation.sweep(store.open_prompts(), now=NOW)
    assert len(swept["entries"]) == 1
    assert swept["entries"][0]["escalation"]["kind"] == "permission"
