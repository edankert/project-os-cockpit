"""HTTP-level tests for ``GET /api/render`` (FEAT-0008 / TASK-0067).

Spins up the real request handler against a temp docs dir on an
ephemeral port (same pattern as the other cockpit endpoint tests in
``test_cockpit_state.py``) and exercises the contract documented in
``docs/references/COCKPIT-API.md``.
"""

from __future__ import annotations

import json
import threading
import urllib.parse
import urllib.request
from http.client import HTTPResponse
from pathlib import Path

import pytest

from project_os_cockpit.server import (
    DocsServer,
    _NoDNSThreadingHTTPServer,
    _make_handler,
)


def _spin_up(docs_dir: Path):
    """Start the handler on an ephemeral port; return (port, httpd)."""
    server = DocsServer(docs_root=docs_dir, bind="127.0.0.1", port=0)
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


def _write_sample_docs(tmp_path: Path) -> Path:
    """Create a minimal docs tree with one note + one nested folder.

    Returns the path to the docs root.
    """
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "README.md").write_text("# Hi\n\nWelcome.\n", encoding="utf-8")
    nested = docs / "features" / "sample"
    nested.mkdir(parents=True)
    (nested / "FEAT-0001-Sample.md").write_text(
        "---\n"
        "type: \"[[feature]]\"\n"
        "id: FEAT-0001\n"
        "title: \"Sample feature\"\n"
        "status: planned\n"
        "created: 2026-05-25\n"
        "---\n\n"
        "# Sample feature\n\n"
        "Some body text.\n",
        encoding="utf-8",
    )
    return docs


def _get(port: int, path: str) -> tuple[int, dict[str, str], dict]:
    """GET ``http://127.0.0.1:<port><path>``; return (status, headers, body-as-dict)."""
    url = f"http://127.0.0.1:{port}{path}"
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:  # type: HTTPResponse
            status = resp.status
            headers = {k: v for k, v in resp.getheaders()}
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        headers = {k: v for k, v in exc.headers.items()}
        raw = exc.read()
    body = json.loads(raw.decode("utf-8")) if raw else {}
    return status, headers, body


# ---- Happy path ----

def test_render_returns_html_and_metadata(tmp_path: Path):
    docs = _write_sample_docs(tmp_path)
    port, httpd = _spin_up(docs)
    try:
        rel = "features/sample/FEAT-0001-Sample.md"
        status, headers, body = _get(
            port,
            "/api/render?path=" + urllib.parse.quote(rel),
        )
        assert status == 200
        assert headers["Content-Type"].startswith("application/json")
        # Schema version is read from the constant so this test stays
        # honest across bumps (FEAT-0013's new SSE event bumped it to 3).
        from project_os_cockpit import cockpit as _ck
        assert headers["X-Cockpit-Schema"] == str(_ck.SCHEMA_VERSION)
        assert body["schema_version"] == _ck.SCHEMA_VERSION
        assert body["rel_path"] == rel
        assert body["title"] == "Sample feature"
        # Frontmatter passes through with date sanitised to a string.
        assert body["frontmatter"]["id"] == "FEAT-0001"
        assert body["frontmatter"]["status"] == "planned"
        assert body["frontmatter"]["created"] == "2026-05-25"
        # Rendered body HTML — body text is present, frontmatter isn't
        # (render_markdown_body drops the YAML block).
        assert "Some body text." in body["html"]
        assert "FEAT-0001" not in body["html"]
        # Pre-rendered metadata strip (TASK-0075) — wraps a <details>
        # with the same class mode 1 emits.
        assert "metadata-strip" in body["metadata_html"]
        assert "FEAT-0001" in body["metadata_html"]
        # Status renders as a chip rather than plain text.
        assert "status-chip" in body["metadata_html"]
        # linked / backlinks shape — empty arrays for an unconnected note.
        assert isinstance(body["linked"], list)
        assert isinstance(body["backlinks"], list)
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_render_metadata_resolves_wikilinks_and_bare_ids(tmp_path: Path):
    """`metadata_html` must turn `[[FEAT-XXXX]]` references AND bare
    `FEAT-XXXX` IDs into clickable anchors — same behaviour as
    mode 1's metadata strip (TASK-0075).
    """
    docs = tmp_path / "docs"
    docs.mkdir()
    # Two referenceable notes so the resolver has targets.
    feat_dir = docs / "features" / "alpha"
    feat_dir.mkdir(parents=True)
    (feat_dir / "FEAT-0042-Alpha.md").write_text(
        "---\nid: FEAT-0042\ntitle: Alpha\n---\n# Alpha\n",
        encoding="utf-8",
    )
    (docs / "features" / "alpha" / "TASK-0099-Beta.md").write_text(
        "---\nid: TASK-0099\ntitle: Beta\n---\n# Beta\n",
        encoding="utf-8",
    )
    # The note under test references both — wikilink form and bare ID.
    consumer = docs / "consumer.md"
    consumer.write_text(
        "---\n"
        "id: CONSUMER\n"
        "title: Consumer\n"
        "related:\n"
        "  - \"[[FEAT-0042]]\"\n"
        "  - TASK-0099\n"
        "---\n"
        "# Consumer\n",
        encoding="utf-8",
    )
    port, httpd = _spin_up(docs)
    try:
        status, _, body = _get(
            port, "/api/render?path=" + urllib.parse.quote("consumer.md"),
        )
        assert status == 200
        meta = body["metadata_html"]
        # Both reference styles should land as <a> tags pointing at
        # the resolved targets.
        assert 'href="/docs/features/alpha/FEAT-0042-Alpha.md"' in meta, meta
        assert 'href="/docs/features/alpha/TASK-0099-Beta.md"' in meta, meta
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_render_tolerates_leading_docs_prefix(tmp_path: Path):
    """The cockpit URLs use `/docs/...`; the API should accept a path
    with or without that leading segment."""
    docs = _write_sample_docs(tmp_path)
    port, httpd = _spin_up(docs)
    try:
        rel_with_prefix = "docs/features/sample/FEAT-0001-Sample.md"
        status, _, body = _get(
            port,
            "/api/render?path=" + urllib.parse.quote(rel_with_prefix),
        )
        assert status == 200
        # rel_path in the response is normalised (prefix stripped).
        assert body["rel_path"] == "features/sample/FEAT-0001-Sample.md"
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_render_handles_readme(tmp_path: Path):
    docs = _write_sample_docs(tmp_path)
    port, httpd = _spin_up(docs)
    try:
        status, _, body = _get(port, "/api/render?path=README.md")
        assert status == 200
        assert "Welcome." in body["html"]
        # No frontmatter → empty dict, fallback title from filename or H1.
        assert body["frontmatter"] == {}
        assert body["title"]  # non-empty
    finally:
        httpd.shutdown()
        httpd.server_close()


# ---- Error cases ----

def test_render_missing_path_returns_400(tmp_path: Path):
    docs = _write_sample_docs(tmp_path)
    port, httpd = _spin_up(docs)
    try:
        status, _, body = _get(port, "/api/render")
        assert status == 400
        assert body["ok"] is False
        assert "path" in body["error"].lower()
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_render_traversal_blocked(tmp_path: Path):
    docs = _write_sample_docs(tmp_path)
    port, httpd = _spin_up(docs)
    try:
        # Try to escape via ..
        status, _, body = _get(
            port,
            "/api/render?path=" + urllib.parse.quote("../secret.md"),
        )
        assert status == 403
        assert body["ok"] is False
        assert "traversal" in body["error"].lower()
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_render_404_when_file_missing(tmp_path: Path):
    docs = _write_sample_docs(tmp_path)
    port, httpd = _spin_up(docs)
    try:
        status, _, body = _get(
            port,
            "/api/render?path=" + urllib.parse.quote("does/not/exist.md"),
        )
        assert status == 404
        assert body["ok"] is False
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_render_404_when_not_markdown(tmp_path: Path):
    docs = _write_sample_docs(tmp_path)
    # Drop a non-md file in the tree.
    (docs / "image.png").write_bytes(b"\x89PNG\r\n")
    port, httpd = _spin_up(docs)
    try:
        status, _, body = _get(
            port,
            "/api/render?path=" + urllib.parse.quote("image.png"),
        )
        assert status == 404
        assert body["ok"] is False
        assert "markdown" in body["error"].lower()
    finally:
        httpd.shutdown()
        httpd.server_close()
