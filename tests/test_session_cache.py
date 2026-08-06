"""Prompt-cache economics read from a transcript (FEAT-0081 / TASK-0343).

Covers:
- Deduplication by ``message.id`` — Claude Code writes one entry per
  content block, so a naive scan double-counts every multi-block turn.
- The bounded tail read finding the last turn without reading the file.
- warm / cooling / cold against elapsed time, and the cold resume cost.
- Full-prefix re-write classification: session-start, TTL expiry,
  model switch (ISS-0104), and the honest ``other`` bucket.
- Degradation: absent file, empty file, truncated final line, entries
  carrying no usage.
"""

from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path

from project_os_cockpit import session_cache as sc

BASE = _dt.datetime(2026, 8, 6, 12, 0, tzinfo=_dt.timezone.utc)


def _ts(minutes: float) -> str:
    return (BASE + _dt.timedelta(minutes=minutes)).isoformat().replace(
        "+00:00", "Z"
    )


def _turn(
    mid: str,
    minutes: float,
    *,
    read: int,
    write: int,
    model: str = "claude-opus-5",
    blocks: int = 1,
    ttl: str = "1h",
) -> list[str]:
    """One assistant turn as ``blocks`` transcript entries.

    Every entry repeats the same ``usage`` and ``message.id`` — the shape
    the real files have, and the reason dedupe exists.
    """
    creation = {
        "ephemeral_1h_input_tokens": write if ttl == "1h" else 0,
        "ephemeral_5m_input_tokens": write if ttl == "5m" else 0,
    }
    entry = {
        "type": "assistant",
        "timestamp": _ts(minutes),
        "message": {
            "id": mid,
            "model": model,
            "usage": {
                "input_tokens": 2,
                "cache_read_input_tokens": read,
                "cache_creation_input_tokens": write,
                "cache_creation": creation,
                "output_tokens": 100,
            },
        },
    }
    return [json.dumps(entry) for _ in range(blocks)]


def _write(tmp_path: Path, lines: list[str], name: str = "t.jsonl") -> str:
    path = tmp_path / name
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    sc._LIVE_CACHE.clear()
    sc._HISTORY_CACHE.clear()
    return str(path)


# ---- dedupe -----------------------------------------------------------

def test_multi_block_turn_counted_once(tmp_path: Path) -> None:
    """Four entries, one message id — one turn, counted once."""
    path = _write(tmp_path, _turn("m1", 0, read=0, write=20_000, blocks=4))
    hist = sc.history(path)
    assert hist is not None
    assert hist.turns == 1
    assert hist.write_tokens == 20_000   # not 80_000


def test_distinct_turns_all_counted(tmp_path: Path) -> None:
    lines = (
        _turn("m1", 0, read=0, write=20_000, blocks=3)
        + _turn("m2", 1, read=20_000, write=5_000, blocks=2)
    )
    hist = sc.history(_write(tmp_path, lines))
    assert hist is not None
    assert hist.turns == 2
    assert hist.read_tokens == 20_000
    assert hist.write_tokens == 25_000


# ---- live tail read ---------------------------------------------------

def test_live_state_reads_last_turn(tmp_path: Path) -> None:
    lines = (
        _turn("m1", 0, read=0, write=20_000)
        + _turn("m2", 5, read=20_000, write=4_000)
    )
    path = _write(tmp_path, lines)
    state = sc.live_state(path, now=(BASE + _dt.timedelta(minutes=6)).timestamp())
    assert state is not None
    # Prefix after the last turn = what it read plus what it wrote.
    assert state.prefix_tokens == 24_000
    assert state.state == "warm"
    assert state.ttl_seconds == sc.TTL_1H


def test_live_state_does_not_read_whole_file(tmp_path: Path) -> None:
    """A transcript far larger than the tail budget still resolves, and
    the read is bounded — the strip re-renders on every snapshot."""
    filler = [
        json.dumps({"type": "user", "message": {"id": f"u{i}", "pad": "x" * 4000}})
        for i in range(400)
    ]
    lines = filler + _turn("last", 10, read=600_000, write=9_000)
    path = _write(tmp_path, lines)
    assert Path(path).stat().st_size > sc.TAIL_BYTES
    state = sc.live_state(path, now=(BASE + _dt.timedelta(minutes=11)).timestamp())
    assert state is not None
    assert state.prefix_tokens == 609_000


def test_warm_cooling_cold_by_elapsed_time(tmp_path: Path) -> None:
    path = _write(tmp_path, _turn("m1", 0, read=500_000, write=10_000))
    for minutes, expected in ((5, "warm"), (50, "cooling"), (75, "cold")):
        state = sc.live_state(
            path, now=(BASE + _dt.timedelta(minutes=minutes)).timestamp()
        )
        assert state is not None
        assert state.state == expected, f"{minutes}min -> {state.state}"


def test_cold_resume_cost_is_the_write_premium(tmp_path: Path) -> None:
    """510k tokens of opus prefix, re-written at 2x base input."""
    path = _write(tmp_path, _turn("m1", 0, read=500_000, write=10_000))
    state = sc.live_state(path, now=(BASE + _dt.timedelta(minutes=90)).timestamp())
    assert state is not None
    assert state.state == "cold"
    assert round(state.resume_cost_usd, 2) == round(510_000 / 1e6 * 5.0 * 2.0, 2)
    assert round(state.warm_cost_usd, 2) == round(510_000 / 1e6 * 5.0 * 0.1, 2)
    # The whole point: the swing is 20x.
    assert state.resume_cost_usd == state.warm_cost_usd * 20


def test_age_recomputed_on_cache_hit(tmp_path: Path) -> None:
    """A memoised state must still cool — the file not changing is
    exactly the case where the badge needs to move."""
    path = _write(tmp_path, _turn("m1", 0, read=500_000, write=10_000))
    first = sc.live_state(path, now=(BASE + _dt.timedelta(minutes=1)).timestamp())
    second = sc.live_state(path, now=(BASE + _dt.timedelta(minutes=90)).timestamp())
    assert first is not None and second is not None
    assert first.state == "warm"
    assert second.state == "cold"


def test_ttl_follows_the_write_kind(tmp_path: Path) -> None:
    path = _write(tmp_path, _turn("m1", 0, read=9_000, write=1_000, ttl="5m"))
    state = sc.live_state(path, now=(BASE + _dt.timedelta(minutes=1)).timestamp())
    assert state is not None
    assert state.ttl_seconds == sc.TTL_5M


# ---- classification (ISS-0104) ----------------------------------------

def test_first_turn_is_session_start_not_waste(tmp_path: Path) -> None:
    path = _write(tmp_path, _turn("m1", 0, read=0, write=30_000))
    hist = sc.history(path)
    assert hist is not None
    assert [e.cause for e in hist.events] == [sc.CAUSE_SESSION_START]
    assert hist.as_dict()["avoidable_cost_usd"] == 0.0


def test_idle_over_ttl_is_expiry(tmp_path: Path) -> None:
    lines = (
        _turn("m1", 0, read=0, write=20_000)
        + _turn("m2", 90, read=0, write=400_000)   # 90 min gap
    )
    hist = sc.history(_write(tmp_path, lines))
    assert hist is not None
    assert hist.events[1].cause == sc.CAUSE_TTL_EXPIRY


def test_model_switch_named(tmp_path: Path) -> None:
    lines = (
        _turn("m1", 0, read=0, write=20_000, model="claude-opus-5")
        + _turn("m2", 5, read=0, write=400_000, model="claude-opus-4-8")
    )
    hist = sc.history(_write(tmp_path, lines))
    assert hist is not None
    ev = hist.events[1]
    assert ev.cause == sc.CAUSE_MODEL_SWITCH
    assert ev.prev_model == "claude-opus-5"
    assert ev.model == "claude-opus-4-8"


def test_small_model_switch_is_not_named(tmp_path: Path) -> None:
    """Below the discard floor a switch is noise, not a finding."""
    lines = (
        _turn("m1", 0, read=0, write=20_000, model="claude-opus-5")
        + _turn("m2", 5, read=0, write=6_000, model="claude-opus-4-8")
    )
    hist = sc.history(_write(tmp_path, lines))
    assert hist is not None
    assert hist.events[1].cause == sc.CAUSE_OTHER


def test_sub_hour_rewrite_without_switch_is_other(tmp_path: Path) -> None:
    """Eviction before TTL is real. ``other`` is the honest answer, not
    a bucket to force these into."""
    lines = (
        _turn("m1", 0, read=0, write=20_000)
        + _turn("m2", 5, read=0, write=300_000)   # same model, 5 min gap
    )
    hist = sc.history(_write(tmp_path, lines))
    assert hist is not None
    assert hist.events[1].cause == sc.CAUSE_OTHER


def test_buckets_and_avoidable_cost(tmp_path: Path) -> None:
    lines = (
        _turn("m1", 0, read=0, write=20_000)
        + _turn("m2", 90, read=0, write=100_000)
        + _turn("m3", 95, read=0, write=200_000, model="claude-opus-4-8")
    )
    hist = sc.history(_write(tmp_path, lines))
    assert hist is not None
    buckets = hist.buckets()
    assert buckets[sc.CAUSE_SESSION_START]["count"] == 1
    assert buckets[sc.CAUSE_TTL_EXPIRY]["tokens"] == 100_000
    assert buckets[sc.CAUSE_MODEL_SWITCH]["tokens"] == 200_000
    # Avoidable excludes the unavoidable first cold write.
    payload = hist.as_dict()
    assert payload["avoidable_cost_usd"] > 0
    assert payload["avoidable_cost_usd"] < (
        payload["read_cost_usd"] + payload["write_cost_usd"]
    )


def test_live_model_switch_reported(tmp_path: Path) -> None:
    lines = (
        _turn("m1", 0, read=600_000, write=10_000, model="claude-opus-5")
        + _turn("m2", 2, read=0, write=610_000, model="claude-opus-4-8")
    )
    path = _write(tmp_path, lines)
    state = sc.live_state(path, now=(BASE + _dt.timedelta(minutes=3)).timestamp())
    assert state is not None
    assert state.model_switch is not None
    assert state.model_switch["from"] == "claude-opus-5"
    assert state.model_switch["to"] == "claude-opus-4-8"
    assert state.model_switch["discarded_tokens"] == 610_000
    assert state.as_dict()["model_switch"]["cost_usd"] > 0


# ---- degradation ------------------------------------------------------

def test_absent_file(tmp_path: Path) -> None:
    assert sc.live_state(str(tmp_path / "nope.jsonl")) is None
    assert sc.history(str(tmp_path / "nope.jsonl")) is None
    assert sc.live_state(None) is None
    assert sc.history(None) is None


def test_empty_and_usageless_transcript(tmp_path: Path) -> None:
    empty = tmp_path / "empty.jsonl"
    empty.write_text("", encoding="utf-8")
    assert sc.live_state(str(empty)) is None

    lines = [json.dumps({"type": "user", "message": {"id": "u1"}})]
    assert sc.live_state(_write(tmp_path, lines, "u.jsonl")) is None


def test_truncated_final_line_tolerated(tmp_path: Path) -> None:
    """A transcript being written to has a partial last line."""
    path = tmp_path / "partial.jsonl"
    good = _turn("m1", 0, read=100_000, write=5_000)[0]
    path.write_text(good + "\n" + '{"type":"assistant","mess', encoding="utf-8")
    sc._LIVE_CACHE.clear()
    sc._HISTORY_CACHE.clear()
    state = sc.live_state(
        str(path), now=(BASE + _dt.timedelta(minutes=1)).timestamp()
    )
    assert state is not None
    assert state.prefix_tokens == 105_000


def test_price_table_by_family() -> None:
    assert sc.price_per_mtok("claude-opus-5") == 5.0
    assert sc.price_per_mtok("claude-fable-5") == 10.0
    assert sc.price_per_mtok("claude-sonnet-5") == 3.0
    assert sc.price_per_mtok("claude-haiku-4-5-20251001") == 1.0
    assert sc.price_per_mtok(None) == sc._PRICE_DEFAULT
