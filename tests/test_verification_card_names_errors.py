"""The Verification card names the notes it counts (acceptance check 1.11.1).

The card used to render `validator: 4 errors` and stop. That agrees with a
terminal run on the *number* and tells the reader nothing they can act on —
and the check asks for *same error count, **same notes named***.

The gap was invisible while the corpus was clean: zero on screen and zero in
the terminal reads as agreement. It surfaced only when the surface was driven
against a repo with real errors in it, which is why the check was ticked,
then **unticked**, then fixed.

**This is a static guard and its limits are the point.** The suite has no JS
runtime, so nothing here proves the rows render — the walked check does that.
What this catches is the specific regression: somebody simplifying the card
back to a count, which is exactly how it started. It asserts the code still
reads per-error fields and still bounds the list visibly.
"""

from __future__ import annotations

import re
from pathlib import Path

RENDERER = (
    Path(__file__).resolve().parents[1]
    / "desktop" / "src" / "renderer" / "renderer.ts"
)


def _fill_verification_health() -> str:
    """The body of `fillVerificationHealth`, to the next top-level function."""
    src = RENDERER.read_text(encoding="utf-8")
    start = src.index("async function fillVerificationHealth")
    rest = src[start:]
    end = rest.index("\nfunction ", 1)
    return rest[:end]


def test_the_card_reads_each_error_not_just_the_count() -> None:
    body = _fill_verification_health()
    assert "errorRows" in body, "the card must hold the errors, not only their length"
    for field in ("err.id", "err.rel", "err.message"):
        assert field in body, (
            f"{field} is what makes the row nameable; the payload has carried "
            "it since FEAT-0018, and dropping it returns the card to a bare count"
        )


def test_the_named_list_is_bounded_and_says_so() -> None:
    """A cap is fine; a silent cap is not.

    The project's own rule: if a surface bounds coverage, it must say what it
    dropped. A `+N more` that disappears is a list claiming to be complete.
    """
    src = RENDERER.read_text(encoding="utf-8")
    assert re.search(r"const VALIDATOR_NAMED_LIMIT = \d+;", src)
    body = _fill_verification_health()
    assert "VALIDATOR_NAMED_LIMIT" in body
    assert "more`" in body or "more'" in body, (
        "the overflow must be counted on screen, never dropped"
    )


def test_the_rows_are_removed_before_being_rebuilt() -> None:
    """The card refills on navigation; stale rows would accumulate.

    Cheap to get wrong and invisible until a reader sees the same error
    listed three times, which would be this surface asserting something
    false about its own subject.
    """
    body = _fill_verification_health()
    assert "querySelectorAll('.ctx-validator-row')" in body
    assert ".remove()" in body
