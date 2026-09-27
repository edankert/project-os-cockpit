// The release test page's rules ([[FEAT-0155]], [[TASK-0643]]).
//
// Run from the BUILT `release-test.js`, the file the shell loads, rather than
// by asserting that a string appears in the TypeScript (ISS-0055). Only the
// pure functions are exercised: which result a test note gets, what a check
// shows, what asks for the owner, where Continue goes, and how the walk
// page's saved state is carried over.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import * as vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const built = path.join(here, '..', 'dist', 'renderer', 'release-test.js');

async function load() {
  const context = vm.createContext({ console });
  vm.runInContext(await fs.readFile(built, 'utf8'), context);
  return context;
}

/** A value from the sandbox, as a plain value of this realm. */
const plain = (v) => JSON.parse(JSON.stringify(v));

function check(number, tags, checks, extra = {}) {
  return {
    number, action: `Do ${number}.`, tags, checks, preparation: !checks.length,
    start: '', readiness: null, timer: 0, capture: '', compare_with: [], path: '',
    expected: [{ text: `See ${number}.`, tags, passed: [] }], ...extra,
  };
}

function page(results = {}) {
  const hub = {
    number: 1, name: 'Equipment Hub', slug: 'equipment-hub', unplaced: false,
    count: 4, owed: 2, tests: ['TST-0001', 'TST-0002'], bench_line: 'KICKR',
    state: '', procedure: 'p.md', problems: [], what_changed: [], nothing_changed: false,
    setup: { bench: [], before: [], later: [] }, omitted: 0, progress: { done: 0, total: 3 },
    groups: [{ title: 'Layout', start: 'Hub open.', checks: [
      check(1, ['TST-0001.1'], ['TST-0001']),
      check(2, [], []),
      check(3, ['TST-0001.2'], ['TST-0001']),
      check(4, ['TST-0002'], ['TST-0002']),
    ] }],
  };
  const rides = {
    ...hub, number: 2, name: 'Rides', slug: 'rides', tests: ['TST-0003'], owed: 1,
    groups: [{ title: '', start: '', checks: [check(1, ['TST-0003'], ['TST-0003'])] }],
  };
  return { platform: 'android', release: 'REL-0017', error: '', sections: [hub, rides], results };
}

function mark(rt, p, sectionIndex, number, result, reason = '') {
  const section = p.sections[sectionIndex];
  const c = section.groups.flatMap((g) => g.checks).find((x) => x.number === number);
  return [rt.rtCheckKey(p, section, c), { result, reason, at: '' }];
}

test('a test note gets a result only when every printed check citing it has one', async () => {
  const rt = await load();
  const p = page();
  let marks = Object.fromEntries([mark(rt, p, 0, 1, 'pass')]);
  assert.equal(rt.rtNoteResults(p, marks)['TST-0001'], undefined,
    'check 3 also cites TST-0001 and has no result yet');
  marks = Object.fromEntries([mark(rt, p, 0, 1, 'pass'), mark(rt, p, 0, 3, 'pass')]);
  assert.equal(rt.rtNoteResults(p, marks)['TST-0001'].result, 'pass');
});

test('the note takes the most serious result, with each reason named by check', async () => {
  const rt = await load();
  const p = page();
  const marks = Object.fromEntries([
    mark(rt, p, 0, 1, 'pass'), mark(rt, p, 0, 3, 'fail', 'Slot empty'),
  ]);
  const note = rt.rtNoteResults(p, marks)['TST-0001'];
  assert.equal(note.result, 'fail');
  assert.equal(note.reason, 'check 3: Slot empty');
  assert.equal(rt.rtWorst(['pass', 'na']), 'pass', 'N/A where it does not exist, pass elsewhere');
  assert.equal(rt.rtWorst(['fail', 'question']), 'question', 'an unclear check outranks a failure');
  assert.equal(rt.rtWorst(['partial', 'blocked', 'excused']), 'blocked');
});

test('a result other than Pass is not written without its reason', async () => {
  const rt = await load();
  const p = page();
  const marks = Object.fromEntries([mark(rt, p, 0, 4, 'blocked')]);
  assert.equal(rt.rtNoteResults(p, marks)['TST-0002'], undefined);
  const withReason = Object.fromEntries([mark(rt, p, 0, 4, 'blocked', 'No meter')]);
  assert.equal(rt.rtNoteResults(p, withReason)['TST-0002'].result, 'blocked');
});

test('a check with no result here shows the ledger result of its notes', async () => {
  const rt = await load();
  const p = page({ 'TST-0002': { result: 'pass', reason: '', date: '2026-09-20' } });
  const section = p.sections[0];
  const c4 = section.groups[0].checks[3];
  assert.deepEqual(plain(rt.rtCheckState(p, section, c4, {})),
    { result: 'pass', reason: '', source: 'ledger' });
  const c1 = section.groups[0].checks[0];
  assert.equal(rt.rtCheckState(p, section, c1, {}).result, '', 'TST-0001 has no ledger result');
});

test('the tally counts checks that take a result, and preparation is not one', async () => {
  const rt = await load();
  const p = page();
  const marks = Object.fromEntries([mark(rt, p, 0, 1, 'pass'), mark(rt, p, 0, 4, 'fail', 'x')]);
  const tally = rt.rtSectionTally(p, p.sections[0], marks);
  assert.equal(tally.total, 3);
  assert.equal(tally.done, 2);
  assert.deepEqual(plain(tally.counts), { pass: 1, fail: 1 });
});

test('Needs you lists failures, questions, blocks and partials, and a refused procedure', async () => {
  const rt = await load();
  const p = page();
  p.sections[1].problems = ['it no longer covers TST-0003'];
  const marks = Object.fromEntries([mark(rt, p, 0, 1, 'pass'), mark(rt, p, 0, 4, 'fail', 'Wrong slot')]);
  const needs = rt.rtNeedsYou(p, marks);
  assert.deepEqual(plain(needs.map((n) => [n.section.slug, n.check ? n.check.number : null, n.result])),
    [['equipment-hub', 4, 'fail'], ['rides', null, 'question']]);
});

test('Continue goes to the first check with no result, starting in the last section opened', async () => {
  const rt = await load();
  const p = page();
  const marks = Object.fromEntries([mark(rt, p, 0, 1, 'pass')]);
  assert.equal(rt.rtContinue(p, marks, '').check.number, 3, 'check 2 is preparation');
  assert.equal(rt.rtContinue(p, marks, 'rides').section.slug, 'rides');
});

test('a check is kept by its tags and action, so its number can change', async () => {
  const rt = await load();
  const p = page();
  const section = p.sections[0];
  const c = section.groups[0].checks[2];
  const key = rt.rtCheckKey(p, section, c);
  const renumbered = { ...c, number: 2 };
  assert.equal(rt.rtCheckKey(p, section, renumbered), key);
  assert.notEqual(rt.rtCheckKey(p, section, { ...c, action: 'Do something else.' }), key);
});

test("the walk page's saved step results move to the check with the same tags", async () => {
  const rt = await load();
  const p = page();
  const sig = (tags) => JSON.stringify({ head: 'x', lines: [['t', '', tags]] });
  const old = {
    [`REL-0017|android|Equipment Hub|${sig([['TST-0001', '2']])}`]: { verdict: 'pass', reason: '' },
    [`REL-0017|android|Equipment Hub|${sig([['TST-0009', '1']])}`]: { verdict: 'fail', reason: 'gone' },
    [`REL-0017|ios|Equipment Hub|${sig([['TST-0001', '2']])}`]: { verdict: 'pass', reason: '' },
  };
  const { marks, used } = rt.rtCarryWalkMarks(p, old);
  const section = p.sections[0];
  const c3 = section.groups[0].checks[2];
  assert.equal(marks[rt.rtCheckKey(p, section, c3)].result, 'pass');
  assert.equal(Object.keys(marks).length, 1, 'a step that no longer exists is dropped');
  assert.equal(used.length, 2, 'the iOS entry belongs to the iOS page and is left for it');
});

test('the five walk storage keys are moved once, and a saved place gets the new address', async () => {
  const rt = await load();
  const store = new Map([
    ['cockpit:walk-place:ws', '~walk/android'],
    ['cockpit:walk-steps:ws', '{}'],
    ['cockpit:release-test-focus:ws', 'kept'],
    ['cockpit:walk-focus:ws', 'older'],
  ]);
  const api = {
    getItem: (k) => (store.has(k) ? store.get(k) : null),
    setItem: (k, v) => store.set(k, v),
    removeItem: (k) => store.delete(k),
  };
  const moved = rt.rtMigrateStorage(api, 'ws');
  assert.deepEqual(plain([...moved].sort()), ['walk-focus', 'walk-place', 'walk-steps']);
  assert.equal(store.get('cockpit:release-test-place:ws'), '~release-test/android');
  assert.equal(store.get('cockpit:release-test-focus:ws'), 'kept', 'a value under the new name wins');
  assert.ok(![...store.keys()].some((k) => k.startsWith('cockpit:walk-')), 'every old key is removed');
  assert.deepEqual(plain(rt.rtMigrateStorage(api, 'ws')), [], 'a second run moves nothing');
});

test('the old addresses open the release test', async () => {
  const rt = await load();
  assert.equal(rt.rtAddressFor('~walk'), '~release-test');
  assert.equal(rt.rtAddressFor('~walk/ios'), '~release-test/ios');
  assert.equal(rt.rtAddressFor('~walker'), '~walker');
});

test('the Tests view owns the release test pages, so a write never lands the reader elsewhere', async () => {
  // From the built renderer, the function the landing guard calls (ISS-0263).
  const src = await fs.readFile(path.join(here, '..', 'dist', 'renderer', 'renderer.js'), 'utf8');
  const start = src.indexOf('const VIEW_OWNED_PAGES');
  const table = src.slice(start, src.indexOf('};', start) + 2);
  const fnStart = src.indexOf('function onOwnedPage(');
  let depth = 0;
  let i = src.indexOf('{', fnStart);
  for (; i < src.length; i += 1) {
    if (src[i] === '{') depth += 1;
    else if (src[i] === '}') { depth -= 1; if (depth === 0) break; }
  }
  const onOwnedPage = new Function(`${table}\n${src.slice(fnStart, i + 1)}\nreturn onOwnedPage;`)();
  assert.equal(onOwnedPage('tests', '~release-test/android/equipment-hub'), true);
  assert.equal(onOwnedPage('tests', '~release-test'), true);
  assert.equal(onOwnedPage('publication', '~release-test/android'), false,
    'the release test left Publication with the walk page');
  assert.equal(onOwnedPage('publication', '~release/next'), true);
});

test('after a result the overview counts, Continue and Needs you change without a reload', async () => {
  // The overview is drawn from the browser's results every time it opens, so
  // a result given on a section page is in it the next time it is drawn.
  const rt = await load();
  const p = page();
  const before = {};
  const after = Object.fromEntries([mark(rt, p, 0, 1, 'fail', 'Wrong name')]);
  assert.equal(rt.rtSectionTally(p, p.sections[0], before).done, 0);
  assert.equal(rt.rtSectionTally(p, p.sections[0], after).done, 1);
  assert.equal(rt.rtContinue(p, before, '').check.number, 1);
  assert.equal(rt.rtContinue(p, after, '').check.number, 3);
  assert.equal(rt.rtNeedsYou(p, before).length, 0);
  assert.equal(rt.rtNeedsYou(p, after)[0].text, 'Wrong name');
  assert.equal(rt.rtDotState(rt.rtSectionTally(p, p.sections[0], after)), 'bad');
});

test('a readiness problem with no result asks for the owner', async () => {
  const rt = await load();
  const p = page();
  p.sections[1].groups[0].checks[0].readiness = {
    kind: 'preparation', reason: 'No way to set this up yet.', issue: 'ISS-0512', result: 'blocked' };
  const needs = rt.rtNeedsYou(p, {});
  assert.deepEqual(plain(needs.map((n) => [n.section.slug, n.result, n.text])),
    [['rides', 'blocked', 'No way to set this up yet. (ISS-0512)']]);
});

test('Needs you shows one entry for one reason, naming every check it holds', async () => {
  const rt = await load();
  const p = page();
  // TST-0001 failed in the ledger; checks 1 and 3 both cite it.
  p.results['TST-0001'] = { result: 'fail', reason: 'The slot is empty.', date: '2026-09-27' };
  const needs = rt.rtNeedsYou(p, {});
  assert.deepEqual(plain(needs.map((n) => [n.section.slug, n.result, n.text, n.checks])),
    [['equipment-hub', 'fail', 'The slot is empty.', [1, 3]]]);
});


test("the platform row in the pane counts what Needs you lists, and drops the count at zero", async () => {
  const context = vm.createContext({
    console,
    document: { createElement: () => ({ className: '', textContent: '', title: '', removed: false,
      remove() { this.removed = true; } }) },
  });
  vm.runInContext(await fs.readFile(built, 'utf8'), context);
  const added = [];
  const title = { after: (node) => added.push(node) };
  const item = { querySelector: (sel) => sel === '.nav-title' ? title
    : sel.includes('rt-nav-needs') ? added.find((n) => !n.removed) || null : null };
  const li = { querySelector: (sel) => sel === ':scope > .nav-item' ? item : null };
  const p = page();
  const marks = Object.fromEntries([mark(context, p, 0, 1, 'fail', 'Slot missing'), mark(context, p, 1, 1, 'question', 'Which one?')]);
  const n = context.rtNeedsYou(p, marks).length;
  assert.equal(n, 2);
  context.rtSetNavNeeds(li, n);
  assert.equal(added.length, 1);
  assert.equal(added[0].textContent, '2');
  assert.match(added[0].className, /rt-nav-needs/);
  context.rtSetNavNeeds(li, 0);
  assert.equal(added[0].removed, true);
});
