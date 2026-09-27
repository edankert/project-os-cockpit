"""No live name says walk, sitting or survey ([[TASK-0639]], FEAT-0155).

The walk became the release test on 2026-09-27 (project-os-dev ADR-0050): a
sitting is a section, the survey is what changed, a verdict is a result. This
searches the cockpit's code for the old words **in code**: identifiers,
string literals, CSS classes and the HTML. Comments and docstrings are left
alone, because they record why the code is the way it is, and that history
used the old words.

Two places keep the old words on purpose, and only they are allowed: the
redirect that opens `~walk` addresses as the release test, and the table that
moves the walk page's browser storage to its new keys.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sorted(p for p in (ROOT / "src" / "project_os_cockpit").glob("*.py")
            if not p.name.endswith("_bundled.py"))
WEB = sorted([*(ROOT / "desktop" / "src" / "renderer").glob("*.ts"),
              *(ROOT / "desktop" / "src" / "renderer").glob("*.css"),
              *(ROOT / "desktop" / "src" / "renderer").glob("*.html")])

OLD = re.compile(r"walk|sitting|survey", re.I)

#: Where an old word stays, as `(file name, text that must be on the line)`.
ALLOWED = [
    #: The redirect: `~walk` and `~walk/<platform>` open the release test.
    ("renderer.ts", "normalised === '~walk'"),
    ("release-test.ts", "~walk"),
    #: The storage migration table and the step results it carries over.
    ("release-test.ts", "'walk-"),
    ("release-test.ts", "release-test-walk-steps"),
    ("release-test.ts", "rtCarryWalkMarks"),
    ("release-test.ts", "old: Record<string, { verdict?: string; reason?: string }>"),
    ("release-test.ts", "sitting"),
    #: The validator code for an old name has to say what the old name was.
    ("validation-rows.ts", "'OLD-NAME'"),
    #: The DOM's own name for walking a tree.
    ("renderer.ts", "createTreeWalker"),
    ("renderer.ts", "walker.nextNode"),
]


#: "Walk" as ordinary English: a pass over a tree or a corpus (REQ-0037
#: keeps it). Named one by one, so a new use of the word has to be looked at.
ALLOWED_PY = {
    ("cli.py", "_walk_up_for_discovery"),
    ("index.py", "_walk_markdown"),
    ("index.py", "_walk_assets"),
    ("obligations.py", "_walk"),
    ("command_targets.py", "walk"),
}


def _allowed(path: Path, line: str) -> bool:
    return any(path.name == name and needle in line for name, needle in ALLOWED)


def _python_hits(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(
                    getattr(body[0], "value", None), ast.Constant):
                docstrings.add(id(body[0].value))
    hits = []
    for node in ast.walk(tree):
        words: list[str] = []
        if isinstance(node, ast.Constant) and isinstance(node.value, str) \
                and id(node) not in docstrings:
            words.append(node.value)
        elif isinstance(node, ast.Name):
            words.append(node.id)
        elif isinstance(node, ast.Attribute):
            words.append(node.attr)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            words.append(node.name)
        elif isinstance(node, ast.arg):
            words.append(node.arg)
        for word in words:
            if OLD.search(word) and (path.name, word) not in ALLOWED_PY:
                hits.append(f"{path.name}:{getattr(node, 'lineno', '?')}: {word[:80]!r}")
    return hits


def _web_hits(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    #: Comments out, line numbers kept.
    text = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    text = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    hits = []
    for number, line in enumerate(text.splitlines(), start=1):
        code = re.sub(r"(^|[^:'\"`])//.*$", r"\1", line) if path.suffix == ".ts" else line
        if OLD.search(code) and not _allowed(path, code):
            hits.append(f"{path.name}:{number}: {code.strip()[:100]}")
    return hits


def test_no_code_in_the_cockpit_says_walk_sitting_or_survey() -> None:
    hits = [hit for path in PY for hit in _python_hits(path)]
    hits += [hit for path in WEB for hit in _web_hits(path)]
    assert not hits, (
        "the old names are live again; the release test says release test, "
        "section, what changed and result (project-os-dev ADR-0050):\n"
        + "\n".join(hits[:60]) + (f"\n... and {len(hits) - 60} more" if len(hits) > 60 else ""))
