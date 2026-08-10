"""TASK-0380 — the standing set as extensible data.

REQ-0033: declared once, singular by construction, extensible without code.
The tests are about the *properties*, because the membership will change and
the properties must not.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from project_os_cockpit import standing

REPO = Path(__file__).resolve().parents[1]


def test_the_base_set_is_the_class_ISS_0125_measured() -> None:
    names = {d.name for d in standing.BASE_STANDING}
    assert names == {
        "README", "INDEX", "ARCHITECTURE", "GLOSSARY",
        "OWNERSHIP", "DESIGN", "STYLEGUIDE", "PHASES",
    }
    for doc in standing.BASE_STANDING:
        assert doc.question, f"{doc.name} is in the set without saying what it answers"


def test_every_entry_resolves_to_exactly_one_file_here() -> None:
    """REQ-0033's singularity criterion, against the real corpus."""
    for res in standing.resolve(REPO / "docs", REPO):
        assert res.state == "present", f"{res.document.name} is {res.state}: {res.paths}"


def test_a_rival_copy_is_ambiguous_not_last_writer_wins(tmp_path: Path) -> None:
    """Two files claiming one entry means the set has become a type.

    A resolver returning the first match would hide that forever, which is why
    `Resolution.paths` carries every match rather than one.
    """
    docs = tmp_path / "docs"
    (docs / "sub").mkdir(parents=True)
    (docs / "GLOSSARY.md").write_text("# a\n", encoding="utf-8")
    (docs / "sub" / "GLOSSARY.md").write_text("# b\n", encoding="utf-8")
    byname = {r.document.name: r for r in standing.resolve(docs, tmp_path)}
    assert byname["GLOSSARY"].state == "ambiguous"
    assert len(byname["GLOSSARY"].paths) == 2
    assert byname["GLOSSARY"].path is None, "an ambiguous entry must not pick one"


def test_container_readmes_do_not_make_README_ambiguous(tmp_path: Path) -> None:
    """Eight container directories carry a README and none is the project's.

    The first cut searched recursively and reported README ambiguous — a
    sentence about the search, not about the corpus.
    """
    docs = tmp_path / "docs"
    (docs / "issues").mkdir(parents=True)
    (docs / "README.md").write_text("# project\n", encoding="utf-8")
    (docs / "issues" / "README.md").write_text("# signpost\n", encoding="utf-8")
    byname = {r.document.name: r for r in standing.resolve(docs, tmp_path)}
    assert byname["README"].state == "present"


def test_a_missing_required_entry_is_reported(tmp_path: Path) -> None:
    """The case the presence check exists for — `yourtrainer-mcp` is missing
    five of the eight."""
    docs = tmp_path / "docs"
    docs.mkdir(parents=True)
    (docs / "README.md").write_text("# only this\n", encoding="utf-8")
    states = {r.document.name: r.state for r in standing.resolve(docs, tmp_path)}
    assert states["README"] == "present"
    assert states["GLOSSARY"] == "missing"


def test_a_project_extends_the_set_without_touching_the_base(tmp_path: Path) -> None:
    """REQ-0033: adding a document is a data edit, and a project addition must
    not live anywhere `sync-project-os.sh` overwrites."""
    (tmp_path / "SNAPSHOT.yaml").write_text(
        "docs_system:\n"
        "  standing:\n"
        "    - name: SECURITY\n"
        "      question: what must never leak?\n"
        "    - CONTRIBUTING\n",
        encoding="utf-8",
    )
    names = [d.name for d in standing.manifest(tmp_path)]
    assert "SECURITY" in names and "CONTRIBUTING" in names
    # …and the base is unchanged for every other project.
    assert "SECURITY" not in {d.name for d in standing.BASE_STANDING}


def test_a_broken_snapshot_does_not_take_the_manifest_with_it(tmp_path: Path) -> None:
    """The base set is the part that matters and needs no snapshot."""
    (tmp_path / "SNAPSHOT.yaml").write_text("docs_system: [ this is not\n", encoding="utf-8")
    names = {d.name for d in standing.manifest(tmp_path)}
    assert "GLOSSARY" in names


def test_adding_a_document_needs_no_code_change() -> None:
    """The manifest is data. If a consumer named a document, adding one would
    mean editing that consumer too — which is the drift this shape avoids."""
    src = (REPO / "src" / "project_os_cockpit" / "standing.py").read_text(encoding="utf-8")
    after_base = src.split("BASE_STANDING", 1)[1].split(")\n", 1)[1]
    for name in ("GLOSSARY", "STYLEGUIDE", "OWNERSHIP"):
        assert f'"{name}"' not in after_base, (
            f"{name} is named below the manifest — a consumer knows a member "
            "by name, so adding one would need a code change"
        )


# ---- freshness, and the absence of a lifecycle (TASK-0381) -------------

import datetime as _dt


def test_no_standing_document_carries_a_lifecycle_status() -> None:
    """ISS-0125's finding, closed (TASK-0381).

    `active` is in the **work-in-flight band**, so these documents were
    coloured, sorted and counted as work somebody was doing — 18 references
    and the glossary made up 19 of the 44 rows Active mode called `Doing`.
    They have no lifecycle; `updated:` is their only state.
    """
    offenders = [
        f.document for f in standing.check(REPO / "docs", REPO)
        if f.kind == "has_status"
    ]
    assert not offenders, f"standing documents still carrying a status: {offenders}"


def test_staleness_warns_and_never_errors() -> None:
    """Upstream ADR-0011's pattern. A build that fails because a glossary is
    old gets the check disabled within a week."""
    for finding in standing.check(REPO / "docs", REPO):
        if finding.kind in ("stale", "stub"):
            assert finding.severity == "warning", (
                f"{finding.document} {finding.kind} is an error; it must warn"
            )


def test_the_four_kinds_are_reported_distinctly(tmp_path: Path) -> None:
    """Collapsing them into "problem" loses the only useful part — what to do
    about each differs completely."""
    docs = tmp_path / "docs"
    (docs / "sub").mkdir(parents=True)
    (docs / "README.md").write_text("# ok\n", encoding="utf-8")
    (docs / "GLOSSARY.md").write_text("# a\n", encoding="utf-8")
    (docs / "sub" / "GLOSSARY.md").write_text("# b\n", encoding="utf-8")
    (docs / "DESIGN.md").write_text(
        '---\nupdated: 2020-01-01\n---\n# d\n<a placeholder>\n<another one>\n<a third>\n',
        encoding="utf-8",
    )
    kinds = {f.document: f.kind for f in standing.check(docs, tmp_path)}
    assert kinds["GLOSSARY"] == "ambiguous"
    assert kinds["INDEX"] == "missing"
    assert kinds["DESIGN"] in ("stub", "stale")
    seen = {f.kind for f in standing.check(docs, tmp_path)}
    assert {"ambiguous", "missing"} <= seen


def test_the_staleness_horizon_carries_its_reason() -> None:
    """A round number with no reason is a number somebody will change on a
    whim. 180 was chosen against what abandonment actually looked like."""
    src = (REPO / "src" / "project_os_cockpit" / "standing.py").read_text(encoding="utf-8")
    block = src.split("STALE_AFTER_DAYS")[0][-1400:]
    assert "ISS-0125" in block, "the horizon does not cite what it was measured against"
    assert "parameter" in block.lower(), "the horizon does not say it is adjustable"


def test_a_stale_document_is_found_by_age_not_by_name() -> None:
    docs = REPO / "docs"
    stale = {f.document for f in standing.check(docs, REPO) if f.kind == "stale"}
    # Measured 2026-08-10: DESIGN and STYLEGUIDE untouched since 2026-01-26.
    assert stale, "nothing reports stale in a corpus ISS-0125 measured at 94%"
    for name in stale:
        text = (docs / f"{name}.md").read_text(encoding="utf-8")
        m = standing._UPDATED_RE.search(text)
        if m:
            age = (_dt.date.today() - _dt.date.fromisoformat(m.group(1))).days
            assert age > standing.STALE_AFTER_DAYS
