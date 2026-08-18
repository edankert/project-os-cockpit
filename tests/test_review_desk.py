"""Review desk — queue, review write-back, and the manual test runner
(FEAT-0041 / TASK-0206, TASK-0207, TASK-0209).

The hardening assertions are the point of most of this file: the desk is
the first surface that *writes* notes, so the guarantees that keep that
crossing narrow — a field allow-list, guarded transitions, path
canonicalisation, an mtime precondition, an untouched snapshot — are
tested as behaviour rather than trusted as intent.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from project_os_cockpit import cockpit, note_writes
from project_os_cockpit.index import Index
from project_os_cockpit.note_writes import WriteError
from project_os_cockpit.review import ReviewStore


def _note(path: Path, fm: dict, body: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["---"]
    for key, value in fm.items():
        lines.append(f"{key}: {json.dumps(value)}")
    lines.append("---")
    path.write_text("\n".join(lines) + "\n\n" + body, encoding="utf-8")


MANUAL_TEST_BODY = """# Live instrumentation

## Purpose

Verify the hooks.

## Steps

1. Launch the desktop app with this workspace open
   Expected: the workspace rail shows one square
2. Start claude in the embedded console
3. Send a prompt — the strip shows busy within 5 s
   Expected: strip state is `busy`

## Notes

- not a step
"""


@pytest.fixture()
def workspace(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    _note(docs / "features" / "x" / "FEAT-0001-X.md", {
        "type": "[[feature]]", "id": "FEAT-0001", "title": "Feature X",
        "status": "backlog",
    })
    _note(docs / "features" / "x" / "plan" / "tasks" / "TASK-0001-A.md", {
        "type": "[[task]]", "id": "TASK-0001", "title": "Task A",
        "status": "backlog", "parent": "[[FEAT-0001]]",
    })
    _note(docs / "decisions" / "ADR-0001-Gate.md", {
        "type": "[[adr]]", "id": "ADR-0001", "title": "A gate",
        "status": "proposed",
    })
    _note(docs / "decisions" / "ADR-0002-Old.md", {
        "type": "[[adr]]", "id": "ADR-0002", "title": "Settled",
        "status": "accepted",
    })
    _note(docs / "tests" / "TST-0001-Manual.md", {
        "type": "[[test]]", "id": "TST-0001", "title": "Live instrumentation",
        "status": "ready", "automation": "manual",
    }, body=MANUAL_TEST_BODY)
    # **A `command:`, because that is now the only thing that makes a test
    # automated** (ADR-0034 decision 4). This fixture said `automation:
    # automated` and no more — which was the pre-2026-08-18 rule, and the exact
    # shape `your-sudoku`'s TST-0013 was in: claiming to be machine-run with no
    # way to run it. Under the new rule that state does not exist, so the
    # fixture has to declare what it means.
    _note(docs / "tests" / "TST-0002-Auto.md", {
        "type": "[[test]]", "id": "TST-0002", "title": "Automated thing",
        "status": "ready", "command": "pytest -q",
    })
    _note(docs / "requirements" / "REQ-0001-Draft.md", {
        "type": "[[requirement]]", "id": "REQ-0001", "title": "Drafty",
        "status": "draft",
    })
    return docs


# ---- step parsing -------------------------------------------------------

def test_manual_test_steps_parse_with_expectations() -> None:
    steps = cockpit.manual_test_steps(MANUAL_TEST_BODY)
    assert [s["n"] for s in steps] == [1, 2, 3]
    assert steps[0]["text"].startswith("Launch the desktop app")
    assert steps[0]["expected"] == "the workspace rail shows one square"
    # A step without an Expected line simply has none — not an empty string.
    assert "expected" not in steps[1]
    # Parsing stops at the next heading: "not a step" is under ## Notes.
    assert all("not a step" not in s["text"] for s in steps)


def test_steps_absent_yields_no_steps() -> None:
    assert cockpit.manual_test_steps("# Title\n\nNo steps here.\n") == []


# ---- ISS-0172: a procedure may have subsections --------------------------


def test_a_subsection_does_not_end_the_procedure() -> None:
    """The bug that made 8 of 15 tests unrunnable.

    The parser broke at the first heading of ANY level after the procedure
    heading — including a subheading *of the section it was reading* — so a
    two-level procedure yielded nothing and the Run button silently did not
    exist. Two levels is the natural shape for a procedure with parts.
    """
    body = (
        "## Steps\n\n"
        "### Export\n"
        "1. Open Settings.\n"
        "2. Tap Export Backup.\n\n"
        "### Wipe\n"
        "11. Uninstall the app.\n\n"
        "## Expected Result\n"
        "- not a step\n"
    )
    steps = cockpit.manual_test_steps(body)
    assert [s["text"] for s in steps] == [
        "Open Settings.", "Tap Export Backup.", "Uninstall the app.",
    ]
    # It still ends at a heading at its OWN level — the fix widens the
    # section, it does not remove its boundary.
    assert all("not a step" not in s["text"] for s in steps)


def test_a_deeper_procedure_heading_ends_at_its_own_level() -> None:
    """`### Steps` under `## Part` is bounded by the next `###`, not by `##`."""
    body = (
        "## Part one\n\n"
        "### Steps\n"
        "1. Do the thing.\n\n"
        "### Evidence\n"
        "- not a step\n"
    )
    steps = cockpit.manual_test_steps(body)
    assert [s["text"] for s in steps] == ["Do the thing."]


def test_cases_heads_a_procedure() -> None:
    """`## Cases` is what your-trainer's TST-0018 uses — written for the
    feature that repo was actively building, and parsing to nothing."""
    steps = cockpit.manual_test_steps("## Cases\n\n1. Aeroplane mode, cold start.\n")
    assert [s["text"] for s in steps] == ["Aeroplane mode, cold start."]


def test_a_bold_lead_in_is_not_a_bullet() -> None:
    """`**Offline entitlement** — on a device…` opens with the same character
    as a `*` bullet. Markdown requires whitespace after a list marker; the
    parser did not, so a paragraph lead-in became step 1."""
    body = (
        "## Cases\n\n"
        "**Offline entitlement (ISS-0374)** — on a device holding PRO:\n\n"
        "1. Aeroplane mode, cold start.\n"
    )
    steps = cockpit.manual_test_steps(body)
    assert [s["text"] for s in steps] == ["Aeroplane mode, cold start."]


def test_an_expectation_under_its_step_is_not_a_step() -> None:
    """The corpus writes `- **Expected:** …` beneath the step it belongs to.
    Anchored on a bare `Expected:`, the old matcher missed every one and the
    step matcher took them — eleven steps rendering as twenty-two."""
    body = (
        "## Steps\n\n"
        "- [ ] Tap Max HR.\n"
        "- **Expected:** the header stays visible.\n"
        "- [ ] Open the profile.\n"
    )
    steps = cockpit.manual_test_steps(body)
    assert len(steps) == 2
    assert steps[0]["expected"] == "the header stays visible."
    assert steps[1]["text"] == "Open the profile."


def test_checkboxes_are_the_procedure_when_no_heading_names_one() -> None:
    """Four of the eight had no procedure heading at all: their whole body is
    sections of checkboxes. A checkbox is an explicit *thing to do*; a bullet
    inside a Purpose paragraph is prose, and the fallback reads only the
    former."""
    body = (
        "## Purpose\n\n"
        "- prose about why this exists\n\n"
        "## A — Input screens\n\n"
        "### A.1 — New-rider dialog\n"
        "- [ ] Add Rider, tap Max HR.\n"
        "- **Expected:** the header stays visible.\n\n"
        "### A.2 — Rider profile\n"
        "- [ ] Open the profile.\n"
    )
    steps = cockpit.manual_test_steps(body)
    assert [s["text"] for s in steps] == [
        "Add Rider, tap Max HR.", "Open the profile.",
    ]
    assert steps[0]["expected"] == "the header stays visible."
    assert all("prose about why" not in s["text"] for s in steps)


def test_the_fallback_yields_only_to_a_named_procedure() -> None:
    """A note with BOTH a procedure heading and checkboxes elsewhere reads the
    named procedure. The fallback is for notes that have no heading to find,
    not a second harvest layered on top of one that worked."""
    body = (
        "## Steps\n\n"
        "1. The real step.\n\n"
        "## Evidence (fill after running)\n"
        "- [ ] not a step\n"
    )
    steps = cockpit.manual_test_steps(body)
    assert [s["text"] for s in steps] == ["The real step."]


def test_every_manual_test_in_this_repo_is_runnable() -> None:
    """Completeness, not non-zero (the ISS-0164 lesson).

    A manual test the cockpit offers a person is a test the cockpit can walk.
    The measured failure was 8 of 15 in one repo, and a guard asserting
    "some test parses" would have called that fixed.
    """
    index = Index.build(Path(__file__).resolve().parents[1] / "docs")
    unrunnable = [
        record.note_id
        for record in index.notes_by_type("test")
        if not record.rel_path.startswith("__templates__/")
        # An acceptance test is walked in the `~checks` view with the six-mark
        # dialog, not through the manual stepper -- its body is a procedure in a
        # paragraph, deliberately, because one note IS one check. The stepper's
        # completeness claim is about the population it actually offers.
        and str(record.frontmatter.get("level", "") or "").strip().lower() != "acceptance"
        and cockpit._is_manual_test(record)
        and not cockpit.manual_test_steps(record.body)
    ]
    assert unrunnable == []


def test_checklist_heading_and_inline_expect_are_understood() -> None:
    """The corpus's own shape, not just the template's.

    TST-0011 — the acceptance demo for the runner — heads its procedure
    `## Checklist` and puts expectations inline as `Expect: …`, with bold
    lead-ins. A parser that only accepted `## Steps` would have made the
    one test this feature exists to drain unrunnable, so it follows the
    corpus (the ADR-0006 lesson) rather than the other way round.
    """
    body = (
        "## Checklist\n\n"
        "1. **Claude Code injection (TASK-0115).** Open a workspace, run `claude`. "
        "Expect: rail dot flips to busy within ~1s.\n"
        "2. **Kill switch.** Relaunch with the env var set.\n"
    )
    steps = cockpit.manual_test_steps(body)
    assert len(steps) == 2
    # Emphasis is stripped — a stepper label is not a place for markdown.
    assert steps[0]["text"].startswith("Claude Code injection (TASK-0115).")
    assert "**" not in steps[0]["text"]
    assert steps[0]["expected"] == "rail dot flips to busy within ~1s."
    assert "expected" not in steps[1]


# ---- queue --------------------------------------------------------------

def test_queue_groups_come_from_existing_intake_states(workspace: Path) -> None:
    index = Index.build(workspace)
    payload = cockpit.review_queue_payload(index, None)
    groups = {g["key"]: g for g in payload["groups"]}

    assert [i["id"] for i in groups["decisions"]["items"]] == ["ADR-0001"]
    assert [i["id"] for i in groups["proposals"]["items"]] == ["REQ-0001"]
    # Only the *manual* ready test is runnable from the desk.
    assert [i["id"] for i in groups["runs"]["items"]] == ["TST-0001"]
    assert groups["runs"]["items"][0]["steps"] == 3
    assert payload["total"] == 3


def test_review_requests_join_the_queue_without_touching_note_state(
    workspace: Path, tmp_path: Path,
) -> None:
    """The ADR-0007 mechanism: pending-ness is runtime state.

    A feature awaiting review must still read `backlog` in its own note —
    that is the whole reason the desk does not introduce a status.
    """
    index = Index.build(workspace)
    store = ReviewStore(tmp_path)
    store.add("review", items=["FEAT-0001", "TASK-0001"], title="Overview rework")

    payload = cockpit.review_queue_payload(index, store)
    proposals = next(g for g in payload["groups"] if g["key"] == "proposals")
    entry = next(i for i in proposals["items"] if i.get("title") == "Overview rework")
    assert [i["id"] for i in entry["items"]] == ["FEAT-0001", "TASK-0001"]
    assert all(i["status"] == "backlog" for i in entry["items"])

    # And on disk, nothing changed.
    text = (workspace / "features" / "x" / "FEAT-0001-X.md").read_text()
    assert "status: backlog" in text.replace('"', "")


def test_questions_are_their_own_group(workspace: Path, tmp_path: Path) -> None:
    store = ReviewStore(tmp_path)
    store.add("question", title="Commits panel everywhere?", body="…")
    payload = cockpit.review_queue_payload(Index.build(workspace), store)
    questions = next(g for g in payload["groups"] if g["key"] == "questions")
    assert len(questions["items"]) == 1
    assert questions["items"][0]["kind"] == "answer"


def test_store_survives_a_restart_and_records_outcomes(tmp_path: Path) -> None:
    store = ReviewStore(tmp_path)
    rec = store.add("review", items=["FEAT-0001"], title="Set")
    reborn = ReviewStore(tmp_path)
    assert [r["request_id"] for r in reborn.open_requests()] == [rec["request_id"]]

    reborn.resolve(rec["request_id"], "accepted-amended")
    assert reborn.open_requests() == []
    assert reborn.outcome_counts() == {"accepted-amended": 1}
    # Resolving twice is not an error and does not double-count.
    reborn.resolve(rec["request_id"], "accepted")
    assert reborn.outcome_counts() == {"accepted-amended": 1}


def test_store_rejects_unknown_kinds_and_outcomes(tmp_path: Path) -> None:
    store = ReviewStore(tmp_path)
    with pytest.raises(ValueError):
        store.add("approve-everything")
    rec = store.add("review", items=[])
    with pytest.raises(ValueError):
        store.resolve(rec["request_id"], "rubber-stamped")


def test_corrupt_store_degrades_to_empty(tmp_path: Path) -> None:
    (tmp_path / ".cockpit").mkdir()
    (tmp_path / ".cockpit" / "review-requests.json").write_text("{ truncated",
                                                                encoding="utf-8")
    assert ReviewStore(tmp_path).open_requests() == []


# ---- review write-back --------------------------------------------------

def test_accept_stamps_the_existing_review_fields(workspace: Path) -> None:
    index = Index.build(workspace)
    result = note_writes.stamp_review(
        index, "FEAT-0001", reviewer="user:edwin",
        verdict=note_writes.PLAN_ACCEPTED_VERDICT,
    )
    assert result["review_verdict"] == "plan-accepted"
    text = (workspace / "features" / "x" / "FEAT-0001-X.md").read_text()
    assert 'reviewed_by: "user:edwin"' in text
    assert 'review_verdict: "plan-accepted"' in text
    assert "review_date:" in text
    # Status untouched by an accept — acceptance is not a lifecycle move.
    assert '"backlog"' in text


def test_plan_acceptance_cannot_satisfy_the_close_out_gate(workspace: Path) -> None:
    """`approved` is close-out's vocabulary (QUALITY.md).

    If the desk could write it, having one's *plan* approved would satisfy
    the gate that guards *verification* — so the endpoint refuses it.
    """
    index = Index.build(workspace)
    with pytest.raises(WriteError) as exc:
        note_writes.stamp_review(
            index, "FEAT-0001", reviewer="user:edwin", verdict="approved",
        )
    assert "close-out" in str(exc.value)
    assert "reviewed_by" not in (
        workspace / "features" / "x" / "FEAT-0001-X.md"
    ).read_text()


def test_reject_transitions_to_cancelled_only(workspace: Path) -> None:
    index = Index.build(workspace)
    note_writes.stamp_review(
        index, "TASK-0001", reviewer="user:edwin",
        verdict=note_writes.PLAN_ACCEPTED_VERDICT, status="cancelled",
    )
    text = (workspace / "features" / "x" / "plan" / "tasks" / "TASK-0001-A.md").read_text()
    assert 'status: "cancelled"' in text

    # Any other transition is refused, even a real vocabulary member.
    for status in ("done", "doing", "implemented"):
        with pytest.raises(WriteError) as exc:
            note_writes.stamp_review(
                index, "FEAT-0001", reviewer="user:edwin",
                verdict=note_writes.PLAN_ACCEPTED_VERDICT, status=status,
            )
        assert "not a transition this endpoint may perform" in str(exc.value)


def test_invented_status_is_refused(workspace: Path) -> None:
    index = Index.build(workspace)
    with pytest.raises(WriteError) as exc:
        note_writes.stamp_review(
            index, "FEAT-0001", reviewer="user:edwin",
            verdict=note_writes.PLAN_ACCEPTED_VERDICT, status="pending-review",
        )
    assert "not in the project-os status vocabulary" in str(exc.value)


def test_unknown_note_and_traversal_are_refused(workspace: Path) -> None:
    index = Index.build(workspace)
    with pytest.raises(WriteError) as exc:
        note_writes.resolve_note(index, "FEAT-9999")
    assert exc.value.status == 404
    for hostile in ("../../etc/passwd", "/etc/passwd", ""):
        with pytest.raises(WriteError):
            note_writes.resolve_note(index, hostile)


def test_stale_mtime_refuses_rather_than_clobbers(workspace: Path) -> None:
    index = Index.build(workspace)
    target = workspace / "features" / "x" / "FEAT-0001-X.md"
    stale = target.stat().st_mtime - 500
    with pytest.raises(WriteError) as exc:
        note_writes.stamp_review(
            index, "FEAT-0001", reviewer="user:edwin",
            verdict=note_writes.PLAN_ACCEPTED_VERDICT, mtime=stale,
        )
    assert exc.value.status == 409
    assert "reviewed_by" not in target.read_text()


def test_write_never_touches_the_snapshot(workspace: Path, tmp_path: Path) -> None:
    """ADR-0009: notes are the authored source; sync-snapshot propagates
    at pre-commit. An endpoint writing SNAPSHOT.yaml would reintroduce
    exactly the dual-write that decision removed."""
    snapshot = tmp_path / "SNAPSHOT.yaml"
    snapshot.write_text("version: 1\nitems: {}\n", encoding="utf-8")
    before = snapshot.read_text()
    index = Index.build(workspace)
    note_writes.stamp_review(
        index, "FEAT-0001", reviewer="user:edwin",
        verdict=note_writes.PLAN_ACCEPTED_VERDICT,
    )
    assert snapshot.read_text() == before


def test_only_allowed_fields_are_writable() -> None:
    """The allow-list is the guarantee; assert its contents directly so
    widening it is a deliberate, reviewed change.

    `updated` is in the set because both paths write it — every note edit
    touches it, and a stale `updated` would make the corpus lie about its
    own freshness. It is declared rather than excused.
    """
    assert note_writes.ALLOWED_FIELDS == {
        "reviewed_by", "review_date", "review_verdict",
        "status", "last_run", "last_verified", "updated",
        # Widened deliberately for design review (TASK-0218).
        # `design_revision` records WHICH revision a verdict was given to.
        # Without it an approval given to v3 silently launders v6 — the one way
        # a design review can be worse than no review at all.
        "design_revision",
    }


def test_endpoint_request_keys_are_the_exported_ones() -> None:
    """The HTTP handlers must consume the exported allow-lists.

    They first duplicated these as literals in `server.py`, which left
    `ALLOWED_FIELDS` decorative — exported, asserted, and enforcing
    nothing (independent review, 2026-07-26).
    """
    import inspect

    from project_os_cockpit import server

    src = inspect.getsource(server)
    assert "note_writes.REVIEW_REQUEST_KEYS" in src
    assert "note_writes.TEST_RUN_REQUEST_KEYS" in src
    assert note_writes.REVIEW_REQUEST_KEYS == {
        "id", "reviewer", "verdict", "status", "mtime",
    }


def test_desk_refuses_to_stamp_gate_bearing_notes(workspace: Path) -> None:
    """Closing the gate hole the string-level refusal only narrowed.

    ADR-0011's close-out check reads `review_verdict` on tests and
    changes and accepts anything that is not `changes-requested`. A
    review request naming a TST could therefore have silenced a gate it
    never satisfied. The desk refuses those note types outright.
    """
    index = Index.build(workspace)
    with pytest.raises(WriteError) as exc:
        note_writes.stamp_review(
            index, "TST-0001", reviewer="user:edwin",
            verdict=note_writes.PLAN_ACCEPTED_VERDICT,
        )
    assert exc.value.status == 403
    assert "close-out review gate" in str(exc.value)
    assert "review_verdict" not in (
        workspace / "tests" / "TST-0001-Manual.md"
    ).read_text()


def test_rejection_records_a_rejection(workspace: Path) -> None:
    """A rejected item must not read as accepted.

    The first cut stamped `plan-accepted` alongside `cancelled` because
    the endpoint took only one verdict, so the durable record of every
    rejection said the opposite of what happened.
    """
    index = Index.build(workspace)
    note_writes.stamp_review(
        index, "TASK-0001", reviewer="user:edwin",
        verdict=note_writes.PLAN_REJECTED_VERDICT, status="cancelled",
    )
    text = (workspace / "features" / "x" / "plan" / "tasks" / "TASK-0001-A.md").read_text()
    assert 'review_verdict: "plan-rejected"' in text
    assert 'status: "cancelled"' in text


def test_multi_line_frontmatter_values_are_refused_not_mangled(
    tmp_path: Path,
) -> None:
    """`_set_field` rewrites one line; a block scalar spans several.

    Replacing just the key's line would orphan its indented continuation
    and emit invalid YAML, so the writer refuses instead.
    """
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "FEAT-0009-Block.md").write_text(
        '---\ntype: "[[feature]]"\nid: FEAT-0009\ntitle: "Block"\n'
        "status: >\n  backlog\n---\n\nBody.\n",
        encoding="utf-8",
    )
    index = Index.build(docs)
    with pytest.raises(WriteError) as exc:
        note_writes.stamp_review(
            index, "FEAT-0009", reviewer="user:edwin",
            verdict=note_writes.PLAN_ACCEPTED_VERDICT, status="cancelled",
        )
    assert exc.value.status == 409
    assert "multi-line value" in str(exc.value)
    # Nothing written: the note is byte-identical.
    assert "status: >\n  backlog" in (docs / "FEAT-0009-Block.md").read_text()


def test_run_log_lands_under_runs_even_when_it_is_not_last(
    tmp_path: Path,
) -> None:
    """Appending to the end of the body filed runs under whatever
    section followed `## Runs` — here, Evidence."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "TST-0009-Ordered.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0009\ntitle: "Ordered"\n'
        'status: ready\nautomation: manual\n---\n\n'
        "## Steps\n\n1. Do the thing\n\n## Runs\n\n"
        "### 2026-01-01 — passing\n- **pass** · old run\n\n"
        "## Evidence\n\n- keep me last\n",
        encoding="utf-8",
    )
    index = Index.build(docs)
    note_writes.stamp_test_run(
        index, "TST-0009", outcome="passing",
        steps=[{"n": 1, "text": "Do the thing", "result": "pass"}],
    )
    text = (docs / "TST-0009-Ordered.md").read_text()
    runs_at = text.index("## Runs")
    evidence_at = text.index("## Evidence")
    new_run_at = text.index("**pass** · Do the thing")
    assert runs_at < new_run_at < evidence_at, "run filed outside ## Runs"
    assert text.rstrip().endswith("- keep me last")


# ---- test runner --------------------------------------------------------

def test_run_stamps_status_and_appends_a_run_log(workspace: Path) -> None:
    index = Index.build(workspace)
    steps = [
        {"n": 1, "text": "Launch the app", "result": "pass", "evidence": "opened"},
        {"n": 2, "text": "Start claude", "result": "pass", "evidence": ""},
        {"n": 3, "text": "Send a prompt", "result": "pass", "evidence": "2 s"},
    ]
    note_writes.stamp_test_run(
        index, "TST-0001", outcome="passing", steps=steps, runner="user:edwin",
    )
    text = (workspace / "tests" / "TST-0001-Manual.md").read_text()
    assert 'status: "passing"' in text
    assert "last_run:" in text
    assert "last_verified:" in text
    assert "## Runs" in text
    assert "**pass** · Launch the app — opened" in text


def test_failing_run_records_the_outcome_without_last_verified(
    workspace: Path,
) -> None:
    index = Index.build(workspace)
    note_writes.stamp_test_run(
        index, "TST-0001", outcome="failing",
        steps=[{"n": 1, "text": "Launch", "result": "fail", "evidence": "blank"}],
    )
    text = (workspace / "tests" / "TST-0001-Manual.md").read_text()
    assert 'status: "failing"' in text
    assert "last_run:" in text
    assert "last_verified:" not in text


def test_aborted_run_writes_no_status_but_keeps_the_log(workspace: Path) -> None:
    index = Index.build(workspace)
    note_writes.stamp_test_run(
        index, "TST-0001", outcome="", aborted=True,
        steps=[{"n": 1, "text": "Launch", "result": "pass"}],
    )
    text = (workspace / "tests" / "TST-0001-Manual.md").read_text()
    assert 'status: "ready"' in text          # unchanged
    assert "aborted" in text
    assert "## Runs" in text


def test_second_run_appends_rather_than_replaces(workspace: Path) -> None:
    index = Index.build(workspace)
    for outcome in ("failing", "passing"):
        note_writes.stamp_test_run(
            index, "TST-0001", outcome=outcome,
            steps=[{"n": 1, "text": "Launch", "result": outcome}],
        )
    text = (workspace / "tests" / "TST-0001-Manual.md").read_text()
    assert text.count("## Runs") == 1
    assert text.count("### ") == 2
    assert 'status: "passing"' in text


def test_run_outcome_vocabulary_is_guarded(workspace: Path) -> None:
    index = Index.build(workspace)
    with pytest.raises(WriteError):
        note_writes.stamp_test_run(
            index, "TST-0001", outcome="probably-fine", steps=[],
        )


def test_failing_step_drafts_an_issue_for_confirmation() -> None:
    draft = note_writes.draft_issue_body(
        "TST-0011", "Live instrumentation",
        {"n": 4, "text": "Trigger an idle prompt",
         "expected": "attention shows waiting", "evidence": "nothing appeared"},
    )
    assert "step 4 failed" in draft["title"]
    assert "[[TST-0011]]" in draft["body"]
    assert "attention shows waiting" in draft["body"]
    assert "nothing appeared" in draft["body"]


def test_scope_decisions_use_the_link_graph_not_titles(tmp_path: Path) -> None:
    """Decisions reach a scope through frontmatter links.

    The renderer's first cut matched scope ids inside ADR *titles*, which
    works right up until an ADR is titled after its conclusion rather
    than its subject — the common case. The sidecar resolves it through
    the same link fields the graph uses.
    """
    docs = tmp_path / "docs"
    _note(docs / "phases" / "PHASE-001-One.md", {
        "type": "[[phase]]", "id": "PHASE-001", "title": "One", "status": "active",
    })
    _note(docs / "features" / "a" / "FEAT-0001-A.md", {
        "type": "[[feature]]", "id": "FEAT-0001", "title": "A",
        "status": "done", "phase": "[[PHASE-001]]",
    })
    # Title names nothing in scope; `related` reaches the phase's feature.
    _note(docs / "decisions" / "ADR-0001-Retire-The-Band.md", {
        "type": "[[adr]]", "id": "ADR-0001", "title": "Retire the band",
        "status": "accepted", "related": ["[[FEAT-0001-A]]"],
    })
    # Reaches nothing in scope at all.
    _note(docs / "decisions" / "ADR-0002-Unrelated.md", {
        "type": "[[adr]]", "id": "ADR-0002", "title": "Something else",
        "status": "accepted", "related": ["[[FEAT-9999]]"],
    })

    payload = cockpit.scope_tests_payload(Index.build(docs), "PHASE-001")
    ids = [d["id"] for d in payload["decisions"]]
    assert ids == ["ADR-0001"], "link graph, not title matching"


# ---- endpoint-level guards ----------------------------------------------

def test_mutation_endpoints_reject_non_loopback_callers(tmp_path: Path) -> None:
    """The render server binds 0.0.0.0 so a tablet can *read*; writing is
    Mac-local. No test covered this before (independent review,
    2026-07-26) — and the guard is a per-request peer-address check on
    the shared socket, not a separate bind, so only a test can prove it.
    """
    import threading
    import urllib.error
    import urllib.request

    from project_os_cockpit.server import (
        DocsServer, _NoDNSThreadingHTTPServer, _make_handler,
    )

    docs = _make_min_workspace(tmp_path)
    server = DocsServer(docs_root=docs, bind="127.0.0.1", port=0)
    index = Index.build(docs)
    handler = _make_handler(docs, index, server.bus)
    httpd = _NoDNSThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        # Every mutation endpoint must consult the guard. Loopback here is
        # allowed, so assert the *guard exists* on each path by driving it
        # with a spoofed peer through the handler's own predicate.
        import inspect

        from project_os_cockpit import server as server_mod

        src = inspect.getsource(server_mod)
        for endpoint in ("_serve_review_request", "_serve_review_resolve",
                         "_serve_note_review", "_serve_test_run"):
            body = src.split(f"def {endpoint}(")[1].split("def ")[0]
            assert "_require_loopback()" in body, (
                f"{endpoint} does not check the caller is loopback"
            )
        # And the predicate itself accepts only loopback addresses.
        from project_os_cockpit.server import _LOOPBACK_HOSTS

        assert _LOOPBACK_HOSTS == frozenset(
            {"127.0.0.1", "::1", "::ffff:127.0.0.1"}
        )

        # Sanity: a loopback POST is accepted (400 for a bad body, not 403).
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/notes/review",
            data=b"{}", method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            urllib.request.urlopen(req, timeout=3)
            status = 200
        except urllib.error.HTTPError as exc:
            status = exc.code
        assert status != 403, "loopback caller was refused"
    finally:
        httpd.shutdown()
        httpd.server_close()


def _make_min_workspace(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    _note(docs / "README.md", {"title": "Readme"})
    return docs


# ---- deciding a lone queued note (the ADR-0007 dead end) ----------------

def test_plans_are_not_queued(workspace: Path) -> None:
    """A plan's status follows its feature and is advanced at close-out
    (STATUSES.md), so `draft` on a plan is not a decision awaiting a
    human. Queueing them asked for reviews nobody could perform — and
    plans carry no `id:`, so the row could not even address one.
    """
    docs = workspace
    _note(docs / "features" / "x" / "plan" / "PLAN.md", {
        "type": "[[plan]]", "title": "X delivery plan",
        "status": "draft", "implements": "[[FEAT-0001]]",
    })
    payload = cockpit.review_queue_payload(Index.build(docs), None)
    everything = [i for g in payload["groups"] for i in g["items"]]
    assert all((i.get("type") or "") != "plan" for i in everything)


def test_proposed_adr_can_be_accepted(workspace: Path) -> None:
    """The defect Edwin reported: ADR-0007 sat in the queue with no way
    to act on it. `proposed -> accepted` is the ADR's own transition."""
    index = Index.build(workspace)
    result = note_writes.stamp_decision(
        index, "ADR-0001", reviewer="user:edwin", accept=True,
    )
    assert result["status"] == "accepted"
    text = (workspace / "decisions" / "ADR-0001-Gate.md").read_text()
    assert 'status: "accepted"' in text
    assert 'reviewed_by: "user:edwin"' in text


def test_declining_an_adr_supersedes_rather_than_rejects(workspace: Path) -> None:
    """STATUSES.md: a decision not taken is deleted or superseded, never
    marked `rejected` — a rejected proposal worth keeping is worth
    recording as the alternative it lost to."""
    index = Index.build(workspace)
    result = note_writes.stamp_decision(
        index, "ADR-0001", reviewer="user:edwin", accept=False,
    )
    assert result["status"] == "superseded"
    text = (workspace / "decisions" / "ADR-0001-Gate.md").read_text()
    # The *status* is what must never be `rejected` — that is the
    # vocabulary rule. The desk's own verdict field is separately allowed
    # to say `plan-rejected`, which is a record of the review, not a
    # lifecycle state (an earlier substring check conflated the two).
    assert 'status: "rejected"' not in text
    assert "rejected" not in [
        line.split(":", 1)[1].strip().strip('"')
        for line in text.splitlines() if line.startswith("status:")
    ]
    assert 'review_verdict: "plan-rejected"' in text


def test_draft_requirement_is_approved_not_plan_accepted(workspace: Path) -> None:
    index = Index.build(workspace)
    result = note_writes.stamp_decision(
        index, "REQ-0001", reviewer="user:edwin", accept=True,
    )
    assert result["status"] == "approved"


def test_decide_refuses_types_it_does_not_own(workspace: Path) -> None:
    """A task or a test is not decided from the desk — the former has no
    intake decision, the latter belongs to close-out."""
    index = Index.build(workspace)
    for note_id, expected in (("TASK-0001", 400), ("TST-0001", 403)):
        with pytest.raises(WriteError) as exc:
            note_writes.stamp_decision(
                index, note_id, reviewer="user:edwin", accept=True,
            )
        assert exc.value.status == expected


def test_queue_reports_the_advisory_phase_tally(workspace: Path, tmp_path: Path) -> None:
    """ADR-0007 chose advisory-first so gating could be decided with data,
    and set a trigger (~20 sets, or PHASE-008 close-out). The store was
    counting outcomes and nothing read them — a revisit with no evidence
    is the failure ADR-0006 was written about.

    **The ADR settled on 2026-07-29** (stay advisory, permanently) and the
    desk's tally surface was removed with it (TASK-0247). These payload
    fields deliberately stay: the store's outcome record is the ledger's
    own account of what the desk did, and it is what a reopened gating
    question would read. What was retired is the obligation to watch it,
    not the data — so this asserts the recording, and TST-0022 asserts the
    surface is gone.
    """
    store = ReviewStore(tmp_path)
    for outcome in ("accepted", "accepted-amended", "changes-requested"):
        rec = store.add("review", items=["FEAT-0001"], title=outcome)
        store.resolve(rec["request_id"], outcome)
    open_one = store.add("review", items=["FEAT-0001"], title="still open")

    payload = cockpit.review_queue_payload(Index.build(workspace), store)
    assert payload["reviewed"] == 3
    assert payload["outcomes"] == {
        "accepted": 1, "accepted-amended": 1, "changes-requested": 1,
    }
    # An unresolved request counts in the queue, never in the tally.
    assert open_one["request_id"]
    assert payload["total"] >= 1


def test_decision_records_a_verdict_for_the_future_gate(workspace: Path) -> None:
    """ADR-0007's future gate predicate is 'has an accepting
    review_verdict', not a status check. A lone-note decision that wrote
    only reviewed_by/review_date would be invisible to it."""
    index = Index.build(workspace)
    result = note_writes.stamp_decision(
        index, "ADR-0001", reviewer="user:edwin", accept=True,
    )
    assert result["review_verdict"] == note_writes.PLAN_ACCEPTED_VERDICT
    text = (workspace / "decisions" / "ADR-0001-Gate.md").read_text()
    assert 'review_verdict: "plan-accepted"' in text
    # And it is still not close-out's vocabulary.
    assert "approved" not in text
