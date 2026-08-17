"""The gate is a delta, not a census (TST-0035 / FEAT-0108).

`your-trainer`'s gate has said *"a release is blocked"* at **all twelve tags**
— 1, 15, 85, 130, 22, 47, 47, 47, and 60 at HEAD. It is the steady state, and
a sentence correct and ignored twelve times is one the reader skips.

The central claims here are about **twelve real releases** and a fixture cannot
carry them, so they are asserted against the live repo and skipped when it is
absent. The *shapes* — how a missing baseline degrades, what happens when a
section is inserted above a check, which subject states go quiet — are pinned
on fixtures, because they must hold whatever the fleet looks like next month.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from project_os_cockpit import acceptance, obligations, publication
from project_os_cockpit.index import Index

TRAINER = Path.home() / "Dev" / "repos" / "your-trainer"
needs_trainer = pytest.mark.skipif(
    not (TRAINER / "docs" / acceptance.SUITE_REL).exists(),
    reason="../your-trainer is not present",
)


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, text=True).stdout


def _suite(*rows: str) -> str:
    return "# Tier 1 — Feature Tests\n\n## 1.1 An area (FEAT-0001)\n\n" + "".join(
        f"{r}\n" for r in rows
    )


def _repo_with_tag(tmp_path: Path, before: str, after: str) -> Path:
    root = tmp_path / "repo"
    (root / "docs" / "tests").mkdir(parents=True)
    _git(root.parent, "init", "-q", str(root))
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "T")
    path = root / "docs" / acceptance.SUITE_REL
    path.write_text(before, encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "before")
    _git(root, "tag", "v1.0.0")
    path.write_text(after, encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "after")
    return root


# ----- the delta itself -----------------------------------------------------


def test_a_row_added_since_the_tag_is_new_not_chronic(tmp_path: Path) -> None:
    root = _repo_with_tag(
        tmp_path,
        _suite("- [ ] **Old:** was already open."),
        _suite("- [ ] **Old:** was already open.",
               "- [ ] **Fresh:** arrived after the tag."),
    )
    split = acceptance.delta(
        acceptance.load(root / "docs"), acceptance.suite_at(root, "v1.0.0"),
    )
    assert [i.name for i in split["new"]] == ["Fresh"]
    assert [i.name for i in split["chronic"]] == ["Old"]
    assert split["regressed"] == []


def test_a_row_ticked_at_the_tag_and_unticked_now_is_regressed(
    tmp_path: Path,
) -> None:
    root = _repo_with_tag(
        tmp_path,
        _suite("- [x] **Was walked:** and passed."),
        _suite("- [ ] **Was walked:** and passed."),
    )
    split = acceptance.delta(
        acceptance.load(root / "docs"), acceptance.suite_at(root, "v1.0.0"),
    )
    assert [i.name for i in split["regressed"]] == ["Was walked"]
    assert split["new"] == [] and split["chronic"] == []


def test_inserting_a_section_above_a_check_does_not_make_it_new(
    tmp_path: Path,
) -> None:
    """The diff is on NAME within tier, never on `Item.number`.

    Numbers shift when a section is inserted above — the same asymmetry
    `locate()` relies on, pointing the other way: there it makes a stale
    address FAIL rather than resolve to the wrong row; here it would report an
    untouched check as brand-new work. This is the mutation that must fail.
    """
    before = _suite("- [ ] **Stable:** unchanged by the insertion.")
    after = (
        "# Tier 1 — Feature Tests\n\n"
        "## 1.1 A new area (FEAT-0002)\n\n"
        "- [ ] **Inserted:** genuinely new.\n\n"
        "## 1.2 An area (FEAT-0001)\n\n"
        "- [ ] **Stable:** unchanged by the insertion.\n"
    )
    root = _repo_with_tag(tmp_path, before, after)
    current = acceptance.load(root / "docs")
    stable = next(i for i in current.items if i.name == "Stable")
    assert stable.number == "1.2.1", "the number must actually have moved"

    split = acceptance.delta(current, acceptance.suite_at(root, "v1.0.0"))
    assert [i.name for i in split["new"]] == ["Inserted"]
    assert [i.name for i in split["chronic"]] == ["Stable"]


# ----- degradation: eleven of twelve repos have no tags ---------------------


def test_no_baseline_yields_the_census_not_a_delta() -> None:
    suite = acceptance.Suite(items=acceptance.parse(
        _suite("- [ ] **A:** x.", "- [ ] **B:** y."),
    ))
    split = acceptance.delta(suite, None)
    assert split["comparable"] is False
    assert len(split["chronic"]) == 2
    assert split["new"] == [] and split["regressed"] == []


def test_a_ref_that_does_not_resolve_is_none_not_an_empty_suite(
    tmp_path: Path,
) -> None:
    """`None` and "an empty suite" are different answers.

    A tag from before the file existed must not read as *"the suite had no
    items then"*, because that would make every current row `regressed`.
    """
    root = _repo_with_tag(tmp_path, _suite("- [ ] **A:** x."),
                          _suite("- [ ] **A:** x.", "- [ ] **B:** y."))
    assert acceptance.suite_at(root, "v9.9.9") is None


def test_the_gate_payload_without_a_project_root_is_unchanged() -> None:
    """Every argument after `docs_root` is additive.

    The Tests view and `mountReleaseGate` both call this with one argument and
    must keep getting what they always got.
    """
    got = acceptance.gate_payload(TRAINER / "docs") if TRAINER.exists() else None
    if got is None:
        pytest.skip("../your-trainer is not present")
    assert got["delta"]["comparable"] is False
    assert got["quiet"] == []
    assert "blocking" in got and "counts" in got


# ----- the in-flight rule, as corrected (TASK-0447) -------------------------


class _Rec:
    def __init__(self, status: str) -> None:
        self.status = status
        self.title = ""
        self.rel_path = ""


class _Index:
    """Just enough index for the predicate."""

    def __init__(self, statuses: dict[str, str]) -> None:
        self._s = statuses

    def by_id(self, note_id: str):          # noqa: ANN201
        return note_id if note_id in self._s else None

    def get(self, path):                    # noqa: ANN001, ANN201
        return _Rec(self._s[path]) if path in self._s else None


def test_a_done_subject_does_not_quiet_an_acceptance_row() -> None:
    """The correction that this task turned on.

    Applying the requirement/test rule verbatim quieted **60 of 60** and the
    gate vanished, because `RESTING_STATES` contains `done` and `fixed` and
    almost every acceptance row names a shipped feature or a fixed issue. An
    acceptance row is a regression check: it is MOST worth walking once the
    behaviour ships.
    """
    index = _Index({"FEAT-0011": "done", "ISS-0268": "fixed"})
    assert obligations.ids_are_unbuilt(("FEAT-0011",), index) is False
    assert obligations.ids_are_unbuilt(("ISS-0268",), index) is False
    # …and the old predicate would have said the opposite, which is the bug.
    assert obligations.ids_in_flight(("FEAT-0011",), index) is False


def test_only_an_unbuilt_subject_goes_quiet() -> None:
    index = _Index({"FEAT-0074": "backlog", "FEAT-0090": "planned",
                    "FEAT-0091": "deferred", "FEAT-0092": "doing"})
    assert obligations.ids_are_unbuilt(("FEAT-0074",), index) is True
    assert obligations.ids_are_unbuilt(("FEAT-0090",), index) is True
    assert obligations.ids_are_unbuilt(("FEAT-0091",), index) is True
    assert obligations.ids_are_unbuilt(("FEAT-0092",), index) is False


def test_a_row_with_no_subject_or_an_unknown_one_is_never_quiet() -> None:
    """Absence of evidence is not evidence of rest — the fail-safe direction."""
    index = _Index({"FEAT-0074": "backlog"})
    assert obligations.ids_are_unbuilt((), index) is False
    assert obligations.ids_are_unbuilt(("FEAT-9999",), index) is False
    # An unresolvable id alongside an unbuilt one still asks.
    assert obligations.ids_are_unbuilt(("FEAT-0074", "FEAT-9999"), index) is False


def test_any_built_subject_makes_a_multi_subject_row_walkable() -> None:
    index = _Index({"FEAT-0001": "backlog", "FEAT-0007": "done"})
    assert obligations.ids_are_unbuilt(("FEAT-0001", "FEAT-0007"), index) is False
    assert obligations.ids_are_unbuilt(("FEAT-0001",), index) is True


def test_a_quiet_row_names_its_subject_and_that_subjects_status() -> None:
    """ADR-0028 decision 5 — derived silence must be inspectable."""
    index = _Index({"FEAT-0074": "backlog"})
    why = obligations.resting_reason(("FEAT-0074",), index)
    assert why == [{"id": "FEAT-0074", "status": "backlog",
                    "title": "", "rel": ""}]


# ----- stale evidence (TASK-0448) -------------------------------------------


def test_a_ticked_row_annotated_rerun_is_stale_not_satisfied() -> None:
    items = acceptance.parse(_suite(
        "- [x] **Walked:** and then the code moved. "
        "RE-RUN (TASK-0385: the screen was replaced)",
    ))
    assert items[0].stale is True
    assert items[0].rerun == "TASK-0385: the screen was replaced"


def test_an_unticked_annotated_row_is_blocking_and_not_double_counted() -> None:
    """It is already in `blocking`; counting it as stale as well would report
    the same row twice under two headings that mean opposite things."""
    suite = acceptance.Suite(items=acceptance.parse(_suite(
        "- [ ] **Never walked:** RE-RUN (TASK-0385: moved)",
    )))
    assert len(suite.blocking()) == 1
    assert suite.items[0].stale is False


def test_the_suites_own_rules_line_is_not_read_as_an_annotation() -> None:
    """`## Rules` says *"RE-RUN annotations are cleared"*. A rule that swept up
    its own description would be silently self-referential."""
    text = (
        "## Rules\n\n"
        "5. After a verified release: Tier 3 tests are removed, RE-RUN "
        "annotations are cleared.\n\n"
        + _suite("- [x] **Fine:** nothing stale here.")
    )
    items = acceptance.parse(text)
    assert [i.name for i in items] == ["Fine"]
    assert items[0].rerun == ""


def test_the_word_rerun_in_prose_needs_the_parenthetical() -> None:
    items = acceptance.parse(_suite(
        "- [x] **Prose:** you may want to re-run this by hand, RE-RUN someday.",
    ))
    assert items[0].rerun == "" and items[0].stale is False


# ----- the failed mark (TASK-0454) ------------------------------------------


def test_a_failed_check_is_named_and_still_blocks() -> None:
    """`[F]` is read as `failed` so a surface can say so, and its effect on the
    gate is deliberately identical to what it was before — a check that failed
    is not a check that passed."""
    suite = acceptance.Suite(items=acceptance.parse(_suite(
        "- [F] **Broke:** **FAILS 2026-06-07** — tracked as [[ISS-0285]].",
    )))
    assert suite.items[0].failed is True
    assert suite.items[0].settled is False
    assert len(suite.blocking()) == 1


# ----- against the real twelve releases -------------------------------------


@needs_trainer
def test_the_delta_against_your_trainers_real_tags() -> None:
    """The claim this feature stands on, measured rather than fixtured.

    **Asserted as invariants, not as absolute counts**, and that is a lesson
    paid for three times in one session. `../your-trainer`'s suite is a live
    document: Edwin edits it, and now — because this phase shipped — he also
    *marks checks in it from the app*. A test pinning "60 blocking" fails the
    moment the tool it is testing is used successfully, which is the worst
    possible failure signal.

    So what is pinned is what cannot drift without the code being wrong: the
    split accounts for every blocking row and loses none, the baseline is the
    tag of the newest shipped release, and nothing is negative. The absolute
    figures of the day are recorded in [[FEAT-0108]] and the phase note, which
    are the right place for a measurement — they are dated.
    """
    index = Index.build(TRAINER / "docs")
    payload = publication.release_payload(TRAINER, index, "next")
    gate = payload["gate"]
    delta = gate["delta"]

    assert delta["comparable"] is True
    assert delta["baseline"] == "v2.1.6", "the newest released tag"

    groups = ("new", "chronic", "regressed")
    total = sum(len(delta[g]) for g in groups) + len(gate["quiet"])
    assert total == len(gate["blocking"]), (
        "every blocking row lands in exactly one group"
    )
    # Real work exists, or the corpus stopped being the corpus this describes.
    assert len(gate["blocking"]) > 0
    assert len(delta["new"]) + len(delta["chronic"]) > 0
    # A row cannot be in two groups at once.
    keys = [r["number"] for g in groups for r in delta[g]]
    keys += [r["number"] for r in gate["quiet"]]
    assert len(keys) == len(set(keys))
    # Stale rows are TICKED, so they are disjoint from everything above.
    assert not ({r["number"] for r in gate["stale"]} & set(keys))


@needs_trainer
def test_every_quiet_row_is_quiet_for_a_named_reason() -> None:
    index = Index.build(TRAINER / "docs")
    gate = publication.release_payload(TRAINER, index, "next")["gate"]
    for row in gate["quiet"]:
        assert row["subjects"], f"{row['number']} is quiet and says nothing"
        for subject in row["subjects"]:
            assert subject["status"] in obligations.NOT_YET_BUILT


@needs_trainer
def test_chronic_rows_carry_the_tag_they_have_been_open_since() -> None:
    index = Index.build(TRAINER / "docs")
    gate = publication.release_payload(TRAINER, index, "next")["gate"]
    since = [r["since"] for r in gate["delta"]["chronic"]]
    assert since, "the corpus has chronic rows"
    assert all(since), "every chronic row was present at some tag"
    # Every tag named must be a real one, and the release count must agree
    # with where that tag sits in history — the relationship, not the date.
    tags = _git(TRAINER, "tag", "--sort=v:refname").split()
    for row in gate["delta"]["chronic"]:
        assert row["since"] in tags, row["since"]
        expected = len(tags) - tags.index(row["since"]) - 1
        assert row["releases_since"] == expected, row


@needs_trainer
def test_the_gate_has_never_been_clear_at_any_tag() -> None:
    """The measurement that reframes the surface. If this ever fails because a
    release shipped green, that is worth knowing and the number below is what
    should change — not this assertion's existence."""
    tags = _git(TRAINER, "tag", "--sort=v:refname").split()
    assert len(tags) >= 12
    blocked = 0
    for tag in tags:
        suite = acceptance.suite_at(TRAINER, tag)
        if suite is not None and suite.blocking():
            blocked += 1
    assert blocked == len(tags), "twelve releases, twelve blocked ships"


def test_tags_but_no_released_note_falls_back_to_the_newest_tag(
    tmp_path: Path,
) -> None:
    """Three of the twelve repos are in exactly this state — a tag history and
    no `REL-*` notes at all. The baseline must still be a real tag."""
    root = _repo_with_tag(tmp_path, _suite("- [ ] **A:** x."),
                          _suite("- [ ] **A:** x.", "- [ ] **B:** y."))

    class _Empty:
        def notes_by_type(self, kind: str):     # noqa: ANN201, ARG002
            return []

    assert publication.baseline_ref(root, _Empty()) == "v1.0.0"


def test_no_tags_at_all_yields_no_baseline(tmp_path: Path) -> None:
    """Eleven of twelve repos. The ordinary path, not an error state."""
    root = tmp_path / "bare"
    (root / "docs").mkdir(parents=True)
    _git(root.parent, "init", "-q", str(root))

    class _Empty:
        def notes_by_type(self, kind: str):     # noqa: ANN201, ARG002
            return []

    assert publication.baseline_ref(root, _Empty()) == ""


def test_a_tag_from_before_the_suite_existed_degrades_to_the_census(
    tmp_path: Path,
) -> None:
    """The file is absent at the tag. That must read as *"nothing to compare"*
    and not as *"the suite was empty then"*, which would make every current row
    `regressed`."""
    root = tmp_path / "repo"
    (root / "docs" / "tests").mkdir(parents=True)
    _git(root.parent, "init", "-q", str(root))
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "T")
    (root / "docs" / "seed.md").write_text("x\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "before the suite")
    _git(root, "tag", "v0.1.0")
    (root / "docs" / acceptance.SUITE_REL).write_text(
        _suite("- [ ] **A:** x."), encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "the suite arrives")

    assert acceptance.suite_at(root, "v0.1.0") is None
    split = acceptance.delta(acceptance.load(root / "docs"), None)
    assert split["comparable"] is False
    assert len(split["chronic"]) == 1 and split["regressed"] == []


def test_a_file_that_does_not_parse_at_the_tag_yields_an_empty_baseline(
    tmp_path: Path,
) -> None:
    """Present but not a suite — no tier headings, so `parse` yields nothing.
    Distinct from `None`: git COULD read it, so the diff is honest about
    having a baseline that happens to hold no gating rows."""
    root = _repo_with_tag(
        tmp_path, "just some prose, no tier headings at all\n",
        _suite("- [ ] **A:** x."),
    )
    baseline = acceptance.suite_at(root, "v1.0.0")
    assert baseline is not None and baseline.items == []
    split = acceptance.delta(acceptance.load(root / "docs"), baseline)
    assert [i.name for i in split["new"]] == ["A"]


# ----- the age and the historical line --------------------------------------


def test_releases_since_counts_tags_cut_after_the_one_named() -> None:
    tags = ["v1.0.0", "v1.1.0", "v2.0.0", "v2.1.0"]
    assert acceptance._releases_since("v1.0.0", tags) == 3
    assert acceptance._releases_since("v2.1.0", tags) == 0
    # Unknown is 0, never the total — a row nobody can date must not report as
    # the oldest debt in the project.
    assert acceptance._releases_since("v9.9.9", tags) == 0
    assert acceptance._releases_since("", tags) == 0


def test_the_summary_states_the_median_rather_than_asserting_today_is_bad() -> None:
    line = acceptance._summary(
        ["v1", "v2", "v3"], {"v1": 10, "v2": 30, "v3": 50}, 60)
    assert line == "3 releases, median 30 blocking at ship. This is 60."


def test_the_summary_is_empty_when_no_tag_can_be_parsed() -> None:
    assert acceptance._summary([], {}, 60) == ""
    assert acceptance._summary(["v1"], {}, 60) == ""


@needs_trainer
def test_the_historical_line_is_computed_from_the_real_tags() -> None:
    """*"Twelve releases, median 36 blocking at ship. This is 60."* Without it
    60 is a number with nothing to compare against — which is how it came to
    be ignored twelve times."""
    index = Index.build(TRAINER / "docs")
    delta = publication.release_payload(TRAINER, index, "next")["gate"]["delta"]
    # The tag count is stable — tags do not move — but the live figure is
    # whatever the suite says today, including after somebody marks a check
    # from the app. Shape, not value.
    assert re.fullmatch(
        r"12 releases, median \d+ blocking at ship\. This is \d+\.",
        delta["summary"],
    ), delta["summary"]


@needs_trainer
def test_the_oldest_chronic_row_carries_its_release_count() -> None:
    index = Index.build(TRAINER / "docs")
    chronic = publication.release_payload(
        TRAINER, index, "next")["gate"]["delta"]["chronic"]
    oldest = max(chronic, key=lambda r: r["releases_since"])
    # Some row is the oldest and it is dated against a real tag. Which row that
    # is changes the moment anybody marks a check, so it is not pinned.
    assert oldest["releases_since"] >= 1
    assert oldest["since"] in _git(TRAINER, "tag", "--sort=v:refname").split()
