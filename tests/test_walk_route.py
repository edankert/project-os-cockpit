"""`/api/cockpit/walk` — one platform, named or refused ([[TASK-0618]]).

The route's whole job beyond serving the payload is to refuse the two requests
that would answer confidently and wrongly: `all`, which would ask a walker to
tick a check for a platform they are not holding, and a name no ledger carries,
which reads no verdicts and so reports **every check in the repo** as owed.
"""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from project_os_cockpit.server import (
    DocsServer,
    _NoDNSThreadingHTTPServer,
    _make_handler,
)


def _docs(tmp_path: Path, *, release_platform: str | None = "android") -> Path:
    docs = tmp_path / "docs"
    (docs / "tests" / "acceptance").mkdir(parents=True)
    (docs / "releases" / "ledgers").mkdir(parents=True)
    for n, area in (("0001", "Profile"), ("0002", "Workouts")):
        (docs / "tests" / "acceptance" / f"TST-{n}-C.md").write_text(
            f'---\ntype: "[[test]]"\nid: TST-{n}\ntitle: "C {n}"\n'
            f'level: acceptance\nstatus: active\narea: "{area}"\nmark: todo\n'
            "---\n\n# C\n\n## Setup\n\nA phone.\n", encoding="utf-8")
    if release_platform is not None:
        (docs / "releases" / "REL-0001-R.md").write_text(
            '---\ntype: "[[release]]"\nid: REL-0001\ntitle: "R"\nstatus: draft\n'
            f'version: "1.1.0"\nplatform: "{release_platform}"\npreparing: true\n'
            'features: []\nupdated: "2026-09-13"\n---\n\n# R\n', encoding="utf-8")
    (docs / "releases" / "ledgers" / "WORKING-android.json").write_text(
        json.dumps({"platform": "android", "entries": [
            {"check": "TST-0001", "date": "2026-09-13", "mark": "pass",
             "by": "user:edwin", "method": "manual"},
        ]}), encoding="utf-8")
    (docs / "releases" / "ledgers" / "WORKING-ios.json").write_text(
        json.dumps({"platform": "ios", "entries": []}), encoding="utf-8")
    return docs


def _spin_up(docs: Path):
    server = DocsServer(docs_root=docs, bind="127.0.0.1", port=0)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0),
        _make_handler(server.docs_root, server.index, server.bus,
                      cockpit_state=server.cockpit_state),
    )
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd.server_address[1], httpd


def _get(port: int, query: str = "") -> tuple[int, Any]:
    url = f"http://127.0.0.1:{port}/api/cockpit/walk{query}"
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


def _ids(payload: dict) -> list[str]:
    rows = [r for s in payload["sittings"] for r in s["rows"]]
    rows.extend(payload["unplaced"])
    return [r["id"] for r in rows]


def test_a_named_platform_serves_its_owed_rows(tmp_path: Path) -> None:
    port, httpd = _spin_up(_docs(tmp_path))
    try:
        status, payload = _get(port, "?platform=android")
        assert status == 200
        assert payload["platform"] == "android"
        assert _ids(payload) == ["TST-0002"]
        #: iOS has cleared nothing, so it owes both.
        _, ios = _get(port, "?platform=ios")
        assert _ids(ios) == ["TST-0001", "TST-0002"]
    finally:
        httpd.shutdown()


def test_an_absent_platform_asks_the_open_release(tmp_path: Path) -> None:
    """The same defaulting rule `/api/cockpit/acceptance` uses ([[ISS-0289]]),
    so a client that sends no parameter gets the walk for the release it is
    preparing rather than for whichever ledger sorts first."""
    port, httpd = _spin_up(_docs(tmp_path, release_platform="ios"))
    try:
        status, payload = _get(port)
        assert status == 200
        assert payload["platform"] == "ios"
    finally:
        httpd.shutdown()


def test_all_is_refused(tmp_path: Path) -> None:
    """A union walk would ask a walker to tick a check for a platform they are
    not holding, so the route refuses rather than answering."""
    port, httpd = _spin_up(_docs(tmp_path))
    try:
        status, payload = _get(port, "?platform=all")
        assert status == 400
        assert payload["ok"] is False
        assert "one platform" in payload["error"]
        assert payload["platforms"] == ["android", "ios"]
    finally:
        httpd.shutdown()


def test_an_unknown_platform_is_refused_not_answered(tmp_path: Path) -> None:
    """The failure this guard exists for: a mistyped name reads no ledger, so
    every check in the repo comes back owed with nothing saying why."""
    port, httpd = _spin_up(_docs(tmp_path))
    try:
        status, payload = _get(port, "?platform=andriod")
        assert status == 400
        assert "andriod" in payload["error"]
        assert payload["platforms"] == ["android", "ios"]
    finally:
        httpd.shutdown()


def test_the_release_id_is_carried_through(tmp_path: Path) -> None:
    port, httpd = _spin_up(_docs(tmp_path))
    try:
        _, payload = _get(port, "?platform=android&release=REL-0001")
        assert payload["release"] == "REL-0001"
    finally:
        httpd.shutdown()


def test_a_repo_with_one_ledger_and_no_release_still_walks(tmp_path: Path) -> None:
    """No draft release to ask, one ledger to read: the walk is that one rather
    than a refusal a reader cannot act on."""
    docs = _docs(tmp_path, release_platform=None)
    (docs / "releases" / "ledgers" / "WORKING-ios.json").unlink()
    port, httpd = _spin_up(docs)
    try:
        status, payload = _get(port)
        assert status == 200
        assert payload["platform"] == "android"
    finally:
        httpd.shutdown()
