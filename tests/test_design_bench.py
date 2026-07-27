"""Design bench — the register and the artifact endpoint (FEAT-0042).

Two things are being guarded, and both were decisions rather than mechanics:

**Membership is by type, never by path.** The Library group used to find
designs with a `references/design/` regex, so a design note anywhere else was
invisible and a reference that happened to sit in that folder was mislabelled.
The type is the claim; the path is where someone put the file.

**`viewport` absence is meaningful.** It says the artifact is a document
*about* a surface rather than the surface itself. Independent review of
PHASE-009 found the phase's flagship benefit — "renders at the viewport the app
actually runs at" — did not apply to its flagship artifact, because DES-0001 is
a scrolling dossier of mocks fixed at 1240px. Framing that at 900px would have
satisfied an exit criterion while demonstrating nothing.
"""

from __future__ import annotations

import json
from pathlib import Path

from project_os_cockpit import cockpit
from project_os_cockpit.index import Index


def _note(path: Path, fm: dict, body: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["---"]
    for k, v in fm.items():
        lines.append(f"{k}: {json.dumps(v)}")
    lines.append("---")
    path.write_text("\n".join(lines) + "\n\n" + body, encoding="utf-8")


def _corpus(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    _note(docs / "designs" / "DES-0001-System.md", {
        "type": "[[design]]", "id": "DES-0001", "title": "The system",
        "status": "implemented", "role": "system", "asset": "system.html",
        "viewport": 900, "implements": ["[[FEAT-0001]]", "[[PHASE-002]]"],
    })
    (docs / "designs" / "system.html").write_text("<h1>system</h1>", encoding="utf-8")
    _note(docs / "designs" / "DES-0002-Dossier.md", {
        "type": "[[design]]", "id": "DES-0002", "title": "A dossier",
        "status": "draft", "asset": "dossier.html",
    })
    (docs / "designs" / "dossier.html").write_text("<h1>dossier</h1>", encoding="utf-8")
    # A design that does NOT live under designs/ — membership is by type.
    _note(docs / "features" / "x" / "DES-0003-Elsewhere.md", {
        "type": "[[design]]", "id": "DES-0003", "title": "Somewhere else",
        "status": "proposed", "asset": "elsewhere.html",
    })
    (docs / "features" / "x" / "elsewhere.html").write_text("<i>e</i>", encoding="utf-8")
    # A reference sitting in designs/ — must NOT be counted as a design.
    _note(docs / "designs" / "REF-0009-Not-A-Design.md", {
        "type": "[[reference]]", "id": "REF-0009", "title": "Not a design",
        "status": "active",
    })
    return docs


# ---- membership -----------------------------------------------------------

def test_membership_is_by_type_not_path(tmp_path: Path) -> None:
    payload = cockpit.designs_payload(Index.build(_corpus(tmp_path)))
    ids = [d["id"] for d in payload["designs"]]
    assert ids == ["DES-0001", "DES-0002", "DES-0003"]
    assert "REF-0009" not in ids, (
        "a reference inside designs/ was counted as a design — membership "
        "must come from `type:`, not from where the file sits"
    )


def test_a_design_outside_the_designs_folder_is_still_found(tmp_path: Path) -> None:
    """The path-regex version made this note invisible."""
    payload = cockpit.designs_payload(Index.build(_corpus(tmp_path)))
    elsewhere = next(d for d in payload["designs"] if d["id"] == "DES-0003")
    assert elsewhere["rel"] == "features/x/DES-0003-Elsewhere.md"
    assert elsewhere["asset"] == "features/x/elsewhere.html", (
        "asset must resolve relative to the NOTE, not to docs/designs/"
    )


# ---- the two declared fields ---------------------------------------------

def test_viewport_absence_is_preserved_not_defaulted(tmp_path: Path) -> None:
    """A dossier has no viewport. Defaulting one would frame a scrolling
    document at a device width and demonstrate nothing."""
    payload = cockpit.designs_payload(Index.build(_corpus(tmp_path)))
    by_id = {d["id"]: d for d in payload["designs"]}
    assert by_id["DES-0001"]["viewport"] == 900
    assert by_id["DES-0002"]["viewport"] is None
    assert by_id["DES-0003"]["viewport"] is None


def test_a_junk_viewport_degrades_to_none(tmp_path: Path) -> None:
    docs = _corpus(tmp_path)
    _note(docs / "designs" / "DES-0004-Junk.md", {
        "type": "[[design]]", "id": "DES-0004", "title": "Junk viewport",
        "status": "draft", "asset": "dossier.html", "viewport": "wide",
    })
    payload = cockpit.designs_payload(Index.build(docs))
    junk = next(d for d in payload["designs"] if d["id"] == "DES-0004")
    assert junk["viewport"] is None


def test_role_defaults_to_proposal(tmp_path: Path) -> None:
    """`system` must be claimed explicitly — a project has one system and many
    proposals, so the safe default is the common case."""
    payload = cockpit.designs_payload(Index.build(_corpus(tmp_path)))
    by_id = {d["id"]: d for d in payload["designs"]}
    assert by_id["DES-0001"]["role"] == "system"
    assert by_id["DES-0002"]["role"] == "proposal"


def test_missing_asset_is_reported_not_hidden(tmp_path: Path) -> None:
    docs = _corpus(tmp_path)
    _note(docs / "designs" / "DES-0005-Gone.md", {
        "type": "[[design]]", "id": "DES-0005", "title": "Missing asset",
        "status": "draft", "asset": "nope.html",
    })
    payload = cockpit.designs_payload(Index.build(docs))
    gone = next(d for d in payload["designs"] if d["id"] == "DES-0005")
    assert gone["asset"] == "designs/nope.html"
    assert gone["has_asset"] is False, (
        "the surface needs to distinguish 'no artifact declared' from "
        "'declared but missing' so it can say which"
    )


def test_implements_resolves_every_id_type(tmp_path: Path) -> None:
    payload = cockpit.designs_payload(Index.build(_corpus(tmp_path)))
    system = next(d for d in payload["designs"] if d["id"] == "DES-0001")
    assert system["implements"] == ["FEAT-0001", "PHASE-002"]


# ---- the real corpus ------------------------------------------------------

def test_the_repos_own_designs_resolve() -> None:
    """Against the real notes, not a fixture. DES-0001 is a dossier (no
    viewport); DES-0002 is the design system (viewport 900, role system)."""
    docs = Path(__file__).resolve().parents[1] / "docs"
    payload = cockpit.designs_payload(Index.build(docs))
    by_id = {d["id"]: d for d in payload["designs"]}
    assert "DES-0001" in by_id and "DES-0002" in by_id
    assert by_id["DES-0001"]["has_asset"] is True
    assert by_id["DES-0001"]["viewport"] is None, (
        "DES-0001 is a scrolling dossier of mocks; a viewport here would frame "
        "it at a size that exercises nothing"
    )
    assert by_id["DES-0002"]["role"] == "system"
    assert by_id["DES-0002"]["viewport"] == 900


# ---- the artifact endpoint ------------------------------------------------

def test_design_asset_endpoint_serves_only_claimed_artifacts(tmp_path: Path) -> None:
    """The rule that stops a render surface becoming a file browser.

    `/design-asset/<rel>` serves an artifact verbatim so it can be framed. If
    it served any file under `docs/` by path, the cockpit would expose every
    note, every snapshot and every fixture over HTTP to anything that could
    reach the sidecar. Only paths *claimed by a design note's* `asset:` are
    served.
    """
    import threading
    import urllib.error
    import urllib.request

    from project_os_cockpit.server import (
        DocsServer, _NoDNSThreadingHTTPServer, _make_handler,
    )

    docs = _corpus(tmp_path)
    (docs / "secret.md").write_text("# not an artifact\n", encoding="utf-8")
    (docs / "designs" / "unclaimed.html").write_text("<b>orphan</b>", encoding="utf-8")

    server = DocsServer(docs_root=docs, bind="127.0.0.1", port=0)
    index = Index.build(docs)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0), _make_handler(docs, index, server.bus))
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    def get(path: str):
        try:
            with urllib.request.urlopen(
                    f"http://127.0.0.1:{port}{path}", timeout=3) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    try:
        status, body = get("/design-asset/designs/system.html")
        assert status == 200 and b"system" in body, "a claimed artifact must serve"

        # Not claimed by any note's asset: — even though it is a real file
        # sitting in designs/ next to the others.
        assert get("/design-asset/designs/unclaimed.html")[0] == 404, (
            "an unclaimed .html in designs/ was served; the endpoint must gate "
            "on the design register, not on the directory"
        )
        # An ordinary note.
        assert get("/design-asset/secret.md")[0] == 404
        # Traversal, unencoded and encoded.
        assert get("/design-asset/../../etc/passwd")[0] in (403, 404)
        assert get("/design-asset/%2e%2e%2f%2e%2e%2fetc%2fpasswd")[0] in (403, 404)

        # The register itself is served and matches the payload.
        status, body = get("/api/cockpit/designs")
        assert status == 200
        assert {d["id"] for d in json.loads(body)["designs"]} == {
            "DES-0001", "DES-0002", "DES-0003"}
    finally:
        httpd.shutdown()


def test_design_asset_response_is_not_cacheable_and_does_not_sniff() -> None:
    """An artifact is authored content. It must not be cached across revisions
    (a compare view would show a stale one) and must not be content-sniffed."""
    import inspect

    from project_os_cockpit import server as server_mod

    body = inspect.getsource(server_mod).split("def _serve_design_asset(")[1].split("\n        def ")[0]
    assert "no-store" in body
    assert "nosniff" in body
