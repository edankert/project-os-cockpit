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
