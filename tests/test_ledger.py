"""The acceptance ledger — a verdict is an event ([[ADR-0037]]).

What is pinned here is the arity and the expiry, because those are the two
things a scalar `mark:` could not hold and the two things a future cleanup
would flatten first.

**The expiry is the load-bearing one.** `Item.excepted` was `mark in {canceled,
-}` read from frontmatter and scoped to nothing, so a check excused once was
excused on every release afterwards — while the comment directly above that set
still described the per-release property [[ADR-0029]] designed and lost when it
moved the release exception from `[!]` to `[-]`. Nobody noticed for three weeks
because `mark: canceled` is written 0 times in all three repos. A test is what
notices.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from project_os_cockpit import ledger as L


@pytest.fixture()
def docs(tmp_path: Path) -> Path:
    root = tmp_path / "docs"
    root.mkdir()
    return root


def _walk(docs: Path, platform: str, check: str, mark: str, **kw: object):
    return L.append(docs, platform, check=check, mark=mark,
                    by=kw.pop("by", "user:edwin"),
                    method=kw.pop("method", "manual"), **kw)  # type: ignore[arg-type]


# ------------------------------------------------------------ the three axes

def test_a_verdict_carries_its_platform_its_method_its_author_and_its_date(
    docs: Path,
) -> None:
    """[[REQ-0052]]. The arity a scalar could not hold."""
    _walk(docs, "android", "TST-0028", "pass", when="2026-08-14")
    found = L.verdicts(docs, "android")["TST-0028"]
    assert (found.mark, found.date, found.by, found.method) == (
        "pass", "2026-08-14", "user:edwin", "manual")
    # And the same check is UNTOUCHED on the other platform, which is the whole
    # point: 513 of your-trainer's passes were earned on Android and the schema
    # had no way to say so.
    assert L.verdicts(docs, "ios") == {}


def test_a_check_with_no_entry_is_owed_on_that_platform(docs: Path) -> None:
    """[[REQ-0054]]: absence IS the initial state.

    Add a platform and every check is immediately owed there — no schema
    change, no key to add, no backfill of 671 notes. A per-note `applies:`
    field would be `PARITY_MATRIX` in frontmatter, rotting by the mechanism
    that matrix demonstrated eight times in one device session.
    """
    _walk(docs, "android", "TST-0028", "pass", when="2026-08-14")
    assert "TST-0028" in L.verdicts(docs, "android")
    assert "TST-0028" not in L.verdicts(docs, "ios")
    assert L.platforms(docs) == ["android"]


# ------------------------------------------------------ the expiry (d7)

def test_an_excused_check_expires_when_its_ledger_seals(docs: Path) -> None:
    """[[ADR-0037]] decision 7 — the property no note field can hold.

    `excused` is *not done this cycle, by decision*. It clears the gate for the
    release it belongs to and for no other. A field on a note has one value and
    no release attached, which is exactly how ADR-0029's per-release exception
    became permanent without anybody deciding it.
    """
    _walk(docs, "android", "TST-0402", "excused",
          reason="Route map is not in v2.1.6.", when="2026-08-15")
    assert L.verdicts(docs, "android")["TST-0402"].mark == "excused"

    L.seal(docs, "android", release="REL-0012", version="v2.1.6",
           when="2026-08-20")
    assert "TST-0402" not in L.verdicts(docs, "android"), (
        "an excused check must be owed again on the next release")


def test_na_and_pass_persist_across_the_seal(docs: Path) -> None:
    """The other half, and the reason `na` and `excused` are two values.

    `na` is a statement about the check and the platform — *there is no
    OS-level auto-backup surface on iOS* — so re-asking it every release is the
    maintained-matrix failure this design exists to remove.
    """
    _walk(docs, "ios", "TST-0141", "na",
          reason="No OS-level auto-backup surface on iOS.", when="2026-08-15")
    _walk(docs, "ios", "TST-0028", "pass", when="2026-08-15")
    L.seal(docs, "ios", release="REL-0013", version="ios/v0.1.0",
           when="2026-08-20")

    after = L.verdicts(docs, "ios")
    assert after["TST-0141"].mark == "na"
    assert after["TST-0028"].mark == "pass"
    # And they now name the release that earned them.
    assert after["TST-0141"].release == "REL-0013"


def test_a_blocking_verdict_does_not_persist_either(docs: Path) -> None:
    """`fail`, `blocked` and `question` are statements about one attempt.

    Carrying them forward would be worse than useless: a check that failed in
    August would still read `fail` in December having never been retried, and
    the reason on it would describe a build nobody ships any more.
    """
    _walk(docs, "android", "TST-0500", "fail", reason="Crashes on connect.",
          when="2026-08-15")
    L.seal(docs, "android", release="REL-0012", version="v2.1.6",
           when="2026-08-20")
    assert "TST-0500" not in L.verdicts(docs, "android")


# ------------------------------------------------------------ invalidation

def test_an_invalidation_re_arms_the_check(docs: Path) -> None:
    """And it is why `mark: rerun` is not in this vocabulary.

    [[ADR-0034]] minted `rerun` three weeks earlier and called it *"the
    addition that earns the migration on its own"*, because `mark: " "` plus an
    `invalidated_by:` block recorded *"nobody has walked it"* against a check
    somebody had walked. An invalidation with a date, sitting after the pass it
    overtakes, makes the two distinguishable by construction — so the value is
    not wrong, it is unnecessary.
    """
    _walk(docs, "android", "TST-0028", "pass", when="2026-08-14")
    L.append(docs, "android", check="TST-0028", invalidated_by="TASK-0776",
             when="2026-08-16")
    assert "TST-0028" not in L.verdicts(docs, "android")

    # And a later walk settles it again, with the history intact on the file.
    _walk(docs, "android", "TST-0028", "pass", when="2026-08-17")
    assert L.verdicts(docs, "android")["TST-0028"].date == "2026-08-17"


def test_an_na_is_invalidatable_like_any_other_verdict(docs: Path) -> None:
    """[[REQ-0054]]: the escape hatch is not a one-way door."""
    _walk(docs, "ios", "TST-0141", "na", reason="No surface on iOS.",
          when="2026-08-15")
    L.append(docs, "ios", check="TST-0141", invalidated_by="FEAT-0140",
             when="2026-08-18")
    assert "TST-0141" not in L.verdicts(docs, "ios")


# ----------------------------------------------------------------- refusals

def test_a_reason_bearing_mark_is_refused_without_a_reason(docs: Path) -> None:
    """[[ADR-0029]]'s rule, enforced for the first time against something real.

    Measured 2026-08-19: `verdict_reason:` is non-empty on **0 of 671** notes.
    The rule held only because nobody ever wrote one of the four marks that
    demanded it — it was never tested against anything.
    """
    for mark in sorted(L.NEEDS_REASON):
        with pytest.raises(L.LedgerError, match="needs a reason"):
            _walk(docs, "android", "TST-0001", mark, when="2026-08-15")
    # `pass` is the one that does not need one.
    _walk(docs, "android", "TST-0001", "pass", when="2026-08-15")


@pytest.mark.parametrize("missing", ["by", "method", "date"])
def test_an_entry_missing_an_axis_is_refused(docs: Path, missing: str) -> None:
    raw = {"check": "TST-0001", "mark": "pass", "date": "2026-08-15",
           "by": "user:edwin", "method": "manual"}
    raw[missing] = ""
    with pytest.raises(L.LedgerError):
        L.check_entry(raw, where="test")


def test_an_entry_may_not_contradict_its_file(docs: Path) -> None:
    """The platform is the ledger's. An entry that could state its own would be
    a second encoding of one fact, which is what [[ADR-0032]] spent a decision
    removing."""
    with pytest.raises(L.LedgerError, match="second encoding"):
        L.check_entry({"check": "TST-0001", "mark": "pass",
                       "date": "2026-08-15", "by": "u", "method": "manual",
                       "platform": "ios"}, where="test")


def test_a_mark_and_an_invalidation_are_two_events(docs: Path) -> None:
    with pytest.raises(L.LedgerError, match="two events"):
        L.check_entry({"check": "TST-0001", "mark": "pass",
                       "invalidated_by": "TASK-0001", "date": "2026-08-15"},
                      where="test")


def test_an_unrecognised_mark_is_refused(docs: Path) -> None:
    """Fails closed, the direction every mark decision in this project has
    taken since [[ISS-0141]]."""
    with pytest.raises(L.LedgerError, match="expected one of"):
        _walk(docs, "android", "TST-0001", "done", when="2026-08-15")


def test_a_platform_that_would_escape_the_directory_is_refused(
    docs: Path,
) -> None:
    """`platform` comes from a note field and becomes a filename."""
    for bad in ("../etc", "An/Droid", "", "Android"):
        with pytest.raises(L.LedgerError, match="usable platform name"):
            L.working_path(docs, bad)


# ------------------------------------------------------------------ evidence

def test_evidence_is_a_sibling_of_entries_not_a_field_on_one(
    docs: Path,
) -> None:
    """[[ADR-0037]] decision 1, Edwin's call. It joins by `check` + `date`."""
    L.append(docs, "android", check="TST-0034", mark="pass",
             by="user:edwin", method="manual", when="2026-08-15",
             evidence=[{"ref": "docs/tests/evidence/scan.png",
                        "note": "Pixel 8a"}])
    raw = json.loads(L.working_path(docs, "android").read_text())
    assert "evidence" not in raw["entries"][0], (
        "an entry must stay one line — evidence is bulky and arrives late")
    assert raw["evidence"][0]["check"] == "TST-0034"
    assert raw["evidence"][0]["date"] == "2026-08-15"


def test_evidence_for_a_walk_nobody_recorded_is_reported(docs: Path) -> None:
    """The same guard `cover_check` applies to `covered_by:` ([[ISS-0198]]):
    a claim pointing at nothing reads as backed and is not."""
    _walk(docs, "android", "TST-0034", "pass", when="2026-08-15")
    led = L.working(docs, "android")
    led.evidence.append(L.Evidence(check="TST-0034", date="2026-08-99",
                                   ref="x.png"))
    assert [v.ref for v in L.orphan_evidence(led)] == ["x.png"]
    # The matching pair is not an orphan.
    led.evidence.append(L.Evidence(check="TST-0034", date="2026-08-15",
                                   ref="ok.png"))
    assert [v.ref for v in L.orphan_evidence(led)] == ["x.png"]


# -------------------------------------------------------------- the file

def test_a_sealed_ledger_stays_on_its_own_platform(docs: Path) -> None:
    """The bug this test exists for, found by sealing one rather than reading
    the code.

    `_platform_of` split the filename on its FIRST hyphen, so
    `REL-0012-android` read as platform `0012-android` — which matched no
    filter. The ledger disappeared from its own platform the moment it was
    sealed, and every verdict in it silently stopped counting. Silent, and in
    the direction that lets a release through.
    """
    _walk(docs, "android", "TST-0028", "pass", when="2026-08-14")
    sealed = L.seal(docs, "android", release="REL-0012", version="v2.1.6",
                    when="2026-08-20")
    assert sealed.name == "REL-0012-android.json"
    assert L.platforms(docs) == ["android"]
    assert "TST-0028" in L.verdicts(docs, "android")


def test_sealing_removes_the_working_ledger_and_starts_a_fresh_one(
    docs: Path,
) -> None:
    """There is always exactly one open ledger per platform."""
    _walk(docs, "android", "TST-0028", "pass", when="2026-08-14")
    L.seal(docs, "android", release="REL-0012", version="v2.1.6",
           when="2026-08-20")
    assert not L.working_path(docs, "android").exists()
    assert L.working(docs, "android").entries == []

    _walk(docs, "android", "TST-0029", "pass", when="2026-08-21")
    assert L.working_path(docs, "android").exists()


def test_sealing_twice_onto_one_release_is_refused(docs: Path) -> None:
    _walk(docs, "android", "TST-0028", "pass", when="2026-08-14")
    L.seal(docs, "android", release="REL-0012", version="v2.1.6",
           when="2026-08-20")
    _walk(docs, "android", "TST-0029", "pass", when="2026-08-21")
    with pytest.raises(L.LedgerError, match="already exists and is sealed"):
        L.seal(docs, "android", release="REL-0012", version="v2.1.6",
               when="2026-08-22")


def test_sealing_an_empty_cycle_is_refused(docs: Path) -> None:
    """A release nobody verified anything for is not a sealed record of a
    walk; it is a file that looks like one."""
    with pytest.raises(L.LedgerError, match="empty cycle"):
        L.seal(docs, "android", release="REL-0012", version="v2.1.6")


def test_one_entry_per_line_so_a_diff_reads_as_what_was_added(
    docs: Path,
) -> None:
    """Not decoration. `json.dumps(indent=2)` puts every scalar on its own
    line, which turns appending one event into a forty-line diff — on the file
    a CI runner appends to on every green build."""
    for n in range(3):
        _walk(docs, "android", f"TST-000{n}", "pass", when="2026-08-14")
    text = L.working_path(docs, "android").read_text()
    entry_lines = [l for l in text.splitlines() if '"check"' in l]
    assert len(entry_lines) == 3
    # Still valid JSON, and still round-trips.
    assert len(json.loads(text)["entries"]) == 3
    assert len(L.load(docs, "android")[0].entries) == 3


def test_a_ledger_whose_field_contradicts_its_filename_is_refused(
    docs: Path,
) -> None:
    L.ledgers_dir(docs).mkdir(parents=True)
    (L.ledgers_dir(docs) / "WORKING-android.json").write_text(
        json.dumps({"platform": "ios", "entries": [], "evidence": []}))
    with pytest.raises(L.LedgerError, match="must agree"):
        L.load(docs)


def test_a_repo_with_no_ledger_is_not_a_broken_one(docs: Path) -> None:
    """Absent is a real state — nine of the twelve fleet repos are in it —
    and it must never raise, only report nothing."""
    assert L.load(docs) == []
    assert L.platforms(docs) == []
    assert L.verdicts(docs, "android") == {}


# --------------------------------------------------- the join (TASK-0536)

CHECK_NOTE = """---
type: "[[test]]"
id: {cid}
level: acceptance
status: active
tier: 1
area: "Hardware Connectivity"
mark: {mark}
covers: []
---

# {cid}

A procedure.
"""


def _corpus(docs: Path, **checks: str) -> Path:
    """A checks directory, with each note's LEGACY frontmatter mark."""
    out = docs / "tests" / "acceptance"
    out.mkdir(parents=True, exist_ok=True)
    for cid, mark in checks.items():
        (out / f"{cid}-A-Check.md").write_text(
            CHECK_NOTE.format(cid=cid, mark=mark))
    return out


def test_a_repo_with_no_ledger_reads_exactly_as_before(docs: Path) -> None:
    """Nine of twelve fleet repos have no ledger and must not move an inch."""
    from project_os_cockpit import acceptance

    _corpus(docs, **{"TST-0001": "done", "TST-0002": "todo"})
    suite = acceptance.load(docs, platform="android")
    marks = {i.note_id: i.mark for i in suite.items}
    assert marks == {"TST-0001": "done", "TST-0002": "todo"}
    assert [i.checked for i in suite.items if i.note_id == "TST-0001"] == [True]


def test_the_ledger_outvotes_a_leftover_frontmatter_mark(docs: Path) -> None:
    """[[REQ-0054]] made operational, and the direction matters.

    Once a ledger exists, **the absence of an entry IS the verdict**. A
    leftover `mark: done` in frontmatter — which every unmigrated note still
    carries — must not out-vote it, or the migration would have two sources
    disagreeing and the older one winning.
    """
    from project_os_cockpit import acceptance

    _corpus(docs, **{"TST-0001": "done", "TST-0002": "done"})
    _walk(docs, "android", "TST-0001", "pass", when="2026-08-14")

    suite = acceptance.load(docs, platform="android")
    by_id = {i.note_id: i for i in suite.items}
    assert by_id["TST-0001"].mark == "pass" and by_id["TST-0001"].checked
    assert by_id["TST-0002"].mark == "todo", (
        "no entry means owed, whatever the note still says")
    assert not by_id["TST-0002"].settled


def test_the_same_check_settles_on_one_platform_and_not_the_other(
    docs: Path,
) -> None:
    """The sentence the whole decision exists for."""
    from project_os_cockpit import acceptance

    _corpus(docs, **{"TST-0001": "done"})
    _walk(docs, "android", "TST-0001", "pass", when="2026-08-14")

    assert acceptance.load(docs, platform="android").items[0].settled
    assert not acceptance.load(docs, platform="ios").items[0].settled


def test_both_exceptions_clear_the_gate_and_blocked_does_not(
    docs: Path,
) -> None:
    from project_os_cockpit import acceptance

    _corpus(docs, **{"TST-0001": "todo", "TST-0002": "todo",
                     "TST-0003": "todo"})
    _walk(docs, "android", "TST-0001", "na", reason="No surface.",
          when="2026-08-14")
    _walk(docs, "android", "TST-0002", "excused", reason="Not this cycle.",
          when="2026-08-14")
    _walk(docs, "android", "TST-0003", "blocked", reason="Rig down.",
          when="2026-08-14")

    by_id = {i.note_id: i for i in acceptance.load(docs, platform="android").items}
    assert by_id["TST-0001"].settled and by_id["TST-0002"].settled
    assert not by_id["TST-0003"].settled, (
        "an accident is not a decision — blocked must hold the release")


def test_the_suite_says_which_platform_its_verdicts_are_about(
    docs: Path,
) -> None:
    """A surface rendering verdicts without naming their platform is the
    defect this decision exists to remove, one level up."""
    from project_os_cockpit import acceptance

    _corpus(docs, **{"TST-0001": "done"})
    assert acceptance.load(docs, platform="ios").platform == "ios"
    assert acceptance.load(docs).platform == ""


# ---------------------------------------------------- burndown (TASK-0535)

def test_the_burndown_is_a_query_over_ledgers(docs: Path) -> None:
    """A-`pass` with no surviving verdict on B. The question PARITY_MATRIX was
    hand-maintained to answer, and the first time this repo can ask it."""
    _walk(docs, "android", "TST-0001", "pass", when="2026-08-14")
    _walk(docs, "android", "TST-0002", "pass", when="2026-08-14")
    _walk(docs, "android", "TST-0003", "pass", when="2026-08-14")
    _walk(docs, "ios", "TST-0002", "pass", when="2026-08-15")
    _walk(docs, "ios", "TST-0003", "na", reason="No surface on iOS.",
          when="2026-08-15")

    gaps = L.burndown(docs, "android", "ios")
    assert [g.check for g in gaps] == ["TST-0001"], (
        "na drops out by construction; a walked check is not a gap")
    assert gaps[0].since == "2026-08-14"


def test_an_expired_excuse_reappears_in_the_burndown(docs: Path) -> None:
    """`excused` is a gap and `na` is not, which is the whole reason they are
    two values."""
    _walk(docs, "android", "TST-0001", "pass", when="2026-08-14")
    _walk(docs, "ios", "TST-0001", "excused", reason="Not this cycle.",
          when="2026-08-15")
    assert L.burndown(docs, "android", "ios") == []

    L.seal(docs, "ios", release="REL-0013", version="ios/v0.1.0",
           when="2026-08-20")
    assert [g.check for g in L.burndown(docs, "android", "ios")] == ["TST-0001"]


def test_an_android_fix_re_arms_both_platforms_at_once(docs: Path) -> None:
    """The `ISS-0365`/`ISS-0366` class, structurally.

    An invalidation names **the check**, not a platform's copy of it — so a fix
    that lands on Android puts the check back in the owed set on iOS too. That
    is the whole reason an iOS twin of an Android fix can stop going missing.
    """
    _walk(docs, "android", "TST-0001", "pass", when="2026-08-14")
    _walk(docs, "ios", "TST-0001", "pass", when="2026-08-14")
    assert L.owed(docs, "ios", ["TST-0001"]) == []

    for platform in ("android", "ios"):
        L.append(docs, platform, check="TST-0001",
                 invalidated_by="TASK-0900", when="2026-08-18")
    assert L.owed(docs, "android", ["TST-0001"]) == ["TST-0001"]
    assert L.owed(docs, "ios", ["TST-0001"]) == ["TST-0001"]


def test_the_run_list_and_the_gate_read_one_predicate(docs: Path) -> None:
    """Two implementations of one predicate is how a badge and a gate come to
    disagree about the same corpus."""
    _walk(docs, "android", "TST-0001", "pass", when="2026-08-14")
    _walk(docs, "android", "TST-0002", "blocked", reason="Rig down.",
          when="2026-08-14")
    _walk(docs, "android", "TST-0003", "na", reason="No surface.",
          when="2026-08-14")
    assert L.owed(docs, "android",
                  ["TST-0001", "TST-0002", "TST-0003", "TST-0004"]) == [
        "TST-0002", "TST-0004"]
