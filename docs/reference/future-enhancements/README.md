---
type: "[[reference]]"
id: REFERENCE-FUTURE-COCKPIT-ENHANCEMENTS
title: "Possible future cockpit enhancements"
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
scope: "project"
source:
  - "Edwin 2026-09-16: review the cockpit against design, development, testing and issue triage, including similar solutions; prefer less or differently presented data."
  - "Edwin 2026-09-16: 'I like to see percentages / progress bars and different colours/status badges instead of seeing all these text strings.'"
  - "Repository documentation, implementation, live sidecar responses and rendered desktop views reviewed on 2026-09-16."
related:
  - "[[REFERENCE-CAPABILITY-REGISTER]]"
  - "[[ADR-0020]]"
  - "[[ADR-0028]]"
  - "[[DES-0012]]"
  - "[[RISK-0009]]"
  - "[[ISS-0306]]"
tags: [reference, future-enhancements, cockpit, usability]
---

# Possible future cockpit enhancements

## Purpose and standing

The cockpit should make current work, outstanding decisions and release readiness clear at a glance. This section records possible enhancements from the September 2026 review for later discussion and design.

These proposals are not approved features, an implementation plan or new lifecycle rules. Existing decisions remain in force. Selecting an enhancement later requires the normal documentation intake and any necessary design decisions.

## User preference: keep visual progress

**Edwin prefers percentages, progress bars, colours and status badges over sentence-heavy status summaries.** The initial review suggested replacing percentage-led summaries with explanatory sentences. This reference revises that suggestion: retain the visual indicators and make their scope clearer. Use short text only when a blocker, decision or next action needs an explanation.

- Keep percentages and progress bars prominent for measurable progress.
- Use compact badges to distinguish design, implementation, verification and release state.
- Reuse the established semantic colours and status vocabulary. Pair colour with a label or icon so meaning does not depend on colour alone.
- Label what a percentage measures. Implementation at 100% can coexist with acceptance at 60% and a blocked release.
- Reveal the numerator, denominator and outstanding items on expansion or inspection.
- Show unknown progress explicitly when no meaningful denominator exists. Do not invent a design-completion percentage from the presence of a document.
- Keep blockers visible beside the bar. A high completion percentage must not conceal a failing release check.

An illustrative feature row could show `Implementation 100%` with a progress bar, `Acceptance 60%` with another bar, and an amber `Needs testing` badge. A short action such as `Run checks` opens the work behind the badge. These labels illustrate presentation, not additions to the canonical status taxonomy.

## What the cockpit must help the human do

| Activity | What should be clear | Human contribution |
| --- | --- | --- |
| Design a feature | Proposal, unresolved questions, review state and readiness for implementation | Refine the proposal, review it and accept the intended design |
| Follow development | Active phase or feature, measurable progress, blockers and who acts next | Answer questions and resolve decisions that stop progress |
| Build and test | Candidate to test, automated results, remaining acceptance work and release blockers | Use the product, record acceptance results and decide release readiness |
| Handle issues | Observed problem, reproduction evidence, impact and proposed fix | Triage, refine scope and decide priority or deferral |

Issues and tests can matter throughout the lifecycle. They should remain visible beside the work they affect, as described in [[ADR-0028]].

## Findings from the current cockpit

These observations describe the working tree and live data inspected on 2026-09-16. Counts are examples from that review, not current project metrics.

| Observed presentation | Consequence |
| --- | --- |
| Overview led with 124 historical transitions above the current focus. | Earlier activity occupied the space needed for current decisions and progress. |
| Tests said “Nothing owed on tests”; its navigator showed six outstanding feature tests; Publication showed three unchecked release tests. | Different scopes appeared contradictory without an immediate explanation. |
| PHASE-037 showed 100%, an active status and two remaining items. | The percentage needed a clear label explaining which work was complete. |
| Intent combined project reference material with a long design register. | Finding a design did not immediately reveal what needed a decision. |
| A triage issue prominently offered Fix before Triage / refine. | The primary action could encourage implementation before assessment. |
| Publication repeated checks across the gate, scope decisions and contents sections. | Understanding one set of outstanding work required repeated reading. |
| Notes opened with substantial frontmatter, and the overview had several additional registers in its context pane. | Supporting information competed with the main activity. |
| The guided test page exposed raw Markdown and authoring detail in places. | The procedure required interpretation before the user could follow it. |

The review used the real sidecar through an isolated renderer harness. It inspected screens and data without executing builds, submitting decisions or recording acceptance results. Shell integrations were stubbed, so this was not a complete acceptance run.

## Possible enhancements

### 1. Put decisions, active progress and release readiness first

Organize Overview around three compact groups: decisions needing the human, work in progress, and the next release. Use progress bars and badges within each group. Show the immediate blocker or question only where it adds information.

Move the historical digest below current work and collapse it to a brief summary. Keep project totals, completed phases and detailed task squares available through expansion. Deferred work should remain discoverable without competing with work that is actually progressing.

Reuse the existing obligation calculations. Each summary should open the action beside its subject. [[ADR-0020]] gives each obligation one home; this proposal does not create a separately maintained review queue. Any richer aggregation that changes that decision needs explicit reconsideration.

### 2. Make progress bars and status badges describe distinct facts

Keep implementation progress separate from acceptance progress. A feature with every task finished may still require testing or approval. A phase's completion view should also account for its exit conditions.

Use a small number of clearly labelled indicators at each level. The overview shows feature or phase progress; expanding a row shows the contributing tasks and checks. Avoid displaying every measure at every level.

Where checklist counts are meaningful, derive percentages from them and show the counts on inspection. Where design readiness is qualitative, use the existing status badge and an unresolved-question count. Do not combine task completion, design approval and test success into an unexplained overall percentage.

Cancelled work, deferred work, exceptions and missing evidence need defined treatment in any denominator. An excused test remains distinguishable from a passed test, even when the release gate considers it settled.

### 3. Frame design review around the pending decision

Lead a design review with its current badge, the proposal or visual, and the unresolved question. Make the agent's recommendation and changes since the previous review easy to inspect.

Offer actions appropriate to the design's state: accept for implementation, request changes, or ask for investigation. Keep the feature's identity visible as the human and agent iterate. Open requirements, mockups and full discussion when needed.

Preserve the existing note and image viewer approach. This proposal does not reinstate the retired design bench. If approval is tied to a specific revision later, address [[RISK-0009]] deliberately; that requires stronger records as well as a different presentation.

### 4. Connect the build candidate to automated and acceptance testing

Provide a clear route through preparing a candidate, opening or installing it, running automated checks, completing acceptance testing, and reviewing release readiness.

Identify the candidate and platform beside the test progress. Show automated results separately from human acceptance results, with compact bars and badges. State when results belong to an older candidate or when that relationship is unknown.

Offer Start testing or Resume testing from the release summary. Reuse the existing guided procedure and ledger. Keep required devices, environments and setup beside the procedure. Expand logs and evidence on demand.

Prioritize failing, untested and invalidated checks. Collapse passed checks and group procedures by the screen or activity being tested. A release can have high test completion and still show a blocking failure prominently.

The review did not find a clear end-to-end build-and-open journey comparable to the existing test and release views. Candidate identity and launch integration therefore need capability work. Reorganizing existing checks is mainly presentation work.

### 5. Make triage lead to an explicit disposition

Show the issue's affected behavior, reproduction state and impact on current work or release. Use its severity and lifecycle badges prominently. Keep the explanation short enough to support the decision.

Make the primary action fit the issue's maturity: investigate, accept for fixing, defer or decline. A proposed fix can accompany the evidence once available. Implementing a fix should follow the applicable triage decision.

When testing finds an issue, retain the originating test step, candidate, platform and evidence. Make the affected check easy to rerun after the fix. Reuse existing capture and linking capabilities where possible.

### 6. Reduce competing information while retaining visual signals

- Collapse frontmatter by default and lead with the note's purpose or current decision.
- Consider collapsing the right context pane on overview and workflow pages.
- Give primary navigation visible text labels alongside its icons.
- Lead with readable titles and make IDs secondary.
- Keep agent activity visible, with session cost and cache details available on demand.
- Distinguish an agent working from a request the human can answer.
- Use brief action labels and status badges instead of paragraphs explaining internal workflow rules.
- Combine repeated warnings about one underlying record problem into one inspectable summary.
- Render guided test procedures cleanly, without raw markup or authoring comments.

### 7. Make missing or inconsistent records visible

Progress indicators should reveal uncertainty when their inputs cannot be trusted. Missing test coverage is different from tests that passed. A missing candidate is different from a failed build.

[[ISS-0306]] records incomplete screen documentation that limits the cockpit's own changed-screen survey. The review found two surface notes, so the issue's earlier one-note count was already historical. Improve the input records before presenting the survey as complete.

The review also found malformed quoting in SNAPSHOT.yaml despite a successful documentation-validator result. The quoting was repaired while recording this reference. The mismatch remains useful evidence that a clean validator result does not establish every kind of record consistency.

The snapshot narrative described PHASE-040 as deferred while its structured status was planned. Trust the structured planned state until the discrepancy is reconciled. This reference changes neither the phase nor its scope.

## Similar solutions and useful patterns

Official documentation was researched on 2026-09-16. The proposed applications below are review judgments, not claims that these products implement project-os workflows.

| Solution | Relevant pattern | Possible application here |
| --- | --- | --- |
| [Linear project updates](https://linear.app/docs/initiative-and-project-updates) and [milestones](https://linear.app/docs/project-milestones) | Project health and progress have an overview, with explanation available alongside them. | Keep visual progress prominent and attach concise explanations to exceptions. |
| [Linear triage](https://linear.app/docs/triage) | Issues have explicit accept, duplicate, decline and snooze actions. | Make the human's triage decision clear before emphasizing implementation. |
| [Basecamp Shape Up: Show Progress](https://basecamp.com/shapeup/3.4-chapter-13) | Progress distinguishes resolving uncertainty from executing understood work. | Use distinct design and implementation signals while retaining Edwin's preferred percentages and bars. |
| [Kiro specs](https://kiro.dev/docs/specs/) | Requirements, design and implementation tasks form a connected feature workflow. | Keep the feature and its pending handoff recognizable throughout refinement and implementation. |
| [Jira Product Discovery delivery](https://support.atlassian.com/jira-product-discovery/docs/manage-the-delivery-tab/) | Ideas connect to delivery work and its progress. | Preserve the feature's purpose and design context as implementation advances. |
| [Qase test runs](https://docs.qase.io/en/articles/5563702-test-runs) | Runs carry environments and configurations; execution supports steps, evidence and defects. | Make testing a guided activity tied to an identified candidate and platform. |
| [GitHub Copilot output review](https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/review-copilot-output) | Agent work is handed to a human through a reviewable change. | Keep agent completion distinguishable from human approval and acceptance. |

## Possible order and evaluation

An initial design could simplify Overview, clarify progress denominators and testing scopes, and collapse metadata. A later design could improve design-review and triage handoffs. Candidate build and launch integration can be assessed as a separate capability. This sequence is a suggestion, not scheduled work.

Evaluate any proposed design with the user's real project data:

- Can Edwin identify current work, the next decision and the release blocker within ten seconds?
- Do percentages, bars, colours and badges communicate the state before explanatory text is read?
- Is it clear what each progress bar measures and why a nearly complete item can still be blocked?
- Can the relevant decision or test procedure be reached directly from its summary?
- Can a test result be traced to the candidate and platform actually tested?
- Do an empty queue, deferred work and unknown readiness remain distinguishable?

## Maintenance

Keep this section as reference material until an enhancement is selected. Link any resulting design or feature back here and identify which proposal it adopts or revises. Preserve dated observations as evidence rather than updating their example counts to resemble live metrics.

The user's preference for visual progress takes precedence over the earlier review's sentence-heavy suggestion and illustrative prototype. Any future mockup should follow the preference recorded here.
