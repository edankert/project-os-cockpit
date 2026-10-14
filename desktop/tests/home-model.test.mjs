// What the draft home window shows (FEAT-0160).
//
// Runs against the BUILT file, evaluated the way the page loads it: a plain
// script defining globals, like `deep-link.js`.

import { test, before } from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import * as vm from 'node:vm';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const here = path.dirname(fileURLToPath(import.meta.url));
const built = path.join(here, '..', 'dist', 'renderer', 'home-model.js');
const builtLink = path.join(here, '..', 'dist', 'renderer', 'deep-link.js');
const payload = createRequire(import.meta.url)(path.join(here, '..', 'dist', 'ipc', 'home-payload.js'));

let m;
let parseLink;
before(async () => {
  const linkCtx = vm.createContext({});
  vm.runInContext(`${await fs.readFile(builtLink, 'utf-8')}\n;globalThis.__p = parseCockpitLink;`, linkCtx);
  parseLink = (url) => JSON.parse(JSON.stringify(linkCtx.__p(url)));
  await fs.access(built);            // fail loudly rather than skip silently
  const src = await fs.readFile(built, 'utf-8');
  const ctx = vm.createContext({});
  vm.runInContext(`${src}
;globalThis.__m = { homeOwedRows, homeSortOwed, homeLinkTarget, homeActivePhases,
  homePlannedCount, homePhaseAnswers, homeAgentWord, homeAgentRank, homeOwedEmptyText,
  homeVerbGlyph, homeBoard, homeVerbTotals };`, ctx);
  const plain = (v) => JSON.parse(JSON.stringify(v));
  m = Object.fromEntries(Object.entries(ctx.__m).map(([k, f]) => [k, (...a) => plain(f(...a))]));
});

const ws = { workspaceId: 'w1', project: 'Your Trainer', projectId: 'your-trainer' };

test('a thing owed that has a note is one row with its own verb', () => {
  const rows = m.homeOwedRows(ws, [{
    kind: 'adr', verb: 'Decide', noun: 'ADRs', label: 'Decide 2 ADRs', count: 2,
    items: [
      { id: 'ADR-0011', title: 'Speed shown', rel: 'decisions/ADR-0011-X.md', verb: 'Decide' },
      { id: 'ADR-0012', title: 'Another', rel: 'decisions/ADR-0012-Y.md' },
    ],
  }]);
  assert.equal(rows.length, 2);
  assert.deepEqual(rows[0], { ...ws, verb: 'Decide', id: 'ADR-0011', title: 'Speed shown', rel: 'decisions/ADR-0011-X.md', page: '', count: 1 });
  assert.equal(rows[1].verb, 'Decide', 'an item with no verb takes its group\'s');
});

test('seventy-three commits to push are one row, not seventy-three', () => {
  const items = Array.from({ length: 73 }, (_, i) => ({ id: `c${i}`, title: `commit ${i}`, rel: '', url: '~history' }));
  const rows = m.homeOwedRows(ws, [{ kind: 'unpushed commit', verb: 'Push', noun: 'commits', label: 'Push 73 commits', count: 73, items }]);
  assert.equal(rows.length, 1);
  assert.equal(rows[0].title, 'Push 73 commits');
  assert.equal(rows[0].id, '');
  assert.equal(rows[0].rel, '');
  assert.equal(rows[0].page, '~history', 'the row opens the page where the push is done');
  assert.equal(rows[0].count, 73, 'the one mark carries the number it stands for');
  assert.equal(m.homeLinkTarget(rows[0].id, rows[0].rel, rows[0].page), '~history');
});

test('a group that names no items still shows as one row, and an empty group shows nothing', () => {
  assert.equal(m.homeOwedRows(ws, [{ verb: 'Push', label: 'Push 4 commits', count: 4 }]).length, 1);
  assert.equal(m.homeOwedRows(ws, [{ verb: 'Push', label: 'Push 0 commits', count: 0, items: [] }]).length, 0);
  assert.deepEqual(m.homeOwedRows(ws, undefined), []);
});

test('decisions sort before housekeeping, and an unknown verb sorts last but stays', () => {
  const row = (verb, project, id) => ({ ...ws, project, verb, id, title: id, rel: 'x.md' });
  const sorted = m.homeSortOwed([
    row('Push', 'b', ''), row('Frobnicate', 'a', 'X-1'), row('Triage', 'a', 'ISS-2'),
    row('Decide', 'b', 'ADR-2'), row('Decide', 'a', 'ADR-9'), row('Accept', 'a', 'DES-1'),
  ]);
  assert.deepEqual(sorted.map((r) => `${r.verb}/${r.project}/${r.id}`), [
    'Decide/a/ADR-9', 'Decide/b/ADR-2', 'Accept/a/DES-1', 'Triage/a/ISS-2', 'Push/b/', 'Frobnicate/a/X-1',
  ]);
});

test('a row opens by its note ID when the link parser would read it as one', () => {
  assert.equal(m.homeLinkTarget('ADR-0026', 'decisions/ADR-0026-X.md'), 'ADR-0026');
  assert.equal(m.homeLinkTarget('phase-028', 'phases/PHASE-028-X.md'), 'PHASE-028');
  // A change note's ID is not `LETTERS-digits`, so it opens by path, from the repository root.
  assert.equal(m.homeLinkTarget('CHG-20260927-The-Walk', 'changes/CHG-20260927-The-Walk.md'), 'docs/changes/CHG-20260927-The-Walk.md');
  assert.equal(m.homeLinkTarget('', ''), '', 'nothing to open means the project alone');
  assert.equal(m.homeLinkTarget('', '../outside.md'), '', 'a path that leaves the repository is not sent');
  assert.equal(m.homeLinkTarget('', '', 'https://example.com'), '', 'only the present window\'s own pages are sent');
});

const phase = {
  key: 'PHASE-019', title: 'iOS Parity — the long explanation', status: 'active', rel: 'phases/PHASE-019.md',
  tasks: { done: 40, in_progress: 2, backlog: 28 }, waiting: 1,
  features: [
    { id: 'FEAT-0001', title: 'One', bucket: 'done' },
    { id: 'FEAT-0085', title: 'BLE Reliability Layer — and why', bucket: 'in_progress' },
    { id: 'FEAT-0127', title: 'Debug builds', bucket: 'backlog' },
  ],
};

test('a phase answers the four questions', () => {
  const a = m.homePhaseAnswers(phase);
  assert.equal(a.title, 'iOS Parity');
  assert.equal(a.done, 1);
  assert.deepEqual(a.now, [{ id: 'FEAT-0085', label: 'FEAT-0085 BLE Reliability Layer' }]);
  assert.deepEqual(a.next, [{ id: 'FEAT-0127', label: 'FEAT-0127 Debug builds' }]);
  assert.equal(a.left, '30 tasks still open, 1 waiting on you.');
});

test('a phase with nothing open says so, and one task is singular', () => {
  const done = m.homePhaseAnswers({ key: 'P', tasks: { done: 3, in_progress: 0, backlog: 0 }, features: [{ id: 'F', title: 'x', bucket: 'done' }] });
  assert.equal(done.left, 'No task or feature is open.');
  const one = m.homePhaseAnswers({ key: 'P', tasks: { in_progress: 1 }, features: [] });
  assert.equal(one.left, '1 task still open.');
  // Features still open with no task written yet is not "nothing left".
  const untasked = m.homePhaseAnswers({ key: 'P', tasks: {}, features: [{ id: 'F', title: 'x', bucket: 'backlog' }] });
  assert.equal(untasked.left, 'Features are still open, and no task is written for them yet.');
});

test('only active phases are listed; planned ones are counted, without the parking lot', () => {
  const phases = [{ key: 'A', status: 'active' }, { key: 'B', status: 'planned' }, { key: 'PHASE-999', status: 'planned' }, { key: 'C', status: 'done' }];
  assert.deepEqual(m.homeActivePhases(phases).map((p) => p.key), ['A']);
  assert.equal(m.homePlannedCount(phases), 1);
});

test('an agent state reads as one of six words, and an unknown state is never "working"', () => {
  assert.equal(m.homeAgentWord('busy', true), 'working');
  assert.equal(m.homeAgentWord('needs-input', true), 'needs your answer');
  assert.equal(m.homeAgentWord('waiting', true), 'finished its turn');
  assert.equal(m.homeAgentWord('error', true), 'stuck');
  assert.equal(m.homeAgentWord('idle', true), 'quiet');
  assert.equal(m.homeAgentWord(null, true), 'quiet');
  assert.equal(m.homeAgentWord('something-new', true), 'quiet');
  assert.equal(m.homeAgentWord('busy', false), 'not open');
  assert.ok(m.homeAgentRank('needs your answer') < m.homeAgentRank('working'));
  assert.ok(m.homeAgentRank('working') < m.homeAgentRank('quiet'));
});

test('every owed row carries exactly one verb', () => {
  const rows = m.homeOwedRows(ws, [
    { verb: 'Decide', items: [{ id: 'ADR-0001', title: 'a', rel: 'd/a.md' }, { id: 'ADR-0002', title: 'b', rel: 'd/b.md', verb: 'Decide' }] },
    { verb: 'Push', noun: 'commits', label: 'Push 2 commits', count: 2, items: [{ id: 'c1', rel: '' }, { id: 'c2', rel: '' }] },
  ]);
  for (const r of rows) assert.match(r.verb, /^[A-Z][a-z]+$/, JSON.stringify(r));
});

test('the link a row sends is read back by the link parser as the same project and target', () => {
  const link = (id, rel) => {
    const target = m.homeLinkTarget(id, rel);
    // What main builds from the page's request (home-window.ts, `home:open`).
    return target
      ? `cockpit://your-trainer/${target.split('/').map(encodeURIComponent).join('/')}`
      : 'cockpit://your-trainer';
  };
  assert.deepEqual(parseLink(link('ADR-0011', 'decisions/ADR-0011-X.md')),
    { project: 'your-trainer', target: { kind: 'note', id: 'ADR-0011' } });
  assert.deepEqual(parseLink(link('CHG-20260927-The Walk', 'changes/CHG-20260927-The Walk.md')),
    { project: 'your-trainer', target: { kind: 'path', rel: 'docs/changes/CHG-20260927-The Walk.md' } });
  assert.deepEqual(parseLink(link('', '')), { project: 'your-trainer', target: { kind: 'none' } });
  assert.deepEqual(parseLink(`cockpit://your-trainer/${m.homeLinkTarget('', '', '~history')}`),
    { project: 'your-trainer', target: { kind: 'path', rel: '~history' } });
});

test('a project that was not read never becomes "nothing needs you"', () => {
  assert.equal(m.homeOwedEmptyText([{ notRead: null }, { notRead: null }]), 'Nothing needs you.');
  const mixed = m.homeOwedEmptyText([{ notRead: null }, { notRead: 'it is not open in the cockpit' }]);
  assert.match(mixed, /1 project that was read/);
  assert.match(mixed, /1 was not read/);
  const none = m.homeOwedEmptyText([{ notRead: 'x' }, { notRead: 'y' }]);
  assert.doesNotMatch(none, /Nothing needs you/);
  assert.match(none, /No project could be read/);
  assert.equal(m.homeOwedEmptyText([]), 'No project was found.');
});

test('unticked exit criteria are listed as what still stands', () => {
  const a = m.homePhaseAnswers({ ...phase, exit: [
    { text: 'Every screen has its counterpart', done: true },
    { text: 'The release test has been walked', done: false },
    { text: 'A ride uploads', done: false } ] });
  assert.deepEqual(a.stands, ['The release test has been walked', 'A ride uploads']);
  assert.equal(a.criteria, '2 of 3 exit criteria not ticked yet:');
});

test('not read, none written and all ticked are three different sentences', () => {
  const said = (exit) => m.homePhaseAnswers({ ...phase, exit }).criteria;
  assert.equal(said(null), 'Its exit criteria were not read.');
  assert.equal(said(undefined), 'Its exit criteria were not read.');
  assert.equal(said([]), 'The phase note lists no exit criteria.');
  assert.equal(said([{ text: 'x', done: true }]), 'Its one exit criterion is ticked.');
  assert.equal(said([{ text: 'x', done: true }, { text: 'y', done: true }]), 'All 2 exit criteria are ticked.');
  assert.equal(said([{ text: 'x', done: false }]), '1 of 1 exit criterion not ticked yet:');
  assert.equal(new Set([said(null), said([]), said([{ text: 'x', done: true }])]).size, 3);
});

test('the payload keeps active and planned phases only, focus first', () => {
  // The focus phase has the LATER key, so only the focus rule can put it first.
  const stats = { focus: { items: { phase: { id: 'PHASE-021' } } }, phases: [
    { key: 'PHASE-001', status: 'done' }, { key: 'PHASE-030', status: 'planned' },
    { key: 'PHASE-021', status: 'active', tasks: { done: 2 } },
    { key: 'PHASE-019', status: 'active', title: 'iOS', waiting: 1, tasks: { in_progress: 2, backlog: 28 },
      features: [{ id: 'FEAT-0085', title: 'BLE', status: 'doing', bucket: 'in_progress', children: [1, 2, 3] }] },
    { key: 'PHASE-040', status: 'deferred' }, { key: 'unphased', status: null } ] };
  const out = payload.trimPhases(stats);
  assert.deepEqual(out.map((p) => p.key), ['PHASE-021', 'PHASE-019', 'PHASE-030']);
  assert.equal(out[0].focus, true);
  assert.equal(out[1].focus, false);
  assert.deepEqual(out[1].tasks, { done: 0, in_progress: 2, backlog: 28 });
  assert.deepEqual(out[1].features, [{ id: 'FEAT-0085', title: 'BLE', status: 'doing', bucket: 'in_progress' }]);
  assert.equal(out[1].exit, null, 'criteria are unread until fetched, not empty');
  assert.deepEqual(payload.trimPhases(null), []);
});

test('exit criteria are taken only from an answer about the same phase, and read plainly', () => {
  const scoped = { scope: { id: 'PHASE-028' }, exit_criteria: [
    { text: 'Supervised from a phone without widening what [[RISK-0005]] forbids — evidence: <the path>', done: false },
    { text: 'See [[ADR-0009-The-Principal|the principal]] rule', done: true } ] };
  assert.deepEqual(payload.trimCriteria(scoped, 'PHASE-028'), [
    { text: 'Supervised from a phone without widening what RISK-0005 forbids', done: false },
    { text: 'See the principal rule', done: true } ]);
  assert.equal(payload.trimCriteria(scoped, 'PHASE-029'), null, 'an answer about another phase is not this one\'s');
  assert.equal(payload.trimCriteria(null, 'PHASE-028'), null);
  assert.equal(payload.trimCriteria({ scope: { id: 'PHASE-028' }, exit_criteria: null }, 'PHASE-028'), null);
});

test('a release is shown only while one is being prepared', () => {
  assert.deepEqual(
    payload.trimRelease({ exists: true, preparing: true, id: 'REL-0017', version: '2.2.0', status: 'draft', rel: 'r.md', open_tests: [1, 2], settle: [1] }),
    { id: 'REL-0017', version: '2.2.0', status: 'draft', rel: 'r.md', openTests: 2, toSettle: 1 });
  assert.equal(payload.trimRelease({ exists: true, preparing: false, id: 'REL-0016' }), null);
  assert.equal(payload.trimRelease({ exists: false }), null);
  assert.equal(payload.trimRelease(null), null);
});

// ---- The picture: the board the window draws ------------------------------

test('every verb has a mark, and a verb nobody knows still gets one', () => {
  for (const v of ['Decide', 'Accept', 'Approve', 'Run', 'Confirm', 'Triage', 'Push', 'Deploy']) {
    assert.equal(m.homeVerbGlyph(v), v.toLowerCase());
  }
  assert.equal(m.homeVerbGlyph('Frobnicate'), 'other');
  assert.equal(m.homeVerbGlyph(''), 'other');
  assert.equal(new Set(['Decide', 'Accept', 'Approve', 'Run', 'Confirm', 'Triage', 'Push', 'Deploy'].map(m.homeVerbGlyph)).size, 8,
    'no two verbs share a mark');
});

test('a phase is drawn as one mark per feature, finished first, then its exit criteria', () => {
  const a = m.homePhaseAnswers({ ...phase, features: [
    { id: 'F3', title: 'c', bucket: 'backlog' }, { id: 'F1', title: 'a', bucket: 'done' }, { id: 'F2', title: 'b', bucket: 'in_progress' } ],
    exit: [{ text: 'x', done: true }, { text: 'y', done: false }] });
  assert.deepEqual(a.segments.map((s) => `${s.id}:${s.state}`), ['F1:done', 'F2:now', 'F3:next']);
  assert.deepEqual(a.exit, [{ text: 'x', done: true }, { text: 'y', done: false }]);
  assert.deepEqual(a.tasks, { done: 40, now: 2, next: 28 });
  assert.equal(m.homePhaseAnswers(phase).exit, null, 'criteria that were not read are null, not an empty list');
});

const boardProjects = [
  { workspaceId: 'w1', project: 'quiet-one', projectId: 'quiet-one', notRead: null, owed: [], phases: [] },
  { workspaceId: 'w2', project: 'busy-one', projectId: 'busy-one', notRead: null,
    owed: [{ verb: 'Triage', items: [{ id: 'ISS-0001', title: 't', rel: 'i/1.md' }] }], phases: [phase, { key: 'P2', status: 'planned' }] },
  { workspaceId: 'w3', project: 'asking-one', projectId: 'asking-one', notRead: null,
    owed: [{ verb: 'Push', noun: 'commits', label: 'Push 5 commits', count: 5, items: Array.from({ length: 5 }, () => ({ id: 'c', rel: '', url: '~history' })) },
           { verb: 'Decide', items: [{ id: 'ADR-0001', title: 'd', rel: 'd/1.md' }, { id: 'ADR-0002', title: 'e', rel: 'd/2.md' }] }], phases: [] },
  { workspaceId: 'w4', project: 'closed-one', projectId: 'closed-one', notRead: 'it is not open in the cockpit', owedCount: 3, owed: [], phases: [] },
  { workspaceId: 'w5', project: 'also-quiet', projectId: 'also-quiet', notRead: null, owed: [{ verb: 'Run', items: [{ id: 'TST-0001', title: 'r', rel: 't/1.md' }] }], phases: [] },
];
const boardFleet = [
  { workspaceId: 'w1', state: 'idle', live: true }, { workspaceId: 'w2', state: 'busy', live: true, lastPrompt: 'do  the\nthing' },
  { workspaceId: 'w3', state: 'needs-input', live: true, message: 'May I?' }, { workspaceId: 'w4', state: null, live: false },
];

test('the board puts the projects that want a person first', () => {
  const rows = m.homeBoard(boardProjects, boardFleet);
  assert.deepEqual(rows.map((r) => `${r.project}:${r.word}`), [
    'asking-one:needs your answer', 'busy-one:working', 'also-quiet:quiet', 'quiet-one:quiet', 'closed-one:not open',
  ], 'by the agent\'s state, then by how much is owed, then by name');
  const asking = rows[0];
  assert.deepEqual(asking.owed.map((o) => `${o.verb}:${o.id}:${o.count}`), ['Decide:ADR-0001:1', 'Decide:ADR-0002:1', 'Push::5']);
  assert.equal(asking.detail, 'May I?');
  assert.equal(rows[1].detail, 'do the thing', 'the tooltip text is one line');
  assert.deepEqual(rows[1].phases.map((p) => p.key), ['PHASE-019'], 'active phases only');
});

test('a project that was not read keeps its reason and its last count, and no marks', () => {
  const closed = m.homeBoard(boardProjects, boardFleet).find((r) => r.project === 'closed-one');
  assert.equal(closed.notRead, 'it is not open in the cockpit');
  assert.equal(closed.owedCount, 3);
  assert.deepEqual(closed.owed, []);
  // A project the fleet has no row for is not open if it was not read, and quiet otherwise.
  const noFleet = m.homeBoard(boardProjects, []);
  assert.equal(noFleet.find((r) => r.project === 'closed-one').word, 'not open');
  assert.equal(noFleet.find((r) => r.project === 'quiet-one').word, 'quiet');
});

test('the totals count the marks that are drawn, in drawing order', () => {
  const totals = m.homeVerbTotals(m.homeBoard(boardProjects, boardFleet));
  assert.deepEqual(totals.map((t) => `${t.verb}:${t.glyph}:${t.count}`),
    ['Decide:decide:2', 'Run:run:1', 'Triage:triage:1', 'Push:push:1'], 'five commits are one mark, so Push counts once');
  assert.deepEqual(m.homeVerbTotals([]), []);
});
