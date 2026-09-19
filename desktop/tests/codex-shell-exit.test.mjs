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

test('exiting Codex returns to the same cockpit shell', { skip: !fs.existsSync('/bin/zsh') }, () => {
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), 'cockpit-codex-exit-'));
  try {
    const bin = path.join(temporary, 'bin');
    const home = path.join(temporary, 'home');
    const argvFile = path.join(temporary, 'codex-argv');
    const replacementLauncher = path.join(temporary, 'replacement-launcher.sh');
    const curlArgvFile = path.join(temporary, 'curl-argv');
    const curlBodyFile = path.join(temporary, 'curl-body');
    fs.mkdirSync(bin);
    fs.mkdirSync(home);
    fs.writeFileSync(path.join(home, '.zshrc'), '');
    fs.writeFileSync(path.join(bin, 'codex'), '#!/bin/sh\nprintf "%s\\n" "$@" > "$CODEX_ARGV_FILE"\nprintf "codex child ran\\n"\nexit 17\n', { mode: 0o755 });
    fs.writeFileSync(path.join(bin, 'curl'), '#!/bin/sh\nprintf "%s\\n" "$@" > "$CURL_ARGV_FILE"\ncat > "$CURL_BODY_FILE"\nexit 0\n', { mode: 0o755 });
    fs.writeFileSync(replacementLauncher, '#!/bin/sh\nprintf "updated launcher ran\\n"\n', { mode: 0o755 });

    const source = fs.readFileSync(built, 'utf-8');
    const module = { exports: {} };
    vm.runInNewContext(source, {
      module,
      exports: module.exports,
      require: (name) => name === 'electron'
        ? { app: { getPath: () => temporary } }
        : requireBuiltin(name),
      process,
      console,
    }, { filename: built });
    const instrument = module.exports.ensureInstrumentation('shell-exit-test');
    assert.ok(instrument, 'cockpit generated its zsh startup files');
    const instrumentDir = path.dirname(instrument.zdotdir);
    const launchScript = path.join(instrumentDir, 'codex-launch.sh');

    const result = spawnSync('/bin/zsh', ['-i', '-c',
      'print "before=$$"; codex; result=$?; print "after=$$ status=$result"; cp "$REPLACEMENT_LAUNCHER" "$CODEX_LAUNCH_SCRIPT"; codex'], {
      env: {
        ...process.env,
        HOME: home,
        CODEX_ARGV_FILE: argvFile,
        CODEX_LAUNCH_SCRIPT: launchScript,
        REPLACEMENT_LAUNCHER: replacementLauncher,
        PATH: `${bin}:${process.env.PATH ?? ''}`,
        ...instrument.env,
        COCKPIT_NO_INSTRUMENT: '',
      },
      cwd: temporary,
      encoding: 'utf-8',
      timeout: 5000,
    });
    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /codex child ran/);
    const before = result.stdout.match(/before=(\d+)/)?.[1];
    const after = result.stdout.match(/after=(\d+) status=17/)?.[1];
    assert.ok(before, `shell did not start: ${result.stdout}`);
    assert.equal(after, before, `Codex exit did not return to the original shell: ${result.stdout}`);
    assert.match(result.stdout, /updated launcher ran/, 'the same shell loads the regenerated launcher');
    const args = fs.readFileSync(argvFile, 'utf-8').trim().split('\n');
    assert.ok(args.includes('--no-alt-screen'));
    const configs = args.flatMap((arg, i) => arg === '-c' ? [args[i + 1]] : []);
    for (const event of ['SessionStart', 'UserPromptSubmit', 'PreToolUse',
      'PostToolUse', 'PermissionRequest', 'Stop', 'SessionEnd']) {
      assert.equal(configs.filter((value) => value.startsWith(`hooks.${event}=`)).length, 1,
        `${event} should be forwarded once`);
    }
    assert.equal(configs.filter((value) => value.startsWith('notify=')).length, 1);
    assert.ok(!args.includes('--dangerously-bypass-hook-trust'));

    fs.writeFileSync(path.join(instrumentDir, 'hook-env'), 'COCKPIT_HOOK_URL="http://127.0.0.1:8766"\n');
    const event = JSON.stringify({ hook_event_name: 'UserPromptSubmit', session_id: 'codex-test', prompt: 'fix' });
    const hookConfig = configs.find((value) => value.startsWith('hooks.UserPromptSubmit='));
    const encodedCommand = hookConfig?.match(/command=("(?:[^"\\]|\\.)*")/)?.[1];
    assert.ok(encodedCommand, `missing hook command in ${hookConfig}`);
    const hookCommand = JSON.parse(encodedCommand);
    const hook = spawnSync('/bin/sh', ['-c', hookCommand], {
      input: event,
      env: { ...process.env, PATH: `${bin}:${process.env.PATH ?? ''}`, CURL_ARGV_FILE: curlArgvFile, CURL_BODY_FILE: curlBodyFile },
      encoding: 'utf-8', timeout: 5000,
    });
    assert.equal(hook.status, 0, hook.stderr);
    assert.equal(hook.stdout, '{}\n');
    assert.equal(fs.readFileSync(curlBodyFile, 'utf-8'), event);
    assert.match(fs.readFileSync(curlArgvFile, 'utf-8'), /\/api\/agent-hook\?agent=codex/);
  } finally {
    fs.rmSync(temporary, { recursive: true, force: true });
  }
});

function requireBuiltin(name) {
  if (name === 'node:fs') return fs;
  if (name === 'node:path') return path;
  throw new Error(`Unexpected import: ${name}`);
}
