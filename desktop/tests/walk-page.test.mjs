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
      surface: 'Profile', surface_note: 'SUR-0001', checks: ['TST-0001'],
      changes: [{ id: 'TASK-0001', title: 'Rewrote it', reopened: 'It moved.' }],
    }],
  }));
  const sections = page.children.filter(
    (c) => c.className.includes('walk-survey')
      || c.className.includes('walk-sittings'));
  assert.equal(sections[0].className, 'walk-survey');
  const quoted = all(page, 'walk-reopened');
  assert.equal(quoted.length, 1);
  assert.equal(quoted[0].textContent, 'It moved.');
});

test('a cause the index could not resolve is named, never dropped', async () => {
  const document = makeDom();
  const { buildSurveySection } = await load({ document });
  const section = buildSurveySection(payload({
    survey: [{
      surface: 'Profile', surface_note: null, checks: ['TST-0001'],
      changes: [{ id: 'TASK-9999', title: null, reopened: null }],
    }],
  }));
  const causes = all(section, 'walk-survey-cause');
  assert.equal(causes.length, 1);
  assert.match(causes[0].textContent, /TASK-9999/);
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
  const bodies = ['walkOneCheck', 'markWalkRow'].map((n) => extract(src, n))
    .join('\n');
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
