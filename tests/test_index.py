"""Unit tests for :mod:`docs_server.index`.

Validates TASK-0007's DoD:
- ``Index.build`` walks the docs root and populates lookup tables.
- ``paths`` / ``get`` / ``by_id`` / ``links_from`` / ``links_to`` work.
- Outbound links are extracted from BOTH body and frontmatter.
- Unresolvable wikilinks don't raise.
- ``invalidate`` re-parses on edit, removes on delete, re-discovers on add.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from docs_server.index import Index, NoteRecord


FIXTURE = Path(__file__).parent / "fixtures" / "index_basic"


@pytest.fixture()
def docs_root(tmp_path: Path) -> Path:
    """Copy the static fixture into a temp dir so tests can mutate it."""
    target = tmp_path / "docs"
    shutil.copytree(FIXTURE, target)
    return target


@pytest.fixture()
def index(docs_root: Path) -> Index:
    return Index.build(docs_root)


# ---- structural ---------------------------------------------------------


def test_build_indexes_real_notes_only(index: Index) -> None:
    """Real notes in the index; templates excluded from type counts."""
    rel_paths = {index.get(p).rel_path for p in index.paths()}
    assert "FEAT-0001-Alpha.md" in rel_paths
    assert "FEAT-0002-Beta.md" in rel_paths
    assert "REQ-0001-Some-Req.md" in rel_paths
    # Templates ARE indexed (so [[feature]] resolves), but they don't show
    # up in browseable type counts.
    assert "__templates__/feature.md" in rel_paths
    counts = index.type_counts()
    assert counts["feature"] == 2  # FEAT-0001 + FEAT-0002, NOT the template
    assert counts["requirement"] == 1


def test_get_returns_note_record(index: Index, docs_root: Path) -> None:
    record = index.get(docs_root / "FEAT-0001-Alpha.md")
    assert isinstance(record, NoteRecord)
    assert record.note_id == "FEAT-0001"
    assert "FEAT-0001" in record.aliases
    assert record.note_type == "feature"
    assert record.status == "active"
    assert record.title == "Alpha feature"
    # body field stored
    assert "References" in record.body


def test_by_id_resolves_via_priority_order(index: Index, docs_root: Path) -> None:
    """``id`` table has higher priority than filename / title."""
    p = index.by_id("FEAT-0001")
    assert p is not None
    assert p.name == "FEAT-0001-Alpha.md"
    # Filename without extension also works (filename table).
    assert index.by_id("FEAT-0001-Alpha") == p
    # Title also works (title table — lowest priority).
    assert index.by_id("Alpha feature") == p
    # Unknown returns None, doesn't raise.
    assert index.by_id("nope") is None
    assert index.by_id("") is None


def test_resolve_returns_url(index: Index) -> None:
    assert index.resolve("FEAT-0001") == "/docs/FEAT-0001-Alpha.md"
    assert index.resolve("Ghost") is None


# ---- link graph ---------------------------------------------------------


def test_links_from_includes_body_and_frontmatter(
    index: Index, docs_root: Path
) -> None:
    """Outbound links pulled from both body wikilinks and frontmatter values."""
    feat1 = docs_root / "FEAT-0001-Alpha.md"
    out = index.links_from(feat1)
    rel = {index.get(p).rel_path for p in out}
    # Body link to FEAT-0002 (with display alias)
    assert "FEAT-0002-Beta.md" in rel
    # Frontmatter `related: ["[[FEAT-0002]]"]` — same target, dedup OK
    # Body link to REQ-0001 with display alias
    assert "REQ-0001-Some-Req.md" in rel
    # `type: "[[feature]]"` resolves to the template
    assert "__templates__/feature.md" in rel


def test_links_to_is_reverse_of_links_from(index: Index, docs_root: Path) -> None:
    feat1 = docs_root / "FEAT-0001-Alpha.md"
    feat2 = docs_root / "FEAT-0002-Beta.md"
    # FEAT-0001 -> FEAT-0002 means FEAT-0002 has FEAT-0001 in its inbound.
    assert feat1 in index.links_to(feat2)
    # FEAT-0002 -> FEAT-0001 also (via implements + body).
    assert feat2 in index.links_to(feat1)
    # REQ-0001 specifies FEAT-0001
    req1 = docs_root / "REQ-0001-Some-Req.md"
    assert req1 in index.links_to(feat1)


def test_unresolved_wikilink_does_not_raise(index: Index, docs_root: Path) -> None:
    """``[[Ghost]]`` in FEAT-0002 should be silently skipped, not raise."""
    feat2 = docs_root / "FEAT-0002-Beta.md"
    out = index.links_from(feat2)
    rel_targets = {index.get(p).rel_path for p in out}
    # Resolves links present, omits the ghost.
    assert "FEAT-0001-Alpha.md" in rel_targets
    assert all("Ghost" not in r for r in rel_targets)


def test_self_links_excluded(index: Index, docs_root: Path) -> None:
    """A note linking to itself should not appear in its own outbound set."""
    feat1 = docs_root / "FEAT-0001-Alpha.md"
    assert feat1 not in index.links_from(feat1)


# ---- mutation -----------------------------------------------------------


def test_invalidate_after_edit_updates_links(
    index: Index, docs_root: Path
) -> None:
    """Editing a note's body should re-discover its outbound links."""
    feat1 = docs_root / "FEAT-0001-Alpha.md"
    req1 = docs_root / "REQ-0001-Some-Req.md"

    # Initially FEAT-0001 has REQ-0001 in its outbound (body link).
    assert req1 in index.links_from(feat1)
    assert feat1 in index.links_to(req1)

    # Edit FEAT-0001 to remove the REQ-0001 link.
    text = feat1.read_text(encoding="utf-8")
    new_text = text.replace("[[REQ-0001|the requirement]]", "the requirement")
    feat1.write_text(new_text, encoding="utf-8")
    index.invalidate(feat1)

    assert req1 not in index.links_from(feat1)
    assert feat1 not in index.links_to(req1)


def test_invalidate_after_delete_removes_record(
    index: Index, docs_root: Path
) -> None:
    """Deletion drops the record + the deleted file's outbound mirrors,
    but preserves inbound from sources that still claim to link there.

    Rationale: a source file's wikilinks still point at the deleted target
    in its body / frontmatter. Until that source itself is re-indexed,
    ``links_to(deleted)`` is the most accurate "who currently claims to
    link here" answer we have.
    """
    feat2 = docs_root / "FEAT-0002-Beta.md"
    feat1 = docs_root / "FEAT-0001-Alpha.md"
    # Before: feat1 -> feat2 AND feat2 -> feat1.
    assert feat2 in index.links_from(feat1)
    assert feat1 in index.links_from(feat2)
    assert feat2 in index.links_to(feat1)
    assert feat1 in index.links_to(feat2)

    feat2.unlink()
    index.invalidate(feat2)

    # Lookup tables: gone.
    assert index.get(feat2) is None
    assert index.by_id("FEAT-0002") is None
    assert index.resolve("FEAT-0002") is None

    # feat1's outbound still claims feat2 (we don't re-read other notes).
    assert feat2 in index.links_from(feat1)
    # Inbound to feat2 is preserved — feat1 still claims to link there.
    assert feat1 in index.links_to(feat2)
    # But feat2's old outbound was popped, so feat2 no longer in inbound[feat1].
    assert feat2 not in index.links_to(feat1)


def test_invalidate_after_recreate_re_indexes(
    index: Index, docs_root: Path
) -> None:
    new_path = docs_root / "FEAT-0003-Gamma.md"
    new_path.write_text(
        "---\n"
        'type: "[[feature]]"\n'
        'id: FEAT-0003\n'
        'aliases: ["FEAT-0003"]\n'
        "title: Gamma\n"
        "status: backlog\n"
        "---\n"
        "# Gamma\n\nLinks to [[FEAT-0001]].\n",
        encoding="utf-8",
    )
    index.invalidate(new_path)

    assert index.by_id("FEAT-0003") == new_path
    feat1 = docs_root / "FEAT-0001-Alpha.md"
    assert new_path in index.links_to(feat1)


# ---- excluded directories ----------------------------------------------


def test_paths_includes_template_notes_for_resolution(
    index: Index, docs_root: Path
) -> None:
    """``[[feature]]`` should still resolve to the template stub."""
    template = docs_root / "__templates__" / "feature.md"
    assert template in index.paths()
    assert index.by_id("FEAT-0000") == template
    # And the type wikilink resolves through the filename table.
    assert index.resolve("feature") == "/docs/__templates__/feature.md"
