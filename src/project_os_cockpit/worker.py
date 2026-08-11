"""The standing worker's brakes, and its lease (FEAT-0074).

[[REQ-0031]]'s fourth criterion is the order this module was built in:

    *"Every halt path exercised by drill before any repo runs unattended —
    brakes are tested before the hill."*

So the stop conditions and the lease exist before the loop that would need
them, and `tests/test_worker.py` drills every halt path.

**Nothing here starts a loop.** `can_start` is a predicate, and its first
question is whether an approved delegation policy exists — which by
`delegation.load`'s default it does not, until a principal approves one
([[ADR-0009]] §4). A worker with no policy is not a worker.

The stop conditions, from REQ-0031:

* budgets bound every loop — sessions per day, wall-clock per session;
* failure compounds toward **stopping**, never toward retrying: two failed
  close-outs park an item, three parked items halt the worker;
* the human's stop switch halts from the landing, without shell access;
* a halt **files what and why** — a halted worker is an obligation on the desk,
  not an absence.

That last one is the difference between a system that stopped and a system that
merely went quiet, and quiet is indistinguishable from broken.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
from pathlib import Path
from typing import Any

from . import delegation

LEASE_REL = Path(".cockpit") / "lease.json"
STOP_REL = Path(".cockpit") / "worker-stop"

#: Defaults, stated here because the number IS the decision.
MAX_SESSIONS_PER_DAY = 12
MAX_SESSION_MINUTES = 30
#: Two failed close-outs park an item; three parked items halt the worker.
FAILURES_TO_PARK = 2
PARKED_TO_HALT = 3
#: A lease whose heartbeat is older than this is expired — as an escalation
#: event, never a silent takeover.
LEASE_STALE_MINUTES = 10


def _now() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


def _iso(value: _dt.datetime) -> str:
    return value.isoformat(timespec="seconds")


# ---- the lease ------------------------------------------------------------


def read_lease(root: Path) -> dict[str, Any] | None:
    try:
        raw = json.loads((root / LEASE_REL).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return raw if isinstance(raw, dict) else None


def lease_state(root: Path, *, now: _dt.datetime | None = None) -> dict[str, Any]:
    """Live, expired, or absent — and an expired lease is an **event**.

    A worker that silently took over an expired lease would make two workers on
    one repo indistinguishable from one worker with a slow heartbeat.
    """
    now = now or _now()
    lease = read_lease(root)
    if not lease:
        return {"state": "absent"}
    beat = lease.get("heartbeat") or lease.get("acquired") or ""
    try:
        last = _dt.datetime.fromisoformat(str(beat).replace("Z", "+00:00"))
    except ValueError:
        return {"state": "expired", "lease": lease, "why": "unreadable heartbeat"}
    if last.tzinfo is None:
        last = last.replace(tzinfo=_dt.timezone.utc)
    age_minutes = (now - last).total_seconds() / 60.0
    if age_minutes > LEASE_STALE_MINUTES:
        return {"state": "expired", "lease": lease, "age_minutes": age_minutes,
                "why": f"heartbeat {age_minutes:.0f}m old (limit {LEASE_STALE_MINUTES}m)"}
    return {"state": "live", "lease": lease, "age_minutes": age_minutes}


def acquire(root: Path, *, worker_id: str, item: str = "",
            now: _dt.datetime | None = None) -> dict[str, Any]:
    """Claim the repo, or refuse **naming the holder**.

    "Refused" with no name is a dead end; with a name it is a question somebody
    can answer.
    """
    now = now or _now()
    state = lease_state(root, now=now)
    if state["state"] == "live":
        holder = state["lease"].get("worker_id", "unknown")
        return {"ok": False, "error": f"a live lease is held by {holder!r}",
                "holder": holder}
    if state["state"] == "expired":
        # Not taken silently: expiry is surfaced, and taking over is a separate
        # decision the caller makes with the reason in hand.
        return {"ok": False, "error": f"lease expired ({state.get('why')}) — "
                "expiry is an escalation, not an opening", "expired": state}
    lease = {"worker_id": worker_id, "item": item,
             "acquired": _iso(now), "heartbeat": _iso(now)}
    path = root / LEASE_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(lease, indent=2), encoding="utf-8")
    return {"ok": True, "lease": lease}


def release(root: Path) -> bool:
    try:
        (root / LEASE_REL).unlink()
        return True
    except OSError:
        return False


# ---- the brakes -----------------------------------------------------------


def stop_requested(root: Path) -> bool:
    """The human's stop switch, from the landing — no shell access needed."""
    return (root / STOP_REL).exists()


def request_stop(root: Path, *, reason: str = "", actor: str = "") -> dict[str, Any]:
    path = root / STOP_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"reason": reason, "actor": actor, "at": _iso(_now())}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def clear_stop(root: Path) -> bool:
    try:
        (root / STOP_REL).unlink()
        return True
    except OSError:
        return False


def assess_halt(
    root: Path,
    *,
    sessions_today: int = 0,
    session_minutes: float = 0.0,
    parked_items: int = 0,
    validator_failing: bool = False,
    now: _dt.datetime | None = None,
) -> dict[str, Any]:
    """Should the worker stop, and **why**?

    Returns the first reason found, in the order a person would want them: an
    explicit human stop before any computed one, because "somebody said stop"
    outranks every budget.

    Every branch names its reason. A halt with no reason is the quiet this
    module exists to prevent.
    """
    if stop_requested(root):
        return {"halt": True, "reason": "stop-switch",
                "detail": "a human asked the worker to stop"}
    policy = delegation.load(root)
    if not policy.get("approved"):
        return {"halt": True, "reason": "no-delegation",
                "detail": "no approved delegation policy — no policy, no worker"}
    if validator_failing:
        return {"halt": True, "reason": "validator-red",
                "detail": "the record does not validate; working on a broken record compounds it"}
    if parked_items >= PARKED_TO_HALT:
        return {"halt": True, "reason": "parked-items",
                "detail": f"{parked_items} items parked (limit {PARKED_TO_HALT}) — "
                          "failure is compounding, not clearing"}
    if sessions_today >= MAX_SESSIONS_PER_DAY:
        return {"halt": True, "reason": "session-budget",
                "detail": f"{sessions_today} sessions today (limit {MAX_SESSIONS_PER_DAY})"}
    if session_minutes >= MAX_SESSION_MINUTES:
        return {"halt": True, "reason": "wall-clock",
                "detail": f"{session_minutes:.0f}m in this session (limit {MAX_SESSION_MINUTES}m)"}
    return {"halt": False, "reason": "", "detail": "within every bound"}


def should_park(failures: int) -> bool:
    """Failure compounds toward stopping, never toward retrying."""
    return failures >= FAILURES_TO_PARK


def can_start(root: Path, *, worker_id: str = "", now: _dt.datetime | None = None) -> dict[str, Any]:
    """Everything that must be true before a loop may begin.

    Deliberately a predicate and not a launcher: **this module starts nothing.**
    The order is the safety order — policy first, because without a delegation
    there is no worker to have budgets.
    """
    halt = assess_halt(root, now=now)
    if halt["halt"]:
        return {"ok": False, "why": halt["reason"], "detail": halt["detail"]}
    state = lease_state(root, now=now)
    if state["state"] == "live" and state["lease"].get("worker_id") != worker_id:
        return {"ok": False, "why": "lease-held",
                "detail": f"held by {state['lease'].get('worker_id')!r}"}
    return {"ok": True, "why": "", "detail": "policy approved, no halt, lease free"}
