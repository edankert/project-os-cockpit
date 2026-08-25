"""Every source file parses under the oldest Python this project claims (ISS-0256).

A syntax error is the one defect class that is *invisible* to every check
running on a newer interpreter. `tools/scripts/migrate-acceptance-checks.py`
used a backslash inside an f-string expression — legal from 3.12 (PEP 701),
a `SyntaxError` on the 3.11 this project's `requires-python` promises. It sat
green here for 13 days on 3.13, passed `validate-docs`, and passed
`validate-docs.sh --as-committed`, which materialises `HEAD` and so catches
untracked and ignored files but still runs the local interpreter.

The honest check would be "compile every file under the floor interpreter",
and that is what CI does by pinning `3.11`. This runs on whatever is
installed, so it checks the two constructs PEP 701 *relaxed* — the ones that
compile here and cannot compile there:

  1. a backslash anywhere inside an f-string expression, and
  2. a string inside an f-string expression quoted with an enclosing
     f-string's quote character.

It is deliberately not a general 3.11 grammar check; it cannot be one without
a 3.11 interpreter. It covers the gap that actually bit.

The scan retires itself once `requires-python` reaches 3.12 — at that point
both constructs are legal everywhere the project runs, and a check that can
no longer fail is worse than no check.
"""

from __future__ import annotations

import io
import re
import tokenize
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

SKIP = (".venv", "node_modules", "python-runtime", "__pycache__", "tools/cockpit/")


def _floor() -> tuple[int, int]:
    """The oldest Python `pyproject.toml` promises to support."""
    text = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'requires-python\s*=\s*"[^0-9]*(\d+)\.(\d+)', text)
    assert match, "pyproject.toml has no parseable requires-python"
    return int(match.group(1)), int(match.group(2))


def _sources() -> list[Path]:
    return [
        p for p in sorted(REPO.rglob("*.py"))
        if not any(s in str(p.relative_to(REPO)) for s in SKIP)
    ]


def pre_701_violations(path: Path) -> list[tuple[int, str]]:
    """f-string constructs that Python 3.11 rejects and 3.12 accepts.

    Exposed rather than inlined so the guard can be exercised against a known
    offender — a detector nothing has ever seen fire is an assumption.
    """
    found: list[tuple[int, str]] = []
    source = path.read_text(encoding="utf-8")
    tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    quotes: list[str] = []
    for tok in tokens:
        if tok.type == tokenize.FSTRING_START:
            quotes.append(tok.string[-1])
            continue
        if tok.type == tokenize.FSTRING_END:
            if quotes:
                quotes.pop()
            continue
        if not quotes:
            continue
        # A MIDDLE is the innermost f-string's own literal text. It only sits
        # inside an *expression* when another f-string encloses it — which is
        # exactly the nested case that bit, so the depth test is load-bearing.
        if tok.type == tokenize.FSTRING_MIDDLE and len(quotes) < 2:
            continue
        if "\\" in tok.string:
            found.append((tok.start[0], f"backslash in an f-string expression: {tok.string!r}"))
        elif tok.type == tokenize.STRING and tok.string.lstrip("rbfRBF")[:1] in quotes:
            found.append((tok.start[0], f"reuses an enclosing f-string quote: {tok.string!r}"))
    return found


def test_the_floor_is_below_the_pep_701_relaxation() -> None:
    """If this fails the project has moved to 3.12+ and the scan below is
    dead weight — delete it rather than leaving a check that cannot fail."""
    assert _floor() < (3, 12), (
        "requires-python has reached 3.12; PEP 701 makes both constructs legal "
        "everywhere this project runs, so this module should be deleted"
    )


def test_the_scan_sees_a_known_offender() -> None:
    """The detector, run against the construct that caused ISS-0256. Written
    the obvious way first, this returned nothing — it skipped the nested
    literal where the backslash actually lives."""
    offender = REPO / "tests" / "fixtures" / "pep701_offender.py.txt"
    hits = pre_701_violations(offender)
    assert hits, f"the detector missed the very line it exists for ({offender})"
    assert all("backslash" in why for _, why in hits)


def test_no_source_file_needs_a_python_newer_than_the_floor() -> None:
    violations = [
        f"{p.relative_to(REPO)}:{line}  {why}"
        for p in _sources()
        for line, why in pre_701_violations(p)
    ]
    assert not violations, (
        "these compile on this machine and are a SyntaxError on the Python CI "
        "pins — the file will not parse at all, so it fails before it runs:\n  "
        + "\n  ".join(violations)
    )
