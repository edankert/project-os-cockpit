// Every project's Codex hooks run one identical command (TASK-0661).
//
// Codex trusts a hook by a hash of its command, and keeps one trust entry
// per event for every project. When each project's command named its own
// folder, trusting the hooks in one project un-trusted them in the others
// (ISS-0322). This builds two projects' launchers from the real generator
// and runs the shared forwarder with a stand-in curl.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import * as fs from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';
import * as vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const built = path.join(here, '..', 'dist', 'ipc', 'agent-instrument.js');

function generator(userData) {
  const module = { exports: {} };
  vm.runInNewContext(fs.readFileSync(built, 'utf-8'), {
    module, exports: module.exports, process, console,
    require: (name) => {
      if (name === 'electron') return { app: { getPath: () => userData, getAppPath: () => path.join(here, '..') } };
      if (name === 'node:fs') return fs;
      if (name === 'node:path') return path;
      throw new Error(`Unexpected import: ${name}`);
    },
  }, { filename: built });
  return module.exports;
}

/** The `-c hooks.*` values a launcher passes to Codex. */
function hookFlags(launcher) {
  return [...fs.readFileSync(launcher, 'utf-8').matchAll(/-c '(hooks\.[^']*(?:'\\''[^']*)*)'/g)].map((m) => m[1]);
}

test('two projects pass Codex byte-identical hook commands', () => {
  const userData = fs.mkdtempSync(path.join(os.tmpdir(), 'cockpit-hooks-'));
  try {
    const g = generator(userData);
    const a = g.ensureInstrumentation('project-a');
    const b = g.ensureInstrumentation('project-b');
    const flagsA = hookFlags(path.join(path.dirname(a.zdotdir), 'codex-launch.sh'));
    const flagsB = hookFlags(path.join(path.dirname(b.zdotdir), 'codex-launch.sh'));
    assert.equal(flagsA.length, 10);
    assert.deepEqual(flagsA, flagsB);
    assert.equal(flagsA.some((f) => f.includes('project-a')), false, 'no project folder in the command');
  } finally { fs.rmSync(userData, { recursive: true, force: true }); }
});

test('the shared forwarder posts to the sidecar of the terminal it runs in, and only then', () => {
  const userData = fs.mkdtempSync(path.join(os.tmpdir(), 'cockpit-hooks-'));
  try {
    const g = generator(userData);
    const a = g.ensureInstrumentation('project-a');
    const b = g.ensureInstrumentation('project-b');
    const dirA = path.dirname(a.zdotdir);
    const dirB = path.dirname(b.zdotdir);
    fs.writeFileSync(path.join(dirA, 'hook-env'), 'COCKPIT_HOOK_URL="http://127.0.0.1:8001"\n');
    fs.writeFileSync(path.join(dirB, 'hook-env'), 'COCKPIT_HOOK_URL="http://127.0.0.1:8002"\n');
    const bin = path.join(userData, 'bin');
    fs.mkdirSync(bin);
    const argv = path.join(userData, 'curl-argv');
    fs.writeFileSync(path.join(bin, 'curl'), `#!/bin/sh\nprintf "%s\\n" "$@" > "${argv}"\ncat >/dev/null\n`, { mode: 0o755 });
    const forwarder = path.join(userData, 'instrument', 'codex-hook-forward.sh');
    const run = (env) => {
      fs.rmSync(argv, { force: true });
      const r = spawnSync('/bin/sh', [forwarder], {
        input: '{"hook_event_name":"SessionStart"}',
        env: { PATH: `${bin}:/usr/bin:/bin`, ...env }, encoding: 'utf-8', timeout: 5000,
      });
      assert.equal(r.stdout, '{}\n');
      return fs.existsSync(argv) ? fs.readFileSync(argv, 'utf-8') : null;
    };
    assert.match(run({ COCKPIT_INSTRUMENT_DIR: dirA }), /http:\/\/127\.0\.0\.1:8001\/api\/agent-hook\?agent=codex/);
    assert.match(run({ COCKPIT_INSTRUMENT_DIR: dirB }), /http:\/\/127\.0\.0\.1:8002\//);
    assert.equal(run({}), null, 'no terminal folder: nothing is posted');
    assert.equal(run({ COCKPIT_INSTRUMENT_DIR: dirA, COCKPIT_NO_INSTRUMENT: '1' }), null, 'the kill switch posts nothing');
  } finally { fs.rmSync(userData, { recursive: true, force: true }); }
});
