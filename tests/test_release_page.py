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
    row = groups["rung-next"]["items"][0]
    assert row["url"] == "~release/next"
    assert row["action"] == "~release/next"


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
    assert src.count("await askForText(") >= 5, src.count("await askForText(")
