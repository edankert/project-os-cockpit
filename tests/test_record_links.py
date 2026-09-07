"""Links in the record resolve ([[ISS-0287]]).

**Nothing read a link in a note's body until this file existed.**
`tools/scripts/validate-docs.py` is thorough about the *graph* — a task's
`parent:`, the backlink, snapshot membership — and reads no prose. The
`link-check` workflow reads external URLs and says so in its own first
comment. So the 7,000-odd wikilinks a reader actually clicks through had never
been checked by anything, and 25 of them resolved to nothing: citations of
three zero-byte task notes, dates without the title the filename carries, and
real files that live outside the `docs/` tree the resolver walks.

**Why here and not in the validator.** `tools/sync/MANIFEST.yaml` lists
`tools/scripts/` as `template`, so a check added to `validate-docs.py` would
be reported as divergence on the next upstream sync. Same reasoning that put
the `review_response` rule in `CLAUDE.md`. The rule is proposed upstream;
until then it is this repository's, and it runs where this repository's own
rules run.
"""
from __future__ import annotations

import collections
import pathlib
import re

from project_os_cockpit import wikilinks
from project_os_cockpit.index import Index

DOCS = pathlib.Path(__file__).resolve().parent.parent / "docs"

FENCE = re.compile(r"^\s*(?:```|~~~).*$")
WIKI = re.compile(r"\[\[([^\]]+)\]\]")
MD_LINK = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)\s]+?)(?:\s+\"[^\"]*\")?\)")
EXTERNAL = re.compile(r"^(?:https?:|mailto:|#|\{|<)")


def live_text(text: str) -> str:
    """The body, with frontmatter, fenced blocks and inline code removed.

    **Whole-document, never line by line.** An inline code span may wrap across
    a line break, and a per-line pass pairs the stray backticks either side of
    the break into a span that was never opened — which reported the correctly
    backticked ``[[X]]`` in `docs/references/COCKPIT-API.md` as a broken link.
    A guard that cries wolf on correct prose is one somebody deletes.

    Code is excluded because that is where syntax is *explained*:
    ``[[FEAT-...]]``, ``[[CHK-*]]``, ``![Alt](./image.png)``. Measured while
    writing this: 206 of the 232 raw matches in `docs/` are examples of the
    form, written correctly, and only 26 were live prose.
    """
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            nl = text.find("\n", end + 1)
            text = text[nl + 1:] if nl != -1 else ""
    kept, fenced = [], False
    for line in text.splitlines():
        if FENCE.match(line):
            fenced = not fenced
            continue
        if not fenced:
            kept.append(line)
    return re.sub(r"`{1,3}[^`]*?`{1,3}", " ", "\n".join(kept), flags=re.S)


def test_every_wikilink_in_the_record_resolves() -> None:
    """A `[[…]]` a reader can click reaches a note.

    An unresolved one is not silent: `wikilinks.py` renders it as
    `<span class="broken-wikilink">`, so this is a guard on something already
    visible on screen — which is how it was found, by Edwin reading the pages
    rather than by any check.
    """
    index = Index.build(DOCS)
    bad: dict[str, list[str]] = collections.defaultdict(list)
    for note in sorted(DOCS.rglob("*.md")):
        for raw in WIKI.findall(live_text(note.read_text(encoding="utf-8"))):
            target = raw.split("|")[0].strip()
            #: `project#ID` is another repository's note and resolves there,
            #: never here ([[FEAT-0093]]).
            if not target or wikilinks.split_cross_repo(target):
                continue
            if index.resolve(target.split("#")[0].strip()) is None:
                bad[target].append(str(note))
    assert not bad, "unresolved wikilinks:\n" + "\n".join(
        f"  {t!r} in {', '.join(sorted(set(w))[:3])}" for t, w in sorted(bad.items()))


def test_every_relative_link_in_the_record_points_at_a_file() -> None:
    """A `[label](path)` reaches something on disk.

    Zero were broken when this was written, and all seven the first scan
    reported were `![Alt](./image.png)`-style examples inside fenced blocks.
    The guard exists for the ones that will not be examples.
    """
    bad: list[str] = []
    for note in sorted(DOCS.rglob("*.md")):
        for _, target in MD_LINK.findall(live_text(note.read_text(encoding="utf-8"))):
            if EXTERNAL.match(target):
                continue
            path = target.split("#")[0]
            if not path:
                continue
            if not (note.parent / path).exists():
                bad.append(f"  {target!r} in {note}")
    assert not bad, "relative links pointing at nothing:\n" + "\n".join(bad)


def test_no_note_is_an_empty_file() -> None:
    """A zero-byte note is worse than a missing one.

    `TASK-0182`, `TASK-0183` and `TASK-0187` were committed as 0-byte files on
    21–22 July and stayed that way: the work shipped, the filenames existed, and
    the notes held nothing. So every citation of them dangled, and because they
    carry no frontmatter they were invisible to the snapshot, the navigator and
    every count — present enough to be linked, absent from everything that
    reads the record.
    """
    empty = [str(p) for p in sorted(DOCS.rglob("*.md")) if p.stat().st_size == 0]
    assert not empty, "zero-byte notes:\n" + "\n".join(f"  {p}" for p in empty)
