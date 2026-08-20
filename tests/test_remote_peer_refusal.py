"""Every guarded POST endpoint **actually refuses** a non-loopback peer.

[[TASK-0363]] / [[REQ-0027]] / [[RISK-0001]]. The threat model in one
sentence: the render server binds `0.0.0.0` so a tablet on the Wi-Fi can
read the notes, and the only thing separating that reader from a writer is
a per-request peer check on the shared socket.

**Why a second test beside `test_every_note_mutating_endpoint_requires_loopback`.**
That one (TASK-0280) enumerates the POST dispatch and fails when a new route
forgets the guard — it is the reason a route cannot be added unnoticed, and it
stays. But it decides by *reading source text*: it asserts the substring
`_require_loopback` appears somewhere in the handler body. It would pass on a
handler that assigned the name to a variable, called it behind a condition that
is never true, or called it and ignored the result. It has never sent a request.

This file sends the requests. A route is proved by a **403 over a real socket
from a peer the server believes is remote**, which is the property REQ-0027
actually states. The two are complementary and neither subsumes the other:
delete this file and a guard can rot into a no-op; delete that one and a new
route simply never appears here.
"""

from __future__ import annotations

import ast
import json
import threading
import urllib.error
import urllib.request
from http import HTTPStatus
from pathlib import Path

import pytest

from project_os_cockpit.server import (
    DocsServer,
    _LOOPBACK_HOSTS,
    _NoDNSThreadingHTTPServer,
    _make_handler,
)

SERVER_PY = (
    Path(__file__).resolve().parents[1]
    / "src" / "project_os_cockpit" / "server.py"
)

#: Called inside dispatch branches but never the handler for one.
_DISPATCH_HELPERS = frozenset({"_drain_request_body", "_respond_status", "_respond_json"})

#: RFC 5737 TEST-NET-3 — reserved for documentation, routable nowhere.
REMOTE_PEER = "203.0.113.7"


def _post_routes() -> dict[str, str]:
    """`{path: handler}` parsed from `_route_post`'s dispatch.

    Parsed with `ast` rather than a regex: the sibling test's regex carries a
    `[\\s\\S]{0,120}?` window between the path and the call, which silently
    drops a route whose branch grows past it. Two independent parses of the
    same table also cross-check each other — they are asserted equal below.
    """
    tree = ast.parse(SERVER_PY.read_text(encoding="utf-8"))
    fn = next(
        n for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == "_route_post"
    )
    routes: dict[str, str] = {}
    for node in ast.walk(fn):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if not (isinstance(test, ast.Compare)
                and isinstance(test.comparators[0], ast.Constant)):
            continue
        path = test.comparators[0].value
        if not isinstance(path, str) or not path.startswith("/api/"):
            continue
        for call in ast.walk(node):
            #: **Any** `self.<method>()` in the branch, not only `_serve_*`.
            #: The first cut required that prefix and so did the sibling test,
            #: which meant a handler named anything else was invisible to BOTH
            #: enumerations — they could not disagree about a route they both
            #: missed. Found by review, 2026-08-20.
            if (isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Attribute)
                    and isinstance(call.func.value, ast.Name)
                    and call.func.value.id == "self"
                    and call.func.attr not in _DISPATCH_HELPERS):
                routes[path] = call.func.attr
                break
    return routes


def _handler_body(name: str) -> str:
    tree = ast.parse(SERVER_PY.read_text(encoding="utf-8"))
    fn = next(
        n for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == name
    )
    return ast.get_source_segment(SERVER_PY.read_text(encoding="utf-8"), fn) or ""


def _split() -> tuple[dict[str, str], dict[str, str]]:
    """The dispatch, partitioned into (guarded, open)."""
    guarded, open_ = {}, {}
    for path, handler in _post_routes().items():
        body = _handler_body(handler)
        (guarded if "_require_loopback" in body else open_)[path] = handler
    return guarded, open_


@pytest.fixture()
def remote_server(tmp_path):
    """A live server that believes every caller is at `REMOTE_PEER`.

    The socket is still loopback — only the *reported* peer is faked, which is
    what the guard reads. Overriding `client_address` on the handler subclass
    (rather than monkeypatching `_is_loopback`) keeps the real predicate in the
    path: `_is_loopback` still runs, still consults `_LOOPBACK_HOSTS`, and still
    decides. A test that stubs the predicate cannot catch the predicate going
    wrong.
    """
    root = tmp_path / "proj"
    docs = root / "docs"
    docs.mkdir(parents=True)
    (docs / "README.md").write_text("# Hi\n", encoding="utf-8")
    (root / "SNAPSHOT.yaml").write_text("version: 1\n", encoding="utf-8")
    server = DocsServer(docs_root=docs, bind="127.0.0.1", port=0)
    base_cls = _make_handler(
        server.docs_root, server.index, server.bus,
        cockpit_state=server.cockpit_state,
        agent_tracker=server.agent_tracker,
    )

    class RemoteHandler(base_cls):  # type: ignore[misc,valid-type]
        @property
        def client_address(self):
            return (REMOTE_PEER, 54321)

        @client_address.setter
        def client_address(self, _value):
            pass  # socketserver assigns the real peer; we keep the fake.

        def log_message(self, *_a):  # quiet
            pass

    httpd = _NoDNSThreadingHTTPServer(("127.0.0.1", 0), RemoteHandler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        httpd.shutdown()
        httpd.server_close()


def _post(base: str, path: str, payload: dict) -> tuple[int, str]:
    req = urllib.request.Request(
        base + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Connection": "close"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")


def test_the_fake_peer_is_not_in_the_loopback_set() -> None:
    """The fixture is only meaningful if the address it fakes is genuinely
    remote. Asserted against the set the predicate consults, so widening
    `_LOOPBACK_HOSTS` to something absurd fails here rather than turning every
    assertion below into a tautology.
    """
    assert REMOTE_PEER not in _LOOPBACK_HOSTS
    assert _LOOPBACK_HOSTS == frozenset({"127.0.0.1", "::1", "::ffff:127.0.0.1"})


def test_both_parses_of_the_dispatch_agree() -> None:
    """This file's `ast` walk and the sibling test's regex must see the same
    table. They are the two independent enumerations REQ-0027 rests on; if they
    diverge, one of them is missing a route and neither can say which.
    """
    import re

    src = SERVER_PY.read_text(encoding="utf-8")
    post_block = src.split("def _route_post")[1].split("\n        def ")[0]
    by_regex = {
        p for p, _ in re.findall(
            r'if path == "(/api/[^"]+)"[\s\S]{0,120}?self\.(_serve_\w+)\(',
            post_block,
        )
    }
    by_ast = set(_post_routes())
    assert by_ast == by_regex, (
        "the two enumerations of the POST dispatch disagree; "
        f"ast-only={sorted(by_ast - by_regex)} regex-only={sorted(by_regex - by_ast)}"
    )


def test_every_guarded_endpoint_refuses_a_remote_peer(remote_server) -> None:
    """**The assertion this file exists for.** Not "the guard is mentioned" —
    the guard *fires*, on every route that claims it, over a real socket.

    A 400 here would be a finding rather than a pass: it would mean the handler
    parsed a remote caller's body before deciding whether to talk to them.
    """
    guarded, open_ = _split()
    #: **An exact partition, not a floor.** The first cut asserted
    #: `len(guarded) >= 25` against an actual 27 — two routes could lose their
    #: guard and the sweep would still "pass" over a quietly smaller domain.
    #: Review, 2026-08-20.
    routes = _post_routes()
    assert set(guarded) | set(open_) == set(routes), (
        "the partition does not cover the dispatch: "
        f"{sorted(set(routes) - (set(guarded) | set(open_)))}"
    )
    assert (len(guarded), len(open_)) == (27, 5), (
        f"the dispatch split moved: {len(guarded)} guarded / {len(open_)} open. "
        "That is not automatically wrong — but it must be a deliberate edit here."
    )

    wrong: list[tuple[str, int, str]] = []
    for path in sorted(guarded):
        status, body = _post(remote_server, path, {})
        if status != HTTPStatus.FORBIDDEN:
            wrong.append((path, status, body[:120]))
    assert not wrong, (
        "these endpoints did NOT refuse a non-loopback peer "
        f"(expected {int(HTTPStatus.FORBIDDEN)}): {wrong}"
    )


def test_no_guard_call_has_its_answer_discarded() -> None:
    """**The failure mode this file's docstring named and did not catch.**

    Found by independent review, 2026-08-20. Change one handler from

        if not self._require_loopback():
            return

    to a bare `self._require_loopback()` and the guard still *fires* — the peer
    at `203.0.113.7` still receives `403 mutations are loopback-only` — and the
    handler carries on and **writes the note anyway**. Refusal real, write real.
    All eight tests here passed, the sibling passed, all 1965 passed.

    Why every dynamic assertion missed it: they all read a **status code**, and
    `_require_loopback` responds *before* returning `False`, so the 403 is
    already on the wire by the time its answer is thrown away. [[REQ-0027]] is
    about the write, not the reply — and I had been asserting the reply.

    So this is a **different question and therefore a different predicate**
    ([[REQ-0059]]): not *"does the guard fire?"* but *"is its answer used?"*.
    Answered statically, because it is a property of the code rather than of a
    request: a call whose value is discarded is an `ast.Expr` wrapping the
    call, and there is no other way to spell it.

    Enumerated over every call site, so a new handler is in this domain the
    moment it is written.
    """
    tree = ast.parse(SERVER_PY.read_text(encoding="utf-8"))
    discarded = [
        n.lineno for n in ast.walk(tree)
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
        and isinstance(n.value.func, ast.Attribute)
        and n.value.func.attr == "_require_loopback"
    ]
    assert not discarded, (
        "these `_require_loopback()` calls throw their answer away, so the "
        f"handler refuses the caller and then writes anyway — server.py lines {discarded}"
    )
    #: And the domain is non-empty, so the assertion above cannot pass by
    #: having nothing to look at.
    sites = sum(
        1 for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and n.func.attr == "_require_loopback"
    )
    assert sites == 27, f"expected 27 guard call sites, found {sites}"


def test_the_refusal_says_why(remote_server) -> None:
    """The 403 carries the documented reason, so a LAN reader who hits one gets
    an explanation rather than a bare status.
    """
    guarded, _ = _split()
    path = sorted(guarded)[0]
    status, body = _post(remote_server, path, {})
    assert status == HTTPStatus.FORBIDDEN
    assert json.loads(body) == {"ok": False, "error": "mutations are loopback-only"}


def test_the_open_endpoints_stay_reachable(remote_server) -> None:
    """The classification is pinned in **both** directions.

    A guard that refused everything would pass the test above and break the
    reading surface: `cockpit.js` posts `/api/cockpit/tab-state` on a heartbeat
    from the tablet this bind exists for, so a 403 there is a regression, not
    caution. These five change runtime state only — the sibling test asserts
    they write nothing under `docs/`; this one asserts they still answer.
    """
    _, open_ = _split()
    assert set(open_) == {
        "/api/cockpit/focus",
        "/api/cockpit/tab-state",
        "/api/cockpit/agent-state",
        "/api/agent-hook",
        "/api/cockpit/dispatch",
    }, f"the open set changed: {sorted(open_)}"

    #: A well-formed heartbeat from the LAN peer must be accepted.
    status, _ = _post(remote_server, "/api/cockpit/tab-state",
                      {"tab_id": "t1", "url": "/README.md", "following": True})
    assert status == HTTPStatus.OK, (
        "the reading surface's heartbeat was refused; the tablet the 0.0.0.0 "
        "bind exists for cannot report which note it is on"
    )


def test_a_loopback_peer_is_not_refused(tmp_path) -> None:
    """The mirror case, on the same routes, without the fake peer — otherwise
    every assertion above is satisfied by a server that 403s unconditionally.
    """
    root = tmp_path / "proj"
    docs = root / "docs"
    docs.mkdir(parents=True)
    (docs / "README.md").write_text("# Hi\n", encoding="utf-8")
    (root / "SNAPSHOT.yaml").write_text("version: 1\n", encoding="utf-8")
    server = DocsServer(docs_root=docs, bind="127.0.0.1", port=0)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0),
        _make_handler(
            server.docs_root, server.index, server.bus,
            cockpit_state=server.cockpit_state,
            agent_tracker=server.agent_tracker,
        ),
    )
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        base = f"http://127.0.0.1:{port}"
        guarded, _ = _split()
        refused = [
            p for p in sorted(guarded)
            if _post(base, p, {})[0] == HTTPStatus.FORBIDDEN
        ]
        assert not refused, (
            f"loopback callers were refused by {refused} — the guard is not "
            "discriminating, it is just saying no"
        )
    finally:
        httpd.shutdown()
        httpd.server_close()


# ---- the browser front door's half of the bargain (FEAT-0083) --------------

COCKPIT_JS = (
    Path(__file__).resolve().parents[1]
    / "src" / "project_os_cockpit" / "static" / "cockpit.js"
)


def test_mode_one_posts_to_nothing_note_backed() -> None:
    """[[FEAT-0083]] criterion 4: *"Nothing in mode 1 issues a POST to a
    `note_writes`-backed endpoint."*

    The guard above proves the **server** refuses a remote writer. This proves
    the **client** never asks — a different property, and the one that decays
    as the eleven reading views get ported. A ported view that brings its
    desktop write control along would still be refused over the LAN, but it
    would offer the user a button that silently fails on the tablet and works
    on the Mac, which is the confusing half of ADR-0010 that the classification
    exists to avoid.

    Asserted against the guarded set rather than a hand-written list of paths,
    so a newly guarded endpoint is in this test's domain the moment it exists.
    """
    js = COCKPIT_JS.read_text(encoding="utf-8")
    guarded, _ = _split()
    reached = sorted(p for p in guarded if f'"{p}"' in js)
    assert not reached, (
        "the browser cockpit references loopback-guarded write endpoints "
        f"{reached}; mode 1 is the reading surface (ADR-0010, FEAT-0083)"
    )


def test_the_browser_clients_endpoint_inventory() -> None:
    r"""The reading surface's whole server-facing footprint, pinned.

    **This test previously asserted a false number.** It read
    `fetch\("(/api/[^"]+)"` — call sites — and reported that `cockpit.js`
    reaches *two* endpoints. It reaches **five** plus an SSE stream, because
    the file's own idiom is `fetchJson(url)`, and the regex could not see
    through it. The wrong figure was copied into [[FEAT-0083]] criterion 4,
    the CHG note and [[PHASE-029]] before review caught it.

    So the inventory now reads **string literals**, which is the property that
    actually holds: an endpoint the client talks to has to appear in the file
    as text, whatever wrapper carries it.

    The number matters because [[PHASE-029]] is about to move it. Eleven
    reading views arriving should show up here as a diff, not as silence.
    """
    import re

    js = COCKPIT_JS.read_text(encoding="utf-8")
    literals = sorted(set(re.findall(r'"(/(?:api|_events)[^"]*)"', js)))
    assert literals == [
        "/_events",                   # SSE, read-only
        "/api/",                      # a prefix test, not a call
        "/api/cockpit/context",       # read
        "/api/cockpit/nav?mode=",     # read
        "/api/cockpit/tab-state",     # POST — runtime-only, on the open list
        "/api/cockpit/validation",    # read
        "/api/terminal",              # read; its socket binds loopback only
    ], literals


def test_the_client_makes_exactly_one_post() -> None:
    """[[FEAT-0083]] criterion 4 from the other side.

    `test_mode_one_posts_to_nothing_note_backed` asks whether any *guarded*
    path appears in the JS. Review showed that is defeatable by construction —
    `var u = "/api/notes/" + "tick"` appears nowhere as a whole literal. This
    asks the blunter question instead: **how many POSTs does the client make
    at all?** One. Any second POST fails here regardless of how its URL is
    spelled, which is the property string-matching cannot give.

    Neither test subsumes the other and both are cheap. Stated plainly because
    the honest limit is worth more than a guard that looks total and is not.
    """
    import re

    js = COCKPIT_JS.read_text(encoding="utf-8")
    posts = re.findall(r'method:\s*"POST"', js)
    assert len(posts) == 1, (
        f"the browser cockpit now issues {len(posts)} POSTs; it is the reading "
        "surface (ADR-0010) and every write belongs behind REQ-0034's "
        "authenticated path"
    )
