// The walk page, built from a real payload ([[TASK-0619]]).
//
// These run the REAL builders out of the built bundle against a minimal DOM,
// rather than asserting that a string appears in the TypeScript. Both design
// reviewers walked through a source-text guard independently and reached the
// same objection (ISS-0055): a rename or a hoist, and the guard still passes
// while the behaviour it names is gone.
//
// The three properties asserted here are the three the feature is *for*:
// every owed row appears exactly once, in payload order; the survey comes
// first; and a mark repaints one row and moves nothing else.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const builtRenderer = path.join(here, '..', 'dist', 'renderer', 'renderer.js');

async function source() {
  return fs.readFile(builtRenderer, 'utf8');
}

/** One function declaration, bounded by its own closing brace. */
function extract(src, name) {
  let start = src.indexOf(`function ${name}(`);
  assert.notEqual(start, -1, `${name} not found in the built renderer`);
  // Keep the `async` keyword. Slicing from `function` dropped it, and the
  // extracted body then held an `await` in a non-async function — a
  // SyntaxError at `new Function`, which reads as the test being broken
  // rather than as the extractor being wrong by one word.
  if (src.slice(start - 6, start) === 'async ') start -= 6;
  let depth = 0;
  let i = src.indexOf('{', src.indexOf(')', start));
  for (; i < src.length; i += 1) {
    if (src[i] === '{') depth += 1;
    else if (src[i] === '}') { depth -= 1; if (depth === 0) break; }
  }
  return src.slice(start, i + 1);
}

/** One top-level `const NAME = {…};`, so a function under test reads the real
 *  table rather than a copy of it (`markWord` reads `MARK_TITLE`). */
function extractConst(src, name) {
  const start = src.indexOf(`const ${name} =`);
  assert.notEqual(start, -1, `${name} not found in the built renderer`);
  let depth = 0;
  let i = src.indexOf('{', start);
  for (; i < src.length; i += 1) {
    if (src[i] === '{') depth += 1;
    else if (src[i] === '}') { depth -= 1; if (depth === 0) break; }
  }
  return src.slice(start, src.indexOf(';', i) + 1);
}

// --------------------------------------------------------------- a tiny DOM

function makeDom() {
  const byId = new Map();
  function el(tag) {
    const node = {
      tagName: tag.toUpperCase(),
      children: [],
      parent: null,
      _text: '',
      className: '',
      title: '',
      type: '',
      hidden: false,
      style: {},
      dataset: {},
      listeners: {},
      get id() { return this._id || ''; },
      set id(v) { this._id = v; byId.set(v, this); },
      get textContent() {
        return [this._text, ...this.children.map((c) => c.textContent)]
          .filter(Boolean).join(' ');
      },
      set textContent(v) { this._text = String(v); this.children = []; },
      get classList() {
        const self = this;
        return {
          add(...names) {
            const have = self.className.split(' ').filter(Boolean);
            for (const n of names) if (!have.includes(n)) have.push(n);
            self.className = have.join(' ');
          },
          contains(n) { return self.className.split(' ').includes(n); },
          toggle(n) {
            if (this.contains(n)) {
              self.className = self.className.split(' ')
                .filter((x) => x !== n).join(' ');
            } else this.add(n);
          },
        };
      },
      appendChild(child) {
        child.parent = node;
        node.children.push(child);
        return child;
      },
      append(...kids) { for (const k of kids) node.appendChild(k); },
      replaceChildren(...kids) {
        node.children = [];
        for (const k of kids) node.appendChild(k);
      },
      insertBefore(child, ref) {
        const at = ref ? node.children.indexOf(ref) : -1;
        child.parent = node;
        if (at === -1) node.children.push(child);
        else node.children.splice(at, 0, child);
        return child;
      },
      replaceWith(other) {
        const at = node.parent ? node.parent.children.indexOf(node) : -1;
        assert.notEqual(at, -1, 'replaceWith on a detached node');
        other.parent = node.parent;
        node.parent.children[at] = other;
      },
      setAttribute(k, v) { node.dataset[k] = v; },
      addEventListener(kind, fn) {
        (node.listeners[kind] ||= []).push(fn);
      },
      click() { for (const fn of node.listeners.click || []) fn({}); },
      querySelector(sel) {
        const want = sel.split(' ').pop().replace(/^\./, '');
        const stack = [...node.children];
        while (stack.length) {
          const n = stack.shift();
          if (n.className.split(' ').includes(want)) return n;
          stack.push(...n.children);
        }
        return null;
      },
      querySelectorAll(sel) {
        const want = sel.split(' ').pop().replace(/^\./, '');
        const found = [];
        const stack = [...node.children];
        while (stack.length) {
          const n = stack.shift();
          if (n.className.split(' ').includes(want)) found.push(n);
          stack.push(...n.children);
        }
        return found;
      },
    };
    return node;
  }
  return {
    createElement: el,
    getElementById: (id) => byId.get(id) || null,
  };
}

/** Everything under `root` whose class list holds `cls`, in document order. */
function all(root, cls) {
  const out = [];
  const visit = (n) => {
    if (n.className.split(' ').includes(cls)) out.push(n);
    for (const c of n.children) visit(c);
  };
  visit(root);
  return out;
}

// ---------------------------------------------------------------- the wiring

const NAMES = [
  'buildWalkPage', 'buildSittingSection', 'buildWalkRow', 'buildSurveySection',
  'decideFallbackWalkCheck',
  'buildWalkReview',
  'walkNotice', 'walkBlock', 'walkRowId', 'walkLink', 'buildWalkRefusal',
  // The script (PHASE-044). `buildSurveySection` and `buildSittingSection`
  // call into these, so the page cannot be built without them.
  'buildSurveyCard', 'buildSurveyCaptures', 'walkCaptureSrc', 'walkDocsRel',
  'readProcedure', 'buildProcedureSection', 'buildWalkStep', 'buildStepTick',
  'buildProcedureVerdicts', 'walkLineText', 'walkSetupBody', 'walkTagLabel', 'combineStepMarks',
  'stepMarkKey', 'stepSignature', 'walkStepsKey', 'loadStepMarks',
  'saveStepMarks', 'walkFocusKey', 'loadWalkFocus', 'saveWalkFocus',
  'decideUnavailableWalkCheck',
  'walkEvidenceKey', 'loadWalkEvidence', 'saveWalkEvidence', 'evidenceKey',
  'walkBuildHint', 'saveCurrentWalkEvidence', 'walkEvidenceOwner', 'attachWalkEvidenceImage',
  'walkLedgerEvidence',
  'buildWalkEvidence', 'hasRequiredWalkEvidence', 'walkStepNeedsLedgerRetry', 'buildWalkTimer',
  'refreshWalkEvidenceComparisons',
  'walkInvalidationEpoch', 'archiveWalkMark',
  'walkReadyKey', 'loadWalkReady', 'saveWalkReady', 'walkUnready', 'walkCheckHeld',
  'waitingSteps', 'walkProcedureId', 'walkStepId', 'walkVerdictsId',
  'walkFocusAt', 'resolveWalkStep', 'walkStepPosition', 'walkKeyNavigation',
  'buildWalkResume', 'buildWalkAttention', 'walkEvidenceChecks', 'walkEvidenceStale',
  'walkEarlierObservation', 'walkProblemsSoFar', 'markWord',
];

async function load({ document, navigateTo = () => {}, marks = [] } = {}) {
  const src = await source();
  const bodies = [...NAMES.map((n) => extract(src, n)), extractConst(src, 'MARK_TITLE')].join('\n');
  // `buildCheckRow` is the checks page's row and is exercised by its own
  // tests; here it is a stub that records which check it was asked to draw,
  // so the assertions are about the WALK's ordering and not about the row.
  const stub = `
function buildCheckRow(item, manual, controls, onMark) {
  const row = document.createElement('div');
  row.className = 'checks-row';
  row.dataset.check = item.id || item.number;
  row.dataset.controls = controls;
  row.addEventListener('click', () => onMark(item));
  return row;
}
function openWalkNote(id) { navigateTo('note:' + id); }
async function markWalkRow(item) { marks.push(item.id); }
async function markWalkStep() {}
let activeWalkFocus = null;
let walkStorageUnsafe = false;
let walkData = null;
function showStatus() {}
const sidecarBaseUrl = 'http://127.0.0.1:7777';
const activeId = 'ws-1';
const localStorage = {
  getItem: () => null, setItem: () => {}, removeItem: () => {},
};
`;
  const fn = new Function(
    'document', 'navigateTo', 'marks',
    `${stub}\n${bodies}\nreturn { ${NAMES.join(', ')} };`,
  );
  return fn(document, navigateTo, marks);
}

// ---------------------------------------------------------------- fixtures

function payload(over = {}) {
  return {
    platform: 'android',
    release: 'REL-0017',
    gallery: null,
    survey: [],
    sittings: [
      {
        name: 'A fresh install',
        state: 'the app installed and never opened',
        bench: ['a wiped phone'],
        surfaces: ['Profile'], checks: [],
        rows: [row('TST-0001'), row('TST-0002')],
      },
      {
        name: 'Riding',
        state: '', bench: [], surfaces: ['Riding'], checks: [],
        rows: [row('TST-0003')],
      },
    ],
    unplaced: [],
    counts: { owed: 3, placed: 3, unplaced: 0 },
    order_source: 'walk.md',
    walk_rel: 'tests/acceptance/WALK.md',
    template_rel: '__templates__/walk.md',
    errors: [], warnings: [], notices: [],
    ...over,
  };
}

function row(id, over = {}) {
  return {
    id, number: id, name: `Check ${id}`, area: 'Profile', mark: 'todo',
    rel: `tests/acceptance/${id}.md`, refs: [],
    setup: 'A signed-out app.', steps: '1. Tap it.', expect: 'It opens.',
    lead: null, after: [], ...over,
  };
}

// ------------------------------------------------------------------- tests

test('every owed row is rendered exactly once, in payload order', async () => {
  const document = makeDom();
  const { buildWalkPage } = await load({ document });
  const page = buildWalkPage(payload());
  const drawn = all(page, 'checks-row').map((n) => n.dataset.check);
  assert.deepEqual(drawn, ['TST-0001', 'TST-0002', 'TST-0003']);
});

test('the survey is the first section on the page', async () => {
  const document = makeDom();
  const { buildWalkPage } = await load({ document });
  const page = buildWalkPage(payload({
    survey: [{
      surface: 'Profile', surface_note: 'SUR-0001', parent: null,
      unresolved: false, captures: [],
      changes: [{ id: 'CHG-1', title: 'The profile moves',
        sentence: 'the sign-in button sits under the avatar now.' }],
    }],
  }));
  const sections = page.children.filter(
    (c) => c.className.includes('walk-survey')
      || c.className.includes('walk-sittings'));
  assert.equal(sections[0].className, 'walk-survey');
  const said = all(page, 'walk-survey-sentence');
  assert.equal(said.length, 1);
  assert.equal(said[0].textContent,
    'the sign-in button sits under the avatar now.');
});

test('the survey names no check', async () => {
  // Rule 2: a list of places to open, not a list of things to run.
  const document = makeDom();
  const { buildSurveySection } = await load({ document });
  const section = buildSurveySection(payload({
    survey: [{
      surface: 'Profile', surface_note: 'SUR-0001', parent: null,
      unresolved: false, captures: [],
      changes: [{ id: 'CHG-1', title: 'It moved', sentence: 'the avatar moved.' }],
    }],
  }));
  assert.equal(all(section, 'checks-chip').length, 0);
  assert.ok(!section.textContent.includes('TST-'));
});

test('a screen no surface note carries is named, never dropped', async () => {
  const document = makeDom();
  const { buildSurveySection } = await load({ document });
  const section = buildSurveySection(payload({
    survey: [{
      surface: 'SUR-9999', surface_note: 'SUR-9999', parent: null,
      unresolved: true, captures: [],
      changes: [{ id: 'CHG-1', title: null, sentence: 'something moved.' }],
    }],
  }));
  assert.equal(all(section, 'walk-survey-unresolved').length, 1);
  assert.match(all(section, 'walk-survey-cause')[0].textContent, /CHG-1/);
});

test('a screen captured before and now shows both pictures', async () => {
  const document = makeDom();
  const { buildSurveySection } = await load({ document });
  const section = buildSurveySection(payload({
    survey: [{
      surface: 'Profile', surface_note: 'SUR-0001', parent: null,
      unresolved: false,
      changes: [{ id: 'CHG-1', title: 'It moved', sentence: 'the avatar moved.' }],
      captures: [
        { key: 'profile', state: null, before: 'a/v1.0/profile.png',
          after: 'a/candidate/profile.png', new: false },
        { key: 'profile-pro', state: 'pro', before: null,
          after: 'a/candidate/profile-pro.png', new: true },
      ],
    }],
  }));
  const shots = all(section, 'walk-survey-capture');
  assert.equal(shots.length, 3);
  assert.match(all(section, 'walk-survey-capture-key')[1].textContent, /new/);
});

test('the survey says why it has no release to compare against', async () => {
  const document = makeDom();
  const { buildSurveySection } = await load({ document });
  const section = buildSurveySection(payload({
    survey: [], survey_problem: 'the tag `v1.0` is not in this checkout',
  }));
  assert.match(all(section, 'walk-survey-problem')[0].textContent, /v1\.0/);
  assert.match(all(section, 'empty-note')[0].textContent,
    /Changed-screen review is unavailable/);
  assert.doesNotMatch(all(section, 'empty-note')[0].textContent,
    /altered no screen/);
});

test('the gallery command is printed verbatim', async () => {
  const document = makeDom();
  const { buildSurveySection } = await load({ document });
  const section = buildSurveySection(payload({ gallery: './gradlew shots' }));
  assert.match(all(section, 'walk-gallery')[0].textContent, /\.\/gradlew shots/);
});

test('a sitting prints the state it needs and what is on the bench', async () => {
  const document = makeDom();
  const { buildWalkPage } = await load({ document });
  const page = buildWalkPage(payload());
  const states = all(page, 'walk-sitting-state');
  assert.equal(states.length, 1, 'only the sitting that states one says so');
  assert.match(states[0].textContent, /installed and never opened/);
  assert.equal(all(page, 'walk-bench')[0].children.length, 1);
});

test('a row carries the check\'s setup, steps and expected result', async () => {
  const document = makeDom();
  const { buildWalkRow } = await load({ document });
  const el = buildWalkRow(row('TST-0001'));
  const text = all(el, 'walk-proc-text').map((n) => n.textContent);
  assert.deepEqual(text, ['A signed-out app.', '1. Tap it.', 'It opens.']);
});

test('a note with no headings says so and prints its own prose', async () => {
  const document = makeDom();
  const { buildWalkRow } = await load({ document });
  const el = buildWalkRow(row('TST-0001', {
    setup: null, steps: null, expect: null,
    lead: 'Open the app and look at the splash screen.',
  }));
  const blocks = all(el, 'walk-proc-block');
  assert.match(blocks[0].textContent, /not stated/);
  assert.match(blocks[1].textContent, /Open the app and look/);
  assert.match(blocks[1].textContent, /no steps/);
  //: Every block that is missing something offers the note, because writing
  //: it is the fix.
  assert.ok(all(el, 'file-row').length >= 2);
});

test('a row that states all three says nothing about anything missing',
  async () => {
    //: The first cut used one sentence for both *"the note has none"* and
    //: *"this is not what the heading asked for"*, so a check whose Setup is
    //: written in full carried the line **"Setup: not stated"** underneath
    //: it. Found on `TST-0088`'s own row while walking it.
    const document = makeDom();
    const { buildWalkRow } = await load({ document });
    const el = buildWalkRow(row('TST-0001'));
    assert.equal(all(el, 'walk-proc-why').length, 0);
    assert.equal(all(el, 'walk-proc-block').filter(
      (b) => b.classList.contains('is-partial')
        || b.classList.contains('is-missing')).length, 0);
    //: …and no button offering the note, which on a complete row would be
    //: its id printed a second time under its own procedure.
    assert.equal(all(el, 'file-row').length, 0);
  });

test('no row and no heading mentions a time', async () => {
  const document = makeDom();
  const { buildWalkPage } = await load({ document });
  const page = buildWalkPage(payload());
  const words = /\b(minute|minutes|duration|estimate|eta|hours?)\b/i;
  const visit = (n) => {
    if (!n.children.length && words.test(n.textContent)) {
      assert.fail(`the walk page printed a time: ${n.textContent}`);
    }
    for (const c of n.children) visit(c);
  };
  visit(page);
});

test('a repo with no walk order is told, and pointed at the template', async () => {
  const document = makeDom();
  const opened = [];
  const { buildWalkPage } = await load({
    document, navigateTo: (rel) => opened.push(rel),
  });
  const page = buildWalkPage(payload({ order_source: 'fallback' }));
  const banner = all(page, 'walk-banner')[0];
  assert.ok(banner, 'no banner on an unordered walk');
  assert.match(banner.textContent, /Unordered/);
  all(banner, 'file-row')[0].click();
  assert.deepEqual(opened, ['/docs/__templates__/walk.md']);
});

test('an authored order draws no banner', async () => {
  const document = makeDom();
  const { buildWalkPage } = await load({ document });
  assert.equal(all(buildWalkPage(payload()), 'walk-banner').length, 0);
});

test('an ordering cycle is reported on the page', async () => {
  const document = makeDom();
  const { buildWalkPage } = await load({ document });
  const page = buildWalkPage(payload({
    errors: ['Riding: `after:` forms a cycle over TST-0003, TST-0004'],
    warnings: ['the sitting "Empty" names neither `surfaces` nor `checks`'],
  }));
  const notices = all(page, 'walk-notice');
  assert.equal(notices.length, 2);
  assert.ok(notices[0].classList.contains('is-error'));
  assert.ok(notices[1].classList.contains('is-warn'));
});

test('nothing owed says so instead of drawing an empty walk', async () => {
  const document = makeDom();
  const { buildWalkPage } = await load({ document });
  const page = buildWalkPage(payload({
    sittings: [], unplaced: [], counts: { owed: 0, placed: 0, unplaced: 0 },
  }));
  assert.equal(all(page, 'checks-row').length, 0);
  assert.match(page.textContent, /Nothing is owed on android/);
});

test('unplaced rows are last, and say whose worklist they are', async () => {
  const document = makeDom();
  const { buildWalkPage } = await load({ document });
  const page = buildWalkPage(payload({
    unplaced: [row('TST-0009')],
    counts: { owed: 4, placed: 3, unplaced: 1 },
  }));
  const drawn = all(page, 'checks-row').map((n) => n.dataset.check);
  assert.equal(drawn[drawn.length - 1], 'TST-0009');
  assert.match(page.textContent, /walk order’s worklist/);
});

test('a row addresses itself, so a repaint can replace one element', async () => {
  const document = makeDom();
  const { buildWalkRow, walkRowId } = await load({ document });
  const el = buildWalkRow(row('TST-0001'));
  assert.equal(el.id, walkRowId('TST-0001'));
  assert.equal(walkRowId('TST-0001'), 'walk-row-TST-0001');
});

test('marking a row calls the walk\'s own handler, not the checks page\'s',
  async () => {
    const document = makeDom();
    const marks = [];
    const { buildWalkRow } = await load({ document, marks });
    const el = buildWalkRow(row('TST-0001'));
    all(el, 'checks-row')[0].click();
    await new Promise((r) => setTimeout(r, 0));
    assert.deepEqual(marks, ['TST-0001']);
  });

test('the walk address is built in one place', async () => {
  const document = makeDom();
  const { walkLink } = await load({ document });
  assert.equal(walkLink('android'), '~walk/android');
  assert.equal(walkLink('Android'), '~walk/android');
  assert.equal(walkLink(''), '~walk');
  //: A platform name becomes a path segment, so it is encoded here rather
  //: than at the three call sites.
  assert.equal(walkLink('web app'), '~walk/web%20app');
});

test('a refused walk renders the reason and the platforms that exist',
  async () => {
    const document = makeDom();
    const opened = [];
    const { buildWalkRefusal } = await load({
      document, navigateTo: (rel) => opened.push(rel),
    });
    const page = buildWalkRefusal('all', {
      error: 'a walk is on one platform. Ask for one of: android, ios',
      platforms: ['android', 'ios'],
    });
    assert.match(page.textContent, /one platform/);
    const buttons = all(page, 'file-row');
    assert.equal(buttons.length, 2);
    buttons[1].click();
    assert.deepEqual(opened, ['~walk/ios']);
  });

// ---------------------------------------------------- the repaint after a mark
//
// **The property the page is for.** TASK-0556 recorded Edwin's rule for
// `~checks`: *"a list that reorders itself as you tick things is one you lose
// your place in."* The walk goes further — a ticked row keeps its element's
// position, and every other row keeps its element, so nothing under the
// reader's cursor moves.

async function loadRepaint({ document, fresh, walkData }) {
  const src = await source();
  const bodies = [...[...NAMES, 'repaintWalkRow'].map((n) => extract(src, n)),
    extractConst(src, 'MARK_TITLE')].join('\n');
  const stub = `
function buildCheckRow(item, manual, controls, onMark) {
  const row = document.createElement('div');
  row.className = 'checks-row';
  row.dataset.check = item.id || item.number;
  row.dataset.mark = item.mark;
  return row;
}
function openWalkNote() {}
async function markWalkRow() {}
const activeId = 'ws-1';
let activeWalkFocus = null;
const localStorage = { getItem: () => null, setItem: () => {} };
function showStatus() {}
`;
  const fn = new Function(
    'document', 'navigateTo', 'fetch', 'sidecarBaseUrl', 'walkData',
    'checksHistory',
    `${stub}\n${bodies}\nreturn { repaintWalkRow, buildWalkPage, walkRowId };`,
  );
  return fn(
    document, () => {}, async () => ({ ok: true, json: async () => fresh }),
    'http://127.0.0.1:1', walkData, {},
  );
}

test('a repaint replaces one row and rebuilds no sitting', async () => {
  const document = makeDom();
  const before = payload();
  //: The same payload with TST-0002 failed rather than owed. It is still on
  //: the list, so the fresh payload still carries it.
  const after = payload();
  after.sittings[0].rows[1] = row('TST-0002', { mark: 'failed' });

  const { repaintWalkRow, buildWalkPage } = await loadRepaint({
    document, fresh: after, walkData: before,
  });
  const page = buildWalkPage(before);
  const sittings = all(page, 'walk-sitting');
  const kept = all(page, 'walk-row').map((n) => n.id);

  assert.equal(await repaintWalkRow('TST-0002'), true);

  //: Same sitting elements, same row ids, same order. A rebuild would give
  //: new objects for all of them.
  assert.deepEqual(all(page, 'walk-sitting'), sittings);
  assert.deepEqual(all(page, 'walk-row').map((n) => n.id), kept);
  assert.deepEqual(all(page, 'checks-row').map((n) => n.dataset.check),
                   ['TST-0001', 'TST-0002', 'TST-0003']);
});

test('a row that has left the owed set keeps its place and is marked walked',
  async () => {
    //: The common tick is a `pass`, which removes the check from
    //: `ledger.owed` — so the fresh payload no longer carries it. Rebuilding
    //: from that payload would make the row the walker just ticked vanish
    //: under their cursor, and they would have no way to tell a landed tick
    //: from a lost one.
    const document = makeDom();
    const before = payload();
    const after = payload();
    after.sittings[0].rows = [row('TST-0001')];
    after.counts = { owed: 2, placed: 2, unplaced: 0 };

    const { repaintWalkRow, buildWalkPage, walkRowId } = await loadRepaint({
      document, fresh: after, walkData: before,
    });
    const page = buildWalkPage(before);
    assert.equal(await repaintWalkRow(
      'TST-0002', { verdict: 'pass', reason: '' }), true);

    const still = all(page, 'checks-row').map((n) => n.dataset.check);
    assert.deepEqual(still, ['TST-0001', 'TST-0002', 'TST-0003']);
    const el = document.getElementById(walkRowId('TST-0002'));
    assert.ok(el.classList.contains('is-walked'));
    //: …and it says what was recorded. Without the verdict travelling with
    //: the repaint the row kept the `[ ]` the fetched payload was built with
    //: — *nobody has walked this*, on the row just walked. Seen live while
    //: walking TST-0088.
    assert.equal(all(el, 'checks-row')[0].dataset.mark, 'pass');
  });

// ------------------------------------------------- whose ledger a tick lands in
//
// **The defect this pins is invisible on a one-ledger repo, and silent on a
// two-ledger one.** `walkOneCheck` used to take the platform from the nav
// picker. A walk is one platform by construction — it is in the address — so
// with the picker on `ios`, a tick on `~walk/android` wrote the Android walk's
// verdict into the iOS ledger and the row redrew as still owed, with no error.
// Found by independent review, 2026-09-13.

async function loadMark({ posts, picker, ledgers, walkData }) {
  const src = await source();
  const bodies = ['postCheckVerdict', 'walkOneCheck', 'markWalkRow']
    .map((n) => extract(src, n)).join('\n');
  const stub = `
async function askForMark() { return { verdict: 'pass', reason: 'held' }; }
async function postJson(path, body) { posts.push({ path, body }); return {}; }
function showStatus() {}
function scheduleHide() {}
function verdictPlatform() {
  if (picker && picker !== 'all') return picker;
  return ledgers.length === 1 ? ledgers[0] : '';
}
async function repaintWalkRow() { return true; }
const docView = { scrollTop: 0 };
const requestAnimationFrame = (fn) => fn();
const checksHistory = {};
`;
  const fn = new Function(
    'posts', 'picker', 'ledgers', 'walkData',
    `${stub}\n${bodies}\nreturn { markWalkRow };`,
  );
  return fn(posts, picker, ledgers, walkData);
}

test('a tick on the walk is recorded against the walk\'s own platform',
  async () => {
    const posts = [];
    const { markWalkRow } = await loadMark({
      posts, picker: 'ios', ledgers: ['android', 'ios'],
      walkData: { platform: 'android' },
    });
    await markWalkRow({ id: 'TST-0001', number: 'TST-0001', name: 'C', mark: 'todo' });
    assert.equal(posts.length, 1);
    assert.equal(posts[0].path, '/api/notes/mark-check');
    assert.equal(posts[0].body.platform, 'android',
      'the nav picker won over the address the walk was opened at');
    assert.equal(posts[0].body.verdict, 'pass');
  });

test('the walk does not need the checks page to have been opened first',
  async () => {
    //: `ledgerPlatforms` is filled in by `renderChecksPage`. A walker who
    //: arrives from the publication ladder has not been there, so the picker
    //: fallback returned `''` — and the server refuses a mark that names no
    //: platform, on the one page the whole feature exists for.
    const posts = [];
    const { markWalkRow } = await loadMark({
      posts, picker: 'all', ledgers: [], walkData: { platform: 'macos' },
    });
    await markWalkRow({ id: 'TST-0001', number: 'TST-0001', name: 'C', mark: 'todo' });
    assert.equal(posts[0].body.platform, 'macos');
  });

test('unplaced rows say something a reader can act on in either order',
  async () => {
    const document = makeDom();
    const { buildWalkPage } = await load({ document });
    const authored = buildWalkPage(payload({
      unplaced: [row('TST-0009')],
      counts: { owed: 4, placed: 3, unplaced: 1 },
    }));
    assert.match(authored.textContent, /walk order’s worklist/);
    const fallback = buildWalkPage(payload({
      order_source: 'fallback',
      unplaced: [row('TST-0009', { area: '' })],
      counts: { owed: 4, placed: 3, unplaced: 1 },
    }));
    //: With no walk order there is no sitting to add, so the page must not
    //: send the reader to a file that does not exist.
    assert.ok(!/add a sitting/.test(fallback.textContent));
    assert.match(fallback.textContent, /name no surface in `area:`/);
  });

// ===========================================================================
// The walk page reads as a script (PHASE-044 / FEAT-0150).
//
// Three properties, and they are the three the phase is *for*: a sitting with
// a written procedure draws the setup once instead of once per check; a tick
// goes on a step; and walking a sitting step by step writes the same ledger
// events, check for check and mark for mark, as ticking each of its checks
// one by one on FEAT-0149's page.
//
// The third is asserted by running BOTH paths against the same stubbed POST
// and comparing the bodies — not by computing the expected bodies the same
// way the code under test does, which would pass however wrong the combine
// rule was.
// ===========================================================================

const PROC_NAMES = [
  'buildProcedureSection', 'buildWalkStep', 'buildStepTick',
  'buildProcedureVerdicts', 'buildSurveyCard', 'buildSurveyCaptures',
  'buildSurveySection', 'buildSittingSection', 'buildWalkRow', 'buildWalkPage',
  'decideFallbackWalkCheck',
  'buildWalkReview',
  'walkNotice', 'walkBlock', 'walkRowId', 'readProcedure', 'combineStepMarks',
  'stepMarkKey', 'stepSignature', 'walkStepsKey', 'loadStepMarks',
  'saveStepMarks', 'pruneStepMarks', 'waitingSteps', 'walkLineText', 'walkSetupBody', 'walkVisibleAction',
  'walkCompletedKey', 'loadWalkCompleted', 'rememberWalkCompleted', 'walkQuery',
  'walkTagLabel',
  'walkDocsRel', 'walkCaptureSrc', 'walkProcedureId', 'walkStepId',
  'walkVerdictsId', 'markWalkStep', 'postCheckVerdict', 'walkOneCheck',
  'walkFocusKey', 'loadWalkFocus', 'saveWalkFocus', 'advanceWalkFocus',
  'decideUnavailableWalkCheck',
  'walkEvidenceKey', 'loadWalkEvidence', 'saveWalkEvidence', 'evidenceKey',
  'walkBuildHint', 'saveCurrentWalkEvidence', 'walkEvidenceOwner', 'attachWalkEvidenceImage',
  'walkLedgerEvidence',
  'buildWalkEvidence', 'hasRequiredWalkEvidence', 'walkStepNeedsLedgerRetry', 'buildWalkTimer',
  'refreshWalkEvidenceComparisons',
  'walkInvalidationEpoch', 'archiveWalkMark',
  'walkReadyKey', 'loadWalkReady', 'saveWalkReady', 'walkUnready', 'walkCheckHeld',
  'walkFocusAt', 'resolveWalkStep', 'walkStepPosition', 'walkKeyNavigation',
  'buildWalkResume', 'buildWalkAttention', 'walkEvidenceChecks', 'walkEvidenceStale',
  'walkEarlierObservation', 'walkProblemsSoFar', 'markWord',
];

/** A localStorage that behaves like one, including a JSON round trip. */
function makeStorage(seed = {}) {
  const box = new Map(Object.entries(seed));
  return {
    getItem: (k) => (box.has(k) ? box.get(k) : null),
    setItem: (k, v) => { box.set(k, String(v)); },
    removeItem: (k) => { box.delete(k); },
    _box: box,
  };
}

async function loadProc({
  document, posts = [], verdicts = [], localStorage = makeStorage(),
  navigateTo = () => {}, sidecarBaseUrl = 'http://127.0.0.1:7777',
  activeId = 'ws-1', asks = [], statuses = [], postFailures = { remaining: 0 },
  attachmentResponse = null,
  initialWalkData = null,
} = {}) {
  const src = await source();
  const bodies = [...PROC_NAMES.map((n) => extract(src, n)), extractConst(src, 'MARK_TITLE')].join('\n');
  const stub = `
function buildCheckRow(item, manual, controls, onMark) {
  const row = document.createElement('div');
  row.className = 'checks-row';
  row.dataset.check = item.id || item.number;
  row.dataset.controls = controls;
  return row;
}
function openWalkNote(id) { navigateTo('note:' + id); }
async function markWalkRow() {}
async function postJson(path, body) {
  if (postFailures.remaining > 0) {
    postFailures.remaining -= 1;
    throw new Error('offline');
  }
  posts.push({ path, body });
  if (path === '/api/notes/attach') return attachmentResponse || {};
  return {};
}
function showStatus(message, kind) { statuses.push({ message, kind }); }
function scheduleHide() {}
async function askForMark(opts) {
  asks.push(opts);
  const said = verdicts.shift();
  return said === undefined ? null : said;
}
async function repaintWalkProcedure() { return true; }
async function repaintWalkRow() { return true; }
async function renderWalkPage() { return true; }
const STEP_MARK_CHOICES = ['pass', 'partial', 'fail', 'question'];
const docView = { scrollTop: 0 };
const requestAnimationFrame = (fn) => fn();
let checksHistory = {};
let walkData = initialWalkData;
let activeWalkFocus = null;
let walkStorageUnsafe = false;
const walkTimers = new Map();
const window = globalThis;
`;
  const fn = new Function(
    'document', 'navigateTo', 'posts', 'verdicts', 'localStorage',
    'sidecarBaseUrl', 'activeId', 'asks', 'statuses', 'postFailures',
    'attachmentResponse', 'initialWalkData',
    `${stub}\n${bodies}\nreturn { ${PROC_NAMES.join(', ')} };`,
  );
  return fn(document, navigateTo, posts, verdicts, localStorage,
            sidecarBaseUrl, activeId, asks, statuses, postFailures,
            attachmentResponse, initialWalkData);
}

/** A fixture sitting whose procedure has four steps citing three checks.
 *
 *  `TST-0001` states two steps and is cited by steps 1 and 3, so it is the
 *  check that proves a verdict waits for every citing tick. `TST-0002` is
 *  cited once. `TST-0003` states no numbered steps at all, so it is one owed
 *  part cited by its bare id — the shape 53 of `your-trainer`'s 61 rows are
 *  in. Step 4 also carries a tag that has already been walked. */
function procedureSitting(over = {}) {
  return {
    name: 'A fresh install',
    state: 'the app installed and never opened',
    bench: ['a wiped phone'],
    surfaces: ['Profile'], checks: [],
    rows: [row('TST-0001'), row('TST-0002'), row('TST-0003')],
    procedure: {
      path: 'docs/tests/acceptance/walk/fresh-install.md',
      sitting: 'A fresh install',
      setup: 'A wiped phone with the candidate build sideloaded.',
      problems: [], remarks: [], omitted: 2,
      owed_checks: ['TST-0001', 'TST-0002', 'TST-0003'],
      steps: [
        { number: 1, head: 'Open the app on the Profile screen.',
          surface: 'Profile', surface_note: 'SUR-0001',
          lines: [
            { text: '1. Open the app on the Profile screen.', tags: [] },
            { text: '   - The avatar sits above the name. `TST-0001.1`',
              quote: 'The avatar sits above the name.',
              tags: [{ check: 'TST-0001', step: '1', owed: true }] },
          ] },
        { number: 2, head: 'Tap Settings.', surface: 'Settings',
          surface_note: 'SUR-0002',
          lines: [
            { text: '2. Tap Settings.', tags: [] },
            { text: '   - The sheet opens from the bottom. `TST-0002.1`',
              quote: 'The sheet opens from the bottom.',
              tags: [{ check: 'TST-0002', step: '1', owed: true }] },
          ] },
        { number: 3, head: 'Go back.', surface: null, surface_note: null,
          lines: [
            { text: '3. Go back. `TST-0001.2`', quote: 'Go back.',
              tags: [{ check: 'TST-0001', step: '2', owed: true }] },
          ] },
        { number: 4, head: 'Close the app.', surface: 'Profile',
          surface_note: 'SUR-0001',
          lines: [
            { text: '4. Close the app.', tags: [] },
            { text: '   - Nothing is left running. `TST-0003` `TST-0004.1`',
              quote: 'Nothing is left running.',
              tags: [{ check: 'TST-0003', step: null, owed: true },
                     { check: 'TST-0004', step: '1', owed: false }] },
          ] },
      ],
    },
    ...over,
  };
}

function procedurePayload(over = {}) {
  return payload({
    sittings: [procedureSitting()],
    counts: { owed: 3, placed: 3, unplaced: 0 },
    ...over,
  });
}

// ------------------------------------------------ TASK-0623: the procedure

test('a sitting with a procedure states its setup once, not once per check',
  async () => {
    const document = makeDom();
    const { buildWalkPage } = await loadProc({ document });
    const page = buildWalkPage(procedurePayload());
    //: Three checks in this sitting. Drawn as rows that is three Setup
    //: blocks; drawn as the script it is one.
    const setups = all(page, 'walk-proc-text')
      .filter((n) => n.textContent.includes('wiped phone'));
    assert.equal(setups.length, 1);
    assert.equal(all(page, 'checks-row').length, 0,
      'a scripted sitting draws the script, not the per-check rows');
  });

test('a procedure setup written as a list is drawn as one', async () => {
  // Your Trainer's generator output, 2026-09-25: one bullet per item, a blank
  // line between items, and a line that continues the item above it.
  const sitting = procedureSitting();
  sitting.procedure.setup = '- The debug build with **no rider**.\n\n'
    + '- A tablet and a phone,\n  both on the same build.\n\n'
    + 'A closing sentence that is not an item.';
  const document = makeDom();
  const { buildWalkPage } = await loadProc({ document });
  const page = buildWalkPage(procedurePayload({ sittings: [sitting] }));
  const setup = all(page, 'walk-proc-setup');
  assert.equal(setup.length, 1);
  const [list, closing] = setup[0].children;
  assert.equal(list.tagName.toLowerCase(), 'ul');
  assert.deepEqual(list.children.map((li) => li.textContent), [
    'The debug build with no rider.',
    'A tablet and a phone,\nboth on the same build.',
  ]);
  assert.equal(closing.tagName.toLowerCase(), 'p');
  assert.equal(closing.textContent, 'A closing sentence that is not an item.');
  assert.ok(!/^- /m.test(setup[0].textContent), 'a list marker was drawn as text');
});

test('every printed step is drawn, with the screen it happens on', async () => {
  const document = makeDom();
  const { buildWalkPage } = await loadProc({ document });
  const page = buildWalkPage(procedurePayload());
  const heads = all(page, 'walk-step-head').map((n) => n.textContent);
  assert.deepEqual(heads, [
    'Step 1 — Profile', 'Step 2 — Settings', 'Step 3', 'Step 4 — Profile',
  ]);
});

test('the active action omits only the screen label already in its heading', async () => {
  const sitting = procedureSitting();
  sitting.procedure.steps[0].head =
    '1. **Profile (SUR-0001).** Open the app on the Profile screen.';
  sitting.procedure.steps[1].head =
    '2. **Another screen (SUR-0002).** Tap Settings.';
  const source = sitting.procedure.steps[0].head;
  const document = makeDom();
  const { buildWalkPage } = await loadProc({ document });
  const page = buildWalkPage(procedurePayload({ sittings: [sitting] }));
  const first = all(page, 'walk-step')[0];
  assert.equal(all(first, 'walk-step-head')[0].textContent, 'Step 1 — Profile');
  assert.equal(all(first, 'walk-step-said')[0].textContent,
    'Open the app on the Profile screen.');
  assert.equal(all(first, 'walk-step-said')[1].textContent,
    'The avatar sits above the name.');
  assert.equal(all(all(page, 'walk-step')[1], 'walk-step-said')[0].textContent,
    'Another screen (SUR-0002). Tap Settings.');
  assert.equal(sitting.procedure.steps[0].head, source);
});

test('an expectation line shows the exact quote while check tags stay in details',
  async () => {
    const document = makeDom();
    const { buildWalkPage } = await loadProc({ document });
    const page = buildWalkPage(procedurePayload());
    const lines = all(page, 'walk-step-line')
      .filter((n) => n.className.includes('is-expectation'));
    assert.equal(lines.length, 4);
    //: The quote is the check's own Expect text. The tag remains available
    //: in details without interrupting the action and result.
    assert.equal(all(lines[0], 'walk-step-said')[0].textContent,
      'The avatar sits above the name.');
    assert.deepEqual(all(page, 'walk-step-coverage')[0].children
      .filter((n) => n.className.includes('walk-tag')).map((n) => n.textContent),
      ['TST-0001.1']);
  });

test('a tag already walked on this platform is marked passed', async () => {
  const document = makeDom();
  const { buildWalkPage } = await loadProc({ document });
  const page = buildWalkPage(procedurePayload());
  const passed = all(page, 'walk-tag')
    .filter((n) => n.className.includes('is-passed'));
  assert.deepEqual(passed.map((n) => n.textContent), ['TST-0004.1']);
  //: And it is not something the walker can tick: the tick is on the step,
  //: and a passed tag is not in the step's owed set, so no verdict for
  //: TST-0004 is ever waiting on it.
  const waiting = all(page, 'walk-proc-verdict').map((n) => n.textContent);
  assert.ok(!waiting.some((t) => t.includes('TST-0004')));
});

test('the steps left out of the printed procedure are accounted for',
  async () => {
    const document = makeDom();
    const { buildWalkPage } = await loadProc({ document });
    const page = buildWalkPage(procedurePayload());
    assert.match(page.textContent,
      /2 further steps in this procedure are left out/);
    assert.match(page.textContent, /4 steps to walk/);
  });

test('a procedure the module refused shows why and falls back to rows',
  async () => {
    const document = makeDom();
    const { buildWalkPage } = await loadProc({ document });
    const broken = procedureSitting();
    broken.procedure.problems = [
      'A fresh install owes TST-0002 step 1 and no step cites it',
    ];
    const page = buildWalkPage(procedurePayload({ sittings: [broken] }));
    assert.match(page.textContent, /no step cites it/);
    assert.equal(all(page, 'walk-procedure').length, 0);
    assert.deepEqual(all(page, 'checks-row').map((n) => n.dataset.check),
      ['TST-0001', 'TST-0002', 'TST-0003']);
  });

test('a sitting with no procedure renders exactly as before', async () => {
  const document = makeDom();
  const { buildWalkPage } = await loadProc({ document });
  const page = buildWalkPage(payload());
  assert.equal(all(page, 'walk-procedure').length, 0);
  assert.deepEqual(all(page, 'checks-row').map((n) => n.dataset.check),
    ['TST-0001', 'TST-0002', 'TST-0003']);
});

test('an unscripted decision card offers no Pass and writes no verdict until chosen',
  async () => {
    const document = makeDom();
    const posts = [], asks = [], statuses = [];
    const verdicts = [
      { verdict: 'pass', reason: '' },
      { verdict: 'na', reason: 'Android Backup has no iOS equivalent.' },
    ];
    const { buildWalkRow } = await loadProc({
      document, posts, asks, statuses, verdicts,
      initialWalkData: { release: 'REL-0017', platform: 'ios', history: {} },
    });
    const card = buildWalkRow(row('TST-0290', {
      readiness: { kind: 'decision', reason: 'Choose the iOS scope.', issue: 'ISS-0444' },
    }));
    assert.equal(all(card, 'checks-row')[0].dataset.controls, false);
    assert.match(all(card, 'walk-row-readiness')[0].textContent,
      /Needs a decision.*Choose the iOS scope.*ISS-0444/);
    const decide = all(card, 'walk-row-readiness')[0].querySelector('.file-row');
    decide.click();
    await new Promise(setImmediate);
    assert.deepEqual(asks[0].only, ['blocked', 'excused', 'na']);
    assert.equal(posts.length, 0, 'even a dialog bug cannot turn this into Pass');
    assert.match(statuses[0].message, /needs a release decision/);
    decide.click();
    await new Promise(setImmediate);
    assert.equal(posts.length, 1);
    assert.equal(posts[0].body.platform, 'ios');
    assert.equal(posts[0].body.verdict, 'na');
  });

test('an unscripted preparation card needs an explicit ready confirmation',
  async () => {
    const document = makeDom();
    const localStorage = makeStorage();
    const { buildWalkRow } = await loadProc({
      document, localStorage,
      initialWalkData: { release: 'REL-0017', platform: 'ios', history: {} },
    });
    const host = document.createElement('div');
    host.appendChild(buildWalkRow(row('TST-0001', {
      readiness: { kind: 'preparation', reason: 'Bring the backup file.' },
    })));
    assert.equal(all(host, 'checks-row')[0].dataset.controls, false);
    all(host, 'walk-row-readiness')[0].querySelector('.file-row').click();
    assert.equal(all(host, 'walk-row-readiness').length, 0);
    assert.equal(all(host, 'checks-row')[0].dataset.controls, true);
  });

test('the procedure is read through one adapter', async () => {
  //: [[TASK-0623]]'s last box: upstream's payload shape is read in exactly
  //: one place, so the shape changing is one edit here.
  const document = makeDom();
  const { readProcedure } = await loadProc({ document });
  const view = readProcedure(procedureSitting());
  assert.deepEqual(view.citing, {
    'TST-0001': [1, 3], 'TST-0002': [2], 'TST-0003': [4],
  });
  assert.equal(readProcedure({ ...procedureSitting(), procedure: null }), null);
});

// -------------------------------------------------- TASK-0624: a step tick

test('the worst mark among the citing steps decides the verdict', async () => {
  const document = makeDom();
  const { combineStepMarks } = await loadProc({ document });
  assert.equal(combineStepMarks(['pass', 'pass']), 'pass');
  assert.equal(combineStepMarks(['pass', 'partial']), 'partial');
  assert.equal(combineStepMarks(['partial', 'fail']), 'fail');
  //: A question on any citing step makes the check a question: somebody who
  //: did not understand one step did not understand the check.
  assert.equal(combineStepMarks(['fail', 'question']), 'question');
  assert.equal(combineStepMarks([]), '');
});

test('a check with an unticked citing step gets no ledger event', async () => {
  const document = makeDom();
  const posts = [];
  const proc = await loadProc({
    document, posts,
    verdicts: [{ verdict: 'pass', reason: '' }],
  });
  const v = procedurePayload();
  const sitting = v.sittings[0];
  const view = proc.readProcedure(sitting);
  //: `TST-0001` is cited by steps 1 and 3. Tick only step 1.
  await proc.markWalkStep(v, sitting, view, view.steps[0]);
  assert.deepEqual(posts, [],
    'a verdict was written from half a walk');
});

test('removing one tick before the last leaves the ledger untouched',
  async () => {
    const document = makeDom();
    const posts = [];
    const storage = makeStorage();
    const proc = await loadProc({
      document, posts, localStorage: storage,
      verdicts: [{ verdict: 'pass', reason: '' },
                 { verdict: 'pass', reason: '' },
                 { verdict: 'pass', reason: '' }],
    });
    const v = procedurePayload();
    const sitting = v.sittings[0];
    const view = proc.readProcedure(sitting);
    //: Three of the four steps, and the one left out is `TST-0001`'s second.
    await proc.markWalkStep(v, sitting, view, view.steps[0]);
    await proc.markWalkStep(v, sitting, view, view.steps[1]);
    await proc.markWalkStep(v, sitting, view, view.steps[3]);
    //: The two checks whose steps ARE all ticked are written; the one still
    //: waiting is not.
    assert.deepEqual(posts.map((p) => p.body.id), ['TST-0002', 'TST-0003']);
    //: Now take the tick back off step 2 and re-tick nothing: still nothing
    //: new, and `TST-0001` has never had an event.
    const held = JSON.parse(storage.getItem(proc.walkStepsKey('ws-1')));
    delete held[proc.stepMarkKey('REL-0017', 'android', 'A fresh install',
                                 view.sigs[2])];
    storage.setItem(proc.walkStepsKey('ws-1'), JSON.stringify(held));
    assert.ok(!posts.some((p) => p.body.id === 'TST-0001'));
  });

test('walking a sitting step by step writes the same events as ticking its '
  + 'checks one by one', async () => {
  //: **The phase's first exit criterion.** Both paths run against the same
  //: stubbed POST and the bodies are compared; nothing here recomputes what
  //: the code under test computes.
  const document = makeDom();

  // --- path A: four step ticks. Step 3 fails, which is TST-0001's second
  //     part, so TST-0001 must come out `fail` and carry the step's reason.
  const stepPosts = [];
  const byStep = await loadProc({
    document, posts: stepPosts,
    verdicts: [
      { verdict: 'pass', reason: '' },
      { verdict: 'pass', reason: '' },
      { verdict: 'fail', reason: 'the back gesture closed the app' },
      { verdict: 'pass', reason: '' },
    ],
  });
  const v = procedurePayload();
  const sitting = v.sittings[0];
  const view = byStep.readProcedure(sitting);
  for (const step of view.steps) {
    await byStep.markWalkStep(v, sitting, view, step);
  }

  // --- path B: the same three checks, ticked one by one on FEAT-0149's page
  //     with the verdicts those steps combine to.
  const rowPosts = [];
  const byRow = await loadProc({
    document, posts: rowPosts,
    verdicts: [
      { verdict: 'pass', reason: '' },
      { verdict: 'fail', reason: 'Step 3: the back gesture closed the app' },
      { verdict: 'pass', reason: '' },
    ],
  });
  //: In the order the step walk settles them: TST-0002 at step 2, then
  //: TST-0001 at step 3 — its second citing step, which is the one that
  //: completes it — and TST-0003 last, at step 4.
  for (const id of ['TST-0002', 'TST-0001', 'TST-0003']) {
    await byRow.walkOneCheck(sitting.rows.find((r) => r.id === id),
                             'android', async () => true);
  }

  assert.deepEqual(stepPosts, rowPosts);
  //: And the combine rule is what makes them equal: TST-0001 is `fail`
  //: because one of its two steps failed, not `pass` because the other held.
  const one = stepPosts.find((p) => p.body.id === 'TST-0001');
  assert.equal(one.body.verdict, 'fail');
  assert.equal(one.body.reason, 'Step 3: the back gesture closed the app');
  assert.equal(one.body.method, 'manual');
  assert.equal(one.body.platform, 'android');
});

test('real procedure verdicts equal direct check verdicts',
  { skip: !process.env.WALK_REAL_PROCEDURE_IN }, async () => {
    const v = JSON.parse(await fs.readFile(process.env.WALK_REAL_PROCEDURE_IN, 'utf8'));
    const sitting = v.sittings[0];
    const document = makeDom();
    const stepPosts = [];
    const statuses = [];
    const byStep = await loadProc({ document, posts: stepPosts, statuses });
    const view = byStep.readProcedure(sitting);
    for (const step of view.steps) {
      if (v.platform === 'ios' && step.number === 8) {
        // Your Trainer retired TST-0412 on 2026-09-17, and with it the ERG colour
        // capture this step used to request, so the real step is no longer
        // evidence-gated. The gate itself stays covered by the synthetic tests.
        assert.ok(!stepPosts.some((post) => post.body.id === 'TST-0370'),
          'the first of two real observation steps wrote a verdict');
      }
      await byStep.markWalkStep(v, sitting, view, step, true);
    }

    const rowPosts = [];
    const byRow = await loadProc({ document, posts: rowPosts,
      verdicts: sitting.rows.map(() => ({ verdict: 'pass', reason: '' })) });
    for (const row of sitting.rows) {
      await byRow.walkOneCheck(row, v.platform, async () => true);
    }
    assert.deepEqual(stepPosts, rowPosts);
    assert.deepEqual(stepPosts.map((post) => post.body.id),
      sitting.rows.map((row) => row.id));
    if (process.env.WALK_REAL_PROCEDURE_OUT) {
      await fs.writeFile(process.env.WALK_REAL_PROCEDURE_OUT,
        JSON.stringify({ steps: stepPosts.map((post) => post.body),
          checks: rowPosts.map((post) => post.body) }), 'utf8');
    }
  });

/** Every sitting of a real platform walk, walked step by step with Pass
 *  (TASK-0631, criterion D2: "unchanged procedures produce the same verdicts
 *  as the previous flow"). The walker's own preparation is done first: a
 *  `preparation` readiness is confirmed and every evidence prompt gets a note
 *  and build. A `decision` readiness cannot be confirmed, so a check behind
 *  one must get no verdict from its steps. Every other check must get exactly
 *  the request a direct Pass on its row would send.
 *
 *  Which steps are held is worked out here from the payload, not with
 *  `walkUnready`: asking the code under test which checks it holds could not
 *  catch a wrong hold rule (FEAT-0151 review, 2026-09-25). It counts a
 *  `preparation` readiness as not held only because the loop below confirms
 *  every one first; drop that confirmation and this must change with it. */
function heldStepsFromPayload(procedure) {
  const byNumber = new Map(procedure.steps.map((step) => [step.number, step]));
  const held = new Set();
  const heldAt = (number, seen = new Set()) => {
    if (seen.has(number)) return false;
    seen.add(number);
    const step = byNumber.get(number);
    if (step?.readiness && step.readiness.kind !== 'preparation') return true;
    return (procedure.requires?.[String(number)] || []).some((n) => heldAt(n, seen));
  };
  for (const step of procedure.steps) if (heldAt(step.number)) held.add(step.number);
  return held;
}

test('every real sitting walked by steps equals direct check verdicts',
  { skip: !process.env.WALK_ALL_PROCEDURES_IN }, async () => {
    const v = JSON.parse(await fs.readFile(process.env.WALK_ALL_PROCEDURES_IN, 'utf8'));
    const report = { platform: v.platform, sittings: [] };
    for (const sitting of v.sittings) {
      if (!sitting.procedure) continue;
      const storage = makeStorage();
      const stepPosts = [];
      const byStep = await loadProc({ document: makeDom(), posts: stepPosts,
        localStorage: storage });
      const view = byStep.readProcedure(sitting);
      const ready = {};
      for (const step of view.steps) {
        if (step.readiness?.kind === 'preparation')
          ready[byStep.evidenceKey(v, sitting, view, step.number)] = true;
      }
      assert.ok(byStep.saveWalkReady(ready));
      const heldSteps = heldStepsFromPayload(sitting.procedure);
      const held = new Set();
      for (const step of view.steps) {
        if (step.capturePrompt) {
          assert.ok(byStep.saveCurrentWalkEvidence(v, sitting, view, step,
            'Synthetic audit observation.', 'audit-build'));
        }
        const blocked = heldSteps.has(step.number);
        const before = stepPosts.length;
        await byStep.markWalkStep(v, sitting, view, step, true);
        if (blocked) {
          assert.equal(stepPosts.length, before,
            `${sitting.name} step ${step.number} wrote while held`);
          for (const id of Object.keys(view.citing))
            if (view.citing[id].includes(step.number)) held.add(id);
        }
      }
      const posted = new Set(stepPosts.map((post) => post.body.id));
      for (const id of held) {
        assert.ok(!posted.has(id),
          `${sitting.name}: ${id} got a verdict although a citing step is held`);
      }

      const rowPosts = [];
      const passing = sitting.rows.filter((row) => !held.has(row.id || row.number));
      const byRow = await loadProc({ document: makeDom(), posts: rowPosts,
        verdicts: passing.map(() => ({ verdict: 'pass', reason: '' })) });
      for (const row of passing) {
        await byRow.walkOneCheck(row, v.platform, async () => true);
      }
      const byId = (a, b) => a.body.id.localeCompare(b.body.id);
      assert.deepEqual(stepPosts.slice().sort(byId), rowPosts.slice().sort(byId),
        `${sitting.name}: step and direct verdicts differ`);
      report.sittings.push({
        name: sitting.name,
        steps: view.steps.length,
        rows: sitting.rows.length,
        posted: [...posted].sort(),
        held: [...held].sort(),
        requests: stepPosts.map((post) => post.body),
      });
    }
    if (process.env.WALK_ALL_PROCEDURES_OUT) {
      await fs.writeFile(process.env.WALK_ALL_PROCEDURES_OUT,
        JSON.stringify(report), 'utf8');
    }
  });

test('a step held by a decision records nothing, here or in the ledger', async () => {
  // The readiness gate in `markWalkStep`, guarded without Your Trainer's corpus
  // (FEAT-0151 review, 2026-09-25: only the corpus test caught its removal).
  const sitting = procedureSitting();
  sitting.procedure.steps[1].readiness = { kind: 'decision', reason: 'Choose first.' };
  const storage = makeStorage();
  const posts = [];
  const statuses = [];
  const proc = await loadProc({ document: makeDom(), posts, statuses, localStorage: storage });
  const v = procedurePayload({ sittings: [sitting] });
  const view = proc.readProcedure(sitting);
  await proc.markWalkStep(v, sitting, view, view.steps[1], true);
  assert.deepEqual(posts, []);
  assert.deepEqual(proc.loadStepMarks(), {}, 'a held step saved a mark');
  assert.match(statuses.at(-1).message, /Resolve the preparation or decision/);
});

test('a hold declared after a step was marked still holds its check', async () => {
  // Reviewer B's reproduction, FEAT-0151 review round 1. TST-0001 is cited by
  // steps 1 and 3. Step 3 is marked while nothing is held; the procedure then
  // makes step 3 depend on step 4, which needs unconfirmed preparation. Step 3's own words
  // do not change, so its saved mark survives, and marking step 1 wrote the check.
  const storage = makeStorage();
  const posts = [];
  const first = await loadProc({ document: makeDom(), posts, localStorage: storage });
  const before = procedureSitting();
  const v1 = procedurePayload({ sittings: [before] });
  const view1 = first.readProcedure(before);
  await first.markWalkStep(v1, before, view1, view1.steps[2], true);
  assert.deepEqual(posts, []);

  const after = procedureSitting();
  after.procedure.requires = { 3: [4] };
  after.procedure.steps[3].readiness = { kind: 'preparation', reason: 'Bring the meter.' };
  const second = await loadProc({ document: makeDom(), posts, localStorage: storage });
  const v2 = procedurePayload({ sittings: [after] });
  const view2 = second.readProcedure(after);
  assert.equal(second.walkUnready(v2, after, view2, view2.steps[2]).length, 1);
  await second.markWalkStep(v2, after, view2, view2.steps[0], true);
  assert.deepEqual(posts.map((post) => post.body.id), [],
    'TST-0001 was written while step 3 was held');
  assert.equal(second.walkStepNeedsLedgerRetry(v2, after, view2, view2.steps[0]), false,
    'a held check was offered as a retry');
});

test('a step whose whole action is its screen label keeps the label', async () => {
  const proc = await loadProc({ document: makeDom() });
  const step = { surface: 'Profile', surfaceNote: 'SUR-0001' };
  assert.equal(proc.walkVisibleAction('Profile (SUR-0001).', step), 'Profile (SUR-0001).');
  assert.equal(proc.walkVisibleAction('Profile (SUR-0001). Tap Edit.', step), 'Tap Edit.');
});

test('ledger replay scenarios use the real step marker', async () => {
  const results = {};
  const cases = [
    ['pass', 'TST-9901', 'pass', ''],
    ['partial', 'TST-9902', 'partial', 'the second observation was incomplete'],
    ['fail', 'TST-9903', 'fail', 'the expected result was absent'],
    ['question', 'TST-9904', 'question', 'the result was ambiguous'],
    ['correction', 'TST-9905', 'fail', 'the first reading was wrong'],
    ['interrupted', 'TST-9906', 'pass', ''],
  ];
  for (const platform of ['android', 'ios']) {
    results[platform] = {};
    for (const [name, id, verdict, reason] of cases) {
      const sitting = procedureSitting();
      const original = 'TST-0001';
      sitting.rows.find((item) => item.id === original).id = id;
      sitting.procedure.owed_checks = sitting.procedure.owed_checks
        .map((check) => check === original ? id : check);
      for (const step of sitting.procedure.steps) {
        for (const line of step.lines) {
          for (const tag of line.tags) {
            if (tag.check === original) tag.check = id;
          }
        }
      }
      const payload = procedurePayload({ platform, sittings: [sitting] });
      const posts = [];
      const storage = makeStorage();
      const first = await loadProc({ document: makeDom(), posts,
        localStorage: storage,
        verdicts: verdict === 'pass' ? [] : [{ verdict, reason }] });
      const view = first.readProcedure(sitting);
      await first.markWalkStep(payload, sitting, view, view.steps[0], true);
      const before = posts.length;
      assert.equal(before, 0, `${platform} ${name} wrote from the first of two steps`);
      const marker = name === 'interrupted'
        ? await loadProc({ document: makeDom(), posts, localStorage: storage })
        : first;
      const resumed = marker.readProcedure(sitting);
      await marker.markWalkStep(payload, sitting, resumed, resumed.steps[2],
        verdict === 'pass');
      if (name === 'correction') {
        await marker.markWalkStep(payload, sitting, resumed, resumed.steps[2], true);
      }
      assert.deepEqual(posts.map((post) => post.path),
        name === 'correction'
          ? ['/api/notes/mark-check', '/api/notes/mark-check']
          : ['/api/notes/mark-check']);
      results[platform][name] = { before, requests: posts.map((post) => post.body) };
    }
  }
  if (process.env.WALK_LEDGER_SCENARIOS_OUT) {
    await fs.writeFile(process.env.WALK_LEDGER_SCENARIOS_OUT,
      JSON.stringify(results), 'utf8');
  }
});

test('a step tick names the walk\'s own platform, never the picker',
  async () => {
    const document = makeDom();
    const posts = [];
    const proc = await loadProc({
      document, posts,
      verdicts: [{ verdict: 'pass', reason: '' }],
    });
    const v = procedurePayload({ platform: 'ios' });
    const sitting = v.sittings[0];
    const view = proc.readProcedure(sitting);
    await proc.markWalkStep(v, sitting, view, view.steps[1]);
    assert.equal(posts[0].body.platform, 'ios');
  });

test('a step tick is held per release, platform, sitting and step',
  async () => {
    const document = makeDom();
    const storage = makeStorage();
    const proc = await loadProc({
      document, localStorage: storage,
      verdicts: [{ verdict: 'pass', reason: '' }],
    });
    const v = procedurePayload();
    const sitting = v.sittings[0];
    const view = proc.readProcedure(sitting);
    await proc.markWalkStep(v, sitting, view, view.steps[0]);
    const held = JSON.parse(storage.getItem('cockpit:walk-steps:ws-1'));
    //: Content identifies the observation, so editing its action or
    //: expectation cannot reuse a mark even if the check tags stay the same.
    assert.deepEqual(Object.keys(held),
      [`REL-0017|android|A fresh install|${view.sigs[view.steps[0].number]}`]);
    //: Never in the repo and never in the ledger: the only write that left
    //: this tick was the check's own verdict, and there was none to write.
    assert.equal(storage._box.size, 1);
  });

test('a tick spent on a verdict is forgotten when the step stops printing',
  async () => {
    const document = makeDom();
    const storage = makeStorage();
    const proc = await loadProc({ document, localStorage: storage });
    const view = proc.readProcedure(procedurePayload().sittings[0]);
    const kept = `REL-0017|android|A fresh install|${view.sigs[view.steps[1].number]}`;
    storage.setItem('cockpit:walk-steps:ws-1', JSON.stringify({
      [kept]: { verdict: 'pass', reason: '' },
      'REL-0017|android|A fresh install|missing-step': { verdict: 'pass', reason: '' },
      'REL-0017|ios|A fresh install|missing-step': { verdict: 'pass', reason: '' },
    }));
    proc.pruneStepMarks(procedurePayload());
    const held = JSON.parse(storage.getItem('cockpit:walk-steps:ws-1'));
    //: Step 2 still prints, so its tick stays. Step 9 does not, so the
    //: Android tick is spent — and the iOS one is untouched, because that is
    //: a different walk of the same procedure.
    assert.deepEqual(Object.keys(held).sort(), [
      kept, 'REL-0017|ios|A fresh install|missing-step',
    ].sort());
  });

test('the page says which step each verdict is still waiting on', async () => {
  const document = makeDom();
  const storage = makeStorage();
  const { buildWalkPage, readProcedure } = await loadProc({ document, localStorage: storage });
  const sitting = procedurePayload().sittings[0];
  const view = readProcedure(sitting);
  storage.setItem('cockpit:walk-steps:ws-1', JSON.stringify({
    [`REL-0017|android|A fresh install|${view.sigs[view.steps[0].number]}`]:
      { verdict: 'pass', reason: '' },
  }));
  const page = buildWalkPage(procedurePayload());
  const states = all(page, 'walk-proc-verdict').map((n) => n.textContent);
  assert.ok(states.some((t) => t.includes('TST-0001')
    && t.includes('waiting on step 3')), states.join(' | '));
});

test('nothing on the procedure moves when a step is ticked', async () => {
  //: [[TASK-0556]]: a list that reorders itself as you tick things is one you
  //: lose your place in. A ticked step keeps its number and its position.
  const document = makeDom();
  const storage = makeStorage();
  const { buildWalkPage, readProcedure } = await loadProc({ document, localStorage: storage });
  const view = readProcedure(procedurePayload().sittings[0]);
  storage.setItem('cockpit:walk-steps:ws-1', JSON.stringify({
    [`REL-0017|android|A fresh install|${view.sigs[view.steps[2].number]}`]:
      { verdict: 'fail', reason: 'no' },
  }));
  const page = buildWalkPage(procedurePayload());
  const order = all(page, 'walk-step-head').map((n) => n.textContent);
  assert.deepEqual(order, [
    'Step 1 — Profile', 'Step 2 — Settings', 'Step 3', 'Step 4 — Profile',
  ]);
  const ticked = all(page, 'walk-step-button')
    .filter((n) => n.textContent.includes('fail'));
  assert.match(ticked[0].textContent, /fail/);
});

// -------------------------------------------- TASK-0622: the survey's cards

test('a child screen is drawn inside its parent\'s card', async () => {
  const document = makeDom();
  const { buildSurveySection } = await loadProc({ document });
  const section = buildSurveySection(payload({
    survey: [
      { surface: 'Workout editor', surface_note: 'SUR-0001', parent: null,
        unresolved: false, captures: [],
        changes: [{ id: 'CHG-1', title: 'A', sentence: 'the editor moved.' }] },
      { surface: 'HR-zone interval sheet', surface_note: 'SUR-0002',
        parent: 'SUR-0001', unresolved: false, captures: [],
        changes: [{ id: 'CHG-2', title: 'B', sentence: 'the sheet moved.' }] },
    ],
  }));
  const cards = section.children.filter(
    (c) => c.className.split(' ').includes('walk-survey-surface'));
  assert.equal(cards.length, 1, 'the dialog got a card of its own');
  //: `all` reports the root it was handed, so the parent card is the first
  //: of the two and the dialog is the one drawn inside it.
  const inside = all(cards[0], 'walk-survey-surface');
  assert.equal(inside.length, 2);
  assert.equal(inside[0], cards[0]);
  assert.ok(inside[1].className.includes('is-child'));
  assert.match(inside[1].textContent, /HR-zone interval sheet/);
});

test('a child whose parent this release did not change stands on its own',
  async () => {
    const document = makeDom();
    const { buildSurveySection } = await loadProc({ document });
    const section = buildSurveySection(payload({
      survey: [
        { surface: 'HR-zone interval sheet', surface_note: 'SUR-0002',
          parent: 'SUR-0001', unresolved: false, captures: [],
          changes: [{ id: 'CHG-2', title: 'B', sentence: 'it moved.' }] },
      ],
    }));
    assert.equal(all(section, 'walk-survey-surface').length, 1);
  });

test('before and after are served through the framed viewer route',
  async () => {
    const document = makeDom();
    const { buildSurveySection } = await loadProc({ document });
    const section = buildSurveySection(payload({
      survey: [{
        surface: 'Profile', surface_note: 'SUR-0001', parent: null,
        unresolved: false, changes: [],
        captures: [{ key: 'profile', state: null,
          before: 'docs/tests/acceptance/gallery/v1.0/profile.png',
          after: 'docs/tests/acceptance/gallery/candidate/profile.png',
          new: false }],
      }],
    }));
    const srcs = all(section, 'walk-survey-capture').map((n) => n.dataset.src);
    assert.deepEqual(srcs, [
      'http://127.0.0.1:7777/framed/tests/acceptance/gallery/v1.0/profile.png',
      'http://127.0.0.1:7777/framed/tests/acceptance/gallery/candidate/profile.png',
    ]);
    //: Both captions, so the walker knows which picture is which.
    assert.deepEqual(all(section, 'walk-survey-when').map((n) => n.textContent),
      ['at the last release', 'now']);
  });

test('a capture outside the workspace docs directory gets no URL', async () => {
  //: No new route reads outside a workspace ([[TASK-0622]]). A path the
  //: framed viewer cannot serve resolves to nothing rather than to a guess.
  const document = makeDom();
  const { walkCaptureSrc } = await loadProc({ document });
  assert.equal(walkCaptureSrc('../elsewhere/shot.png'), '');
  assert.equal(walkCaptureSrc('build/shot.png'), '');
  assert.equal(walkCaptureSrc('docs/a/b.png'),
    'http://127.0.0.1:7777/framed/a/b.png');
});

test('a card with only an after picture says new', async () => {
  const document = makeDom();
  const { buildSurveySection } = await loadProc({ document });
  const section = buildSurveySection(payload({
    survey: [{
      surface: 'Profile', surface_note: 'SUR-0001', parent: null,
      unresolved: false, changes: [],
      captures: [{ key: 'profile', state: 'pro', before: null,
        after: 'docs/g/candidate/profile.png', new: true }],
    }],
  }));
  assert.match(all(section, 'walk-survey-capture-key')[0].textContent,
    /profile \(pro\) — new/);
  assert.equal(all(section, 'walk-survey-capture').length, 1);
});

test('a procedure adds no test id to the survey', async () => {
  //: Rule 2 again, now that a procedure's tags put check ids on the page:
  //: they belong to the sittings, and the survey is still a list of places
  //: to open.
  const document = makeDom();
  const { buildSurveySection } = await loadProc({ document });
  const section = buildSurveySection(procedurePayload({
    survey: [{
      surface: 'Profile', surface_note: 'SUR-0001', parent: null,
      unresolved: false, captures: [],
      changes: [{ id: 'CHG-1', title: 'It moved', sentence: 'the avatar moved.' }],
    }],
  }));
  assert.ok(!section.textContent.includes('TST-'));
});

test('a card with no capture explains the missing comparison beside its sentence',
  async () => {
    const document = makeDom();
    const { buildSurveySection } = await loadProc({ document });
    const section = buildSurveySection(payload({
      survey: [{
        surface: 'Profile', surface_note: 'SUR-0001', parent: null,
        unresolved: false,
        changes: [{ id: 'CHG-1', title: 'A', sentence: 'the avatar moved.' }],
        captures: [{ key: 'profile', state: null, before: null, after: null,
          new: false }],
      }],
    }));
    assert.equal(all(section, 'walk-survey-captures').length, 0);
    assert.equal(all(section, 'walk-survey-capture-key').length, 0);
    assert.match(section.textContent, /the avatar moved/);
    assert.match(section.textContent, /No reference capture is available/);
  });

test('a step line shows its words, not its markdown', async () => {
  //: Found by rendering the first procedure in a real browser, 2026-09-14:
  //: the step's own line came out as `**Ride cockpit.** Pedal for five
  //: seconds`, asterisks and all. The stub DOM could not show it because
  //: nothing here reads the text the way a person does.
  const document = makeDom();
  const { walkLineText } = await loadProc({ document });
  assert.equal(
    walkLineText('1. **Ride cockpit.** Pedal for five seconds.', []),
    'Ride cockpit. Pedal for five seconds.');
  assert.equal(walkLineText('   - __The banner reads DONE.__', []),
    'The banner reads DONE.');
  //: The tag comes off too, and what is left is the check's own words.
  assert.equal(
    walkLineText('   - The cadence rises. `TST-0001.1`',
                 [{ check: 'TST-0001', step: '1', owed: true }]),
    'The cadence rises.');
});

test('the mark dialog leaves off the screen label its title already names', async () => {
  // Your Trainer's Fresh install step 10, 2026-09-25: the title read
  // `Settings (SUR-0044). In Developer Settings… — Settings`.
  const document = makeDom();
  const asks = [];
  const proc = await loadProc({ document, asks });
  const sitting = procedureSitting();
  sitting.procedure.steps[0].head = '**Profile (SUR-0001).** Open the app on the Profile screen.';
  const v = procedurePayload({ sittings: [sitting] });
  const view = proc.readProcedure(sitting);
  await proc.markWalkStep(v, sitting, view, view.steps[0]);
  assert.equal(asks[0].name, 'Open the app on the Profile screen. — Profile');
});

test('the mark dialog names the step in words, not markdown', async () => {
  //: The dialog read `Step 1 **Ride cockpit.** Pedal for five seconds…` the
  //: first time a procedure was rendered in a browser, 2026-09-14. It builds
  //: its name from the step head, so it needs the same cleaning the page's
  //: own lines get.
  const document = makeDom();
  const asks = [];
  const proc = await loadProc({
    document, asks, verdicts: [{ verdict: 'pass', reason: '' }],
  });
  const sitting = procedureSitting();
  sitting.procedure.steps[0].head = '**Ride cockpit.** Pedal for five seconds.';
  const v = procedurePayload({ sittings: [sitting] });
  const view = proc.readProcedure(sitting);
  await proc.markWalkStep(v, sitting, view, view.steps[0]);
  assert.equal(asks.length, 1);
  assert.equal(asks[0].number, 'Step 1');
  assert.equal(asks[0].name, 'Ride cockpit. Pedal for five seconds. — Profile');
  //: Pass is the primary action; the dialog holds the three observation
  //: outcomes that need an explanation, never the scope decisions.
  assert.deepEqual(asks[0].only, ['partial', 'fail', 'question']);
});

test('a step inserted mid-walk does not inherit the mark of the step that '
  + 'used to sit there', async () => {
  //: **A step number is a position, not an identity** — the bundled module
  //: says so, and keying a tick on the number alone let an edited procedure
  //: hand a mark to a step nobody walked. If that step shares a check with
  //: another, the check's verdict is then built partly from a tick that was
  //: never given for it. Found by independent review, 2026-09-14.
  const document = makeDom();
  const storage = makeStorage();
  const before = await loadProc({
    document, localStorage: storage, verdicts: [{ verdict: 'pass', reason: '' }],
  });
  const v = procedurePayload();
  const sitting = v.sittings[0];
  await before.markWalkStep(v, sitting, before.readProcedure(sitting),
                            before.readProcedure(sitting).steps[0]);
  assert.equal(Object.keys(
    JSON.parse(storage.getItem('cockpit:walk-steps:ws-1'))).length, 1);

  //: Now the procedure gains a new first step citing a different owed part.
  //: Every later step shifts up one.
  const edited = procedureSitting();
  edited.procedure.steps.unshift({
    number: 1, head: 'Wipe the phone.', surface: 'Profile',
    surface_note: 'SUR-0001',
    lines: [
      { text: '1. Wipe the phone.', tags: [] },
      { text: '   - The app is gone. `TST-0002.2`',
        quote: 'The app is gone.',
        tags: [{ check: 'TST-0002', step: '2', owed: true }] },
    ],
  });
  edited.procedure.steps.forEach((s, i) => { s.number = i + 1; });
  const after = await loadProc({ document, localStorage: storage });
  const page = after.buildWalkPage(procedurePayload({ sittings: [edited] }));
  const ticks = all(page, 'walk-step-button').map((n) => n.textContent);
  assert.equal(ticks[0], 'Pass and next',
    'the new first step inherited the old first step\'s mark');
  //: And the step that genuinely holds the mark still shows it, at its new
  //: number — the tick followed what it settles, not where it sat.
  assert.ok(ticks.some((label) => /Recorded — pass/.test(label)), ticks.join(' | '));
});

test('an expectation line prints the module\'s quote, not one the page derives',
  async () => {
    //: The upstream validator compares the module's `quote_of` against the
    //: check's `## Expect` text. The page derived its own — stripping tag
    //: literals and emphasis with its own rules — so on a line carrying
    //: emphasis the two disagreed and the walker judged a sentence nothing
    //: had checked. Found by independent review, 2026-09-14.
    const document = makeDom();
    const { buildWalkPage } = await loadProc({ document });
    const sitting = procedureSitting();
    sitting.procedure.steps[0].lines[1] = {
      text: '   - The banner reads **DONE** now. `TST-0001.1`',
      quote: 'The banner reads **DONE** now.',
      tags: [{ check: 'TST-0001', step: '1', owed: true }],
    };
    const page = buildWalkPage(procedurePayload({ sittings: [sitting] }));
    const said = all(page, 'walk-step-said').map((n) => n.textContent);
    assert.ok(said.includes('The banner reads **DONE** now.'), said.join(' | '));
    //: And the page's own stripping is NOT applied to it.
    assert.ok(!said.includes('The banner reads DONE now.'), said.join(' | '));
  });

test('a step instruction with no expectation still reads as words', async () => {
  //: The module reads no expectation from an instruction line, so there is no
  //: quote for it and the page's own cleaning is what makes it legible.
  const document = makeDom();
  const { buildWalkPage } = await loadProc({ document });
  const page = buildWalkPage(procedurePayload());
  const said = all(page, 'walk-step-said').map((n) => n.textContent);
  assert.ok(said.includes('Open the app on the Profile screen.'), said.join(' | '));
});

test('a fresh guided walk shows one survey card and then one current step', async () => {
  const document = makeDom();
  const storage = makeStorage();
  const { buildWalkPage } = await loadProc({ document, localStorage: storage });
  const changes = [1, 2].map((n) => ({
    surface: `Screen ${n}`, surface_note: `SUR-000${n}`, parent: null,
    unresolved: false, captures: [],
    changes: [{ id: `CHG-${n}`, title: null, sentence: `Change ${n}.` }],
  }));
  const page = buildWalkPage(procedurePayload({ survey: changes }));
  const survey = all(page, 'walk-survey')[0];
  const sittings = all(page, 'walk-sittings')[0];
  const cards = all(survey, 'walk-survey-surface');
  assert.equal(survey.hidden, false);
  assert.equal(sittings.hidden, true);
  assert.deepEqual(cards.map((card) => card.hidden), [false, true]);

  const nav = all(page, 'walk-focus-nav')[0];
  nav.children.find((child) => child.textContent === 'Next screen').click();
  assert.deepEqual(cards.map((card) => card.hidden), [true, false]);
  nav.children.find((child) => child.textContent === 'Start tests').click();
  assert.equal(survey.hidden, true);
  assert.equal(sittings.hidden, false);
  assert.deepEqual(all(page, 'walk-step').map((step) => step.hidden),
    [false, true, true, true]);
  const saved = JSON.parse(storage.getItem('cockpit:walk-focus:ws-1'));
  assert.equal(saved.stage, 'session');
  assert.equal(saved.surveyIndex, 1);
});

test('a retained preparation action continues without a check verdict', async () => {
  const document = makeDom();
  const storage = makeStorage();
  const posts = [];
  const asks = [];
  const { buildWalkPage } = await loadProc({ document, localStorage: storage,
    posts, asks });
  const sitting = procedureSitting();
  sitting.procedure.steps[0].preparation = true;
  sitting.procedure.steps[0].lines = [
    { text: '1. Open the app on the Profile screen.', tags: [] },
  ];
  const page = buildWalkPage(procedurePayload({ sittings: [sitting] }));
  all(page, 'walk-focus-nav')[0].children
    .find((child) => child.textContent === 'Start tests').click();
  const first = all(page, 'walk-step')[0];
  assert.match(first.textContent, /Preparation for the next observation/);
  const control = all(first, 'walk-step-button')[0];
  assert.equal(control.textContent, 'Continue');
  control.click();
  assert.deepEqual(posts, []);
  assert.deepEqual(asks, []);
  assert.equal(all(page, 'walk-step')[1].hidden, false);
  const marks = JSON.parse(storage.getItem('cockpit:walk-steps:ws-1'));
  assert.equal(Object.values(marks)[0].verdict, 'done');
});

test('the current action keeps occasional navigation under Walk options', async () => {
  const document = makeDom();
  const posts = [];
  const { buildWalkPage } = await loadProc({ document, posts });
  const page = buildWalkPage(procedurePayload());
  const nav = all(page, 'walk-focus-nav')[0];
  nav.children.find((child) => child.textContent === 'Start tests').click();

  assert.equal(nav.children.find((child) => child.tagName === 'STRONG').textContent,
    'Step 1 of 4');
  assert.deepEqual(nav.children.filter((child) => child.tagName === 'BUTTON')
    .map((child) => child.textContent), ['Review results']);
  const options = all(nav, 'walk-options')[0];
  assert.equal(options.children[0].textContent, 'Walk options');
  const controls = options.children[1].children;
  assert.ok(controls.some((child) => child.textContent.startsWith('Go to session')));
  assert.ok(controls.some((child) => child.textContent === 'Changed screens'));
  assert.ok(controls.some((child) => child.textContent === 'Next step'));
  assert.ok(controls.some((child) => child.textContent === 'Show nearby steps'));
  assert.ok(controls.some((child) => child.textContent === 'Show full session'));
  const picker = all(options, 'walk-step-select')[0];
  assert.equal(picker.children.length, 4);
  assert.match(picker.children[2].textContent, /Step 3 — Go back/);

  controls.find((child) => child.textContent === 'Next step').click();
  assert.deepEqual(all(page, 'walk-step').map((step) => step.hidden),
    [true, false, true, true]);
  const currentPicker = all(nav, 'walk-step-select')[0];
  assert.equal(currentPicker.value, '1');
  currentPicker.value = '3';
  currentPicker.listeners.change[0]();
  assert.deepEqual(all(page, 'walk-step').map((step) => step.hidden),
    [true, true, true, false]);
  assert.deepEqual(posts, [], 'navigation alone cannot record a verdict');
});

test('session state and equipment move into setup and stay reachable on resume', async () => {
  const document = makeDom();
  const { buildWalkPage } = await loadProc({ document });
  const sitting = procedureSitting();
  sitting.procedure.steps[2].readiness = {
    kind: 'preparation', reason: 'Prepare a second rider.' };
  const page = buildWalkPage(procedurePayload({ sittings: [sitting] }));
  const section = all(page, 'walk-sitting')[0];
  const setup = all(section, 'walk-proc-block')[0];
  const readiness = all(section, 'walk-proc-readiness')[0];
  assert.equal(setup.open, true);
  assert.equal(readiness.open, true);
  assert.match(setup.textContent, /the app installed and never opened/);
  assert.match(setup.textContent, /a wiped phone/);
  assert.equal(section.children.some((child) => child.className === 'walk-sitting-state'), false);
  assert.equal(section.children.some((child) => child.className === 'walk-bench'), false);

  const nav = all(page, 'walk-focus-nav')[0];
  nav.children.find((child) => child.textContent === 'Start tests').click();
  const options = all(nav, 'walk-options')[0];
  options.children[1].children
    .find((child) => child.textContent === 'Next step').click();
  assert.equal(setup.open, false);
  assert.equal(readiness.open, false);
  assert.match(setup.textContent, /a wiped phone/,
    'the closed disclosure still holds the setup for reopening');
  assert.match(readiness.textContent, /Prepare a second rider/,
    'the readiness list remains available without repeating it above a later action');
});

test('a later comparison opens evidence saved at its preparation step after restart', async () => {
  const storage = makeStorage();
  const posts = [];
  const statuses = [];
  const sitting = procedureSitting();
  sitting.procedure.steps[0].preparation = true;
  sitting.procedure.steps[0].required_state = 'The ride is running without an HRM.';
  sitting.procedure.steps[0].capture_prompt = 'Record the AVG HR row.';
  sitting.procedure.steps[0].lines = [
    { text: '1. Open the app on the Profile screen.', tags: [] },
  ];
  sitting.procedure.steps[1].use_capture = [1];
  const data = procedurePayload({ sittings: [sitting] });
  const document = makeDom();
  const api = await loadProc({ document, localStorage: storage, posts, statuses });
  const { buildWalkPage } = api;
  const page = buildWalkPage(data);
  all(page, 'walk-focus-nav')[0].children
    .find((child) => child.textContent === 'Start tests').click();
  const first = all(page, 'walk-step')[0];
  const laterStep = all(page, 'walk-step')[1];
  assert.equal(all(laterStep, 'walk-step-button')[0].disabled, true);
  const view = api.readProcedure(sitting);
  await api.markWalkStep(data, sitting, view, view.steps[1], true);
  assert.deepEqual(posts, []);
  assert.ok(statuses.some((status) => status.message.includes('requested evidence')));
  all(first, 'walk-step-button')[0].click();
  assert.equal(all(page, 'walk-step')[1].hidden, true,
    'the later comparison must not open before its source evidence is saved');
  all(first, 'walk-step-evidence-note')[0].value = 'AVG HR showed -- below HR.';
  all(first, 'walk-step-evidence-build')[0].value = 'android debug 41';
  first.children.find((child) => child.className === 'walk-step-evidence')
    .children.find((child) => child.textContent === 'Save evidence').click();
  all(first, 'walk-step-button')[0].click();
  assert.equal(all(page, 'walk-step')[1].hidden, false);
  assert.match(all(page, 'walk-step-evidence')[1].textContent,
    /AVG HR showed -- below HR/);
  assert.equal(all(laterStep, 'walk-step-button')[0].disabled, false);
  const restartedDocument = makeDom();
  const restarted = await loadProc({ document: restartedDocument,
    localStorage: storage });
  const resumed = restarted.buildWalkPage(data);
  assert.match(all(resumed, 'walk-step-evidence')[1].textContent,
    /AVG HR showed -- below HR/);
  assert.match(all(resumed, 'walk-step-evidence')[1].textContent,
    /build android debug 41/);
});

test('a source step files its PNG under the later check and shows build and image at comparison', async () => {
  const storage = makeStorage();
  const posts = [];
  const proc = await loadProc({ document: makeDom(), localStorage: storage, posts,
    attachmentResponse: { result: {
      rel: 'attachments/TST-0002/2026-09-16-1.png',
    } },
  });
  const sitting = procedureSitting();
  sitting.procedure.steps[0].preparation = true;
  sitting.procedure.steps[0].capture_prompt = 'Record the starting row.';
  sitting.procedure.steps[0].required_state = 'The ride is running.';
  sitting.procedure.steps[0].lines = [
    { text: '1. Open the app on the Profile screen.', tags: [] },
  ];
  sitting.procedure.steps[1].use_capture = [1];
  const v = procedurePayload({ sittings: [sitting] });
  const view = proc.readProcedure(sitting);
  assert.equal(proc.saveCurrentWalkEvidence(v, sitting, view, view.steps[0],
    'The row starts blue.', ''), false);
  assert.equal(proc.hasRequiredWalkEvidence(v, sitting, view, view.steps[0]), false);
  assert.equal(proc.saveCurrentWalkEvidence(v, sitting, view, view.steps[0],
    'The row starts blue.', 'android debug 41'), true);
  const bytes = Uint8Array.from([137, 80, 78, 71, 13, 10, 26, 10, 0]);
  const file = { name: 'tablet.png', size: bytes.length,
    arrayBuffer: async () => bytes.buffer };
  assert.equal(await proc.attachWalkEvidenceImage(v, sitting, view, view.steps[0], file), true);
  assert.equal(posts.length, 1);
  assert.equal(posts[0].path, '/api/notes/attach');
  assert.equal(posts[0].body.id, 'TST-0002');
  assert.match(posts[0].body.caption, /android, REL-0017, build android debug 41, The ride is running/);
  assert.match(posts[0].body.png_base64, /^iVBORw0KGgo/);
  const later = proc.buildWalkEvidence(v, sitting, view, view.steps[1]);
  assert.match(later.textContent, /build android debug 41/);
  assert.match(later.textContent, /The row starts blue/);
  assert.match(all(later, 'walk-step-evidence-image')[0].src,
    /\/framed\/attachments\/TST-0002\/2026-09-16-1.png$/);
  assert.equal(posts.filter((event) => event.path === '/api/notes/mark-check').length, 0);
  await proc.markWalkStep(v, sitting, view, view.steps[1], true);
  const verdict = posts.find((event) => event.path === '/api/notes/mark-check');
  assert.equal(verdict.body.id, 'TST-0002');
  assert.equal(verdict.body.evidence[0].ref,
    'docs/attachments/TST-0002/2026-09-16-1.png');
  assert.match(verdict.body.evidence[0].note, /build android debug 41/);
});

test('attaching a PNG through the visible step control refreshes the next comparison', async () => {
  const storage = makeStorage();
  const posts = [];
  const proc = await loadProc({ document: makeDom(), localStorage: storage, posts,
    attachmentResponse: { result: { rel: 'attachments/TST-0002/2026-09-16-1.png' } },
  });
  const sitting = procedureSitting();
  sitting.procedure.steps[0].preparation = true;
  sitting.procedure.steps[0].capture_prompt = 'Record the starting row.';
  sitting.procedure.steps[0].lines = [
    { text: '1. Open the app on the Profile screen.', tags: [] },
  ];
  sitting.procedure.steps[1].use_capture = [1];
  const page = proc.buildWalkPage(procedurePayload({ sittings: [sitting] }));
  const steps = all(page, 'walk-step');
  assert.match(all(steps[1], 'walk-step-evidence')[0].textContent, /is missing/);
  all(steps[0], 'walk-step-evidence-note')[0].value = 'The row starts blue.';
  all(steps[0], 'walk-step-evidence-build')[0].value = 'android debug 41';
  const bytes = Uint8Array.from([137, 80, 78, 71, 13, 10, 26, 10, 0]);
  all(steps[0], 'walk-step-evidence-file')[0].files = [{
    name: 'tablet.png', size: bytes.length,
    arrayBuffer: async () => bytes.buffer,
  }];
  all(steps[0], 'walk-step-evidence')[0].children
    .find((child) => child.textContent === 'Attach PNG').click();
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(posts[0].path, '/api/notes/attach');
  assert.match(all(steps[1], 'walk-step-evidence')[0].textContent, /The row starts blue/);
  assert.equal(all(steps[1], 'walk-step-evidence-image').length, 1);
});

test('a bad attachment response leaves the saved note without a false image link', async () => {
  const storage = makeStorage();
  const posts = [];
  const statuses = [];
  const proc = await loadProc({ document: makeDom(), localStorage: storage,
    posts, statuses, attachmentResponse: {} });
  const sitting = procedureSitting();
  sitting.procedure.steps[0].capture_prompt = 'Record the starting row.';
  const v = procedurePayload({ sittings: [sitting] });
  const view = proc.readProcedure(sitting);
  assert.equal(proc.saveCurrentWalkEvidence(v, sitting, view, view.steps[0],
    'The row starts blue.', 'android debug 41'), true);
  const bytes = Uint8Array.from([137, 80, 78, 71, 13, 10, 26, 10, 0]);
  const file = { name: 'tablet.png', size: bytes.length,
    arrayBuffer: async () => bytes.buffer };
  assert.equal(await proc.attachWalkEvidenceImage(v, sitting, view, view.steps[0], file), false);
  const saved = proc.loadWalkEvidence()[proc.evidenceKey(v, sitting, view, 1)];
  assert.equal(saved.attachmentRel, undefined);
  assert.ok(statuses.some((status) => status.message.includes('no safe file path')));
  assert.equal(posts.length, 1);
});

test('a failed ledger write leaves the saved mark and offers retry without changing it', async () => {
  const document = makeDom();
  const storage = makeStorage();
  const posts = [];
  const failures = { remaining: 1 };
  const proc = await loadProc({ document, localStorage: storage, posts,
    postFailures: failures,
    verdicts: [{ verdict: 'fail', reason: 'the sheet stayed closed' }] });
  const v = procedurePayload();
  const sitting = v.sittings[0];
  const view = proc.readProcedure(sitting);
  await proc.markWalkStep(v, sitting, view, view.steps[1]);
  assert.deepEqual(posts, []);
  const held = JSON.parse(storage.getItem(proc.walkStepsKey('ws-1')));
  assert.equal(Object.values(held)[0].verdict, 'fail');
  const button = all(proc.buildStepTick(v, sitting, view, view.steps[1]),
    'walk-step-button')[0];
  assert.equal(button.textContent, 'Retry ledger write');
  button.click();
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(posts.length, 1);
  assert.equal(posts[0].body.verdict, 'fail');
  assert.equal(posts[0].body.reason, 'Step 2: the sheet stayed closed');
});

test('partial and question corrections append history without an accidental duplicate', async () => {
  const document = makeDom();
  const posts = [];
  const proc = await loadProc({ document, posts, verdicts: [
    { verdict: 'partial', reason: 'one detail is missing' },
    { verdict: 'pass', reason: '' },
    { verdict: 'question', reason: 'the copy is ambiguous' },
  ] });
  const v = procedurePayload();
  const sitting = v.sittings[0];
  const view = proc.readProcedure(sitting);
  await proc.markWalkStep(v, sitting, view, view.steps[1]);
  await proc.markWalkStep(v, sitting, view, view.steps[1]);
  await proc.markWalkStep(v, sitting, view, view.steps[3]);
  await proc.markWalkStep(v, sitting, view, view.steps[1], true);
  assert.deepEqual(posts.map((event) => [event.body.id, event.body.verdict]), [
    ['TST-0002', 'partial'], ['TST-0002', 'pass'], ['TST-0003', 'question'],
  ]);
  assert.equal(posts[0].body.reason, 'Step 2: one detail is missing');
  assert.equal(posts[2].body.reason, 'Step 4: the copy is ambiguous');
});

test('refused local storage prevents a verdict and reports the unsaved observation', async () => {
  const storage = makeStorage();
  storage.setItem = () => { throw new Error('quota exceeded'); };
  const document = makeDom();
  const posts = [];
  const statuses = [];
  const proc = await loadProc({ document, localStorage: storage, posts, statuses });
  const v = procedurePayload();
  const view = proc.readProcedure(v.sittings[0]);
  await proc.markWalkStep(v, v.sittings[0], view, view.steps[1], true);
  assert.deepEqual(posts, []);
  assert.ok(statuses.some((status) => status.kind === 'error'
    && status.message.includes('could not save the observation')));
});

test('an edited instruction keeps its old observation for review without applying it', async () => {
  const document = makeDom();
  const storage = makeStorage();
  const proc = await loadProc({ document, localStorage: storage });
  const before = procedurePayload();
  const old = proc.readProcedure(before.sittings[0]);
  const key = proc.stepMarkKey(before.release, before.platform,
    before.sittings[0].name, old.sigs[1]);
  storage.setItem(proc.walkStepsKey('ws-1'), JSON.stringify({
    [key]: { verdict: 'pass', reason: '' },
  }));
  const edited = procedurePayload();
  edited.sittings[0].procedure.steps[0].head = 'Open Profile and inspect the new avatar.';
  const changed = proc.pruneStepMarks(edited);
  assert.deepEqual(changed, ['TST-0001']);
  assert.ok(JSON.parse(storage.getItem(proc.walkStepsKey('ws-1')))[key],
    'the old observation must remain available for review');
  const now = proc.readProcedure(edited.sittings[0]);
  assert.notEqual(now.sigs[1], old.sigs[1]);
  assert.equal(storage.getItem(proc.walkStepsKey('ws-1'))?.includes(now.sigs[1]), false);
});

test('a candidate invalidation archives earlier step marks and retains new work', async () => {
  const document = makeDom();
  const storage = makeStorage();
  const proc = await loadProc({ document, localStorage: storage });
  const data = procedurePayload();
  const view = proc.readProcedure(data.sittings[0]);
  const key = proc.stepMarkKey(data.release, data.platform,
    data.sittings[0].name, view.sigs[1]);
  storage.setItem(proc.walkStepsKey('ws-1'), JSON.stringify({
    [key]: { verdict: 'pass', reason: '', basis: { 'TST-0001': '' } },
  }));
  data.history = { 'TST-0001': [{ platform: 'android', invalidated_by: 'CHG-NEW',
    mark: 'pass', reason: '' }] };
  assert.deepEqual(proc.pruneStepMarks(data), ['TST-0001']);
  assert.equal(JSON.parse(storage.getItem(proc.walkStepsKey('ws-1')))[key], undefined);
  const archived = JSON.parse(storage.getItem('cockpit:walk-observation-history:ws-1'));
  assert.equal(archived[0].mark.verdict, 'pass');
  storage.setItem(proc.walkStepsKey('ws-1'), JSON.stringify({
    [key]: { verdict: 'fail', reason: 'new observation',
      basis: { 'TST-0001': 'CHG-NEW' } },
  }));
  assert.deepEqual(proc.pruneStepMarks(data), []);
  assert.equal(JSON.parse(storage.getItem(proc.walkStepsKey('ws-1')))[key].verdict, 'fail');
});

test('readiness holds dependent actions while an independent step stays reachable', async () => {
  const document = makeDom();
  const storage = makeStorage();
  const posts = [];
  const { buildWalkPage } = await loadProc({ document, localStorage: storage, posts });
  const sitting = procedureSitting();
  sitting.procedure.requires = { 2: [1] };
  sitting.procedure.steps[0].readiness = {
    kind: 'preparation', reason: 'Bring the meter.', issue: 'ISS-1001',
  };
  sitting.procedure.steps[3].readiness = {
    kind: 'decision', reason: 'Choose the intended closing result.', issue: 'ISS-1002',
  };
  const page = buildWalkPage(procedurePayload({ sittings: [sitting] }));
  assert.match(all(page, 'walk-proc-readiness')[0].textContent,
    /1 need preparation, 1 need a decision/);
  let steps = all(page, 'walk-step');
  assert.equal(all(steps[0], 'walk-step-button')[0].disabled, true);
  assert.equal(all(steps[1], 'walk-step-button')[0].disabled, true);
  assert.equal(all(steps[2], 'walk-step-button')[0].disabled, false);
  assert.equal(all(steps[3], 'walk-step-button')[0].disabled, true);
  const confirm = all(steps[0], 'walk-step-readiness')[0].children
    .find((child) => child.textContent === 'I have this ready');
  confirm.click();
  steps = all(page, 'walk-step');
  assert.equal(all(steps[0], 'walk-step-button')[0].disabled, false);
  assert.equal(all(steps[1], 'walk-step-button')[0].disabled, false);
  assert.equal(all(steps[3], 'walk-step-button')[0].disabled, true);
  assert.deepEqual(posts, [], 'confirming setup must not write a verdict');
});

test('an authored timer reports interruption and never records a verdict', async () => {
  const storage = makeStorage();
  const posts = [];
  const sitting = procedureSitting();
  sitting.procedure.steps[0].timer_seconds = 1;
  const data = procedurePayload({ sittings: [sitting] });
  const document = makeDom();
  const { buildWalkPage } = await loadProc({ document, localStorage: storage, posts });
  const page = buildWalkPage(data);
  all(page, 'walk-focus-nav')[0].children
    .find((child) => child.textContent === 'Start tests').click();
  const timer = all(page, 'walk-step-timer')[0];
  assert.match(timer.textContent, /Optional 1-second timer/);
  timer.children.find((child) => child.textContent === 'Start timer').click();
  const resumed = await loadProc({ document: makeDom(), localStorage: storage, posts });
  const reopened = resumed.buildWalkPage(data);
  assert.match(all(reopened, 'walk-step-timer')[0].textContent,
    /A previous timer was interrupted/);
  await new Promise((resolve) => setTimeout(resolve, 1200));
  assert.match(timer.textContent, /Timer ended/);
  assert.deepEqual(posts, []);
});

test('the current step can open its own before and after reference images', async () => {
  const document = makeDom();
  const { buildWalkPage } = await loadProc({ document });
  const page = buildWalkPage(procedurePayload({ survey: [{
    surface: 'Profile', surface_note: 'SUR-0001', parent: null,
    unresolved: false, changes: [], captures: [{
      key: 'profile', state: 'FREE rider',
      before: 'docs/gallery/old/profile.png', after: 'docs/gallery/candidate/profile.png',
      new: false,
    }],
  }] }));
  const reference = all(page, 'walk-step-reference')[0];
  assert.match(reference.textContent, /android, REL-0017/);
  assert.match(reference.textContent, /FREE rider/);
  assert.equal(all(reference, 'walk-survey-capture').length, 2);
});

test('the walk review keeps failed and questioned checks visible after navigation', async () => {
  const document = makeDom();
  const { buildWalkPage } = await loadProc({ document });
  const sitting = procedureSitting();
  sitting.rows = [row('TST-0002', { mark: 'fail' }),
    row('TST-0003', { mark: 'question' })];
  sitting.procedure.owed_checks = ['TST-0002', 'TST-0003'];
  const data = procedurePayload({ sittings: [sitting],
    counts: { owed: 2, placed: 2, unplaced: 0 }, history: {
    'TST-0001': [{ platform: 'android', mark: 'pass', reason: '',
      invalidated_by: '' }],
    'TST-0002': [{ platform: 'android', mark: 'fail', reason: 'sheet stayed closed',
      invalidated_by: '' }],
    'TST-0003': [{ platform: 'android', mark: 'question', reason: 'copy ambiguous',
      invalidated_by: '' }],
  } });
  const page = buildWalkPage(data);
  const nav = all(page, 'walk-focus-nav')[0];
  nav.children.find((child) => child.textContent === 'Start tests').click();
  nav.children.find((child) => child.textContent === 'Review results').click();
  const summary = all(page, 'walk-review-summary')[0];
  assert.equal(summary.hidden, false);
  assert.match(summary.textContent, /2 checks still need attention/);
  assert.match(summary.textContent, /TST-0002.*sheet stayed closed/);
  assert.match(summary.textContent, /TST-0003.*copy ambiguous/);
  assert.ok(!summary.textContent.includes('TST-0001'));
  nav.children.find((child) => child.textContent === 'Back to sessions').click();
  assert.equal(all(page, 'walk-sittings')[0].hidden, false);
});

test('the walk review counts an earlier excuse that expired when its ledger sealed', async () => {
  const document = makeDom();
  const { buildWalkPage } = await loadProc({ document });
  const sitting = procedureSitting();
  sitting.rows = [row('TST-0001')];
  sitting.procedure.owed_checks = ['TST-0001'];
  const data = procedurePayload({ sittings: [sitting],
    counts: { owed: 1, placed: 1, unplaced: 0 },
    history: { 'TST-0001': [{ platform: 'android', release: 'REL-0016',
      mark: 'excused', reason: 'Not a regression.', invalidated_by: '' }] } });
  const page = buildWalkPage(data);
  const nav = all(page, 'walk-focus-nav')[0];
  nav.children.find((child) => child.textContent === 'Start tests').click();
  nav.children.find((child) => child.textContent === 'Review results').click();
  const summary = all(page, 'walk-review-summary')[0];
  assert.match(summary.textContent, /1 check still needs attention/);
  assert.match(summary.textContent, /TST-0001.*earlier excuse from REL-0016 expired/);
  assert.ok(!summary.textContent.includes('Not a regression.'),
    'an expired excuse reason must not read like the current release decision');
});

test('a completed check remains correctable after restart and keeps its ledger history', async () => {
  const storage = makeStorage();
  const posts = [];
  const first = await loadProc({ document: makeDom(), localStorage: storage, posts });
  const original = procedurePayload();
  const originalSitting = original.sittings[0];
  const originalProc = first.readProcedure(originalSitting);
  await first.markWalkStep(original, originalSitting, originalProc, originalProc.steps[1], true);
  assert.deepEqual(first.loadWalkCompleted('REL-0017', 'android'), ['TST-0002']);
  assert.match(first.walkQuery('android', 'REL-0017'), /review=TST-0002/);
  assert.equal(posts.length, 1);

  const reviewSitting = structuredClone(originalSitting);
  reviewSitting.rows = [row('TST-0002')];
  reviewSitting.procedure.steps = [reviewSitting.procedure.steps[1]];
  reviewSitting.procedure.owed_checks = ['TST-0002'];
  const review = procedurePayload({
    sittings: [], unplaced: [], counts: { owed: 0, placed: 0, unplaced: 0 },
    review_sittings: [reviewSitting],
    history: { 'TST-0002': [{ platform: 'android', release: 'REL-0017',
      mark: 'pass', reason: '', invalidated_by: '' }] },
  });
  const restarted = await loadProc({ document: makeDom(), localStorage: storage,
    posts, verdicts: [{ verdict: 'fail', reason: 'the sheet stayed closed' }] });
  assert.deepEqual(restarted.pruneStepMarks(review), []);
  const page = restarted.buildWalkPage(review);
  assert.match(page.textContent, /Correct a completed observation/);
  assert.match(page.textContent, /TST-0002 pass/);
  assert.equal(all(page, 'walk-step-button')[0].textContent, 'Saved — pass');
  all(page, 'walk-step-alternate')[0].click();
  await new Promise((resolve) => setImmediate(resolve));
  assert.deepEqual(posts.map((event) => event.body.verdict), ['pass', 'fail']);
  assert.equal(posts[1].body.reason, 'Step 2: the sheet stayed closed');
  assert.equal(review.history['TST-0002'][0].mark, 'fail');
  assert.equal(review.history['TST-0002'][1].mark, 'pass');
  const savedFocus = JSON.parse(storage.getItem('cockpit:walk-focus:ws-1'));
  assert.equal(savedFocus.stage, 'session');
  assert.equal(savedFocus.sitting, 'A fresh install');
  const current = restarted.readProcedure(reviewSitting);
  await restarted.markWalkStep(review, reviewSitting, current, current.steps[0], false, true);
  assert.equal(posts.length, 2, 'retrying the identical result appended a duplicate event');
});

test('an edited completed step asks for a new run instead of inheriting its old mark', async () => {
  const storage = makeStorage();
  const first = await loadProc({ document: makeDom(), localStorage: storage });
  const original = procedurePayload();
  const sitting = original.sittings[0];
  const proc = first.readProcedure(sitting);
  await first.markWalkStep(original, sitting, proc, proc.steps[1], true);
  const changed = structuredClone(sitting);
  changed.rows = [row('TST-0002')];
  changed.procedure.steps = [changed.procedure.steps[1]];
  changed.procedure.steps[0].head = 'Open the sheet from the new control.';
  changed.procedure.owed_checks = ['TST-0002'];
  const review = procedurePayload({
    sittings: [], unplaced: [], counts: { owed: 0, placed: 0, unplaced: 0 },
    review_sittings: [changed],
    history: { 'TST-0002': [{ platform: 'android', mark: 'pass', reason: '',
      invalidated_by: '' }] },
  });
  const restarted = await loadProc({ document: makeDom(), localStorage: storage });
  assert.deepEqual(restarted.pruneStepMarks(review), ['TST-0002']);
  const page = restarted.buildWalkPage(review);
  assert.equal(all(page, 'walk-step-button')[0].textContent, 'Record a new run');
  assert.match(page.textContent, /Open the sheet from the new control/);
  const current = restarted.readProcedure(changed);
  await restarted.markWalkStep(review, changed, current, current.steps[0], true, false, true);
  assert.deepEqual(restarted.pruneStepMarks(review), []);
  const archive = JSON.parse(storage.getItem('cockpit:walk-observation-history:ws-1'));
  assert.equal(archive.length, 1, 'the older observation was not preserved after the new run');
});

test('an intentional repeated run appends a ledger event while a correction to the same result does not', async () => {
  const storage = makeStorage();
  const posts = [];
  const first = await loadProc({ document: makeDom(), localStorage: storage, posts });
  const original = procedurePayload();
  const sitting = original.sittings[0];
  const proc = first.readProcedure(sitting);
  await first.markWalkStep(original, sitting, proc, proc.steps[1], true);
  const completed = structuredClone(sitting);
  completed.rows = [row('TST-0002')];
  completed.procedure.steps = [completed.procedure.steps[1]];
  completed.procedure.owed_checks = ['TST-0002'];
  const review = procedurePayload({
    sittings: [], unplaced: [], counts: { owed: 0, placed: 0, unplaced: 0 },
    review_sittings: [completed],
    history: { 'TST-0002': [{ platform: 'android', mark: 'pass', reason: '',
      invalidated_by: '' }] },
  });
  const restarted = await loadProc({ document: makeDom(), localStorage: storage,
    posts, verdicts: [{ verdict: 'pass', reason: '' },
      { verdict: 'pass', reason: '' }] });
  const page = restarted.buildWalkPage(review);
  all(page, 'walk-step-alternate')[0].click();
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(posts.length, 1, 'an unchanged correction duplicated the verdict');
  all(page, 'walk-step-rerun')[0].click();
  await new Promise((resolve) => setImmediate(resolve));
  assert.deepEqual(posts.map((event) => event.body.verdict), ['pass', 'pass']);
  assert.equal(review.history['TST-0002'].length, 2);
});

test('a failed correction-index save pauses the ledger write', async () => {
  const storage = makeStorage();
  const normalSet = storage.setItem;
  storage.setItem = (key, value) => {
    if (key.startsWith('cockpit:walk-completed:')) throw new Error('quota');
    normalSet(key, value);
  };
  const posts = [];
  const statuses = [];
  const proc = await loadProc({ document: makeDom(), localStorage: storage,
    posts, statuses });
  const v = procedurePayload();
  const sitting = v.sittings[0];
  const view = proc.readProcedure(sitting);
  await proc.markWalkStep(v, sitting, view, view.steps[1], true);
  assert.deepEqual(posts, []);
  assert.ok(statuses.some((status) => status.message.includes('correction route could not be saved')));
});

test('an invalid completed procedure shows its check instructions and repair reason', async () => {
  const document = makeDom();
  const proc = await loadProc({ document });
  const v = procedurePayload({
    sittings: [], unplaced: [], counts: { owed: 0, placed: 0, unplaced: 0 },
    review_sittings: [],
    review_unavailable: [{ row: row('TST-0002'),
      reason: 'The procedure expectation no longer matches the check.' }],
  });
  const page = proc.buildWalkPage(v);
  assert.match(page.textContent, /procedure needs repair/);
  assert.match(page.textContent, /expectation no longer matches/);
  assert.match(page.textContent, /A signed-out app/);
  assert.match(page.textContent, /It opens/);
});

// ===========================================================================
// FEAT-0151's detailed criteria, B1 to B9 and C1 to C7 (2026-09-24).
//
// One test per criterion that TASK-0629 or TASK-0630 had not yet proved. Each
// drives the real builders through the page's own controls where it can, so
// a criterion is ticked on behaviour and not on a function's return value.
// ===========================================================================

const settle = () => new Promise((resolve) => setImmediate(resolve));
const navOf = (page) => all(page, 'walk-focus-nav')[0];
const visibleSteps = (page) => all(page, 'walk-step')
  .map((step, n) => (step.hidden ? null : n)).filter((n) => n !== null);
const press = (page, label) => {
  const nav = navOf(page);
  const found = [...nav.children, ...all(nav, 'file-row'), ...all(nav, 'review-btn')]
    .find((child) => child.textContent === label);
  assert.ok(found, `no control labelled ${label}: ${nav.textContent}`);
  found.click();
};
const optionsButton = (page, label) => {
  const menu = all(navOf(page), 'walk-options-menu')[0];
  const found = menu.children.find((child) => child.textContent === label);
  assert.ok(found, `no option ${label}`);
  found.click();
};
const twoScreens = () => [1, 2].map((n) => ({
  surface: `Screen ${n}`, surface_note: `SUR-000${n}`, parent: null,
  unresolved: false, captures: [],
  changes: [{ id: `CHG-${n}`, title: null, sentence: `Change ${n}.` }],
}));

test('B1: returning to the survey shows the last screen viewed and Continue keeps the step', async () => {
  const storage = makeStorage();
  const posts = [];
  const { buildWalkPage } = await loadProc({ document: makeDom(), localStorage: storage, posts });
  const page = buildWalkPage(procedurePayload({ survey: twoScreens() }));
  press(page, 'Next screen');
  press(page, 'Start tests');
  optionsButton(page, 'Next step');
  assert.deepEqual(visibleSteps(page), [1]);
  optionsButton(page, 'Changed screens');
  const cards = all(all(page, 'walk-survey')[0], 'walk-survey-surface');
  assert.deepEqual(cards.map((card) => card.hidden), [true, false],
    'the survey reopens on the screen last viewed');
  assert.ok(!navOf(page).textContent.includes('Start tests'));
  press(page, 'Continue at step 2');
  assert.deepEqual(visibleSteps(page), [1], 'Continue returns to the saved step');
  assert.deepEqual(posts, []);
});

test('B3: the session counts done steps and attention, and names steps by display position', async () => {
  const storage = makeStorage();
  const posts = [];
  const { buildWalkPage } = await loadProc({ document: makeDom(), localStorage: storage,
    posts, verdicts: [{ verdict: 'fail', reason: 'the sheet stayed closed' }] });
  const sitting = procedureSitting();
  //: Source numbers 11 to 14 printed as steps 1 to 4, which is what an
  //: owed walk with omitted steps looks like.
  sitting.procedure.steps.forEach((step, n) => {
    step.number = 11 + n;
    step.display_number = n + 1;
  });
  const page = buildWalkPage(procedurePayload({ sittings: [sitting] }));
  assert.match(page.children[0].textContent, /REL-0017, android/);
  press(page, 'Start tests');
  assert.match(navOf(page).textContent, /Step 1 of 4/);
  assert.match(all(navOf(page), 'walk-focus-progress')[0].textContent, /^0 of 4 done$/);
  all(all(page, 'walk-step')[0], 'walk-step-button')[0].click();
  await settle();
  assert.match(all(navOf(page), 'walk-focus-progress')[0].textContent, /^1 of 4 done$/);
  const waiting = all(all(page, 'walk-step')[0], 'walk-step-waiting')[0].textContent;
  assert.equal(waiting, 'TST-0001 waits on step 3', 'a display position, not source step 13');
  all(all(page, 'walk-step')[1], 'walk-step-alternate')[0].click();
  await settle();
  assert.match(all(navOf(page), 'walk-focus-progress')[0].textContent,
    /^2 of 4 done · 1 needs attention$/);
  assert.match(all(page, 'walk-proc-verdicts')[0].textContent, /waiting on step 3/);
  assert.ok(!all(page, 'walk-proc-verdicts')[0].textContent.includes('13'));
});

test('B4: the first step does not repeat the state its open setup already states', async () => {
  const { buildWalkPage } = await loadProc({ document: makeDom() });
  const sitting = procedureSitting();
  sitting.procedure.steps[0].required_state = 'the app installed and never opened';
  sitting.procedure.steps[2].required_state = 'the app installed and never opened';
  const page = buildWalkPage(procedurePayload({ sittings: [sitting] }));
  const section = all(page, 'walk-sitting')[0];
  const said = section.textContent.split('the app installed and never opened').length - 1;
  assert.equal(said, 2, 'once in the setup, once on step 3 where the setup is folded');
  assert.equal(all(all(page, 'walk-step')[0], 'walk-step-state').length, 0);
  assert.equal(all(all(page, 'walk-step')[2], 'walk-step-state').length, 1);
});

test('B5: arrow keys move between screens and steps and record nothing', async () => {
  const storage = makeStorage();
  const posts = [];
  const document = makeDom();
  let dialog = null;
  document.querySelector = (selector) => (selector === '.ask-backdrop' ? dialog : null);
  const api = await loadProc({ document, localStorage: storage, posts });
  const page = api.buildWalkPage(procedurePayload({ survey: twoScreens() }));
  const key = (name, tagName = 'BODY') => api.walkKeyNavigation({
    key: name, target: { tagName }, preventDefault() {},
  });
  assert.equal(key('ArrowRight'), true);
  const cards = all(all(page, 'walk-survey')[0], 'walk-survey-surface');
  assert.deepEqual(cards.map((card) => card.hidden), [true, false]);
  press(page, 'Start tests');
  assert.equal(key('ArrowRight'), true);
  assert.deepEqual(visibleSteps(page), [1]);
  assert.equal(key('ArrowLeft'), true);
  assert.deepEqual(visibleSteps(page), [0]);
  assert.equal(key('ArrowLeft'), false, 'nothing before the first step');
  assert.equal(key('ArrowRight', 'TEXTAREA'), false, 'typing in a field keeps its arrows');
  dialog = {};
  assert.equal(key('ArrowRight'), false, 'an open mark dialog keeps its arrows');
  assert.deepEqual(visibleSteps(page), [0]);
  assert.deepEqual(posts, []);
  assert.equal(storage.getItem('cockpit:walk-steps:ws-1'), null, 'no step was marked');
});

test('B6, B7, C7: a problem stays on its step, stays listed after moving on, and a decision returns to the step', async () => {
  const storage = makeStorage();
  const posts = [];
  const asks = [];
  const statuses = [];
  const api = await loadProc({ document: makeDom(), localStorage: storage, posts, asks,
    statuses, verdicts: [
      { verdict: 'fail', reason: 'the sheet stayed closed' },
      { verdict: 'blocked', reason: 'no second phone today' },
    ] });
  const sitting = procedureSitting();
  sitting.procedure.steps[3].readiness = { kind: 'decision', reason: 'Needs a second phone.' };
  const page = api.buildWalkPage(procedurePayload({ sittings: [sitting] }));
  press(page, 'Start tests');
  optionsButton(page, 'Next step');
  all(all(page, 'walk-step')[1], 'walk-step-alternate')[0].click();
  await settle();
  assert.deepEqual(posts.map((post) => [post.body.id, post.body.verdict]), [['TST-0002', 'fail']]);
  assert.deepEqual(visibleSteps(page), [1], 'Something wrong does not move the reader');
  const card = all(page, 'walk-step')[1];
  assert.match(card.children[0].textContent, /^Step 2 — Settings$/, 'the active card is not renumbered');
  assert.equal(all(card, 'walk-step-button')[0].textContent, 'Recorded — fail · next');

  optionsButton(page, 'Next step');
  assert.deepEqual(visibleSteps(page), [2]);
  const attention = all(navOf(page), 'walk-attention')[0];
  assert.ok(attention, 'the failed step is listed in the main path');
  assert.match(attention.textContent, /Step 2 — fail: the sheet stayed closed/);
  attention.children.find((child) => child.textContent.startsWith('Step 2')).click();
  assert.deepEqual(visibleSteps(page), [1]);

  optionsButton(page, 'Next step');
  optionsButton(page, 'Next step');
  assert.deepEqual(visibleSteps(page), [3]);
  const unavailable = all(all(page, 'walk-step')[3], 'walk-step-unavailable')[0];
  unavailable.children.find((child) => child.textContent.startsWith('TST-0003')).click();
  await settle();
  assert.match(asks[asks.length - 1].detail, /The procedure says: Needs a second phone\./);
  assert.deepEqual(asks[asks.length - 1].only, ['blocked', 'excused', 'na']);
  assert.deepEqual(posts.map((post) => [post.body.id, post.body.verdict]),
    [['TST-0002', 'fail'], ['TST-0003', 'blocked']]);
  assert.deepEqual(visibleSteps(page), [3], 'the decision returns to the same step');
  assert.match(all(all(page, 'walk-step')[3], 'walk-step-decision')[0].textContent,
    /TST-0003 — blocked, recorded as a release decision: no second phone today/);
  assert.ok(statuses.some((status) => /still on step 4/.test(status.message)));
  assert.match(all(navOf(page), 'walk-attention')[0].textContent, /TST-0003 — blocked/);
});

test('B9: finishing the walk with a question and a half-observed check says what is unresolved', async () => {
  const storage = makeStorage();
  const posts = [];
  const api = await loadProc({ document: makeDom(), localStorage: storage, posts,
    verdicts: [{ verdict: 'question', reason: 'the copy is ambiguous' }] });
  const data = procedurePayload();
  const page = api.buildWalkPage(data);
  press(page, 'Start tests');
  all(all(page, 'walk-step')[0], 'walk-step-button')[0].click();
  await settle();
  all(all(page, 'walk-step')[1], 'walk-step-button')[0].click();
  await settle();
  assert.deepEqual(posts.map((post) => [post.body.id, post.body.verdict]), [['TST-0002', 'pass']]);
  optionsButton(page, 'Next step');
  all(all(page, 'walk-step')[3], 'walk-step-alternate')[0].click();
  await settle();
  assert.deepEqual(posts.map((post) => [post.body.id, post.body.verdict]),
    [['TST-0002', 'pass'], ['TST-0003', 'question']]);
  press(page, 'Review results');
  const summary = all(page, 'walk-review-summary')[0];
  assert.match(summary.textContent, /2 checks still need attention/);
  assert.match(summary.textContent, /given a clearing result during this walk: TST-0002 pass/);
  assert.match(summary.textContent,
    /TST-0001 — Check TST-0001: observed in part, waiting on step 3 of A fresh install/);
  assert.match(summary.textContent,
    /TST-0003 — Check TST-0003: question — Step 4: the copy is ambiguous/);
  assert.ok(!all(summary, 'walk-review-state')[0].textContent.includes('Every check'));
  press(page, 'Back to sessions');
  optionsButton(page, 'Changed screens');
  assert.equal(posts.length, 2, 'viewing the survey or the summary writes nothing');
});

test('C1: leaving midway through a two-step check and restarting keeps it open and in place', async () => {
  const storage = makeStorage();
  const posts = [];
  const first = await loadProc({ document: makeDom(), localStorage: storage, posts });
  const data = procedurePayload();
  const page = first.buildWalkPage(data);
  press(page, 'Start tests');
  all(all(page, 'walk-step')[0], 'walk-step-button')[0].click();
  await settle();
  assert.deepEqual(posts, [], 'TST-0001 waits for its second step');
  assert.deepEqual(visibleSteps(page), [1]);

  const restarted = await loadProc({ document: makeDom(), localStorage: storage, posts });
  const again = restarted.buildWalkPage(procedurePayload());
  assert.deepEqual(visibleSteps(again), [1], 'the selected step survives the restart');
  assert.match(navOf(again).textContent, /Step 2 of 4/);
  assert.match(all(navOf(again), 'walk-focus-progress')[0].textContent, /^1 of 4 done$/);
  assert.match(all(navOf(again), 'walk-resume')[0].textContent,
    /You are resuming this walk at step 2/);
  assert.match(all(again, 'walk-proc-verdicts')[0].textContent, /waiting on step 3/);
  assert.deepEqual(posts, [], 'the restart did not pass the check');
  const otherWorkspace = await loadProc({ document: makeDom(), localStorage: storage,
    activeId: 'ws-2' });
  const elsewhere = otherWorkspace.buildWalkPage(procedurePayload());
  assert.equal(all(elsewhere, 'walk-survey')[0].hidden, false,
    'another workspace does not inherit the position');
});

test('C2: a resumed step names the state to restore, the steps that set it up, and that nothing checked it', async () => {
  const storage = makeStorage();
  const posts = [];
  const first = await loadProc({ document: makeDom(), localStorage: storage, posts });
  const sitting = procedureSitting();
  sitting.procedure.steps[0].preparation = true;
  sitting.procedure.steps[0].lines = [{ text: '1. Open the app on the Profile screen.', tags: [] }];
  sitting.procedure.steps[2].required_state = 'Signed in as the FREE rider, Sweet Spot Base running';
  const data = procedurePayload({ sittings: [sitting] });
  const page = first.buildWalkPage(data);
  press(page, 'Start tests');
  optionsButton(page, 'Next step');
  optionsButton(page, 'Next step');
  assert.equal(all(navOf(page), 'walk-resume').length, 0, 'moving within one visit is not a resume');

  const restarted = await loadProc({ document: makeDom(), localStorage: storage, posts });
  const again = restarted.buildWalkPage(data);
  const resume = all(navOf(again), 'walk-resume')[0];
  assert.match(resume.textContent, /You are resuming this walk at step 3/);
  assert.match(resume.textContent,
    /Put the app back in this state before you continue: Signed in as the FREE rider, Sweet Spot Base running/);
  assert.match(resume.textContent, /has not checked this state/);
  const routes = resume.children.filter((child) => child.tagName === 'BUTTON')
    .map((child) => child.textContent);
  assert.deepEqual(routes.slice(0, 2), ['Step 1 — Open the app on the Profile screen.',
    'Step 2 — Tap Settings.']);
  assert.ok(routes.includes('Show required setup'));
  resume.children.find((child) => child.textContent === 'Show required setup').click();
  assert.equal(all(again, 'walk-proc-block')[0].open, true);
  resume.children.find((child) => child.textContent.startsWith('Step 1')).click();
  assert.deepEqual(visibleSteps(again), [0]);
  assert.equal(all(navOf(again), 'walk-resume').length, 0, 'the notice retires once the walker moves');
  assert.deepEqual(posts, []);
});

test('C3: evidence saved before a candidate invalidation no longer answers the comparison', async () => {
  const storage = makeStorage();
  const api = await loadProc({ document: makeDom(), localStorage: storage });
  const sitting = procedureSitting();
  sitting.procedure.steps[0].capture_prompt = 'Record the avatar size.';
  sitting.procedure.steps[2].use_capture = [1];
  const before = procedurePayload({ sittings: [sitting] });
  const view = api.readProcedure(sitting);
  assert.ok(api.saveCurrentWalkEvidence(before, sitting, view, view.steps[0],
    'Avatar 48 px.', 'android debug 41'));
  assert.equal(api.hasRequiredWalkEvidence(before, sitting, view, view.steps[2]), true);

  const after = procedurePayload({ sittings: [sitting], history: {
    'TST-0001': [{ platform: 'android', release: 'REL-0017', mark: 'pass', reason: '',
      invalidated_by: 'CHG-NEW' }] } });
  assert.equal(api.hasRequiredWalkEvidence(after, sitting, view, view.steps[2]), false);
  assert.match(api.buildWalkEvidence(after, sitting, view, view.steps[2]).textContent,
    /Evidence from step 1 was saved before CHG-NEW made this check owed again/);
  assert.match(api.buildWalkEvidence(after, sitting, view, view.steps[0]).textContent,
    /saved before CHG-NEW made this check owed again\. Look again/);
  assert.equal(api.buildStepTick(after, sitting, view, view.steps[2])
    .children[0].disabled, true, 'a stale comparison cannot be passed');

  assert.ok(api.saveCurrentWalkEvidence(after, sitting, view, view.steps[0],
    'Avatar 56 px.', 'android debug 42'));
  assert.equal(api.hasRequiredWalkEvidence(after, sitting, view, view.steps[2]), true);
});

test('C3: an edited step says an earlier mark no longer counts, and another platform inherits nothing', async () => {
  const storage = makeStorage();
  const api = await loadProc({ document: makeDom(), localStorage: storage,
    verdicts: [{ verdict: 'fail', reason: 'the sheet stayed closed' }] });
  const original = procedurePayload();
  const view = api.readProcedure(original.sittings[0]);
  await api.markWalkStep(original, original.sittings[0], view, view.steps[1]);

  const edited = procedurePayload();
  edited.sittings[0].procedure.steps[1].lines[1].quote = 'The sheet slides up from the bottom.';
  assert.deepEqual(api.pruneStepMarks(edited), ['TST-0002']);
  const now = api.readProcedure(edited.sittings[0]);
  const tick = api.buildStepTick(edited, edited.sittings[0], now, now.steps[1]);
  assert.equal(all(tick, 'walk-step-button')[0].textContent, 'Pass and next');
  assert.match(all(tick, 'walk-step-earlier')[0].textContent,
    /You recorded fail on earlier instructions for this step\. That mark does not count now/);

  const ios = procedurePayload({ platform: 'ios' });
  const iosView = api.readProcedure(ios.sittings[0]);
  const iosTick = api.buildStepTick(ios, ios.sittings[0], iosView, iosView.steps[1]);
  assert.equal(all(iosTick, 'walk-step-button')[0].textContent, 'Pass and next');
  assert.equal(all(iosTick, 'walk-step-earlier').length, 0);
});

test('C7: a regenerated procedure lands on the nearest step and says why', async () => {
  const storage = makeStorage();
  const first = await loadProc({ document: makeDom(), localStorage: storage });
  const page = first.buildWalkPage(procedurePayload());
  press(page, 'Start tests');
  optionsButton(page, 'Next step');
  optionsButton(page, 'Next step');
  assert.deepEqual(visibleSteps(page), [2]);

  const rewritten = procedurePayload();
  rewritten.sittings[0].procedure.steps[2].lines[0].quote = 'Go back to Profile.';
  const same = (await loadProc({ document: makeDom(), localStorage: storage }))
    .buildWalkPage(rewritten);
  assert.deepEqual(visibleSteps(same), [2]);
  assert.match(all(navOf(same), 'walk-focus-moved')[0].textContent,
    /The instructions for “Go back\.” changed since you last saw them/);

  const replaced = procedurePayload();
  replaced.sittings[0].procedure.steps[2].head = 'Open Help.';
  const moved = (await loadProc({ document: makeDom(), localStorage: storage }))
    .buildWalkPage(replaced);
  assert.deepEqual(visibleSteps(moved), [2], 'the same position, not the first unmarked step');
  assert.match(all(navOf(moved), 'walk-focus-moved')[0].textContent,
    /The procedure changed since you last saw it: “Go back\.” is no longer in this walk/);

  const renamed = procedurePayload();
  renamed.sittings[0].name = 'A fresh install, rewritten';
  const elsewhere = (await loadProc({ document: makeDom(), localStorage: storage }))
    .buildWalkPage(renamed);
  assert.match(all(navOf(elsewhere), 'walk-focus-moved')[0].textContent,
    /The session “A fresh install” has nothing left to walk on this release/);
});

test('B9: a half-observed check whose saved step failed says so in the summary', async () => {
  const api = await loadProc({ document: makeDom(), localStorage: makeStorage(),
    verdicts: [{ verdict: 'fail', reason: 'the avatar overlaps the name' }] });
  const data = procedurePayload();
  const view = api.readProcedure(data.sittings[0]);
  await api.markWalkStep(data, data.sittings[0], view, view.steps[0]);
  assert.match(api.buildWalkReview(data).textContent,
    /TST-0001 — Check TST-0001: observed in part \(step 1 fail so far\), waiting on step 3 of A fresh install/);
});
