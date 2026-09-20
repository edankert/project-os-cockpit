"""A write must say it is JSON, or it is refused ([[ISS-0301]]).

**The hole.** The only gate on the sidecar's write routes is
`_require_loopback`, which asks where the request came from. A page the
cockpit's viewer frames comes from this machine, so it passes. Its sandbox is
`allow-scripts` with no same-origin flag, which stops it reading the reply and
not sending the request — and the write happens either way.

What made it reachable without the person noticing is the **preflight**. A
browser sends a cross-origin POST with no permission asked first only while
its `Content-Type` is `text/plain`, `application/x-www-form-urlencoded` or
`multipart/form-data`. `_read_json_body` ignored the header entirely, so a
`text/plain` body was parsed as JSON. The reviewer demonstrated it with one
curl against a live sidecar on 2026-09-12:

    curl -X POST -H 'Content-Type: text/plain' -d '{"kind":"bogus"}' \
        .../api/cockpit/review-request
    -> unknown kind: bogus          (the body was parsed)

**What these tests are not.** This closes the no-preflight path; it is not the
whole answer. A page that sets `application/json` is preflighted, and the day
the sidecar answers a preflight this guard stops mattering. The full fix is a
secret the shell knows and a framed page does not, and it is not made here.

These tests send real requests from a loopback peer, so the loopback guard is
satisfied and the `Content-Type` refusal is the only thing that can produce
the refusal being asserted.
"""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http import HTTPStatus
from pathlib import Path

import pytest

from project_os_cockpit.server import (
    DocsServer,
    _NoDNSThreadingHTTPServer,
    _make_handler,
)

#: The route enumeration is the sibling file's, parsed from `_route_post` with
#: `ast`. Imported rather than copied: two parses of one dispatch table that
#: drift apart are worse than one, and that file explains at length why a regex
#: over the branch is not good enough.
from test_remote_peer_refusal import _split  # noqa: E402


@pytest.fixture()
def port(tmp_path: Path):
    root = tmp_path / "proj"
    docs = root / "docs"
    docs.mkdir(parents=True)
    (docs / "README.md").write_text("# Hi\n", encoding="utf-8")
    (root / "SNAPSHOT.yaml").write_text("version: 1\n", encoding="utf-8")
    server = DocsServer(docs_root=docs, bind="127.0.0.1", port=0)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0),
        _make_handler(server.docs_root, server.index, server.bus,
                      cockpit_state=server.cockpit_state,
                      agent_tracker=server.agent_tracker))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        yield httpd.server_address[1]
    finally:
        httpd.shutdown()
        httpd.server_close()


def _post(port: int, path: str, content_type: str | None) -> tuple[int, dict]:
    headers = {} if content_type is None else {"Content-Type": content_type}
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=json.dumps({"kind": "bogus"}).encode(),
        method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            return exc.code, json.loads(raw or b"{}")
        except ValueError:
            return exc.code, {"raw": raw.decode("utf-8", "replace")}


def test_the_reviewers_curl_is_refused_now(port: int) -> None:
    """The demonstration, run as itself.

    `/api/cockpit/review-request` answered *"unknown kind: bogus"* — which is
    the route reporting that it read and understood the body. It must now stop
    before that, so the assertion is on the status and on the body NOT having
    been parsed.
    """
    status, body = _post(port, "/api/cockpit/review-request", "text/plain")

    assert status == int(HTTPStatus.UNSUPPORTED_MEDIA_TYPE), (status, body)
    assert "application/json" in str(body.get("error", "")), body
    assert "bogus" not in json.dumps(body), (
        "the body was parsed before the refusal — the endpoint still read it")


def test_a_json_body_still_reaches_the_route(port: int) -> None:
    """The other side, and the reason this is not simply a closed door.

    The same request with the header the real clients send gets through to the
    route and is answered by the route. If this ever fails, every write in the
    shell, in Deck and in the CLI has stopped working.
    """
    status, body = _post(port, "/api/cockpit/review-request", "application/json")

    assert status != int(HTTPStatus.UNSUPPORTED_MEDIA_TYPE), (status, body)
    assert "bogus" in json.dumps(body), (
        "the route no longer sees the body it is meant to read: %r" % body)


@pytest.mark.parametrize("header", [
    "text/plain",
    "text/plain;charset=UTF-8",
    "application/x-www-form-urlencoded",
    "multipart/form-data; boundary=x",
    None,
])
def test_every_no_preflight_content_type_is_refused(port: int, header) -> None:
    """The three values a browser will send cross-origin without asking first,
    plus the absent header a hand-rolled `fetch` produces.

    Parametrised rather than written once on `text/plain`, because the
    exploitable set is the whole simple-request family and a guard that names
    only the one in the report is a guard against the report.
    """
    status, _ = _post(port, "/api/cockpit/review-request", header)
    assert status == int(HTTPStatus.UNSUPPORTED_MEDIA_TYPE), header


def test_a_charset_parameter_does_not_defeat_the_guard(port: int) -> None:
    """`application/json; charset=utf-8` is JSON. Some clients send it, and a
    naive equality on the raw header would refuse them — which is how a
    security guard becomes the thing someone disables."""
    status, body = _post(
        port, "/api/cockpit/review-request", "application/json; charset=utf-8")
    assert status != int(HTTPStatus.UNSUPPORTED_MEDIA_TYPE), (status, body)


def test_no_guarded_write_route_still_reads_a_plain_text_body(port: int) -> None:
    """**Every write route, not the one in the report.**

    A framed page knows its sidecar's URL from `location`, so it can address
    all of them. The guard living in `_read_json_body` is what makes this
    true for the whole set at once; a route that grew its own body reader
    would fall out of it silently, which is exactly what five routes had done
    before this change.
    """
    guarded, _open = _split()
    assert len(guarded) > 20, (
        "the route enumeration came back nearly empty; it is parsing nothing")

    leaked = []
    for path in sorted(guarded):
        status, _ = _post(port, path, "text/plain")
        if status != int(HTTPStatus.UNSUPPORTED_MEDIA_TYPE):
            leaked.append((path, status))

    assert not leaked, (
        "these write routes still read a body a browser sends cross-origin "
        "with no preflight: " + ", ".join(f"{p} -> {s}" for p, s in leaked))
