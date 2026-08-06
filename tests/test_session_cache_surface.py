"""Cache economics on the wire (FEAT-0081 / TASK-0344, TASK-0345).

Covers the two surfaces the reader feeds:
- the ``cache`` block on ``/api/cockpit/state``, which the agent strip
  renders without a second fetch;
- ``GET /api/cockpit/session-cache``, the retrospective per-workspace
  accounting.

The reader itself is covered in ``test_session_cache.py``; this file is
about the wiring, including the case that matters most in practice — a
session whose transcript path points at nothing must yield an absent
badge, never an error.
"""

from __future__ import annotations

import datetime as _dt
import json
import threading
import urllib.request
from pathlib import Path
from typing import Any

from project_os_cockpit import session_cache
from project_os_cockpit.agent_hooks import AgentSessionTracker
from project_os_cockpit.server import (
    DocsServer,
    _NoDNSThreadingHTTPServer,
    _make_handler,
)

SID = "sess-cache-1"
BASE = _dt.datetime.now(_dt.timezone.utc)


def _make_workspace(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "README.md").write_text("# Hi\n", encoding="utf-8")
    (docs / "changes").mkdir()
    return docs


def _spin_up(docs: Path, tracker: AgentSessionTracker):
    server = DocsServer(docs_root=docs, bind="127.0.0.1", port=0)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0),
        _make_handler(
            server.docs_root, server.index, server.bus,
            cockpit_state=server.cockpit_state,
            agent_tracker=tracker,
        ),
    )
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return server, httpd, port


def _get(port: int, path: str) -> dict:
    with urllib.request.urlopen(
        f"http://127.0.0.1:{port}{path}", timeout=3,
    ) as resp:
        return json.loads(resp.read())


def _transcript(
    tmp_path: Path,
    turns: list[tuple[float, int, int, str]],
    name: str = "t.jsonl",
) -> str:
    """``turns`` is (minutes_ago, read, write, model)."""
    lines = []
    for i, (ago, read, write, model) in enumerate(turns):
        ts = (BASE - _dt.timedelta(minutes=ago)).isoformat().replace(
            "+00:00", "Z"
        )
        lines.append(json.dumps({
            "type": "assistant",
            "timestamp": ts,
            "message": {
                "id": f"m{i}",
                "model": model,
                "usage": {
                    "cache_read_input_tokens": read,
                    "cache_creation_input_tokens": write,
                    "cache_creation": {
                        "ephemeral_1h_input_tokens": write,
                        "ephemeral_5m_input_tokens": 0,
                    },
                },
            },
        }))
    path = tmp_path / name
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    session_cache._LIVE_CACHE.clear()
    session_cache._HISTORY_CACHE.clear()
    return str(path)


def _tracker_with(docs: Path, tmp_path: Path, transcript: str | None):
    tracker = AgentSessionTracker(
        docs_root=docs, sessions_path=tmp_path / "sessions.json"
    )
    ev: dict[str, Any] = {"hook_event_name": "SessionStart", "session_id": SID}
    if transcript is not None:
        ev["transcript_path"] = transcript
    tracker.ingest(ev)
    return tracker


def test_state_carries_warm_cache_block(tmp_path: Path) -> None:
    docs = _make_workspace(tmp_path)
    path = _transcript(tmp_path, [(30, 0, 20_000, "claude-opus-5"),
                                  (2, 500_000, 10_000, "claude-opus-5")])
    tracker = _tracker_with(docs, tmp_path, path)
    _server, httpd, port = _spin_up(docs, tracker)
    try:
        cache = _get(port, "/api/cockpit/state")["cache"]
        assert cache["state"] == "warm"
        assert cache["prefix_tokens"] == 510_000
        # The 20x swing is the whole point of the badge.
        assert cache["resume_cost_usd"] > cache["warm_cost_usd"]
    finally:
        httpd.shutdown()


def test_state_reports_cold_after_ttl(tmp_path: Path) -> None:
    docs = _make_workspace(tmp_path)
    path = _transcript(tmp_path, [(200, 0, 20_000, "claude-opus-5"),
                                  (90, 400_000, 8_000, "claude-opus-5")])
    tracker = _tracker_with(docs, tmp_path, path)
    _server, httpd, port = _spin_up(docs, tracker)
    try:
        cache = _get(port, "/api/cockpit/state")["cache"]
        assert cache["state"] == "cold"
        assert cache["resume_cost_usd"] > 0
    finally:
        httpd.shutdown()


def test_state_reports_model_switch(tmp_path: Path) -> None:
    """ISS-0104 on the live surface."""
    docs = _make_workspace(tmp_path)
    path = _transcript(tmp_path, [(10, 600_000, 5_000, "claude-opus-5"),
                                  (2, 0, 605_000, "claude-opus-4-8")])
    tracker = _tracker_with(docs, tmp_path, path)
    _server, httpd, port = _spin_up(docs, tracker)
    try:
        switch = _get(port, "/api/cockpit/state")["cache"]["model_switch"]
        assert switch["from"] == "claude-opus-5"
        assert switch["to"] == "claude-opus-4-8"
        assert switch["discarded_tokens"] == 605_000
    finally:
        httpd.shutdown()


def test_missing_transcript_yields_no_cache_block(tmp_path: Path) -> None:
    """An absent badge, never an error — this runs in the snapshot path."""
    docs = _make_workspace(tmp_path)
    tracker = _tracker_with(docs, tmp_path, str(tmp_path / "gone.jsonl"))
    _server, httpd, port = _spin_up(docs, tracker)
    try:
        state = _get(port, "/api/cockpit/state")
        assert "cache" not in state
        assert state.get("session") is not None   # the rest still renders
    finally:
        httpd.shutdown()


def test_no_transcript_path_at_all(tmp_path: Path) -> None:
    docs = _make_workspace(tmp_path)
    tracker = _tracker_with(docs, tmp_path, None)
    _server, httpd, port = _spin_up(docs, tracker)
    try:
        assert "cache" not in _get(port, "/api/cockpit/state")
    finally:
        httpd.shutdown()


def test_session_cache_endpoint_splits_by_cause(tmp_path: Path) -> None:
    docs = _make_workspace(tmp_path)
    path = _transcript(tmp_path, [
        (300, 10_000, 20_000, "claude-opus-5"),
        (200, 0, 100_000, "claude-opus-5"),     # 100 min gap -> expiry
        (195, 0, 200_000, "claude-opus-4-8"),   # 5 min gap + switch
    ])
    tracker = _tracker_with(docs, tmp_path, path)
    _server, httpd, port = _spin_up(docs, tracker)
    try:
        report = _get(port, "/api/cockpit/session-cache")
        rew = report["rewrites"]
        assert rew[session_cache.CAUSE_TTL_EXPIRY]["tokens"] == 100_000
        assert rew[session_cache.CAUSE_MODEL_SWITCH]["tokens"] == 200_000
        assert report["turns"] == 3
        assert report["transcripts"] == 1
        assert report["avoidable_cost_usd"] > 0
    finally:
        httpd.shutdown()


def test_session_cache_endpoint_empty_workspace(tmp_path: Path) -> None:
    docs = _make_workspace(tmp_path)
    tracker = AgentSessionTracker(
        docs_root=docs, sessions_path=tmp_path / "sessions.json"
    )
    _server, httpd, port = _spin_up(docs, tracker)
    try:
        report = _get(port, "/api/cockpit/session-cache")
        assert report["transcripts"] == 0
        assert report["rewrites"] == {}
        assert report["avoidable_cost_usd"] == 0.0
    finally:
        httpd.shutdown()
