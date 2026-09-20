"""``GET /api/cockpit/vocabulary`` — the vocabularies served as data (ISS-0292).

project-os-deck reads the same notes this cockpit reads and could not ask it
which statuses belong to which band, which severities a write will accept, or
which callout types render. So it copied the tables, and its copy put `draft`,
`proposed` and `ready` in the wrong band within two days. It also asks for an
issue's severity in a free text box, because the four legal values were never
available to offer.

These tests assert the reply against `statuses.py`, `note_writes.SEVERITIES`
and `callouts.KNOWN_TYPES` themselves rather than against a recorded fixture.
A fixture would pin today's values; what a client needs pinned is that the
route still carries *every* table, so dropping one is what has to fail here.
"""

from __future__ import annotations

import json
import threading
import urllib.request
from pathlib import Path

import pytest

from project_os_cockpit import callouts, cockpit, note_writes, statuses
from project_os_cockpit.server import (
    DocsServer,
    _NoDNSThreadingHTTPServer,
    _make_handler,
)


@pytest.fixture()
def port(tmp_path: Path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "FEAT-0001-Thing.md").write_text(
        '---\ntype: "[[feature]]"\nid: FEAT-0001\ntitle: "Thing"\n'
        "status: done\n---\n\n# Thing\n", encoding="utf-8")
    server = DocsServer(docs_root=docs, bind="127.0.0.1", port=0)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0),
        _make_handler(server.docs_root, server.index, server.bus,
                      cockpit_state=server.cockpit_state))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        yield httpd.server_address[1]
    finally:
        httpd.shutdown()
        httpd.server_close()


def _get(port: int, path: str) -> dict:
    with urllib.request.urlopen(
        f"http://127.0.0.1:{port}{path}", timeout=5
    ) as resp:
        assert resp.status == 200
        return json.loads(resp.read())


def test_the_route_serves_every_vocabulary_a_client_would_copy(port: int) -> None:
    """The six tables ISS-0292 names, each against its own source module.

    Dropping one from the payload is the way this capability quietly stops
    being one, so each is asserted by name and by content.
    """
    got = _get(port, "/api/cockpit/vocabulary")

    assert got["bands"] == {b: list(m) for b, m in statuses.BANDS.items()}, (
        "the bands are what Deck copied and got wrong; they must be served "
        "exactly as statuses.BANDS holds them")
    assert got["band_tokens"] == dict(statuses.BAND_TOKEN)
    assert got["completed"] == sorted(statuses.COMPLETED_STATUSES)
    assert got["legacy_bands"] == dict(statuses.LEGACY_STATUS_BAND)
    assert got["severity_order"] == list(cockpit.SEVERITY_ORDER)
    assert got["severities"] == sorted(note_writes.SEVERITIES)
    assert got["callout_types"] == sorted(callouts.KNOWN_TYPES)
    assert got["schema_version"] == cockpit.SCHEMA_VERSION


def test_the_band_deck_got_wrong_is_the_one_the_route_says(port: int) -> None:
    """The measured drift, asserted as itself.

    Deck put `draft`, `proposed` and `ready` in its "doing" band; `BANDS` puts
    all three in `pending`. A client reading this route gets the right answer
    without a second table to maintain.
    """
    bands = _get(port, "/api/cockpit/vocabulary")["bands"]
    for status in ("draft", "proposed", "ready"):
        assert status in bands["pending"], status
        assert status not in bands["active"], status


def test_a_severity_the_write_path_refuses_is_not_offered(port: int) -> None:
    """The severities served are the ones `/api/notes/transition` accepts.

    The point of serving them is that a picker can offer four values instead
    of a text box collecting a fifth. That only holds while the two agree, so
    the agreement is the assertion — both directions, so neither list can grow
    a value the other has not.
    """
    got = _get(port, "/api/cockpit/vocabulary")
    assert set(got["severities"]) == set(note_writes.SEVERITIES)
    assert set(got["severity_order"]) == set(note_writes.SEVERITIES), (
        "the ranking and the accepted set have diverged; a picker built on "
        "the ranking would now offer a value the write path refuses")


def test_the_payload_is_stable_across_calls(port: int) -> None:
    """Three of these tables are sets in Python, and a frozenset's iteration
    order is not stable across runs. A client pins this payload to a fixture —
    Deck does exactly that — so a payload that reorders itself would fail that
    fixture for no reason anybody could find."""
    first = _get(port, "/api/cockpit/vocabulary")
    second = _get(port, "/api/cockpit/vocabulary")
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    for key in ("completed", "severities", "callout_types"):
        assert first[key] == sorted(first[key]), f"{key} is not sorted"
