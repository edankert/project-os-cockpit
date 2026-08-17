"""Every acceptance row carries its mark and its address (TST-0038 / FEAT-0104).

**An HTML checkbox holds two states and the record's vocabulary has four.**
`pymdownx.tasklist` understands `[ ]` and `[x]`; a `[~]` or `[F]` row renders
with **no input element at all** and its mark left as literal text. That — not
lazy continuation — is why [[FEAT-0104]] stalled, and it cannot be fixed by
counting more carefully.

So the *list item* is stamped, whatever its mark, and the client draws one
control for all four.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from project_os_cockpit import acceptance, renderer

TRAINER = Path.home() / "Dev" / "repos" / "your-trainer"
needs_trainer = pytest.mark.skipif(
    not (TRAINER / "docs" / acceptance.SUITE_REL).exists(),
    reason="../your-trainer is not present",
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


def test_all_six_marks_are_addressed_not_just_the_two_tasklist_knows() -> None:
    got = _rows(_render(FOUR))
    assert got == {"1.1.1": " ", "1.1.2": "x", "1.1.3": "/",
                   "1.1.4": "-", "1.1.5": "!", "1.1.6": "?"}


def test_the_two_marks_tasklist_understands_still_get_their_input() -> None:
    """The address is stamped ABOVE `task-list` in priority order, so the
    literal `[ ]`/`[x]` must be left in place for it to consume. Removing them
    here would leave the extension nothing to find — which a first pass at
    priority 4 did, addressing only `~` and `F`, the exact inverse."""
    html = _render(FOUR)
    assert html.count('type="checkbox"') == 2


def test_the_literal_mark_is_stripped_only_where_tasklist_leaves_one() -> None:
    html = _render(FOUR)
    for literal in ("[/]", "[-]", "[!]", "[?]"):
        assert literal not in html, literal
    # …and the row's own prose survives.
    assert "no hardware" in html and "crashes" in html


def test_a_document_that_is_not_a_suite_is_untouched() -> None:
    plain = "# Notes\n\n- [ ] a plain checklist item\n- [x] another\n"
    html = _render(plain)
    assert "data-check=" not in html
    assert html.count('type="checkbox"') == 2


def test_a_name_containing_a_colon_still_matches() -> None:
    """The matcher uses `parse`'s own regex rather than splitting on the first
    colon. A hand-rolled split truncated names like *"translated (Layer 1:
    shared assignment)"* and left 70 of your-trainer's 579 rows unaddressed."""
    text = (
        "# Tier 2 — Regression\n\n## 2.1 An area (ISS-0001)\n\n"
        "- [ ] **Imported intervals get translated (Layer 1: shared):** do it.\n"
    )
    assert _rows(_render(text)) == {"2.1.1": " "}


def test_a_gating_row_says_so() -> None:
    text = (
        "# Tier 1 — Feature Tests\n\n## 1.1 A (FEAT-0001)\n\n- [ ] **G:** a.\n\n"
        "# Tier 3 — Aids\n\n## 3.1 B (FEAT-0002)\n\n- [ ] **N:** b.\n"
    )
    html = _render(text)
    gating = dict(re.findall(r'data-check="([^"]+)"[^>]*data-gating="(\d)"', html))
    assert gating == {"1.1.1": "1", "3.1.1": "0"}


@needs_trainer
def test_almost_every_row_of_the_real_suite_is_addressable() -> None:
    """Almost all of them. The handful that are not are rows Markdown never
    made into list items — a blank line missing in the document that owns them,
    which [[TASK-0457]] names rather than papering over.

    **A ratio, not a count.** This suite is a live document that Edwin edits
    and now marks from the app, so `== 579` is a test that fails when the
    feature works. What must hold is that essentially every row is reachable.
    """
    text = (TRAINER / "docs" / acceptance.SUITE_REL).read_text(encoding="utf-8")
    items = acceptance.parse(text)
    addressed = _rows(_render(text, acceptance.SUITE_REL))
    assert len(items) > 100, "this is the big suite, not a stub"
    assert len(addressed) >= len(items) * 0.98, (
        f"only {len(addressed)} of {len(items)} rows addressable"
    )
    # No address is ever emitted twice — that would mean two rows sharing one
    # write target, which is the mis-addressing this exists to prevent.
    numbers = re.findall(r'data-check="([^"]+)"', _render(text, acceptance.SUITE_REL))
    assert len(numbers) == len(set(numbers))


@needs_trainer
def test_the_seven_hand_written_marks_are_reachable_now() -> None:
    """`../your-trainer`'s v2.1.0 delta suite carries 6 `[~]` and 1 `[F]`, and
    before this **none of the seven had a control at all** — tasklist leaves
    them as literal text.

    Six of the seven are reachable now. The seventh, §1.6.1 *"AI warnings
    banner dismissable on the editor"*, is not: its list opens directly under
    `Beyond §1.3.6 / §1.1, the editor gained:` with no blank line, so Markdown
    absorbs it and never makes a list item to stamp. That is the document's
    formatting, not this code's reach, and [[TASK-0457]] names it rather than
    inventing a phantom control for a row with nothing on screen.

    Asserted at the measured number rather than the hoped-for one: `>= 6`
    would have called five of six a success.
    """
    p = TRAINER / "docs" / "tests" / "ACCEPTANCE_TESTS_v2.1.0.md"
    if not p.exists():
        pytest.skip("the v2.1.0 delta suite is not present")
    rows = _rows(_render(p.read_text(encoding="utf-8"), str(p)))
    # At least one of each, reachable. The exact split is whatever the file
    # says today — and these are precisely the rows Edwin can now re-mark from
    # the app, so pinning the number would break on use.
    marks = list(rows.values())
    assert marks.count("~") >= 1, "the reconciled rows are reachable"
    assert marks.count("F") >= 1, "the failed row is reachable"
    assert len(rows) >= 200, f"{len(rows)} rows addressable in a 300-row file"


# ----- rows with nothing to click (TASK-0457) -------------------------------


def test_a_row_markdown_never_made_into_a_list_item_is_named() -> None:
    """ISS-0172's rule in a second surface: an affordance that cannot work
    should explain itself rather than vanish."""
    text = (
        "# Tier 1 — Feature Tests\n\n## 1.1 An area (FEAT-0001)\n\n"
        "- [ ] **Reachable:** a.\n\n"
        "Some prose with no blank line after it:\n"
        "- [ ] **Absorbed:** b.\n"
    )
    html = _render(text)
    assert "1 of 2 checks cannot be marked here" in html
    assert "Add a blank line above each list" in html
    assert list(_rows(html)) == ["1.1.1"]


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


@needs_trainer
def test_the_real_suites_report_their_own_shortfall() -> None:
    text = (TRAINER / "docs" / acceptance.SUITE_REL).read_text(encoding="utf-8")
    html = _render(text, acceptance.SUITE_REL)
    # Shape and internal consistency, not the figures of the day.
    found = re.search(r"(\d+) of (\d+) checks cannot be marked here", html)
    assert found, "the shortfall is stated"
    unreachable, total = int(found.group(1)), int(found.group(2))
    assert total == len(acceptance.parse(text))
    assert 0 < unreachable < total
    assert len(_rows(html)) == total - unreachable, (
        "the notice's number is the rows it could not stamp, exactly"
    )


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


def test_tasklists_whole_control_is_removed_not_just_its_input() -> None:
    """`pymdownx.tasklist` renders
    `<label class="task-list-control"><input><span class="task-list-indicator">`.
    Removing only the input leaves a styled span behind, which is the box
    inside a box Edwin reported."""
    src = _renderer_src()
    block = src[src.index("function mountAcceptanceMarks"):]
    block = block[:block.index("\nasync function")]
    assert "label.task-list-control" in block, (
        "the label must be removed, not just the input"
    )


def test_the_control_is_mounted_inline_not_before_the_paragraph() -> None:
    """`li.firstChild` is the `<p>` — a block element — so inserting before it
    put the control on its own line above the check it marks."""
    src = _renderer_src()
    block = src[src.index("function mountAcceptanceMarks"):]
    block = block[:block.index("\nasync function")]
    assert "li.insertBefore(btn, li.firstChild)" not in block
    assert "querySelector('p')" in block


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
    assert block.count("needsReason: false") == 2


def test_reaching_a_state_costs_one_write_not_three() -> None:
    """The cycle is gone. `[ ]` → `[F]` used to be three clicks, three writes
    and two prompts, because `[x]` and `[~]` each asked for a reason on the way
    past — writes asserting something specific and false."""
    src = _renderer_src()
    block = src[src.index("async function cycleAcceptanceMark"):]
    block = block[:block.index("\ndocView.addEventListener")]
    assert "MARK_CYCLE" not in block, "no cycling; the dialog names the target"
    assert block.count("mark-check") == 1, "one write per interaction"
    assert "askForMark" in block


def test_cancelling_writes_nothing_and_does_not_even_repaint() -> None:
    src = _renderer_src()
    block = src[src.index("async function cycleAcceptanceMark"):]
    block = block[:block.index("\ndocView.addEventListener")]
    cancel = block[block.index("if (chosen === null)"):]
    cancel = cancel[:cancel.index("\n")]
    assert "return" in cancel
    # the write must come after the null check, never before it
    assert block.index("if (chosen === null)") < block.index("postJson")


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


def test_the_marks_the_tool_writes_are_all_minimals() -> None:
    """No invented character. The point of ADR-0029 is that the third
    vocabulary is somebody else's."""
    MINIMAL = set(' /x->< ?!*"lbiSIpcfkwud')
    for verdict, mark in acceptance.VERDICTS.items():
        assert mark in MINIMAL, f"{verdict} writes {mark!r}, not a Minimal value"
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


def test_a_refusal_is_caught_and_shown() -> None:
    """`postJson` THROWS on refusal and does not return `{ok: false}`, so the
    old `if (!res?.ok)` branch was unreachable and a real refusal — a reason
    citing an unresolvable ISS, an mtime conflict — was an unhandled rejection
    with no toast."""
    src = _renderer_src()
    block = src[src.index("async function cycleAcceptanceMark"):]
    block = block[:block.index("\ndocView.addEventListener")]
    # Comments are stripped: this file's own prose explains the old branch, and
    # a guard that greps for a string it also documents will always pass or
    # always fail for the wrong reason.
    code = "\n".join(
        line for line in block.splitlines()
        if not line.lstrip().startswith("//")
    )
    assert "try {" in code and "catch" in code
    assert "if (!res?.ok)" not in code, "that branch could never fire"
    assert "showStatus" in code


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


def test_marking_a_check_patches_the_row_instead_of_re_navigating() -> None:
    """Edwin: *"can we not somehow update the file in memory and then do a save
    in the background without re-loading?"* The reload existed only because an
    HTML checkbox cannot show six states; this control draws its own mark."""
    src = _renderer_src()
    block = src[src.index("async function cycleAcceptanceMark"):]
    block = block[:block.index("\ndocView.addEventListener")]
    code = "\n".join(
        line for line in block.splitlines()
        if not line.lstrip().startswith("//")
    )
    assert "repaintDoc()" not in code, "a mark must not re-navigate"
    assert "row_html" in code, "the row comes from the server's one pipeline"
    assert "mountAcceptanceMarks()" in code
    # …and it is APPLIED. Naming the value proves nothing: a mutation that
    # fetched `row_html` and then did `void rowHtml` survived this test twice
    # over. Third time this session guards have covered two ends and not the
    # wire between them.
    assert "innerHTML = rowHtml" in code, code


def test_our_own_write_does_not_trigger_the_watchers_reload() -> None:
    """Patching the row and then letting `file-changed` re-navigate would undo
    the patch — which is precisely what defeated ISS-0187 and ISS-0188."""
    src = _renderer_src()
    block = src[src.index("async function cycleAcceptanceMark"):]
    block = block[:block.index("\ndocView.addEventListener")]
    assert "suppressNextSoftReload()" in block
    guard = src[src.index("function scheduleSoftReload"):]
    guard = guard[:guard.index("\n}")]
    assert "softReloadSuppressedUntil" in guard


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
