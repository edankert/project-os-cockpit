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


def test_the_phase_with_open_work_sorts_first(index: Index) -> None:
    """Measured before building: **1 of 18** feature groups had open work,
    and it sorted seventeenth. The whole point of the view was below the
    fold under twenty finished phases."""
    groups = cockpit._features_groups(index)
    first = groups[0]
    assert cockpit._group_is_settled(
        [type("R", (), {"status": i.get("status")})() for i in first["items"]]
    ) == 0, f"the first phase group is entirely complete: {first['key']}"


def test_phase_order_survives_among_equals() -> None:
    """Sorting on open-ness must not shuffle the settled half.

    The finished phases still read as a chronology; only the partition
    between settled and unsettled is new.
    """
    settled = [
        g["key"] for g in cockpit._features_groups(Index.build(DOCS))
        if g["key"].startswith("PHASE-") and g["key"] != "PHASE-999"
    ]
    tail = [k for k in settled if k not in ("PHASE-022",)]
    assert tail == sorted(tail), f"phase order was disturbed: {tail}"


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


def test_risks_stay_a_separate_block(index: Index) -> None:
    """Two blocks on one surface by design (FEAT-0047).

    Interleaving them on open-ness would make the Issues stat tile
    disagree with what the pane shows — every risk is open, so risks
    would take the top and the issue count would look wrong.
    """
    labels = [g["label"] for g in cockpit._issues_groups(index)]
    risk_at = [i for i, x in enumerate(labels) if x.startswith("Risks")]
    issue_at = [i for i, x in enumerate(labels) if not x.startswith("Risks")]
    assert min(risk_at) > max(issue_at), labels


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
