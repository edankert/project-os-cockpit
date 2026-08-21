#!/usr/bin/env python3
"""The test declares the check it covers ([[FEAT-0138]] / [[TASK-0542]]).

**The dependency inverts.** `covered_by:` on the check was a *standing claim*
and it rots silently: rename, delete or `@Ignore` the covering test and the
note keeps asserting coverage while the check drops out of the run list
permanently, with no signal. That is worse than a stale verdict, because a
stale verdict still asks.

So the declaration moves **into the test**, where deleting the test deletes the
claim:

    def test_every_guarded_endpoint_refuses_a_remote_peer(...):
        # Covers: TST-0076

Findable by one grep:

    grep -rn "Covers: TST-" .

**Comment-and-grep, not an annotation.** `@Covers("TST-0076")` is the shape and
it is deliberately not v1: choosing an annotation first would make this depend
on shipping a library into two toolchains, and a v1 that needs one ships
nowhere. A comment works in pytest and in JVM today, with one comment prefix
per language and one regular expression for the whole thing.

**The declaration must sit INSIDE a test.** That is what makes the association
mechanical rather than guessed: the owning test is the nearest test
declaration at or above the marker. A marker outside a test names nothing that
can be observed running, and is refused rather than attributed to whatever
happens to be near it.

Usage:
    coverage-declarations.py --repo-root R --scan
    coverage-declarations.py --repo-root R --check
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

#: One comment prefix and one test-declaration pattern per language.
#: pytest and JVM are the two [[TASK-0542]] names; Swift is here because
#: `your-trainer` ships an iOS half and adding it is one row.
LANGUAGES: dict[str, tuple[str, "re.Pattern[str]"]] = {
    ".py": ("#", re.compile(r"^\s*(?:async\s+)?def\s+(test_\w+)\s*\(")),
    ".kt": ("//", re.compile(r"^\s*(?:internal\s+|private\s+|public\s+)?fun\s+`?([A-Za-z_][\w ]*)`?\s*\(")),
    ".java": ("//", re.compile(r"^\s*(?:public|private|protected)\s+void\s+(\w+)\s*\(")),
    ".swift": ("//", re.compile(r"^\s*func\s+(test\w*)\s*\(")),
}

#: The marker word followed by one or more check ids on one line. Anchored to
#: the word so a sentence mentioning coverage in prose is not a declaration.
#:
#: **This comment deliberately does not spell out an example.** `--check`
#: reports a declaration outside a test, and a comment in this file quoting
#: the convention IS one -- the tool reporting its own documentation. The
#: usage example lives in the module docstring, where the tokenizer correctly
#: sees a string rather than a comment.
DECLARATION = re.compile(r"\bCovers:\s*((?:TST-\d{3,5}\s*,?\s*)+)")
CHECK_ID = re.compile(r"TST-\d{3,5}")

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
    "python-runtime", ".gradle", ".idea", "site-packages",
}


class Declaration:
    """One `Covers:` marker: which check, which test, and where."""

    __slots__ = ("check", "test", "rel", "line")

    def __init__(self, check: str, test: str, rel: str, line: int) -> None:
        self.check, self.test, self.rel, self.line = check, test, rel, line

    def __repr__(self) -> str:                        # pragma: no cover
        return f"<{self.check} <- {self.test} ({self.rel}:{self.line})>"


def _python_structure(text: str) -> "tuple[set[int], list[tuple[int, str]]] | None":
    """Real comment lines and real test functions, for Python, exactly.

    **This exists because the first version read its own docstring.** The
    marker is a comment, so the first cut asked whether `#` appeared before it
    on the line -- and this file's usage example is a `#` comment *inside a
    string*, indented under a `def test_...` line that is also inside that
    string. The scanner reported two coverage claims for a test it had never
    seen, sourced from its own documentation.

    That is the guard-matching-its-own-comment failure this repo keeps paying
    for, so Python is handled by the tokenizer and the AST rather than by a
    substring: `tokenize` knows a comment from a string containing one, and
    `ast` knows a function from a line that looks like one.

    `None` when the file does not parse, and the caller falls back to the
    line-oriented heuristic -- a scanner that goes silent on a syntax error
    would hide every declaration in the file it is least sure about.
    """
    import ast
    import io
    import tokenize

    comments: set[int] = set()
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT:
                comments.add(tok.start[0])
        tree = ast.parse(text)
    except (SyntaxError, tokenize.TokenError, ValueError, IndentationError):
        return None
    tests: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test_"):
                tests.append((node.lineno, node.name))
    tests.sort()
    return comments, tests


def scan_text(text: str, suffix: str, rel: str) -> list[Declaration]:
    """Declarations in one source file, each attributed to its owning test.

    The owning test is the nearest test declaration **at or above** the
    marker, which is what makes the association mechanical: the marker sits
    inside the test, so the test above it is the one that runs it.
    """
    prefix, test_re = LANGUAGES[suffix]
    exact = _python_structure(text) if suffix == ".py" else None
    out: list[Declaration] = []
    current = ""
    for lineno, line in enumerate(text.splitlines(), 1):
        if exact is None:
            hit = test_re.match(line)
            if hit:
                current = next(g for g in hit.groups() if g)
        found = DECLARATION.search(line)
        if not found:
            continue
        if exact is None:
            #: **A declaration is a COMMENT.** Without this every string
            #: literal describing the convention reads as a coverage claim.
            #: Approximate for the languages with no parser here; Python gets
            #: the exact answer above.
            if prefix not in line[:found.start()]:
                continue
        else:
            comments, tests = exact
            if lineno not in comments:
                continue
            owning = [name for line_no, name in tests if line_no <= lineno]
            current = owning[-1] if owning else ""
        for check in CHECK_ID.findall(found.group(1)):
            out.append(Declaration(check, current, rel, lineno))
    return out


def scan(root: Path) -> list[Declaration]:
    out: list[Declaration] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in LANGUAGES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):         # pragma: no cover
            continue
        if "Covers:" not in text:
            continue
        out.extend(scan_text(text, path.suffix,
                             path.relative_to(root).as_posix()))
    return out


def acceptance_checks(root: Path) -> set[str]:
    """Every `level: acceptance` note id in `docs/`.

    Frontmatter read line-wise rather than through PyYAML: this runs in the
    same places the validator does and must not add a dependency to do it.
    """
    out: set[str] = set()
    docs = root / "docs"
    for path in docs.rglob("*.md") if docs.is_dir() else []:
        if "__templates__" in path.as_posix():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):         # pragma: no cover
            continue
        if not text.startswith("---"):
            continue
        head = text.split("---", 2)[1] if text.count("---") >= 2 else ""
        if not re.search(r"^level:\s*[\"']?acceptance", head, re.M):
            continue
        hit = re.search(r"^id:\s*(\S+)", head, re.M)
        if hit:
            out.add(hit.group(1).strip().strip('"').strip("'"))
    return out


def problems(root: Path) -> list[str]:
    """Everything `--check` refuses, as sentences.

    Two rules, and both are about a declaration that cannot be OBSERVED:

    * one naming a check that does not exist, or is not an acceptance check --
      the emitter would append an entry for it and the gate would read a
      verdict about nothing;
    * one that is not inside a test -- nothing runs it, so nothing can ever
      emit or stop emitting for it, which is the whole mechanism.
    """
    known = acceptance_checks(root)
    out: list[str] = []
    for decl in scan(root):
        where = "%s:%d" % (decl.rel, decl.line)
        if not decl.test:
            out.append(
                "%s declares %s outside any test; the declaration must sit "
                "inside the test that covers it, because a marker nothing "
                "runs can never stop emitting" % (where, decl.check))
            continue
        if decl.check not in known:
            out.append(
                "%s declares %s, which is not an acceptance check in this "
                "repo; coverage of a check that does not exist is a verdict "
                "about nothing" % (where, decl.check))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    root = Path(args.repo_root).resolve()

    if args.scan or not args.check:
        for decl in scan(root):
            print("%s\t%s\t%s:%d" % (decl.check, decl.test, decl.rel, decl.line))
    if args.check:
        found = problems(root)
        for line in found:
            print("ERROR [COVERAGE-DECLARATION] %s" % line, file=sys.stderr)
        if found:
            return 1
        print("coverage-declarations: OK (%s)" % root)
    return 0


if __name__ == "__main__":                            # pragma: no cover
    raise SystemExit(main())
