"""A walker marks a check; the tool finds the ledger ([[ISS-0290]]).

Edwin, twice, mid-walk: *"My understanding of the functionality is that I
update the notes and you then update the ledger, I do not update the ledger
directly"*, and later *"Could not mark the test as passing because there was no
ledger for it."* Both are the same refusal — `record_verdict` requires a
platform and the client had none to send.

[[ISS-0272]] answered the unambiguous half (one ledger platform, send it) and
left the hard half open. `../your-trainer` is the hard half: an Android ledger,
an iOS ledger, and a picker that never reached this route.

**The open release is the declaration nobody was reading.** A repo preparing an
Android release is being walked on Android, and that is the same source
[[ISS-0289]] gave the read path.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from project_os_cockpit import ledger as L, note_writes
from project_os_cockpit.index import Index

CHECK = ('---\ntype: "[[test]]"\nid: TST-0001\ntitle: "C"\n'
         'level: acceptance\nstatus: active\narea: "A"\nmark: todo\n'
         'covers: ["[[FEAT-0001]]"]\n---\n\n# C\n')
FEATURE = ('---\ntype: "[[feature]]"\nid: FEAT-0001\ntitle: "T"\n'
           'status: done\n---\n\n# T\n')


def _docs(tmp: Path, *, release_platform: str | None = None,
          ledgers: tuple[str, ...] = ()) -> Path:
    docs = tmp / "docs"
    (docs / "tests" / "acceptance").mkdir(parents=True)
    (docs / "features").mkdir(parents=True)
    (docs / "releases" / "ledgers").mkdir(parents=True)
    (docs / "tests" / "acceptance" / "TST-0001-C.md").write_text(
        CHECK, encoding="utf-8")
    (docs / "features" / "FEAT-0001-T.md").write_text(FEATURE, encoding="utf-8")
    if release_platform is not None:
        (docs / "releases" / "REL-0001-R.md").write_text(
            '---\ntype: "[[release]]"\nid: REL-0001\ntitle: "R"\nstatus: draft\n'
            f'version: "1.1.0"\nplatform: "{release_platform}"\npreparing: true\n'
            'features: []\nupdated: "2026-09-08"\n---\n\n# R\n', encoding="utf-8")
    for platform in ledgers:
        (docs / "releases" / "ledgers" / f"WORKING-{platform}.json").write_text(
            json.dumps({"platform": platform, "entries": []}), encoding="utf-8")
    return docs


# ---- resolution order -----------------------------------------------------

def test_the_open_release_says_which_platform_is_being_walked(tmp_path: Path) -> None:
    """The regression, and your-trainer's exact shape: two ledgers, so
    [[ISS-0272]]'s single-platform shortcut cannot fire, and an open Android
    release that has said what is being walked."""
    docs = _docs(tmp_path, release_platform="android", ledgers=("android", "ios"))
    assert note_writes.verdict_platform(docs, Index.build(docs)) == "android"


def test_an_explicit_platform_is_never_overridden(tmp_path: Path) -> None:
    """A caller who named one walked on it. The release is a fallback, and a
    fallback that outranks an answer is a wrong verdict on the wrong ledger."""
    docs = _docs(tmp_path, release_platform="android", ledgers=("android", "ios"))
    assert note_writes.verdict_platform(docs, Index.build(docs), "ios") == "ios"


def test_one_ledger_platform_still_answers_on_its_own(tmp_path: Path) -> None:
    """[[ISS-0272]], unchanged: no release open, one ledger, nothing ambiguous."""
    docs = _docs(tmp_path, ledgers=("android",))
    assert note_writes.verdict_platform(docs, Index.build(docs)) == "android"


def test_two_ledgers_and_no_open_release_still_refuses(tmp_path: Path) -> None:
    """The question is real — which one did you walk on? — and guessing puts a
    verdict on the wrong platform, which is worse than being asked."""
    docs = _docs(tmp_path, ledgers=("android", "ios"))
    assert note_writes.verdict_platform(docs, Index.build(docs)) == ""


def test_a_release_with_no_platform_does_not_answer(tmp_path: Path) -> None:
    """An open release that never said what it ships has not declared anything,
    and must not be read as though it had."""
    docs = _docs(tmp_path, release_platform="", ledgers=("android", "ios"))
    assert note_writes.verdict_platform(docs, Index.build(docs)) == ""


# ---- what the walker is told when it genuinely cannot be answered ---------

def test_the_refusal_names_what_would_answer_it(tmp_path: Path) -> None:
    """It used to say *"use the ledger write path and send `platform`"* — advice
    for whoever is calling the API, met by somebody ticking a checklist."""
    docs = _docs(tmp_path, ledgers=("android", "ios"))
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.mark_check(Index.build(docs), check_id="TST-0001",
                               verdict="pass")
    assert exc.value.status == 409
    assert "android, ios" in exc.value.message
    assert "platform:" in exc.value.message


# ---- the release makes its own ledger -------------------------------------

def test_creating_a_release_creates_the_ledger_it_will_be_walked_against(
    tmp_path: Path,
) -> None:
    """Edwin: *"when creating a new release that the ledger is automatically
    created and can accept the new verdicts"*."""
    docs = _docs(tmp_path)
    result = note_writes.create_release(
        Index.build(docs), docs, title="v2.2.0", version="2.2.0",
        platform="android")
    assert result["platform"] == "android"
    assert (docs / "releases" / "ledgers" / "WORKING-android.json").exists()
    assert L.platforms(docs) == ["android"]
    note = (docs / "releases" / result["rel"].split("releases/")[-1]).read_text()
    assert 'platform: "android"' in note


def test_the_new_release_accepts_a_verdict_without_being_told_the_platform(
    tmp_path: Path,
) -> None:
    """The two halves together, which is the whole point: create the release,
    then mark a check the way a walker does — sending no platform at all."""
    docs = _docs(tmp_path)
    note_writes.create_release(Index.build(docs), docs, title="v2.2.0",
                               version="2.2.0", platform="android")
    index = Index.build(docs)
    platform = note_writes.verdict_platform(docs, index)
    note_writes.record_verdict(docs, index, check_id="TST-0001",
                               platform=platform, verdict="pass",
                               by="user:edwin")
    assert L.verdicts(docs, "android")["TST-0001"].mark == "pass"


def test_an_existing_ledger_is_never_overwritten(tmp_path: Path) -> None:
    """Idempotent, and it must be: an existing ledger is somebody's record."""
    docs = _docs(tmp_path, ledgers=("android",))
    L.append(docs, "android", check="TST-0001", mark="pass", by="user:edwin")
    note_writes.create_release(Index.build(docs), docs, title="v2.2.0",
                               version="2.2.0", platform="android")
    assert L.verdicts(docs, "android")["TST-0001"].mark == "pass"


def test_a_platform_that_would_escape_the_ledger_directory_is_refused(
    tmp_path: Path,
) -> None:
    """It becomes a filename, so it is guarded where it is accepted rather than
    where it is joined."""
    docs = _docs(tmp_path)
    for bad in ("../etc", "AND ROID", "an/droid"):
        with pytest.raises(note_writes.WriteError) as exc:
            note_writes.create_release(Index.build(docs), docs, title="v",
                                       version="2.2.0", platform=bad)
        assert exc.value.status == 400
