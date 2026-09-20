"""HTTP-level tests for ``POST /api/notes/check-toggle``
(FEAT-0011 / TASK-0074).

Verifies the file write-back path the native renderer uses when the
user clicks a task-list checkbox: the request shape, path-traversal
guard, index lookup against the source file, and the actual on-disk
mutation.
"""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import pytest

from project_os_cockpit.server import (
    DocsServer,
    _NoDNSThreadingHTTPServer,
    _make_handler,
)


def _make_docs_with_tasks(tmp_path: Path) -> tuple[Path, Path]:
    docs = tmp_path / "docs"
    docs.mkdir()
    note = docs / "checklist.md"
    note.write_text(
        "# Checklist\n"
        "\n"
        "- [ ] alpha\n"
        "- [x] beta\n"
        "- [ ] gamma\n",
        encoding="utf-8",
    )
    return docs, note


def _spin_up(docs: Path):
    server = DocsServer(docs_root=docs, bind="127.0.0.1", port=0)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0),
        _make_handler(
            server.docs_root, server.index, server.bus,
            cockpit_state=server.cockpit_state,
        ),
    )
    port = httpd.server_address[1]
    th = threading.Thread(target=httpd.serve_forever, daemon=True)
    th.start()
    return port, httpd


def _post(port: int, body: dict[str, Any]) -> tuple[int, dict]:
    url = f"http://127.0.0.1:{port}/api/notes/check-toggle"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


# ---- Happy paths ----

def test_toggle_on(tmp_path: Path):
    docs, note = _make_docs_with_tasks(tmp_path)
    port, httpd = _spin_up(docs)
    try:
        status, body = _post(port, {
            "path": "checklist.md", "index": 0, "checked": True,
        })
        assert status == 200
        assert body == {"ok": True}
        content = note.read_text(encoding="utf-8")
        # alpha (index 0) toggled on; beta + gamma unchanged.
        assert "- [x] alpha" in content
        assert "- [x] beta" in content
        assert "- [ ] gamma" in content
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_toggle_off(tmp_path: Path):
    docs, note = _make_docs_with_tasks(tmp_path)
    port, httpd = _spin_up(docs)
    try:
        status, body = _post(port, {
            "path": "checklist.md", "index": 1, "checked": False,
        })
        assert status == 200
        assert body == {"ok": True}
        content = note.read_text(encoding="utf-8")
        assert "- [ ] alpha" in content
        assert "- [ ] beta" in content  # was [x], now [ ]
        assert "- [ ] gamma" in content
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_toggle_tolerates_docs_prefix(tmp_path: Path):
    docs, _note = _make_docs_with_tasks(tmp_path)
    port, httpd = _spin_up(docs)
    try:
        status, body = _post(port, {
            "path": "docs/checklist.md", "index": 0, "checked": True,
        })
        assert status == 200
        assert body == {"ok": True}
    finally:
        httpd.shutdown()
        httpd.server_close()


# ---- Error cases ----

def test_400_on_missing_path(tmp_path: Path):
    docs, _ = _make_docs_with_tasks(tmp_path)
    port, httpd = _spin_up(docs)
    try:
        status, body = _post(port, {"index": 0, "checked": True})
        assert status == 400
        assert body["ok"] is False
        assert "path" in body["error"].lower()
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_400_on_missing_index(tmp_path: Path):
    docs, _ = _make_docs_with_tasks(tmp_path)
    port, httpd = _spin_up(docs)
    try:
        status, body = _post(port, {"path": "checklist.md", "checked": True})
        assert status == 400
        assert body["ok"] is False
        assert "index" in body["error"].lower()
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_400_on_missing_checked(tmp_path: Path):
    docs, _ = _make_docs_with_tasks(tmp_path)
    port, httpd = _spin_up(docs)
    try:
        status, body = _post(port, {"path": "checklist.md", "index": 0})
        assert status == 400
        assert body["ok"] is False
        assert "checked" in body["error"].lower()
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_403_on_path_traversal(tmp_path: Path):
    docs, _ = _make_docs_with_tasks(tmp_path)
    port, httpd = _spin_up(docs)
    try:
        status, body = _post(port, {
            "path": "../escape.md", "index": 0, "checked": True,
        })
        assert status == 403
        assert body["ok"] is False
        assert "traversal" in body["error"].lower()
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_404_on_missing_file(tmp_path: Path):
    docs, _ = _make_docs_with_tasks(tmp_path)
    port, httpd = _spin_up(docs)
    try:
        status, body = _post(port, {
            "path": "no-such-file.md", "index": 0, "checked": True,
        })
        assert status == 404
        assert body["ok"] is False
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_404_on_out_of_range_index(tmp_path: Path):
    docs, _ = _make_docs_with_tasks(tmp_path)
    port, httpd = _spin_up(docs)
    try:
        status, body = _post(port, {
            "path": "checklist.md", "index": 99, "checked": True,
        })
        assert status == 404
        assert body["ok"] is False
        assert "index" in body["error"].lower()
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_nested_indent_tasks(tmp_path: Path):
    """Indented (nested) task-list items count toward the index too —
    the rendered DOM produces them in document order."""
    docs = tmp_path / "docs"
    docs.mkdir()
    note = docs / "nested.md"
    note.write_text(
        "- [ ] outer\n"
        "  - [ ] inner-a\n"
        "  - [x] inner-b\n"
        "- [ ] outer-2\n",
        encoding="utf-8",
    )
    port, httpd = _spin_up(docs)
    try:
        # Toggle the third checkbox (inner-b) off.
        status, _ = _post(port, {
            "path": "nested.md", "index": 2, "checked": False,
        })
        assert status == 200
        text = note.read_text(encoding="utf-8")
        assert "  - [ ] inner-b" in text
        # Others unchanged.
        assert "- [ ] outer" in text
        assert "  - [ ] inner-a" in text
        assert "- [ ] outer-2" in text
    finally:
        httpd.shutdown()
        httpd.server_close()


# ---- the position must name the same row in the page and the file ---------
# (ISS-0184)


def _make_docs_with_an_absorbed_list(tmp_path: Path) -> tuple[Path, Path]:
    """A document whose file holds five task lines and whose page draws two.

    The first list opens on the line immediately after a paragraph, with no
    blank line between. Markdown calls that lazy continuation: the list is
    absorbed into the paragraph and draws no checkbox at all, while a
    line-based reader counts every row. This is the shape the whole issue is
    about, written out rather than described.
    """
    docs = tmp_path / "docs"
    docs.mkdir()
    note = docs / "suite.md"
    note.write_text(
        "# Suite\n"
        "\n"
        "## Export gating\n"
        "\n"
        "These are the rows nobody can click:\n"
        "- [ ] absorbed one\n"
        "- [ ] absorbed two\n"
        "- [ ] absorbed three\n"
        "\n"
        "## Per-rider export\n"
        "\n"
        "- [ ] drawn one\n"
        "- [ ] drawn two\n",
        encoding="utf-8",
    )
    return docs, note


def test_a_click_is_refused_when_the_page_and_the_file_hold_different_boxes(
    tmp_path: Path,
) -> None:
    """**The reader ticks one row and a different row changes** (ISS-0184).

    On this document the page draws two checkboxes and the file holds five, so
    position 0 is "drawn one" to the reader and "absorbed one" to the server.
    Before this guard the write landed on "absorbed one" and the endpoint
    answered `{"ok": true}` — a tick the reader cannot see, on a row they were
    not looking at, reported as success.

    Asserted on the file as well as on the reply, because a refusal that still
    writes is the failure wearing a different answer.
    """
    docs, note = _make_docs_with_an_absorbed_list(tmp_path)
    before = note.read_text(encoding="utf-8")
    port, httpd = _spin_up(docs)
    try:
        status, body = _post(port, {
            "path": "suite.md", "index": 0, "checked": True,
        })
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 404, (status, body)
    assert body["ok"] is False
    assert "cannot be addressed" in body["error"], body["error"]
    assert note.read_text(encoding="utf-8") == before, (
        "the toggle was refused and wrote anyway")


def test_a_click_is_refused_when_the_text_does_not_match_the_line(
    tmp_path: Path,
) -> None:
    """The second guard: the counts agree, and the file still moved.

    A page is drawn, somebody edits the file, and the reader clicks. Position 1
    was "beta" when the page was drawn and is "inserted" now. The client sends
    the prose it is showing, so the server can see the two disagree instead of
    ticking whatever has moved into that slot.
    """
    docs, note = _make_docs_with_tasks(tmp_path)
    port, httpd = _spin_up(docs)
    try:
        status, body = _post(port, {
            "path": "checklist.md", "index": 2, "checked": True,
            "raw": "beta",
        })
        assert status == 404, (status, body)
        assert "on the page" in body["error"], body["error"]
        assert "- [ ] gamma" in note.read_text(encoding="utf-8"), (
            "the mismatched toggle wrote to gamma anyway")

        #: And the matching text writes, so the guard is not simply refusing
        #: everything — which a refusal-only assertion cannot tell apart.
        status, body = _post(port, {
            "path": "checklist.md", "index": 2, "checked": True,
            "raw": "gamma",
        })
        assert status == 200, (status, body)
        assert "- [x] gamma" in note.read_text(encoding="utf-8")
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_the_renderer_sends_the_text_it_is_showing() -> None:
    """The client half. The server's text guard can only fire on what it is
    given, so the call site that omits it is the way this fix stops working.

    Weak by itself — it reads the source — which is why it is the second guard
    here and not the only one: the count refusal above needs nothing from the
    client at all.
    """
    src = (Path(__file__).resolve().parents[1] / "desktop" / "src"
           / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    i = src.index("/api/notes/check-toggle")
    window = src[i - 600:i + 400]
    assert "tgt.dataset.raw" in window, window
    assert "{ raw }" in window, window
