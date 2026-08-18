"""ISS-0197 — `## Runs` was write-only, and now reads back.

`stamp_test_run` has written a per-step result under that heading since the
runner existed, and nothing ever parsed it: `_RUNS_HEADING_RE` occurred only in
the writer. The results were prose, the note's status was the only state a run
left behind, and a walk interrupted at step 60 of 107 recorded sixty results
and reported nothing.

Found by independent review of PHASE-035, as the true and much narrower content
of a claim that manual-test steps were "invisible" — they are parsed, counted,
stepped and stamped; what was missing was reading the stamp back.
"""

from __future__ import annotations

from pathlib import Path

from project_os_cockpit import cockpit, note_writes
from project_os_cockpit.index import Index

BODY = """
## Steps

1. Open the app
2. Click the thing
3. Read the number

## Runs

### 2026-08-01 — failing (by user:edwin)
- **pass** · Open the app
- **fail** · Click the thing — the button does nothing

### 2026-08-10 — passing (by user:edwin)
- **pass** · Click the thing — fixed by TASK-0001
"""


def test_the_runs_section_reads_back_newest_first() -> None:
    runs = cockpit.manual_test_runs(BODY)
    assert [r["date"] for r in runs] == ["2026-08-10", "2026-08-01"]
    assert runs[0]["outcome"] == "passing"
    assert runs[0]["runner"] == "user:edwin"
    assert runs[1]["steps"][1] == {
        "result": "fail", "text": "Click the thing",
        "evidence": "the button does nothing",
    }


def test_a_partial_walk_does_not_unprove_the_steps_it_never_reached() -> None:
    """The question the write-only log could not answer.

    A step's state is its result in the most recent run that MENTIONS it. The
    2026-08-10 run touched only step 2; reading "the latest run" instead would
    report step 1 as unproven because a later, shorter walk did not repeat it.
    """
    state = cockpit.manual_test_step_state(BODY)
    assert state["declared"] == 3
    assert state["proven"] == 2, state
    assert state["unproven"] == ["Read the number"]
    assert state["results"]["Click the thing"] == "pass"


def test_the_runs_section_round_trips_through_its_own_writer(tmp_path: Path) -> None:
    """Parsed with the writer's shape, so the two cannot drift apart quietly.

    If `_append_run_log` changes its format, this fails on the same commit —
    rather than the reader silently returning nothing, which is indistinguishable
    from a test nobody has walked.
    """
    docs = tmp_path / "docs"
    (docs / "tests").mkdir(parents=True)
    note = docs / "tests" / "TST-0001-Walk.md"
    note.write_text(
        '---\ntype: "[[test]]"\nid: TST-0001\ntitle: "w"\nstatus: ready\n'
        'kind: manual\nlevel: system\nlast_verified: "2026-08-18"\ncovers: []\n---\n'
        "\n## Steps\n\n1. First thing\n2. Second thing\n", encoding="utf-8")

    note_writes.stamp_test_run(
        Index.build(docs), "TST-0001", outcome="passing", runner="user:edwin",
        steps=[{"text": "First thing", "result": "pass", "evidence": "saw it"},
               {"text": "Second thing", "result": "fail", "evidence": ""}])

    body = note.read_text().split("---", 2)[2]
    runs = cockpit.manual_test_runs(body)
    assert len(runs) == 1, "the writer's own output must parse"
    assert runs[0]["outcome"] == "passing"
    assert [s["result"] for s in runs[0]["steps"]] == ["pass", "fail"]
    assert runs[0]["steps"][0]["evidence"] == "saw it"

    state = cockpit.manual_test_step_state(body)
    assert state["unproven"] == ["Second thing"]
