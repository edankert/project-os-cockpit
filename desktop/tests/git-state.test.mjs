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
  // The git pass is a Python subprocess since TASK-0422 — one implementation
  // for the badge, History and this shell — so the suite needs an interpreter
  // that can import the package. `pythonExecutable()` normally resolves a
  // bundled runtime through Electron's `app`, which is absent here; the
  // pytest bridge hands us its own interpreter, and this fallback keeps
  // `node --test` runnable on its own.
  if (!process.env.COCKPIT_DESKTOP_PYTHON) {
    const venv = path.join(here, '..', '..', '.venv', 'bin', 'python');
    try {
      await fs.access(venv);
      process.env.COCKPIT_DESKTOP_PYTHON = venv;
    } catch { process.env.COCKPIT_DESKTOP_PYTHON = 'python3'; }
  }
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

test('a remote with no upstream is UNKNOWN, and unknown is not zero (TASK-0421)', async () => {
  // The case ADR-0027's fourth admission test exists for, on the surfaces
  // that had never honoured it. A real github-shaped remote and a branch
  // tracking nothing: `rev-list @{u}..HEAD` cannot run, so no count exists.
  const root = await mkTmp('no-upstream');
  await run(root, ['init', '--initial-branch=main', '.']);
  await run(root, ['config', 'user.email', 'test@example.invalid']);
  await run(root, ['config', 'user.name', 'Test']);
  await run(root, ['config', 'commit.gpgsign', 'false']);
  await fs.writeFile(path.join(root, 'SNAPSHOT.yaml'), 'project:\n  name: t\n', 'utf-8');
  await run(root, ['add', '-A']);
  await run(root, ['commit', '-m', 'base']);
  await run(root, ['remote', 'add', 'origin', 'https://github.com/example/z.git']);

  fleet.__configureFleetHealth(() => [ws(root, 'unknown-1')]);
  await fleet.refreshGitState();

  const row = rowFor('unknown-1');
  assert.equal(row.remoteKind, 'backup', 'the remote is real and classifiable');
  assert.equal(row.ahead, null,
    'no upstream means no count — 0 would say "nothing to publish", which is '
    + 'the one thing nobody knows');
});

test('the count and the dirty count come from the sidecar\'s own module (TASK-0422)', async () => {
  // Not "the two numbers happen to match" — the shell's row is compared
  // against what `python -m project_os_cockpit.fleet_git` says for the same
  // repo, which is the module the badge and History read. If the shell ever
  // grows its own walk again, these diverge the moment either changes.
  const root = await makeRepo('one-walk', { ahead: 2,
    remoteUrl: 'https://github.com/example/w.git' });
  await fs.mkdir(path.join(root, 'docs'), { recursive: true });
  await fs.writeFile(path.join(root, 'docs', 'note.md'), '# uncommitted\n', 'utf-8');

  fleet.__configureFleetHealth(() => [ws(root, 'one-walk-1')]);
  await fleet.refreshGitState();
  const row = rowFor('one-walk-1');

  const direct = await new Promise((resolve, reject) => {
    execFile(
      process.env.COCKPIT_DESKTOP_PYTHON,
      ['-m', 'project_os_cockpit.fleet_git', root],
      { timeout: 20_000, cwd: path.join(here, '..', '..') },
      (err, stdout) => (err ? reject(err) : resolve(JSON.parse(stdout.trim()))),
    );
  });

  assert.equal(row.ahead, direct.ahead);
  assert.equal(row.dirty, direct.dirty);
  assert.equal(row.remoteKind, direct.remote_kind);
  assert.equal(row.ahead, 2);
  assert.equal(row.dirty, 1, 'the uncommitted note is in scope: docs/');
});

test('git.ts no longer walks git for a count (TASK-0422)', async () => {
  // The guard ISS-0165 asked for: the check that publication is walked once
  // could only see the two surfaces written in Python, so it was structurally
  // blind to the one that disagreed. Source text, deliberately — the point is
  // that no second implementation EXISTS, which no behavioural test can say.
  const raw = await fs.readFile(
    path.join(here, '..', 'src', 'ipc', 'git.ts'), 'utf-8');
  // COMMENTS STRIPPED FIRST, and this is not a detail: the first version of
  // this guard failed against the very change it was written for, because the
  // paragraph explaining that the counting had been removed NAMED the two
  // commands it removed. A guard a comment can satisfy — or break — is
  // measuring prose, and this repo has been bitten by both directions of that
  // in one week.
  const src = raw
    .replace(/\/\*[\s\S]*?\*\//g, '')
    .split('\n').filter((l) => !l.trim().startsWith('//')).join('\n');
  assert.ok(!src.includes('rev-list'),
    'git.ts counts commits again — the badge and this shell are two '
    + 'implementations of one number, which is ISS-0165');
  assert.ok(!src.includes('--porcelain'),
    'git.ts counts uncommitted files again — same defect, one number left');
  assert.ok(!src.includes('probeGitState'),
    'probeGitState is back; the fleet git pass is fleet_git.py');
  // And what it MUST keep: the classification that decides whether a push
  // may run at all is re-derived here on purpose.
  assert.ok(src.includes('export function remoteKind'),
    'git.ts must keep its own remote classification — a UI state is not a '
    + 'guard, and this is the process that runs the push');
});

test('remoteKind classifies remotes the way the push does', async () => {
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
