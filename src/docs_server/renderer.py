"""Markdown -> HTML render pipeline.

Reads a ``.md`` source file, splits frontmatter via ``python-frontmatter``,
runs Markdown via ``markdown`` + selected ``pymdownx`` extensions, and wraps
the result in the shared HTML shell from :mod:`docs_server.templates`.

Wikilink resolution is intentionally out of scope here — TASK-0003 layers
that on top of this pipeline by post-processing the rendered HTML (or by
adding a markdown extension) using the index built in TASK-0007.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import frontmatter
import markdown

from . import templates


MARKDOWN_EXTENSIONS: list[str] = [
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


def render_markdown_file(source_path: Path, *, rel_path: str) -> str:
    """Render a single ``.md`` file to a complete HTML document.

    ``rel_path`` is the docs-root-relative path used for the breadcrumb;
    the actual filesystem read uses ``source_path``.
    """
    raw = source_path.read_text(encoding="utf-8")
    post = frontmatter.loads(raw)
    metadata: dict[str, Any] = dict(post.metadata or {})
    body_md = post.content

    title = _derive_title(metadata, body_md, source_path)
    body_html = _markdown_to_html(body_md)

    return templates.page(
        title=title,
        body_html=body_html,
        rel_path=rel_path,
        metadata=metadata,
    )


def _markdown_to_html(text: str) -> str:
    md = markdown.Markdown(
        extensions=MARKDOWN_EXTENSIONS,
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
