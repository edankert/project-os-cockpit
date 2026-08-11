"""The worker's brakes, drilled before the hill (FEAT-0074 / REQ-0031).

REQ-0031's fourth criterion is the order this was built in:

    *"Every halt path exercised by drill before any repo runs unattended —
    brakes are tested before the hill."*

So the central test is an **enumeration of halt paths**, not a sample. A stop
condition that exists but has never been exercised is a stop condition nobody
knows the shape of, and the first time it runs will be the time it matters.

**Nothing here starts a loop.** `can_start` is a predicate; the module launches
nothing. Its first question is whether an approved delegation policy exists,
which by default it does not.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import pytest

from project_os_cockpit import worker

NOW = dt.datetime(2026, 8, 11, 12, 0, tzinfo=dt.timezone.utc)


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """A repo with an approved policy — so halt tests exercise the halt they
    name rather than tripping on the policy gate first."""
    (tmp_path / "DELEGATION.md").write_text(
        "---\nstatus: approved\n---\n\n- judgment: close tasks → any-delegate\n",
        encoding="utf-8",
    )
    return tmp_path


# ---- the drill: every halt path -------------------------------------------


def test_drill_the_stop_switch_halts(repo: Path) -> None:
    worker.request_stop(repo, reason="enough for today", actor="user:edwin")
    got = worker.assess_halt(repo)
    assert got["halt"] is True and got["reason"] == "stop-switch"


def test_drill_no_delegation_halts(tmp_path: Path) -> None:
    """The default, and the most important halt: no policy, no worker."""
    got = worker.assess_halt(tmp_path)
    assert got["halt"] is True and got["reason"] == "no-delegation"


def test_drill_a_red_validator_halts(repo: Path) -> None:
    """Working on a record that does not validate compounds the breakage."""
    got = worker.assess_halt(repo, validator_failing=True)
    assert got["halt"] is True and got["reason"] == "validator-red"


def test_drill_parked_items_halt(repo: Path) -> None:
    """Failure compounds toward stopping, never toward retrying."""
    assert worker.assess_halt(repo, parked_items=2)["halt"] is False
    got = worker.assess_halt(repo, parked_items=3)
    assert got["halt"] is True and got["reason"] == "parked-items"


def test_drill_the_session_budget_halts(repo: Path) -> None:
    got = worker.assess_halt(repo, sessions_today=worker.MAX_SESSIONS_PER_DAY)
    assert got["halt"] is True and got["reason"] == "session-budget"


def test_drill_the_wall_clock_halts(repo: Path) -> None:
    got = worker.assess_halt(repo, session_minutes=worker.MAX_SESSION_MINUTES + 1)
    assert got["halt"] is True and got["reason"] == "wall-clock"


def test_every_halt_carries_a_reason(repo: Path) -> None:
    """A halt with no reason is the quiet this module exists to prevent — a
    system that stopped and one that merely went silent look identical."""
    cases = [
        {"validator_failing": True},
        {"parked_items": 9},
        {"sessions_today": 99},
        {"session_minutes": 999},
    ]
    for kwargs in cases:
        got = worker.assess_halt(repo, **kwargs)
        assert got["halt"] is True, kwargs
        assert got["reason"] and got["detail"], got


def test_a_human_stop_outranks_every_computed_halt(repo: Path) -> None:
    """"Somebody said stop" beats any budget — the order a person expects."""
    worker.request_stop(repo, reason="stop", actor="user:edwin")
    got = worker.assess_halt(repo, validator_failing=True, sessions_today=99)
    assert got["reason"] == "stop-switch", got


def test_clearing_the_stop_switch_lets_it_run_again(repo: Path) -> None:
    worker.request_stop(repo, reason="pause", actor="user:edwin")
    assert worker.stop_requested(repo) is True
    worker.clear_stop(repo)
    assert worker.assess_halt(repo)["halt"] is False


# ---- the lease ------------------------------------------------------------


def test_a_second_worker_is_refused_and_told_who_holds_it(repo: Path) -> None:
    """"Refused" with no name is a dead end; with a name it is a question
    somebody can answer."""
    worker.acquire(repo, worker_id="w1", item="TASK-1", now=NOW)
    got = worker.acquire(repo, worker_id="w2", item="TASK-2", now=NOW)
    assert got["ok"] is False
    assert "w1" in got["error"] and got["holder"] == "w1"


def test_an_expired_lease_is_an_escalation_not_an_opening(repo: Path) -> None:
    """A silent takeover makes two workers on one repo indistinguishable from
    one worker with a slow heartbeat."""
    worker.acquire(repo, worker_id="w1", now=NOW)
    later = NOW + dt.timedelta(minutes=worker.LEASE_STALE_MINUTES + 5)
    state = worker.lease_state(repo, now=later)
    assert state["state"] == "expired"
    got = worker.acquire(repo, worker_id="w2", now=later)
    assert got["ok"] is False, "an expired lease was silently taken over"
    assert "escalation" in got["error"]


def test_a_released_lease_frees_the_repo(repo: Path) -> None:
    worker.acquire(repo, worker_id="w1", now=NOW)
    worker.release(repo)
    assert worker.acquire(repo, worker_id="w2", now=NOW)["ok"] is True


def test_an_unreadable_lease_expires_rather_than_being_trusted(repo: Path) -> None:
    (repo / worker.LEASE_REL).parent.mkdir(parents=True, exist_ok=True)
    (repo / worker.LEASE_REL).write_text("{not json", encoding="utf-8")
    assert worker.lease_state(repo, now=NOW)["state"] == "absent"

    (repo / worker.LEASE_REL).write_text(
        json.dumps({"worker_id": "w1", "heartbeat": "not-a-date"}), encoding="utf-8",
    )
    assert worker.lease_state(repo, now=NOW)["state"] == "expired"


# ---- starting is a predicate, not an action -------------------------------


def test_can_start_refuses_without_a_policy(tmp_path: Path) -> None:
    got = worker.can_start(tmp_path, worker_id="w1")
    assert got["ok"] is False and got["why"] == "no-delegation"


def test_can_start_refuses_while_another_holds_the_lease(repo: Path) -> None:
    worker.acquire(repo, worker_id="w1", now=NOW)
    assert worker.can_start(repo, worker_id="w2", now=NOW)["why"] == "lease-held"


def test_the_module_starts_nothing() -> None:
    """Asserted in the source: this is brakes and a claim, not a loop.

    Building the halting machinery before the loop is REQ-0031's own order —
    brakes are tested before the hill — and a module that could start a run
    would have inverted it.
    """
    src = (
        Path(__file__).resolve().parent.parent
        / "src" / "project_os_cockpit" / "worker.py"
    ).read_text(encoding="utf-8")
    for launcher in ("subprocess", "Popen", "spawn", "os.system", "threading"):
        assert launcher not in src, f"worker.py can launch something via {launcher}"
