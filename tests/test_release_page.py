"""The release page, and the guard that would have caught ISS-0176 (TST-0033).

The page exists because a left-pane row popping a dialog is the wrong shape —
the navigator navigates, the centre pane acts. It also removes the dialog,
which matters more than it sounds: `window.prompt` is not implemented in
Electron and had been dead in **five** places across four shipped features.

Every one of those features had tests on its payload, its write path and its
endpoint. None pressed the button. `test_the_renderer_never_calls_window_prompt`
is the assertion that was missing.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from project_os_cockpit import cockpit, publication
from project_os_cockpit.index import Index

RENDERER = (
    Path(__file__).resolve().parents[1]
    / "desktop" / "src" / "renderer" / "renderer.ts"
)
SUITE = (
    "# Tier 1 — Feature Tests\n\n## 1.1 Area (FEAT-0001)\n"
    "- [ ] **A:** do it.\n- [x] **B:** done.\n"
)


def _docs(tmp_path: Path, *, suite: bool = True) -> Path:
    d = tmp_path / "docs"
    (d / "tests").mkdir(parents=True)
    if suite:
        (d / "tests" / "ACCEPTANCE_TESTS.md").write_text(SUITE, encoding="utf-8")
    (d / "features" / "f").mkdir(parents=True)
    (d / "features" / "f" / "FEAT-0001-F.md").write_text(
        '---\ntype: "[[feature]]"\nid: FEAT-0001\ntitle: "A feature"\n'
        "status: done\n---\n", encoding="utf-8",
    )
    return d


def _rel(docs: Path, rid: str, status: str, version: str,
         preparing: str = "", features: str = "[]") -> None:
    d = docs / "releases"
    d.mkdir(parents=True, exist_ok=True)
    body = (
        f'---\ntype: "[[release]]"\nid: {rid}\ntitle: "R"\n'
        f'status: {status}\nversion: "{version}"\nfeatures: {features}\n'
    )
    if preparing:
        body += f'preparing: "{preparing}"\n'
    (d / f"{rid}-R.md").write_text(body + "---\n", encoding="utf-8")


# ---- the payload ---------------------------------------------------------


def test_next_answers_even_with_no_release_note(tmp_path: Path) -> None:
    """The ordinary case: the open release is derived and nothing is written
    until a person declares one."""
    docs = _docs(tmp_path)
    d = publication.release_payload(docs.parent, Index.build(docs), "next")
    assert d["exists"] is False
    assert d["preparing"] is False
    assert d["contents"]["kind"] == "derived"
    assert d["contents"]["count"] == 1


def test_contents_come_from_the_existing_computation(tmp_path: Path) -> None:
    """`unreleased_payload`'s own keys — `items` and `since` — read rather
    than near-missed. A second vocabulary for one computation is how two
    surfaces come to disagree, and the first draft of this invented `rows`
    and `latest` and silently reported nothing."""
    docs = _docs(tmp_path)
    _rel(docs, "REL-0001", "released", "1.0.0")
    d = publication.release_payload(docs.parent, Index.build(docs), "next")
    assert d["contents"]["since"] == "REL-0001"
    assert [r["id"] for r in d["contents"]["rows"]] == ["FEAT-0001"]


def test_a_shipped_release_reports_what_it_named(tmp_path: Path) -> None:
    """The frozen list is the record. Recomputing it would make a shipped
    release's contents drift as the project moved on."""
    docs = _docs(tmp_path)
    _rel(docs, "REL-0001", "released", "1.0.0", features='["[[FEAT-0001]]"]')
    d = publication.release_payload(docs.parent, Index.build(docs), "REL-0001")
    assert d["contents"]["kind"] == "frozen"
    assert d["contents"]["count"] == 1


def test_the_gate_rides_the_page(tmp_path: Path) -> None:
    docs = _docs(tmp_path)
    d = publication.release_payload(docs.parent, Index.build(docs), "next")
    assert d["gate"]["exists"] is True
    assert [b["name"] for b in d["gate"]["blocking"]] == ["A"]


def test_no_suite_is_reported_rather_than_read_as_clear(tmp_path: Path) -> None:
    docs = _docs(tmp_path, suite=False)
    d = publication.release_payload(docs.parent, Index.build(docs), "next")
    assert d["gate"]["exists"] is False
    assert d["gate"]["blocked"] is False


def test_the_row_navigates_to_the_page(tmp_path: Path) -> None:
    """Edwin: *"I would have expected that if I selected the Next Release
    item that this would bring up a virtual page."* It used to carry an action
    that popped a dialog — the wrong shape, and dead besides."""
    docs = _docs(tmp_path)
    groups = {
        g["key"]: g for g in cockpit.nav_payload(
            Index.build(docs), "publication", project_root=docs.parent,
        )["groups"]
    }
    nxt = groups["release-next"]
    assert nxt["url"] == "~release/next"
    assert nxt["type"] == "release"


# ---- ISS-0176 ------------------------------------------------------------


def test_the_renderer_never_calls_window_prompt() -> None:
    """**The assertion that was missing for four features.**

    Electron removed `window.prompt` in v3 and this app is on 32. Five call
    sites were dead in the desktop shell — drafting a release, reconciling a
    criterion, filing an issue from a failure, annotating a design, and
    preparing a release — and every one worked in the browser cockpit, which
    is why it went unnoticed for months.

    A comment saying "do not use prompt" would not have caught it. This does.
    """
    src = RENDERER.read_text(encoding="utf-8")
    code = [
        line for line in src.splitlines()
        if "window.prompt" in line
        and not line.lstrip().startswith(("//", "*", "/*"))
    ]
    assert code == [], code


def test_the_replacement_exists_and_is_shared() -> None:
    """One input, not five. The next call site cannot be written the broken
    way by copying a neighbour, because no neighbour does it that way."""
    src = RENDERER.read_text(encoding="utf-8")
    assert "function askForText(" in src
    # Four, not five: `promptPrepareRelease` was deleted by FEAT-0107 — the
    # version field on the release page is the only way to start one now.
    assert src.count("await askForText(") >= 4, src.count("await askForText(")


# ---- ISS-0190: the errand comes before the inventory ----------------------


def _body_of(src: str, signature: str) -> str:
    """The source of one function, bounded by its OWN end.

    Bounding a slice on a distant landmark is how an earlier edit in this
    phase removed 5315 lines of `renderer.ts` in a single replacement — the
    typechecker caught it, and the rule since is that the boundary is
    computed. Brace-counted from the opening `{` of the signature.
    """
    start = src.index(signature)
    depth = 0
    for i in range(src.index("{", start), len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[start:i + 1]
    raise AssertionError(f"{signature} never closes")


def test_the_gate_is_built_before_what_is_in_the_release() -> None:
    """Edwin: *"move the acceptance tests section to the top ... since this
    needs to be completed (the features/issues are things that simply ship
    with this release)"*.

    Asserted on the ORDER OF THE APPENDS inside `buildReleasePage`, which is
    what puts one section above another — not on the order the sections are
    declared, and not on either name appearing in the file.
    """
    body = _body_of(
        RENDERER.read_text(encoding="utf-8"), "function buildReleasePage(",
    )
    gate = body.index("wrap.appendChild(gateSection)")
    # The features list — the section that used to be first.
    contents = body.index("section.appendChild(list);")
    assert gate < contents, (
        "the gate section is appended after the release's contents, so it "
        "renders below them"
    )
    # And it is genuinely the first thing after the header/version controls:
    # nothing else may be appended between them.
    between = body[body.index("wrap.append(start, err);"):gate]
    assert "wrap.append" not in between.replace("wrap.append(start, err);", ""), (
        f"something is appended between the header and the gate: {between!r}"
    )


def test_a_gate_row_wears_the_documents_control_and_no_buttons() -> None:
    """Edwin: *"remove the buttons on the right, if you want you can have the
    checkbox on the left as long as the check box functionality is the same as
    in the .md file."*

    `Pass · Partial · Fail` was a second vocabulary — three verbs against the
    document's six marks — for one act on one check.
    """
    src = RENDERER.read_text(encoding="utf-8")
    assert "function verdictControls(" not in src, (
        "the three verdict buttons are back"
    )
    body = _body_of(src, "function gateGroup(")
    # APPENDED, not merely built. A guard that asserted a mark token was
    # created and not that it was attached is how ISS-0186's last mutation
    # survived; creating a node is not showing it.
    assert "li.appendChild(gateMark(" in body, body[:400]
    # …and it is the row's FIRST child, which is what "on the left" means.
    first = body.index("li.appendChild(gateMark(")
    assert first < body.index("li.append(n, t, a"), (
        "the mark is added after the number and title, so it is not the "
        "row's left-hand column"
    )
    assert "review-btn" not in body, "a button crept back onto the row"


def test_the_walk_layer_still_writes_through_the_documents_own_path() -> None:
    """*"the same as in the .md file"* means the same dialog and the same
    endpoint, not a lookalike. Both are asserted as USED — the value reaching
    the call — rather than as names appearing somewhere in the function.

    **The gate-row half of this guard is gone, and deliberately** (ADR-0035).
    It asserted that `markGateRow` delegated to `walkOneCheck`; a release page
    no longer writes a check at all, so there is nothing to delegate. That the
    helper stays deleted is asserted in `test_acceptance_marks.py` — here it
    would read as an absence, which is the weakest possible form of the claim.

    What survives is the whole of the original property for the surface that
    *does* write: `~checks` and the check's own note.
    """
    src = RENDERER.read_text(encoding="utf-8")
    body = _body_of(src, "async function walkOneCheck(")
    assert "await askForMark({" in body, body
    assert "'/api/notes/mark-check'" in body, body
    # The reason and the verdict the dialog returned are what is sent. A
    # mutation posting a fixed verdict would pass a name-only check.
    assert "verdict: chosen.verdict" in body and "reason: chosen.reason" in body
    # A refusal is caught and shown. `postJson` THROWS; an `if (!res.ok)`
    # branch here would be unreachable (ISS-0187, on the other caller).
    assert "catch" in body and "showStatus(" in body


def test_the_walk_holds_the_readers_place() -> None:
    """A repaint that moves the reader is the defect ISS-0187/0188/0189 were
    three rounds of.

    Pinned on the ORDER (read, repaint, restore) and on the restore happening
    inside an animation frame as well, because ISS-0188's fix did exactly this
    one frame too early and a source-shape guard could not see it.

    **The `renderReleasePage(releaseId)` assertion is gone** (ADR-0035): it
    pinned the repaint the release page passed in, and the release page no
    longer marks anything. The scroll property itself belongs to
    `walkOneCheck` and is unchanged — it is what `~checks` still relies on.
    """
    src = RENDERER.read_text(encoding="utf-8")
    body = _body_of(src, "async function walkOneCheck(")

    def at(needle: str) -> int:
        # `str.index` raises ValueError when the thing is simply GONE, which
        # is the most likely regression here and the one that would report as
        # a crashed test rather than a failed assertion.
        assert needle in body, f"{needle!r} is not in markGateRow:\n{body}"
        return body.index(needle)

    read = at("const held = docView.scrollTop;")
    repaint = at("await repaint()")
    restore = at("docView.scrollTop = held;")
    frame = at("requestAnimationFrame(")
    assert read < repaint < restore, body[read:]
    assert repaint < frame, "the frame-deferred restore runs before the repaint"
    assert "docView.scrollTop = held" in body[frame:], (
        "the animation frame does not restore the position, so the "
        "synchronous restore is alone and lands before layout"
    )


def test_the_suite_opens_from_a_row_and_not_a_button() -> None:
    """Edwin: *"remove the open the acceptance tests button, just show this as
    a file link instead, similar to how the requirements are shown on that
    page."* Every other file on this page is a row you click."""
    src = RENDERER.read_text(encoding="utf-8")
    # Code lines only. The comment above the replacement quotes the button it
    # replaced, and a guard that a neighbouring sentence can satisfy is the
    # third failure mode this control has produced (ISS-0187).
    live = [
        line for line in src.splitlines()
        if "Open the acceptance tests" in line
        and not line.lstrip().startswith(("//", "*", "/*"))
    ]
    assert live == [], live
    body = _body_of(src, "function buildGateSection(")
    assert "scoped-rowlist" in body, "the suite has no file row"
    assert "fileRow.addEventListener('click'" in body
    assert "navigateTo(`/docs/${gate.rel}`)" in body
    # …and no primary button survives in the section.
    assert "is-primary" not in body, body


def _calls(src: str, opener: str) -> list[str]:
    """Every `opener…)` argument block, brace/paren-counted to its own close."""
    out: list[str] = []
    at = src.find(opener)
    while at != -1:
        depth = 0
        for i in range(at + len(opener) - 1, len(src)):
            if src[i] in "({":
                depth += 1
            elif src[i] in ")}":
                depth -= 1
                if depth == 0:
                    out.append(src[at:i + 1])
                    break
        at = src.find(opener, at + 1)
    return out


def test_no_gate_group_says_nothing_when_it_is_empty() -> None:
    """`None.` is on TASK-0318's contentless list, and an empty gate group is
    usually the *good news* on the page — it should be able to say so.

    Every group that renders a heading is checked, so a fourth group added
    next month is covered without this test being edited. The two collapsed
    groups are exempt by construction: their `<details>` only exists when they
    have rows, so their empty branch is unreachable.
    """
    body = _body_of(
        RENDERER.read_text(encoding="utf-8"), "function buildGateSection(",
    )
    headed = [c for c in _calls(body, "gateGroup({") if "heading" in c]
    assert len(headed) >= 2, f"the sweep found {len(headed)} headed groups"
    mute = [c for c in headed if not re.search(r"\bempty\b", c)]
    assert mute == [], mute
