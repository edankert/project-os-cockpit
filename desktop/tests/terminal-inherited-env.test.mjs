// A new cockpit terminal starts without another Claude session's variables
// (ISS-0319 / TASK-0652).
//
// Runs the built terminal.js with stand-ins for Electron, node-pty and tmux.
// The app's own environment and the tmux server's global environment both
// carry what a Claude session in another cockpit terminal leaves behind; the
// test reads back the environment the terminal is spawned with and the tmux
// commands issued before the session is created.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';
import * as vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const built = path.join(here, '..', 'dist', 'ipc', 'terminal.js');
const tmux = '/opt/homebrew/bin/tmux';
const userData = '/private/tmp/terminal-inherited-env-test';
const instrument = path.join(userData, 'instrument', 'other-workspace');
const plugin = '/Applications/Cockpit/plugin/claude-code';

/** What a Claude session in another cockpit terminal leaves behind. */
const leftBehind = {
  CLAUDECODE: '1',
  CLAUDE_PID: '1247',
  CLAUDE_EFFORT: 'high',
  CLAUDE_CODE_ENTRYPOINT: 'cli',
  CLAUDE_CODE_CHILD_SESSION: '1',
  CLAUDE_CODE_SESSION_ID: '177b9b4e-b9cb-4962-9408-ed4887bc6aef',
  CLAUDE_CODE_SESSION_ATTENDED: '1',
  CLAUDE_CODE_EXECPATH: '/Users/someone/.local/share/claude/versions/2.1.292',
  CLAUDE_CODE_MAX_OUTPUT_TOKENS: '64000',
  CLAUDE_CODE_MESSAGING_SOCKET: '/tmp/cc-socks/1247.sock',
  CLAUDE_CODE_MESSAGING_TOKEN: 'e9a5',
  AI_AGENT: 'claude',
  TMUX: '/private/tmp/tmux-502/cockpit,1833,10',
  TMUX_PANE: '%3',
  ZDOTDIR: path.join(instrument, 'zdotdir'),
  COCKPIT_INSTRUMENT_DIR: instrument,
  CLAUDE_CODE_PLUGIN_DIRS: `/Users/someone/my-plugins:${plugin}`,
};

function harness({ appEnv, serverEnv }) {
  const source = fs.readFileSync(built, 'utf-8');
  const handlers = new Map();
  const tmuxCalls = [];
  const spawns = [];
  const window = { id: 7, isDestroyed: () => false, webContents: { send() {} } };
  const fakeRequire = (name) => {
    if (name === 'electron') return {
      app: { getPath: () => userData, quit() {} },
      BrowserWindow: { fromWebContents: () => window, fromId: () => window },
      ipcMain: { handle: (channel, handler) => handlers.set(channel, handler), on() {} },
    };
    if (name === 'node:child_process') return {
      execFileSync: (_binary, args) => {
        if (args[0] === '-V') return 'tmux 3.7b';
        tmuxCalls.push([...args]);
        if (args.includes('show-environment')) {
          if (serverEnv === null) throw new Error('no server running');
          return Object.entries(serverEnv).map(([k, v]) => `${k}=${v}`).join('\n') + '\n-REMOVED\n';
        }
        return '';
      },
      execFile: (_binary, _args, _options, callback) => queueMicrotask(() => callback(null, '', '')),
    };
    if (name === 'node:fs') return { existsSync: (file) => file === tmux, mkdirSync() {}, writeFileSync() {} };
    if (name === 'node:os') return os;
    if (name === 'node:path') return path;
    if (name === 'node-pty') return {
      spawn: (file, args, options) => {
        spawns.push({ file, args, env: options.env, tmuxCallsBefore: tmuxCalls.length });
        return { onData() {}, onExit() {}, write() {}, resize() {}, kill() {} };
      },
    };
    if (name === './agent-instrument') return {
      ensureInstrumentation: () => null,
      claudePluginDir: () => plugin,
    };
    throw new Error(`Unexpected import: ${name}`);
  };
  const module = { exports: {} };
  vm.runInNewContext(source, {
    module,
    exports: module.exports,
    require: fakeRequire,
    process: { env: appEnv, platform: 'darwin' },
    console,
    setTimeout,
  }, { filename: built });
  module.exports.registerTerminalIpc({ getActiveWindow: () => window });
  const spawn = handlers.get('terminal:spawn')({ sender: 'owner' }, { workspaceId: 'ws', cwd: '/private/tmp' });
  assert.equal(spawn.ok, true);
  return { tmuxCalls, spawns, inheritedValue: module.exports.inheritedValue };
}

const own = { SHELL: '/bin/zsh', HOME: '/Users/someone', PATH: '/usr/bin:/bin' };

test('a terminal is spawned without the variables another Claude session left in the app', () => {
  const h = harness({ appEnv: { ...own, ...leftBehind }, serverEnv: null });
  assert.equal(h.spawns.length, 1);
  const env = h.spawns[0].env;
  for (const name of Object.keys(leftBehind)) {
    if (name === 'CLAUDE_CODE_PLUGIN_DIRS') continue;
    assert.equal(env[name], undefined, `${name} reached the terminal`);
  }
  assert.equal(env.CLAUDE_CODE_PLUGIN_DIRS, '/Users/someone/my-plugins');
  assert.equal(env.PATH, own.PATH);
  assert.equal(env.HOME, own.HOME);
  assert.equal(env.TERM, 'xterm-256color');
});

test('the running tmux server loses the same variables before the session is created', () => {
  const h = harness({ appEnv: own, serverEnv: { ...leftBehind, LANG: 'en_GB.UTF-8' } });
  const before = h.tmuxCalls.slice(0, h.spawns[0].tmuxCallsBefore);
  const unset = before.filter((a) => a.includes('-u')).map((a) => a.at(-1)).sort();
  const expected = Object.keys(leftBehind).filter((n) => n !== 'CLAUDE_CODE_PLUGIN_DIRS').sort();
  assert.deepEqual(unset, expected);
  const reset = before.filter((a) => a.includes('set-environment') && !a.includes('-u'));
  assert.deepEqual(reset.map((a) => a.slice(-2)), [['CLAUDE_CODE_PLUGIN_DIRS', '/Users/someone/my-plugins']]);
  assert.equal(before.some((a) => a.includes('LANG')), false, 'an unrelated variable was touched');
  for (const args of before.filter((a) => a.includes('set-environment'))) {
    assert.deepEqual(args.slice(0, 4), ['-L', 'cockpit', 'set-environment', '-g']);
  }
});

test('the person\'s own ZDOTDIR and plugin folders are kept', () => {
  const { inheritedValue } = harness({ appEnv: own, serverEnv: {} });
  const root = path.join(userData, 'instrument');
  assert.equal(inheritedValue('ZDOTDIR', '/Users/someone/.config/zsh', root, plugin), '/Users/someone/.config/zsh');
  assert.equal(inheritedValue('ZDOTDIR', `${root}-elsewhere/zdotdir`, root, plugin), `${root}-elsewhere/zdotdir`);
  assert.equal(inheritedValue('CLAUDE_CODE_PLUGIN_DIRS', plugin, root, plugin), undefined);
  assert.equal(inheritedValue('CLAUDE_CODE_PLUGIN_DIRS', '/a:/b', root, plugin), '/a:/b');
  assert.equal(inheritedValue('CLAUDE_CODE_PLUGIN_DIRS', `/a:${plugin}`, root, undefined), `/a:${plugin}`);
});
