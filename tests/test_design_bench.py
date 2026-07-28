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
    # A document must not be offered device widths at all.
    assert "if (!d.viewport && v.w) b.disabled = true;" in src


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

def test_the_library_design_group_points_at_the_bench_not_the_note(tmp_path: Path) -> None:
    """Built, tested, and unreachable: the only link to `~design/<id>` lived
    inside the register, which nothing pointed to. A closed loop with no
    entrance — found by Edwin opening the app and seeing nothing."""
    docs = _corpus(tmp_path)
    groups = cockpit._library_groups(Index.build(docs), None, [])
    design = next((g for g in groups if g.get("key") == "design"), None)
    assert design is not None, "the Library has no Design group"
    for item in design["items"]:
        assert item["url"].startswith("~design/"), (
            "the Library opens the design NOTE; the note is prose about a "
            "design, the artifact is the design"
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
    assert order[:2] == ["overview", "design"], order
    for structural in ("features", "tasks", "issues"):
        assert order.index("design") < order.index(structural)

    # The strip's markup carries its own order; both must agree, because the
    # buttons are what a human actually sees.
    html = (Path(__file__).resolve().parents[1]
            / "desktop" / "src" / "renderer" / "index.html").read_text(encoding="utf-8")
    buttons = re.findall(r'top-bar-btn[^>]*data-mode="(\w+)"', html)
    assert buttons.index("design") == 1, buttons
    for structural in ("features", "tasks", "issues"):
        assert buttons.index("design") < buttons.index(structural)


def test_the_mode_has_a_button_an_icon_and_a_server_that_serves_it() -> None:
    """Three separate places, and a mode missing any one of them is broken
    in a way the other two hide. The design bench has already shipped twice
    with a payload nothing could reach; this asserts the whole path."""
    html = (Path(__file__).resolve().parents[1]
            / "desktop" / "src" / "renderer" / "index.html").read_text(encoding="utf-8")
    assert 'data-mode="design"' in html
    src = _renderer()
    assert re.search(r"design:\s*'<circle", src), "no icon; the button renders blank"
    assert "design" in cockpit.NAV_MODES
    assert cockpit._design_groups is not None


def test_reselecting_design_keeps_the_open_artifact() -> None:
    """`startsWith`, not equality. Clicking Design while DES-0002 is open
    must not throw you back to the register — reselecting a mode is not a
    request to lose your place, and equality here would make it one."""
    src = _renderer()
    block = src.split("if (currentNavMode === 'design') {")[1].split("const platform =")[0]
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
    return src.split("if (currentNavMode === 'design') {")[1].split("const platform =")[0]


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
        hoisted = bool(defn and "currentRel.startsWith('~design')" in defn.group(1))
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
    block = src.split("if (currentNavMode === 'design') {")[1].split("const platform =")[0]
    assert "return;" not in block, (
        "design mode returned early; the nav list would never load"
    )


def test_the_system_is_separated_from_the_proposals(tmp_path: Path) -> None:
    """One standing reference and many transient ones behave differently.
    Listed together, the system that never leaves gets buried among proposals
    that arrive and go quiet."""
    docs = tmp_path / "docs"
    _note(docs / "designs" / "DES-0001-System.md", {
        "type": "[[design]]", "id": "DES-0001", "title": "System",
        "status": "accepted", "role": "system"})
    _note(docs / "designs" / "DES-0002-Proposal.md", {
        "type": "[[design]]", "id": "DES-0002", "title": "Proposal",
        "status": "proposed", "role": "proposal"})
    idx = Index.build(docs)
    groups = cockpit.nav_payload(idx, mode="design")["groups"]
    assert [g["key"] for g in groups] == ["design-system", "design-proposals"]
    assert groups[0]["items"][0]["id"] == "DES-0001"
    assert groups[1]["items"][0]["id"] == "DES-0002"


def test_nav_items_point_at_the_bench_not_the_raw_note(tmp_path: Path) -> None:
    """The whole reason this mode exists: clicking a design in the Library
    did nothing, because the item pointed at a Markdown file the design
    surface never claimed. The url is overridden deliberately."""
    idx = Index.build(_corpus(tmp_path))
    groups = cockpit.nav_payload(idx, mode="design")["groups"]
    items = [i for g in groups for i in g["items"]]
    assert items, "the corpus has designs; the nav found none"
    for item in items:
        assert item["url"].startswith("~design/"), item


def test_a_design_with_no_role_is_a_proposal(tmp_path: Path) -> None:
    """Defaulting the other way would promote every unlabelled draft into the
    standing-reference slot, which is the slot that must stay small."""
    docs = tmp_path / "docs"
    _note(docs / "designs" / "DES-0003-Nameless.md", {
        "type": "[[design]]", "id": "DES-0003", "title": "Nameless",
        "status": "draft"})
    idx = Index.build(docs)
    groups = cockpit.nav_payload(idx, mode="design")["groups"]
    assert [g["key"] for g in groups] == ["design-proposals"]


def test_no_designs_yields_no_empty_headings(tmp_path: Path) -> None:
    """A project with no designs gets an empty pane, not two labelled boxes
    with nothing in them."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "README.md").write_text("# x\n", encoding="utf-8")
    idx = Index.build(docs)
    assert cockpit.nav_payload(idx, mode="design")["groups"] == []


def test_the_mode_adds_and_removes_nothing() -> None:
    """This adds a seventh button; it must not quietly retire an existing one.
    A stored preference pointing at any prior mode still has to resolve, and
    `design` must not land in the retired list where it would be migrated
    away the moment someone selected it."""
    src = _renderer()
    for prior in ("overview", "features", "tasks", "issues", "review", "library"):
        assert "'%s'" % prior in src.split("const NAV_MODES = [")[1].split("]")[0]
    retired = src.split("const RETIRED_NAV_MODES: readonly string[] = [")[1].split("]")[0]
    assert "design" not in retired
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
    btn = re.search(r'<button[^>]*data-mode="design"[^>]*>', html).group(0)
    assert btn.startswith("<button")
    assert 'role="tab"' in btn and 'aria-label="Design"' in btn


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
    b = _brief(tmp_path, "# B\n\n## REPLACE ME\nbody\n\n## Real\ncontent\n")
    assert [s["heading"] for s in b["sections"]] == ["Real"]
    for s in b["sections"]:
        assert "REPLACE" not in s["heading"].upper()
        assert "REPLACE" not in s["body"].upper()


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
