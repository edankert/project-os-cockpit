"""FEAT-0146 / REQ-0062 — a link that names a design's ID opens the design bench.

`cockpit://your-health/DES-0002` used to open the design's note, a page of
text with one button on it. The mockups are on the bench, `~design/DES-0002`.
The rule that decides between the two is `designBenchTarget` in
`desktop/src/renderer/deep-link.ts`, and `desktop/tests/deep-link.test.mjs`
runs it in node.

These tests pin WHERE the renderer asks that rule, as source text. The rule is
asked in exactly one place, `locateAndOpen`, which every link resolved by ID
passes through. It must not be asked in `navigateTo`, because three controls
open a design note by its path on purpose: the bench header's ID chip, the
bench's `Read <ID> as a note` button, and an owed design's landing row. A rule
in `navigateTo` would send each of them back to the bench, and the reader
could never reach the note.

**The limit of these tests.** They pin where the call is written, not what the
window shows. A correct refactor that renames `locateAndOpen` turns them red,
and a bug inside `navigateTo`'s `~design/` branch does not. TST-0085 is the
check of the window.
"""

from __future__ import annotations

import re
from pathlib import Path

from conftest import js_function_body

REPO_ROOT = Path(__file__).resolve().parent.parent
RENDERER = REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts"


def _code_only(body: str) -> str:
    """The body without its comments, so a comment that names a function is
    not mistaken for a call to it."""
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    return re.sub(r"//[^\n]*", "", body)


def _calls(src: str, name: str) -> list[int]:
    """Where `name(` is called in `src`: not declared, not only mentioned."""
    code = _code_only(src)
    return [m.start() for m in re.finditer(rf"(?<!function )\b{name}\(", code)]


def test_locate_and_open_asks_the_design_rule_before_it_locates_the_note() -> None:
    """The one change REQ-0062 needs. If the lookup came first, every design
    would open its note, which is the defect this feature exists to remove."""
    src = RENDERER.read_text(encoding="utf-8")
    body = _code_only(js_function_body(src, "async function locateAndOpen("))
    assert "designBenchTarget(" in body, (
        "locateAndOpen no longer asks designBenchTarget; a link naming a "
        "design's ID opens the note again"
    )
    assert "/api/cockpit/locate" in body, "locateAndOpen no longer locates the note"
    assert body.index("designBenchTarget(") < body.index("/api/cockpit/locate"), (
        "the note is located before the design rule is asked"
    )
    # When the rule answers, the answer is opened and the lookup does not run.
    assert re.search(
        r"if \(bench\) \{ void navigateTo\(bench\); return; \}", body,
    ), "the bench target is not opened, or the lookup still runs after it"


def test_the_design_rule_is_asked_nowhere_else() -> None:
    """In particular not in `navigateTo`. The ID chip, the `Read <ID> as a
    note` button and an owed design's landing row all call
    `navigateTo(d.rel)`, and a rule there would make the note unreachable."""
    src = RENDERER.read_text(encoding="utf-8")
    calls = _calls(src, "designBenchTarget")
    assert len(calls) == 1, f"designBenchTarget is called {len(calls)} times in renderer.ts"
    for fn in ("async function navigateTo(", "async function navigateToInner("):
        assert "designBenchTarget" not in _code_only(js_function_body(src, fn)), (
            f"{fn} asks the design rule; every design note opened by path "
            "would bounce to the bench"
        )


def test_every_route_that_resolves_a_link_by_id_goes_through_locate_and_open() -> None:
    """The other half of the chain, added after the independent review found
    it unpinned. The tests above pin that `locateAndOpen` asks the rule; they
    say nothing about links still reaching `locateAndOpen`. Four one-line
    edits — deleting either same-project call, deleting the parked jump's
    call, or opening `target.id` as a path — passed every test in this file.

    The three routes are: a `cockpit://` link to the project on screen, a
    cross-repo link to the project on screen, and either kind parked while the
    window switches project.
    """
    src = RENDERER.read_text(encoding="utf-8")
    link = _code_only(js_function_body(src, "async function openCockpitLink("))
    assert "void locateAndOpen(target.id, project);" in link, (
        "a cockpit:// link naming an ID no longer resolves through locateAndOpen"
    )
    jump = _code_only(js_function_body(src, "async function jumpToCrossRepoNote("))
    assert "void locateAndOpen(noteId, project);" in jump, (
        "a cross-repo link to the project on screen no longer resolves through locateAndOpen"
    )
    ready = _code_only(src.split("case 'ready': {", 1)[1].split("case 'failed'", 1)[0])
    assert "void locateAndOpen(jump.noteId, jump.project);" in ready, (
        "a link parked while the window switches project is never resolved"
    )
    # …and the rule is asked about the note, not about the project. Both are
    # strings, so swapping them builds and every other test passes.
    locate = _code_only(js_function_body(src, "async function locateAndOpen("))
    assert "designBenchTarget(noteId," in locate, "the rule is asked about the wrong value"


def test_a_parked_link_is_consumed_only_by_the_project_it_names() -> None:
    """ISS-0298. Picking a third project on the rail while a link's switch is
    in flight used to hand the parked link to whichever workspace reported
    ready next — now a link can land on the wrong project's bench, not just
    its note. The reader is told when a link is dropped, because a link that
    silently does nothing looks the same as one that failed."""
    src = RENDERER.read_text(encoding="utf-8")
    # Dropped where the reader goes elsewhere, because the landing the link
    # suppressed is decided before the link would be consumed. Dropping it
    # only on arrival left the project they picked with an empty centre pane.
    opening = _code_only(js_function_body(src, "async function openWorkspace("))
    assert "pendingCrossRepoJump && !workspaceIsProject(" in opening, (
        "openWorkspace carries a parked link into a project the link never named"
    )
    assert "pendingCrossRepoJump = null;" in opening and "suppressLandingOnce = false;" in opening
    assert opening.index("pendingCrossRepoJump && !workspaceIsProject(") < opening.index("activeId = id;"), (
        "the link is dropped after the switch has already begun"
    )
    # Said where it survives: an earlier showStatus is overwritten by the
    # spawn line in the same turn, and the reader never sees it.
    assert "droppedLink\n    ? `${droppedLink} was not opened" in opening, (
        "the dropped link is not reported, or is reported before the spawn line"
    )
    assert opening.index("'Starting cockpit…'") > opening.index("droppedLink ="), (
        "the drop message cannot outlive the spawn message"
    )
    # …and the same rule where the link is consumed.
    ready = _code_only(src.split("case 'ready': {", 1)[1].split("case 'failed'", 1)[0])
    guard = ready.split("if (pendingCrossRepoJump) {", 1)[1]
    assert "const mine = workspaceIsProject(p.workspaceId, jump.project);" in guard, (
        "a parked link is consumed without checking which project arrived"
    )
    # The branch itself, not just the computation: `if (false)` above the same
    # lines left every other assertion here true.
    assert "if (!mine) {" in guard, "the arriving project is computed and not acted on"
    assert guard.index("const mine") < guard.index("void locateAndOpen("), (
        "the link is opened before the arriving project is checked"
    )
    # The match accepts a project id or the shell's own workspace id, the pair
    # `openCockpitLink` resolves a link against.
    matcher = _code_only(js_function_body(src, "function workspaceIsProject("))
    assert "ws.projectId" in matcher and "ws.id.toLowerCase()" in matcher


def test_a_reply_from_the_project_the_reader_left_never_lands() -> None:
    """Both fixes from the review's findings 7 and 8. Each reads the reply's
    body, then checks that the sidecar it asked is still the sidecar on
    screen. Checking before the body is read leaves a window in which the
    previous project's answer is drawn — which is the symptom ISS-0296 and
    ISS-0297 exist to remove."""
    src = RENDERER.read_text(encoding="utf-8")
    for fn, after in (
        ("async function loadOverviewScopePane(", "scopePhaseList = phases;"),
        ("async function fetchDesignRegister(", "designRegister = Array.isArray"),
    ):
        body = _code_only(js_function_body(src, fn))
        assert "base !== sidecarBaseUrl" in body, f"{fn} keeps no note of which project it asked"
        assert body.index("await resp.json()" if "Design" in fn else "await r.json()") \
            < body.index("base !== sidecarBaseUrl") < body.index(after), (
            f"{fn} checks for a switch before it reads the reply, not after"
        )


def test_the_link_reads_a_fresh_register_not_the_cached_one() -> None:
    """`fetchDesignRegister()` keeps the last good list when a fetch fails.
    Right after a project switch, that list belongs to the project the reader
    just left, so a failed fetch would send `DES-0002` to the wrong bench. The
    link must fetch the register now and fall back to the note.

    Checked in `locateAndOpen` and in the helper it fetches through, because
    swapping the fresh fetch for the cached one could be done in either.
    """
    src = RENDERER.read_text(encoding="utf-8")
    locate = _code_only(js_function_body(src, "async function locateAndOpen("))
    helper = _code_only(js_function_body(src, "async function designsForLink("))
    assert "designsForLink()" in locate, "locateAndOpen no longer fetches the register for the link"
    for name, body in (("locateAndOpen", locate), ("designsForLink", helper)):
        assert "fetchDesignRegister(" not in body, f"{name} reads the cached register"
        assert not re.search(r"\bdesignRegister\b", body), f"{name} reads the cached register"
    assert "/api/cockpit/designs" in helper
    # Every failure is an empty list, so the link opens the note as before.
    assert "catch {\n    return [];" in helper
    assert "if (!resp.ok) return [];" in helper


def test_a_project_switch_forgets_the_previous_projects_designs() -> None:
    """ISS-0297. A design note looks itself up in `designRegister` for its
    banner, and refetches the list only when it is empty. Left standing across
    a switch, the list is the previous project's: DES-0003 opened from a
    your-health link was looked up in your-health's designs and drawn with no
    banner. The same rule as the other per-project caches `openWorkspace`
    clears (ISS-0015)."""
    src = RENDERER.read_text(encoding="utf-8")
    body = _code_only(js_function_body(src, "async function openWorkspace("))
    assert "designRegister = [];" in body, "openWorkspace keeps the previous project's designs"
