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
