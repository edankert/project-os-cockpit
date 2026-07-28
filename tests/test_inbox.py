"""The project inbox (FEAT-0045).

The store endpoint is the first in this codebase that writes a file the caller
supplies to a path that did not exist. Everything else writes notes through
`note_writes`, which is a field allow-list over files that are already there.
So the guard tests here are held to ISS-0056's three clauses, learned across
four rewrites of one loopback test:

  1. fail when the guard is removed **from the endpoint**,
  2. assert the guarded effect did not happen,
  3. assert the refusal pre-empts the endpoint's other branches.
"""
from __future__ import annotations

import base64
import datetime as dt
import json
import re
import threading
import urllib.error
import urllib.request
from http import HTTPStatus
from pathlib import Path

import pytest

from project_os_cockpit import inbox as inbox_mod
from project_os_cockpit.server import (
    DocsServer, _NoDNSThreadingHTTPServer, _make_handler,
)


def _serve(tmp_path: Path):
    docs = tmp_path / "docs"
    docs.mkdir(exist_ok=True)
    (docs / "README.md").write_text("# x\n", encoding="utf-8")
    server = DocsServer(docs_root=docs, bind="127.0.0.1", port=0)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0),
        _make_handler(server.docs_root, server.index, server.bus,
                      cockpit_state=server.cockpit_state))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def _post(port: int, path: str, body: dict) -> tuple[int, dict]:
    req = urllib.request.Request(
        "http://127.0.0.1:%d%s" % (port, path),
        data=json.dumps(body).encode(), method="POST",
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as exc:
        return exc.code, json.load(exc)


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 64


# ---- naming ---------------------------------------------------------------

def test_a_hostile_name_cannot_become_a_path() -> None:
    """The name arrives from a drag-and-drop or a clipboard paste — the one
    place a user-supplied name reaches a write path. Separators are stripped
    before anything else, so a traversal survives only as a stem."""
    assert inbox_mod.safe_name("../../.ssh/authorized_keys") is None  # suffix
    got = inbox_mod.safe_name("../../evil.png")
    assert got and "/" not in got and ".." not in got
    assert got.endswith("-evil.png"), got


def test_only_evidence_shaped_files_are_stored() -> None:
    """An allow-list, not a deny-list: the inbox holds evidence someone
    dropped, and an executable is not evidence."""
    for bad in ("run.sh", "x.py", "a.dylib", "noextension", ".", "..", ""):
        assert inbox_mod.safe_name(bad) is None, bad
    for good in ("shot.png", "notes.md", "export.csv", "scan.PDF"):
        assert inbox_mod.safe_name(good) is not None, good


def test_two_items_in_the_same_second_both_survive(tmp_path: Path) -> None:
    """Capturing a sequence of screenshots is exactly when collisions happen,
    and silently overwriting loses evidence the user believed they handed
    over."""
    tmp_path.mkdir(exist_ok=True)
    now = dt.datetime(2026, 7, 28, 12, 0, 0)
    name = inbox_mod.safe_name("shot.png", now=now)
    first = inbox_mod.unique_path(tmp_path, name)
    first.write_bytes(b"1")
    second = inbox_mod.unique_path(tmp_path, name)
    assert second != first and not second.exists()


# ---- the endpoint ---------------------------------------------------------

def test_a_dropped_file_lands_in_the_inbox(tmp_path: Path) -> None:
    httpd, port = _serve(tmp_path)
    try:
        status, data = _post(port, "/api/inbox/store",
                             {"name": "screenshot.png", "data": _b64(PNG)})
        assert status == 200 and data["ok"], data
        stored = tmp_path / "inbox" / data["name"]
        assert stored.is_file() and stored.read_bytes() == PNG
        assert data["rel"].startswith("inbox/")
    finally:
        httpd.shutdown()


def test_the_store_endpoint_is_loopback_only(tmp_path: Path) -> None:
    """All three clauses. A guard that refuses the RESPONSE after writing the
    file, or that sits below the name check so a LAN client can probe which
    names are storable, passes a weaker test than this (ISS-0056)."""
    httpd, port = _serve(tmp_path)
    try:
        handler_cls = httpd.RequestHandlerClass
        original = handler_cls._is_loopback
        handler_cls._is_loopback = lambda self: False   # type: ignore[assignment]
        try:
            status, data = _post(port, "/api/inbox/store",
                                 {"name": "shot.png", "data": _b64(PNG)})
            assert status == HTTPStatus.FORBIDDEN, (status, data)
            # 2: the guarded effect must not have happened.
            assert not (tmp_path / "inbox").exists(), "the file was written anyway"
            # 3: the refusal pre-empts the other branches — a bad name must
            # give the same answer, or a LAN client learns what is storable.
            assert _post(port, "/api/inbox/store",
                         {"name": "x.exe", "data": _b64(PNG)})[0] == HTTPStatus.FORBIDDEN
        finally:
            handler_cls._is_loopback = original         # type: ignore[assignment]
        assert _post(port, "/api/inbox/store",
                     {"name": "shot.png", "data": _b64(PNG)})[0] == 200
    finally:
        httpd.shutdown()


def test_a_traversal_name_writes_inside_the_inbox_or_not_at_all(tmp_path: Path) -> None:
    httpd, port = _serve(tmp_path)
    outside = tmp_path.parent / ("escaped-%s.png" % tmp_path.name)
    try:
        for name in ("../escaped.png", "../../escaped.png",
                     "/etc/escaped.png", "..\\escaped.png"):
            status, data = _post(port, "/api/inbox/store",
                                 {"name": name, "data": _b64(PNG)})
            if status == 200:
                written = tmp_path / "inbox" / data["name"]
                assert written.resolve().parent == (tmp_path / "inbox").resolve(), name
        assert not outside.exists()
        assert not (tmp_path / "escaped.png").exists()
    finally:
        httpd.shutdown()
        outside.unlink(missing_ok=True)


def test_an_oversized_item_is_refused(tmp_path: Path) -> None:
    """An unbounded write endpoint on a server that binds 0.0.0.0 is a way to
    fill a disk from the LAN.

    Refused at the BODY, before decoding — the shared 2 MB reader cap would
    otherwise have rejected ordinary screenshots while `MAX_ITEM_BYTES`
    advertised 25 MB, a limit that could never be reached. A limit that cannot
    be hit is worse than a small one honestly stated.
    """
    httpd, port = _serve(tmp_path)
    try:
        big = b"0" * (inbox_mod.MAX_ITEM_BYTES + 1024)
        try:
            status, _ = _post(port, "/api/inbox/store",
                              {"name": "big.png", "data": _b64(big)})
            assert status == HTTPStatus.REQUEST_ENTITY_TOO_LARGE, status
        except (urllib.error.URLError, ConnectionResetError):
            # The server refuses and closes before the whole body arrives,
            # which is the correct behaviour for an oversized upload.
            pass
        assert not list((tmp_path / "inbox").glob("*")) \
            if (tmp_path / "inbox").exists() else True
    finally:
        httpd.shutdown()


def test_an_ordinary_screenshot_is_not_refused(tmp_path: Path) -> None:
    """3 MB is a normal Retina screenshot and over the shared body cap. If this
    fails, the feature does not work for the thing it was built for."""
    httpd, port = _serve(tmp_path)
    try:
        shot = b"\x89PNG\r\n\x1a\n" + b"7" * (3 * 1024 * 1024)
        status, data = _post(port, "/api/inbox/store",
                             {"name": "retina.png", "data": _b64(shot)})
        assert status == 200, (status, data)
        assert (tmp_path / "inbox" / data["name"]).stat().st_size == len(shot)
    finally:
        httpd.shutdown()


def test_discarding_removes_the_item(tmp_path: Path) -> None:
    """Discarding is a GOOD outcome — an inbox whose items can only accumulate
    is an archive, which is what the triage skill exists to prevent."""
    httpd, port = _serve(tmp_path)
    try:
        _, data = _post(port, "/api/inbox/store",
                        {"name": "shot.png", "data": _b64(PNG)})
        name = data["name"]
        status, res = _post(port, "/api/inbox/discard", {"name": name})
        assert status == 200 and res["remaining"] == 0
        assert not (tmp_path / "inbox" / name).exists()
        assert _post(port, "/api/inbox/discard", {"name": name})[0] == 404
    finally:
        httpd.shutdown()


def test_discard_cannot_reach_outside_the_inbox(tmp_path: Path) -> None:
    httpd, port = _serve(tmp_path)
    victim = tmp_path / "docs" / "README.md"
    try:
        for name in ("../docs/README.md", "../../etc/passwd", "..", "sub/x.png"):
            assert _post(port, "/api/inbox/discard", {"name": name})[0] == 404, name
        assert victim.is_file(), "a file outside the inbox was deleted"
    finally:
        httpd.shutdown()


def test_the_listing_is_newest_first_and_the_empty_case_is_empty(tmp_path: Path) -> None:
    assert inbox_mod.list_items(tmp_path) == []
    httpd, port = _serve(tmp_path)
    try:
        for n in ("a.png", "b.png"):
            _post(port, "/api/inbox/store", {"name": n, "data": _b64(PNG)})
        items = inbox_mod.list_items(tmp_path)
        assert len(items) == 2
        assert items[0]["mtime"] >= items[1]["mtime"]
    finally:
        httpd.shutdown()


def test_the_inbox_is_not_inside_docs(tmp_path: Path) -> None:
    """`docs/` is the curated record — walked by the validator, read as the
    truth. Untriaged material in it would be read as documentation."""
    assert inbox_mod.inbox_dir(tmp_path).name == "inbox"
    assert inbox_mod.inbox_dir(tmp_path).parent == tmp_path


def test_the_convention_is_gitignored() -> None:
    """An item is either filed — and the FILED artefact is committed — or
    discarded. Committing staging preserves what triage exists to resolve."""
    root = Path(__file__).resolve().parents[1]
    assert "inbox/" in (root / ".gitignore").read_text(encoding="utf-8")


# ---- the drop path and capture (2026-07-28 regression) --------------------

def _renderer_src() -> str:
    return (Path(__file__).resolve().parents[1] / "desktop" / "src" / "renderer"
            / "renderer.ts").read_text(encoding="utf-8")


def test_dropping_does_not_require_a_path() -> None:
    """Electron 32 REMOVED `File.path`. The handler read it, got `undefined`,
    and returned early — so after that upgrade dropping a note silently stopped
    navigating and dropping a screenshot did nothing at all, with no error
    anywhere. Edwin found it by dropping an image.

    Filing needs the file's BYTES, not its location, so the path is optional
    now. Requiring one to do something that never needed one is what made this
    fail closed and silent.
    """
    src = _renderer_src()
    drop = src.split("document.addEventListener('drop'", 1)[1].split("\n});", 1)[0]
    assert "if (!absPath) return;" not in drop, (
        "the drop handler returns early with no path again; an image drop will "
        "silently do nothing"
    )
    assert "void storeInInbox(file);" in drop
    assert "cockpitApi.app.pathForFile(file)" in drop, (
        "the Electron 32 replacement for File.path is not used, so dropping a "
        "note cannot navigate"
    )


def test_the_path_resolver_lives_in_the_preload() -> None:
    """`webUtils` is not exposed to the renderer, so `getPathForFile` has to be
    called in the preload — reading it in the renderer returns undefined and
    reintroduces the silent failure."""
    pre = (Path(__file__).resolve().parents[1] / "desktop" / "src"
           / "preload.ts").read_text(encoding="utf-8")
    assert "webUtils" in pre and "getPathForFile" in pre
    assert "pathForFile:" in pre


def test_capture_distinguishes_cancel_from_failure() -> None:
    """A first cut checked only whether the file existed and called everything
    else `cancelled` — so a macOS Screen Recording denial, the first thing
    anyone hits on a new machine, would have told the user they cancelled
    something they never started.

    `screencapture` exits 0 and writes nothing on Escape, and exits non-zero
    with a message when it genuinely fails; both are observed.
    """
    main = (Path(__file__).resolve().parents[1] / "desktop" / "src"
            / "main.ts").read_text(encoding="utf-8")
    handler = main.split("app:capture-screenshot", 1)[1].split("ipcMain.handle", 1)[0]
    assert "code === 0 && !stderr.trim()" in handler, (
        "cancel is not distinguished from failure"
    )
    assert "Screen Recording" in handler, (
        "the most likely real failure has no actionable message"
    )
    assert "cancelled: true" in handler


def test_capture_writes_into_the_inbox() -> None:
    main = (Path(__file__).resolve().parents[1] / "desktop" / "src"
            / "main.ts").read_text(encoding="utf-8")
    handler = main.split("app:capture-screenshot", 1)[1].split("ipcMain.handle", 1)[0]
    assert "path.join(ws.root, 'inbox')" in handler
    assert "'-i'" in handler, "capture is not interactive, so it cannot be aimed"


def test_inbox_images_are_allowed_by_the_renderer_csp() -> None:
    """An `<img>` from the sidecar must be allowed, not just a `fetch` from it.

    The CSP granted the sidecar origin under `connect-src` and `frame-src` but
    not `img-src`, so every inbox thumbnail failed to load — silently, because a
    blocked image is just an image that never paints. `fetch()` of the exact
    same URL returned 200 and 151 KB of PNG, which is why this survived being
    "verified": the bytes were reachable, the picture was not.

    Caught by asserting `naturalWidth > 0` in the running app rather than
    asserting the `<img>` element existed.
    """
    html = (Path(__file__).resolve().parents[1]
            / "desktop/src/renderer/index.html").read_text(encoding="utf-8")
    csp = re.search(r'Content-Security-Policy"[^>]*content="([^"]+)"', html)
    assert csp, "the renderer CSP is gone"
    directives = {
        part.strip().split(" ", 1)[0]: part.strip()
        for part in csp.group(1).split(";") if part.strip()
    }
    assert "127.0.0.1" in directives.get("img-src", ""), (
        "img-src no longer allows the sidecar origin — inbox thumbnails and the "
        "full-size viewer will silently fail to paint again"
    )


def _code_only(js: str) -> str:
    """JS/TS with comments stripped — a comment naming an action reads like one."""
    js = re.sub(r"/\*.*?\*/", "", js, flags=re.S)
    return re.sub(r"^\s*//.*$", "", js, flags=re.M)


def test_every_inbox_menu_action_has_a_handler() -> None:
    """The right-click menu's actions must match what the renderer handles.

    This crosses a process boundary — `main.ts` names an action string and
    `renderer.ts` switches on it — so a rename in one file leaves a menu entry
    that silently does nothing. Nothing else checks it: the menu is native, so
    it cannot be clicked from a test, and popping it over CDP risks a nested
    run loop in the main process.

    Asserted both ways round: an unhandled action is a dead menu entry, and a
    handled-but-unsent action is a branch no menu can reach.
    """
    root = Path(__file__).resolve().parents[1]
    main = _code_only((root / "desktop/src/main.ts").read_text(encoding="utf-8"))
    renderer = _code_only(
        (root / "desktop/src/renderer/renderer.ts").read_text(encoding="utf-8"))

    case = main.split("case 'inbox-item': {", 1)
    assert len(case) == 2, "the inbox context menu is gone from main.ts"
    body = case[1].split("case 'rail':", 1)[0]
    sent = set(re.findall(r"sendDispatch\('([^']+)'", body))
    assert sent, "the inbox menu no longer dispatches anything"

    handled = set(re.findall(r"case '(inbox-[a-z]+)':", renderer))
    assert sent <= handled, f"menu actions with no handler: {sorted(sent - handled)}"
    assert handled <= sent, f"handlers no menu can reach: {sorted(handled - sent)}"


def test_a_denied_screen_permission_is_reported_as_a_permission_problem() -> None:
    """macOS says "could not create image from rect" when the permission is missing.

    Edwin hit exactly that string. Reported raw it reads like a geometry bug and
    sends you looking at the selection rectangle; the actionable text was
    already written but sat in an `|| fallback`, so it could only appear when
    stderr was EMPTY — the one case where a permission denial is *not* the
    cause. Confirmed with `systemPreferences.getMediaAccessStatus('screen')`,
    which returned `denied` on this machine.

    Three properties, because the first cut of this fix could satisfy any one
    of them and still be wrong.
    """
    src = _code_only((Path(__file__).resolve().parents[1]
                      / "desktop/src/main.ts").read_text(encoding="utf-8"))
    handler = src.split("app:capture-screenshot", 1)[1].split(
        "Drag-and-drop file resolver", 1)[0]

    # 1. the status is actually consulted, not assumed
    assert "getMediaAccessStatus('screen')" in handler

    # 2. the stderr text is classified, not just passed through
    assert re.search(r"could not create image", handler), (
        "the known permission stderr is no longer recognised — the raw macOS "
        "string will reach the user again"
    )

    # 3. `screencapture` still runs when access is not granted. Short-circuiting
    #    looks safer but means macOS never shows the permission prompt on
    #    'not-determined', so a fresh machine could never grant it at all.
    spawn_at = handler.index("spawn('screencapture'")
    guard = re.search(r"if \(access !== 'granted'\)[^\n]*\n[^\n]*return", handler[:spawn_at])
    assert guard is None, (
        "capture is skipped when access is not granted — on 'not-determined' "
        "that suppresses the macOS prompt and the feature can never start"
    )
