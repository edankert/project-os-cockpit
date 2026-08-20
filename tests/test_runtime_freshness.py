"""The sidecar can say whether it is running the code that is on disk.

ISS-0140. A sidecar is an editable install, so it needs no rebuild — but a
running process never re-imports, and the SSE soft-reload refreshes documents
rather than modules. The renderer has the same shape for a different reason:
`dist/renderer/*.js` is read once at window creation.

Neither noticed a rebuild and nothing on screen said so, which cost a false
bug report on 2026-08-10 (a stale sidecar rendering the Tests view as
Features) and a false observation on 2026-08-11 (a shell running 1 day
23 hours, showing agent chips for notes nobody had touched). Both times the
expensive part was investigating a defect that did not exist.

These drive the endpoint against a real server, because what is asserted is a
comparison between a *process* and a *filesystem*. Mocking either side would
test the arithmetic rather than the question.
"""

from __future__ import annotations

import json
import os
import threading
import time
import urllib.request
from pathlib import Path

from project_os_cockpit import server
from project_os_cockpit.server import (
    DocsServer,
    _NoDNSThreadingHTTPServer,
    _make_handler,
)


def _spin_up(docs: Path, shell_assets: Path | None = None):
    server = DocsServer(docs_root=docs, bind="127.0.0.1", port=0,
                        shell_assets=shell_assets)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0),
        _make_handler(
            server.docs_root, server.index, server.bus,
            cockpit_state=server.cockpit_state,
            shell_assets=server.shell_assets,
        ),
    )
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return port, httpd


def _runtime(port: int) -> dict:
    with urllib.request.urlopen(
        f"http://127.0.0.1:{port}/api/cockpit/runtime", timeout=3
    ) as resp:
        return json.loads(resp.read())


def _docs(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "README.md").write_text("# Docs\n", encoding="utf-8")
    return docs


def test_a_fresh_process_is_not_stale(tmp_path: Path) -> None:
    """The common case, and the one that must not cry wolf."""
    port, httpd = _spin_up(_docs(tmp_path))
    try:
        r = _runtime(port)
        assert r["sidecar_stale"] is False
        assert r["started_at"] > 0
        assert r["source_newest"] > 0
    finally:
        httpd.shutdown()


def test_source_newer_than_the_process_reads_as_stale(
        tmp_path: Path, monkeypatch) -> None:
    """The whole point: the answer is computed, not remembered.

    A `.py` under the package newer than the process start is exactly the
    condition a developer creates by editing code with the app open — and
    exactly what nothing reported until this endpoint existed.

    **Written by moving the process start, not the file** ([[ISS-0251]]).

    The first cut set the mtime of the **real** `src/project_os_cockpit/
    cockpit.py` five seconds into the future and restored it in a `finally`.
    Within one process that is safe. Across processes it is not: staleness is
    `newest .py under the package > this process's start`, so for the length of
    that window *every* sidecar running against this working tree reports
    stale — including one another pytest process has just spun up. It cost two
    red tests in a 1977-test run on 2026-08-20, both passing in isolation, in a
    repo where a red suite is a stop signal.

    That is precisely the failure this file exists to prevent. Its own opening
    docstring: *"Both times the expensive part was investigating a defect that
    did not exist."*

    The comparison has two sides and only one of them is shared. Moving
    `_PROCESS_STARTED_AT` — module state, private to this process — exercises
    the identical predicate and mutates nothing another reader can see.
    """
    port, httpd = _spin_up(_docs(tmp_path))
    try:
        #: Anything under the package's newest .py. Zero is unambiguous and
        #: needs no clock arithmetic.
        monkeypatch.setattr(server, "_PROCESS_STARTED_AT", 0.0)
        r = _runtime(port)
        assert r["sidecar_stale"] is True, (
            "a source file newer than the process must read as stale — this "
            "is the comparison ISS-0140 exists to make"
        )
        #: The domain is real: the predicate is comparing against something.
        assert r["source_newest"] > 0

        monkeypatch.setattr(server, "_PROCESS_STARTED_AT", time.time() + 60)
        assert _runtime(port)["sidecar_stale"] is False, (
            "and it must clear again: a staleness signal that latches is a "
            "signal people learn to stop seeing"
        )
    finally:
        httpd.shutdown()


def test_the_freshness_test_does_not_touch_a_shared_file() -> None:
    """[[ISS-0251]]'s guard, and the reason it is a guard rather than an edit.

    The obvious repair — keep forward-dating the file but restore it faster —
    narrows the window without closing it. The property that matters is that
    **no test in this file mutates a path outside `tmp_path`**, because this
    file's whole subject is not reporting staleness that is not there.

    **Parsed, not grepped.** The first cut searched the source text for the
    call and matched *its own docstring and its own assertion string* — the
    same over-broad-text-match this codebase has now produced eight times in
    one phase. A guard satisfied by the prose explaining it is not a guard.

    `ast` finds real call sites and cannot see a mention.
    """
    import ast

    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    calls = [
        n.lineno for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and n.func.attr == "utime"
    ]
    assert not calls, (
        "a test in this file sets an mtime (lines %s); if the target is a "
        "real source file, every concurrent reader of this working tree sees "
        "false staleness (ISS-0251)" % calls
    )


def test_assets_answer_even_when_there_are_none(tmp_path: Path) -> None:
    """No `--shell-assets` is a legitimate state, not an error.

    Standalone (`python -m project_os_cockpit docs`) has no bundle to be
    stale about. The fields still answer, so a client can tell *no assets*
    from *assets are current* without special-casing a missing key.
    """
    port, httpd = _spin_up(_docs(tmp_path))
    try:
        r = _runtime(port)
        assert isinstance(r["assets_newest"], (int, float))
        assert r["assets_dir"] == ""
        assert r["assets_newest"] == 0
    finally:
        httpd.shutdown()


def test_assets_are_reported_when_the_shell_passes_them(tmp_path: Path) -> None:
    """With a bundle, the newest asset mtime is what the client compares
    against its own window start — so it has to be real, not a placeholder."""
    assets = tmp_path / "renderer"
    assets.mkdir()
    (assets / "renderer.js").write_text("// bundle\n", encoding="utf-8")
    port, httpd = _spin_up(_docs(tmp_path), shell_assets=assets)
    try:
        r = _runtime(port)
        assert r["assets_dir"].endswith("renderer")
        assert r["assets_newest"] > 0
    finally:
        httpd.shutdown()
