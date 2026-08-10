"""TASK-0371 — the Tests view.

Tests had no view. The 23 ``TST-*`` notes were reachable through a register on
the review desk, a per-scope verification panel and a stat tile — three
surfaces answering three different questions, none of them *what do we
verify*. This asserts the view that answers it.

Two properties get the most attention here, because both are places the record
has already been caught disagreeing with itself:

* **One group per test.** A test in two groups is one item as two rows on one
  screen, which is the failure ISS-0068 names and which the Issues triage tray
  produced on its first draft.
* **One staleness rule.** The project's threshold is
  ``DEFAULT_STALENESS_DAYS`` overridden by ``SNAPSHOT.yaml
  verification.staleness_days`` — the validator's number and the validator's
  config key. A second rule is the defect ISS-0024 and ISS-0069 are both
  about, and there *was* a second one: ``MANUAL_TEST_STALE_DAYS = 60`` in the
  desktop renderer, on a different field, gated to manual tests.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from project_os_cockpit import cockpit, obligations
from project_os_cockpit.cockpit import nav_payload
from project_os_cockpit.index import Index

REPO_ROOT = Path(__file__).resolve().parent.parent
REPO_DOCS = REPO_ROOT / "docs"
RENDERER = REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts"


@pytest.fixture(scope="module")
def repo_index() -> Index:
    return Index.build(REPO_DOCS)


def _items(groups: list) -> list[dict]:
    out: list[dict] = []
    for group in groups:
        out.extend(group.get("items") or [])
    return out


# ---- the register --------------------------------------------------------


def test_the_view_holds_the_whole_test_corpus(repo_index: Index) -> None:
    """Set equality against the corpus, not non-emptiness.

    ISS-0062's type-based plan lookup returned 14 entirely convincing rows out
    of 33 and every shape assertion in the suite passed on it. A view that
    lists *some* tests looks exactly like one that lists all of them.
    """
    groups = nav_payload(repo_index, mode="tests")["groups"]
    listed = {item["id"] for item in _items(groups)}
    corpus = {r.note_id for r in repo_index.notes_by_type("test")}
    assert listed == corpus, {
        "missing from the view": sorted(corpus - listed),
        "in the view but not the corpus": sorted(listed - corpus),
    }


def test_every_test_appears_in_exactly_one_group(repo_index: Index) -> None:
    """ISS-0068's rule, inside one surface: one home, never two rows."""
    groups = nav_payload(repo_index, mode="tests")["groups"]
    ids = [item["id"] for item in _items(groups)]
    duplicated = sorted({i for i in ids if ids.count(i) > 1})
    assert not duplicated, f"listed in more than one group: {duplicated}"


def test_both_storage_locations_reach_the_view(repo_index: Index) -> None:
    """LIFECYCLE.md's hybrid rule splits tests between
    ``docs/features/<slug>/plan/tests/`` and ``docs/tests/``. That is a filing
    decision; a reader looking for "the tests" should not have to know it.

    Guarded against the vacuous pass: the corpus must actually hold both, or
    this asserts nothing.
    """
    corpus = list(repo_index.notes_by_type("test"))
    scoped = {r.note_id for r in corpus if r.rel_path.startswith("features/")}
    system = {r.note_id for r in corpus if r.rel_path.startswith("tests/")}
    assert scoped and system, "the corpus no longer exercises both locations"

    listed = {item["id"] for item in _items(nav_payload(repo_index, mode="tests")["groups"])}
    assert scoped <= listed and system <= listed


def test_a_row_says_which_feature_it_verifies(repo_index: Index) -> None:
    """The reader's mental model is the feature, not the directory."""
    rows = {i["id"]: i for i in _items(nav_payload(repo_index, mode="tests")["groups"])}
    # Declared, multi-feature, and path-resolved — one of each, so a resolver
    # that handled only its own repo's convention would fail here.
    assert rows["TST-0011"]["features"] == [
        "FEAT-0019", "FEAT-0020", "FEAT-0021", "FEAT-0022",
    ]
    assert rows["TST-0016"]["features"] == ["FEAT-0018"]
    # docs/tests/ — system-wide, and correctly owned by nothing.
    assert rows["TST-0001"]["features"] == []
    assert "system-wide" in rows["TST-0001"]["subtitle"]


# ---- the obligation ------------------------------------------------------


def test_the_needs_a_run_group_is_the_registrys_count(repo_index: Index) -> None:
    """The group and the badge must be the same number.

    They are computed by different code paths — ``_tests_groups`` builds the
    pane, ``obligations.counts`` builds the badge — and the whole point of the
    registry is that the predicate lives in one place. Two numbers on one
    screen disagreeing is the failure mode this asserts against.
    """
    groups = nav_payload(repo_index, mode="tests")["groups"]
    owed = [g for g in groups if g["key"] == "needs-run"]
    badge = obligations.counts(repo_index)["tests"]
    assert sum(len(g["items"]) for g in owed) == badge
    if owed:
        assert owed[0]["needs_human"] is True
        assert owed[0] is groups[0], "what is owed goes first"


def test_an_empty_group_is_absent_rather_than_zero(repo_index: Index) -> None:
    """A permanent `Failing · 0` is the shape of thing a reader learns to stop
    seeing, and this pane has been taught that lesson twice."""
    groups = nav_payload(repo_index, mode="tests")["groups"]
    assert all(g["items"] for g in groups)
    # Vacuity guard: this corpus must be missing at least one of the five, or
    # the assertion above never exercises absence.
    assert {g["key"] for g in groups} < {
        "needs-run", "failing", "stale", "never", "verified",
    }


# ---- one staleness rule --------------------------------------------------


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _corpus(root: Path, staleness: str | None, last_verified: str) -> Index:
    snapshot = "project: demo\n"
    if staleness is not None:
        snapshot += f"verification:\n  staleness_days: {staleness}\n"
    _write(root / "SNAPSHOT.yaml", snapshot)
    _write(root / "docs" / "tests" / "TST-0001-Old.md", (
        "---\n"
        'type: "[[test]]"\n'
        "id: TST-0001\n"
        'title: "An old pass"\n'
        "status: passing\n"
        f'last_verified: "{last_verified}"\n'
        "---\n\n# TST-0001\n"
    ))
    return Index.build(root / "docs")


def test_staleness_reads_the_projects_config_key(tmp_path: Path) -> None:
    """Not merely the project's *number* — its config source.

    A view that hard-coded 90 would pass an assertion about the default and
    still be a second rule the moment a repo set the key. So the same note is
    graded against three settings of ``verification.staleness_days``, and the
    group it lands in has to move.
    """
    day = "2026-01-01"   # comfortably old under any threshold used here

    stale = _corpus(tmp_path / "tight", "30", day)
    keys = {g["key"] for g in nav_payload(stale, mode="tests")["groups"]}
    assert keys == {"stale"}

    # A threshold longer than the note's age must move it out of `stale` —
    # asserted with a value nothing else in the project uses, so a hard-coded
    # 90 (or a hard-coded 60) fails here.
    fresh = _corpus(tmp_path / "loose", "99999", day)
    keys = {g["key"] for g in nav_payload(fresh, mode="tests")["groups"]}
    assert keys == {"verified"}


def test_the_default_threshold_is_the_validators(tmp_path: Path) -> None:
    """With no key set, the fallback is `DEFAULT_STALENESS_DAYS` — the
    validator's number, not a second default invented for this view."""
    assert cockpit.DEFAULT_STALENESS_DAYS == 90
    index = _corpus(tmp_path / "unset", None, "2026-01-01")
    assert cockpit._staleness_days(index.docs_root) == cockpit.DEFAULT_STALENESS_DAYS


def test_the_renderers_second_staleness_rule_is_gone() -> None:
    """``MANUAL_TEST_STALE_DAYS = 60`` graded the verification panel at 60 days
    on ``last_run``, and only for manual tests, while the validator and the
    overview's `unproven` marker used 90 on ``last_verified`` for everything.

    Measured 2026-08-10 on this corpus: the project's rule calls 2 tests stale
    (TST-0001/TST-0002, 94 days); the renderer's called 0, because both are
    automated. A panel reading "all fresh" beside a validator saying otherwise
    is exactly ISS-0024/ISS-0069.
    """
    src = RENDERER.read_text(encoding="utf-8")
    assert not re.search(r"const MANUAL_TEST_STALE_DAYS\s*=", src), (
        "the renderer declared its own staleness threshold again"
    )
    body = re.search(
        r"function isStaleRun\(test: ScopeTest\): boolean \{(.*?)\n\}", src, re.S,
    ).group(1)
    assert "test.stale" in body and "daysSince" not in body, body


def test_the_scope_panel_is_graded_by_the_same_rule(repo_index: Index) -> None:
    """The panel and the view must not disagree about one test.

    They are different payloads (`scope_tests_payload` against `_tests_groups`)
    and that is precisely how two rules survived side by side for a month.
    """
    view = {i["id"]: i["stale"] for i in _items(nav_payload(repo_index, mode="tests")["groups"])}
    panel = cockpit.scope_tests_payload(repo_index, "FEAT-0018")["tests"]
    assert panel, "FEAT-0018 no longer has linked tests — pick another scope"
    for row in panel:
        assert row["stale"] == view[row["id"]], row["id"]


# ---- who runs it ---------------------------------------------------------


def test_a_recorded_command_means_the_machine_runs_it(repo_index: Index) -> None:
    """`_is_unproven` already read `command` and said *"executable: the runner
    stamps it, not a human"*. `_is_manual_test` did not, so TST-0022 —
    ``command: .venv/bin/pytest tests/test_surface_ownership.py -q`` — was
    offered a manual stepper and counted among the tests a scope asks a person
    to walk. One question, one rule (TASK-0371).
    """
    by_id = {r.note_id: r for r in repo_index.notes_by_type("test")}
    tst22 = by_id["TST-0022"]
    assert str(tst22.frontmatter.get("command") or "").strip()
    assert cockpit._is_manual_test(tst22) is False
    # Still true of a genuinely manual test, which carries steps and no command.
    tst11 = by_id["TST-0011"]
    assert not str(tst11.frontmatter.get("command") or "").strip()
    assert cockpit._is_manual_test(tst11) is True


# ---- the shell draws it --------------------------------------------------


def test_the_shell_has_a_tests_button_and_it_is_wired() -> None:
    """A server mode with no button is a view nobody can reach, and a button
    whose mode is absent from `NAV_MODES` is a click that does nothing."""
    html = (REPO_ROOT / "desktop" / "src" / "renderer" / "index.html").read_text(encoding="utf-8")
    buttons = re.findall(r'top-bar-btn[^>]*data-mode="(\w+)"', html)
    assert "tests" in buttons
    assert buttons.index("issues") < buttons.index("tests") < buttons.index("review")

    src = RENDERER.read_text(encoding="utf-8")
    modes = re.search(r"const NAV_MODES = \[(.*?)\]", src, re.S).group(1)
    assert "'tests'" in modes
    assert "tests" in cockpit.NAV_MODES


def test_the_verified_group_is_not_rolled_up_behind_a_divider() -> None:
    """`groupNamesStateThemselves` decides whether settled groups sit in place
    or collapse under one "settled" line. Every test in this corpus is
    `passing`, so without this the Tests view's answer — all 23 verified —
    would be filed behind a divider that says nothing about tests.
    """
    src = RENDERER.read_text(encoding="utf-8")
    body = re.search(
        r"function groupNamesStateThemselves\(mode: NavMode\): boolean \{(.*?)\n\}",
        src, re.S,
    ).group(1)
    assert "'tests'" in body


def test_the_tests_badge_maps_to_the_tests_mode() -> None:
    """The registry names its view `tests`; the button's `data-mode` is
    `tests`. One mapping table, and it has to carry the pair."""
    src = RENDERER.read_text(encoding="utf-8")
    table = re.search(r"const MODE_FOR_VIEW: Record<string, string> = \{(.*?)\n  \};", src, re.S).group(1)
    assert re.search(r"tests:\s*'tests'", table)
    assert obligations.VIEW_TESTS in obligations.views_owed()
    assert "test" in obligations.views_owed()[obligations.VIEW_TESTS]
