"""The delegation policy: its format, and the default that must never grant.

ADR-0009 §4 made a delegation *a per-repo recorded fact*. The single most
important property in this module is what happens when that fact is **absent**:

    no policy → no delegation → no worker

A default that grants authority is authority nobody granted. So every path in
`permits` returns False unless something explicitly says yes, and these tests
spend most of their effort on the paths where a permissive default would hide.
"""

from __future__ import annotations

from pathlib import Path

from project_os_cockpit import delegation

APPROVED = """---
status: approved
---
# Delegation

- judgment: triage issues → agent:principal [threshold: severity below high]
- judgment: close tasks → any-delegate
"""


def test_no_policy_file_delegates_nothing(tmp_path: Path) -> None:
    """The property the whole feature rests on."""
    policy = delegation.load(tmp_path)
    assert policy["present"] is False and policy["approved"] is False
    assert delegation.permits(policy, "triage issues", "agent:principal") is False


def test_a_draft_policy_is_no_policy(tmp_path: Path) -> None:
    """The note passes through the gate it configures. An agent that could
    write its own policy and have it obeyed would be delegating to itself."""
    (tmp_path / delegation.POLICY_REL).write_text(
        APPROVED.replace("status: approved", "status: draft"), encoding="utf-8",
    )
    policy = delegation.load(tmp_path)
    assert policy["present"] is True and policy["approved"] is False
    assert policy["delegations"] == [], "a draft policy exposed its delegations"
    assert delegation.permits(policy, "triage issues", "agent:principal") is False


def test_an_unreadable_status_is_treated_as_unapproved(tmp_path: Path) -> None:
    """Guessing in the permissive direction is the one mistake this cannot
    afford, so an unparseable note grants nothing."""
    (tmp_path / delegation.POLICY_REL).write_text(
        "# Delegation\n\n- judgment: anything → any-delegate\n", encoding="utf-8",
    )
    assert delegation.load(tmp_path)["approved"] is False


def test_an_approved_policy_permits_only_what_it_names(tmp_path: Path) -> None:
    (tmp_path / delegation.POLICY_REL).write_text(APPROVED, encoding="utf-8")
    policy = delegation.load(tmp_path)
    assert policy["approved"] is True
    assert delegation.permits(policy, "triage issues", "agent:principal") is True
    assert delegation.permits(policy, "close tasks", "agent:principal") is True
    # Not named → not permitted. No wildcard, no prefix match, no inheritance.
    assert delegation.permits(policy, "accept features", "agent:principal") is False
    assert delegation.permits(policy, "triage", "agent:principal") is False


def test_a_delegation_names_who(tmp_path: Path) -> None:
    """`any-delegate` is explicit; an unnamed actor gets nothing."""
    (tmp_path / delegation.POLICY_REL).write_text(APPROVED, encoding="utf-8")
    policy = delegation.load(tmp_path)
    assert delegation.permits(policy, "close tasks", "agent:other") is True   # any-delegate
    assert delegation.permits(policy, "triage issues", "agent:other") is False
    assert delegation.permits(policy, "triage issues", "") is False


def test_entries_inside_a_fence_are_examples_not_grants() -> None:
    """The template ships its entries commented out; a parser that read a
    fenced example as a grant would delegate on install."""
    text = "---\nstatus: approved\n---\n\n```\n- judgment: everything → any-delegate\n```\n"
    assert delegation.parse(text)["delegations"] == []


def test_the_shipped_template_delegates_nothing() -> None:
    """Asserted against the real file: the default a repo starts from."""
    template = (
        Path(__file__).resolve().parent.parent
        / "docs" / "__templates__" / "delegation.md"
    ).read_text(encoding="utf-8")
    parsed = delegation.parse(template)
    assert parsed["status"] != "approved", "the shipped template is pre-approved"
    assert parsed["delegations"] == [], parsed["delegations"]


def test_the_stamp_pins_the_policy_version() -> None:
    """*Who, under what authority, as the policy stood when* — without the sha
    a policy that changed after the write makes the audit unanswerable."""
    stamped = delegation.stamp("abc123def456789")
    assert "agent:principal" in stamped
    assert "DELEGATION.md@abc123def456" in stamped


def test_an_html_comment_is_not_a_grant() -> None:
    """The bug the template test caught on its first run.

    The shipped template ships its examples inside `<!-- -->`. A parser that
    understood only code fences would have delegated everything **on install** —
    the permissive-default mistake this whole module exists to avoid, arriving
    through the one file every repo copies.
    """
    text = (
        "---\nstatus: approved\n---\n\n"
        "<!--\n- judgment: everything → any-delegate\n-->\n\n"
        "- judgment: triage issues → agent:principal\n"
    )
    got = delegation.parse(text)["delegations"]
    assert [d["judgment"] for d in got] == ["triage issues"], got


# ---------------------------------------------------------------------------
# TASK-0327 — the two layers (REQ-0030)
# ---------------------------------------------------------------------------

from project_os_cockpit import note_writes  # noqa: E402

APPROVED_POLICY = {
    "approved": True,
    "delegations": [{"judgment": "approve requirement", "to": "agent:principal",
                     "threshold": ""}],
}


def test_a_human_sees_the_table_as_written() -> None:
    """The delegate filter must not narrow what a person may do."""
    verbs = [a["verb"] for a in note_writes.legal_actions("requirement", "draft")]
    assert verbs == ["Approve", "Decline"]


def test_a_delegate_with_no_policy_is_offered_nothing() -> None:
    """No policy, no delegation, no actions — the default carried through to
    the surface, so an out-of-policy action is never even shown."""
    offered = note_writes.legal_actions(
        "requirement", "draft", caller="agent:principal",
    )
    assert offered == []


def test_a_draft_policy_offers_nothing() -> None:
    """A draft policy is no policy, at the offer layer too."""
    draft = {**APPROVED_POLICY, "approved": False}
    offered = note_writes.legal_actions(
        "requirement", "draft", caller="agent:principal", policy=draft,
    )
    assert offered == []


def test_a_delegate_is_offered_only_what_the_policy_names() -> None:
    """`Approve` is delegated; `Decline` is not, and is therefore absent —
    rather than shown-and-refused, which teaches the delegate to try."""
    offered = [
        a["verb"] for a in note_writes.legal_actions(
            "requirement", "draft", caller="agent:principal", policy=APPROVED_POLICY,
        )
    ]
    assert offered == ["Approve"], offered


def test_an_unnamed_caller_is_treated_as_human_not_as_a_delegate() -> None:
    """Existing call sites pass no caller. They must keep working — and it is
    safe because a delegate is identified by *saying so*, while the guard that
    stops one lives at the write path where identity is checked."""
    assert note_writes.legal_actions("requirement", "draft", caller="") != []
