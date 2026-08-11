"""One voice for every empty state (FEAT-0073 / TASK-0318).

An empty pane is the most common state a new reader meets and the least
informative one the cockpit produced. Measured before this task:

    '(no items)'        a phase with nothing in it
    '(no children)'     a phase nothing names
    'All clear.'        the review queue with nothing owed

None of those says *what the pane shows*, so none tells the reader whether
they are looking at a working surface with nothing in it or a broken one. The
register got it right and nothing else copied it:

    'No design notes yet. A design is a note with type: [[design]].'

**The pattern**: say what the pane shows, then the shortest path to having
some. Both halves, in one sentence.

This is a sweep over the literals rather than a rule applied at one call site,
because there is no shared empty-state helper to hang a rule on — the panes
each build their own element. A sweep is what covers a pane written next week.
"""

from __future__ import annotations

import re
from pathlib import Path

RENDERER = (
    Path(__file__).resolve().parent.parent
    / "desktop" / "src" / "renderer" / "renderer.ts"
)

#: Phrases that name nothing. Each was in the file before TASK-0318.
CONTENTLESS = ("(no items)", "(no children)", "All clear.", "None.", "Empty.")

#: Empty states that deliberately do not offer a path, with the reason.
#: Kept as data so an exception is a decision someone wrote down rather than a
#: string that quietly failed to match the pattern.
EXCEPTIONS: dict[str, str] = {
    "Empty — nothing to triage.": (
        "An empty inbox is the SUCCESS condition (LIFECYCLE.md: 'its success "
        "condition is being empty'). Offering the shortest path to having some "
        "would be instructions for making work for yourself."
    ),
    "+ to add": (
        "The workspace rail is a column of ~40px squares; a sentence cannot "
        "render in it. The pattern is split across two carriers — the visible "
        "label is the path, and the `title` says what the rail shows: "
        "'No workspaces yet — + adds a repo with a SNAPSHOT.yaml.'"
    ),
    "No longer in the inbox — it has been filed or discarded.": (
        "Not an empty pane — it reports what happened to one item. The path is "
        "the thing that already occurred."
    ),
}


def _empty_state_literals() -> list[tuple[int, str]]:
    """Every `textContent` assigned next to an `*empty*` className."""
    lines = RENDERER.read_text(encoding="utf-8").split("\n")
    out: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        if not re.search(r"className = '[^']*empty", line):
            continue
        for j in range(i, min(i + 5, len(lines))):
            m = re.search(r"textContent\s*=\s*'((?:[^'\\]|\\.)*)'\s*;", lines[j])
            if m:
                # Decode only `\uXXXX` escapes. `unicode_escape` over the whole
                # string would re-decode real UTF-8 em dashes as latin-1 and
                # turn them into mojibake — which it did, and the EXCEPTIONS
                # check caught it by failing to match a live literal.
                text = re.sub(
                    r"\\u([0-9a-fA-F]{4})",
                    lambda mm: chr(int(mm.group(1), 16)),
                    m.group(1),
                )
                out.append((j + 1, text))
                break
    return out


def test_the_sweep_reaches_the_empty_states() -> None:
    """A sweep that swept nothing would pass for the wrong reason."""
    found = _empty_state_literals()
    assert len(found) >= 8, f"only {len(found)} empty-state literals found: {found}"


def test_no_empty_state_says_nothing() -> None:
    """The three that named nothing, and anything that joins them."""
    bad = [
        f"line {n}: {text!r}"
        for n, text in _empty_state_literals()
        if text.strip() in CONTENTLESS
    ]
    assert not bad, (
        "empty states that do not say what the pane shows:\n  " + "\n  ".join(bad)
    )


def test_every_empty_state_says_what_and_how() -> None:
    """What the pane shows, then the shortest path to having some.

    The path is detected by the punctuation the pattern uses — an em dash or a
    second sentence — rather than by matching prose, so a differently-worded
    but complete message passes and a bare noun phrase does not.
    """
    thin: list[str] = []
    for n, text in _empty_state_literals():
        body = text.strip()
        if body in EXCEPTIONS:
            continue
        has_path = "—" in body or re.search(r"\.\s+\S", body)
        if not has_path or len(body) < 25:
            thin.append(f"line {n}: {body!r}")
    assert not thin, (
        "empty states naming what is absent but not how to have some:\n  "
        + "\n  ".join(thin)
        + "\n\nPattern: '<what this pane shows> — <shortest path to having some>.'"
        "\nIf a path is genuinely wrong here, add it to EXCEPTIONS with the reason."
    )


def test_every_exception_is_still_used() -> None:
    """An exception for a string nobody renders is a stale licence.

    Without this, EXCEPTIONS only ever grows: a message gets reworded, its
    entry stops matching, and the entry survives as permission for a string
    that no longer exists.
    """
    live = {text.strip() for _, text in _empty_state_literals()}
    stale = [text for text in EXCEPTIONS if text not in live]
    assert not stale, f"EXCEPTIONS entries no longer rendered anywhere: {stale}"
