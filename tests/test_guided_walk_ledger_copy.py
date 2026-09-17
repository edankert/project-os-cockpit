"""Guided-walk outcomes against copies of the current platform ledgers."""

from __future__ import annotations

import shutil
import json
import os
import subprocess
import copy
from pathlib import Path

import pytest

from project_os_cockpit import acceptance, ledger
from project_os_cockpit.index import Index


YOUR_TRAINER = Path(__file__).resolve().parents[2] / "your-trainer"
COCKPIT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("platform", ["android", "ios"])
def test_walk_outcomes_preserve_ledger_history_on_a_copy(tmp_path: Path, platform: str) -> None:
    source = YOUR_TRAINER / "docs" / "releases" / "ledgers" / f"WORKING-{platform}.json"
    if not source.is_file():
        pytest.skip(f"Your Trainer ledger is absent: {source}")
    original = source.read_bytes()
    docs = tmp_path / "docs"
    target = docs / "releases" / "ledgers" / source.name
    target.parent.mkdir(parents=True)
    shutil.copyfile(source, target)

    cases = {
        "TST-9901": ("pass", "", False),
        "TST-9902": ("partial", "one observation was incomplete", False),
        "TST-9903": ("fail", "the expected result was absent", True),
        "TST-9904": ("question", "the expected result is ambiguous", True),
    }
    for check, (mark, reason, still_owed) in cases.items():
        assert check in ledger.owed(docs, platform, [check])
        ledger.append(docs, platform, check=check, mark=mark, reason=reason,
                      by="user:edwin", when="2026-09-16")
        assert (check in ledger.owed(docs, platform, [check])) is still_owed
        assert ledger.verdicts(docs, platform)[check].mark == mark

    # A deliberate correction is another event. It does not erase the failed
    # observation or leave the gate blocked after the new pass is recorded.
    ledger.append(docs, platform, check="TST-9903", mark="pass",
                  by="user:edwin", when="2026-09-16")
    assert "TST-9903" not in ledger.owed(docs, platform, ["TST-9903"])
    history = ledger.events_by_check(docs, platform)["TST-9903"]
    assert [event["mark"] for event in history[:2]] == ["pass", "fail"]
    assert source.read_bytes() == original


@pytest.mark.parametrize("platform", ["android", "ios"])
def test_renderer_step_requests_settle_copied_ledgers(
        tmp_path: Path, platform: str) -> None:
    """Replay requests from the built renderer, including a restart mid-check."""
    source = YOUR_TRAINER / "docs" / "releases" / "ledgers" / f"WORKING-{platform}.json"
    assert source.is_file(), f"platform ledger missing: {source}"
    original = source.read_bytes()
    emitted = tmp_path / "renderer-requests.json"
    env = {**os.environ, "WALK_LEDGER_SCENARIOS_OUT": str(emitted)}
    subprocess.run(
        ["node", "--test", "--test-name-pattern=ledger replay scenarios",
         "desktop/tests/walk-page.test.mjs"],
        cwd=COCKPIT, env=env, check=True, capture_output=True, text=True,
    )
    scenarios = json.loads(emitted.read_text(encoding="utf-8"))[platform]
    expected = {
        "pass": ("pass", False),
        "partial": ("partial", False),
        "fail": ("fail", True),
        "question": ("question", True),
        "correction": ("pass", False),
        "interrupted": ("pass", False),
    }
    assert set(scenarios) == set(expected)
    for name, (final_mark, still_owed) in expected.items():
        case = scenarios[name]
        docs = tmp_path / name / "docs"
        target = docs / "releases" / "ledgers" / source.name
        target.parent.mkdir(parents=True)
        shutil.copyfile(source, target)
        requests = case["requests"]
        assert case["before"] == 0, f"{name} wrote a verdict before its second step"
        assert len(requests) == (2 if name == "correction" else 1)
        check = requests[0]["id"]
        assert check not in ledger.events_by_check(docs, platform)
        assert check in ledger.owed(docs, platform, [check])
        for request in requests:
            assert request["platform"] == platform
            assert request["id"] == check
            assert request["method"] == "manual"
            ledger.append(
                docs, platform, check=check, mark=request["verdict"],
                reason=request["reason"], by=request["by"],
                method=request["method"], when="2026-09-17",
            )
        assert ledger.verdicts(docs, platform)[check].mark == final_mark
        assert (check in ledger.owed(docs, platform, [check])) is still_owed
        history = ledger.events_by_check(docs, platform)[check]
        assert len(history) == len(requests)
        if name == "correction":
            assert [event["mark"] for event in history] == ["pass", "fail"]
        assert source.read_bytes() == original


@pytest.mark.parametrize("platform", ["android", "ios"])
def test_real_free_ride_procedure_matches_direct_check_verdicts(
        tmp_path: Path, platform: str) -> None:
    """The current authored procedure and direct check controls emit identical verdicts."""
    docs_root = YOUR_TRAINER / "docs"
    source = docs_root / "releases" / "ledgers" / f"WORKING-{platform}.json"
    if not source.is_file():
        pytest.skip(f"Your Trainer ledger is absent: {source}")
    original = source.read_bytes()
    payload = acceptance.walk_payload(
        docs_root, Index.build(docs_root), platform=platform,
        release="REL-0017" if platform == "android" else "",
    )
    sitting = next(item for item in payload["sittings"]
                   if item["name"] == "FREE rides in each mode")
    selected = copy.deepcopy(sitting)
    if platform == "android":
        check_ids = ("TST-0034", "TST-0315")
        step_numbers = {1, 6, 13, 14}
    else:
        check_ids = ("TST-0034", "TST-0124", "TST-0370")
        step_numbers = {6, 7, 8}
    selected["rows"] = [row for row in selected["rows"]
                        if row["id"] in check_ids]
    selected["procedure"]["steps"] = [
        step for step in selected["procedure"]["steps"]
        if step["number"] in step_numbers
    ]
    selected["procedure"]["owed_checks"] = list(check_ids)
    assert tuple(row["id"] for row in selected["rows"]) == check_ids
    assert {step["number"] for step in selected["procedure"]["steps"]} == step_numbers
    payload["sittings"] = [selected]
    payload["counts"] = {"owed": len(check_ids), "placed": len(check_ids),
                         "unplaced": 0}
    payload["unplaced"] = []
    fixture = tmp_path / "procedure.json"
    fixture.write_text(json.dumps(payload), encoding="utf-8")
    emitted = tmp_path / "verdicts.json"
    env = {**os.environ, "WALK_REAL_PROCEDURE_IN": str(fixture),
           "WALK_REAL_PROCEDURE_OUT": str(emitted)}
    subprocess.run(
        ["node", "--test", "--test-name-pattern=real procedure verdicts",
         "desktop/tests/walk-page.test.mjs"],
        cwd=COCKPIT, env=env, check=True, capture_output=True, text=True,
    )
    verdicts = json.loads(emitted.read_text(encoding="utf-8"))
    assert verdicts["steps"] == verdicts["checks"]
    assert [item["id"] for item in verdicts["steps"]] == list(check_ids)
    for path in ("steps", "checks"):
        copied_docs = tmp_path / path / "docs"
        target = copied_docs / "releases" / "ledgers" / source.name
        target.parent.mkdir(parents=True)
        shutil.copyfile(source, target)
        for request in verdicts[path]:
            assert request["verdict"] == "pass"
            assert request["platform"] == platform
            assert request["id"] in ledger.owed(copied_docs, platform, check_ids)
            ledger.append(
                copied_docs, platform, check=request["id"],
                mark=request["verdict"], reason=request["reason"],
                by=request["by"], method=request["method"], when="2026-09-17",
            )
        assert ledger.owed(copied_docs, platform, check_ids) == []
        assert all(ledger.verdicts(copied_docs, platform)[check].mark == "pass"
                   for check in check_ids)
    assert source.read_bytes() == original
