"""One release in preparation per platform ([[TASK-0557]]).

Edwin, 2026-08-19: *"Let's consider one release at the time only, multiple
releases should use git branches anyway. We can potentially have multiple
releases going on at the same time for different platforms."*
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from project_os_cockpit import publication
from project_os_cockpit.index import Index

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "scripts" / "validate-docs.py"


def _repo(tmp: Path, releases: list[tuple[str, str, str, str]]) -> Path:
    """`releases` is (id, status, version, platform)."""
    docs = tmp / "docs" / "releases"
    docs.mkdir(parents=True)
    (tmp / "SNAPSHOT.yaml").write_text(
        'version: 1\nproject:\n  name: "t"\n  repo_root: "."\n'
        "counters:\n  REL: 9\nitems: {}\n", encoding="utf-8")
    for rid, status, version, platform in releases:
        #: **`preparing:` is FRONTMATTER, not a status** (FEAT-0105 /
        #: TASK-0438) — `STATUSES.md` allows a release only draft / released /
        #: reverted and is template-owned. A `draft` alone is *open*, not
        #: *prepared for ship*, and the first version of these fixtures omitted
        #: the field: `preparing()` returned `None` and two assertions failed
        #: for a reason with nothing to do with platforms.
        prep = "preparing: true\n" if status == "draft" else ""
        (docs / f"{rid}-R.md").write_text(
            f'---\ntype: "[[release]]"\nid: {rid}\ntitle: "R"\n'
            f'status: {status}\nversion: "{version}"\nplatform: "{platform}"\n'
            f'{prep}---\n\n# R\n', encoding="utf-8")
    return tmp


def _errors(repo: Path) -> str:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(repo)],
        capture_output=True, text=True).stdout


def test_two_preparing_on_one_platform_is_an_error(tmp_path: Path) -> None:
    """**The state [[ADR-0037]]'s ledger cannot represent.** One working ledger
    per platform, and sealing assigns it to a release — so a verdict recorded
    while two were open would belong to neither by construction. An error, not
    a warning: it must not be reachable quietly.
    """
    repo = _repo(tmp_path, [
        ("REL-0001", "released", "1.0.0", "android"),
        ("REL-0002", "draft", "1.1.0", "android"),
        ("REL-0003", "draft", "1.2.0", "android"),
    ])
    out = _errors(repo)
    assert "ERROR [RELEASE-PREPARING]" in out, out[-500:]
    assert "REL-0002, REL-0003" in out


def test_two_platforms_preparing_at_once_is_fine(tmp_path: Path) -> None:
    """The half of the decision that permits: *"multiple releases going on at
    the same time for different platforms."*"""
    repo = _repo(tmp_path, [
        ("REL-0001", "released", "1.0.0", "android"),
        ("REL-0002", "draft", "1.1.0", "android"),
        ("REL-0003", "draft", "1.1.0", "ios"),
    ])
    assert "RELEASE-PREPARING" not in _errors(repo)


def test_a_draft_a_shipped_version_overtook_is_not_preparing(tmp_path: Path) -> None:
    """*Preparing* is narrower than `draft`. `your-trainer` carries `REL-0008`
    at `draft`, version 2.0.2, with 2.1.6 shipped — stale record-keeping, not a
    release in preparation. Counting it would report a conflict that is not
    one, and this is the exact corpus shape that would have produced it.
    """
    repo = _repo(tmp_path, [
        ("REL-0001", "draft", "2.0.2", "android"),
        ("REL-0002", "released", "2.1.6", "android"),
        ("REL-0003", "draft", "2.2.0", "android"),
    ])
    assert "RELEASE-PREPARING" not in _errors(repo)


def test_the_wrapper_still_answers_for_a_single_release(tmp_path: Path) -> None:
    """`preparing()` stays as a thin wrapper so six call sites move one at a
    time — *"a rename that touches every consumer in one commit is how the last
    three regressions in this phase were introduced."*
    """
    repo = _repo(tmp_path, [
        ("REL-0001", "released", "1.0.0", ""),
        ("REL-0002", "draft", "1.1.0", ""),
    ])
    index = Index.build(repo / "docs")
    assert (publication.preparing(index) or {}).get("id") == "REL-0002"
    assert {p: r["id"] for p, r in
            publication.preparing_by_platform(index).items()} == {"": "REL-0002"}
    assert publication.preparing_conflicts(index) == {}


def test_a_release_with_no_platform_is_its_own_key(tmp_path: Path) -> None:
    """*"A release with no `platform:` takes them all"* — the opt-in rule
    [[DES-0012]] D4 gives release contents. Keyed under `""`, the
    platform-less world every repo but `your-trainer` lives in.
    """
    repo = _repo(tmp_path, [
        ("REL-0001", "draft", "1.1.0", ""),
        ("REL-0002", "draft", "1.1.0", "ios"),
    ])
    index = Index.build(repo / "docs")
    assert set(publication.preparing_by_platform(index)) == {"", "ios"}
    assert publication.preparing_conflicts(index) == {}


def test_the_two_version_parsers_agree() -> None:
    """The validator restates `_version_key` because it is stdlib-only and
    copied downstream. Two copies of one predicate is [[REQ-0059]]'s forbidden
    shape unless something holds them to the same answers — this does.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location("_vd", VALIDATOR)
    vd = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(vd)
    for raw in ("1.0.0", "2.1.10", "2.1.9", "v3.0", "", "1.2.3-rc1", "2.0"):
        assert vd._release_version_key(raw) == publication._version_key(raw), raw


def test_two_open_drafts_nobody_declared_are_not_a_conflict(tmp_path: Path) -> None:
    """**`preparing:` is frontmatter, not a status** (FEAT-0105 / TASK-0438).

    The first cut of the validator rule keyed on `status: draft` alone, so it
    and `publication.preparing` would have disagreed about what *preparing*
    means — [[REQ-0059]]'s one-question-two-implementations, and the third
    instance found in this phase. Two open drafts nobody has declared for ship
    are an ordinary repo, not an error.
    """
    docs = tmp_path / "docs" / "releases"
    docs.mkdir(parents=True)
    (tmp_path / "SNAPSHOT.yaml").write_text(
        'version: 1\nproject:\n  name: "t"\n  repo_root: "."\n'
        "counters:\n  REL: 9\nitems: {}\n", encoding="utf-8")
    for rid, version in (("REL-0002", "1.1.0"), ("REL-0003", "1.2.0")):
        (docs / f"{rid}-R.md").write_text(
            f'---\ntype: "[[release]]"\nid: {rid}\ntitle: "R"\n'
            f'status: draft\nversion: "{version}"\nplatform: "android"\n'
            f'---\n\n# R\n', encoding="utf-8")
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(tmp_path)],
        capture_output=True, text=True).stdout
    assert "RELEASE-PREPARING" not in out, out[-400:]
    #: …and the library agrees, which is the property that matters.
    index = Index.build(tmp_path / "docs")
    assert publication.preparing_conflicts(index) == {}
    assert publication.preparing_by_platform(index) == {}
