---
type: "[[reference]]"
id: REFERENCE-ABSTRACTION-LEVELS-SCAN
aliases: ["REFERENCE-ABSTRACTION-LEVELS-SCAN"]
title: "How other tools cut a project into levels, and what of it applies to the cockpit"
status: active
owner: user:edwin
created: 2026-09-20
updated: 2026-09-20
scope: "project"
source:
  - "Edwin 2026-09-20: 'ideally you want to provide different levels of abstraction instead, where each level of abstraction gets you closer to the real content, the full ticket content ... Review research existing online solutions and suggest options and possible designs.'"
  - "Web search and vendor documentation read on 2026-09-20; every claim below carries the link it came from."
related:
  - "[[DES-0016-Levels-Of-Abstraction]]"
  - "[[DES-0015-The-Cockpit-In-Layers]]"
  - "[[PHASE-045-The-Cockpit-In-Layers]]"
  - "[[REFERENCE-FUTURE-COCKPIT-ENHANCEMENTS]]"
tags: [reference, research, levels, abstraction, navigation]
---

# How other tools cut a project into levels

## Purpose

This is the research behind [[DES-0016-Levels-Of-Abstraction]]. It records what six families of tools do about the same problem — one record, readers who need it at very different distances — so the design can borrow with a citation instead of inventing. It is a reading of public documentation on 2026-09-20, not a trial: nothing here was installed or measured.

Read the design for the proposal. Read this for why the proposal looks the way it does, and for the four traps it is deliberately avoiding.

## The six families

### 1. Work trackers that stack a hierarchy: Jira Align, Linear

Jira Align builds its levels out of the organisation chart. Enterprise contains portfolios, a portfolio contains programs (SAFe's release trains), a program contains teams, and the requirement hierarchy hangs off that. Its organisation report is a tree with an **"Expand/Collapse to Level"** control: you pick the level and the whole report collapses to it ([Jira Align: organizational hierarchy](https://help.jiraalign.com/hc/en-us/articles/360010921393-Organizational-hierarchy), [Jira Align organizational structure](https://help.jiraalign.com/hc/en-us/articles/115000152674-Jira-Align-organizational-structure)).

Linear stacks three levels of work instead of people — initiative, project, issue — and makes the roll-up automatic: issue completion rolls into project progress, project progress rolls into initiative progress, so the leadership view is a live rendering rather than a second thing to maintain. On top of that it adds a written update with a three-value health signal, **On track / At risk / Off track**, because progress alone does not say whether anyone is worried ([Linear: initiatives](https://linear.app/docs/initiatives), [Linear: initiative and project updates](https://linear.app/docs/initiative-and-project-updates), [Linear: project updates](https://linear.app/docs/project-updates)).

**Borrow:** one explicit control that says which level you are at, and roll-ups computed from the rows beneath rather than typed in by a person. **Avoid:** Jira Align's premise that the levels are the org chart. This fleet has one person; its levels have to be cut by question, not by reporting line.

### 2. Architecture diagrams that are defined by their audience: the C4 model

C4 is four diagrams of one system — system context, container, component, code — and its whole argument is that each is for a different reader: "tell different stories to different audiences", executives at context, developers at container and component ([The C4 model, InfoQ](https://www.infoq.com/articles/C4-architecture-model/), [Baeldung: C4 abstraction levels](https://www.baeldung.com/cs/c4-model-abstraction-levels), [Lucid: introduction to C4](https://lucid.co/blog/c4-model)). The levels are commonly described as country, city, neighbourhood and street view, and the rule is that you never explain everything in one overloaded diagram.

**Borrow:** the definition of a level. A level is a reader and a question, not a quantity of data. This is the single idea that separates DES-0016 from DES-0015, which cut the same material by payload size.

### 3. The visualization literature: Shneiderman's mantra

"Overview first, zoom and filter, then details-on-demand" is Shneiderman's 1996 formulation, and the paper that states it also lists seven tasks rather than three: overview, zoom, filter, details-on-demand, **relate, history and extract** ([The Eyes Have It, Shneiderman 1996 (PDF)](https://www.cs.umd.edu/~ben/papers/Shneiderman1996eyes.pdf), [Beyond guidelines: what can we learn from the Visual Information Seeking Mantra](https://www.researchgate.net/publication/4175429_Beyond_guidelines_What_can_we_learn_from_the_Visual_Information_Seeking_Mantra)).

**Borrow:** the three forgotten tasks. *Relate* is the cockpit's `[[wikilink]]` graph and it already works. *History* is the digest and the timeline. *Extract* — take this subset away with you — is the one the cockpit has nowhere, and it is what a walk sheet, a review packet and a release report each are. Naming it as a task at every level is cheaper than inventing a feature for each.

### 4. The dashboard taxonomy: strategic, tactical, operational, analytical

The business-intelligence literature has been splitting dashboards by decision horizon for years: strategic for the executive (outcomes, long horizon), tactical for the middle (initiatives over weeks and months), operational for activity in a single area, analytical for the person who will dig ([Yellowfin: operational, strategic or analytical](https://www.yellowfinbi.com/blog/operational-strategic-or-analytical-dashboard-which-type-best-for-bi), [Luzmo: dashboard types](https://www.luzmo.com/blog/dashboard-types-strategic-operational-tactical), [Domo: executive reporting dashboards](https://www.domo.com/learn/article/the-ultimate-guide-to-creating-executive-level-reporting-dashboards)). The design principle they all restate is progressive disclosure as **Summary → Segment → Detail**, each step answering a more specific question, with the reader choosing how deep to go ([Progressive disclosure in enterprise design](https://medium.com/@theuxarchitect/progressive-disclosure-in-enterprise-design-less-is-more-until-it-isnt-01c8c6b57da9), [UXPin: dashboard design principles](https://www.uxpin.com/studio/blog/dashboard-design-principles/)).

**Borrow:** Summary → Segment → Detail as the shape of every descent, and the executive rule that a strategic screen carries outcomes rather than activity. **Avoid:** the part of this literature that builds a separate dashboard per role. Four dashboards over one record is four things to keep true.

### 5. Operational drill-down: Grafana, Datadog, and the exemplar

Observability tools solved the hardest version of this problem: a number on a wall board and a billion raw events underneath it. Their ladder is metrics for "something is wrong", traces for "where", logs for "what happened", and the link between the levels is the **exemplar** — a pointer stored on the aggregate metric that names one trace id, so a latency spike opens the exact slow request ([Grafana Drilldown apps](https://grafana.com/blog/grafana-drilldown-apps-the-improved-queryless-experience-formerly-known-as-the-explore-apps/), [Grafana: traces and telemetry](https://grafana.com/docs/grafana/latest/visualizations/simplified-exploration/traces/concepts/telemetry/), [Datadog observability explained](https://technoroots.org/insights/datadog-observability-explained-metrics-logs-and-traces-and-how-they-work-8rM6B)). Grafana's newer "Drilldown" apps make the descent point-and-click, with no query language in the way.

**Borrow:** the exemplar, generalised into DES-0016's drill-down contract — a number at any level is the count of rows the next level can list, and clicking it lands on exactly those rows. This is the rule the cockpit's **Tests 1 / 90** tile breaks today.

### 6. Engineering intelligence, and agent traces

The engineering-metrics vendors have split precisely along the audience line. Jellyfish sells to VPs and CTOs and is built around investment allocation and board reporting; Swarmia deliberately optimises for team understanding over executive dashboards; LinearB sits between with manager metrics plus workflow automation ([LinearB vs Jellyfish vs Swarmia](https://wetheflywheel.com/en/comparisons/linearb-vs-jellyfish-vs-swarmia/), [LinearB vs Swarmia](https://pensero.ai/blog/linearb-vs-swarmia), [Top engineering intelligence platforms](https://uplevelteam.com/blog/top-engineering-intelligence-platforms)). The published comparisons also note what happens at the bottom of those ladders: team metrics are the default, but a manager can drill into an individual's activity.

Below even that, the agent-observability tools record what a machine did: LangSmith captures runs, traces and threads with step-level cost and latency across generations, tool calls and retrievals; Braintrust captures each tool call with name, arguments, return values, latency and retries, and lets you replay the trace ([Braintrust: agent observability guide 2026](https://www.braintrust.dev/articles/agent-observability-complete-guide-2026), [LangChain: LLM observability tools](https://www.langchain.com/resources/llm-observability-tools), [Best AI agent observability tools for coding teams](https://www.augmentcode.com/tools/best-ai-agent-observability-tools)).

**Borrow:** the shape of the cockpit's bottom level. The agent session already produces turns, tool calls, cost and context; treating it as a trace with a replay is a presentation of data the sidecar already holds. **Avoid:** the individual-drill-down habit. In a one-person fleet the "individual" is Edwin and the agents he runs, so the political hazard is absent — but the design hazard is not: a level that exists to watch effort rather than to check a claim will be read as noise and then ignored.

## What the scan changes in the proposal

Six rules taken, with the source that argues for each:

1. **A level is a reader and a question** (C4). Not a payload budget, which is what DES-0015 cut by.
2. **Roll-ups are computed, never typed** (Linear). The cockpit already derives everything from notes; the portfolio level must not introduce a status somebody maintains by hand.
3. **One explicit control names the level** (Jira Align's expand-to-level). Without it the reader knows where they are only by recognising the page.
4. **Summary → Segment → Detail on every descent** (the dashboard literature), with the corollary that the executive screen shows outcomes, not activity.
5. **Every aggregate carries its exemplar** (Grafana, Datadog). Restated as the drill-down contract in the design's Plate 7.
6. **Health is a word beside the bar** (Linear's On track / At risk / Off track). A percentage says how far; it never says whether anyone is worried.

Four traps to avoid, each of which some tool in this scan fell into:

1. **The org chart as the ladder** (Jira Align). Wrong shape for one person and thirteen repositories.
2. **A separate dashboard per role** (the BI taxonomy). One ladder with a remembered starting level costs less and cannot drift.
3. **Counting the record instead of the world.** Measured on 2026-09-20: the fleet holds 263 features at an active status against 13 focus items. A portfolio tile reading "263 in flight" would be arithmetically correct and practically false.
4. **Levels that measure effort** (the individual-drill-down habit). The bottom of this ladder exists so a claim can be checked, not so activity can be watched.

## Standing

Reference material. It records a reading, not a decision, and it goes stale as the products change — every claim is dated 2026-09-20 and carries its link, so a later reader can re-check rather than trust it.
