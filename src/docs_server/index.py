"""Note index — the in-memory data layer the renderer and cockpit query.

Provides three things:

1. **Lookup tables** for wikilink resolution (``id`` / aliases / filename
   / title), per the REQ-0002 priority order. Used by the markdown
   ``WikilinkExtension`` and the metadata-strip resolver.
2. **Type / status views** for the auto-index pages (``/index/<plural>``).
3. **Backlink graph** — outbound and inbound link sets keyed by note path,
   built by scanning each note's frontmatter values *and* body for
   ``[[Target]]`` patterns and resolving them through the same priority
   tables. Consumed by FEAT-0004's backlinks panel and FEAT-0006's
   CONTEXT pane (``file.hasLink(this.file)``).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator

import frontmatter

from .events import is_under_ci, relative_to_ci
from .wikilinks import WIKILINK_RE

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
    body: str = ""
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
        # Backlink graph — populated lazily after the lookup tables exist
        # because outbound resolution depends on every note being known
        # already. See ``_rebuild_links`` for the second pass.
        self._outbound: dict[Path, frozenset[Path]] = {}
        self._inbound: dict[Path, set[Path]] = {}

    # ---- construction ----

    @classmethod
    def build(cls, docs_root: Path) -> "Index":
        idx = cls(docs_root)
        # First pass: populate records + lookup tables. Outbound link
        # resolution requires every potential target to already be in the
        # tables, so we don't compute links until after the walk.
        for md_path in idx._walk_markdown():
            idx._index_path(md_path, _build_links=False)
        # Second pass: now that every note is known, walk each note's
        # frontmatter + body and compute its outbound link set.
        for md_path in list(idx._records):
            idx._rebuild_links(md_path)
        log.info(
            "index: %d notes (ids:%d aliases:%d filenames:%d titles:%d, "
            "outbound edges:%d, inbound targets:%d)",
            len(idx._records),
            len(idx._by_id),
            len(idx._by_alias),
            len(idx._by_filename),
            len(idx._by_title),
            sum(len(s) for s in idx._outbound.values()),
            len(idx._inbound),
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

    def _index_path(self, md_path: Path, *, _build_links: bool = True) -> None:
        """Read + parse a single note and populate the lookup tables.

        When ``_build_links`` is true (the default — used by ``invalidate``)
        the outbound link graph is rebuilt for this path immediately. The
        ``build`` classmethod sets it false during the initial walk so
        wikilink resolution can wait until every note is known.
        """
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
            body=post.content,
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

        if _build_links:
            self._rebuild_links(md_path)

    # ---- lookups ----

    def paths(self) -> list[Path]:
        """All indexed note paths (sorted by POSIX rel_path for determinism)."""
        return sorted(
            self._records.keys(),
            key=lambda p: self._records[p].rel_path,
        )

    def by_id(self, alias_or_id: str) -> Path | None:
        """Resolve an ``id`` / alias / filename / title to a path.

        Same priority order as :meth:`resolve`, but returns the path
        directly rather than a URL.
        """
        return self._lookup_path(alias_or_id)

    def resolve(self, target: str) -> str | None:
        """Return the docs URL for ``target`` or ``None`` if unresolvable."""
        path = self._lookup_path(target)
        if path is None:
            return None
        return self.url_for(path)

    def _lookup_path(self, target: str) -> Path | None:
        target = (target or "").strip()
        if not target:
            return None
        for table in (self._by_id, self._by_alias, self._by_filename, self._by_title):
            path = table.get(target)
            if path is not None:
                return path
        return None

    def get(self, path: Path) -> NoteRecord | None:
        return self._records.get(path.resolve())

    def url_for(self, path: Path) -> str:
        rel = relative_to_ci(path.resolve(), self.docs_root)
        if rel is None:
            raise ValueError(f"path not under docs root: {path}")
        return f"/docs/{rel}"

    def links_from(self, path: Path) -> frozenset[Path]:
        """Outbound: paths the note at ``path`` links to (frontmatter + body)."""
        return self._outbound.get(path.resolve(), frozenset())

    def links_to(self, path: Path) -> frozenset[Path]:
        """Inbound: paths whose body / frontmatter link to ``path``."""
        return frozenset(self._inbound.get(path.resolve(), set()))

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

    def invalidate(self, md_path: Path) -> None:
        """Re-parse a single ``.md`` path and patch the lookup tables + graph.

        Removes the path entirely if it no longer exists or is now excluded.
        Called by the watcher subscriber on every ``.md`` file event.
        """
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

    # Backwards-compatible alias — original name was ``update_path`` before
    # the cockpit task spec adopted ``invalidate``. Kept for any external
    # callers (currently none in-tree).
    update_path = invalidate

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
                self.invalidate(event.abs_path)
            except Exception:
                log.exception("index: invalidate failed for %s", event.abs_path)

        bus.subscribe(_on_event)

    # ---- backlink graph internals ----

    def _rebuild_links(self, md_path: Path) -> None:
        """(Re)compute the outbound set for ``md_path`` and patch inbound mirrors.

        Unresolvable wikilinks are logged at DEBUG (most ``[[Foo]]``-style
        unresolved hits are example syntax in docs/templates/SCHEMAS, not
        real broken refs). Each unique unresolved target is logged at most
        once per rebuild for the same file.
        """
        record = self._records.get(md_path)
        if record is None:
            return

        raw_targets: list[str] = list(_wikilinks_in_frontmatter(record.frontmatter))
        raw_targets.extend(_wikilinks_in_body(record.body))

        new_targets: set[Path] = set()
        unresolved_logged: set[str] = set()
        for raw in raw_targets:
            target = (raw or "").strip()
            if not target:
                continue
            path = self._lookup_path(target)
            if path is None:
                if target not in unresolved_logged:
                    unresolved_logged.add(target)
                    log.debug(
                        "index: unresolved wikilink in %s: [[%s]]",
                        record.rel_path,
                        target,
                    )
                continue
            if path == record.path:
                continue  # ignore self-links
            new_targets.add(path)

        old_targets = self._outbound.get(md_path, frozenset())
        for tgt in old_targets - new_targets:
            inbound = self._inbound.get(tgt)
            if inbound is not None:
                inbound.discard(md_path)
                if not inbound:
                    self._inbound.pop(tgt, None)
        for tgt in new_targets - old_targets:
            self._inbound.setdefault(tgt, set()).add(md_path)
        self._outbound[md_path] = frozenset(new_targets)

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
        # Drop outbound edges and remove ``md_path`` from each former target's
        # inbound set. ``_inbound[md_path]`` (who points AT this note) is left
        # alone — those source notes still claim to link here, and if a new
        # note appears at the same path the inbound set is already correct.
        for tgt in self._outbound.pop(md_path, frozenset()):
            inbound = self._inbound.get(tgt)
            if inbound is not None:
                inbound.discard(md_path)
                if not inbound:
                    self._inbound.pop(tgt, None)


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


def _wikilinks_in_body(body: str) -> Iterator[str]:
    for m in WIKILINK_RE.finditer(body or ""):
        yield m.group(1)


def _wikilinks_in_frontmatter(value: Any) -> Iterator[str]:
    """Walk a frontmatter value (scalar / list / dict) yielding wikilink targets."""
    if isinstance(value, str):
        for m in WIKILINK_RE.finditer(value):
            yield m.group(1)
    elif isinstance(value, list):
        for item in value:
            yield from _wikilinks_in_frontmatter(item)
    elif isinstance(value, dict):
        for v in value.values():
            yield from _wikilinks_in_frontmatter(v)
