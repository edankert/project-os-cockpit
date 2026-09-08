"""Preparing a release is one workflow ([[FEAT-0145]], [[REQ-0061]]).

Four write paths that did not exist and one computation that nobody ran:
setting a release's **version** and **platform** after it was created,
**abandoning** one that will not ship, **settling** the checks it owes from the
page that reports them, and the **coverage sweep** that says what it ships that
nothing verifies.

Constructed fixtures throughout. This repo has one release, no ledger and no
abandoned note, so the corpus cannot exercise any of it — the same reason
[[TASK-0576]]'s suite is built rather than measured.

The one thing measured rather than constructed is the shape of the refusals:
they are `create_release`'s, and `test_the_version_refusals_are_one_function`
asserts the two paths share the code rather than agreeing by inspection.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from project_os_cockpit import ledger, note_writes, publication
from project_os_cockpit.index import Index


def _repo(
    tmp: Path, *, platform: str = "android", status: str = "draft",
    version: str = "1.1.0", created: str = "2026-01-01",
    ledgers: tuple[str, ...] = ("android", "ios"),
    covered: bool = True, exception: str = "",
) -> Path:
    """One done feature, one check that may or may not cover it, one release.

    `covered=False` is the state [[TASK-0603]] exists for and the one the
    fixture had to be taught: a repo whose check names nothing was passing the
    positive case by accident, which is exactly how `FEATURE-UNCOVERED`'s own
    guard went a month without testing its positive half.
    """
    docs = tmp / "docs"
    (docs / "releases" / "ledgers").mkdir(parents=True)
    (docs / "features" / "f").mkdir(parents=True)
    (docs / "tests" / "acceptance").mkdir(parents=True)
    (tmp / "SNAPSHOT.yaml").write_text(
        'version: 1\nproject:\n  name: "t"\n  repo_root: "."\nitems: {}\n',
        encoding="utf-8")

    extra = f'acceptance_exception: "{exception}"\n' if exception else ""
    (docs / "features" / "f" / "FEAT-0001-T.md").write_text(
        '---\ntype: "[[feature]]"\nid: FEAT-0001\ntitle: "Thing"\n'
        f'status: done\nplatform: "{platform}"\n{extra}'
        '---\n\n# T\n', encoding="utf-8")
    covers = '["[[FEAT-0001]]"]' if covered else "[]"
    (docs / "tests" / "acceptance" / "TST-0001-C.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0001\ntitle: "Check one"\n'
        'level: acceptance\nstatus: active\narea: "Sync"\nmark: todo\n'
        f'covers: {covers}\n---\n\n# C\n\nOpen Settings and read the line.\n',
        encoding="utf-8")

    (docs / "releases" / "REL-0001-v1.1.0.md").write_text(
        '---\ntype: "[[release]]"\nid: REL-0001\ntitle: "R"\n'
        f'status: {status}\nversion: "{version}"\nplatform: "{platform}"\n'
        f'preparing: "2026-09-08"\nfeatures: []\ncreated: {created}\n'
        'updated: "2026-09-08"\n---\n\n# R\n', encoding="utf-8")
    for name in ledgers:
        (docs / "releases" / "ledgers" / f"WORKING-{name}.json").write_text(
            json.dumps({"platform": name, "entries": []}), encoding="utf-8")
    return docs


def _fm(docs: Path, name: str = "REL-0001-v1.1.0.md") -> dict:
    raw = (docs / "releases" / name).read_text(encoding="utf-8")
    return yaml.safe_load(raw.split("---", 2)[1]) or {}


# ---- step 2: the platform is offered, not typed ---------------------------

def test_platform_candidates_union_the_ledgers_and_the_notes(tmp_path: Path) -> None:
    """Both sources, because they answer different questions.

    A ledger platform is one a verdict has been recorded against; a note
    platform is one somebody tagged work with. Offering only the first hides a
    platform nobody has walked yet; offering only the second hides one whose
    ledger exists because a release was drafted against it.
    """
    docs = _repo(tmp_path, platform="web", ledgers=("android", "ios"))
    rows = publication.platform_candidates(Index.build(docs))
    ids = [r["id"] for r in rows]
    assert ids[0] == "", "every platform is not the first option"
    assert set(ids) == {"", "android", "ios", "web"}
    by_id = {r["id"]: r for r in rows}
    assert by_id["android"]["ledger"] and not by_id["android"]["in_notes"]
    assert by_id["web"]["in_notes"] and not by_id["web"]["ledger"]


def test_a_repo_with_nothing_still_gets_the_every_platform_option(
        tmp_path: Path) -> None:
    """An empty picker is a question with no answers."""
    docs = _repo(tmp_path, platform="", ledgers=())
    rows = publication.platform_candidates(Index.build(docs))
    assert [r["id"] for r in rows] == [""]


def test_no_candidate_is_a_value_the_write_path_would_refuse(
        tmp_path: Path) -> None:
    """**The picker never offers what the writer rejects.**

    `platform:` is free text in the corpus and one repo carries `Android 14`
    with a space. It becomes a ledger filename, so `ledger.working_path`
    refuses it — and offering it would be a control whose only outcome is an
    error message.
    """
    docs = _repo(tmp_path, platform="android")
    (docs / "features" / "f" / "FEAT-0002-U.md").write_text(
        '---\ntype: "[[feature]]"\nid: FEAT-0002\ntitle: "U"\n'
        'status: done\nplatform: "Android 14"\n---\n\n# U\n', encoding="utf-8")
    rows = publication.platform_candidates(Index.build(docs))
    for row in rows:
        if not row["id"]:
            continue
        ledger.working_path(docs, row["id"])          # raises if unusable


# ---- step 1: version and platform after creation --------------------------

def test_creating_a_release_writes_its_platform_and_scopes_the_gate(
        tmp_path: Path) -> None:
    """[[REQ-0061]] criterion 1, both halves and the control that sends it.

    `create_release` learned to take a `platform` under [[ISS-0290]], and the
    page's *Name the version* control posted `{version, actor}` and nothing
    else — so **every release created in the tool still arrived
    platform-less**, and the gate still fell back to the union. The write path
    was fixed and the only caller was not, which is a state no test asked
    about.
    """
    docs = _repo(tmp_path, ledgers=("android", "ios"))
    (docs / "releases" / "REL-0001-v1.1.0.md").unlink()
    #: Android has walked the only check; iOS has walked nothing. A release
    #: that names Android is clear, one that names nothing takes the union and
    #: is not.
    (docs / "releases" / "ledgers" / "WORKING-android.json").write_text(
        json.dumps({"platform": "android", "entries": [
            {"check": "TST-0001", "date": "2026-09-08", "mark": "pass",
             "by": "user:edwin", "method": "manual"}]}), encoding="utf-8")

    out = note_writes.create_release(
        Index.build(docs), docs, title="v3.0.0", version="3.0.0",
        platform="android", actor="user:edwin")
    assert out["platform"] == "android"
    assert out["ledger"].endswith("WORKING-android.json")
    #: The id is allocated from the corpus, and deleting the fixture's release
    #: file does not lower the high-water mark — so this is REL-0001 again in a
    #: repo whose only release note was just removed. Read the id the writer
    #: reports rather than one composed here.
    written = docs / "releases" / f"{out['id']}-v3.0.0.md"
    assert written.is_file(), sorted(p.name for p in (docs / "releases").glob("*.md"))
    assert _fm(docs, written.name)["platform"] == "android"

    payload = publication.release_payload(
        tmp_path, Index.build(docs), out["id"])
    assert payload["gate"]["platform"] == "android"
    assert not payload["gate"]["blocking"], (
        "the gate on the next screen is not scoped to the platform just named")

    #: **And the control sends it.** Asserted on the renderer's source, because
    #: there is no DOM harness — the same limit every other surface guard here
    #: has, and the reason the defect above survived: the write path had a test
    #: and its only caller had none.
    src = (Path(__file__).resolve().parents[1] / "desktop" / "src" / "renderer"
           / "renderer.ts").read_text(encoding="utf-8")
    start = src.index("'/api/notes/release-prepare'")
    assert "platform: picker.value" in src[start:start + 200], (
        "the create control posts no platform, so a release drafted in the "
        "tool arrives platform-less")


def test_setting_the_platform_writes_it_and_creates_its_ledger(
        tmp_path: Path) -> None:
    """[[ISS-0290]]'s other half, on the update path.

    `ledger.platforms()` reads the directory, so a platform with no file is one
    the tool does not know the repo has — and a release whose platform has no
    ledger cannot accept the first verdict of its own cycle.
    """
    docs = _repo(tmp_path, platform="", ledgers=())
    out = note_writes.update_release(
        Index.build(docs), docs, "REL-0001", platform="ios")
    assert _fm(docs)["platform"] == "ios"
    assert (docs / "releases" / "ledgers" / "WORKING-ios.json").is_file()
    assert out["ledger"].endswith("WORKING-ios.json")


def test_changing_the_platform_moves_the_gate_and_touches_no_check(
        tmp_path: Path) -> None:
    """[[REQ-0061]] criterion 2, and it is the criterion [[ISS-0288]] earned.

    A release that says `ios` is graded against the iOS ledger; one that says
    nothing takes the union, where a check clears only if every platform
    cleared it. Two ledgers is what it takes to see the difference.
    """
    docs = _repo(tmp_path, platform="")
    (docs / "releases" / "ledgers" / "WORKING-android.json").write_text(
        json.dumps({"platform": "android", "entries": [
            {"check": "TST-0001", "date": "2026-09-08", "mark": "pass",
             "by": "user:edwin", "method": "manual"}]}), encoding="utf-8")
    before = (docs / "tests" / "acceptance" / "TST-0001-C.md").read_text(
        encoding="utf-8")

    union = publication.release_payload(tmp_path, Index.build(docs), "REL-0001")
    assert union["gate"]["blocking"], "the union should still owe this check"

    note_writes.update_release(
        Index.build(docs), docs, "REL-0001", platform="android")
    scoped = publication.release_payload(
        tmp_path, Index.build(docs), "REL-0001")
    assert not scoped["gate"]["blocking"], (
        "naming the platform did not scope the gate to its ledger")
    assert (docs / "tests" / "acceptance" / "TST-0001-C.md").read_text(
        encoding="utf-8") == before, "a check note was rewritten"


def test_the_version_refusals_are_one_function(tmp_path: Path) -> None:
    """`create_release` and `update_release` share the code, not an opinion.

    Two implementations of one rule is [[REQ-0059]]'s forbidden shape, and this
    one would drift quietly: a version refusal that disagrees between creating
    and editing is invisible until somebody edits.
    """
    docs = _repo(tmp_path, status="released", version="2.0.0")
    index = Index.build(docs)
    (docs / "releases" / "REL-0002-v2.1.0.md").write_text(
        '---\ntype: "[[release]]"\nid: REL-0002\ntitle: "N"\nstatus: draft\n'
        'version: "2.1.0"\nplatform: "android"\npreparing: ""\nfeatures: []\n'
        'created: 2026-09-08\nupdated: "2026-09-08"\n---\n\n# N\n',
        encoding="utf-8")
    index = Index.build(docs)
    for bad, why in (("nope", "not a version"), ("1.9.0", "at or below")):
        with pytest.raises(note_writes.WriteError) as exc:
            note_writes.update_release(index, docs, "REL-0002", version=bad)
        assert why in exc.value.message


def test_a_shipped_release_refuses_every_change(tmp_path: Path) -> None:
    """[[ADR-0035]]: what a released release contained is a fact about the
    past. Three write paths, one refusal, and it names the decision."""
    docs = _repo(tmp_path, status="released")
    index = Index.build(docs)
    for call in (
        lambda: note_writes.update_release(index, docs, "REL-0001",
                                           platform="ios"),
        lambda: note_writes.abandon_release(index, "REL-0001", reason="no"),
        lambda: note_writes.delete_release(index, docs, "REL-0001"),
    ):
        with pytest.raises(note_writes.WriteError) as exc:
            call()
        assert exc.value.status == 409
        assert "shipped" in exc.value.message


def test_an_abandoned_release_cannot_be_deleted_changed_or_settled(
        tmp_path: Path) -> None:
    """**The defect the tests did not have.**

    The first cut refused only `released`, so an abandoned release could be
    deleted outright — which destroys precisely the record abandoning exists to
    keep, and it could be done on the same day it was abandoned, because the
    only other guard was *created today*. Found by walking the endpoints
    against a live sidecar; every test asked about a `draft`.

    Each refusal names the status it hit: *shipped*, *rolled back* and
    *abandoned* are terminal for different reasons, and one shared message
    would give the right answer for the wrong one.
    """
    docs = _repo(tmp_path, created=note_writes._today())
    note_writes.abandon_release(
        Index.build(docs), "REL-0001", reason="dropped", actor="user:edwin")
    index = Index.build(docs)

    assert "abandoned" in note_writes.delete_refusal(index, docs, "REL-0001")
    for call in (
        lambda: note_writes.delete_release(index, docs, "REL-0001"),
        lambda: note_writes.update_release(index, docs, "REL-0001",
                                           version="9.9.9"),
        lambda: note_writes.settle_checks(
            docs, index, release_id="REL-0001", checks=["TST-0001"],
            mark="excused", reason="no", by="user:edwin"),
    ):
        with pytest.raises(note_writes.WriteError) as exc:
            call()
        assert exc.value.status == 409
        assert "abandoned" in exc.value.message
    assert (docs / "releases" / "REL-0001-v1.1.0.md").is_file()

    #: **And the page offers none of it.** A settle list on a release whose
    #: every settle would be refused is a screen of buttons that exist to fail.
    payload = publication.release_payload(tmp_path, index, "REL-0001")
    assert payload["settle"] == []
    assert payload["coverage"]["scoped"] is False
    assert "abandoned" in payload["delete_refusal"] or not payload["delete_refusal"]

    #: Abandoning one twice says so, rather than saying it cannot be changed —
    #: a different fact, and the one a reader needs.
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.abandon_release(
            Index.build(docs), "REL-0001", reason="again")
    assert "already abandoned" in exc.value.message


def test_the_filename_is_not_renamed_and_the_write_says_so(
        tmp_path: Path) -> None:
    """Every `[[REL-0001-v1.1.0]]` in the corpus resolves through the stem.

    Renaming the file to match a new version would break links to buy a tidier
    path, so the version moves and the name does not — and the response says
    the two have parted, because a reader who later greps for the number needs
    to know.
    """
    docs = _repo(tmp_path)
    out = note_writes.update_release(
        Index.build(docs), docs, "REL-0001", version="1.2.0")
    assert (docs / "releases" / "REL-0001-v1.1.0.md").is_file()
    assert _fm(docs)["version"] == "1.2.0"
    assert out["stale_stem"] is True
    assert out["stem"] == "REL-0001-v1.1.0"


# ---- step 1: abandoning ---------------------------------------------------

def test_abandoning_needs_a_reason(tmp_path: Path) -> None:
    """The note survives precisely so somebody can read why the number was
    skipped. An abandoned release with no reason is a deleted one that still
    takes up space."""
    docs = _repo(tmp_path)
    index = Index.build(docs)
    for empty in ("", "   ", "\n"):
        with pytest.raises(note_writes.WriteError) as exc:
            note_writes.abandon_release(index, "REL-0001", reason=empty)
        assert exc.value.status == 400
        assert "reason" in exc.value.message


def test_abandoning_keeps_the_note_its_reason_and_its_successor(
        tmp_path: Path) -> None:
    """[[REQ-0061]] criterion 3, all three halves."""
    docs = _repo(tmp_path)
    (docs / "releases" / "REL-0002-v1.2.0.md").write_text(
        '---\ntype: "[[release]]"\nid: REL-0002\ntitle: "N"\nstatus: draft\n'
        'version: "1.2.0"\nplatform: "android"\npreparing: ""\nfeatures: []\n'
        'created: 2026-09-08\nupdated: "2026-09-08"\n---\n\n# N\n',
        encoding="utf-8")
    index = Index.build(docs)
    note_writes.abandon_release(
        index, "REL-0001", reason="the store rejected the build",
        superseded_by="REL-0002", actor="user:edwin")
    fm = _fm(docs)
    assert (docs / "releases" / "REL-0001-v1.1.0.md").is_file()
    assert fm["status"] == "abandoned"
    assert "REL-0002" in str(fm["superseded_by"])
    #: `preparing:` is what tells the gate obligation a release window is open.
    #: An abandoned release still carrying it asks for a walk nobody owes.
    assert not str(fm.get("preparing") or "").strip()
    body = (docs / "releases" / "REL-0001-v1.1.0.md").read_text(encoding="utf-8")
    assert "the store rejected the build" in body


def test_an_abandoned_version_is_not_silently_reusable(tmp_path: Path) -> None:
    """The whole reason abandoning keeps the file.

    The number stays taken, and the refusal names the note holding it — so
    reusing it deliberately is possible and reusing it by accident is not.
    """
    docs = _repo(tmp_path)
    note_writes.abandon_release(
        Index.build(docs), "REL-0001", reason="dropped")
    index = Index.build(docs)
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.create_release(
            index, docs, title="v1.1.0", version="1.1.0")
    assert "REL-0001" in exc.value.message


def test_an_abandoned_release_is_not_open(tmp_path: Path) -> None:
    """`open_releases` filters on `draft`, so abandoning takes the release out
    of every count that asks what is in flight — which is the state
    `your-trainer`'s REL-0013 has been wrongly inside since 2026-08-16."""
    docs = _repo(tmp_path)
    assert publication.open_releases(Index.build(docs))
    note_writes.abandon_release(Index.build(docs), "REL-0001", reason="no")
    assert not publication.open_releases(Index.build(docs))
    assert not publication.stale_drafts(Index.build(docs))


def test_an_abandoned_release_still_appears_in_the_navigator(
        tmp_path: Path) -> None:
    """**The point of keeping the note is that somebody can find it.**

    The publication navigator built rows for open drafts, released releases
    and overtaken drafts — three populations that between them do not include
    `abandoned`. So abandoning a release removed it from the one surface whose
    subject is releases, and the answer to *what happened to 2.1.7* was
    silence. `REQ-0061` criterion 3 was literally met and its argument was not.

    Found by independent review, 2026-09-08.
    """
    from project_os_cockpit import cockpit

    docs = _repo(tmp_path)
    before = cockpit.nav_payload(Index.build(docs), mode="publication")
    assert any(g["key"].startswith("release-") for g in before["groups"])

    note_writes.abandon_release(
        Index.build(docs), "REL-0001", reason="the store rejected the build")
    after = cockpit.nav_payload(Index.build(docs), mode="publication")
    rows = [g for g in after["groups"] if g["key"] == "abandoned-REL-0001"]
    assert rows, [g["key"] for g in after["groups"]]
    assert rows[0]["status"] == "abandoned"
    assert "1.1.0" in rows[0]["label"]
    assert not rows[0]["default_open"], "a fact about the past is not work"


def test_abandoned_is_a_legal_release_status_everywhere() -> None:
    """Upstream and down, or a repo writes a status its own validator rejects.

    `validate_docs_bundled.py` is the sidecar's copy and is NOT covered by
    `sync-project-os.sh`, which copies `tools/` — so it needs its own edit and
    is the one that would have been missed.
    """
    from project_os_cockpit import statuses, validate_docs_bundled

    assert "abandoned" in validate_docs_bundled.ALLOWED_STATUS["release"]
    assert "abandoned" in statuses.VOCABULARY
    assert "abandoned" in statuses.COMPLETED_STATUSES
    root = Path(__file__).resolve().parents[1]
    for rel in ("tools/scripts/validate-docs.py",
                "tools/instructions/STATUSES.md"):
        assert "abandoned" in (root / rel).read_text(encoding="utf-8"), rel


# ---- step 1: the narrow delete -------------------------------------------

def test_delete_is_refused_for_a_note_that_is_not_brand_new(
        tmp_path: Path) -> None:
    docs = _repo(tmp_path, created="2026-01-01")
    refusal = note_writes.delete_refusal(Index.build(docs), docs, "REL-0001")
    assert "abandon it instead" in refusal


def test_delete_is_refused_when_something_links_to_it(tmp_path: Path) -> None:
    docs = _repo(tmp_path, created=note_writes._today())
    (docs / "features" / "f" / "FEAT-0002-L.md").write_text(
        '---\ntype: "[[feature]]"\nid: FEAT-0002\ntitle: "L"\nstatus: done\n'
        '---\n\n# L\n\nShips in [[REL-0001-v1.1.0]].\n', encoding="utf-8")
    refusal = note_writes.delete_refusal(Index.build(docs), docs, "REL-0001")
    assert "FEAT-0002" in refusal


def test_delete_is_refused_when_a_ledger_is_sealed_against_it(
        tmp_path: Path) -> None:
    docs = _repo(tmp_path, created=note_writes._today())
    (docs / "releases" / "ledgers" / "REL-0001-android.json").write_text(
        json.dumps({"platform": "android", "release": "REL-0001",
                    "version": "1.1.0", "sealed": "2026-09-08",
                    "entries": []}), encoding="utf-8")
    refusal = note_writes.delete_refusal(Index.build(docs), docs, "REL-0001")
    assert "sealed" in refusal


def test_delete_removes_a_note_nothing_has_become_part_of(
        tmp_path: Path) -> None:
    docs = _repo(tmp_path, created=note_writes._today())
    assert not note_writes.delete_refusal(Index.build(docs), docs, "REL-0001")
    note_writes.delete_release(Index.build(docs), docs, "REL-0001")
    assert not (docs / "releases" / "REL-0001-v1.1.0.md").exists()


# ---- step 3: settling -----------------------------------------------------

def test_settling_writes_a_ledger_event_and_no_note(tmp_path: Path) -> None:
    """[[REQ-0055]] is unchanged: a settle is an event, and it never touches a
    check note. Guarded rather than reviewed — a surviving frontmatter write
    does not raise, it puts a scalar back where the migration removed one."""
    docs = _repo(tmp_path)
    before = (docs / "tests" / "acceptance" / "TST-0001-C.md").read_text(
        encoding="utf-8")
    out = note_writes.settle_checks(
        docs, Index.build(docs), release_id="REL-0001", checks=["TST-0001"],
        mark="excused", reason="the trainer is in the loft", by="user:edwin")
    assert out["count"] == 1 and out["platform"] == "android"
    assert (docs / "tests" / "acceptance" / "TST-0001-C.md").read_text(
        encoding="utf-8") == before
    book = ledger.working(docs, "android")
    assert [(e.check, e.mark, e.reason, e.by) for e in book.entries] == [
        ("TST-0001", "excused", "the trainer is in the loft", "user:edwin")]


def test_the_platform_comes_from_the_release(tmp_path: Path) -> None:
    """The walker should not have to know ([[ISS-0290]]). Two ledgers and no
    platform on the client is the exact state that made a mark impossible."""
    docs = _repo(tmp_path, platform="ios")
    out = note_writes.settle_checks(
        docs, Index.build(docs), release_id="REL-0001", checks=["TST-0001"],
        mark="na", reason="no ERG on this bike", by="user:edwin", platform="")
    assert out["platform"] == "ios"
    assert ledger.working(docs, "ios").entries


def test_a_settle_uses_ITS_releases_platform_not_the_first_open_one(
        tmp_path: Path) -> None:
    """**Two open drafts is what it takes to see this.**

    `verdict_platform` answers *which platform is being walked* by reading the
    first open release — right for a walker on `~checks`, who is not standing
    on any particular release, and wrong for a settle, which names one. With
    the resolver consulted first, settling a check on the second draft wrote
    the event into the first draft's ledger.

    A single-draft fixture passes either way, which is why the ordering was
    wrong to begin with.
    """
    #: **The settled release must be the one `verdict_platform` would NOT
    #: pick**, or the test passes on the mutant. `open_releases` sorts by
    #: version `reverse=True`, so *the first open release* is the
    #: HIGHEST-versioned draft. An earlier cut of this test settled the higher
    #: one, so the resolver returned the right platform by coincidence and the
    #: defect survived its own guard. Found by independent review, 2026-09-08.
    #: The release being settled here is `1.1.0`; `2.0.0` is the one the
    #: resolver reaches for.
    docs = _repo(tmp_path, platform="ios")
    (docs / "releases" / "REL-0002-v2.0.0.md").write_text(
        '---\ntype: "[[release]]"\nid: REL-0002\ntitle: "N"\nstatus: draft\n'
        'version: "2.0.0"\nplatform: "android"\npreparing: ""\nfeatures: []\n'
        'created: 2026-09-08\nupdated: "2026-09-08"\n---\n\n# N\n',
        encoding="utf-8")
    from project_os_cockpit import publication as _pub
    assert [r["id"] for r in _pub.open_releases(Index.build(docs))][0] == "REL-0002", (
        "the fixture no longer puts the OTHER release first, so this test "
        "would pass whichever way the resolution is ordered")

    out = note_writes.settle_checks(
        docs, Index.build(docs), release_id="REL-0001", checks=["TST-0001"],
        mark="na", reason="no ERG on iOS", by="user:edwin")
    assert out["platform"] == "ios"
    assert not ledger.working(docs, "android").entries, (
        "the event landed in the other open release's ledger")


def test_every_settle_needs_a_reason(tmp_path: Path) -> None:
    """The difference between a settle and an undocumented exception."""
    docs = _repo(tmp_path)
    index = Index.build(docs)
    for mark in sorted(note_writes.SETTLE_MARKS):
        with pytest.raises(note_writes.WriteError) as exc:
            note_writes.settle_checks(
                docs, index, release_id="REL-0001", checks=["TST-0001"],
                mark=mark, reason="  ", by="user:edwin")
        assert exc.value.status == 400
        assert "reason" in exc.value.message


def test_a_bulk_settle_is_atomic_per_check_not_per_request(
        tmp_path: Path) -> None:
    """Twelve checks where the eighth is unknown records seven and reports the
    eighth. **A ledger is append-only**, so the events before a refusal stand;
    reporting the whole batch as a failure would be the dishonest option."""
    docs = _repo(tmp_path)
    out = note_writes.settle_checks(
        docs, Index.build(docs), release_id="REL-0001",
        checks=["TST-0001", "TST-9999"], mark="excused",
        reason="not this cycle", by="user:edwin")
    assert out["count"] == 1
    assert [r["id"] for r in out["refused"]] == ["TST-9999"]
    assert len(ledger.working(docs, "android").entries) == 1


def test_blocked_settles_and_still_blocks(tmp_path: Path) -> None:
    """[[ADR-0041]]: `blocked` is a deliberately useless-looking control.
    Recording *the rig was down* must never clear the gate — a gate that
    clears on whatever happens to be broken that day clears on anything."""
    docs = _repo(tmp_path)
    note_writes.settle_checks(
        docs, Index.build(docs), release_id="REL-0001", checks=["TST-0001"],
        mark="blocked", reason="the rig was down", by="user:edwin")
    payload = publication.release_payload(
        tmp_path, Index.build(docs), "REL-0001")
    owed = [r for group in payload["settle"] for r in group["rows"]]
    assert [r["id"] for r in owed] == ["TST-0001"]
    assert owed[0]["reason"] == "the rig was down", (
        "the row came back with no reason showing, so the button looks dead")


def test_settle_rows_group_by_area_and_flag_this_releases_own(
        tmp_path: Path) -> None:
    """Grouped because the wall was the problem.

    Measured on `../your-trainer` 2026-09-08 with REL-0017 open on Android:
    52 rows across 15 areas, 9 of them naming a feature the release carries.
    The fixture is two areas, because what this pins is the grouping and the
    flag rather than the corpus's numbers — those move under every commit.
    """
    docs = _repo(tmp_path)
    (docs / "tests" / "acceptance" / "TST-0002-D.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0002\ntitle: "Check two"\n'
        'level: acceptance\nstatus: active\narea: "Onboarding"\nmark: todo\n'
        'covers: []\n---\n\n# D\n', encoding="utf-8")
    index = Index.build(docs)
    note_writes.release_contents(
        index, "REL-0001", action="add", feature_id="FEAT-0001")
    payload = publication.release_payload(tmp_path, Index.build(docs), "REL-0001")
    areas = {g["area"]: g for g in payload["settle"]}
    assert set(areas) == {"Sync", "Onboarding"}
    assert areas["Sync"]["rows"][0]["covers_release"] is True
    assert areas["Onboarding"]["rows"][0]["covers_release"] is False
    #: The check's own words, which is what [[ADR-0041]] decision 4 rests on.
    assert "Open Settings" in areas["Sync"]["rows"][0]["text"]


# ---- step 4: the coverage sweep -------------------------------------------

def test_a_feature_no_check_names_is_a_gap(tmp_path: Path) -> None:
    docs = _repo(tmp_path, covered=False)
    index = Index.build(docs)
    gaps = publication.coverage_gaps(index, "REL-0001", {"FEAT-0001"})
    assert [r["id"] for r in gaps["uncovered"]] == ["FEAT-0001"]


def test_a_written_exception_is_an_answer_not_an_absence(
        tmp_path: Path) -> None:
    """Edwin's own correction: not all features need acceptance tests. A
    feature carrying `acceptance_exception:` has been answered for, and listing
    it would ask the question twice."""
    docs = _repo(tmp_path, covered=False, exception="no user-facing surface")
    gaps = publication.coverage_gaps(Index.build(docs), "REL-0001", {"FEAT-0001"})
    assert gaps["uncovered"] == []


def test_a_requirement_with_unticked_criteria_is_a_gap(tmp_path: Path) -> None:
    """From `criteria.payload`, which already owns *a criterion of record with
    no verification record* — not a second parse written here."""
    docs = _repo(tmp_path)
    (docs / "requirements").mkdir()
    (docs / "requirements" / "REQ-0001-R.md").write_text(
        '---\ntype: "[[requirement]]"\nid: REQ-0001\ntitle: "Rule"\n'
        'status: approved\nimplements: "[[FEAT-0001]]"\n---\n\n'
        '# Rule\n\n## Acceptance criteria\n\n- [ ] The banner says the date.\n'
        '- [x] The banner is dismissible.\n', encoding="utf-8")
    gaps = publication.coverage_gaps(Index.build(docs), "REL-0001", {"FEAT-0001"})
    assert [r["id"] for r in gaps["unmet"]] == ["REQ-0001"]
    assert gaps["unmet"][0]["open"] == 1
    assert gaps["unmet"][0]["sample"] == ["The banner says the date."]


def test_a_shipped_release_computes_no_coverage_gap(tmp_path: Path) -> None:
    """A released release is a record. Proposing checks for it is proposing
    work against something frozen ([[ADR-0035]])."""
    docs = _repo(tmp_path, status="released", covered=False)
    payload = publication.release_payload(tmp_path, Index.build(docs), "REL-0001")
    assert payload["coverage"]["scoped"] is False
    assert payload["settle"] == []


# ---- the verbs ------------------------------------------------------------

def test_a_release_has_agent_verbs_and_the_prefix_resolves() -> None:
    """`DEFAULT_ACTIONS` had no `release` key, and `NOTE_TYPE_BY_PREFIX` had no
    `REL` — so a release verb would not have resolved even once it existed."""
    from project_os_cockpit import agent_actions

    verbs = {v["key"] for v in agent_actions.DEFAULT_ACTIONS["release"]}
    assert "commission-checks" in verbs
    prompt = next(v["prompt"] for v in agent_actions.DEFAULT_ACTIONS["release"]
                  if v["key"] == "commission-checks")
    #: The split [[FEAT-0145]] step 4 rests on, asserted in the words the agent
    #: actually reads: the gap is computed, the drafting is proposed, and
    #: nothing enters the gate.
    assert "Do not recompute" in prompt
    assert "working tree" in prompt
    assert "do not seal" in prompt.lower()
    #: **No verdict field.** The plan said `mark: todo`; the validator refuses
    #: `mark` outright in a repo that keeps ledgers (LEDGER-FIELD, [[ADR-0037]]),
    #: and it refused the acceptance check written for this very feature. A
    #: prompt that tells an agent to write a field the validator rejects is a
    #: prompt that produces work somebody has to undo.
    assert "no `mark:`" in prompt and "LEDGER-FIELD" in prompt
    src = (Path(__file__).resolve().parents[1] / "desktop" / "src"
           / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    assert "REL: 'release'" in src


def test_every_new_write_path_is_routed_and_loopback_guarded() -> None:
    """[[ISS-0270]]: a complete, tested write path that nothing could call.
    `retire_check` was exactly that for two months."""
    src = (Path(__file__).resolve().parents[1] / "src" / "project_os_cockpit"
           / "server.py").read_text(encoding="utf-8")
    for route, handler in (
        ("/api/notes/release-update", "_serve_release_update"),
        ("/api/notes/release-abandon", "_serve_release_abandon"),
        ("/api/notes/release-delete", "_serve_release_delete"),
        ("/api/notes/release-settle", "_serve_release_settle"),
    ):
        assert f'path == "{route}"' in src, route
        start = src.index(f"def {handler}(self)")
        end = src.index("\n        def ", start + 1)
        assert "_require_loopback" in src[start:end], handler
