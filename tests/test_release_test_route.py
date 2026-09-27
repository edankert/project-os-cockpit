"""`/api/cockpit/release-test` — one platform's release test ([[TASK-0640]]).

The page is upstream's generator's own data (`release_test_payload`), plus
which checks already have a result in the open ledger. What is asserted here
is what the cockpit adds or decides:

- the checks shown are what the open release owed, so a check stays on the
  page after its result is recorded, with that result beside it;
- an invalidation after a result reopens the check and drops the result;
- the set of test notes equals `ledger.owed` once the open ledger's results
  are set aside;
- the route refuses `all` and a platform no ledger carries;
- a platform with no open release of its own is tested against the newest.
"""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from project_os_cockpit import acceptance, cockpit
from project_os_cockpit import ledger as _ledger
from project_os_cockpit.index import Index
from project_os_cockpit.server import (
    DocsServer,
    _NoDNSThreadingHTTPServer,
    _make_handler,
)


def _docs(tmp_path: Path, *, release_platform: str | None = "android",
          entries: list[dict] | None = None) -> Path:
    docs = tmp_path / "docs"
    (docs / "tests" / "acceptance" / "release-test").mkdir(parents=True)
    (docs / "releases" / "ledgers").mkdir(parents=True)
    for n, area in (("0001", "Profile"), ("0002", "Profile"), ("0003", "Workouts")):
        (docs / "tests" / "acceptance" / f"TST-{n}-C.md").write_text(
            f'---\ntype: "[[test]]"\nid: TST-{n}\ntitle: "C {n}"\n'
            f'level: acceptance\nstatus: active\narea: "{area}"\n'
            "---\n\n# C\n\n## Setup\n\nA phone.\n\n## Steps\n\n1. Open it.\n\n"
            f"## Expect\n\n- It opens, {n}.\n", encoding="utf-8")
    (docs / "tests" / "acceptance" / "RELEASE-TEST.md").write_text(
        '---\ntype: "[[reference]]"\ntitle: "Section order"\nstatus: active\n---\n\n'
        '# Section order\n\n### Profile\n\n```yaml\nsurfaces: ["Profile"]\n'
        'bench: ["A phone", "A strap"]\n```\n\n'
        '### Workouts\n\n```yaml\nsurfaces: ["Workouts"]\n```\n', encoding="utf-8")
    (docs / "tests" / "acceptance" / "release-test" / "profile.md").write_text(
        '---\ntype: "[[reference]]"\nsection: "Profile"\n---\n\n'
        '# Profile\n\n## Setup\n\nOpen the app.\n\n## Steps\n\n'
        '### Opening\n\nStart: the app open.\n\n'
        '1. Open Profile.\n   - `TST-0001.1`\n'
        '2. Open it again.\n   - `TST-0002.1`\n', encoding="utf-8")
    if release_platform is not None:
        (docs / "releases" / "REL-0001-R.md").write_text(
            '---\ntype: "[[release]]"\nid: REL-0001\ntitle: "R"\nstatus: draft\n'
            f'version: "1.1.0"\nplatform: "{release_platform}"\npreparing: true\n'
            'features: []\nupdated: "2026-09-13"\n---\n\n# R\n', encoding="utf-8")
    (docs / "releases" / "ledgers" / "WORKING-android.json").write_text(
        json.dumps({"platform": "android", "entries": entries if entries is not None else [
            {"check": "TST-0001", "date": "2026-09-13", "result": "pass",
             "by": "user:edwin", "method": "manual"},
        ]}), encoding="utf-8")
    (docs / "releases" / "ledgers" / "WORKING-ios.json").write_text(
        json.dumps({"platform": "ios", "entries": []}), encoding="utf-8")
    return docs


def _spin_up(docs: Path):
    server = DocsServer(docs_root=docs, bind="127.0.0.1", port=0)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0),
        _make_handler(server.docs_root, server.index, server.bus,
                      cockpit_state=server.cockpit_state),
    )
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd.server_address[1], httpd


def _get(port: int, query: str = "") -> tuple[int, Any]:
    url = f"http://127.0.0.1:{port}/api/cockpit/release-test{query}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


def _tests(page: dict) -> list[str]:
    return sorted(t for section in page["sections"] for t in section["tests"])


def test_a_check_stays_on_the_page_after_its_result_is_recorded(tmp_path: Path) -> None:
    page = acceptance.release_test_payload(_docs(tmp_path) , platform="android",
                                           release="REL-0001")
    assert page["error"] == ""
    #: TST-0001 passed in the open ledger, and is still shown, with its result.
    assert _tests(page) == ["TST-0001", "TST-0002", "TST-0003"]
    assert page["results"] == {"TST-0001": {"result": "pass", "reason": "",
                                            "date": "2026-09-13"}}
    profile = page["sections"][0]
    assert profile["slug"] == "profile"
    assert profile["progress"] == {"done": 1, "total": 2}
    assert page["progress"] == {"done": 1, "total": 3}
    #: Test notes beside printed checks, as the acceptance page counts them.
    assert page["notes"] == {"total": 3, "owed": 2}


def test_the_page_is_the_generators_own_data(tmp_path: Path) -> None:
    page = acceptance.release_test_payload(_docs(tmp_path), platform="android",
                                           release="REL-0001")
    profile = page["sections"][0]
    assert [g["title"] for g in profile["groups"]] == ["Opening"]
    assert profile["groups"][0]["start"] == "the app open."
    first = profile["groups"][0]["checks"][0]
    assert (first["number"], first["action"], first["tags"]) == (1, "Open Profile.", ["TST-0001.1"])
    assert first["expected"][0]["text"] == "It opens, 0001."
    assert profile["setup"]["bench"] == ["A phone", "A strap"]
    assert profile["bench_line"] == "A phone · A strap"


def test_an_invalidation_after_a_result_reopens_the_check(tmp_path: Path) -> None:
    docs = _docs(tmp_path, entries=[
        {"check": "TST-0001", "date": "2026-09-13", "result": "pass",
         "by": "user:edwin", "method": "manual"},
        {"check": "TST-0001", "date": "2026-09-14", "invalidated_by": "TASK-0001",
         "reason": "the profile moved"},
    ])
    page = acceptance.release_test_payload(docs, platform="android", release="REL-0001")
    assert "TST-0001" in _tests(page)
    assert page["results"] == {}


def test_the_tests_shown_are_what_the_ledger_owed_before_this_release(tmp_path: Path) -> None:
    """Setting the open ledger's results aside must give exactly the set
    `ledger.owed` reports for a ledger holding none of them."""
    docs = _docs(tmp_path, entries=[])
    page = acceptance.release_test_payload(docs, platform="android", release="REL-0001")
    owed = _ledger.owed(docs, "android", ["TST-0001", "TST-0002", "TST-0003"])
    assert _tests(page) == sorted(owed)


def test_a_sealed_pass_is_not_shown(tmp_path: Path) -> None:
    docs = _docs(tmp_path, entries=[])
    (docs / "releases" / "ledgers" / "REL-0000-android.json").write_text(json.dumps({
        "platform": "android", "release": "REL-0000", "sealed": "2026-09-01",
        "entries": [{"check": "TST-0003", "date": "2026-09-01", "mark": "pass",
                     "by": "user:edwin", "method": "manual"}]}), encoding="utf-8")
    page = acceptance.release_test_payload(docs, platform="android", release="REL-0001")
    assert "TST-0003" not in _tests(page)


def test_the_route_serves_a_platform_and_names_its_release(tmp_path: Path) -> None:
    port, httpd = _spin_up(_docs(tmp_path))
    try:
        status, page = _get(port, "?platform=android")
        assert status == 200
        assert (page["platform"], page["release"], page["version"]) == ("android", "REL-0001", "1.1.0")
        assert page["platforms"] == ["android", "ios"]
    finally:
        httpd.shutdown()


def test_a_platform_with_no_release_of_its_own_uses_the_newest(tmp_path: Path) -> None:
    port, httpd = _spin_up(_docs(tmp_path))
    try:
        status, page = _get(port, "?platform=ios")
        assert status == 200
        assert page["release"] == "REL-0001"
        assert _tests(page) == ["TST-0001", "TST-0002", "TST-0003"]
    finally:
        httpd.shutdown()


def test_all_and_an_unknown_platform_are_refused(tmp_path: Path) -> None:
    port, httpd = _spin_up(_docs(tmp_path))
    try:
        status, body = _get(port, "?platform=all")
        assert status == 400 and "one platform" in body["error"]
        status, body = _get(port, "?platform=andriod")
        assert status == 400 and "no ledger for platform" in body["error"]
    finally:
        httpd.shutdown()


def test_the_tests_pane_lists_each_platform_and_its_sections(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    group = cockpit._release_test_group(Index.build(docs))
    assert group is not None
    assert group["label"] == "Release test · v1.1.0"
    rows = {item["title"].split(" · ")[0]: item for item in group["items"]}
    assert set(rows) == {"Android", "iOS"}
    assert rows["Android"]["title"] == "Android · 1/3 checks"
    #: Its sections show without a click (Edwin, 2026-09-27).
    assert rows["Android"]["open"] is True
    assert rows["Android"]["url"] == "~release-test/android"
    assert [s["url"] for s in rows["Android"]["items"]] == [
        "~release-test/android/profile", "~release-test/android/workouts"]


def test_no_section_order_means_no_release_test_group(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    (docs / "tests" / "acceptance" / "RELEASE-TEST.md").unlink()
    assert cockpit._release_test_group(Index.build(docs)) is None


def test_the_ledger_reads_both_keys_and_writes_result(tmp_path: Path) -> None:
    """New entries use `result`; an entry written before 2026-09-27 uses
    `mark`, and both are read for good (project-os-dev ADR-0050)."""
    docs = _docs(tmp_path, entries=[
        {"check": "TST-0002", "date": "2026-09-10", "mark": "fail",
         "reason": "old key", "by": "user:edwin", "method": "manual"},
    ])
    [working] = [l for l in _ledger.load(docs, "android") if l.is_working]
    assert working.entries[0].mark == "fail"
    _ledger.append(docs, "android", check="TST-0003", mark="pass",
                   by="user:edwin", method="manual")
    raw = json.loads((docs / "releases" / "ledgers" / "WORKING-android.json").read_text())
    assert [("result" in e, "mark" in e) for e in raw["entries"]] == [(True, False), (True, False)]


YOUR_TRAINER = Path.home() / "Dev" / "repos" / "your-trainer" / "docs"


def test_on_your_trainer_the_page_is_what_is_owed_plus_what_this_release_recorded() -> None:
    """Measured on the real corpus, both platforms ([[TASK-0640]]).

    The page shows what the open release owed, so its test notes are the ones
    `ledger.owed` still reports, plus exactly those the open ledger has a
    result for. Nothing else gets in and nothing owed is missing.
    """
    import pytest
    if not (YOUR_TRAINER / "tests" / "acceptance" / "RELEASE-TEST.md").is_file():
        pytest.skip("your-trainer is not checked out beside this repo")
    from project_os_cockpit.index import Index
    index = Index.build(YOUR_TRAINER)
    manual = [i.note_id for i in acceptance.load(YOUR_TRAINER, index, platform="android").items
              if i.note_id and acceptance.kind_of(i) in acceptance.MANUAL_KINDS]
    for platform in _ledger.platforms(YOUR_TRAINER):
        page = acceptance.release_test_payload(YOUR_TRAINER, platform=platform)
        assert page["error"] == ""
        shown = set(_tests(page))
        owed = set(_ledger.owed(YOUR_TRAINER, platform, manual))
        assert owed <= shown, sorted(owed - shown)[:10]
        #: "Test notes still owed" is the acceptance page's manual count.
        assert page["notes"]["owed"] == len(owed), platform
        assert shown - owed == {t for t in page["results"]
                                if page["results"][t]["result"] in {"pass", "partial", "na", "excused"}}, platform
