// The other projects' counts, as the shell writes them for each cockpit
// terminal's Claude plugin (FEAT-0157 / TASK-0671).
//
// Runs the built needs-count.js and needs-elsewhere-file.js as they are, and
// the built home-window.js with stand-ins for Electron and its neighbours, so
// the home window and the file are compared through their real code. A small
// HTTP server plays a live sidecar.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs';
import * as http from 'node:http';
import { createRequire } from 'node:module';
import * as os from 'node:os';
import * as path from 'node:path';
import * as vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const dist = path.join(here, '..', 'dist', 'ipc');
const require = createRequire(import.meta.url);
const { needsYouCount, coldCount, UNKNOWN } = require(path.join(dist, 'needs-count.js'));
const { elsewherePayload, writeAtomic, NEEDS_ELSEWHERE_FILE } = require(path.join(dist, 'needs-elsewhere-file.js'));

/** A sidecar answering only what the home window and the count read. */
async function sidecar(total) {
  const server = http.createServer((req, res) => {
    const url = new URL(req.url, 'http://x');
    const body = {
      '/api/cockpit/obligations': { total, views: { features: total }, breakdown: {} },
      '/api/cockpit/landing': { groups: [] },
      '/api/cockpit/stats': { phases: [] },
      '/api/cockpit/release': {},
    }[url.pathname];
    res.writeHead(body ? 200 : 404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(body ?? {}));
  });
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  return { base: `http://127.0.0.1:${server.address().port}`, close: () => server.close() };
}

async function getJson(url) {
  try {
    const r = await fetch(url);
    return r.ok ? await r.json() : null;
  } catch {
    return null;
  }
}

const ws = (id, name = id) => ({ id, name, root: `/repos/${id}`, projectId: id });

/** The built home window, with the given workspaces, live sidecars and cold digests. */
function homeWindow(workspaces, live, cold) {
  const built = path.join(dist, 'home-window.js');
  const handlers = {};
  const module = { exports: {} };
  vm.runInNewContext(fs.readFileSync(built, 'utf-8'), {
    module, exports: module.exports, console, process, setTimeout, clearTimeout, AbortController, fetch, URL,
    __dirname: dist,
    require: (name) => {
      if (name === 'electron') return { BrowserWindow: function () {}, ipcMain: { handle: (c, fn) => { handlers[c] = fn; } } };
      if (name === 'node:path') return path;
      if (name === './workspaces') return { getAllWorkspaces: () => workspaces };
      if (name === './fleet-health') return {
        liveSidecarUrl: async (w) => live[w.id] ?? null,
        fleetHealth: () => ({ rows: Object.entries(cold).map(([workspaceId, digest]) => ({ workspaceId, digest })) }),
      };
      if (name === './home-payload') return require(path.join(dist, 'home-payload.js'));
      if (name === './needs-count') return require(path.join(dist, 'needs-count.js'));
      throw new Error(`unexpected import ${name}`);
    },
  }, { filename: built });
  module.exports.registerHomeWindowIpc({ openInMain() {} });
  return () => handlers['home:data']();
}

test('the folder of a workspace never lists that workspace', () => {
  const rows = [
    { id: 'a', name: 'alpha', count: { count: 2, asOf: 't', source: 'live' } },
    { id: 'b', name: 'beta', count: { count: 5, asOf: 't', source: 'cold' } },
  ];
  const file = elsewherePayload('a', rows, Date.UTC(2026, 9, 14, 21, 30));
  assert.equal(file.workspace_id, 'a');
  assert.deepEqual(file.projects.map((p) => p.workspace_id), ['b']);
  assert.equal(file.written_at, '2026-10-14T21:30:00.000Z');
  assert.equal(file.schema_version, 1);
});

test('a count nobody read is null and unknown, never 0', async () => {
  const deps = (over) => ({ liveUrl: async () => null, cold: () => undefined, getJson, now: () => 0, ...over });
  // No sidecar and no cold pass.
  assert.deepEqual(await needsYouCount(ws('a'), deps()), UNKNOWN);
  // A sidecar that runs and does not answer.
  assert.deepEqual(await needsYouCount(ws('a'), deps({ liveUrl: async () => 'http://127.0.0.1:9', getJson: async () => null })), UNKNOWN);
  // An answer without a total.
  assert.deepEqual(await needsYouCount(ws('a'), deps({ liveUrl: async () => 'http://x', getJson: async () => ({ views: {} }) })), UNKNOWN);
  const file = elsewherePayload('self', [{ id: 'a', name: 'a', count: UNKNOWN }], 0);
  assert.equal(file.projects[0].count, null);
  assert.equal(file.projects[0].source, 'unknown');
  // A cold pass that counted zero is a zero, with its date.
  assert.deepEqual(coldCount({ needsYou: 0, computedAt: '2026-10-14T19:02:00Z' }),
    { count: 0, asOf: '2026-10-14T19:02:00Z', source: 'cold' });
});

test('the write goes through a new file, so a folder that refuses one keeps the old file', (t) => {
  if (process.getuid?.() === 0) return t.skip('root ignores the folder permission');
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'needs-elsewhere-'));
  writeAtomic(dir, NEEDS_ELSEWHERE_FILE, '{"old":true}\n');
  assert.deepEqual(fs.readdirSync(dir), [NEEDS_ELSEWHERE_FILE], 'no temporary file is left behind');
  fs.chmodSync(dir, 0o555);
  try {
    // A write straight into the existing file would succeed here, because the
    // file itself is still writable; only a new file in the folder is refused.
    assert.throws(() => writeAtomic(dir, NEEDS_ELSEWHERE_FILE, '{"new":true}\n'));
    assert.equal(fs.readFileSync(path.join(dir, NEEDS_ELSEWHERE_FILE), 'utf-8'), '{"old":true}\n');
  } finally {
    fs.chmodSync(dir, 0o755);
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test('the home window and the file give one project the same number', async () => {
  const live = await sidecar(7);
  try {
    const workspaces = [ws('live-one'), ws('cold-one'), ws('unread-one')];
    const liveUrls = { 'live-one': live.base };
    const cold = { 'cold-one': { needsYou: 4, computedAt: '2026-10-14T19:02:00Z' } };
    const home = await homeWindow(workspaces, liveUrls, cold)();
    const deps = { liveUrl: async (w) => liveUrls[w.id] ?? null, cold: (id) => cold[id], getJson, now: () => Date.now() };
    for (const w of workspaces) {
      const row = home.projects.find((p) => p.workspaceId === w.id);
      const counted = await needsYouCount(w, deps);
      assert.equal(row.owedCount, counted.count, `${w.id}: home window ${row.owedCount}, file ${counted.count}`);
    }
    assert.equal(home.projects.find((p) => p.workspaceId === 'live-one').owedCount, 7);
    assert.equal(home.projects.find((p) => p.workspaceId === 'cold-one').owedCount, 4);
    assert.equal(home.projects.find((p) => p.workspaceId === 'unread-one').owedCount, null);
  } finally {
    live.close();
  }
});
