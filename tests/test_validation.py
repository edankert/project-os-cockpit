"""Validation health endpoint + runner (FEAT-0018 / TASK-0111).

Covers:
- report-line parsing (`ERROR [CODE] msg` / `WARN  [CODE] msg`) with
  ID + repo-relative-path extraction;
- validator locate order (repo copy preferred, bundled copy fallback);
- `GET /api/cockpit/validation` wire shapes for all three states:
  `ok` (clean repo), `failing` (induced snapshot↔note status drift,
  with a deep-link `url` per error), `unavailable` (no SNAPSHOT.yaml —
  validator exit 2);
- ok→failing flip through `ValidationRunner.refresh()` (the cache the
  endpoint serves);
- debounced re-run + `cockpit:validation` SSE fan-out when a docs file
  event arrives on the shared bus;
- no duplicate SSE when the observable result is unchanged.

The badge / drift-panel UI (TASK-0112) and the waiver/verdict/adequacy
chips (TASK-0113) consume these payloads; the payload flags for
TASK-0113 are covered in `test_validation_flags_on_nav_items` below.
"""

from __future__ import annotations

import json
import shutil
import socket
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

from project_os_cockpit import cockpit, templates
from project_os_cockpit.events import EventBus, FileEvent
from project_os_cockpit.index import Index
from project_os_cockpit.server import (
    CockpitState,
    _NoDNSThreadingHTTPServer,
    _make_handler,
)
from project_os_cockpit.validation import (
    BUNDLED_VALIDATOR,
    ValidationRunner,
    parse_report_lines,
)


NOTE_REL = "features/sample/FEAT-0001-Sample.md"


def _make_repo(tmp_path: Path, *, with_snapshot: bool = True) -> tuple[Path, Path]:
    """A minimal project-os repo the validator accepts cleanly."""
    root = tmp_path / "repo"
    docs = root / "docs"
    note = docs / NOTE_REL
    note.parent.mkdir(parents=True)
    note.write_text(
        '---\n'
        'type: "[[feature]]"\n'
        'id: FEAT-0001\n'
        'title: "Sample feature"\n'
        'status: backlog\n'
        '---\n'
        '\n'
        '# Sample feature\n',
        encoding="utf-8",
    )
    if with_snapshot:
        (root / "SNAPSHOT.yaml").write_text(
            'version: 1\n'
            'updated: "2026-07-17T00:00Z"\n'
            'counters:\n'
            '  FEAT: 1\n'
            'focus:\n'
            '  feature: "FEAT-0001"\n'
            'items:\n'
            '  features:\n'
            '    FEAT-0001:\n'
            '      title: "Sample feature"\n'
            '      status: backlog\n'
            f'      file: "docs/{NOTE_REL}"\n',
            encoding="utf-8",
        )
    return root, docs


def _induce_status_drift(docs: Path) -> None:
    """Note says done, snapshot says backlog → ITEM-STATUS error."""
    note = docs / NOTE_REL
    note.write_text(
        note.read_text(encoding="utf-8").replace(
            "status: backlog", "status: done"
        ),
        encoding="utf-8",
    )


def _spin_up(docs: Path, runner: ValidationRunner | None = None):
    """Handler + HTTP server around a docs root (no DocsServer — the
    collaborators are built directly so tests control the runner)."""
    docs = docs.resolve()
    bus = EventBus()
    index = Index.build(docs)
    if runner is not None:
        bus.subscribe(runner.on_event)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0),
        _make_handler(
            docs, index, bus,
            cockpit_state=CockpitState(),
            validation_runner=runner,
        ),
    )
    port = httpd.server_address[1]
    th = threading.Thread(target=httpd.serve_forever, daemon=True)
    th.start()
    return bus, index, httpd, port


def _get_validation(port: int) -> tuple[int, dict[str, str], dict]:
    url = f"http://127.0.0.1:{port}/api/cockpit/validation"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return (
                resp.status,
                {k: v for k, v in resp.getheaders()},
                json.loads(resp.read()),
            )
    except urllib.error.HTTPError as exc:
        return exc.code, {k: v for k, v in exc.headers.items()}, json.loads(exc.read())


# ---- unit: report parsing ----

def test_parse_report_lines_shapes() -> None:
    stdout = (
        "ERROR [ITEM-STATUS] FEAT-0001 status drift: snapshot=backlog "
        "note=done (docs/features/sample/FEAT-0001-Sample.md)\n"
        "ERROR [SNAP-KEYS] SNAPSHOT.yaml missing required top-level key: counters\n"
        "WARN  [PATH-ALIAS] 2 item(s) use legacy `path:` instead of `file:` "
        "(e.g. FEAT-0003); prefer `file:` per SNAPSHOT.md\n"
        "validate-docs: FAIL (2 errors)\n"
    )
    errors, warnings = parse_report_lines(stdout)
    assert len(errors) == 2
    assert errors[0]["code"] == "ITEM-STATUS"
    assert errors[0]["id"] == "FEAT-0001"
    assert errors[0]["rel"] == "docs/features/sample/FEAT-0001-Sample.md"
    assert "status drift" in errors[0]["message"]
    # No ID / path in the message → explicit None, not a bogus match.
    assert errors[1]["id"] is None
    assert errors[1]["rel"] is None
    assert len(warnings) == 1
    assert warnings[0]["code"] == "PATH-ALIAS"
    assert warnings[0]["id"] == "FEAT-0003"


# ---- unit: locate order ----

def test_locate_prefers_repo_copy_then_bundled(tmp_path: Path) -> None:
    root, _docs = _make_repo(tmp_path)
    runner = ValidationRunner(root)
    # No repo copy → bundled fallback.
    assert runner.locate_validator() == BUNDLED_VALIDATOR
    # Repo copy appears → it wins.
    repo_copy = root / "tools" / "scripts" / "validate-docs.py"
    repo_copy.parent.mkdir(parents=True)
    shutil.copy(BUNDLED_VALIDATOR, repo_copy)
    assert runner.locate_validator() == repo_copy


# ---- wire: the three states ----

def test_endpoint_ok_state(tmp_path: Path) -> None:
    _root, docs = _make_repo(tmp_path)
    _bus, _index, httpd, port = _spin_up(docs)
    try:
        status, headers, body = _get_validation(port)
        assert status == 200
        assert headers["X-Cockpit-Schema"] == str(cockpit.SCHEMA_VERSION)
        assert body["ok"] is True
        assert body["state"] == "ok"
        assert body["errors"] == []
        assert body["warnings"] == []
        assert body["checked_at"]
        assert body["schema_version"] == cockpit.SCHEMA_VERSION
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_endpoint_reports_drift_with_deep_link(tmp_path: Path) -> None:
    _root, docs = _make_repo(tmp_path)
    _induce_status_drift(docs)
    _bus, _index, httpd, port = _spin_up(docs)
    try:
        status, _headers, body = _get_validation(port)
        assert status == 200
        assert body["ok"] is False
        assert body["state"] == "failing"
        assert body["errors"], "expected at least one violation"
        drift = [e for e in body["errors"] if e["code"] == "ITEM-STATUS"]
        assert drift, f"no ITEM-STATUS error in {body['errors']}"
        entry = drift[0]
        assert entry["id"] == "FEAT-0001"
        assert entry["rel"] == f"docs/{NOTE_REL}"
        # Deep link resolved via the existing index resolver (TASK-0112).
        assert entry["url"] == f"/docs/{NOTE_REL}"
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_endpoint_unavailable_without_snapshot(tmp_path: Path) -> None:
    _root, docs = _make_repo(tmp_path, with_snapshot=False)
    _bus, _index, httpd, port = _spin_up(docs)
    try:
        status, _headers, body = _get_validation(port)
        assert status == 200
        assert body["ok"] is False
        assert body["state"] == "unavailable"
        assert body["errors"] == []
        assert body.get("detail")
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_refresh_flips_ok_to_failing(tmp_path: Path) -> None:
    root, docs = _make_repo(tmp_path)
    runner = ValidationRunner(root)
    _bus, index, httpd, port = _spin_up(docs, runner)
    runner._resolver = index.resolve  # deep links via the shared index
    try:
        _status, _headers, body = _get_validation(port)
        assert body["state"] == "ok"
        _induce_status_drift(docs)
        runner.refresh()
        _status, _headers, body = _get_validation(port)
        assert body["state"] == "failing"
        assert any(e["code"] == "ITEM-STATUS" for e in body["errors"])
    finally:
        httpd.shutdown()
        httpd.server_close()


# ---- SSE fan-out on watcher events ----

def _open_sse(port: int) -> tuple[socket.socket, bytes]:
    sock = socket.create_connection(("127.0.0.1", port), timeout=3)
    sock.sendall(
        b"GET /_events HTTP/1.1\r\n"
        b"Host: 127.0.0.1\r\n"
        b"Accept: text/event-stream\r\n"
        b"Connection: keep-alive\r\n"
        b"\r\n"
    )
    sock.settimeout(3)
    buf = b""
    while b"\r\n\r\n" not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            raise AssertionError("SSE socket closed before headers")
        buf += chunk
    _headers, body_start = buf.split(b"\r\n\r\n", 1)
    return sock, body_start


def _wait_for_event(
    sock: socket.socket, body_buffer: bytes, event_name: str,
    timeout: float = 6.0,
) -> str | None:
    deadline = time.time() + timeout
    buffer = body_buffer
    while time.time() < deadline:
        text = buffer.decode("utf-8", errors="replace")
        marker = f"event: {event_name}\n"
        idx = text.find(marker)
        if idx >= 0:
            after = text[idx + len(marker):]
            for line in after.split("\n"):
                if line.startswith("data: "):
                    return line[len("data: "):]
                if line == "":
                    return ""
        try:
            sock.settimeout(max(0.1, deadline - time.time()))
            chunk = sock.recv(4096)
        except socket.timeout:
            break
        if not chunk:
            break
        buffer += chunk
    return None


def test_file_event_triggers_debounced_rerun_and_sse(tmp_path: Path) -> None:
    root, docs = _make_repo(tmp_path)
    runner = ValidationRunner(root, debounce_seconds=0.05)
    bus, index, httpd, port = _spin_up(docs, runner)
    runner._bus = bus
    runner._resolver = index.resolve
    try:
        runner.refresh()  # seed cache while the repo is clean
        sock, body_start = _open_sse(port)
        try:
            _induce_status_drift(docs)
            # Simulate the docs watcher's publish for the edited note —
            # the runner is subscribed to the same bus the watcher feeds.
            bus.publish(FileEvent(
                kind="modified",
                rel_path=NOTE_REL,
                abs_path=docs / NOTE_REL,
            ))
            data = _wait_for_event(sock, body_start, "cockpit:validation")
            assert data is not None, "no cockpit:validation SSE within timeout"
            payload = json.loads(data)
            assert payload["state"] == "failing"
            assert any(e["code"] == "ITEM-STATUS" for e in payload["errors"])
        finally:
            sock.close()
    finally:
        runner.stop()
        httpd.shutdown()
        httpd.server_close()


def test_no_sse_when_result_unchanged(tmp_path: Path) -> None:
    root, _docs = _make_repo(tmp_path)
    bus = EventBus()
    seen: list = []
    bus.subscribe(seen.append)
    runner = ValidationRunner(root, bus)
    runner.refresh()   # first result always publishes (no previous state)
    runner.refresh()   # identical result → no second event
    events = [e for e in seen if getattr(e, "event_type", "") == "cockpit:validation"]
    assert len(events) == 1


def test_debounce_coalesces_bursts(tmp_path: Path) -> None:
    """A burst of schedule() calls collapses into ONE validator run —
    each call must cancel the pending timer (TASK-0111 "debounced")."""
    root, _docs = _make_repo(tmp_path)
    runner = ValidationRunner(root, debounce_seconds=0.15)
    runs: list[int] = []
    orig_run = runner._run_validator

    def counted_run():
        runs.append(1)
        return orig_run()

    runner._run_validator = counted_run  # type: ignore[method-assign]
    try:
        for _ in range(5):
            runner.schedule()
            time.sleep(0.01)
        deadline = time.time() + 3.0
        while not runs and time.time() < deadline:
            time.sleep(0.05)
        time.sleep(0.4)  # window for any (buggy) extra timers to fire
        assert len(runs) == 1, f"burst produced {len(runs)} runs, expected 1"
    finally:
        runner.stop()


# ---- TASK-0113: verification flags on nav/context item payloads ----

def test_validation_flags_on_nav_items(tmp_path: Path) -> None:
    """`_verification_flags` rides nav items: waived / review_verdict on
    any note, adequacy presence on `test` notes."""
    root, docs = _make_repo(tmp_path)
    waived = docs / "features" / "sample" / "FEAT-0002-Waived.md"
    waived.write_text(
        '---\n'
        'type: "[[feature]]"\n'
        'id: FEAT-0002\n'
        'title: "Waived feature"\n'
        'status: done\n'
        'verification_waiver: "manual-only surface, reviewed 2026-07-17"\n'
        'review_verdict: approved\n'
        '---\n\n# Waived feature\n',
        encoding="utf-8",
    )
    tests_dir = docs / "tests"
    tests_dir.mkdir()
    (tests_dir / "TST-0001-With-Evidence.md").write_text(
        '---\n'
        'type: "[[test]]"\n'
        'id: TST-0001\n'
        'title: "Guarded"\n'
        'status: passing\n'
        'adequacy: "mutation run 2026-07-17: 4/4 killed"\n'
        '---\n\n# Guarded\n',
        encoding="utf-8",
    )
    (tests_dir / "TST-0002-No-Evidence.md").write_text(
        '---\n'
        'type: "[[test]]"\n'
        'id: TST-0002\n'
        'title: "Unguarded"\n'
        'status: passing\n'
        '---\n\n# Unguarded\n',
        encoding="utf-8",
    )
    index = Index.build(docs.resolve())
    payload = cockpit.nav_payload(index, mode="features")
    items = [
        it
        for g in payload["groups"]
        for it in g.get("items", [])
    ]
    by_id = {it["id"]: it for it in items if it.get("id")}
    assert by_id["FEAT-0002"]["waived"] is True
    assert by_id["FEAT-0002"]["review_verdict"] == "approved"
    assert "waived" not in by_id["FEAT-0001"]
    assert "review_verdict" not in by_id["FEAT-0001"]

    lib = cockpit.nav_payload(index, mode="library")

    def _walk(groups):
        for g in groups:
            for it in g.get("items", []):
                yield it
            yield from _walk(g.get("subgroups", []))

    tst = {it["id"]: it for it in _walk(lib["groups"]) if it.get("id")}
    assert tst["TST-0001"]["adequacy"] is True
    assert tst["TST-0002"]["adequacy"] is False


# ---- TASK-0113: metadata-strip chip rendering (templates.py) ----

def test_metadata_strip_renders_waiver_and_verdict_chips() -> None:
    """The strip appends the amber waiver chip next to the status chip,
    keeps the waiver row's reason text, and renders review_verdict as a
    data-verdict chip (green approved / red changes-requested via CSS)."""
    html = templates._metadata_strip_html(
        {
            "status": "done",
            "verification_waiver": "manual-only surface, reviewed 2026-07-17",
            "review_verdict": "approved",
        },
        None,
    )
    # Status dd carries the status chip immediately followed by the waiver chip.
    assert '<span class="status-chip" data-status="done">done</span> ' in html
    assert html.count('class="waiver-chip"') == 2  # next to status + waiver row
    assert "manual-only surface, reviewed 2026-07-17" in html
    assert '<span class="verdict-chip" data-verdict="approved">approved</span>' in html

    html2 = templates._metadata_strip_html(
        {"status": "done", "review_verdict": "changes-requested"}, None
    )
    # No waiver → no waiver chip anywhere.
    assert "waiver-chip" not in html2
    assert 'data-verdict="changes-requested"' in html2
