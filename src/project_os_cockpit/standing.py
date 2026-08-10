"""The project's standing documents: one per project, no lifecycle, human-facing.

`ISS-0125` measured the class: `README`, `INDEX`, `ARCHITECTURE`, `GLOSSARY`,
`OWNERSHIP`, `DESIGN`, `STYLEGUIDE`, `PHASES` — present in **90 of 96** possible
slots across the fleet, and **85 of those 90 stale or undated**. Not missing.
Unnamed as a set, unchecked, and unreachable — and a document nobody is ever
asked about is a document nobody updates.

**A manifest, not a type** (REQ-0033). A type models an open population: there
will be a ninth feature, a fortieth issue. There will never be a second
glossary. So the set is data, and `ISS-0124`'s question — whether these types
need status tables — is answered the other way: they carry no lifecycle status
at all, and `updated:` is the field that means something.

**Where the base set lives, and why it is not in `tools/`.** TASK-0380 assumed
the base would be template-owned and synced. It is better here: `sync-project-os.sh`
copies `tools/` wholesale, so anything a project added there would be destroyed
by the next sync — and the cockpit is never installed into a downstream repo at
all (CLAUDE.md: *"Repos are consumed by discovery, not by a shim"*). One
declaration in the app applies to every repo it renders, which is the property
"template-owned" was reaching for, without the sync hazard.

A project extends the set through its own `SNAPSHOT.yaml`, which is never
synced. That is the half that must survive an update, and it is the half that
lives in the repo being described.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class StandingDocument:
    """One entry in the manifest."""

    name: str
    #: What question a reader opens it to answer. Not a description of the
    #: file — the reason it is in the set at all.
    question: str
    required: bool = True

    @property
    def filename(self) -> str:
        return f"{self.name}.md"


#: The base set, applying to every repo the cockpit renders.
BASE_STANDING: tuple[StandingDocument, ...] = (
    StandingDocument("README", "what is this project?"),
    StandingDocument("INDEX", "where do I find things?"),
    StandingDocument("ARCHITECTURE", "how is it built?"),
    StandingDocument("GLOSSARY", "what do the words mean?"),
    StandingDocument("OWNERSHIP", "who decides what?"),
    StandingDocument("DESIGN", "what should it look like?"),
    StandingDocument("STYLEGUIDE", "how is it written?"),
    StandingDocument("PHASES", "what order is it being built in?"),
)


@dataclass(frozen=True)
class Resolution:
    """How one manifest entry resolved against a real docs tree.

    `paths` carries **every** match, not the first. An entry resolving to two
    files means the set has quietly become a type, which is the drift REQ-0033
    exists to catch — and a resolver that returned the first match would hide
    it forever.
    """

    document: StandingDocument
    paths: tuple[Path, ...]

    @property
    def state(self) -> str:
        if len(self.paths) == 1:
            return "present"
        if not self.paths:
            return "missing" if self.document.required else "absent"
        return "ambiguous"

    @property
    def path(self) -> Path | None:
        return self.paths[0] if len(self.paths) == 1 else None


def _extensions_from_snapshot(project_root: Path) -> list[StandingDocument]:
    """Project-specific entries from `SNAPSHOT.yaml`'s `docs_system.standing`.

    That block exists today and **nothing reads it** — `source_of_truth`,
    `instructions`, `references`, no consumer anywhere. This gives a dead field
    its first one rather than inventing a place beside it.

    Parsed leniently: a malformed snapshot must not take the manifest with it,
    because the base set is the part that matters and it needs no snapshot.
    """
    snapshot = project_root / "SNAPSHOT.yaml"
    if not snapshot.is_file():
        return []
    try:
        import yaml

        data = yaml.safe_load(snapshot.read_text(encoding="utf-8")) or {}
    except Exception:
        return []
    block = (data.get("docs_system") or {}).get("standing") or []
    if not isinstance(block, list):
        return []
    out: list[StandingDocument] = []
    for entry in block:
        if isinstance(entry, str):
            out.append(StandingDocument(entry.strip(), "", required=True))
        elif isinstance(entry, dict):
            name = str(entry.get("name") or "").strip()
            if not name:
                continue
            out.append(StandingDocument(
                name,
                str(entry.get("question") or ""),
                required=bool(entry.get("required", True)),
            ))
    return out


def manifest(project_root: Path) -> tuple[StandingDocument, ...]:
    """The base set plus this project's extensions, deduplicated by name.

    One function, so no consumer can read half the manifest — which is how a
    check ends up disagreeing with the surface it is meant to guard.
    """
    seen = {d.name.upper(): d for d in BASE_STANDING}
    for extra in _extensions_from_snapshot(project_root):
        seen.setdefault(extra.name.upper(), extra)
    return tuple(seen.values())


#: Names that also occur as container-directory signposts. `docs/issues/README.md`
#: and its eight siblings are boilerplate, not the project's README — the third
#: of the three jobs `reference` does (ISS-0125). A recursive search for
#: `README.md` finds nine of them and reports the entry ambiguous, which is a
#: sentence about the *search*, not about the corpus.
_ROOT_ONLY: frozenset[str] = frozenset({"README"})


def resolve(docs_root: Path, project_root: Path | None = None) -> list[Resolution]:
    """Resolve every manifest entry against a docs tree, in manifest order.

    The canonical location is the **docs root** — every member of this class
    sits there, which is what ISS-0125 measured. A copy deeper in the tree is a
    *rival*, and reporting it is the whole point of `Resolution.paths` carrying
    more than one path: an entry with two files has quietly become a type,
    which is the drift REQ-0033 exists to catch.

    `README` is root-only, because eight container directories carry one and
    none of them is the project's.
    """
    root = project_root or docs_root.parent
    out: list[Resolution] = []
    for doc in manifest(root):
        canonical = docs_root / doc.filename
        matches: list[Path] = [canonical] if canonical.is_file() else []
        if doc.name.upper() not in _ROOT_ONLY:
            matches.extend(sorted(
                p for p in docs_root.glob(f"**/{doc.filename}")
                if p != canonical
                and "__templates__" not in p.parts
                and "__bases__" not in p.parts
            ))
        out.append(Resolution(doc, tuple(matches)))
    return out
