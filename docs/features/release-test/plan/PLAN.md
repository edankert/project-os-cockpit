---
type: "[[plan]]"
title: "Build the release test section by section"
status: draft
owner: user:edwin
created: 2026-09-27
updated: 2026-09-27
source: ["Edwin, 2026-09-27: approved example page and decisions D1 to D3"]
implements: ["[[FEAT-0155-The-Release-Test-Goes-Section-By-Section]]"]
related: ["[[PHASE-043-The-Walk-Page]]"]
---

# Build the release test section by section

## Delivery sequence

1. Rename the walk to the release test across the cockpit, with a redirect from the old address and a one-time move of saved browser results ([[TASK-0639-Rename-The-Walk-To-The-Release-Test]]). This goes first so the new code is written with the new names.
2. Carry the generator's sections, groups, Setup and what changed into the payload ([[TASK-0640-The-Release-Test-Payload]]).
3. Add the Tests pane entry ([[TASK-0641-The-Release-Test-In-The-Tests-Pane]]), the platform overview with Continue and Needs you ([[TASK-0642-The-Platform-Overview-Continue-And-Needs-You]]), and the section page with its results ([[TASK-0643-The-Section-Page-And-Its-Results]]). The pane and the section page can be built side by side once the payload exists.
4. Pilot Your Trainer's Android Equipment Hub section and compare it with the example page; then the other Android sections; then iOS ([[TASK-0645-Pilot-The-Equipment-Section-Then-The-Rest]]).
5. Retire the Publication view's walk page, and supersede the notes this replaces ([[TASK-0644-Retire-The-Walk-Page-In-The-Publication-View]]).

## Dependencies

- **Hard:** project-os-dev must rename its generator and produce sections, groups, "Start:" lines, the three-part Setup, what changed per platform and readiness before steps 1 and 2 can finish (project-os-dev: release test generator, vocabulary ADR and release-prep skill, ID to follow). The cockpit bundles that generator byte for byte and does not work these out itself.
- **Hard:** the pilot in step 4 needs Your Trainer's rewritten equipment section and shortened `## Expect` lines (your-trainer: rewrite of the procedures and test notes, equipment section pilot, ID to follow).
- **Soft:** the old page stays in place until the pilot passes, so a release in progress is never left without a page.

## Open questions

- The word "section" already names "Feature tests", "Regression tests" and "Automated tests" in this repository ([[ADR-0039-Three-Sections-Derived-Not-Filed]]). See the feature's open questions.
