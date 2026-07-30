"""TST-0022 — surface ownership (PHASE-010).

REQ-0025 gates FEAT-0050 on a property nothing else in the toolchain
checks: that removing a type's Library group did not make the type
unreachable. The validator reads the corpus, not the UI. The existing
payload tests in ``test_cockpit.py`` assert group *shape*, which passes
just as happily on a group that lost its contents.

So these assert reachability **by count against the corpus**, not by
non-emptiness. That is the distinction that matters: ISS-0062's
type-based plan lookup returned 14 entirely convincing rows out of 33,
and every shape assertion in the suite passed on it.

What these do NOT cover, deliberately: whether a payload that reaches the
renderer is actually *drawn*. Both cockpit reachability bugs in PHASE-009
were renderer-side with correct payloads. TST-0022 carries manual steps
for that, and they are the honest part of the suite.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest

from project_os_cockpit import cockpit
from project_os_cockpit.cockpit import nav_payload
from project_os_cockpit.index import Index

FIXTURE = Path(__file__).parent / "fixtures" / "index_basic"
REPO_DOCS = Path(__file__).resolve().parent.parent / "docs"


@pytest.fixture()
def docs_root(tmp_path: Path) -> Path:
    target = tmp_path / "docs"
    shutil.copytree(FIXTURE, target)
    return target


@pytest.fixture()
def index(docs_root: Path) -> Index:
    return Index.build(docs_root)


@pytest.fixture(scope="module")
def repo_index() -> Index:
    """This repo's real corpus. Used only where the property under test is
    about the corpus itself (the untyped-plan population), which no
    synthetic fixture would honestly reproduce."""
    return Index.build(REPO_DOCS)


@pytest.fixture(scope="module")
def attention_index(tmp_path_factory) -> Index:
    """This repo's corpus plus one note in each attention state.

    The two guards below used to read `repo_index` directly and assert that
    *some* item needed attention. That made them fail the moment the project
    was healthy — which is the state the project is supposed to be in, and
    the state it reached the day PHASE-013 closed its last triage issue. A
    guard that goes red when the work is done is measuring the corpus, not
    the encoding.

    Injecting the states keeps what the guard was actually for (the payload
    can *reach* every DES-0004 state) while dropping the accidental
    dependency on the corpus being in trouble.
    """
    root = tmp_path_factory.mktemp("attention") / "docs"
    shutil.copytree(REPO_DOCS, root)
    phase = "[[PHASE-013-Fleet-Surfaces]]"
    (root / "issues" / "ISS-9001-Fixture-Triage.md").write_text(
        "---\ntype: \"[[issue]]\"\nid: ISS-9001\nstatus: triage\n"
        f"phase: \"{phase}\"\nseverity: low\n---\n# fixture\n",
        encoding="utf-8",
    )
    (root / "tests" / "TST-9001-Fixture-Ready.md").write_text(
        "---\ntype: \"[[test]]\"\nid: TST-9001\nstatus: ready\n"
        f"phase: \"{phase}\"\n---\n# fixture\n",
        encoding="utf-8",
    )
    return Index.build(root)


# ---- 1/2: plans reachable from their feature (ISS-0062) ----------------


def test_every_plan_on_disk_resolves_to_its_feature(repo_index: Index) -> None:
    """Asserted against a filesystem glob, never a literal.

    The corpus was 33 plans / 14 typed when ISS-0062 was filed, and 38/19
    once PHASE-010 added its own five features. A frozen number would
    fail on the next feature anyone creates, and the property is "every
    plan on disk resolves", not "there are N plans".

    A revert to ``notes_by_type("plan")`` fails here because the typed
    subset is strictly smaller than the glob.
    """
    on_disk = set(REPO_DOCS.glob("features/*/plan/PLAN.md"))
    resolved = {
        plan.path
        for record in repo_index.notes_by_type("feature")
        if (plan := cockpit._feature_plan(repo_index, record)) is not None
    }
    assert resolved == on_disk

    typed = {r.path for r in repo_index.notes_by_type("plan")}
    assert typed < on_disk, (
        "if every plan were typed this test could not distinguish the "
        "path-based lookup from the type-based one it replaced"
    )


def test_an_untyped_plan_still_gets_a_row(repo_index: Index) -> None:
    """The 19 files with no frontmatter at all. They were unreachable
    everywhere — `features/` is a DOC_TREE_EXCLUDED_ROOTS root, so they
    never joined the Docs tree either."""
    untyped = [
        p for p in REPO_DOCS.glob("features/*/plan/PLAN.md")
        if not p.read_text(encoding="utf-8").startswith("---")
    ]
    assert untyped, "corpus no longer has an untyped plan to prove this on"

    payload = nav_payload(repo_index, mode="features")
    rows = {
        item["url"]
        for group in payload["groups"]
        for feature in group["items"]
        for item in feature.get("children", [])
        if item.get("type") == "plan"
    }
    for path in untyped:
        rel = path.relative_to(REPO_DOCS.parent).as_posix()
        assert f"/{rel}" in rows, f"untyped plan unreachable: {rel}"


def test_a_feature_without_a_plan_gains_no_placeholder(index: Index) -> None:
    """No empty child, no placeholder row — a feature with no plan must
    render exactly as it did before FEAT-0046."""
    payload = nav_payload(index, mode="features")
    for group in payload["groups"]:
        for feature in group["items"]:
            for child in feature.get("children", []):
                assert child.get("url"), f"placeholder child on {feature['id']}"


# ---- 3: risks reachable from the Issues mode (FEAT-0047) --------------


def test_every_risk_appears_in_the_issues_mode(docs_root: Path) -> None:
    risks = docs_root / "risks"
    risks.mkdir(parents=True, exist_ok=True)
    for n, sev in enumerate(("high", "medium", "medium", "low"), start=1):
        (risks / f"RISK-000{n}-Sample.md").write_text(
            f'---\ntype: "[[risk]]"\nid: RISK-000{n}\ntitle: "Risk {n}"\n'
            f'status: open\nseverity: {sev}\n---\n# Risk {n}\n',
            encoding="utf-8",
        )
    fresh = Index.build(docs_root)
    payload = nav_payload(fresh, mode="issues")
    listed = {
        item["id"]
        for group in payload["groups"]
        for item in group["items"]
        if item.get("type") == "risk"
    }
    assert listed == {r.note_id for r in fresh.notes_by_type("risk")}


def test_risks_get_their_own_groups_not_the_issue_buckets(
    docs_root: Path,
) -> None:
    """Mixing risks into the severity buckets would make the Issues
    stat-tile count disagree with what the pane shows."""
    risks = docs_root / "risks"
    risks.mkdir(parents=True, exist_ok=True)
    (risks / "RISK-0001-Sample.md").write_text(
        '---\ntype: "[[risk]]"\nid: RISK-0001\ntitle: "Risk"\n'
        'status: open\nseverity: high\n---\n# Risk\n',
        encoding="utf-8",
    )
    fresh = Index.build(docs_root)
    payload = nav_payload(fresh, mode="issues")
    for group in payload["groups"]:
        types = {item.get("type") for item in group["items"]}
        assert len(types) <= 1, f"group {group['key']} mixes {types}"
        if "risk" in types:
            assert group["key"].startswith("risk:")


def test_a_corpus_with_no_risks_is_unchanged(index: Index) -> None:
    assert not list(index.notes_by_type("risk")), "fixture gained a risk"
    payload = nav_payload(index, mode="issues")
    assert not any(g["key"].startswith("risk:") for g in payload["groups"])


# ---- 4: changes reachable from the overview (FEAT-0048) ---------------


def test_the_changes_split_is_a_partition(repo_index: Index) -> None:
    """recent + buckets must equal the corpus. A change falling out of
    both would vanish from the only surface that lists it."""
    payload = cockpit.changes_payload(repo_index)
    seen = len(payload["recent"])
    for bucket in payload["buckets"]:
        seen += len(bucket["items"])
        for sub in bucket.get("subgroups", []):
            seen += len(sub["items"])
    assert seen == payload["total"] == len(list(repo_index.notes_by_type("change")))


# ---- 5/6: the review desk's registers (FEAT-0049) ---------------------


def test_the_tests_register_holds_the_whole_corpus(repo_index: Index) -> None:
    """The desk's `runs` group is gated to manual-and-`ready` — a queue
    slice. Both counts are asserted so collapsing one into the other
    fails rather than looking tidier."""
    payload = cockpit.review_queue_payload(repo_index)
    register = payload["registers"]["tests"]
    assert {t["id"] for t in register} == {
        r.note_id for r in repo_index.notes_by_type("test")
    }

    runs = next(g for g in payload["groups"] if g["key"] == "runs")
    assert len(runs["items"]) < len(register), (
        "the queue slice and the register must stay distinct"
    )


def test_the_reviewed_register_comes_from_note_frontmatter(
    repo_index: Index,
) -> None:
    """Not the store: `_MAX_REQUESTS = 200` trims oldest-first on every
    save, so a store-sourced register would silently lose its tail."""
    register = cockpit.review_queue_payload(repo_index)["registers"]["reviewed"]
    expected = {
        r.note_id or r.rel_path
        for r in repo_index.iter_records()
        if isinstance(r.frontmatter.get("review_verdict"), str)
        and r.frontmatter["review_verdict"].strip()
    }
    assert {r["id"] or r["rel"] for r in register} == expected
    assert register, "corpus has recorded verdicts; the register found none"


def test_an_empty_verdict_is_not_a_reviewed_item(docs_root: Path) -> None:
    """Six notes in this repo declare `review_verdict: ""`. An empty
    verdict is the absence of one — counting them would report more
    reviewed items than were reviewed, which is the unearned
    verification ADR-0010 exists to prevent.

    The opposite call from the missing-date case below, deliberately.
    """
    (docs_root / "CHG-20260101-Empty.md").write_text(
        '---\ntype: "[[change]]"\nid: CHG-20260101-Empty\ntitle: "Empty"\n'
        'status: merged\nreview_verdict: ""\n---\n# Empty\n',
        encoding="utf-8",
    )
    fresh = Index.build(docs_root)
    register = cockpit.review_queue_payload(fresh)["registers"]["reviewed"]
    assert "CHG-20260101-Empty" not in {r["id"] for r in register}


def test_a_verdict_without_a_date_still_lists(docs_root: Path) -> None:
    """A recorded verdict with incomplete metadata is a reviewed item —
    worth showing, sorted last. Dropping it would hide exactly the
    records worth chasing."""
    (docs_root / "CHG-20260101-Undated.md").write_text(
        '---\ntype: "[[change]]"\nid: CHG-20260101-Undated\ntitle: "Undated"\n'
        'status: merged\nreview_verdict: approved\n---\n# Undated\n',
        encoding="utf-8",
    )
    (docs_root / "CHG-20260102-Dated.md").write_text(
        '---\ntype: "[[change]]"\nid: CHG-20260102-Dated\ntitle: "Dated"\n'
        'status: merged\nreview_verdict: approved\n'
        'review_date: 2026-07-01\n---\n# Dated\n',
        encoding="utf-8",
    )
    fresh = Index.build(docs_root)
    register = cockpit.review_queue_payload(fresh)["registers"]["reviewed"]
    ids = [r["id"] for r in register]
    assert "CHG-20260101-Undated" in ids
    assert ids.index("CHG-20260102-Dated") < ids.index("CHG-20260101-Undated")


# ---- 7/8/9: the reduction itself (FEAT-0050) --------------------------


def test_library_is_pins_and_the_tree(repo_index: Index) -> None:
    payload = nav_payload(repo_index, mode="library", project_root=REPO_DOCS.parent)
    keys = {g["key"] for g in payload["groups"]}
    assert keys <= {"pinned", "docs-tree"}, sorted(keys)


def test_the_skip_set_is_not_derived_from_the_empty_tuple() -> None:
    """`_BY_TYPE_SKIP_IN_LIBRARY` used to be derived from
    ``LIBRARY_RARE_TYPES``. Emptying that tuple without rewriting the
    skip-set would let every canonical type clearing
    ``_BY_TYPE_MIN_COUNT`` reappear under a ``by-type:`` key — the
    reduction undone through the back door, with no test failing.
    """
    assert cockpit.LIBRARY_RARE_TYPES == ()
    for type_name in (
        "change", "adr", "decision", "release", "risk", "test",
        "workflow", "plan", "design",
    ):
        assert type_name in cockpit._BY_TYPE_SKIP_IN_LIBRARY, type_name


def test_workflows_browse_in_the_docs_tree(repo_index: Index) -> None:
    payload = nav_payload(repo_index, mode="library", project_root=REPO_DOCS.parent)
    tree = next(g for g in payload["groups"] if g["key"] == "docs-tree")
    labels = {sg["label"] for sg in tree.get("subgroups", [])}
    assert "workflows/" in labels, sorted(labels)


# ---- the record column's source (ISS-0065) ----------------------------


def test_decisions_have_a_payload_of_their_own(repo_index: Index) -> None:
    """The defect REQ-0025 was written to prevent, arriving from the one
    direction the gate did not check.

    The overview record column built its Decisions and Verification cards
    from `GET /api/cockpit/nav?mode=library`. Reducing that mode took the
    harvest from 149 items to 0, so both cards stopped being built —
    silently, because each sits behind a `length > 0` guard. And the
    reduction was justified *by* this column, which was circular: the
    column was that Library group, reshaped.

    So decisions get a payload that answers the question directly. A nav
    mode is a navigation surface; it is not an API for "what exists".
    """
    payload = cockpit.decisions_payload(repo_index)
    assert {d["id"] for d in payload["decisions"]} == {
        r.note_id for r in (
            *repo_index.notes_by_type("adr"),
            *repo_index.notes_by_type("decision"),
        )
    }
    assert payload["total"] > 0, "corpus has ADRs; the payload found none"

    # Every entry must be *openable*, not merely present. The renderer
    # drops rows with no `rel`, so a payload that returns ids and blank
    # rels empties the card exactly as ISS-0065 did — an id-only check
    # passed that mutation when it was tried.
    for d in payload["decisions"]:
        assert d["rel"], f"{d['id']} has no rel; the row would be dropped"
        assert (REPO_DOCS / d["rel"]).exists(), f"{d['rel']} does not resolve"


SERVER = (
    Path(__file__).resolve().parent.parent
    / "src" / "project_os_cockpit" / "server.py"
)


@pytest.mark.parametrize(
    "route", ["/api/cockpit/decisions", "/api/cockpit/review-queue"],
)
def test_the_record_columns_endpoints_exist_on_both_sides(route: str) -> None:
    """A cross-process contract with no guard, per the ISS-0065 re-review.

    The record column now depends on two HTTP paths spelled as string
    literals in two files in two languages. A typo on either side — or a
    renamed server route — empties a card silently, because every card
    sits behind a `length > 0` guard. That is ISS-0065's exact signature,
    reintroduced by its own fix in a new place.

    Nothing else in the suite compares the two spellings: the payload
    tests call `cockpit.*_payload()` directly and never touch a route, and
    the renderer tests read source without resolving what it fetches.
    """
    assert f'path == "{route}"' in SERVER.read_text(encoding="utf-8"), (
        f"server.py does not serve {route}"
    )
    assert route in _renderer_code(), f"no renderer fetch for {route}"


def test_the_decisions_route_answers_through_the_http_handler(
    tmp_path: Path,
) -> None:
    """The literal-matching test above still cannot catch a handler that
    is registered but broken, so this exercises the real dispatch path
    end to end against a live server on an ephemeral port.

    Deliberately not asserting contents — `test_decisions_have_a_payload_of_their_own`
    owns that. What this owns is "the route the renderer names actually
    returns decisions", which is the half that was missing.
    """
    import json
    import threading
    import urllib.request

    from project_os_cockpit.server import (
        DocsServer, _make_handler, _NoDNSThreadingHTTPServer,
    )

    shutil.copytree(FIXTURE, tmp_path / "docs")
    adr_dir = tmp_path / "docs" / "decisions"
    adr_dir.mkdir(parents=True, exist_ok=True)
    (adr_dir / "ADR-0099-Sample.md").write_text(
        '---\ntype: "[[adr]]"\nid: ADR-0099\ntitle: "Sample"\n'
        'status: accepted\n---\n# Sample\n',
        encoding="utf-8",
    )

    server = DocsServer(docs_root=tmp_path / "docs", bind="127.0.0.1", port=0)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0),
        _make_handler(
            server.docs_root, server.index, server.bus,
            cockpit_state=server.cockpit_state,
        ),
    )
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/api/cockpit/decisions", timeout=10,
        ) as resp:
            assert resp.status == 200
            body = json.load(resp)
        assert "ADR-0099" in {d["id"] for d in body["decisions"]}
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_the_record_column_does_not_harvest_a_nav_mode() -> None:
    """ISS-0065's root cause, asserted structurally.

    A count test cannot catch this: the payload was well-formed and the
    tests all passed. What was wrong was *where the renderer looked*, so
    that is what is pinned. `fillRecordColumn` must not source its cards
    from `fetchRecordNotes`, whose contract is "walk a nav payload and
    keep whatever has an id" — a shape that changes when a nav mode does.
    """
    fn = _renderer_code().split("async function fillRecordColumn(")[1]
    fn = fn.split("\n}")[0]
    assert "fetchRecordNotes" not in fn, (
        "the record column is harvesting a nav mode again (ISS-0065)"
    )
    assert "fetchDecisions()" in fn and "fetchTestsRegister()" in fn


def test_the_nav_harvest_helper_is_gone() -> None:
    """`fetchRecordNotes(mode)` — walk any nav payload, keep whatever has
    an id — is the abstraction that caused ISS-0065, not just a casualty.
    It let three callers depend on a nav mode's *contents*, which is a UI
    decision and free to change. It changed; two of the three stayed
    broken through a full review of the phase that broke them.

    Asserted on comment-stripped source, because the deletion is
    explained in a comment that names the function.
    """
    assert "fetchRecordNotes" not in _renderer_code()


def test_the_quick_palette_covers_every_type_bearing_mode() -> None:
    """The near-miss that had no test.

    `buildQuickCorpus` fetched `mode=library` alone, documented as "the
    broadest single fetch" — true until PHASE-010 reduced that mode, at
    which point Cmd+P would have silently narrowed to pins and loose
    files: a still-populated palette with half the corpus unfindable.
    That was caught by reading, not by a test, which is the same way
    ISS-0065 was missed.

    So the coverage claim is pinned. `library` alone is not enough, and
    the modes that carry the moved types must all be present.
    """
    code = _renderer_code()
    block = code.split("const QUICK_CORPUS_MODES = [")[1].split("]")[0]
    modes = set(re.findall(r"'([a-z]+)'", block))
    assert {"features", "tasks", "issues", "design", "library"} <= modes, modes
    # Changes and tests have no nav mode; they must be reached explicitly.
    corpus_fn = code.split("async function buildQuickCorpus(")[1].split("\n}\n")[0]
    assert "review-queue" in corpus_fn, "tests are not in the palette"
    assert "cockpit/changes" in corpus_fn, "changes are not in the palette"


# ---- the dead stat tiles (ISS-0063) -----------------------------------


RENDERER = (
    Path(__file__).resolve().parent.parent
    / "desktop" / "src" / "renderer" / "renderer.ts"
)


def _renderer_code() -> str:
    """The renderer with `//` comments stripped, whole-line and trailing.

    Needed because several of these assertions are "this call site no
    longer exists", and the reasons those call sites were removed are
    recorded in comments that name them. Matching raw source made three
    such assertions fail on their own explanations.

    Trailing comments are stripped too, after round three found that
    stripping only whole-line ones left a hole: a typo'd fetch followed by
    `// was /api/cockpit/decisions` on the same line satisfied the
    route-contract test. Contrived, but the fix is one line and a guard
    with a known bypass is the kind this suite otherwise avoids.

    `://` is skipped so URLs survive — the strings being asserted on are
    themselves URL paths, and a naive split would erase them.
    """
    out = []
    for line in RENDERER.read_text(encoding="utf-8").splitlines():
        search_from = 0
        while (idx := line.find("//", search_from)) != -1:
            if idx > 0 and line[idx - 1] == ":":   # part of `http://`
                search_from = idx + 2
                continue
            line = line[:idx]
            break
        out.append(line)
    return "\n".join(out)


def _stat_tile_call(label: str) -> str:
    """The `buildStatTile('<label>', …)` call, up to its closing paren.

    Tolerant of a newline between the paren and the label — the Reqs tile
    is written that way, and a matcher that missed it would have reported
    "no such tile" rather than "tile has no destination".
    """
    src = RENDERER.read_text(encoding="utf-8")
    match = re.search(rf"buildStatTile\(\s*'{label}'", src)
    assert match is not None, f"no buildStatTile call for {label!r}"
    start = match.start()
    depth = 0
    for i in range(start, len(src)):
        if src[i] == "(":
            depth += 1
        elif src[i] == ")":
            depth -= 1
            if depth == 0:
                return src[start:i + 1]
    raise AssertionError(f"unbalanced parens in the {label} tile call")


@pytest.mark.parametrize(
    ("label", "mode"), [("Risks", "issues"), ("Tests", "review")],
)
def test_the_dead_stat_tiles_gained_a_destination(label: str, mode: str) -> None:
    """`buildStatTile` renders a <button> only when passed a navMode.
    Risks and Tests were passed none, so they showed a count and
    navigated nowhere (ISS-0063) — indistinguishable on inspection from
    the three that worked, and only detectable by clicking."""
    assert f"'{mode}'" in _stat_tile_call(label)


# ---- desk section order and naming (ISS-0064) -------------------------


def test_only_one_desk_section_is_headed_reviewed() -> None:
    """TASK-0242 took the word `Reviewed` for its register without noticing
    the ADR-0007 tally already used it, leaving two sections a few rows
    apart both headed `Reviewed` with different counts — 1 (review
    interactions at the desk) against 62 (notes carrying a verdict).
    ISS-0064.

    Still asserted after TASK-0247 removed the tally: the collision is
    gone by subtraction now, and this keeps it gone if a future section
    reaches for the same word.
    """
    src = RENDERER.read_text(encoding="utf-8")
    headings = re.findall(r"textContent = `(\w+) · \$\{", src)
    assert headings.count("Reviewed") == 1, (
        f"expected exactly one Reviewed heading, found {headings}"
    )


def test_the_advisory_tally_is_gone_from_the_desk() -> None:
    """ADR-0007 settled on 2026-07-29 (stay advisory, permanently), so the
    instrument built to inform that decision has no consumer — TASK-0247.

    The *recording* deliberately survives: the store still stamps outcomes
    and the payload still carries them (asserted by
    `test_queue_reports_the_advisory_phase_tally`). Only the surface goes,
    so this checks the renderer and its stylesheet, not the payload.
    """
    src = RENDERER.read_text(encoding="utf-8")
    css = (RENDERER.parent / "renderer.css").read_text(encoding="utf-8")
    for dead in ("review-tally", "Outcomes · "):
        assert f"'{dead}'" not in src and f"`{dead}" not in src, dead
    # No dead rules left behind — a stylesheet keeping selectors for a
    # deleted block is how CSS becomes unreadable.
    assert ".review-tally {" not in css
    assert ".review-tally-row" not in css
    assert ".review-tally-note" not in css


def test_the_desk_pane_order_is_queue_reviewed_tests() -> None:
    """Both registers are appended at the tail of the same function, so
    the order is positional: a future addition appending in the obvious
    place reshuffles the pane without failing anything. That is exactly
    how ISS-0064 happened, so the order is pinned here.
    """
    src = RENDERER.read_text(encoding="utf-8")
    pane = src.split("function renderReviewQueuePane(")[1].split("\n}")[0]
    positions = {
        name: pane.index(name)
        for name in ("buildQueueRow", "buildReviewedRegister",
                     "buildTestsRegister")
    }
    assert (positions["buildQueueRow"]
            < positions["buildReviewedRegister"]
            < positions["buildTestsRegister"]), positions


def test_the_reqs_tile_stays_dead_on_purpose() -> None:
    """Out of scope for PHASE-010 and recorded as such: requirements nest
    under features, so the tile has no single destination. Asserted so
    the omission reads as a decision rather than an oversight."""
    call = _stat_tile_call("Reqs")
    assert not re.search(r",\s*'[a-z]+'\s*\)$", call.strip()), call


# ---- PHASE-012 / DES-0004: the square encoding -------------------------------


def test_every_des_0004_state_is_reachable(attention_index: Index) -> None:
    """The accepted encoding, asserted against the live corpus.

    A count test is the right shape here for the reason ISS-0062 taught: a
    payload that emits `state: null` for everything would render as today's
    two-state strip and pass any shape assertion.
    """
    data = cockpit.stats_payload(attention_index)
    items = []
    for ph in data["phases"]:
        for f in ph["features"]:
            items.append(f)
            items.extend(f["children"])
        items.extend(ph["loose"])

    states = {i.get("state") for i in items}
    for expected in ("delivered", "dropped", "deferred", "doing", "unproven"):
        assert expected in states, f"no item renders as {expected}"
    assert None in states, "nothing renders as plain not-started"

    # The dot composes with a fill rather than replacing one, and is rare by
    # design — triage/review/ready plus computed-blocked.
    assert 0 < sum(1 for i in items if i.get("attn")) < len(items) / 10


def test_tests_are_in_the_phase_strip(repo_index: Index) -> None:
    """`ready` tests get a dot, which needs them in the payload at all — they
    were absent, so DES-0004 could not have been implemented in CSS alone."""
    data = cockpit.stats_payload(repo_index)
    types = {
        i["type"]
        for ph in data["phases"]
        for i in [*ph["features"], *(c for f in ph["features"] for c in f["children"]), *ph["loose"]]
    }
    assert "test" in types, "tests are not in the phase strip"
    assert "risk" not in types, (
        "risks reached the strip — none carry a phase:, so this would mean "
        "they are all landing under Unphased (out of scope, DES-0004)"
    )


def test_blocked_is_computed_from_depends_not_from_a_status(
    docs_root: Path,
) -> None:
    """ISS-0071. The first version's docstring claimed a behavioural assertion
    its body never made — `def _has_unresolved_dependency(rec): return False`
    passed all 594 tests — and its source slice read the wrong function's body,
    so re-adding a blocked-status branch passed under a message saying it had
    not.

    Behavioural now: an unfinished item whose dependency is unresolved carries
    the dot; the same item whose dependency is done does not.
    """
    (docs_root / "features").mkdir(exist_ok=True)
    (docs_root / "features" / "FEAT-0600-Probe.md").write_text(
        '---\ntype: "[[feature]]"\nid: FEAT-0600\ntitle: "Probe"\n'
        'status: backlog\nphase: "[[PHASE-600]]"\n---\n# Probe\n',
        encoding="utf-8",
    )

    def write_blocker(status: str) -> None:
        (docs_root / "TASK-0601-Blocker.md").write_text(
            f'---\ntype: "[[task]]"\nid: TASK-0601\ntitle: "Blocker"\n'
            f'status: {status}\nphase: "[[PHASE-600]]"\n---\n# Blocker\n',
            encoding="utf-8",
        )

    (docs_root / "TASK-0600-Blocked.md").write_text(
        '---\ntype: "[[task]]"\nid: TASK-0600\ntitle: "Blocked"\n'
        'status: doing\nphase: "[[PHASE-600]]"\n'
        'depends: ["[[TASK-0601]]"]\n---\n# Blocked\n',
        encoding="utf-8",
    )

    def attn_of(note_id: str) -> bool:
        payload = cockpit.stats_payload(Index.build(docs_root))
        for ph in payload["phases"]:
            pool = [*ph["features"],
                    *(c for f in ph["features"] for c in f["children"]),
                    *ph["loose"]]
            for item in pool:
                if item.get("id") == note_id:
                    return bool(item.get("attn"))
        raise AssertionError(f"{note_id} is not in the payload at all")

    write_blocker("backlog")
    assert attn_of("TASK-0600"), (
        "an unfinished item with an unresolved `depends:` carries no dot"
    )
    # ...and it is still `doing`, so the dot composes with a fill rather than
    # replacing it — the property STATUSES.md requires.
    write_blocker("done")
    assert not attn_of("TASK-0600"), (
        "the blocker is done and the item still reads as blocked"
    )

    # A `status: blocked` must NOT be what drives it — that status is not in the
    # vocabulary and no note carries it.
    assert not [
        r for r in Index.build(docs_root).iter_records()
        if (r.status or "").strip().lower() == "blocked"
    ]

    # And the branch must not come back. This is a source check because a dead
    # branch is behaviourally INVISIBLE — nothing carries the status, so adding
    # `if status == "blocked"` changes no output and no behavioural test can
    # see it. The previous version claimed to catch this and sliced the wrong
    # function's body; slicing correctly is what makes the claim true.
    src = (Path(__file__).resolve().parent.parent
           / "src" / "project_os_cockpit" / "cockpit.py").read_text(encoding="utf-8")
    after = src[src.index("    def _needs_human("):]
    body = after[:after.index("\n    def ", 1)]
    # Narrowed: `statuses.BANDS["blocked"]` in here is CORRECT — that band holds
    # `failing` and `reopened`, which are real statuses (ISS-0071 gave them the
    # dot). What must not come back is comparing the status to the literal, the
    # dead branch STATUSES.md:59 forbids.
    for dead in ('== "blocked"', "== 'blocked'", 'status == "blocked"'):
        assert dead not in body, (
            f"_needs_human compares status to the `blocked` literal ({dead}); "
            "STATUSES.md:59 makes blocked-ness a `depends:` relationship, so "
            "that branch is dead code which only looks like a guard"
        )

def test_the_staleness_threshold_is_the_validators(repo_index: Index) -> None:
    """A cockpit that called a test stale at 30 days while the validator called
    it fresh at 89 would be a second vocabulary — the defect ISS-0024 and
    ISS-0069 are both about. DES-0004's first draft cited "9 stale tests" on a
    threshold nobody had adopted; at the real 90 there are none.
    """
    validator = (Path(__file__).resolve().parent.parent
                 / "tools" / "scripts" / "validate-docs.py").read_text(encoding="utf-8")
    m = re.search(r"^DEFAULT_STALENESS_DAYS = (\d+)", validator, re.M)
    assert m, "the validator no longer declares DEFAULT_STALENESS_DAYS"
    assert cockpit.DEFAULT_STALENESS_DAYS == int(m.group(1)), (
        f"cockpit says {cockpit.DEFAULT_STALENESS_DAYS}, validator says {m.group(1)}"
    )


def test_the_waiting_on_you_list_is_gone() -> None:
    """ISS-0068. Deleted, not emptied — and its helpers with it, including the
    dedup pass that existed only because two appenders raced."""
    code = _renderer_code()
    # Declarations, not bare names: `AttentionRow` is a substring of the live
    # and unrelated `buildAttentionRow` (the agent attention panel), and a
    # guard that fails on a neighbour's name is a guard nobody trusts.
    for gone in ("function buildWaitingOnYou", "function collectAttention",
                 "async function appendAsyncWaitingRows",
                 "function buildWaitingRow", "interface AttentionRow"):
        assert gone not in code, f"`{gone}` is back (ISS-0068)"
    assert "buildAttentionRow" in code, (
        "the agent attention panel's row builder went with it — different "
        "surface, unrelated to the retired overview section"
    )
    css = (RENDERER.parent / "renderer.css").read_text(encoding="utf-8")
    assert ".ov-waiting" not in css, "the retired section's CSS is back"


def test_the_phase_header_carries_what_squares_cannot(attention_index: Index) -> None:
    """A collapsed phase renders its squares with `offsetParent: null`, so
    without a header count the encoding LOSES what the list showed. And
    "all resolved, not closed" is a property of the phase, so no square holds it.
    """
    data = cockpit.stats_payload(attention_index)
    assert all("waiting" in ph and "unclosed" in ph for ph in data["phases"])
    assert any(ph["waiting"] for ph in data["phases"]), "no phase reports waiting"

    code = _renderer_code()
    assert "ov-phase-pill is-waiting" in code
    assert "ov-phase-pill is-unclosed" in code


def test_unclosed_uses_the_validators_own_gate() -> None:
    """ISS-0071. The first version of this test restated the implementation —
    `unclosed` *is* `all(state in RESOLVED_STATES)` and it asserted exactly
    that, so it could not fail and never read the validator. Reverting
    `unclosed` to its buggy first cut left it green.

    This compares the two tables directly, which is the thing that was wrong:
    the payload omitted `risk`, so a risk parked on a phase made the marker
    offer a close-out PHASE-CHILDREN would refuse.
    """
    validator = (Path(__file__).resolve().parent.parent
                 / "tools" / "scripts" / "validate-docs.py").read_text(encoding="utf-8")
    block = validator[validator.index("PHASE_RESOLVED = {"):]
    block = block[:block.index("\n}")]
    theirs = {
        m.group(1): {s.strip().strip('"') for s in m.group(2).split(",") if s.strip()}
        for m in re.finditer(r'"(\w+)": \{([^}]*)\}', block)
    }
    ours = {k: set(v) for k, v in cockpit.PHASE_RESOLVED.items()}
    assert ours == theirs, (
        f"the close-out marker's gate has drifted from the validator's.\n"
        f"cockpit: {ours}\nvalidator: {theirs}"
    )

    m = re.search(r"^CLOSED_PHASE_STATUSES = \(([^)]*)\)", validator, re.M)
    assert m
    assert cockpit.CLOSED_PHASE_STATUSES == {
        s.strip().strip('"') for s in m.group(1).split(",") if s.strip()
    }


def test_an_unresolved_child_of_any_policed_type_blocks_close_out(
    docs_root: Path,
) -> None:
    """Behavioural, per type, including `risk` — the omission ISS-0071 found.

    Builds a phase whose every note is resolved, asserts it is offered for
    close-out, then parks one unresolved note of each policed type on it and
    asserts the offer is withdrawn. A test that only checked the happy corpus
    is what let the risk case through.
    """
    phase_dir = docs_root / "phases"
    phase_dir.mkdir(parents=True, exist_ok=True)
    (phase_dir / "PHASE-500-Probe.md").write_text(
        '---\ntype: "[[phase]]"\nid: PHASE-500\ntitle: "Probe"\n'
        'status: active\norder: 500\n---\n# Probe\n\n## Exit Criteria\n- [x] x\n',
        encoding="utf-8",
    )
    (docs_root / "features").mkdir(exist_ok=True)
    (docs_root / "features" / "FEAT-0500-Probe.md").write_text(
        '---\ntype: "[[feature]]"\nid: FEAT-0500\ntitle: "Probe"\n'
        'status: done\nphase: "[[PHASE-500-Probe]]"\n---\n# Probe\n',
        encoding="utf-8",
    )

    def offered() -> bool:
        payload = cockpit.stats_payload(Index.build(docs_root))
        ph = next((p for p in payload["phases"] if p["key"] == "PHASE-500"), None)
        assert ph is not None, "the probe phase vanished from the payload"
        return bool(ph["unclosed"])

    assert offered(), "a fully resolved phase is not offered for close-out"

    UNRESOLVED = {
        "task": ("TASK-0500", "backlog"),
        "issue": ("ISS-0500", "open"),
        "requirement": ("REQ-0500", "draft"),
        "feature": ("FEAT-0501", "doing"),
        "risk": ("RISK-0500", "open"),
    }
    for note_type, (note_id, status) in UNRESOLVED.items():
        probe = docs_root / f"{note_id}-Probe.md"
        probe.write_text(
            f'---\ntype: "[[{note_type}]]"\nid: {note_id}\ntitle: "Probe"\n'
            f'status: {status}\nphase: "[[PHASE-500-Probe]]"\n---\n# Probe\n',
            encoding="utf-8",
        )
        try:
            assert not offered(), (
                f"PHASE-500 is still offered for close-out with an unresolved "
                f"{note_type} ({note_id} at {status}) parked on it — "
                f"PHASE-CHILDREN would refuse it"
            )
        finally:
            probe.unlink()
        assert offered(), f"removing the {note_type} probe did not restore the offer"

def test_a_design_note_digest_ignores_what_recording_a_review_touches() -> None:
    """ISS-0057. `at_revision` follows the artifact, so a design's Problem,
    Approach, Regions or Tokens could be rewritten under a reviewer with every
    staleness signal still reading current.

    The objection that kept this in triage was that a review *appends to* the
    note's `## Review` section, so a naive "did the note change" check would
    invalidate itself the instant it was recorded. Asserted here in both
    directions, because the fix is only correct if both hold.
    """
    class Rec:
        def __init__(self, fm: dict, body: str) -> None:
            self.frontmatter, self.body = fm, body

    fm = {"id": "DES-0000", "title": "x", "review_verdict": "", "updated": "2026-01-01"}
    body = "## Problem\n\nA thing is wrong.\n\n## Review\n\n<none yet>\n"
    base = cockpit.design_note_digest(Rec(dict(fm), body))

    appended = body.replace("<none yet>", "<none yet>\n\nRound one: approved.")
    assert cockpit.design_note_digest(Rec(dict(fm), appended)) == base, (
        "filing a review changed the digest, so a review would invalidate itself"
    )

    # Every field the accept path writes, not just the verdict. ISS-0071 found
    # `status` missing: stamp_design_verdict flips draft -> accepted, so an
    # accepting verdict changed its own digest — the objection this fix exists
    # to answer, reintroduced by the fix.
    stamped = {**fm, "review_verdict": "approved", "updated": "2026-07-30",
               "status": "accepted", "reviewed_by": "user:edwin",
               "review_date": "2026-07-30", "design_revision": "abc1234"}
    assert cockpit.design_note_digest(Rec(stamped, body)) == base, (
        "a field the accept path writes changed the digest, so recording a "
        "verdict invalidates itself"
    )

    rewritten = body.replace("A thing is wrong.", "Actually a different thing.")
    assert cockpit.design_note_digest(Rec(dict(fm), rewritten)) != base, (
        "the substance changed and the digest did not — the whole point"
    )


def test_every_task_note_on_disk_is_reachable(repo_index: Index) -> None:
    """ISS-0067, and the same assertion shape as the plan count: against a
    filesystem glob, not a literal, because a type-based lookup returns a
    plausible subset and passes any shape check."""
    on_disk = set(REPO_DOCS.glob("features/*/plan/tasks/TASK-*.md"))
    reached = {r.path for r in cockpit._task_records(repo_index)}
    assert on_disk <= reached, f"unreachable task notes: {sorted(on_disk - reached)}"

    typed = {r.path for r in repo_index.notes_by_type("task")}
    assert typed < on_disk | typed, (
        "if every task were typed this could not distinguish the path fallback "
        "from the type lookup it supplements"
    )


def test_root_file_rows_are_distinguishable_from_docs_notes(repo_index: Index) -> None:
    """ISS-0037. `/README.md` and `/docs/README.md` both reduced to the rel
    `README.md` — in `extractRel` *and* in `/api/render` — so two distinct
    Library rows collapsed onto one fetch and the top-level files were dead
    clicks from FEAT-0010 onward.

    The rel now carries the disambiguator the url always had.
    """
    items = cockpit._project_root_tree_items(REPO_DOCS.parent)
    assert items, "no top-level project files found"
    for item in items:
        assert item["url"].startswith("~root/"), item
    # `~`-prefixed urls survive extractRel — that is why this shape was chosen
    # over keeping a bare leading slash.
    code = _renderer_code()
    assert "if (url.startsWith('~')) return url;" in code
    assert "pathOnly.startsWith('~root/')" in code, "the renderer does not route ~root/"
    server = SERVER.read_text(encoding="utf-8")
    assert 'explicit_root = rel_path.startswith("root/")' in server

    # BOTH clients. ISS-0071: the first guard grepped renderer.ts only, so the
    # payload change landed while mode 1's cockpit.js — which has no
    # `extractRel` and fetches the raw href — started 404ing on `~root/…`. The
    # desktop gained a working link and the browser lost one, undetected.
    browser = (Path(__file__).resolve().parent.parent / "src" / "project_os_cockpit"
               / "static" / "cockpit.js").read_text(encoding="utf-8")
    assert '"~root/"' in browser, (
        "mode 1 does not handle the ~root/ prefix, so the Library's top-level "
        "project files are dead clicks there"
    )


def test_no_legal_status_falls_through_unmarked() -> None:
    """ISS-0071. `failing` was the one legal status with no mark and no dot, so
    a failing test rendered identically to unstarted work — on a strip this
    change had just added tests to, right after deleting the overview's only
    other surface for it.

    Swept over the **vocabulary**, not the corpus, because the corpus contains
    no failing test: a count test passed over the gap, and did.

    Swept per type against the validator's own `ALLOWED_STATUS` table, not the
    cross product. Two earlier versions of this test were wrong in that way —
    one asked `is_done_status("test", "done")` (false: tests are done at
    `passing`) and reported the whole done band; the next asked every status of
    every type and reported 46 pairs like `("issue", "merged")` that no note can
    hold. A sweep over impossible inputs is noise, and noise gets suppressed.
    """
    from project_os_cockpit import statuses

    validator = (Path(__file__).resolve().parent.parent
                 / "tools" / "scripts" / "validate-docs.py").read_text(encoding="utf-8")
    block = validator[validator.index("ALLOWED_STATUS = {"):]
    block = block[:block.index("\n}")]
    allowed = {
        m.group(1): {s.strip().strip('"') for s in m.group(2).split(",") if s.strip()}
        for m in re.finditer(r'"(\w+)":\s*\{([^}]*)\}', block)
    }
    assert {"task", "issue", "feature", "requirement", "test"} <= set(allowed), (
        f"could not read the validator's per-type statuses: {sorted(allowed)}"
    )

    #: Legitimately unmarked, with the reason. "Not started" is a real state and
    #: plain hollow is its mark.
    UNMARKED_BY_DESIGN = (
        set(statuses.BANDS["pending"])          # backlog / open / draft / proposed / …
        | {"approved", "accepted", "next"}      # decided, not begun
        | {"ready"}                             # only a TEST's `ready` is an ask; see below
    )

    unmarked: list[tuple[str, str]] = []
    for note_type in ("task", "issue", "feature", "requirement", "test"):
        for status in sorted(allowed[note_type]):
            if status in UNMARKED_BY_DESIGN and not (
                note_type == "test" and status == "ready"
            ):
                continue
            if (cockpit.square_state_for(status, note_type) is None
                    and not cockpit.needs_human_for(status, note_type)):
                unmarked.append((note_type, status))
    assert not unmarked, (
        f"legal statuses render identically to not-started: {unmarked}. Each "
        "needs a fill, a dot, or an entry in UNMARKED_BY_DESIGN with a reason — "
        "silence is how `failing` went unmarked."
    )

    # And the case that bit: every status in the blocked band is marked, for
    # every type that can hold it.
    for note_type in ("task", "issue", "feature", "requirement", "test"):
        for status in sorted(set(statuses.BANDS["blocked"]) & allowed[note_type]):
            assert cockpit.needs_human_for(status, note_type), (
                f"{note_type} at {status!r} (blocked band) carries no dot"
            )

def test_the_module_twins_agree_with_the_payload(repo_index: Index) -> None:
    """`square_state_for` / `needs_human_for` exist so the sweep above can
    enumerate the vocabulary, and they are only useful if they agree with what
    the payload actually emits. Checked against every item in the live corpus.
    """
    data = cockpit.stats_payload(repo_index)
    items = [i for ph in data["phases"]
             for i in [*ph["features"],
                       *(c for f in ph["features"] for c in f["children"]),
                       *ph["loose"]]]
    assert items
    for item in items:
        expected = cockpit.square_state_for(item["status"], item["type"])
        # `unproven` is an overlay the twin does not model (it needs frontmatter),
        # and it only ever replaces `delivered`.
        actual = item.get("state")
        if actual == "unproven":
            assert expected == "delivered", (
                f"{item['id']} reads unproven but its status maps to {expected}"
            )
            continue
        assert actual == expected, (
            f"{item['id']} ({item['type']} at {item['status']!r}): payload says "
            f"{actual!r}, the twin says {expected!r}"
        )
