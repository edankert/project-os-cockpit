"""Cockpit JSON API payload builders.

Pure functions that take an :class:`docs_server.index.Index` and return the
dicts that get serialised on the ``/api/cockpit/nav`` and
``/api/cockpit/context`` endpoints. Kept separate from the HTTP handler so
they're trivially testable: every assertion lives at the dict level, not
at HTTP-status level.

Schema is versioned via ``SCHEMA_VERSION`` and surfaced both inline in the
payload and in an ``X-Cockpit-Schema`` header so the JS client can detect
bumps and refuse to render an unknown shape.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .index import Index, NoteRecord

SCHEMA_VERSION: int = 1

# Stable display order for type groups in the right pane. Anything outside
# this list lands at the end, alphabetically.
TYPE_ORDER: tuple[str, ...] = (
    "feature",
    "task",
    "requirement",
    "issue",
    "risk",
    "adr",
    "change",
    "release",
    "workflow",
    "test",
    "phase",
    "plan",
    "dashboard",
)
_TYPE_RANK: dict[str, int] = {t: i for i, t in enumerate(TYPE_ORDER)}


def nav_payload(index: Index) -> dict[str, Any]:
    """Left-pane payload — features grouped by phase."""
    features = index.notes_by_type("feature")  # already excludes templates
    # Group by phase target string (e.g. "PHASE-001-MVP"). Notes without a
    # phase land in a fallback group keyed by None.
    grouped: dict[str | None, list[NoteRecord]] = {}
    for record in features:
        target = _phase_target(record)
        grouped.setdefault(target, []).append(record)

    groups: list[dict[str, Any]] = []
    # Render groups sorted by the phase note's `order` (if known), else by
    # phase id alphabetically. Unphased features go last.
    sortable: list[tuple[Any, str | None, list[NoteRecord]]] = []
    for target, records in grouped.items():
        if target is None:
            sortable.append((float("inf"), None, records))
            continue
        phase_record = _resolve_phase(index, target)
        order = _coerce_int(
            phase_record.frontmatter.get("order") if phase_record else None
        )
        sortable.append((order if order is not None else float("inf"), target, records))
    sortable.sort(key=lambda t: (t[0], t[1] or ""))

    for _order, target, records in sortable:
        phase_record = _resolve_phase(index, target) if target else None
        groups.append(
            {
                "phase_id": phase_record.note_id if phase_record else None,
                "phase_title": (
                    phase_record.title if phase_record and phase_record.title
                    else target  # fall back to the wikilink target string
                ),
                "phase_url": (
                    index.url_for(phase_record.path) if phase_record else None
                ),
                "items": [
                    _nav_item(index, r)
                    for r in sorted(records, key=lambda x: (x.note_id or "", x.rel_path))
                ],
            }
        )
    return {"schema_version": SCHEMA_VERSION, "groups": groups}


def context_payload(index: Index, this: str | None) -> dict[str, Any]:
    """Right-pane payload for an active note.

    ``this`` may be a note ID/alias or a docs-root-relative path. Returns
    an empty payload (no ``active`` block, empty lists) when ``this`` is
    missing or unresolvable.
    """
    record: NoteRecord | None = None
    if this:
        path = _resolve_this(index, this)
        if path is not None:
            record = index.get(path)

    if record is None:
        return {
            "schema_version": SCHEMA_VERSION,
            "active": None,
            "linked": [],
            "backlinks": [],
        }

    out_paths = index.links_from(record.path)
    in_paths = index.links_to(record.path) - out_paths

    return {
        "schema_version": SCHEMA_VERSION,
        "active": {
            "id": record.note_id,
            "title": record.title,
            "url": index.url_for(record.path),
        },
        "linked": _grouped_items(index, out_paths),
        "backlinks": _grouped_items(index, in_paths),
    }


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _nav_item(index: Index, record: NoteRecord) -> dict[str, Any]:
    return {
        "id": record.note_id,
        "title": record.title or record.path.stem,
        "status": record.status,
        "goal": record.frontmatter.get("goal") or "",
        "url": index.url_for(record.path),
    }


def _context_item(index: Index, record: NoteRecord) -> dict[str, Any]:
    return {
        "id": record.note_id,
        "title": record.title or record.path.stem,
        "status": record.status,
        "priority": record.frontmatter.get("priority"),
        "url": index.url_for(record.path),
    }


def _grouped_items(index: Index, paths: set[Path]) -> list[dict[str, Any]]:
    """Group ``paths`` by note type and emit items in stable order.

    Templates are excluded — placeholder IDs in the right pane would be
    noise. An item with no ``type`` lands under ``"untyped"``.
    """
    groups: dict[str, list[NoteRecord]] = {}
    for path in paths:
        record = index.get(path)
        if record is None:
            continue
        if record.rel_path.startswith("__templates__/"):
            continue
        bucket = record.note_type or "untyped"
        groups.setdefault(bucket, []).append(record)

    ordered_keys = sorted(
        groups,
        key=lambda t: (_TYPE_RANK.get(t, len(TYPE_ORDER)), t),
    )
    return [
        {
            "type": key,
            "items": [
                _context_item(index, r)
                for r in sorted(
                    groups[key], key=lambda x: (x.note_id or "", x.rel_path)
                )
            ],
        }
        for key in ordered_keys
    ]


def _phase_target(record: NoteRecord) -> str | None:
    """Extract the phase wikilink target from a note's frontmatter.

    Accepts both scalar (``phase: "[[PHASE-001-MVP]]"``) and list
    (``phase: ["[[PHASE-001-MVP]]"]``) forms. Returns the bare target
    string, or ``None`` if no phase is set.
    """
    raw = record.frontmatter.get("phase")
    if isinstance(raw, list):
        raw = raw[0] if raw else None
    if not isinstance(raw, str):
        return None
    s = raw.strip()
    if s.startswith("[[") and s.endswith("]]"):
        s = s[2:-2].strip()
    return s or None


def _resolve_phase(index: Index, target: str) -> NoteRecord | None:
    path = index.by_id(target)
    if path is None:
        return None
    return index.get(path)


def _resolve_this(index: Index, this: str) -> Path | None:
    """Resolve the ``this`` query parameter to a note path.

    Tries id/alias/filename/title first (cheap, common case). Falls back
    to a path-style lookup (treating ``this`` as docs-root-relative) so
    the JS client can hand over either form.
    """
    by_id = index.by_id(this)
    if by_id is not None:
        return by_id
    # Path-style fallback. Strip leading ``/docs/`` if present (the JS
    # client may pass URLs verbatim).
    rel = this.lstrip("/")
    if rel.startswith("docs/"):
        rel = rel[len("docs/"):]
    candidate = (index.docs_root / rel).resolve()
    if candidate.suffix.lower() != ".md":
        return None
    record = index.get(candidate)
    return candidate if record is not None else None


def _coerce_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return None
    return None
