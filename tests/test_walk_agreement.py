"""The walk page and `walk-sheet.py` agree, on both platforms ([[TASK-0626]]).

Edwin's goal, 2026-09-14: *"The cockpit walk page and walk-sheet.py agree on
survey, sittings, steps and owed set for both platforms."* Four comparisons,
run against `your-trainer`'s live corpus when that repo is checked out beside
this one, and against a fixture always.

**Why this exists at all.** The page and the generated sheet are two readers of
one set of rules. `TESTING.md` rule 7 says bundling the module is what keeps
them from disagreeing, and bundling alone does not: `walk_payload` calls the
module's functions in its own order with its own arguments, and on
2026-09-14 an independent review found it passing only the OWED checks where
the generator passes every known one — so the two refused and accepted the
same procedure differently. That defect is fixed and this is the test that
would have caught it.

A fixture cannot catch a rule that only fires at 600 notes, which is why the
live half is here; the live half skips when the repo is absent, which is why
the fixture half is too.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from project_os_cockpit import acceptance, ledger
from project_os_cockpit.index import Index

YOUR_TRAINER = Path(__file__).resolve().parents[2] / "your-trainer"


# ------------------------------------------------------------ the comparison

def _sheet(repo_root: Path, platform: str, release: str = ""):
    """The walk `walk-sheet.py` would print, built the way that script builds it."""
    walk = acceptance._walk_module()
    return walk.generate(repo_root, release, platform)


def _page(repo_root: Path, platform: str, release: str = "") -> dict:
    docs = repo_root / "docs"
    return acceptance.walk_payload(docs, Index.build(docs),
                                   platform=platform, release=release)


def _compare(repo_root: Path, platform: str) -> None:
    """The four things the goal names, asserted one at a time.

    Separately rather than as one structural equality: the payload is a JSON
    shape and the sheet is a dataclass tree, so a single `==` is not available
    — and four assertions say which of the four disagreed, which is what a
    reader of the failure needs.
    """
    page = _page(repo_root, platform)
    sheet = _sheet(repo_root, platform)

    # 1. the survey — the screens the release changed, in order
    assert [s["surface"] for s in page["survey"]] == [s.title for s in sheet.survey]
    assert [s["surface_note"] or "" for s in page["survey"]] \
        == [s.id for s in sheet.survey]
    #: The captures too: a page showing a picture the sheet does not is a page
    #: showing a screen from a release nobody compared against.
    assert [[c["key"] for c in s["captures"]] for s in page["survey"]] \
        == [[c.key for c in s.captures] for s in sheet.survey]

    # 2. the sittings, in the consumer's authored order
    assert [s["name"] for s in page["sittings"]] \
        == [p.sitting.name for p in sheet.sittings]

    # 3. the printed steps of each sitting's procedure
    for mine, theirs in zip(page["sittings"], sheet.sittings):
        procedure = mine["procedure"]
        if theirs.procedure is None:
            assert procedure is None, mine["name"]
            continue
        assert procedure is not None, mine["name"]
        assert procedure["problems"] == theirs.procedure.problems, mine["name"]
        assert [s["number"] for s in procedure["steps"]] \
            == [s.number for s in theirs.steps], mine["name"]
        assert procedure["omitted"] == theirs.omitted, mine["name"]
        assert procedure["owed_checks"] == [c.id for c in theirs.owed_checks]

    # 4. the owed set
    mine_owed = sorted([r["id"] for s in page["sittings"] for r in s["rows"]]
                       + [r["id"] for r in page["unplaced"]])
    theirs_owed = sorted([c.id for p in sheet.sittings for c in p.rows]
                         + [c.id for c in sheet.unplaced])
    assert mine_owed == theirs_owed


# ------------------------------------------------------------ on a fixture

def _fixture(tmp_path: Path) -> Path:
    """A repo with two platforms, a screen with a child dialog, a change note
    naming both, a walk order and a procedure."""
    repo = tmp_path / "repo"
    docs = repo / "docs"
    for sub in ("surfaces", "tests/acceptance/walk", "releases/ledgers", "changes"):
        (docs / sub).mkdir(parents=True, exist_ok=True)
    (docs / "surfaces" / "SUR-0001.md").write_text(
        '---\ntype: "[[surface]]"\nid: SUR-0001\ntitle: "Ride cockpit"\n'
        'status: active\nkind: screen\n---\n\n# Ride cockpit\n', encoding="utf-8")
    (docs / "surfaces" / "SUR-0002.md").write_text(
        '---\ntype: "[[surface]]"\nid: SUR-0002\ntitle: "HR-zone sheet"\n'
        'status: active\nkind: screen\nparent: "SUR-0001"\n---\n\n# HR-zone sheet\n',
        encoding="utf-8")
    for tid, area in (("TST-0001", "Ride cockpit"), ("TST-0002", "HR-zone sheet")):
        (docs / "tests" / "acceptance" / f"{tid}.md").write_text(
            f'---\ntype: "[[test]]"\nid: {tid}\ntitle: "{tid}"\n'
            f'level: acceptance\nstatus: active\narea: "{area}"\nmark: todo\n'
            f"---\n\n# {tid}\n\n## Setup\nRiding.\n\n## Steps\n1. Look.\n\n"
            f"## Expect\n- It is there.\n", encoding="utf-8")
    (docs / "tests" / "acceptance" / "WALK.md").write_text(
        '---\ntype: "[[reference]]"\ntitle: "Walk order"\nstatus: active\n'
        'owner: user:fixture\n---\n\n# Walk order\n\n### Riding\n\n'
        '```yaml\nsurfaces: ["Ride cockpit", "HR-zone sheet"]\n'
        'state: "on a ride"\n```\n', encoding="utf-8")
    (docs / "tests" / "acceptance" / "walk" / "riding.md").write_text(
        '---\ntype: "[[reference]]"\ntitle: "Procedure — Riding"\n'
        'status: active\nowner: user:fixture\nsitting: "Riding"\n---\n\n'
        "# Procedure — Riding\n\n## Setup\n\nOn a ride, pedalling.\n\n"
        "## Steps\n\n1. **Ride cockpit.** Look at it.\n"
        "   - It is there. `TST-0001.1`\n"
        "2. **HR-zone sheet.** Open it.\n   - It is there. `TST-0002.1`\n"
        "3. **Ride cockpit.** Listen to it.\n   - It is quiet. `TST-0003.1`\n",
        encoding="utf-8")
    #: **A check the procedure cites and the release does NOT owe.** A
    #: procedure covers its whole sitting and the sheet prints the owed part
    #: of it, so its tags legitimately name checks that have already passed.
    #: `walk_payload` passed only the OWED checks to the module until
    #: 2026-09-14, which made every such tag read as naming no check at all —
    #: and the page refused a procedure the generator accepted. Without a
    #: passed check here this file could not see that regression; reverting
    #: the fix left all four of its tests green (independent review,
    #: 2026-09-14).
    (docs / "tests" / "acceptance" / "TST-0003.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0003\ntitle: "TST-0003"\n'
        'level: acceptance\nstatus: active\narea: "Ride cockpit"\nmark: todo\n'
        "---\n\n# TST-0003\n\n## Setup\nRiding.\n\n## Steps\n1. Listen.\n\n"
        "## Expect\n- It is quiet.\n", encoding="utf-8")
    passed = [{"check": "TST-0003", "date": "2026-09-01", "mark": "pass",
               "by": "user:edwin", "method": "manual"}]
    for platform in ("android", "ios"):
        (docs / "releases" / "ledgers" / f"WORKING-{platform}.json").write_text(
            json.dumps({"platform": platform, "entries": passed}),
            encoding="utf-8")
    return repo


def test_the_page_and_the_sheet_agree_on_a_two_platform_fixture(
        tmp_path: Path) -> None:
    """Both platforms, because the two are separate ledgers over one corpus and
    a walk built from the wrong one reports every check as owed."""
    repo = _fixture(tmp_path)
    for platform in ("android", "ios"):
        _compare(repo, platform)


def test_the_fixture_actually_exercises_a_procedure(tmp_path: Path) -> None:
    """A guard on the guard. `_compare` passes trivially where neither side
    has a procedure, a survey or an owed row, so the fixture is asserted to
    hold all three — otherwise the test above could go green on nothing."""
    repo = _fixture(tmp_path)
    page = _page(repo, "android")
    procedure = page["sittings"][0]["procedure"]
    assert procedure is not None and not procedure["problems"], procedure
    #: Step 3 cites a check that has already passed, so it is NOT printed —
    #: which is the filtering rule, and the reason the procedure is accepted
    #: rather than refused for citing a check outside the owed set.
    assert [s["number"] for s in procedure["steps"]] == [1, 2]
    assert procedure["omitted"] == 1
    assert page["counts"]["owed"] == 2
    assert not page["errors"], page["errors"]


def test_a_procedure_citing_an_already_passed_check_is_not_refused(
        tmp_path: Path) -> None:
    """The regression this file's docstring claims, now actually guarded.

    `walk_payload` reads every check a procedure cites, not only the owed
    ones. Passing the owed set alone made a tag naming a passed check read as
    naming no check at all, so this page refused a procedure `walk-sheet.py`
    accepted — the disagreement `TESTING.md` rule 7 says bundling the module
    prevents. Reverting that fix left all four of this file's other tests
    green until the fixture gained a passed check.
    """
    repo = _fixture(tmp_path)
    for platform in ("android", "ios"):
        procedure = _page(repo, platform)["sittings"][0]["procedure"]
        assert procedure["problems"] == [], (platform, procedure["problems"])
        #: And the module, run the way the script runs it, says the same.
        theirs = _sheet(repo, platform).sittings[0]
        assert theirs.procedure.problems == [], platform


# ------------------------------------------------------------ on the corpus

@pytest.mark.skipif(not (YOUR_TRAINER / "docs").is_dir(),
                    reason="your-trainer is not checked out beside this repo")
def test_the_page_and_the_sheet_agree_on_your_trainer() -> None:
    """Every platform `your-trainer` keeps a ledger for.

    Read from the ledger directory rather than named here: the repo shipped
    Android first and added iOS later, and a test naming both would have
    failed on the day the second ledger did not exist yet.
    """
    known = ledger.platforms(YOUR_TRAINER / "docs")
    assert known, "your-trainer keeps no ledger; the walk cannot be compared"
    for platform in known:
        _compare(YOUR_TRAINER, platform)


@pytest.mark.skipif(not (YOUR_TRAINER / "docs").is_dir(),
                    reason="your-trainer is not checked out beside this repo")
def test_the_live_payload_reports_no_errors_on_either_platform() -> None:
    """[[FEAT-0149]]'s review finding 5, closed for this path.

    `errors` is where the payload reports a check the ledger says is owed and
    the module resolved as settled. It is empty on every corpus measured, and
    a walker is entitled to be told when it is not — so an empty list is
    asserted rather than assumed.
    """
    for platform in ledger.platforms(YOUR_TRAINER / "docs"):
        page = _page(YOUR_TRAINER, platform)
        assert page["errors"] == [], (platform, page["errors"])
