---
type: "[[task]]"
id: TASK-0604
aliases: ["TASK-0604"]
title: "An agent drafts the missing checks and a person accepts them — a `commission-checks` verb on the release type, writing notes into the working tree and nothing into the gate"
status: done
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-09-08
updated: "2026-09-08"
source: ["[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]", "Edwin, 2026-09-08: 'add new checks if required (these might be LLM/Human actions?)'"]
parent: "[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]"
effort: M
due: ""
depends: ["[[TASK-0603]]"]
blocks: []
related: ["[[REQ-0061-A-Release-Is-Written-Through-One-Workflow]]", "[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]"]
tests: []
---

# An agent drafts the missing checks; a person accepts them

[[TASK-0603]] names what is uncovered. This task offers to write it, and stops well short of putting it in the gate.

**The rule, from [[FEAT-0145]]:** *"A check nobody read is a check nobody will walk, and a generated suite that grows on its own is worse than a short one somebody meant."* Every proposal arrives as a note in the working tree, reviewed as a diff.

## Definition of Done

- [x] `agent_actions.DEFAULT_ACTIONS` gains a **`release`** key. It currently holds `task`, `issue`, `feature`, `requirement`, `phase`, `design` and `risk` — a release has never had a verb.
- [x] The `commission-checks` verb's prompt **names the uncovered features** from [[TASK-0603]]'s computation, so the agent is not asked to rediscover them.
- [x] The prompt says to draft `TST-*` notes in the working tree, in the repo's own voice, from the feature and task notes, at `level: acceptance` and **carrying no verdict field at all**.

  *(Not `mark: todo`, which is what [[FEAT-0145]] and this task both said. In a repo that keeps ledgers the validator refuses `mark:` outright — `LEDGER-FIELD`, [[ADR-0037]]: a verdict on the note is a second source for one fact. Found the direct way: the acceptance check written for this very feature, [[TST-0083]], was rejected by the validator for carrying it. A prompt that tells an agent to write a field the validator rejects produces work somebody has to undo, so the prompt names the rule and the code.)*
- [x] The prompt says explicitly that **nothing is written into the gate** and no verdict is recorded. An agent that settles what it just proposed is the failure this whole split exists to prevent.
- [x] `REL` is added to `NOTE_TYPE_BY_PREFIX` in `renderer.ts`, or the verb never resolves. The map currently holds `TASK`, `ISS`, `FEAT`, `REQ`, `PHASE` and `RISK`; `noteTypeOfId('REL-0016')` returns `null` today, so `verbsForId` finds nothing whatever `DEFAULT_ACTIONS` contains.
- [x] The verb is offered on `draft` releases only — `when: ["draft"]`. Commissioning checks for a shipped release is proposing work against a frozen record.
- [x] The drafted notes are visible as a diff before anything is committed. The dispatch queue already delivers this; the task is to not build a second path around it.

## Steps

- [x] Add the `release` entry and the verb to `agent_actions.py`.
- [x] Add `REL: 'release'` to `NOTE_TYPE_BY_PREFIX`.
- [x] Confirm the verb appears on a draft release row and not on a released one.
- [x] Guard: every type named in `DEFAULT_ACTIONS` resolves through `noteTypeOfId` for its own id prefix. That is the general form of the defect this task fixes, and it will catch the next type added on one side only.

## Notes

**Why a verb and not a button that calls a model.** The dispatch queue is the one place an agent action is recorded, reviewable and stoppable. A release page that calls a model directly is a second, unlogged path to the same act.

**Carrying no verdict is the whole of the safety property.** A drafted check that arrives with any verdict at all is a claim about something nobody ran. In a ledger repo the field does not exist on the note, so the property is structural: the check is owed until somebody appends an event for it.
