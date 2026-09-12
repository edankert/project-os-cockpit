"""FEAT-0093 / ADR-0024 — a note in another project is one click away.

41 files in this repo and 6 in the template cite `ADR-0011` or `ADR-0013`.
Both notes exist, in `project-os-dev`, which no citation names — so every one
renders as a broken wikilink, and the cost was an hour spent preparing to
rewrite a decision that had been sitting upstream for a year.

The property under test is not that a link renders. It is that the two halves
of the lookup stay in the processes that can answer them: the sidecar knows
its own corpus and nothing else, the shell knows the fleet and no corpus.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from conftest import js_function_body

from project_os_cockpit.cockpit import project_id
from project_os_cockpit.wikilinks import resolve_text_to_html, split_cross_repo

REPO_ROOT = Path(__file__).resolve().parent.parent
REPO_DOCS = REPO_ROOT / "docs"
RENDERER = REPO_ROOT / "desktop" / "src" / "renderer" / "renderer.ts"


@pytest.mark.parametrize("target,expected", [
    ("project-os-dev#ADR-0011", ("project-os-dev", "ADR-0011")),
    ("your-health#ISS-0007", ("your-health", "ISS-0007")),
    ("project-os-dev#CHG-20260811-Gate-Green", ("project-os-dev", "CHG-20260811-Gate-Green")),
    # A bare id keeps its meaning exactly: this repo, or broken.
    ("ADR-0011", None),
    # Ordinary Obsidian heading links must NOT be swallowed — this is the
    # collision `#` buys, and the pattern is strict about the id half for it.
    ("Some Note#Some Heading", None),
    ("README#Edit policy", None),
    ("x#lowercase", None),
])
def test_the_cross_repo_form_is_recognised_and_nothing_else_is(target, expected) -> None:
    assert split_cross_repo(target) == expected


def test_a_cross_repo_link_carries_data_not_a_url() -> None:
    """The sidecar serves one repo. Emitting an `href` it cannot honour would
    be the surface asserting something it does not know — so it emits the two
    parts and the shell, which holds the fleet, does the lookup."""
    html = resolve_text_to_html("see [[project-os-dev#ADR-0011]]", lambda t: None)
    assert 'class="cross-repo-link"' in html
    assert 'data-project="project-os-dev"' in html
    assert 'data-note-id="ADR-0011"' in html
    assert 'href="#"' in html
    assert "broken-wikilink" not in html


def test_an_ordinary_broken_link_still_reads_broken() -> None:
    """The regression that would hide every genuine typo: a pattern loose
    enough to treat `[[ADR-9999]]` as cross-repo would make unresolvable links
    look like reachable ones."""
    html = resolve_text_to_html("[[ADR-9999]]", lambda t: None)
    assert "broken-wikilink" in html and "cross-repo-link" not in html


def test_both_wikilink_consumers_handle_it() -> None:
    """`wikilinks.py` names two consumers — the markdown body and the
    frontmatter strip — and says they share one regex and one resolver so they
    stay consistent. A cross-repo link that worked in the body and broke in
    `related:` would be that consistency quietly lost."""
    src = (REPO_ROOT / "src" / "project_os_cockpit" / "wikilinks.py").read_text()
    body = src.split("class _WikilinkInlineProcessor", 1)[1]
    strip = src.split("def _render_match", 1)[1].split("class ", 1)[0]
    assert "split_cross_repo" in body
    assert "split_cross_repo" in strip


def test_the_project_id_is_the_directory_name_by_default() -> None:
    """Neither thing that looks like an id can be one: `project.name` carries
    spaces and reads `REPLACE ME` in the template, and the shell's workspace
    id is a sha1 of an absolute path."""
    assert project_id(REPO_DOCS) == "project-os-cockpit"
    fleet = Path.home() / "Dev" / "repos"
    for name in ("project-os-dev", "your-health"):
        docs = fleet / name / "docs"
        if docs.exists():
            assert project_id(docs) == name


def test_an_explicit_project_id_wins(tmp_path: Path) -> None:
    """The override exists for the case the default cannot survive: a repo
    renamed or cloned into a different folder changes identity silently, and
    every reference to it breaks with no error anywhere."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "SNAPSHOT.yaml").write_text(
        'project:\n  name: "Renamed Thing"\n  id: "original-name"\n', encoding="utf-8",
    )
    assert project_id(tmp_path / "docs") == "original-name"
    (tmp_path / "SNAPSHOT.yaml").write_text(
        'project:\n  name: "Renamed Thing"\n', encoding="utf-8",
    )
    assert project_id(tmp_path / "docs") == tmp_path.name


# ---- the shell half ------------------------------------------------------


def test_the_shell_reports_a_project_it_does_not_have() -> None:
    """A dead click is the failure this feature exists to remove. A reference
    to a project not on this machine is a real answer — the note may exist and
    simply not be here — and must not look identical to one that resolves."""
    src = RENDERER.read_text(encoding="utf-8")
    fn = re.search(r"async function jumpToCrossRepoNote\(.*?\n\}", src, re.S)
    assert fn, "the follow handler is gone"
    body = fn.group(0)
    assert "No project" in body and "showStatus" in body
    assert "w.projectId === project" in body


def test_the_jump_survives_the_workspace_switch() -> None:
    """The two legs live in different processes: the shell switches, and only
    the ARRIVING sidecar can say where the id lives. Without the parked jump,
    the reader lands on the new workspace's overview instead of the note they
    clicked."""
    src = RENDERER.read_text(encoding="utf-8")
    assert "pendingCrossRepoJump" in src
    ready = src.split("case 'ready': {", 1)[1].split("case 'failed'", 1)[0]
    assert "pendingCrossRepoJump" in ready, (
        "the parked jump is never consumed; a cross-repo click switches "
        "workspace and then forgets what it was for"
    )
    # …and before the landing, or the landing wins the race.
    assert ready.index("pendingCrossRepoJump") < ready.index("renderInboxPanel")


def test_the_jump_suppresses_the_arriving_landing_rather_than_racing_it() -> None:
    """Both are async and the landing has a head start, so "be quick" is not a
    mechanism. Measured before the fix: the click switched to project-os-dev
    and the centre pane read *"Features (by phase) — Nothing owed on
    features"*, the arriving workspace's landing having overwritten the note.

    This is the third time this shape has been got wrong here — ISS-0040 is
    the README fetch beating a virtual landing, and then the guard naming one
    mode while Review and Design inherited the bug — which is why the
    suppression is asserted on every branch that can navigate rather than on
    the one that happened to lose.
    """
    src = RENDERER.read_text(encoding="utf-8")
    assert "suppressLandingOnce" in src and "consumeLandingSuppression" in src
    nav = src.split("async function loadWsNav(", 1)[1].split("\nasync function", 1)[0]
    # The suppression decides every landing. Since ISS-0295 a soft reload
    # skips the landing outright, and that check comes FIRST so it does not
    # consume a suppression armed for an arrival that has not happened yet.
    assert re.search(
        r"const skipLanding = opts\.land === false \|\| consumeLandingSuppression\(\);", nav
    ), "skipLanding must come from the suppression, with land:false checked before it"
    # Every landing navigation inside loadWsNav is guarded.
    #
    # **A click handler is not one.** The race this guards is between an
    # arriving workspace's landing and a note already being fetched, both at
    # PANE-LOAD time. A navigation the reader asked for by pressing a button
    # cannot lose that race — it happens long after both have settled — and
    # suppressing the landing on it would break the button instead.
    #
    # The distinction is needed because this slice runs to the next top-level
    # `async function` and so takes in the plain `function`s defined after
    # `loadWsNav`, including `renderNavGroup`. FEAT-0103's gate controls are
    # the first click handlers to land inside that window.
    for line in nav.splitlines():
        if "void navigateTo(" in line and "~" in line:
            before = nav[:nav.index(line)][-400:]
            if "addEventListener('click'" in before:
                continue
            assert "skipLanding" in line or "skipLanding" in before, line
    # …and the README fallback, for a jump arriving into a mode with no
    # landing at all.
    ready = src.split("case 'ready': {", 1)[1].split("case 'failed'", 1)[0]
    assert "!pendingCrossRepoJump) void navigateTo('README.md')" in ready


def test_a_skipped_overview_landing_still_loads_the_left_pane() -> None:
    """ISS-0296. In Overview mode the left pane is drawn by rendering the
    `~overview` page, and a link that switches project skips that page so its
    own target wins. Skipping the pane with it left "Pick a workspace" on
    screen, or the previous project's phases under the new project's name.
    So the Overview branch draws the pane on the path that skips the page."""
    src = RENDERER.read_text(encoding="utf-8")
    nav = js_function_body(src, "async function loadWsNav(")
    overview = nav.split("if (currentNavMode === 'overview') {", 1)[1].split("return;", 1)[0]
    assert re.search(
        r"if \(!skipLanding\) void navigateTo\(target[^;]*;\s*(//[^\n]*\n\s*)*else void loadOverviewScopePane\(\);",
        overview,
    ), "the Overview branch skips the landing without drawing the left pane"
    loader = js_function_body(src, "async function loadOverviewScopePane(")
    assert "/api/cockpit/stats" in loader and "renderOverviewScopePane()" in loader
    # A reply from the project the reader has since left is dropped.
    assert "base !== sidecarBaseUrl" in loader


def test_the_suppression_cannot_outlive_its_jump() -> None:
    """A flag that stayed armed would swallow the next legitimate landing —
    you would click Issues and stay where you were, once, unreproducibly."""
    src = RENDERER.read_text(encoding="utf-8")
    fn = re.search(r"function consumeLandingSuppression\(\).*?\n\}", src, re.S)
    assert fn and "suppressLandingOnce = false;" in fn.group(0)


# ---- every route that resolves a link by ID (FEAT-0146, then FEAT-0148) ----
#
# These moved here from `tests/test_design_links.py` when the design-bench link
# rule was deleted (TASK-0614). The rule lasted one day; the guards under it
# did not belong to it. Three of them came out of FEAT-0146's independent
# review, which found four one-line edits to the link routes passing every
# test, and the fourth is ISS-0298's — a parked link opening in whichever
# project arrived first, which predates the rule and outlives it.

def _code_only(body: str) -> str:
    """The body without its comments, so a comment that names a function is
    not mistaken for a call to it."""
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    return re.sub(r"//[^\n]*", "", body)


def _calls(src: str, name: str) -> list[int]:
    """Where `name(` is called in `src`: not declared, not only mentioned."""
    code = _code_only(src)
    return [m.start() for m in re.finditer(rf"(?<!function )\b{name}\(", code)]


def test_every_route_that_resolves_a_link_by_id_goes_through_locate_and_open() -> None:
    """Every link resolved by ID has to arrive at one function, and nothing
    used to check that it did. FEAT-0146's independent review found four
    one-line edits — deleting either same-project call, deleting the parked
    jump's call, or opening `target.id` as a path — that broke links in the
    window while passing every automated test.

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
    # …and it is asked about the note, not about the project. Both arguments
    # are strings, so swapping them builds and every other test passes. The
    # design-bench rule this clause was written for is gone (TASK-0614); the
    # argument order it protected is still the thing a refactor gets wrong.
    locate = _code_only(js_function_body(src, "async function locateAndOpen("))
    assert "encodeURIComponent(noteId)" in locate, (
        "locateAndOpen looks up something other than the note's ID"
    )


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
