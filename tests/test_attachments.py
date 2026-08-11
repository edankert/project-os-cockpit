"""Evidence is a file in the record, not a screenshot on one machine (TASK-0297).

`REQ-0028` exists because PHASE-022 ran twelve acceptance rounds whose only
witness record was a chat transcript. A capture that lives in `inbox/` — which
is gitignored staging for material nobody has decided about — is the same
failure one layer down: a witness with no artifact.

So captures land under `docs/attachments/<NOTE-ID>/` and are committed. The
`/docs/<path>` route already serves anything under `docs/` and the renderer
already rewrites image sources, so the picture renders with no new read path.
"""

from __future__ import annotations

import base64
import struct
import zlib
from pathlib import Path

import pytest

from project_os_cockpit import note_writes
from project_os_cockpit.index import Index


def _png(width: int = 1, height: int = 1) -> bytes:
    """A real, minimal PNG — the magic check must be exercised by a true one."""
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + b"\xff\x00\x00" * width for _ in range(height))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


@pytest.fixture()
def docs(tmp_path: Path) -> Path:
    d = tmp_path / "docs"
    (d / "issues").mkdir(parents=True)
    (d / "issues" / "ISS-9001-X.md").write_text(
        '---\ntype: "[[issue]]"\nid: ISS-9001\naliases: ["ISS-9001"]\n'
        'title: "X"\nstatus: triage\n---\n\n# X\n', encoding="utf-8",
    )
    return d


def test_a_capture_lands_in_the_record_and_cites_itself(docs: Path) -> None:
    result = note_writes.attach_capture(
        Index.build(docs), docs, "ISS-9001",
        png_base64=base64.b64encode(_png()).decode(), caption="the refusal",
    )
    stored = docs / result["rel"]
    assert stored.exists() and stored.read_bytes().startswith(b"\x89PNG")
    assert result["rel"].startswith("attachments/ISS-9001/")
    # The markdown is returned ready to paste — the citation is the point, not
    # the file: an attachment nobody links to is a file in a folder.
    assert result["markdown"] == f'![the refusal](/docs/{result["rel"]})'
    assert result["url"] == f'/docs/{result["rel"]}'


def test_captures_on_the_same_day_do_not_overwrite(docs: Path) -> None:
    index = Index.build(docs)
    b64 = base64.b64encode(_png()).decode()
    first = note_writes.attach_capture(index, docs, "ISS-9001", png_base64=b64)
    second = note_writes.attach_capture(index, docs, "ISS-9001", png_base64=b64)
    assert first["rel"] != second["rel"], "the second capture replaced the first"
    assert (docs / first["rel"]).exists() and (docs / second["rel"]).exists()


def test_a_note_that_does_not_exist_gets_no_directory(docs: Path) -> None:
    """Evidence for an id nobody allocated creates a folder the record cannot
    explain."""
    with pytest.raises(note_writes.WriteError):
        note_writes.attach_capture(
            Index.build(docs), docs, "ISS-9999",
            png_base64=base64.b64encode(_png()).decode(),
        )
    assert not (docs / "attachments" / "ISS-9999").exists()


def test_only_a_png_is_stored(docs: Path) -> None:
    """The renderer emits an `<img>` for whatever is here; serving an arbitrary
    uploaded byte stream out of the docs tree is a different feature with a
    different threat model."""
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.attach_capture(
            Index.build(docs), docs, "ISS-9001",
            png_base64=base64.b64encode(b"GIF89a not a png").decode(),
        )
    assert "not a PNG" in exc.value.message


def test_malformed_base64_is_refused_rather_than_written(docs: Path) -> None:
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.attach_capture(
            Index.build(docs), docs, "ISS-9001", png_base64="not base64 !!!",
        )
    assert "base64" in exc.value.message
    assert not (docs / "attachments").exists()


def test_a_data_uri_prefix_is_accepted(docs: Path) -> None:
    """The renderer's capture bridge hands back a data URI; making the caller
    strip it is the kind of detail that gets got wrong once per call site."""
    uri = "data:image/png;base64," + base64.b64encode(_png()).decode()
    result = note_writes.attach_capture(Index.build(docs), docs, "ISS-9001", png_base64=uri)
    assert (docs / result["rel"]).read_bytes().startswith(b"\x89PNG")


def test_an_oversized_capture_is_refused(docs: Path) -> None:
    """Git history cannot forget a large blob by deleting the file later."""
    big = b"\x89PNG\r\n\x1a\n" + b"\x00" * (note_writes.MAX_ATTACHMENT_BYTES + 1)
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.attach_capture(
            Index.build(docs), docs, "ISS-9001",
            png_base64=base64.b64encode(big).decode(),
        )
    assert exc.value.status == 413


def test_the_id_cannot_escape_the_attachments_directory(docs: Path) -> None:
    """`../` in an id must not become a path."""
    with pytest.raises(note_writes.WriteError):
        note_writes.attach_capture(
            Index.build(docs), docs, "../../etc/passwd",
            png_base64=base64.b64encode(_png()).decode(),
        )


def test_the_attach_endpoint_is_guarded() -> None:
    src = (
        Path(__file__).resolve().parents[1]
        / "src" / "project_os_cockpit" / "server.py"
    ).read_text(encoding="utf-8")
    assert '"/api/notes/attach"' in src
    handler = src.split("def _serve_note_attach")[1].split("\n        def ")[0]
    assert "_require_loopback" in handler, "attachments write to docs/ unguarded"


def test_a_staged_capture_is_refiled_and_leaves_staging(tmp_path: Path) -> None:
    """The desktop bridge writes to `inbox/`; filing it means moving it OUT.

    `inbox/`'s success condition is being empty (LIFECYCLE.md), so a capture
    that stayed there after being cited would be evidence in two places, one of
    them gitignored.
    """
    import json
    import threading
    import urllib.request
    from project_os_cockpit.server import DocsServer, _NoDNSThreadingHTTPServer, _make_handler

    root = tmp_path / "proj"
    docs = root / "docs" / "issues"
    docs.mkdir(parents=True)
    (docs / "ISS-9001-X.md").write_text(
        '---\ntype: "[[issue]]"\nid: ISS-9001\naliases: ["ISS-9001"]\n'
        'title: "X"\nstatus: triage\n---\n\n# X\n', encoding="utf-8",
    )
    (root / "SNAPSHOT.yaml").write_text("project: demo\n", encoding="utf-8")
    inbox = root / "inbox"
    inbox.mkdir()
    staged = inbox / "2026-08-11-screenshot.png"
    staged.write_bytes(_png())

    server = DocsServer(docs_root=root / "docs", bind="127.0.0.1", port=0)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0),
        _make_handler(server.docs_root, server.index, server.bus,
                      cockpit_state=server.cockpit_state,
                      agent_tracker=server.agent_tracker),
    )
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/notes/attach",
            data=json.dumps({"id": "ISS-9001", "inbox_name": staged.name}).encode(),
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            body = json.load(resp)
    finally:
        httpd.shutdown()

    assert body["ok"] is True, body
    rel = body["result"]["rel"]
    assert (root / "docs" / rel).read_bytes().startswith(b"\x89PNG")
    assert not staged.exists(), "the capture stayed in gitignored staging after being filed"
    assert body["result"]["staged_removed"] is True


def test_a_staged_name_cannot_escape_the_inbox(tmp_path: Path) -> None:
    """A name arriving from a renderer must not be able to read an arbitrary path."""
    import json
    import threading
    import urllib.request
    import urllib.error
    from project_os_cockpit.server import DocsServer, _NoDNSThreadingHTTPServer, _make_handler

    root = tmp_path / "proj"
    (root / "docs" / "issues").mkdir(parents=True)
    (root / "docs" / "issues" / "ISS-9001-X.md").write_text(
        '---\ntype: "[[issue]]"\nid: ISS-9001\naliases: ["ISS-9001"]\n'
        'title: "X"\nstatus: triage\n---\n\n# X\n', encoding="utf-8",
    )
    (root / "SNAPSHOT.yaml").write_text("project: demo\n", encoding="utf-8")
    (root / "inbox").mkdir()
    secret = root / "secret.png"
    secret.write_bytes(_png())

    server = DocsServer(docs_root=root / "docs", bind="127.0.0.1", port=0)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0),
        _make_handler(server.docs_root, server.index, server.bus,
                      cockpit_state=server.cockpit_state,
                      agent_tracker=server.agent_tracker),
    )
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/notes/attach",
            data=json.dumps({"id": "ISS-9001", "inbox_name": "../secret.png"}).encode(),
            headers={"Content-Type": "application/json"}, method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                body = json.load(resp)
        except urllib.error.HTTPError as exc:
            body = json.loads(exc.read().decode())
    finally:
        httpd.shutdown()

    assert body["ok"] is False, "a traversing name was accepted"
    assert secret.exists(), "the file outside inbox/ was consumed"
