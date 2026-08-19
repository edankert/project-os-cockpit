"""Ordering, not filtering (PHASE-022 / FEAT-0056).

At the time these were written **91% of this repo's corpus was complete**
— tasks 99%, changes 100%, issues 99%, features 96%. Any design that
treats "done" as a thing to remove is designing against nearly all of it,
and `Hide completed` measurably was one: 1 of 18 feature groups survived
it, 0 of 5 severity buckets, and the right-hand context pane of FEAT-0051
and ISS-0080 emptied outright.

The rule these guards encode is **fold on volume, never on meaning**. A
completed task under its feature is what the feature is made of; a
completed task in a list of 264 is something you scroll past. Same
status, different job — so the response differs by pane, not by status.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from project_os_cockpit import cockpit, statuses
from project_os_cockpit.index import Index

REPO_ROOT = Path(__file__).resolve().parents[1]
_PHASE_ID_ONLY = re.compile(r"PHASE-\d+")
DOCS = REPO_ROOT / "docs"


@pytest.fixture(scope="module")
def index() -> Index:
    return Index.build(DOCS)


# ---------------------------------------------------------------------------
# ISS-0082 — a phase's identity is its ID, not its title
# ---------------------------------------------------------------------------


def test_phase_links_resolve_to_a_phase_that_exists(index: Index) -> None:
    """The data half of ISS-0082.

    ISS-0077's merge renamed PHASE-016 and left four notes pointing at the
    dead slug. Nothing caught it: PHASE-CHILDREN validates the phase's own
    ``features:`` list, which the merge *did* update, and no rule walked
    the reverse direction.
    """
    known = set()
    for rec in index.notes_by_type("phase"):
        if rec.note_id:
            known.add(rec.note_id)
            m = re.search(r"(PHASE-\d+)", rec.note_id)
            if m:
                known.add(m.group(1))

    dangling: list[str] = []
    for rec in index.iter_records():
        raw = rec.frontmatter.get("phase")
        if isinstance(raw, list):
            raw = raw[0] if raw else None
        if not isinstance(raw, str) or not raw.strip():
            continue
        target = cockpit._phase_target(rec)
        if target and target not in known:
            dangling.append(f"{rec.rel_path}: phase -> {raw}")

    assert not dangling, "phase links pointing at a phase note that does not exist:\n" + "\n".join(dangling)


def test_the_dangling_link_guard_can_actually_fail() -> None:
    """The review found the corpus guard above cannot detect ISS-0082.

    Once `_phase_target` extracts the ID, the dead slug
    ``PHASE-016-Errors-Become-Work`` resolves to ``PHASE-016``, which IS
    in `known` — so re-introducing the exact defect leaves the guard
    green. It catches a link to a phase that never existed; it does not
    catch a link to a phase that was renamed.

    That is not a reason to delete it, but it IS a reason to state what
    it covers, and to check the uncovered half here: the raw link text
    must name a note that exists on disk.
    """
    known_slugs = {
        rec.path.stem for rec in Index.build(DOCS).notes_by_type("phase")
    }
    stale: list[str] = []
    for rec in Index.build(DOCS).iter_records():
        raw = rec.frontmatter.get("phase")
        if isinstance(raw, list):
            raw = raw[0] if raw else None
        if not isinstance(raw, str) or not raw.strip():
            continue
        slug = raw.strip().strip("[]").split("|")[0].strip()
        # `[[PHASE-016]]` is the ID-only form LIFECYCLE.md says to PREFER,
        # and both `_phase_target` and the validator accept it. Round-2
        # review caught this guard rejecting it — a guard that fails on the
        # documented-preferred spelling would push authors away from it.
        if _PHASE_ID_ONLY.fullmatch(slug):
            continue
        if slug and slug not in known_slugs:
            stale.append(f"{rec.rel_path}: phase -> {slug}")
    assert not stale, (
        "a phase link names a slug with no note behind it — the ISS-0082 "
        "defect, which survives a rename because the ID still resolves:\n"
        + "\n".join(stale)
    )


def test_a_retitled_phase_does_not_fork_its_group() -> None:
    """The structural half — the part that stops it recurring.

    Two links to the same phase under different titles must produce ONE
    grouping key. Before the fix ``_phase_target`` returned the whole
    slug, so the navigator forked while the overview (which extracts the
    ID) did not: the two paths reading one field differently *was* the
    bug, and repairing only the data would leave the next rename to do it
    again.
    """

    class _Rec:
        def __init__(self, phase: str) -> None:
            self.frontmatter = {"phase": phase}

    old = cockpit._phase_target(_Rec("[[PHASE-016-Errors-Become-Work]]"))
    new = cockpit._phase_target(_Rec("[[PHASE-016-The-Overview-Answers-Questions]]"))
    assert old == new == "PHASE-016", (old, new)


def test_exactly_one_group_per_phase(index: Index) -> None:
    """The symptom, asserted directly: a duplicate key is a phantom."""
    keys = [g["key"] for g in cockpit._features_groups(index)]
    dupes = {k for k in keys if keys.count(k) > 1}
    assert not dupes, f"the features navigator renders a phase twice: {dupes}"


# ---------------------------------------------------------------------------
# TASK-0267 — one comparator, open before done
# ---------------------------------------------------------------------------


def test_open_sorts_before_done() -> None:
    items = [
        {"id": "a", "status": "fixed"},
        {"id": "b", "status": "open"},
        {"id": "c", "status": "done"},
        {"id": "d", "status": "doing"},
    ]
    ordered = [i["id"] for i in sorted(items, key=cockpit.open_first_key)]
    assert ordered[:2] == ["b", "d"], ordered
    assert ordered[2:] == ["a", "c"], ordered


def test_the_comparator_is_stable_within_a_state() -> None:
    """Existing order (ID, severity, path) must survive as the tiebreak.

    A sort that also reshuffles items sharing a state makes every list
    move for no reason the reader can see.
    """
    items = [{"id": x, "status": "done"} for x in "zyxw"]
    assert [i["id"] for i in sorted(items, key=cockpit.open_first_key)] == list("zyxw")


def test_the_comparator_reads_the_shared_vocabulary() -> None:
    """Not a second hand-written list.

    ISS-0023 found the status vocabulary restated in eight places, drifted
    in three: ``implemented`` was coloured done but ranked open, so a
    corpus of 97 implemented requirements never cleared the navigator.
    """
    for status in statuses.COMPLETED_STATUSES:
        assert cockpit.open_first_key({"status": status})[0] == 1, (
            f"{status!r} is terminal but the comparator ranks it open"
        )
    for status in statuses.BANDS["active"] + statuses.BANDS["pending"]:
        assert cockpit.open_first_key({"status": status})[0] == 0, (
            f"{status!r} is open but the comparator ranks it done"
        )


def test_an_unknown_status_ranks_open() -> None:
    """The safe default: an unrecognised status is work, not history.

    Ranking it done would quietly sink a note whose status is a typo —
    the failure mode that hides the very thing you need to notice.
    """
    assert cockpit.open_first_key({"status": "wat"})[0] == 0
    assert cockpit.open_first_key({})[0] == 0


def test_the_comparator_is_actually_applied_to_the_issue_buckets() -> None:
    """The review's sharpest finding: removing the open-first pass from
    `_open_first` left all 669 tests green.

    A comparator tested only on a fixture guards a function nobody has to
    call. This reaches the real call site through a synthetic corpus, so
    deleting the sort makes it fail.
    """
    class _Rec:
        def __init__(self, nid: str, status: str) -> None:
            self.note_id, self.status = nid, status
            self.rel_path, self.frontmatter = Path(nid), {"severity": "medium"}

    # ID order puts the completed one FIRST, so the natural sort and the
    # open-first sort disagree — the only arrangement that can catch it.
    records = [_Rec("ISS-0001", "fixed"), _Rec("ISS-0002", "open")]
    assert [r.note_id for r in cockpit._open_first(records)] == [
        "ISS-0002", "ISS-0001",
    ], "_open_first returned ID order — the open-first pass is not applied"


def test_the_features_navigator_orders_its_items_open_first(index: Index) -> None:
    """Same finding, the other call site.

    Asserted on real payload items rather than a fixture: within every
    phase group, no completed feature may precede an open one.
    """
    offenders: list[str] = []
    for g in cockpit._features_groups(index):
        seen_done = False
        for item in g["items"]:
            done = statuses.is_completed(item.get("status"))
            if done:
                seen_done = True
            elif seen_done:
                offenders.append(f"{g['key']}: {item.get('id')} follows a completed item")
    assert not offenders, offenders


# ---------------------------------------------------------------------------
# TASK-0268 — groups still holding open work sort first
# ---------------------------------------------------------------------------


def test_the_leading_phase_group_is_never_a_finished_one(index: Index) -> None:
    """What "groups with open work first" became under three bands.

    The first version asserted the leading group contains an open item.
    That encoded the two-band rule and expired the moment PHASE-022 was
    reopened with every one of its features already `done` — an `active`
    phase holding finished work legitimately leads, because the phase's
    own status is the authored fact and the items are not.

    So the assertion is about the BAND, which is the rule, rather than
    about the items, which are the corpus.
    """
    groups = cockpit._features_groups(index)
    first = groups[0]
    rec = cockpit._resolve_phase(index, first["key"]) if first["key"].startswith("PHASE-") else None
    assert cockpit._phase_group_rank(rec, []) < 2, (
        f"a finished phase leads the features navigator: {first['key']}"
    )


def test_phase_order_survives_within_each_band() -> None:
    """Sorting on the bands must not shuffle order inside a band.

    Twice rewritten for the same reason, worth naming: the first version
    excluded 'PHASE-999', the second also 'PHASE-022' — each hardcoding
    which phases happened to be unsettled that day, and each expiring
    when the corpus moved (the third break was four *planned* phases
    correctly rising to the upcoming band). The rule, not the corpus:
    within each band, phase order ascends.
    """
    idx = Index.build(DOCS)
    groups = [g for g in cockpit._features_groups(idx) if g["key"].startswith("PHASE-")]
    banded: dict[int, list[str]] = {}
    for g in groups:
        rec = cockpit._resolve_phase(idx, g["key"])
        banded.setdefault(cockpit._phase_group_rank(rec, []), []).append(g["key"])
    for rank, keys in banded.items():
        assert keys == sorted(keys), (
            f"phase order disturbed within band {rank}: {keys}"
        )
    # …and the bands themselves are in order (in flight, upcoming, finished).
    ranks = [cockpit._phase_group_rank(cockpit._resolve_phase(idx, g["key"]), [])
             for g in groups]
    assert ranks == sorted(ranks), f"bands interleaved: {ranks}"


def test_a_settled_critical_bucket_falls_below_an_open_medium() -> None:
    """Severity ranks what to do first *among things there are to do*.

    A `critical` bucket in which every issue is fixed contains nothing to
    act on; a `medium` bucket holding one open issue does. This is the
    intended reading, and it is the one that looks wrong at a glance —
    hence an explicit guard.

    Built from a fixture rather than the live corpus deliberately: this
    repo currently has **zero** open issues, so a corpus-derived version
    of this assertion passes without testing anything. It did exactly
    that the moment ISS-0082 closed.
    """

    class _Rec:
        def __init__(self, status: str) -> None:
            self.status = status

    buckets = [
        ("critical", [_Rec("fixed")]),
        ("high", [_Rec("fixed"), _Rec("fixed")]),
        ("medium", [_Rec("fixed"), _Rec("open")]),
        ("low", [_Rec("fixed")]),
    ]
    order = [k for k, _ in cockpit._settled_last(buckets)]
    assert order[0] == "medium", order
    # …and severity order is intact among the settled remainder.
    assert order[1:] == ["critical", "high", "low"], order


def test_risks_are_not_in_the_issues_surface_at_all() -> None:
    """FEAT-0047's arrangement, superseded (Edwin, 2026-08-10 — ISS-0128).

    That feature put risks on the Issues surface as a *separate block*,
    because "what is wrong" and "what could go wrong" are the same question
    in different tenses. The decision went the other way: a risk is a
    standing constraint on the project, so it lives in the constraints view.

    **The concern the original guard protected still holds and is what is
    asserted here.** It existed so the Issues stat tile could not disagree
    with what the pane shows — every risk is `open`, so interleaving them
    would have put risks at the top and made the issue count look wrong.
    With risks gone from the surface entirely, the tile and the pane agree
    by construction, and this asserts that rather than deleting the guard
    along with the arrangement it guarded.
    """
    from project_os_cockpit.index import Index as _I

    idx = _I.build(REPO_ROOT / "docs")
    labels = [g["label"] for g in cockpit._issues_groups(idx)]
    assert not [x for x in labels if x.startswith("Risks")], labels

    rows = [
        item for group in cockpit._issues_groups(idx)
        for item in group["items"]
    ]
    assert all(r.get("type") != "risk" for r in rows), (
        "a risk is still rendered on the Issues surface"
    )


def test_an_empty_group_counts_as_settled() -> None:
    """There is nothing in it to act on."""
    assert cockpit._group_is_settled([]) == 1


def test_the_backlog_pen_does_not_outrank_the_phase_in_flight() -> None:
    """The review caught a two-band split being wrong here.

    `PHASE-999 · Future / Unphased` is permanently `planned`, therefore
    permanently unsettled, so under a settled/unsettled sort it sat above
    the phase actually being worked FOREVER. Worse: closing a phase
    settles it, so the phase just finished sank and the pen took the top.

    Three bands — in flight, upcoming, finished — fix both.
    """
    class _P:
        def __init__(self, status: str) -> None:
            self.status = status

    # ALL FIVE statuses STATUSES.md line 81 allows for a phase. The first
    # version of this test enumerated four and omitted `deferred`, which
    # was exactly the one that fell through to the unknown-status arm and
    # ranked in flight — tying with the active phase and winning on
    # `order`. A vocabulary test that skips a member is not one.
    assert cockpit._phase_group_rank(_P("active"), []) == 0
    assert cockpit._phase_group_rank(_P("planned"), []) == 1
    assert cockpit._phase_group_rank(_P("deferred"), []) == 1
    assert cockpit._phase_group_rank(_P("done"), []) == 2
    assert cockpit._phase_group_rank(_P("superseded"), []) == 2
    for parked in ("planned", "deferred"):
        assert cockpit._phase_group_rank(_P("active"), []) < cockpit._phase_group_rank(_P(parked), []), (
            f"a {parked} phase outranks the phase in flight"
        )


def test_every_allowed_phase_status_is_ranked_explicitly() -> None:
    """The guard that would have caught `deferred` without anyone noticing.

    Ties the ranking to STATUSES.md's list rather than to whichever values
    the author happened to think of.
    """
    allowed = ("planned", "active", "done", "deferred", "superseded")

    class _P:
        def __init__(self, status: str) -> None:
            self.status = status

    unknown = cockpit._phase_group_rank(_P("definitely-not-a-status"), [])
    for status in allowed:
        rank = cockpit._phase_group_rank(_P(status), [])
        assert statuses.band_of(status) is not None, (
            f"{status!r} is allowed for a phase but absent from statuses.BANDS"
        )
        if status != "active":
            assert not (rank == unknown and status != "active"), (
                f"{status!r} falls through to the unknown-status arm instead "
                "of being ranked explicitly"
            )


def test_the_phase_in_flight_leads_the_features_navigator(index: Index) -> None:
    """The end-to-end version, on the real corpus.

    Written against the ACTIVE phase rather than 'the first group has open
    work': the original exit-criteria evidence said 'PHASE-022 moved from
    17th to 1st' and stopped being true the moment PHASE-022 closed. An
    assertion that only holds while the work is open is not an assertion.
    """
    groups = cockpit._features_groups(index)
    ranks = [
        cockpit._phase_group_rank(
            cockpit._resolve_phase(index, g["key"]) if g["key"].startswith("PHASE-") else None,
            [],
        )
        for g in groups
    ]
    assert ranks == sorted(ranks), (
        "phase groups are not banded in-flight / upcoming / finished: "
        f"{[(g['key'], r) for g, r in zip(groups, ranks)]}"
    )


def test_an_unknown_phase_status_ranks_in_flight() -> None:
    """Matching `open_first_key`: a typo must not sink a whole group."""
    class _P:
        status = "wat"
    assert cockpit._phase_group_rank(_P(), []) == 0


# ---------------------------------------------------------------------------
# The call sites, on a corpus built to disagree
# ---------------------------------------------------------------------------
#
# Mutation testing found two guards above still vacuous: deleting the
# open-first sort from `_features_groups`, and deleting `_settled_last`
# from the issue buckets, both left the suite green. This repo's own
# corpus cannot catch them — its feature IDs happen to already run
# open-first, and it has zero open issues, so both sorts are no-ops on it.
#
# A guard that only fails on data we happen to have is a guard that
# expires. These build the disagreement deliberately.


def _note(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{body.strip()}\n---\n\n# body\n", encoding="utf-8")


@pytest.fixture()
def adversarial_docs(tmp_path: Path) -> Index:
    """A corpus where ID order and open-first order DISAGREE.

    The open feature has the *higher* ID and the open issue the *lower*
    severity, so any implementation that falls back to the natural order
    produces a different answer from a correct one.
    """
    docs = tmp_path / "docs"
    _note(docs / "phases" / "PHASE-001-Only.md", """
type: "[[phase]]"
id: PHASE-001
title: "Only"
status: active
order: 1
""")
    # FEAT-0001 is done, FEAT-0002 is open — ID order puts done first.
    _note(docs / "features" / "a" / "FEAT-0001-Done.md", """
type: "[[feature]]"
id: FEAT-0001
title: "Done one"
status: done
phase: "[[PHASE-001-Only]]"
""")
    _note(docs / "features" / "b" / "FEAT-0002-Open.md", """
type: "[[feature]]"
id: FEAT-0002
title: "Open one"
status: doing
phase: "[[PHASE-001-Only]]"
""")
    # A settled `critical` bucket and an unsettled `medium` one.
    _note(docs / "issues" / "ISS-0001-Crit.md", """
type: "[[issue]]"
id: ISS-0001
title: "Crit"
status: fixed
severity: critical
""")
    _note(docs / "issues" / "ISS-0002-Med.md", """
type: "[[issue]]"
id: ISS-0002
title: "Med"
status: open
severity: medium
""")
    return Index.build(docs)


def test_a_done_feature_with_a_lower_id_still_sorts_below_an_open_one(
    adversarial_docs: Index,
) -> None:
    """Deleting the open-first sort in `_features_groups` must fail here."""
    groups = cockpit._features_groups(adversarial_docs)
    phase = next(g for g in groups if g["key"] == "PHASE-001")
    assert [i["id"] for i in phase["items"]] == ["FEAT-0002", "FEAT-0001"], (
        "features fell back to ID order — the open-first pass is not applied"
    )


def test_a_settled_critical_bucket_sorts_below_an_open_medium_one(
    adversarial_docs: Index,
) -> None:
    """Deleting `_settled_last` from the issue buckets must fail here."""
    labels = [g["label"] for g in cockpit._issues_groups(adversarial_docs)]
    assert labels[0] == "Medium", (
        f"a settled critical bucket outranked an unsettled medium one: {labels}"
    )


# ---------------------------------------------------------------------------
# Mode 1 (`static/cockpit.js`) — the hand-written twin
# ---------------------------------------------------------------------------
#
# The review's second finding: mode 1 carries its own `openFirst` /
# `completionRank` / `foldGroup` / fold limit and NOTHING exercised any of
# it. The close-out claimed both surfaces "got the same treatment"; only
# one got guards.
#
# Two implementations of one rule drift — that is what ISS-0023 recorded
# across eight surfaces. These run the real JS through node against the
# same cases the TypeScript twin faces, so the two must agree or fail.

import json
import shutil

COCKPIT_JS = Path(__file__).resolve().parents[1] / "src" / "project_os_cockpit" / "static" / "cockpit.js"


def _run_mode1(script: str) -> object:
    """Evaluate `script` with mode 1's fold helpers in scope.

    `cockpit.js` is an IIFE that touches `document` on load, so the three
    functions are lifted out by source slice rather than by executing the
    file — the same technique `desktop/tests` uses on the built renderer.
    """
    node = shutil.which("node")
    if not node:
        pytest.skip("node not available")
    src = COCKPIT_JS.read_text(encoding="utf-8")
    # The vocabulary the helpers close over, then the helpers themselves.
    vstart = src.index("  var COMPLETED_STATUSES = {")
    vend = src.index("};", vstart) + 2
    start = src.index("  function completionRank(item) {")
    end = src.index("  var NAV_GROUP_FOLD_LIMIT")
    limit_line = src[end:src.index("\n", src.index("=", end))] + ";"
    body = src[vstart:vend] + "\n" + src[start:end] + limit_line.replace("  var", "var")
    prog = f"{body}\nconsole.log(JSON.stringify((() => {{ {script} }})()));"
    out = subprocess.run([node, "-e", prog], capture_output=True, text=True, timeout=30)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


import subprocess  # noqa: E402  (placed with its use, above)


def test_mode1_orders_open_first_like_mode3() -> None:
    got = _run_mode1(
        "return openFirst(["
        "{id:'a',status:'done'},{id:'b',status:'doing'},"
        "{id:'c',status:'fixed'},{id:'d',status:'open'}]).map(x=>x.id);"
    )
    assert got == ["b", "d", "a", "c"], got


def test_mode1_ranks_an_unknown_status_open_like_mode3() -> None:
    assert _run_mode1("return [completionRank({status:'wat'}), completionRank({})];") == [0, 0]


def test_mode1_collapses_a_settled_group_to_a_count_like_mode3() -> None:
    got = _run_mode1(
        "var r = foldGroup([{status:'done'},{status:'fixed'}], 100, true);"
        "return [r.head.length, r.hidden];"
    )
    assert got == [0, 2], got


def test_mode1_folds_on_length_not_status_like_mode3() -> None:
    got = _run_mode1(
        "var items = Array.from({length:50},()=>({status:'open'}));"
        "var r = foldGroup(items, 8, false); return [r.head.length, r.hidden];"
    )
    assert got == [8, 42], got


def test_mode1_preserves_the_head_plus_hidden_invariant() -> None:
    got = _run_mode1(
        "var out = []; var shapes = [[], [{status:'open'}],"
        "[{status:'done'},{status:'done'}],"
        "Array.from({length:40},(_,i)=>({status: i%3 ? 'done':'open'}))];"
        "for (const items of shapes) for (const c of [true,false])"
        "for (const l of [-1,0,1,8,12,1000]) {"
        "var r = foldGroup(items,l,c);"
        "out.push(r.head.length + r.hidden === items.length && r.hidden >= 0); }"
        "return out.every(Boolean);"
    )
    assert got is True, "mode 1 drops rows or over-reports the count at some limit"


def test_mode1_uses_the_same_fold_limit_as_mode3() -> None:
    """One number, two files. It has no business differing."""
    ts = (
        Path(__file__).resolve().parents[1]
        / "desktop" / "src" / "renderer" / "renderer.ts"
    ).read_text(encoding="utf-8")
    m = re.search(r"const NAV_GROUP_FOLD_LIMIT = (\d+);", ts)
    assert m, "NAV_GROUP_FOLD_LIMIT not found in renderer.ts"
    assert _run_mode1("return NAV_GROUP_FOLD_LIMIT;") == int(m.group(1))


def test_the_dangling_link_guard_accepts_the_id_only_form(tmp_path: Path) -> None:
    """Round-2 review: the guard rejected `[[PHASE-016]]`.

    That is the spelling LIFECYCLE.md tells authors to prefer, and both
    `_phase_target` and the validator accept it. A guard that fails on the
    documented-preferred form pushes authors away from it.
    """
    docs = tmp_path / "docs"
    _note(docs / "phases" / "PHASE-001-Only.md", """
type: "[[phase]]"
id: PHASE-001
title: "Only"
status: active
order: 1
""")
    _note(docs / "features" / "a" / "FEAT-0001-A.md", """
type: "[[feature]]"
id: FEAT-0001
title: "A"
status: doing
phase: "[[PHASE-001]]"
""")
    idx = Index.build(docs)
    feat = next(r for r in idx.notes_by_type("feature"))
    assert cockpit._phase_target(feat) == "PHASE-001"
    groups = cockpit._features_groups(idx)
    assert [g["key"] for g in groups] == ["PHASE-001"], (
        "the ID-only phase link did not resolve to its phase group"
    )


def test_mode1_context_pane_cannot_be_made_to_filter_like_mode3() -> None:
    """The mutation that survived the first full sweep.

    Mode 3's `contextGroupRows` was guarded by the node suite; mode 1's
    twin was not, so flipping its one `false` to `true` left everything
    green — on the pane whose emptying is the entire reason for the
    phase, on the surface that had already been caught once for having no
    guards at all.
    """
    got = _run_mode1(
        "var all = [{status:'done'},{status:'fixed'},{status:'merged'}];"
        "var r = contextGroupRows(all, 12);"
        "return [r.head.length, r.hidden, contextGroupRows.length];"
    )
    head, hidden, arity = got
    assert head == 3 and hidden == 0, (
        "mode 1's context pane filtered a fully completed group — this is "
        "the case that emptied FEAT-0051 and ISS-0080 entirely"
    )
    assert arity == 2, "contextGroupRows grew a third parameter — the collapse flag is back"


def test_mode1_context_pane_still_folds_on_length() -> None:
    got = _run_mode1(
        "var many = Array.from({length:79},function(_,i){return {status:'done'};});"
        "var r = contextGroupRows(many, 12); return [r.head.length, r.hidden];"
    )
    assert got == [12, 67], got


# ---------------------------------------------------------------------------
# FEAT-0057 — the record grammar, on mode 1's twin
# ---------------------------------------------------------------------------


def test_mode1_uniform_status_matches_mode3() -> None:
    got = _run_mode1(
        "return [uniformStatus([{status:'done'},{status:'done'}]),"
        " uniformStatus([{status:'DONE'},{status:'done'}]),"
        " uniformStatus([{status:'done'},{status:'open'}]),"
        " uniformStatus([]), uniformStatus([{},{}])];"
    )
    assert got == ["done", "done", None, None, None], got


def test_mode1_head_summary_matches_mode3() -> None:
    got = _run_mode1(
        "return [groupHeadSummary([{status:'done'},{status:'done'}]),"
        " groupHeadSummary([{status:'done'},{status:'open'}]),"
        " groupHeadSummary([{status:'open'},{status:'doing'}]),"
        " groupHeadSummary([])];"
    )
    assert got == ["2 · done", "2 · 1 done", "2", ""], got


def test_mode1_head_summary_always_leads_with_the_count() -> None:
    """The count is what makes a closed group distinguishable from an
    empty one — the failure FEAT-0056 exists to have fixed."""
    got = _run_mode1(
        "var shapes=[[{status:'done'}],[{status:'done'},{status:'open'}],"
        "[{},{},{}],Array.from({length:261},function(){return {status:'done'};})];"
        "return shapes.map(function(s){"
        "  return groupHeadSummary(s).indexOf(String(s.length))===0;});"
    )
    assert got == [True, True, True, True], got


def test_the_two_surfaces_agree_on_the_rollup_nouns() -> None:
    """`16 finished phases · 54 features` reads; `16 finished groups · 54
    items` does not, and saying what is behind the line is the whole value
    of collapsing to one.

    Both surfaces hand-write this table, which is the shape that drifted
    twice already in this phase.
    """
    ts = (
        REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts"
    ).read_text(encoding="utf-8")
    m = re.search(r"const ROLLUP_NOUNS[^=]*= \{(.*?)\n\};", ts, re.DOTALL)
    assert m, "ROLLUP_NOUNS not found in renderer.ts"
    ts_pairs = set(re.findall(r"'([a-z]+)', '([a-z]+)'", m.group(1)))

    js = COCKPIT_JS.read_text(encoding="utf-8")
    m2 = re.search(r"var ROLLUP_NOUNS = \{(.*?)\n  \};", js, re.DOTALL)
    assert m2, "ROLLUP_NOUNS not found in cockpit.js"
    js_pairs = set(re.findall(r'"([a-z]+)", "([a-z]+)"', m2.group(1)))

    assert ts_pairs <= js_pairs, (
        "the two surfaces disagree on the roll-up nouns; "
        f"only in renderer.ts: {ts_pairs - js_pairs}"
    )


def test_the_active_row_selector_matches_the_markup() -> None:
    """ISS-0083 — `refreshActiveNavRow` selected `li.nav-item` while
    `navItem` puts that class on the DIV inside the `li`, so it matched no
    navigable row and the highlight never appeared (measured at f5e6637:
    112 rows, `is-active` on zero of them).

    Guarded by source shape rather than behaviour because the fix is a
    selector, and a selector that stops matching fails silently — which is
    exactly how it survived this long.
    """
    ts = (
        REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts"
    ).read_text(encoding="utf-8")
    body = re.search(
        r"function refreshActiveNavRow\(\): void \{(.*?)\n\}", ts, re.DOTALL
    )
    assert body, "refreshActiveNavRow not found"
    src = body.group(1)
    assert "li[data-rel]" in src, (
        "refreshActiveNavRow no longer selects on data-rel — `li.nav-item` "
        "matches nothing, because navItem puts that class on the inner div"
    )
    assert "querySelector('.nav-item')" in src, (
        "the is-active class must land on the .nav-item div, which is what "
        "`.ws-nav-content .nav-item.is-active` styles"
    )


def test_mode1_shortens_change_ids_like_mode3() -> None:
    """ISS-0084, on the hand-written twin."""
    got = _run_mode1(
        "return [shortNoteId('CHG-20260802-Completed-Work-Collapses'),"
        " shortNoteId('FEAT-0057'), shortNoteId('CHG-20260802'),"
        " shortNoteId('CHANGES-README'), shortNoteId('')];"
    )
    assert got == ["CHG-20260802", "FEAT-0057", "CHG-20260802", "CHANGES-README", ""], got


# ---------------------------------------------------------------------------
# ISS-0085 — every renderer the picker can return, not just the one I edited
# ---------------------------------------------------------------------------


def _renderer_bodies(src: str, names: list[str]) -> dict[str, str]:
    """Body of each named function, respecting its indentation.

    An earlier version ended the match at `\n}` in column 0. `cockpit.js`
    is one big IIFE, so its functions close at `\n  }` — the body ran on
    past the real end and swallowed the very helper being asserted for,
    and the guard passed on a source that did not delegate. Verified by
    mutation this time: breaking mode 1's `navItemNested` now fails.
    """
    out: dict[str, str] = {}
    for name in names:
        m = re.search(rf"^([ \t]*)function {name}\(", src, re.M)
        assert m, f"{name} not found"
        indent = m.group(1)
        tail = src[m.start():]
        # Close on the first line that is exactly this function's indent
        # followed by `}` — brace matching without a JS parser.
        close = re.search(rf"\n{indent}\}}", tail)
        assert close, f"{name}: no closing brace at indent {len(indent)}"
        out[name] = tail[: close.end()]
    return out


def test_every_lifecycle_renderer_delegates_to_one_row_builder() -> None:
    """ISS-0085's actual defect, and the reason it went unnoticed.

    `pickItemRenderer` returns one of four functions. TASK-0271 rewrote
    `navItem` and its guard was written against `navItem` too — so the
    guard confirmed the reading, not the behaviour, and risks, designs,
    requirements and plans kept a 90px two-line card.

    Asserting delegation rather than height because height needs a live
    DOM: three copies that must stay identical is the thing that broke,
    and one builder is what makes it impossible.
    """
    for path, decl in (
        (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts", "buildNavRow"),
        (COCKPIT_JS, "buildNavRow"),
    ):
        src = path.read_text(encoding="utf-8")
        assert f"function {decl}(" in src, f"{path.name} has no shared row builder"
        for name in ("navItem", "navItemStacked", "navItemNested"):
            body = _renderer_bodies(src, [name])[name]
            assert decl in body, (
                f"{path.name}: {name} does not go through {decl} — that is three "
                "copies of one row again, which is what ISS-0085 was"
            )


def test_no_lifecycle_renderer_emits_a_subtitle() -> None:
    """The second line Edwin asked to remove.

    The server sends a subtitle for every feature (`goal`), design and
    risk (first body paragraph) — 50 rows in the pilot workspace — so a
    renderer that prints it is a two-line row in practice, whatever its
    CSS says.
    """
    for path in (
        REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts",
        COCKPIT_JS,
    ):
        src = path.read_text(encoding="utf-8")
        bodies = _renderer_bodies(src, ["buildNavRow"])
        assert "subtitle" not in bodies["buildNavRow"], (
            f"{path.name}: the shared row renders item.subtitle — that is the "
            "second line, on every feature, design and risk"
        )


def test_the_picker_routes_only_to_known_renderers() -> None:
    """If a fifth layout appears, it must be a deliberate addition rather
    than a silent fall-through to a row nobody checked."""
    for path, pat in (
        (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts",
         r"function pickItemRenderer\([^)]*\)[^{]*\{(.*?)\n\}"),
        (COCKPIT_JS, r"function pickItemRenderer\(layout\) \{(.*?)\n  \}"),
    ):
        body = re.search(pat, path.read_text(encoding="utf-8"), re.DOTALL)
        assert body, f"pickItemRenderer not found in {path.name}"
        returned = set(re.findall(r"return (navItem\w*)", body.group(1)))
        # `navItemSurface` is the fourth, added 2026-08-19, and it is the
        # DELIBERATE case this guard asks for. The three above are
        # lifecycle rows differing only by indent — which is why TASK-0271
        # collapsed them after they drifted. A surface is not a lifecycle
        # row: Edwin asked for it to be drawn "the same as the phases are
        # shown in the left pane of the overview", so it is built from
        # `buildPhaseRow`'s shape and REUSES THE OVERVIEW'S OWN CLASSES
        # (`ov-phase`, `ov-phase-under`, `ov-chev`). That is the opposite
        # of the drift this guards: it shares a definition with the thing
        # it must look like rather than copying one.
        #: **Per front door**, because they now differ and that is recorded
        #: rather than hidden ([[ISS-0230]]): the desktop shell has
        #: `navItemSurface`, the browser cockpit does not. [[PHASE-029]] is
        #: exactly this subject — *"the two front doors answer the same
        #: questions, and differ only where a difference was decided"* — so
        #: the difference is named here and the guard keeps its teeth on both.
        expected = {"navItemStacked", "navItemCompact", "navItem"}
        if path.name == "renderer.ts":
            expected |= {"navItemSurface"}
        assert returned == expected, (
            f"{path.name}: pickItemRenderer routes to {returned}; a new renderer "
            "must be brought into the shared row builder deliberately"
        )


# ---------------------------------------------------------------------------
# ISS-0086 — the completed band names the taxonomy, it does not hide it
# ---------------------------------------------------------------------------


def test_the_completed_band_defaults_open_on_both_surfaces() -> None:
    """Collapsing a group's BODY hides items nobody is working on.
    Collapsing its HEAD hides which phases exist — a taxonomy, not a
    backlog. The first roll-up was a bare `<details>`, closed and
    unpersisted, so the features navigator's whole top level became two
    rows and the phase list left the page.

    The overview's scope pane has never made that mistake, which is why
    both surfaces now default open and persist the divergence.
    """
    ts = (
        REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts"
    ).read_text(encoding="utf-8")
    band = re.search(
        r"function navCompletedBandOpen\(mode: NavMode\): boolean \{(.*?)\n\}",
        ts, re.DOTALL,
    )
    assert band, "navCompletedBandOpen not found"
    assert "v === null ? true" in band.group(1), (
        "the completed band no longer defaults open — an unset preference "
        "must show the taxonomy, not hide it"
    )

    js = COCKPIT_JS.read_text(encoding="utf-8")
    m = re.search(r'key: "nav:" \+ mode \+ ":__settled",(.*?)\}\)\);', js, re.DOTALL)
    assert m, "the settled band was not found in cockpit.js"
    assert "defaultOpen: true" in m.group(1), (
        "mode 1's completed band does not default open"
    )


def test_both_surfaces_call_the_band_completed() -> None:
    """One idea must not wear two names across two panes.

    The overview's scope pane says `Completed · N`; the navigator said
    `17 finished phases · 56 features`.
    """
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    js = COCKPIT_JS.read_text(encoding="utf-8")
    assert "`Completed · ${groups.length}`" in ts, "renderer.ts does not say Completed · N"
    assert '"Completed \\u00b7 " + settledGroups.length' in js, (
        "cockpit.js does not say Completed · N"
    )
    # …and the overview, which is the surface both are aligning to.
    assert "`Completed · ${complete.length}`" in ts, (
        "the overview's own wording changed — the three must move together"
    )


def test_the_review_desk_shortens_change_ids_too() -> None:
    """ISS-0084 reached the nav rows and the context pane but not the
    desk's `queue-row`, which rendered
    `CHG-20260802-Completed-Work-Collapses` in full.

    Third occurrence in this phase of a change landing in some renderers
    and not all of them — hence a guard that names every call site rather
    than one.
    """
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    raw = re.findall(r"^\s*id\.textContent = (\w+)\.id;$", ts, re.M)
    assert not raw, (
        f"{len(raw)} review-desk row(s) still render the raw id: {raw}"
    )
    assert "shortNoteId(item.id)} ${item.title" in ts, (
        "the queue row still concatenates the full id into its title"
    )


def test_the_scope_row_carries_its_phase_id() -> None:
    """The overview's scope pane was the one surface with no IDs on it —
    24 rows reading `MVP`, `Downstream pilot`, with nothing tying them to
    the PHASE-nnn every other surface names them by (Edwin, 2026-08-02).
    """
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    fn = re.search(r"function buildScopeRow\((.*?)\n\}", ts, re.DOTALL)
    assert fn, "buildScopeRow not found"
    body = fn.group(1)
    assert "shortNoteId(id)" in body, "the scope row does not render its ID"
    assert "ov-typed" in body, (
        "the scope row's ID does not use the shared type-coloured grammar"
    )
    # …and both call sites pass one.
    assert ts.count("`~overview/${p.key}`, overviewScope === p.key") == 2
    for call in re.findall(r"buildScopeRow\((?:.|\n)*?\)\);", ts):
        if "~overview/${p.key}" in call:
            assert "p.key,\n" in call or "p.key," in call.split("overviewScope")[1], (
                f"a scope row is built without its phase id: {call[:90]}"
            )


def test_the_scope_name_is_not_capped_below_the_row() -> None:
    """`flex: none; max-width: 55%` capped every name at 224px in a 424px
    row — a cap that exists to leave room for the progress bar, applied
    also to completed rows that carry no bar. 13 of 24 rows truncated
    with ~200px unused.
    """
    css = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css").read_text(encoding="utf-8")
    rule = re.search(r"\.scope-name \{(.*?)\}", css, re.DOTALL)
    assert rule, ".scope-name rule not found"
    assert "max-width: 55%" not in rule.group(1), (
        "the scope name is capped again — it must take the row's slack"
    )
    assert "flex: 1 1 auto" in rule.group(1), "the scope name does not grow"
    bar = re.search(r"\.scope-bar \{(.*?)\}", css, re.DOTALL)
    assert bar and "flex: 0 0" in bar.group(1), (
        "the progress bar grows again, which starves the name it shares a row with"
    )


def test_the_nav_group_head_shares_the_context_head_box() -> None:
    """ISS-0087 — FEAT-0057 matched the two panes' TYPE and stopped.

    Font size, weight, transform, letter-spacing and colour were already
    identical; every remaining difference was the box. Measured: 42px
    against the context card head's 22px, nineteen times over in the
    features navigator, on a pane whose rows are 27px.

    Density is set by the box, not by the font — which is why "same
    grammar" was not enough to check.
    """
    for path in (
        REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css",
        REPO_ROOT / "src" / "project_os_cockpit" / "static" / "cockpit.css",
    ):
        css = path.read_text(encoding="utf-8")
        rule = re.search(r"\.nav-group-header \{(.*?)\}", css, re.DOTALL)
        assert rule, f"{path.name}: .nav-group-header rule not found"
        body = rule.group(1)
        assert "padding: 4px 8px" in body, (
            f"{path.name}: the group head's padding no longer matches the "
            "context card head it is aligned to"
        )
        assert "background: none" in body, (
            f"{path.name}: the group head has a background again — a bar per "
            "group is what makes nineteen heads read as nineteen bars"
        )
        assert "border-bottom: 0" in body, f"{path.name}: the head's rule is back"


def test_the_chip_does_not_set_the_group_head_height() -> None:
    """The chip measured 21px against the head text's 16px, so it alone
    decided how tall a group head was. Trimmed to sit inside the line.

    Scoped to the HEAD only: in a row the chip is the row's own subject
    and must keep its size.
    """
    for path in (
        REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css",
        REPO_ROOT / "src" / "project_os_cockpit" / "static" / "cockpit.css",
    ):
        css = path.read_text(encoding="utf-8")
        rule = re.search(r"\.nav-group-header \.status-chip \{(.*?)\}", css, re.DOTALL)
        assert rule, f"{path.name}: the head's chip is unconstrained again"
        assert "line-height: 15px" in rule.group(1), (
            f"{path.name}: the chip's line-height sets the head's height again"
        )


# ---------------------------------------------------------------------------
# FEAT-0058 — one shape per navigator
# ---------------------------------------------------------------------------


def test_a_settled_group_opens_shut() -> None:
    """TASK-0275 — the context pane's rule, in the navigator.

    A shut card still carries its name and count, so nothing is hidden
    that the head did not already say. The server's `default_open: false`
    must still win: this adds a reason to close, never a reason to open.
    """
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    m = re.search(r"\(details as HTMLDetailsElement\)\.open =\s*(.*?);", ts, re.DOTALL)
    assert m, "the group's open state is no longer set where expected"
    expr = m.group(1)
    assert "!settledGroup" in expr and "default_open !== false" in expr, (
        f"a settled group no longer opens shut, or the server's default was "
        f"dropped: {expr!r}"
    )
    js = COCKPIT_JS.read_text(encoding="utf-8")
    assert "defaultOpen: !groupIsSettled(g.items || [])" in js, (
        "mode 1's settled groups do not open shut"
    )


def test_only_the_tasks_navigator_skips_the_completed_divider() -> None:
    """TASK-0276 — the divider appears only where a group's own name does
    not already say it is finished.

    `Done`, `Cancelled`, `Superseded` say it; a phase title and a severity
    do not. Encoded as a question the next navigator can answer, rather
    than a list it has to find itself in.
    """
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    fn = re.search(
        r"function groupNamesStateThemselves\(mode: NavMode\): boolean \{(.*?)\n\}",
        ts, re.DOTALL,
    )
    assert fn, "groupNamesStateThemselves not found"
    assert "mode === 'tasks'" in fn.group(1), (
        "the divider rule changed which modes it covers"
    )
    js = COCKPIT_JS.read_text(encoding="utf-8")
    assert 'var namesStateThemselves = mode === "tasks";' in js, (
        "mode 1 disagrees about which navigator skips the divider"
    )


def test_a_status_named_group_does_not_repeat_its_status() -> None:
    """`Done · 265`, not `Done · 265 · done`."""
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    # The summary now has three arms (thing / status-named / everything
    # else), so the check is on the branch rather than on its old shape.
    assert "} else if (groupNamesStateThemselves(mode)) {\n    summaryText = String(items.length || '');" in ts, (
        "the tasks navigator's group head prints its status twice again"
    )


def test_feature_children_summary_counts_tasks_separately() -> None:
    """The children toggle names what a feature carries (TASK-0367).

    Before tasks joined the child list (TASK-0366) both renderers computed
    "everything that is not a plan is a requirement". With tasks in the list
    that turns FEAT-0006 — 9 requirements, a plan and 48 tasks — into
    "57 requirements · plan".

    Asserted in both front doors because the label is hand-written twice, and
    a count that silently mislabels is the shape of defect this phase keeps
    finding.
    """
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    js = (REPO_ROOT / "src" / "project_os_cockpit" / "static" / "cockpit.js").read_text(encoding="utf-8")
    for name, src in (("renderer.ts", ts), ("cockpit.js", js)):
        assert "childrenSummary" in src, f"{name} has no children summary helper"
        body_start = src.index("childrenSummary")
        window = src[body_start:body_start + 1400]
        assert "task" in window, (
            f"{name}'s children summary does not count tasks — a feature with "
            "48 of them will report them as requirements"
        )
        assert "requirement" in window, f"{name}'s summary stopped counting requirements"
        assert "plan" in window, f"{name}'s summary stopped counting plans"


def test_feature_children_fold_on_volume_in_both_front_doors() -> None:
    """A feature's children fold at the same limit its groups do (TASK-0367).

    FEAT-0006 carries 58 children. The child list was previously rendered
    whole because it only ever held a handful of requirements; tasks changed
    the volume, not the rule. Both renderers reuse `foldGroup` and
    `NAV_GROUP_FOLD_LIMIT` rather than growing a second fold.
    """
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    js = (REPO_ROOT / "src" / "project_os_cockpit" / "static" / "cockpit.js").read_text(encoding="utf-8")
    for name, src in (("renderer.ts", ts), ("cockpit.js", js)):
        assert "foldGroup(kids, NAV_GROUP_FOLD_LIMIT" in src or \
               "foldGroup(visibleChildren, NAV_GROUP_FOLD_LIMIT" in src, (
            f"{name} does not fold feature children on the shared limit"
        )
        assert "nav-more-btn" in src, (
            f"{name}'s child fold does not use the established more-row — the "
            "count of what was withheld is never optional"
        )


def test_changes_requested_is_not_treated_as_finished() -> None:
    """TASK-0277 — the sharpest point of that phase — as amended by ISS-0121.

    `changes-requested` means a reviewer asked for work. TASK-0277 promoted
    those rows to sit with live work, which was right, and read the verdict
    alone, which was not: the field is **sticky**. Measured 2026-08-10, all
    ten rows the desk headed `Changes requested` had reached a terminal
    status. Genuinely owed: zero.

    So the assertion moved rather than relaxed. The vocabulary of owed
    verdicts now lives in `cockpit.py` beside the statuses that qualify it
    (the ISS-0023 rule), and the renderer reads the flag it is sent. This
    guards both halves: the vocabulary is still complete, and the renderer
    still does not re-derive it.
    """
    from project_os_cockpit import cockpit

    # The vocabulary half — unchanged in meaning, moved in location.
    assert cockpit.OWED_VERDICTS == {"changes-requested", "rejected"}, (
        "an owed verdict was added or dropped without this test noticing"
    )
    for done in ("approved", "accepted", "plan-accepted"):
        assert done not in cockpit.OWED_VERDICTS, (
            f"{done!r} is being treated as owed — all are finished verdicts, "
            "and reconciling them is ISS-0069's problem, not this one's"
        )

    # The sticky half — ISS-0121. A terminal subject owes nothing.
    assert cockpit._verdict_is_owed("changes-requested", "open") is True
    assert cockpit._verdict_is_owed("changes-requested", "fixed") is False
    assert cockpit._verdict_is_owed("changes-requested", "done") is False
    assert cockpit._verdict_is_owed("changes-requested", "merged") is False
    assert cockpit._verdict_is_owed("approved", "open") is False

    # The renderer half — reads the server's flag, never the verdict string.
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    fn = re.search(
        r"function isOwedVerdict\(item: ReviewRegisterReviewed\): boolean \{(.*?)\n\}",
        ts, re.DOTALL,
    )
    assert fn, "isOwedVerdict not found, or no longer takes the whole item"
    body = fn.group(1)
    assert "item.owed" in body, "the renderer is not reading the server's flag"
    for owed in ("changes-requested", "rejected"):
        assert owed not in body, (
            f"{owed!r} is restated in the renderer — the vocabulary belongs to "
            "cockpit.py alone (ISS-0023)"
        )
    assert "`Changes requested · ${owed.length}`" in ts, (
        "the owed verdicts no longer get their own live section"
    )


def test_the_review_desk_puts_completed_last() -> None:
    """"Completed at the bottom" is the ordering the other three
    navigators use, and the desk emits its two halves from one builder."""
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    order = [
        ts.index("owed.top && owed.top.childElementCount"),
        ts.index("buildTestsRegister(payload.registers?.tests"),
        ts.index("appendIf(wrap, owed.bottom"),
    ]
    assert order == sorted(order), (
        "the review desk's completed band is no longer last"
    )


# ---------------------------------------------------------------------------
# ISS-0088 — the card is a style, not just a behaviour
# ---------------------------------------------------------------------------


def test_no_record_card_title_says_here() -> None:
    """Four scoped cards were built as `Verification here`, `Decisions
    here`, `In flight here`, `Attention here`. The pane already says what
    it is scoped to."""
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    stray = re.findall(r"'([A-Z][\w ]*) here'", ts)
    assert not stray, f"card titles still say 'here': {stray}"


def test_a_group_head_uses_the_row_grammar() -> None:
    """ISS-0088 — the head carried an icon and one flat label string, so
    the ID inside it could not be type-coloured. The icon was a third
    encoding of a fact the coloured ID already carries."""
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    fn = re.search(r"function renderNavGroup\((?:.|\n)*?\n\}", ts)
    assert fn, "renderNavGroup not found"
    body = fn.group(0)
    assert "groupIcon(mode, group)" not in body, "the group head paints an icon again"
    assert "ov-typed" in body, "the group head's id is not type-coloured"


def test_the_pill_follows_whether_the_name_already_says_it() -> None:
    """Two wrong answers preceded this one, and the shape is worth keeping.

    First the pill was suppressed when the item SUMMARY happened to end in
    the same word — defensible, and the output looked random (PHASE-001
    bare, PHASE-002 pilled). Then ISS-0088 made it unconditional, which
    put a `done` pill on a card called `Done`.

    Neither "always" nor "never" was right. The question is whether the
    LABEL is already the status — the same question the divider and the
    head summary ask, so one rule serves three uses.
    """
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    # A third clause joined the condition at ISS-0090: a head that names a
    # THING carries no pill either, because the overview's scope rows have
    # never had one. Asserted on the two predicates rather than the whole
    # line, so refining the rule again does not need this rewritten a
    # fourth time — only inverting it does.
    cond = re.search(r"if \(group\.status && ([^)]*\)[^{]*)\{", ts)
    assert cond, "the pill's condition is no longer where expected"
    assert "!groupNamesStateThemselves(mode)" in cond.group(1), (
        "the pill no longer keys on whether the group's name states its status"
    )
    js = COCKPIT_JS.read_text(encoding="utf-8")
    assert "if (g.status && !namesStateThemselves" in js, (
        "mode 1's pill disagrees with mode 3's"
    )


def test_the_children_toggle_sits_on_the_row() -> None:
    """It was a `<details><summary>2 requirements · plan` beneath the
    feature — a second row describing the first. Its presence is the
    signal; the label was spending a whole row on it."""
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    fn = re.search(r"function navItem\(item: NavItem\): HTMLLIElement \{(?:.|\n)*?\n\}", ts)
    assert fn, "navItem not found"
    body = fn.group(0)
    assert "line.insertBefore(btn" in body, (
        "the children toggle is no longer inserted into the row's own line"
    )
    assert "renderItemChildren" not in body, (
        "navItem builds the old second-row disclosure again"
    )


def test_every_nav_mode_has_a_rollup_noun() -> None:
    """`Completed · 1  1 item` on the design view — `ROLLUP_NOUNS` had no
    entry, so it fell back to "item". Saying what is behind the line is
    the whole value of collapsing to one."""
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    modes = set(re.findall(r"'(\w+)'", re.search(r"const NAV_MODES[^=]*=\s*\[(.*?)\]", ts, re.DOTALL).group(1)))
    table = re.search(r"const ROLLUP_NOUNS[^=]*= \{(.*?)\n\};", ts, re.DOTALL).group(1)
    covered = set(re.findall(r"^\s*(\w+):\s*\{", table, re.M))
    missing = {m for m in modes if m not in covered} - {"overview", "review"}
    assert not missing, (
        f"these nav modes would render `N items` in their completed band: {missing}"
    )


def test_nav_groups_carry_the_card_frame() -> None:
    """FEAT-0058 gave the navigators the right pane's BEHAVIOUR and none
    of its look, so nothing read as a card."""
    for path in (
        REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css",
        REPO_ROOT / "src" / "project_os_cockpit" / "static" / "cockpit.css",
    ):
        css = path.read_text(encoding="utf-8")
        # ALL matching rules, not the first: `cockpit.css` carries an older
        # `.nav-group { border-bottom }` further up, and a guard that read
        # only the first block would report the frame missing while it sat
        # thirty lines below.
        blocks = re.findall(r"\.nav-group \{(.*?)\}", css, re.DOTALL)
        assert blocks, f"{path.name}: no .nav-group rule at all"
        assert any("border-radius: 6px" in b for b in blocks), (
            f"{path.name}: the card frame is gone"
        )
        # REVERSED at ISS-0092. This asserted the band was frameless, on the
        # reasoning that a card containing cards nests two identical
        # borders. That holds where its children are framed — and not in
        # the features view, where the phases inside are *things* and carry
        # no frame of their own, leaving the completed section reading as
        # whatever was left at the bottom rather than as one object.
        #
        # The rule is ONE BORDER PER OBJECT: the band has it, its children
        # do not.
        band = re.search(r"\.nav-group\.nav-rollup \{(.*?)\}", css, re.DOTALL)
        assert band and "border: 1px solid var(--border)" in band.group(1), (
            f"{path.name}: the completed band is not a card"
        )
        inner = re.search(r"\.nav-rollup \.nav-group \{(.*?)\}", css, re.DOTALL)
        assert inner and "border: 0" in inner.group(1), (
            f"{path.name}: the band's children carry a second frame inside its own"
        )



def test_a_features_head_names_a_thing_not_a_category() -> None:
    """The correction four rounds of matching produced (ISS-0089).

    `TASKS` is scaffolding you read past — faint, small, uppercase is
    right. `PHASE-007 · Agent instrumentation` IS the content, and the
    same treatment hides what the pane was opened to find.
    """
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    fn = re.search(
        r"function groupLabelIsCategory\(mode: NavMode\): boolean \{(.*?)\n\}",
        ts, re.DOTALL,
    )
    assert fn, "groupLabelIsCategory not found"
    assert "mode !== 'features'" in fn.group(1), (
        "the category/thing split changed which navigator names things"
    )
    assert "summary.classList.add('is-thing')" in ts, (
        "the head no longer marks itself as naming a thing"
    )
    css = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css").read_text(encoding="utf-8")
    rule = re.search(r"\.nav-group-header\.is-thing \{(.*?)\}", css, re.DOTALL)
    assert rule, "no styling distinguishes a thing-head from a category-head"
    body = rule.group(1)
    assert "text-transform: none" in body, "a thing's name is still uppercased like a label"
    assert "color: var(--text)" in body, "a thing's name is still rendered faint"


def test_a_thing_head_is_framed_like_every_other_group() -> None:
    """Reversed on Edwin's decision, 2026-08-11 (ISS-0131).

    This test used to assert the opposite — `border: 0` — on the reasoning
    that *four boxes around four categories read as structure; eighteen around
    eighteen phases read as clutter*. That was true when written and the count
    changed underneath it: the view opens on `OPEN · 8` with finished phases
    folded into a roll-up, so the live choice is about eight boxes, which is
    the case the same argument endorses.

    So the assertion is inverted rather than deleted, and it now says the
    stronger thing: a phase group keeps the BASE `.nav-group` box, so Features,
    Issues and Intent cannot drift apart by carrying separate numbers.

    **Both stylesheets, because there are two.** `renderer.css` (mode 3) and
    `cockpit.css` (mode 1) each carry this rule and the desktop shell loads
    both, with cockpit.css winning. Editing only the renderer's copy changed
    nothing on screen — exactly the double cost [[FEAT-0073]] names. A guard
    that reads one file would have called that fixed.
    """
    for path in (
        REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css",
        REPO_ROOT / "src" / "project_os_cockpit" / "static" / "cockpit.css",
    ):
        css = path.read_text(encoding="utf-8")
        rule = re.search(
            r"\.nav-group:has\(> \.nav-group-header\.is-thing\) \{(.*?)\}", css, re.DOTALL,
        )
        assert rule, f"{path.name}: the is-thing group rule is gone"
        body = rule.group(1)
        for stripped in ("border: 0", "background: none", "border-radius: 0"):
            assert stripped not in body, (
                f"{path.name}: `{stripped}` takes the card back off the phase group; "
                "Features would stop matching Issues and Intent"
            )


def test_the_overview_completed_card_contains_its_rows() -> None:
    """The frame sat on the heading button alone, with the 22 phase rows
    as a sibling outside it — a card counting phases it did not enclose."""
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    # Scoped to the function: `card.append(head, body)` appears twice in
    # this file, so an unscoped check passed while the overview's own call
    # was mutated away. Caught by mutation, not by reading.
    fn = re.search(
        r"function renderOverviewScopePane\(\): void \{(?:.|\n)*?\n\}", ts,
    )
    assert fn, "renderOverviewScopePane not found"
    assert "card.append(head, body);" in fn.group(0), (
        "the overview's completed card no longer contains its rows"
    )
    css = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css").read_text(encoding="utf-8")
    band = re.search(r"\.scope-band \{(.*?)\}", css, re.DOTALL)
    assert band and "border: 0" in band.group(1), (
        "the frame is back on the heading rather than on the card"
    )


def test_the_live_set_is_named_where_the_finished_one_is() -> None:
    """Edwin asked for two SETS of cards. A set with no name is not one."""
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    assert "`Open · ${live.length}`" in ts, "the live set has no heading"
    assert "!groupNamesStateThemselves(currentNavMode)" in ts, (
        "the live heading appears in the tasks view, whose groups need no divider"
    )


def test_a_thing_head_matches_the_overview_scope_row() -> None:
    """ISS-0090 — [[ISS-0089]] moved the phase head off the label
    treatment and stopped one step short of the row it was aiming at:
    weight 500 against 400, `--text` against `--text-muted`, and a `done`
    pill beside a `· done` summary inside a band headed `Completed`.
    """
    css = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css").read_text(encoding="utf-8")
    rules = re.findall(r"\.nav-group-header\.is-thing \{(.*?)\}", css, re.DOTALL)
    joined = "\n".join(rules)
    assert "font-weight: 400" in joined, "the phase head is heavier than the scope row"
    assert "color: var(--text-muted)" in joined, "the phase head is brighter than the scope row"
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    assert "groupLabelIsCategory(mode)) {\n    appendIf(summary, statusChip(group.status));" in ts, (
        "a head that names a thing carries a status pill again — the "
        "overview's scope rows never had one"
    )
    assert "`✓ ${items.length}`" in ts, (
        "a finished phase no longer uses the scope row's ✓ N trailing form"
    )


def test_an_absent_id_still_occupies_the_id_column() -> None:
    """A plan child carries `id: ""` deliberately — an untyped plan still
    gets a row — and the renderer skipped the id span entirely, so its
    title took the id's place and sat **78px** left of its sibling
    requirements.

    The id column is a column: an absent value has to occupy it.
    """
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    assert "const handle = item.id || (item.type ? item.type.toUpperCase() : '');" in ts, (
        "an item with no id renders no handle, so it leaves the id column"
    )
    js = COCKPIT_JS.read_text(encoding="utf-8")
    assert 'var handle = item.id || (item.type ? String(item.type).toUpperCase() : "");' in js, (
        "mode 1 disagrees about the id-column placeholder"
    )
    for path in (
        REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css",
        REPO_ROOT / "src" / "project_os_cockpit" / "static" / "cockpit.css",
    ):
        css = path.read_text(encoding="utf-8")
        assert ".nav-item-children-list .nav-id { min-width: 9ch; }" in css, (
            f"{path.name}: the nested id column has no width, so a short handle "
            "puts its row on a different grid"
        )
        stand_in = re.search(r"\.nav-id\.is-typeless \{(.*?)\}", css, re.DOTALL)
        assert stand_in and "font-size" not in stand_in.group(1), (
            f"{path.name}: the stand-in handle sets its own font-size — `ch` is "
            "relative to the font, so that narrows the column it shares"
        )


def test_a_group_heads_id_never_shrinks() -> None:
    """ISS-0091 — `flex: none` was scoped to `.nav-item-line`, so in a
    HEAD the id was a flexible child of an overflow-hidden container and a
    long phase title squeezed it. `PHASE-007` rendered 7px of 62.

    The ellipsis belongs on the NAME: a flex container cannot ellipsise
    its children, so `text-overflow` on the inner did nothing and
    `overflow: hidden` merely clipped.
    """
    for path in (
        REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css",
        REPO_ROOT / "src" / "project_os_cockpit" / "static" / "cockpit.css",
    ):
        css = path.read_text(encoding="utf-8")
        assert ".nav-group-header .nav-id { flex: none; }" in css, (
            f"{path.name}: a group head's id can shrink again"
        )
        assert re.search(
            r"\.nav-group-header \.group-header-name \{[^}]*text-overflow: ellipsis", css, re.DOTALL,
        ), f"{path.name}: the head's name does not carry the ellipsis"
    css = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css").read_text(encoding="utf-8")
    inner = re.search(r"\.ws-nav-content \.group-header-inner \{(.*?)\}", css, re.DOTALL)
    assert inner and "overflow: hidden" not in inner.group(1), (
        "the head's inner clips its children again instead of letting the "
        "name ellipsise"
    )


def test_one_expand_handle_across_the_tree() -> None:
    """Three shapes for one gesture: an 8px rotated-border caret on group
    heads, a 4px solid triangle on feature rows, and the same triangle in
    the right pane — so two levels of one tree disagreed while a third
    surface already had the answer.
    """
    css = (REPO_ROOT / "src" / "project_os_cockpit" / "static" / "cockpit.css").read_text(encoding="utf-8")
    chev = re.search(r"\.group-chevron::before \{(.*?)\}", css, re.DOTALL)
    assert chev, "the group chevron no longer draws a triangle"
    body = chev.group(1)
    assert "border-left: 4px solid currentColor" in body, (
        "the group handle is not the 4px solid triangle used everywhere else"
    )
    old = re.search(r"\.group-chevron \{(.*?)\}", css, re.DOTALL)
    assert old and "border-right" not in old.group(1), (
        "the rotated-border caret is back on group heads"
    )
    # …and it matches the right pane's, which already had the right shape.
    ren = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css").read_text(encoding="utf-8")
    # ALL blocks: `.ov-chev::before` is declared once and then overridden
    # for the open state, and a first-match search finds the override —
    # the same trap that made an earlier guard in this file pass on a
    # mutated source.
    ov = re.findall(r"\.ov-chev::before \{(.*?)\}", ren, re.DOTALL)
    assert any("border-left: 4px solid currentColor" in b for b in ov), (
        "the right pane's handle changed; the three must move together"
    )


def test_a_severity_with_both_halves_renders_two_cards() -> None:
    """ISS-0092 — buckets were severity alone, so the live/completed split
    had to place each one whole. A `Medium` holding one open issue and
    fifty-six fixed ones went live with all fifty-seven inside it.

    Today's corpus cannot catch this: every issue is fixed, so every
    bucket is homogeneous by accident. Built to disagree, as with the
    features comparator.
    """
    docs = None
    import tempfile
    docs = Path(tempfile.mkdtemp()) / "docs"
    _note(docs / "issues" / "ISS-0001-A.md", """
type: "[[issue]]"
id: ISS-0001
title: "Open medium"
status: open
severity: medium
""")
    _note(docs / "issues" / "ISS-0002-B.md", """
type: "[[issue]]"
id: ISS-0002
title: "Fixed medium"
status: fixed
severity: medium
""")
    idx = Index.build(docs)
    groups = cockpit._issues_groups(idx)
    keys = [g["key"] for g in groups]
    assert keys == ["medium", "medium:done"], keys
    assert [i["id"] for i in groups[0]["items"]] == ["ISS-0001"]
    assert [i["id"] for i in groups[1]["items"]] == ["ISS-0002"]
    # …and each bucket is homogeneous, which is what lets the navigator's
    # existing rule place them without knowing about severity.
    for g in groups:
        done = {statuses.is_completed(i.get("status")) for i in g["items"]}
        assert len(done) == 1, f"{g['key']} straddles the completed split"


def test_no_rule_between_phase_rows_and_the_band_is_a_card() -> None:
    """Eighteen frames read as clutter, so ISS-0089 replaced them with
    eighteen hairlines — which read as a table. And the completed band was
    a heading over a border-top, on the reasoning that a card containing
    cards nests two frames; true where its children are framed, false in
    the features view where the phases carry none.

    One border per object.
    """
    css = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css").read_text(encoding="utf-8")
    thing = re.search(
        r"\.nav-group:has\(> \.nav-group-header\.is-thing\) \{(.*?)\}", css, re.DOTALL,
    )
    assert thing, "the thing-group rule is gone"
    assert "border-bottom" not in thing.group(1), (
        "phases are ruled off from one another again"
    )
    band = re.search(r"\.ws-nav-content \.nav-group\.nav-rollup \{(.*?)\}", css, re.DOTALL)
    assert band and "border: 1px solid var(--border)" in band.group(1), (
        "the completed band is not a card"
    )
    assert "border-radius: 6px" in band.group(1), "the band has no card radius"
    inner = re.search(r"\.ws-nav-content \.nav-rollup \.nav-group \{(.*?)\}", css, re.DOTALL)
    assert inner and "border: 0" in inner.group(1), (
        "the band's children carry a second frame inside its own"
    )


def test_one_section_heading_style() -> None:
    """ISS-0093 — `.nav-set-heading` was a second style for the role
    `.scope-heading` already filled: 11px/600 spaced with padding against
    10px/700 spaced with margin. Written without checking the first
    existed.
    """
    for path in (
        REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css",
        REPO_ROOT / "src" / "project_os_cockpit" / "static" / "cockpit.css",
    ):
        css = path.read_text(encoding="utf-8")
        rule = re.search(r"\.nav-set-heading,\n\.nav-rollup-label \{(.*?)\}", css, re.DOTALL)
        assert rule, f"{path.name}: the navigator headings have their own rule again"
        body = rule.group(1)
        assert "font-size: 10px" in body and "font-weight: 700" in body, (
            f"{path.name}: the navigator heading does not match .scope-heading"
        )
        assert ".nav-set-heading { padding: 0; margin: 10px 4px 4px; }" in css, (
            f"{path.name}: the heading spaces itself with padding, which made "
            "the same words a 29px block against the overview's 15px"
        )


def test_a_chip_does_not_set_a_row_height() -> None:
    """Design's rows were 27px and every other navigator's 24, purely
    because a status chip was present. Same failure as the group head at
    ISS-0087: the chip is the tallest thing on the line and it is not the
    line's subject."""
    for path in (
        REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css",
        REPO_ROOT / "src" / "project_os_cockpit" / "static" / "cockpit.css",
    ):
        css = path.read_text(encoding="utf-8")
        rule = re.search(r"\.nav-item-line \.status-chip \{(.*?)\}", css, re.DOTALL)
        assert rule and "line-height: 15px" in rule.group(1), (
            f"{path.name}: a chip sets the row's height again"
        )


def test_the_phase_head_sits_left_of_its_features() -> None:
    """A parent indented further than its children is the one arrangement
    a tree must never produce — the phase id measured 45px and the
    features beneath it 43.

    The BODY carries the indent, not the group: indenting the group moves
    the head too, which is the thing being indented from.

    The rule is the INVARIANT — head left of its children — not one way of
    achieving it. It used to assert `padding: 0` on the group, which stopped
    being the mechanism when the card came back (ISS-0131): the group now
    carries the base box's padding and the body still adds its own on top, so
    the head is left of its features by construction. Measured live after the
    change: phase id at 74px, its first feature id at 86px.

    What must not return is a SECOND left indent on the group itself, which is
    what compounded to 45px in ISS-0093.
    """
    for path in (
        REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css",
        REPO_ROOT / "src" / "project_os_cockpit" / "static" / "cockpit.css",
    ):
        css = path.read_text(encoding="utf-8")
        assert re.search(
            r"\.nav-group:has\(> \.nav-group-header\.is-thing\) > \.group-body \{[^}]*padding-left:",
            css,
        ), f"{path.name}: the body no longer carries the indent, so the head moves with its children"
        thing = re.search(
            r"\.nav-group:has\(> \.nav-group-header\.is-thing\) \{(.*?)\}", css, re.DOTALL,
        )
        assert thing, f"{path.name}: the is-thing group rule is gone"
        assert "padding-left:" not in thing.group(1), (
            f"{path.name}: the thing-group declares its own left padding again — "
            "the second indent that compounded to 45px in ISS-0093"
        )


# ---------------------------------------------------------------------------
# ISS-0097/0098/0099 — the phase-scoped overview's rows
# ---------------------------------------------------------------------------


def test_every_id_rendering_site_shortens(  ) -> None:
    """ISS-0099 — the fourth surface ISS-0084's shortening had to reach.

    The nav rows, the context pane, the focus chip and the review desk were
    each fixed as they were found; the activity feed was not among them,
    and rendered `CHG-20260525-Agent-Waiting-Notification` in a narrow
    column, wrapping to four lines.

    So this enumerates instead of naming: **anything that puts a note id
    into the DOM must pass it through `shortNoteId`.** A fifth surface
    fails by existing rather than by being remembered.
    """
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    offenders: list[str] = []

    # textContent assignments from an `.id` property
    for m in re.finditer(r"^\s*(\w+)\.textContent = ([\w.]*\.id)\s*;", ts, re.M):
        offenders.append(f"textContent = {m.group(2)}")
    # innerHTML template literals interpolating a bare escaped id
    for m in re.finditer(r"escapeHtml\((\w+\.id(?: \|\| '')?)\)", ts):
        line_start = ts.rfind("\n", 0, m.start()) + 1
        line = ts[line_start:ts.find("\n", m.start())]
        # A `title="…"` attribute legitimately carries the full value —
        # but the exemption is PER OCCURRENCE, not per line. Checking the
        # line let one `title="${escapeHtml(id)}"` exempt the visible
        # `${escapeHtml(id)}` beside it, and the mutation that reverted the
        # visible one passed. Found by mutation, not by reading.
        before = ts[line_start:m.start()]
        in_title_attr = before.rstrip().endswith('title="${')
        if in_title_attr:
            continue
        offenders.append(line.strip()[:70])

    assert not offenders, (
        "these render a raw note id — pass it through shortNoteId(), or the "
        "next CHG slug wraps to four lines wherever this lands:\n  "
        + "\n  ".join(offenders)
    )


def test_the_scoped_list_rows_have_a_layout() -> None:
    """ISS-0097 — `.scoped-rowlist` and `.verification-list` were styled
    nowhere at all, so their spans concatenated:
    `TST-0005GET /api/render — … guardauto · ran 2026-05-25`.

    The tell that the layout was intended and never written:
    `.verification-meta` carries `margin-left: auto`, which silently does
    nothing outside a flex row.
    """
    css = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css").read_text(encoding="utf-8")
    row = re.search(r"\.scoped-rowlist li \{(.*?)\}", css, re.DOTALL)
    assert row, "the scoped list rows have no rule at all"
    body = row.group(1)
    assert "display: flex" in body, "the row is not a flex row, so its fields concatenate"
    assert "gap:" in body, "the row has no gap, so its fields touch"
    assert re.search(r"\.scoped-rowlist \.scoped-row-id \{[^}]*flex: none", css, re.DOTALL), (
        "the id can shrink again — it is short and fixed; the title is what shortens"
    )
    assert re.search(
        r"\.scoped-rowlist \.scoped-row-title \{[^}]*text-overflow: ellipsis", css, re.DOTALL,
    ), "the title does not ellipsise, so a long one will wrap the row"


def test_a_feature_rows_squares_cannot_change_its_height() -> None:
    """ISS-0098 — `.scoped-feat-sqs` was `flex: 1` (basis 0) AND
    `flex-wrap: wrap`, so a row whose annotation trail wanted space
    squeezed the strip to one square wide and it wrapped to nine lines:
    116px against its neighbours' 32.

    A row whose height depends on its child count is not a row.
    """
    css = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css").read_text(encoding="utf-8")
    rules = re.findall(r"\.scoped-feat-sqs \{(.*?)\}", css, re.DOTALL)
    assert rules, ".scoped-feat-sqs has no rule"
    latest = rules[-1]
    assert "flex-wrap: nowrap" in latest, "the squares strip can wrap again"
    assert "flex: 0 0 auto" in latest, (
        "the squares strip can shrink below its content again"
    )
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    assert re.search(r"const FEATURE_SQUARE_LIMIT = \d+;", ts), (
        "the run is uncapped, so a 37-child feature overflows"
    )
    assert "scoped-feat-more" in ts, "an overflowing strip does not say how many it withheld"


def test_overview_rows_are_grids_with_assigned_columns() -> None:
    """ISS-0100 — both row types were flex chains, so every field sat after
    the natural width of the one before it and nothing lined up: chips at
    seven different x across seven feature rows, six across six phase rows.

    Two things this guard exists to keep, both learned by measuring after
    the grid was added and finding it still wrong:

    1. **Columns are assigned, not inferred.** Auto-placement fills the
       first free cell, so a row lacking a pill slid its row-meta into the
       pill's column.
    2. **One flexible column, not two.** A `1fr` title with an `auto` last
       column made the title 518/593/701px across three rows.
    """
    css = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css").read_text(encoding="utf-8")

    for sel in (r"\.ov-phase-head", r"\.scoped-feat"):
        # ONE block per selector, and it declares the grid.
        #
        # Reading the first block found a dead first-generation rule;
        # reading the last found a one-line `align-items` patch. Both were
        # the same mistake — a selector with three blocks has no single
        # answer to "what does this rule say", so the guard now requires
        # there to be one. (Third time this file has hit the first-match
        # trap; this is the version that removes the trap rather than
        # stepping around it.)
        blocks = re.findall(rf"^{sel} \{{(.*?)^\}}", css, re.DOTALL | re.M)
        assert len(blocks) == 1, (
            f"{sel} has {len(blocks)} rule blocks — merge them; a reader "
            "cannot tell which one wins, and neither could this guard"
        )
        rule = type("M", (), {"group": lambda self, _n, b=blocks[0]: b})()
        assert "display: grid" in rule.group(1), (
            f"{sel} is a flex chain again — its fields will sit wherever the "
            "one before them ends"
        )

    # Every field names its column explicitly.
    for sel, col in (
        (".ov-phase-head > .ov-phase-title", 3),
        # `awaiting close-out` alone, since attention moved inline into the
        # progress field (ISS-0102).
        (".ov-phase-head > .ov-phase-rowmeta", 4),
        (".ov-phase-head > .ov-phase-count", 5),
        # The phase's state reads LAST, after the numbers it qualifies
        # (ISS-0102). Fixed column, `justify-self: start`, so every chip on
        # the page starts at the same x.
        (".ov-phase-head > .status-chip", 6),
        # The chip is column 2 on purpose (ISS-0101): a feature's own state
        # belongs beside its NAME, ahead of the fraction and squares, which
        # describe its children. It used to render last, where `planned`
        # read as a label on the squares next to it.
        (".scoped-feat > .scoped-feat-name", 1), (".scoped-feat > .status-chip", 2),
        (".scoped-feat > .scoped-feat-frac", 3), (".scoped-feat > .scoped-feat-sqs", 4),
        (".scoped-feat > .scoped-feat-next", 5),
    ):
        assert re.search(rf"{re.escape(sel)} *\{{[^}}]*grid-column: {col}", css), (
            f"{sel} has no assigned column — auto-placement will drift it"
        )

    # The phase row is ONE row, and says so.
    #
    # Assigning columns is not enough on its own. Sparse auto-placement
    # never moves its cursor backwards, so the moment the chip (column 6)
    # was appended to the DOM before the count (column 5), the count could
    # not fit behind the cursor and opened a second grid row: the progress
    # field dropped under the title while every x co-ordinate still measured
    # correct. Pinning the row is what makes the assignments independent of
    # append order, which is the only reason to assign them at all.
    for sel in (
        ".ov-phase-head > .ov-chev", ".ov-phase-head > .ov-phase-id",
        ".ov-phase-head > .ov-phase-title", ".ov-phase-head > .ov-phase-rowmeta",
        ".ov-phase-head > .ov-phase-count", ".ov-phase-head > .status-chip",
    ):
        assert re.search(rf"{re.escape(sel)} *\{{[^}}]*grid-row: 1", css), (
            f"{sel} does not pin `grid-row: 1` — reordering the appends will "
            "silently wrap it onto a second line"
        )

    # Exactly one flexible column at each end of each row.
    for sel in (r"\.ov-phase-head", r"\.scoped-feat"):
        rule = re.findall(rf"^{sel} \{{(.*?)^\}}", css, re.DOTALL | re.M)[0]
        tmpl = re.search(r"grid-template-columns:(.*?);", rule, re.DOTALL)
        assert tmpl, f"{sel} declares no columns"
        assert " auto;" not in tmpl.group(1).replace("\n", " ") + ";", (
            f"{sel} ends on an `auto` column: with a 1fr title that makes the "
            "title's width depend on the last column's content"
        )


def test_the_annotation_lead_has_its_own_column() -> None:
    """`▸ doing`, `▸ open` and `▸ triage` are different lengths, so on a
    flex row the id after them started at a different x on every line."""
    css = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css").read_text(encoding="utf-8")
    rule = re.search(r"\.scoped-next-item \{(.*?)\}", css, re.DOTALL)
    assert rule and "display: grid" in rule.group(1), (
        "the annotation item is not a grid, so its id moves with its lead word"
    )
    assert "var(--col-lead)" in rule.group(1), "the lead has no column of its own"


def test_the_column_widths_live_in_one_place() -> None:
    """Sized to each field's worst case and declared once, so the columns
    are a decision rather than an accident of content order."""
    css = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css").read_text(encoding="utf-8")
    for tok in ("--col-chip", "--col-count", "--col-flags", "--col-frac",
                "--col-sqs", "--col-lead", "--col-annid"):
        assert re.search(rf"{tok}: \d+px;", css), f"{tok} is not declared"


def test_progress_is_one_field_and_attention_is_counted_once() -> None:
    """ISS-0101 — the phase row carried four state fields and counted some
    items twice.

    `24/51`, `47%` and `10 in flight` are three readings of one fact — how
    far this phase has got — and sat in three columns with an unrelated
    pill between them. Meanwhile `15 waiting` was an aggregate and, three
    columns later, the row itemised part of the *same set* as
    `2 triage · 1 in review`.

    Edwin could not say what `waiting` meant, which is the right response
    to a number partly repeated beside itself under another name.
    """
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    assert "` · ${inFlight} in flight`" in ts, (
        "in-flight left the progress field it is part of"
    )
    # The word is `attention`: the page's own stat legend reads
    # `done · in flight · attention · backlog`, and three CSS classes carry
    # `is-attention`. `needs you` belongs to AGENT state (`needs-input`), a
    # different idea — using it here collided the two (ISS-0102).
    # The word is `attention`: the page's own stat legend reads
    # `done · in flight · attention · backlog`, and three CSS classes carry
    # `is-attention`. `needs you` belongs to AGENT state (`needs-input`), a
    # different idea — using it here collided the two (ISS-0102).
    assert "` · ${p.waiting} attention`" in ts, (
        "the attention count uses another surface's vocabulary again"
    )
    assert "function attentionBreakdown" in ts, (
        "the breakdown has no home; it belongs in the pill's tooltip, not in "
        "a column beside the count it is a subset of"
    )
    # buildPhaseMeta keeps only what neither field can say.
    #
    # Comments stripped first: the function's own comment *explains* that
    # in-flight moved out, and matching prose would flag the explanation as
    # the offence. That is ISS-0069's false-positive shape, and this guard
    # walked straight into it on its first run.
    meta = re.search(r"function buildPhaseMeta\((?:.|\n)*?\n\}", ts).group(0)
    meta = re.sub(r"//[^\n]*", "", meta)
    for gone in ("in flight", "triage", "in review", "failing test"):
        assert gone not in meta, (
            f"buildPhaseMeta counts `{gone}` again — that is the double-count"
        )
    assert "awaiting close-out" in meta, (
        "the one fact neither the progress nor the attention field can carry "
        "went with them"
    )


def test_attention_reads_inline_with_the_progress_it_belongs_to() -> None:
    """Edwin asked where the attention pill took him. Nowhere — and making
    it navigate would only have repeated what clicking the row already
    does, so **a number that leads nowhere should not be dressed as a
    control.**

    It now reads inline after `in flight`, in the progress field's own font
    and size, differing only in colour: one more reading of the same phase,
    on the same line as the others.
    """
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    assert "ov-phase-attn-inline" in ts, "attention left the progress field"
    assert "ov-phase-pill is-attention" not in ts, (
        "the boxed attention pill is back — it looked like a control and was not"
    )
    css = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css").read_text(encoding="utf-8")
    rule = re.search(r"\.ov-phase-attn-inline \{(.*?)\}", css, re.DOTALL)
    assert rule, "the inline attention has no rule"
    body = rule.group(1)
    assert "--severity-medium" in body, (
        "attention is not the amber every other attention marker uses"
    )
    for prop in ("font-size", "font-weight", "border", "background"):
        assert prop not in body, (
            f"the inline attention sets `{prop}` — it must differ from the "
            "progress text it sits in by COLOUR alone"
        )


def test_the_open_by_default_rule_is_wired_to_the_number_the_row_prints() -> None:
    """ISS-0103. The rule itself is a truth table in `completed-work.ts` and
    is tested as one by `fleet-health.test.mjs`; what cannot be tested there
    is the WIRING, and the wiring is where this could go wrong silently.

    Two ways it could:

    1. `phaseIsOpen` stops consulting the rule and goes back to `!complete`.
       Every phase re-opens and the page is loud again.
    2. The rule is consulted but fed `p.tasks.in_progress` instead of
       `countInFlight(p)`. Those are two different definitions of in-flight
       — the row would print one number and open on the other — and ISS-0023
       is the eight-copy version of exactly that.
    """
    src = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    body = _renderer_bodies(src, ["phaseIsOpen"])["phaseIsOpen"]
    # Comments stripped before the negative assertions: the first version of
    # this guard failed on the comment that EXPLAINS why `in_progress` must
    # not be read here. A guard that a correct explanation can break teaches
    # people to delete the explanation.
    code = "\n".join(
        ln for ln in body.splitlines() if not ln.lstrip().startswith(("//", "*", "/*"))
    )

    assert "phaseOpensByDefault" in code, (
        "phaseIsOpen no longer consults the open-by-default rule"
    )
    assert "countInFlight(p)" in code, (
        "the rule is not being fed the same in-flight count the row prints"
    )
    assert "in_progress" not in code, (
        "phaseIsOpen reads `tasks.in_progress` — a SECOND definition of "
        "in-flight, so the row would print one number and open on another"
    )
    # The stored value must still win, or an SSE re-render re-collapses a
    # phase the reader opened — the accordion would fight them.
    assert "stored === undefined" in code, (
        "the default no longer defers to a stored open/closed state; an SSE "
        "re-render will re-collapse whatever the reader opened"
    )

    # And the rule lives where node can execute it, not in a DOM function.
    cw = (REPO_ROOT / "desktop" / "src" / "renderer" / "completed-work.ts").read_text(encoding="utf-8")
    assert "function phaseOpensByDefault(" in cw, (
        "the rule moved back into the renderer, where it can only be grepped"
    )


def test_one_definition_of_which_phase_statuses_are_active() -> None:
    """`sortLivePhases` and the open-by-default rule ask the same question —
    is anyone in this phase — and answered it from two tables until
    ISS-0103 merged them.

    Guarding this because the drift is invisible: two tables agreeing today
    look exactly like one table, right up until someone adds a status to
    the one they happened to be reading.
    """
    ts = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    cw = (REPO_ROOT / "desktop" / "src" / "renderer" / "completed-work.ts").read_text(encoding="utf-8")

    assert "PHASE_ACTIVE_STATUSES" in cw, "the shared active-status set is gone"
    assert "PHASE_ACTIVE_STATUSES" not in ts, (
        "the renderer declares its own copy of the active-status set"
    )
    rank = re.search(r"const PHASE_LIVE_RANK[^;]*;", ts, re.DOTALL)
    assert rank, "PHASE_LIVE_RANK not found"
    for status in ("active", "doing"):
        assert status not in rank.group(0), (
            f"PHASE_LIVE_RANK names `{status}` again — that is the second "
            "table, and rank 0 must come from phaseIsActiveStatus"
        )
    assert "phaseIsActiveStatus" in ts, (
        "the renderer no longer asks the shared predicate which phases are active"
    )
