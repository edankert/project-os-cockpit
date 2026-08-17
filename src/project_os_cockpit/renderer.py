"""Markdown -> HTML render pipeline.

Reads a ``.md`` source file, splits frontmatter via ``python-frontmatter``,
runs Markdown via ``markdown`` + selected ``pymdownx`` extensions and the
project's own :class:`project_os_cockpit.wikilinks.WikilinkExtension`, and wraps
the result in the shared HTML shell from :mod:`project_os_cockpit.templates`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import frontmatter
import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

import html as _html
import itertools as _it
import logging
import re as _re

from . import templates
from .note_writes import _criterion_text
from .callouts import CalloutExtension
from .wikilinks import Resolver, WikilinkExtension


AssetResolver = Callable[[str, Path], str | None]


MARKDOWN_EXTENSIONS_BASE: list[str] = [
    "tables",
    "fenced_code",
    "toc",
    "pymdownx.superfences",
    "pymdownx.highlight",
    "pymdownx.tasklist",
]

MARKDOWN_EXTENSION_CONFIGS: dict[str, dict[str, Any]] = {
    "toc": {"permalink": False},
    "pymdownx.highlight": {
        "use_pygments": True,
        "noclasses": False,
        "css_class": "codehilite",
    },
    "pymdownx.tasklist": {
        # Obsidian-style: render `- [x]` / `- [ ]` as visual checkboxes,
        # read-only (we're a renderer, not an editor — the source is the
        # truth, the page is the view).
        "clickable_checkbox": False,
        "custom_checkbox": True,
    },
}


def render_markdown_body(
    source_path: Path,
    *,
    resolver: Resolver | None = None,
    asset_resolver: AssetResolver | None = None,
) -> str:
    """Render just the body of a ``.md`` file to HTML, no page chrome.

    Used by the landing-page fallback to embed a README inside the cockpit
    shell without re-running the full ``page()`` wrapper.
    """
    raw = source_path.read_text(encoding="utf-8")
    post = frontmatter.loads(raw)
    return _markdown_to_html(
        post.content,
        resolver=resolver,
        asset_resolver=asset_resolver,
        source_path=source_path,
    )


def render_markdown_text(
    body: str,
    *,
    source_path: Path,
    resolver: Resolver | None = None,
    asset_resolver: AssetResolver | None = None,
) -> str:
    """Render a markdown *fragment* already in memory (ISS-0151).

    `render_markdown_body` reads a file; the brief's sections are slices of one
    that has already been parsed, and re-reading to re-split it would put the
    section boundaries in two places.
    """
    return _markdown_to_html(
        body,
        resolver=resolver,
        asset_resolver=asset_resolver,
        source_path=source_path,
    )


def render_markdown_file(
    source_path: Path,
    *,
    rel_path: str,
    resolver: Resolver | None = None,
    asset_resolver: AssetResolver | None = None,
    url_prefix: str = "/docs",
    reload_source: str | None = None,
) -> str:
    """Render a single ``.md`` file to a complete HTML document.

    ``rel_path`` is the route-root-relative path used for the breadcrumb;
    the actual filesystem read uses ``source_path``. ``url_prefix`` is the URL
    root for that route, defaulting to ``/docs``. ``resolver`` (when
    provided) is consulted by :class:`WikilinkExtension` and by the
    metadata-strip wikilink resolver in :mod:`project_os_cockpit.templates`.
    """
    raw = source_path.read_text(encoding="utf-8")
    post = frontmatter.loads(raw)
    metadata: dict[str, Any] = dict(post.metadata or {})
    body_md = post.content

    title = _derive_title(metadata, body_md, source_path)
    body_html = _markdown_to_html(
        body_md,
        resolver=resolver,
        asset_resolver=asset_resolver,
        source_path=source_path,
    )

    note_id = metadata.get("id") if isinstance(metadata.get("id"), str) else None
    route_prefix = url_prefix.rstrip("/")
    url = f"{route_prefix}/{rel_path}" if route_prefix else f"/{rel_path}"
    cockpit_active = {
        "id": note_id,
        "path": rel_path,
        "url": url,
        "title": title,
    }

    return templates.page(
        title=title,
        body_html=body_html,
        rel_path=rel_path,
        metadata=metadata,
        resolver=resolver,
        reload_source=rel_path if reload_source is None else reload_source,
        path_prefix=route_prefix or "",
        cockpit_active=cockpit_active,
    )


def _markdown_to_html(
    text: str,
    *,
    resolver: Resolver | None,
    asset_resolver: AssetResolver | None,
    source_path: Path,
) -> str:
    # Callouts before the wikilink extension for no ordering reason — they
    # are independent — but registered ALWAYS, including for notes rendered
    # without a resolver, because a decision record is prose in a file and
    # is read from more places than the note page (FEAT-0095).
    extensions: list[Any] = [
        *MARKDOWN_EXTENSIONS_BASE, CalloutExtension(),
        # Stamps every acceptance row with its mark and its address, because
        # an HTML checkbox holds two states and the record's vocabulary has
        # four. Inert for every document that is not an acceptance suite.
        AcceptanceMarkExtension(text),
    ]
    if resolver is not None:
        image_resolver = (
            (lambda target: asset_resolver(target, source_path))
            if asset_resolver is not None
            else None
        )
        extensions.append(WikilinkExtension(resolver, image_resolver=image_resolver))
    if asset_resolver is not None:
        extensions.append(ImageSourceExtension(asset_resolver, source_path))
    md = markdown.Markdown(
        extensions=extensions,
        extension_configs=MARKDOWN_EXTENSION_CONFIGS,
        output_format="html5",
        tab_length=2,
    )
    return _annotate_checkbox_source(md.convert(text), text)


#: A rendered task-list checkbox, as pymdownx.tasklist emits it. Matched on
#: the input element rather than the `<li>`, because that is the node the
#: renderer already holds when a criterion is clicked.
log = logging.getLogger("project_os_cockpit.renderer")

_RENDERED_BOX_RE = _re.compile(r"<input(?=[^>]*\btype=\"checkbox\")")
#: A task row's mark as it stands in the tree, BEFORE `task-list` runs. One
#: character between brackets, whatever it is — the classification belongs to
#: `acceptance.parse`, not here.
_TREE_MARK_RE = _re.compile(r"^\[(.)\]\s*")


def _annotate_checkbox_source(html: str, source_md: str) -> str:
    """Carry each checkbox's **raw** source prose onto its rendered input.

    ISS-0137. Markdown consumes inline markup on the way out: `` `x` ``
    becomes ``<code>x</code>``, ``[[y]]`` becomes an anchor, ``**z**``
    becomes ``<strong>``. A client that recovers the criterion by reading
    ``textContent`` therefore produces a string the *source* does not
    contain — and `note_writes.resolve_criterion` matches against the source
    line, exactly and deliberately, because ambiguity there is a refusal
    rather than a guess.

    The two never agreed for any criterion carrying markup, which measured
    on this corpus was **26 of 53 open criteria**. The tick prompt accepted
    the evidence and then the write was refused, which is the worst order to
    fail in: the reader has already done the thinking.

    So the raw line travels with the box. The correspondence is ordinal —
    the Nth rendered checkbox is the Nth task-list line in the source — the
    same walk `server._toggle_task_at` has always relied on for plain
    toggles, and the same document order Markdown guarantees.

    ``data-raw`` is the criterion's prose after ``_criterion_text``, so a
    ticked box carries the criterion rather than the criterion plus its
    evidence, and re-resolving addresses the criterion.
    """
    raws = [
        _criterion_text(line) for line in source_md.splitlines()
        if _criterion_text(line) is not None
    ]
    if not raws:
        return html

    # **The counts must agree, or nothing is labelled** (ISS-0175).
    #
    # The ordinal correspondence this function relies on is FALSE whenever
    # Markdown declines to make a list. A task list that opens immediately
    # after a paragraph line — no blank line between — is lazy continuation:
    # it is absorbed into the paragraph and renders **no checkboxes at all**,
    # while `_criterion_text` is line-based and counts every one.
    #
    # Measured on `your-trainer`'s acceptance suite: 579 source task lines,
    # 542 rendered inputs, and from the first divergence at box #257 every
    # subsequent box carried a DIFFERENT row's text — 285 of 542 mislabelled.
    #
    # `resolve_criterion` matches the source exactly and deliberately, because
    # ambiguity there is meant to be a refusal rather than a guess. Feeding it
    # a confidently wrong value defeats that. The over-count branch below
    # already states the principle — *"leaving the attribute off degrades to
    # the old behaviour rather than mislabelling a box with somebody else's
    # text"* — and this applies it to the whole document rather than to one
    # box, because a count mismatch means the alignment is unknowable, not
    # merely short.
    rendered_boxes = len(_RENDERED_BOX_RE.findall(html))
    if rendered_boxes != len(raws):
        log.warning(
            "checkbox annotation skipped: %d rendered boxes against %d source "
            "task lines. A task list that opens immediately after a paragraph "
            "renders no checkboxes; add a blank line before it.",
            rendered_boxes, len(raws),
        )
        return html

    # The check's ADDRESS is NOT emitted here. It lives on the `<li>`, put
    # there by `AcceptanceMarkTreeprocessor`, because two of the four marks
    # never become an `<input>` at all and an address that only reaches half
    # the vocabulary is worse than none. Emitting it in both places produced
    # 1088 addresses for 579 rows, which is how this was caught.
    counter = _it.count()

    def _sub(match: "_re.Match[str]") -> str:
        idx = next(counter)
        if idx >= len(raws):
            # More rendered boxes than source lines should be impossible;
            # leaving the attribute off degrades to the old behaviour rather
            # than mislabelling a box with somebody else's text.
            return match.group(0)
        return f'{match.group(0)} data-raw="{_html.escape(raws[idx], quote=True)}"'

    return _RENDERED_BOX_RE.sub(_sub, html)


def _check_numbers(source_md: str) -> tuple[list[str], list[str]]:
    """Each task line's acceptance address, or ``""`` where it has none.

    Positional with `raws` above, and guarded by the same count agreement:
    this is only ever consulted when rendered boxes and source task lines
    already match, so the Nth entry belongs to the Nth box.

    A document that is not an acceptance suite yields all-empty and the
    attribute is simply not emitted.
    """
    from . import acceptance

    try:
        items = acceptance.parse(source_md)
    except Exception:                      # pragma: no cover — parse is total
        return [], []
    if not items:
        return [], []
    # `parse` walks task lines in document order and skips fences, exactly as
    # `_criterion_text` does, so the two lists correspond one-for-one. Asserted
    # by length rather than assumed: a mismatch means some other rule differs
    # between them, and the safe answer is to emit no addresses at all.
    numbers = [i.number for i in items]
    names = [i.name for i in items]
    raw_count = sum(
        1 for line in source_md.splitlines()
        if _criterion_text(line) is not None
    )
    return (numbers, names) if len(numbers) == raw_count else ([], [])


class ImageSourceTreeprocessor(Treeprocessor):
    """Resolve standard Markdown image URLs to stable ``/docs/...`` URLs."""

    def __init__(self, md, asset_resolver: AssetResolver, source_path: Path) -> None:
        super().__init__(md)
        self._asset_resolver = asset_resolver
        self._source_path = source_path

    def run(self, root):  # type: ignore[override]
        for el in root.iter("img"):
            src = el.get("src")
            if not src:
                continue
            resolved = self._asset_resolver(src, self._source_path)
            if resolved:
                el.set("src", resolved)
        return root


class AcceptanceMarkTreeprocessor(Treeprocessor):
    """Make every acceptance row carry its mark and its address (TASK-0456).

    **An HTML checkbox cannot hold four states, and `pymdownx.tasklist` only
    knows two.** Measured: a `- [~]` or `- [F]` row renders with *no input
    element at all* and its mark left as literal `[~]` text in the prose. So
    the seven marked rows in `../your-trainer`'s v2.1.0 suite are unclickable,
    and the whole document's annotation is skipped because 258 rendered boxes
    cannot be aligned to 300 source rows.

    That — not lazy continuation — is the real reason [[FEAT-0104]] stalled.
    The note recorded ISS-0175 as the blocker; ISS-0175 accounts for 35 of the
    42 missing boxes in that file and the marks account for the other 7, and
    neither can be fixed by counting more carefully.

    So the *list item* is stamped rather than the input: every gating row gets
    ``data-check``, ``data-check-name`` and ``data-mark`` whatever its mark,
    and the client draws a four-state control from them. Rows Markdown never
    made into list items at all are still beyond reach — [[TASK-0457]] names
    those rather than pretending.
    """

    def __init__(self, md, source_md: str) -> None:
        super().__init__(md)
        self._source = source_md

    def run(self, root):  # type: ignore[override]
        from . import acceptance

        items = acceptance.parse(self._source)
        if not items:
            return root
        # Only the rows Markdown actually made into list items can be
        # addressed. Matching is by NAME, in document order, so a row that
        # never became an `<li>` is skipped rather than shifting every
        # address after it — the failure this whole task exists to remove.
        by_name: dict[str, list] = {}
        for item in items:
            by_name.setdefault(item.name.strip(), []).append(item)

        for li in root.iter("li"):
            text = "".join(li.itertext()).strip()
            if not text:
                continue
            # `pymdownx.tasklist` swaps the literal for an `<input>` in a
            # POSTprocessor, after every treeprocessor has run. So at this
            # point all four marks are still prose — including the two the
            # extension understands — and reading the tree for an input finds
            # nothing. Measured, not assumed: a first pass looked for the
            # input and addressed only the `~`/`F` rows, which is the exact
            # inverse of what the extension supports.
            # ANY single-character mark, decided by `acceptance.parse` rather
            # than by a list here. Minimal defines 22 values (ADR-0029) and
            # this must not carry a second, narrower opinion about which are
            # real — six mean something to a gate, sixteen parse as
            # unrecognised and block, and both cases still need addressing so
            # the reader can change them.
            found = _TREE_MARK_RE.match(text)
            if not found:
                continue                       # not a task row at all
            mark = found.group(1)
            text = text[found.end():].lstrip()

            name = _leading_name(text)
            queue = by_name.get(name)
            if not queue:
                continue
            item = queue.pop(0)
            li.set("data-check", item.number)
            li.set("data-check-name", item.name)
            li.set("data-mark", mark)
            li.set("data-gating", "1" if item.tier in acceptance.GATING_TIERS
                   else "0")
            # Strip the literal mark ONLY for the two tasklist does not
            # understand. Its own postprocessor consumes `[ ]` and `[x]`
            # itself, and removing them here would leave it nothing to find.
            # Only the marks `tasklist` does not consume itself. It handles
            # `[ ]` and `[x]`/`[X]`; every other value it leaves as literal
            # prose, and that literal is what has to come off.
            if mark not in {" ", "x", "X"}:
                _strip_literal_mark(li, mark)

        # Rows Markdown never made into a list item at all (TASK-0457).
        #
        # Their list opens directly under a paragraph line, so lazy
        # continuation absorbs it and there is no `<li>` to stamp and nothing
        # on screen to click. They are still in the gate's count and they are
        # still real work.
        #
        # Named rather than left absent: ISS-0172's rule is that an affordance
        # which cannot work should explain itself rather than vanish. And NOT
        # auto-fixed — reformatting somebody's document because it would be
        # more convenient to click is a different act, and it would rewrite the
        # file the gate reads.
        unreachable = len(items) - sum(
            1 for li in root.iter("li") if li.get("data-check")
        )
        if unreachable > 0:
            _prepend_unreachable_notice(root, unreachable, len(items))
        return root


def _prepend_unreachable_notice(root, count: int, total: int) -> None:  # noqa: ANN001
    """State how many checks have no clickable control, and the one-line fix."""
    import xml.etree.ElementTree as ET

    box = ET.Element("div", {"class": "callout callout-warning acc-unreachable"})
    title = ET.SubElement(box, "p", {"class": "callout-title"})
    title.text = (
        f"{count} of {total} checks cannot be marked here"
    )
    body = ET.SubElement(box, "p")
    body.text = (
        "Their list opens directly under a paragraph, so Markdown renders no "
        "checkbox for them. Add a blank line above each list to make them "
        "clickable. Until then they still count towards the release gate and "
        "must be marked by editing this file."
    )
    root.insert(0, box)


def _leading_name(text: str) -> str:
    """A row's name, read with **`parse`'s own regex** rather than a lookalike.

    This runs before the inline processor, so the `**` are still literal and
    the same pattern applies to the tree text as to the source line.

    Splitting on the first colon looked equivalent and is not: a name may
    contain one — *"Imported intervals get translated (Layer 1: shared
    assignment)"* — and a hand-rolled split truncates it, so the row fails to
    match and goes unaddressed. That accounted for most of the 70 rows this
    could not reach on `your-trainer`'s suite. Two parsers for one convention
    is the drift this project keeps paying for; there is now one.
    """
    from .acceptance import _NAME_RE

    named = _NAME_RE.match(text.strip())
    if named:
        return named.group(1).strip()
    return text.strip().strip("*").strip()


def _strip_literal_mark(li, mark: str) -> None:  # noqa: ANN001
    """Remove the leading `[<mark>] ` that tasklist left as prose."""
    literal = f"[{mark}]"
    for node in li.iter():
        if node.text and node.text.lstrip().startswith(literal):
            stripped = node.text.lstrip()
            node.text = stripped[len(literal):].lstrip()
            return


class AcceptanceMarkExtension(Extension):
    def __init__(self, source_md: str) -> None:
        super().__init__()
        self._source_md = source_md

    def extendMarkdown(self, md) -> None:  # type: ignore[override]
        md.treeprocessors.register(
            AcceptanceMarkTreeprocessor(md, self._source_md),
            "project_os_acceptance_marks",
            # ABOVE `task-list` (25), which is the whole trick. Below it, the
            # extension has already swapped `[ ]`/`[x]` for a stashed raw-HTML
            # input, so neither the literal nor an `<input>` element is in the
            # tree and only the two marks it does NOT understand survive to be
            # read — the exact inverse of what is wanted, and what a first
            # pass at priority 4 actually produced.
            #
            # Above it, all four marks are still prose. `[ ]` and `[x]` are
            # left in place for tasklist to consume; only `[~]` and `[F]`,
            # which it would leave as literal text forever, are removed here.
            26,
        )


class ImageSourceExtension(Extension):
    def __init__(self, asset_resolver: AssetResolver, source_path: Path) -> None:
        super().__init__()
        self._asset_resolver = asset_resolver
        self._source_path = source_path

    def extendMarkdown(self, md) -> None:  # type: ignore[override]
        md.treeprocessors.register(
            ImageSourceTreeprocessor(md, self._asset_resolver, self._source_path),
            "project_os_image_sources",
            5,
        )


def _derive_title(metadata: dict[str, Any], body: str, source_path: Path) -> str:
    title = metadata.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return source_path.stem
