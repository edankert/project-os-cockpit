---
type: instruction
id: INSTR-DECISIONS
status: active
owner: group:maintainers
created: 2026-01-27
updated: 2026-08-12
tags: [instructions, decisions]
---

# Decision records (ADRs)

Use ADRs (`../../docs/decisions/ADR-####-*.md`) for durable decisions that affect multiple files/flows.

## When to create an ADR
- A convention/contract changes (schemas, status models, directory layout).
- There are real alternatives with tradeoffs.
- A choice impacts more than one workflow or team.

## How to record ADRs
1. Create the ADR note from `../../docs/__templates__/adr.md`.
2. Add/update the entry in `../../SNAPSHOT.yaml` under `items.decisions`.
3. Link the ADR to impacted items via `related`.

## Superseding
- If ADR B replaces ADR A:
  - ADR B sets `supersedes: [[ADR-A]]`
  - ADR A sets `superseded: [[ADR-B]]` and status becomes `superseded`

## A decision that is not a yes/no

Some ADRs propose an option and leave threads open inside their own consequences. Accepting one of those stamps every thread at once, which is how a decision sits `proposed` for months: the reader can see what they cannot answer.

**Give the note an `## Acceptance` section and put each open thread in it as a criterion.** They are then tickable one at a time, with evidence, through the same machinery a feature's criteria use — no new mechanism, and the unticked ones are the honest residue.

```markdown
## Acceptance

- [ ] **The read-only digest:** decided, or deferred with a home and a reason.
- [ ] **`Recent`:** kept in both surfaces or dropped from both. Say which.
```

**Accepting with a criterion still open is allowed.** A person may take a decision while a thread stands, and the record should show that rather than prevent it. Blocking the verb would trade an honest record for a tidy one.

Most ADRs are a genuine yes/no and need none of this. The section is available, not required.

## Recording why, not only what

Every human verb — accept, approve, decline, supersede, triage — may carry a **note**, and it is appended to the note being decided under a single `## Decision record` heading:

```markdown
## Decision record

> [!note] Accept — 2026-08-12 (user:edwin)
> Option 3, but consequence 3 needs the digest question settled first.
```

Three properties, each deliberate:

- **It is an Obsidian callout.** One syntax, two readers: Obsidian renders it natively and so does the cockpit. A tool-only marker would make the record legible in one place.
- **It appends.** A second decision adds a second callout; the first is never edited. A decision record that can be rewritten is not one.
- **The prose is quoted line by line**, so a note containing `---`, a heading, or its own callout cannot alter the file it lands in.

Without this a project can record *that* a human decided and never *why* — measured in one repo across six write paths, exactly one carried the person's own words, and only onto a checkbox.

## A decision that offers options

If the decision is a choice between paths, put them under `## Options` so a person can be offered them and their answer can be recorded. **Either form**, both readable:

```markdown
## Options

1. **Deprecate mode 1.** Honest about where the effort goes; loses the tablet reader.
2. **Full parity.** Requires the write endpoints on a LAN-reachable surface. Refused: …
3. **Mode 1 is the reading surface.** Every view that answers a question without …
```

```markdown
## Options

### 1. The human publishes, on cadence (status quo)

The worker commits; a person pushes when they look…
```

Then **name the one you propose in the `## Decision` section** — "Option 3" — so a surface can default to it rather than guessing.

**This is checked.** `DECISION-OPTIONS` is an error when an `## Options` section yields fewer than two readable options, or when they do not number `1..N`. That is deliberate: a control can only offer what a document declares, and a convention nobody validates drifts per author until the control silently stops appearing. It is an error rather than a dated warning because the convention is new and there is no debt to grandfather (ADR-0011).

Recording a choice writes `decided_option:` in the frontmatter and names it in the decision-record callout. **Accepting without choosing stays legal** — a decision may be taken as proposed, and demanding a choice would turn an offer into a gate.

## A decision that states a rule

Some decisions are quantified: **every member of DOMAIN satisfies P**. Record one as an ordinary ADR carrying three additional sections — a section convention, not a new note kind (ADR-0023; the bar a new kind must clear is ADR-0022's). **The `## Rule` heading's presence is what marks a rule-ADR**: there is no `kind:` field and no new type, so do not use that heading as prose scaffolding in a decision that is not a rule — a note carrying it is checked as one.

```markdown
## Rule
One testable normative sentence.

## Domain
The enumerable set the rule ranges over.

## Conformance
The named discharge, and which side is authoritative on disagreement.
```

- **`## Rule`** — one testable normative sentence. If it takes a paragraph, it is two rules or not yet a rule.
- **`## Domain`** — the enumerable set or registry the rule ranges over: a type enum, a directory, a manifest, a table. **If the set cannot be named, the rule is not ready to be decided** — a rule over "everything relevant" cannot be conformed to and cannot be checked, and naming the domain often forces the missing registry into existence, which is most of the rule's value.
- **`## Conformance`** — the named discharge: one or more `TST-*` notes, a type that makes the violation unrepresentable (the strongest form — a test is deliberately not required), or a validator check code. Plus **one sentence naming which side is authoritative when the rule and an artifact disagree** — whether a conflict means the artifact is wrong or the rule has been overtaken. Without that sentence a violation has no defined resolution, and the rule quietly becomes advisory on first contact.

**Provenance.** A harvested rule cites the nominating issue family in its `## Context`, and **the trigger is the second issue of a kind, not the first** — one instance is a bug, two is a domain, and filing the third one-off is the failure this convention exists to catch (the sibling search in `../skills/issue-intake/SKILL.md` is where the second instance gets noticed). An up-front rule says **"from principle"** and lands its conformance the same day: it has no scars keeping it precise, so the check is the substitute for the evidence it does not have.

**Landing a rule over an existing corpus.** Reuse the machinery, do not reinvent it: the rule's check lands warning-first with a dated promotion (`PROMOTIONS` in `../scripts/validate-docs.py`), and instances already violating at promotion are listed by ID with reasons in `../GRANDFATHERED.yaml`. ADR-0011's clauses apply unweakened — the cutover is encoded in code, no more than 90 days out, and promotion over unpaid debt is forbidden. A rule whose corpus holds zero violations skips the warning entirely and errors from day one: with nothing to migrate, a warning would be the permanent tier that ADR forbids.

**Options.** A rule-ADR carries `## Options` under exactly the rule above ("A decision that offers options"), unchanged: required whenever the decision offers a choice — and most real rules did reject something specific, a threshold, a default, or the type deferred in favour of the check.

**This is checked.** `DECISION-RULE` is an error when a decision note carries a `## Rule` heading and its `## Domain` or `## Conformance` section is missing or empty — at **any** status, because a `proposed` rule binds nothing yet but is malformed in exactly the same way. `TST-*` IDs named under `## Conformance` must resolve to notes; a check code, a type name, or plain prose there is read as prose and never as a dangling link. Headings inside fenced code blocks or HTML comments do not count, which is why the commented block in `../../docs/__templates__/adr.md` cannot arm the check against the template's own output. An error rather than a dated warning for the same reason as `DECISION-OPTIONS`: at landing (censused 2026-08-12) the fleet held zero violations, so there was no debt to migrate (ADR-0011).
