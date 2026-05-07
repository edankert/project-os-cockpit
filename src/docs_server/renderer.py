"""Markdown -> HTML render pipeline.

Reads a ``.md`` source file, splits frontmatter via ``python-frontmatter``,
runs Markdown via ``markdown`` + selected ``pymdownx`` extensions and the
project's own :class:`docs_server.wikilinks.WikilinkExtension`, and wraps
the result in the shared HTML shell from :mod:`docs_server.templates`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import frontmatter
import markdown

from . import templates
from .wikilinks import Resolver, WikilinkExtension


MARKDOWN_EXTENSIONS_BASE: list[str] = [
    "tables",
    "fenced_code",
    "toc",
    "pymdownx.superfences",
    "pymdownx.highlight",
]

MARKDOWN_EXTENSION_CONFIGS: dict[str, dict[str, Any]] = {
    "toc": {"permalink": False},
    "pymdownx.highlight": {
        "use_pygments": True,
        "noclasses": False,
        "css_class": "codehilite",
    },
}


def render_markdown_file(
    source_path: Path,
    *,
    rel_path: str,
    resolver: Resolver | None = None,
) -> str:
    """Render a single ``.md`` file to a complete HTML document.

    ``rel_path`` is the docs-root-relative path used for the breadcrumb;
    the actual filesystem read uses ``source_path``. ``resolver`` (when
    provided) is consulted by :class:`WikilinkExtension` and by the
    metadata-strip wikilink resolver in :mod:`docs_server.templates`.
    """
    raw = source_path.read_text(encoding="utf-8")
    post = frontmatter.loads(raw)
    metadata: dict[str, Any] = dict(post.metadata or {})
    body_md = post.content

    title = _derive_title(metadata, body_md, source_path)
    body_html = _markdown_to_html(body_md, resolver=resolver)

    return templates.page(
        title=title,
        body_html=body_html,
        rel_path=rel_path,
        metadata=metadata,
        resolver=resolver,
        reload_source=rel_path,
    )


def _markdown_to_html(text: str, *, resolver: Resolver | None) -> str:
    extensions: list[Any] = list(MARKDOWN_EXTENSIONS_BASE)
    if resolver is not None:
        extensions.append(WikilinkExtension(resolver))
    md = markdown.Markdown(
        extensions=extensions,
        extension_configs=MARKDOWN_EXTENSION_CONFIGS,
        output_format="html5",
        tab_length=2,
    )
    return md.convert(text)


def _derive_title(metadata: dict[str, Any], body: str, source_path: Path) -> str:
    title = metadata.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return source_path.stem
