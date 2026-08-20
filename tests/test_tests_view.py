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

import copy

import datetime as _dt
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
    """Rows from the TEST-NOTE groups only.

    The view carries two populations (TASK-0373): the executable/manual test
    notes, and the acceptance suite's tiers. Everything in this section is about
    the first, so the tier groups are excluded here rather than by each
    assertion — a filter written once is one that cannot be forgotten in the
    next test.

    Since ADR-0031 both populations are the `test` type and `level:` separates
    them, so the corpus side of these comparisons filters on level rather than
    getting the separation free from the type.

    **The filter is the row's id, not the group's key** (ADR-0039). It used to
    skip any group keyed `tier*`, which worked while the two populations were
    two sets of groups. They are now merged -- both derive to the same three
    sections, and emitting two groups labelled `Feature tests` would be
    ISS-0068's one-item-two-homes defect wearing a different hat -- so a
    non-acceptance test row lives INSIDE a section group, beside the area
    surfaces. An area surface is keyed by the area's name; a test is keyed by
    its `TST-*` id, which is the difference this reads.
    """
    out: list[dict] = []
    for group in groups:
        for item in group.get("items") or []:
            if str(item.get("id") or "").upper().startswith("TST-"):
                out.append(item)
    return out


# ---- the register --------------------------------------------------------


#: `owed_corpus` moved to `tests/conftest.py` on 2026-08-13 (TASK-0416):
#: a second module needed it, and copying it would have been the very
#: mistake that task removes from the production code — two derivations of
#: one thing, agreeing by coincidence until they stop.


def test_the_view_holds_the_whole_test_corpus(repo_index: Index) -> None:
    """Set equality against the corpus, not non-emptiness.

    ISS-0062's type-based plan lookup returned 14 entirely convincing rows out
    of 33 and every shape assertion in the suite passed on it. A view that
    lists *some* tests looks exactly like one that lists all of them.
    """
    groups = nav_payload(repo_index, mode="tests")["groups"]
    listed = {item["id"] for item in _items(groups)}
    corpus = {r.note_id for r in repo_index.notes_by_type("test")
              if str(r.frontmatter.get("level", "") or "").strip().lower() != "acceptance"}
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
    corpus = [r for r in repo_index.notes_by_type("test")
              if str(r.frontmatter.get("level", "") or "").strip().lower() != "acceptance"]
    scoped = {r.note_id for r in corpus if r.rel_path.startswith("features/")}
    system = {r.note_id for r in corpus if r.rel_path.startswith("tests/")}
    assert scoped and system, "the corpus no longer exercises both locations"

    listed = {item["id"] for item in _items(nav_payload(repo_index, mode="tests")["groups"])}
    assert scoped <= listed and system <= listed


def test_a_row_says_which_feature_it_verifies(repo_index: Index) -> None:
    """The reader's mental model is the feature, not the directory.

    ADR-0032: the answer comes from the test's ``covers:`` and from nothing
    else. The path case this used to assert is gone with the fallback — three
    tests fleet-wide resolved that way and all three now declare their subject,
    which is the whole point of removing an encoding that only applied when
    another was missing.
    """
    rows = {i["id"]: i for i in _items(nav_payload(repo_index, mode="tests")["groups"])}
    # TST-0011 covers NINE features, not four. Five of them (FEAT-0023..0027)
    # were named by the features' own `tests:` lists and not by the test, and
    # its checklist items cite them by number in the body -- so the reverse
    # encoding was the more complete of the two, which is the finding that
    # made the drift worth measuring rather than assuming.
    assert rows["TST-0011"]["features"] == [
        "FEAT-0019", "FEAT-0020", "FEAT-0021", "FEAT-0022",
        "FEAT-0023", "FEAT-0024", "FEAT-0025", "FEAT-0026", "FEAT-0027",
    ]
    assert rows["TST-0016"]["features"] == ["FEAT-0018"]
    # A test that was resolved BY PATH before ADR-0032 and now declares it.
    assert rows["TST-0019"]["features"] == ["FEAT-0006"]
    # docs/tests/ — system-wide, and correctly owned by nothing.
    assert rows["TST-0001"]["features"] == []
    assert "system-wide" in rows["TST-0001"]["subtitle"]


def test_a_tests_subjects_never_come_from_its_directory(repo_index: Index) -> None:
    """ADR-0032: where a test lives is a filing decision, not a claim.

    Guarded on a test that HAS the path shape a resolver would fall back on —
    ``features/<slug>/plan/tests/`` — with its ``covers:`` removed. A resolver
    still reading the directory answers with the owning feature; one reading
    only the declared edge answers with nothing.
    """
    from project_os_cockpit.cockpit import _test_feature_ids

    record = next(
        r for r in repo_index.notes_by_type("test")
        if r.rel_path.startswith("features/") and r.note_id == "TST-0019"
    )
    stripped = copy.copy(record)
    stripped.frontmatter = {
        k: v for k, v in record.frontmatter.items()
        if k not in ("covers", "features", "verifies", "validates", "parent", "implements")
    }
    assert _test_feature_ids(repo_index, stripped) == []


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
    # Vacuity guard: this corpus must be missing at least one section, or the
    # assertion above never exercises absence.
    note_keys = {g["key"] for g in groups}
    # **Six sections, and a strict subset** (ADR-0039). `Broken command` is
    # the sharpest case: it is empty across all 139 automated notes in the
    # fleet, so it must be ABSENT rather than a permanent `Broken command · 0`.
    assert note_keys < {
        "needs-you",
        # The acceptance side keys a section `tier1`/`tier2`/`tier3` because
        # that is the address the front ends use. Nothing reads a `tier:`.
        "tier1", "tier2", "tier3",
        "feature", "regression", "automated",
        "broken-command", "retired",
    }


# ---- one staleness rule --------------------------------------------------


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _corpus(root: Path, staleness: str | None, last_verified: str,
            *, command: str = "pytest -q") -> Index:
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
        # **A `command:`, because time-based staleness is now an EXECUTABLE
        # test's rule** (ADR-0034 decision 2). A command-less test re-arms by
        # `invalidated_by:` instead, which is what the next test asserts.
        + (f'command: "{command}"\nlast_run: "{last_verified}"\n' if command else "")
        + f'last_verified: "{last_verified}"\n'
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

    # **Read off the ROW, not the group** (ADR-0039). `Stale` and `Verified`
    # were sections while a section was a verdict state; they are neither now,
    # and staleness is a property of a row inside whatever section the check
    # belongs to. The claim this guard exists for is untouched: the threshold
    # comes from the project's config key and a note's grading moves with it.
    def _stale_flags(index):
        return {i["id"]: i["stale"]
                for i in _items(nav_payload(index, mode="tests")["groups"])}

    stale = _corpus(tmp_path / "tight", "30", day)
    assert set(_stale_flags(stale).values()) == {True}

    # A threshold longer than the note's age must stop grading it stale —
    # asserted with a value nothing else in the project uses, so a hard-coded
    # 90 (or a hard-coded 60) fails here.
    fresh = _corpus(tmp_path / "loose", "99999", day)
    assert set(_stale_flags(fresh).values()) == {False}


def test_a_human_walked_test_does_not_go_stale_by_time(tmp_path: Path) -> None:
    """ADR-0034 decision 2: re-arming is a property of execution, not of age.

    A machine re-runs on every commit, so *"is this result old"* is a fair
    question. A person does not, so the question is *"has anything CHANGED
    under this walk"* — which `invalidated_by:` answers and no threshold can.

    The proxy was wrong in both directions: a walk untouched for a year is
    current if nothing it covers has moved, and one performed yesterday is
    stale if something has. Same note, same date, same threshold as the `stale`
    case above — only the `command:` differs.
    """
    walked = _corpus(tmp_path / "walked", "30", "2026-01-01", command="")
    flags = {i["id"]: i["stale"]
             for i in _items(nav_payload(walked, mode="tests")["groups"])}
    assert flags and not any(flags.values()), (
        "a command-less test must not be graded by age")


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
    # Compared over what BOTH surfaces list, which is the property: two rules
    # must not disagree about one test. Since ADR-0031 the panel legitimately
    # holds more — an acceptance test covering FEAT-0018 verifies it, so the
    # per-scope panel says so, while the navigator renders that population under
    # its tier instead. Different membership by design; identical grading where
    # they overlap.
    shared = [row for row in panel if row["id"] in view]
    assert shared, "the panel and the view no longer share a test — the comparison is vacuous"
    for row in shared:
        assert row["stale"] == view[row["id"]], row["id"]


# ---- who runs it ---------------------------------------------------------


def test_a_recorded_command_means_the_machine_runs_it(repo_index: Index) -> None:
    """`_is_unproven` already read `command` and said *"executable: the runner
    stamps it, not a human"*. `_is_manual_test` did not, so TST-0022 —
    ``command: .venv/bin/pytest tests/test_surface_ownership.py -q`` — was
    offered a manual stepper and counted among the tests a scope asks a person
    todo. One question, one rule (TASK-0371).
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
    # `review` lost its button in TASK-0378, so the anchor is Library — the
    # structural modes still come before the reading one.
    assert buttons.index("issues") < buttons.index("tests") < buttons.index("library")
    assert "review" not in buttons

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


# ---- TASK-0372: the runner moves ----------------------------------------
#
# The move is routing and placement. What gets WRITTEN must be identical, and
# these assert that against a real HTTP server rather than by reading the
# source — the guard the desk's own suite learned to want (ISS-0055).


def _min_workspace(root: Path, body: str) -> Path:
    docs = root / "docs"
    (root / "SNAPSHOT.yaml").write_text("project: demo\n", encoding="utf-8")
    _write(docs / "tests" / "TST-0001-Demo.md", body)
    return docs


TEST_NOTE = """---
type: "[[test]]"
id: TST-0001
title: "A demo test"
status: ready
kind: manual
owner: user:edwin
last_verified: "2026-08-01"
---

# TST-0001

## Steps

1. Open the pane. Expect: it opens
2. Press the button. Expect: something happens

## Runs

### 2026-08-01 — passing (by user:edwin)
- **pass** · An earlier run, so the append has a section to land in

## Later section

Text under a heading that follows the Runs section — the placement bug an
independent review found in 2026-07-26, re-asserted after the move.
"""


def _serve(docs: Path):
    """The real handler on an ephemeral port, as the desk suite does it."""
    import threading

    from project_os_cockpit.server import (
        DocsServer, _make_handler, _NoDNSThreadingHTTPServer,
    )

    server = DocsServer(docs_root=docs, bind="127.0.0.1", port=0)
    index = Index.build(docs)
    handler = _make_handler(docs, index, server.bus)
    httpd = _NoDNSThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def _post(port: int, path: str, payload: dict) -> dict:
    import json
    import urllib.request

    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=json.dumps(payload).encode(), method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode())


@pytest.fixture()
def runner_workspace(tmp_path: Path):
    docs = _min_workspace(tmp_path, TEST_NOTE)
    httpd, port = _serve(docs)
    try:
        yield docs, port
    finally:
        httpd.shutdown()


def test_a_run_writes_what_it_always_wrote(runner_workspace) -> None:
    """The round-trip assertion, re-run after the move: the note is
    byte-identical outside its allow-listed fields and the appended log."""
    docs, port = runner_workspace
    note = docs / "tests" / "TST-0001-Demo.md"
    before = note.read_text(encoding="utf-8")

    out = _post(port, "/api/notes/test-run", {
        "id": "TST-0001", "outcome": "passing", "aborted": False,
        "runner": "user:edwin", "mtime": note.stat().st_mtime,
        "steps": [{"n": 1, "text": "Open the pane", "result": "pass",
                   "evidence": "it opened"}],
    })
    assert out["ok"] is True
    after = note.read_text(encoding="utf-8")

    today = _dt.date.today().isoformat()
    assert 'status: "passing"' in after
    assert today in after           # last_run and last_verified both stamped
    assert after.count(today) >= 3  # last_run, last_verified, updated
    # Everything the run does not own is untouched, line for line.
    def carried(text: str) -> list[str]:
        head = text.split("---", 2)[1].splitlines()
        return [ln for ln in head
                if not ln.split(":")[0].strip() in
                {"status", "last_run", "last_verified", "updated"}]
    assert carried(after) == carried(before)
    # The new entry lands at the END of `## Runs` and before the section that
    # follows it — not simply at the end of the body, which is the defect an
    # independent review found on 2026-07-26.
    runs = after[after.index("## Runs"):after.index("## Later section")]
    assert "An earlier run" in runs and "it opened" in runs
    assert runs.index("An earlier run") < runs.index("it opened")


def test_a_failing_run_returns_the_draft_it_always_promised(runner_workspace) -> None:
    """`draft_issue_body` existed from TASK-0209 and had no caller outside its
    unit test, while TST-0021 recorded that a failing step "produces an issue
    draft" and the run summary told the user one would be offered. TASK-0372
    wired it to the response — never to a write."""
    docs, port = runner_workspace
    note = docs / "tests" / "TST-0001-Demo.md"
    out = _post(port, "/api/notes/test-run", {
        "id": "TST-0001", "outcome": "failing", "aborted": False,
        "runner": "user:edwin", "mtime": note.stat().st_mtime,
        "steps": [
            {"n": 1, "text": "Open the pane", "result": "pass", "evidence": "fine"},
            {"n": 2, "text": "Press the button", "expected": "something happens",
             "result": "fail", "evidence": "nothing happened"},
        ],
    })
    draft = out["result"]["issue_draft"]
    assert "step 2 failed" in draft["title"]
    assert "[[TST-0001]]" in draft["body"]
    assert "something happens" in draft["body"]      # what the note promised
    assert "nothing happened" in draft["body"]       # what the person saw
    # Offered, never filed: allocating an id is a preflight decision.
    assert not list((docs / "issues").glob("*.md")) if (docs / "issues").is_dir() else True


@pytest.mark.parametrize(
    ("outcome", "aborted", "result"),
    [
        ("passing", False, "pass"),
        # An ABORTED run that had already failed a step. The first version of
        # this case sent a passing step, so `first_fail` was None whatever the
        # code did and dropping the `aborted` guard changed nothing — a test
        # that could not fail, caught by mutating the guard it was there for.
        ("", True, "fail"),
    ],
)
def test_only_a_completed_failure_carries_a_draft(
    runner_workspace, outcome: str, aborted: bool, result: str,
) -> None:
    """A passing run has nothing to file, and an aborted one is not evidence
    either way — the same reason it writes no status. Offering an issue for a
    run the person walked out of would turn "I stopped here" into a finding."""
    docs, port = runner_workspace
    note = docs / "tests" / "TST-0001-Demo.md"
    out = _post(port, "/api/notes/test-run", {
        "id": "TST-0001", "outcome": outcome, "aborted": aborted,
        "runner": "user:edwin", "mtime": note.stat().st_mtime,
        "steps": [{"n": 1, "text": "Open the pane", "result": result,
                   "evidence": "whatever happened"}],
    })
    assert "issue_draft" not in out["result"]


def test_the_run_route_moved_and_the_old_one_redirects() -> None:
    """A deep link in somebody's history is exactly what a migration is for —
    the `RETIRED_NAV_MODES` lesson, applied to a route."""
    src = RENDERER.read_text(encoding="utf-8")
    assert "normalised.startsWith('~tests/') && normalised.endsWith('/run')" in src
    assert "normalised.startsWith('~review/') && normalised.endsWith('/run')" in src
    assert "navigateTo(`~tests/${id}/run`, { replace: true })" in src
    # Nothing navigates to the old route any more; the redirect serves links
    # that already exist, not clicks the app is still making.
    assert "~review/${" not in src.replace("~review/${key}", "")
    # And the desk's own copy of the runner entry point is gone rather than
    # left unreachable — a "moved" surface that still exists in two places has
    # not moved.
    assert "opts.run" not in src


# ---- TASK-0373: the tier suite and the release gate ----------------------
#
# The contract in `tools/instructions/TESTING.md` has described Tier 1/2/3 and
# "a release is blocked while any Tier 1/Tier 2 test is unchecked" since the
# template was written. Measured 2026-08-10 across the twelve repos the cockpit
# renders: 92 `TST-*` notes, ZERO tier classification, and a gate that had
# never been able to fire. These assert the first instance of it.

from project_os_cockpit import acceptance, statuses  # noqa: E402


SUITE = REPO_DOCS / "tests" / "ACCEPTANCE_TESTS.md"


def test_this_repo_has_a_suite_with_tier_one_populated() -> None:
    """The thing no repo had ever done."""
    suite = acceptance.load(REPO_DOCS)
    assert suite.exists, "docs/tests/ACCEPTANCE_TESTS.md is missing"
    assert len(suite.tier(1)) >= 20, len(suite.tier(1))
    assert suite.tier(2), "no regression tier"
    # Every Tier 1 section names the features it covers, or the tier is a list
    # of chores rather than feature tests.
    for item in suite.tier(1):
        assert any(r.startswith("FEAT-") for r in item.refs), item.key


def test_every_tier_two_item_names_the_issue_that_created_it() -> None:
    """TESTING.md: *"Each references the `ISS-*` that created it."* A
    regression test that cannot say what it regressed against is a Tier 1 test
    filed in the wrong place."""
    suite = acceptance.load(REPO_DOCS)
    assert suite.missing_issue_refs() == []

    # **The predicate must be able to fire**, asserted on constructed input.
    # Independent review, 2026-08-20: this assertion held over a `return []`,
    # because moving the reader off `tier:` had made its two clauses
    # contradict — `your-trainer` went 73 -> 0 and the whole suite stayed
    # green. A clean corpus cannot tell a working check from a dead one, and
    # this repo's corpus is clean.
    named = acceptance.item_from_note(
        {"id": "TST-9001", "title": "named", "level": "acceptance",
         "mark": " ", "covers": ["[[ISS-0001]]"]}, rel="x.md")
    unnamed = acceptance.item_from_note(
        {"id": "TST-9002", "title": "unnamed", "level": "acceptance",
         "mark": " ", "covers": ["[[PHASE-0013]]"]}, rel="y.md")
    probe = acceptance.Suite(path=None, items=[named, unnamed],
                             shape=acceptance.SHAPE_NOTES, platform="")
    assert [i.note_id for i in probe.missing_issue_refs()] == ["TST-9002"]


# ---- ISS-0173: the suite writes its ids bare -----------------------------


def test_a_bare_id_in_a_headings_parenthetical_is_a_ref() -> None:
    """How every suite in the fleet actually writes it.

    `_ID_RE` matched wikilink form only, and not one heading in
    `your-trainer`'s 1082-line suite uses it — 72 of 82 named a subject and
    the parser found none.
    """
    assert acceptance.heading_refs(
        "1.6 Monetization & Licensing (FEAT-0011, FEAT-0104)",
    ) == ("FEAT-0011", "FEAT-0104")


def test_wikilinked_ids_still_resolve_and_do_not_duplicate() -> None:
    """The old form keeps working, and an id written both ways is one ref."""
    assert acceptance.heading_refs("1.1 Profile ([[FEAT-0002]])") == ("FEAT-0002",)
    assert acceptance.heading_refs("2.1 Thing ([[ISS-0001]], ISS-0002)") == (
        "ISS-0001", "ISS-0002",
    )


def test_an_id_in_prose_is_not_a_ref() -> None:
    """The guard the bare form needs. A heading that *mentions* an id is not a
    heading that *names its subject*, and harvesting prose would give the
    scoped gate false subjects — which is worse than none, because it looks
    like an answer."""
    assert acceptance.heading_refs("1.9 Handles TASK-0132-style imports") == ()
    # …and a trailing parenthetical that is prose stays prose.
    assert acceptance.heading_refs("1.9 Imports (see the TASK-0132 note)") == (
        "TASK-0132",
    ), "an id inside the parenthetical is a ref even beside words — the anchor \
is the parenthetical, not the absence of prose in it"


def test_only_the_trailing_parenthetical_is_read() -> None:
    """Measured 2026-08-16: 114 of 114 id-bearing headings across every suite
    in the fleet put all of theirs there, and `area` already strips exactly
    that span."""
    assert acceptance.heading_refs("1.2 (FEAT-0001) Hardware Connectivity") == ()


def test_the_suites_sections_resolve_to_subjects() -> None:
    """The property the scoped gate depends on: a blocking row can say what it
    verifies. Asserted on this repo's own suite, where every Tier 1 section
    names its features."""
    suite = acceptance.load(REPO_DOCS)
    tier1 = suite.tier(1)
    assert tier1, "no Tier 1 items"
    assert all(item.refs for item in tier1), [
        i.key for i in tier1 if not i.refs
    ]


def test_every_id_the_suite_names_exists() -> None:
    """A checklist citing a feature or an issue that is not in the corpus is
    the drift `test_every_test_named_in_a_note_exists` catches for TST notes,
    one level up."""
    index = Index.build(REPO_DOCS)
    suite = acceptance.load(REPO_DOCS)
    missing = sorted({
        ref for item in suite.items for ref in item.refs
        if index.by_id(ref) is None
    })
    assert not missing, f"the suite names ids that do not exist: {missing}"


def test_the_tiers_render_in_the_tests_view(repo_index: Index) -> None:
    """"the view renders by tier" — and keeps the two populations apart.

    A `TST-*` note and a suite checkbox are different objects at different
    granularities (TESTING.md: both systems coexist). Merging them would put an
    automated contract test beside "click each stat tile" as though a person
    owed both.
    """
    groups = {g["key"]: g for g in nav_payload(repo_index, mode="tests")["groups"]}
    suite = acceptance.load(REPO_DOCS)
    # **Sections, derived** (ADR-0039). The keys are still `tier1`/`tier2`/
    # `tier3` because that is the address the front ends use, but the
    # population behind each is `section_of`, and nothing reads a `tier:`.
    #
    # A section is on the view when it HOLDS something — an empty one is
    # skipped, because `Automated tests · 0` would say "nothing is automated"
    # about a repo that automated nothing.
    #
    # Written as the rule rather than as today's answer, for the third time in
    # this file: the first version asserted all three unconditionally, which
    # encoded "this repo always has a third section" — the opposite of what
    # the third section is.
    sections = ("feature", "regression", "automated")
    for i, name in enumerate(sections, start=1):
        checks = suite.section(name)
        present = f"tier{i}" in groups
        # **A biconditional, asserted in both directions.** Independent review
        # caught this half-converted: `assert present is bool(checks) or
        # present` cannot fail when `present` is true, so the rule its comment
        # claimed was unasserted in the direction that matters.
        #
        # A section can be present on the non-acceptance tests' account alone —
        # they merge into the same group — so presence implies *checks or
        # merged rows*, and absence implies neither.
        merged = [r for r in (groups.get(f"tier{i}", {}).get("items") or [])
                  if str(r.get("id") or "").upper().startswith("TST-")]
        if present:
            assert checks or merged, (name, "present but empty")
        else:
            assert not checks, (name, len(checks))

    #: **Surfaces, not checks** (ISS-0222). Every check is inside exactly one
    #: of them — a surface that dropped checks would be hiding work rather
    #: than grouping it — and the non-acceptance tests merged into the section
    #: each carry a surface of their own, so the count is areas plus those.
    areas = {str(x.area or "").strip() or "—" for x in suite.section("feature")}
    own = [i for i in groups["tier1"]["items"]
           if str(i.get("id") or "").upper().startswith("TST-")]
    assert len(groups["tier1"]["items"]) == len(areas) + len(own)
    counted = sum(r["progress"]["total"] for r in groups["tier1"]["items"])
    assert counted == len(suite.section("feature")) + len(own), (
        "a surface dropped checks")

    # A manual section asks something of a person while anything is unsettled.
    # **`Automated tests` never does**, which is ISS-0237 stated as a guard:
    # nine of `your-trainer`'s 68 blocking checks were executed by a machine.
    for i, name in ((1, "feature"), (2, "regression")):
        owed = any(not x.settled for x in suite.section(name))
        if f"tier{i}" in groups:
            assert groups[f"tier{i}"].get("needs_human", False) is owed
    if "tier3" in groups:
        assert "needs_human" not in groups["tier3"]

    # **One item, one home** (ISS-0068), and the check is now over EVERY group
    # rather than over the tier ones: the two populations share sections since
    # ADR-0039, so "a note id must not be in a tier group" is no longer the
    # rule — "no id may appear twice anywhere" is, and it is strictly stronger.
    seen: list[str] = []
    for group in groups.values():
        for item in group["items"]:
            seen.append(str(item.get("id")))
            for kid in item.get("items") or []:
                seen.append(str(kid.get("id")))
    duplicated = {x for x in seen if seen.count(x) > 1}
    assert not duplicated, f"rendered twice on one screen: {sorted(duplicated)}"


# ---- the gate ------------------------------------------------------------


def test_the_gate_reads_the_live_suite_and_agrees_with_it() -> None:
    """Not a fixture — the live suite.

    This test was written as *"the gate fires on this repo right now"*, asserting
    `blocked is True`, because every box was authored unchecked and nothing had
    been walked. On 2026-08-11 the last Tier 1/2 item was settled and the
    assertion inverted: a green gate arrived as a red test. Its own docstring
    had predicted the day and got the direction wrong.

    So it asserts the *agreement* instead, which is true in both states: the
    gate blocks exactly when the document has an unsettled gating item, and
    names each one. The blocking direction is proved against fixtures by
    `test_an_unchecked_tier_one_test_blocks_and_checking_it_clears`, which is
    where a claim about mechanism belongs — a live corpus is evidence about
    today.
    """
    gate = acceptance.gate_payload(REPO_DOCS)
    suite = acceptance.load(REPO_DOCS)
    assert gate["exists"] is True
    owed = [i for i in suite.items if i.tier in (1, 2) and not i.settled]
    assert gate["blocked"] is bool(owed)
    assert len(gate["blocking"]) == len(owed)
    assert all(b["tier"] in (1, 2) for b in gate["blocking"])
    if gate["blocked"]:
        assert gate["blocking"], "blocked with nothing named is a bug in the gate"


def test_the_gate_states_the_contracts_own_rule() -> None:
    """The wording is TESTING.md's, verbatim. A surface that paraphrased it
    would be a second statement of the rule, and the two would drift."""
    rule = acceptance.gate_payload(REPO_DOCS)["rule"]
    contract = (REPO_ROOT / "tools" / "instructions" / "TESTING.md").read_text(
        encoding="utf-8",
    )
    template = (REPO_DOCS / "__templates__" / "acceptance-tests.md").read_text(
        encoding="utf-8",
    )
    assert rule in template, "the band's wording is not the template's"
    assert "**blocked** if any **manual** check is not settled" in contract


def test_a_reconciled_row_reads_settled_on_the_tests_view(repo_index: Index) -> None:
    """The two surfaces the tier fix produced, neither of which had a test.

    The label must carry the denominator the document holds *and* name the
    reconciled count — `26/27 · 1 reconciled`, never `26/26`, which is the
    rounding-down this fixed. And the row's status must be `reconciled`, which
    is a real member of `statuses.BANDS["archived"]`: if it were a bare string
    the renderer did not know, `groupIsSettled` would rank it **open** and a
    fully-settled tier would render as outstanding work — which is what
    happened, and what independent review caught.
    """
    groups = {g["key"]: g for g in nav_payload(repo_index, mode="tests")["groups"]}
    suite = acceptance.load(REPO_DOCS)
    for tier in (1, 2, 3):
        items = suite.tier(tier)
        # An empty tier has no group at all — see the reasoning in
        # `test_the_tiers_render_in_the_tests_view`. Tier 3 became empty when
        # ISS-0143 retired its two items after REL-0001, which is the state
        # the tier contract expects between releases.
        if not items:
            assert f"tier{tier}" not in groups
            continue
        group = groups[f"tier{tier}"]
        reconciled = sum(1 for i in items if i.reconciled)
        #: The denominator is what the DOCUMENT holds. ISS-0241 changed the
        #: form of this head — `26/27 completed · 1 todo` became
        #: `all 27 done · 1 reconciled`, because the todo half was the
        #: fraction subtracted — but not the thing this test is about: a check
        #: settled by decision is still one of the 27, named beside the count
        #: rather than quietly removed from both halves of it.
        automated = any(getattr(i, "command", "") for i in items)
        if not automated:
            #: **The total is read off the label, not recomputed here**
            #: ([[ISS-0242]]). The head counts the acceptance checks PLUS the
            #: non-acceptance tests merged into the section, and asserting an
            #: exact figure would mean restating that merge in the test — a
            #: second implementation of the thing under test, which is how a
            #: guard comes to agree with a bug.
            #:
            #: What this test is about survives intact: the denominator must
            #: hold every check the document has, INCLUDING the reconciled
            #: one. That is the `26/26` rounding-down it was written for.
            import re as _re2
            shown = _re2.search(r"· (?:\d+ of )?(?:all )?(\d+)", group["label"])
            assert shown, group["label"]
            assert int(shown.group(1)) >= len(items), (
                f"the head's denominator ({shown.group(1)}) is smaller than "
                f"the {len(items)} checks the section holds — a check has "
                f"been dropped from it: {group['label']!r}"
            )
            if reconciled:
                assert f"all {len(items) - reconciled} done" not in group["label"], (
                    group["label"])
        if reconciled:
            assert f"· {reconciled} reconciled" in group["label"], group["label"]
        else:
            assert "reconciled" not in group["label"], group["label"]
        # **A row is a SURFACE** (ISS-0222), so its status is about the whole
        # surface: `passing` only when every check in it is settled AND none
        # is standing on evidence a change overtook. A surface that read green
        # while one of its ticks was stale would be the lie that made
        # `your-trainer`'s honest blocking number 113 read as 60, one level up.
        per_area: dict[str, list] = {}
        for i in items:
            per_area.setdefault(str(i.area or "").strip() or "—", []).append(i)
        #: **A surface carries no status** (ISS-0226). It wore `ready`/
        #: `passing` — the runner's vocabulary, for a place in the application
        #: that is not run and cannot pass, and a second encoding of the bar
        #: besides. Its state is `progress`, and its CHECKS keep their own
        #: statuses as children.
        for row in group["items"]:
            # A section holds area surfaces AND the non-acceptance tests that
            # derive to it (ADR-0039). Only the first kind is an area; a test
            # surface is keyed by its `TST-*` id and carries its own progress.
            if str(row.get("id") or "").upper().startswith("TST-"):
                continue
            found = per_area[row["id"]]
            assert "status" not in row, (row["id"], row.get("status"))
            settled = sum(1 for i in found
                          if i.checked or i.reconciled or i.excepted)
            assert row["progress"]["done"] == settled
            assert row["progress"]["total"] == len(found)
            assert row["progress"]["stale"] == sum(1 for i in found if i.stale)
            assert len(row["items"]) == len(found), "a surface lost its checks"
    # The property the status buys, stated where it can fail: every value the
    # view emits is one the vocabulary knows, so no surface ranks it open.
    #: **A check emits a ledger MARK, and no status at all** ([[ISS-0232]]).
    #: `passing` belongs to the runner; an acceptance check rests at `active`
    #: and its outcome is an event. So the property this asserts inverts: no
    #: row anywhere under a tier may carry a value `statuses.VOCABULARY` owns,
    #: because that vocabulary is what decides whether something ranks as open
    #: work — and a check ranked by it would be counted twice.
    from project_os_cockpit import ledger as _ledger

    rows = [kid for k, g in groups.items() if k.startswith("tier")
            for row in g["items"] for kid in row.get("items") or []]
    assert rows, "no checks reachable — this guard would pass vacuously"
    assert not any("status" in kid for kid in rows)
    marks = {kid["mark"] for kid in rows if kid.get("mark")}
    assert marks <= _ledger.MARKS, marks - _ledger.MARKS


def test_the_gate_states_its_local_extension_beside_the_contracts_rule() -> None:
    """The contract blocks on *unsettled* and names one escape: a documented
    release exception. This repo clears a check a second way — reconciliation —
    so the gate implements something looser than the sentence it quotes.

    The contract's word changed with ADR-0039 (*unchecked* → *unsettled*, and
    *Tier 1/Tier 2* → *manual*); the shape of this guard did not, which is the
    point of quoting rather than paraphrasing.

    Independent review's finding. The answer is not to paraphrase the contract
    (that is the drift `rule` exists to prevent) but to state the extension
    beside it, and to say plainly that the two are different things: a
    reconciled check is **not** a release exception.
    """
    gate = acceptance.gate_payload(REPO_DOCS)
    assert "unsettled" in gate["rule"]
    local = gate["local_rule"]
    assert "reconcil" in local.lower()
    assert "not release exceptions" in local, (
        "the extension must distinguish itself from the contract's escape, or "
        "a reader counts one as the other"
    )
    # …and it must reach a surface. A payload nobody renders is the same
    # silence, one layer down — re-review's finding, since the blocked band is
    # precisely where a reader asks why a `[~]` item is not in the list.
    src = RENDERER.read_text(encoding="utf-8")
    band = re.search(r"async function mountReleaseGate\(\).*?\n\}", src, re.S).group(0)
    assert "gate.local_rule" in band
    assert band.index("gate.rule") < band.index("gate.local_rule"), (
        "the contract's own sentence comes first; the local extension follows it"
    )


def _suite_fixture(root: Path, tier1: str, tier2: str = "- [x] **B:** b.") -> Path:
    docs = root / "docs"
    _write(docs / "tests" / "ACCEPTANCE_TESTS.md", (
        "---\n"
        'type: "[[reference]]"\n'
        "id: ACCEPTANCE-TESTS\n"
        "---\n\n"
        "# Acceptance Test Suite: demo\n\n"
        "## Rules\n\n"
        "1. This numbered list is not a test and must not be parsed as one.\n"
        "- [ ] **Scaffolded from the template:** and this checkbox is not one\n"
        "  either — it sits above every tier heading, so it belongs to no tier.\n\n"
        "---\n\n"
        "# Tier 1 — Feature Tests\n\n"
        "## 1.1 An area ([[FEAT-0001]])\n\n"
        f"{tier1}\n\n"
        "---\n\n"
        "# Tier 2 — Regression Tests\n\n"
        "## 2.1 A bug ([[ISS-0001]])\n\n"
        f"{tier2}\n\n"
        "---\n\n"
        "# Tier 3 — Verification Tests (current build)\n\n"
        "- [ ] **C:** never gates, whatever its state.\n"
    ))
    return docs


def test_an_unchecked_tier_one_test_blocks_and_checking_it_clears(
    tmp_path: Path,
) -> None:
    """The demonstration TASK-0373 asks for: prove the gate with a
    deliberately unchecked test, then restore."""
    blocked = acceptance.gate_payload(
        _suite_fixture(tmp_path / "before", "- [ ] **A:** a."),
    )
    assert blocked["blocked"] is True
    assert [b["name"] for b in blocked["blocking"]] == ["A"]

    clear = acceptance.gate_payload(
        _suite_fixture(tmp_path / "after", "- [x] **A:** a."),
    )
    assert clear["blocked"] is False
    assert clear["blocking"] == []


def test_a_reconciled_item_is_settled_and_still_counted(tmp_path: Path) -> None:
    """ISS-0141. `- [~]` is the record's mark for a check settled by decision
    rather than walked — 1.5.2 describes a surface retired before the suite was
    written. It must not block, and it must not disappear: the first parser
    matched only ` |x|X`, so the line was never an item at all and the view
    reported a full bar over a document with one more row in it."""
    docs = _suite_fixture(tmp_path / "recon", "- [~] **A:** cut by decision.")
    suite = acceptance.load(docs)
    item = suite.tier(1)[0]
    assert (item.checked, item.reconciled, item.settled) == (False, True, True)
    gate = acceptance.gate_payload(docs)
    assert gate["blocked"] is False
    assert gate["counts"]["tier1"] == {
        # `excepted` joins the breakdown (FEAT-0104) and is reported BESIDE
        # `reconciled`, never folded into it: both are non-blocking, and there
        # the resemblance stops. `~` is permanent and says the check no longer
        # applies; `!` is per-release and says it still applies and was not
        # done. Conflating them is the loss ISS-0141 exists to prevent.
        "total": 1, "unchecked": 0, "reconciled": 1, "excepted": 0,
        # ADR-0039: the bucket names the derived section it counts, so a
        # reader is not left inferring it from the `tier1` key -- which is
        # kept only so a pinned client keeps reading.
        "section_key": "feature", "label": "Feature tests",
    }
    tier1 = acceptance.payload(docs)["tiers"][0]
    assert (tier1["total"], tier1["checked"], tier1["reconciled"]) == (1, 0, 1)
    assert tier1["excepted"] == 0


@pytest.mark.parametrize("line", [
    "- [v] **A:** a typo, not a tick.",
    # `[-]` used to be here as "another typo". ADR-0029 gave it a meaning —
    # Minimal's *canceled*, a check that could not be run and is not holding
    # the release — so it is recognised now and `[v]`/`[@]` carry this case.
    "- [@] **A:** another one.",
    "- [ x] **A:** a space before the x.",
    "  - [ ] **A:** indented under something.",
    "* [ ] **A:** a star bullet.",
    "+ [ ] **A:** a plus bullet.",
    "- [] **A:** no gap at all.",
])
def test_a_mark_nobody_recognises_blocks_rather_than_vanishing(
    tmp_path: Path, line: str,
) -> None:
    """The half of ISS-0141 that had no behaviour to test, because the line was
    skipped: a typo removed a check from the gate and every surface then agreed
    the suite was complete. Unclassifiable is **owed** — the direction that
    fails safely.

    Parametrised after independent review, which found the first fix had
    widened the *mark* and left the *line shape* alone: `- [v]` blocked, and
    `- [ x]`, an indented bullet and a `*` bullet all still vanished. Every
    shape ISS-0141 names is a case here, plus the two it does not.

    `- [ x]` earns its own mention: it must block, **not** be stripped into a
    tick. A parser generous enough to read a typo as a walked check is worse
    than one that drops it.
    """
    docs = _suite_fixture(tmp_path / "shape", line)
    item = acceptance.load(docs).tier(1)[0]
    assert (item.checked, item.reconciled, item.settled) == (False, False, False)
    gate = acceptance.gate_payload(docs)
    assert gate["blocked"] is True
    assert [b["name"] for b in gate["blocking"]] == ["A"]


def test_a_checkbox_inside_a_code_fence_is_an_example(tmp_path: Path) -> None:
    """`criteria.py` and the validator's box counter both skip fences on the
    stated ground that a `- [ ]` in a code block is an example, not a
    criterion. This module did not — so a documentation example inside the
    suite would have been a real gating item, blocking a release on a line
    nobody wrote as a check.

    Found by re-review, and it is the one drop the raw-line guard could not
    have caught: raw and parsed would both have counted it. The two agree on
    fences and on nothing else."""
    docs = _suite_fixture(tmp_path / "fence", (
        "- [x] **A:** walked.\n\n"
        "```markdown\n"
        "- [ ] **Example:** how to write one of these.\n"
        "```\n"
    ))
    suite = acceptance.load(docs)
    assert [i.name for i in suite.tier(1)] == ["A"], [i.name for i in suite.tier(1)]
    assert acceptance.gate_payload(docs)["blocked"] is False


def test_the_live_suite_loses_no_line_to_the_parser() -> None:
    """The one non-tautological claim about the live document.

    Every other live-corpus assertion derives its expectation from
    `acceptance.load` — the same function under test — so a line the parser
    drops shrinks both sides together and nothing fails. Independent review
    demonstrated it: one Tier 1 item made to vanish from `ACCEPTANCE_TESTS.md`,
    **ISS-0141's exact defect**, and this file stayed green at 52 passed.

    So: count the checkbox lines with a regex that shares no code with the
    parser, and require the parsed count to equal it. A dropped line fails
    here and only here.
    """
    suite_file = REPO_DOCS / acceptance.SUITE_REL
    if suite_file.exists():
        text = suite_file.read_text(encoding="utf-8")
        # Only what sits under a tier heading — the preamble's own checkbox is
        # deliberately not a test (`test_nothing_above_the_first_tier_heading…`).
        body = re.split(r"(?m)^#\s+Tier\s+1\b", text, maxsplit=1)[1]
        # Fences are skipped on both sides: a `- [ ]` in a code block is an
        # example of a checkbox, not one. That is the single structural rule
        # this counter shares with the parser — it deliberately shares no
        # *item* regex, which is the independence that makes the comparison
        # worth anything.
        raw, in_fence = 0, False
        for line in body.splitlines():
            if re.match(r"^\s*(```|~~~)", line):
                in_fence = not in_fence
                continue
            if not in_fence and re.match(r"^\s*[-*+]\s+\[", line):
                raw += 1
        subject = "checkbox line(s) in the suite"
    else:
        # **The same claim about the shape this repo now stores** (ADR-0030).
        # The suite is `CHK-*` notes, so the independent counter is a walk of
        # the directory looking for the one field that makes a note a check —
        # `tier:` — with a regex that shares no code with `item_from_note`.
        #
        # Rewritten rather than deleted, and that distinction is the whole
        # point: this guard exists because independent review made one Tier 1
        # item vanish and the file stayed green at 52 passed. A guard whose
        # subject changes storage and is deleted takes its property with it,
        # which is how a corpus loses the only check that was ever independent
        # of the reader under test.
        # Every note in the acceptance directory, without asking whether its
        # tier reads — because a check whose tier cannot be read still blocks
        # (it lands in Tier 1), and a counter that skipped it would agree with
        # a reader that had lost it.
        #
        # Both id shapes: `TST-*` since ADR-0031 folded the check type into
        # `test`, `CHK-*` in a repo that has not run the merge migration. Never
        # both — the migration renames in place.
        _acc = REPO_DOCS / acceptance.CHECKS_REL
        raw = len(list(_acc.glob("TST-*.md")) or list(_acc.glob("CHK-*.md")))
        subject = "acceptance note(s) on disk"
    parsed = len(acceptance.load(REPO_DOCS).items)
    assert parsed == raw, (
        f"{raw - parsed} {subject} are invisible to the reader — the gate is "
        "counting a smaller suite than the one on disk"
    )


def test_a_clear_gate_says_which_of_its_tests_were_reconciled() -> None:
    """A clear band reading *"every Tier 1 and Tier 2 test is checked"* is
    false when one of them was settled by decision instead — and the clear
    state is where an overstatement costs most, because nobody looks twice at
    a green light. The band must have both sentences and pick on the count."""
    src = RENDERER.read_text(encoding="utf-8")
    band = re.search(r"async function mountReleaseGate\(\).*?\n\}", src, re.S).group(0)
    assert "reconciled" in band, "the clear band cannot distinguish completed from settled"
    assert "by reconciliation rather than by being completed" in band
    assert band.index("const reconciled") < band.index("Release gate clear")


def test_tier_three_never_gates(tmp_path: Path) -> None:
    """TESTING.md: *"Tier 3 tests do not gate releases (they are verification
    aids, not requirements)."* The fixture's Tier 3 item is unchecked in both
    cases above; only Tier 1/2 move the verdict."""
    docs = _suite_fixture(tmp_path / "t3", "- [x] **A:** a.")
    gate = acceptance.gate_payload(docs)
    assert gate["blocked"] is False
    assert acceptance.load(docs).tier(3), "the fixture lost its Tier 3 item"


def test_a_repo_with_no_suite_is_unknown_not_clear(tmp_path: Path) -> None:
    """**Absent is not passing**, and this is the assertion the whole task
    turns on: before today every repo had no suite, so `blocking()` was empty
    and any naive gate would have reported clear. A green light nobody earned
    is worse than no gate."""
    docs = tmp_path / "empty" / "docs"
    docs.mkdir(parents=True)
    gate = acceptance.gate_payload(docs)
    assert gate["exists"] is False
    assert gate["blocked"] is False        # nothing to block ON
    # …so the surface must distinguish the two, and does:
    src = RENDERER.read_text(encoding="utf-8")
    band = re.search(r"async function mountReleaseGate\(\).*?\n\}", src, re.S).group(0)
    assert "if (!gate.exists)" in band
    assert band.index("if (!gate.exists)") < band.index("if (!gate.blocked)"), (
        "the unknown case must be decided before the clear case, or a repo "
        "with no suite renders as a passing gate"
    )


def test_nothing_above_the_first_tier_heading_is_a_test(tmp_path: Path) -> None:
    """The template's preamble carries a numbered `## Rules` list, a `## Test
    Tiers` bullet list and prose. A parser that swept the whole document would
    report them as unchecked Tier 0 items — which, being unchecked, would block
    every release forever on the strength of the rules text.

    The fixture carries a **checkbox** in the preamble, not only a numbered
    list: with prose alone this passed whether or not the guard existed, which
    a mutation caught."""
    docs = _suite_fixture(tmp_path / "rules", "- [ ] **A:** a.")
    items = acceptance.load(docs).items
    assert {i.tier for i in items} == {1, 2, 3}
    assert all(i.name in {"A", "B", "C"} for i in items), [i.name for i in items]


# ---- TASK-0375: decide and accept on the constraints view ----------------


def test_a_proposed_adr_is_this_views_obligation(owed_corpus: Index) -> None:
    """From the registry, and marked on the row rather than counted twice.

    Measured 2026-08-10: the intent view owes exactly **one** thing, and it is
    `ADR-0010` — which is also one of the four decisions REL-0001 says to raise
    and stop on. A view whose obligation list has one member is easy to build
    wrong and impossible to notice, so the mark and the badge are asserted to
    be the same predicate.
    """
    groups = nav_payload(owed_corpus, mode="design")["groups"]
    # `needs-you` is a SHORTCUT list, not a group of this view's own
    # making (ADR-0025): its rows keep their structural place too, and
    # counting or enumerating them here would count the same obligation
    # twice. Excluded explicitly rather than by loosening the assertion.
    owed = [
        i for g in groups if g["key"] != "needs-you"
        for i in g["items"] if i.get("owed")
    ]
    # The whole view's badge, standing documents included (TASK-0382) — the
    # assertion is that the marks and the count are one predicate, so it must
    # be taken over the whole view rather than one group of it.
    assert obligations.counts(owed_corpus)["intent"] == len(owed)
    assert all(i["owed_verb"] for i in owed)
    note_owed = {
        i["id"] for g in groups
        if g["key"] not in ("standing", "needs-you")
        for i in g["items"] if i.get("owed")
    }
    # The PROPERTY, not the membership. This asserted `== {"ADR-0010"}` and
    # broke the moment a second ADR was proposed ([[ADR-0021]], 2026-08-11) —
    # correct behaviour failing a test that had pinned the corpus's state on
    # the day it was written. What matters is that every `proposed` ADR is
    # owed here and nothing settled is.
    proposed_adrs = {
        (r.note_id or "")
        for r in owed_corpus.notes_by_type("adr")
        if str(r.status or "").strip().lower() == "proposed"
        and not r.rel_path.startswith("__templates__/")
    }
    proposed_adrs |= {
        (r.note_id or "")
        for r in owed_corpus.notes_by_type("decision")
        if str(r.status or "").strip().lower() == "proposed"
        and not r.rel_path.startswith("__templates__/")
    }
    # A `proposed` DESIGN is owed here too — it is waiting on an Accept, which
    # is the same obligation wearing a different type. Left out of the first
    # generalisation and caught when DES-0009 was briefly offered for review.
    proposed_adrs |= {
        (r.note_id or "")
        for r in owed_corpus.notes_by_type("design")
        if str(r.status or "").strip().lower() == "proposed"
        and not r.rel_path.startswith("__templates__/")
    }
    assert proposed_adrs, "no proposed ADR in the corpus; this test proves nothing"
    assert note_owed == proposed_adrs, (
        f"owed set {sorted(note_owed)} does not match the proposed ADRs "
        f"{sorted(proposed_adrs)}"
    )
    # The fixture's own proposed ADR, not a corpus id (ISS-0153's lesson):
    # `ADR-0010` was named here and stopped being owed on 2026-08-12 when Edwin
    # accepted it — a project making progress must not fail its own tests.
    assert "ADR-9002" in note_owed, "the fixture's proposed ADR is not owed"


def test_a_design_verdict_cannot_go_through_the_transition_path(
    tmp_path: Path,
) -> None:
    """ISS-0056, which the generic transition table re-opened.

    A design accepted through `/api/notes/transition` gets `status: accepted`
    and **no `design_revision`** — so an approval given to revision 3 silently
    covers revision 6. Rejection is worse: it writes `cancelled` onto a design
    that may already be `implemented`.

    Refused in the writer, not only in the UI. A design reaching
    `stamp_transition` at all means something routed around the endpoint.
    """
    from project_os_cockpit import note_writes

    docs = tmp_path / "docs"
    _write(docs / "designs" / "DES-0001-Demo.md", (
        "---\n"
        'type: "[[design]]"\n'
        "id: DES-0001\n"
        'title: "A demo design"\n'
        "status: proposed\n"
        "---\n\n# DES-0001\n"
    ))
    index = Index.build(docs)
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.stamp_transition(index, "DES-0001", to_status="accepted")
    assert exc.value.status == 403
    assert "/api/design/verdict" in exc.value.message
    assert "ISS-0056" in exc.value.message
    # And the note is untouched — a refusal that half-wrote would be worse
    # than the bug.
    assert "status: proposed" in (docs / "designs" / "DES-0001-Demo.md").read_text()


def test_the_buttons_still_appear_and_carry_their_endpoint() -> None:
    """Refusing the path must not remove the action.

    The vocabulary stays in `HUMAN_TRANSITIONS` — a design at `proposed` is
    still accepted or declined by a human — and each action names the endpoint
    that has to serve it, plus what it means there. Deriving `accept` in the
    renderer from the verb's name (or from the tone `confirm` carries) is the
    status vocabulary leaking into TypeScript one field at a time.
    """
    from project_os_cockpit import note_writes

    actions = note_writes.legal_actions("design", "proposed")
    assert [a["verb"] for a in actions] == ["Accept", "Decline"]
    assert all(a["endpoint"] == "/api/design/verdict" for a in actions)
    assert actions[0]["accept"] is True and actions[0]["verdict"] == "approved"
    assert actions[1]["accept"] is False
    # Nothing else is routed away, so the field cannot become decoration.
    assert all(
        not a.get("endpoint")
        for kind, status in (("adr", "proposed"), ("requirement", "draft"),
                             ("issue", "triage"))
        for a in note_writes.legal_actions(kind, status)
    )


def test_the_renderer_reads_the_field_not_the_type() -> None:
    """One place knows designs are special, and it is not this one.

    A `type === 'design'` branch in the renderer would be that knowledge in a
    second place, and the two would drift the first time another type earned
    its own endpoint.
    """
    src = RENDERER.read_text(encoding="utf-8")
    fn = re.search(
        r"async function performNoteAction\(.*?\n\}", src, re.S,
    ).group(0)
    assert "action.endpoint === '/api/design/verdict'" in fn
    assert "noteType" not in fn and "note.type" not in fn
    verdict = re.search(
        r"async function performDesignVerdict\(.*?\n\}\n\n", src, re.S,
    ).group(0)
    # The revision is fetched, never assumed, and a dirty artifact is refused:
    # the frame shows a working copy no revision covers.
    assert "design-revisions/" in verdict
    assert "revs.dirty" in verdict
    assert "action.verdict" in verdict and "action.accept" in verdict
    # Posts to the route it was SENT, so the endpoint is named once.
    assert "postJson(action.endpoint!" in verdict


# ---- TASK-0382: the standing documents land on Intent --------------------


def test_the_intent_view_opens_on_the_standing_set(repo_index: Index) -> None:
    """*"What is this project?"* is the question the view answers, so it opens
    on the documents that answer it — in manifest order, all eight, present or
    not. A manifest of eight showing six would answer "which of these exist"
    with silence, and a missing ARCHITECTURE is the most interesting row."""
    from project_os_cockpit import standing

    groups = nav_payload(repo_index, mode="design")["groups"]
    # **Amended 2026-08-12 (FEAT-0094).** Intent now opens on what needs a
    # person, and the standing set leads everything after it — Edwin's
    # request, and the same shape every other view got. The claim this test
    # protects is unchanged in substance: the standing set is the first thing
    # about the PROJECT that the view says, ahead of designs and decisions.
    own = [g for g in groups if g["key"] != "needs-you"]
    assert own[0]["key"] == "standing", [g["key"] for g in groups]
    if groups[0]["key"] == "needs-you":
        assert groups[0]["needs_human"] is True
    listed = [i["id"] for g in groups if g["key"] == "standing" for i in g["items"]]
    assert listed == [d.name for d in standing.manifest(REPO_DOCS.parent)]
    # Each row says when it was last confirmed, or what is wrong with it.
    assert all(i["subtitle"] for g in groups if g["key"] == "standing" for i in g["items"])


def test_a_stub_is_owed_and_staleness_only_marks(owed_corpus: Index) -> None:
    """The line, and it is a decision rather than an oversight.

    Missing / ambiguous / stub are binary and one act clears each: write the
    document, delete the rival, fill in the template. Staleness returns by the
    calendar, so counting it is a badge that re-arms itself forever — the
    permanent nag this project has been bitten by twice (PHASE-015's close-out
    pill, `Doing · 44`). It still marks the row.

    Measured 2026-08-10: ARCHITECTURE and OWNERSHIP hold their templates;
    DESIGN and STYLEGUIDE were last confirmed 196 days ago.

    That last number is **not** asserted. It was, and the test began failing on
    2026-08-11 for the only reason it could: the day count is computed from
    today, so a literal `196 days` is true for one day and false forever after.
    A test that expires by the calendar is the same re-arming-by-time problem
    this very test exists to keep OUT of the badge. What matters is that the
    row reports a staleness at all, and that reporting it does not make it owed.
    """
    rows = {i["id"]: i
            for g in nav_payload(owed_corpus, mode="design")["groups"]
            if g["key"] == "standing"
            for i in g["items"]}
    # `GLOSSARY` is the fixture's genuine stub. `ARCHITECTURE` was named here
    # and stopped being one when ISS-0153 taught the check that inline code is
    # not a template — which is the check getting *better*, not the row.
    assert rows["GLOSSARY"].get("owed") is True
    assert rows["GLOSSARY"]["owed_verb"] == "Write", (
        "a stub is written, not confirmed — you cannot confirm a document "
        "nobody has written (ISS-0153)"
    )
    # Stale marks — a status the navigator can sort and fold on — but does not
    # ask, so it carries no `owed`.
    # `STYLEGUIDE` is the fixture's constructed stale document. `DESIGN` was
    # named here and stopped being stale on 2026-08-12 when it was rewritten —
    # a test about an age rule must not depend on a document being neglected.
    assert rows["STYLEGUIDE"]["status"] == "review"
    assert "owed" not in rows["STYLEGUIDE"]
    assert re.search(r"last confirmed \d+ days ago", rows["STYLEGUIDE"]["subtitle"]), (
        f"the row should report its staleness in days; got {rows['STYLEGUIDE']['subtitle']!r}"
    )


def test_the_standing_obligation_reaches_the_intent_badge(owed_corpus: Index) -> None:
    """A panel that did not reach the badge would be decoration.

    The subject here is a **manifest entry**, not a note type — which is why
    `architecture`/`glossary`/`reference` still declare `NONE` in the
    type-keyed table and this is declared beside it. Both feed one count, so
    the badge stays the sum of what the view marks.
    """
    # DISTINCT ids, not a count of marks (ADR-0025). The `needs-you` group is
    # a shortcut list whose rows keep their structural place, so counting
    # marks now counts the same obligation twice — which is the one hazard
    # that decision introduces, and the badge is exactly the surface it would
    # have broken.
    marked = len({
        i["id"] for g in nav_payload(owed_corpus, mode="design")["groups"]
        for i in g["items"] if i.get("owed")
    })
    assert obligations.counts(owed_corpus)["intent"] == marked
    assert obligations.standing_owed(owed_corpus.docs_root) > 0, (
        "this repo no longer exercises the standing obligation — pick another "
        "assertion or the guard is vacuous"
    )
    # And the total the badges claim is still the sum of the badges.
    badges = obligations.badges_payload(owed_corpus)
    assert badges["total"] == sum(badges["views"].values())


def test_the_standing_set_is_not_a_second_obligation_list(repo_index: Index) -> None:
    """ISS-0068 forbids one obligation with two homes. The Library still shows
    these as *files* in a tree, which is a different question (ISS-0125 keeps
    that overlap deliberately) — but no other group in any view may mark them
    as owed."""
    standing_ids = {
        i["id"]
        for g in nav_payload(repo_index, mode="design")["groups"]
        if g["key"] == "standing"
        for i in g["items"]
    }
    for mode in ("features", "issues", "tests", "library", "design"):
        for group in nav_payload(repo_index, mode=mode)["groups"]:
            # `needs-you` joins `standing` as an exemption (ADR-0025): it is
            # a shortcut list, so the same obligation appearing there and in
            # its structural place is the decision rather than the defect.
            # Everything else still obeys ISS-0068.
            if group["key"] in ("standing", "needs-you"):
                continue
            clashing = {
                i.get("id") for i in group["items"] if i.get("owed")
            } & standing_ids
            assert not clashing, f"{mode}/{group['key']} also marks {clashing}"


# ---- TASK-0313 groundwork: the digest reads the registry ------------------


def test_the_digest_and_the_badges_count_the_same_things(owed_corpus: Index) -> None:
    """`DIGEST_NEEDS_YOU` was a second list of what needs a person — six types
    and their states, written before the registry existed. TASK-0313's own note
    said what to do about it: *"it reads from FEAT-0089's registry once that
    lands. If it outlives the registry it becomes exactly the drift ISS-0023
    describes."*

    The difference is not cosmetic. The old list omitted `change` (81 owed
    here) and `feature`, and could not express the `test` predicate's
    manual-only clause — so a digest built from it would have told the
    returning human that 8 things needed them while the badges said 96.

    **The standing gap closed on 2026-08-13** (ISS-0159). This asserted
    `badges - standing`, on the reasoning that *"their subject is a manifest
    entry rather than a note, and the digest is a note digest"*. Two things
    that were true when it was written stopped being true:

    - `owed_items` had no rows for a note-less obligation, so the digest could
      not have included one had it wanted to. TASK-0416 gave them rows.
    - The digest's `needs_you` **list** is no longer rendered anywhere — ISS-0145
      took it off the band, because *"an obligation is not news"*. What survives
      is the **count**, on the attention card, sitting beside the very badges it
      disagreed with. A note-shaped list was a defensible thing to scope to
      notes; a count of what needs a person is not.

    So the gap was a limitation described as a principle, and the number was
    short by exactly the note-less obligations — 13 against 14 on the live repo,
    and thirty-eight apart on one with stale standing documents and unpushed
    work. TASK-0313's own intent is what now holds: *"it reads from FEAT-0089's
    registry."*

    The digest remains a legitimate **superset**: it also carries notes whose
    `review_verdict` still owes work, which the registry does not count.
    """
    digest = cockpit.digest_payload(
        owed_corpus.docs_root.parent, owed_corpus, "1970-01-01T00:00:00Z",
    )
    badges = obligations.badges_payload(owed_corpus)
    assert digest["needs_you_count"] >= badges["total"], (
        "the digest under-reports what the badges show — a note-less "
        "obligation has gone invisible to it again (ISS-0159)"
    )
    owed_ids = {
        r["id"] for rows in obligations.owed_items(owed_corpus).values() for r in rows
    }
    digest_ids = {str(i.get("id") or "") for i in digest["needs_you"]}
    assert owed_ids <= digest_ids, sorted(owed_ids - digest_ids)
    # The note-less kinds are what this used to exclude, so assert they are
    # actually present rather than trusting the totals to have covered them.
    assert obligations.standing_owed(owed_corpus.docs_root) > 0, (
        "the fixture's standing set is clean — the case this closes is not "
        "exercised, and the assertions above would pass vacuously"
    )
    # And every row says what is owed of it, from the registry's verb.
    typed = [i for i in digest["needs_you"] if i.get("owed")]
    assert typed and all(i["owed_verb"] for i in typed)


# ---- FEAT-0071: since you looked -----------------------------------------
#
# Source-level for the two surfaces, because the renderer is one module with
# no exports and the repo has no DOM harness — a limitation TST-0022 already
# discloses. The PAYLOAD half is asserted behaviourally above and in
# `test_watermark.py`; what these pin are the decisions DES-0008 made that a
# later edit could silently reverse.


def _renderer_fn(name: str) -> str:
    src = RENDERER.read_text(encoding="utf-8")
    match = re.search(rf"function {name}\(.*?\n\}}\n", src, re.S)
    assert match, f"{name} is gone from the renderer"
    return match.group(0)


def test_caught_up_records_when_the_digest_was_computed() -> None:
    """The single most reversible decision in this feature.

    `computed_at`, never `Date.now()`: anything that lands while the human is
    reading must not be marked seen. Posting the moment of the click would be
    a one-word edit that loses work silently and looks identical on screen.
    """
    band = _renderer_fn("mountDigestBand")
    assert "'/api/cockpit/caught-up', { at: d!.computed_at }" in band
    assert "Date.now()" not in band and "new Date()" not in band


def test_the_caught_up_button_is_at_the_foot() -> None:
    """DES-0008: *"`Caught up` sits at its end — reading to the bottom is what
    being caught up means."* In the header it would be a dismiss control, and a
    dismiss control on a digest is a way to mark unread things read."""
    band = _renderer_fn("mountDigestBand")
    assert band.index("digest-head") < band.index("digest-foot")
    assert band.index("digest-list") < band.index("digest-caught-up")
    # …and it clears the band it sits under (ISS-0145). Re-rendering was the
    # right answer while the band also held obligations; with those gone,
    # anything short of removal is a dismiss control that does not dismiss.
    assert "band.remove()" in band
    assert "void mountDigestBand()" not in band


def test_the_band_carries_news_and_not_obligations() -> None:
    """This asserted the reverse until 2026-08-11, and the reversal is the
    point (ISS-0145).

    DES-0008 lifted *"needs-you items above the merely-informational"* because
    the digest was the only surface gathering obligations. The badges and the
    view landings ([[FEAT-0092]]) are that surface now, so a band headed
    *"Since you looked"* carrying things that did not happen while you were
    away files them under the wrong sentence — and made `Caught up` a control
    that could not clear what it sat beneath.

    The payload still returns both lists: `needs_you_count` feeds the rail's
    per-workspace attention dot, which is a different surface with a different
    question.
    """
    band = _renderer_fn("mountDigestBand")
    assert "const moved = d.transitions" in band
    assert "const owed = d.needs_you" not in band, (
        "the obligations half is back in the digest; it belongs to the badges"
    )
    assert "digest-list is-owed" not in band


def test_the_band_is_absent_when_nothing_is_behind() -> None:
    """Absent, never a permanent "nothing happened" — the shape of thing a
    reader learns to stop seeing, which this surface has been taught twice."""
    band = _renderer_fn("mountDigestBand")
    # `needs_you_count` deliberately no longer keeps it open (ISS-0145): an
    # obligation is not news, and a band that stayed for one was a band whose
    # dismiss control could not dismiss it.
    assert "if (!d || !d.transition_count) return;" in band


def test_the_landing_cards_widened_past_waiting_terminals() -> None:
    """DES-0008's actual complaint: *"the landing's NEEDS-YOU cards know only
    about waiting terminals"*. A repo with eleven things needing a human and a
    quiet terminal looked exactly like a repo with nothing to do.

    A `record` card fixes that — and rides on the existing card when one is
    already there, because one workspace as two rows is the failure ISS-0068
    names.
    """
    src = RENDERER.read_text(encoding="utf-8")
    entries = _renderer_fn("attentionEntries")
    assert "'needs-input' | 'waiting' | 'record'" in src
    assert "carded.has(wsId)" in entries, (
        "a workspace with both an agent and owed work would get two cards"
    )
    # And a record card opens the overview, where the digest band is — not the
    # terminal, which is what made these cards terminal-only in the first place.
    row = _renderer_fn("buildAttentionRow")
    assert "entry.kind === 'record'" in row and "'~overview'" in row


def test_every_workspaces_sidecar_url_is_kept() -> None:
    """"One line per workspace" looked impossible because the renderer threw
    the data away: the shell announces one sidecar URL per workspace and the
    `ready` handler discarded every one but the active workspace's."""
    src = RENDERER.read_text(encoding="utf-8")
    assert "sidecarUrls.set(p.workspaceId, p.url);" in src
    assert src.index("sidecarUrls.set(p.workspaceId, p.url);") < src.index(
        "if (p.workspaceId !== activeId)",
    ), "the URL must be kept BEFORE the active-workspace guard returns"


def test_the_digest_is_pulled_and_rate_limited() -> None:
    """DES-0008's Out of Scope: *"Notifications, badges, or anything pushed.
    Pulled on arrival, always."* And `refreshAttention` is called from a dozen
    places as a plain redraw, so the fetch behind it must not run every time."""
    src = RENDERER.read_text(encoding="utf-8")
    assert "DIGEST_MIN_INTERVAL_MS = 30_000" in src
    refresh = _renderer_fn("refreshAttention")
    # Repaints via `paintAttention`, never itself — a slow sidecar must not be
    # able to start a loop.
    assert "paintAttention(attentionEntries())" in refresh
    assert "refreshAttention()" not in refresh.split("function refreshAttention")[1]


# ---- FEAT-0090: the desk retires -----------------------------------------


def test_every_row_of_the_rehoming_table_is_reachable(owed_corpus: Index) -> None:
    """ADR-0020's table, walked against the live corpus rather than inspected.

    Nine rows. Two are empty in this corpus today (no `proposed` design, no
    manual test at `ready`) — and an empty row is exactly how `change` and
    `release` went missing from the registry, so their homes are asserted to
    EXIST rather than to be populated.
    """
    def owed_ids(mode: str) -> set[str]:
        out: set[str] = set()
        for group in nav_payload(owed_corpus, mode=mode)["groups"]:
            for item in group["items"]:
                if item.get("owed"):
                    out.add(str(item.get("id")))
                for child in item.get("children") or []:
                    if child.get("owed"):
                        out.add(str(child.get("id")))
        return out

    # 1. Decisions — ADR `proposed` → the constraints view.
    assert "ADR-9002" in owed_ids("design")
    # 2. Proposals — requirement `draft` → Features.
    assert {i for i in owed_ids("features") if i.startswith("REQ-")}
    # 3/4. design `proposed` and manual `ready` are empty here; their views
    #      own the kind, which is what must survive an empty corpus.
    views = obligations.views_owed()
    assert "design" in views[obligations.VIEW_INTENT]
    assert "test" in views[obligations.VIEW_TESTS]
    # 5. The tests register → the Tests view.
    # The section a row lands in is derived now, so this asserts the row is
    # REACHABLE rather than naming a verdict-state group that is gone (ADR-0039).
    assert _items(nav_payload(owed_corpus, mode="tests")["groups"])
    # 6. `changes-requested` re-review → the view owning each note's type.
    #
    # This step asserted `not [r for r in reviewed if r["owed"]]` — that the
    # corpus contains **zero** outstanding verdicts. That was a true statement
    # about the data on the day it was written (all ten rows terminal, which is
    # ISS-0121's finding) written in the position of a rule, so the first honest
    # `changes-requested` recorded against this repo broke it. Three arrived on
    # 2026-08-14 from a real review pass, and a suite that fails when review
    # finds something is a suite that discourages review.
    #
    # ISS-0120's class exactly, and this file is where that lesson was learned.
    # The rule underneath is the same one steps 1–5 assert: an owed row is
    # *reachable* from the view that owns its type. Whether any exist is data.
    reviewed = cockpit._reviewed_register(owed_corpus)
    assert reviewed, "the reviewed register is empty; nothing below tests anything"
    for row in reviewed:
        if not row.get("owed"):
            continue
        note = owed_corpus.by_id(str(row["id"]))
        assert note is not None, f"{row['id']} is owed but resolves to no note"
        record = owed_corpus.get(note)
        view = obligations.for_type(record.note_type)
        assert view, (
            f"{row['id']} carries an owed verdict but its type "
            f"{record.note_type!r} belongs to no view, so nothing surfaces it"
        )
    # ISS-0121's finding, stated as the property rather than as a count: a
    # sticky verdict on a note that has since reached a terminal status is not
    # owed. That is what keeps the register from nagging about settled work.
    for row in reviewed:
        if row.get("owed"):
            note = owed_corpus.by_id(str(row["id"]))
            record = owed_corpus.get(note) if note else None
            assert record is not None and not cockpit.is_done_status(
                record.note_type, str(record.status or "")), (
                f"{row['id']} is terminal but still counted as owing a re-review"
            )
    # 7. "am I done" → the badges.
    assert obligations.badges_payload(owed_corpus)["total"] > 0
    # 8. Reviewed register → the record surfaces.
    src = RENDERER.read_text(encoding="utf-8")
    assert "fillReviewedCard" in src
    assert "/api/cockpit/reviewed" in src
    # 9. Questions → nowhere, deliberately: no obligation kind claims them.
    assert "question" not in obligations.declared_types()


def test_the_badges_still_total_the_registry_with_no_desk() -> None:
    """The assertion TASK-0378 asks for by name.

    The desk's one number was the thing the badges replace. If retiring it
    left any kind uncounted, the sum stops matching — which is the same
    property FEAT-0089 was built to make checkable.
    """
    index = Index.build(REPO_DOCS)
    badges = obligations.badges_payload(index)
    assert badges["total"] == sum(badges["views"].values())
    per_type = obligations.views_owed()
    assert set(badges["kinds"]) == {
        t for types in per_type.values() for t in types
    }
    # And every declared owing kind has a view that exists.
    for view, types in per_type.items():
        assert view in obligations.VIEWS
        for note_type in types:
            assert obligations.for_type(note_type).view == view


def test_the_desk_button_and_mode_are_gone_and_migrate() -> None:
    """A stored preference pointing at a mode with no button is the trap
    `RETIRED_NAV_MODES` exists to prevent — the reader lands somewhere they
    cannot see is selected and cannot leave by clicking."""
    html = (REPO_ROOT / "desktop" / "src" / "renderer" / "index.html").read_text(
        encoding="utf-8",
    )
    buttons = re.findall(r'top-bar-btn[^>]*data-mode="(\w+)"', html)
    assert "review" not in buttons
    src = RENDERER.read_text(encoding="utf-8")
    retired = re.search(r"const RETIRED_NAV_MODES[^=]*= \[(.*?)\]", src, re.S).group(1)
    assert "'review'" in retired
    fallback = re.search(
        r"const RETIRED_MODE_FALLBACK[^=]*= \{(.*?)\n\};", src, re.S,
    ).group(1)
    assert re.search(r"review:\s*'overview'", fallback)


def test_the_review_route_stays_while_the_ledger_has_open_entries() -> None:
    """Retiring the route with a live request behind it would strand it.

    Measured 2026-08-10: this repo's `.cockpit/review-requests.json` holds one
    OPEN entry. Where proposals, questions and offered designs finally land is
    ISS-0126 — Edwin's decision, and deliberately not guessed at — so the route
    stays served and the record column links to it when, and only when, there
    is something behind it.
    """
    src = RENDERER.read_text(encoding="utf-8")
    assert "normalised === '~review'" in src, "the route was deleted"
    card = _renderer_fn("fillReviewedCard")
    assert "openReviewRequestCount" in card
    assert "if (open <= 0) return;" in card, (
        "the ledger link must be absent when the ledger is empty"
    )
    # The store itself is untouched — `review_queue_payload` and the resolve
    # path still exist, which is the DoD's "the review ledger and its store are
    # untouched".
    server = (REPO_ROOT / "src" / "project_os_cockpit" / "server.py").read_text(
        encoding="utf-8",
    )
    assert "/api/cockpit/review-queue" in server
    assert "/api/cockpit/review-resolve" in server


# ----- `Verified` is a claim, not a fallback (ISS-0212 / REQ-0046) ----------


def _groups_for(docs: Path) -> dict[str, list[str]]:
    from project_os_cockpit.index import Index
    return {
        g["key"]: [str(i.get("id") or i.get("title")) for i in g["items"]]
        for g in cockpit._tests_groups(Index.build(docs))
    }


def test_a_status_nobody_handled_is_visible_rather_than_reported_as_passing(
    tmp_path: Path,
) -> None:
    """REQ-0046, asserted on the FALLBACK and not on the three known ids.

    `_tests_groups` ended in `else: verified`, so any status the chain did not
    name landed in the one group whose label is a claim about evidence — *this
    was checked and it passed*. `your-trainer` supplied the instance: three
    `status: retired` documents, one of them a **run plan**, reported as
    verified tests.

    The instance is not the point and a guard keyed on `retired` would miss
    the next one. This invents a status no vocabulary contains and asserts it
    surfaces loudly, which is the same shape as ADR-0034's fail-closed clause:
    when a classifier meets something it does not understand, the safe
    direction is the one that asks for a person.
    """
    docs = tmp_path / "docs"
    (docs / "tests").mkdir(parents=True)
    (docs / "tests" / "TST-0001-Invented.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0001\ntitle: "A test in a state nobody '
        'planned for"\nstatus: quiescent\nlast_verified: 2026-08-18\n---\n\n'
        "# A test in a state nobody planned for\n",
        encoding="utf-8",
    )
    groups = _groups_for(docs)
    # **The fallback is no longer a claim about evidence** (ADR-0039). There is
    # no `Verified` group and no `unclassified` catch-all, because no section
    # is decided by a status any more: `feature` means *this check is about
    # current behaviour*, which is a statement about the check's subject and
    # not about whether anybody ran it.
    #
    # So the fail-closed property is preserved in the direction that matters —
    # the row is VISIBLE, and it is visible in a section that is completed
    # rather than one asserting it already passed. A status nobody planned for
    # can no longer be laundered into evidence, because no section carries any.
    assert "TST-0001" in groups.get("feature", []), (
        "an unrecognised status vanished instead of surfacing; a row the view "
        "cannot classify must be visible, not quiet"
    )
    assert "TST-0001" not in groups.get("automated", []), (
        "a note with no command: reached the section that means CI executes it"
    )
    assert "TST-0001" not in groups.get("retired", []), (
        "a status nobody planned for was read as terminal"
    )


def test_a_retired_test_is_not_a_passing_one(tmp_path: Path) -> None:
    """The instance, kept beside the general rule rather than instead of it.

    A retired test has been withdrawn, not passed. `your-trainer` carries a
    retired checklist, a retired test list and a retired run plan — documents
    the PHASE-035 migration read *from*, left carrying `type: "[[test]]"`.
    """
    docs = tmp_path / "docs"
    (docs / "tests").mkdir(parents=True)
    (docs / "tests" / "TST-0002-Withdrawn.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0002\ntitle: "Withdrawn"\n'
        "status: retired\nlast_verified: 2026-08-18\n---\n\n# Withdrawn\n",
        encoding="utf-8",
    )
    groups = _groups_for(docs)
    # The group is `retired` since ADR-0039 — `resolved` was its key when the
    # sections were verdict states. The claim is unchanged: withdrawn is not
    # passed, and it must not sit anywhere that reads as evidence.
    assert "TST-0002" in groups.get("retired", [])
    assert "TST-0002" not in groups.get("feature", [])
    assert "TST-0002" not in groups.get("automated", [])


# ----- the tier tracking line (TASK-0509) -----------------------------------


def _suite_repo(tmp_path: Path, rows: list[tuple[str, str, str]]) -> Path:
    """A minimal notes-shaped acceptance suite. `rows` is (id, mark, extra)."""
    docs = tmp_path / "docs"
    (docs / "tests" / "acceptance").mkdir(parents=True)
    for num, (tid, mark, extra) in enumerate(rows, start=1):
        (docs / "tests" / "acceptance" / f"{tid}.md").write_text(
            f'---\ntype: "[[test]]"\nid: {tid}\ntitle: "Check {num}"\n'
            f'level: acceptance\nstatus: active\ntier: 1\n'
            f'number: "1.1.{num}0"\narea: "Area"\nmark: {mark}\n{extra}---\n\n'
            f"# Check {num}\n",
            encoding="utf-8",
        )
    return docs


def _tier_label(docs: Path) -> str:
    from project_os_cockpit.index import Index
    for g in cockpit._tests_groups(Index.build(docs)):
        if str(g.get("key", "")).startswith("tier"):
            return str(g["label"])
    raise AssertionError("no tier group")


def test_the_tracking_line_counts_re_runs_and_stale_ticks_separately() -> None:
    """TASK-0509, on synthetic data **because the corpus cannot exercise it.**

    Edwin: *"it would be nice to show a tracking line how many tsts have been
    completed and how many tests will need to be rerun."*

    Two different things mean "needs re-run" and the tracking line counts them
    apart. `mark: rerun` is the explicit act — the tick was cleared and the
    change named. `stale` is a tick still standing over evidence the record
    says was overtaken.

    **Neither exists in any live repo right now**: `your-trainer` carries 0 of
    each, because the 54 hand-written `RE-RUN` annotations were deliberately
    cleared. So both halves of this feature would ship never having run, which
    is how the `tier["stale"]` version of this line — a key that payload does
    not have — nearly shipped as a clause that could never fire.
    """
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        docs = _suite_repo(Path(td), [
            ("TST-0001", "done", ""),
            ("TST-0002", "done", ""),
            ("TST-0003", "rerun", ""),
            ("TST-0004", "todo", ""),
            ("TST-0005", "done",
             'invalidated_by:\n  change: "TASK-0999"\n  reason: "the API moved"\n'),
        ])
        label = _tier_label(docs)

    assert "1 need re-check" in label, label  # ADR-0039: no *run* in the UI
    assert "1 stale" in label, (
        f"the stale tick is not counted: {label!r}. It is a tick standing over "
        "evidence the record says was overtaken — neither walked nor owed, and "
        "the larger of the two populations in practice"
    )
    # **2, not 1** — the `rerun` row counts here as well as under its own
    # heading, because a check whose tick was cleared is a check somebody has
    # outstanding. Asserted deliberately rather than adjusted to match: the
    # first version of this expected 1, which would have meant a re-run row
    # silently missing from the count of outstanding work.
    #
    # **And 5, not 4** — a stale tick is still DONE and stays in the
    # denominator. What is untrue about it is that its evidence holds, which
    # is why it is reported beside the count rather than added to it.
    #
    # ISS-0241 replaced `3/5 completed · 2 todo` here. The two were one fact:
    # `unchecked` is `total - checked - reconciled` by construction, so the
    # pair could not disagree under any input and the second said nothing the
    # first had not. `outstanding` is Edwin's word for the half that survives.
    assert "2 of 5 outstanding" in label, label
    assert "completed" not in label, (
        f"the derived half is back: {label!r}. A head that prints both the "
        "completed fraction and the outstanding count prints one number twice."
    )
    assert "todo" not in label, (
        f"`todo` is not the word (ISS-0241, Edwin): {label!r}"
    )


def test_no_nav_payload_field_is_sent_and_never_drawn() -> None:
    """**The class, not the instance** ([[ISS-0225]]).

    `TASK-0550` put a surface's progress in `subtitle`, which `buildNavRow`
    documents as *"deliberately NOT rendered"*. It was computed per surface,
    serialised, sent, and dropped — and every test passed, because every test
    asserted the payload.

    Nothing anywhere failed when the server sent a field no renderer read.
    This is that check: every key the nav emits on an item must appear in
    `buildNavRow`'s source, or it is data nobody will ever see.
    """
    from pathlib import Path as _P

    #: **The whole renderer, not just `buildNavRow`.** A key another row
    #: builder or the palette reads is not dropped on the floor; the claim
    #: here is that nothing is sent which NOTHING reads.
    src = (_P(__file__).resolve().parents[1] / "desktop" / "src" / "renderer"
           / "renderer.ts").read_text()

    emitted: set[str] = set()
    for group in nav_payload(Index.build(REPO_DOCS), "tests")["groups"]:
        for item in group.get("items") or []:
            emitted |= set(item)
            for kid in item.get("items") or []:
                emitted |= set(kid)

    #: `subtitle` is the one key deliberately dropped, and the docstring says
    #: so. Named here rather than exempted by absence, because an exemption
    #: nobody can see is how the next one gets added.
    known_unread = {
        #: Documented in `buildNavRow` as never rendered — the left pane is a
        #: selection list, not a place for summaries.
        "subtitle",
        #: **Found by this guard on its first run, and pre-existing.**
        #: `ISS-0197` added it so a row could say *"60 of 107 proven"* rather
        #: than leaving an abandoned walk indistinguishable from one nobody
        #: started — and no renderer ever read it. Named here rather than
        #: deleted, because the sentence it was added for is still worth
        #: saying and the fix is to draw it, not to stop sending it
        #: ([[ISS-0229]]).
        "steps_proven",
    }
    unread = {k for k in emitted - known_unread if k not in src}
    assert not unread, (
        f"the nav sends {sorted(unread)} and buildNavRow reads none of them — "
        "data computed, serialised and dropped on the floor")


def test_a_surface_ref_is_an_issue_or_nothing() -> None:
    """[[ISS-0235]]: `covers:` is what a check verifies, not what the surface is.

    `_surface_ref` resolved any ref every check in a surface shared — and for
    Tier 1 that is the `FEAT-*` they all cover, so `Profile Management`
    rendered as *"User Management"*. The renderer substitutes `ref_title` for
    the title, so a non-issue ref silently renames the surface.

    **Asserted across every reachable repo**, because this was invisible in
    the one it was written in: `project-os-cockpit`'s Tier 1 areas span
    several features, so no ref is shared and the intersection is empty. It
    was live in `your-trainer` from the first commit.
    """
    from pathlib import Path as _P

    fleet = _P.home() / "Dev" / "repos"
    seen = 0
    for repo in ("project-os-cockpit", "your-trainer", "your-sudoku"):
        docs = fleet / repo / "docs"
        if not docs.is_dir():
            continue
        for group in nav_payload(Index.build(docs), "tests")["groups"]:
            if not str(group["key"]).startswith("tier"):
                continue
            for row in group.get("items") or []:
                seen += 1
                ref = row.get("ref")
                assert ref is None or str(ref).startswith("ISS-"), (
                    f"{repo}: surface {row['title']!r} carries {ref} — a "
                    "surface IS an issue or it is nothing; a feature is what "
                    "its checks cover")
    assert seen > 20, "no surfaces reachable — this guard would pass vacuously"


def test_the_nav_leads_with_what_is_owed() -> None:
    """[[TASK-0556]]: surfaces by percentage incomplete, checks incomplete first.

    Asserted across every reachable repo — the last three defects here were
    each invisible in the one they were written in ([[ISS-0219]],
    [[ISS-0221]], [[ISS-0235]]).
    """
    from pathlib import Path as _P

    fleet = _P.home() / "Dev" / "repos"
    seen = 0
    for repo in ("project-os-cockpit", "your-trainer", "your-sudoku"):
        docs = fleet / repo / "docs"
        if not docs.is_dir():
            continue
        for group in nav_payload(Index.build(docs), "tests")["groups"]:
            if not str(group["key"]).startswith("tier"):
                continue
            rows = group.get("items") or []
            seen += len(rows)
            pcts = [r["progress"]["pct"] for r in rows]
            assert pcts == sorted(pcts), (
                f"{repo}/{group['key']}: surfaces are not led by what is "
                f"owed — {pcts}")
            for row in rows:
                #: A check with no mark is owed; one with a clearing mark is
                #: not. The bands must not interleave.
                bands = [bool(k.get("mark")) and k["mark"] in
                         {"pass", "partial", "na", "excused"}
                         for k in row.get("items") or []]
                assert bands == sorted(bands), (
                    f"{repo}: {row['title']!r} interleaves settled checks "
                    "with owed ones")
    assert seen > 20, "no surfaces reachable — this guard would pass vacuously"
    #: **The child order is NOT asserted here**, and that is deliberate.
    #: Measured: **zero** surfaces in the fleet mix settled and owed checks —
    #: only this repo has a ledger and all 34 of its checks pass, while the
    #: other two have no marks at all. So a corpus assertion about child order
    #: would agree with any implementation, and a mutant removing the sort
    #: survived exactly that. It is proved on constructed input instead, in
    #: `test_incomplete_checks_sort_first_whatever_their_ids`.


def test_incomplete_checks_sort_first_whatever_their_ids() -> None:
    """The child order, on constructed input ([[TASK-0556]]).

    **The corpus cannot prove this.** Every surface in the fleet that mixes
    settled and owed checks happens to carry them in an order the id sort
    already produces — so removing the child sort entirely left
    `test_the_nav_leads_with_what_is_owed` green. A guard that only ever sees
    data which agrees with it is not a guard.

    So this constructs the case the corpus lacks: a settled check with a LOW
    id and an owed one with a high id, where id order and owed-first order
    disagree.
    """
    from project_os_cockpit import cockpit

    items = [
        {"id": "TST-0001", "number": "TST-0001", "name": "settled first",
         "checked": True, "area": "A", "refs": ()},
        {"id": "TST-0009", "number": "TST-0009", "name": "owed last",
         "checked": False, "area": "A", "refs": ()},
        {"id": "TST-0005", "number": "TST-0005", "name": "stale tick",
         "checked": True, "stale": True, "area": "A", "refs": ()},
    ]
    rows = cockpit._surface_rows(items, "~checks", 1)
    assert [k["id"] for k in rows[0]["items"]] == [
        "TST-0005", "TST-0009", "TST-0001"], (
        "owed first, then id order inside each band — and a STALE tick is "
        "owed, because it stands over evidence a change overtook")


def test_the_section_head_prints_no_number_the_others_already_give() -> None:
    """**One fact, one number** ([[ISS-0241]]).

    The head carried `{checked}/{total} completed` and `{unchecked} todo`
    side by side. `unchecked` is `total - checked - reconciled` *by
    construction*, so no corpus, no mark and no migration could ever make the
    two disagree — the second number was the first one subtracted and printed
    again, for the whole of its life.

    Guarded on the DERIVED value rather than on the wording, because wording
    is what a later edit changes. The suite below is built so that `checked`
    (12) appears nowhere else it could legitimately come from: the head may
    say 3 and 15, and if `12` is on it, the arithmetic has come back.
    """
    import tempfile
    rows = [(f"TST-{n:04d}", "done", "") for n in range(1, 13)]
    rows += [(f"TST-{n:04d}", "todo", "") for n in range(13, 16)]
    with tempfile.TemporaryDirectory() as td:
        label = _tier_label(_suite_repo(Path(td), rows))

    assert "3 of 15 outstanding" in label, label
    assert "12" not in label, (
        f"the completed count is derivable and back on the head: {label!r}. "
        "12 is 15 - 3; the head already carries both."
    )


def test_a_finished_section_says_so_rather_than_printing_a_zero() -> None:
    """`all 27 done`, not `0 of 27 outstanding` ([[ISS-0241]]).

    A zero is a sentence about the absence of work. The reader of a finished
    section wants the fact, and it is the one state where the total alone is
    the entire answer.
    """
    import tempfile
    rows = [(f"TST-{n:04d}", "done", "") for n in range(1, 5)]
    with tempfile.TemporaryDirectory() as td:
        label = _tier_label(_suite_repo(Path(td), rows))

    assert "all 4 done" in label, label
    assert "outstanding" not in label, (
        f"a finished section is reporting an empty obligation: {label!r}"
    )


def test_an_automated_head_claims_no_ci_execution() -> None:
    """**The count, and nothing about who ran it** ([[ISS-0241]]).

    This head said `{total} executed by CI`, derived from `command:` being
    present and from no observed run anywhere. Measured in `your-trainer` at
    HEAD on 2026-08-20: all 89 automated acceptance checks carry
    `evidence: []` and an empty `verdict_date`, **nine of them sit at
    `mark: todo`**, and no workflow in that repo executes them as checks —
    `android-tests.yml` runs the underlying gradle tests, and nothing maps a
    result back onto a note.

    So the phrase told a reader 89 checks were in hand over a record holding
    no result for any of them. [[ISS-0237]] inverted: that one removed a false
    obligation, and its fix left a false assurance standing in its place.

    The word `automated` does not appear either — the section is already
    called *Automated tests*, and saying it twice is what [[ISS-0089]] took
    off the group heads.
    """
    import tempfile
    from project_os_cockpit.index import Index

    cmd = 'command: "pytest -q"\n'
    rows = [("TST-0001", "done", cmd), ("TST-0002", "todo", cmd)]
    with tempfile.TemporaryDirectory() as td:
        docs = _suite_repo(Path(td), rows)
        groups = {str(g.get("key")): g for g in cockpit._tests_groups(Index.build(docs))}

    head = str(groups["tier3"]["label"])
    assert head == "Automated tests · 2", head
    assert "CI" not in head, head
    #: The obligation vocabulary must not reach this head at all: none of these
    #: words describes a list no person is progressing through (ADR-0039).
    for owed in ("outstanding", "completed", "todo", "done"):
        assert owed not in head.lower(), (owed, head)


def test_a_count_bearing_head_suppresses_the_trailing_row_count() -> None:
    """**Two numbers, two populations, adjacent** ([[ISS-0241]]).

    The label counts CHECKS; the front ends append `groupHeadSummary`, which
    counts the group's nav ROWS — area surfaces here. On `your-trainer` that
    put `361/406 completed` next to `50 · 1 done`: eight times apart, both
    readable as *how many tests are in here*, with nothing on screen saying
    which was which.

    Suppressed by a FLAG from the server, not by either client sniffing its
    own label. For a phase, feature or task group the trailing count is the
    only count the head has, and inferring the rule from the text would take
    it away from them the first time one of those labels happened to contain a
    digit.
    """
    import tempfile
    from project_os_cockpit.index import Index

    rows = [(f"TST-{n:04d}", "done", "") for n in range(1, 4)]
    with tempfile.TemporaryDirectory() as td:
        groups = cockpit._tests_groups(Index.build(_suite_repo(Path(td), rows)))

    counted = [g for g in groups if str(g.get("key", "")).startswith("tier")]
    assert counted, "no section to check"
    for g in counted:
        assert g.get("head_counts") is True, (g.get("key"), g.get("label"))

    #: **And it is not nav-wide.** A head whose label carries no count keeps
    #: its trailing summary; this is the half of the change that a later
    #: simplification is most likely to flatten.
    for g in groups:
        if not str(g.get("key", "")).startswith("tier"):
            assert not g.get("head_counts"), (g.get("key"), g.get("label"))


def test_both_front_doors_read_head_counts() -> None:
    """A flag the server sends and neither client reads is a flag that does
    nothing — the [[ISS-0225]] defect, at group level rather than row level.

    Asserted against both renderers' source because this repo has two front
    doors ([[PHASE-029]]) and the browser one has shipped a suppression the
    desktop one did not have before.
    """
    from pathlib import Path as _P

    root = _P(__file__).resolve().parents[1]
    for rel in ("src/project_os_cockpit/static/cockpit.js",
                "desktop/src/renderer/renderer.ts"):
        src = (root / rel).read_text(encoding="utf-8")
        assert "head_counts" in src, (
            f"{rel} never reads `head_counts`, so the count-bearing heads "
            "still print a second, different-population number there."
        )


def _groups(docs: Path) -> dict[str, dict]:
    from project_os_cockpit.index import Index
    return {str(g.get("key")): g for g in cockpit._tests_groups(Index.build(docs))}


def _merged_test(docs: Path, tid: str, status: str, extra: str = "") -> None:
    """A non-acceptance test that lands IN a derived section rather than in
    `Needs you`.

    **Its subject has to exist and be terminal.** Without that the in-flight
    rule (ADR-0028) leaves the obligation live, the row is routed to
    `Needs you`, and it never reaches the section whose head this is about —
    which is what the first version of these fixtures did, silently: the
    assertions failed against `all 4 done` because the `ready` row was in a
    different group entirely. It is also the real corpus's shape: this repo's
    three `ready` merged rows are quiet, not owed.
    """
    (docs / "features" / "f").mkdir(parents=True, exist_ok=True)
    (docs / "features" / "f" / "FEAT-0001-Subject.md").write_text(
        '---\ntype: "[[feature]]"\nid: FEAT-0001\ntitle: "Subject"\n'
        'status: done\n---\n\n# Subject\n', encoding="utf-8")
    (docs / "tests").mkdir(exist_ok=True)
    (docs / "tests" / f"{tid}.md").write_text(
        f'---\ntype: "[[test]]"\nid: {tid}\ntitle: "Merged {tid}"\n'
        f'status: {status}\ncovers: ["[[FEAT-0001]]"]\n{extra}---\n\n# Merged\n',
        encoding="utf-8")


def test_the_section_head_counts_the_rows_merged_into_it() -> None:
    """**The head counts what the section HOLDS** ([[ISS-0242]]).

    [[ADR-0039]] requires one section per name, so the non-acceptance `TST-*`
    rows are **merged** into the derived sections rather than emitted as a
    second group under the same label. The head was computed before that
    merge, so every merged row was invisible to it.

    Measured on this repo at the time of the fix: Feature tests counted 27 and
    held 32, and the head read **`all 27 done`** while three of the five
    merged rows sat at `ready`. A head asserting everything is finished, over
    a group holding three things that are not, is [[ISS-0241]]'s defect
    arriving through a second door.

    Built on synthetic input rather than the corpus, so the numbers cannot
    drift out from under the assertion.
    """
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        docs = _suite_repo(Path(td), [(f"TST-{n:04d}", "done", "") for n in range(1, 4)])
        #: Two non-acceptance tests in the same section: one finished, one not.
        _merged_test(docs, "TST-0900", "passing")
        _merged_test(docs, "TST-0901", "ready")
        label = str(_groups(docs)["tier1"]["label"])

    #: 3 checks + 2 merged = 5, and the `ready` one is outstanding.
    assert "1 of 5 outstanding" in label, label
    assert "all 3 done" not in label, (
        f"the head is still counting only the acceptance half: {label!r}"
    )


def test_a_ready_test_is_outstanding_not_done() -> None:
    """**`statuses.is_completed`, not the row's `owed` flag** ([[ISS-0242]]).

    The first cut of the merge fix read outstanding off `progress.done`, which
    `_test_as_surface` derives from `owed` — the obligations registry's
    question, *does this need a person right now* ([[ADR-0027]]). That answers
    `False` for a test at `ready`, so the head still printed `all 32 done`
    over three tests nobody has got passing.

    The head asks the narrower question the whole view is about: **is this
    finished.** Guarded directly, because the two predicates agree on every
    row of this repo's corpus except the ones that matter.
    """
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        docs = _suite_repo(Path(td), [("TST-0001", "done", "")])
        _merged_test(docs, "TST-0902", "ready")
        label = str(_groups(docs)["tier1"]["label"])

    assert "1 of 2 outstanding" in label, label
    assert "done" not in label, (
        f"a `ready` test is being reported as finished: {label!r}"
    )


def test_a_section_with_no_acceptance_checks_still_gets_a_section_head() -> None:
    """**The answer to Edwin's question** ([[ISS-0242]]): *"Why does automated
    tests look different in this project then on the your-trainer project?"*

    Because this repo's suite holds no automated acceptance checks at all, so
    no host was emitted for that section and the group fell through with a
    bare label — its count relegated to the trailing summary, while every
    sibling carried one inline. The same section, the same name, a different
    head, decided by whether the repo happens to hold a check of that kind.

    `Needs you`, `Broken command` and `Retired` keep their trailing summary
    deliberately — they are cross-cutting state groups rather than sections of
    the suite, and [[ISS-0241]] left them alone on purpose. Asserted here so a
    later sweep does not "make them consistent".
    """
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        docs = _suite_repo(Path(td), [("TST-0001", "done", "")])
        (docs / "tests").mkdir(exist_ok=True)
        for tid in ("TST-0910", "TST-0911"):
            (docs / "tests" / f"{tid}.md").write_text(
                f'---\ntype: "[[test]]"\nid: {tid}\ntitle: "Auto {tid}"\n'
                f'status: active\ncommand: "pytest -q"\n---\n\n# Auto\n',
                encoding="utf-8")
        groups = _groups(docs)

    auto = groups["automated"]
    assert str(auto["label"]) == "Automated tests · 2", auto["label"]
    assert auto.get("head_counts") is True, auto
    #: No obligation vocabulary on an automated head (ADR-0039), even though
    #: both rows are `active` and therefore "not completed".
    for owed in ("outstanding", "done", "todo"):
        assert owed not in str(auto["label"]).lower(), (owed, auto["label"])


def test_the_head_scaffolding_never_reaches_a_client() -> None:
    """`_head` carries the numbers so the merge can rebuild the label. A key
    the server sends and no renderer reads is [[ISS-0225]] exactly, so it is
    popped — asserted rather than trusted, because it is invisible in the UI
    either way.
    """
    from project_os_cockpit.index import Index

    for g in cockpit._tests_groups(Index.build(REPO_DOCS)):
        assert "_head" not in g, g.get("key")
        assert "_records" not in g, g.get("key")


#: The desktop renderer is TypeScript and these are source-level guards, the
#: same shape `test_no_nav_payload_field_is_sent_and_never_drawn` uses. They
#: are deliberately anchored on the DECISION rather than on formatting: each
#: asserts a thing that must not exist, so a reformat cannot satisfy them and
#: a re-introduction cannot hide behind one.
_RENDERER = Path(__file__).resolve().parents[1] / "desktop/src/renderer/renderer.ts"


def test_no_gate_row_draws_a_mark() -> None:
    """[[ISS-0244]]. Edwin: *"just show them as a list of tst links like the
    features below."*

    `gateMark` is **deleted, not left unreferenced** — the rule this file
    already applied to `markGateRow`: *a live-looking helper is how the next
    caller re-acquires the behaviour a decision just removed.* [[ADR-0035]]
    took the click away after [[ISS-0210]] found sixty live marks on the page
    whose purpose is to report a release is not ready, and the glyph that
    survived was identical on every row of the four unsettled lists.
    """
    src = _RENDERER.read_text(encoding="utf-8")
    assert "function gateMark" not in src, (
        "gateMark is back. It draws a token that is uniform on every row of "
        "Blocking / New / Chronic / Regressed, because those rows are "
        "unsettled by construction."
    )
    assert "gateMark(" not in src, "a caller is drawing the gate mark again"
    #: Where the mark VARIES it survives as a word, on those two groups only.
    assert "withMark" in src, "the Quiet / Stale distinction has been dropped"
    assert src.count("withMark: true") == 2, (
        "withMark belongs to exactly two groups — Quiet and Stale evidence. "
        "A stale row is TICKED, which is the whole of what makes it stale; "
        "the four unsettled lists have nothing to distinguish."
    )


def test_the_gate_row_id_is_typed_like_a_feature_row() -> None:
    """The features row's own treatment, which is the shape Edwin pointed at
    ([[ISS-0244]]). `item.number` already resolves to `TST-0044` wherever a
    check carries no positional `number:` — the [[ISS-0219]] fallback — so the
    id on screen is the note's and the row only needed to look like one.
    """
    src = _RENDERER.read_text(encoding="utf-8")
    i = src.index("function gateGroup")
    body = src[i:i + 4000]
    assert "'scoped-row-id mono ov-typed'" in body, body[:200]
    assert "n.dataset.type = 'test'" in body


def test_the_command_is_not_in_the_checkbox_slot() -> None:
    """[[ISS-0243]]. Edwin: *"this details page shows the command as one of the
    first list items, this doesn't have enough space there; if we show the
    command then it should be underneath the description instead."*

    Worse than cramped: the slot was `max-width: 22ch` with an ellipsis, and
    **all 89 of `your-trainer`'s commands begin `cd android && ./gradlew`** —
    one distinct value across the entire page, with the discriminating tail
    exactly what the ellipsis ate.
    """
    src = _RENDERER.read_text(encoding="utf-8")
    i = src.index("function buildCheckRow")
    body = src[i:i + 6000]
    assert "row.appendChild(cmd)" not in body, (
        "the command is back in the row's leading slot, where 89 rows render "
        "the same 22 characters"
    )
    assert "body.appendChild(cmd)" in body, "the command is not under the description"
    #: And the CSS must not re-clip it — the tail is the identifying part.
    css = (Path(__file__).resolve().parents[1]
           / "desktop/src/renderer/renderer.css").read_text(encoding="utf-8")
    j = css.index(".checks-row.is-automated .checks-row-command")
    rule = css[j:css.index("}", j)]
    assert "max-width: 22ch" not in rule, rule
    assert "text-overflow: ellipsis" not in rule, rule


def test_an_automated_area_shows_no_completion_percentage() -> None:
    """[[ISS-0243]]. `checkPercent` is a person's progress through a list, and
    nobody is progressing through one a machine executes ([[ADR-0039]]).

    It ran regardless of `manual`, so `your-trainer`'s automated page read
    **90% complete across 15 areas** over 89 checks carrying `evidence: []`
    and an empty `verdict_date` — no recorded result for any of them, nine at
    `mark: todo`. [[ISS-0241]]'s false assurance, one surface down, wearing a
    number instead of a phrase.
    """
    src = _RENDERER.read_text(encoding="utf-8")
    i = src.index("for (const area of areas)")
    body = src[i:i + 2500]
    assert "checkPercent(area.items)" in body, "the percentage vanished entirely"
    j = body.index("checkPercent(area.items)")
    guard = body[max(0, j - 400):j]
    assert "if (manual)" in guard, (
        "checkPercent is not guarded on `manual` — an automated surface is "
        f"reporting a completion figure again: {guard[-200:]!r}"
    )


def test_no_group_asserts_a_pass_for_a_status_it_does_not_recognise() -> None:
    """[[ISS-0212]]: *"a retired note is reported as verified."*

    `_tests_groups` used to bucket by a chain of `elif`s ending in
    `else: verified`, so `retired` — matching nothing above it — fell into the
    group whose label makes the strongest possible claim: **this was checked
    and it passed.** Three retired documents in `your-trainer` landed there: a
    checklist, a test list and a **run plan**, none of which is a test at all.

    Two properties, and the second is why this issue needs no nav-level
    fail-loud group:

    1. There is no group that asserts a pass. `retired` routes to a band that
       names what it is, and the `else` is `Feature tests` — which claims
       nothing about a verdict.
    2. **An unrecognised status cannot reach a committed corpus.** `STATUS-VALUE`
       errors on any value outside the type's allowed set, at pre-commit and in
       CI. A group for the unrecognised case would be a second, weaker copy of
       a check that already fails the commit — and a group nobody may notice is
       exactly the quiet this issue objects to.
    """
    import tempfile
    from project_os_cockpit.index import Index

    with tempfile.TemporaryDirectory() as td:
        docs = Path(td) / "docs"
        (docs / "tests").mkdir(parents=True)
        _merged_test(docs, "TST-0803", "passing")
        (docs / "tests" / "TST-0802.md").write_text(
            '---\ntype: "[[test]]"\nid: TST-0802\ntitle: "Retired doc"\n'
            'status: retired\n---\n\n# Retired\n', encoding="utf-8")
        groups = {str(g.get("key")): g for g in
                  cockpit._tests_groups(Index.build(docs))}

    assert "TST-0802" in [str(i.get("id")) for i in groups["retired"]["items"]]
    #: **Anchored, not substring-matched.** The first cut asserted `"verified"
    #: not in label` and failed on `Retired · no longer verified` — a label
    #: that says the opposite of what the guard was looking for. Third time in
    #: this sitting that an over-broad text match tripped on the words
    #: explaining the fix; the claim is that no group is HEADED `Verified`.
    import re as _re3
    for g in groups.values():
        label = str(g.get("label", ""))
        assert not _re3.match(r"\s*verified\b", label, _re3.I), (
            f"a group is headed `Verified` again — the one label that asserts "
            f"a check was run and passed: {label!r}"
        )

    #: The second property, asserted against the validator rather than assumed.
    from project_os_cockpit import validate_docs_bundled as _v
    legal = _v.ALLOWED_STATUS.get("test") or _v.ALLOWED_STATUS.get("[[test]]")
    assert legal, "no allowed-status table for a test note"
    assert "wibble" not in legal, "sanity: the bogus value must not be legal"
    assert "retired" in legal, (
        "`retired` is a legal test status — so the group it lands in is a "
        "statement about a real state, not a fallback"
    )
