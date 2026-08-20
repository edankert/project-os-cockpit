"""The resolver exists twice, so the two copies are asserted to agree.

`validate_docs_bundled.py` is stdlib-only and self-contained because it is
copied whole into every downstream repo; it cannot import the package. So
`command_targets.resolve` and `validate-docs.py::resolve_command` are the same
logic written twice, which is a standing invitation to drift.

The repo has paid for this shape before. `acceptance.normalise_mark` was fixed
for a leading-space typo and `validate-docs.py::_acceptance_is_settled` was not
— and the validator is the copy that gates pre-commit and CI, so the fix landed
everywhere except where it mattered. That guard loads both copies from disk and
asserts the behaviour; this one does the same.

**Both copies are loaded from disk**, including `tools/scripts/validate-docs.py`,
because it is a third file and byte-identity with the bundled one is maintained
by hand.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from project_os_cockpit import command_targets as ct

REPO_ROOT = Path(__file__).resolve().parent.parent
COPIES = (
    REPO_ROOT / "tools" / "scripts" / "validate-docs.py",
    REPO_ROOT / "src" / "project_os_cockpit" / "validate_docs_bundled.py",
)

#: Every shape the resolver distinguishes, including the two that are only
#: reachable on constructed input because the corpus holds neither.
CASES = (
    "pytest tests/present.py -q",
    "pytest tests/present.py::test_x -q",
    "pytest tests/absent.py -q",
    "pytest tests/present.py tests/absent.py -q",
    "cd android && ./gradlew :app:testDebugUnitTest --tests com.x.PresentTest",
    "cd android && ./gradlew :app:testDebugUnitTest --tests com.x.AbsentTest",
    "./gradlew :app:connectedDebugAndroidTest "
    "-Pandroid.testInstrumentationRunnerArguments.class=com.x.PresentTest",
    "make check",
    "./gradlew test --rerun-tasks",
    'pytest "tests/present.py -q',
    "",
)


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(f"v_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "present.py").write_text("x = 1\n", encoding="utf-8")
    src = tmp_path / "android" / "app" / "src" / "test" / "kotlin" / "com" / "x"
    src.mkdir(parents=True)
    (src / "PresentTest.kt").write_text("class PresentTest\n", encoding="utf-8")
    return tmp_path


@pytest.mark.parametrize("copy", COPIES, ids=lambda p: p.name)
def test_the_copies_agree_on_every_shape(copy: Path, repo: Path) -> None:
    module = _load(copy)
    for command in CASES:
        assert module.resolve_command(command, repo) == ct.resolve(command, repo), (
            f"{copy.name} disagrees with command_targets on {command!r}")


@pytest.mark.parametrize("copy", COPIES, ids=lambda p: p.name)
def test_the_copies_agree_across_the_real_corpus(copy: Path) -> None:
    """Constructed cases prove the shapes; the corpus proves the population."""
    module = _load(copy)
    import re
    seen = 0
    for path in sorted((REPO_ROOT / "docs").rglob("TST-*.md")):
        if "__templates__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        fm = text[4:text.find("\n---", 3)]
        m = re.search(r"^command:\s*(.*)$", fm, re.M)
        command = m.group(1).strip().strip('"') if m else ""
        if not command:
            continue
        seen += 1
        assert module.resolve_command(command, REPO_ROOT) == ct.resolve(command, REPO_ROOT), (
            f"{copy.name} disagrees on {path.name}")
    assert seen >= 30, f"only {seen} automated notes reached — guard is thinning"


@pytest.mark.parametrize("copy", COPIES, ids=lambda p: p.name)
def test_the_pattern_SETS_agree_not_just_the_answers(copy: Path) -> None:
    """**The cases prove the shapes; this proves the vocabulary.**

    Independent review, 2026-08-20: dropping `swift` from `_CMD_SOURCE_PATH` in
    BOTH validator copies, while leaving `command_targets._SOURCE_PATH` alone,
    passed every case above — because no case names a `.swift` file. Five of
    the six extensions the resolver recognises are unexercised by the
    constructed set and by the corpus, which has no iOS command at all.

    Comparing the pattern sets directly closes that: an extension can be added
    or removed on one side and the pair goes red, whether or not any test
    happens to name a file of that kind.
    """
    module = _load(copy)
    assert module._CMD_SOURCE_PATH.pattern == ct._SOURCE_PATH.pattern
    assert module._CMD_JVM_CLASS.pattern == ct._JVM_CLASS.pattern
    assert tuple(module._CMD_JVM_SUFFIXES) == tuple(ct._JVM_SUFFIXES)
    assert (module.CMD_RESOLVES, module.CMD_BROKEN, module.CMD_UNCHECKABLE) == (
        ct.RESOLVES, ct.BROKEN, ct.UNCHECKABLE)


def test_the_two_validator_files_are_byte_identical() -> None:
    """They have always been, and nothing enforced it until now.

    `tools/scripts/validate-docs.py` is what every hook, CI step and fleet
    check executes; the bundled copy is what the cockpit imports. A change
    landing in one and not the other is the exact failure mode above, and it
    is silent — both files parse, both run, and they answer differently.
    """
    a, b = (p.read_bytes() for p in COPIES)
    assert a == b, (
        "the two validator copies have diverged; copy "
        "src/project_os_cockpit/validate_docs_bundled.py over "
        "tools/scripts/validate-docs.py")
