// A cockpit terminal loads the Claude plugin, and nothing else is
// generated for Claude (FEAT-0156 / TASK-0650).
//
// Runs the built agent-instrument.js against a stand-in Electron `app`,
// then starts the generated zsh startup files in a real zsh with a
// stand-in HOME, and reads CLAUDE_CODE_PLUGIN_DIRS back. RISK-0004's rule
// is checked here too: HOME's .claude folder is byte-identical afterwards.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import * as fs from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';
import * as vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const built = path.join(here, '..', 'dist', 'ipc', 'agent-instrument.js');
const appPath = path.join(here, '..');
const pluginDir = path.join(appPath, 'plugin', 'claude-code');
const hasZsh = fs.existsSync('/bin/zsh');

/** Loads the built module with `app` pointing at a temporary state folder. */
function load(state, app = appPath) {
  const module = { exports: {} };
  vm.runInNewContext(fs.readFileSync(built, 'utf-8'), {
    module,
    exports: module.exports,
    require: (name) => name === 'electron'
      ? { app: { getPath: () => state, getAppPath: () => app } }
      : name === 'node:fs' ? fs : name === 'node:path' ? path : assert.fail(`unexpected import ${name}`),
    process,
    console: { ...console, error: () => {} },
  }, { filename: built });
  return module.exports;
}

/** A temporary state folder and HOME, with a ~/.claude to watch. */
function sandbox(userZshrc = '') {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'cockpit-claude-plugin-'));
  const home = path.join(root, 'home');
  fs.mkdirSync(path.join(home, '.claude'), { recursive: true });
  fs.writeFileSync(path.join(home, '.claude', 'settings.json'), '{"env":{}}\n');
  fs.writeFileSync(path.join(home, '.zshrc'), userZshrc);
  return { root, home, state: path.join(root, 'state') };
}

/** Every file under a folder, with a hash of its bytes and its mtime. */
function fingerprint(dir) {
  const out = {};
  for (const entry of fs.readdirSync(dir, { recursive: true })) {
    const file = path.join(dir, entry);
    const stat = fs.statSync(file);
    if (stat.isFile()) {
      out[entry] = `${createHash('sha256').update(fs.readFileSync(file)).digest('hex')} ${stat.mtimeMs}`;
    }
  }
  return out;
}

/** Runs `script` in an interactive zsh started from the generated files. */
function zsh(instrument, home, script, extraEnv = {}) {
  const result = spawnSync('/bin/zsh', ['-i', '-c', script], {
    env: { PATH: process.env.PATH ?? '/usr/bin:/bin', HOME: home, ...instrument.env, ...extraEnv },
    encoding: 'utf-8',
    timeout: 5000,
  });
  assert.equal(result.status, 0, result.stderr);
  return result.stdout;
}

test('the terminal puts the plugin on CLAUDE_CODE_PLUGIN_DIRS once, after the user\'s own value', { skip: !hasZsh }, () => {
  const { root, home, state } = sandbox('export CLAUDE_CODE_PLUGIN_DIRS=/mine\nalias claude="claude --mine"\n');
  try {
    const before = fingerprint(path.join(home, '.claude'));
    const instrument = load(state).ensureInstrumentation('ws');
    assert.ok(instrument, 'instrumentation was generated');
    const out = zsh(instrument, home,
      'print -r -- "outer=$CLAUDE_CODE_PLUGIN_DIRS"; '
      + 'zsh -i -c \'print -r -- "nested=$CLAUDE_CODE_PLUGIN_DIRS"\'; '
      + 'print -r -- "claude=$(whence -w claude)"');
    assert.match(out, new RegExp(`^outer=/mine:${pluginDir}$`, 'm'));
    assert.match(out, new RegExp(`^nested=/mine:${pluginDir}$`, 'm'), 'a nested shell adds the folder only once');
    assert.match(out, /^claude=claude: alias$/m, 'the user\'s claude alias is left alone, no cockpit wrapper');
    assert.deepEqual(fingerprint(path.join(home, '.claude')), before, '~/.claude is untouched (RISK-0004)');
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test('with no value of the user\'s, the variable is just the plugin, also in a nested shell', { skip: !hasZsh }, () => {
  const { root, home, state } = sandbox();
  try {
    const instrument = load(state).ensureInstrumentation('ws');
    const out = zsh(instrument, home,
      'print -r -- "outer=$CLAUDE_CODE_PLUGIN_DIRS"; zsh -i -c \'print -r -- "nested=$CLAUDE_CODE_PLUGIN_DIRS"\'');
    assert.match(out, new RegExp(`^outer=${pluginDir}$`, 'm'));
    assert.match(out, new RegExp(`^nested=${pluginDir}$`, 'm'));
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test('no Claude settings, hook or status-line file is written, and an old one is left in place', () => {
  const { root, state } = sandbox();
  try {
    const dir = path.join(state, 'instrument', 'ws');
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, 'claude-settings.json'), '{"old":true}');
    const instrument = load(state).ensureInstrumentation('ws');
    assert.ok(instrument);
    const files = fs.readdirSync(dir).sort();
    assert.deepEqual(files, ['claude-settings.json', 'codex-launch.sh', 'hook-env', 'zdotdir']);
    assert.ok(fs.existsSync(path.join(state, 'instrument', 'codex-hook-forward.sh')),
      'one Codex forwarder serves every project (TASK-0661)');
    assert.equal(fs.readFileSync(path.join(dir, 'claude-settings.json'), 'utf-8'), '{"old":true}',
      'a terminal opened before the update still runs claude --settings on this file');
    const zshrc = fs.readFileSync(path.join(dir, 'zdotdir', '.zshrc'), 'utf-8');
    assert.doesNotMatch(zshrc, /'claude'\(\)|unalias claude|--settings|statusline/);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test('the kill switch: no files at spawn, and no plugin when set inside the shell', { skip: !hasZsh }, () => {
  const { root, home, state } = sandbox();
  const saved = process.env.COCKPIT_NO_INSTRUMENT;
  try {
    process.env.COCKPIT_NO_INSTRUMENT = '1';
    assert.equal(load(state).ensureInstrumentation('ws'), null);
    assert.equal(fs.existsSync(path.join(state, 'instrument', 'ws')), false);
    delete process.env.COCKPIT_NO_INSTRUMENT;
    const instrument = load(state).ensureInstrumentation('ws');
    const out = zsh(instrument, home, 'print -r -- "dirs=$CLAUDE_CODE_PLUGIN_DIRS"', { COCKPIT_NO_INSTRUMENT: '1' });
    assert.match(out, /^dirs=$/m);
  } finally {
    if (saved === undefined) delete process.env.COCKPIT_NO_INSTRUMENT;
    else process.env.COCKPIT_NO_INSTRUMENT = saved;
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test('a checkout without the plugin folder loads nothing rather than a missing folder', { skip: !hasZsh }, () => {
  const { root, home, state } = sandbox();
  try {
    const instrument = load(state, path.join(root, 'no-app')).ensureInstrumentation('ws');
    assert.ok(instrument, 'Codex is still instrumented');
    const out = zsh(instrument, home, 'print -r -- "dirs=$CLAUDE_CODE_PLUGIN_DIRS"');
    assert.match(out, /^dirs=$/m);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test('the plugin folder the shell names is the one in this repository', () => {
  assert.ok(fs.existsSync(path.join(pluginDir, '.claude-plugin', 'plugin.json')));
  assert.ok(fs.existsSync(path.join(pluginDir, 'hooks', 'hooks.json')));
});
