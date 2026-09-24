// Native user hooks are separate from Codex login and config.toml. This
// installer runs only after the user enables the Codex settings toggle.
import * as fs from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';
import { CODEX_HOOK_EVENTS } from './agent-instrument';

function object(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

export function configureCodexExternalHooks(
  enabled: boolean, scriptPath: string,
  configDir = process.env.CODEX_HOME || path.join(os.homedir(), '.codex'),
): { ok: boolean; error?: string } {
  const target = path.join(configDir, 'hooks.json');
  const command = `python3 '${scriptPath.replace(/'/g, `'\\''`)}' codex`;
  let temporary: string | undefined;
  try {
    const exists = fs.existsSync(target);
    if (!enabled && !exists) return { ok: true };
    const original = exists ? fs.readFileSync(target, 'utf8') : '';
    const settings: unknown = exists ? JSON.parse(original) : {};
    if (!object(settings) || (settings.hooks !== undefined && !object(settings.hooks))) {
      throw new Error('expected a hooks object');
    }
    const hooks = (settings.hooks ?? {}) as Record<string, unknown>;
    let removed = false;
    for (const [event, value] of Object.entries(hooks)) {
      if (!Array.isArray(value) || value.some((group) => !object(group)
        || !Array.isArray(group.hooks) || group.hooks.some((hook: unknown) => !object(hook)))) {
        throw new Error(`invalid hook groups for ${event}`);
      }
      // Keep the group's matcher/metadata and every unrelated handler.
      const groups = value.flatMap((group: Record<string, unknown>) => {
        const handlers = group.hooks as Record<string, unknown>[];
        const kept = handlers.filter((hook) => hook.command !== command);
        if (kept.length !== handlers.length) removed = true;
        return kept.length === handlers.length ? [group]
          : kept.length ? [{ ...group, hooks: kept }] : [];
      });
      if (groups.length || value.length === 0) hooks[event] = groups;
      else delete hooks[event];
    }
    if (!enabled && !removed) return { ok: true };
    if (enabled) {
      for (const event of CODEX_HOOK_EVENTS) {
        const groups = (hooks[event] ?? []) as unknown[];
        groups.push({ hooks: [{ type: 'command', command, timeout: 3 }] });
        hooks[event] = groups;
      }
    }
    if (Object.keys(hooks).length) settings.hooks = hooks;
    else delete settings.hooks;
    const next = JSON.stringify(settings, null, 2) + '\n';
    if (next === original) return { ok: true };
    fs.mkdirSync(configDir, { recursive: true });
    if (enabled && exists && !fs.existsSync(`${target}.cockpit-backup`)) {
      fs.copyFileSync(target, `${target}.cockpit-backup`, fs.constants.COPYFILE_EXCL);
    }
    temporary = `${target}.cockpit-${process.pid}-${Date.now()}.tmp`;
    fs.writeFileSync(temporary, next, { flag: 'wx', mode: exists ? fs.statSync(target).mode : 0o600 });
    fs.renameSync(temporary, target);
    temporary = undefined;
    return { ok: true };
  } catch (error) {
    return { ok: false, error: `Could not update ${target}: ${String(error)}. Existing configuration was preserved.` };
  } finally {
    if (temporary) try { fs.unlinkSync(temporary); } catch { /* already gone */ }
  }
}
