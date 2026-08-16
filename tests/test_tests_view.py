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
    assert note_keys < {
        "needs-run",
        # ADR-0028: owed by its type, resting by its subject. It gets a group
        # rather than falling through to `Never verified` — that group is a
        # statement about evidence, and evidence is not why this one is quiet.
        "resting",
        "failing", "stale", "never", "verified",
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
    # A tier is on the view when it HOLDS something — `_acceptance_tier_groups`
    # skips an empty one, because `Tier 3 · 0` would say "nothing to verify"
    # about a project that verified nothing.
    #
    # Written as the rule rather than as today's answer, for the third time in
    # this file: the first version asserted all three tiers unconditionally,
    # which encoded "this repo always has Tier 3 items" — the opposite of what
    # Tier 3 is. It failed on 2026-08-14 when ISS-0143 retired the last two
    # after REL-0001, exactly as the contract requires, so honouring the rule
    # broke the test that was supposed to guard it.
    for tier in (1, 2, 3):
        present = f"tier{tier}" in groups
        assert present is bool(suite.tier(tier)), (tier, sorted(groups))
    assert len(groups["tier1"]["items"]) == len(suite.tier(1))
    # The gating tiers ask something of a person while anything is unsettled;
    # Tier 3 never does — TESTING.md is explicit that it does not gate. Stated
    # as the rule rather than as today's answer: the first version asserted
    # `needs_human is True` because everything was unwalked on the day it was
    # written, and it failed the moment the last box was ticked — reporting a
    # green gate as a broken test.
    for tier in (1, 2):
        owed = any(not i.settled for i in suite.tier(tier))
        assert groups[f"tier{tier}"].get("needs_human", False) is owed
    if "tier3" in groups:
        assert "needs_human" not in groups["tier3"]
    # And no note id appears in a tier group: one item, one home (ISS-0068).
    note_ids = {r.note_id for r in repo_index.notes_by_type("test")}
    tier_ids = {i["id"] for k, g in groups.items() if k.startswith("tier")
                for i in g["items"]}
    assert not (note_ids & tier_ids)


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
    assert "**blocked** if any Tier 1 or Tier 2 test is unchecked" in contract


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
        walked = sum(1 for i in items if i.checked)
        reconciled = sum(1 for i in items if i.reconciled)
        assert f"· {walked}/{len(items)}" in group["label"], group["label"]
        if reconciled:
            assert f"· {reconciled} reconciled" in group["label"], group["label"]
        else:
            assert "reconciled" not in group["label"], group["label"]
        by_number = {i.number: i for i in items}
        for row in group["items"]:
            item = by_number[row["id"]]
            expected = ("passing" if item.checked
                        else "reconciled" if item.reconciled else "ready")
            assert row["status"] == expected, (row["id"], row["status"])
    # The property the status buys, stated where it can fail: every value the
    # view emits is one the vocabulary knows, so no surface ranks it open.
    emitted = {row["status"] for k, g in groups.items() if k.startswith("tier")
               for row in g["items"]}
    assert emitted <= statuses.VOCABULARY, emitted - statuses.VOCABULARY
    assert "reconciled" in statuses.COMPLETED_STATUSES


def test_the_gate_states_its_local_extension_beside_the_contracts_rule() -> None:
    """The contract blocks on *unchecked* and names one escape: a documented
    release exception. This repo clears a check a second way — reconciliation —
    so the gate implements something looser than the sentence it quotes.

    Independent review's finding. The answer is not to paraphrase the contract
    (that is the drift `rule` exists to prevent) but to state the extension
    beside it, and to say plainly that the two are different things: a
    reconciled check is **not** a release exception.
    """
    gate = acceptance.gate_payload(REPO_DOCS)
    assert "unchecked" in gate["rule"]
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
        "total": 1, "unchecked": 0, "reconciled": 1,
    }
    tier1 = acceptance.payload(docs)["tiers"][0]
    assert (tier1["total"], tier1["checked"], tier1["reconciled"]) == (1, 0, 1)


@pytest.mark.parametrize("line", [
    "- [v] **A:** a typo, not a tick.",
    "- [-] **A:** another one.",
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
    text = REPO_DOCS.joinpath(acceptance.SUITE_REL).read_text(encoding="utf-8")
    # Only what sits under a tier heading — the preamble's own checkbox is
    # deliberately not a test (`test_nothing_above_the_first_tier_heading…`).
    body = re.split(r"(?m)^#\s+Tier\s+1\b", text, maxsplit=1)[1]
    # Fences are skipped on both sides: a `- [ ]` in a code block is an example
    # of a checkbox, not one. That is the single structural rule this counter
    # shares with the parser — it deliberately shares no *item* regex, which is
    # the independence that makes the comparison worth anything.
    raw, in_fence = 0, False
    for line in body.splitlines():
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            continue
        if not in_fence and re.match(r"^\s*[-*+]\s+\[", line):
            raw += 1
    parsed = len(acceptance.load(REPO_DOCS).items)
    assert parsed == raw, (
        f"{raw - parsed} checkbox line(s) in the suite are invisible to the "
        "parser — the gate is counting a smaller document than the one on disk"
    )


def test_a_clear_gate_says_which_of_its_tests_were_reconciled() -> None:
    """A clear band reading *"every Tier 1 and Tier 2 test is checked"* is
    false when one of them was settled by decision instead — and the clear
    state is where an overstatement costs most, because nobody looks twice at
    a green light. The band must have both sentences and pick on the count."""
    src = RENDERER.read_text(encoding="utf-8")
    band = re.search(r"async function mountReleaseGate\(\).*?\n\}", src, re.S).group(0)
    assert "reconciled" in band, "the clear band cannot distinguish walked from settled"
    assert "by reconciliation rather than by being walked" in band
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
    assert any(g["key"] == "verified" or g["key"] == "stale"
               for g in nav_payload(owed_corpus, mode="tests")["groups"])
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
