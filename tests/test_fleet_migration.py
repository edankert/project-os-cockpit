"""The fleet backlink reconciliation writes only what the notes declare (TST-0080).

`tools/scripts/migrate-fleet-validator.py` edits feature notes and `SNAPSHOT.yaml`
across four repos and 3993 hand-written notes (ISS-0209, FEAT-0143). The census
(TASK-0579) showed the whole migration is two rules -- `PARENT-BACKLINK` and
`SNAPSHOT-MEMBERSHIP` -- which are one relationship seen from its two ends, so
the tool performs one operation and everything here is about *that operation not
overreaching*:

  - it writes the parent from the child, never the child from the parent;
  - a second run changes nothing;
  - a note that is already correct is not touched AT ALL, byte for byte, because
    a YAML round-trip over this corpus would be a silent 3993-file diff;
  - a `parent:` naming a note that does not exist creates no membership.

Every test drives the real module against real files in a tmp repo. The
`plan_backlinks` half is deliberately driven through the *upstream validator's*
own `build_note_index`/`extract_ids` -- the same functions the rule uses -- so a
test cannot pass by agreeing with a second opinion about which notes exist.
"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
UPSTREAM = Path.home() / "Dev" / "repos" / "project-os"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


mig = _load("_migrate_fleet_validator", REPO / "tools" / "scripts" / "migrate-fleet-validator.py")


@pytest.fixture(scope="module")
def validator():
    """Upstream's validator if it is on this machine, else this repo's.

    This repo's copy is a superset of upstream's for every function used here
    (`build_note_index`, `extract_ids`, `note_type`, `prefix_of`, `ID_RE`), so
    the fallback keeps the module runnable on a clean CI checkout that has no
    sibling `project-os`. TST-0079's lesson: a suite that only runs on the
    authoring machine has never run.
    """
    root = UPSTREAM if (UPSTREAM / "tools" / "scripts" / "validate-docs.py").is_file() else REPO
    return mig.load_validator(root)


FEATURE = """---
type: "[[feature]]"
id: {fid}
aliases: ["{fid}"]
title: "A feature"
status: doing
owner: user:edwin
created: 2026-08-29
updated: 2026-08-29
goal: "Something"
requirements: []
{tasks}related:
  - "[[SOMETHING-ELSE]]"
---

# A feature

Body text that must survive untouched.
"""

TASK = """---
type: "[[task]]"
id: {tid}
aliases: ["{tid}"]
title: "A task"
status: done
owner: user:edwin
created: 2026-08-29
updated: 2026-08-29
parent: "{parent}"
---

# A task
"""

ISSUE = """---
type: "[[issue]]"
id: {iid}
aliases: ["{iid}"]
title: "An issue"
status: fixed
owner: user:edwin
created: 2026-08-29
updated: 2026-08-29
severity: low
component: tooling
parent: "{parent}"
---

# An issue
"""

SNAPSHOT = """version: 1
project:
  name: "fixture"
counters:
  FEAT: 1
  TASK: 3
items:
  features:
    # A load-bearing comment: this must survive the rewrite.
    FEAT-0001:
      title: "A feature"
      status: doing
{snap_tasks}      file: "docs/features/FEAT-0001-A-Feature.md"
"""


def build_repo(tmp_path, *, feature_tasks="", snap_tasks="", tasks=(("TASK-0001", "FEAT-0001"),),
               issues=()):
    root = tmp_path / "repo"
    (root / "docs" / "features").mkdir(parents=True)
    (root / "docs" / "tasks").mkdir(parents=True)
    (root / "docs" / "issues").mkdir(parents=True)
    (root / "docs" / "features" / "FEAT-0001-A-Feature.md").write_text(
        FEATURE.format(fid="FEAT-0001", tasks=feature_tasks), encoding="utf-8")
    for tid, parent in tasks:
        (root / "docs" / "tasks" / ("%s-A-Task.md" % tid)).write_text(
            TASK.format(tid=tid, parent=parent), encoding="utf-8")
    for iid, parent in issues:
        (root / "docs" / "issues" / ("%s-An-Issue.md" % iid)).write_text(
            ISSUE.format(iid=iid, parent=parent), encoding="utf-8")
    (root / "SNAPSHOT.yaml").write_text(SNAPSHOT.format(snap_tasks=snap_tasks), encoding="utf-8")
    return root


def run(validator, root, dry_run=False):
    index, _ = validator.build_note_index(root / "docs")
    plan = mig.plan_backlinks(validator, index)
    written, unhandled = mig.apply_plan(validator, index, plan, dry_run)
    assert unhandled == [], unhandled
    index2, _ = validator.build_note_index(root / "docs")
    snap = mig.reconcile_snapshot(validator, root, index2, dry_run,
                                  mig.planned_tasks(validator, plan) if dry_run else None)
    return plan, written, snap


# ------------------------------------------------------- the direction of fit

def test_the_feature_learns_the_tasks_that_declare_it(tmp_path, validator):
    root = build_repo(tmp_path, tasks=(("TASK-0001", "FEAT-0001"), ("TASK-0002", "FEAT-0001")))
    _plan, written, _snap = run(validator, root)
    assert len(written) == 1
    text = (root / "docs" / "features" / "FEAT-0001-A-Feature.md").read_text()
    assert "TASK-0001-A-Task" in text and "TASK-0002-A-Task" in text
    index, _ = validator.build_note_index(root / "docs")
    assert mig.plan_backlinks(validator, index).additions == {}


def test_an_issue_goes_to_the_issues_field_not_the_tasks_field(tmp_path, validator):
    root = build_repo(tmp_path, tasks=(), issues=(("ISS-0001", "FEAT-0001"),))
    _plan, written, _snap = run(validator, root)
    assert [w[1] for w in written] == ["issues"]
    text = (root / "docs" / "features" / "FEAT-0001-A-Feature.md").read_text()
    assert 'issues:\n  - "[[ISS-0001-An-Issue]]"' in text


def test_an_issue_already_named_in_fixes_is_not_copied_into_issues(tmp_path, validator):
    """`PARENT-BACKLINK` accepts `fixes:` OR `issues:`; satisfying one satisfies it.

    Judging satisfaction on the write-target alone would duplicate every issue a
    repo happens to record under `fixes:` into a second field, on a corpus where
    57 of the 1044 findings are issues.
    """
    root = build_repo(tmp_path, tasks=(), issues=(("ISS-0001", "FEAT-0001"),),
                      feature_tasks='fixes: ["[[ISS-0001-An-Issue]]"]\n')
    before = (root / "docs" / "features" / "FEAT-0001-A-Feature.md").read_bytes()
    plan, written, _snap = run(validator, root)
    assert plan.additions == {} and written == []
    assert (root / "docs" / "features" / "FEAT-0001-A-Feature.md").read_bytes() == before


def test_the_child_is_never_written_from_the_parent(tmp_path, validator):
    """A feature naming a task that does not claim it is REPORTED and kept.

    The opposite -- teaching the task a `parent:` it never declared, or deleting
    the entry -- both invent state. `PARENT-BACKLINK` only ever fires on a
    missing back-reference, so neither is a repair.
    """
    root = build_repo(tmp_path, tasks=(("TASK-0002", ""),),
                      feature_tasks='tasks: ["[[TASK-0002-A-Task]]"]\n')
    task_before = (root / "docs" / "tasks" / "TASK-0002-A-Task.md").read_bytes()
    feat_before = (root / "docs" / "features" / "FEAT-0001-A-Feature.md").read_bytes()
    plan, written, _snap = run(validator, root)
    assert ("FEAT-0001", "tasks", "TASK-0002") in plan.unclaimed
    assert written == []
    assert (root / "docs" / "tasks" / "TASK-0002-A-Task.md").read_bytes() == task_before
    assert (root / "docs" / "features" / "FEAT-0001-A-Feature.md").read_bytes() == feat_before


def test_a_dangling_parent_creates_no_membership(tmp_path, validator):
    root = build_repo(tmp_path, tasks=(("TASK-0001", "FEAT-9999"),))
    plan, written, _snap = run(validator, root)
    assert ("TASK-0001", "FEAT-9999") in plan.dangling
    assert written == []
    assert "FEAT-9999" not in (root / "SNAPSHOT.yaml").read_text()


# ------------------------------------------------------------- not overreaching

def test_a_correct_note_is_not_touched_byte_for_byte(tmp_path, validator):
    """The load-bearing assertion of this module.

    3993 notes, hand-written over months, with hard-wrapped prose and comments
    in frontmatter. A rewrite that reorders keys or reflows a string is a whole-
    corpus diff that reads as a one-line change. So the tool compares ID SETS
    and only a genuine difference is allowed to touch bytes.
    """
    root = build_repo(tmp_path, feature_tasks='tasks: [ "[[TASK-0001-A-Task]]" ]   # spaced oddly on purpose\n',
                      snap_tasks='      tasks: ["TASK-0001"]\n')
    before = (root / "docs" / "features" / "FEAT-0001-A-Feature.md").read_bytes()
    snap_before = (root / "SNAPSHOT.yaml").read_bytes()
    plan, written, snap = run(validator, root)
    assert plan.additions == {} and written == [] and snap == []
    assert (root / "docs" / "features" / "FEAT-0001-A-Feature.md").read_bytes() == before
    assert (root / "SNAPSHOT.yaml").read_bytes() == snap_before


def test_a_second_run_changes_nothing(tmp_path, validator):
    root = build_repo(tmp_path, tasks=(("TASK-0001", "FEAT-0001"), ("TASK-0002", "FEAT-0001")))
    run(validator, root)
    after_first = {p: p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}
    plan, written, snap = run(validator, root)
    assert plan.additions == {} and written == [] and snap == []
    assert {p: p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()} == after_first


def test_dry_run_reports_the_same_writes_and_makes_none(tmp_path, validator):
    root = build_repo(tmp_path, tasks=(("TASK-0001", "FEAT-0001"), ("TASK-0002", "FEAT-0001")))
    before = {p: p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}
    _plan, dry_written, dry_snap = run(validator, root, dry_run=True)
    assert {p: p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()} == before
    _plan, wet_written, wet_snap = run(validator, root)
    assert [(w[0], w[1], w[2]) for w in dry_written] == [(w[0], w[1], w[2]) for w in wet_written]
    assert dry_snap == wet_snap


def test_the_body_and_the_other_frontmatter_keys_survive(tmp_path, validator):
    root = build_repo(tmp_path, tasks=(("TASK-0001", "FEAT-0001"),))
    run(validator, root)
    text = (root / "docs" / "features" / "FEAT-0001-A-Feature.md").read_text()
    assert "Body text that must survive untouched." in text
    assert 'goal: "Something"' in text
    assert '  - "[[SOMETHING-ELSE]]"' in text
    assert text.count("\n---\n") == 1


# ------------------------------------------------------------------- snapshot

def test_the_snapshot_follows_the_note_and_keeps_its_comments(tmp_path, validator):
    root = build_repo(tmp_path, tasks=(("TASK-0001", "FEAT-0001"), ("TASK-0002", "FEAT-0001")),
                      snap_tasks='      tasks: ["TASK-0003"]\n')
    _plan, _written, snap = run(validator, root)
    text = (root / "SNAPSHOT.yaml").read_text()
    assert ("FEAT-0001", 1, 2) in snap
    assert '      tasks: ["TASK-0001", "TASK-0002"]' in text
    assert "# A load-bearing comment: this must survive the rewrite." in text
    assert 'file: "docs/features/FEAT-0001-A-Feature.md"' in text


def test_the_snapshot_gains_the_key_when_it_has_none(tmp_path, validator):
    root = build_repo(tmp_path, tasks=(("TASK-0001", "FEAT-0001"),), snap_tasks="")
    _plan, _written, snap = run(validator, root)
    assert ("FEAT-0001", 0, 1) in snap
    text = (root / "SNAPSHOT.yaml").read_text()
    assert '      tasks: ["TASK-0001"]' in text
    assert 'file: "docs/features/FEAT-0001-A-Feature.md"' in text


def test_a_block_sequence_in_the_snapshot_is_read_whole(tmp_path, validator):
    """Reading only the `tasks:` line would see an empty list and rewrite a
    correct entry on every run -- an idempotence break that only shows up in a
    repo that happens to use block style."""
    root = build_repo(tmp_path, tasks=(("TASK-0001", "FEAT-0001"),),
                      feature_tasks='tasks: ["[[TASK-0001-A-Task]]"]\n',
                      snap_tasks='      tasks:\n        - "TASK-0001"\n')
    snap_before = (root / "SNAPSHOT.yaml").read_bytes()
    _plan, _written, snap = run(validator, root)
    assert snap == []
    assert (root / "SNAPSHOT.yaml").read_bytes() == snap_before


# --------------------------------------------------------- the rule agrees

def test_the_migration_makes_the_upstream_rules_stop_firing(tmp_path, validator):
    """End to end, against the real validator rather than against this module's
    idea of it: a corpus that reports both rules must report neither afterwards."""
    root = build_repo(tmp_path, tasks=(("TASK-0001", "FEAT-0001"), ("TASK-0002", "FEAT-0001")),
                      snap_tasks='      tasks: ["TASK-0003"]\n')
    up = UPSTREAM / "tools" / "scripts" / "validate-docs.py"
    if not up.is_file():
        pytest.skip("no sibling project-os checkout to run the real validator from")

    def findings():
        proc = subprocess.run([sys.executable, str(up), "--repo-root", str(root)],
                              capture_output=True, text=True)
        return [l for l in proc.stdout.splitlines()
                if "PARENT-BACKLINK" in l or "SNAPSHOT-MEMBERSHIP" in l]

    assert findings(), "fixture must reproduce the finding, or this proves nothing"
    run(validator, root)
    assert findings() == []


def test_a_one_line_flow_mapping_in_the_snapshot_is_reconciled(tmp_path, validator):
    """`your-trainer` writes every snapshot feature as a one-line flow mapping.

    The block-form reader matched none of them, so the first real run there
    reported "0 snapshot entries" and left 33 SNAPSHOT-MEMBERSHIP errors standing
    in the largest repo in the fleet -- a migration reporting success against
    work it had not done.
    """
    root = build_repo(tmp_path, tasks=(("TASK-0001", "FEAT-0001"), ("TASK-0002", "FEAT-0001")))
    snap = root / "SNAPSHOT.yaml"
    snap.write_text(snap.read_text().replace(
        '    FEAT-0001:\n      title: "A feature"\n      status: doing\n'
        '      file: "docs/features/FEAT-0001-A-Feature.md"\n',
        '    FEAT-0001: { file: "docs/features/FEAT-0001-A-Feature.md", '
        'title: "A feature", status: doing }\n'), encoding="utf-8")
    _plan, _written, changes = run(validator, root)
    assert ("FEAT-0001", 0, 2) in changes
    text = snap.read_text()
    assert 'tasks: ["TASK-0001", "TASK-0002"]' in text
    assert 'file: "docs/features/FEAT-0001-A-Feature.md"' in text
    assert 'status: doing' in text
    assert "# A load-bearing comment: this must survive the rewrite." in text


def test_a_flow_mapping_already_correct_is_left_alone(tmp_path, validator):
    root = build_repo(tmp_path, tasks=(("TASK-0001", "FEAT-0001"),),
                      feature_tasks='tasks: ["[[TASK-0001-A-Task]]"]\n')
    snap = root / "SNAPSHOT.yaml"
    snap.write_text(snap.read_text().replace(
        '    FEAT-0001:\n      title: "A feature"\n      status: doing\n'
        '      file: "docs/features/FEAT-0001-A-Feature.md"\n',
        '    FEAT-0001: { file: "docs/features/FEAT-0001-A-Feature.md", '
        'tasks: ["TASK-0001"], status: doing }\n'), encoding="utf-8")
    before = snap.read_bytes()
    _plan, _written, changes = run(validator, root)
    assert changes == []
    assert snap.read_bytes() == before


# ------------------------------------------- the writer, driven on its own

NOTE = '''---
type: "[[feature]]"
id: FEAT-0001
tasks: [ "[[TASK-0002-B]]",   "[[TASK-0001-A]]" ]   # spaced oddly, out of order
goal: "unchanged"
---

body
'''


def test_the_writer_returns_the_input_when_the_id_set_already_matches(validator):
    """Driven directly, because `plan_backlinks` short-circuits before reaching it.

    Found by mutation: deleting this early return passed all fifteen tests above,
    since a satisfied feature never enters `plan.additions` and the writer is
    never called for it. The guard is real -- it is what stops a reordering or a
    re-quoting from becoming a diff -- and it was guarded by nothing.
    """
    out = mig.set_frontmatter_list(NOTE, "tasks",
                                   ["TASK-0001-A", "TASK-0002-B"], validator.ID_RE)
    assert out == NOTE


def test_the_writer_rewrites_when_the_id_set_differs(validator):
    out = mig.set_frontmatter_list(NOTE, "tasks",
                                   ["TASK-0001-A", "TASK-0002-B", "TASK-0003-C"],
                                   validator.ID_RE)
    assert out != NOTE
    assert 'tasks:\n  - "[[TASK-0001-A]]"\n  - "[[TASK-0002-B]]"\n  - "[[TASK-0003-C]]"\n' in out
    assert 'goal: "unchanged"' in out and "\nbody\n" in out
    assert "# spaced oddly, out of order" not in out


def test_the_writer_adds_no_empty_key(validator):
    without = NOTE.replace(
        'tasks: [ "[[TASK-0002-B]]",   "[[TASK-0001-A]]" ]   # spaced oddly, out of order\n', "")
    assert mig.set_frontmatter_list(without, "tasks", [], validator.ID_RE) == without


def test_the_writer_refuses_a_file_with_no_frontmatter(validator):
    with pytest.raises(ValueError):
        mig.set_frontmatter_list("no frontmatter here\n", "tasks", ["TASK-0001-A"], validator.ID_RE)


# --------------------------------------- the gaps independent review found
#
# Every test below exists because a mutant survived the suite above, or because
# a real note shape in the fleet had no fixture. Each names the mutant it kills.

def test_an_entry_no_child_claims_survives_a_rewrite_of_the_same_list(tmp_path, validator):
    """The merge loop in `plan_backlinks` was guarded by nothing.

    Deleting it passed all 31 tests, and the tool would then DELETE every entry
    no child claims the next time it touched that list -- five live entries
    across `your-health` and `your-trainer`. The earlier unclaimed test only
    covers the case where nothing is added, so the writer is never called.
    """
    root = build_repo(tmp_path, tasks=(("TASK-0001", "FEAT-0001"), ("TASK-0002", "")),
                      feature_tasks='tasks: ["[[TASK-0002-A-Task]]"]\n')
    plan, written, _snap = run(validator, root)
    assert ("FEAT-0001", "tasks", "TASK-0002") in plan.unclaimed
    text = (root / "docs" / "features" / "FEAT-0001-A-Feature.md").read_text()
    assert "TASK-0002-A-Task" in text, "the unclaimed entry was dropped by the rewrite"
    assert "TASK-0001-A-Task" in text


def test_a_partly_populated_list_gains_only_what_is_missing(tmp_path, validator):
    """The commonest real shape had no fixture at all.

    Every other fixture starts from a list that is empty, complete, or satisfied
    through `fixes:`. `set(children) <= named_anywhere` -> `set(children) &
    named_anywhere` ("satisfied once ANY child is named") passed all 31 tests
    and leaves `PARENT-BACKLINK` firing for every sibling.
    """
    root = build_repo(tmp_path, tasks=(("TASK-0001", "FEAT-0001"), ("TASK-0002", "FEAT-0001"),
                                       ("TASK-0003", "FEAT-0001")),
                      feature_tasks='tasks: ["[[TASK-0001-A-Task]]"]\n')
    _plan, written, _snap = run(validator, root)
    assert [w[2] for w in written] == [3]
    index, _ = validator.build_note_index(root / "docs")
    assert mig.plan_backlinks(validator, index).additions == {}


def test_main_runs_end_to_end_and_its_dry_run_previews_the_snapshot(tmp_path, validator, capsys):
    """`main()` was reached by no test, so four of its behaviours were unguarded:
    the dry run's snapshot preview, artefact pruning (ISS-0257's whole
    mitigation), the report lines, and the exit code."""
    root = build_repo(tmp_path, tasks=(("TASK-0001", "FEAT-0001"), ("TASK-0002", "FEAT-0001")))
    before = {p: p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}

    assert mig.main([str(root), "--dry-run", "--no-sync"]) == 0
    dry = capsys.readouterr().out
    assert "SNAPSHOT  FEAT-0001 tasks: 0 -> 2" in dry, "the preview was silent about the snapshot"
    assert {p: p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()} == before

    assert mig.main([str(root), "--no-sync"]) == 0
    wet = capsys.readouterr().out
    assert "BACKLINK  FEAT-0001 `tasks:` -> 2 entries" in wet
    assert "SNAPSHOT  FEAT-0001 tasks: 0 -> 2" in wet
    assert 'tasks: ["TASK-0001", "TASK-0002"]' in (root / "SNAPSHOT.yaml").read_text()

    assert mig.main([str(root), "--no-sync"]) == 0
    assert "0 note(s) rewritten, 0 snapshot entries" in capsys.readouterr().out


def test_main_refuses_a_directory_with_no_snapshot(tmp_path, validator):
    (tmp_path / "notarepo").mkdir()
    with pytest.raises(SystemExit):
        mig.main([str(tmp_path / "notarepo"), "--no-sync"])


def test_the_sync_output_parser_finds_the_paths_it_wrote(validator):
    """`parse_synced_paths` + `prune_artefacts` are ISS-0257's mitigation and
    were reached by nothing; `ARTEFACT_FRAGMENTS = ()` survived the suite."""
    out = ("[dry-run] sync-project-os: 2 copied\n"
           "[dry-run]   synced  tools/scripts/__pycache__/validate-docs.cpython-313.pyc\n"
           "  synced  tools/scripts/validate-docs.py (forced)\n"
           "  GONE  docs/__templates__/old.base\n")
    assert mig.parse_synced_paths(out) == [
        "tools/scripts/__pycache__/validate-docs.cpython-313.pyc",
        "tools/scripts/validate-docs.py",
    ]


def test_prune_artefacts_removes_only_build_output(tmp_path):
    repo = tmp_path / "repo"
    (repo / "tools" / "scripts" / "__pycache__").mkdir(parents=True)
    (repo / "tools" / "scripts" / "__pycache__" / "v.pyc").write_bytes(b"x")
    (repo / "tools" / "scripts" / "validate-docs.py").write_text("x", encoding="utf-8")
    paths = ["tools/scripts/__pycache__/v.pyc", "tools/scripts/validate-docs.py"]
    assert mig.prune_artefacts(repo, paths, dry_run=True) == ["tools/scripts/__pycache__/v.pyc"]
    assert (repo / "tools" / "scripts" / "__pycache__" / "v.pyc").exists()
    assert mig.prune_artefacts(repo, paths, dry_run=False) == ["tools/scripts/__pycache__/v.pyc"]
    assert not (repo / "tools" / "scripts" / "__pycache__" / "v.pyc").exists()
    assert (repo / "tools" / "scripts" / "validate-docs.py").exists()


# ------------------------------------------ note shapes that exist out there

MULTILINE_FLOW = '''---
type: "[[feature]]"
id: FEAT-0001
tasks: [
  "[[TASK-0001-A]]"
]
goal: "unchanged"
---

body
'''


def test_a_flow_list_closing_at_column_zero_is_consumed_whole(validator):
    """Three notes in `your-trainer` close a multi-line flow list at column 0.

    Consuming only the INDENTED continuation left the `]` behind as an orphan
    line, so the rewrite produced frontmatter that does not parse -- ISS-0260's
    defect, reintroduced by the tool that found it.
    """
    import yaml
    out = mig.set_frontmatter_list(MULTILINE_FLOW, "tasks",
                                   ["TASK-0001-A", "TASK-0002-B"], validator.ID_RE)
    assert "\n]" not in out
    end = out.find("\n---", 3)
    data = yaml.safe_load(out[4:end])
    assert data["tasks"] == ["[[TASK-0001-A]]", "[[TASK-0002-B]]"]
    assert data["goal"] == "unchanged"
    assert mig.set_frontmatter_list(MULTILINE_FLOW, "tasks",
                                    ["TASK-0001-A"], validator.ID_RE) == MULTILINE_FLOW


def test_crlf_and_a_bom_are_read_rather_than_refused(validator):
    """Both are live in the fleet (`articles`, one `your-sudoku` PLAN.md).

    `ValueError` here came out of `apply_plan`, which writes note by note AFTER
    the forced validator copy -- so the crash left a half-migrated corpus and a
    repo that could not commit.
    """
    crlf = NOTE.replace("\n", "\r\n")
    assert mig.set_frontmatter_list(crlf, "tasks",
                                    ["TASK-0001-A", "TASK-0002-B"], validator.ID_RE) == crlf
    out = mig.set_frontmatter_list(crlf, "tasks",
                                   ["TASK-0001-A", "TASK-0002-B", "TASK-0003-C"], validator.ID_RE)
    assert "TASK-0003-C" in out and out.startswith("---\r\n")
    bom = "﻿" + NOTE
    assert mig.set_frontmatter_list(bom, "tasks",
                                    ["TASK-0001-A", "TASK-0002-B"], validator.ID_RE) == bom


def test_an_unreadable_note_is_reported_and_the_rest_still_migrate(tmp_path, validator):
    """One bad note must not halt a 2519-note corpus midway."""
    root = build_repo(tmp_path, tasks=(("TASK-0001", "FEAT-0001"),))
    broken = root / "docs" / "features" / "FEAT-0002-Broken.md"
    broken.write_text("no frontmatter at all\nid: FEAT-0002\n", encoding="utf-8")
    (root / "docs" / "tasks" / "TASK-0009-A-Task.md").write_text(
        TASK.format(tid="TASK-0009", parent="FEAT-0002"), encoding="utf-8")
    index, _ = validator.build_note_index(root / "docs")
    plan = mig.plan_backlinks(validator, index)
    written, unhandled = mig.apply_plan(validator, index, plan, dry_run=False)
    assert [u[0] for u in unhandled] == ["FEAT-0002"]
    assert [w[0] for w in written] == ["FEAT-0001"]
    assert "TASK-0001-A-Task" in (root / "docs" / "features" / "FEAT-0001-A-Feature.md").read_text()
