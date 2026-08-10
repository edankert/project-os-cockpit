"""TASK-0312 — the returning human's watermark.

DES-0008's two rules, and both are about what the watermark must *not* do:
it must not move itself, and it must not default to now.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from project_os_cockpit.watermark import EPOCH, Watermark

REPO = Path(__file__).resolve().parents[1]


def test_an_unset_watermark_reads_as_the_epoch(tmp_path: Path) -> None:
    """The first digest shows everything, honestly.

    Defaulting to *now* would report a quiet project because the install had
    no memory, not because nothing happened — the same lie in a different
    shape.
    """
    w = Watermark(tmp_path)
    assert w.seen_at == EPOCH
    assert w.is_set is False
    assert w.payload()["is_set"] is False


def test_only_catch_up_moves_it(tmp_path: Path) -> None:
    """Presence is not attention (DES-0008). A watermark that moves itself
    turns the digest into a slot machine."""
    w = Watermark(tmp_path)
    # Everything a reader does, short of the button.
    w.payload(); w.seen_at; w.is_set
    assert Watermark(tmp_path).is_set is False, "reading the watermark moved it"

    w.catch_up("2026-08-10T12:00:00Z")
    assert Watermark(tmp_path).seen_at == "2026-08-10T12:00:00Z"


def test_catch_up_takes_the_digest_timestamp_not_the_click(tmp_path: Path) -> None:
    """Otherwise anything landing while they read is silently marked seen."""
    w = Watermark(tmp_path)
    w.catch_up("2026-08-09T08:00:00Z")
    assert w.seen_at == "2026-08-09T08:00:00Z"


def test_it_survives_the_renderer_and_the_process(tmp_path: Path) -> None:
    """Server-side, per DES-0008: clearing the renderer's storage must not
    lose it."""
    Watermark(tmp_path).catch_up("2026-08-10T09:00:00Z")
    assert (tmp_path / ".cockpit" / "last-seen.json").is_file()
    assert Watermark(tmp_path).seen_at == "2026-08-10T09:00:00Z"


def test_a_corrupt_store_degrades_to_unset(tmp_path: Path) -> None:
    """Fails in the safe direction: unset means "show everything", so a
    truncated write loses the marker rather than hiding a backlog."""
    d = tmp_path / ".cockpit"
    d.mkdir(parents=True)
    (d / "last-seen.json").write_text('{"seen_at": "2026-0', encoding="utf-8")
    w = Watermark(tmp_path)
    assert w.seen_at == EPOCH and w.is_set is False


def test_catching_up_is_counted(tmp_path: Path) -> None:
    """ADR-0007's lesson: an instrument nobody reads is worth having only if
    someone will read it. The count is what would tell you whether the digest
    is used at all."""
    w = Watermark(tmp_path)
    w.catch_up("2026-08-10T10:00:00Z")
    w.catch_up("2026-08-10T11:00:00Z")
    assert json.loads((tmp_path / ".cockpit" / "last-seen.json").read_text())[
        "caught_up_count"
    ] == 2


def test_the_catch_up_endpoint_is_loopback_guarded() -> None:
    """It writes runtime state rather than docs/, and is guarded anyway: it
    records *this human's* attention, and a LAN peer marking someone else
    caught up would silently empty their digest."""
    src = (REPO / "src" / "project_os_cockpit" / "server.py").read_text(encoding="utf-8")
    m = re.search(r"\n        def _serve_caught_up\(", src)
    assert m, "the catch-up handler is missing"
    body = src[m.end():].split("\n        def ")[0]
    assert "_require_loopback" in body
