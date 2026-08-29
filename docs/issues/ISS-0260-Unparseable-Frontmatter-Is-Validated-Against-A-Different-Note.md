---
type: "[[issue]]"
id: ISS-0260
aliases: ["ISS-0260"]
title: "A note whose frontmatter is not YAML is validated against a different, partial reading of itself — `load_yaml` swallows the parse error and the lenient fallback answers instead"
status: open
owner: user:edwin
created: 2026-08-29
updated: 2026-08-29
severity: high
component: tooling
phase: "[[PHASE-999-Future]]"
related: ["[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]", "[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]", "[[ISS-0183-The-Canonical-Machine-Readable-File-Did-Not-Parse]]"]
---

# Unparseable frontmatter is validated against a different note

`load_yaml` is the validator's single entry point for every piece of YAML it reads:

```python
def load_yaml(text):
    try:
        import yaml
        return yaml.safe_load(text)
    except Exception:
        return parse_yaml_subset(text)
```

The `except` is there so a repo with no PyYAML still works — a good reason. But it does not distinguish *"PyYAML is not installed"* from *"PyYAML is installed and this text is not YAML"*. In the second case the note is handed to `parse_yaml_subset`, which is deliberately lenient (*"best-effort on lists-of-maps"*, and it `continue`s past any line it cannot match) — so the validator reads a **partial but plausible** version of the note and reports on that, with no signal that it did.

There is a `SNAP-PARSE` rule for `SNAPSHOT.yaml`. **There is no equivalent for a note.**

## Two live instances, and the first one is mine

**It hid my own defect for two commits.** On 2026-08-29 ([[TASK-0586-Your-Trainer-Scopes-Its-Release]]) a string replace with no count added `FEAT-0104` at every `]` in thirteen `covers:` lists, producing:

```yaml
covers: ["[[FEAT-0011, "[[FEAT-0104-MultiRiderFreeAndProSeat]]"], "[[FEAT-0104-...]]"]", "[[FEAT-0104-...]]"]
```

`validate-docs.sh` reported **0 errors** over that, twice, in a repo whose pre-commit hook runs it. What caught it was `project-os-cockpit`'s own test suite, which loads those notes with PyYAML and refuses them — i.e. a check in a *different repository*.

**And eight notes have been living there.** `your-trainer`'s `REQ-0194`–`REQ-0201` (committed `2f336d3b`, 2026-07-24) have a second criteria list appended at the wrong indent. The fallback silently drops it, so `REQ-BOXES` reports *"4 acceptance criteria remain unticked"* against a note whose criteria are all marked ✅ — a real-looking finding derived from a reading of the file that does not exist on disk.

## Why this belongs in [[PHASE-041]]'s family

The phase's subject is a check that reported success while it could not see the problem. This is the same shape one level down: the validator is not wrong about the note, it is right about a *different* note, and nothing in its output distinguishes the two.

## Options

1. **Catch `ImportError` only**, and let a genuine parse failure raise — then report it as `NOTE-PARSE`, an error naming the file and the YAML message.
2. Keep the fallback, but have `load_yaml` report when it *used* the fallback while PyYAML was available.

Option 1 is right; option 2 is what to do if some repo genuinely depends on the leniency, which should be measured before assuming.

## Done when

- [ ] A note whose frontmatter does not parse is reported by ID and path, with the parser's message.
- [ ] The fleet is measured for existing instances first — [[project-os-dev#ADR-0011]] clause 3 forbids promoting over debt, and `your-trainer` alone has eight.
- [ ] Proposed upstream: `load_yaml` is in the template-owned validator, so every repo carries the defect.
