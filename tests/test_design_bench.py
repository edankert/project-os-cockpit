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

import inspect
import json
from http import HTTPStatus
import re
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
    # No viewport: it is a document. It declared 900 before the page existed,
    # recording the height REQ-0022 asserts rather than a width the artifact
    # is drawn at — and that one wrong field framed a scrolling reference page
    # inside a 900px window (ISS-0045).
    assert by_id["DES-0002"]["viewport"] is None


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


# ---- the render surface (TASK-0215) --------------------------------------

def _renderer() -> str:
    return (Path(__file__).resolve().parents[1]
            / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")


def test_frame_allows_scripts_but_nothing_else() -> None:
    """DES-0001 carries a theme toggle, so a script-free sandbox would break
    the acceptance subject. Everything else stays denied — and crucially the
    sandbox is NOT the protection against reaching a mutation endpoint, since
    a sandbox attribute does not restrict network. That protection is the
    asset route being GET-only and gated on the register."""
    src = _renderer()
    assert "'sandbox', 'allow-scripts'" in src
    for forbidden in ("allow-same-origin", "allow-top-navigation", "allow-forms",
                      "allow-popups", "allow-modals"):
        assert forbidden not in src, (
            "the design frame grants %s; an artifact is content, not code" % forbidden
        )


def test_declared_viewport_is_used_and_absence_means_scroll() -> None:
    """`declared` resolves to the note's viewport, or no framing at all. A
    dossier framed at a device width demonstrates nothing."""
    src = _renderer()
    assert "preset.key === 'declared' ? d.viewport : preset.w" in src
    # A document is not offered device widths at all — and no longer even
    # shown the bar. The first version rendered five buttons and disabled
    # four of them; Edwin's question ("why do we have these options if all we
    # show is a page") is answered by not rendering it (ISS-0045).
    head = src.split("function buildDesignHeader(")[1].split("\nfunction ")[0]
    assert "if (d.viewport) {" in head


def test_missing_artifact_is_distinguished_from_none_declared() -> None:
    """A blank pane for either would hide a typo committed weeks earlier."""
    src = _renderer()
    assert "declares no artifact yet" in src
    assert "Artifact not found" in src


def test_900_is_present_as_a_preset() -> None:
    """REQ-0022 asserts every state section fits above the fold at 900px, so a
    design reviewed at another size is reviewed against the wrong question."""
    assert "h: 900" in _renderer()


def test_the_asset_url_is_percent_encoded_per_segment() -> None:
    """A path segment with a space or '#' must not break the frame src, and
    encoding the whole path would destroy the separators."""
    assert "d.asset.split('/').map(encodeURIComponent).join('/')" in _renderer()


# ---- revision capture (TASK-0220) ----------------------------------------

def _git_workspace(tmp_path: Path) -> Path:
    import subprocess
    docs = tmp_path / "docs"
    _note(docs / "designs" / "DES-0001-X.md", {
        "type": "[[design]]", "id": "DES-0001", "title": "X",
        "status": "draft", "asset": "x.html",
    }, "# X\n")
    (docs / "designs" / "x.html").write_text("<h1>v1</h1>", encoding="utf-8")
    for args in (["init", "-q"], ["config", "user.email", "t@e.com"],
                 ["config", "user.name", "T"], ["add", "-A"],
                 ["commit", "-qm", "seed"]):
        subprocess.run(["git", "-C", str(tmp_path), *args], check=True,
                       capture_output=True)
    return docs


def _capture(docs: Path, payload: dict) -> tuple[int, dict]:
    import json as _json
    import threading
    import urllib.error
    import urllib.request

    from project_os_cockpit.server import (
        DocsServer, _NoDNSThreadingHTTPServer, _make_handler,
    )
    srv = DocsServer(docs_root=docs, bind="127.0.0.1", port=0)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0), _make_handler(docs, Index.build(docs), srv.bus))
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/design/capture",
            data=_json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.status, _json.loads(r.read())
        except urllib.error.HTTPError as e:
            try:
                return e.code, _json.loads(e.read())
            except Exception:
                return e.code, {}
    finally:
        httpd.shutdown()


def test_capture_commits_the_artifact_alone_with_its_reason(tmp_path: Path) -> None:
    """The hole PHASE-009 was built around and did not fill: TASK-0216 renders
    git history and nothing deposited it."""
    import subprocess
    docs = _git_workspace(tmp_path)
    (docs / "designs" / "x.html").write_text("<h1>v2</h1>", encoding="utf-8")
    # An unrelated dirty file must NOT be swept into the capture commit.
    (docs / "unrelated.md").write_text("noise\n", encoding="utf-8")

    status, body = _capture(docs, {"id": "DES-0001", "reason": "tightened the band"})
    assert status == 200 and body["ok"] is True

    log = subprocess.run(["git", "-C", str(tmp_path), "log", "--oneline", "-1"],
                         capture_output=True, text=True).stdout
    assert "design(DES-0001): tightened the band" in log

    files = subprocess.run(
        ["git", "-C", str(tmp_path), "show", "--name-only", "--format=", "HEAD"],
        capture_output=True, text=True).stdout.split()
    assert sorted(files) == ["docs/designs/DES-0001-X.md", "docs/designs/x.html"], (
        "capture swept in an unrelated file; the reason must not end up buried "
        "in a commit that changed other things"
    )


def test_capture_returns_the_sha_that_is_actually_head(tmp_path: Path) -> None:
    """A commit cannot contain its own hash. An early version wrote a
    placeholder, committed, corrected it and amended — which changed the sha
    again, so every log entry named a commit that did not exist."""
    import subprocess
    docs = _git_workspace(tmp_path)
    (docs / "designs" / "x.html").write_text("<h1>v2</h1>", encoding="utf-8")
    _, body = _capture(docs, {"id": "DES-0001", "reason": "why"})
    head = subprocess.run(["git", "-C", str(tmp_path), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    assert head.startswith(body["sha"])


def test_revision_log_records_the_reason_and_no_sha(tmp_path: Path) -> None:
    docs = _git_workspace(tmp_path)
    (docs / "designs" / "x.html").write_text("<h1>v2</h1>", encoding="utf-8")
    _capture(docs, {"id": "DES-0001", "reason": "raised contrast"})
    note = (docs / "designs" / "DES-0001-X.md").read_text(encoding="utf-8")
    assert "## Revisions" in note
    assert "— raised contrast" in note
    assert "`" not in note.split("## Revisions")[1], (
        "the log must carry no sha — a commit cannot name itself, and the "
        "pairing survives a rebase only if it is by order and date"
    )


def test_capture_requires_a_reason(tmp_path: Path) -> None:
    docs = _git_workspace(tmp_path)
    (docs / "designs" / "x.html").write_text("<h1>v2</h1>", encoding="utf-8")
    status, body = _capture(docs, {"id": "DES-0001"})
    assert status == 400 and "reason" in body["error"]


def test_capture_refuses_when_there_is_nothing_to_capture(tmp_path: Path) -> None:
    """Otherwise the log fills with entries recording that nothing changed."""
    docs = _git_workspace(tmp_path)
    status, body = _capture(docs, {"id": "DES-0001", "reason": "no edit made"})
    assert status == 409 and "no change" in body["error"]


def test_capture_is_loopback_gated() -> None:
    import inspect

    from project_os_cockpit import server as server_mod

    body = inspect.getsource(server_mod).split("def _serve_design_capture(")[1]
    body = body.split("\n        def ")[0]
    assert "_require_loopback()" in body, (
        "capture writes to the repo and runs git; it must not be reachable "
        "from the LAN the render server binds to"
    )


# ---- revisions and compare (TASK-0216) -----------------------------------

def test_revisions_follow_a_rename(tmp_path: Path) -> None:
    """`--follow` matters here: DES-0001's asset moved from
    references/design/ to designs/ when the design type landed. Without it the
    history would truncate at the rename and the design would look new."""
    import subprocess
    docs = _git_workspace(tmp_path)
    subprocess.run(["git", "-C", str(tmp_path), "mv",
                    "docs/designs/x.html", "docs/designs/renamed.html"],
                   check=True, capture_output=True)
    note = docs / "designs" / "DES-0001-X.md"
    note.write_text(note.read_text().replace('"x.html"', '"renamed.html"'), encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-qm", "design(DES-0001): renamed"],
                   check=True, capture_output=True)

    payload = cockpit.design_revisions_payload(tmp_path, Index.build(docs), "DES-0001")
    assert payload["available"] is True
    assert len(payload["revisions"]) >= 2, (
        "history truncated at the rename — --follow is what keeps a renamed "
        "design's past attached to it"
    )


def test_dirty_is_reported(tmp_path: Path) -> None:
    """An uncaptured edit is a revision the compare view cannot see."""
    docs = _git_workspace(tmp_path)
    clean = cockpit.design_revisions_payload(tmp_path, Index.build(docs), "DES-0001")
    assert clean["dirty"] is False
    (docs / "designs" / "x.html").write_text("<h1>edited</h1>", encoding="utf-8")
    dirty = cockpit.design_revisions_payload(tmp_path, Index.build(docs), "DES-0001")
    assert dirty["dirty"] is True


def test_the_reason_is_extracted_from_the_commit_subject(tmp_path: Path) -> None:
    docs = _git_workspace(tmp_path)
    (docs / "designs" / "x.html").write_text("<h1>v2</h1>", encoding="utf-8")
    _capture(docs, {"id": "DES-0001", "reason": "raised contrast"})
    payload = cockpit.design_revisions_payload(tmp_path, Index.build(docs), "DES-0001")
    assert payload["revisions"][0]["reason"] == "raised contrast"


def test_historical_asset_reads_without_touching_the_tree(tmp_path: Path) -> None:
    """`git show`, never a checkout. A compare view that stashed the user's
    uncommitted work to render a diff would be data loss wearing a feature's
    clothes."""
    docs = _git_workspace(tmp_path)
    (docs / "designs" / "x.html").write_text("<h1>v2</h1>", encoding="utf-8")
    _capture(docs, {"id": "DES-0001", "reason": "second"})
    payload = cockpit.design_revisions_payload(tmp_path, Index.build(docs), "DES-0001")
    old = payload["revisions"][-1]["sha"]

    # Leave an uncommitted edit in place; reading history must not disturb it.
    (docs / "designs" / "x.html").write_text("<h1>uncommitted</h1>", encoding="utf-8")
    body = cockpit.design_asset_at(tmp_path, Index.build(docs), "DES-0001", old)
    assert body is not None and b"v1" in body
    assert (docs / "designs" / "x.html").read_text() == "<h1>uncommitted</h1>", (
        "reading a historical revision modified the working copy"
    )


def test_a_bogus_sha_is_refused_before_it_reaches_git(tmp_path: Path) -> None:
    docs = _git_workspace(tmp_path)
    idx = Index.build(docs)
    for bad in ("", "HEAD; rm -rf /", "../../etc/passwd", "zzzz", "g" * 40):
        assert cockpit.design_asset_at(tmp_path, idx, "DES-0001", bad) is None


def test_compare_renders_both_sides_at_the_same_viewport() -> None:
    """Comparing two renders at different sizes would show the layout
    changing rather than the design."""
    src = _renderer()
    assert "body.classList.add('is-compare')" in src
    assert "buildDesignFrame(d), buildDesignFrame(d, designCompareSha)" in src


# ---- region-anchored annotation (TASK-0217) ------------------------------

def _design_with_regions(tmp_path: Path, html: str) -> Path:
    docs = tmp_path / "docs"
    _note(docs / "designs" / "DES-0001-X.md", {
        "type": "[[design]]", "id": "DES-0001", "title": "X",
        "status": "proposed", "asset": "x.html",
    }, "# X\n")
    (docs / "designs" / "x.html").write_text(html, encoding="utf-8")
    return docs


def test_a_comment_survives_its_region_MOVING_on_the_page(tmp_path: Path) -> None:
    """The premise of anchoring by id. Coordinate pins die on the next
    revision, and the founding artifact went through six in one session."""
    from project_os_cockpit import note_writes
    docs = _design_with_regions(
        tmp_path,
        '<div data-design-region="top">A</div><div data-design-region="band">B</div>')
    note = docs / "designs" / "DES-0001-X.md"
    fm, body = note_writes._split_frontmatter(note.read_text())
    note.write_text("---\n" + "\n".join(fm) + "\n---\n" + note_writes.append_design_comment(
        body, region="band", date="2026-07-27", author="user:edwin",
        text="too loud"), encoding="utf-8")

    # Move the region to the top of the document — a different position, same id.
    (docs / "designs" / "x.html").write_text(
        '<div data-design-region="band">B</div><div data-design-region="top">A</div>',
        encoding="utf-8")

    payload = cockpit.design_comments_payload(docs, Index.build(docs), "DES-0001")
    assert payload["comments"][0]["region"] == "band"
    assert payload["comments"][0]["orphaned"] is False
    assert payload["orphans"] == []


def test_a_comment_ORPHANS_when_its_region_is_renamed(tmp_path: Path) -> None:
    """The case that actually discriminates. A rename is indistinguishable
    from delete-and-add, so the comment cannot follow — but it must be SHOWN,
    not dropped, or the objection disappears with no way to know."""
    from project_os_cockpit import note_writes
    docs = _design_with_regions(tmp_path, '<div data-design-region="band">B</div>')
    note = docs / "designs" / "DES-0001-X.md"
    fm, body = note_writes._split_frontmatter(note.read_text())
    note.write_text("---\n" + "\n".join(fm) + "\n---\n" + note_writes.append_design_comment(
        body, region="band", date="2026-07-27", author="", text="too loud"),
        encoding="utf-8")

    (docs / "designs" / "x.html").write_text(
        '<div data-design-region="focus-band">B</div>', encoding="utf-8")

    payload = cockpit.design_comments_payload(docs, Index.build(docs), "DES-0001")
    assert payload["comments"][0]["orphaned"] is True
    assert len(payload["orphans"]) == 1, "the comment was dropped rather than flagged"


def test_duplicate_region_ids_are_deduped_in_declaration_order(tmp_path: Path) -> None:
    """A multi-plate dossier will plausibly repeat an id — DES-0001's own
    data-pin numbers restart per plate, which is why the contract requires
    scoping."""
    docs = _design_with_regions(
        tmp_path,
        '<i data-design-region="a">1</i><i data-design-region="b">2</i>'
        '<i data-design-region="a">3</i>')
    assert cockpit.design_regions(docs, "designs/x.html") == ["a", "b"]


def test_the_document_lane_is_not_an_orphan(tmp_path: Path) -> None:
    """Some criticism has no region — 'too much violet everywhere'. Inventing
    a region to host it would make the region list a fiction."""
    from project_os_cockpit import note_writes
    docs = _design_with_regions(tmp_path, '<div data-design-region="band">B</div>')
    note = docs / "designs" / "DES-0001-X.md"
    fm, body = note_writes._split_frontmatter(note.read_text())
    note.write_text("---\n" + "\n".join(fm) + "\n---\n" + note_writes.append_design_comment(
        body, region="", date="2026-07-27", author="", text="too much violet"),
        encoding="utf-8")
    payload = cockpit.design_comments_payload(docs, Index.build(docs), "DES-0001")
    assert payload["comments"][0]["region"] == ""
    assert payload["comments"][0]["orphaned"] is False


def test_comments_are_plain_markdown_in_the_note(tmp_path: Path) -> None:
    """REQ-0023's 'readable without the tool' clause. A reviewer must be able
    to read the objections as text and tell what each refers to."""
    from project_os_cockpit import note_writes
    body = note_writes.append_design_comment(
        "# X\n", region="plate-c", date="2026-07-27",
        author="user:edwin", text="the focus band is too loud")
    assert "- **plate-c** · 2026-07-27 · user:edwin — the focus band is too loud" in body
    assert note_writes.read_design_comments(body)[0]["region"] == "plate-c"


def test_comment_endpoint_rejects_an_undeclared_region(tmp_path: Path) -> None:
    """A comment anchored to a region the artifact does not declare would
    never render — accepting it would lose the objection silently."""
    import json as _json
    import threading
    import urllib.error
    import urllib.request

    from project_os_cockpit.server import (
        DocsServer, _NoDNSThreadingHTTPServer, _make_handler,
    )
    docs = _design_with_regions(tmp_path, '<div data-design-region="band">B</div>')
    srv = DocsServer(docs_root=docs, bind="127.0.0.1", port=0)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0), _make_handler(docs, Index.build(docs), srv.bus))
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    def post(payload):
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/design/comment",
            data=_json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.status, _json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, _json.loads(e.read())

    try:
        status, body = post({"id": "DES-0001", "region": "nope", "text": "x"})
        assert status == 400 and "unknown region" in body["error"]
        assert body["regions"] == ["band"], "the error must say what IS valid"
        assert post({"id": "DES-0001", "region": "band", "text": "ok"})[0] == 200
        assert post({"id": "DES-0001", "region": "", "text": "doc lane"})[0] == 200
    finally:
        httpd.shutdown()


def test_comment_endpoint_is_loopback_gated() -> None:
    import inspect

    from project_os_cockpit import server as server_mod

    body = inspect.getsource(server_mod).split("def _serve_design_comment(")[1]
    body = body.split("\n        def ")[0]
    assert "_require_loopback()" in body


def test_the_real_dossier_declares_its_29_regions() -> None:
    docs = Path(__file__).resolve().parents[1] / "docs"
    regions = cockpit.design_regions(docs, "designs/overview-redesign-dossier.html")
    assert len(regions) == 29
    assert len(set(regions)) == 29, "duplicate region ids in the real artifact"
    assert [r for r in regions if "-pin-" not in r] == [
        "plate-a", "plate-b", "plate-c", "plate-d", "plate-e", "states", "notes"]


# ---- desk review (TASK-0218) ---------------------------------------------

def test_a_design_enters_the_queue_only_when_proposed() -> None:
    """`draft` means the author is still writing it; `implemented` is after it
    was built. Queueing either asks for a decision nobody owes — the mistake
    plans made (ISS-0031)."""
    assert cockpit.QUEUE_INTAKE_STATES["design"] == ("proposed",)


def test_accepting_a_design_does_not_mark_it_implemented() -> None:
    """`implemented` is what the code shipping means, and only the parity
    check can honestly claim it."""
    from project_os_cockpit import note_writes
    assert note_writes.DECIDE_TRANSITIONS["design"] == ("accepted", "cancelled")


def test_rejection_is_cancelled_not_superseded() -> None:
    """`superseded` means a LATER design replaced it — a different fact about
    the future than 'this one was turned down'."""
    from project_os_cockpit import note_writes
    assert note_writes.DECIDE_TRANSITIONS["design"][1] == "cancelled"


def test_the_verdict_records_which_revision_it_judged(tmp_path: Path) -> None:
    """The field that stops an old approval laundering a new design."""
    from project_os_cockpit import note_writes
    docs = _git_workspace(tmp_path)
    (docs / "designs" / "x.html").write_text("<h1>v2</h1>", encoding="utf-8")
    _capture(docs, {"id": "DES-0001", "reason": "second cut"})
    revs = cockpit.design_revisions_payload(tmp_path, Index.build(docs), "DES-0001")
    sha = revs["revisions"][0]["sha"]

    result = note_writes.stamp_design_verdict(
        Index.build(docs), "DES-0001", reviewer="user:edwin",
        verdict="approved", revision=sha, accept=True)
    assert result["design_revision"] == sha
    note = (docs / "designs" / "DES-0001-X.md").read_text()
    assert f'design_revision: "{sha}"' in note
    assert 'status: "accepted"' in note


def test_a_verdict_naming_a_revision_that_does_not_exist_is_refused(tmp_path: Path) -> None:
    """Otherwise the pin is decoration: a verdict could name anything and the
    laundering it exists to prevent would be back."""
    import json as _json
    import threading
    import urllib.error
    import urllib.request

    from project_os_cockpit.server import (
        DocsServer, _NoDNSThreadingHTTPServer, _make_handler,
    )
    docs = _git_workspace(tmp_path)
    srv = DocsServer(docs_root=docs, bind="127.0.0.1", port=0)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0), _make_handler(docs, Index.build(docs), srv.bus))
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    def post(payload):
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/design/verdict",
            data=_json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.status, _json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, _json.loads(e.read())

    try:
        status, body = post({"id": "DES-0001", "verdict": "approved",
                             "revision": "deadbee", "reviewer": "user:edwin"})
        assert status == 400 and "not in this design's history" in body["error"]
        # And a verdict with no revision at all.
        status, body = post({"id": "DES-0001", "verdict": "approved",
                             "reviewer": "user:edwin"})
        assert status == 400 and "launder" in body["error"]
    finally:
        httpd.shutdown()


def test_verdict_endpoint_is_loopback_gated() -> None:
    import inspect

    from project_os_cockpit import server as server_mod

    body = inspect.getsource(server_mod).split("def _serve_design_verdict(")[1]
    body = body.split("\n        def ")[0]
    assert "_require_loopback()" in body


def test_stamping_a_non_design_is_refused(tmp_path: Path) -> None:
    from project_os_cockpit import note_writes
    docs = _corpus(tmp_path)
    _note(docs / "features" / "FEAT-0001-F.md", {
        "type": "[[feature]]", "id": "FEAT-0001", "title": "F", "status": "backlog"})
    try:
        note_writes.stamp_design_verdict(
            Index.build(docs), "FEAT-0001", reviewer="u", verdict="approved",
            revision="abc1234")
        raise AssertionError("stamped a design verdict onto a feature")
    except note_writes.WriteError as exc:
        assert "not a design" in str(exc)


# ---- reachability (the surface must have a door) --------------------------

def test_designs_reach_the_bench_from_the_design_mode(tmp_path: Path) -> None:
    """Built, tested, and unreachable: the only link to `~design/<id>` lived
    inside the register, which nothing pointed to. A closed loop with no
    entrance — found by Edwin opening the app and seeing nothing.

    The Library Design group that originally carried this guard was
    removed in PHASE-010 (TASK-0243) as a duplicate of the Design mode
    FEAT-0043 had since built. The *guard* is what mattered, so it moves
    to the surface that now owns the route rather than being deleted with
    the group — removing the duplicate must not remove the assertion that
    the survivor still works.
    """
    docs = _corpus(tmp_path)
    index = Index.build(docs)
    groups = cockpit._design_groups(index, None)
    # The `designs` group only, since TASK-0374 widened this view into the
    # project's constraints. The guard is about the *route to the bench*, and
    # only a design has one — an ADR or a risk in this view is a note.
    items = [item for g in groups if g["key"] == "designs" for item in g["items"]]
    assert items, "the Design mode lists no designs"
    for item in items:
        assert item["url"].startswith("~design/"), (
            "the mode opens the design NOTE; the note is prose about a "
            "design, the artifact is the design"
        )

    # ...and Library no longer offers a second, competing route to it.
    lib = cockpit._library_groups(index, None, [])
    assert not any(g.get("key") == "design" for g in lib), (
        "the Library Design group was removed as a duplicate (TASK-0243)"
    )


def test_a_design_note_offers_its_artifact() -> None:
    """Opening a design note and seeing only prose is correct for Markdown
    and wrong for a design."""
    src = _renderer()
    assert "buildDesignNoteBanner" in src
    assert "Open ${d.id} in the design bench" in src
    assert "=== 'design'" in src, "the banner must be gated on the note type"


def test_a_virtual_page_url_survives_extractRel() -> None:
    """The second reachability bug. `extractRel` accepted only `/docs/…` and
    returned null for anything else — so a Library row pointing at
    `~design/DES-0001` got no data-rel, and every nav path keys off data-rel.
    The row rendered, looked clickable, and did nothing."""
    src = _renderer()
    fn = src.split("function extractRel(")[1].split("\n}")[0]
    assert "url.startsWith('~')" in fn, (
        "extractRel drops virtual pages; a Library row that points at one is "
        "a dead click"
    )


# ---- the project brief (TASK-0223) ---------------------------------------

def _brief(tmp_path: Path, text: str | None) -> dict:
    if text is not None:
        (tmp_path / "LLM_BRIEF.md").write_text(text, encoding="utf-8")
    return cockpit.brief_payload(tmp_path)


def test_three_states_not_two(tmp_path: Path) -> None:
    """'No brief' and 'a brief that says REPLACE ME' call for different
    things: one project never adopted the convention, the other adopted it and
    stopped. Collapsing them hides the second — which is the one worth acting
    on, and was 10 of 11 fleet repos."""
    assert _brief(tmp_path, None)["state"] == "absent"
    assert _brief(tmp_path, "# B\n- Name: REPLACE ME\n")["state"] == "unfilled"
    assert _brief(tmp_path, "# B\n- Name: thing\n- Purpose: does a thing\n")["state"] == "filled"


def test_placeholder_text_is_never_returned(tmp_path: Path) -> None:
    """A surface leading with 'Purpose: REPLACE ME' every session is worse
    than one that says the brief needs writing."""
    b = _brief(tmp_path, "# B\n- Name: REPLACE ME\n- Purpose: REPLACE ME\n")
    assert b["name"] == "" and b["purpose"] == ""
    assert b["placeholders"] == 2


def test_a_partially_filled_brief_keeps_what_is_real(tmp_path: Path) -> None:
    """Half-done is the common state of a file being written."""
    b = _brief(tmp_path, "# B\n- Name: the thing\n- Purpose: REPLACE ME\n")
    assert b["name"] == "the thing"
    assert b["purpose"] == ""
    assert b["state"] == "unfilled"
    # The name survives INTO the unfilled state — that is the point. State
    # says the identity is incomplete; it does not discard the half that is
    # real (ISS-0035).
    assert b["placeholders"] == 1


def test_parsing_is_tolerant_of_a_hand_edited_file(tmp_path: Path) -> None:
    """The brief is prose a human edits. A reordered section, an unknown
    heading, or a missing one are all normal and none may break the surface."""
    b = _brief(tmp_path, "# B\n\n## Something Nobody Planned\nfree text\n\n"
                         "## Project Identity\n- Purpose: backwards order\n")
    assert b["purpose"] == "backwards order"
    # Nothing left to fill: zero placeholders and real content. Reporting
    # `unfilled` here would headline "This project has not said what it is"
    # over a file someone finished writing — the mirror of the bug the state
    # field was reshaped to fix (ISS-0036).
    assert b["state"] == "filled"
    assert b["placeholders"] == 0
    assert [s["heading"] for s in b["sections"]] == [
        "Something Nobody Planned", "Project Identity"]


def test_an_empty_section_is_dropped(tmp_path: Path) -> None:
    b = _brief(tmp_path, "# B\n\n## Filled\ncontent\n\n## Empty\n\n## Also Filled\nx\n")
    assert [s["heading"] for s in b["sections"]] == ["Filled", "Also Filled"]


def test_the_real_brief_is_filled_and_parses() -> None:
    """Against this repo, not a fixture. It said REPLACE ME until 2026-07-28."""
    root = Path(__file__).resolve().parents[1]
    b = cockpit.brief_payload(root)
    assert b["state"] == "filled", "this repo's brief regressed to a placeholder"
    assert b["name"] == "project-os-cockpit"
    assert "cockpit" in b["purpose"].lower()
    assert any(s["heading"] == "Invariants" for s in b["sections"])


def test_the_band_never_renders_the_placeholder(tmp_path: Path) -> None:
    """The property is about the placeholder TEXT, not about which fields the
    unfilled branch touches.

    The first version of this test asserted the branch never reads
    `brief.name` — which is neither necessary (the payload scrubs it) nor
    sufficient (nothing stopped the branch rendering `sections[].body`, which
    carried the placeholder verbatim). Independent review demonstrated the
    leak with both tests green. So: assert the payload, at every field a
    surface could render.
    """
    b = _brief(tmp_path, "# B\n\n## Project Identity\n- Name: REPLACE ME\n"
                         "- Purpose: REPLACE ME\n\n## Invariants\n"
                         "- REPLACE ME\n- a real invariant\n")
    rendered = [b["name"], b["purpose"]] + [s["body"] for s in b["sections"]]
    for value in rendered:
        assert "REPLACE" not in value.upper(), value
    # The real line beside the placeholder survives — scrubbing is per LINE,
    # because discarding a half-written section would punish progress.
    assert any("a real invariant" in s["body"] for s in b["sections"])

    src = _renderer()
    band = src.split("function buildIdentityBand(")[1].split("\nasync function")[0]
    assert "has not said what it is" in band


def test_the_unfilled_band_leads_with_the_name_when_there_is_one(tmp_path: Path) -> None:
    """Headlining "this project has not said what it is" over a name the
    payload just parsed calls the file a liar (ISS-0035). `name` is already
    placeholder-scrubbed, so a non-empty value here is always real."""
    b = _brief(tmp_path, "# B\n- Name: the thing\n- Purpose: REPLACE ME\n")
    assert b["state"] == "unfilled" and b["name"] == "the thing"
    src = _renderer()
    band = src.split("function buildIdentityBand(")[1].split("\nasync function")[0]
    unfilled = band.split("if (brief.state === 'unfilled')")[1].split("return band;")[0]
    assert "brief.name" in unfilled, (
        "the unfilled branch ignores a name the payload parsed"
    )
    assert "brief.placeholders\n" in unfilled or "brief.placeholders" in unfilled


def test_an_absent_brief_degrades_silently() -> None:
    """Not every project adopts the convention; nagging one that never did is
    noise rather than a finding."""
    src = _renderer()
    assert "brief.state === 'absent') return null" in src


# ---- the top-level mode (TASK-0224) --------------------------------------

def test_design_sits_second_before_the_structure_modes() -> None:
    """The *position* is the decision, so it is what gets asserted.

    Edwin's reasoning: design is one of the first things you do, so it
    belongs before Features/Tasks/Issues rather than appended at the end
    where a new mode naturally lands. Ordering is the kind of thing a later
    edit reshuffles without noticing, and once Design is eighth in the strip
    it reads as an afterthought again — which is exactly the state this task
    exists to leave behind.
    """
    src = _renderer()
    modes = re.search(r"const NAV_MODES = \[([^\]]+)\]", src).group(1)
    order = [m.strip().strip("'") for m in modes.split(",")]
    assert order[:2] == ["overview", "intent"], order
    # `tasks` is still in NAV_MODES (the server serves it) but has no button
    # since TASK-0368 — position is asserted for the modes a human can click.
    for structural in ("features", "tasks", "issues"):
        assert order.index("intent") < order.index(structural)

    # The strip's markup carries its own order; both must agree, because the
    # buttons are what a human actually sees.
    html = (Path(__file__).resolve().parents[1]
            / "desktop" / "src" / "renderer" / "index.html").read_text(encoding="utf-8")
    buttons = re.findall(r'top-bar-btn[^>]*data-mode="(\w+)"', html)
    assert buttons.index("intent") == 1, buttons
    assert "tasks" not in buttons, (
        "the Tasks button was retired in TASK-0368 — tasks hang under their "
        "feature, and a button here would be a second home for them"
    )
    for structural in ("features", "issues"):
        assert buttons.index("intent") < buttons.index(structural)


def test_the_mode_has_a_button_an_icon_and_a_server_that_serves_it() -> None:
    """Three separate places, and a mode missing any one of them is broken
    in a way the other two hide. The design bench has already shipped twice
    with a payload nothing could reach; this asserts the whole path."""
    html = (Path(__file__).resolve().parents[1]
            / "desktop" / "src" / "renderer" / "index.html").read_text(encoding="utf-8")
    assert 'data-mode="intent"' in html
    src = _renderer()
    # Keyed by `data-mode`: when the id became `intent` (TASK-0385) and this
    # key did not, the lookup fell through to `TYPE_ICONS._default` and the
    # button silently wore the wrong glyph. This assertion caught it.
    assert re.search(r"intent:\s*'<circle", src), "no icon; the button renders blank"
    assert "intent" in cockpit.NAV_MODES
    assert cockpit._design_groups is not None


def test_reselecting_design_keeps_the_open_artifact() -> None:
    """`startsWith`, not equality. Clicking Design while DES-0002 is open
    must not throw you back to the register — reselecting a mode is not a
    request to lose your place, and equality here would make it one."""
    src = _renderer()
    block = src.split("if (currentNavMode === 'intent') {")[1].split("const platform =")[0]
    assert "currentRel.startsWith('~design')" in block
    assert "currentRel === '~design'" not in block


def _design_branch(src: str) -> str:
    """The design branch of `loadWsNav`, as source.

    Read as text because the renderer is TypeScript and this suite is Python.
    That makes these assertions weaker than executing the code, so they are
    written to fail against the mutations that actually matter rather than to
    restate what the source says — ISS-0034 found three tests here that a
    permanently-unreachable mode passed unchanged.
    """
    return src.split("if (currentNavMode === 'intent') {")[1].split("const platform =")[0]


def test_the_guard_polarity_is_the_one_that_navigates() -> None:
    """The mutation that matters: inverting the guard to
    `if (currentRel && currentRel.startsWith('~design'))` makes the mode
    permanently unreachable by click while every other test stays green — it
    navigates only when already there. Asserting the negation explicitly is
    what a grep for `startsWith` could not do.
    """
    src = _renderer()
    block = _design_branch(src)
    before = block.split("void navigateTo('~design'")[0]
    guard = before.rsplit("if (", 1)[1].rsplit(")", 1)[0]

    # Two shapes are correct, and the test accepts both. A test that fails on
    # a semantically identical refactor trains people to weaken it, which is
    # how a guard stops guarding — so hoisting the condition to a named
    # boolean must pass, as long as the branch still fires on its NEGATION
    # and the name resolves to the same check.
    inline = "!currentRel" in guard and "!currentRel.startsWith('~design')" in guard
    hoisted = False
    m = re.fullmatch(r"!([A-Za-z_$][\w$]*)", guard.strip())
    if m:
        defn = re.search(r"(?:const|let)\s+%s\s*=([^;]+);" % re.escape(m.group(1)), src)
        # The definition's POLARITY matters, not just that it mentions the
        # check. Round 3 of independent review found the widened test admitted
        #   const notOnDesign = !!currentRel && !currentRel.startsWith('~design');
        #   if (!notOnDesign) { navigateTo('~design') }
        # which navigates only when nothing is open or when already on design —
        # ISS-0034's defect exactly, with the suite green. A hoisted name may
        # only mean "already on design", never its negation.
        hoisted = bool(
            defn
            and "currentRel.startsWith('~design')" in defn.group(1)
            and "!currentRel.startsWith('~design')" not in defn.group(1)
        )
    assert inline or hoisted, (
        "the guard around navigateTo is %r — it must fire when ~design is "
        "NOT already open. A guard that fires only when it IS never opens it."
        % guard
    )


def test_the_branch_actually_navigates() -> None:
    """Deleting the navigateTo call and leaving the branch and its comments
    behind also left 70 tests green. The call is the whole behaviour."""
    block = _design_branch(_renderer())
    assert "void navigateTo('~design'" in block, (
        "the design branch no longer navigates; selecting the mode would "
        "leave whatever page was already open"
    )


def test_the_route_the_mode_navigates_to_is_one_the_router_handles() -> None:
    """The wire, not the endpoints. Both reachability bugs in this surface
    were a control pointing at a url shape nothing downstream claimed, so the
    target string is checked against the router's own literal and against
    `extractRel`, which silently discarded `~design/...` once already."""
    src = _renderer()
    assert "normalised === '~design' || normalised.startsWith('~design/')" in src, (
        "the router no longer claims ~design; the mode would navigate nowhere"
    )
    rel = src.split("function extractRel(")[1].split("\n}")[0]
    assert "url.startsWith('~')" in rel and "return url;" in rel


def test_design_mode_still_fetches_the_nav() -> None:
    """Overview and Review return early — they are pages with no list. Design
    is both, so an early return here would leave the left pane showing
    whatever the previous mode put there."""
    src = _renderer()
    block = src.split("if (currentNavMode === 'intent') {")[1].split("const platform =")[0]
    assert "return;" not in block, (
        "design mode returned early; the nav list would never load"
    )


def test_designs_are_one_list_split_by_state_not_by_role(tmp_path: Path) -> None:
    """RETIRED SPLIT, kept as a guard against its return (ISS-0089).

    This used to assert `design-system` and `design-proposals` as separate
    groups, on the reasoning that "one standing reference and many
    transient ones behave differently" and the system would otherwise be
    buried.

    Measured against the real corpus, that produced a section containing
    exactly ONE note and scattered three designs across two headings, for
    a `role:` field the reader never asked about. Edwin: *"why do we need
    this design system section, why not just have these designs under
    completed?"*

    The split that matters is the one every other navigator makes —
    finished against live — and a design system note is simply a design
    that is `implemented`. `role:` still exists in frontmatter and is
    still read by the bench; it is no longer a navigation axis.
    """
    docs = tmp_path / "docs"
    _note(docs / "designs" / "DES-0001-System.md", {
        "type": "[[design]]", "id": "DES-0001", "title": "System",
        "status": "accepted", "role": "system"})
    _note(docs / "designs" / "DES-0002-Proposal.md", {
        "type": "[[design]]", "id": "DES-0002", "title": "Proposal",
        "status": "proposed", "role": "proposal"})
    idx = Index.build(docs)
    groups = cockpit.nav_payload(idx, mode="design")["groups"]
    groups = [g for g in groups if g["key"] != "standing"]
    assert [g["key"] for g in groups] == ["designs"], (
        "the role-based split is back; it put one note in a section of its own"
    )
    assert [i["id"] for i in groups[0]["items"]] == ["DES-0001", "DES-0002"]


def test_nav_items_point_at_the_bench_not_the_raw_note(tmp_path: Path) -> None:
    """The whole reason this mode exists: clicking a design in the Library
    did nothing, because the item pointed at a Markdown file the design
    surface never claimed. The url is overridden deliberately."""
    idx = Index.build(_corpus(tmp_path))
    groups = cockpit.nav_payload(idx, mode="design")["groups"]
    # Scoped to the `designs` group since TASK-0374: the view widened into the
    # project's constraints, and an ADR, a risk or a reference is a note rather
    # than a design — the bench has nothing to render for one, so those rows
    # correctly point at the note itself.
    designs = [i for g in groups if g["key"] == "designs" for i in g["items"]]
    assert designs, "the corpus has designs; the nav found none"
    for item in designs:
        assert item["url"].startswith("~design/"), item


def test_a_design_with_no_role_still_lists(tmp_path: Path) -> None:
    """`role:` used to decide which of two groups a design landed in, so a
    missing one had to default somewhere. With one list it decides
    nothing — but a design carrying no `role` must still appear, which is
    the half of the old guard still worth having.
    """
    docs = tmp_path / "docs"
    _note(docs / "designs" / "DES-0003-Nameless.md", {
        "type": "[[design]]", "id": "DES-0003", "title": "Nameless",
        "status": "draft"})
    idx = Index.build(docs)
    groups = [g for g in cockpit.nav_payload(idx, mode="design")["groups"]
              if g["key"] != "standing"]
    assert [g["key"] for g in groups] == ["designs"]
    assert [i["id"] for i in groups[0]["items"]] == ["DES-0003"]


def test_no_designs_yields_no_empty_headings(tmp_path: Path) -> None:
    """A project with no designs gets an empty pane, not two labelled boxes
    with nothing in them."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "README.md").write_text("# x\n", encoding="utf-8")
    idx = Index.build(docs)
    # The standing set is always present — every manifest entry renders,
    # missing ones included, which is TASK-0382's point. What must not appear
    # is an empty *designs* heading.
    groups = [g for g in cockpit.nav_payload(idx, mode="design")["groups"]
              if g["key"] != "standing"]
    assert groups == []


def test_the_mode_adds_and_removes_nothing() -> None:
    """This adds a seventh button; it must not quietly retire an existing one.
    A stored preference pointing at any prior mode still has to resolve, and
    the mode must not land in the retired list where it would be migrated
    away the moment someone selected it.

    TASK-0385 renamed the mode `design` -> `intent`, so the id under test is
    `intent`. `design` is now deliberately IN the retired list, mapped to
    `intent`, which is how an old stored preference migrates instead of
    falling through to the features default."""
    src = _renderer()
    for prior in ("overview", "features", "tasks", "issues", "review", "library"):
        assert "'%s'" % prior in src.split("const NAV_MODES = [")[1].split("]")[0]
    retired = src.split("const RETIRED_NAV_MODES: readonly string[] = [")[1].split("]")[0]
    assert "intent" not in retired, (
        "the live mode is in the retired list; selecting it would migrate it away"
    )
    assert "design" in retired, (
        "the old id must stay retired-and-mapped, or a stored `design` lands in "
        "the features fallback instead of on Intent"
    )
    assert "design: 'intent'," in src, "the retired `design` has no fallback target"
    assert "active" in retired and "recent" in retired, (
        "the retirement list changed; stored preferences would migrate differently"
    )


def test_the_button_is_keyboard_reachable_like_the_others() -> None:
    """No extra machinery: it is a real <button> with role=tab and an
    aria-label, so focus and Enter/Space already work. Asserted because a
    <div> with a click handler would look identical on screen and be
    unreachable without a mouse."""
    html = (Path(__file__).resolve().parents[1]
            / "desktop" / "src" / "renderer" / "index.html").read_text(encoding="utf-8")
    btn = re.search(r'<button[^>]*data-mode="intent"[^>]*>', html).group(0)
    assert btn.startswith("<button")
    assert 'role="tab"' in btn and 'aria-label="Intent"' in btn, (
        "the accessible name must be the name on screen — TASK-0385 renamed "
        "the view to Intent, and a screen reader saying 'Design' would be the "
        "rename half-done in the place it is hardest to notice"
    )


# ---- design rationale (TASK-0225) ----------------------------------------

def _rationale_corpus(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    _note(docs / "designs" / "DES-0001-Linked.md", {
        "type": "[[design]]", "id": "DES-0001", "title": "Linked",
        "status": "accepted", "role": "system",
        "related": ["[[ADR-0006-Retire-Band]]", "[[FEAT-0001]]"],
        "implements": ["[[ADR-0009-Notes-Authored]]"],
    })
    _note(docs / "designs" / "DES-0002-Bare.md", {
        "type": "[[design]]", "id": "DES-0002", "title": "Bare",
        "status": "proposed", "role": "proposal",
        "related": ["[[FEAT-0001]]"],
    })
    _note(docs / "designs" / "DES-0003-Broken.md", {
        "type": "[[design]]", "id": "DES-0003", "title": "Broken",
        "status": "draft", "role": "proposal",
        "related": ["[[ADR-9999-Nonexistent]]"],
    })
    _note(docs / "decisions" / "ADR-0006-Retire-Band.md", {
        "type": "[[adr]]", "id": "ADR-0006", "title": "Retire the delivered band",
        "status": "accepted",
        "decision": "Remove the delivered palette band from every status surface",
    })
    _note(docs / "decisions" / "ADR-0009-Notes-Authored.md", {
        "type": "[[adr]]", "id": "ADR-0009", "title": "Notes are the authored source",
        "status": "accepted",
        "decision": "Write a status once, in the note; the sync script propagates it",
    })
    # Governance. Linked by nothing, and must stay out of every design.
    _note(docs / "decisions" / "ADR-0011-Dated-Promotion.md", {
        "type": "[[adr]]", "id": "ADR-0011", "title": "Dated promotion of review warnings",
        "status": "accepted",
        "decision": "A review warning becomes an error on a fixed date",
    })
    return docs


def _rationale_for(tmp_path: Path, design_id: str) -> list:
    payload = cockpit.designs_payload(Index.build(_rationale_corpus(tmp_path)))
    return next(d for d in payload["designs"] if d["id"] == design_id)["rationale"]


def test_only_the_adrs_a_design_links_appear(tmp_path: Path) -> None:
    """The filter is the whole task. ADR-0011 is real, accepted, and sitting
    in the same corpus — it is process governance, and a design surface that
    lists it buries the two decisions that actually explain the design."""
    ids = [r["id"] for r in _rationale_for(tmp_path, "DES-0001")]
    assert ids == ["ADR-0009", "ADR-0006"], (
        "expected implements-then-related order, ADR-only, deduped"
    )
    assert "ADR-0011" not in ids


def test_non_adr_links_are_not_dragged_in(tmp_path: Path) -> None:
    """`related:` carries features, phases and issues too. This section is
    about decisions; everything else already has a place on the surface."""
    for entry in _rationale_for(tmp_path, "DES-0001"):
        assert entry["id"].startswith("ADR-"), entry


def test_a_design_linking_no_adrs_gets_nothing(tmp_path: Path) -> None:
    """Not an empty section. An empty 'Rationale' heading reads as 'no
    decisions were made here', which is a claim; absence is not."""
    assert _rationale_for(tmp_path, "DES-0002") == []
    src = _renderer()
    block = src.split("function buildDesignRationale(")[1].split("\nfunction ")[0]
    assert "if (!entries.length) return null;" in block
    # Appended only when non-null, so a design with no linked ADRs gets no
    # heading at all. It now lands in the shell sidebar rather than the page.
    assert "if (rationale) side.append(rationale);" in src


def test_the_line_is_the_adrs_own_decision_field(tmp_path: Path) -> None:
    """The sentence its author wrote to be quoted — never a paraphrase. A
    generated summary of a decision is the kind of confident restatement that
    misleads exactly where accuracy matters."""
    entry = next(r for r in _rationale_for(tmp_path, "DES-0001") if r["id"] == "ADR-0006")
    assert entry["decision"] == (
        "Remove the delivered palette band from every status surface")
    assert entry["url"], "no url; the entry cannot open the ADR"
    src = _renderer()
    assert "r.decision || r.title || r.id" in src, (
        "the fallback chain changed; it must degrade to the title and then the "
        "id, and never to a generated summary"
    )


def test_a_broken_adr_link_is_reported_not_dropped(tmp_path: Path) -> None:
    """Silently omitting it hides a typo in the note's own frontmatter — and
    the reason this resolves through the link graph rather than a title
    heuristic is that links are checkable in a way guesses are not."""
    entries = _rationale_for(tmp_path, "DES-0003")
    assert [e["id"] for e in entries] == ["ADR-9999"]
    assert entries[0]["missing"] is True
    assert entries[0]["decision"] == ""
    src = _renderer()
    assert "is linked but no such note exists" in src


def test_resolution_is_by_link_never_by_title(tmp_path: Path) -> None:
    """A title-substring match was tried once in the review desk and removed
    in independent review: a guess that is usually right is worse than an
    explicit link, because nobody can tell when it is wrong."""
    body = inspect.getsource(cockpit._design_rationale)
    for heuristic in ("in record.title", "title.lower()", "startswith(d[\"title\"]"):
        assert heuristic not in body, (
            "rationale resolution reads titles; it must read links only"
        )
    assert "index.by_id(" in body


def test_the_real_corpus_matches_what_the_task_predicted() -> None:
    """DES-0001 links ADR-0006 and DES-0002 links none — written into the task
    note before the code existed. Asserting it here means the feature is
    verified against the project it ships in, not only against fixtures."""
    docs = Path(__file__).resolve().parents[1] / "docs"
    payload = cockpit.designs_payload(Index.build(docs))
    by_id = {d["id"]: d for d in payload["designs"]}
    assert [r["id"] for r in by_id["DES-0001"]["rationale"]] == ["ADR-0006"]
    assert by_id["DES-0002"]["rationale"] == []
    assert by_id["DES-0001"]["rationale"][0]["decision"].startswith("Remove the")


# ---- the identity band's link actually resolves (ISS-0033) ---------------

def _serve(docs: Path):
    """A real server on an ephemeral port.

    Deliberately end-to-end. ISS-0033 was a control pointing at a url the
    render endpoint refused, and the fix looked correct as a one-line
    allowlist addition — until it was curled and still 404'd, because the
    handler never consulted the allowlist. Only the wire tells you that.
    """
    import threading
    from project_os_cockpit.server import (
        DocsServer, _NoDNSThreadingHTTPServer, _make_handler,
    )
    server = DocsServer(docs_root=docs, bind="127.0.0.1", port=0)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0),
        _make_handler(server.docs_root, server.index, server.bus,
                      cockpit_state=server.cockpit_state),
    )
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def _render(port: int, rel: str) -> dict:
    import urllib.error
    import urllib.parse
    import urllib.request
    url = ("http://127.0.0.1:%d/api/render?path=%s"
           % (port, urllib.parse.quote(rel)))
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return json.loads(exc.read())


def test_the_brief_link_resolves_over_http(tmp_path: Path) -> None:
    """The identity band's only link, exercised the way a click exercises it.

    It navigated to `LLM_BRIEF.md`, which lives one level ABOVE docs_root, and
    the endpoint answered `not a markdown file` — sending the renderer into
    mountPlaceholder, which REPLACES the design surface with "No note here".
    Asserting the button's label would never have caught it.
    """
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "README.md").write_text("# hi\n", encoding="utf-8")
    (tmp_path / "LLM_BRIEF.md").write_text(
        "# LLM Brief\n\n## Project Identity\n- Name: fixture\n"
        "- Purpose: to be opened\n", encoding="utf-8")
    httpd, port = _serve(docs)
    try:
        got = _render(port, "LLM_BRIEF.md")
        assert got.get("ok") is not False, got
        assert got["rel_path"] == "LLM_BRIEF.md"
        assert "fixture" in got["html"]

        # The same defect existed for the Library's README row all along;
        # the allowlist was never consulted by this endpoint.
        assert _render(port, "README.md").get("ok") is not False

        # Widening stops at the allowlist. A root file that is NOT on it
        # stays refused, and traversal stays blocked.
        (tmp_path / "SECRETS.md").write_text("# no\n", encoding="utf-8")
        assert _render(port, "SECRETS.md").get("ok") is False
        assert _render(port, "../SECRETS.md").get("ok") is False
    finally:
        httpd.shutdown()


def test_the_renderer_does_not_route_bare_root_urls() -> None:
    """Routing `/README.md` looked like a free bonus while closing ISS-0033
    and was not: `/docs/README.md` and `/README.md` both reduce to
    `README.md`, so two distinct Library rows collapsed onto one fetch. Those
    rows stay dead clicks (ISS-0037) until the rel carries the disambiguator
    the url already has. The identity band is unaffected — it calls
    `navigateTo(brief.rel)` directly and never passes through here."""
    src = _renderer()
    rel = src.split("function extractRel(")[1].split("\n}")[0]
    assert ".test(url)" not in rel, (
        "extractRel routes a bare root url again; `/docs/X.md` and `/X.md` "
        "collide on one rel and the server decides which file you get"
    )


# ---- resolution order (ISS-0036) -----------------------------------------

def test_the_docs_note_wins_over_the_root_file(tmp_path: Path) -> None:
    """`docs/README.md` is a real note in this repo. The first version of the
    root-file branch tested the allowlist AFTER stripping the `docs/` prefix
    and resolved the root allowlist FIRST, so an explicit, unambiguous request
    for the docs note was answered with the project-root README.

    Both halves are asserted: the disambiguator is kept, and docs_root is
    tried first — either one alone leaves a shadow in one direction.
    """
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "README.md").write_text("# docs one\ndocs-body\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# root one\nroot-body\n", encoding="utf-8")
    (tmp_path / "LLM_BRIEF.md").write_text(
        "# LLM Brief\n\n## Project Identity\n- Name: fixture\n"
        "- Purpose: to be opened\n", encoding="utf-8")
    httpd, port = _serve(docs)
    try:
        for asked in ("docs/README.md", "/docs/README.md", "README.md"):
            got = _render(port, asked)
            assert "docs-body" in got.get("html", ""), (
                "%s resolved to the project-root README, shadowing a real "
                "note" % asked
            )
        # The root file is reachable exactly when docs has no file by that
        # name — which is the true state of affairs for the brief.
        assert "fixture" in _render(port, "LLM_BRIEF.md")["html"]
    finally:
        httpd.shutdown()


# ---- the remaining round-2 findings --------------------------------------

def test_a_placeholder_heading_is_scrubbed_too(tmp_path: Path) -> None:
    """The heading is a renderable field. The first fix enumerated name,
    purpose and body — one field short of the contract its own docstring
    stated, which is the same shape as the defect it closed."""
    b = _brief(tmp_path, "# B\n\n## REPLACE ME\nreal body here\n\n## Real\ncontent\n")
    for s in b["sections"]:
        assert "REPLACE" not in s["heading"].upper()
        assert "REPLACE" not in s["body"].upper()
    # The unwritten HEADING is dropped; the real body under it survives. The
    # first version discarded the whole section, which contradicted the
    # per-line body policy — dropping real content because its heading was
    # left unwritten (round 3 independent review).
    assert any(s["body"] == "real body here" and s["heading"] == ""
               for s in b["sections"]), b["sections"]
    assert any(s["heading"] == "Real" for s in b["sections"])


def test_a_section_that_is_only_a_placeholder_disappears(tmp_path: Path) -> None:
    """Nothing named, nothing said — there is no content to preserve."""
    b = _brief(tmp_path, "# B\n\n## REPLACE ME\nREPLACE ME\n\n## Real\ncontent\n")
    assert [s["heading"] for s in b["sections"]] == ["Real"]


def test_a_hand_written_prose_brief_is_filled(tmp_path: Path) -> None:
    """No `- Name:` bullets, no placeholders, real content — a finished brief
    written by someone who never adopted the convention. Calling it unfilled
    would hold the author to a parser's convenience and contradict the
    payload's own promise of tolerant parsing."""
    b = _brief(tmp_path, "# Brief\n\n## What this is\n"
                         "A long-form description written by hand.\n")
    assert b["state"] == "filled"
    assert b["name"] == "" and b["placeholders"] == 0


def test_an_empty_brief_is_still_unfilled(tmp_path: Path) -> None:
    """The `nothing left to fill` clause must not swallow a file with nothing
    IN it — zero placeholders and zero content is not a finished brief."""
    assert _brief(tmp_path, "# Brief\n")["state"] == "unfilled"


def test_a_filled_brief_still_reports_residual_placeholders() -> None:
    """`state: filled, placeholders: 1` rendered as simply complete. The
    surface being the feedback loop is this feature's whole thesis — a brief
    nobody is told about is what left 10 of 11 fleet repos unfilled."""
    src = _renderer()
    band = src.split("function buildIdentityBand(")[1].split("\nasync function")[0]
    filled = band.split("return band;", 1)[1]
    assert "brief.placeholders" in filled, (
        "the filled branch never mentions residual placeholders"
    )
    assert "still template placeholders" in filled


# ---- app-shell layout (ISS-0039 / TASK-0226) -----------------------------

def test_height_follows_the_same_absence_rule_as_width() -> None:
    """`declared` honoured an absent viewport for width and ignored it for
    height, so a document — the case that should scroll freely — was forced
    into a 900px window inside a scrolling page. A declared viewport still
    keeps its fixed height: the framing IS the point."""
    src = _renderer()
    assert ("const framedHeight = preset.key === 'declared' "
            "? (d.viewport ? preset.h : null) : preset.h;") in src
    assert "else frame.style.height = '100%';" in src


def test_fill_actually_fills() -> None:
    """`Fill` set w and h to null, so no height was applied and
    `.design-frame { min-height: 320px }` won — a preset named Fill rendered
    a 320px box."""
    src = _renderer()
    presets = src.split("const DESIGN_VIEWPORTS")[1].split("];")[0]
    assert "{ key: 'fill', label: 'Fill', w: null, h: null }" in presets
    # With w and h null, both axes now resolve to 100% of the shell-sized
    # stage rather than to the iframe's intrinsic default.
    assert "frame.style.width = '100%';" in src


def test_the_shell_class_is_cleared_when_leaving_a_design(tmp_path: Path) -> None:
    """`design-page` was never removed from #doc-view. Harmless while it only
    added padding; adding `overflow: hidden` to the same element would have
    stopped EVERY subsequent page scrolling. Both classes now come off at
    each site that switches away."""
    src = _renderer()
    switches = src.count("'design-page', 'is-design-shell'")
    assert switches >= 4, (
        "only %d page-switch sites clear the shell class; a stale "
        "`is-design-shell` freezes scrolling on whatever page comes next"
        % switches
    )
    # The register is a list and must keep scrolling.
    assert "docView.classList.remove('is-design-shell');" in src


def test_the_sidebar_holds_the_rail_and_rationale_not_the_stage() -> None:
    """They used to sit under the frame in the page's scroller. In a shell
    there is no page scroller, so anything left there is unreachable."""
    src = _renderer()
    paint = src.split("const paint = () => {")[1].split("\n  };")[0]
    assert "side.append(buildDesignRevisionRail(d, paint));" in paint
    assert "side.append(rationale);" in paint
    assert "root.append(head, stage);" in paint
    assert "const head = buildDesignHeader(d, paint);" in paint


def test_the_layout_harness_runs_the_real_bundle() -> None:
    """Layout defects are invisible to every test in this file — all of them
    read a payload or a line of source, and pytest cannot measure a box.

    The first harness measured a DOM written **by hand**. It passed while the
    surface was still wrong on screen, because a mock cannot reproduce the
    height chain that matters (`.stage > .stage-main > .doc-view`), the real
    stylesheet order, or what `paint()` actually builds. So the assertion here
    is not "a harness exists" but "the harness loads the shipped bundle" — a
    harness that can pass while the app is broken is worse than none.
    """
    harness = (Path(__file__).resolve().parents[1]
               / "desktop" / "harness" / "design-harness.html")
    assert harness.is_file(), "the design harness was deleted"
    text = harness.read_text(encoding="utf-8")
    assert "../dist/renderer/renderer.js" in text, (
        "the harness no longer loads the real bundle; it is a mock again"
    )
    for css in ("base.css", "cockpit.css", "renderer.css"):
        assert "../dist/renderer/" + css in text, css
    assert "no scroller nests inside another" in text
    assert "the page does not scroll" in text
    assert "collapsing the sidebar gives the artifact the pane" in text
    # The stub bridge must stay complete: one missing namespace throws at
    # module scope and the bundle stops, which the harness then reports as
    # "the surface does not render" — a false negative that cost a round.
    for ns in ("onMenuDispatch", "workspaces", "sidecar", "dispatch", "terminal"):
        assert ns in text, ns


def test_the_details_sidebar_can_be_collapsed() -> None:
    """Measured against the real renderer: a 1356px pane left the frame at
    1036px, and DES-0001's dossier is authored at 1240px — so the design
    scrolled sideways inside its own frame. Collapsed, the frame reaches
    1312px and the horizontal scroll is gone."""
    src = _renderer()
    assert "cockpit:design-side" in src, "the choice does not persist"
    assert "toggle.className = 'design-side-toggle';" in src
    # The control must live in the HEAD, not the sidebar: a toggle that
    # disappears with the thing it toggles cannot bring it back.
    paint = src.split("const paint = () => {")[1].split("\n  };")[0]
    assert "head.append(toggle);" in paint
    assert "side.append(toggle)" not in paint


# ---- a design with no artifact must still lead somewhere (ISS-0041) ------

def test_an_artifactless_design_can_still_be_read() -> None:
    """DES-0002 is the design SYSTEM and its entire content is prose. With
    `asset: ""` the stage rendered "declares no artifact yet" and stopped —
    Edwin: "I cannot open it in the tool". The note banner pointed at the
    bench and nothing pointed back, so the system was readable only outside
    the app that exists to show it."""
    src = _renderer()
    assert "Read ${d.id} as a note" in src, (
        "the empty stage offers no way through to the prose"
    )
    # And from any design, artifact or not: the id chip is the link.
    assert "idChip.setAttribute('role', 'link');" in src
    assert "const openNote = () => { void navigateTo(d.rel); };" in src
    # Keyboard-reachable, since it is a span rather than a real <a>.
    assert "e.key === 'Enter' || e.key === ' '" in src


def test_the_no_artifact_path_stays_covered(tmp_path: Path) -> None:
    """Was grounded in DES-0002, which declared no asset. TASK-0228 gave it
    one, so this moved to a fixture rather than being deleted — the note said
    so itself when the premise still held. A design may legitimately have no
    artifact (a proposal being written), and that path still needs a door."""
    docs = tmp_path / "docs"
    _note(docs / "designs" / "DES-0009-No-Artifact.md", {
        "type": "[[design]]", "id": "DES-0009", "title": "Nothing yet",
        "status": "draft", "role": "proposal", "asset": "",
    })
    payload = cockpit.designs_payload(Index.build(docs))
    record = payload["designs"][0]
    assert record["has_asset"] is False
    assert record["rel"].endswith(".md"), (
        "the empty stage links to `rel`; without it there is no way through"
    )


def test_the_empty_stage_does_not_stretch_its_message() -> None:
    """The stage stretches its children so an iframe can fill it — applied to
    a one-line button that made a full-height slab (Edwin, 2026-07-28).
    Measured after the fix: 25px button in a 765px stage."""
    src = _renderer()
    assert src.count("wrap.classList.add('is-empty');") == 2, (
        "both empty branches (no asset declared, asset missing) must opt out "
        "of the stretch"
    )
    css = (Path(__file__).resolve().parents[1]
           / "desktop" / "src" / "renderer" / "renderer.css").read_text(encoding="utf-8")
    assert ".design-stage.is-empty" in css


def test_the_design_page_fills_the_context_pane() -> None:
    """It cleared the right pane and never refilled it, so a design note's
    real links were invisible on the surface built to show the design —
    DES-0002 names DES-0001, TST-0019, ISS-0023 and REQ-0022. The context
    endpoint already answers this for any note; the page never asked."""
    src = _renderer()
    page = src.split("async function renderDesignPage(")[1].split("\nasync function")[0]
    assert "void loadRightPane(d.rel);" in page, (
        "the design page clears the context pane without refilling it"
    )


def test_the_harness_covers_the_empty_stage() -> None:
    """A design with no artifact is its own layout case — a message, not a
    surface — and the case the register's only artifactless design exercises."""
    harness = (Path(__file__).resolve().parents[1]
               / "desktop" / "harness" / "design-harness.html").read_text(encoding="utf-8")
    assert "#empty" in harness
    assert "the button is not a full-height slab" in harness
    assert "the context pane carries the note" in harness


# ---- the shell stylesheet route (TASK-0227) ------------------------------

def _serve_with_shell(docs: Path, shell: Path | None):
    import threading
    from project_os_cockpit.server import (
        DocsServer, _NoDNSThreadingHTTPServer, _make_handler,
    )
    server = DocsServer(docs_root=docs, bind="127.0.0.1", port=0,
                        shell_assets=shell)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0),
        _make_handler(server.docs_root, server.index, server.bus,
                      cockpit_state=server.cockpit_state,
                      shell_assets=server.shell_assets))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def _raw(port: int, path: str) -> tuple[int, bytes]:
    import urllib.error
    import urllib.request
    try:
        with urllib.request.urlopen(
                "http://127.0.0.1:%d%s" % (port, path), timeout=5) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def _mini_docs(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "README.md").write_text("# hi\n", encoding="utf-8")
    return docs


def test_the_shell_stylesheet_is_served_when_the_path_is_given(tmp_path: Path) -> None:
    """A design artifact is served from the SIDECAR origin, so a <link> inside
    it resolves against the sidecar — which knew about base.css and cockpit.css
    and had never heard of renderer.css, where every widget style lives."""
    shell = tmp_path / "shell"
    shell.mkdir()
    (shell / "renderer.css").write_text(".design-chip { color: red }", encoding="utf-8")
    httpd, port = _serve_with_shell(_mini_docs(tmp_path), shell)
    try:
        status, body = _raw(port, "/_shell/renderer.css")
        assert status == 200, status
        assert b"design-chip" in body
    finally:
        httpd.shutdown()


def test_no_copy_of_the_stylesheet_is_made() -> None:
    """Serve, never copy. A second copy of a stylesheet is precisely the drift
    this project was founded on (ISS-0023), and the design system is the last
    place that should carry one."""
    pkg_static = (Path(__file__).resolve().parents[1]
                  / "src" / "project_os_cockpit" / "static")
    assert not (pkg_static / "renderer.css").exists(), (
        "renderer.css was copied into the package's static dir; it must be "
        "SERVED from the desktop build, not duplicated"
    )


def test_mode_1_degrades_to_404_rather_than_erroring(tmp_path: Path) -> None:
    """The sidecar runs without the desktop app at all. Absence is a normal
    state here, not a fault — so it must not be a hard dependency and must not
    raise."""
    httpd, port = _serve_with_shell(_mini_docs(tmp_path), None)
    try:
        status, _ = _raw(port, "/_shell/renderer.css")
        assert status == 404, status
        # And the rest of the server is unaffected.
        assert _raw(port, "/healthz")[0] == 200
    finally:
        httpd.shutdown()


def test_the_route_is_an_allow_list_not_a_directory_share(tmp_path: Path) -> None:
    """The design surface needs the stylesheet. Nothing about that is a reason
    to expose the bundle, its source maps, or anything else the build emits."""
    shell = tmp_path / "shell"
    shell.mkdir()
    (shell / "renderer.css").write_text("ok", encoding="utf-8")
    (shell / "renderer.js").write_text("console.log(1)", encoding="utf-8")
    (shell / "renderer.js.map").write_text("{}", encoding="utf-8")
    httpd, port = _serve_with_shell(_mini_docs(tmp_path), shell)
    try:
        assert _raw(port, "/_shell/renderer.css")[0] == 200
        for denied in ("renderer.js", "renderer.js.map", "index.html"):
            assert _raw(port, "/_shell/" + denied)[0] == 404, denied
    finally:
        httpd.shutdown()


def test_traversal_and_escape_are_refused(tmp_path: Path) -> None:
    """The guards are `_serve_static`'s, reused rather than re-derived — this
    route must not become the one place traversal checking was rewritten
    slightly differently."""
    shell = tmp_path / "shell"
    shell.mkdir()
    (shell / "renderer.css").write_text("ok", encoding="utf-8")
    (tmp_path / "secret.css").write_text("leaked", encoding="utf-8")
    httpd, port = _serve_with_shell(_mini_docs(tmp_path), shell)
    try:
        for attack in ("/_shell/../secret.css", "/_shell/..%2Fsecret.css",
                       "/_shell/", "/_shell/sub/renderer.css"):
            status, body = _raw(port, attack)
            assert status in (403, 404), (attack, status)
            assert b"leaked" not in body, attack
    finally:
        httpd.shutdown()


def test_the_desktop_passes_the_path_and_derives_it_once() -> None:
    """`main.ts` already loads `renderer/index.html` relative to __dirname;
    deriving the assets path a second way would let it drift from the one the
    window actually loads."""
    sidecar = (Path(__file__).resolve().parents[1]
               / "desktop" / "src" / "ipc" / "sidecar.ts").read_text(encoding="utf-8")
    assert "'--shell-assets'" in sidecar
    assert "function shellAssetsPath()" in sidecar
    assert "existsSync(path.join(dir, 'renderer.css'))" in sidecar, (
        "the path is passed without checking the file is there; mode-1 and a "
        "half-built tree would both send a bad path"
    )


# ---- the living style guide (TASK-0228) ----------------------------------

def _code_only(js: str) -> str:
    """JS with comments stripped.

    Three tests in this file have now matched their own explanatory prose
    instead of the code — a comment quoting the bug it warns about reads
    exactly like the bug. Strip once, in one place.
    """
    js = re.sub(r"/\*.*?\*/", "", js, flags=re.S)
    return re.sub(r"^\s*//.*$", "", js, flags=re.M)


def _style_guide() -> str:
    return (Path(__file__).resolve().parents[1] / "docs" / "designs"
            / "DES-0002-style-guide.html").read_text(encoding="utf-8")


def test_the_style_guide_types_no_values() -> None:
    """The whole argument for the page: the status palette is already stated
    in base.css with membership in statuses.py, kept in agreement by TST-0019.
    A hand-typed swatch page would be the FOURTH statement and the one place
    with no check. Read from source, drift is impossible rather than caught."""
    html = _style_guide()
    body = html.split("<script>", 1)[1]
    # No literal colours anywhere in the logic.
    assert not re.search(r"#[0-9A-Fa-f]{6}\b", body), (
        "a hex colour is typed into the style guide; every value must be read"
    )
    assert not re.search(r"\bhsl\(\s*\d", body), "an hsl value is typed in"
    #  was the original mechanism and is deliberately gone:
    # a probe inherits the document theme, so it could not read both schemes
    # once the app started handing this page a dark one. Reading declarations
    # is what replaced it.
    for mechanism in ("document.styleSheets", "getPropertyValue", "cssRules"):
        assert mechanism in body, mechanism


def test_band_membership_is_read_from_css_too() -> None:
    """base.css states membership as `.status-chip[data-status="x"] { color:
    var(--status-y) }`, so the page reports the counts without a list of
    statuses existing anywhere inside it."""
    body = _style_guide().split("<script>", 1)[1]
    assert 'data-status="([^"]+)"' in body
    assert "var\\((--status-[a-z]+)\\)" in body or "--status-[a-z]+" in body


def test_no_top_level_declaration_shadows_a_window_property() -> None:
    """`const top` is a SyntaxError — `top` is a non-configurable window
    property — and it killed the entire script silently. `node --check` passed
    it, because Node has no window. This is the check that would have."""
    body = _style_guide().split("<script>", 1)[1].rsplit("</script>", 1)[0]
    declared = set(re.findall(
        r"^(?:const|let|var|function)\s+([A-Za-z_$][\w$]*)", body, re.M))
    reserved = {
        "top", "self", "parent", "name", "status", "length", "location",
        "history", "origin", "screen", "closed", "frames", "event", "opener",
        "window", "document", "external", "menubar", "toolbar", "scrollbars",
        "personalbar", "locationbar", "statusbar", "frameElement",
    }
    clash = declared & reserved
    assert not clash, (
        "top-level %s shadows a non-configurable window property; the whole "
        "script becomes a SyntaxError and the page renders blank" % sorted(clash)
    )


def test_the_gaps_and_the_degraded_path_are_stated() -> None:
    """DES-0002 records that there is no type scale and no spacing scale. An
    invented scale would be worse than the gap. And with the shell stylesheet
    absent (mode-1), unstyled markup would read as a design regression."""
    html = _style_guide()
    assert "No declared type scale" in html
    assert "No spacing tokens exist" in html
    assert "The widget gallery needs the desktop shell" in html
    assert "shellPresent" in html


def test_zero_is_not_counted_as_spacing() -> None:
    """`0px` topped the distribution at 154 uses — a reset, not a spacing
    decision, and it said nothing about density."""
    assert "if (px !== '0px')" in _style_guide()


def test_des_0002_now_has_its_artifact() -> None:
    """The note said of itself that the page did not exist yet and that it
    would stay draft until it rendered."""
    docs = Path(__file__).resolve().parents[1] / "docs"
    payload = cockpit.designs_payload(Index.build(docs))
    system = next(d for d in payload["designs"] if d["id"] == "DES-0002")
    assert system["has_asset"] is True
    assert system["asset"].endswith("DES-0002-style-guide.html")
    assert system["status"] == "implemented"


# ---- the sandboxed frame can still read tokens (ISS-0043) ----------------

def test_stylesheets_are_fetchable_from_an_opaque_origin(tmp_path: Path) -> None:
    """The design frame is sandboxed WITHOUT allow-same-origin, so it has an
    opaque origin and `cssRules` on same-server stylesheets throws. The page
    re-injects them as inline sheets, and that fetch needs CORS."""
    shell = tmp_path / "shell"
    shell.mkdir()
    (shell / "renderer.css").write_text(".x{}", encoding="utf-8")
    httpd, port = _serve_with_shell(_mini_docs(tmp_path), shell)
    import urllib.request
    try:
        for path in ("/_static/base.css", "/_shell/renderer.css"):
            with urllib.request.urlopen(
                    "http://127.0.0.1:%d%s" % (port, path), timeout=5) as r:
                assert r.headers.get("Access-Control-Allow-Origin") == "*", path
    finally:
        httpd.shutdown()


def test_cors_is_css_only(tmp_path: Path) -> None:
    """Narrowed deliberately: this must not become blanket CORS on every
    static file the package ships."""
    httpd, port = _serve_with_shell(_mini_docs(tmp_path), None)
    import urllib.request
    try:
        with urllib.request.urlopen(
                "http://127.0.0.1:%d/_static/cockpit.js" % port, timeout=5) as r:
            assert r.headers.get("Access-Control-Allow-Origin") is None, (
                "cockpit.js carries CORS; the allowance is for stylesheets"
            )
    finally:
        httpd.shutdown()


def test_the_guide_reinjects_rather_than_weakening_the_sandbox() -> None:
    """The repair must not be `allow-same-origin`. A frame with both flags can
    remove its own sandbox, which is why the frame test exists at all."""
    html = _style_guide()
    assert "reinjectBlocked" in html
    assert "data-reinjected-from" in html
    src = _renderer()
    assert "allow-same-origin" not in src, (
        "the sandbox was widened to fix a CSS-reading problem; re-inject the "
        "stylesheet instead"
    )


def test_the_guide_never_fails_blank() -> None:
    """A blank page is the worst failure mode for a page whose job is to show
    things — and blank is exactly what this shipped as."""
    assert "failed to build itself" in _style_guide()


# ---- theme, fit and margins (ISS-0044) -----------------------------------

def test_the_theme_travels_in_the_url() -> None:
    """The artifact is sandboxed with an opaque origin: it can reach neither
    the parent nor localStorage, so the URL is the only channel. A page that
    documents both schemes sitting light inside a dark cockpit looked wrong,
    and an artifact is free to ignore the hint."""
    src = _renderer()
    assert "?theme=${document.documentElement.dataset.theme" in src
    guide = _style_guide()
    assert "new URLSearchParams(location.search).get('theme')" in guide


def test_both_palettes_are_read_from_declarations_not_a_probe() -> None:
    """A probe cannot escape the document's own theme — light is the `:root`
    default and only `[data-theme="dark"]` exists — so once the app started
    handing this page a dark theme, the LIGHT column silently showed dark
    values. Reading the declarations is theme-independent."""
    guide = _style_guide()
    assert "function paletteMaps()" in guide
    assert "getComputedStyle(probe)" not in guide


def test_root_detection_accepts_a_bare_data_theme_selector() -> None:
    """base.css writes its dark block as a BARE `[data-theme="dark"]` while
    renderer.css writes `:root[data-theme="dark"]`. Requiring the `:root`
    skipped base.css's dark palette entirely, and the dark column showed light
    values for every token the shell does not override."""
    guide = _style_guide()
    assert "isRootish" in guide
    assert "data-theme=[\"']?[\\w-]+[\"']?" in guide


def test_a_framed_design_is_scaled_rather_than_scrolled() -> None:
    """A 900px frame in a ~767px stage made the stage a second scroller, and
    centred in a wide pane it left a broad dead zone either side of the design
    where the wheel moved that stage a few pixels instead of the artifact."""
    src = _renderer()
    assert "Math.min(1, box.height / framedHeight, box.width / width)" in src
    assert "new ResizeObserver(fit)" in src
    css = (Path(__file__).resolve().parents[1] / "desktop" / "src" / "renderer"
           / "renderer.css").read_text(encoding="utf-8")
    framed = css.split(".design-shell-body .design-stage.is-framed {")[1].split("}")[0]
    assert "overflow: hidden" in framed, (
        "the framed stage is a scroller again; scaling exists so it is not"
    )


def test_the_viewport_chooser_is_only_for_surfaces() -> None:
    """`viewport:` absence already means "this is a document, let it flow" for
    the width, the height and the framing. The chrome had not been told, so a
    document rendered a five-button bar of which four were disabled."""
    src = _renderer()
    head = src.split("function buildDesignHeader(")[1].split("\nfunction ")[0]
    assert "if (d.viewport) {" in head
    assert "b.disabled = true" not in head, (
        "the bar is rendered-then-disabled again; it should not be rendered"
    )


def test_the_design_system_is_a_document_not_a_surface() -> None:
    """DES-0002 declared `viewport: 900`, recording the height REQ-0022
    asserts rather than a width the artifact is drawn at. That one wrong field
    framed a scrolling reference page inside a 900px window."""
    docs = Path(__file__).resolve().parents[1] / "docs"
    system = next(d for d in cockpit.designs_payload(Index.build(docs))["designs"]
                  if d["id"] == "DES-0002")
    assert system["viewport"] is None, (
        "the style guide declares a viewport again; it is a document"
    )


def test_an_artifact_resets_the_shell_body_it_inherits() -> None:
    """base.css declares `body { height: 100dvh; display: flex; overflow:
    hidden }` and renderer.css adds `body { display: block; overflow: hidden }`
    — correct for a window that owns the viewport, fatal for a document. The
    first artifact to link them rendered fully and could not be scrolled a
    pixel: 4792px of content clipped to a 963px viewport (ISS-0046)."""
    guide = _style_guide()
    style = guide.split('<style id="own-styles">', 1)[1].split("</style>", 1)[0]
    # Strip CSS comments first: the block above this rule QUOTES base.css's
    # `overflow: hidden`, and matching one's own explanatory prose instead of
    # the code is a mistake this suite has already made once.
    style = re.sub(r"/\*.*?\*/", "", style, flags=re.S)
    body_rule = style.split("body {", 1)[1].split("}", 1)[0]
    assert "overflow: visible" in body_rule, (
        "the artifact does not reset the shell's `overflow: hidden`; it will "
        "render everything and scroll nothing"
    )
    assert "display: block" in body_rule
    assert "height: auto" in body_rule
    assert "html { height: auto; overflow: visible; }" in style
    # No shouting: source order is enough, and !important here would mean the
    # stylesheet is being misused rather than borrowed.
    assert "!important" not in style


def test_the_authoring_contract_carries_the_rule() -> None:
    """Not a patch in one page: this is the standing cost of TASK-0227, and
    every future artifact wanting real widgets pays it."""
    contract = (Path(__file__).resolve().parents[1] / "docs" / "features"
                / "design-bench" / "plan" / "tasks"
                / "TASK-0221-Design-Authoring-Contract.md").read_text(encoding="utf-8")
    assert "inheriting the application's shell" in contract
    assert "overflow: visible" in contract


def test_reinjected_sheets_go_before_the_artifacts_own_styles() -> None:
    """ISS-0043's repair appended the fetched app stylesheets to <head>, which
    put `body { overflow: hidden }` AFTER the reset ISS-0046 added to undo it.
    The reset lost on source order and the page could not scroll — two correct
    fixes cancelling out. Borrowed styles first, author styles last."""
    guide = _style_guide()
    assert 'id="own-styles"' in guide, (
        "the page's own <style> is unmarked, so re-injection cannot position "
        "itself relative to it"
    )
    assert "document.head.insertBefore(el, document.getElementById('own-styles'));" in guide
    assert "document.head.appendChild(el)" not in guide, (
        "re-injection appends again; the app's shell rules will outrank the "
        "artifact's reset"
    )


def test_token_values_never_reach_an_html_parser() -> None:
    """`--icon-folder` holds `url("data:image/svg+xml;utf8,<svg …>")`. Built by
    string concatenation into innerHTML, the quote closed the style attribute
    and the SVG was parsed as markup — 16 stray elements in the palette. A
    value read from a stylesheet is DATA (ISS-0048)."""
    body = _code_only(_style_guide().split("<script>", 1)[1])
    assert "swatchRow" in body and "createElement('i')" in body
    for banned in ("'<div class=\"sw\"", "style=\"background:'", "innerHTML = '<div"):
        assert banned not in body, banned
    # The value goes through textContent and style APIs, never markup.
    assert "label.textContent = name;" in body
    assert "chip.style.setProperty('mask-image', value);" in body


def test_a_token_is_not_assumed_to_be_a_colour() -> None:
    """Assets (`url(…)`, used as mask-image) and shadow triples are not
    colours; painting them as backgrounds said nothing and printed hundreds of
    characters of data URI into the value column."""
    body = _style_guide().split("<script>", 1)[1]
    assert "function tokenKind(" in body
    assert "'asset'" in body and "'shadow'" in body and "'colour'" in body
    assert "url(data:image/svg+xml …)" in body, (
        "the raw data URI is printed again; it is payload, not a value"
    )


# ---- review findings F2 / F3 / F5 ----------------------------------------

def test_the_asset_route_declares_utf8(tmp_path: Path) -> None:
    """`guess_type` returns `text/html` with no charset, while the HISTORICAL
    route hard-codes utf-8 — so the same bytes decoded two ways and
    revision-compare showed an encoding difference as a design difference
    (ISS-0050). Asked over HTTP, because the previous guard grepped the
    handler's source and could not see a header that was absent."""
    docs = tmp_path / "docs"
    (docs / "designs").mkdir(parents=True)
    (docs / "README.md").write_text("# x\n", encoding="utf-8")
    _note(docs / "designs" / "DES-0001-Enc.md", {
        "type": "[[design]]", "id": "DES-0001", "title": "Enc",
        "status": "draft", "role": "proposal", "asset": "enc.html"})
    # No <meta charset> — exactly DES-0001's shape.
    (docs / "designs" / "enc.html").write_text(
        "<h1>project-os-cockpit · design review</h1>", encoding="utf-8")
    httpd, port = _serve(docs)
    import urllib.request
    try:
        with urllib.request.urlopen(
                "http://127.0.0.1:%d/design-asset/designs/enc.html" % port,
                timeout=5) as r:
            ctype = r.headers.get("Content-Type", "")
            assert "charset=utf-8" in ctype.lower(), ctype
            assert "·" in r.read().decode("utf-8")
    finally:
        httpd.shutdown()


def test_sheet_provenance_survives_reinjection() -> None:
    """A re-injected sheet is a <style>, so `href` is null. A filter written
    as `(sheet.href || '').includes(...)` matched nothing in the sandboxed
    runtime — the only runtime the app uses — and the spacing section rendered
    zero bars under prose calling itself the live measurement (ISS-0051)."""
    guide = _style_guide()
    assert "function sheetOrigin(sheet)" in guide
    assert "data-reinjected-from" in guide
    body = _code_only(guide.split("<script>", 1)[1])
    assert "(sheet.href || '')" not in body, (
        "a sheet's origin is read from href alone again; re-injected sheets "
        "have none and will be silently skipped"
    )
    # Every provenance question goes through the one helper.
    assert body.count("sheetOrigin(") >= 3


def test_the_type_specimens_do_not_reach_a_parser() -> None:
    """`--font-sans` contains `"Segoe UI"`. Interpolated, the quotes closed the
    attribute and the specimen rendered the INHERITED font — looking almost
    right while demonstrating nothing, the worst failure a specimen has
    (ISS-0052). ISS-0048 fixed this in swatchRow only."""
    body = _code_only(_style_guide().split("<script>", 1)[1])
    assert "font-family:' + v" not in body
    assert "n.style.setProperty('font-family', value);" in body
    # The guard for ISS-0048 inspected one function and certified the fix it
    # was written beside; this one covers the whole script.
    assert "style=\"font-family:" not in body


def test_the_shell_declares_no_alias_for_a_base_css_role() -> None:
    """The shell declared `--fg`/`--fg-muted`/`--fg-faint`/`--accent` for roles
    base.css already names, and overrode `--bg`/`--border` with different
    values — so DES-0002 documented one palette while the desktop drew another
    (ISS-0042). One vocabulary now: if a role exists in base.css, the shell
    uses base.css's name."""
    root = Path(__file__).resolve().parents[1]
    shell = (root / "desktop" / "src" / "renderer" / "renderer.css").read_text(encoding="utf-8")
    base = (root / "src" / "project_os_cockpit" / "static" / "base.css").read_text(encoding="utf-8")
    base_tokens = set(re.findall(r"^\s*(--[a-z0-9-]+)\s*:", base, re.M))
    shell_tokens = set(re.findall(r"^\s*(--[a-z0-9-]+)\s*:", shell, re.M))

    overlap = shell_tokens & base_tokens
    assert not overlap, (
        "the shell redeclares %s, which base.css already owns — that is the "
        "two-palettes bug, back" % sorted(overlap)
    )
    for alias in ("--fg", "--fg-muted", "--fg-faint", "--accent"):
        assert alias not in shell_tokens, alias
        assert ("var(%s)" % alias) not in shell, alias

    # The four that remain name roles base.css genuinely lacks.
    assert shell_tokens >= {"--bg-elevated", "--accent-soft",
                            "--row-hover", "--row-active"}


def test_every_token_the_shell_uses_is_declared_somewhere() -> None:
    """Deleting a declaration while a usage survives is silent: `var()` with no
    fallback is invalid at computed-value time, so the element renders
    inherited and looks almost right.

    Only `var()` WITHOUT a fallback can fail that way, and only outside a
    comment. A first version of this test grepped every `var(` and pinned four
    tokens; independent review showed three were non-problems — two carry
    fallbacks and one appears solely inside a `base.css` comment. Counting
    those as defects normalised them next to the one real case.
    """
    root = Path(__file__).resolve().parents[1]
    files = [root / "src" / "project_os_cockpit" / "static" / "base.css",
             root / "src" / "project_os_cockpit" / "static" / "cockpit.css",
             root / "desktop" / "src" / "renderer" / "renderer.css"]
    declared, at_risk = set(), set()
    for f in files:
        text = re.sub(r"/\*.*?\*/", "", f.read_text(encoding="utf-8"), flags=re.S)
        declared |= set(re.findall(r"^\s*(--[a-z0-9-]+)\s*:", text, re.M))
        # `var(--x)` with no comma before the closing paren — no fallback.
        at_risk |= set(re.findall(r"var\(\s*(--[a-z0-9-]+)\s*\)", text))
    dangling = at_risk - declared
    # `--surface-1` (cockpit.css) predates ISS-0042 and is genuinely broken;
    # pinning it means a NEW one fails here instead of hiding beside it.
    assert dangling <= {"--surface-1"}, sorted(dangling)


def test_the_boot_path_does_not_race_a_virtual_landing_mode() -> None:
    """The sidecar-ready handler sends the centre pane to README unless the
    mode lands on a virtual page. It named only `overview`, so Review
    inherited the bug the day it shipped and Design the day it shipped:
    select Design, restart, land on README with the Design button lit
    (ISS-0040 §2).

    Round 3 of independent review noted this fix was UNGUARDED — reverting the
    set to `{'overview'}` left the suite green — and that reachability
    therefore had one guarded path (the click) and one unguarded (the boot),
    with the unguarded one being the one that actually broke.
    """
    src = _renderer()
    decl = re.search(
        r"const MODES_WITH_VIRTUAL_LANDING[^=]*=\s*new Set\(\[([^\]]*)\]",
        src)
    assert decl, "the boot guard's mode set is gone; README will race again"
    # Quoted literals only — the block carries prose now, and splitting on
    # commas swept the comments into the set (they contain both).
    modes = set(re.findall(r"'([a-z]+)'", decl.group(1)))
    # `inbox` joined on 2026-07-28 (FEAT-0045) and left again the same day
    # (TASK-0234) when it stopped being a mode at all and became a left-pane
    # tray. The set is pinned rather than merely non-empty precisely so
    # adding or removing a virtual-landing mode has to come here and say so.
    # `review` left the set in TASK-0378 with its button: the route is still
    # served, but nothing lands there on workspace open, so claiming a landing
    # would send the centre pane to a page nobody asked for.
    # **Widened by FEAT-0092 on 2026-08-11**, which is exactly the event this
    # pinning exists to force a sentence about: Features, Issues and Tests
    # each gained a landing page leading with what their badge counts, so all
    # three must be here or the boot path sends them to README.md and the
    # landing loses the race it was written to win. The Library is still
    # absent, deliberately — it owes nothing and is a file browser.
    assert modes == {"overview", "intent", "features", "issues", "tests"}, modes

    # And the README fallback must actually consult it.
    ready = src.split("case 'ready': {", 1)[1].split("break;", 1)[0]
    assert "MODES_WITH_VIRTUAL_LANDING.has(currentNavMode)" in ready
    assert "currentNavMode !== 'overview'" not in ready, (
        "the guard names one mode again; every future virtual-landing mode "
        "inherits the race"
    )


# ---- offering a design for review (TASK-0229) -----------------------------

def _repo_with_design(tmp_path: Path, status: str = "implemented") -> Path:
    import subprocess
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    docs = tmp_path / "docs"
    (docs / "designs").mkdir(parents=True)
    (docs / "README.md").write_text("# x\n", encoding="utf-8")
    _note(docs / "designs" / "DES-0001-D.md", {
        "type": "[[design]]", "id": "DES-0001", "title": "A design",
        "status": status, "role": "proposal", "asset": "d.html"})
    (docs / "designs" / "d.html").write_text("<h1>d</h1>", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "-c", "user.email=t@t",
                    "-c", "user.name=t", "commit", "-qm", "first"], check=True)
    return docs


def _post(port: int, path: str, body: dict) -> tuple[int, dict]:
    import urllib.error
    import urllib.request
    req = urllib.request.Request(
        "http://127.0.0.1:%d%s" % (port, path),
        data=json.dumps(body).encode(), method="POST",
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as exc:
        return exc.code, json.load(exc)


def _queue(port: int) -> list:
    import urllib.request
    with urllib.request.urlopen(
            "http://127.0.0.1:%d/api/cockpit/review-queue" % port, timeout=5) as r:
        q = json.load(r)
    return [i for g in q["groups"] for i in g["items"]]


def test_a_design_can_be_offered_without_changing_its_status(tmp_path: Path) -> None:
    """The desk had two entry paths and designs were wired to only one. No
    design in this repo has ever been `proposed`, so the review path TASK-0218
    built had never been entered — the only way in was to change a status to
    something untrue (TASK-0229)."""
    docs = _repo_with_design(tmp_path, status="implemented")
    httpd, port = _serve(docs)
    try:
        status, data = _post(port, "/api/design/offer-review", {"id": "DES-0001"})
        assert status == 200 and data["ok"], data
        assert data["request"]["subject"] == "DES-0001"
        # The note is untouched: no status written, no frontmatter change.
        text = (docs / "designs" / "DES-0001-D.md").read_text(encoding="utf-8")
        assert "status: \"implemented\"" in text or "status: implemented" in text
        assert "proposed" not in text
        rows = _queue(port)
        assert [r.get("subject") for r in rows if r.get("subject")] == ["DES-0001"]
    finally:
        httpd.shutdown()


def test_the_request_records_the_revision_it_was_raised_against(tmp_path: Path) -> None:
    """A review is of a REVISION, not of "the design". TASK-0218 already
    requires `design_revision` on accept and validates it against real history;
    without the same on the request, a reviewer can accept something other than
    what they were shown and neither party would know."""
    docs = _repo_with_design(tmp_path)
    httpd, port = _serve(docs)
    try:
        _, data = _post(port, "/api/design/offer-review", {"id": "DES-0001"})
        sha = data["request"]["at_revision"]
        assert re.fullmatch(r"[0-9a-f]{7,40}", sha), sha

        import urllib.request
        rid = data["request"]["request_id"]
        with urllib.request.urlopen(
                "http://127.0.0.1:%d/api/cockpit/review/%s" % (port, rid),
                timeout=5) as r:
            detail = json.load(r)
        assert detail["at_revision"] == sha
        assert detail["revision_moved"] is False

        # Move the artifact on; the desk must say the reviewer was asked about
        # something older.
        import subprocess
        (docs / "designs" / "d.html").write_text("<h1>d2</h1>", encoding="utf-8")
        subprocess.run(["git", "-C", str(docs.parent), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(docs.parent), "-c", "user.email=t@t",
                        "-c", "user.name=t", "commit", "-qm", "second"], check=True)
        with urllib.request.urlopen(
                "http://127.0.0.1:%d/api/cockpit/review/%s" % (port, rid),
                timeout=5) as r:
            detail = json.load(r)
        assert detail["revision_moved"] is True, detail
        assert detail["head_revision"] != sha
    finally:
        httpd.shutdown()


def test_offering_twice_is_idempotent(tmp_path: Path) -> None:
    """A human asked to look at one thing should see one row, however many
    times the button is pressed."""
    docs = _repo_with_design(tmp_path)
    httpd, port = _serve(docs)
    try:
        _, first = _post(port, "/api/design/offer-review", {"id": "DES-0001"})
        _, second = _post(port, "/api/design/offer-review", {"id": "DES-0001"})
        assert second.get("already_open") is True
        assert second["request"]["request_id"] == first["request"]["request_id"]
        assert len([r for r in _queue(port) if r.get("subject")]) == 1
    finally:
        httpd.shutdown()


def test_status_intake_and_the_ledger_do_not_double_list(tmp_path: Path) -> None:
    """A design can arrive by both routes. It must appear once, and the ledger
    row wins because it carries the revision the reviewer was asked about."""
    docs = _repo_with_design(tmp_path, status="proposed")
    httpd, port = _serve(docs)
    try:
        assert len([r for r in _queue(port) if r.get("id") == "DES-0001"]) == 1
        _post(port, "/api/design/offer-review", {"id": "DES-0001"})
        rows = _queue(port)
        hits = [r for r in rows
                if r.get("subject") == "DES-0001" or r.get("id") == "DES-0001"]
        assert len(hits) == 1, hits
        assert hits[0].get("at_revision"), "the surviving row lost the revision"
    finally:
        httpd.shutdown()


def test_an_unknown_or_missing_design_is_refused_or_reported(tmp_path: Path) -> None:
    """Offering something that is not a design is refused outright; a design
    that disappears AFTER being offered leaves a row that explains itself
    rather than one pointing at nothing."""
    docs = _repo_with_design(tmp_path)
    httpd, port = _serve(docs)
    try:
        assert _post(port, "/api/design/offer-review", {"id": "DES-9999"})[0] == 404
        assert _post(port, "/api/design/offer-review", {})[0] == 400
    finally:
        httpd.shutdown()


def test_a_request_whose_design_vanished_explains_itself(tmp_path: Path) -> None:
    """A design deleted or renamed AFTER being offered must leave a row that
    says so. Dropping it silently would strand the request forever; leaving it
    pointing at nothing is worse than a row that explains itself.

    Driven at the payload level with a stub store rather than by deleting a
    file mid-request: the live index caches the note, so a filesystem race
    would have tested the watcher rather than this branch.
    """
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "README.md").write_text("# x\n", encoding="utf-8")

    class _Store:
        def open_requests(self):
            return [{"request_id": "abc", "kind": "review", "title": "Design review",
                     "items": ["DES-0404"], "subject": "DES-0404",
                     "at_revision": "deadbee", "ts": "2026-07-28T00:00:00+00:00"}]
        def outcome_counts(self):
            return {}

    payload = cockpit.review_queue_payload(Index.build(docs), _Store())
    row = next(i for g in payload["groups"] for i in g["items"]
               if i.get("subject") == "DES-0404")
    assert row["subject_missing"] is True
    assert row["at_revision"] == "deadbee"


def test_the_offer_endpoint_is_loopback_only(tmp_path: Path) -> None:
    """Every mutation endpoint is loopback-guarded; the render server binds
    0.0.0.0 so a tablet on the LAN can read it.

    Driven through the **endpoint**, not the guard. Two earlier versions of
    this test failed to catch the mutation that motivated them: the first
    string-matched the handler source (so moving the check out while leaving
    its text behind passed), the second exercised `_require_loopback` in
    isolation (so DELETING its call from this endpoint passed). This makes a
    real request with `_is_loopback` forced false and asserts the endpoint
    refuses — which is the only shape that ties the guard to its use
    (ISS-0056 rounds 1 and 2).
    """
    docs = _repo_with_design(tmp_path)
    httpd, port = _serve(docs)
    try:
        handler_cls = httpd.RequestHandlerClass
        original = handler_cls._is_loopback
        handler_cls._is_loopback = lambda self: False       # type: ignore[assignment]
        try:
            status, data = _post(port, "/api/design/offer-review", {"id": "DES-0001"})
            assert status == HTTPStatus.FORBIDDEN, (status, data)
            assert data["ok"] is False
            # AND the side effect must not have happened. A guard moved to sit
            # AFTER `review_store.add(...)` returns the same 403 while writing
            # the row — refusing the response, not the write (round 3). The
            # rule: a guard test must fail when the guard is removed from the
            # thing it guards, AND assert the guarded effect did not occur.
            assert not [r for r in _queue(port) if r.get("subject")], (
                "the endpoint refused the response but still wrote the ledger"
            )
            # THIRD clause: the refusal must pre-empt the endpoint's other
            # branches. A guard sitting after the read branches returns 403
            # with no row written — passing the two checks above — while a LAN
            # client still enumerates the register by response code: 403 for a
            # real id, 404 for a fake one, plus a designs scan and two git
            # subprocesses per probe. Neither is a write, so the queue cannot
            # see it (independent review round 4).
            unknown, _ = _post(port, "/api/design/offer-review", {"id": "DES-9999"})
            assert unknown == HTTPStatus.FORBIDDEN, (
                "a non-loopback client learned whether DES-9999 exists: got "
                "%s, so the guard sits below the register lookup" % unknown
            )
        finally:
            handler_cls._is_loopback = original             # type: ignore[assignment]

        # And a genuine loopback request still works, so the guard is not
        # simply refusing everything.
        assert _post(port, "/api/design/offer-review", {"id": "DES-0001"})[0] == 200
    finally:
        httpd.shutdown()


def test_the_design_surface_offers_the_control() -> None:
    src = _renderer()
    assert "/api/design/offer-review" in src
    assert "'Ask for review'" in src
    # Says which of the two things happened rather than pretending a second
    # press did something.
    assert "already_open" in src


# ---- ISS-0056 fixes -------------------------------------------------------

def test_a_design_never_reaches_the_plan_verdict_path() -> None:
    """A ledger row rendered through `buildProposalView`, whose Accept posts
    `plan-accepted` with NO revision and whose Reject writes
    `status: cancelled` onto a design that may be `implemented`. `design` is
    not in GATE_BEARING_TYPES, so those writes landed — reproducing, one click
    later, the exact defect this task was written to prevent (ISS-0056)."""
    src = _renderer()
    dispatch = src.split("} else if (detail.request", 1)[1].split("docView.hidden", 1)[0]
    assert "detail.subject_type === 'design'" in dispatch
    assert "buildDesignReviewView(detail)" in dispatch
    # And the design view must use the revision-validated endpoint.
    view = _code_only(
        src.split("function buildDesignReviewView(")[1].split("\n/** A request whose")[0])
    assert "'/api/design/verdict'" in view
    assert "revision: detail.at_revision" in view
    assert "status: 'cancelled'" not in view, (
        "the design view cancels a design from the client; the design endpoint "
        "decides what a rejection means for a design's status"
    )
    assert "plan-accepted" not in view and "plan-rejected" not in view


def test_the_reviewer_is_told_when_the_artifact_moved() -> None:
    """The payload carried `revision_moved`/`head_revision` and no client read
    them, so the DoD bullet claiming "the desk says so" was false."""
    src = _renderer()
    view = _code_only(
        src.split("function buildDesignReviewView(")[1].split("\n/** A request whose")[0])
    assert "detail.revision_moved" in view
    assert "detail.head_revision" in view
    assert "detail.dirty" in view


def test_an_orphaned_request_can_be_cleared() -> None:
    """Accept and Reject both posted to `/api/notes/review` for an id that no
    longer resolves, 404'd, and never reached review-resolve — so the row was
    unclearable except by hand-editing the ledger."""
    src = _renderer()
    assert "buildOrphanedRequestView(detail)" in src
    # `_code_only`: the comment inside this function NAMES the endpoint it no
    # longer calls. Fourth time this suite has matched its own prose.
    view = _code_only(
        src.split("function buildOrphanedRequestView(")[1].split("\nasync function")[0])
    assert "'/api/cockpit/review-resolve'" in view
    assert "/api/notes/review" not in view, (
        "clearing an orphan writes a note; there is no note to write"
    )


def test_offering_is_idempotent_under_concurrency(tmp_path: Path) -> None:
    """`open_for_subject` then `add` was check-then-act across two lock
    acquisitions: 16 concurrent offers produced 9 open requests and 9
    indistinguishable rows. The check now happens inside `add`, under the same
    lock that appends."""
    import threading
    from project_os_cockpit.review import ReviewStore
    store = ReviewStore(tmp_path)
    barrier = threading.Barrier(16)

    def offer() -> None:
        barrier.wait()
        store.add("review", items=["DES-0001"], subject="DES-0001",
                  at_revision="abc1234", title="Design review")

    threads = [threading.Thread(target=offer) for _ in range(16)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(store.open_requests()) == 1, store.open_requests()


def test_a_design_with_no_committed_revision_is_refused(tmp_path: Path) -> None:
    """`head == ""` made `at_revision` absent, and the detail route's
    `if subject and asked_at` then skipped every staleness field — a 200
    indistinguishable from a good one. That was DES-0002's own situation until
    its `asset` was filled in. `/api/design/verdict` refuses this; so does the
    offer."""
    import subprocess
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    docs = tmp_path / "docs"
    (docs / "designs").mkdir(parents=True)
    (docs / "README.md").write_text("# x\n", encoding="utf-8")
    _note(docs / "designs" / "DES-0002-S.md", {
        "type": "[[design]]", "id": "DES-0002", "title": "No artifact",
        "status": "implemented", "role": "system", "asset": ""})
    httpd, port = _serve(docs)
    try:
        status, data = _post(port, "/api/design/offer-review", {"id": "DES-0002"})
        assert status == 409, (status, data)
        assert "no committed revision" in data["error"]
        assert not [r for r in _queue(port) if r.get("subject")]
    finally:
        httpd.shutdown()


def test_a_design_offered_dirty_records_that_it_was(tmp_path: Path) -> None:
    """The surface renders the WORKING COPY, so a design offered dirty was
    reviewed against something `at_revision` does not name — and
    `revision_moved` stays false, because the commit did not move."""
    docs = _repo_with_design(tmp_path)
    (docs / "designs" / "d.html").write_text("<h1>edited</h1>", encoding="utf-8")
    httpd, port = _serve(docs)
    try:
        _, data = _post(port, "/api/design/offer-review", {"id": "DES-0001"})
        assert data["request"].get("dirty_at_offer") is True, data["request"]
    finally:
        httpd.shutdown()


def test_the_review_shows_the_revision_being_judged() -> None:
    """Edwin: "it is unclear what I accept since the document does not show its
    content." Accepting a revision you cannot see is the exact failure this
    surface exists to prevent.

    The frame is built from `at_revision`, so it renders the reviewed
    revision rather than the working copy — the same distinction
    `design_revision` draws on the verdict itself.
    """
    src = _renderer()
    view = _code_only(
        src.split("function buildDesignReviewView(")[1].split("\n/** A request whose")[0])
    assert "buildDesignFrame(d, detail.at_revision" in view, (
        "the review renders the working copy, not the revision under review"
    )
    assert "fetchDesignRegister()" in view
    # An artifact that cannot be shown says why rather than leaving a blank box.
    assert "no longer in the design register" in view
    assert "declares no artifact" in view


def test_the_design_review_follows_the_established_review_shape() -> None:
    """Edwin, across three corrections: "Looks different to usual other
    options", "the buttons ... are usually shown at the top", "the buttons and
    note doesn't look great".

    All three were the same mistake — building a review screen beside a
    convention that already existed rather than using it. The shape is
    `buildReviewHeader` with the actions IN the header, `.review-comment` for
    the note back, and `.review-note` reserved for rendered note content
    (putting a textarea in it is why it looked wrong).
    """
    src = _renderer()
    view = _code_only(
        src.split("function buildDesignReviewView(")[1].split("\n/** A request whose")[0])
    assert "buildReviewHeader(" in view, "the design review builds its own header"
    assert "note.status, actions, provenance" in view, (
        "the actions are not passed into the header, so they render below the "
        "content instead of at the top"
    )
    for cls in ("review-btn is-good", "review-btn is-primary", "review-btn is-bad"):
        assert cls in view, cls
    assert "comment.className = 'review-comment';" in view
    assert "comment.className = 'review-note'" not in view, (
        "`review-note` is the rendered-note container, not a textarea"
    )
    assert "'review-accept'" not in view and "'review-reject'" not in view


def test_the_design_review_shows_both_the_artifact_and_the_prose() -> None:
    """`buildSingleNoteReview` carries the comment "the first cut rendered a
    header, buttons and nothing else — asking for approval of content it never
    showed (reported 2026-07-26)". The design review reproduced that defect two
    days later, so it now mounts both: the artifact for what it looks like, and
    the note body for why."""
    src = _renderer()
    view = _code_only(
        src.split("function buildDesignReviewView(")[1].split("\n/** A request whose")[0])
    assert "buildDesignFrame(d, detail.at_revision" in view, (
        "the review renders the working copy, not the revision under review"
    )
    assert "fillReviewNoteBody(body, note.rel)" in view, (
        "the note's prose is not shown; the artifact says what it looks like, "
        "the note says why"
    )
    assert "no longer in the design register" in view
    assert "declares no artifact" in view


def test_request_changes_leaves_a_design_in_the_queue() -> None:
    """The proposal path leaves the request open on Request changes. The design
    path must match, or a reviewer who asks for changes loses the row."""
    src = _renderer()
    view = _code_only(
        src.split("function buildDesignReviewView(")[1].split("\n/** A request whose")[0])
    assert "'changes-requested', null, null," in view, (
        "Request changes resolves the ledger entry; it must leave it open"
    )
    assert "if (outcome && request.request_id)" in view


def test_accepting_does_not_demote_an_implemented_design(tmp_path: Path) -> None:
    """`accepted` means "agreed, not yet built"; `implemented` means the code
    shipped. Accepting a design at `implemented` wrote `accepted` over it —
    replacing a true status with a false one, one click after an offer that
    scrupulously wrote none. Every design that can be offered today is
    `implemented`, which is this feature's own premise (ISS-0056 round 2)."""
    from project_os_cockpit import note_writes
    docs = tmp_path / "docs"
    _note(docs / "designs" / "DES-0001-D.md", {
        "type": "[[design]]", "id": "DES-0001", "title": "D",
        "status": "implemented", "role": "proposal", "asset": "d.html",
        "reviewed_by": "", "review_date": "", "review_verdict": "",
        "design_revision": ""})
    (docs / "designs" / "d.html").write_text("<h1>d</h1>", encoding="utf-8")
    note_writes.stamp_design_verdict(
        Index.build(docs), "DES-0001", reviewer="user:edwin",
        verdict="accepted", revision="abc1234", accept=True)
    text = (docs / "designs" / "DES-0001-D.md").read_text(encoding="utf-8")
    assert 'status: "implemented"' in text, "an implemented design was demoted"
    # The verdict itself is still recorded — declining the status move must not
    # swallow the review.
    assert 'review_verdict: "accepted"' in text
    assert 'design_revision: "abc1234"' in text


def test_accepting_still_advances_a_design_that_is_not_built(tmp_path: Path) -> None:
    """The refusal is of BACKWARDS moves only; a `proposed` design accepted
    must still advance, or the guard would have eaten the feature."""
    from project_os_cockpit import note_writes
    docs = tmp_path / "docs"
    _note(docs / "designs" / "DES-0002-P.md", {
        "type": "[[design]]", "id": "DES-0002", "title": "P",
        "status": "proposed", "role": "proposal", "asset": "p.html",
        "reviewed_by": "", "review_date": "", "review_verdict": "",
        "design_revision": ""})
    (docs / "designs" / "p.html").write_text("<h1>p</h1>", encoding="utf-8")
    note_writes.stamp_design_verdict(
        Index.build(docs), "DES-0002", reviewer="user:edwin",
        verdict="accepted", revision="abc1234", accept=True)
    assert 'status: "accepted"' in (docs / "designs" / "DES-0002-P.md").read_text(
        encoding="utf-8")


def test_subject_type_is_set_even_without_a_revision(tmp_path: Path) -> None:
    """`subject_type` was computed inside `if subject and asked_at`, so a row
    with a subject and no `at_revision` — the shape every pre-fix offer wrote —
    still dispatched to the plan-verdict path (ISS-0056 round 2)."""
    docs = _repo_with_design(tmp_path)
    # Filed BEFORE the server starts: the handler holds its own ReviewStore
    # instance, loaded once, so a second instance's writes are invisible to it.
    from project_os_cockpit.review import ReviewStore
    req = ReviewStore(docs.parent).add(
        "review", items=["DES-0001"], subject="DES-0001",
        title="Design review")   # no at_revision
    httpd, port = _serve(docs)
    import urllib.request
    try:
        with urllib.request.urlopen(
                "http://127.0.0.1:%d/api/cockpit/review/%s"
                % (port, req["request_id"]), timeout=5) as r:
            detail = json.load(r)
        assert detail.get("subject_type") == "design", detail
        assert "at_revision" not in detail
    finally:
        httpd.shutdown()


def test_requesting_changes_keeps_the_comment() -> None:
    """The placeholder promises the note is "sent with Request changes"; the
    first cut recorded a verdict and dropped the text (ISS-0056 round 2)."""
    src = _renderer()
    view = _code_only(
        src.split("function buildDesignReviewView(")[1].split("\n/** A request whose")[0])
    assert "'/api/design/comment'" in view, (
        "Request changes discards the reviewer's note"
    )
    assert "region: ''" in view


def test_a_historical_render_is_not_gated_on_the_working_copy() -> None:
    """`has_asset` is an `is_file()` on the working copy. An artifact deleted
    after being offered still renders fine at the revision under review."""
    src = _renderer()
    view = _code_only(
        src.split("function buildDesignReviewView(")[1].split("\n/** A request whose")[0])
    assert "if (!d.has_asset && !detail.at_revision)" in view


def test_the_dirty_banners_say_different_things() -> None:
    """One is about the moment of offering, the other about now, and the first
    cut fired the same present-tense sentence for both — contradicting the line
    above it about which revision is framed."""
    src = _renderer()
    view = _code_only(
        src.split("function buildDesignReviewView(")[1].split("\n/** A request whose")[0])
    assert "request.dirty_at_offer" in view and "else if (detail.dirty)" in view
    assert "had uncommitted changes when it was offered" in view
    assert "not part of what you are reviewing here" in view


def test_rejecting_does_not_cancel_a_design_that_shipped(tmp_path: Path) -> None:
    """The mirror of the demotion bug, and invisible to rank: `cancelled`
    ranks ABOVE `implemented`, so cancelling a shipped design reads as a
    FORWARD move. A design that shipped cannot be un-shipped by a verdict —
    deciding to replace it is a new design or an issue (ISS-0056 round 3)."""
    from project_os_cockpit import note_writes
    docs = tmp_path / "docs"
    _note(docs / "designs" / "DES-0001-D.md", {
        "type": "[[design]]", "id": "DES-0001", "title": "D",
        "status": "implemented", "role": "proposal", "asset": "d.html",
        "reviewed_by": "", "review_date": "", "review_verdict": "",
        "design_revision": ""})
    (docs / "designs" / "d.html").write_text("<h1>d</h1>", encoding="utf-8")
    note_writes.stamp_design_verdict(
        Index.build(docs), "DES-0001", reviewer="user:edwin",
        verdict="rejected", revision="abc1234", accept=False)
    text = (docs / "designs" / "DES-0001-D.md").read_text(encoding="utf-8")
    assert 'status: "implemented"' in text, "a shipped design was cancelled"
    assert 'review_verdict: "rejected"' in text, "the verdict was swallowed"


def test_rejecting_still_cancels_a_design_that_has_not_shipped(tmp_path: Path) -> None:
    """The refusal is about settled statuses, not about rejection."""
    from project_os_cockpit import note_writes
    docs = tmp_path / "docs"
    _note(docs / "designs" / "DES-0002-P.md", {
        "type": "[[design]]", "id": "DES-0002", "title": "P",
        "status": "proposed", "role": "proposal", "asset": "p.html",
        "reviewed_by": "", "review_date": "", "review_verdict": "",
        "design_revision": ""})
    (docs / "designs" / "p.html").write_text("<h1>p</h1>", encoding="utf-8")
    note_writes.stamp_design_verdict(
        Index.build(docs), "DES-0002", reviewer="user:edwin",
        verdict="rejected", revision="abc1234", accept=False)
    assert 'status: "cancelled"' in (docs / "designs" / "DES-0002-P.md").read_text(
        encoding="utf-8")


def test_the_known_status_set_covers_the_vocabulary() -> None:
    """An unknown status was silently demoted — a fail-OPEN that quietly
    reopened the very bug this exists to prevent.

    Was a rank table until independent review proved the ranks dead: replacing
    the backwards comparison with `False` left every test passing, because
    accept's candidate is `accepted` and everything above it is settled. The
    live use was always membership."""
    from project_os_cockpit import note_writes
    from project_os_cockpit.validate_docs_bundled import ALLOWED_STATUS
    assert note_writes._DESIGN_KNOWN_STATUSES == set(ALLOWED_STATUS["design"]), (
        "the known-status set has drifted from the design vocabulary"
    )
    assert note_writes._DESIGN_SETTLED <= set(ALLOWED_STATUS["design"])
    assert not hasattr(note_writes, "_DESIGN_STATUS_RANK"), (
        "the dead rank table is back; `_DESIGN_SETTLED` is the guard"
    )


def test_an_unknown_status_fails_closed(tmp_path: Path) -> None:
    """Belt to the assertion's braces: if a status ever escapes the table, the
    verdict is still recorded and the status is left alone."""
    from project_os_cockpit import note_writes
    docs = tmp_path / "docs"
    _note(docs / "designs" / "DES-0003-X.md", {
        "type": "[[design]]", "id": "DES-0003", "title": "X",
        "status": "some-future-status", "role": "proposal", "asset": "x.html",
        "reviewed_by": "", "review_date": "", "review_verdict": "",
        "design_revision": ""})
    (docs / "designs" / "x.html").write_text("<h1>x</h1>", encoding="utf-8")
    note_writes.stamp_design_verdict(
        Index.build(docs), "DES-0003", reviewer="user:edwin",
        verdict="accepted", revision="abc1234", accept=True)
    text = (docs / "designs" / "DES-0003-X.md").read_text(encoding="utf-8")
    assert 'status: "some-future-status"' in text
    assert 'review_verdict: "accepted"' in text


def test_a_historical_render_survives_a_deleted_artifact() -> None:
    """`buildDesignFrame` kept its own unconditional `has_asset` return below
    the relaxed outer gate, so only the message changed — the revision still
    did not render (ISS-0056 round 3)."""
    src = _renderer()
    frame = _code_only(
        src.split("function buildDesignFrame(")[1].split("\nfunction ")[0])
    assert "if (!d.has_asset && !atSha)" in frame, (
        "the historical render is still gated on the working copy"
    )


# ---- the project stylesheet route (TASK-0230) -----------------------------

def _repo_with_project_css(tmp_path: Path, declared: list[str] | None = None) -> Path:
    docs = tmp_path / "docs"
    (docs / "designs").mkdir(parents=True)
    (docs / "README.md").write_text("# x\n", encoding="utf-8")
    fm = {"type": "[[design]]", "id": "DES-0001", "title": "System",
          "status": "draft", "role": "system", "asset": ""}
    if declared is not None:
        fm["stylesheets"] = declared
    _note(docs / "designs" / "DES-0001-S.md", fm)
    (tmp_path / "public" / "css").mkdir(parents=True)
    (tmp_path / "public" / "css" / "style.css").write_text(
        ":root { --brand: #123456 }", encoding="utf-8")
    # A real stylesheet the note does NOT declare.
    (tmp_path / "public" / "css" / "private.css").write_text(
        ":root { --secret: #abcdef }", encoding="utf-8")
    (tmp_path / "secrets.env").write_text("TOKEN=hunter2\n", encoding="utf-8")
    return docs


def _get(port: int, path: str) -> tuple[int, bytes, dict]:
    import urllib.error
    import urllib.request
    try:
        with urllib.request.urlopen(
                "http://127.0.0.1:%d%s" % (port, path), timeout=5) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(), dict(exc.headers)


def test_a_declared_stylesheet_is_served(tmp_path: Path) -> None:
    """Every downstream stylesheet lives ABOVE the docs root, so a design
    artifact could not read its own project's tokens and a downstream design
    system could only ever be a hand-typed table (TASK-0230)."""
    docs = _repo_with_project_css(tmp_path, ["public/css/style.css"])
    httpd, port = _serve(docs)
    try:
        status, body, headers = _get(port, "/_project/public/css/style.css")
        assert status == 200, status
        assert b"--brand" in body
        assert headers.get("Content-Type", "").startswith("text/css")
        # A sandboxed frame has an opaque origin and must fetch + re-inject.
        assert headers.get("Access-Control-Allow-Origin") == "*"
    finally:
        httpd.shutdown()


def test_the_allowlist_is_the_corpus_not_a_constant(tmp_path: Path) -> None:
    """A real stylesheet the notes do not declare is refused. Widening the
    route means declaring a path in a note a human reviews — a hardcoded list
    would drift from the notes it describes (ISS-0023's failure)."""
    docs = _repo_with_project_css(tmp_path, ["public/css/style.css"])
    httpd, port = _serve(docs)
    try:
        assert _get(port, "/_project/public/css/style.css")[0] == 200
        assert _get(port, "/_project/public/css/private.css")[0] == 404, (
            "an undeclared stylesheet was served; the route is a directory "
            "share rather than an allow-list"
        )
    finally:
        httpd.shutdown()


def test_declaring_nothing_serves_nothing(tmp_path: Path) -> None:
    """The empty case must be closed, not open."""
    docs = _repo_with_project_css(tmp_path, None)
    httpd, port = _serve(docs)
    try:
        assert _get(port, "/_project/public/css/style.css")[0] == 404
    finally:
        httpd.shutdown()


def test_the_route_reads_css_and_nothing_else(tmp_path: Path) -> None:
    """The render server binds 0.0.0.0. The narrowing to `.css` is what stops
    this becoming a general file read."""
    docs = _repo_with_project_css(
        tmp_path, ["public/css/style.css", "../secrets.env", "secrets.env"])
    httpd, port = _serve(docs)
    try:
        for attack in ("/_project/secrets.env", "/_project/../secrets.env",
                       "/_project/..%2Fsecrets.env", "/_project/",
                       "/_project/public/css/../../secrets.env"):
            status, body, _ = _get(port, attack)
            assert status in (403, 404), (attack, status)
            assert b"hunter2" not in body, attack
    finally:
        httpd.shutdown()


def test_a_symlink_out_of_the_tree_is_refused(tmp_path: Path) -> None:
    """The allow-list cannot see through a link, so containment is checked
    after resolution as well as before."""
    outside = tmp_path.parent / ("outside-%s.css" % tmp_path.name)
    outside.write_text(":root { --leaked: red }", encoding="utf-8")
    docs = _repo_with_project_css(tmp_path, ["public/css/link.css"])
    try:
        (tmp_path / "public" / "css" / "link.css").symlink_to(outside)
    except OSError:
        pytest.skip("symlinks unavailable")
    httpd, port = _serve(docs)
    try:
        status, body, _ = _get(port, "/_project/public/css/link.css")
        assert status == 403, status
        assert b"--leaked" not in body
    finally:
        httpd.shutdown()
        outside.unlink(missing_ok=True)


def test_a_declared_but_missing_stylesheet_404s(tmp_path: Path) -> None:
    """Declared and absent is a normal state — a path renamed in the project
    and not yet in the note. It must not raise."""
    docs = _repo_with_project_css(tmp_path, ["public/css/gone.css"])
    httpd, port = _serve(docs)
    try:
        assert _get(port, "/_project/public/css/gone.css")[0] == 404
        assert _get(port, "/healthz")[0] == 200
    finally:
        httpd.shutdown()


def test_the_declaration_is_normalised_at_one_place(tmp_path: Path) -> None:
    """A declaration the route would refuse anyway should never have counted,
    so the payload and the allow-list agree by construction."""
    docs = tmp_path / "docs"
    _note(docs / "designs" / "DES-0001-S.md", {
        "type": "[[design]]", "id": "DES-0001", "title": "S", "status": "draft",
        "role": "system", "asset": "",
        "stylesheets": ["/public/css/a.css", "b.css", "../evil.css",
                        "notes.md", "", "b.css"]})
    idx = Index.build(docs)
    payload = cockpit.designs_payload(idx)["designs"][0]
    assert payload["stylesheets"] == ["public/css/a.css", "b.css"], payload
    assert cockpit.project_stylesheet_allowlist(idx) == {"public/css/a.css", "b.css"}


def test_the_route_guards_hold_even_if_the_declaration_filter_does_not(
        tmp_path: Path, monkeypatch) -> None:
    """The route's own `.css` and traversal checks are unreachable while
    `_design_stylesheets` drops those declarations first — so mutating either
    one out changed nothing, and the tests above were exercising the FILTER,
    not the route (found by mutation, 2026-07-28).

    Two layers deserve two tests. This one hands the route a hostile
    allow-list directly, which is what would happen if the filter were ever
    relaxed, and asserts the route refuses on its own.
    """
    docs = _repo_with_project_css(tmp_path, ["public/css/style.css"])
    hostile = {"secrets.env", "../secrets.env", "public/css/style.css"}
    monkeypatch.setattr(cockpit, "project_stylesheet_allowlist",
                        lambda index: hostile)
    httpd, port = _serve(docs)
    try:
        # Non-CSS, allow-listed: refused by the route's own extension check.
        status, body, _ = _get(port, "/_project/secrets.env")
        assert status == 404, status
        assert b"hunter2" not in body
        # Traversal, allow-listed: refused by the route's own `..` check.
        status, body, _ = _get(port, "/_project/../secrets.env")
        assert status in (403, 404), status
        assert b"hunter2" not in body
        # And the legitimate one still works, so the guards are not blanket.
        assert _get(port, "/_project/public/css/style.css")[0] == 200
    finally:
        httpd.shutdown()


# ---- native token sources (ISS-0059) --------------------------------------

def test_kotlin_colours_are_synthesised_into_css() -> None:
    """Three fleet apps declare their palette in Kotlin or Swift and have no
    application CSS, so the living style guide could not read them at all.
    Synthesised at READ TIME — a generated file committed beside the source is
    a second copy that goes stale the first time someone edits Color.kt and
    forgets to regenerate (ISS-0059)."""
    from project_os_cockpit import token_sources
    css = token_sources.synthesise_css(
        "val PrimaryBlue = Color(0xFF2563EB)\n"
        "val Ghost = Color(0x33FFFFFF)   // translucent\n"
        "package com.secret.thing\n", "Color.kt")
    assert "--PrimaryBlue: #2563EB;" in css
    # Alpha survives as a real CSS value rather than being silently dropped.
    assert "--Ghost:" in css and "transparent" in css
    # The SOURCE never leaves the machine — only extracted tokens.
    assert "package com.secret.thing" not in css
    assert ":root {" in css, "tokens declared outside :root have no page value"


def test_swift_component_colours_are_synthesised() -> None:
    from project_os_cockpit import token_sources
    css = token_sources.synthesise_css(
        "static let brandPurple = Color(red: 0x74 / 255.0, green: 0x74 / 255.0,"
        " blue: 0xB0 / 255.0)\n", "Theme.swift")
    assert "--brandPurple: #7474B0;" in css


def test_swift_unit_interval_colours_are_synthesised() -> None:
    """ISS-0073. SwiftUI's `Color(red:green:blue:)` takes 0–1 doubles; the
    `/ 255.0` spelling above is one way of writing them, not the only one.

    Reporting a fully-specified colour as unresolvable spends the "no honest
    value" signal on a colour that has one, and a reader who sees several
    unresolved tokens learns to skim past the ones that genuinely could not
    be read.
    """
    from project_os_cockpit import token_sources
    css = token_sources.synthesise_css(
        "static let zoneRecovery = Color(red: 0.6, green: 0.6, blue: 0.6)\n",
        "ZoneColorUtils.swift")
    assert "--zoneRecovery: #999999;" in css

    # Both spellings still work, and neither steals the other's matches.
    both = token_sources.synthesise_css(
        "static let a = Color(red: 0x74 / 255.0, green: 0x74 / 255.0, blue: 0xB0 / 255.0)\n"
        "static let b = Color(red: 1.0, green: 0, blue: 0)\n",
        "Theme.swift")
    assert "--a: #7474B0;" in both
    assert "--b: #FF0000;" in both


def test_a_derived_colour_is_named_never_guessed() -> None:
    """`Color.blue.opacity(0.3)` derives from a system colour whose value
    depends on platform and appearance. There is no honest hex, so the token
    is emitted with its source expression — the page shows it exists and says
    what it derives from rather than inventing a swatch."""
    from project_os_cockpit import token_sources
    css = token_sources.synthesise_css(
        "static let cellSelected = Color.blue.opacity(0.3)\n", "Theme.swift")
    assert "--cellSelected: Color.blue.opacity(0.3);" in css
    assert "#" not in css.split("--cellSelected")[1].split(";")[0]

    # ISS-0073's fix must not reach these: a system colour still has no
    # honest hex, and inventing one is worse than reporting it.
    system = token_sources.synthesise_css(
        "static let zoneEndurance = Color.blue\n"
        "static let zoneTempo = Color.green\n", "ZoneColorUtils.swift")
    assert "--zoneEndurance: Color.blue;" in system
    assert "#" not in system


def test_an_expression_cannot_escape_a_css_value() -> None:
    """Only text a `Color…` pattern matched is ever emitted, and it is
    stripped of anything that could close a declaration."""
    from project_os_cockpit import token_sources
    css = token_sources.synthesise_css(
        'static let evil = Color.x } body { background: url("http://x") } /*\n',
        "Theme.swift")
    body = css.split("--evil:")[1].split("\n")[0]
    for ch in ("{", "}", ";", '"', "<"):
        assert ch not in body.replace(";", "", 1), (ch, body)


def test_an_unrecognised_source_says_so(tmp_path: Path) -> None:
    """Silence would look identical to a project with no colours."""
    from project_os_cockpit import token_sources
    css = token_sources.synthesise_css("fun main() { println(1) }\n", "Main.kt")
    assert "no colour declarations recognised" in css


def test_the_synthesised_route_serves_css_and_sets_cors(tmp_path: Path) -> None:
    """The shared CORS helper keys off the FILENAME, which is right for the
    static routes and wrong here: a synthesised response is named `Color.kt`
    and is `text/css`, so the helper stayed silent and the sandboxed frame's
    fetch failed with everything else working. curl could not see it, because
    curl has an origin (ISS-0059)."""
    docs = tmp_path / "docs"
    (docs / "designs").mkdir(parents=True)
    (docs / "README.md").write_text("# x\n", encoding="utf-8")
    _note(docs / "designs" / "DES-0001-S.md", {
        "type": "[[design]]", "id": "DES-0001", "title": "S", "status": "draft",
        "role": "system", "asset": "", "stylesheets": ["ui/Color.kt"]})
    (tmp_path / "ui").mkdir()
    (tmp_path / "ui" / "Color.kt").write_text(
        "package secret.pkg\nval Brand = Color(0xFF112233)\n", encoding="utf-8")
    httpd, port = _serve(docs)
    try:
        status, body, headers = _get(port, "/_project/ui/Color.kt")
        assert status == 200, status
        assert headers.get("Content-Type", "").startswith("text/css")
        assert headers.get("Access-Control-Allow-Origin") == "*", (
            "a sandboxed opaque-origin frame cannot fetch this"
        )
        assert b"--Brand: #112233;" in body
        assert b"package secret.pkg" not in body, "the source leaked"
    finally:
        httpd.shutdown()
