"""The release gate is graded on the release's platform ([[ISS-0288]]).

`release_payload` asked the platform question twice and answered it two ways:
`shipping_in` filtered the contents by `_platform_of_release` ([[ISS-0261]])
while the gate call passed no platform at all and fell to the union rule — a
check clears only where *every* platform with a ledger cleared it.

The union is correct for a release that has not said what it ships
([[DES-0012]] D4) and stays. What it must not do is override a release that
HAS said, which is the state `../your-trainer` was in on 2026-09-08: an open
Android release, an Android ledger resolving 569 checks, an iOS ledger holding
one entry, and a gate reporting **635 of 636 owed**.

Two ledgers is what it takes to see this, which is why it survived: eleven of
twelve fleet repos have at most one, and the union over one ledger is that
ledger.
"""

from __future__ import annotations

import json
from pathlib import Path

from project_os_cockpit import publication
from project_os_cockpit.index import Index


def _repo(tmp: Path, *, release_platform: str) -> Path:
    """One done feature, two checks covering it, and both walked on Android.

    iOS has a ledger and has walked neither — the shape of a repo that ships
    two platforms on separate cadences.
    """
    docs = tmp / "docs"
    (docs / "releases" / "ledgers").mkdir(parents=True)
    (docs / "features" / "f").mkdir(parents=True)
    (docs / "tests" / "acceptance").mkdir(parents=True)

    (docs / "features" / "f" / "FEAT-0001-T.md").write_text(
        '---\ntype: "[[feature]]"\nid: FEAT-0001\ntitle: "Thing"\n'
        'status: done\n---\n\n# T\n', encoding="utf-8")
    for n in ("0001", "0002"):
        (docs / "tests" / "acceptance" / f"TST-{n}-C.md").write_text(
            f'---\ntype: "[[test]]"\nid: TST-{n}\ntitle: "C {n}"\n'
            'level: acceptance\nstatus: active\narea: "A"\nmark: todo\n'
            'covers: ["[[FEAT-0001]]"]\n---\n\n# C\n', encoding="utf-8")

    (docs / "releases" / "REL-0001-R.md").write_text(
        '---\ntype: "[[release]]"\nid: REL-0001\ntitle: "R"\nstatus: draft\n'
        f'version: "1.1.0"\nplatform: "{release_platform}"\npreparing: true\n'
        'features: []\nupdated: "2026-09-08"\n---\n\n# R\n', encoding="utf-8")

    (docs / "releases" / "ledgers" / "WORKING-android.json").write_text(
        json.dumps({"platform": "android", "entries": [
            {"check": "TST-0001", "date": "2026-09-08", "mark": "pass",
             "by": "user:edwin", "method": "manual"},
            {"check": "TST-0002", "date": "2026-09-08", "mark": "pass",
             "by": "user:edwin", "method": "manual"},
        ]}), encoding="utf-8")
    (docs / "releases" / "ledgers" / "WORKING-ios.json").write_text(
        json.dumps({"platform": "ios", "entries": []}), encoding="utf-8")
    return docs


def _blocking(docs: Path, tmp: Path) -> list[str]:
    payload = publication.release_payload(tmp, Index.build(docs), "next")
    return [row["id"] for row in payload["gate"]["blocking"]]


def test_an_android_release_is_graded_on_the_android_ledger(tmp_path: Path) -> None:
    """The regression. Both checks passed on Android, the release ships
    Android, so the gate is clear — and before the fix both came back owed
    because iOS had not walked them."""
    docs = _repo(tmp_path, release_platform="android")
    assert _blocking(docs, tmp_path) == []


def test_a_release_that_names_no_platform_still_takes_them_all(tmp_path: Path) -> None:
    """[[DES-0012]] D4, unchanged. Saying nothing is not saying Android: the
    union fails closed, and that is the property the fix must not spend."""
    docs = _repo(tmp_path, release_platform="")
    assert sorted(_blocking(docs, tmp_path)) == ["TST-0001", "TST-0002"]


def test_an_ios_release_is_graded_on_the_ios_ledger(tmp_path: Path) -> None:
    """The other direction, which the Android case alone cannot tell from a
    gate that simply ignores the ledger: iOS has walked neither check, so an
    iOS release owes both."""
    docs = _repo(tmp_path, release_platform="ios")
    assert sorted(_blocking(docs, tmp_path)) == ["TST-0001", "TST-0002"]
