// Git state reaches every workspace, including the one you have open
// (TASK-0415 / ISS-0156).
//
// Runs against the BUILT modules with REAL git repositories, for the
// same reason `fleet-health.test.mjs` uses real HTTP servers: the defect
// this guards was invisible to every existing test because nothing
// asserted the property, and a mock of `git` would have been written by
// the same person who misunderstood which workspaces got probed.
//
// The bug, precisely: `ahead` and `remoteKind` were assigned only by the
// cold pass, which skips any workspace with a live sidecar — so the repo
// you were working in, the one accumulating commits, was the one with no
// count. And because the live path replaced the row wholesale, a count
// learned while a workspace was cold was *erased* when its sidecar
// reported. Both cases are below.

import { test, before, beforeEach, after } from 'node:test';
import assert from 'node:assert/strict';
import * as http from 'node:http';
import { execFile } from 'node:child_process';
import * as fs from 'node:fs/promises';
import * as os from 'node:os';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const builtFleet = path.join(here, '..', 'dist', 'ipc', 'fleet-health.js');
const builtGit = path.join(here, '..', 'dist', 'ipc', 'git.js');

let fleet;
let git;
before(async () => {
  await fs.access(builtFleet);
  await fs.access(builtGit);
  fleet = await import(`file://${builtFleet}`);
  git = await import(`file://${builtGit}`);
});

// ---- real git repositories -----------------------------------------

const tmpRoots = [];

function run(cwd, args) {
  return new Promise((resolve, reject) => {
    execFile('git', ['-C', cwd, ...args], { timeout: 15_000 }, (err, stdout, stderr) => {
      if (err) reject(new Error(`git ${args.join(' ')}: ${stderr || err.message}`));
      else resolve(stdout.trim());
    });
  });
}

async function mkTmp(name) {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), `git-state-${name}-`));
  tmpRoots.push(dir);
  // macOS puts tmpdir under /var → /private/var, and the identity check
  // resolves the workspace root before comparing.
  return await fs.realpath(dir);
}

/** A work repo with an upstream, `ahead` commits past it, and `origin`
 *  finally pointed at `remoteUrl` so the classification can be chosen
 *  independently of where the pushes actually went. */
async function makeRepo(name, { ahead = 0, remoteUrl = null } = {}) {
  const bare = await mkTmp(`${name}-bare`);
  await run(bare, ['init', '--bare', '--initial-branch=main', '.']);
  const work = await mkTmp(name);
  await run(work, ['init', '--initial-branch=main', '.']);
  await run(work, ['config', 'user.email', 'test@example.invalid']);
  await run(work, ['config', 'user.name', 'Test']);
  await run(work, ['config', 'commit.gpgsign', 'false']);
  await fs.writeFile(path.join(work, 'SNAPSHOT.yaml'), 'project:\n  name: t\n', 'utf-8');
  await run(work, ['add', '-A']);
  await run(work, ['commit', '-m', 'base']);
  await run(work, ['remote', 'add', 'origin', bare]);
  await run(work, ['push', '-u', 'origin', 'main']);
  for (let i = 0; i < ahead; i += 1) {
    await fs.writeFile(path.join(work, `f${i}.txt`), String(i), 'utf-8');
    await run(work, ['add', '-A']);
    await run(work, ['commit', '-m', `c${i}`]);
  }
  // Re-point origin AFTER pushing: the tracking ref stays valid, so a
  // repo can be `ahead 3` of a github-shaped remote without a network.
  if (remoteUrl) await run(work, ['remote', 'set-url', 'origin', remoteUrl]);
  return work;
}

// ---- a fake sidecar, so a workspace can be LIVE ---------------------

const sidecars = new Set();

async function fakeSidecar(root) {
  const clients = new Set();
  const server = http.createServer((req, res) => {
    if (req.url === '/api/cockpit/identity') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ root }));
      return;
    }
    if (req.url === '/api/cockpit/validation') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ ok: true, state: 'ok', errors: [], warnings: [],
        checked_at: '2026-08-13T10:00:00.000+00:00' }));
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
  const handle = {
    url: `http://127.0.0.1:${server.address().port}`,
    /** Push a fresh validator report over SSE — what the real sidecar
     *  does on every docs change, and what used to wipe git state. */
    pushReport(report) {
      for (const c of clients) {
        c.write(`event: cockpit:validation\ndata: ${JSON.stringify(report)}\n\n`);
      }
    },
    async close() {
      sidecars.delete(handle);
      for (const c of clients) c.end();
      server.closeAllConnections();
      await new Promise((r) => server.close(r));
    },
  };
  sidecars.add(handle);
  return handle;
}

async function markLive(root, url) {
  await fs.mkdir(path.join(root, '.cockpit'), { recursive: true });
  await fs.writeFile(path.join(root, '.cockpit', 'url'), url, 'utf-8');
}

async function until(pred, ms = 4000, label = 'condition') {
  const deadline = Date.now() + ms;
  while (Date.now() < deadline) {
    if (await pred()) return;
    await new Promise((r) => setTimeout(r, 25));
  }
  assert.fail(`timed out waiting for ${label}`);
}

const ws = (root, id) => ({ id, root, name: id, projectId: id, lastOpened: null, pinned: false });
const rowFor = (id) => fleet.fleetHealth().rows.find((r) => r.workspaceId === id);

beforeEach(() => { fleet.__resetFleetHealth(); });
after(async () => {
  fleet.__resetFleetHealth();
  for (const sc of Array.from(sidecars)) { try { await sc.close(); } catch { /* gone */ } }
  for (const d of tmpRoots) await fs.rm(d, { recursive: true, force: true });
});

// ---- cases ----------------------------------------------------------

test('ISS-0156: a workspace with a LIVE sidecar still reports its unpushed count', async () => {
  const root = await makeRepo('live', { ahead: 2, remoteUrl: 'https://github.com/example/x.git' });
  const sc = await fakeSidecar(root);
  await markLive(root, sc.url);
  fleet.__configureFleetHealth(() => [ws(root, 'live-1')]);

  await fleet.refreshLiveWorkspaces();
  await until(() => fleet.hasLiveSubscription('live-1'), 4000, 'live subscription');
  await fleet.refreshGitState();

  const row = rowFor('live-1');
  // The whole defect in one assertion: this was `undefined`, and every
  // surface reads `typeof ahead === 'number' && ahead > 0`, so all three
  // of them went quiet together for the repo you had open.
  assert.equal(row.ahead, 2, 'a live workspace must carry its unpushed count');
  assert.equal(row.remoteKind, 'backup');
  assert.equal(row.source, 'live', 'and must still be a live validator row');
});

test('a live validator report does not erase git state', async () => {
  const root = await makeRepo('clobber', { ahead: 3, remoteUrl: 'https://github.com/example/y.git' });
  const sc = await fakeSidecar(root);
  await markLive(root, sc.url);
  fleet.__configureFleetHealth(() => [ws(root, 'clobber-1')]);

  await fleet.refreshLiveWorkspaces();
  await until(() => fleet.hasLiveSubscription('clobber-1'), 4000, 'live subscription');
  await fleet.refreshGitState();
  assert.equal(rowFor('clobber-1').ahead, 3);

  // The sidecar reports drift — the row is rebuilt from the report, which
  // is exactly the path that used to drop `ahead` on the floor.
  sc.pushReport({ ok: false, state: 'failing', errors: [{ code: 'METRICS', message: 'e' }],
    warnings: [], checked_at: '2026-08-13T11:00:00.000+00:00' });
  await until(() => rowFor('clobber-1').state === 'failing', 4000, 'drift to arrive');

  assert.equal(rowFor('clobber-1').ahead, 3, 'git state survives a validator report');
  assert.equal(rowFor('clobber-1').remoteKind, 'backup');
});

test('no remote is null-and-none, never zero — the worse fact keeps its own shape', async () => {
  const root = await mkTmp('no-remote');
  await run(root, ['init', '--initial-branch=main', '.']);
  await run(root, ['config', 'user.email', 'test@example.invalid']);
  await run(root, ['config', 'user.name', 'Test']);
  await fs.writeFile(path.join(root, 'SNAPSHOT.yaml'), 'project:\n  name: t\n', 'utf-8');
  await run(root, ['add', '-A']);
  await run(root, ['commit', '-m', 'base']);

  fleet.__configureFleetHealth(() => [ws(root, 'bare-1')]);
  await fleet.refreshGitState();

  const row = rowFor('bare-1');
  assert.equal(row.remoteKind, 'none');
  assert.equal(row.ahead, null,
    'null means "nothing to be ahead of"; 0 would read as "up to date"');
});

test('a deploy remote is counted, and classified as deploy', async () => {
  // The count matters as much as the refusal: PHASE-030 counts these as
  // an obligation of their own kind, so a repo that can only be deployed
  // must not report zero unpublished work.
  const root = await makeRepo('deploy', { ahead: 4,
    remoteUrl: 'root@76.13.51.7:/home/edankert/repos/example.com.git' });
  fleet.__configureFleetHealth(() => [ws(root, 'deploy-1')]);
  await fleet.refreshGitState();

  const row = rowFor('deploy-1');
  assert.equal(row.remoteKind, 'deploy');
  assert.equal(row.ahead, 4, 'a deploy remote still has unpublished commits');
});

test('probeGitState classifies remotes the way the push does', async () => {
  // The classification exists twice on purpose — git.ts will not trust one
  // that arrived over IPC — so the probe and the guard must agree, and
  // unknown shapes must land on `deploy`.
  const table = [
    ['https://github.com/edankert/project-os-cockpit.git', 'backup'],
    ['git@github.com:edankert/project-os-cockpit.git', 'backup'],
    ['https://gitlab.com/x/y.git', 'backup'],
    ['root@76.13.51.7:/home/edankert/repos/site.git', 'deploy'],
    ['/srv/git/thing.git', 'deploy'],
    ['ssh://deploy@example.com/var/repo.git', 'deploy'],
    ['', 'none'],
  ];
  for (const [url, expected] of table) {
    assert.equal(git.remoteKind(url), expected, url || '(empty)');
  }
});
