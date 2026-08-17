"""The `check` type sits outside the test gates, and the gates say so (TASK-0459).

[[ADR-0030]] gives acceptance checks their own note type rather than reusing
`TST-*`, and its whole argument is that five collisions vanish **by
construction** rather than by exemption logic. A test that only asserted the
type exists would not check that claim at all — so every assertion here is
about a gate NOT firing, and each one names the gate it is about.

The corpus is built rather than borrowed: the live one is about to acquire 34
real checks, and a guard that reads them would pass for the wrong reason the
moment somebody marks one.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from project_os_cockpit import obligations
from project_os_cockpit.index import Index

REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = REPO_ROOT / "tools" / "scripts" / "validate-docs.py"

#: A check with a real verdict on it — the state the gates are asked about.
#: `mark: "!"` is deliberately the *failed* mark: if any gate were keyed on
#: something other than `status:`, a failed check is where it would show.
CHECK_NOTE = """---
type: "[[check]]"
id: CHK-0001
aliases: ["CHK-0001"]
title: "The navigator opens on what is owed"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "The navigator"
section: "1.3"
ordinal: 10
mark: "!"
verdict_date: 2026-08-17
verdict_reason: "the tray was empty with three items at triage"
automation: manual
covers: []
---

# The navigator opens on what is owed

Open the navigator. Expect the triage tray first.
"""

SNAPSHOT = """version: 1
updated: "2026-08-17T00:00Z"
project:
  name: "probe"
  repo_root: "."
focus:
  task: ""
  feature: ""
  phase: ""
  issue: ""
  note: ""
counters:
  CHK: 1
items: {}
"""


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """A minimal project-os repo holding exactly one check."""
    docs = tmp_path / "docs" / "tests" / "acceptance"
    docs.mkdir(parents=True)
    (docs / "CHK-0001-The-Navigator.md").write_text(CHECK_NOTE, encoding="utf-8")
    (tmp_path / "SNAPSHOT.yaml").write_text(SNAPSHOT, encoding="utf-8")
    return tmp_path


def _validate(root: Path) -> tuple[int, str]:
    done = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(root)],
        capture_output=True, text=True,
    )
    return done.returncode, done.stdout + done.stderr


# --------------------------------------------------------------- the validator

def test_a_check_with_a_verdict_validates(repo: Path) -> None:
    """The first exemption: nothing about `mark:` is a validator subject.

    A `CHK-*` carrying a failed verdict and an untouched `status:` is the
    normal steady state of an acceptance suite between walks. If it did not
    validate, every repo would be red for as long as anything was unwalked.
    """
    code, out = _validate(repo)
    assert code == 0, out


def test_the_check_fires_no_review_no_runner_and_no_entrypoint(repo: Path) -> None:
    """The three gates ADR-0030 names, each keyed on something a check lacks.

    REVIEW gates a `TST-*` reaching `passing`; TEST-FIELDS/TEST-ENTRYPOINT gate
    a `test` note's runner contract; STATUS-TYPE fires on a type with no status
    table. A check reaches none of them — and the point is that this holds
    because the type is a sibling, not because a special case was written.
    """
    _code, out = _validate(repo)
    for line in out.splitlines():
        if "CHK-0001" not in line and "CHK-0001-The-Navigator" not in line:
            continue
        assert not any(
            gate in line for gate in
            ("REVIEW", "TEST-ENTRYPOINT", "TEST-FIELDS", "STATUS-TYPE")
        ), f"a check tripped a test gate: {line}"


def test_status_type_is_silent_about_the_check_type(repo: Path) -> None:
    """The type is KNOWN, which is the condition STATUS-TYPE reports on."""
    _code, out = _validate(repo)
    assert "note type 'check'" not in out, out


def test_the_counter_covers_checks(repo: Path) -> None:
    """`counters.CHK` is enforced like any other prefix.

    Without `CHK` in the validator's `ID_PREFIXES`, `check_counter` returns
    before it can compare anything — so a corpus could allocate any id it
    liked and nothing would say so. Asserted by making the counter too low and
    requiring the complaint.
    """
    snap = repo / "SNAPSHOT.yaml"
    snap.write_text(SNAPSHOT.replace("CHK: 1", "CHK: 0"), encoding="utf-8")
    code, out = _validate(repo)
    assert code != 0 and "COUNTER" in out and "CHK-0001" in out, out


# --------------------------------------------------------------- the registry

def test_check_is_declared_owed_nothing() -> None:
    """ADR-0030's second exemption, and the one it calls its own biggest risk."""
    ob = obligations.for_type("check")
    assert ob is not None, "the `check` type is undeclared in the registry"
    assert not ob.owed, "a check must never owe a person anything"
    assert "ADR-0030" in ob.reason


def test_no_check_ever_reaches_a_badge(repo: Path) -> None:
    """The guarantee that outranks every surface in this phase.

    Not *"the registry says none"* — that is the line above. This walks a real
    corpus containing a check with a failing verdict and asserts the payloads a
    badge is built from carry nothing about it. A per-check obligation is the
    granularity's most tempting use and the one thing forbidden outright.
    """
    index = Index.build(repo / "docs")
    owed = obligations.owed_items(index)
    for kind, rows in owed.items():
        for row in rows:
            assert not str(row.get("id", "")).startswith("CHK-"), (
                f"a check reached the {kind} obligation group: {row}"
            )
    assert "check" not in obligations.counts_by_kind(index)
    assert obligations.counts(index).get("check", 0) == 0


# ----------------------------------------------------------- the status tables

def test_a_check_can_never_hold_a_runner_status() -> None:
    """Why the collisions vanish by construction.

    Both the runner-only rule and the review gate are keyed on `passing`. A
    vocabulary that cannot express it cannot trip either, whatever a future
    edit does to the checks around it.
    """
    from project_os_cockpit import validate_docs_bundled as v

    assert v.ALLOWED_STATUS["check"] == {"draft", "active", "retired"}
    assert not v.ALLOWED_STATUS["check"] & set(v.TEST_RUNNER_STATUSES)
    for collection in v.REVIEW_SETTLED_STATUSES:
        assert "check" not in v.COLLECTION_TYPE.get(collection, set())


def test_retiring_a_check_is_not_gated_on_a_test() -> None:
    """`retired` is terminal and deliberately disclaimed in the verify gate.

    A check is verified by being walked. Demanding a linked passing test before
    one may be retired would gate a human judgement on an automated one — safe
    today only because `items.checks` is always empty, which is a trap for
    whoever first fills it rather than a guarantee.
    """
    src = (REPO_ROOT / "tools" / "scripts" / "validate-docs.py").read_text(encoding="utf-8")
    assert 'if coll_name == "checks":\n                terminal = None' in src
