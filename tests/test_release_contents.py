"""`POST /api/notes/release-contents` — composing a release ([[TASK-0558]]).

A release note has carried `features:` since [[REL-0001]] and **nothing has
ever written it**. Constructed fixtures throughout: no repo composes a release
yet, so the corpus cannot exercise any of this.
"""

from __future__ import annotations

import pytest
from pathlib import Path

from project_os_cockpit import note_writes
from project_os_cockpit.index import Index


def _repo(tmp: Path, *, status: str = "draft", features: str = "[]",
          extra: list[tuple[str, str, str, str]] | None = None) -> Path:
    docs = tmp / "docs"
    (docs / "releases").mkdir(parents=True)
    (docs / "features" / "f").mkdir(parents=True)
    (docs / "releases" / "REL-0001-R.md").write_text(
        f'---\ntype: "[[release]]"\nid: REL-0001\ntitle: "R"\n'
        f'status: {status}\nversion: "1.1.0"\nplatform: "android"\n'
        f'preparing: true\nfeatures: {features}\nupdated: "2026-01-01"\n'
        f'---\n\n# R\n', encoding="utf-8")
    for fid in ("FEAT-0001", "FEAT-0002"):
        (docs / "features" / "f" / f"{fid}-Thing.md").write_text(
            f'---\ntype: "[[feature]]"\nid: {fid}\ntitle: "Thing"\n'
            f'status: done\n---\n\n# T\n', encoding="utf-8")
    for rid, st, ver, plat in (extra or []):
        (docs / "releases" / f"{rid}-R.md").write_text(
            f'---\ntype: "[[release]]"\nid: {rid}\ntitle: "R"\n'
            f'status: {st}\nversion: "{ver}"\nplatform: "{plat}"\n'
            f'preparing: true\nfeatures: ["[[FEAT-0001-Thing]]"]\n---\n\n# R\n',
            encoding="utf-8")
    return docs


def test_add_then_remove_round_trips(tmp_path: Path) -> None:
    docs = _repo(tmp_path)
    out = note_writes.release_contents(
        Index.build(docs), "REL-0001", action="add", feature_id="FEAT-0001")
    assert out["features"] == ["[[FEAT-0001-Thing]]"]
    #: Written as an INLINE list, never a quoted string — quoting it makes the
    #: whole list one value, which is FEAT-0107/TASK-0445's defect where a
    #: release reported nothing it had verified.
    raw = (docs / "releases" / "REL-0001-R.md").read_text(encoding="utf-8")
    assert 'features: ["[[FEAT-0001-Thing]]"]' in raw, raw[:400]

    out = note_writes.release_contents(
        Index.build(docs), "REL-0001", action="remove", feature_id="FEAT-0001",
        reason="waiting on a backend deploy")
    assert out["features"] == []
    assert "features: []" in (docs / "releases" / "REL-0001-R.md").read_text()


def test_a_shipped_release_is_immutable(tmp_path: Path) -> None:
    """[[ADR-0035]]: changing what a released release contained rewrites what
    it was measured against, and a sealed ledger is only worth reading because
    that cannot happen."""
    docs = _repo(tmp_path, status="released")
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.release_contents(
            Index.build(docs), "REL-0001", action="add", feature_id="FEAT-0001")
    assert exc.value.status == 409
    assert "shipped" in exc.value.message


def test_an_unresolvable_id_is_refused(tmp_path: Path) -> None:
    """A text box for an id is how [[ISS-0142]] happened. This is the server
    half of that lesson; the candidate list is the client half."""
    docs = _repo(tmp_path)
    for bad in ("FEAT-9999", "", "REL-0001"):
        with pytest.raises(note_writes.WriteError):
            note_writes.release_contents(
                Index.build(docs), "REL-0001", action="add", feature_id=bad)


def test_the_same_feature_in_two_open_releases_on_one_platform_is_refused(
        tmp_path: Path) -> None:
    docs = _repo(tmp_path, extra=[("REL-0002", "draft", "1.2.0", "android")])
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.release_contents(
            Index.build(docs), "REL-0001", action="add", feature_id="FEAT-0001")
    assert "REL-0002" in exc.value.message


def test_across_platforms_it_is_the_normal_case(tmp_path: Path) -> None:
    """**The rule that is easy to get wrong.** An earlier draft said *any* two
    open releases, which would have been wrong the first time a feature shipped
    to both — Edwin: *"a feature can be (is more than likely) delivered to
    multiple platforms."* Measured in `your-trainer`: 45 android features, 9
    ios, 25 cross-platform.
    """
    docs = _repo(tmp_path, extra=[("REL-0002", "draft", "1.2.0", "ios")])
    out = note_writes.release_contents(
        Index.build(docs), "REL-0001", action="add", feature_id="FEAT-0001")
    assert out["features"] == ["[[FEAT-0001-Thing]]"]


def test_the_id_is_the_member_not_the_slug(tmp_path: Path) -> None:
    """`[[FEAT-0001-Thing]]` and a bare `FEAT-0001` name one feature. The slug
    is display; removing on the id must find it either way."""
    docs = _repo(tmp_path, features='["[[FEAT-0001]]"]')
    out = note_writes.release_contents(
        Index.build(docs), "REL-0001", action="remove", feature_id="FEAT-0001",
        reason="not this cycle")
    assert out["features"] == []


def test_a_bad_action_is_a_client_error(tmp_path: Path) -> None:
    docs = _repo(tmp_path)
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.release_contents(
            Index.build(docs), "REL-0001", action="toggle",
            feature_id="FEAT-0001")
    assert exc.value.status == 400


def test_the_endpoint_is_loopback_only() -> None:
    """Every write path in this server is loopback-only, and the refusals live
    in `note_writes` rather than the handler — a rule enforced at the transport
    is a rule the next caller does not get."""
    src = (Path(__file__).resolve().parents[1]
           / "src" / "project_os_cockpit" / "server.py").read_text(encoding="utf-8")
    i = src.index("def _serve_release_contents")
    body = src[i:i + 1800]
    assert "self._require_loopback()" in body
    assert "note_writes.release_contents(" in body


# ---- the candidate list and the picker (TASK-0511) -------------------------

RENDERER = (Path(__file__).resolve().parents[1]
            / "desktop" / "src" / "renderer" / "renderer.ts")


def test_a_candidate_is_not_claimed_by_another_release_on_this_platform(
        tmp_path: Path) -> None:
    """**Without a candidate list the control is a text box, and a text box for
    an id is how [[ISS-0142]] happened.**

    The list is server-owned because the rule it encodes — what another open
    release on this platform already claims — is the same one the write path
    refuses on, and two implementations of one question is [[REQ-0059]]'s
    forbidden shape (three instances found in this phase already).
    """
    from project_os_cockpit import publication

    docs = _repo(tmp_path, extra=[("REL-0002", "draft", "1.2.0", "android")])
    ids = [c["id"] for c in
           publication.contents_candidates(Index.build(docs), "REL-0001", "android")]
    assert "FEAT-0001" not in ids, "a feature another open release claims is offered"

    #: …and across platforms it is not claimed at all.
    docs = _repo(tmp_path / "b", extra=[("REL-0002", "draft", "1.2.0", "ios")])
    ids = [c["id"] for c in
           publication.contents_candidates(Index.build(docs), "REL-0001", "android")]
    assert "FEAT-0001" in ids


def test_what_the_release_already_names_is_not_a_candidate(tmp_path: Path) -> None:
    from project_os_cockpit import publication

    docs = _repo(tmp_path, features='["[[FEAT-0001-Thing]]"]')
    ids = [c["id"] for c in
           publication.contents_candidates(Index.build(docs), "REL-0001", "android")]
    assert "FEAT-0001" not in ids


def test_the_first_add_is_announced_as_a_semantic_jump() -> None:
    """**[[REQ-0048]] criterion 4**: *a release naming nothing keeps derived
    contents*, and eleven historical releases depend on it. Naming one feature
    switches the release to chosen contents — so the other rows stop being in
    it. A control that made that switch silently would be the worst kind of
    convenience, so the page says it before the click.
    """
    src = RENDERER.read_text(encoding="utf-8")
    i = src.index("const candidates = d.contents_candidates")
    block = src[i:i + 2400]
    assert "c.kind === 'derived'" in block, "the derived case is not distinguished"
    assert "the rest stop being in it" in block, (
        "the jump from derived to chosen contents is not announced"
    )


def test_compose_is_offered_only_before_a_release_ships() -> None:
    """[[ADR-0035]]: a shipped release's contents are a fact about the past."""
    src = RENDERER.read_text(encoding="utf-8")
    i = src.index("const candidates = d.contents_candidates")
    assert "d.status !== 'released'" in src[i:i + 700]
    j = src.index("drop.textContent = 'Remove'")
    assert "d.status !== 'released'" in src[max(0, j - 700):j]


def test_remove_is_offered_only_on_rows_the_release_names() -> None:
    """A derived row is not a choice anybody made, so there is nothing to take
    back — and a remove there would have to name the whole contents first,
    silently, which is the jump the warning exists to make explicit."""
    src = RENDERER.read_text(encoding="utf-8")
    j = src.index("drop.textContent = 'Remove'")
    guard = src[max(0, j - 700):j]
    assert "c.kind !== 'derived'" in guard, guard[-200:]


def test_the_client_re_decides_nothing() -> None:
    """All three refusals live in `note_writes`. A rule enforced in the
    renderer is a rule the other front door does not get ([[ISS-0230]])."""
    src = RENDERER.read_text(encoding="utf-8")
    i = src.index("async function composeRelease(")
    body = src[i:i + 1400]
    assert "/api/notes/release-contents" in body
    for reimplemented in ("released", "already in", "platform"):
        assert f"if ({reimplemented}" not in body, (
            f"the renderer is re-deciding `{reimplemented}` instead of "
            "reporting the server's refusal"
        )


# ---- a phase contributes its features (REQ-0048 criterion 2) --------------

def _repo_with_phase(tmp: Path) -> Path:
    docs = _repo(tmp)
    (docs / "phases").mkdir(parents=True, exist_ok=True)
    (docs / "phases" / "PHASE-0001-A-Phase.md").write_text(
        '---\ntype: "[[phase]]"\nid: PHASE-0001\ntitle: "A phase"\n'
        'status: active\norder: 1\n'
        'features: ["[[FEAT-0001-Thing]]", "[[FEAT-0002-Thing]]"]\n'
        '---\n\n# A phase\n', encoding="utf-8")
    return docs


def test_a_phase_contributes_its_features_and_is_not_stored(tmp_path: Path) -> None:
    """[[REQ-0048]] criterion 2: *a phase contributes features; no second
    encoding.*

    **That criterion answers the question the plan left open** — whether the
    expansion is remembered or re-derived. It is remembered **as features**:
    storing the phase would put a second encoding of membership on the release,
    and the release would disagree with the phase the first time a feature
    moved between them. A phase's members change; what a release *contains*
    must not change under it.
    """
    docs = _repo_with_phase(tmp_path)
    out = note_writes.release_contents(
        Index.build(docs), "REL-0001", action="add", feature_id="PHASE-0001")
    assert out["contributed"] == ["FEAT-0001", "FEAT-0002"]
    assert out["features"] == ["[[FEAT-0001-Thing]]", "[[FEAT-0002-Thing]]"]
    #: The phase itself is nowhere in the note.
    raw = (docs / "releases" / "REL-0001-R.md").read_text(encoding="utf-8")
    assert "PHASE-0001" not in raw, raw[:400]


def test_removing_a_phase_removes_what_it_contributed(tmp_path: Path) -> None:
    docs = _repo_with_phase(tmp_path)
    note_writes.release_contents(
        Index.build(docs), "REL-0001", action="add", feature_id="PHASE-0001")
    out = note_writes.release_contents(
        Index.build(docs), "REL-0001", action="remove", feature_id="PHASE-0001",
        reason="the whole phase slips")
    assert out["features"] == []


def test_a_phase_clash_names_the_feature_not_the_phase(tmp_path: Path) -> None:
    """A phase whose members are split across two releases must refuse on the
    **member that clashes** and say which — refusing on the phase's own id
    would leave a person with no way to find out what the problem was."""
    docs = _repo_with_phase(tmp_path)
    (docs / "releases" / "REL-0002-R.md").write_text(
        '---\ntype: "[[release]]"\nid: REL-0002\ntitle: "R"\nstatus: draft\n'
        'version: "1.2.0"\nplatform: "android"\npreparing: true\n'
        'features: ["[[FEAT-0002-Thing]]"]\n---\n\n# R\n', encoding="utf-8")
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.release_contents(
            Index.build(docs), "REL-0001", action="add", feature_id="PHASE-0001")
    assert "FEAT-0002" in exc.value.message, exc.value.message
    assert "PHASE-0001" not in exc.value.message


def test_a_phase_naming_nothing_that_resolves_is_refused(tmp_path: Path) -> None:
    """Fail-closed: a phase that contributes nothing is a broken link, not an
    empty add that reports success."""
    docs = _repo(tmp_path)
    (docs / "phases").mkdir(parents=True, exist_ok=True)
    (docs / "phases" / "PHASE-0002-Empty.md").write_text(
        '---\ntype: "[[phase]]"\nid: PHASE-0002\ntitle: "Empty"\n'
        'status: active\norder: 2\nfeatures: ["[[FEAT-9999]]"]\n'
        '---\n\n# Empty\n', encoding="utf-8")
    with pytest.raises(note_writes.WriteError):
        note_writes.release_contents(
            Index.build(docs), "REL-0001", action="add", feature_id="PHASE-0002")


def test_a_note_that_is_neither_is_refused(tmp_path: Path) -> None:
    docs = _repo(tmp_path)
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.release_contents(
            Index.build(docs), "REL-0001", action="add", feature_id="REL-0001")
    assert "carries features" in exc.value.message
