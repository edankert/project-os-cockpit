"""Every source file parses under the oldest Python this project claims (ISS-0256).

A syntax error is the one defect class that is *invisible* to every check
running on a newer interpreter. `tools/scripts/migrate-acceptance-checks.py`
used a backslash inside an f-string expression — legal from 3.12 (PEP 701),
a `SyntaxError` on the 3.11 this project's `requires-python` promises. It sat
green here for 13 days on 3.13, passed `validate-docs`, and passed
`validate-docs.sh --as-committed`, which materialises `HEAD` and so catches
untracked and ignored files but still runs the local interpreter.

So the check has two halves, and which one runs depends on the interpreter:

**On the floor interpreter (< 3.12) — `compile()` every file.** Authoritative
and exhaustive: it is the real grammar, and it catches every syntax defect
rather than the two this module can name. This is the half CI runs.

**Above it (>= 3.12) — scan for the constructs PEP 701 relaxed**, which are
the ones that compile here and cannot compile there: a backslash anywhere
inside an f-string expression, and a string inside an f-string expression
quoted with an enclosing f-string's quote character. Narrower by necessity —
without a floor interpreter there is nothing to ask — but it moves discovery
from a push to a local run.

*(The first version of this module had only the second half, and reached for
`tokenize.FSTRING_START`, which **3.12 added**. So a guard written to protect
3.11 raised `AttributeError` on 3.11 — the same mistake it exists to catch,
one layer up. Found by CI, which is the point.)*

The module retires itself once `requires-python` reaches 3.12: both constructs
become legal everywhere the project runs, and a check that cannot fail is
worse than no check.
"""

from __future__ import annotations

import io
import re
import sys
import tokenize
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

SKIP = (".venv", "node_modules", "python-runtime", "__pycache__", "tools/cockpit/")

OFFENDER = REPO / "tests" / "fixtures" / "pep701_offender.py.txt"

#: 3.12 both relaxed the f-string grammar (PEP 701) and added the tokens that
#: let us see inside one. They arrived together, which is why the scan is
#: available only where it is not authoritative.
CAN_SCAN = sys.version_info >= (3, 12)


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
    """If this fails the project has moved to 3.12+ and this module is dead
    weight — delete it rather than leaving a check that cannot fail."""
    assert _floor() < (3, 12), (
        "requires-python has reached 3.12; PEP 701 makes both constructs legal "
        "everywhere this project runs, so this module should be deleted"
    )


def test_the_guard_fires_on_a_known_offender() -> None:
    """The construct from ISS-0256, kept verbatim, put through whichever half
    of the check this interpreter can run. Neither half is trusted unseen."""
    source = OFFENDER.read_text(encoding="utf-8")
    if not CAN_SCAN:
        with pytest.raises(SyntaxError):
            compile(source, str(OFFENDER), "exec")
        return
    hits = pre_701_violations(OFFENDER)
    assert hits, f"the detector missed the very line it exists for ({OFFENDER})"
    assert all("backslash" in why for _, why in hits)


@pytest.mark.skipif(CAN_SCAN, reason="not the floor interpreter — the scan covers it instead")
def test_every_source_file_compiles_under_the_floor() -> None:
    """The authoritative half: the real grammar, every file, every construct.
    Runs where it matters, because CI pins the floor."""
    failures = []
    for path in _sources():
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except SyntaxError as exc:
            failures.append(f"{path.relative_to(REPO)}:{exc.lineno}  {exc.msg}")
    assert not failures, (
        "these do not parse on the Python this project claims to support, so "
        "they fail before they run:\n  " + "\n  ".join(failures)
    )


@pytest.mark.skipif(not CAN_SCAN, reason="the compile check is authoritative here")
def test_no_source_file_needs_a_python_newer_than_the_floor() -> None:
    """The narrow half, for interpreters too new to answer the real question."""
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
