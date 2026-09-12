---
type: "[[test]]"
id: TST-0085
aliases: ["TST-0085"]
title: "A link to a design shows the design"
status: active
owner: user:edwin
created: 2026-09-11
updated: 2026-09-11
phase: "[[PHASE-005-Desktop-Shell]]"
tier: 1
area: "Desktop shell and workspaces"
covers: ["[[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]"]
last_verified: 2026-09-11
related: ["[[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]", "[[TST-0084-A-Design-ID-Opens-The-Bench-And-Other-IDs-Open-Their-Note]]"]
level: acceptance
---

# A link to a design shows the design

Send the running cockpit a link that names a design's ID, and the design's page appears, not its note. That sentence is the whole check. Steps 9 and 10 were added on 2026-09-11 for two defects the first walk found, both about what else a link's project switch must get right. [[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]] exists because on 2026-09-10 such a link opened a page of text with one button on it.

Run the cockpit from source with the build that carries FEAT-0146, and send each link with `desktop/scripts/open-link.sh`. Expect, in order:

1. **From another project.** With project-os-cockpit on screen, run `desktop/scripts/open-link.sh your-health DES-0002`. The window switches to your-health and shows the design bench: a header with DES-0002's title and a `DES-0002` chip, and under it the design's page with its mockup images. It does not show the note's text with an "Open DES-0002 in the design bench" button.
2. **From the same project.** With your-health on screen and some other note open, send the same link. The bench opens without a project switch. Press Back, and the note you were on returns.
3. **The note is one click away, and stays.** On the bench, click the `DES-0002` chip in the header. The note opens and stays open. It does not bounce back to the bench.
4. **A path still means the file.** Run `desktop/scripts/open-link.sh your-health docs/designs/DES-0002-Recovery-And-Food.md`. The note opens, not the bench.
5. **A design with nothing to show opens its note.** Run `desktop/scripts/open-link.sh project-os-cockpit DES-0003`. DES-0003 declares no artifact and no variants, so its note opens, with the banner "This design has no artifact yet."
6. **Any other ID is unchanged.** Run `desktop/scripts/open-link.sh your-health FEAT-0107`. The feature's note opens, as it did before this change.
7. **A cross-repo link to a design.** In project-os-cockpit, open PHASE-028 and click `project-os-deck#DES-0001` in its frontmatter strip. The window switches to project-os-deck and shows DES-0001 on the bench.
8. **An owed design's row still opens its note.** In your-health, open the Intent view. If DES-0002 is listed as needing you, its row opens the note, where Accept is, and not the bench.

9. **The left pane arrives with the project.** Put the left pane in Overview mode on project-os-cockpit, then send step 1's link again. The bench opens, and the left pane lists *your-health's* phases. It must not say "Pick a workspace from the rail on the left", and it must not go on listing project-os-cockpit's phases under Your Health's name ([[ISS-0296-A-Link-That-Switches-Project-In-Overview-Leaves-The-Left-Pane-Unloaded]]).
10. **A link belongs to the project it names.** Send step 1's link from project-os-cockpit, and before your-health has finished starting, click a third project on the rail. That project opens, on its own first page, and the status bar says "DES-0002 was not opened: you switched to another project." The bench must not open in the third project ([[ISS-0298-A-Parked-Link-Opens-In-Whichever-Project-Arrives-First]]).

**What must not happen:** anything that opens a design's note by its path landing on the bench instead. Steps 3, 4 and 8 are the ones to watch. If any of them shows the bench, the rule has leaked out of the one place it belongs, and the note has become unreachable.

The rule and its call site are also checked without a window by [[TST-0084-A-Design-ID-Opens-The-Bench-And-Other-IDs-Open-Their-Note]]. This check is the part those tests cannot see.

## Walked 2026-09-11 (model:claude-opus-5)

Every step passed. They were not all walked in the same place, and the difference matters to anyone relying on this record.

**In the running window.** The cockpit was restarted by its pid with the FEAT-0146 build, and a debugging port was opened. Each link was sent with `desktop/scripts/open-link.sh`, and the window's state was read through the port. Steps 1, 2, 3, 4 and 6 passed there. Step 1 showed DES-0002's page with its 19 images, not the note. Step 3's chip opened the note, and it was still open 4 seconds later. Step 5 switched to project-os-cockpit and opened DES-0003's note, but its banner was not checked in the window.

**In the renderer harness.** Edwin was using the window during the walk. A click on the rail moved it back to your-health 7 seconds after a link had moved it away, so the rest was walked elsewhere. The harness was a copy of `desktop/harness/live-harness.html` in a hidden, separate Electron instance, with three workspaces backed by three sidecars started for the walk. It runs the same built renderer and stubs only the Electron bridge, so a link reaches `openCockpitLink` without passing through the main process. Steps 7 and 8, and the banner in step 5, were walked only there. All eight steps were then walked again there on the final build, and all passed.

**Two defects found by this walk**, both fixed before the final pass:

- Step 5's banner was missing after a project switch: [[ISS-0297-After-A-Project-Switch-A-Design-Note-Loses-Its-Banner]].
- A link parked while the window switched could be opened by whichever project arrived first: [[ISS-0298-A-Parked-Link-Opens-In-Whichever-Project-Arrives-First]], found by the independent review and fixed with step 10 added to this check.
- A link that switches project while the left pane is in Overview left that pane unloaded: [[ISS-0296-A-Link-That-Switches-Project-In-Overview-Leaves-The-Left-Pane-Unloaded]]. A your-health session reported it in the window's console during the walk.

**Also checked.** `cockpit://your-health/~design/DES-0002`, the bench address written as a path, still opens the bench. With the design register made to fail, by a network error and then by HTTP 500, `DES-0002` opened its note both times.

**Walked again after the independent review**, in the harness, on the build that carries its fixes. Step 9: with the left pane in Overview on project-os-cockpit, the link opened the bench and the pane listed your-health's phases. Step 10: with a third project picked mid-switch, the bench did not open there, the status bar read "DES-0002 was not opened: you switched to another project.", and the third project landed on its own overview. A plain link to the bench still worked immediately afterwards.

**Not recorded in the ledger.** No `pass` was appended to `docs/releases/ledgers/WORKING-macos.json`. Three steps were walked only outside the window, so this record is not a person's pass in the running window. Until someone records one, the check is owed on macos.
