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
import re as _re


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


def test_a_stale_document_is_found_by_age_not_by_name(tmp_path) -> None:
    """Staleness is **constructed**, not borrowed.

    This read the live corpus and relied on DESIGN and STYLEGUIDE having sat
    untouched since 2026-01-26. On 2026-08-12 both were rewritten and the
    corpus had no stale document at all — so a test about an age rule failed
    because the documents got looked after, which is the outcome the rule
    exists to produce.
    """
    import shutil
    docs = tmp_path / "docs"
    shutil.copytree(REPO / "docs", docs)
    (tmp_path / "SNAPSHOT.yaml").write_text("project:\n  name: probe\n", encoding="utf-8")
    old_day = _dt.date.today() - _dt.timedelta(days=standing.STALE_AFTER_DAYS + 40)
    target = docs / "GLOSSARY.md"
    text = target.read_text(encoding="utf-8")
    target.write_text(
        _re.sub(r"^updated: .*$", f"updated: {old_day.isoformat()}", text, count=1,
                flags=_re.M),
        encoding="utf-8",
    )
    stale = {f.document for f in standing.check(docs, tmp_path) if f.kind == "stale"}
    assert "GLOSSARY" in stale, stale
    for name in stale:
        m = standing._UPDATED_RE.search((docs / f"{name}.md").read_text(encoding="utf-8"))
        if m:
            age = (_dt.date.today() - _dt.date.fromisoformat(m.group(1))).days
            assert age > standing.STALE_AFTER_DAYS


def test_every_standing_document_still_parses_as_a_note() -> None:
    """Regression, 2026-08-10 (TASK-0381 → caught by TASK-0374).

    Stripping `status:` glued the closing `---` onto the last frontmatter
    line (`tags: [design]---`), so **all seven documents silently stopped
    parsing**: `type=None`, `id=None`, invisible to every payload that reads
    by type.

    Nothing caught it. The validator passed, the suite passed, and the
    standing checks passed because they read the file with a regex rather
    than as a note. It surfaced only because the Intent view rendered
    `Reference · 3` where more was expected.

    So the assertion is that these are *notes*, not that the text looks
    right — the property, not the shape.
    """
    from project_os_cockpit.index import Index

    import frontmatter as _fm

    docs = REPO / "docs"
    index = Index.build(docs)
    for res in standing.resolve(docs, REPO):
        if res.path is None:
            continue
        try:
            res.path.relative_to(docs)
        except ValueError:
            # A repo-root member (LLM_BRIEF, SECURITY). The docs index walks
            # `docs/` only, so it can never appear there — but the property
            # this test is about is that the file **parses as a note**, and
            # that holds wherever it lives. Read it directly rather than
            # excusing it.
            post = _fm.loads(res.path.read_text(encoding="utf-8"))
            assert post.metadata.get("type"), (
                f"{res.document.name} has no type — its frontmatter does not parse"
            )
            assert post.metadata.get("id"), f"{res.document.name} has no id"
            continue
        record = index.get(res.path)
        assert record is not None, f"{res.document.name} is not in the index"
        assert record.note_type, (
            f"{res.document.name} has no type — its frontmatter does not parse"
        )


def test_a_root_level_document_is_not_labelled_under_docs() -> None:
    """`~root/LLM_BRIEF.md` is a file at the repo root. The doc header composed
    `docs/${rel}` unconditionally and printed `docs/~root/LLM_BRIEF.md` — a
    path that does not exist, while the content beneath it rendered perfectly.

    A standing document may live beside the docs tree rather than inside it
    (FEAT-0091's extension point), so the label has to know the difference.
    """
    import re as _r
    renderer = REPO / "desktop" / "src" / "renderer" / "renderer.ts"
    fn = _r.search(r"function buildDocHeader\(.*?\n\}", renderer.read_text(), _r.S)
    assert fn, "buildDocHeader is gone"
    body = fn.group(0)
    assert "rel.startsWith('~root/')" in body, (
        "a repo-root document is still labelled as living under docs/"
    )


# ---- ISS-0166: the manifest is read once, and the tree walked once ---------


def test_the_snapshot_is_parsed_once_per_view_not_once_per_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A view selection must not re-read an unchanged 204 KB file seven times.

    Measured when this was filed: Intent cost **1.25s** against Issues' 0.03s,
    and the only difference between them is that Issues never resolves the
    standing manifest. `manifest()` parsed `SNAPSHOT.yaml` on every call, for
    one field holding two entries, and [[ADR-0025]] had just put *what needs a
    person* on every view — so a per-call cost became a per-view one.

    Asserted as a count rather than a duration: a timing test on a shared
    machine is a flake, and what actually regressed is the number of parses.
    """
    import yaml

    from project_os_cockpit import cockpit
    from project_os_cockpit.index import Index

    calls = {"n": 0}
    real = yaml.safe_load

    def counted(stream, *a, **k):  # type: ignore[no-untyped-def]
        calls["n"] += 1
        return real(stream, *a, **k)

    monkeypatch.setattr(yaml, "safe_load", counted)
    standing.clear_manifest_cache()

    index = Index.build(REPO / "docs")
    cockpit.nav_payload(index, mode="intent")   # warm: one parse is allowed
    calls["n"] = 0
    cockpit.nav_payload(index, mode="intent")

    assert calls["n"] == 0, (
        "the standing manifest is parsing SNAPSHOT.yaml again on an unchanged "
        f"file ({calls['n']} times for one Intent payload) — ISS-0166"
    )


def test_a_changed_snapshot_is_re_read(tmp_path: Path) -> None:
    """The cache is keyed on the snapshot's CONTENT, so an edit is seen.

    Same length and (potentially) the same filesystem timestamp tick as the
    version before it — which is exactly the case a `(mtime_ns, size)` stamp
    would have served stale, and the reason this is a digest.
    """
    snapshot = tmp_path / "SNAPSHOT.yaml"
    snapshot.write_text(
        "docs_system:\n  standing:\n    - AAAAAAAA\n", encoding="utf-8")
    assert "AAAAAAAA" in {d.name for d in standing.manifest(tmp_path)}

    snapshot.write_text(
        "docs_system:\n  standing:\n    - BBBBBBBB\n", encoding="utf-8")
    names = {d.name for d in standing.manifest(tmp_path)}

    assert "BBBBBBBB" in names, "an edited snapshot must be re-read"
    assert "AAAAAAAA" not in names, "the previous manifest is still being served"


def test_resolving_the_manifest_walks_the_tree_once(tmp_path: Path) -> None:
    """Ten entries were ten recursive walks — `glob("**/<file>")` per entry.

    Over ~900 notes, seven times per Intent selection. The rivals are one
    question asked of one tree, so they are answered by reading it once.
    """
    docs = tmp_path / "docs"
    (docs / "deep" / "deeper").mkdir(parents=True)
    (tmp_path / "SNAPSHOT.yaml").write_text("docs_system: {}\n", encoding="utf-8")
    for name in ("ARCHITECTURE.md", "GLOSSARY.md"):
        (docs / name).write_text("# x\n", encoding="utf-8")
    # A rival copy, which is the thing the walk exists to find.
    (docs / "deep" / "deeper" / "GLOSSARY.md").write_text("# rival\n", encoding="utf-8")

    # `Path.rglob(p)` delegates to `Path.glob("**/" + p)`, so counting the
    # recursive GLOB catches both spellings and counts one walk once.
    recursive = {"n": 0}
    real_glob = Path.glob

    def counted(self, pattern, *a, **k):  # type: ignore[no-untyped-def]
        if "**" in str(pattern):
            recursive["n"] += 1
        return real_glob(self, pattern, *a, **k)

    Path.glob = counted  # type: ignore[method-assign]
    try:
        resolutions = standing.resolve(docs, tmp_path)
    finally:
        Path.glob = real_glob  # type: ignore[method-assign]

    assert recursive["n"] <= 1, (
        "resolve() walks the docs tree once per manifest entry again "
        f"({recursive['n']} recursive walks for one resolve) — ISS-0166"
    )
    # And the rival is still found, which is what the walk is for.
    glossary = next(r for r in resolutions if r.document.name == "GLOSSARY")
    assert glossary.state == "ambiguous", glossary.paths
