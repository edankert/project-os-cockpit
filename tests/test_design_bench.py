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
