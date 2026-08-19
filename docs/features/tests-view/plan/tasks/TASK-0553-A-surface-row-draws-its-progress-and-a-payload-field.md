---
type: "[[task]]"
id: TASK-0553
aliases: ["TASK-0553"]
title: "A surface row draws its progress, and a payload field no renderer reads is a failure"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0128-The-Tests-View-Leads-With-The-Work]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# [[ISS-0225]]

See the issue for the reasoning and the suggested fix; its `Done when` is this task's definition of done.

## Done 2026-08-19

The progress moved out of `subtitle` — documented as never rendered — into a `progress` key `buildNavRow` draws as `.ov-phase-under`, the 2px sliver the overview uses for a phase. **And the class is guarded**: `test_no_nav_payload_field_is_sent_and_never_drawn` walks every key the nav emits against the whole renderer. It found one on its first run that was not mine — [[ISS-0229]].
