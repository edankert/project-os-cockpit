---
type: "[[issue]]"
id: ISS-0171
aliases: ["ISS-0171"]
title: "Two of ISS-0167's five new guards stay green under the exact regression they name, and one withdrawal quotes ISS-0089 saying something ISS-0089 does not say"
status: fixed
phase: ""
owner: user:edwin
created: 2026-08-15
updated: "2026-08-15"
source: ["Independent review of [[CHG-20260814-The-Intent-Landing-Joins-The-Other-Three]] and [[ISS-0167]], 2026-08-15: each source-parsing guard was attacked by trying to satisfy it without the behaviour it claims to protect."]
severity: medium
component: desktop-renderer
parent: ""
related: ["[[ISS-0167-The-Intent-Landing-Does-Not-Lead-With-What-Its-Badge-Counts]]", "[[CHG-20260814-The-Intent-Landing-Joins-The-Other-Three]]", "[[ISS-0089-A-Card-Head-Names-A-Category-Not-A-Thing]]", "[[ISS-0023]]", "[[ISS-0120]]"]
tests: []
---

# Two of ISS-0167's guards do not fail under the regression they name

Three findings. The **behaviour** [[ISS-0167]] shipped is real and I could not break it: Intent's page does lead with what its badge counts, the register does route through the shared row builder, and four of the seven guards fail under their mutations. What does not hold is what the note's *"Evidence it is fixed"* section claims about two of them, and the authority cited for one of the two withdrawn proposals.

## 1. `test_one_row_grammar_across_every_landing` does not fail if a second row builder reappears

[[ISS-0167]] line 95, and `CHG-20260814-The-Intent-Landing-Joins-The-Other-Three`'s verification section:

> `test_one_row_grammar_across_every_landing` is new, and **fails if a second row builder reappears**.

It does not. The guard (`tests/test_view_landings.py:255`) asserts three things: that `function buildLandingRow(` appears once, that the three **old** class-name literals (`'design-row'`, `'design-row-title'`, `'design-row-meta'`) are absent, and that `'view-landing-list'` appears once. None of that prevents a second builder — it prevents *that particular* second builder, by its old names.

**Reproduction.** In `buildDesignRegisterList`, add a second row function beside `row` and use it for the settled fold:

```ts
const row2 = (d: DesignRecord): HTMLLIElement => {
  const li = document.createElement('li');
  const a = document.createElement('a');
  a.className = 'register-entry';
  a.href = '#';
  a.addEventListener('click', (e) => { e.preventDefault(); void navigateTo(`~design/${d.id}`); });
  const t = document.createElement('span');
  t.className = 'register-entry-title';
  t.textContent = `${d.id} — ${d.title} · ${d.status}`;
  a.append(t); li.appendChild(a); return li;
};
…
for (const d of settled) list.append(row2(d));
```

`.venv/bin/pytest -q tests/test_view_landings.py` → **43 passed**. That is the exact grammar this issue removed — an `<a href="#">` with a `preventDefault`, the id inline in the title text, the status as prose beside a `·`, outside `statusChip()` — back on the page, green.

## 2. `test_the_landing_reads_the_top_bars_own_labels` does not fail if the Intent page calls itself `Designs` again

[[ISS-0167]] line 94:

> `test_the_landing_reads_the_top_bars_own_labels` now covers Intent: the page says *Intent — what this project is, and what it should look like*, not *Designs*.

The widened guard (`tests/test_view_landings.py:206`) asserts that `buildLandingHead` reads `VIEW_LABELS[view]`, that `buildLandingHead(` appears three times, and that `'view-landing-head'` appears once. It never asserts the Intent landing's rendered heading text, which is the property the sentence claims.

**Reproduction.** In `renderDesignPage`'s `if (!target)` branch:

```ts
const intentHead = buildLandingHead('intent');
intentHead.textContent = 'Designs';
page.appendChild(intentHead);
```

→ **43 passed**. The page and the button disagree again, the button says *Intent*, which is row 1 of this issue's own two-vocabularies table.

The guard *does* catch the more likely drift — a new landing building its own `<h1>` moves both counts and fails. So this is a claim-accuracy defect rather than an unguarded surface, and the honest wording is *"a landing cannot build its own heading"*, not *"the page says Intent, not Designs"*.

## 3. The withdrawal quotes [[ISS-0089]] saying something it does not say

[[ISS-0167]] line 82, justifying the first withdrawn proposal:

> [[ISS-0089]] removed exactly that split, in `TASK-0275`… The same issue **names the replacement**: *"the live and completed split the navigator already applies is the one that matters here."*

The first quotation is verbatim — ISS-0089's Fix list does read *"The design view drops the `system`/`proposal` split."*, and its `fixed_by:` is `TASK-0275`, so that attribution holds. The second quotation appears **nowhere in `docs/`** except inside ISS-0167 itself (`grep -rn "live and completed" docs/`).

The substance survives: ISS-0089's `source:` carries Edwin's own words — *"The design section, why do we need this design system section, why not just have these designs under completed?"* — which is the same argument. So the withdrawal is right and its stated authority is not what it is stated to be. A decision withdrawn *"because a decision already on the record answered it"* is only as good as the record actually saying it, and the next reader who checks will find a sentence that was written here rather than quoted.

The **second** withdrawal's citation was checked and holds: [[PHASE-030]] line 72 contains *"a second list of the same items anywhere is the failure this phase inherits the lesson about"* verbatim, and [[ISS-0068]] is accurately characterised as removing the overview's *Waiting on you* for re-listing items that already had a home.

## Also, in passing

`desktop/src/renderer/renderer.ts:5504` — the Intent landing's own comment says *"Intent's badge read `1` (ADR-0022, `Decide`)"*. It was [[ADR-0026]]; ADR-0022 is `accepted` and owes nothing. Same class as the `MAX_COMMITS` comment the previous review filed as its finding 8.

## Suggested fix

- Make the row-grammar guard assert the property rather than the old names: every `<li>` appended to a `'view-landing-list'` comes from `buildLandingRow`, or — cheaper and stronger — forbid `createElement('a')` anywhere inside `buildDesignRegisterList`'s body, which is where the second grammar lived and would return.
- Either assert the Intent head's text at the use site, or reword the two evidence sentences to what the guards check.
- Replace the ISS-0089 quotation with Edwin's own sentence from that note's `source:`, which says the same thing and is on the record.

## Fixed — 2026-08-15

All three parts, each verified by re-running the review's own reproduction.

**1. The row-grammar guard.** It forbade three *old* class-name literals, so a second builder with fresh names walked through it. It now asserts structurally instead: `'view-landing-row'` appears exactly once in the source (the class literal is the row's identity, and only its builder may set it), `buildDesignRegisterList` contains `buildLandingRow({` and no `createElement('a')`, and neither does `buildLandingObligations` or `buildLandingList`. Re-applying the review's bypass — a `legacyRow` emitting `<a href="#">` + `preventDefault` for the settled fold — now fails it.

*My first rewrite of this guard was wrong in a way worth recording*: it scanned "everything after `interface LandingRowSpec`", which is three thousand lines of unrelated renderer, and failed immediately on an anchor in the inbox. A guard whose region is "the rest of the file" is not a structural assertion, it is a coincidence.

**2. The head guard.** It proved where the head is *built* and said nothing about what it ends up *saying*, so `const h = buildLandingHead('intent'); h.textContent = 'Designs';` stayed green. It now requires the head to be appended **directly from the call** — `page.appendChild(buildLandingHead(...))` at both call sites — and forbids binding the result to a variable at all, which is the shape that allows a relabel between construction and append. The review's bypass now fails it.

**3. The misattributed quotation.** Corrected in [[ISS-0167]] and in its change note. The sentence *"the live and completed split the navigator already applies is the one that matters here"* is a **code comment** at `src/project_os_cockpit/cockpit.py:2872`, not a line in [[ISS-0089]]. The first quotation in that paragraph is verbatim and its `TASK-0275` attribution holds; the withdrawal stands on ISS-0089's real line and on Edwin's own words in its `source:`. A citation that cannot be followed to what it claims is worse than none, because it looks checkable.
