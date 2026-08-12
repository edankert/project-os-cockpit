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


#: A decision that offers options, written here rather than borrowed from the
#: corpus. The first version of these tests used the live `ADR-0010`, and on
#: 2026-08-12 Edwin accepted it in the app mid-session — six tests broke, none
#: of them because the code was wrong. **A test that depends on the status of a
#: note a human can change is a test about the corpus, not about the code.**
DECISION_FIXTURE = """---
type: "[[adr]]"
id: ADR-9001
aliases: ["ADR-9001"]
title: "A probe decision that offers three options"
status: "proposed"
owner: user:edwin
created: 2026-08-12
updated: 2026-08-12
---

# A probe decision

## Options

1. **Do nothing.** The status quo, and its cost.
2. **Do the middle thing.** What it buys and what it costs.
3. **Do the whole thing.** The most expensive path.

## Decision (proposed)

**Option 3**, because the probe says so.

## Acceptance

- [ ] **An open thread:** answered separately from the decision itself.
"""


@pytest.fixture()
def corpus(tmp_path: Path) -> Index:
    shutil.copytree(REPO_DOCS, tmp_path / "docs")
    (tmp_path / "SNAPSHOT.yaml").write_text("project:\n  name: probe\n", encoding="utf-8")
    (tmp_path / "docs" / "decisions" / "ADR-9001-Probe.md").write_text(
        DECISION_FIXTURE, encoding="utf-8",
    )
    return Index.build(tmp_path / "docs")


# ---- FEAT-0095: the note on a transition ---------------------------------


def test_a_transition_records_the_reasoning(corpus: Index) -> None:
    """Edwin's placement, and his answer: *"included in the note being
    reviewed/decided/agreed, dated and added to the end in its own notes
    section, maybe we can use the callout notation from Obsidian."*"""
    note_writes.stamp_transition(
        corpus, "ADR-9001", to_status="accepted", actor="user:edwin",
        note="Option 3, but consequence 3 is not settled.",
    )
    text = (corpus.docs_root / "decisions" / "ADR-9001-Probe.md").read_text()
    assert "## Decision record" in text
    assert re.search(r"> \[!note\] Accept — \d{4}-\d{2}-\d{2} \(user:edwin\)", text)
    assert "> Option 3, but consequence 3 is not settled." in text


def test_no_note_leaves_the_body_untouched(corpus: Index) -> None:
    """Omitting it must cost nothing. A verb that started appending an empty
    section to every note it touched would be worse than the gap."""
    path = corpus.docs_root / "decisions" / "ADR-9001-Probe.md"
    before = path.read_text()
    note_writes.stamp_transition(corpus, "ADR-9001", to_status="accepted", actor="user:edwin")
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
            corpus, "ADR-9001", to_status="accepted", actor="user:edwin",
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
    assert "querySelector<HTMLTextAreaElement>('.note-action-note')" in fn, (
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
    path = corpus.docs_root / "decisions" / "ADR-9001-Probe.md"
    parsed = criteria.parse_criteria(path.read_text())
    assert len(parsed) == 1, [c["text"] for c in parsed]
    assert all(c["state"] == "open" for c in parsed)

    note_writes.stamp_tick(
        corpus, "ADR-9001", criterion=parsed[0]["raw"],
        evidence="Dropped from both.", actor="user:edwin",
    )
    after = path.read_text()
    assert "— evidence: Dropped from both. (user:edwin," in after
    assert after.count("- [x]") == 1 and after.count("- [ ]") == 0


def test_accepting_with_questions_open_is_allowed(corpus: Index) -> None:
    """Tempting to block and wrong: a person may take a decision while a
    thread stands, and the record should show that rather than prevent it."""
    note_writes.stamp_transition(
        corpus, "ADR-9001", to_status="accepted", actor="user:edwin",
        note="Option 3. The open thread stays open deliberately.",
    )
    text = (corpus.docs_root / "decisions" / "ADR-9001-Probe.md").read_text()
    assert "status: accepted" in text or 'status: "accepted"' in text
    assert "- [ ]" in text, "the open thread was closed by accepting"


# ---- FEAT-0097: a decision offers its options ----------------------------


def test_both_option_forms_in_this_corpus_parse() -> None:
    """Two forms were already in use when the convention was written — `N.
    **Label.**` in two decisions and `### N. Label` in a third — because
    nothing had ever said which was right. Both parse, deliberately: a
    convention that invalidated notes already written would be a migration
    wearing a convention's clothes."""
    from project_os_cockpit import decisions
    seen = {}
    for path in sorted((REPO_DOCS / "decisions").glob("ADR-*.md")):
        payload = decisions.payload(path.read_text(encoding="utf-8"))
        if payload["options"]:
            seen[path.stem.split("-")[1]] = payload
    assert len(seen) >= 3, sorted(seen)
    for adr, payload in seen.items():
        numbers = [o["number"] for o in payload["options"]]
        assert numbers == list(range(1, len(numbers) + 1)), (adr, numbers)
        assert all(o["label"] for o in payload["options"]), adr
        assert payload["proposed"] in numbers, (adr, payload["proposed"])


def test_the_proposed_option_is_read_from_the_decision_not_the_list() -> None:
    """Every option in the list mentions itself by number, so scanning the
    whole note returns option 1 every time."""
    from project_os_cockpit import decisions
    text = (REPO_DOCS / "decisions" / "ADR-0010-What-The-Browser-Cockpit-Is-For.md").read_text()
    assert decisions.proposed_option(text) == 3


def test_a_note_with_no_options_is_unaffected() -> None:
    from project_os_cockpit import decisions
    assert decisions.payload("# x\n\n## Decision\n\nJust do it.\n") == {
        "options": [], "proposed": None,
    }


def test_choosing_an_option_records_it_in_both_places(corpus: Index) -> None:
    """A decision that listed three and recorded only `accepted` has lost the
    answer. It goes in the frontmatter, where a machine reads it, and in the
    callout, where a person does."""
    note_writes.stamp_transition(
        corpus, "ADR-9001", to_status="accepted", actor="user:edwin",
        option="3", note="Do the whole thing.",
    )
    text = (corpus.docs_root / "decisions" / "ADR-9001-Probe.md").read_text()
    assert 'decided_option: "3"' in text
    assert "> [!note] Accept — option 3: Do the whole thing" in text


def test_an_option_the_note_does_not_offer_is_refused(corpus: Index) -> None:
    """The number is a claim about the document; a surface that recorded 9
    against a note offering three would put a lie in the frontmatter."""
    with pytest.raises(note_writes.WriteError) as exc:
        note_writes.stamp_transition(
            corpus, "ADR-9001", to_status="accepted", actor="user:edwin", option="9",
        )
    assert "is not one of them" in exc.value.message


def test_accepting_without_choosing_records_nothing_extra(corpus: Index) -> None:
    """A decision may be accepted as proposed. Demanding a choice would make
    the control a gate rather than an offer."""
    note_writes.stamp_transition(
        corpus, "ADR-9001", to_status="accepted", actor="user:edwin",
    )
    text = (corpus.docs_root / "decisions" / "ADR-9001-Probe.md").read_text()
    assert "decided_option" not in text


def test_the_validator_reports_a_section_it_cannot_read(tmp_path: Path) -> None:
    """The half that makes the convention stick. Edwin: *"how can we make sure
    the LLM formats the document correctly?"* — by checking it, at pre-commit
    and in CI, rather than by writing it down and hoping.

    An **error** and not a dated warning: the convention is new, so there is no
    fleet debt to grandfather, and ADR-0011 forbids a warning with nothing to
    migrate.
    """
    import subprocess
    docs = tmp_path / "docs" / "decisions"
    docs.mkdir(parents=True)
    (tmp_path / "SNAPSHOT.yaml").write_text("project:\n  name: probe\n", encoding="utf-8")
    (docs / "ADR-0001-Bad.md").write_text(
        '---\ntype: "[[adr]]"\nid: ADR-0001\nstatus: proposed\n---\n\n'
        "# Bad\n\n## Options\n\n- one thing\n- another thing\n",
        encoding="utf-8",
    )
    out = subprocess.run(
        ["python3", str(REPO_ROOT / "tools" / "scripts" / "validate-docs.py"),
         "--repo-root", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert "DECISION-OPTIONS" in out.stdout + out.stderr


def test_the_reasoning_field_is_a_textarea() -> None:
    """*"way too small"* — a single 220px line asks for a fragment, and this is
    a sentence about a decision."""
    src = RENDERER.read_text(encoding="utf-8")
    fn = src.split("async function mountActuatorRow", 1)[1].split("\nasync function", 1)[0]
    assert "createElement('textarea')" in fn
    css = (REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.css").read_text()
    rule = css.split(".note-action-note {", 1)[1].split("}", 1)[0]
    assert "min-height" in rule and "220px" not in rule


def test_the_chooser_defaults_to_what_the_note_proposes() -> None:
    """Defaulting to anything else would be the surface quietly disagreeing
    with the document it is displaying."""
    src = RENDERER.read_text(encoding="utf-8")
    fn = src.split("async function mountActuatorRow", 1)[1].split("\nasync function", 1)[0]
    assert "note-action-option" in fn
    assert "opt.number === proposed" in fn
    assert "payload.options ?? []" in fn, (
        "the surface parses the markdown itself; that is a second parser to "
        "keep in step with decisions.py"
    )
