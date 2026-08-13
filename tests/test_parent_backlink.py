"""PARENT-BACKLINK: a relationship declared on one end is declared on both
(FEAT-0081 / TASK-0353, ISS-0112).

The drift this exists for: FEAT-0081 closed as `done` while its note listed
three of its five tasks and none of the issues it fixed. The tasks named
their parent, `SNAPSHOT.yaml` agreed with the tasks, and the feature knew
about neither — so the feature's Acceptance section was missing criteria
for half its delivered behaviour, and every gate in the repo passed.

These cases run the real validator over a throwaway docs tree, so they
fail when the check stops firing rather than when a literal moves.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "tools" / "scripts" / "validate-docs.py"

FEATURE = """---
type: "[[feature]]"
id: FEAT-0001
title: "A feature"
status: doing
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
goal: "g"
tasks: [{tasks}]
fixes: [{fixes}]
---

# A feature

## Acceptance
- [ ] something
"""

TASK = """---
type: "[[task]]"
id: TASK-0001
title: "A task"
status: backlog
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
parent: "[[FEAT-0001]]"
---

# A task

## Definition of Done
- [ ] something
"""

ISSUE = """---
type: "[[issue]]"
id: ISS-0001
title: "An issue"
status: triage
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
severity: low
parent: "[[FEAT-0001]]"
---

# An issue

## Problem
x
"""

SNAPSHOT = """version: 1
updated: "2026-08-06T00:00Z"
template:
  replace_me: false
project:
  name: "t"
  summary: "t"
  repo_root: "."
counters:
  FEAT: 1
  TASK: 1
  ISS: 1
focus:
  task: ""
  feature: ""
  phase: ""
  issue: ""
items:
  features: {}
  tasks: {}
  issues: {}
"""


def _tree(tmp_path: Path, *, tasks: str, fixes: str,
          with_task: bool = True, with_issue: bool = False) -> Path:
    root = tmp_path / "repo"
    (root / "docs" / "features" / "f" / "plan" / "tasks").mkdir(parents=True)
    (root / "docs" / "issues").mkdir(parents=True)
    (root / "SNAPSHOT.yaml").write_text(SNAPSHOT, encoding="utf-8")
    (root / "docs" / "features" / "f" / "FEAT-0001-A-Feature.md").write_text(
        FEATURE.format(tasks=tasks, fixes=fixes), encoding="utf-8")
    if with_task:
        (root / "docs" / "features" / "f" / "plan" / "tasks"
         / "TASK-0001-A-Task.md").write_text(TASK, encoding="utf-8")
    if with_issue:
        (root / "docs" / "issues" / "ISS-0001-An-Issue.md").write_text(
            ISSUE, encoding="utf-8")
    return root


def _run(root: Path) -> str:
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(root)],
        capture_output=True, text=True, timeout=60,
    )
    out = proc.stdout + proc.stderr
    # A usage error contains no gate name, so an `assert "X" not in out`
    # would pass on a broken invocation. Fail loudly instead.
    assert "usage:" not in out.split("\n")[0], f"validator did not run:\n{out}"
    return out


def _assert_error(out: str, code: str) -> None:
    """Assert the code appears **as an error**, not merely somewhere (ISS-0120).

    Severity is the whole point of a gate: a check that warns is a check the
    pre-commit hook and CI both ignore. Every synthetic case here used to
    assert the bare code, and `out` carries both tiers — so replacing
    `emit_for(...)` with `report.warn` left all eleven passing, which is
    precisely the edit that silently disables the gate.

    Found by mutation during round 4 of FEAT-0081's independent review, not by
    reading, which is the argument for mutating a suite you are relying on.
    """
    assert f"ERROR [{code}]" in out, (
        f"{code} did not fire as an ERROR — a warning is a gate nobody "
        f"enforces:\n{out}"
    )


def _assert_absent(out: str, code: str) -> None:
    """Neither tier: a clean tree must not warn about this either."""
    assert code not in out, out


def test_a_task_its_feature_does_not_list_is_an_error(tmp_path: Path) -> None:
    """The drift exactly as it existed on FEAT-0081."""
    out = _run(_tree(tmp_path, tasks="", fixes=""))
    _assert_error(out, "PARENT-BACKLINK")
    assert "TASK-0001" in out and "FEAT-0001" in out


def test_a_listed_task_is_clean(tmp_path: Path) -> None:
    out = _run(_tree(tmp_path, tasks='"[[TASK-0001]]"', fixes=""))
    _assert_absent(out, "PARENT-BACKLINK")


def test_an_issue_its_feature_does_not_list_is_an_error(tmp_path: Path) -> None:
    out = _run(_tree(tmp_path, tasks='"[[TASK-0001]]"', fixes="",
                     with_issue=True))
    _assert_error(out, "PARENT-BACKLINK")
    assert "ISS-0001" in out


def test_an_issue_listed_under_fixes_is_clean(tmp_path: Path) -> None:
    out = _run(_tree(tmp_path, tasks='"[[TASK-0001]]"', fixes='"ISS-0001"',
                     with_issue=True))
    _assert_absent(out, "PARENT-BACKLINK")


def test_related_alone_does_not_satisfy_the_check(tmp_path: Path) -> None:
    """A check that accepted any mention would pass the drift it exists to
    catch — `related:` is not a declaration of ownership."""
    root = _tree(tmp_path, tasks="", fixes="")
    note = root / "docs" / "features" / "f" / "FEAT-0001-A-Feature.md"
    note.write_text(
        note.read_text(encoding="utf-8").replace(
            "fixes: []", 'fixes: []\nrelated: ["[[TASK-0001]]"]'),
        encoding="utf-8")
    _assert_error(_run(root), "PARENT-BACKLINK")


def test_the_real_repo_has_no_new_backlink_errors() -> None:
    """This repo passes its own new gate.

    69 pre-existing violations are in `tools/GRANDFATHERED.yaml` and warn
    rather than error — the mechanism ADR-0011 provides for a gate
    promoted over standing debt. Each one is a small backlog item, and
    the ledger only shrinks. What matters is that *new* drift errors:
    the FEAT-0081 case this gate was written for would now fail.
    """
    out = _run(REPO_ROOT)
    assert "ERROR [PARENT-BACKLINK]" not in out, out


def test_the_ledger_only_covers_debt_that_still_exists() -> None:
    """A grandfathered id that no longer violates is inert but misleading
    — the ledger's own header says it only shrinks."""
    import re
    ledger = (REPO_ROOT / "tools" / "GRANDFATHERED.yaml").read_text(encoding="utf-8")
    block = ledger.split("  PARENT-BACKLINK:\n", 1)
    if len(block) < 2:
        return
    listed = set(re.findall(r"^    (\S+):", block[1].split("  TEST-FIELDS:")[0], re.M))
    out = _run(REPO_ROOT)
    warned = set(re.findall(r"WARN\s+\[PARENT-BACKLINK\] (\S+)", out))
    stale = listed - warned
    assert not stale, f"ledger lists ids that no longer violate: {sorted(stale)}"


# ---- SNAPSHOT-MEMBERSHIP (FEAT-0081 / ISS-0117) -----------------------
#
# PARENT-BACKLINK walks note frontmatter, so the snapshot's own copy of a
# feature's task list was unguarded. FEAT-0081 spent four review rounds
# with five tasks there against thirteen everywhere else, twice recorded
# as repaired without being repaired — both attempts were string replaces
# whose pattern no longer matched, and neither asserted the match.

def _snapshot_with(tasks_in_note: str, tasks_in_snapshot: str) -> str:
    return SNAPSHOT.replace(
        "  features: {}",
        '  features:\n    FEAT-0001:\n      title: "A feature"\n'
        '      status: doing\n'
        f'      tasks: [{tasks_in_snapshot}]\n')


def test_snapshot_disagreeing_with_the_note_is_an_error(tmp_path: Path) -> None:
    root = _tree(tmp_path, tasks='"[[TASK-0001]]"', fixes="")
    (root / "SNAPSHOT.yaml").write_text(
        _snapshot_with('"[[TASK-0001]]"', ""), encoding="utf-8")
    out = _run(root)
    _assert_error(out, "SNAPSHOT-MEMBERSHIP")
    assert "TASK-0001" in out


def test_snapshot_agreeing_with_the_note_is_clean(tmp_path: Path) -> None:
    root = _tree(tmp_path, tasks='"[[TASK-0001]]"', fixes="")
    (root / "SNAPSHOT.yaml").write_text(
        _snapshot_with('"[[TASK-0001]]"', "TASK-0001"), encoding="utf-8")
    _assert_absent(_run(root), "SNAPSHOT-MEMBERSHIP")


def test_a_task_only_in_the_snapshot_is_also_an_error(tmp_path: Path) -> None:
    """Drift in either direction: the note is the authored source
    (ADR-0009), so a snapshot-only task is the snapshot being wrong."""
    root = _tree(tmp_path, tasks="", fixes="", with_task=False)
    (root / "SNAPSHOT.yaml").write_text(
        _snapshot_with("", "TASK-0009"), encoding="utf-8")
    out = _run(root)
    _assert_error(out, "SNAPSHOT-MEMBERSHIP")
    assert "TASK-0009" in out


def test_the_real_repo_has_no_membership_drift() -> None:
    assert "ERROR [SNAPSHOT-MEMBERSHIP]" not in _run(REPO_ROOT)
