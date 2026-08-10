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

import datetime as _dt
import re
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


# ----- freshness, which is the only state these documents have --------------

#: Days after which a standing document is reported stale.
#:
#: 180, and the number has a reason rather than being round. These do not decay
#: like a manual test does (`MANUAL_TEST_STALE_DAYS = 60`, where "it passed
#: once" stops being an answer) — a glossary can be right for a year. What is
#: worth catching is *abandonment*, and ISS-0125 measured what that looks like:
#: `DESIGN.md` and `STYLEGUIDE.md` untouched since the day they were created,
#: six and a half months. 180 flags those and leaves a document someone revisits
#: twice a year alone.
#:
#: A parameter, not a constant of nature. Raise it if it nags; lower it if the
#: fleet's 94% does not move.
STALE_AFTER_DAYS = 180

#: Placeholder shapes that mark a document as still a template. The same
#: counting `brief_payload` does for `LLM_BRIEF.md` — one implementation of
#: "this was never filled in", not two.
_PLACEHOLDER_RE = re.compile(r"<[A-Za-z][^>\n]{2,40}>|TODO|FIXME|replace_me|YYYY-MM-DD")
_PLACEHOLDER_THRESHOLD = 3

_UPDATED_RE = re.compile(r'^updated:\s*"?(\d{4}-\d{2}-\d{2})', re.M)
_STATUS_RE = re.compile(r'^status:\s*\S', re.M)


@dataclass(frozen=True)
class Finding:
    """One thing wrong with one standing document.

    Four kinds, reported **distinctly**: a missing document, an entry claimed
    by two files, a document still holding its template, and one nobody has
    touched. Collapsing them into "problem" would lose the only useful part —
    what to do about it differs completely.
    """

    document: str
    kind: str      # missing | ambiguous | stub | stale | has_status
    detail: str
    severity: str  # error | warning


def check(docs_root: Path, project_root: Path | None = None,
          today: _dt.date | None = None) -> list[Finding]:
    """Every finding for this project's standing set.

    **Staleness warns and never errors.** A stale glossary is worth knowing
    about and worth nobody's build failing over — the pattern upstream ADR-0011
    established for independent review. A blocking gate on documentation nobody
    is currently reading gets disabled within a week, which is worse than a
    warning that is occasionally skipped.

    Lives here rather than in `validate_docs_bundled.py` because that file is
    template-owned and held byte-identical (ISS-0026). The rule is guarded
    locally and proposed upstream — the same split ISS-0069 and the PHASE-999
    rule took before it.
    """
    now = today or _dt.date.today()
    findings: list[Finding] = []
    for res in resolve(docs_root, project_root):
        name = res.document.name
        if res.state == "missing":
            findings.append(Finding(
                name, "missing",
                f"{res.document.filename} is absent; it answers "
                f"{res.document.question!r}",
                "error" if res.document.required else "warning",
            ))
            continue
        if res.state == "ambiguous":
            findings.append(Finding(
                name, "ambiguous",
                "two files claim this entry: "
                + ", ".join(str(p) for p in res.paths),
                "error",
            ))
            continue
        if res.path is None:
            continue
        text = res.path.read_text(encoding="utf-8", errors="replace")

        # A lifecycle status on a document with no lifecycle can only say
        # something false or say nothing (ISS-0125). `active` is in the
        # work-in-flight band, so it says the first.
        if _STATUS_RE.search(text.split("---")[1] if text.startswith("---") else ""):
            findings.append(Finding(
                name, "has_status",
                "carries a lifecycle `status:`, which for a standing document "
                "is either false or meaningless — `updated:` is its only state",
                "warning",
            ))

        body = text.split("---", 2)[-1]
        if len(_PLACEHOLDER_RE.findall(body)) >= _PLACEHOLDER_THRESHOLD:
            findings.append(Finding(
                name, "stub", "still holds its template", "warning",
            ))

        m = _UPDATED_RE.search(text)
        if not m:
            findings.append(Finding(
                name, "stale", "carries no `updated:` date", "warning",
            ))
        else:
            age = (now - _dt.date.fromisoformat(m.group(1))).days
            if age > STALE_AFTER_DAYS:
                findings.append(Finding(
                    name, "stale",
                    f"last confirmed {age} days ago", "warning",
                ))
    return findings
