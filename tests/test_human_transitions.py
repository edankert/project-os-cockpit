"""TASK-0278 — the human-owned transition table, as data.

REQ-0026 is the contract: *the cockpit performs only human-owned transitions*.
A table is only a contract if something refuses to widen it, so these test the
refusal rather than the offer — the offer is visible, the refusal is not.
"""

from __future__ import annotations

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
