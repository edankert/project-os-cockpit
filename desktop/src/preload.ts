// Renderer ↔ main bridge (TASK-0058 placeholder, TASK-0060 / TASK-0061
// fill in the actual surface). Exposes `window.cockpit` to renderer
// code via Electron's contextBridge, so the renderer never touches
// Node APIs directly.

import { contextBridge, ipcRenderer, webUtils } from 'electron';

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
    // Context-aware Edit menu (FEAT-0054 / TASK-0263): main forwards
    // Copy/Paste here so the renderer can route to whichever pane has
    // focus. `role: 'copy'` can only ever see a DOM selection.
    onEdit: (cb: (ev: { action: string }) => void): (() => void) => {
      const handler = (_: unknown, ev: { action: string }): void => cb(ev);
      ipcRenderer.on('menu:edit', handler);
      return () => ipcRenderer.removeListener('menu:edit', handler);
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
    onDispatchSelection: (cb: (text: string) => void): (() => void) => {
      const handler = (_: unknown, text: string): void => cb(text);
      ipcRenderer.on('menu:dispatch-selection', handler);
      return () => ipcRenderer.removeListener('menu:dispatch-selection', handler);
    },
  },
  agents: {
    // Cross-workspace fleet snapshot for the ~agents screen (FEAT-0032).
    fleet: (): Promise<unknown> => ipcRenderer.invoke('agents:fleet'),
    // Session history for one workspace (TASK-0180 / ISS-0013).
    sessions: (workspaceId: string): Promise<unknown> =>
      ipcRenderer.invoke('agents:sessions', workspaceId),
  },
  // Per-workspace docs-validator state across the fleet (FEAT-0028).
  fleetHealth: {
    get: (): Promise<unknown> => ipcRenderer.invoke('fleet:health'),
    // Explicit re-check including cold (sidecar-less) workspaces —
    // those are on a slow schedule, so a surface that wants a fresh
    // answer now has to ask for one (TASK-0249).
    recheck: (): Promise<unknown> => ipcRenderer.invoke('fleet:health-recheck'),
    // Pushed whenever any workspace's validator state changes — the
    // sidecars publish `cockpit:validation` on change, so this is
    // event-driven rather than polled.
    onChange: (cb: (payload: unknown) => void): (() => void) => {
      const handler = (_: unknown, payload: unknown): void => cb(payload);
      ipcRenderer.on('fleet:health', handler);
      return () => ipcRenderer.removeListener('fleet:health', handler);
    },
  },
  // One clipboard path (FEAT-0054 / TASK-0261). The renderer never
  // touches `navigator.clipboard`: it needs document focus to write and
  // a permission to read, and Electron's main-process clipboard needs
  // neither. Both calls RESOLVE with a result rather than rejecting, so
  // a caller cannot accidentally ignore a failure.
  clipboard: {
    write: (text: string): Promise<{ ok: boolean; error?: string }> =>
      ipcRenderer.invoke('clipboard:write', text),
    read: (): Promise<{ ok: boolean; text?: string; error?: string }> =>
      ipcRenderer.invoke('clipboard:read'),
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
    // Electron 32 REMOVED `File.path` (deprecated in 30). The drop handler
    // read it, got `undefined`, and returned silently — so dropping a note
    // stopped navigating and dropping a screenshot did nothing at all, with
    // no error anywhere. `webUtils.getPathForFile` is the replacement, and it
    // must be called in the preload: it is not exposed to the renderer.
    pathForFile: (file: File): string => {
      try { return webUtils.getPathForFile(file); } catch { return ''; }
    },
    captureScreenshot: (workspaceId: string): Promise<{
      ok: boolean; name?: string; cancelled?: boolean; error?: string;
    }> => ipcRenderer.invoke('app:capture-screenshot', workspaceId),
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
