---
type: "[[issue]]"
id: ISS-0021
aliases: ["ISS-0021"]
title: "Independent review of the model-routing upstreaming returned changes-requested — independence rule weakened, opusplan claim wrong, downstream hooks.json not updated"
status: fixed
severity: high
owner: user:edwin
created: 2026-07-24
updated: 2026-07-24
source: ["independent-review"]
related: ["[[FEAT-0039-Model-Routing-Subagents]]", "[[TASK-0197-Upstream-And-Adopt]]", "[[CHG-20260724-Model-Routing-Upstreamed]]"]
---

# ISS-0021 — model-routing review findings

Independent review (Opus 4.8, 2026-07-24) of the upstreaming work returned `changes-requested`. Findings, most severe first.

## 1. HIGH — the independence guardrail was weakened, and the new rule contradicts QUALITY.md

`QUALITY.md` ("Independent review (different-model)") and `independent-review/SKILL.md` rule 1 both require a **different model family or a human** — never the authoring model. The rewritten `independent-reviewer` subagent text narrowed its disclosure trigger from *same family* to *same model*, and told the agent its pass "carries weight" because the pins differ. `ADAPTER.md` codified the same error ("the pairing is the real safeguard"). Both `claude-fable-5` and `claude-opus-4-8` are Claude family, so that pairing never satisfied the rule.

Failure scenario: an Opus session authors a CHG, delegates to the Fable-pinned reviewer, which records `review_verdict: approved` **without** the cross-vendor caveat — because the models differ — and QUALITY.md's gate is silently satisfied by a review it forbids.

Compounding: the stated rationale for changing `REVIEWER_MODEL` (that Opus was "the recommended session model", making reviewer == author) cited a recommendation that this same change introduced. Upstream had no `model` key at all. Under the actual family-based rule, the old and new pins are equally non-independent — the "defect" being fixed was manufactured.

Also: `PLANNER_MODEL == REVIEWER_MODEL`, so planning artifacts are reviewed by the model that wrote them.

## 2. MEDIUM — the `opusplan` claim is factually wrong (3 files)

Claimed "it bypasses this routing". Subagent `model:` frontmatter takes precedence over the session model, so a session on `opusplan` still resolves `planner`/`independent-reviewer` to their pins. Only the main-loop model changes.

## 3. MEDIUM — downstream `tools/adapters/claude-code/hooks.json` was never updated

`.claude/settings.json` got the `UserPromptSubmit` entry but the template-owned `hooks.json` in this repo did not. `ADAPTER.md` documents "copy `hooks.json` into `.claude/settings.json`" as the manual install path — following it today would silently delete the routing hook.

## 4. MEDIUM — the required review fields were missing

Upstream's `CHG-20260724-Model-Routing.md` omitted `reviewed_by`/`review_date`/`review_verdict` entirely (all three are required by `docs/__templates__/change.md`); the downstream note had them empty. `validate-docs.sh` does not enforce these keys, so the omission was silent.

## 5. MEDIUM-LOW — hook status vocabulary incomplete, and `deferred` mis-classified

`open`, `blocked`, `reopened`, `wont-fix` hit no branch and fell through to "no active focus item resolved" — actively misleading when focus **is** set, and `open` is the normal working state for an issue. Separately the hook listed `deferred` as terminal; `STATUSES.md` states it is explicitly **non-terminal** (parked).

## 6. LOW — stale paths after the `.claude/hooks/` deletion

`FEAT-0039` Links block and `plan/PLAN.md` still pointed at the deleted `.claude/hooks/model-routing-hint.sh`; the FEAT Links line also omitted TASK-0197.

## 7. LOW — `CLAUDE.md` overstated the drift guard

Said the hook is "generated" (it is hand-written; only agents/skills/cursor-rules are generated) and implied a template sync keeps the agent files current. `sync-project-os.sh` copies `tools/` and never touches `.claude/`, and this repo has no `generate-adapters.py` — so the real property is "a sync will never update these", not "a sync is a no-op".

## 8. LOW — `status_of()` could read a nested `status:`

The status match was indentation-agnostic while the item-boundary guard only fired at 4 spaces, so an item with no own `status` but a nested block containing one (e.g. `tests: - status: passing`) yielded the nested value.

## 9. INFO — per-prompt context cost

~380 chars injected every prompt, ~180 of it unconditional boilerplate.

## Second review pass (2026-07-24)

Re-review of the fixes confirmed 8 of 9 resolved and found four more:

- **A. HIGH — the same overclaim survived in the first change note.** [[CHG-20260724-Model-Routing-Subagents]] still asserted the Opus/Fable pairing "satisfies the independent-review skill's different-model-family rule by construction" — a merged, `approved` note telling future readers the QUALITY.md gate was already met. Corrected in place with an explicit correction paragraph, and the note now carries the same-family `review_note` its siblings had.
- **B. LOW — `status_of()` did not strip quotes** (`focus_id()` did). A snapshot written as `status: "doing"` — valid YAML — would have matched no branch and emitted "no active focus item resolved" while focus was set, reintroducing finding 5's failure mode. Fixed; not reachable in either repo today since no snapshot quotes statuses.
- **C. LOW — `plan/PLAN.md` used `status: complete`**, which is not in the `[[plan]]` allowed set (`draft`, `active`, `done`, `superseded`); the validator does not check plan statuses, so it passed silently. Now `done`.
- **E. INFO — upstream did not apply its own advice**: `ADAPTER.md` says to keep the session model off the reviewer's pin, but upstream `.claude/settings.json` had no `model` key at all, so an upstream session could itself be `claude-fable-5` (reviewer == author). Upstream now pins `"model": "opus"`.

Two observations were accepted as-is: `reopened` routing to the planning branch (defensible — a regression usually does want re-triage), and the fact that requirement/phase statuses map to branches unreachable via `focus` keys (harmless completeness).

## Open follow-up

**D — the model-pin format is unverified end-to-end.** The pins moved from the `fable` alias to the full `claude-fable-5` ID. Upstream already used a full ID (`claude-opus-4-8`) before this work, so the convention is established, but nothing in either repo proves Claude Code honours a full model ID in subagent frontmatter. If it silently ignored it, the subagents would inherit the session model and the routing would be inert with no signal. Confirm once with `/agents` in a fresh session before the fleet rollout.

## Resolution

Findings 1–9 plus A/B/C/E addressed under [[TASK-0197-Upstream-And-Adopt]]; see [[CHG-20260724-Model-Routing-Upstreamed]] for what changed and the re-review verdict. D remains open as a manual check.
