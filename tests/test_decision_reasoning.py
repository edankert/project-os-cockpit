"""PHASE-032 — a judgment carries its reasoning.

Measured before this existed (ISS-0152): six write paths, exactly one carrying
the person's own words, and only onto a checkbox line. A human could record
*that* they decided and never *why*.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest

from project_os_cockpit import note_writes
from project_os_cockpit.index import Index
from project_os_cockpit.renderer import render_markdown_text

REPO_ROOT = Path(__file__).resolve().parent.parent
REPO_DOCS = REPO_ROOT / "docs"
RENDERER = REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts"


@pytest.fixture()
def corpus(tmp_path: Path) -> Index:
    shutil.copytree(REPO_DOCS, tmp_path / "docs")
    (tmp_path / "SNAPSHOT.yaml").write_text("project:\n  name: probe\n", encoding="utf-8")
    return Index.build(tmp_path / "docs")


# ---- FEAT-0095: the note on a transition ---------------------------------


def test_a_transition_records_the_reasoning(corpus: Index) -> None:
    """Edwin's placement, and his answer: *"included in the note being
    reviewed/decided/agreed, dated and added to the end in its own notes
    section, maybe we can use the callout notation from Obsidian."*"""
    note_writes.stamp_transition(
        corpus, "ADR-0022", to_status="accepted", actor="user:edwin",
        note="Option 3, but consequence 3 is not settled.",
    )
    text = (corpus.docs_root / "decisions" / "ADR-0022-Whether-A-Delegate-May-Push.md").read_text()
    assert "## Decision record" in text
    assert re.search(r"> \[!note\] Accept — \d{4}-\d{2}-\d{2} \(user:edwin\)", text)
    assert "> Option 3, but consequence 3 is not settled." in text


def test_no_note_leaves_the_body_untouched(corpus: Index) -> None:
    """Omitting it must cost nothing. A verb that started appending an empty
    section to every note it touched would be worse than the gap."""
    path = corpus.docs_root / "decisions" / "ADR-0022-Whether-A-Delegate-May-Push.md"
    before = path.read_text()
    note_writes.stamp_transition(corpus, "ADR-0022", to_status="accepted", actor="user:edwin")
    after = path.read_text()
    assert "Decision record" not in after
    # Only the frontmatter moved.
    assert before.split("---", 2)[2] == after.split("---", 2)[2]


def test_a_second_decision_appends_and_never_edits() -> None:
    """A decision record that can be rewritten is not one."""
    body = "# A note\n\nSome body.\n"
    body = note_writes._append_decision_record(body, verb="Accept", actor="a", note="First.")
    body = note_writes._append_decision_record(body, verb="Supersede", actor="b", note="Second.")
    assert body.count("## Decision record") == 1
    assert body.count("> [!note]") == 2
    assert body.index("First.") < body.index("Second.")


def test_hostile_prose_cannot_escape_its_block() -> None:
    """The note is a person's free text appended to a file the validator reads.
    Every line is quoted on the way in, so frontmatter delimiters, headings and
    a nested callout are inert."""
    out = note_writes._append_decision_record(
        "# x\n", verb="Accept", actor="a",
        note="---\nstatus: hacked\n---\n# A heading\n> [!danger] nested",
    )
    body = out.split("## Decision record", 1)[1]
    for line in body.splitlines():
        assert not line or line.startswith(">"), line


def test_a_note_has_a_ceiling(corpus: Index) -> None:
    """Prose, not an essay — and a cap the caller learns about rather than
    silently truncating what someone wrote."""
    with pytest.raises(note_writes.WriteError):
        note_writes.stamp_transition(
            corpus, "ADR-0022", to_status="accepted", actor="user:edwin",
            note="x" * (note_writes.NOTE_MAX_CHARS + 1),
        )


def test_the_field_reads_at_click_time() -> None:
    """Built before the reader types, so a value captured in the closure is
    always the empty string — the bug this shape exists to avoid."""
    src = RENDERER.read_text(encoding="utf-8")
    assert "class=\"note-action-note\"" in src or "'note-action-note'" in src
    fn = src.split("async function mountActuatorRow", 1)[1].split("\nasync function", 1)[0]
    # **Built inside this function**, not merely referenced from it. The first
    # attempt anchored on `docView.querySelector('details.metadata-strip')`,
    # which appears in `mountTestRunButton` too — so the field was created on
    # the test-run row and the actuator row had none. Every assertion here
    # passed; the field was simply not on the note. Found by looking.
    assert "note.className = 'note-action-note'" in fn, (
        "the field is created outside mountActuatorRow; a shared anchor put it "
        "on another row"
    )
    assert "querySelector<HTMLInputElement>('.note-action-note')" in fn, (
        "the field's value is captured when the row is built, so it is always "
        "the empty string by the time anyone clicks"
    )


# ---- TASK-0397: callouts render ------------------------------------------


@pytest.mark.parametrize("kind", ["note", "question", "warning", "info", "tip"])
def test_a_callout_renders_as_a_callout(kind: str) -> None:
    html = render_markdown_text(
        f"> [!{kind}] A title\n> The body.", source_path=Path("x.md"),
    )
    assert f'data-callout="{kind}"' in html
    assert "A title" in html and "The body." in html
    assert f"[!{kind}]" not in html, "the marker is printed at the reader"


def test_an_unknown_type_degrades_and_keeps_its_title() -> None:
    """Obsidian ships dozens and a downstream repo may use any; an
    unrecognised one is a rendering question, never an error."""
    html = render_markdown_text("> [!wibble] Still a title\n> body",
                                source_path=Path("x.md"))
    assert 'data-callout="wibble"' in html
    assert 'data-callout-unknown="true"' in html
    assert "Still a title" in html and "[!wibble]" not in html


def test_a_plain_blockquote_is_untouched() -> None:
    html = render_markdown_text("> just a quote", source_path=Path("x.md"))
    assert "<blockquote>" in html and "callout" not in html


def test_both_front_doors_style_callouts() -> None:
    """Mode 1 renders the same notes through the same pipeline. A decision
    record legible in the shell and not on the tablet is the divergence
    ADR-0010 is about."""
    for css in ("desktop/src/renderer/renderer.css",
                "src/project_os_cockpit/static/cockpit.css"):
        text = (REPO_ROOT / css).read_text(encoding="utf-8")
        assert ".callout-title" in text and ".callout-body" in text, css


# ---- FEAT-0096: a decision states its open questions ----------------------


def test_a_decision_can_carry_tickable_criteria(corpus: Index) -> None:
    """No new write path: `criteria.py` parses an Acceptance section on any
    note and the tick is not gated by type. Asserted because the *convention*
    is new even though the machinery is not."""
    from project_os_cockpit import criteria
    path = corpus.docs_root / "decisions" / "ADR-0010-What-The-Browser-Cockpit-Is-For.md"
    parsed = criteria.parse_criteria(path.read_text())
    assert len(parsed) == 2, [c["text"] for c in parsed]
    assert all(c["state"] == "open" for c in parsed)

    note_writes.stamp_tick(
        corpus, "ADR-0010", criterion=parsed[1]["raw"],
        evidence="Dropped from both.", actor="user:edwin",
    )
    after = path.read_text()
    assert "— evidence: Dropped from both. (user:edwin," in after
    assert after.count("- [x]") == 1 and after.count("- [ ]") == 1


def test_accepting_with_questions_open_is_allowed(corpus: Index) -> None:
    """Tempting to block and wrong: a person may take a decision while a
    thread stands, and the record should show that rather than prevent it."""
    note_writes.stamp_transition(
        corpus, "ADR-0010", to_status="accepted", actor="user:edwin",
        note="Option 3. The digest thread stays open deliberately.",
    )
    text = (corpus.docs_root / "decisions" / "ADR-0010-What-The-Browser-Cockpit-Is-For.md").read_text()
    assert "status: accepted" in text or 'status: "accepted"' in text
    assert "- [ ]" in text, "the open thread was closed by accepting"
