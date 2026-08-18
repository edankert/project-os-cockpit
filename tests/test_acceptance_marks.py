"""The mark dialog, and the guarantee that no document carries a check any more.

**This module used to guard a treeprocessor.** An HTML checkbox holds two
states and the record's vocabulary has six, so every row of a rendered
`ACCEPTANCE_TESTS.md` was stamped with its mark and its address and the client
drew a control from them. That surface is gone (ISS-0192): every suite in the
fleet is `CHK-*` notes, and the walk is `~checks`.

Sixteen guards went with it — the six-mark addressing, the tasklist
interaction, the unreachable-row notice, the mount, the in-place row patch and
the watcher suppression. Each was correct about a mechanism that no longer
exists, and a guard for one of those reads as coverage.

What remains is what survived the move: **the dialog**, which was always
storage-independent, and one new guard for the property the deletion buys —
that no rendered document stamps a check address at all.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from project_os_cockpit import acceptance, renderer

TRAINER = Path.home() / "Dev" / "repos" / "your-trainer"
#: **Keyed on the SUITE, in either shape** (ADR-0030). This read
#: `(TRAINER / "docs" / acceptance.SUITE_REL).exists()` and reported
#: *"../your-trainer is not present"* — and the moment that repo migrated, the
#: repo was present, its suite was 579 notes, and eleven tests went quiet
#: saying the corpus was missing. Six of them were the release-gate delta,
#: which is exactly what the migration had to be checked against.
#:
#: A skip condition that names one storage shape is a guard that expires when
#: the storage changes, and it expires **silently and with a false reason** —
#: which is worse than failing, because a red test gets read.
needs_trainer = pytest.mark.skipif(
    not acceptance.load(TRAINER / "docs").exists,
    reason="../your-trainer has no acceptance suite in either shape",
)

#: The two tests below read a **rendered file-shaped suite** in `../your-trainer`
#: and assert the treeprocessor addresses its rows. That subject is gone: the
#: repo migrated its 579 rows to `CHK-*` notes on 2026-08-17, and no repo in the
#: fleet renders an acceptance document any more.
#:
#: Kept, with a condition that is TRUE, rather than deleted or left pointing at
#: `needs_trainer` — which would have skipped them for the wrong reason, the
#: exact defect the comment above records. They go when the document plumbing
#: goes ([[ISS-0192]]), which is the same commit that removes what they guard.
needs_file_shaped_suite = pytest.mark.skipif(
    not (TRAINER / "docs" / acceptance.SUITE_REL).exists(),
    reason="no repo stores its acceptance suite as a document any more "
           "(ADR-0030); these guard the plumbing ISS-0192 removes",
)

FOUR = (
    "# Tier 1 — Feature Tests\n\n## 1.1 An area (FEAT-0001)\n\n"
    "- [ ] **Unwalked:** a.\n\n"
    "- [x] **Passed:** b.\n\n"
    "- [/] **Partial:** c. **Partial pass 2026-08-17** — de-DE only\n\n"
    "- [-] **Canceled:** d. **Blocked 2026-08-17** — no hardware\n\n"
    "- [!] **Failed:** e. **FAILS 2026-08-17** — crashes\n\n"
    "- [?] **Unclear:** f. **Open 2026-08-17** — what is a slot?\n"
)


def _render(text: str, name: str = "x.md") -> str:
    return renderer.render_markdown_text(
        text, source_path=Path(name),
        resolver=lambda *a, **k: None, asset_resolver=lambda *a, **k: None,
    )


def _rows(html: str) -> dict[str, str]:
    """`{check number: mark}` for every addressed row."""
    out: dict[str, str] = {}
    for li in re.findall(r"<li[^>]*>", html):
        number = re.search(r'data-check="([^"]+)"', li)
        mark = re.search(r'data-mark="([^"]*)"', li)
        if number and mark:
            out[number.group(1)] = mark.group(1)
    return out


def test_a_document_that_is_not_a_suite_is_untouched() -> None:
    plain = "# Notes\n\n- [ ] a plain checklist item\n- [x] another\n"
    html = _render(plain)
    assert "data-check=" not in html
    assert html.count('type="checkbox"') == 2


# ----- rows with nothing to click (TASK-0457) -------------------------------


def test_a_suite_where_every_row_is_clickable_says_nothing() -> None:
    assert "acc-unreachable" not in _render(FOUR)


def test_the_notice_is_never_auto_fixed() -> None:
    """Reformatting somebody's document because it would be more convenient to
    click is a different act, and it would rewrite the file the gate reads. The
    count is stated; the blank line is theirs."""
    source = (
        "# Tier 1 — Feature Tests\n\n## 1.1 An area (FEAT-0001)\n\n"
        "Prose:\n- [ ] **Absorbed:** b.\n"
    )
    before = source
    _render(source)
    assert source == before


# ----- the affordance, reported from use (ISS-0185) -------------------------


def _renderer_src() -> str:
    return (
        Path(__file__).resolve().parents[1]
        / "desktop" / "src" / "renderer" / "renderer.ts"
    ).read_text(encoding="utf-8")


def _renderer_css() -> str:
    return (
        Path(__file__).resolve().parents[1]
        / "desktop" / "src" / "renderer" / "renderer.css"
    ).read_text(encoding="utf-8")


def test_the_mark_has_no_border_around_a_glyph_that_is_already_one() -> None:
    css = _renderer_css()
    block = css[css.index(".acc-mark {"):]
    block = block[:block.index("}")]
    assert "border: 0" in block, "a 1px box around a ring glyph is a box in a box"


def test_one_dialog_offers_every_option() -> None:
    """Edwin: *"maybe if we bring up a dialog, can we then have one dialog with
    all options?"* Six choices now (ADR-0029), and the four that move the gate
    on somebody's judgement cannot be taken without a reason."""
    src = _renderer_src()
    block = src[src.index("const MARK_CHOICES"):]
    block = block[:block.index("function askForMark")]
    for verdict in ("pass", "partial", "excused", "failed", "question", "clear"):
        assert f"verdict: '{verdict}'" in block, verdict
    # Every mark that clears or holds the gate on someone's judgement needs a
    # reason; only a plain pass and a plain clear do not.
    assert block.count("needsReason: true") == 4
    # Three now: pass, clear, and **needs-re-run** (TASK-0466), which is not a
    # seventh mark — it writes `[ ]` like clear — but a seventh ACT, and the
    # only one that requires naming a change rather than a reason. Both
    # requirements are asserted, because an option that asks for nothing is
    # exactly the `[!]` gap ISS-0177 records.
    assert block.count("needsReason: false") == 3
    assert block.count("needsChange: true") == 1
    assert "verdict: 'needs-re-run'" in block


def test_the_dialog_refuses_a_reasonless_verdict_before_the_round_trip() -> None:
    """Refused in the client as well as the server, so the reader is told
    before the round trip rather than after it.

    The check moved into `refresh` when the dialog became select-then-save
    (ISS-0187): it now gates the Save button continuously rather than firing
    once on a click.
    """
    src = _renderer_src()
    block = src[src.index("const refresh = ()"):]
    block = block[:block.index("};")]
    assert "needs && !field.value.trim()" in block
    assert "save.disabled" in block


# ----- ADR-0029's table, exactly ---------------------------------------------


@pytest.mark.parametrize(("mark", "field", "blocks"), [
    (" ", None,           True),    # to-do
    ("x", "checked",      False),   # done
    ("X", "checked",      False),   # done, legal Markdown variant
    ("/", "reconciled",   False),   # incomplete
    ("~", "reconciled",   False),   # incomplete — legacy alias
    ("-", "excepted",     False),   # canceled
    ("!", "failed",       True),    # important
    ("F", "failed",       True),    # important — legacy alias
    ("?", "question",     True),    # question
    ("S", None,           True),    # one of Minimal's other sixteen
    ("@", None,           True),    # a typo
])
def test_the_mark_table_is_adr_0029s(
    mark: str, field: str | None, blocks: bool,
) -> None:
    """The whole decision, asserted as a table so a change to any row of it is
    a change to a test rather than a surprise in a release gate."""
    suite = acceptance.Suite(items=acceptance.parse(
        f"# Tier 1 — T\n\n## 1.1 A (FEAT-0001)\n\n- [{mark}] **X:** y.\n",
    ))
    item = suite.items[0]
    for candidate in ("checked", "reconciled", "excepted", "failed", "question"):
        assert getattr(item, candidate) is (candidate == field), (
            f"[{mark}] {candidate}"
        )
    assert bool(suite.blocking()) is blocks, f"[{mark}] blocking"


def test_the_legacy_aliases_behave_exactly_as_their_targets() -> None:
    """`~` and `F` are read forever and never written. If they ever diverge
    from `/` and `!`, seven rows in `../your-trainer` quietly change meaning."""
    def one(mark: str) -> tuple:
        item = acceptance.parse(
            f"# Tier 1 — T\n\n## 1.1 A (FEAT-0001)\n\n- [{mark}] **X:** y.\n",
        )[0]
        return (item.checked, item.reconciled, item.excepted,
                item.failed, item.question, item.settled)

    assert one("~") == one("/")
    assert one("F") == one("!")
    assert one("X") == one("x")


def test_the_vocabulary_is_minimals_distinctions_under_minimals_names() -> None:
    """No invented CONCEPT. ADR-0029's point survives ADR-0034's notation change.

    This asserted that every written mark was a Minimal *character*. ADR-0034
    replaced the characters with words (ISS-0200), so the character assertion
    would now fail on a decision rather than on a defect — and deleting it
    would take with it the property ADR-0029 was actually protecting: **the
    vocabulary is somebody else's, so a third one does not get invented.**

    So it guards the names instead. Six of the seven are Minimal's own labels
    for its own checkbox states; `rerun` is the deliberate addition, and it is
    asserted as such rather than waved through — an eighth value appearing
    without a decision is exactly what this guards.
    """
    MINIMAL_NAMES = {"done", "incomplete", "canceled", "important", "question", "todo"}
    written = set(acceptance.VERDICTS.values())
    invented = written - MINIMAL_NAMES - {"rerun"}
    assert not invented, (
        f"{sorted(invented)} is neither a Minimal label nor the one addition "
        "ADR-0034 records; a third vocabulary is what ADR-0029 exists to prevent"
    )
    assert "rerun" in written, "the seventh value is the reason ISS-0200 was worth doing"
    for legacy in acceptance.LEGACY_MARKS:
        assert legacy not in acceptance.VERDICTS.values(), (
            f"{legacy!r} is a legacy alias and must never be written"
        )


# ----- the affordance, second round (ISS-0186) ------------------------------


def test_the_control_shows_the_literal_mark_not_a_symbol_glyph() -> None:
    """Edwin: *"I don't like the design of the tick, keep the font simpler."*

    Three of the six were geometric symbol characters that fall back to
    whatever font the system carries them in. The literal renders identically
    everywhere and teaches the syntax a hand-editor needs.
    """
    src = _renderer_src()
    block = src[src.index("const MARK_GLYPH"):]
    block = block[:block.index("};") + 2]
    for decorative in ("○", "✓", "◐", "–", "●", "✕", "☐", "☑"):
        assert decorative not in block, f"{decorative} is a symbol glyph"
    for mark in ("x", "/", "-", "!", "?"):
        assert f"'[{mark}]'" in block or f'"[{mark}]"' in block, mark


def test_the_control_uses_the_monospace_face() -> None:
    css = _renderer_css()
    block = css[css.index(".acc-mark {"):]
    block = block[:block.index("}")]
    assert "--font-mono" in block
    assert "border: 0" in block


def test_the_dialog_is_one_column_and_wide_enough() -> None:
    """Six two-line buttons in a two-column grid wrapped their hints and fought
    for width. A list of consequences is what this is."""
    css = _renderer_css()
    actions = css[css.index(".ask-actions-mark {"):]
    actions = actions[:actions.index("}")]
    assert "flex-direction: column" in actions
    assert "grid-template-columns" not in actions
    card = css[css.index(".ask-card-mark {"):]
    card = card[:card.index("}")]
    assert "44rem" in card, "wider than the 34rem that was cramped"


def test_every_choice_shows_its_mark_in_the_dialog() -> None:
    """So the dialog and the row speak the same language: a reader picks
    `[!] Important` and the row then reads `[!]`."""
    src = _renderer_src()
    block = src[src.index("for (const choice of MARK_CHOICES)"):]
    block = block[:block.index("row.appendChild(btn)")]
    assert "mark-choice-mark" in block, "the token is built"
    assert "choice.mark" in block
    # …and ATTACHED. A first version of this guard checked only that the token
    # was created, and survived a mutation that built it and never appended it.
    # Creating a node is not showing it.
    append = next(l for l in block.splitlines() if "btn.append(" in l)
    assert "token" in append, append.strip()


# ----- the affordance, third round (ISS-0187) -------------------------------


def test_no_caller_assigns_scrolltop_straight_after_a_navigation() -> None:
    """The broken pattern, forbidden file-wide rather than in one function.

    `await navigateTo(...)` followed by `docView.scrollTop = ...` is always
    wrong for the same reason, and the next person to want it will reach for
    exactly that shape.
    """
    src = _renderer_src()
    lines = [
        line for line in src.splitlines()
        if not line.lstrip().startswith("//")
    ]
    for i, line in enumerate(lines[:-3]):
        if "await navigateTo(" not in line:
            continue
        window = "\n".join(lines[i:i + 4])
        assert "docView.scrollTop =" not in window, (
            f"line {i + 1}: a scroll assignment after a navigation is "
            f"overwritten by applyScrollTarget's frame\n{window}"
        )


def test_the_dialog_selects_then_saves() -> None:
    """Edwin went looking for a Done button. Clicking an option used to commit,
    and a reason-less one showed an error and returned, so the same button had
    to be clicked twice with nothing saying so."""
    src = _renderer_src()
    block = src[src.index("function askForMark("):]
    block = block[:block.index("\n}\n") + 3]
    # a commit path distinct from the option click
    assert "const commit = ()" in block
    assert "save.addEventListener('click', commit)" in block
    assert "save.disabled" in block
    # the option click SELECTS; it must not close the dialog
    click = block[block.index("btn.addEventListener('click', () => {"):]
    click = click[:click.index("});")]
    assert "picked = choice" in click
    assert "close(" not in click, "an option click must not commit"


def test_the_files_state_and_the_dialogs_choice_look_different() -> None:
    """`is-current` is the mark the file holds; `is-picked` is what Save will
    write. Conflating them is what made a second click invisible."""
    src = _renderer_src()
    block = src[src.index("function askForMark("):]
    block = block[:block.index("\n}\n") + 3]
    assert "is-current" in block and "is-picked" in block
    css = _renderer_css()
    for cls in (".mark-choice.is-current", ".mark-choice.is-picked"):
        assert cls in css, cls
    def declarations(selector: str) -> set[str]:
        """The rule's declarations, WITHOUT its selector.

        Comparing the whole block was useless: two rules always differ by the
        selector line, so the comparison passed even when the declarations were
        made identical. A mutation that made `is-picked` look exactly like
        `is-current` survived on that.
        """
        block = css[css.index(selector) + len(selector):]
        block = block[block.index("{") + 1:block.index("}")]
        return {d.strip() for d in block.split(";") if d.strip()}

    assert declarations(".mark-choice.is-current") != declarations(
        ".mark-choice.is-picked"), "the two states must not look the same"


def test_save_is_inert_until_the_verdict_is_complete() -> None:
    """So the dialog cannot be dismissed into a half-stated verdict."""
    src = _renderer_src()
    block = src[src.index("const refresh = ()"):]
    block = block[:block.index("};")]
    assert "save.disabled = picked === null || missing" in block
    assert "needsReason" in block


# ----- the watcher, the path two rounds of guards missed (ISS-0189) ---------


def test_a_held_position_wins_inside_the_animation_frame() -> None:
    """`applyScrollTarget` defers to `requestAnimationFrame`, so a held
    position has to be honoured INSIDE that frame and ahead of both existing
    branches — a synchronous restore around the call ran a frame early and was
    overwritten ([[ISS-0188]])."""
    src = _renderer_src()
    block = src[src.index("function applyScrollTarget("):]
    block = block[:block.index("\n}\n") + 3]
    raf = block[block.index("requestAnimationFrame(() => {"):]
    assert "keepScroll !== undefined" in raf
    assert raf.index("keepScroll !== undefined") < raf.index("if (frag)")
    assert raf.index("keepScroll !== undefined") < raf.index("if (fromHistory)")
    call = src[src.index("applyScrollTarget(pathOnly, frag"):]
    call = call[:call.index(";") + 1]
    assert "keepScroll" in call, call.strip()


def test_the_watchers_own_reload_holds_the_readers_place() -> None:
    """The path both earlier fixes missed. A file changing under an open
    document is not a reason to move the reader to the top of it — true for a
    mark, and equally true for an edit made in another editor."""
    src = _renderer_src()
    block = src[src.index("function scheduleSoftReload"):]
    block = block[:block.index("\n}\n") + 3]
    nav = block[block.index("void navigateTo("):]
    nav = nav[:nav.index(");") + 2]
    assert "keepScroll" in nav, nav.strip()


# ----- the guarantee the deletion buys (ISS-0192) ---------------------------


def test_no_rendered_document_carries_a_check_address() -> None:
    """A frozen release record must not wear a live control.

    `ACCEPTANCE_TESTS_v2.1.0.md` in `../your-trainer` is what v2.1.0 was
    measured against, and it still parses as 300 checks — so while the
    treeprocessor existed it stamped 300 addresses onto it and the client
    mounted 300 mark controls, writing to a file that no longer exists. Before
    the migration those clicks **succeeded, against the living suite**: a mark
    on a frozen record written into a different document.

    Asserted on a document that WOULD have been stamped, so the guard has a
    real subject rather than a trivially-passing one.
    """
    html = _render(FOUR, "docs/tests/ACCEPTANCE_TESTS.md")
    assert "data-check" not in html
    assert "data-mark" not in html
    assert "data-gating" not in html
    # …and the six marks are still just text, which is what a frozen record
    # should be: readable, and inert.
    assert "Partial" in html and "Canceled" in html


def test_the_client_mounts_no_control_on_a_document() -> None:
    """The other half: nothing looks for `li[data-check]` any more.

    **Code lines only.** The comments that record the deletion name the things
    deleted — they have to, or the next reader finds a hole with no account of
    it — and a guard that a neighbouring sentence can BREAK is the same defect
    as one a neighbouring sentence can satisfy, which this project has now
    written down twice.
    """
    live = [
        line for line in _renderer_src().splitlines()
        if not line.lstrip().startswith(("//", "*", "/*", "/**"))
    ]
    code = "\n".join(live)
    for gone in ("mountAcceptanceMarks", "cycleAcceptanceMark",
                 "li[data-check]", "dataset.checkName",
                 "suppressNextSoftReload"):
        assert gone not in code, f"{gone} is still called somewhere"


def test_every_mark_in_the_corpus_has_a_label_a_glyph_and_a_colour() -> None:
    """The tables must be keyed on what the notes actually carry (ISS-0200).

    **This is the guard that did not exist**, and its absence shipped a live
    break: after the vocabulary migration every surface table was still keyed on
    the characters, so in all three migrated suites the filter chips read
    `unrecognised · 33`, rows lost their colour through
    `MARK_CLASS[mark] ?? 'unknown'`, and `MARK_TITLE[mark] ?? ''` emptied both
    the tooltip and the aria-label.

    The three existing renderer guards stayed green throughout, because each
    asserts a table's CONTENTS and none asserts that its KEYS match the corpus.
    So this walks the real marks and demands every table answer.
    """
    import re as _re
    from pathlib import Path as _Path
    from project_os_cockpit import acceptance as _acc
    from project_os_cockpit.index import Index as _Index

    fleet = _Path.home() / "Dev" / "repos"
    marks: set[str] = set()
    for repo in ("project-os-cockpit", "your-sudoku", "your-trainer"):
        docs = fleet / repo / "docs"
        if not docs.is_dir():
            continue
        marks |= {i.mark for i in _acc.load(docs, _Index.build(docs)).items}
    assert marks, "no suite reachable — this guard would pass vacuously"

    missing = sorted(m for m in marks if m not in _acc.MARK_MEANING)
    assert not missing, f"MARK_MEANING has no label for {missing}; the filter bar reads 'unrecognised'"

    renderer = (_Path(__file__).resolve().parent.parent / "desktop" / "src"
                / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    for table in ("MARK_GLYPH", "MARK_TITLE", "MARK_CLASS", "VERDICT_FOR"):
        block = renderer[renderer.index(f"const {table}"):]
        block = block[:block.index("};")]
        absent = sorted(m for m in marks if not _re.search(rf"(^|[{{,\s]){m}\s*:", block))
        assert not absent, f"{table} has no entry for {absent}"
