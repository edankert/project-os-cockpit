"""The survey — the surfaces this release changed ([[TASK-0620]]).

The checks say what must be true. None of them says *open the screens this
release touched and look*, which is the first thing Edwin does by habit and the
one thing the suite never asks for. The information was already recorded: an
invalidation is an event `{check, invalidated_by, date}` in the ledger, and
every check names its surface in `area:`. The survey is that join.

**The predicate is "the latest event is an invalidation."** A check invalidated
and then walked to `pass` is not owed and its surface has been looked at; a
check invalidated after its last `pass` is owed *because of that change*, and
the change is what the walker should open first.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from project_os_cockpit import acceptance, ledger
from project_os_cockpit.index import Index


def _check(docs: Path, tid: str, *, area: str) -> None:
    (docs / "tests" / "acceptance").mkdir(parents=True, exist_ok=True)
    (docs / "tests" / "acceptance" / f"{tid}.md").write_text(
        f'---\ntype: "[[test]]"\nid: {tid}\ntitle: "{tid}"\n'
        f'level: acceptance\nstatus: active\narea: "{area}"\nmark: todo\n'
        f"---\n\n# {tid}\n", encoding="utf-8")


def _ledger(docs: Path, entries: list[dict], platform: str = "android") -> None:
    path = docs / "releases" / "ledgers" / f"WORKING-{platform}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"platform": platform, "entries": entries}),
                    encoding="utf-8")


def _task(docs: Path, tid: str, title: str, body: str = "") -> None:
    (docs / "features" / "f" / "plan" / "tasks").mkdir(parents=True, exist_ok=True)
    (docs / "features" / "f" / "plan" / "tasks" / f"{tid}.md").write_text(
        f'---\ntype: "[[task]]"\nid: {tid}\ntitle: "{title}"\nstatus: done\n'
        f'parent: "[[FEAT-0001]]"\n---\n\n# {title}\n\n{body}\n', encoding="utf-8")


def _change(docs: Path, stem: str, cid: str, title: str, body: str = "") -> None:
    (docs / "changes").mkdir(parents=True, exist_ok=True)
    (docs / "changes" / f"{stem}.md").write_text(
        f'---\ntype: "[[change]]"\nid: {cid}\ntitle: "{title}"\n---\n\n'
        f"# {title}\n\n{body}\n", encoding="utf-8")


def _survey(docs: Path, platform: str = "android") -> list[dict]:
    return acceptance.walk_payload(docs, Index.build(docs),
                                   platform=platform)["survey"]


def _invalidation(check: str, by: str, date: str = "2026-09-10") -> dict:
    return {"check": check, "date": date, "invalidated_by": by,
            "reason": "a change touched this", "by": "user:edwin",
            "method": "manual"}


# ------------------------------------------------------- the predicate

def test_a_surface_appears_when_the_latest_event_is_an_invalidation(
        tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _task(docs, "TASK-0001", "Rewrote the profile screen")
    _ledger(docs, [
        {"check": "TST-0001", "date": "2026-09-01", "mark": "pass",
         "by": "user:edwin", "method": "manual"},
        _invalidation("TST-0001", "TASK-0001"),
    ])
    survey = _survey(docs)
    assert [e["surface"] for e in survey] == ["Profile"]
    assert survey[0]["checks"] == ["TST-0001"]
    assert [c["id"] for c in survey[0]["changes"]] == ["TASK-0001"]
    assert survey[0]["changes"][0]["title"] == "Rewrote the profile screen"


def test_an_invalidation_a_later_pass_overtook_is_not_in_the_survey(
        tmp_path: Path) -> None:
    """The check is not owed, so its surface has been looked at. Listing it
    would send the walker to a screen somebody already walked."""
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _task(docs, "TASK-0001", "Rewrote the profile screen")
    _ledger(docs, [
        _invalidation("TST-0001", "TASK-0001", date="2026-09-01"),
        {"check": "TST-0001", "date": "2026-09-02", "mark": "pass",
         "by": "user:edwin", "method": "manual"},
    ])
    assert _survey(docs) == []


def test_an_owed_check_with_no_invalidation_names_no_surface(
        tmp_path: Path) -> None:
    """Owed because nobody has ever walked it is not *a change reopened it*.
    The survey answers the second question only."""
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _ledger(docs, [])
    payload = acceptance.walk_payload(docs, Index.build(docs), platform="android")
    assert payload["survey"] == []
    assert payload["counts"]["owed"] == 1


def test_a_failed_check_after_an_invalidation_leaves_the_survey(
        tmp_path: Path) -> None:
    """Somebody has looked at the screen — they walked it and it failed. It is
    still owed, and it is no longer news about a changed surface."""
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _task(docs, "TASK-0001", "Rewrote the profile screen")
    _ledger(docs, [
        _invalidation("TST-0001", "TASK-0001", date="2026-09-01"),
        {"check": "TST-0001", "date": "2026-09-02", "mark": "fail",
         "reason": "still broken", "by": "user:edwin", "method": "manual"},
    ])
    payload = acceptance.walk_payload(docs, Index.build(docs), platform="android")
    assert payload["survey"] == []
    assert payload["counts"]["owed"] == 1


# ------------------------------------------------------------- the causes

def test_every_distinct_cause_is_named(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _check(docs, "TST-0002", area="Profile")
    _task(docs, "TASK-0001", "One")
    _task(docs, "TASK-0002", "Two")
    _ledger(docs, [
        _invalidation("TST-0001", "TASK-0001, TASK-0002"),
        _invalidation("TST-0002", "TASK-0002"),
    ])
    survey = _survey(docs)
    assert len(survey) == 1
    assert survey[0]["checks"] == ["TST-0001", "TST-0002"]
    assert [c["id"] for c in survey[0]["changes"]] == ["TASK-0001", "TASK-0002"]


def test_an_id_the_index_cannot_resolve_is_kept_with_no_title(
        tmp_path: Path) -> None:
    """Dropped, it would be an invalidation the walker cannot trace. Kept with
    `title: None`, the page can say *this names something that is not here*."""
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _ledger(docs, [_invalidation("TST-0001", "TASK-9999")])
    survey = _survey(docs)
    assert [(c["id"], c["title"]) for c in survey[0]["changes"]] == [
        ("TASK-9999", None)]


def test_a_change_note_resolves_by_its_full_slug(tmp_path: Path) -> None:
    """`CHG` is not in the validator's id prefixes, so the note index holds no
    change note at all. The walk module keeps a second index for them; without
    it a survey naming a change printed an id and quoted nothing."""
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _change(docs, "CHG-20260913-The-Profile-Moves", "CHG-20260913",
            "The profile moves",
            "## Acceptance checks reopened\n\nThe profile screen was rebuilt.\n")
    _ledger(docs, [_invalidation("TST-0001", "CHG-20260913-The-Profile-Moves")])
    change = _survey(docs)[0]["changes"][0]
    assert change["id"] == "CHG-20260913-The-Profile-Moves"
    assert change["title"] == "The profile moves"
    assert change["reopened"] == "The profile screen was rebuilt."


def test_the_reopened_section_is_quoted_and_nothing_else_is(
        tmp_path: Path) -> None:
    """Where the invalidating note carries the section, it is the sentence the
    walker needs. Nothing else in the note is read — a survey that quoted a
    whole task note would be unreadable at thirty rows."""
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _task(docs, "TASK-0001", "Rewrote it", body=(
        "## Why\n\nA long justification nobody needs here.\n\n"
        "## Acceptance checks reopened\n\nThe sign-in button moved.\n\n"
        "## Notes\n\nMore prose.\n"))
    _ledger(docs, [_invalidation("TST-0001", "TASK-0001")])
    change = _survey(docs)[0]["changes"][0]
    assert change["reopened"] == "The sign-in button moved."
    assert "justification" not in (change["reopened"] or "")


def test_a_note_without_the_section_reopens_nothing_and_still_appears(
        tmp_path: Path) -> None:
    """The section is a convention 33 `your-trainer` notes already follow and
    the template does not require. The survey works without it."""
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _task(docs, "TASK-0001", "Rewrote it", body="## Why\n\nBecause.\n")
    _ledger(docs, [_invalidation("TST-0001", "TASK-0001")])
    change = _survey(docs)[0]["changes"][0]
    assert change["title"] == "Rewrote it"
    assert change["reopened"] is None


# -------------------------------------------------------------- the surface

def test_the_surface_note_is_named_when_the_repo_keeps_one(
        tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    (docs / "surfaces").mkdir(parents=True)
    (docs / "surfaces" / "SUR-0001-Profile.md").write_text(
        '---\ntype: "[[surface]]"\nid: SUR-0001\ntitle: "Profile"\n'
        "status: active\n---\n\n# Profile\n", encoding="utf-8")
    _task(docs, "TASK-0001", "Rewrote it")
    _ledger(docs, [_invalidation("TST-0001", "TASK-0001")])
    assert _survey(docs)[0]["surface_note"] == "SUR-0001"


def test_a_repo_with_no_surface_notes_groups_by_the_area_string(
        tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _task(docs, "TASK-0001", "Rewrote it")
    _ledger(docs, [_invalidation("TST-0001", "TASK-0001")])
    entry = _survey(docs)[0]
    assert entry["surface"] == "Profile"
    assert entry["surface_note"] is None


def test_a_check_with_no_area_is_still_surveyed(tmp_path: Path) -> None:
    """It says the area is missing rather than dropping the row. A check
    reopened by a change and invisible on the survey is the one failure the
    survey exists to prevent."""
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="")
    _task(docs, "TASK-0001", "Rewrote it")
    _ledger(docs, [_invalidation("TST-0001", "TASK-0001")])
    entry = _survey(docs)[0]
    assert entry["checks"] == ["TST-0001"]
    assert "no area" in entry["surface"]


def test_the_survey_is_per_platform(tmp_path: Path) -> None:
    """An Android change reopens the check on both platforms — the payoff
    [[ADR-0037]] names — but each ledger records its own events, so the survey
    reports the platform it was asked about."""
    docs = tmp_path / "docs"
    _check(docs, "TST-0001", area="Profile")
    _task(docs, "TASK-0001", "Rewrote it")
    _ledger(docs, [_invalidation("TST-0001", "TASK-0001")], platform="android")
    _ledger(docs, [], platform="ios")
    assert [e["surface"] for e in _survey(docs, "android")] == ["Profile"]
    assert _survey(docs, "ios") == []


# ------------------------------------------------------------- the live corpus

YOUR_TRAINER = Path(__file__).resolve().parents[2] / "your-trainer" / "docs"


@pytest.mark.skipif(not YOUR_TRAINER.is_dir(),
                    reason="your-trainer is not checked out beside this repo")
def test_the_live_survey_equals_the_ledgers_own_invalidations() -> None:
    """The exit criterion, computed against `ledger.events_by_check` directly.

    Both sides are built here rather than compared to a recorded number: the
    corpus moves, and a test pinned to *six surfaces* would fail on the next
    invalidation for no reason anybody could act on.
    """
    index = Index.build(YOUR_TRAINER)
    platform = (ledger.platforms(YOUR_TRAINER) or ["android"])[0]
    payload = acceptance.walk_payload(YOUR_TRAINER, index, platform=platform)

    events = ledger.events_by_check(YOUR_TRAINER, platform)
    owed_rows = {r["id"]: r for s in payload["sittings"] for r in s["rows"]}
    owed_rows.update({r["id"]: r for r in payload["unplaced"]})

    expected: dict[str, set[str]] = {}
    for check, row in owed_rows.items():
        log = events.get(check) or []
        if not log or not log[0].get("invalidated_by"):
            continue
        surface = row["area"] or "(no area on the check)"
        expected.setdefault(surface, set()).add(check)

    got = {e["surface"]: set(e["checks"]) for e in payload["survey"]}
    assert got == expected

    #: …and every cause named by those events is on the survey.
    for entry in payload["survey"]:
        named = set()
        for check in entry["checks"]:
            raw = (events[check][0].get("invalidated_by") or "")
            named.update(tok.strip().strip("[]") for tok in
                         raw.replace(";", ",").replace(" ", ",").split(",")
                         if tok.strip())
        assert {c["id"] for c in entry["changes"]} == named
