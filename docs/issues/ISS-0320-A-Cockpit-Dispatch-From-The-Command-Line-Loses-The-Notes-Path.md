---
type: "[[issue]]"
id: ISS-0320
aliases: ["ISS-0320"]
title: "A prompt sent with `cockpit dispatch` says \"Read docs/ first\" instead of naming the note's file, unless the quick switcher has been opened"
status: fixed
phase: ""
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[TST-0095-A-Prompt-Dispatched-To-Claude-Arrives-As-A-Submitted-Prompt-And-Can-Be-Cancelled]], step 8, run on 2026-10-14"]
reported_by: agent
question: ""
severity: low
component: desktop
parent: ""
related: ["[[FEAT-0025]]", "[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]"]
tests: []
---

# A `cockpit dispatch` prompt loses the note's path

Found in TST-0095 step 8 on 2026-10-14. Edwin ran `cockpit dispatch TASK-0084` in project-os-deck. The prompt reached Claude as a submitted prompt, as it should. But it read "Work on TASK-0084. Read docs/ first — the note is the spec". A verb button builds "Read docs/features/glass-bands/plan/tasks/TASK-0084-A-Promoted-Card-Is-Laid-Out-At-The-Size-Its-Promotion-Earned.md first". Claude gets a pointer to the whole `docs/` folder instead of the note.

## Cause

`handleDispatchRequest` in `desktop/src/renderer/renderer.ts` looks the note's path up in `quickCorpus`, the quick switcher's list of notes. That list is filled by `buildQuickCorpus`, which runs only when the quick switcher opens. In a window where nobody has opened it since launch, the lookup finds nothing and the path is `''`. The verb templates in `src/project_os_cockpit/agent_actions.py` all write `docs/{rel}`, so the prompt says `docs/`. The comment beside the lookup says "the prompt template tolerates a missing rel (falls back to the ID)"; no template does that.

The verb is lost the same way: the ledger entry for this dispatch has no `verb`, where a button's has `implement`. That is because the CLI sent no `--verb` and the request carries none; the default verb was still used for the prompt.

This predates FEAT-0158. It is the command-line path from FEAT-0025, and FEAT-0158 did not change it.

## Expected

A `cockpit dispatch <ID>` prompt names the note's file exactly as the verb button does, whether or not the quick switcher has been opened.

## Fix, 2026-10-14

Edwin: "fix ISS-0320 ... you found this, you prioritized this, you should fix this."

1. **The sidecar names the note's file.** `POST /api/cockpit/dispatch` with `enqueue` looks the ID up in the project's index and puts `rel` on the request. An ID the project does not have is refused with 404 and "no note with ID … in this project", which `cockpit dispatch` prints, instead of a prompt about nothing.
2. **The window uses it.** `handleDispatchRequest` takes the request's `rel`, and falls back to the quick switcher's list only for an older sidecar. The misleading comment goes.
3. **The verb is named.** `dispatchToAgent` records the verb it used, the note type's default when none was asked for, so the history no longer says "default".
4. **One history entry per dispatch.** The request no longer writes an entry of its own: it carried no agent, and the delivery writes the real one moments later. TST-0095 step 8 showed both (15:35:24 and 15:35:32).

Built and tested in [[TASK-0663-A-Cockpit-Dispatch-Request-Names-The-Notes-File]].
