// Behavioural guards for the fleet-health aggregate (FEAT-0028 / TASK-0248).
//
// Runs against the BUILT module (`dist/ipc/fleet-health.js`) with real
// HTTP servers standing in for sidecars — not string-greps over the
// source. ISS-0055's closing observation is the reason: a guard shaped
// like `assert "someString" in src` survives the rename that breaks the
// behaviour it claims to protect.
//
// `require('electron')` outside Electron resolves to the path string of
// the binary, so property access yields undefined rather than throwing.
// These cases never call `registerFleetHealthIpc`, which is the only
// function that touches `ipcMain`.

import { test, before, beforeEach, after } from 'node:test';
import assert from 'node:assert/strict';
import * as http from 'node:http';
import * as fs from 'node:fs/promises';
import * as os from 'node:os';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const built = path.join(here, '..', 'dist', 'ipc', 'fleet-health.js');

let mod;
before(async () => {
  await fs.access(built); // fail loudly rather than silently skipping
  mod = await import(`file://${built}`);
});

// ---- a fake sidecar -------------------------------------------------

/** An HTTP server answering the three endpoints fleet-health uses.
 *
 *  `report` is mutable so a case can drift a repo mid-test and push the
 *  change over SSE, which is what the real sidecar does.
 */
async function fakeSidecar({ root, report }) {
  const clients = new Set();
  const state = { root, report };
  const server = http.createServer((req, res) => {
    if (req.url === '/api/cockpit/identity') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ root: state.root }));
      return;
    }
    if (req.url === '/api/cockpit/validation') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(state.report));
      return;
    }
    if (req.url === '/_events') {
      res.writeHead(200, { 'Content-Type': 'text/event-stream' });
      res.write(': connected\n\n');
      clients.add(res);
      req.on('close', () => clients.delete(res));
      return;
    }
    res.writeHead(404);
    res.end();
  });
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  const url = `http://127.0.0.1:${server.address().port}`;
  const handle = {
    url,
    setReport(next) { state.report = next; },
    setRoot(next) { state.root = next; },
    push(report) {
      state.report = report;
      for (const c of clients) {
        c.write(`event: cockpit:validation\ndata: ${JSON.stringify(report)}\n\n`);
      }
    },
    get clientCount() { return clients.size; },
    async close() {
      liveSidecars.delete(handle);
      for (const c of clients) c.end();
      // undici keeps fetch sockets alive, so a plain close() waits for
      // idle connections that will never close on their own.
      server.closeAllConnections();
      await new Promise((r) => server.close(r));
    },
  };
  liveSidecars.add(handle);
  return handle;
}

const okReport = (at = '2026-07-30T10:00:00.000+00:00') => ({
  ok: true, state: 'ok', errors: [], warnings: [{ code: 'REVIEW' }], checked_at: at,
});
const failingReport = (n = 3, at = '2026-07-30T10:05:00.000+00:00') => ({
  ok: false,
  state: 'failing',
  errors: Array.from({ length: n }, (_, i) => ({ code: 'METRICS', message: `e${i}` })),
  warnings: [],
  checked_at: at,
});

/** Wait until `pred()` is true, or fail after `ms`. */
async function until(pred, ms = 3000, label = 'condition') {
  const deadline = Date.now() + ms;
  while (Date.now() < deadline) {
    if (await pred()) return;
    await new Promise((r) => setTimeout(r, 25));
  }
  assert.fail(`timed out waiting for ${label}`);
}

// F7 (PHASE-013 review): a failed assertion skipped the `close()` at the
// end of a case body, the fake server kept the event loop alive, and
// `node --test` never exited — turning one assertion failure into a
// three-minute pytest timeout with no message. Sidecars now close in the
// after-hook, whatever happened to the case.
const liveSidecars = new Set();
let tmpRoots = [];
async function workspaceDir(name, urlContents) {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), `fleet-health-${name}-`));
  tmpRoots.push(dir);
  if (urlContents !== undefined) {
    await fs.mkdir(path.join(dir, '.cockpit'), { recursive: true });
    await fs.writeFile(path.join(dir, '.cockpit', 'url'), urlContents, 'utf-8');
  }
  // realpath: macOS puts tmpdir under /var → /private/var, and the
  // identity comparison resolves the workspace root before comparing.
  return await fs.realpath(dir);
}

beforeEach(() => { mod.__resetFleetHealth(); });
after(async () => {
  // Tear the last case's SSE subscription down too — an open request
  // keeps the event loop alive and the runner would never exit.
  mod.__resetFleetHealth();
  for (const sc of Array.from(liveSidecars)) { try { await sc.close(); } catch { /* gone */ } }
  for (const d of tmpRoots) await fs.rm(d, { recursive: true, force: true });
  tmpRoots = [];
});

const rowFor = (id) => mod.fleetHealth().rows.find((r) => r.workspaceId === id);

// ---- cases ----------------------------------------------------------

test('two live workspaces, one drifting, land in the map with their own counts', async () => {
  const cleanRoot = await workspaceDir('clean');
  const driftRoot = await workspaceDir('drift');
  const clean = await fakeSidecar({ root: cleanRoot, report: okReport() });
  const drift = await fakeSidecar({ root: driftRoot, report: failingReport(3) });
  await fs.mkdir(path.join(cleanRoot, '.cockpit'), { recursive: true });
  await fs.writeFile(path.join(cleanRoot, '.cockpit', 'url'), clean.url);
  await fs.mkdir(path.join(driftRoot, '.cockpit'), { recursive: true });
  await fs.writeFile(path.join(driftRoot, '.cockpit', 'url'), drift.url);

  const workspaces = [
    { id: 'w-clean', name: 'clean', root: cleanRoot },
    { id: 'w-drift', name: 'drift', root: driftRoot },
  ];
  mod.__configureFleetHealth(() => workspaces);
  await mod.refreshLiveWorkspaces();

  assert.equal(rowFor('w-clean').state, 'ok');
  assert.equal(rowFor('w-clean').errors, 0);
  assert.equal(rowFor('w-clean').source, 'live');
  assert.equal(rowFor('w-drift').state, 'failing');
  assert.equal(rowFor('w-drift').errors, 3, 'the drifting repo carries its own error count');
  assert.equal(rowFor('w-drift').source, 'live');

  await clean.close();
  await drift.close();
});

test('checked_at is the sidecar\'s timestamp, not the moment we received it', async () => {
  const root = await workspaceDir('stamp');
  const at = '2026-01-01T00:00:00.000+00:00';
  const sc = await fakeSidecar({ root, report: okReport(at) });
  await fs.mkdir(path.join(root, '.cockpit'), { recursive: true });
  await fs.writeFile(path.join(root, '.cockpit', 'url'), sc.url);

  mod.__configureFleetHealth(() => [{ id: 'w', name: 'w', root }]);
  await mod.refreshLiveWorkspaces();

  // Re-stamping on receipt would make a long-cached report look fresh,
  // and TASK-0249's staleness marking reads this field.
  assert.equal(rowFor('w').checkedAt, at);

  await sc.close();
});

test('a cockpit:validation event updates the row without a re-fetch', async () => {
  const root = await workspaceDir('sse');
  const sc = await fakeSidecar({ root, report: okReport() });
  await fs.mkdir(path.join(root, '.cockpit'), { recursive: true });
  await fs.writeFile(path.join(root, '.cockpit', 'url'), sc.url);

  let changes = 0;
  mod.__configureFleetHealth(() => [{ id: 'w', name: 'w', root }], () => { changes += 1; });
  await mod.refreshLiveWorkspaces();
  assert.equal(rowFor('w').state, 'ok');

  // The subscription's socket connects asynchronously; pushing before
  // it attaches would test nothing.
  await until(() => sc.clientCount > 0, 3000, 'the SSE client to attach');
  sc.push(failingReport(2));
  await until(() => rowFor('w').state === 'failing', 3000, 'the SSE event to arrive');
  assert.equal(rowFor('w').errors, 2);
  assert.ok(changes > 0, 'the change callback fired so the renderer is told');

  await sc.close();
});

test('a dead sidecar degrades to unknown rather than freezing on its last report', async () => {
  const root = await workspaceDir('dies');
  const sc = await fakeSidecar({ root, report: failingReport(5) });
  await fs.mkdir(path.join(root, '.cockpit'), { recursive: true });
  await fs.writeFile(path.join(root, '.cockpit', 'url'), sc.url);

  mod.__configureFleetHealth(() => [{ id: 'w', name: 'w', root }]);
  await mod.refreshLiveWorkspaces();
  assert.equal(rowFor('w').state, 'failing');
  assert.equal(rowFor('w').errors, 5);

  await sc.close();
  // The SSE stream ending is the signal; no re-poll is needed.
  await until(() => rowFor('w').state === 'unknown', 3000, 'the row to degrade');
  assert.equal(rowFor('w').source, null, 'unknown carries no source');
  assert.equal(rowFor('w').errors, 0, 'a stale error count must not survive the sidecar');
});

test('a .cockpit/url answering a DIFFERENT root is not trusted', async () => {
  // ISS-0007's failure mode: a url file survives an unclean exit and
  // points at the port another workspace's sidecar now holds. Without
  // the identity check this reports the OTHER repo's drift here.
  const mine = await workspaceDir('mine');
  const theirs = await workspaceDir('theirs');
  const sc = await fakeSidecar({ root: theirs, report: failingReport(9) });
  await fs.mkdir(path.join(mine, '.cockpit'), { recursive: true });
  await fs.writeFile(path.join(mine, '.cockpit', 'url'), sc.url);

  mod.__configureFleetHealth(() => [{ id: 'w', name: 'mine', root: mine }]);
  await mod.refreshLiveWorkspaces();

  assert.equal(await mod.liveSidecarUrl({ id: 'w', root: mine }), null);
  assert.equal(rowFor('w').state, 'unknown', 'a wrong-root sidecar must not colour this repo');
  assert.notEqual(rowFor('w').errors, 9, 'the other repo\'s errors must not appear here');

  // Same server, correct root → now it is trusted. Proves the previous
  // assertion came from the root comparison and not from the fetch
  // failing for some unrelated reason.
  sc.setRoot(mine);
  mod.__resetFleetHealth();
  await mod.refreshLiveWorkspaces();
  assert.equal(rowFor('w').state, 'failing');
  assert.equal(rowFor('w').errors, 9);

  await sc.close();
});

test('a workspace with no sidecar is unknown, and unknown is not ok', async () => {
  const root = await workspaceDir('cold');
  mod.__configureFleetHealth(() => [{ id: 'w', name: 'cold', root }]);
  await mod.refreshLiveWorkspaces();
  const row = rowFor('w');
  assert.equal(row.state, 'unknown');
  assert.notEqual(row.state, 'ok', 'a repo nobody checked must never read as one that passed');
  assert.equal(row.checkedAt, null);
});

test('a non-loopback url in .cockpit/url is refused outright', async () => {
  const root = await workspaceDir('remote', 'http://example.com:8765\n');
  assert.equal(await mod.liveSidecarUrl({ id: 'w', root }), null);
});

test('fleet health never writes to a workspace it reads', async () => {
  // This module is read-only by design and the feature says so; assert
  // it rather than trusting it, because the same claim in TASK-0249
  // covers ten repos nobody asked this app to touch.
  const root = await workspaceDir('readonly');
  const sc = await fakeSidecar({ root, report: okReport() });
  await fs.mkdir(path.join(root, '.cockpit'), { recursive: true });
  await fs.writeFile(path.join(root, '.cockpit', 'url'), sc.url);

  const snapshot = async () => {
    const out = [];
    for (const entry of await fs.readdir(root, { recursive: true, withFileTypes: true })) {
      const abs = path.join(entry.parentPath ?? entry.path, entry.name);
      if (entry.isFile()) out.push([abs, (await fs.stat(abs)).mtimeMs, await fs.readFile(abs, 'utf-8')]);
    }
    return JSON.stringify(out.sort());
  };
  const before = await snapshot();

  mod.__configureFleetHealth(() => [{ id: 'w', name: 'w', root }]);
  await mod.refreshLiveWorkspaces();
  await until(() => sc.clientCount > 0, 3000, 'the SSE client to attach');
  sc.push(failingReport(1));
  await until(() => rowFor('w').state === 'failing', 3000, 'the drift to land');

  assert.equal(await snapshot(), before, 'reading a workspace must not modify it');

  await sc.close();
});

// ---- cold workspaces (TASK-0249) ------------------------------------

test('the cold pass never passes --fix-metrics', () => {
  // The validator has exactly one write path — `fix_metrics`, which
  // rewrites SNAPSHOT.yaml — and it is behind this flag. This runs in
  // repositories nobody asked this app to touch, so the argv is pinned
  // rather than trusted.
  const argv = mod.coldArgv(['/a', '/b']);
  assert.ok(!argv.includes('--fix-metrics'), 'the cold pass must never rewrite another repo');
  assert.deepEqual(argv, ['-m', 'project_os_cockpit.fleet_validate', '/a', '/b']);
});

test('a cold reading older than its schedule is marked stale, a fresh one is not', () => {
  const now = Date.parse('2026-07-30T12:00:00.000Z');
  const base = {
    workspaceId: 'w', name: 'w', root: '/r', state: 'ok',
    errors: 0, warnings: 0, source: 'cold',
  };
  const fresh = { ...base, checkedAt: new Date(now - 60_000).toISOString() };
  const old = { ...base, checkedAt: new Date(now - mod.COLD_STALE_AFTER_MS - 60_000).toISOString() };
  const live = { ...base, source: 'live', checkedAt: old.checkedAt };

  const [f, o, l] = mod.markStale([fresh, old, live], now);
  assert.equal(f.stale, undefined, 'a reading inside its schedule is current');
  assert.equal(o.stale, true, 'an old cold reading must say so rather than pass as current');
  assert.equal(o.state, 'ok', 'stale keeps the state it measured');
  assert.equal(l.stale, undefined, 'live rows are pushed on change and never go stale');
});

// ---- the rail badge (TASK-0250) -------------------------------------
//
// These run against the BUILT renderer bundle. The renderer is a DOM
// module and cannot be imported outside a browser, so the guards below
// are structural — but structural about the two signals being
// SEPARABLE, which is the property that breaks silently.

test('the validator badge and the agent dot never share an element or a class', async () => {
  const js = await fs.readFile(
    path.join(here, '..', 'dist', 'renderer', 'renderer.js'), 'utf-8');
  const css = await fs.readFile(
    path.join(here, '..', 'dist', 'renderer', 'renderer.css'), 'utf-8');

  // Distinct elements: one is `.ws-dot`, one is `.ws-health`.
  assert.ok(js.includes("'ws-health'"), 'the validator badge element is gone');
  assert.ok(js.includes("'ws-dot'"), 'the agent-state dot element is gone');

  // Distinct corners. If these ever match, the two marks overlap and
  // one becomes unreadable — the collision this task exists to avoid.
  const rule = (sel) => {
    const i = css.indexOf(sel);
    assert.notEqual(i, -1, `${sel} has no rule`);
    return css.slice(i, css.indexOf('}', i));
  };
  const dot = rule('.ws-square .ws-dot');
  const health = rule('.ws-square .ws-health');
  assert.match(dot, /bottom:\s*-3px/);
  assert.match(dot, /right:\s*-3px/);
  assert.match(health, /top:\s*-4px/);
  assert.match(health, /left:\s*-4px/);

  // No CSS rule may key off both at once — that would make one signal's
  // appearance depend on the other's value.
  for (const line of css.split('\n')) {
    if (line.includes('ws-dot') && line.includes('ws-health')) {
      assert.fail(`a rule couples the two signals: ${line.trim()}`);
    }
  }
});

// ---- the square encoding, as behaviour (ISS-0074) --------------------
//
// The guard these replace compared string indices in the built bundle. The
// PHASE-013 review broke it: a mutation that ADDED `health-ok` for an
// `unknown` row — every unchecked repo rendering as "checked and clean",
// the exact ISS-0065 failure — kept the literal in place and passed.
//
// `healthMarks` is a pure function in a non-module script, so the test
// evaluates the built file and calls it directly. No DOM, no bundle.

let marks;
before(async () => {
  const src = await fs.readFile(
    path.join(here, '..', 'dist', 'renderer', 'health-marks.js'), 'utf-8');
  marks = new Function(`${src}\nreturn healthMarks;`)();
});

test('an unknown row paints nothing at all — no class, no badge', () => {
  const out = marks({ state: 'unknown', errors: 0 });
  assert.deepEqual(out.classes, [],
    'a repo nobody has checked must carry NO mark — not even a neutral one');
  assert.equal(out.badge, null);
});

test('a missing row is treated exactly like unknown', () => {
  for (const absent of [null, undefined]) {
    const out = marks(absent);
    assert.deepEqual(out.classes, []);
    assert.equal(out.badge, null);
  }
});

test('unknown never yields the class that means checked-and-clean', () => {
  // The specific mutation that defeated the previous guard.
  const out = marks({ state: 'unknown', errors: 0 });
  assert.ok(!out.classes.includes('health-ok'),
    'unknown must not be presentable as a repo that passed (ISS-0065)');
  assert.ok(!out.classes.some((c) => c.startsWith('health-')),
    'no health-* class may attach to a state nobody measured');
});

test('failing carries its count, and only failing carries a numeral', () => {
  assert.equal(marks({ state: 'failing', errors: 3 }).badge, '3');
  assert.equal(marks({ state: 'failing', errors: 120 }).badge, '99+');
  // A `0` badge would be a drift report with no drift.
  assert.equal(marks({ state: 'failing', errors: 0 }).badge, null);
  assert.equal(marks({ state: 'ok', errors: 0 }).badge, null);
  assert.equal(marks({ state: 'unavailable', errors: 0 }).badge, null);
});

test('each measured state gets its own class, and stale composes with it', () => {
  assert.deepEqual(marks({ state: 'ok', errors: 0 }).classes, ['health-ok']);
  assert.deepEqual(marks({ state: 'failing', errors: 1 }).classes, ['health-failing']);
  assert.deepEqual(marks({ state: 'unavailable', errors: 0 }).classes, ['health-unavailable']);
  // stale ADDS to the state's mark rather than replacing it — a stale
  // reading still says what it measured.
  assert.deepEqual(marks({ state: 'ok', errors: 0, stale: true }).classes,
    ['health-ok', 'health-stale']);
});

test('ok and unavailable are distinguishable from each other and from unknown', () => {
  const seen = new Set(['ok', 'failing', 'unavailable', 'unknown'].map(
    (s) => JSON.stringify(marks({ state: s, errors: s === 'failing' ? 2 : 0 }))));
  assert.equal(seen.size, 4, 'two states render identically — one of them is a lie');
});

// ---- validator errors as session rows (FEAT-0051 / TASK-0253) --------
//
// Same approach as `healthMarks` above, for the same reason: the row
// model is pure, so it is evaluated and called directly rather than
// grepped out of the built bundle.

let vr;
before(async () => {
  const src = await fs.readFile(
    path.join(here, '..', 'dist', 'renderer', 'validation-rows.js'), 'utf-8');
  vr = new Function(`${src}
    return { validationRows, noteValidationChange, resetValidationRows,
             validationKey, validationLabel };`)();
});

const err = (code, message, extra = {}) => ({ code, message, ...extra });
const report = (...errors) => ({ state: errors.length ? 'failing' : 'ok', errors });

test('an error becomes a row, and stays open while it is failing', () => {
  vr.resetValidationRows();
  const t0 = 1_000_000;
  vr.noteValidationChange(report(err('METRICS', 'tasks_total is 251 but computed 252')), t0);
  const rows = vr.validationRows([err('METRICS', 'tasks_total is 251 but computed 252')], t0);
  assert.equal(rows.length, 1);
  assert.equal(rows[0].done, false);
  assert.equal(rows[0].entry.code, 'METRICS');
});

test('a fixed error is marked done and LINGERS rather than vanishing', () => {
  vr.resetValidationRows();
  const t0 = 1_000_000;
  const e = err('METRICS', 'counts are behind');
  vr.noteValidationChange(report(e), t0);
  // Fixed a second later — METRICS clears about this fast once
  // sync-snapshot runs, and a row that disappeared instantly means the
  // user sees a number change and never learns what changed.
  vr.noteValidationChange(report(), t0 + 1000);
  const rows = vr.validationRows([], t0 + 2000);
  assert.equal(rows.length, 1, 'the fixed row must still be visible');
  assert.equal(rows[0].done, true);
  assert.equal(rows[0].entry.code, 'METRICS');
});

test('a fixed row is forgotten once its linger expires', () => {
  vr.resetValidationRows();
  const t0 = 1_000_000;
  vr.noteValidationChange(report(err('METRICS', 'x')), t0);
  vr.noteValidationChange(report(), t0 + 1000);
  const late = t0 + 1000 + 6 * 60_000;      // past the 5-minute window
  vr.noteValidationChange(report(), late);
  assert.deepEqual(vr.validationRows([], late), [],
    'a long session must not accumulate every error it ever fixed');
});

test('an error that comes back is open again, not stuck at fixed', () => {
  vr.resetValidationRows();
  const t0 = 1_000_000;
  const e = err('PHASE-CHILDREN', 'PHASE-016 is done but 1 item is unresolved');
  vr.noteValidationChange(report(e), t0);
  vr.noteValidationChange(report(), t0 + 1000);
  vr.noteValidationChange(report(e), t0 + 2000);
  const rows = vr.validationRows([e], t0 + 2000);
  assert.equal(rows.length, 1);
  assert.equal(rows[0].done, false, 'a recurring error must not read as fixed');
});

test('unresolved rows sort above fixed ones', () => {
  vr.resetValidationRows();
  const t0 = 1_000_000;
  const fixed = err('METRICS', 'a');
  const open = err('LINK', 'b');
  vr.noteValidationChange(report(fixed), t0);
  vr.noteValidationChange(report(open), t0 + 1000);   // `fixed` resolved, `open` arrived
  const rows = vr.validationRows([open], t0 + 1000);
  assert.equal(rows.length, 2);
  assert.equal(rows[0].done, false, 'a fixed row must never push a live one down');
  assert.equal(rows[1].done, true);
});

test('two errors with the same code are two rows', () => {
  vr.resetValidationRows();
  const t0 = 1_000_000;
  const a = err('METRICS', 'tasks_total is wrong');
  const b = err('METRICS', 'features_total is wrong');
  vr.noteValidationChange(report(a, b), t0);
  assert.equal(vr.validationRows([a, b], t0).length, 2,
    'the key must include the message — one code can name several problems');
  assert.notEqual(vr.validationKey(a), vr.validationKey(b));
});

test('a code gets a readable label, and an unknown code falls back to itself', () => {
  // The whole point of the panel is that a glance answers "what is this
  // about" — the code alone is accurate and opaque.
  assert.notEqual(vr.validationLabel(err('METRICS', 'x')), 'METRICS');
  assert.match(vr.validationLabel(err('METRICS', 'x')), /count/i);
  assert.equal(vr.validationLabel(err('NOT-A-REAL-CODE', 'x')), 'NOT-A-REAL-CODE',
    'an unrecognised code must show itself rather than a guess');
});

test('clearing drops everything — one repo\'s errors never outlive a switch', () => {
  vr.resetValidationRows();
  const t0 = 1_000_000;
  vr.noteValidationChange(report(err('LINK', 'x')), t0);
  vr.resetValidationRows();
  assert.deepEqual(vr.validationRows([], t0), [],
    "showing one repo's violations under another's session is FEAT-0028's "
    + 'identity bug one scope down');
});

test('every code the validator can emit has a label', async () => {
  // Enumerated from the validator's own emit sites, so this fails when
  // it gains a rule rather than when someone notices. The fallback
  // (show the code) still works — this is about the panel answering
  // "what is this about" for the codes that exist today.
  const py = await fs.readFile(
    path.join(here, '..', '..', 'tools', 'scripts', 'validate-docs.py'), 'utf-8');
  const codes = new Set();
  for (const m of py.matchAll(/(?:report\.error|emit)\("([A-Z0-9-]+)"/g)) codes.add(m[1]);
  assert.ok(codes.size > 15, `only found ${codes.size} codes — the scrape broke`);

  const unlabelled = [...codes].filter(
    (c) => vr.validationLabel({ code: c, message: '' }) === c);
  assert.deepEqual(unlabelled, [],
    `validator codes with no readable label: ${unlabelled.join(', ')}`);
});

// ---- History replaced three tiles (FEAT-0052 / TASK-0256) ------------

test('Activity, Changes and Commits are gone as separate tiles', async () => {
  // Deleting them is the point, not a side effect: landing History
  // beside them would leave the overview with four history surfaces,
  // which is the shape PHASE-010 and PHASE-012 each closed by undoing.
  // The absence is what regresses silently, so the absence is asserted.
  const js = await fs.readFile(
    path.join(here, '..', 'dist', 'renderer', 'renderer.js'), 'utf-8');
  for (const gone of ['function buildActivityTile', 'function buildCommitsTile',
                      'function buildChangesTile', 'async function fillCommits']) {
    assert.ok(!js.includes(gone), `${gone} is back — the overview has two history surfaces`);
  }
  assert.ok(js.includes('function buildHistoryTile'), 'History tile is missing');
  // …and the overview actually mounts it.
  const build = js.slice(js.indexOf('function buildOverviewParts'),
                         js.indexOf('function buildOverviewParts') + 4000);
  assert.ok(build.includes('buildHistoryTile') || js.includes('buildHistoryTile(data)'),
    'the History tile is defined but never mounted');
});

test('the commit divider keeps the undocumented flag', async () => {
  // A commit with no transitions has no rows, so this flag is the only
  // thing keeping it visible — and it is the commit most worth seeing
  // (code moved, nothing recorded it). FEAT-0022's guardrail.
  const js = await fs.readFile(
    path.join(here, '..', 'dist', 'renderer', 'renderer.js'), 'utf-8');
  const fn = js.slice(js.indexOf('function buildCommitDivider'),
                      js.indexOf('function buildTransitionRow'));
  assert.ok(fn.length > 100, 'buildCommitDivider was renamed or removed');
  assert.ok(fn.includes('undocumented'),
    'the divider no longer reads the undocumented flag, so a commit that '
    + 'documented nothing renders identically to one that did');
  assert.ok(fn.includes('nothing documented'), 'the flag has no visible text');
});

test('a created note is not rendered as a journey it never took', async () => {
  const js = await fs.readFile(
    path.join(here, '..', 'dist', 'renderer', 'renderer.js'), 'utf-8');
  const fn = js.slice(js.indexOf('function buildTransitionRow'),
                      js.indexOf('function buildTransitionRow') + 2000);
  assert.ok(fn.includes('created'), 'the row ignores the created flag');
  assert.ok(fn.includes('new · ') || fn.includes('new \\u00b7 '),
    'a created note should read "new · done", not "null → done"');
});

// ---- the contribution grid (FEAT-0053 / TASK-0259) -------------------

let cg;
before(async () => {
  const src = await fs.readFile(
    path.join(here, '..', 'dist', 'renderer', 'contribution-grid.js'), 'utf-8');
  cg = new Function(`${src}
    return { buildGridWeeks, gridStep, gridYears, gridDateKey, gridMonthLabels };`)();
});

test('a day before the first commit is absent, not empty', () => {
  // The correction that matters most on a young repo: "did not exist"
  // and "no activity" are different facts, and GitHub renders them the
  // same. This corpus would otherwise show 40 of 52 weeks as neglect.
  const weeks = cg.buildGridWeeks(
    {}, '2026-05-07', [2, 4, 6], new Date(2026, 6, 30), 52);
  const all = weeks.flat();
  const before = all.filter((c) => c.date < '2026-05-07');
  const after = all.filter((c) => c.date >= '2026-05-07' && c.date <= '2026-07-30');
  assert.ok(before.length > 100, 'expected a long pre-history stretch');
  assert.ok(before.every((c) => c.state === 'absent'),
    'a day the project did not exist must not render as a quiet day');
  assert.ok(after.every((c) => c.state === 'empty'),
    'a day with no activity after the first commit IS empty, not absent');
});

test('intensity uses the payload buckets, not a scale of its own', () => {
  // Measured buckets from this repo: [22, 36, 64].
  const b = [22, 36, 64];
  assert.equal(cg.gridStep(0, b), 'empty');
  assert.equal(cg.gridStep(1, b), 1);
  assert.equal(cg.gridStep(22, b), 1);
  assert.equal(cg.gridStep(23, b), 2);
  assert.equal(cg.gridStep(36, b), 2);
  assert.equal(cg.gridStep(64, b), 3);
  assert.equal(cg.gridStep(199, b), 4);
});

test("this repo's busiest and quietest active days land in different steps", () => {
  // The whole reason for relative scaling. Under GitHub's fixed
  // 1/4/7/10 every one of these would be step 4.
  const b = [22, 36, 64];
  const steps = [1, 6, 13, 29, 38, 46, 64, 80, 89, 199].map((n) => cg.gridStep(n, b));
  assert.ok(new Set(steps).size >= 3,
    `a median active day of 34 must not saturate the scale: got ${steps}`);
});

test('year controls are absent until there is a second year', () => {
  assert.deepEqual(cg.gridYears('2026-05-07', '2026-07-30'), [2026],
    'one year — a selector would offer navigation to nothing');
  assert.deepEqual(cg.gridYears('2024-11-01', '2026-07-30'), [2026, 2025, 2024]);
  assert.deepEqual(cg.gridYears(null, null), []);
});

test('the date key is local, not UTC', () => {
  // toISOString() shifts the date across the boundary for anyone east
  // or west of UTC — a whole day wrong for the cell you clicked.
  const d = new Date(2026, 0, 1, 23, 30);
  assert.equal(cg.gridDateKey(d), '2026-01-01');
  assert.equal(cg.gridDateKey(new Date(2026, 11, 31, 0, 30)), '2026-12-31');
});

test('the grid ends today and columns are whole weeks', () => {
  const today = new Date(2026, 6, 30);
  const weeks = cg.buildGridWeeks({}, '2026-05-07', [1, 2, 3], today, 52);
  assert.ok(weeks.every((c) => c.length === 7), 'every column is a full week');
  const last = weeks[weeks.length - 1];
  assert.ok(last.some((c) => c.date === '2026-07-30'), 'today is in the last column');
});

test('counts come through onto the cell for the tooltip', () => {
  const days = { '2026-07-19': { transitions: 199, commits: 12 } };
  const cell = cg.buildGridWeeks(days, '2026-05-07', [22, 36, 64],
    new Date(2026, 6, 30), 52).flat().find((c) => c.date === '2026-07-19');
  assert.equal(cell.transitions, 199);
  assert.equal(cell.commits, 12);
  assert.equal(cell.state, 4);
});

test('month labels mark where each month starts', () => {
  const weeks = cg.buildGridWeeks({}, '2026-01-01', [1, 2, 3],
    new Date(2026, 6, 30), 52);
  const labels = cg.gridMonthLabels(weeks);
  assert.ok(labels.length >= 12, `expected ~13 month labels, got ${labels.length}`);
  assert.ok(labels.every((l) => /^[A-Z][a-z]{2}$/.test(l.label)));
});

test('the History rail button exists and goes to ~history', async () => {
  const html = await fs.readFile(
    path.join(here, '..', 'dist', 'renderer', 'index.html'), 'utf-8');
  assert.match(html, /id="history-toggle"/, 'the rail button is gone');
  const js = await fs.readFile(
    path.join(here, '..', 'dist', 'renderer', 'renderer.js'), 'utf-8');
  const i = js.indexOf("getElementById('history-toggle')");
  assert.notEqual(i, -1, 'the button has no handler');
  assert.ok(js.slice(i, i + 400).includes("'~history'"),
    'the History button does not navigate to ~history');
});

test('the sparkline is gone from the History tile', async () => {
  const js = await fs.readFile(
    path.join(here, '..', 'dist', 'renderer', 'renderer.js'), 'utf-8');
  assert.ok(!js.includes('ov-history-spark'),
    'the 13-week sparkline is back — the grid replaced it, at higher '
    + 'resolution and with cells that navigate');
});

test('intensity is monotonic and no step shrinks the cell (ISS-0075)', async () => {
  // The busiest days used to render 33% smaller than the quietest: an
  // INSET box-shadow in the background colour is a border drawn inside
  // the box, so step 4 showed 6px of colour against step 1's 9px. The
  // size channel partly cancelled the intensity it was meant to
  // reinforce. Edwin spotted it on sight; the suite could not, because
  // every cell is 9×9 by any measurement a test would take.
  //
  // So this asserts the two properties that were violated, not the
  // pixel values: nothing subtracts from a cell, and darker means busier.
  const css = await fs.readFile(
    path.join(here, '..', 'dist', 'renderer', 'renderer.css'), 'utf-8');

  const opacities = [];
  for (const step of [1, 2, 3, 4]) {
    const sel = `.ov-grid-cell[data-state="${step}"]`;
    const i = css.indexOf(sel);
    assert.notEqual(i, -1, `${sel} has no rule`);
    const rule = css.slice(i, css.indexOf('}', i));
    assert.ok(!rule.includes('inset'),
      `step ${step} carries an inset shadow — that paints INSIDE the cell, `
      + 'so a busier day renders as a smaller mark (ISS-0075)');
    const m = rule.match(/opacity:\s*([\d.]+)/);
    assert.ok(m, `step ${step} sets no opacity, so intensity has no channel`);
    opacities.push(Number(m[1]));
  }
  for (let i = 1; i < opacities.length; i++) {
    assert.ok(opacities[i] > opacities[i - 1],
      `intensity must increase with the step: got ${opacities.join(' → ')}`);
  }
});
