"""Note index — the in-memory data layer the renderer and cockpit query.

For TASK-0003 (wikilink resolver) we need:
- target → URL lookup, with the resolution priority spelled out in REQ-0002.

This module is also the home of the broader index that TASK-0007 (cockpit
infra) will extend with frontmatter records and a backlink graph. The
``NoteRecord`` dataclass is already shaped for that — TASK-0007 just adds
graph methods alongside the existing lookup tables.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import frontmatter

log = logging.getLogger("docs_server.index")

# Directories whose contents are excluded from index walks.
# ``__templates__`` is intentionally NOT excluded — it holds the type-stub
# notes (``feature.md``, ``task.md``, etc.) that wikilinks like
# ``[[feature]]`` resolve to, matching Obsidian's behaviour.
# ``__bases__`` contains ``.base`` YAML files, not ``.md``, so it has nothing
# to index — listing it here is belt-and-braces.
EXCLUDED_DIR_NAMES: frozenset[str] = frozenset(
    {"__bases__", ".obsidian", ".trash", ".git"}
)


@dataclass
class NoteRecord:
    """In-memory representation of a single ``.md`` note."""

    path: Path
    rel_path: str  # POSIX-style, relative to docs_root
    frontmatter: dict[str, Any] = field(default_factory=dict)
    title: str | None = None
    note_id: str | None = None
    aliases: tuple[str, ...] = ()


class Index:
    """Walks the docs tree, exposes wikilink resolution + URL building.

    Resolution priority (per REQ-0002):
      1. Frontmatter ``id`` (covers project-os ID patterns implicitly).
      2. Frontmatter ``aliases``.
      3. Filename without extension.
      4. Frontmatter ``title`` or first ``# H1`` line.

    Shape of internal lookup tables is intentionally separate so collisions
    (an alias that happens to equal another note's filename) resolve in the
    right order. Inserts are first-write-wins per table.
    """

    def __init__(self, docs_root: Path) -> None:
        self.docs_root = docs_root.resolve()
        self._records: dict[Path, NoteRecord] = {}
        self._by_id: dict[str, Path] = {}
        self._by_alias: dict[str, Path] = {}
        self._by_filename: dict[str, Path] = {}
        self._by_title: dict[str, Path] = {}

    # ---- construction ----

    @classmethod
    def build(cls, docs_root: Path) -> "Index":
        idx = cls(docs_root)
        for md_path in idx._walk_markdown():
            idx._index_path(md_path)
        log.info(
            "index: %d notes (ids:%d aliases:%d filenames:%d titles:%d)",
            len(idx._records),
            len(idx._by_id),
            len(idx._by_alias),
            len(idx._by_filename),
            len(idx._by_title),
        )
        return idx

    def _walk_markdown(self) -> Iterable[Path]:
        for md in self.docs_root.rglob("*.md"):
            if self._is_excluded(md):
                continue
            yield md

    def _is_excluded(self, md: Path) -> bool:
        try:
            rel = md.relative_to(self.docs_root)
        except ValueError:
            return True
        return any(
            part in EXCLUDED_DIR_NAMES or part.startswith(".")
            for part in rel.parts[:-1]  # exclude on parent dirs only; allow leaf .md
        )

    def _index_path(self, md_path: Path) -> None:
        try:
            text = md_path.read_text(encoding="utf-8")
        except OSError as exc:
            log.warning("index: cannot read %s: %s", md_path, exc)
            return
        try:
            post = frontmatter.loads(text)
        except Exception as exc:  # pragma: no cover — malformed frontmatter
            log.warning("index: frontmatter parse failed for %s: %s", md_path, exc)
            post = frontmatter.Post(text)

        fm: dict[str, Any] = dict(post.metadata or {})
        note_id = fm.get("id") if isinstance(fm.get("id"), str) and fm.get("id").strip() else None
        aliases_raw = fm.get("aliases") or []
        aliases: tuple[str, ...] = tuple(
            a.strip() for a in aliases_raw if isinstance(a, str) and a.strip()
        )
        title = fm.get("title") if isinstance(fm.get("title"), str) and fm.get("title").strip() else None
        if title is None:
            title = _extract_h1(post.content)

        rel_path = md_path.relative_to(self.docs_root).as_posix()
        record = NoteRecord(
            path=md_path,
            rel_path=rel_path,
            frontmatter=fm,
            title=title,
            note_id=note_id,
            aliases=aliases,
        )
        self._records[md_path] = record

        if note_id:
            self._by_id.setdefault(note_id, md_path)
        for alias in aliases:
            self._by_alias.setdefault(alias, md_path)
        self._by_filename.setdefault(md_path.stem, md_path)
        if title:
            self._by_title.setdefault(title, md_path)

    # ---- lookups ----

    def resolve(self, target: str) -> str | None:
        """Return the docs URL for ``target`` or ``None`` if unresolvable."""
        target = target.strip()
        if not target:
            return None
        for table in (self._by_id, self._by_alias, self._by_filename, self._by_title):
            path = table.get(target)
            if path is not None:
                return self.url_for(path)
        return None

    def get(self, path: Path) -> NoteRecord | None:
        return self._records.get(path.resolve())

    def url_for(self, path: Path) -> str:
        rel = path.resolve().relative_to(self.docs_root).as_posix()
        return f"/docs/{rel}"

    def __len__(self) -> int:
        return len(self._records)

    # ---- mutation (for the watcher in TASK-0005) ----

    def update_path(self, md_path: Path) -> None:
        """Re-index a single ``.md`` path; remove if it no longer exists."""
        md_path = md_path.resolve()
        if md_path in self._records:
            self._remove_path(md_path)
        if md_path.exists() and md_path.suffix.lower() == ".md" and not self._is_excluded(md_path):
            self._index_path(md_path)

    def _remove_path(self, md_path: Path) -> None:
        record = self._records.pop(md_path, None)
        if record is None:
            return
        if record.note_id and self._by_id.get(record.note_id) == md_path:
            self._by_id.pop(record.note_id, None)
        for alias in record.aliases:
            if self._by_alias.get(alias) == md_path:
                self._by_alias.pop(alias, None)
        if self._by_filename.get(md_path.stem) == md_path:
            self._by_filename.pop(md_path.stem, None)
        if record.title and self._by_title.get(record.title) == md_path:
            self._by_title.pop(record.title, None)


def _extract_h1(body: str) -> str | None:
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip() or None
    return None
