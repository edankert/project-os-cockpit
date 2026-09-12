"""FEAT-0147 / REQ-0063 — a picture lives beside the note that shows it.

`__attachments__/` beside the note is the written convention
(`tools/instructions/OBSIDIAN.md`), and a relative path is how a note names a
picture in it. Both forms have to work, because two different authors produce
them: an agent writes `![](__attachments__/plate-3.png)`, and a person who
pastes an image into Obsidian gets `![[plate-3.png]]` — a bare filename
Obsidian resolves across the whole vault.

The resolver was written before any of that was stated, and the order it
already had turned out to be the right one. These tests pin it, so the last
resort stays last: a fleet-wide filename search that quietly picks the wrong
`plate-3.png` is the failure this ordering exists to make rare.

Built with `Index.build`, never `Index(docs)`: the constructor indexes notes
and nothing else, so the filename search sees no pictures and every lookup
that depends on it answers `None`. Two tests here passed against the
constructor anyway, because they resolve one step earlier.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from project_os_cockpit.index import ATTACHMENT_DIR_NAMES, Index

PNG = bytes.fromhex("89504e470d0a1a0a")  # enough to be a file with a suffix


def _docs(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    (docs / "designs").mkdir(parents=True)
    return docs


def _note(docs: Path, rel: str, body: str = "") -> Path:
    path = docs / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('---\ntype: "[[design]]"\nid: DES-0001\n---\n\n' + body, encoding="utf-8")
    return path


def _png(docs: Path, rel: str) -> Path:
    path = docs / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(PNG)
    return path


def test_attachments_is_the_first_directory_tried() -> None:
    """The tuple's order is the convention, not an accident. `__attachments__`
    leads because it is the name written down, and because a
    double-underscore directory is one the system owns, like `__templates__`."""
    assert ATTACHMENT_DIR_NAMES[0] == "__attachments__"
    assert set(ATTACHMENT_DIR_NAMES) >= {"attachments", "images"}, (
        "the older spellings are read, not written: a vault configured years "
        "ago says `attachments`, and its notes must not break"
    )


def test_a_picture_in_attachments_resolves_by_relative_path(tmp_path: Path) -> None:
    """The stated convention, and the only form that renders in Obsidian, in
    the cockpit and on GitHub alike."""
    docs = _docs(tmp_path)
    note = _note(docs, "designs/DES-0001-Recovery.md", "![a plate](__attachments__/plate-3.png)")
    _png(docs, "designs/__attachments__/plate-3.png")
    idx = Index.build(docs)
    assert idx.resolve_asset("__attachments__/plate-3.png", note) == (
        "/docs/designs/__attachments__/plate-3.png")


def test_an_obsidian_embed_resolves_by_bare_filename(tmp_path: Path) -> None:
    """What a person gets by pasting an image into a note. It carries no path
    at all, so it can only be found by the fleet-wide search — which is why
    that search stays."""
    docs = _docs(tmp_path)
    note = _note(docs, "designs/DES-0001-Recovery.md", "![[plate-3.png]]")
    _png(docs, "designs/__attachments__/plate-3.png")
    idx = Index.build(docs)
    assert idx.resolve_asset("plate-3.png", note) == (
        "/docs/designs/__attachments__/plate-3.png")


def test_the_nearer_picture_wins_when_two_share_a_name(tmp_path: Path) -> None:
    """Two `plate-3.png` in one repo is a coin toss the resolver has to call.
    It calls it by proximity to the note that asked, which is a heuristic and
    not a rule — the reason the relative path is the convention."""
    docs = _docs(tmp_path)
    near = _note(docs, "designs/DES-0001-Recovery.md", "![[plate-3.png]]")
    _png(docs, "designs/__attachments__/plate-3.png")
    _png(docs, "features/somewhere-else/__attachments__/plate-3.png")
    idx = Index.build(docs)
    assert idx.resolve_asset("plate-3.png", near) == (
        "/docs/designs/__attachments__/plate-3.png")

    far = _note(docs, "features/somewhere-else/FEAT-0001-Thing.md", "![[plate-3.png]]")
    assert idx.resolve_asset("plate-3.png", far) == (
        "/docs/features/somewhere-else/__attachments__/plate-3.png")


def test_the_fleet_wide_search_prefers_the_nearer_of_two_matches(tmp_path: Path) -> None:
    """The last resort, exercised where it actually runs: neither picture sits
    beside the note or in its `__attachments__`, so the filename search is all
    there is, and it is scored by shared path prefix.

    The obvious version of this test does not reach here — give each note a
    picture in its own `__attachments__` and both resolve one step earlier,
    leaving the scoring untested. Found by mutation: dropping the score left
    that version green.
    """
    docs = _docs(tmp_path)
    note = _note(docs, "features/widgets/plan/TASK-0001-Thing.md", "![[plate-3.png]]")
    _png(docs, "features/widgets/pics/plate-3.png")
    _png(docs, "zebra/pics/plate-3.png")
    idx = Index.build(docs)
    assert idx.resolve_asset("plate-3.png", note) == "/docs/features/widgets/pics/plate-3.png", (
        "the search ignored which note asked; alphabetical order would answer "
        "features/... here by luck, so the far note below is the real assertion"
    )
    far = _note(docs, "zebra/ZEB-0001-Other.md", "![[plate-3.png]]")
    assert idx.resolve_asset("plate-3.png", far) == "/docs/zebra/pics/plate-3.png"


def test_a_path_beside_the_note_beats_an_attachment_directory(tmp_path: Path) -> None:
    """An explicit relative path is an instruction, not a hint. A note that
    names `plate-3.png` beside itself means that file, even when a file of the
    same name sits in `__attachments__/`."""
    docs = _docs(tmp_path)
    note = _note(docs, "designs/DES-0001-Recovery.md", "![](plate-3.png)")
    _png(docs, "designs/plate-3.png")
    _png(docs, "designs/__attachments__/plate-3.png")
    idx = Index.build(docs)
    assert idx.resolve_asset("plate-3.png", note) == "/docs/designs/plate-3.png"


@pytest.mark.parametrize("target", ["notes.md", "../../etc/passwd", "https://example.com/x.png"])
def test_only_images_inside_the_docs_root_resolve(tmp_path: Path, target: str) -> None:
    """The resolver answers for pictures and for this repo only. A Markdown
    file, a path climbing out, and an external URL each get nothing — the
    third because it is already a URL and needs no resolving."""
    docs = _docs(tmp_path)
    note = _note(docs, "designs/DES-0001-Recovery.md")
    _png(docs, "designs/__attachments__/plate-3.png")
    assert Index.build(docs).resolve_asset(target, note) is None


# ---- HTML in a note (ADR-0043) -------------------------------------------
#
# There is no marker: HTML written plainly in a note renders, in Obsidian and
# in the cockpit alike, and a fenced block stays source. These pin both halves,
# because the decision rests on the claim that the two renderers already agree.


def test_html_written_plainly_in_a_note_renders(tmp_path: Path) -> None:
    """The notation, such as it is. Obsidian renders raw HTML natively and so
    does this renderer; ADR-0043 chose no marker on the strength of that."""
    from project_os_cockpit.renderer import render_markdown_text

    html = render_markdown_text(
        'Prose.\n\n<div class="mock"><span>a card</span></div>\n',
        source_path=Path("docs/designs/DES-0001-Thing.md"),
    )
    assert '<div class="mock">' in html and "<span>a card</span>" in html
    assert "&lt;div" not in html, "the markup was escaped; a note can no longer show a mockup"


def test_a_fenced_block_stays_source(tmp_path: Path) -> None:
    """The other half, and the reason the language slot was not overloaded:
    a note documenting HTML must show it, not run it. This repo's own notes
    contain HTML examples written exactly this way."""
    from project_os_cockpit.renderer import render_markdown_text

    html = render_markdown_text(
        '```html\n<div class="mock">x</div>\n```\n',
        source_path=Path("docs/designs/DES-0001-Thing.md"),
    )
    assert "&lt;" in html, "a fenced html block was rendered live instead of shown as source"
    assert '<div class="mock">x</div>' not in html


def test_the_desktop_reader_inserts_the_sidecar_html_unaltered() -> None:
    """The cockpit half of the same claim. The shell writes the sidecar's HTML
    into the document, so whatever the sidecar renders is what a reader sees —
    there is no second sanitiser that would silently strip a note's markup.

    Scripts are a separate matter and are blocked by the page's CSP, which is
    what makes passing the markup through safe to do at all.
    """
    renderer = (Path(__file__).resolve().parent.parent
                / "desktop" / "src" / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    assert "docView.innerHTML = (data.metadata_html || '') + data.html;" in renderer
    index_html = (Path(__file__).resolve().parent.parent
                  / "desktop" / "src" / "renderer" / "index.html").read_text(encoding="utf-8")
    assert "script-src 'self'" in index_html, (
        "the CSP no longer blocks inline scripts, and a note's raw HTML is "
        "passed through untouched -- ADR-0043 rests on that pair"
    )
