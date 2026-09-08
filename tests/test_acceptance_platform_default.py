"""An absent platform asks the open release; `all` still means every one ([[ISS-0289]]).

Two requests used to arrive identically at the endpoint — a person choosing
**All**, and a client that never sent the parameter — and both got the union
rule, where a check clears only where every platform with a ledger cleared it.

Both of the renderer's callers are the second kind (`mountReleaseGate`,
`renderChecksPage`), so on `../your-trainer` the Tests page and the gate band
read **544 unchecked** while its open Android release owed 67.

Two ledgers in the fixture, because the union over one ledger is that ledger and
a single-platform repo cannot tell these apart.
"""

from __future__ import annotations

import json
import threading
import urllib.request
from pathlib import Path
from typing import Any

from project_os_cockpit.server import (
    DocsServer,
    _NoDNSThreadingHTTPServer,
    _make_handler,
)


def _docs(tmp_path: Path, *, release_platform: str | None = "android") -> Path:
    """One done feature, two checks, both walked on Android and neither on iOS."""
    docs = tmp_path / "docs"
    (docs / "tests" / "acceptance").mkdir(parents=True)
    (docs / "features").mkdir(parents=True)
    (docs / "releases" / "ledgers").mkdir(parents=True)

    (docs / "features" / "FEAT-0001-Thing.md").write_text(
        '---\ntype: "[[feature]]"\nid: FEAT-0001\ntitle: "Thing"\n'
        'status: done\n---\n\n# Thing\n', encoding="utf-8")
    for n in ("0001", "0002"):
        (docs / "tests" / "acceptance" / f"TST-{n}-C.md").write_text(
            f'---\ntype: "[[test]]"\nid: TST-{n}\ntitle: "C {n}"\n'
            'level: acceptance\nstatus: active\narea: "A"\nmark: todo\n'
            'covers: ["[[FEAT-0001]]"]\n---\n\n# C\n', encoding="utf-8")

    if release_platform is not None:
        (docs / "releases" / "REL-0001-R.md").write_text(
            '---\ntype: "[[release]]"\nid: REL-0001\ntitle: "R"\nstatus: draft\n'
            f'version: "1.1.0"\nplatform: "{release_platform}"\npreparing: true\n'
            'features: []\nupdated: "2026-09-08"\n---\n\n# R\n', encoding="utf-8")

    (docs / "releases" / "ledgers" / "WORKING-android.json").write_text(
        json.dumps({"platform": "android", "entries": [
            {"check": "TST-0001", "date": "2026-09-08", "mark": "pass",
             "by": "user:edwin", "method": "manual"},
            {"check": "TST-0002", "date": "2026-09-08", "mark": "pass",
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


def _blocking(port: int, query: str = "") -> list[str]:
    url = f"http://127.0.0.1:{port}/api/cockpit/acceptance{query}"
    with urllib.request.urlopen(url, timeout=5) as r:
        payload: Any = json.loads(r.read())
    return sorted(row["id"] for row in (payload["gate"]["blocking"] or []))


def test_no_platform_parameter_grades_on_the_open_release(tmp_path: Path) -> None:
    """The regression. The renderer sends no query string at all, and the open
    release ships Android, where both checks passed — so nothing blocks."""
    port, httpd = _spin_up(_docs(tmp_path))
    try:
        assert _blocking(port) == []
    finally:
        httpd.shutdown()


def test_all_is_still_the_union(tmp_path: Path) -> None:
    """A person who chose **All** asked for every platform and gets it. iOS has
    walked neither check, so both are owed — the fail-closed rule, unspent."""
    port, httpd = _spin_up(_docs(tmp_path))
    try:
        assert _blocking(port, "?platform=all") == ["TST-0001", "TST-0002"]
    finally:
        httpd.shutdown()


def test_an_explicit_platform_beats_the_open_release(tmp_path: Path) -> None:
    """Asking for iOS while an Android release is open answers about iOS. The
    default is a fallback, never an override."""
    port, httpd = _spin_up(_docs(tmp_path))
    try:
        assert _blocking(port, "?platform=ios") == ["TST-0001", "TST-0002"]
    finally:
        httpd.shutdown()


def test_no_open_release_falls_back_to_the_union(tmp_path: Path) -> None:
    """Nothing to ask, so nothing is assumed. A repo mid-cycle must not inherit
    the loosest platform's answer because a release note is missing."""
    port, httpd = _spin_up(_docs(tmp_path, release_platform=None))
    try:
        assert _blocking(port) == ["TST-0001", "TST-0002"]
    finally:
        httpd.shutdown()
