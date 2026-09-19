import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { homedir, tmpdir } from 'node:os';
import { join } from 'node:path';

export interface WeeklyQuota { used_percentage: number; resets_at?: string }
export interface CodexUsage { weekly: WeeklyQuota | null; capturedAt: number }

function record(value: unknown): Record<string, unknown> | null {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
    ? value as Record<string, unknown> : null;
}

// The general Codex bucket is distinct from model-specific allowances. A
// weekly window may be primary (weekly-only plans) or secondary.
export function weeklyQuota(result: unknown): WeeklyQuota | null {
  const root = record(result);
  const buckets = record(root?.rateLimitsByLimitId);
  const bucket = record(buckets ? buckets.codex : root?.rateLimits);
  if (!bucket || (bucket.limitId != null && bucket.limitId !== 'codex')) return null;
  for (const key of ['primary', 'secondary']) {
    const w = record(bucket[key]);
    if (w?.windowDurationMins !== 10_080 || typeof w.usedPercent !== 'number'
      || !Number.isFinite(w.usedPercent) || w.usedPercent < 0 || w.usedPercent > 100) continue;
    const quota: WeeklyQuota = { used_percentage: w.usedPercent };
    if (typeof w.resetsAt === 'number' && Number.isFinite(w.resetsAt) && w.resetsAt > 0) {
      const date = new Date(w.resetsAt * 1000);
      if (Number.isFinite(date.getTime())) quota.resets_at = date.toISOString();
    }
    return quota;
  }
  return null;
}

function codexCommand(): string {
  // GUI apps may not inherit the login shell's PATH. Prefer the user's
  // standalone install, then common package-manager locations.
  return [join(homedir(), '.local/bin/codex'), '/opt/homebrew/bin/codex', '/usr/local/bin/codex']
    .find(existsSync) ?? 'codex';
}

// Only initialize and read account limits. No thread, login or prompt is
// created, and raw account details never cross the renderer boundary.
export function readCodexUsage(command = codexCommand(), timeoutMs = 10_000): Promise<CodexUsage | null> {
  return new Promise((resolve) => {
    const child = spawn(command, ['app-server', '--stdio'], {
      cwd: tmpdir(), stdio: ['pipe', 'pipe', 'ignore'], windowsHide: true,
    });
    let settled = false;
    let initialized = false;
    let buffer = '';
    const timer = setTimeout(() => finish(null), timeoutMs);
    function finish(value: CodexUsage | null): void {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      child.stdin.end();
      child.kill();
      // A stuck server must not accumulate on every two-minute poll.
      const force = setTimeout(() => child.kill('SIGKILL'), 1000);
      force.unref();
      child.once('close', () => clearTimeout(force));
      resolve(value);
    }
    function send(message: unknown): void { child.stdin.write(JSON.stringify(message) + '\n'); }
    child.on('error', () => finish(null));
    child.on('exit', () => finish(null));
    child.stdin.on('error', () => finish(null));
    child.stdout.setEncoding('utf8');
    child.stdout.on('data', (chunk: string) => {
      if (settled) return;
      buffer += chunk;
      if (buffer.length > 1_048_576) { finish(null); return; }
      let newline: number;
      while (!settled && (newline = buffer.indexOf('\n')) >= 0) {
        const line = buffer.slice(0, newline);
        buffer = buffer.slice(newline + 1);
        let message: Record<string, unknown> | null;
        try { message = record(JSON.parse(line)); } catch { continue; }
        if (!message) continue;
        if (message.id === 1 && !initialized) {
          if (message.error || !record(message.result)) { finish(null); return; }
          initialized = true;
          send({ method: 'initialized', params: {} });
          send({ method: 'account/rateLimits/read', id: 2 });
        } else if (message.id === 2 && initialized) {
          if (message.error || !record(message.result)) { finish(null); return; }
          finish({ weekly: weeklyQuota(message.result), capturedAt: Date.now() });
        }
      }
    });
    send({ method: 'initialize', id: 1, params: {
      clientInfo: { name: 'project_os_cockpit_usage', version: '0.1.0' },
    } });
  });
}

let cached: CodexUsage | null = null;
let checkedAt = 0;
let pending: Promise<CodexUsage | null> | null = null;

export function getCodexUsage(): Promise<CodexUsage | null> {
  if (pending) return pending;
  if (Date.now() - checkedAt < 120_000) return Promise.resolve(cached);
  checkedAt = Date.now();
  pending = readCodexUsage().then((value) => {
    cached = value;
    return value;
  }).finally(() => { pending = null; });
  return pending;
}
