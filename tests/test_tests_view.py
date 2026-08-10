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

    The view carries two populations (TASK-0373): the `TST-*` notes, and the
    acceptance suite's tier checkboxes. Everything in this section is about the
    first, so the tier groups are excluded here rather than by each assertion —
    a filter written once is one that cannot be forgotten in the next test.
    """
    out: list[dict] = []
    for group in groups:
        if str(group.get("key") or "").startswith("tier"):
            continue
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
    note_keys = {g["key"] for g in groups if not g["key"].startswith("tier")}
    assert note_keys < {"needs-run", "failing", "stale", "never", "verified"}


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

from project_os_cockpit import acceptance  # noqa: E402


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
    for tier in (1, 2, 3):
        assert f"tier{tier}" in groups, sorted(groups)
    suite = acceptance.load(REPO_DOCS)
    assert len(groups["tier1"]["items"]) == len(suite.tier(1))
    # The gating tiers ask something of a person while anything is unchecked;
    # Tier 3 never does — TESTING.md is explicit that it does not gate.
    assert groups["tier1"].get("needs_human") is True
    assert "needs_human" not in groups["tier3"]
    # And no note id appears in a tier group: one item, one home (ISS-0068).
    note_ids = {r.note_id for r in repo_index.notes_by_type("test")}
    tier_ids = {i["id"] for k, g in groups.items() if k.startswith("tier")
                for i in g["items"]}
    assert not (note_ids & tier_ids)


# ---- the gate ------------------------------------------------------------


def test_the_gate_fires_on_this_repo_right_now() -> None:
    """Not a fixture — the live suite.

    Every box was authored unchecked, because nothing in it has been walked.
    So the gate is genuinely blocking today, which is the first time that has
    been true in this project. If someone checks every Tier 1/2 box this will
    start passing for the right reason.
    """
    gate = acceptance.gate_payload(REPO_DOCS)
    assert gate["exists"] is True
    assert gate["blocked"] is True
    assert gate["blocking"], "blocked with nothing named is a bug in the gate"
    assert all(b["tier"] in (1, 2) for b in gate["blocking"])


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
    assert "**blocked** if any Tier 1 or Tier 2 test is unchecked" in contract


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


def test_a_proposed_adr_is_this_views_obligation(repo_index: Index) -> None:
    """From the registry, and marked on the row rather than counted twice.

    Measured 2026-08-10: the intent view owes exactly **one** thing, and it is
    `ADR-0010` — which is also one of the four decisions REL-0001 says to raise
    and stop on. A view whose obligation list has one member is easy to build
    wrong and impossible to notice, so the mark and the badge are asserted to
    be the same predicate.
    """
    groups = nav_payload(repo_index, mode="design")["groups"]
    owed = [i for g in groups for i in g["items"] if i.get("owed")]
    # The whole view's badge, standing documents included (TASK-0382) — the
    # assertion is that the marks and the count are one predicate, so it must
    # be taken over the whole view rather than one group of it.
    assert obligations.counts(repo_index)["intent"] == len(owed)
    assert all(i["owed_verb"] for i in owed)
    note_owed = {
        i["id"] for g in groups if g["key"] != "standing" for i in g["items"]
        if i.get("owed")
    }
    assert note_owed == {"ADR-0010"}, sorted(note_owed)


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
    assert groups[0]["key"] == "standing", [g["key"] for g in groups]
    listed = [i["id"] for i in groups[0]["items"]]
    assert listed == [d.name for d in standing.manifest(REPO_DOCS.parent)]
    # Each row says when it was last confirmed, or what is wrong with it.
    assert all(i["subtitle"] for i in groups[0]["items"])


def test_a_stub_is_owed_and_staleness_only_marks(repo_index: Index) -> None:
    """The line, and it is a decision rather than an oversight.

    Missing / ambiguous / stub are binary and one act clears each: write the
    document, delete the rival, fill in the template. Staleness returns by the
    calendar, so counting it is a badge that re-arms itself forever — the
    permanent nag this project has been bitten by twice (PHASE-015's close-out
    pill, `Doing · 44`). It still marks the row.

    Measured 2026-08-10: ARCHITECTURE and OWNERSHIP hold their templates;
    DESIGN and STYLEGUIDE were last confirmed 196 days ago.
    """
    rows = {i["id"]: i for i in
            nav_payload(repo_index, mode="design")["groups"][0]["items"]}
    assert rows["ARCHITECTURE"].get("owed") is True
    assert rows["ARCHITECTURE"]["owed_verb"] == "Confirm"
    # Stale marks — a status the navigator can sort and fold on — but does not
    # ask, so it carries no `owed`.
    assert rows["DESIGN"]["status"] == "review"
    assert "owed" not in rows["DESIGN"]
    assert "196 days" in rows["DESIGN"]["subtitle"]


def test_the_standing_obligation_reaches_the_intent_badge(repo_index: Index) -> None:
    """A panel that did not reach the badge would be decoration.

    The subject here is a **manifest entry**, not a note type — which is why
    `architecture`/`glossary`/`reference` still declare `NONE` in the
    type-keyed table and this is declared beside it. Both feed one count, so
    the badge stays the sum of what the view marks.
    """
    marked = sum(
        1 for g in nav_payload(repo_index, mode="design")["groups"]
        for i in g["items"] if i.get("owed")
    )
    assert obligations.counts(repo_index)["intent"] == marked
    assert obligations.standing_owed(REPO_DOCS) > 0, (
        "this repo no longer exercises the standing obligation — pick another "
        "assertion or the guard is vacuous"
    )
    # And the total the badges claim is still the sum of the badges.
    badges = obligations.badges_payload(repo_index)
    assert badges["total"] == sum(badges["views"].values())


def test_the_standing_set_is_not_a_second_obligation_list(repo_index: Index) -> None:
    """ISS-0068 forbids one obligation with two homes. The Library still shows
    these as *files* in a tree, which is a different question (ISS-0125 keeps
    that overlap deliberately) — but no other group in any view may mark them
    as owed."""
    standing_ids = {
        i["id"] for i in nav_payload(repo_index, mode="design")["groups"][0]["items"]
    }
    for mode in ("features", "issues", "tests", "library", "design"):
        for group in nav_payload(repo_index, mode=mode)["groups"]:
            if group["key"] == "standing":
                continue
            clashing = {
                i.get("id") for i in group["items"] if i.get("owed")
            } & standing_ids
            assert not clashing, f"{mode}/{group['key']} also marks {clashing}"
