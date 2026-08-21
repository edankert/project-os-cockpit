"""`REVIEW-STALE` and `review_response:` — a verdict outlives the work it
judged ([[ISS-0253]]).

**Measured 2026-08-20: 49 notes carry `review_verdict: changes-requested`, and
43 of them are at a terminal status** — 27 `done`, 7 `merged`, 4 `implemented`,
5 `fixed` — dating back to 2026-08-02. Every one is true as a fact about a
moment and false as a description of the note today: the findings were acted
on, often within the hour, and nothing writes a new verdict.

**This is [[ISS-0121]] inverted.** That issue found the field sticky in the
*other* direction and the renderer stopped reading it alone because of it. The
same stickiness was here, unaddressed, on the authoring side.

**The fix is not "the author flips it"** — that is exactly what
[[project-os-dev#ADR-0011]] exists to prevent. The gap was that *"the findings
were addressed"* had nowhere to go.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "scripts" / "validate-docs.py"
RENDERER = ROOT / "desktop" / "src" / "renderer" / "renderer.ts"

SNAPSHOT = (
    'version: 1\nupdated: "2026-08-21"\ncounters:\n  FEAT: 1\n'
    'focus:\n  task: ""\nitems:\n  features: {}\n'
)


def _repo(tmp: Path, extra: str, *, status: str = "done") -> Path:
    (tmp / "docs" / "features" / "f").mkdir(parents=True, exist_ok=True)
    (tmp / "SNAPSHOT.yaml").write_text(SNAPSHOT, encoding="utf-8")
    (tmp / "docs" / "features" / "f" / "FEAT-0001-F.md").write_text(
        f'---\ntype: "[[feature]]"\nid: FEAT-0001\ntitle: "F"\n'
        f'status: {status}\nowner: user:edwin\n{extra}---\n\n# F\n',
        encoding="utf-8")
    return tmp


def _findings(tmp: Path) -> list[str]:
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(tmp)],
        capture_output=True, text=True)
    return [ln for ln in out.stdout.splitlines() if "REVIEW-STALE" in ln]


# ---- the population the issue measured -----------------------------------

def test_a_terminal_note_with_an_unanswered_verdict_is_reported(
        tmp_path: Path) -> None:
    _repo(tmp_path, 'reviewed_by: model:x\nreview_date: 2026-08-02\n'
                    'review_verdict: changes-requested\n')
    found = _findings(tmp_path)
    assert len(found) == 1, found
    assert "FEAT-0001" in found[0] and "review_response" in found[0]


def test_recording_what_was_done_clears_it(tmp_path: Path) -> None:
    """**And it does not touch the verdict.** `review_verdict` stays
    `changes-requested` — that is the reviewer's, and self-clearing it turns an
    independent gate into a formality."""
    _repo(tmp_path, 'reviewed_by: model:x\nreview_date: 2026-08-02\n'
                    'review_verdict: changes-requested\n'
                    'review_response: "All three findings applied; banners now '
                    'in the first line of each quarantined section."\n'
                    'review_response_date: 2026-08-20\n')
    assert _findings(tmp_path) == []
    raw = (tmp_path / "docs" / "features" / "f" / "FEAT-0001-F.md").read_text()
    assert "review_verdict: changes-requested" in raw, (
        "the response must sit BESIDE the verdict, never replace it"
    )


def test_flipping_the_verdict_is_not_how_it_clears(tmp_path: Path) -> None:
    """It clears, of course — an `approved` note is not carrying an unanswered
    objection. What the rule must not do is make flipping the *cheapest* way
    out, which is why the message names `review_response:` and not the verdict.
    """
    src = VALIDATOR.read_text(encoding="utf-8")
    i = src.index('"REVIEW-STALE",\n            "%s is')
    message = src[i:i + 700]
    assert "review_response:" in message
    assert "the verdict stays the reviewer's" in message


def test_a_note_still_in_flight_is_not_reported(tmp_path: Path) -> None:
    """Six of the 49 are non-terminal, and reporting them would say a
    reviewer's live objection is a defect in the record."""
    for status in ("doing", "review", "backlog"):
        _repo(tmp_path / status,
              'reviewed_by: model:x\nreview_date: 2026-08-02\n'
              'review_verdict: changes-requested\n', status=status)
        assert _findings(tmp_path / status) == [], status


def test_an_approved_verdict_is_not_reported(tmp_path: Path) -> None:
    _repo(tmp_path, 'reviewed_by: model:x\nreview_date: 2026-08-02\n'
                    'review_verdict: approved\n')
    assert _findings(tmp_path) == []


def test_a_note_with_no_verdict_at_all_is_not_reported(tmp_path: Path) -> None:
    """That is the `REVIEW` gate's subject, not this one. Two rules reporting
    one note under different codes is how a person comes to believe there are
    two problems."""
    _repo(tmp_path, "")
    assert _findings(tmp_path) == []


# ---- the trigger that was deliberately NOT used --------------------------

def test_it_does_not_re_arm_when_the_note_is_edited(tmp_path: Path) -> None:
    """**The obvious trigger is wrong twice over.** `updated:` later than
    `review_date:` re-arms a gate whenever a note is edited for any reason
    ([[ISS-0007]]) — and stamping a verdict IS an edit, so 85 of 103 verdicts
    in this corpus have `updated <= review_date` (`_verdict_is_owed`'s own
    measurement). The discriminator is whether an answer was recorded.
    """
    for updated in ("2026-08-01", "2026-08-02", "2026-12-31"):
        _repo(tmp_path / updated,
              f'reviewed_by: model:x\nreview_date: 2026-08-02\n'
              f'review_verdict: changes-requested\n'
              f'review_response: "fixed"\nupdated: "{updated}"\n')
        assert _findings(tmp_path / updated) == [], updated

    src = VALIDATOR.read_text(encoding="utf-8")
    i = src.index("# -- REVIEW-STALE")
    block = src[i:src.index("# -- requirement lifecycle", i)]
    assert "updated" not in block.split('promotion_emit')[1], (
        "the rule reads `updated:`, which re-arms on every unrelated edit"
    )


# ---- the vocabularies that must not drift --------------------------------

def test_the_validator_and_the_cockpit_agree_on_which_verdicts_owe() -> None:
    """Three copies of one set — the validator, the cockpit and the renderer —
    because the validator is stdlib-only and the renderer is TypeScript. An
    unpinned third copy is [[REQ-0059]]'s forbidden shape."""
    from project_os_cockpit import cockpit, validate_docs_bundled as v

    assert set(v.OWED_VERDICTS) == set(cockpit.OWED_VERDICTS)
    src = RENDERER.read_text(encoding="utf-8")
    i = src.index("const OWED_VERDICT_WORDS = new Set([")
    literal = src[i:src.index("]", i)]
    for word in cockpit.OWED_VERDICTS:
        assert f"'{word}'" in literal, (word, literal)


def test_every_terminal_status_it_names_is_a_real_status() -> None:
    """The cross-type form of the ISS-0011 guard: `REVIEW_TERMINAL_STATUSES`
    spans every note type, so `_check_values` cannot be used on it — asserting
    it against `task` would report `merged` as illegal."""
    from project_os_cockpit import validate_docs_bundled as v

    every = set()
    for allowed in v.ALLOWED_STATUS.values():
        every.update(allowed)
    assert set(v.REVIEW_TERMINAL_STATUSES) <= every


def test_the_table_is_registered_with_the_completeness_guard() -> None:
    """Registration is manual and can be forgotten — ISS-0012 is the record of
    it being forgotten by the very commit that added the guard."""
    from project_os_cockpit import validate_docs_bundled as v

    assert "REVIEW_TERMINAL_STATUSES" in v._CHECKED_TABLE_NAMES
    assert "OWED_VERDICTS" in v._NON_STATUS_COLLECTIONS


# ---- what the reader sees ------------------------------------------------

def test_the_payload_carries_the_response(tmp_path: Path) -> None:
    from project_os_cockpit import cockpit
    from project_os_cockpit.index import Index

    _repo(tmp_path, 'reviewed_by: model:x\nreview_date: 2026-08-02\n'
                    'review_verdict: changes-requested\n'
                    'review_response: "the three findings were applied"\n'
                    'review_response_date: 2026-08-20\n')
    rows = cockpit._reviewed_register(Index.build(tmp_path / "docs"))
    assert rows[0]["verdict"] == "changes-requested"
    assert rows[0]["response"] == "the three findings were applied"
    assert rows[0]["response_date"] == "2026-08-20"
    #: The status is terminal, so nothing is OWED — and that is exactly the
    #: state a reader could not distinguish from an unanswered objection.
    assert rows[0]["owed"] is False


def test_the_desk_says_whether_the_objection_was_answered() -> None:
    src = RENDERER.read_text(encoding="utf-8")
    i = src.index("OWED_VERDICT_WORDS.has(item.verdict)")
    block = src[i:i + 900]
    assert "no response recorded" in block, block[:400]
    assert "answered" in block


def test_the_desk_does_not_read_the_verdict_alone() -> None:
    """[[ISS-0121]]'s lesson, still standing: `owed` is server-computed from
    the note's current status. This adds a second axis, it does not replace
    the first."""
    src = RENDERER.read_text(encoding="utf-8")
    assert "return item.owed === true;" in src
