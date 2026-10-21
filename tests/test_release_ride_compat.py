"""The cockpit reads what a release ride writes ([[TASK-0678]], [[ISS-0326]]).

your-trainer's release ride (its FEAT-0140) records results on a tablet, and
the template's `release-test.py --import-ride` turns them into ledger entries
with `method: "ride"` and a `build` (project-os a76657d). Four things the
cockpit has to do for that, one group of tests each:

1. read a ledger holding a ride entry, and refuse one with no build, as the
   template's validator does;
2. keep every field it does not know when it writes a result into a ledger;
3. count a check as owed on a platform exactly as `release-test.py` does: a
   `command:` covers every platform, `commands.<platform>` covers one, and
   `hand_steps:` keeps those steps owed where a command covers the check;
4. show the sheet's hand-run budget line beside the release's owed count.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from project_os_cockpit import acceptance, publication
from project_os_cockpit import ledger as _ledger
from project_os_cockpit.index import Index

YOUR_TRAINER = Path.home() / "Dev" / "repos" / "your-trainer"


def _rt():
    return acceptance._release_test_module()


def _check(docs: Path, n: str, area: str, extra: str = "", steps: int = 2) -> None:
    body = "\n".join(f"{i}. Do step {i}." for i in range(1, steps + 1))
    (docs / "tests" / "acceptance" / f"TST-{n}-C.md").write_text(
        f'---\ntype: "[[test]]"\nid: TST-{n}\ntitle: "C {n}"\n'
        f'level: acceptance\nstatus: active\narea: "{area}"\n{extra}'
        f"---\n\n# C\n\n## Setup\n\nA phone.\n\n## Steps\n\n{body}\n\n"
        f"## Expect\n\n- It works, {n}.\n", encoding="utf-8")


def _docs(tmp_path: Path, *, android: list[dict] | None = None,
          android_extra: dict | None = None) -> Path:
    """Four checks, one per way a check can be owed or not.

    TST-0001 has no command: owed everywhere. TST-0002 has a command on
    Android only. TST-0003 has a command on Android and keeps step 2 by hand.
    TST-0004 has a `command:`, which covers every platform.
    """
    docs = tmp_path / "docs"
    (docs / "tests" / "acceptance").mkdir(parents=True)
    (docs / "releases" / "ledgers").mkdir(parents=True)
    _check(docs, "0001", "Profile")
    _check(docs, "0002", "Profile", 'commands:\n  android: "pytest tests/a.py"\n')
    _check(docs, "0003", "Workouts",
           'commands:\n  android: "pytest tests/b.py"\nhand_steps: [2]\n')
    _check(docs, "0004", "Workouts", 'command: "pytest tests/c.py"\n')
    (docs / "tests" / "acceptance" / "RELEASE-TEST.md").write_text(
        '---\ntype: "[[reference]]"\ntitle: "Section order"\nstatus: active\n---\n\n'
        '# Section order\n\n### Profile\n\n```yaml\nsurfaces: ["Profile"]\n```\n\n'
        '### Workouts\n\n```yaml\nsurfaces: ["Workouts"]\n```\n', encoding="utf-8")
    (docs / "releases" / "REL-0001-R.md").write_text(
        '---\ntype: "[[release]]"\nid: REL-0001\ntitle: "R"\nstatus: draft\n'
        'version: "1.1.0"\nplatform: "android"\npreparing: true\n'
        'features: []\nupdated: "2026-10-21"\n---\n\n# R\n', encoding="utf-8")
    head = {"platform": "android", **(android_extra or {})}
    (docs / "releases" / "ledgers" / "WORKING-android.json").write_text(
        json.dumps({**head, "entries": android or [], "evidence": []}),
        encoding="utf-8")
    (docs / "releases" / "ledgers" / "WORKING-ios.json").write_text(
        json.dumps({"platform": "ios", "entries": []}), encoding="utf-8")
    return docs


RIDE = {"check": "TST-0001", "result": "pass", "date": "2026-10-21",
        "method": "ride", "by": "user:edwin", "build": "2.2.0 (123)"}


# ------------------------------------------------------------ 1. ride entries

def test_a_ledger_holding_a_ride_result_is_read(tmp_path: Path) -> None:
    """Refusing `ride` refused the whole file, so one imported ride took
    every acceptance check and the release test off the screen."""
    docs = _docs(tmp_path, android=[RIDE])
    found = _ledger.verdicts(docs, "android")
    assert found["TST-0001"].mark == "pass"
    assert found["TST-0001"].method == "ride"
    suite = acceptance.load(docs, Index.build(docs), platform="android")
    assert "TST-0001" not in {i.note_id for i in suite.blocking()}


def test_a_ride_result_with_no_build_is_refused(tmp_path: Path) -> None:
    """The validator requires a ride entry's build; the cockpit agrees, so a
    ledger one of them refuses is not read as sound by the other."""
    ride = {k: v for k, v in RIDE.items() if k != "build"}
    docs = _docs(tmp_path, android=[ride])
    with pytest.raises(_ledger.LedgerError, match="build"):
        _ledger.verdicts(docs, "android")


def test_the_cockpit_and_the_validator_accept_the_same_methods() -> None:
    from project_os_cockpit import validate_docs_bundled as vd
    assert _ledger.METHODS == frozenset(vd.LEDGER_METHODS)


def _import_ride(docs: Path, tmp_path: Path) -> None:
    """Run the template's own import, as `release-test.py --import-ride` does."""
    rt = _rt()
    ride = tmp_path / "ride"
    ride.mkdir()
    (ride / "shot.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    results = ride / "results.json"
    results.write_text(json.dumps({
        "format": rt.RIDE_RESULTS_FORMAT, "release": "REL-0001",
        "platform": "android", "by": "user:edwin",
        "build": {"versionName": "2.2.0", "versionCode": 123},
        "started": "2026-10-21T09:00:00Z", "finished": "2026-10-21T10:00:00Z",
        "steps": [
            {"id": "TST-0001.1", "result": "pass", "evidence": ["shot.png"]},
            {"id": "TST-0001.2", "result": "pass"},
            {"id": "TST-0003.2", "result": "fail", "note": "the chart froze"},
        ],
        "screens": [],
    }), encoding="utf-8")
    plan = rt.plan_ride_import(docs.parent, results, "android")
    assert [e["check"] for e in plan.entries] == ["TST-0001", "TST-0003"]
    rt.apply_ride_import(plan)


def test_a_ledger_the_template_imported_a_ride_into_is_read(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    _import_ride(docs, tmp_path)
    found = _ledger.verdicts(docs, "android")
    assert (found["TST-0001"].mark, found["TST-0001"].method) == ("pass", "ride")
    assert found["TST-0003"].mark == "fail"


# ------------------------------------------------- 2. fields it does not know

def test_a_write_keeps_every_field_it_does_not_know(tmp_path: Path) -> None:
    """Writing one result rewrote the file from what the cockpit knew, so a
    ride entry lost its `build` and a key added later lost itself."""
    ride = {**RIDE, "app": {"versionName": "2.2.0", "device": "tablet"}}
    gone = {"check": "TST-0002", "invalidated_by": "CHG-1", "date": "2026-10-21",
            "reason": "moved", "source": "ci"}
    shot = {"check": "TST-0001", "date": "2026-10-21",
            "ref": "docs/releases/ledgers/evidence/x/shot.png",
            "note": "TST-0001.1", "kind": "png"}
    docs = _docs(tmp_path, android=[ride, gone],
                 android_extra={"ride_format": "release-ride-results/1"})
    path = docs / "releases" / "ledgers" / "WORKING-android.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["evidence"] = [shot]
    path.write_text(json.dumps(raw), encoding="utf-8")

    _ledger.append(docs, "android", check="TST-0003", mark="pass",
                   by="user:edwin", when="2026-10-22")

    after = json.loads(path.read_text(encoding="utf-8"))
    assert after["ride_format"] == "release-ride-results/1"
    assert after["entries"][0] == ride
    assert after["entries"][1] == gone
    assert after["entries"][2]["check"] == "TST-0003"
    assert after["evidence"] == [shot]


def test_an_imported_ride_survives_a_cockpit_write(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    _import_ride(docs, tmp_path)
    path = docs / "releases" / "ledgers" / "WORKING-android.json"
    before = json.loads(path.read_text(encoding="utf-8"))
    _ledger.append(docs, "android", check="TST-0002", mark="pass",
                   by="user:edwin", when="2026-10-22")
    after = json.loads(path.read_text(encoding="utf-8"))
    assert after["entries"][:len(before["entries"])] == before["entries"]
    assert all(e["build"] == "2.2.0 (123)" for e in after["entries"]
               if e.get("method") == "ride")
    assert after["evidence"] == before["evidence"] and after["evidence"]


def test_a_copy_of_your_trainers_ledger_reads_back_as_it_was(tmp_path: Path) -> None:
    """Read and rewritten with nothing added, the real file keeps every
    byte. A copy, never the file: it carries an uncommitted change of Edwin's."""
    real = YOUR_TRAINER / "docs" / "releases" / "ledgers" / "WORKING-android.json"
    if not real.is_file():
        pytest.skip("your-trainer is not checked out beside this repo")
    docs = tmp_path / "docs"
    (docs / "releases" / "ledgers").mkdir(parents=True)
    copy = docs / "releases" / "ledgers" / "WORKING-android.json"
    shutil.copyfile(real, copy)
    _ledger.write(_ledger.working(docs, "android"))
    assert copy.read_bytes() == real.read_bytes()


# --------------------------------------------- 3. owed on which platform

def _owed_here(docs: Path, platform: str) -> set[str]:
    suite = acceptance.load(docs, Index.build(docs), platform=platform)
    return {i.note_id for i in suite.blocking()}


def _owed_upstream(docs: Path, platform: str) -> set[str]:
    rt = _rt()
    read = rt.read_repo(docs.parent, platform)
    return {c.id for c in rt.owed_checks(read.checks, read.events, platform)}


def test_a_command_for_one_platform_takes_the_check_off_that_platform_only(
    tmp_path: Path,
) -> None:
    docs = _docs(tmp_path)
    assert _owed_here(docs, "android") == {"TST-0001", "TST-0003"}
    assert _owed_here(docs, "ios") == {"TST-0001", "TST-0002", "TST-0003"}


def test_the_cockpit_owes_what_the_release_test_owes(tmp_path: Path) -> None:
    """The release page's count and the sheet are one answer a click apart."""
    docs = _docs(tmp_path, android=[RIDE])
    for platform in ("android", "ios"):
        assert _owed_here(docs, platform) == _owed_upstream(docs, platform), platform
        gate = acceptance.gate_payload(docs, index=Index.build(docs), platform=platform)
        unchecked = sum(int(c.get("unchecked") or 0) for c in gate["counts"].values())
        assert unchecked == len(_owed_upstream(docs, platform)), platform


def test_with_no_platform_only_command_counts(tmp_path: Path) -> None:
    """`release-test.py` says so: a reader asking about the note, not about
    one platform's sheet. TST-0003 keeps a hand step and stays owed."""
    docs = _docs(tmp_path)
    assert _owed_here(docs, "") == {"TST-0001", "TST-0002", "TST-0003"}


def test_unusable_hand_steps_keep_the_check_owed(tmp_path: Path) -> None:
    """A hand step naming a step the note does not have keeps the whole
    check on the sheet, the safe direction, in both readers."""
    docs = _docs(tmp_path)
    _check(docs, "0002", "Profile",
           'commands:\n  android: "pytest tests/a.py"\nhand_steps: [9]\n')
    assert "TST-0002" in _owed_here(docs, "android")
    assert _owed_here(docs, "android") == _owed_upstream(docs, "android")


def test_on_your_trainer_the_cockpit_owes_what_the_release_test_owes() -> None:
    docs = YOUR_TRAINER / "docs"
    if not (docs / "tests" / "acceptance" / "RELEASE-TEST.md").is_file():
        pytest.skip("your-trainer is not checked out beside this repo")
    index = Index.build(docs)
    for platform in _ledger.platforms(docs):
        here = {i.note_id for i in
                acceptance.load(docs, index, platform=platform).blocking()}
        assert here == _owed_upstream(docs, platform), platform


# ------------------------------------------------------- 4. the hand-run budget

def test_the_release_page_carries_the_sheets_budget_line(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    payload = publication.release_payload(docs.parent, Index.build(docs), "REL-0001")
    budget = payload["gate"]["budget"]
    assert budget["line"] == ("Hand-run budget: 2 checks with 3 steps are owed "
                              "by hand on Android. The limit is 10 checks.")
    assert (budget["checks"], budget["steps"], budget["limit"], budget["over"]) == (2, 3, 10, 0)


def test_a_release_naming_no_platform_has_no_budget(tmp_path: Path) -> None:
    """A sheet is one platform's; a union has no sheet to take the line from."""
    docs = _docs(tmp_path)
    rel = docs / "releases" / "REL-0001-R.md"
    rel.write_text(rel.read_text(encoding="utf-8").replace('platform: "android"\n', ""),
                   encoding="utf-8")
    payload = publication.release_payload(docs.parent, Index.build(docs), "REL-0001")
    assert not payload["gate"].get("budget")


def test_on_your_trainer_the_budget_is_the_sheets() -> None:
    docs = YOUR_TRAINER / "docs"
    if not (docs / "tests" / "acceptance" / "RELEASE-TEST.md").is_file():
        pytest.skip("your-trainer is not checked out beside this repo")
    index = Index.build(docs)
    opens = [r for r in publication.open_releases(index)
             if str(r.get("platform") or "").strip().lower() == "android"]
    if not opens:
        pytest.skip("your-trainer has no open Android release")
    release = str(opens[0]["id"])
    rt = _rt()
    sheet = rt.sheet_from(rt.read_repo(YOUR_TRAINER, "android"), release, "android")
    expected = rt.budget_line(sheet.budget, "android").replace("**", "")
    payload = publication.release_payload(YOUR_TRAINER, index, release)
    assert payload["gate"]["budget"]["line"] == expected
