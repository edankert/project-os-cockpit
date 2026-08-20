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

**What landed at zero violations was this repo, not the fleet** — a distinction
three independent review passes were needed to force. Measured at HEAD across
every repo carrying a test note: `TEST-AUTOMATED-STATUS` 12,
`TEST-AUTOMATED-EVIDENCE` 24, `CHECK-SUBJECT` 117, and `ACCEPTANCE-STATUS`
**0 everywhere**. So only the last errors from day one; the three carrying debt
are dated to 2026-11-18, because ADR-0011 clause 3 forbids promoting over unpaid
debt and `DECISIONS.md`'s skip-the-warning rule needs a corpus that is clean
*everywhere*, not where the author happened to look.
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
    """Why the corpus was thought clean — and why that was only this repo.

    Asserted rather than claimed, but the assertion is about
    `project-os-cockpit` alone. Reading it as a fleet statement is exactly the
    mistake that dated three rules a review too late; the fleet figures are in
    the module docstring above.
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

#: **The whole cross-product, because a six-case sample missed a cell.**
#:
#: `level` present/absent x `command` present/absent x four statuses. The
#: fourth independent review executed all 24 (three of the statuses plus
#: `active`, at both levels, with and without a command) and found exactly one
#: disagreement with the note: command-bearing, NOT an acceptance check, at
#: `ready` had fallen **silent** — it fails `TEST_RUNNER_STATUSES` and the
#: `elif level == "acceptance"` does not catch it. It had warned one commit
#: earlier.
#:
#: A sample cannot find that. The table can, and every cell is written out
#: rather than computed, so a rule change has to edit the expectation it
#: breaks rather than quietly agreeing with itself.
_SPLIT_MATRIX = [
    # (level, command, status, code, severity)
    # --- acceptance checks a person completes: unchanged since ADR-0031 -----
    ("acceptance", False, "ready",   "ACCEPTANCE-STATUS", "ERROR"),
    ("acceptance", False, "passing", "ACCEPTANCE-STATUS", "ERROR"),
    ("acceptance", False, "failing", "ACCEPTANCE-STATUS", "ERROR"),
    ("acceptance", False, "active",  None,                None),
    # --- acceptance AND automated ------------------------------------------
    # `ready` was already an error with a command: it is what the `Run`
    # obligation counts, so an automated check parked there reaches a badge
    # nobody can act on (ADR-0027). Dating it would weaken a live rule.
    ("acceptance", True,  "ready",   "ACCEPTANCE-STATUS",    "ERROR"),
    # `passing`/`failing` were EXEMPT with a command. That exemption is what
    # ADR-0038 removes, so these are the dated half.
    ("acceptance", True,  "passing", "TEST-AUTOMATED-STATUS", "WARN"),
    ("acceptance", True,  "failing", "TEST-AUTOMATED-STATUS", "WARN"),
    ("acceptance", True,  "active",  None,                    None),
    # --- automated, not an acceptance check: NO rule reached these before ---
    ("",           True,  "ready",   "TEST-AUTOMATED-STATUS", "WARN"),
    ("",           True,  "passing", "TEST-AUTOMATED-STATUS", "WARN"),
    ("",           True,  "failing", "TEST-AUTOMATED-STATUS", "WARN"),
    ("",           True,  "active",  None,                    None),
    # --- a manual test outside the acceptance level: not this rule's business
    ("",           False, "ready",   None, None),
    ("",           False, "passing", None, None),
    ("",           False, "failing", None, None),
    ("",           False, "active",  None, None),
]


@pytest.mark.parametrize("level,command,status,code,severity", _SPLIT_MATRIX,
                         ids=lambda v: str(v))
def test_the_split_follows_what_changed_not_the_level(
    tmp_path: Path, level: str, command: bool, status: str,
    code: str | None, severity: str | None,
) -> None:
    """**Cutting this on `level:` sent 64% of the widened domain to the wrong side.**

    The third independent review found the first split branching on
    `level == "acceptance"` first, so a note that is *both* an acceptance check
    and command-bearing never reached the dated code — erroring on day one over
    a rule it had no chance to satisfy, in repos that still ship the
    `run-tests.py` which writes those statuses.

    The line is not `level:`. It is *what ADR-0038 newly forbids*, which is
    (the rule after) minus (the rule before) — and that difference is not
    expressible as a single field test, which is why it is tabulated.
    """
    repo = _repo(
        tmp_path, status=status,
        level=("level: %s\n" % level) if level else "",
        command='command: "pytest tests/x.py"\n' if command else "",
        extra="" if command or status != "passing" else 'last_verified: "2026-08-01"\nkind: manual\n',
    )
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(repo)],
        capture_output=True, text=True, timeout=120).stdout
    lines = [ln for ln in out.splitlines()
             if "TST-0009" in ln
             and ("ACCEPTANCE-STATUS" in ln or "TEST-AUTOMATED-STATUS" in ln)]
    if code is None:
        assert not lines, ("expected silence", lines)
        return
    assert len(lines) == 1, lines
    assert code in lines[0], lines[0]
    assert lines[0].startswith(severity), lines[0]


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
