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
from typing import Any

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


def test_live_state_resolves_from_a_file_larger_than_the_budget(tmp_path: Path) -> None:
    """The last turn is found even when the file dwarfs the tail budget."""
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


def test_live_read_actually_reads_a_bounded_number_of_bytes(
    tmp_path: Path, monkeypatch: Any,
) -> None:
    """ISS-0109: observe the BYTES, not just the answer.

    The previous guard asserted only that the right prefix came out —
    which it does whether the read is 512KB or 34MB. Replacing
    `start = max(0, size - budget)` with `start = 0` survived it. This
    counts what comes off the disk, so losing the bound turns it red.
    """
    filler = [
        json.dumps({"type": "user", "message": {"id": f"u{i}", "pad": "x" * 4000}})
        for i in range(1500)
    ]
    path = _write(tmp_path, filler + _turn("last", 10, read=600_000, write=9_000))
    size = Path(path).stat().st_size
    assert size > 5_000_000, "fixture must dwarf the tail budget"

    read_bytes = 0
    real_open = open

    def counting_open(file, mode="r", *args, **kwargs):  # type: ignore[no-untyped-def]
        handle = real_open(file, mode, *args, **kwargs)
        if "b" not in mode:
            return handle
        real_read = handle.read

        def read(*a, **k):  # type: ignore[no-untyped-def]
            nonlocal read_bytes
            data = real_read(*a, **k)
            read_bytes += len(data)
            return data

        handle.read = read  # type: ignore[method-assign]
        return handle

    monkeypatch.setattr("builtins.open", counting_open)
    state = sc.live_state(path, now=(BASE + _dt.timedelta(minutes=11)).timestamp())
    assert state is not None and state.prefix_tokens == 609_000
    assert read_bytes <= sc.TAIL_BYTES, (
        f"live read pulled {read_bytes:,} bytes from a {size:,}-byte file; "
        f"the tail budget is {sc.TAIL_BYTES:,}"
    )


def test_tail_budget_is_large_enough_to_find_a_turn_behind_real_output(
    tmp_path: Path,
) -> None:
    """Guards TAIL_BYTES from below — shrinking it to 1KB survived the
    old suite. A turn sitting behind one fat tool result must still be
    found without the fallback read."""
    fat = json.dumps({"type": "user", "message": {"id": "big", "pad": "x" * 200_000}})
    path = _write(tmp_path, _turn("m1", 0, read=400_000, write=6_000) + [fat])
    lines = sc._read_tail(path, sc.TAIL_BYTES)
    assert list(sc._iter_turns(iter(lines))), (
        "TAIL_BYTES is too small to see past a single large entry"
    )


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


# ---- the constants that survived mutation (ISS-0109) ------------------

def test_5m_writes_are_cheaper_than_1h_writes(tmp_path: Path) -> None:
    """`WRITE_MULT_5M` 1.25 -> 99 survived the old suite: nothing costed
    a 5m write. A shorter TTL must cost less to create, not more."""
    p5 = _write(tmp_path, _turn("a", 0, read=0, write=400_000, ttl="5m"), "5m.jsonl")
    p1h = _write(tmp_path, _turn("a", 0, read=0, write=400_000, ttl="1h"), "1h.jsonl")
    h5, h1 = sc.history(p5), sc.history(p1h)
    assert h5 is not None and h1 is not None
    assert h5.write_cost_usd < h1.write_cost_usd
    assert round(h5.write_cost_usd, 4) == round(400_000 / 1e6 * 5.0 * 1.25, 4)


def test_small_rewrites_are_below_the_reporting_floor(tmp_path: Path) -> None:
    """`FULL_REWRITE_MIN` 5000 -> 1000 survived. A re-write under the
    floor must not be reported as an event at all."""
    lines = (
        _turn("m1", 0, read=50_000, write=5_000)
        + _turn("m2", 5, read=0, write=2_000)      # under the floor
        + _turn("m3", 9, read=0, write=9_000)      # over it
    )
    hist = sc.history(_write(tmp_path, lines))
    assert hist is not None
    assert [e.tokens for e in hist.events] == [9_000]


def test_cooling_starts_in_the_last_quarter_of_the_ttl(tmp_path: Path) -> None:
    """The 0.75 threshold -> 0.30 survived. Half-way through the TTL is
    still warm; cooling is the final stretch, or the word means nothing."""
    path = _write(tmp_path, _turn("m1", 0, read=400_000, write=8_000))
    for minutes, expected in ((30, "warm"), (44, "warm"), (46, "cooling")):
        st = sc.live_state(path, now=(BASE + _dt.timedelta(minutes=minutes)).timestamp())
        assert st is not None and st.state == expected, f"{minutes}min -> {st.state}"


def test_live_switch_needs_a_discarded_prefix_not_merely_a_new_model(
    tmp_path: Path,
) -> None:
    """Both live preconditions survived mutation. A model change on a
    turn that READ its cache discarded nothing, and one that wrote only a
    little discarded little — neither is the ISS-0104 event."""
    # Big enough write to clear the discard floor, so the ONLY thing
    # standing between this and a false switch is `last.read == 0`.
    read_hit = (
        _turn("m1", 0, read=600_000, write=5_000, model="claude-opus-5")
        + _turn("m2", 2, read=600_000, write=200_000, model="claude-opus-4-8")
    )
    st = sc.live_state(_write(tmp_path, read_hit, "hit.jsonl"),
                       now=(BASE + _dt.timedelta(minutes=3)).timestamp())
    assert st is not None and st.model_switch is None, "cache was READ — nothing discarded"

    tiny = (
        _turn("m1", 0, read=600_000, write=5_000, model="claude-opus-5")
        + _turn("m2", 2, read=0, write=9_000, model="claude-opus-4-8")
    )
    st = sc.live_state(_write(tmp_path, tiny, "tiny.jsonl"),
                       now=(BASE + _dt.timedelta(minutes=3)).timestamp())
    assert st is not None and st.model_switch is None, "below the discard floor"


# ---- ISS-0106: an API-error placeholder is not a turn -----------------

def _synthetic(mid: str, minutes: float) -> list[str]:
    """The entry Claude Code writes when a request fails."""
    return [json.dumps({
        "type": "assistant",
        "timestamp": _ts(minutes),
        "message": {
            "id": mid, "model": "<synthetic>",
            "content": [{"type": "text",
                         "text": "API Error: Unable to connect to API (ECONNRESET)"}],
            "usage": {"input_tokens": 0, "cache_read_input_tokens": 0,
                      "cache_creation_input_tokens": 0, "output_tokens": 0},
        },
    })]


def test_synthetic_entry_is_not_counted_as_a_turn(tmp_path: Path) -> None:
    lines = (
        _turn("m1", 0, read=100_000, write=5_000)
        + _synthetic("err1", 1)
        + _turn("m2", 2, read=105_000, write=4_000)
    )
    hist = sc.history(_write(tmp_path, lines))
    assert hist is not None
    assert hist.turns == 2


def test_synthetic_entry_does_not_fabricate_a_model_switch(tmp_path: Path) -> None:
    """The defect in full: a retry seconds after a reset made a 3-hour
    idle gap read as one minute AND filed it as a model switch, because
    the placeholder became `prev`. Truth: TTL expiry, same model."""
    lines = (
        _turn("m1", 0, read=600_000, write=5_000, model="claude-opus-5")
        + _synthetic("err1", 179)
        + _turn("m2", 180, read=0, write=610_000, model="claude-opus-5")
    )
    hist = sc.history(_write(tmp_path, lines))
    assert hist is not None
    assert [e.cause for e in hist.events] == [sc.CAUSE_TTL_EXPIRY]
    assert hist.events[0].prev_model == "claude-opus-5"
    assert hist.events[0].gap_seconds == 180 * 60


def test_synthetic_entry_never_reaches_the_strip(tmp_path: Path) -> None:
    lines = (
        _turn("m1", 0, read=600_000, write=5_000, model="claude-opus-5")
        + _synthetic("err1", 2)
    )
    st = sc.live_state(_write(tmp_path, lines),
                       now=(BASE + _dt.timedelta(minutes=3)).timestamp())
    assert st is not None
    assert st.model is None or st.model == "claude-opus-5"
    assert st.model_switch is None
    assert st.prefix_tokens == 605_000


def test_synthetic_entry_is_skipped_even_when_it_reports_tokens(
    tmp_path: Path,
) -> None:
    """The two filters are not redundant, and this is the case that
    separates them: a request that failed after streaming some output
    can carry non-zero usage, so the shape check passes it and only the
    sentinel stops it becoming `prev`."""
    partial = [json.dumps({
        "type": "assistant", "timestamp": _ts(1),
        "message": {"id": "err-partial", "model": "<synthetic>",
                    "usage": {"input_tokens": 4, "cache_read_input_tokens": 0,
                              "cache_creation_input_tokens": 0, "output_tokens": 12}},
    })]
    lines = (
        _turn("m1", 0, read=600_000, write=5_000, model="claude-opus-5")
        + partial
        + _turn("m2", 180, read=0, write=610_000, model="claude-opus-5")
    )
    hist = sc.history(_write(tmp_path, lines))
    assert hist is not None
    assert hist.turns == 2
    assert [e.cause for e in hist.events] == [sc.CAUSE_TTL_EXPIRY]
    assert hist.events[0].prev_model == "claude-opus-5"


def test_zero_usage_entry_is_skipped_under_any_model_name(tmp_path: Path) -> None:
    """The guard is on the SHAPE of the data, not the sentinel string —
    a future placeholder under a different name must not slip through."""
    zero = [json.dumps({
        "type": "assistant", "timestamp": _ts(1),
        "message": {"id": "z1", "model": "claude-opus-5",
                    "usage": {"input_tokens": 0, "cache_read_input_tokens": 0,
                              "cache_creation_input_tokens": 0, "output_tokens": 0}},
    })]
    lines = _turn("m1", 0, read=100_000, write=5_000) + zero
    hist = sc.history(_write(tmp_path, lines))
    assert hist is not None
    assert hist.turns == 1


# ---- ISS-0107 / ISS-0108 ---------------------------------------------

def test_switch_announcement_expires_and_the_state_returns(tmp_path: Path) -> None:
    """A switch is a recent event. Left up forever it suppressed the
    warm/cooling/cold word for the life of the transcript."""
    lines = (
        _turn("m1", 0, read=600_000, write=5_000, model="claude-opus-5")
        + _turn("m2", 2, read=0, write=610_000, model="claude-opus-4-8")
    )
    path = _write(tmp_path, lines)

    fresh = sc.live_state(path, now=(BASE + _dt.timedelta(minutes=5)).timestamp())
    assert fresh is not None and fresh.model_switch is not None
    assert fresh.state == "warm"

    later = sc.live_state(path, now=(BASE + _dt.timedelta(minutes=30)).timestamp())
    assert later is not None and later.model_switch is None, "should have expired"

    cold = sc.live_state(path, now=(BASE + _dt.timedelta(minutes=90)).timestamp())
    assert cold is not None and cold.state == "cold" and cold.model_switch is None


def test_turn_without_a_timestamp_yields_no_badge(tmp_path: Path) -> None:
    """ISS-0108: `cold` with an age of 56 years, asserted from absent
    data. An absent badge is the module's contract for every other
    failure; it is the contract here too."""
    entry = [json.dumps({
        "type": "assistant",
        "message": {"id": "n1", "model": "claude-opus-5",
                    "usage": {"cache_read_input_tokens": 400_000,
                              "cache_creation_input_tokens": 9_000}},
    })]
    assert sc.live_state(_write(tmp_path, entry, "nots.jsonl")) is None


def test_price_table_by_family() -> None:
    assert sc.price_per_mtok("claude-opus-5") == 5.0
    assert sc.price_per_mtok("claude-fable-5") == 10.0
    assert sc.price_per_mtok("claude-sonnet-5") == 3.0
    assert sc.price_per_mtok("claude-haiku-4-5-20251001") == 1.0
    assert sc.price_per_mtok(None) == sc._PRICE_DEFAULT
