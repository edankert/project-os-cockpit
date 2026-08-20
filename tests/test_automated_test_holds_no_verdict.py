"""An automated test holds no verdict, and the validator refuses one (REQ-0058).

**This is a domain widening, not a new rule.** `ACCEPTANCE-STATUS` has forbidden
`ready`/`passing`/`failing` since ADR-0031 — but only at `level: acceptance`,
and it exempted `passing`/`failing` for a note carrying a `command:` on the
ground that the runner owned its status. Measured 2026-08-19, that covered 89 of
the fleet's 139 automated notes: 64% of the domain, with nothing able to say why
it stopped there. ADR-0038 removes the exemption and widens the population.

`TEST-AUTOMATED-EVIDENCE` is the sibling. `last_run:` and `exit_code:` carried
the run that produced a stamped status; with no status they do not merely go
stale, they lie — `your-trainer` holds **69 exit codes against 2 verdicts**, so
67 notes assert a failure recorded nowhere else.

Landed at **zero violations**, so it errors from day one rather than taking a
warning tier — `DECISIONS.md`: a rule whose corpus holds no violations skips the
warning, because a warning would be the permanent tier ADR-0011 forbids.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = REPO_ROOT / "tools" / "scripts" / "validate-docs.py"

NOTE = """---
type: "[[test]]"
id: TST-0009
title: "a test"
status: {status}
{level}{command}{extra}---

# body
"""


def _repo(tmp_path: Path, *, status="active", level="", command="", extra="") -> Path:
    (tmp_path / "docs" / "tests").mkdir(parents=True)
    (tmp_path / "SNAPSHOT.yaml").write_text(
        "version: 1\ncounters:\n  TST: 9\nitems: {}\n", encoding="utf-8")
    (tmp_path / "docs" / "tests" / "TST-0009-A.md").write_text(
        NOTE.format(status=status, level=level, command=command, extra=extra),
        encoding="utf-8")
    return tmp_path


def _all_codes_for(repo: Path, note_id: str) -> list[str]:
    """Every code at any severity, so a WARNING is visible to these guards."""
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(repo)],
        capture_output=True, text=True, timeout=120).stdout
    return [ln.split("]")[0].split("[")[1]
            for ln in out.splitlines()
            if ln.lstrip().startswith(("ERROR", "WARN")) and "[" in ln and note_id in ln]


def _codes(repo: Path) -> list[str]:
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(repo)],
        capture_output=True, text=True, timeout=120).stdout
    return [ln.split("]")[0].split("[")[1]
            for ln in out.splitlines()
            if ln.startswith("ERROR [") and "TST-0009" in ln]


# ------------------------------------------------------- the widened domain

@pytest.mark.parametrize("status", ["passing", "failing"])
def test_an_automated_test_may_not_hold_a_verdict(tmp_path: Path, status: str) -> None:
    """The exemption that is gone: `passing` with a `command:` used to be legal.

    **Its own code, with a cutover** — independent review found this landed as
    a day-one error on a measurement taken in this repo only, while
    `your-trainer` at HEAD carries two violations. `ACCEPTANCE-STATUS` keeps
    its day-one error over `level: acceptance`, where the corpus really is
    clean; the command-bearing half is `TEST-AUTOMATED-STATUS` and warns.
    """
    repo = _repo(tmp_path, status=status, command='command: "pytest tests/x.py"\n')
    assert "TEST-AUTOMATED-STATUS" in _all_codes_for(repo, "TST-0009")


def test_ready_with_a_command_was_already_forbidden_and_still_errors(
    tmp_path: Path,
) -> None:
    """`ready` is not part of the widening and must not inherit its cutover.

    It was already an error with a `command:` before ADR-0038 — `ready` is what
    the `Run` obligation counts, so an automated check parked there reaches a
    badge nobody can act on (ADR-0027). Dating it would weaken a live rule
    under cover of a new one.
    """
    repo = _repo(tmp_path, status="ready", level="level: acceptance\n",
                 command='command: "pytest tests/x.py"\n')
    assert "ACCEPTANCE-STATUS" in _all_codes_for(repo, "TST-0009")


@pytest.mark.parametrize("status", ["ready", "passing", "failing"])
def test_an_acceptance_check_still_may_not(tmp_path: Path, status: str) -> None:
    """The half that was already law, unchanged — 89 notes' worth."""
    repo = _repo(tmp_path, status=status, level="level: acceptance\n")
    assert "ACCEPTANCE-STATUS" in _codes(repo)


def test_a_manual_test_may_still_record_its_verdict(tmp_path: Path) -> None:
    """The 65 notes where `status:` is load-bearing are untouched.

    Deleting the verdict everywhere was the symmetrical option ADR-0038
    rejected: a manual test has no other place to put one.
    """
    repo = _repo(tmp_path, status="passing",
                 extra='last_verified: "2026-08-19"\nkind: manual\n')
    assert "ACCEPTANCE-STATUS" not in _codes(repo)


def test_an_automated_test_at_active_is_fine(tmp_path: Path) -> None:
    repo = _repo(tmp_path, status="active", command='command: "pytest tests/x.py"\n')
    assert _codes(repo) == []


# ------------------------------------------------------------- the evidence

@pytest.mark.parametrize("field", ["last_run", "exit_code"])
def test_evidence_of_a_run_is_refused(tmp_path: Path, field: str) -> None:
    repo = _repo(tmp_path, status="active",
                 command='command: "pytest tests/x.py"\n',
                 extra='%s: "1"\n' % field)
    assert "TEST-AUTOMATED-EVIDENCE" in _all_codes_for(repo, "TST-0009")


def test_a_manual_test_keeps_its_dates(tmp_path: Path) -> None:
    """`last_run:` on a note with no command is not this rule's business."""
    repo = _repo(tmp_path, status="active", extra='last_run: "2026-01-01"\n')
    assert "TEST-AUTOMATED-EVIDENCE" not in _codes(repo)


# ------------------------------------------------------------- the landing

def test_the_corpus_holds_no_violations(tmp_path: Path) -> None:
    """Why this errors on day one instead of warning.

    Asserted rather than claimed: if the migration had missed a note, the rule
    would be landing over unpaid debt, which ADR-0011 forbids.
    """
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(REPO_ROOT)],
        capture_output=True, text=True, timeout=300).stdout
    offenders = [ln for ln in out.splitlines()
                 if "ACCEPTANCE-STATUS" in ln or "TEST-AUTOMATED-EVIDENCE" in ln
                 or "TEST-AUTOMATED-STATUS" in ln]
    assert not offenders, offenders


# ------------------------------------------------- the write path (TASK-0563)

def test_the_cockpit_cannot_stamp_an_automated_note(tmp_path: Path) -> None:
    """`stamp_test_run` records a MANUAL run, and nothing stopped it being
    pointed at a note a machine executes.

    The write it performs is exactly the one the validator now refuses —
    `status`, `last_run`, and `last_verified` on a pass — so leaving it open
    would let the UI author, by hand, the state the corpus was just migrated
    out of. Refused rather than quietly downgraded to a no-op: "recorded
    nothing and said nothing" is how a person comes to believe a check is
    settled.
    """
    from project_os_cockpit import note_writes
    from project_os_cockpit.index import Index

    (tmp_path / "docs" / "tests").mkdir(parents=True)
    note = tmp_path / "docs" / "tests" / "TST-0009-A.md"
    note.write_text(
        '---\ntype: "[[test]]"\nid: TST-0009\ntitle: "a"\nstatus: active\n'
        'command: "pytest tests/x.py"\n---\n\n# body\n', encoding="utf-8")
    before = note.read_bytes()
    index = Index.build(tmp_path / "docs")

    with pytest.raises(note_writes.WriteError) as excinfo:
        note_writes.stamp_test_run(index, "TST-0009", outcome="passing", steps=[])
    assert "command" in str(excinfo.value)
    assert note.read_bytes() == before, "the refusal still wrote"


def test_a_manual_note_can_still_be_stamped(tmp_path: Path) -> None:
    """The 65 notes this path exists for are untouched."""
    from project_os_cockpit import note_writes
    from project_os_cockpit.index import Index

    (tmp_path / "docs" / "tests").mkdir(parents=True)
    note = tmp_path / "docs" / "tests" / "TST-0010-B.md"
    note.write_text(
        '---\ntype: "[[test]]"\nid: TST-0010\ntitle: "b"\nstatus: ready\n---\n\n# body\n',
        encoding="utf-8")
    index = Index.build(tmp_path / "docs")

    result = note_writes.stamp_test_run(index, "TST-0010", outcome="passing", steps=[])
    assert result["outcome"] == "passing"
    assert 'status: "passing"' in note.read_text(encoding="utf-8")


# ------------------------------------------------ the authoring rule (REQ-0060)

CHECK = """---
type: "[[test]]"
id: TST-0011
title: "a check"
status: active
level: acceptance
mark: " "
covers: {covers}
{command}---

# body
"""


def _check_repo(tmp_path: Path, *, covers="[]", command="") -> Path:
    (tmp_path / "docs" / "tests" / "acceptance").mkdir(parents=True)
    (tmp_path / "SNAPSHOT.yaml").write_text(
        "version: 1\ncounters:\n  TST: 11\nitems: {}\n", encoding="utf-8")
    (tmp_path / "docs" / "tests" / "acceptance" / "TST-0011-A.md").write_text(
        CHECK.format(covers=covers, command=command), encoding="utf-8")
    return tmp_path


def _all_codes(repo: Path) -> list[str]:
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(repo)],
        capture_output=True, text=True, timeout=120).stdout
    # The validator pads its severity column, so `WARN` arrives as `WARN  [`.
    return [ln.split("]")[0].split("[")[1]
            for ln in out.splitlines()
            if ln.lstrip().startswith(("ERROR", "WARN")) and "[" in ln
            and "TST-0011" in ln]


@pytest.mark.parametrize("covers", ['[]', '["[[PHASE-0013]]"]', '["[[TASK-0001]]"]'])
def test_a_check_naming_no_subject_is_reported(tmp_path: Path, covers: str) -> None:
    """`covers:` carrying provenance is the same conflation ISS-0235 found.

    Measured at HEAD, 2026-08-20: **117** checks in `your-trainer` and none in
    any other repo. They name only a `PHASE-*` or a `TASK-*`, or nothing —
    provenance rather than the thing verified. *(An earlier figure of 44 here
    was that repo's working tree, not its committed record.)*
    """
    assert "CHECK-SUBJECT" in _all_codes(_check_repo(tmp_path, covers=covers))


@pytest.mark.parametrize("covers", ['["[[FEAT-0001]]"]', '["[[ISS-0001]]"]'])
def test_a_check_naming_its_subject_is_fine(tmp_path: Path, covers: str) -> None:
    assert "CHECK-SUBJECT" not in _all_codes(_check_repo(tmp_path, covers=covers))


def test_an_automated_check_is_exempt(tmp_path: Path) -> None:
    """`command:` decides its section outright, so nothing is being guessed."""
    repo = _check_repo(tmp_path, covers="[]", command='command: "pytest tests/x.py"\n')
    assert "CHECK-SUBJECT" not in _all_codes(repo)


def test_it_warns_rather_than_errors_until_the_cutover(tmp_path: Path) -> None:
    """ADR-0011 clause 3: the debt is real and bounded, so it is dated.

    A check with a justification and no cutover is the permanent-warning tier
    that ADR forbids — the mistake TEST-ENTRYPOINT and STATUS-TYPE shipped with
    and were corrected for on the same day.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("v_promo", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.PROMOTIONS["CHECK-SUBJECT"] == "2026-11-18"
    # The two ADR-0038 codes are dated for the same reason and on the same
    # day: the fleet corpus is not clean, so neither may error on day one.
    assert module.PROMOTIONS["TEST-AUTOMATED-STATUS"] == "2026-11-18"
    assert module.PROMOTIONS["TEST-AUTOMATED-EVIDENCE"] == "2026-11-18"


# ------------------------------- the split, cut on what changed (3rd review)

@pytest.mark.parametrize("level,command,status,expected", [
    # **Newly forbidden by ADR-0038, therefore dated.** A command-bearing note
    # at `passing`/`failing` was EXEMPT before — that was the whole exception
    # the widening removes.
    ("level: acceptance\n", 'command: "pytest tests/x.py"\n', "passing", "TEST-AUTOMATED-STATUS"),
    ("level: acceptance\n", 'command: "pytest tests/x.py"\n', "failing", "TEST-AUTOMATED-STATUS"),
    ("", 'command: "pytest tests/x.py"\n', "passing", "TEST-AUTOMATED-STATUS"),
    # **Forbidden BEFORE ADR-0038, therefore still a day-one error.** `ready`
    # with a command was the exception-to-the-exception ADR-0031 kept, because
    # `ready` is what the `Run` obligation counts and it reaches the badge.
    ("level: acceptance\n", 'command: "pytest tests/x.py"\n', "ready", "ACCEPTANCE-STATUS"),
    ("level: acceptance\n", "", "passing", "ACCEPTANCE-STATUS"),
    ("level: acceptance\n", "", "ready", "ACCEPTANCE-STATUS"),
])
def test_the_split_follows_what_changed_not_the_level(
    tmp_path: Path, level: str, command: str, status: str, expected: str,
) -> None:
    """**Cutting this on `level:` sent 64% of the widened domain to the wrong side.**

    Third independent review, 2026-08-20: the first split branched on
    `level == "acceptance"` first, so a note that is *both* an acceptance check
    and command-bearing never reached the dated code — 89 of the fleet's 139
    automated notes erroring on day one over a rule they had no chance to
    satisfy, in repos that still ship the `run-tests.py` which writes those
    statuses. ADR-0011 clause 3, and the exact failure the dating existed to
    avoid.

    The line is not `level:`. It is *what ADR-0038 newly forbids*.
    """
    repo = _repo(tmp_path, status=status, level=level, command=command)
    codes = _all_codes_for(repo, "TST-0009")
    assert expected in codes, codes
    other = {"TEST-AUTOMATED-STATUS", "ACCEPTANCE-STATUS"} - {expected}
    assert not (other & set(codes)), (codes, "reported under both codes")


def test_nothing_that_errored_before_merely_warns_now(tmp_path: Path) -> None:
    """A split is an easy place to downgrade a case by accident."""
    repo = _repo(tmp_path, status="ready", level="level: acceptance\n",
                 command='command: "pytest tests/x.py"\n')
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(repo)],
        capture_output=True, text=True, timeout=120).stdout
    line = next(l for l in out.splitlines()
                if "TST-0009" in l and "ACCEPTANCE-STATUS" in l)
    assert line.startswith("ERROR"), line
