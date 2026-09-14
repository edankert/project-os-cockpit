"""The survey — the screens this release changed ([[TASK-0620]], upstream ADR-0045).

The checks say what must be true. None of them says *open the screens this
release touched and look*, which is the first thing Edwin does by habit and the
one thing the suite never asks for.

**Where the answer comes from changed on 2026-09-14.** It used to be the
ledger's invalidation events joined to each check's `area:`. An invalidation
names a check and never a screen, so the survey listed test categories such as
"Hardware", which spans five screens, and a change that altered a screen
without reopening a check was invisible. The answer is now the `## Impact`
list on every change note added since the last release tag: one `SUR-*` id per
screen, each with one sentence somebody using the product would understand
(project-os-dev ADR-0045 decision 1; `tools/instructions/TESTING.md`, "The
walk", rule 2).

The rule lives upstream and the bundled module implements it. These tests
assert that the cockpit's payload carries that answer, and carries it in the
shape the page reads.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from project_os_cockpit import acceptance, ledger
from project_os_cockpit.index import Index


def _check(docs: Path, tid: str, *, area: str) -> None:
    (docs / "tests" / "acceptance").mkdir(parents=True, exist_ok=True)
    (docs / "tests" / "acceptance" / f"{tid}.md").write_text(
        f'---\ntype: "[[test]]"\nid: {tid}\ntitle: "{tid}"\n'
        f'level: acceptance\nstatus: active\narea: "{area}"\n'
        f"---\n\n# {tid}\n", encoding="utf-8")


def _ledger(docs: Path, entries: list[dict], platform: str = "android") -> None:
    path = docs / "releases" / "ledgers" / f"WORKING-{platform}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"platform": platform, "entries": entries}),
                    encoding="utf-8")


def _release(docs: Path, *, tag: str = "v1.0", platform: str = "android",
             status: str = "released") -> None:
    (docs / "releases").mkdir(parents=True, exist_ok=True)
    (docs / "releases" / "REL-0001-v1.0.md").write_text(
        '---\ntype: "[[release]]"\nid: REL-0001\ntitle: "v1.0"\n'
        f'status: {status}\nversion: "1.0"\ntag: "{tag}"\n'
        f'date: "2026-08-01"\nplatform: "{platform}"\n---\n\n# v1.0\n',
        encoding="utf-8")


def _surface(docs: Path, sid: str, title: str, *, parent: str = "",
             gallery: str = "[]") -> None:
    (docs / "surfaces").mkdir(parents=True, exist_ok=True)
    (docs / "surfaces" / f"{sid}.md").write_text(
        f'---\ntype: "[[surface]]"\nid: {sid}\ntitle: "{title}"\n'
        f'status: active\nkind: screen\nparent: "{parent}"\n'
        f"gallery: {gallery}\n---\n\n# {title}\n", encoding="utf-8")


def _change(docs: Path, stem: str, title: str, impact: str) -> None:
    (docs / "changes").mkdir(parents=True, exist_ok=True)
    (docs / "changes" / f"{stem}.md").write_text(
        f'---\ntype: "[[change]]"\nid: {stem}\ntitle: "{title}"\n'
        f"status: merged\n---\n\n# {title}\n\n## Impact\n\n{impact}\n",
        encoding="utf-8")


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), "-c", "user.email=f@f",
                    "-c", "user.name=fixture", *args],
                   check=True, capture_output=True)


def _repo(tmp_path: Path) -> Path:
    """A git checkout with one tagged commit, and docs/ inside it.

    The survey asks git which change notes are new, so a fixture without a
    repository and a tag can only exercise the "no release to compare
    against" answer.
    """
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q"],
                   check=True, capture_output=True)
    return docs


def _tag(tmp_path: Path, name: str = "v1.0") -> None:
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-m", "at the tag")
    _git(tmp_path, "tag", name)


def _commit(tmp_path: Path) -> None:
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-m", "after the tag")


def _payload(docs: Path, platform: str = "android") -> dict:
    return acceptance.walk_payload(docs, Index.build(docs), platform=platform)


def _survey(docs: Path, platform: str = "android") -> list[dict]:
    return _payload(docs, platform)["survey"]


# --------------------------------------------------- what reaches the survey

def test_a_change_note_added_since_the_tag_names_its_screen(
        tmp_path: Path) -> None:
    docs = _repo(tmp_path)
    _check(docs, "TST-0001", area="Profile")
    _surface(docs, "SUR-0001", "Profile")
    _release(docs)
    _ledger(docs, [])
    _tag(tmp_path)
    _change(docs, "CHG-20260902-The-Profile-Moves", "The profile moves",
            "- [[SUR-0001]]: the sign-in button sits under the avatar now.")
    _commit(tmp_path)

    survey = _survey(docs)
    assert [e["surface"] for e in survey] == ["Profile"]
    assert survey[0]["surface_note"] == "SUR-0001"
    assert [c["sentence"] for c in survey[0]["changes"]] == [
        "the sign-in button sits under the avatar now."]
    assert survey[0]["changes"][0]["title"] == "The profile moves"


def test_a_change_note_that_existed_at_the_tag_is_not_in_the_survey(
        tmp_path: Path) -> None:
    """The survey is what changed since the last release, not what ever did."""
    docs = _repo(tmp_path)
    _check(docs, "TST-0001", area="Profile")
    _surface(docs, "SUR-0001", "Profile")
    _release(docs)
    _ledger(docs, [])
    _change(docs, "CHG-20260701-Shipped-Already", "Shipped already",
            "- [[SUR-0001]]: this sentence belongs to the last release.")
    _tag(tmp_path)

    assert _survey(docs) == []


def test_a_change_that_altered_no_screen_adds_nothing(tmp_path: Path) -> None:
    docs = _repo(tmp_path)
    _check(docs, "TST-0001", area="Profile")
    _surface(docs, "SUR-0001", "Profile")
    _release(docs)
    _ledger(docs, [])
    _tag(tmp_path)
    _change(docs, "CHG-20260902-A-Build-Script", "A build script moved",
            "- No screen changed: it is a build script.")
    _commit(tmp_path)

    assert _survey(docs) == []


def test_an_id_no_surface_note_carries_is_kept_and_flagged(
        tmp_path: Path) -> None:
    """Dropped, it would be a screen somebody altered and nobody can open."""
    docs = _repo(tmp_path)
    _check(docs, "TST-0001", area="Profile")
    _release(docs)
    _ledger(docs, [])
    _tag(tmp_path)
    _change(docs, "CHG-20260902-A-Ghost", "A ghost",
            "- [[SUR-9999]]: something moved here.")
    _commit(tmp_path)

    entry = _survey(docs)[0]
    assert entry["surface"] == "SUR-9999"
    assert entry["unresolved"] is True


def test_the_survey_names_no_check_at_all(tmp_path: Path) -> None:
    """Rule 2: it is a list of places to open, not a list of things to run."""
    docs = _repo(tmp_path)
    _check(docs, "TST-0001", area="Profile")
    _surface(docs, "SUR-0001", "Profile")
    _release(docs)
    _ledger(docs, [])
    _tag(tmp_path)
    _change(docs, "CHG-20260902-The-Profile-Moves", "The profile moves",
            "- [[SUR-0001]]: the avatar moved.")
    _commit(tmp_path)

    payload = _payload(docs)
    assert payload["counts"]["owed"] == 1
    assert "TST-" not in json.dumps(payload["survey"])


# ------------------------------------------------------------- the shape

def test_a_child_screen_carries_its_parent(tmp_path: Path) -> None:
    """A dialog is a child surface and the page nests it (ADR-0044 rule 2)."""
    docs = _repo(tmp_path)
    _check(docs, "TST-0001", area="Profile")
    _surface(docs, "SUR-0001", "Profile")
    _surface(docs, "SUR-0002", "Avatar dialog", parent="[[SUR-0001]]")
    _release(docs)
    _ledger(docs, [])
    _tag(tmp_path)
    _change(docs, "CHG-20260902-Both", "Both",
            "- [[SUR-0001]]: the avatar moved.\n"
            "- [[SUR-0002]]: the dialog asks for a crop.")
    _commit(tmp_path)

    survey = _survey(docs)
    assert [(e["surface"], e["parent"]) for e in survey] == [
        ("Profile", None), ("Avatar dialog", "SUR-0001")]


def test_captures_are_the_screen_before_and_the_screen_now(
        tmp_path: Path) -> None:
    docs = _repo(tmp_path)
    _check(docs, "TST-0001", area="Profile")
    _surface(docs, "SUR-0001", "Profile", gallery='[profile, "profile-pro:pro"]')
    _release(docs)
    _ledger(docs, [])
    gallery = docs / "tests" / "acceptance" / "gallery"
    (gallery / "v1.0").mkdir(parents=True)
    (gallery / "candidate").mkdir(parents=True)
    (gallery / "v1.0" / "profile.png").write_bytes(b"before")
    (gallery / "candidate" / "profile.png").write_bytes(b"now")
    (gallery / "candidate" / "profile-pro.png").write_bytes(b"now")
    _tag(tmp_path)
    _change(docs, "CHG-20260902-The-Profile-Moves", "The profile moves",
            "- [[SUR-0001]]: the avatar moved.")
    _commit(tmp_path)

    captures = _survey(docs)[0]["captures"]
    assert [(c["key"], c["state"], c["new"]) for c in captures] == [
        ("profile", None, False), ("profile-pro", "pro", True)]
    assert captures[0]["before"].endswith("gallery/v1.0/profile.png")
    assert captures[0]["after"].endswith("gallery/candidate/profile.png")
    assert captures[1]["before"] is None


# --------------------------------------------------- when there is no anchor

def test_a_project_with_no_released_note_says_so_and_still_walks(
        tmp_path: Path) -> None:
    docs = _repo(tmp_path)
    _check(docs, "TST-0001", area="Profile")
    _surface(docs, "SUR-0001", "Profile")
    _ledger(docs, [])
    _tag(tmp_path)
    _change(docs, "CHG-20260902-The-Profile-Moves", "The profile moves",
            "- [[SUR-0001]]: the avatar moved.")
    _commit(tmp_path)

    payload = _payload(docs)
    assert payload["survey"] == []
    assert "no released REL-* note" in payload["survey_problem"]
    assert payload["counts"]["owed"] == 1


def test_a_tag_the_checkout_does_not_carry_says_which_tag(
        tmp_path: Path) -> None:
    """A shallow clone in CI. The survey goes; the rest of the walk stays."""
    docs = _repo(tmp_path)
    _check(docs, "TST-0001", area="Profile")
    _surface(docs, "SUR-0001", "Profile")
    _release(docs, tag="v9.9")
    _ledger(docs, [])
    _tag(tmp_path)

    payload = _payload(docs)
    assert payload["survey"] == []
    assert "v9.9" in payload["survey_problem"]
    assert payload["counts"]["owed"] == 1


def test_the_survey_is_per_platform(tmp_path: Path) -> None:
    """Each platform names its own release note, and tags them differently."""
    docs = _repo(tmp_path)
    _check(docs, "TST-0001", area="Profile")
    _surface(docs, "SUR-0001", "Profile")
    _release(docs, platform="android")
    _ledger(docs, [], platform="android")
    _ledger(docs, [], platform="ios")
    _tag(tmp_path)
    _change(docs, "CHG-20260902-The-Profile-Moves", "The profile moves",
            "- [[SUR-0001]]: the avatar moved.")
    _commit(tmp_path)

    assert [e["surface"] for e in _survey(docs, "android")] == ["Profile"]
    ios = _payload(docs, "ios")
    assert ios["survey"] == []
    assert "no released REL-* note for ios" in ios["survey_problem"]


# ------------------------------------------------------------- the live corpus

YOUR_TRAINER = Path(__file__).resolve().parents[2] / "your-trainer" / "docs"


@pytest.mark.skipif(not YOUR_TRAINER.is_dir(),
                    reason="your-trainer is not checked out beside this repo")
def test_the_live_survey_is_what_its_change_notes_name() -> None:
    """Both sides built here rather than pinned to a number.

    The corpus moves, and a test asserting *three screens* would fail on the
    next change note for no reason anybody could act on. What is asserted is
    the join: every screen on the survey was named by a change note added
    since the tag, and every such screen is on the survey.
    """
    walk = acceptance._walk_module()
    index = Index.build(YOUR_TRAINER)
    platform = (ledger.platforms(YOUR_TRAINER) or ["android"])[0]
    payload = acceptance.walk_payload(YOUR_TRAINER, index, platform=platform)

    repo_root = YOUR_TRAINER.parent
    _, tag, problem = walk.last_release(YOUR_TRAINER, platform)
    if not tag or problem:
        pytest.skip("your-trainer has no reachable release tag for %s" % platform)
    added, problem = walk.changes_since(repo_root, tag)
    if problem:
        pytest.skip(problem)

    expected = {sid for change in walk.load_changes(YOUR_TRAINER, repo_root,
                                                    only=added)
                for sid, _ in change.screens}
    got = {e["surface_note"] or e["surface"] for e in payload["survey"]}
    assert got == expected
    assert "TST-" not in json.dumps(payload["survey"])
