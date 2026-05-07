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

from .events import is_under_ci, relative_to_ci

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
    note_type: str | None = None  # normalised ("feature", "adr", ...) — never wikilink form
    status: str | None = None


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
        rel = relative_to_ci(md, self.docs_root)
        if rel is None:
            return True
        # Exclude on parent dirs only; allow leaf .md.
        parts = rel.split("/")[:-1]
        return any(p in EXCLUDED_DIR_NAMES or p.startswith(".") for p in parts)

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

        rel_path = relative_to_ci(md_path, self.docs_root)
        if rel_path is None:
            return  # safety net — _is_excluded already guards this
        record = NoteRecord(
            path=md_path,
            rel_path=rel_path,
            frontmatter=fm,
            title=title,
            note_id=note_id,
            aliases=aliases,
            note_type=_normalise_type(fm.get("type")),
            status=_normalise_status(fm.get("status")),
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
        rel = relative_to_ci(path.resolve(), self.docs_root)
        if rel is None:
            raise ValueError(f"path not under docs root: {path}")
        return f"/docs/{rel}"

    def __len__(self) -> int:
        return len(self._records)

    # ---- type / status views ----

    def notes_by_type(
        self, note_type: str, *, include_templates: bool = False
    ) -> list[NoteRecord]:
        """All notes whose normalised ``type`` matches (case-insensitive).

        Templates under ``__templates__/`` are excluded by default — they
        carry placeholder IDs (``FEAT-0000`` etc.) that shouldn't appear
        in browseable indexes alongside real notes.
        """
        wanted = note_type.lower()
        return [
            r for r in self._records.values()
            if r.note_type and r.note_type.lower() == wanted
            and (include_templates or not _is_template(r))
        ]

    def type_counts(self, *, include_templates: bool = False) -> dict[str, int]:
        """``{normalised type: count}`` across the index."""
        counts: dict[str, int] = {}
        for record in self._records.values():
            if not record.note_type:
                continue
            if not include_templates and _is_template(record):
                continue
            counts[record.note_type] = counts.get(record.note_type, 0) + 1
        return counts

    # ---- mutation (for the watcher in TASK-0005) ----

    def update_path(self, md_path: Path) -> None:
        """Re-index a single ``.md`` path; remove if it no longer exists."""
        md_path = md_path.resolve()
        # Records are keyed by Path, so case-mismatch on macOS would let a
        # stale entry linger. Find any existing record under the same path
        # case-insensitively and remove it before re-indexing.
        existing = next(
            (p for p in self._records if str(p).lower() == str(md_path).lower()),
            None,
        )
        if existing is not None:
            self._remove_path(existing)
        if (
            md_path.exists()
            and md_path.suffix.lower() == ".md"
            and not self._is_excluded(md_path)
        ):
            self._index_path(md_path)

    def subscribe_to(self, bus) -> None:
        """Register an invalidation callback on ``bus``.

        Called by the server at startup so the index stays in sync with
        the watcher (TASK-0005). ``.md`` events trigger a re-index of
        the affected path; non-``.md`` events are ignored.
        """
        from .events import FileEvent  # local import to avoid cycle at module load

        def _on_event(event: "FileEvent") -> None:
            if event.abs_path.suffix.lower() != ".md":
                return
            try:
                self.update_path(event.abs_path)
            except Exception:
                log.exception("index: update_path failed for %s", event.abs_path)

        bus.subscribe(_on_event)

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


def _normalise_type(raw: Any) -> str | None:
    """Normalise a frontmatter ``type:`` value to a lowercase string.

    Accepts the wikilink form (``"[[feature]]"``) and bare strings
    (``"feature"`` / ``"reference"``); strips brackets, lowercases.
    """
    if not isinstance(raw, str):
        return None
    s = raw.strip()
    if not s:
        return None
    if s.startswith("[[") and s.endswith("]]"):
        s = s[2:-2].strip()
    return s.lower() or None


def _normalise_status(raw: Any) -> str | None:
    if not isinstance(raw, str):
        return None
    s = raw.strip().lower()
    return s or None


def _is_template(record: NoteRecord) -> bool:
    return record.rel_path.startswith("__templates__/")
