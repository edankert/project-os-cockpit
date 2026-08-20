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
        Index.build(docs), "REL-0001", action="remove", feature_id="FEAT-0001")
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
        Index.build(docs), "REL-0001", action="remove", feature_id="FEAT-0001")
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
