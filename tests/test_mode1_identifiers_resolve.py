"""Every name `cockpit.js` calls must be reachable at runtime (ISS-0138).

The browser front door loads exactly one script — `templates.py` emits
`<script src="/_static/cockpit.js">` and nothing else. So a function that
file calls and does not define is a `ReferenceError` on the first page that
hits it, with no second file to rescue it.

That is not hypothetical. `groupIsSettled` was called four times and defined
nowhere for as long as anyone had looked: both side panes rendered
`Nav failed: groupIsSettled is not defined` on **every** note. The 1137-test
suite was green throughout, because nothing here ever evaluated that file in
a JS runtime — `test_status_vocabulary` parses it for strings, which is a
different question.

The desktop renderer is immune to this specific shape because its
plain-script globals (`completed-work.js`, `cache-temperature.js`, …) are
separate `<script>` tags the shell markup lists. Mode 1 has no such
arrangement, so the guard belongs here.

Deliberately a *static* check rather than a headless browser: the failure
mode is a missing binding, which is visible without rendering anything, and
a browser dependency in this suite would buy coverage nobody would run.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

COCKPIT_JS = (
    Path(__file__).resolve().parents[1]
    / "src" / "project_os_cockpit" / "static" / "cockpit.js"
)

#: `function name(` — the only declaration form this file uses.
_DECL_RE = re.compile(r"\bfunction\s+([A-Za-z_$][\w$]*)\s*\(")
#: `var name =` / `const name =` / `let name =`
_ASSIGN_RE = re.compile(r"\b(?:var|const|let)\s+([A-Za-z_$][\w$]*)\s*=")
#: a bare `name(` call — not `.name(`, which is a property access.
_CALL_RE = re.compile(r"(?<![.\w$])([A-Za-z_$][\w$]*)\s*\(")

#: Names a browser supplies. Not a suppression list for our own code: every
#: entry is a global the page genuinely has, and adding one of our function
#: names here would defeat the test on purpose.
_BROWSER_GLOBALS = frozenset({
    "Array", "Boolean", "Date", "Error", "JSON", "Map", "Math", "Number",
    "Object", "Promise", "RegExp", "Set", "String", "Symbol", "WeakMap",
    "AbortController", "CustomEvent", "Event", "EventSource", "FormData",
    "Headers", "Intl", "MutationObserver", "Request", "Response", "URL",
    "URLSearchParams", "IntersectionObserver", "ResizeObserver", "Image",
    "DOMParser", "XMLHttpRequest", "WebSocket", "Blob", "File", "FileReader",
    "alert", "atob", "btoa", "clearInterval", "clearTimeout", "confirm",
    "decodeURI", "decodeURIComponent", "encodeURI", "encodeURIComponent",
    "fetch", "isFinite", "isNaN", "parseFloat", "parseInt", "prompt",
    "queueMicrotask", "requestAnimationFrame", "cancelAnimationFrame",
    "setInterval", "setTimeout", "structuredClone", "console", "document",
    "window", "location", "navigator", "history", "localStorage",
    "sessionStorage", "getComputedStyle", "matchMedia", "scrollTo",
    # Control-flow and operator keywords the call regex can catch when they
    # are followed by a parenthesis.
    "if", "for", "while", "switch", "catch", "return", "typeof", "function",
    "do", "else", "new", "delete", "void", "in", "of", "case", "throw",
    "await", "yield",
})


def _source() -> str:
    return COCKPIT_JS.read_text(encoding="utf-8")


def _defined_names(src: str) -> set[str]:
    return set(_DECL_RE.findall(src)) | set(_ASSIGN_RE.findall(src))


def _called_names(src: str) -> set[str]:
    # Strip block comments, then STRINGS, then line comments — in that order.
    #
    # The order is the whole subtlety and the first draft got it wrong.
    # Stripping `//…` first eats the rest of any line whose *string* contains
    # a `//` (a URL, a path), which leaves an unpaired quote; every later
    # quote then pairs off by one and prose starts reading as code. That
    # draft reported `drift`, `events` and `mismatch` as undefined functions
    # — all three are words inside message strings.
    stripped = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)
    stripped = re.sub(r'"(?:[^"\\\n]|\\.)*"', '""', stripped)
    stripped = re.sub(r"'(?:[^'\\\n]|\\.)*'", "''", stripped)
    stripped = re.sub(r"`(?:[^`\\]|\\.)*`", "``", stripped)
    stripped = re.sub(r"//[^\n]*", " ", stripped)
    return set(_CALL_RE.findall(stripped))


def test_cockpit_js_calls_nothing_it_cannot_resolve() -> None:
    """The regression guard for ISS-0138.

    Mode 1 ships as one file. Anything it calls is either defined in that
    file or supplied by the browser; there is no third source.
    """
    src = _source()
    unresolved = sorted(_called_names(src) - _defined_names(src) - _BROWSER_GLOBALS)
    assert not unresolved, (
        "cockpit.js calls "
        + ", ".join(unresolved)
        + " and nothing defines them. Mode 1 loads exactly one script, so this "
        "throws on the first page that reaches the call — which is how "
        "ISS-0138 made both side panes render an error box on every note."
    )


def test_group_is_settled_is_defined_here_not_borrowed() -> None:
    """The specific name ISS-0138 was about, asserted by name.

    The general test above would catch it. This one names it so a future
    reader of a failure knows which bug came back, and so deleting the
    function fails with its own history attached.
    """
    assert _DECL_RE.search(_source()) is not None
    assert "function groupIsSettled(" in _source(), (
        "groupIsSettled is called four times in cockpit.js. It is defined in "
        "the desktop renderer's completed-work.ts, which mode 1 never loads."
    )


@pytest.mark.parametrize("name", ["completionRank", "openFirst", "foldGroup", "groupIsSettled"])
def test_the_fold_twin_is_complete(name: str) -> None:
    """All four fold functions exist on both front doors.

    `cockpit.js` describes these as the twin of `completed-work.ts`. Its own
    comment said "the three functions below" while the desktop side had
    four — the drift was written down and still not seen. ADR-0021 proposes
    ending the twin; until then, this asserts the copy is whole.
    """
    desktop = (
        Path(__file__).resolve().parents[1]
        / "desktop" / "src" / "renderer" / "completed-work.ts"
    ).read_text(encoding="utf-8")
    # `function name(` here, `function name(` or `function name<T…>(` there:
    # two of the four are generic on the TypeScript side.
    decl = re.compile(rf"function\s+{re.escape(name)}\s*(?:<[^>]*>)?\s*\(")
    assert decl.search(_source()), f"{name} missing from cockpit.js"
    assert decl.search(desktop), f"{name} missing from completed-work.ts"
