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
    all options?"*

    **The ledger's vocabulary** (ADR-0037), and the three answers to *"not
    run"* are drawn apart because they do different things: `na` clears and
    persists, `excused` clears **this release only**, `blocked` keeps
    blocking. Everything but a plain `pass` — and `clear`, which records
    nothing — must say why.
    """
    src = _renderer_src()
    block = src[src.index("const MARK_CHOICES"):]
    block = block[:block.index("function askForMark")]
    for verdict in ("pass", "partial", "na", "excused", "blocked", "fail",
                    "question"):
        assert f"verdict: '{verdict}'" in block, verdict
    # Six: partial, na, excused, blocked, fail, question. Each moves the gate
    # on somebody's judgement, and an option that asks for nothing is exactly
    # the `[!]` gap ISS-0177 records.
    assert block.count("needsReason: true") == 6
    # Two: a plain `pass`, and **needs-re-run** (TASK-0466) — not a mark at all
    # but an ACT, and the only one requiring a change rather than a reason.
    assert block.count("needsReason: false") == 2
    assert block.count("needsChange: true") == 1
    assert "verdict: 'needs-re-run'" in block

    # **`clear` is gone, and that is decision 5 reaching the dialog.** There
    # is no way to record that nobody walked something, because you do not
    # record that you did not do a thing — the absence of an entry says it.
    # The consequence for a walker is real and deliberate: un-recording a
    # verdict means naming the change that invalidated it, which is
    # `needs-re-run` and requires a change id that resolves.
    assert "verdict: 'clear'" not in block
    # **`canceled` is gone too.** It was one value carrying two questions —
    # "cannot apply here" and "not done this cycle" — and the difference
    # between them is whether the exception comes back.
    assert "label: 'Canceled'" not in block




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

    # THIS repo's corpus first, because it is the only one that exists
    # everywhere this test runs. Reaching for ~/Dev/repos alone made the guard
    # unrunnable on a CI runner, where it found no suite and correctly refused
    # to pass on nothing (ISS-0256). The fleet repos still join in when they
    # are present — they carry marks this one does not, which is the whole
    # reason the guard walks real corpora instead of a fixture.
    here = _Path(__file__).resolve().parent.parent
    corpora = [here / "docs"]
    fleet = _Path.home() / "Dev" / "repos"
    corpora += [fleet / r / "docs" for r in ("your-sudoku", "your-trainer")]

    marks: set[str] = set()
    for docs in corpora:
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


def test_a_mistyped_mark_is_never_settled_by_either_reader() -> None:
    """`" x"` and `"x "` must stay unrecognised, in BOTH copies of the rule.

    `_ITEM_RE`'s own comment is the reason: *"`\\" x\\".strip()` is `\\"x\\"`, so a
    parser written from that comment would read a typo as a walked check."*
    Stripping before matching moves a typo from *unrecognised and therefore
    blocking* to `done` and settled — the one change in this migration that
    could let a release through on a check nobody walked.

    **Two readers, and the first fix reached only one.** `acceptance.normalise_mark`
    was corrected and `validate-docs.py::_acceptance_is_settled` was not — which
    is the copy that gates pre-commit and CI, so the fix landed everywhere except
    where it mattered most. Both are asserted here, and the validator is loaded
    from disk so the bundled copy cannot drift silently either.

    A WORD may carry surrounding space, because YAML scalars do and `Done` is
    not a typo. A CHARACTER may not.
    """
    import importlib.util
    from pathlib import Path as _Path

    from project_os_cockpit import acceptance as _acc

    for typo in (" x", "x ", " /", "- ", "\tx"):
        assert _acc.normalise_mark(typo) not in _acc._CHECKED_MARKS, typo
        assert _acc.normalise_mark(typo) not in _acc._RECONCILED_MARKS, typo
        assert _acc.normalise_mark(typo) not in _acc._EXCEPTED_MARKS, typo
    assert _acc.normalise_mark("x") == "done"
    assert _acc.normalise_mark(" Done ") == "done", "a word may carry space"

    root = _Path(__file__).resolve().parent.parent
    for copy in (root / "tools" / "scripts" / "validate-docs.py",
                 root / "src" / "project_os_cockpit" / "validate_docs_bundled.py"):
        spec = importlib.util.spec_from_file_location(f"v_{copy.stem}", copy)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for typo in (" x", "x ", " -"):
            index = {"T": ("path", {"mark": typo, "level": "acceptance"})}
            assert not module._acceptance_is_settled("T", index), (
                f"{copy.name} settles the typo {typo!r} — a release can pass on "
                "a check nobody walked"
            )
        index = {"T": ("path", {"mark": " done ", "level": "acceptance"})}
        assert module._acceptance_is_settled("T", index), copy.name


# ----- the stored form never reaches a screen (ISS-0211) --------------------


#: The seven words `mark:` may hold since ISS-0200. Storage, deliberately — a
#: file wants an unambiguous token that survives an editor eating a `[ ]`.
MARK_WORDS = (
    "todo", "done", "incomplete", "canceled", "important", "question", "rerun",
)


def test_no_surface_brackets_a_raw_mark_rather_than_its_glyph() -> None:
    """ISS-0211, and the reason it is a *guard* rather than three edits.

    ISS-0200 changed `mark:` from characters to words in 669 notes. Three
    render sites read `mark` directly instead of going through `MARK_GLYPH`,
    and the migration re-keyed the maps by hand without noticing:

    * the picker token bracketed the value, so the dialog read
      **`[done] Done — walked and passed`** — the word in brackets beside a
      label that already says it;
    * `item.mark === '-'` became permanently false, so **canceled rows lost
      their strikethrough**;
    * a gate row's `title` said `TST-0123 — done` where the glyph had been.

    **Two of the three fail silently.** A dead comparison raises nothing and a
    `title` attribute is invisible until hovered, which is why a person reading
    a screen found this and neither the type-checker nor the suite did.

    This is the second vocabulary change in two phases to leave a live surface
    on a stale key — `MARK_MEANING` read *"unrecognised · 33"* in all three
    suites after the first. Re-keying by hand a third time is the failure this
    asserts against.
    """
    src = _renderer_src()
    # Bracketing a value is how a glyph is drawn (`[x]`, `[/]`). Bracketing a
    # *mark-bearing expression* means the stored word reaches the screen.
    offenders = re.findall(r"`\[\$\{([^}]*\bmark\b[^}]*)\}\]`", src)
    allowed = {"mark", "choice.mark", "item.mark"}   # only inside a ?? fallback
    for expr in offenders:
        assert expr.strip() in allowed, (
            f"`[${{{expr}}}]` brackets a mark directly — render it through "
            "MARK_GLYPH, which maps `done` to `[x]` and already handles the "
            "legacy characters"
        )
    # Every bracketed fallback must sit behind a MARK_GLYPH lookup, so the raw
    # form is reachable only when the glyph map has no entry at all.
    for expr in offenders:
        pattern = r"MARK_GLYPH\[[^\]]+\]\s*\?\?\s*`\[\$\{" + re.escape(expr) + r"\}\]`"
        assert re.search(pattern, src), (
            f"`[${{{expr}}}]` is not guarded by a `MARK_GLYPH[...] ??` — it "
            "would render the stored word whenever the map is consulted"
        )


def test_no_surface_compares_a_mark_to_a_legacy_character() -> None:
    """The dead-comparison half, which removed styling and raised nothing.

    `item.mark === '-'` was true before ISS-0200 and false forever after. The
    marks a surface receives are normalised words; a comparison against a raw
    character is either dead or about to be, and `MARK_CLASS` is the map that
    answers the question it was asking.
    """
    src = _renderer_src()
    legacy = re.findall(
        r"\.mark\s*(?:\|\|\s*'[^']*'\s*\)?\s*)?===\s*'([^']{0,2})'", src)
    for ch in legacy:
        assert ch in MARK_WORDS, (
            f"a surface compares a mark against the literal {ch!r}; marks "
            "reaching a surface are words (ISS-0200), so this is dead. Use "
            "MARK_CLASS, which maps both forms to one class name"
        )


# ----- a release page records nothing (ADR-0035 / ISS-0210) -----------------


def test_a_gate_row_carries_a_token_and_never_a_control() -> None:
    """ADR-0035, and the guard neither previous removal left behind.

    `REL-0013 · 2.1.7` in `your-trainer` rendered **sixty blocking checks, each
    with a live mark button** — `gateMark(item, releaseId, actionable=true)`.
    The page whose entire purpose is to report that a release is not ready
    offered sixty controls that make it ready, which is not a hypothetical
    about carelessness: the rows are sorted by nothing except *blocks*, and the
    control beside each one is the one that stops it blocking.

    Edwin: *"definitely do not allow these acceptance tests to be checked."*

    **Re-anchored 2026-08-20 ([[ISS-0244]]), and the claim got stronger.** This
    read the body of `gateMark` and asserted it built a span and nothing else.
    `gateMark` no longer exists — Edwin: *"just show them as a list of tst
    links like the features below"* — so there is no longer a mark element on a
    gate row to be static ABOUT. The guard therefore moves up to the row
    builder itself and asserts the property that actually matters and always
    did: **nothing a gate row builds can record a verdict.**

    Asserted on the row builder rather than on the absence of one helper,
    because this control has now been removed three times — [[ISS-0192]] from
    the rendered document, [[ADR-0035]] from the gate, and this — and each
    removal that anchored on a name left the next one unguarded.
    """
    src = _renderer_src()
    body = src[src.index("function gateGroup("):]
    body = body[:body.index("\n}\n") + 3]

    assert "actionable" not in body, (
        "`actionable` is back. ADR-0035 deletes the parameter rather than "
        "defaulting it to false: a parameter with one live value is a decision "
        "waiting to be re-litigated by whoever adds the next caller"
    )
    assert "createElement('button')" not in body, (
        "a gate row builds a button — a release page reports the gate and "
        "records nothing (ADR-0035); walking happens where the steps are"
    )
    #: **Anchored on the ROW'S SHAPE, not on class names** (independent review,
    #: 2026-08-20). The previous version forbade the string `acc-mark` in this
    #: function. The reviewer re-added a glyph using `gate-mark` — a class
    #: whose CSS was still live — and every guard here stayed green. A guard
    #: that names one spelling of a thing is a guard the next spelling walks
    #: past, which is the third time that has happened on this control.
    #:
    #: So the claim is now about what the row IS: the `li` gets exactly the
    #: children the features row gets, and the FIRST of them is the id. A mark
    #: in the gutter has to be appended before the id, and there is no way to
    #: do that without failing this.
    #: **Exactly one add-a-child call, and it is the whole row.** Re-review
    #: 2026-08-20 defeated the previous version twice without using any of the
    #: forbidden vocabulary — `li.prepend(tok)` (not in its `append|appendChild`
    #: alternation) and an `li.appendChild(tok)` placed *after* the row's own
    #: `li.append(...)`. Both put a glyph back in the gutter with the suite
    #: green. Fourth spelling, fourth name-shaped guard, so the claim is now
    #: about the COUNT of ways a child can arrive rather than about names.
    adders = re.findall(
        r"^(?!\s*(?://|\*|/\*)).*\bli\.(append|appendChild|prepend|replaceChildren"
        r"|insertBefore|insertAdjacentElement|insertAdjacentHTML|innerHTML)\b.*$",
        body, re.M)
    assert len(adders) == 1, (
        "a gate row gains children by more than one route, so the row's shape "
        f"is no longer fixed by reading one line: {adders}"
    )
    call = re.search(r"^\s*li\.append\((.*)\);\s*$", body, re.M)
    assert call, "the single add-a-child call is not the row's own `li.append(...)`"
    assert call.group(1).startswith("n, t, a"), (
        "the gate row's children no longer start with id, title, meta — "
        f"something is occupying the gutter again (ISS-0244): {call.group(1)!r}"
    )
    #: And nothing in the function reaches for the mark vocabulary at all.
    #: Belt and braces over the shape check, on live code only.
    live = re.findall(r"^(?!\s*(?://|\*|/\*)).*\b(MARK_GLYPH|MARK_CLASS|acc-mark|gate-mark)\b.*$",
                      body, re.M)
    assert not live, (
        f"a gate row is reaching for the mark vocabulary again: {live}"
    )
    #: The row is still a LINK to the check — the one handler it may carry.
    #: Asserted so "no controls" is not satisfied by making the row inert.
    assert "navigateTo(item.rel" in body, (
        "a gate row no longer opens its check; walking has to stay one click "
        "away, or the removal of the control removed the way to act as well"
    )


def test_the_release_page_has_no_write_path_for_a_check() -> None:
    """The helper goes too, not just its caller.

    `markGateRow` was `walkOneCheck` plus a repaint, reachable only from the
    control above. Left unreferenced it is how the next caller re-acquires the
    behaviour a decision just removed — so ADR-0035 deletes it, and this says
    so where a reader adding a release-page feature will meet it.
    """
    src = _renderer_src()
    calls = re.findall(r"^(?!\s*(?://|\*)).*\bmarkGateRow\s*\(", src, re.M)
    assert not calls, f"markGateRow is live again: {calls}"

    # `buildGateSection`'s own body — not the span up to the next interface,
    # which contains `walkOneCheck`'s definition and would make this vacuous
    # in the noisiest possible way: passing because it matched a declaration.
    start = src.index("function buildGateSection")
    body = src[start:src.index("\n}\n", start) + 3]
    assert "walkOneCheck" not in body, (
        "the gate section reaches walkOneCheck — that is the write path "
        "ADR-0035 removes from any page whose subject is a release"
    )


def test_no_surface_renders_a_raw_mark_unbracketed_either() -> None:
    """[[REQ-0045]]'s title: *"no surface may render the stored form."*

    `test_no_surface_brackets_a_raw_mark_rather_than_its_glyph` guards the
    **bracketed** shape, because that is how [[ISS-0211]] presented. Review
    2026-08-20 showed a raw mark reaching a live surface without brackets and
    walking straight past it:

        bits.push(`marked ${item.mark}`)          // renderer.ts

    drawing **`marked done`** on the release page's Quiet and Stale-evidence
    groups — the stored word, on screen, while REQ-0045 c2 was ticked as
    guarded. The criterion was true about the guard and false about the code.

    So this asks the other half: no template may interpolate `.mark` directly
    into display text. The value must go through `MARK_GLYPH` (the glyph),
    `MARK_TITLE` (the sentence) or `markWord` (the one-word form) — all three
    of which are keyed maps, so an unrecognised mark reports itself instead of
    echoing the note back at the reader.
    """
    import re

    src = _renderer_src()
    #: **Comments stripped first.** The first cut scanned raw source and
    #: matched the `//:` comment explaining this very defect — the sixth
    #: over-broad text guard this phase to flag its own prose. A claim has to
    #: be scoped to the code it is a claim about.
    code = "\n".join(
        ln for ln in src.splitlines()
        if not ln.lstrip().startswith(("//", "/*", "*"))
    )
    bad = []
    for m in re.finditer(r"\$\{[^}]*\.mark\}", code):
        if "MARK_" in m.group(0) or "markWord" in m.group(0):
            continue
        line = code[code.rfind("\n", 0, m.start()) + 1:
                    code.find("\n", m.end())]
        #: The one permitted raw render: the `?? [${…}]` fallback beneath a
        #: `MARK_GLYPH[…]` lookup. An unrecognised mark shows itself in
        #: brackets, which is the honest failure — hiding it would make a
        #: mis-keyed map look like a missing row. Narrow to that exact idiom,
        #: so a bare `${choice.mark}` (review's mutant) still fails.
        if "MARK_GLYPH[" in line and "??" in line:
            continue
        bad.append(m.group(0))
    assert not bad, (
        "these interpolate a stored mark straight into display text; route "
        f"them through MARK_GLYPH / MARK_TITLE / markWord: {bad}"
    )

    #: And the helper the fix introduced reads the map rather than the value,
    #: so it cannot become an echo with a longer name.
    i = src.index("function markWord(")
    body = src[i:src.index("\n}", i)]
    assert "MARK_TITLE[mark]" in body, body
    assert "return mark" not in body, (
        "markWord echoes the stored value; that is the defect wearing a "
        "function call"
    )
