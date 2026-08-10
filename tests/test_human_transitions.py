"""TASK-0278 — the human-owned transition table, as data.

REQ-0026 is the contract: *the cockpit performs only human-owned transitions*.
A table is only a contract if something refuses to widen it, so these test the
refusal rather than the offer — the offer is visible, the refusal is not.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from project_os_cockpit import note_writes, statuses
from project_os_cockpit.index import Index

FIXTURE = Path(__file__).parent / "fixtures" / "index_basic"


@pytest.fixture()
def docs_root(tmp_path: Path) -> Path:
    import shutil
    dest = tmp_path / "docs"
    shutil.copytree(FIXTURE, dest)
    return dest


def test_every_status_in_the_table_exists_in_the_vocabulary() -> None:
    """The ISS-0023 rule, applied to a second table.

    A transition naming a status `statuses.py` does not have would render in
    the default grey, sort nowhere, and be invisible to Hide-completed — the
    exact failure that cost six surfaces weeks of drift.
    """
    for note_type, by_status in note_writes.HUMAN_TRANSITIONS.items():
        for from_status, actions in by_status.items():
            assert from_status in statuses.VOCABULARY, (
                f"{note_type} is offered actions from {from_status!r}, "
                "which is not a status this project has"
            )
            for verb, to_status in actions:
                assert to_status in statuses.VOCABULARY, (
                    f"{note_type} {from_status} -> {to_status!r} ({verb}) "
                    "names a status outside the vocabulary"
                )
                assert verb, "every action needs a verb a human can read"


def test_no_close_out_status_is_reachable_from_the_table() -> None:
    """The half of REQ-0026 that matters (TASK-0278).

    Close-out is the agent's: `done`, `fixed`, `merged`, `implemented`,
    `passing`. If any became reachable here, the cockpit could mark work
    finished without the work being finished — which is the one thing the
    viewer line was drawn to prevent.
    """
    agent_owned = {"done", "fixed", "merged", "implemented", "passing", "verified"}
    reachable = {
        to
        for by_status in note_writes.HUMAN_TRANSITIONS.values()
        for actions in by_status.values()
        for _verb, to in actions
    }
    leaked = reachable & agent_owned
    assert not leaked, f"agent-owned statuses reachable from the cockpit: {sorted(leaked)}"


def test_defer_is_offered_on_a_triage_issue() -> None:
    """ADR-0020's amendment, and the measurement behind it.

    39 issues sit at `triage` across the fleet with a median age of 56 days,
    and the only verbs were accept and decline — so "real, but not now" had
    nowhere to go. `deferred` was already legal and already had a mark.
    """
    verbs = {a["verb"] for a in note_writes.legal_actions("issue", "triage")}
    assert {"Accept", "Defer", "Decline"} <= verbs, verbs


def test_a_note_in_the_wrong_state_is_refused(docs_root: Path) -> None:
    """The table is keyed by the note's CURRENT status, so a stale renderer
    cannot replay an action that has stopped being offered."""
    index = Index.build(docs_root)
    with pytest.raises(note_writes.WriteError) as exc:
        # TASK-0001 is `doing`; tasks are not in the table at all.
        note_writes.stamp_transition(index, "TASK-0001", to_status="done")
    assert "REQ-0026" in exc.value.message
    assert "human-owned" in exc.value.message


def test_an_agent_owned_transition_names_the_rule(docs_root: Path) -> None:
    """A refusal that does not say why teaches nothing (DES-0005)."""
    index = Index.build(docs_root)
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.stamp_transition(index, "REQ-0001", to_status="implemented")
    assert "REQ-0026" in exc.value.message


def test_a_status_outside_the_vocabulary_is_refused(docs_root: Path) -> None:
    index = Index.build(docs_root)
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.stamp_transition(index, "REQ-0001", to_status="banana")
    assert "vocabulary" in exc.value.message


def test_a_legal_transition_writes_only_status_and_updated(docs_root: Path) -> None:
    """Format-preserving, per REQ-0027.

    The **body is byte-identical** and the frontmatter differs only in the two
    fields this write owns. Compared as sets of frontmatter lines rather than
    positionally: a note with no `updated:` gains one, which shifts every line
    after it without any of them changing.
    """
    target = docs_root / "REQ-0001-Some-Req.md"
    raw = target.read_text(encoding="utf-8")
    if "status: draft" not in raw:
        index0 = Index.build(docs_root)
        current = index0.get(index0.by_id("REQ-0001")).status
        target.write_text(raw.replace(f"status: {current}", "status: draft"), encoding="utf-8")
    before = target.read_text(encoding="utf-8")

    index = Index.build(docs_root)
    result = note_writes.stamp_transition(index, "REQ-0001", to_status="approved")
    assert result["from"] == "draft" and result["to"] == "approved"

    after = target.read_text(encoding="utf-8")

    def split(text: str) -> tuple[list[str], str]:
        parts = text.split("---", 2)
        return parts[1].strip().splitlines(), parts[2]

    fm_before, body_before = split(before)
    fm_after, body_after = split(after)

    assert body_after == body_before, "the note's body was rewritten"

    owned = ("status:", "updated:")
    untouched_before = [ln for ln in fm_before if not ln.startswith(owned)]
    untouched_after = [ln for ln in fm_after if not ln.startswith(owned)]
    assert untouched_after == untouched_before, (
        "a transition rewrote frontmatter it does not own"
    )
    # `_set_field` quotes the value it writes — that is the module's existing
    # convention, not this write's choice.
    assert any(
        ln.startswith("status:") and "approved" in ln for ln in fm_after
    ), fm_after


def test_a_stale_mtime_refuses_and_writes_nothing(docs_root: Path) -> None:
    """REQ-0027's precondition: a note edited since render fails loudly."""
    index = Index.build(docs_root)
    target = docs_root / "REQ-0001-Some-Req.md"
    before = target.read_text(encoding="utf-8")
    with pytest.raises(note_writes.WriteError):
        note_writes.stamp_transition(index, "REQ-0001", to_status="approved", mtime=1.0)
    assert target.read_text(encoding="utf-8") == before


# ---- the tick path (TASK-0279) ----------------------------------------


def _req_with_criteria(docs_root: Path) -> Path:
    target = docs_root / "REQ-0002-Criteria.md"
    target.write_text(
        '---\n'
        'type: "[[requirement]]"\n'
        'id: REQ-0002\n'
        'aliases: ["REQ-0002"]\n'
        'title: "Has criteria"\n'
        'status: approved\n'
        'specifies: ["[[FEAT-0001]]"]\n'
        '---\n\n'
        '# Has criteria\n\n'
        '## Acceptance Criteria\n\n'
        '- [ ] The first thing holds\n'
        '  - [ ] A nested thing holds\n'
        '- [ ] The second thing holds\n',
        encoding="utf-8",
    )
    return target


def test_a_tick_writes_the_shape_the_real_validator_parses(docs_root: Path) -> None:
    """The DoD's central proof (TASK-0279).

    Not "it looks right" — the actual `validate_docs_bundled` regexes are run
    over the written line. A tick the validator cannot read is worse than no
    tick, because it looks resolved and does not count toward REQ-BOXES.
    """
    from project_os_cockpit import validate_docs_bundled as v

    target = _req_with_criteria(docs_root)
    index = Index.build(docs_root)
    note_writes.stamp_tick(
        index, "REQ-0002",
        criterion="The first thing holds",
        evidence="tests/test_human_transitions.py",
        actor="user:edwin",
    )
    lines = target.read_text(encoding="utf-8").splitlines()
    ticked = next(ln for ln in lines if "The first thing holds" in ln)
    assert v.CHECKED_RE.match(ticked), f"the validator does not read this as ticked: {ticked!r}"
    assert "evidence:" in ticked and "user:edwin" in ticked

    unticked, checked = v.count_acceptance_boxes(target, heading=r"Acceptance\b")
    assert checked >= 1, "the validator counted no ticked criterion"


def test_a_reconcile_writes_the_tilde_shape(docs_root: Path) -> None:
    from project_os_cockpit import validate_docs_bundled as v

    target = _req_with_criteria(docs_root)
    index = Index.build(docs_root)
    note_writes.stamp_tick(
        index, "REQ-0002",
        criterion="The second thing holds",
        reason="descoped, see ISS-0999",
        actor="user:edwin",
    )
    line = next(
        ln for ln in target.read_text(encoding="utf-8").splitlines()
        if "The second thing holds" in ln
    )
    assert v.RECONCILED_RE.match(line), f"not the reconciled shape: {line!r}"
    assert "descoped" in line


def test_a_tick_preserves_indentation_and_touches_one_line(docs_root: Path) -> None:
    target = _req_with_criteria(docs_root)
    before = target.read_text(encoding="utf-8").splitlines()
    index = Index.build(docs_root)
    note_writes.stamp_tick(
        index, "REQ-0002", criterion="A nested thing holds",
        evidence="a test", actor="user:edwin",
    )
    after = target.read_text(encoding="utf-8").splitlines()
    assert len(after) == len(before)
    differing = [i for i, (b, a) in enumerate(zip(before, after)) if b != a]
    assert len(differing) == 1, f"a tick rewrote {len(differing)} lines"
    assert after[differing[0]].startswith("  - [x]"), (
        f"nesting was lost: {after[differing[0]]!r}"
    )


def test_an_ambiguous_criterion_is_refused_and_writes_nothing(docs_root: Path) -> None:
    """Two criteria with the same prose is not a case to guess at."""
    target = docs_root / "REQ-0003-Ambiguous.md"
    target.write_text(
        '---\ntype: "[[requirement]]"\nid: REQ-0003\ntitle: "Ambiguous"\n'
        'status: approved\n---\n\n## Acceptance Criteria\n\n'
        '- [ ] It works\n- [ ] It works\n',
        encoding="utf-8",
    )
    before = target.read_text(encoding="utf-8")
    index = Index.build(docs_root)
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.stamp_tick(index, "REQ-0003", criterion="It works", evidence="x")
    assert "would be a guess" in exc.value.message
    assert target.read_text(encoding="utf-8") == before


def test_a_missing_criterion_is_refused(docs_root: Path) -> None:
    _req_with_criteria(docs_root)
    index = Index.build(docs_root)
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.stamp_tick(index, "REQ-0002", criterion="Nothing says this", evidence="x")
    assert "no criterion" in exc.value.message


def test_a_tick_needs_evidence_and_a_reconcile_needs_a_reason(docs_root: Path) -> None:
    _req_with_criteria(docs_root)
    index = Index.build(docs_root)
    with pytest.raises(note_writes.WriteError):
        note_writes.stamp_tick(index, "REQ-0002", criterion="The first thing holds")
    with pytest.raises(note_writes.WriteError):
        note_writes.stamp_tick(
            index, "REQ-0002", criterion="The first thing holds",
            evidence="a", reason="b",
        )


def test_a_stale_mtime_refuses_the_tick(docs_root: Path) -> None:
    target = _req_with_criteria(docs_root)
    before = target.read_text(encoding="utf-8")
    index = Index.build(docs_root)
    with pytest.raises(note_writes.WriteError):
        note_writes.stamp_tick(
            index, "REQ-0002", criterion="The first thing holds",
            evidence="x", mtime=1.0,
        )
    assert target.read_text(encoding="utf-8") == before


# ---- issue creation and the hardening suite (TASK-0280) ---------------


def test_create_issue_allocates_the_next_id_from_the_index(docs_root: Path) -> None:
    """The id comes from the index, not the snapshot counter.

    `sync-snapshot.py` raises `counters` to the maximum observed id at
    pre-commit (ADR-0009), so the two agree by construction — reading the
    index means a created issue does not depend on the snapshot being fresh.
    """
    index = Index.build(docs_root)
    first = note_writes.create_issue(index, docs_root, title="A captured thought")
    assert first["id"].startswith("ISS-")
    assert first["status"] == "triage", "capture with no severity queues for triage"

    fresh = Index.build(docs_root)
    second = note_writes.create_issue(fresh, docs_root, title="Another one")
    assert int(second["id"][4:]) == int(first["id"][4:]) + 1


def test_create_issue_with_a_severity_opens_rather_than_queueing(docs_root: Path) -> None:
    """Supplying a severity means the triage judgment has been made."""
    index = Index.build(docs_root)
    result = note_writes.create_issue(
        index, docs_root, title="Known bad", severity="high",
    )
    assert result["status"] == "open"
    assert result["severity"] == "high"


def test_a_created_issue_is_a_note_the_index_can_read(docs_root: Path) -> None:
    """The file has to be a real note, not a plausible-looking one."""
    index = Index.build(docs_root)
    result = note_writes.create_issue(
        index, docs_root, title="Round trips", body="Some detail.",
        component="cockpit", actor="user:edwin",
    )
    fresh = Index.build(docs_root)
    record = fresh.get(fresh.by_id(result["id"]))
    assert record is not None, "the created issue is not indexable"
    assert record.note_type == "issue"
    assert record.status == "triage"
    assert record.title == "Round trips"


def test_the_filename_follows_the_corpus_convention(docs_root: Path) -> None:
    index = Index.build(docs_root)
    result = note_writes.create_issue(
        index, docs_root, title="The register counts settled work as owed!",
    )
    assert result["rel"].startswith("issues/")
    assert result["rel"].endswith(".md")
    stem = Path(result["rel"]).stem
    assert stem.startswith(result["id"] + "-")
    assert "!" not in stem and " " not in stem


# --- the refusals. Each one is a guard; each is broken once below. ---


def test_refusal_unknown_severity(docs_root: Path) -> None:
    index = Index.build(docs_root)
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.create_issue(index, docs_root, title="x", severity="urgent")
    assert "severity" in exc.value.message


def test_refusal_empty_title(docs_root: Path) -> None:
    index = Index.build(docs_root)
    with pytest.raises(note_writes.WriteError):
        note_writes.create_issue(index, docs_root, title="   ")


def test_refusal_path_traversal_in_the_title(docs_root: Path) -> None:
    """A title is user text and reaches a filename. It must not reach a path.

    The slug strips every non-alphanumeric character, so traversal cannot be
    expressed — asserted here rather than assumed, because "the slug handles
    it" is exactly the kind of claim that stops being true when someone
    widens the slug to keep dots or slashes.
    """
    index = Index.build(docs_root)
    result = note_writes.create_issue(
        index, docs_root, title="../../etc/passwd and ../../../escape",
    )
    written = (docs_root / result["rel"]).resolve()
    assert str(written).startswith(str(docs_root.resolve())), written
    assert ".." not in result["rel"]


def test_refusal_duplicate_id_race(docs_root: Path) -> None:
    """Two creates against the SAME stale index must not overwrite each other.

    The second sees the id already on disk and refuses with 409 rather than
    silently replacing a note somebody just filed.
    """
    index = Index.build(docs_root)
    first = note_writes.create_issue(index, docs_root, title="First in")
    before = (docs_root / first["rel"]).read_text(encoding="utf-8")

    # Same index object: it has not seen the file that was just written.
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.create_issue(index, docs_root, title="Second in")
    assert exc.value.status == 409
    assert (docs_root / first["rel"]).read_text(encoding="utf-8") == before


def test_the_creatable_type_allow_list_is_one_type(docs_root: Path) -> None:
    """FEAT-0059's Out of Scope: each further type earns its own review of
    what "next id" and "which template" mean. A constant, not a parameter."""
    assert note_writes.CREATABLE_TYPES == {"issue"}


def test_every_note_mutating_endpoint_requires_loopback() -> None:
    """RISK-0001's threat model, enumerated rather than hand-listed (TASK-0280).

    The render server binds `0.0.0.0` so a tablet can read; the only thing
    separating reading from writing is a per-request peer check. REQ-0027:
    *"No write endpoint is reachable from a non-loopback peer."*

    Routes are read out of the POST dispatch table rather than typed here, so
    **a new write endpoint that forgets the guard fails this test by
    existing**. That is the whole point: `/api/notes/check-toggle` had been
    mutating notes for any LAN peer since FEAT-0011 because it predates
    `note_writes.py` and nothing enumerated it (ISS-0129).

    The two exemptions are named individually, so exempting a third is a
    deliberate edit rather than a widening nobody notices.
    """
    src = (
        Path(__file__).resolve().parents[1]
        / "src" / "project_os_cockpit" / "server.py"
    ).read_text(encoding="utf-8")
    # The POST dispatch table lives in `_route_post`, not in `do_POST` (which
    # only wraps it for BrokenPipeError). Slice to the next same-level def.
    post_block = src.split("def _route_post")[1].split("\n        def ")[0]
    routes = re.findall(
        r'if path == "(/api/[^"]+)"[\s\S]{0,120}?self\.(_serve_\w+)\(', post_block
    )
    assert len(routes) >= 10, f"the parse found only {len(routes)} POST routes"

    # Endpoints that change only runtime state — what the cockpit is looking
    # at, or its in-memory session mirror. They touch nothing in docs/.
    RUNTIME_ONLY = {
        "/api/cockpit/focus",       # moves the centre pane
        "/api/cockpit/tab-state",   # which tab is open
        "/api/cockpit/agent-state", # the agent-state mirror
        "/api/agent-hook",          # agent session events; reads docs_root only to report a path
        "/api/cockpit/dispatch",    # the dispatch queue, in .cockpit/ not docs/
    }

    unguarded = []
    for route, handler in routes:
        # Handlers vary in signature; locate by name and read to the next def.
        marker = re.search(rf"\n        def {handler}\(", src)
        assert marker, f"{handler} is routed but not defined"
        body = src[marker.end():].split("\n        def ")[0]
        if "_require_loopback" in body:
            continue
        if route in RUNTIME_ONLY:
            # The exemption is only honest if the handler really writes
            # nothing under docs/. Checked, not asserted by comment.
            writes = ("write_text(" in body) or ("note_writes." in body)
            assert not writes, (
                f"{route} is exempted as runtime-only but performs a note write"
            )
            continue
        unguarded.append((route, handler))

    assert not unguarded, (
        "these POST endpoints mutate without checking the caller is loopback: "
        f"{unguarded}"
    )


def test_a_criterion_containing_an_em_dash_can_be_ticked(docs_root: Path) -> None:
    """Regression (2026-08-10, found dogfooding the tick path on REQ-0027).

    `_criterion_text` strips the resolution a resolved box carries after an
    em dash. An earlier cut stripped on " — " unconditionally, so any
    criterion *containing* an em dash was truncated and could never be
    matched — REQ-0027's fourth criterion reads "…re-renders its surfaces —
    no optimistic UI, the file is the truth" and was unreachable.

    The discriminator is the box state: an unticked box has no resolution to
    strip, so there is nothing to guess at.
    """
    target = docs_root / "REQ-0004-Em-Dash.md"
    criterion = "The surface re-renders — no optimistic UI, the file is the truth"
    target.write_text(
        '---\ntype: "[[requirement]]"\nid: REQ-0004\ntitle: "Em dash"\n'
        f'status: approved\n---\n\n## Acceptance Criteria\n\n- [ ] {criterion}\n',
        encoding="utf-8",
    )
    index = Index.build(docs_root)
    note_writes.stamp_tick(
        index, "REQ-0004", criterion=criterion, evidence="a test", actor="user:edwin",
    )
    line = next(
        ln for ln in target.read_text(encoding="utf-8").splitlines()
        if "no optimistic UI" in ln
    )
    assert line.startswith("- [x]")
    assert "evidence: a test" in line
    # And re-resolving it matches the criterion rather than nesting.
    fresh = Index.build(docs_root)
    note_writes.stamp_tick(
        fresh, "REQ-0004", criterion=criterion, reason="reconsidered", actor="user:edwin",
    )
    after = next(
        ln for ln in target.read_text(encoding="utf-8").splitlines()
        if "no optimistic UI" in ln
    )
    assert after.startswith("- [~]"), after
    assert after.count("evidence:") == 0, "the previous resolution was nested, not replaced"
