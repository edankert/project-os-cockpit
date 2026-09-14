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
        return this.children.length
          ? this.children.map((c) => c.textContent).join(' ')
          : this._text;
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
  'walkNotice', 'walkBlock', 'walkRowId', 'walkLink', 'buildWalkRefusal',
  // The script (PHASE-044). `buildSurveySection` and `buildSittingSection`
  // call into these, so the page cannot be built without them.
  'buildSurveyCard', 'buildSurveyCaptures', 'walkCaptureSrc', 'walkDocsRel',
  'readProcedure', 'buildProcedureSection', 'buildWalkStep', 'buildStepTick',
  'buildProcedureVerdicts', 'walkLineText', 'walkTagLabel', 'combineStepMarks',
  'stepMarkKey', 'stepSignature', 'walkStepsKey', 'loadStepMarks',
  'saveStepMarks',
  'waitingSteps', 'walkProcedureId', 'walkStepId', 'walkVerdictsId',
];

async function load({ document, navigateTo = () => {}, marks = [] } = {}) {
  const src = await source();
  const bodies = NAMES.map((n) => extract(src, n)).join('\n');
  // `buildCheckRow` is the checks page's row and is exercised by its own
  // tests; here it is a stub that records which check it was asked to draw,
  // so the assertions are about the WALK's ordering and not about the row.
  const stub = `
function buildCheckRow(item, manual, controls, onMark) {
  const row = document.createElement('div');
  row.className = 'checks-row';
  row.dataset.check = item.id || item.number;
  row.addEventListener('click', () => onMark(item));
  return row;
}
function openWalkNote(id) { navigateTo('note:' + id); }
async function markWalkRow(item) { marks.push(item.id); }
async function markWalkStep() {}
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
  const bodies = [...NAMES, 'repaintWalkRow'].map((n) => extract(src, n))
    .join('\n');
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
  'walkNotice', 'walkBlock', 'walkRowId', 'readProcedure', 'combineStepMarks',
  'stepMarkKey', 'stepSignature', 'walkStepsKey', 'loadStepMarks',
  'saveStepMarks', 'pruneStepMarks', 'waitingSteps', 'walkLineText',
  'walkTagLabel',
  'walkDocsRel', 'walkCaptureSrc', 'walkProcedureId', 'walkStepId',
  'walkVerdictsId', 'markWalkStep', 'postCheckVerdict', 'walkOneCheck',
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
  activeId = 'ws-1', asks = [],
} = {}) {
  const src = await source();
  const bodies = PROC_NAMES.map((n) => extract(src, n)).join('\n');
  const stub = `
function buildCheckRow(item, manual, controls, onMark) {
  const row = document.createElement('div');
  row.className = 'checks-row';
  row.dataset.check = item.id || item.number;
  return row;
}
function openWalkNote(id) { navigateTo('note:' + id); }
async function markWalkRow() {}
async function postJson(path, body) { posts.push({ path, body }); return {}; }
function showStatus() {}
function scheduleHide() {}
async function askForMark(opts) {
  asks.push(opts);
  const said = verdicts.shift();
  return said === undefined ? null : said;
}
async function repaintWalkProcedure() { return true; }
const STEP_MARK_CHOICES = ['pass', 'partial', 'fail', 'question'];
const docView = { scrollTop: 0 };
const requestAnimationFrame = (fn) => fn();
let checksHistory = {};
let walkData = null;
`;
  const fn = new Function(
    'document', 'navigateTo', 'posts', 'verdicts', 'localStorage',
    'sidecarBaseUrl', 'activeId', 'asks',
    `${stub}\n${bodies}\nreturn { ${PROC_NAMES.join(', ')} };`,
  );
  return fn(document, navigateTo, posts, verdicts, localStorage,
            sidecarBaseUrl, activeId, asks);
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

test('every printed step is drawn, with the screen it happens on', async () => {
  const document = makeDom();
  const { buildWalkPage } = await loadProc({ document });
  const page = buildWalkPage(procedurePayload());
  const heads = all(page, 'walk-step-head').map((n) => n.textContent);
  assert.deepEqual(heads, [
    'Step 1 — Profile', 'Step 2 — Settings', 'Step 3', 'Step 4 — Profile',
  ]);
});

test('an expectation line shows the check text it quotes and its tags',
  async () => {
    const document = makeDom();
    const { buildWalkPage } = await loadProc({ document });
    const page = buildWalkPage(procedurePayload());
    const lines = all(page, 'walk-step-line')
      .filter((n) => n.className.includes('is-expectation'));
    assert.equal(lines.length, 4);
    //: The quote is the check's own Expect text, and the tag is beside it —
    //: not inside it, where it would read as part of the sentence.
    assert.equal(all(lines[0], 'walk-step-said')[0].textContent,
      'The avatar sits above the name.');
    assert.deepEqual(all(lines[0], 'walk-tag').map((n) => n.textContent),
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
    //: The last segment is what the step CITES, and the number is NOT in
    //: the key: a step number is a position, and positions move.
    assert.deepEqual(Object.keys(held),
      ['REL-0017|android|A fresh install|TST-0001.1']);
    //: Never in the repo and never in the ledger: the only write that left
    //: this tick was the check's own verdict, and there was none to write.
    assert.equal(storage._box.size, 1);
  });

test('a tick spent on a verdict is forgotten when the step stops printing',
  async () => {
    const document = makeDom();
    const storage = makeStorage({
      'cockpit:walk-steps:ws-1': JSON.stringify({
        'REL-0017|android|A fresh install|TST-0002.1': { verdict: 'pass', reason: '' },
        'REL-0017|android|A fresh install|TST-9999.1': { verdict: 'pass', reason: '' },
        'REL-0017|ios|A fresh install|TST-9999.1': { verdict: 'pass', reason: '' },
      }),
    });
    const proc = await loadProc({ document, localStorage: storage });
    proc.pruneStepMarks(procedurePayload());
    const held = JSON.parse(storage.getItem('cockpit:walk-steps:ws-1'));
    //: Step 2 still prints, so its tick stays. Step 9 does not, so the
    //: Android tick is spent — and the iOS one is untouched, because that is
    //: a different walk of the same procedure.
    assert.deepEqual(Object.keys(held).sort(), [
      'REL-0017|android|A fresh install|TST-0002.1',
      'REL-0017|ios|A fresh install|TST-9999.1',
    ]);
  });

test('the page says which step each verdict is still waiting on', async () => {
  const document = makeDom();
  const storage = makeStorage({
    'cockpit:walk-steps:ws-1': JSON.stringify({
      'REL-0017|android|A fresh install|TST-0001.1':
        { verdict: 'pass', reason: '' },
    }),
  });
  const { buildWalkPage } = await loadProc({ document, localStorage: storage });
  const page = buildWalkPage(procedurePayload());
  const states = all(page, 'walk-proc-verdict').map((n) => n.textContent);
  assert.ok(states.some((t) => t.includes('TST-0001')
    && t.includes('waiting on step 3')), states.join(' | '));
});

test('nothing on the procedure moves when a step is ticked', async () => {
  //: [[TASK-0556]]: a list that reorders itself as you tick things is one you
  //: lose your place in. A ticked step keeps its number and its position.
  const document = makeDom();
  const storage = makeStorage({
    'cockpit:walk-steps:ws-1': JSON.stringify({
      'REL-0017|android|A fresh install|TST-0001.2':
        { verdict: 'fail', reason: 'no' },
    }),
  });
  const { buildWalkPage } = await loadProc({ document, localStorage: storage });
  const page = buildWalkPage(procedurePayload());
  const order = all(page, 'walk-step-head').map((n) => n.textContent);
  assert.deepEqual(order, [
    'Step 1 — Profile', 'Step 2 — Settings', 'Step 3', 'Step 4 — Profile',
  ]);
  const ticked = all(page, 'walk-step-button')
    .filter((n) => n.textContent.includes('step 3'));
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

test('a card whose key has no picture at either end shows its sentences only',
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
  //: And four marks, never the three settle ones ([[ADR-0041]]).
  assert.deepEqual(asks[0].only, ['pass', 'partial', 'fail', 'question']);
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
  assert.equal(ticks[0], 'tick step 1',
    'the new first step inherited the old first step\'s mark');
  //: And the step that genuinely holds the mark still shows it, at its new
  //: number — the tick followed what it settles, not where it sat.
  assert.ok(ticks.some((label) => /step 2 — pass/.test(label)), ticks.join(' | '));
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
