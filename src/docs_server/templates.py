"""HTML page assembly: shell, metadata strip, breadcrumb, status chips.

The shell follows REQ-0012 — theme tokens live in ``base.css``; the inline
``<head>`` script resolves the theme before stylesheet apply so the user
never sees a wrong-theme flash on first paint.
"""

from __future__ import annotations

from html import escape
from pathlib import PurePosixPath
from typing import Any, Iterable

from .wikilinks import Resolver, resolve_text_to_html

# Frontmatter keys that get top billing in the metadata strip, in display order.
# Anything else in frontmatter is folded into a generic "other" row at the end.
PRIMARY_META_KEYS: tuple[str, ...] = (
    "id",
    "type",
    "status",
    "phase",
    "owner",
    "parent",
    "implements",
    "specifies",
    "fixes",
    "validates",
    "blocks",
    "depends",
    "related",
    "source",
    "tags",
    "created",
    "updated",
    "due",
    "effort",
    "priority",
    "platform",
)

# Hidden in the strip (noise / housekeeping).
HIDDEN_META_KEYS: frozenset[str] = frozenset({"aliases", "title"})

THEME_BOOTSTRAP = """\
(function () {
  try {
    var saved = localStorage.getItem('docs-server.theme');
    var dark = saved === 'dark' ||
      (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches);
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
  } catch (e) {}
})();
"""

THEME_TOGGLE_SCRIPT = """\
(function () {
  var btn = document.querySelector('.theme-toggle');
  if (!btn) return;
  function update() {
    var t = document.documentElement.getAttribute('data-theme') || 'light';
    btn.setAttribute('aria-pressed', t === 'dark' ? 'true' : 'false');
    btn.textContent = t === 'dark' ? '\\u25D1' : '\\u25D0';
  }
  btn.addEventListener('click', function () {
    var current = document.documentElement.getAttribute('data-theme') || 'light';
    var next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem('docs-server.theme', next); } catch (e) {}
    update();
  });
  update();
})();
"""


def page(
    *,
    title: str,
    body_html: str,
    rel_path: str | None = None,
    metadata: dict[str, Any] | None = None,
    resolver: Resolver | None = None,
    reload_source: str | None = None,
) -> str:
    """Assemble a full HTML document for a rendered note or status page.

    ``reload_source`` controls the live-reload behaviour:
    - a relative ``.md`` path (e.g. ``"features/render-server/FEAT-...md"``)
      means "reload only when this file changes";
    - the literal ``"*"`` means "reload on any file event" (used by the
      landing, index, and directory-listing pages whose content depends on
      the whole tree);
    - ``None`` (default) suppresses live reload entirely.
    """
    breadcrumb = _breadcrumb_html(rel_path) if rel_path else ""
    meta_html = _metadata_strip_html(metadata, resolver) if metadata else ""
    safe_title = escape(title)

    reload_meta = ""
    reload_script = ""
    if reload_source:
        reload_meta = (
            '<meta name="docs-server:source" '
            f'content="{escape(reload_source)}">\n'
        )
        reload_script = '<script src="/_static/sse-reload.js" defer></script>\n'

    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{safe_title} — docs-server</title>\n"
        f"{reload_meta}"
        '<link rel="stylesheet" href="/_static/base.css">\n'
        f"<script>{THEME_BOOTSTRAP}</script>\n"
        f"{reload_script}"
        "</head>\n"
        '<body>\n'
        '<header class="page-header">\n'
        '  <span class="brand">docs-server</span>\n'
        f'  <nav class="breadcrumb" aria-label="Breadcrumb">{breadcrumb}</nav>\n'
        '  <button class="theme-toggle" type="button" aria-label="Toggle light / dark theme" aria-pressed="false">◐</button>\n'
        "</header>\n"
        '<main class="page">\n'
        f"{meta_html}"
        f'<article class="content">\n{body_html}\n</article>\n'
        "</main>\n"
        f"<script>{THEME_TOGGLE_SCRIPT}</script>\n"
        "</body>\n"
        "</html>\n"
    )


def notice_page(
    *,
    title: str,
    heading: str,
    body_html: str,
    error: bool = False,
) -> str:
    """Minimal page for 403 / 404 / placeholder content."""
    cls = "notice error" if error else "notice"
    body = (
        f'<div class="{cls}">\n'
        f"<h2>{escape(heading)}</h2>\n"
        f"{body_html}\n"
        "</div>\n"
    )
    return page(title=title, body_html=body)


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _breadcrumb_html(rel_path: str) -> str:
    parts = [p for p in PurePosixPath(rel_path).parts if p not in (".", "/")]
    if not parts:
        return f'<a href="/">root</a>'

    crumbs: list[str] = [f'<a href="/">root</a>']
    accum = ""
    for i, part in enumerate(parts):
        accum = f"{accum}/{part}" if accum else part
        is_last = i == len(parts) - 1
        if is_last:
            crumbs.append(f"<span>{escape(part)}</span>")
        else:
            href = f"/docs/{accum}/"
            crumbs.append(f'<a href="{escape(href)}">{escape(part)}</a>')
    return '<span class="sep">/</span>'.join(crumbs)


def _metadata_strip_html(meta: dict[str, Any], resolver: Resolver | None) -> str:
    if not meta:
        return ""

    pairs: list[tuple[str, str]] = []
    seen: set[str] = set()

    for key in PRIMARY_META_KEYS:
        if key in HIDDEN_META_KEYS:
            continue
        if key in meta and meta[key] not in (None, "", [], {}):
            pairs.append((key, _render_meta_value(key, meta[key], resolver)))
            seen.add(key)

    for key, value in meta.items():
        if key in HIDDEN_META_KEYS or key in seen:
            continue
        if value in (None, "", [], {}):
            continue
        pairs.append((key, _render_meta_value(key, value, resolver)))

    if not pairs:
        return ""

    rows = "\n".join(
        f"  <dt>{escape(k)}</dt>\n  <dd>{v}</dd>"
        for k, v in pairs
    )
    return f'<aside class="metadata-strip"><dl>\n{rows}\n</dl></aside>\n'


def _render_meta_value(key: str, value: Any, resolver: Resolver | None) -> str:
    """Render a single frontmatter value as HTML.

    Status renders as a chip; lists render as comma-separated entries
    inside a wrapping span; scalar values render as text with wikilinks
    resolved when a ``resolver`` is provided. Wikilink-shaped strings go
    through the resolver like any other — including ``type: "[[feature]]"``,
    which will render as an unresolved (broken) wikilink unless a
    corresponding type-stub note exists. This matches Obsidian's behaviour.
    """
    if key == "status":
        return _status_chip(value)
    if isinstance(value, list):
        if not value:
            return ""
        items = [_render_scalar(v, resolver) for v in value]
        return '<span class="meta-list">' + ", ".join(items) + "</span>"
    if isinstance(value, dict):
        items = [
            f"{escape(str(k))}: {_render_scalar(v, resolver)}"
            for k, v in value.items()
        ]
        return '<span class="meta-list">' + ", ".join(items) + "</span>"
    return _render_scalar(value, resolver)


def _render_scalar(value: Any, resolver: Resolver | None) -> str:
    if value is None:
        return ""
    text = str(value)
    if resolver is not None and "[[" in text:
        return resolve_text_to_html(text, resolver)
    return escape(text)


def _status_chip(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(_status_chip(v) for v in value if v)
    text = str(value).strip()
    if not text:
        return ""
    slug = text.lower().replace(" ", "-")
    return f'<span class="status-chip" data-status="{escape(slug)}">{escape(text)}</span>'


# ---------------------------------------------------------------------------
# Index pages (TASK-0004)
# ---------------------------------------------------------------------------

# Lower rank = earlier in the page. Tuned to satisfy REQ-0007:
#   active/doing/in-progress first → backlog/triage middle → done/closed last.
STATUS_RANK: dict[str, int] = {
    # active / in-progress
    "active": 10, "doing": 11, "in-progress": 11, "next": 12,
    "approved": 13, "accepted": 13,
    # backlog
    "backlog": 30, "planned": 31, "proposed": 31, "draft": 32,
    "todo": 32, "open": 33, "pending": 33, "triage": 34, "reference": 35,
    # done
    "done": 60, "fixed": 60, "merged": 60, "published": 60,
    "verified": 65, "passing": 65,
    # dead / blocked
    "closed": 80, "obsolete": 81, "blocked": 90, "reopened": 91, "failing": 92,
}
STATUS_RANK_DEFAULT: int = 50

# Statuses whose collapsible group defaults to closed (still expandable).
COLLAPSED_BY_DEFAULT: frozenset[str] = frozenset(
    {"done", "fixed", "merged", "published", "verified", "passing",
     "closed", "obsolete"}
)


def index_page_html(
    *,
    type_label: str,        # "features", "tasks", ...
    type_singular: str,     # "feature", "task", ... (matches normalised type)
    notes: list,            # list[NoteRecord]
    docs_root_name: str,
) -> str:
    """Render an index page: notes of one type, grouped by status."""
    if not notes:
        body = (
            f'<h1>{escape(type_label.title())}</h1>\n'
            f'<p class="meta">No notes of type '
            f'<code>{escape(type_singular)}</code> found.</p>'
        )
        return page(
            title=f"index: {type_label}",
            body_html=body,
            rel_path=None,
            reload_source="*",
        )

    # Group by status.
    groups: dict[str, list] = {}
    for note in notes:
        key = note.status or "(no status)"
        groups.setdefault(key, []).append(note)

    # Sort within each group by note_id, then title, then path.
    for key in groups:
        groups[key].sort(
            key=lambda r: (r.note_id or "", r.title or "", r.rel_path)
        )

    # Sort groups by status rank.
    ordered = sorted(
        groups.items(),
        key=lambda kv: (STATUS_RANK.get(kv[0], STATUS_RANK_DEFAULT), kv[0]),
    )

    sections: list[str] = []
    for status, items in ordered:
        open_attr = "" if status in COLLAPSED_BY_DEFAULT else " open"
        rows = "\n".join(_index_row_html(n) for n in items)
        sections.append(
            f'<section class="index-group">\n'
            f'  <details{open_attr}>\n'
            f'    <summary>'
            f'<span class="status-chip" data-status="{escape(status)}">'
            f'{escape(status)}</span>'
            f'<span class="count">{len(items)}</span>'
            f'</summary>\n'
            f'    <ul class="index-items">\n{rows}\n    </ul>\n'
            f'  </details>\n'
            f'</section>'
        )

    body_html = (
        f'<h1>{escape(type_label.title())} '
        f'<span class="muted-count">({len(notes)})</span></h1>\n'
        f'<p class="meta">Index of <code>type: '
        f'[[{escape(type_singular)}]]</code> notes under '
        f'<code>{escape(docs_root_name)}/</code>, grouped by status.</p>\n'
        + "\n".join(sections)
    )
    return page(
        title=f"index: {type_label}",
        body_html=body_html,
        rel_path=None,
        reload_source="*",
    )


def _index_row_html(note) -> str:
    title = note.title or note.path.stem
    href = f"/docs/{note.rel_path}"
    id_part = (
        f'<span class="index-id">{escape(note.note_id)}</span> — '
        if note.note_id else ""
    )
    return (
        f'      <li>{id_part}'
        f'<a href="{escape(href)}">{escape(title)}</a></li>'
    )


def landing_page_html(
    *,
    type_counts: dict[str, int],
    plural_for: dict[str, str],
    docs_root_name: str,
    focus: dict[str, str] | None = None,
    resolver: Resolver | None = None,
) -> str:
    """The ``/`` landing page — counts per indexable type + focus surface."""
    items: list[str] = []
    # Drive the list off plural_for (the canonical set of indexable types) so
    # zero-count types still show up with (0) — gives the user a complete
    # taxonomy view at a glance.
    for type_singular in sorted(plural_for):
        plural = plural_for[type_singular]
        count = type_counts.get(type_singular, 0)
        items.append(
            f'      <li><a href="/index/{escape(plural)}">'
            f'{escape(plural.title())}</a> '
            f'<span class="muted-count">({count})</span></li>'
        )
    indices_html = (
        '<ul class="index-list">\n' + "\n".join(items) + "\n    </ul>"
        if items
        else '<p class="meta">No typed notes indexed yet.</p>'
    )

    focus_html = ""
    if focus:
        focus_rows = "\n".join(
            f'  <dt>{escape(k)}</dt>\n  <dd>{_render_scalar(v, resolver)}</dd>'
            for k, v in focus.items() if v
        )
        if focus_rows:
            focus_html = (
                '<aside class="metadata-strip">\n'
                '  <h2 class="meta-heading">Current focus</h2>\n'
                f'  <dl>\n{focus_rows}\n  </dl>\n'
                '</aside>\n'
            )

    body = (
        f'<h1>{escape(docs_root_name)}</h1>\n'
        f'<p class="meta">Project-os documentation tree. '
        f'Browse by type below, or open '
        f'<a href="/docs/">the filesystem listing</a>.</p>\n'
        f'{focus_html}'
        f'<h2>Indexes</h2>\n'
        f'    {indices_html}\n'
    )
    return page(
        title=docs_root_name,
        body_html=body,
        rel_path=None,
        reload_source="*",
    )


def directory_listing_html(entries: Iterable[tuple[str, str, bool]]) -> str:
    """Render a simple directory listing.

    ``entries`` is an iterable of ``(href, label, is_dir)`` tuples.
    """
    items: list[str] = []
    for href, label, is_dir in entries:
        cls = "dir" if is_dir else "file"
        items.append(
            f'<li class="{cls}"><a href="{escape(href)}">{escape(label)}</a></li>'
        )
    return '<ul class="dir-listing">\n' + "\n".join(items) + "\n</ul>"
