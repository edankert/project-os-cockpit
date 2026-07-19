// Renderer ↔ main bridge (TASK-0058 placeholder, TASK-0060 / TASK-0061
// fill in the actual surface). Exposes `window.cockpit` to renderer
// code via Electron's contextBridge, so the renderer never touches
// Node APIs directly.

import { contextBridge, ipcRenderer } from 'electron';

import type { Workspace } from './types';

const api = {
  workspaces: {
    list: (): Promise<Workspace[]> =>
      ipcRenderer.invoke('workspaces:list'),
    rescan: (): Promise<Workspace[]> =>
      ipcRenderer.invoke('workspaces:rescan'),
    open: (id: string): Promise<{ ok: boolean; error?: string }> =>
      ipcRenderer.invoke('workspaces:open', id),
    // Subscribe to per-workspace agent-state changes (FEAT-0010 /
    // TASK-0082). Main fans diffs from the file poller; this is how
    // the rail dots stay live without HTTP/SSE per workspace.
    onAgentState: (
      cb: (ev: { workspaceId: string; payload: unknown | null }) => void,
    ): (() => void) => {
      const handler = (_: unknown, ev: { workspaceId: string; payload: unknown | null }) => cb(ev);
      ipcRenderer.on('workspaces:agent-state', handler);
      return () => ipcRenderer.removeListener('workspaces:agent-state', handler);
    },
    onSwitchTo: (
      cb: (ev: { workspaceId: string }) => void,
    ): (() => void) => {
      const handler = (_: unknown, ev: { workspaceId: string }) => cb(ev);
      ipcRenderer.on('workspaces:switch-to', handler);
      return () => ipcRenderer.removeListener('workspaces:switch-to', handler);
    },
    notifyActiveChanged: (id: string | null): void => {
      ipcRenderer.send('workspaces:active-changed', id);
    },
    // FEAT-0016 CRUD --------------------------------------------------
    pickAndAdd: (): Promise<{
      workspaces: Workspace[]; added: number; skipped: number;
      cancelled: boolean; error?: string;
    }> => ipcRenderer.invoke('workspaces:pickAndAdd'),
    update: (patch: {
      id: string;
      userName?: string | null;
      userIcon?: string | null;
      userEmoji?: string | null;
      userColor?: string | null;
    }): Promise<{ ok: boolean }> =>
      ipcRenderer.invoke('workspaces:update', patch),
    remove: (id: string): Promise<{ ok: boolean }> =>
      ipcRenderer.invoke('workspaces:remove', id),
    pickIcon: (workspaceId?: string): Promise<{ ok: boolean; dataUri?: string; error?: string }> =>
      ipcRenderer.invoke('workspaces:pickIcon', { workspaceId }),
  },
  sidecar: {
    // Listen for sidecar lifecycle events (ready / failed / exited).
    onEvent: (cb: (ev: { kind: string; payload?: unknown }) => void): (() => void) => {
      const handler = (_: unknown, ev: { kind: string; payload?: unknown }) => cb(ev);
      ipcRenderer.on('sidecar:event', handler);
      return () => ipcRenderer.removeListener('sidecar:event', handler);
    },
  },
  menu: {
    onRescan: (cb: () => void): (() => void) => {
      const handler = (): void => cb();
      ipcRenderer.on('menu:rescan', handler);
      return () => ipcRenderer.removeListener('menu:rescan', handler);
    },
    onToggleTerminal: (cb: () => void): (() => void) => {
      const handler = (): void => cb();
      ipcRenderer.on('menu:toggle-terminal', handler);
      return () => ipcRenderer.removeListener('menu:toggle-terminal', handler);
    },
    onBack: (cb: () => void): (() => void) => {
      const handler = (): void => cb();
      ipcRenderer.on('menu:back', handler);
      return () => ipcRenderer.removeListener('menu:back', handler);
    },
    onForward: (cb: () => void): (() => void) => {
      const handler = (): void => cb();
      ipcRenderer.on('menu:forward', handler);
      return () => ipcRenderer.removeListener('menu:forward', handler);
    },
  },
  agent: {
    onFocus: (cb: (payload: unknown) => void): (() => void) => {
      const handler = (_: unknown, payload: unknown): void => cb(payload);
      ipcRenderer.on('agent:focus', handler);
      return () => ipcRenderer.removeListener('agent:focus', handler);
    },
  },
  agents: {
    // Cross-workspace fleet snapshot for the ~agents screen (FEAT-0032).
    fleet: (): Promise<unknown> => ipcRenderer.invoke('agents:fleet'),
  },
  app: {
    openExternal: (url: string): Promise<{ ok: boolean; error?: string }> =>
      ipcRenderer.invoke('app:openExternal', url),
    revealInFinder: (abs: string): Promise<{ ok: boolean; error?: string }> =>
      ipcRenderer.invoke('app:revealInFinder', abs),
    showContextMenu: (type: string, payload: Record<string, unknown>): Promise<void> =>
      ipcRenderer.invoke('menu:show-context', type, payload),
    onMenuDispatch: (
      cb: (ev: { action: string } & Record<string, unknown>) => void,
    ): (() => void) => {
      const handler = (_: unknown, ev: { action: string } & Record<string, unknown>) => cb(ev);
      ipcRenderer.on('menu:dispatch', handler);
      return () => ipcRenderer.removeListener('menu:dispatch', handler);
    },
    resolveDroppedFile: (absPath: string): Promise<{
      action: 'navigate' | 'offer-add-workspace' | 'ignored';
      workspaceId?: string;
      rel?: string;
      root?: string;
      reason?: string;
    }> => ipcRenderer.invoke('app:resolve-dropped-file', absPath),
  },
  deeplink: {
    onUrl: (cb: (url: string) => void): (() => void) => {
      const handler = (_: unknown, url: string): void => cb(url);
      ipcRenderer.on('deeplink', handler);
      return () => ipcRenderer.removeListener('deeplink', handler);
    },
  },
  settings: {
    get: () => ipcRenderer.invoke('settings:get'),
    set: (patch: Record<string, unknown>) => ipcRenderer.invoke('settings:set', patch),
  },
  dispatch: {
    execute: (workspaceId: string, item: unknown) =>
      ipcRenderer.invoke('dispatch:execute', workspaceId, item),
    list: (workspaceId: string) => ipcRenderer.invoke('dispatch:list', workspaceId),
    remove: (workspaceId: string, index: number) =>
      ipcRenderer.invoke('dispatch:remove', workspaceId, index),
    clear: (workspaceId: string) => ipcRenderer.invoke('dispatch:clear', workspaceId),
    poke: (workspaceId: string, state: string) => {
      ipcRenderer.send('dispatch:poke', { workspaceId, state });
    },
    onQueueChanged: (cb: (ev: { workspaceId: string; items: unknown[] }) => void) => {
      const handler = (_e: unknown, ev: { workspaceId: string; items: unknown[] }) => cb(ev);
      ipcRenderer.on('dispatch:queue-changed', handler);
      return () => ipcRenderer.removeListener('dispatch:queue-changed', handler);
    },
    onDelivered: (cb: (ev: { workspaceId: string; item: unknown; mode: string; warning?: string }) => void) => {
      const handler = (_e: unknown, ev: { workspaceId: string; item: unknown; mode: string; warning?: string }) => cb(ev);
      ipcRenderer.on('dispatch:delivered', handler);
      return () => ipcRenderer.removeListener('dispatch:delivered', handler);
    },
  },
  terminal: {
    spawn: (opts: { workspaceId: string; cwd?: string; cols?: number; rows?: number }): Promise<{ ok: boolean; error?: string }> =>
      ipcRenderer.invoke('terminal:spawn', opts),
    attach: (workspaceId: string): Promise<{ ok: boolean; error?: string; backlog: string }> =>
      ipcRenderer.invoke('terminal:attach', { workspaceId }),
    write: (workspaceId: string, data: string): void => {
      ipcRenderer.send('terminal:input', { workspaceId, data });
    },
    resize: (workspaceId: string, cols: number, rows: number): void => {
      ipcRenderer.send('terminal:resize', { workspaceId, cols, rows });
    },
    dispose: (workspaceId: string): Promise<{ ok: boolean }> =>
      ipcRenderer.invoke('terminal:dispose', { workspaceId }),
    onData: (cb: (ev: { workspaceId: string; data: string }) => void): (() => void) => {
      const handler = (_: unknown, ev: { workspaceId: string; data: string }) => cb(ev);
      ipcRenderer.on('terminal:data', handler);
      return () => ipcRenderer.removeListener('terminal:data', handler);
    },
    onExit: (cb: (info: { workspaceId: string; exitCode: number; signal?: number }) => void): (() => void) => {
      const handler = (_: unknown, info: { workspaceId: string; exitCode: number; signal?: number }) => cb(info);
      ipcRenderer.on('terminal:exit', handler);
      return () => ipcRenderer.removeListener('terminal:exit', handler);
    },
  },
};

contextBridge.exposeInMainWorld('cockpit', api);

// Surface the API shape on TypeScript's global window type.
// (No runtime cost; helps the renderer's tsc see the types.)
export type CockpitApi = typeof api;
