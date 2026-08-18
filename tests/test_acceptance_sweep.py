"""TESTING.md rule 3, made performable (FEAT-0115 / TASK-0467, TASK-0468).

The rule has two halves. *"New feature implemented → add Tier 1 test(s)"* is
done routinely. *"Any code change unchecks overlapping Tier 1/Tier 2 tests"* is
**annotated and not performed** — 54 rows across the fleet carry a hand-written
`RE-RUN (…)` and all 54 are still ticked, because unticking destroyed the only
record that the check had ever passed and there was nowhere to say why.

The benchmark for what tooling has to reproduce is the corpus's own hand
commit, `a4577c01`: six checks added, three invalidated, **one commit**. So the
central assertion here is about that shape.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from project_os_cockpit import acceptance, obligations, sweep
from project_os_cockpit.index import Index
from project_os_cockpit.note_writes import WriteError

FEATURE = """---
type: "[[feature]]"
id: FEAT-9001
aliases: ["FEAT-9001"]
title: "The navigator opens on what is owed"
status: doing
owner: user:edwin
created: 2026-08-01
updated: 2026-08-01
tasks: ["[[TASK-9001]]"]
---

# A feature
"""

TASK = """---
type: "[[task]]"
id: TASK-9001
aliases: ["TASK-9001"]
title: "Do the thing"
status: doing
owner: user:edwin
created: 2026-08-01
updated: 2026-08-01
parent: "[[FEAT-9001]]"
---

# A task
"""


def _check(cid: str, *, area: str, section: str, ordinal: int,
           covers: str = "", mark: str = "done") -> str:
    """A MIGRATED acceptance note — `[[test]]` at `level: acceptance`.

    This fixture built `type: "[[check]]"` notes until 2026-08-18, and that is
    exactly why ISS-0205 could not fail here: `acceptance.load` reads
    `[tests at level: acceptance] or notes_by_type("check")`, so a check-typed
    fixture leaves the left branch empty and the `or` falls through to the very
    shape the sweep was writing. **The guard and the defect shared an
    assumption.** Moved rather than supplemented, deliberately: keeping a
    check-typed fixture alongside would preserve the branch that hid it.
    """
    return (
        "---\n"
        'type: "[[test]]"\n'
        f"id: {cid}\n"
        f'aliases: ["{cid}"]\n'
        f'title: "Check {cid}"\n'
        "status: active\n"
        "owner: user:edwin\n"
        "created: 2026-08-01\n"
        "updated: 2026-08-01\n"
        "level: acceptance\n"
        "tier: 1\n"
        f'area: "{area}"\n'
        f'section: "{section}"\n'
        f"ordinal: {ordinal}\n"
        f'mark: "{mark}"\n'
        'verdict_date: "2026-08-01"\n'
        'verdict_reason: ""\n'
        "invalidated_by: {}\n"
        "automation: manual\n"
        "covered_by: []\n"
        f"covers: [{covers}]\n"
        "burden: []\n"
        "evidence: []\n"
        'migrated_from: ""\n'
        "related: []\n"
        "---\n"
        "\n"
        f"# Check {cid}\n"
        "\n"
        "Do the thing and expect the result.\n"
    )


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    (docs / "features" / "nav").mkdir(parents=True)
    (docs / "features" / "nav" / "FEAT-9001-Nav.md").write_text(
        FEATURE, encoding="utf-8")
    (docs / "features" / "nav" / "TASK-9001-Do.md").write_text(
        TASK, encoding="utf-8")
    checks = docs / "tests" / "acceptance"
    checks.mkdir(parents=True)
    # Two checks this feature originated, one in the same area it did not, and
    # one somewhere else entirely — so "in areas" has something to be right or
    # wrong about.
    (checks / "TST-0001-A.md").write_text(
        _check("TST-0001", area="The navigator", section="1.1", ordinal=10,
               covers='"[[FEAT-9001]]"'), encoding="utf-8")
    (checks / "TST-0002-B.md").write_text(
        _check("TST-0002", area="The navigator", section="1.1", ordinal=20,
               covers='"[[FEAT-9001]]"'), encoding="utf-8")
    (checks / "TST-0003-C.md").write_text(
        _check("TST-0003", area="The navigator", section="1.1", ordinal=30),
        encoding="utf-8")
    (checks / "TST-0004-D.md").write_text(
        _check("TST-0004", area="The overview", section="1.2", ordinal=10),
        encoding="utf-8")
    (tmp_path / "SNAPSHOT.yaml").write_text(
        'version: 1\nupdated: "2026-08-01T00:00Z"\n'
        "focus:\n  task: \"\"\n  issue: \"\"\n"
        "counters:\n  CHK: 4\nitems: {}\n", encoding="utf-8")
    for cmd in (["init", "-q"], ["config", "user.email", "t@example.com"],
                ["config", "user.name", "T"], ["add", "-A"],
                ["commit", "-qm", "base"]):
        subprocess.run(["git", *cmd], cwd=tmp_path, check=True,
                       capture_output=True)
    return tmp_path


@pytest.fixture()
def index(repo: Path) -> Index:
    return Index.build(repo / "docs")


# --------------------------------------------------------- what it offers

def test_the_three_lists_are_three_different_questions(index: Index) -> None:
    """Originated, already-invalidated, and in-the-same-area.

    The third is deliberately a HEURISTIC — TESTING.md's rule is about scope
    *overlap*, which nothing can compute — so it is offered to a person and
    never acted on. That distinction is the whole reason it is a separate list
    rather than folded into the first.
    """
    data = sweep.candidates(index, "FEAT-9001")
    assert [r["id"] for r in data["originated"]] == ["TST-0001", "TST-0002"]
    assert [r["id"] for r in data["in_areas"]] == ["TST-0003"]
    assert data["invalidated"] == []
    # TST-0004 is in another area and appears nowhere. A sweep that offered the
    # whole suite would be a sweep nobody reads.
    assert "TST-0004" not in str(data)


def test_the_subjects_include_the_features_tasks(index: Index) -> None:
    """Edwin's correction, in the data: the coupling runs through invalidation.

    A check is rarely invalidated by *the feature* and usually by one of its
    tasks — 39 of the fleet's 54 annotations name a `TASK-*` and 8 a `FEAT-*`.
    """
    data = sweep.candidates(index, "FEAT-9001")
    assert set(data["subjects"]) == {"FEAT-9001", "TASK-9001"}


def test_a_feature_with_no_checks_is_not_an_error(tmp_path: Path) -> None:
    """*"Not all features might need acceptance tests"* — Edwin.

    Three empty lists is the normal case for most features, and the surface has
    to be able to say so. A payload that raised here would make the common case
    look like a failure.
    """
    docs = tmp_path / "docs"
    (docs / "features" / "x").mkdir(parents=True)
    (docs / "features" / "x" / "FEAT-9001-Nav.md").write_text(
        FEATURE, encoding="utf-8")
    data = sweep.candidates(Index.build(docs), "FEAT-9001")
    assert not data["originated"] and not data["in_areas"]
    assert data["feature"]["impact_state"] == "owed"


# ------------------------------------------------------------- one Save

def test_one_save_reproduces_the_benchmarks_shape(repo: Path,
                                                  index: Index) -> None:
    """`a4577c01`: N added, M invalidated, ONE commit.

    The commit is the half that matters most. A sweep split across three
    commits is three chances to stop halfway, and the corpus's own hand commit
    did it in one — which is the standard the tooling has to meet rather than
    merely approach.
    """
    result = sweep.apply(
        index, "FEAT-9001",
        invalidate=[{"id": "TST-0001", "reason": "the tray moved"}],
        create=[
            {"name": "The tray opens first", "tier": 1, "area": "The navigator",
             "text": "Open it. Expect the tray."},
            {"name": "The tray counts what is owed", "tier": 1,
             "area": "The navigator", "text": "Expect a count."},
        ],
    )
    assert result["created"] == ["TST-0005", "TST-0006"]
    assert result["invalidated"] == ["TST-0001"]
    assert result["sha"], "the sweep did not commit"

    files = subprocess.run(
        ["git", "-C", str(repo), "show", "--name-only", "--format=", "HEAD"],
        capture_output=True, text=True, check=True).stdout.split()
    assert sorted(files) == sorted([
        "docs/features/nav/FEAT-9001-Nav.md",
        "docs/tests/acceptance/TST-0001-A.md",
        "docs/tests/acceptance/TST-0005-Tray-Opens-First.md",
        "docs/tests/acceptance/TST-0006-Tray-Counts-What-Owed.md",
    ]), files


def test_the_invalidated_check_keeps_its_record(repo: Path,
                                                index: Index) -> None:
    """The whole reason 54 rows stayed ticked: unticking destroyed the record.

    After a sweep the check is unticked AND says who unticked it and why, and
    its previous pass date survives — which is what makes staleness arithmetic
    rather than an annotation somebody has to read.
    """
    sweep.apply(index, "FEAT-9001",
                invalidate=[{"id": "TST-0001", "reason": "the tray moved"}])
    item = next(i for i in acceptance.load_notes(
        repo / "docs" / acceptance.CHECKS_REL) if i.note_id == "TST-0001")
    # **`rerun`, not `todo`** (ADR-0034 / ISS-0200). This asserted a blank mark
    # until 2026-08-18, which said *"nobody has walked it"* about a check
    # somebody had walked — the two states were one value in the field every
    # surface reads, and telling them apart needed a date comparison.
    assert item.mark == "rerun" and not item.checked
    assert item.needs_rerun and not item.settled
    assert item.invalidated.change == "FEAT-9001"
    assert item.invalidated.reason == "the tray moved"
    assert item.verdict_date == "2026-08-01", (
        "the pass date was erased, so nothing can tell a later re-walk from "
        "an earlier one"
    )


def test_a_new_check_is_authored_unwalked(repo: Path, index: Index) -> None:
    """A check authored as passed is the assertion problem ADR-0010 removed
    from tests, arriving on the population that gates releases."""
    sweep.apply(index, "FEAT-9001",
                create=[{"name": "New thing", "tier": 1,
                         "area": "The navigator", "text": "Do it."}])
    item = next(i for i in acceptance.load_notes(
        repo / "docs" / acceptance.CHECKS_REL) if i.note_id == "TST-0005")
    assert item.mark == "todo" and not item.settled
    assert item.refs == ("FEAT-9001",), "covers: was not prefilled"
    assert item.area == "The navigator" and item.section == "1.1"
    # Sparse and after everything in its section, so nothing renumbered.
    assert item.ordinal == 40


def test_two_new_checks_in_one_section_do_not_collide(repo: Path,
                                                      index: Index) -> None:
    """Both inserts read the same maximum unless the loop feeds itself.

    Found by writing the loop the obvious way first: two checks, one ordinal,
    and a view whose order depended on filename.
    """
    sweep.apply(index, "FEAT-9001", create=[
        {"name": "One", "tier": 1, "area": "The navigator", "text": "a"},
        {"name": "Two", "tier": 1, "area": "The navigator", "text": "b"},
    ])
    items = {i.note_id: i for i in acceptance.load_notes(
        repo / "docs" / acceptance.CHECKS_REL)}
    assert items["TST-0005"].ordinal != items["TST-0006"].ordinal


# ------------------------------------------------------------- refusals

def test_a_sweep_that_changes_nothing_must_say_why(index: Index) -> None:
    """A date would claim work that did not happen.

    This is the one refusal that protects the three-state design: if an empty
    sweep could stamp today's date, `acceptance_impact:` would collapse into a
    boolean meaning *somebody pressed the button*.
    """
    with pytest.raises(WriteError) as caught:
        sweep.apply(index, "FEAT-9001")
    assert "none —" in caught.value.message


def test_none_needs_a_reason(index: Index) -> None:
    with pytest.raises(WriteError):
        sweep.apply(index, "FEAT-9001", impact="none")
    result = sweep.apply(index, "FEAT-9001",
                         impact="none — this feature touches no user surface")
    assert result["acceptance_impact"].startswith("none —")


def test_it_refuses_a_check_it_cannot_see(index: Index) -> None:
    with pytest.raises(WriteError) as caught:
        sweep.apply(index, "FEAT-9001",
                    invalidate=[{"id": "TST-9999", "reason": "x"}])
    assert "TST-9999" in caught.value.message


def test_nothing_is_written_when_anything_is_refused(repo: Path,
                                                    index: Index) -> None:
    """Validate everything, then write.

    A sweep that created four checks and refused the fifth would leave a corpus
    half swept and a feature saying nothing — worse than refusing, because the
    record would look complete.
    """
    before = sorted(p.name for p in
                    (repo / "docs" / acceptance.CHECKS_REL).glob("TST-*.md"))
    with pytest.raises(WriteError):
        sweep.apply(index, "FEAT-9001", create=[
            {"name": "Fine", "tier": 1, "area": "The navigator", "text": "a"},
            {"name": "", "tier": 1, "area": "The navigator", "text": "b"},
        ])
    after = sorted(p.name for p in
                   (repo / "docs" / acceptance.CHECKS_REL).glob("TST-*.md"))
    assert after == before


def test_the_sweep_is_scoped_to_a_feature(index: Index) -> None:
    with pytest.raises(WriteError) as caught:
        sweep.apply(index, "TASK-9001", impact="none — wrong type")
    assert "not a feature" in caught.value.message


# ------------------------------------------------- the considered obligation

def test_an_in_flight_feature_without_the_field_owes_the_sweep(
    index: Index,
) -> None:
    rows = obligations.owed_items(index)["features"]
    assert [r["id"] for r in rows if r["type"] == "acceptance sweep"] \
        == ["FEAT-9001"]


@pytest.mark.parametrize("impact", ["2026-08-17", "none — nothing to sweep"])
def test_either_authored_state_discharges_it_permanently(
    repo: Path, index: Index, impact: str,
) -> None:
    """Three states, because two would lie.

    A boolean collapses *nothing to do* into *not done* and nags forever, which
    is the ADR-0027 failure by construction — and `none` is the state that
    exists so a feature touching no check can say so once and be quiet.
    """
    sweep._set_impact(repo / "docs" / "features" / "nav" / "FEAT-9001-Nav.md",
                      impact, "2026-08-17")
    fresh = Index.build(repo / "docs")
    rows = obligations.owed_items(fresh)["features"]
    assert not [r for r in rows if r["type"] == "acceptance sweep"]


@pytest.mark.parametrize("status", ["backlog", "planned", "done", "cancelled"])
def test_a_feature_not_in_flight_owes_nothing(repo: Path, status: str) -> None:
    """`backlog` owes nothing because nothing has changed; a terminal feature
    is settled either way and the field then RECORDS whether the sweep happened
    rather than asking for it after the fact."""
    path = repo / "docs" / "features" / "nav" / "FEAT-9001-Nav.md"
    path.write_text(FEATURE.replace("status: doing", f"status: {status}"),
                    encoding="utf-8")
    rows = obligations.owed_items(Index.build(repo / "docs"))["features"]
    assert not [r for r in rows if r["type"] == "acceptance sweep"]


def test_no_check_is_ever_owed_however_many_are_unwalked(repo: Path) -> None:
    """The guarantee that outranks every surface in this phase.

    Measured on a corpus where every check is unwalked — the state that would
    make per-check obligations most tempting and most numerous.
    """
    for path in (repo / "docs" / acceptance.CHECKS_REL).glob("TST-*.md"):
        path.write_text(path.read_text(encoding="utf-8").replace(
            'mark: "done"', 'mark: "todo"'), encoding="utf-8")
    index = Index.build(repo / "docs")
    assert len(acceptance.load(repo / "docs", index).blocking()) == 4
    for view, rows in obligations.owed_items(index).items():
        for row in rows:
            assert not str(row["id"]).startswith("CHK-"), (view, row)
    assert "check" not in obligations.counts_by_kind(index)


def test_a_pass_discharges_the_invalidation_it_answers(repo: Path,
                                                       index: Index) -> None:
    """Re-walking a check is what `invalidated_by:` was waiting for.

    The field means *the evidence behind this tick was overtaken and nobody has
    re-walked it*. The moment somebody does, that sentence stops being true —
    and leaving it would make every migrated check permanently stale, because
    **not one** of the fleet's 54 annotations carries a date for the
    arithmetic in `Item.stale` to use.

    Found by mutation: deleting the clear left the whole suite green.
    """
    from project_os_cockpit import note_writes

    sweep.apply(index, "FEAT-9001",
                invalidate=[{"id": "TST-0001", "reason": "the tray moved"}])
    fresh = Index.build(repo / "docs")
    note_writes.mark_check(fresh, check_id="TST-0001", verdict="pass",
                           reason="walked again on the new tray")
    item = next(i for i in acceptance.load_notes(
        repo / "docs" / acceptance.CHECKS_REL) if i.note_id == "TST-0001")
    assert item.checked
    assert not item.invalidated, (
        "the invalidation survived a re-walk, so the check is stale forever"
    )
    assert item.stale is False


def test_staleness_is_arithmetic_once_both_dates_are_known(repo: Path,
                                                           index: Index) -> None:
    """A pass AFTER the invalidating change answers it; one before does not.

    This is what the migration buys that the annotation could not: the
    60-versus-113 gap stops depending on somebody reading a sentence. Both
    directions are asserted, because a rule that only ever returns `True` also
    passes a one-sided test — and did, until a mutation said so.
    """
    path = next((repo / "docs" / acceptance.CHECKS_REL).glob("TST-0001-*.md"))
    base = path.read_text(encoding="utf-8")

    def rewrite(verdict_date: str, invalidated: str) -> acceptance.Item:
        path.write_text(
            base.replace('verdict_date: "2026-08-01"',
                         f'verdict_date: "{verdict_date}"')
                .replace("invalidated_by: {}",
                         "invalidated_by:\n"
                         '  change: "FEAT-9001"\n'
                         '  reason: "the tray moved"\n'
                         f'  date: "{invalidated}"'),
            encoding="utf-8")
        return next(i for i in acceptance.load_notes(path.parent)
                    if i.note_id == "TST-0001")

    assert rewrite("2026-08-01", "2026-08-10").stale is True
    assert rewrite("2026-08-20", "2026-08-10").stale is False
