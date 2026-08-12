// Renderer entry — workspace switcher + cockpit mount (TASK-0060 + TASK-0061).
//
// NOTE: This file deliberately has NO `import` / `export` statements.
// tsc's `module: CommonJS` setting emits CommonJS module wrappers for
// any file with imports/exports, and `exports`/`require` are NOT
// defined in the renderer's plain `<script>` context. Keeping this
// file as a top-level script avoids needing a bundler or a separate
// tsconfig for the renderer. Types are inlined below.
//
// All Node / Electron access is routed through `window.cockpit`
// (defined in preload.ts). This script runs in the sandboxed renderer
// context.

interface Workspace {
  id: string;
  root: string;
  name: string;
  /** ADR-0024: `project.id` or the directory name — what `[[project#ID]]`
   *  matches. Optional here so an older main process (a shell that has not
   *  been relaunched since this shipped) degrades to "no such project" rather
   *  than to a crash. */
  projectId?: string;
  lastOpened: string | null;
  pinned: boolean;
  icon?: string;
  userName?: string;
  userIcon?: string;
  userEmoji?: string;
  userColor?: string;
}

function effectiveName(ws: Workspace): string {
  return ws.userName && ws.userName.length > 0 ? ws.userName : ws.name;
}

interface SidecarReadyPayload {
  workspaceId: string;
  port: number;
  url: string;
}

interface SidecarFailedPayload {
  workspaceId: string;
  reason: string;
  stderrTail?: string;
}

interface SidecarExitedPayload {
  workspaceId: string;
  code: number | null;
  signal: NodeJS.Signals | null;
}

interface AgentStatePayload {
  state: string;
  ts: string;
  target?: string;
  agent?: string;
  message?: string;
  decayed_from?: string;
}

interface QueuedDispatch {
  id: string; rel: string; verb?: string;
  /** Agent id from the served registry (ISS-0032). A string, not a closed
   *  union: a union here is a second declaration of membership, and the queue
   *  must never discard work for an agent this build does not know. */
  agent: string; prompt: string; ts: string;
}

interface CockpitApi {
  workspaces: {
    list: () => Promise<Workspace[]>;
    rescan: () => Promise<Workspace[]>;
    open: (id: string) => Promise<{ ok: boolean; error?: string }>;
    onAgentState: (
      cb: (ev: { workspaceId: string; payload: AgentStatePayload | null }) => void,
    ) => () => void;
    onSwitchTo: (
      cb: (ev: { workspaceId: string }) => void,
    ) => () => void;
    notifyActiveChanged: (id: string | null) => void;
    pickAndAdd: () => Promise<{
      workspaces: Workspace[]; added: number; skipped: number;
      cancelled: boolean; error?: string;
    }>;
    update: (patch: {
      id: string;
      userName?: string | null;
      userIcon?: string | null;
      userEmoji?: string | null;
      userColor?: string | null;
    }) => Promise<{ ok: boolean }>;
    remove: (id: string) => Promise<{ ok: boolean }>;
    pickIcon: (workspaceId?: string) => Promise<{ ok: boolean; dataUri?: string; error?: string }>;
  };
  sidecar: {
    onEvent: (
      cb: (ev: { kind: string; payload?: unknown }) => void,
    ) => () => void;
  };
  menu: {
    onRescan: (cb: () => void) => () => void;
    onRestartTerminal: (cb: () => void) => () => void;
    onToggleTerminal: (cb: () => void) => () => void;
    onEdit: (cb: (ev: { action: string }) => void) => () => void;
    onBack: (cb: () => void) => () => void;
    onForward: (cb: () => void) => () => void;
  };
  agent: {
    onFocus: (cb: (payload: unknown) => void) => () => void;
    onDispatchSelection: (cb: (text: string) => void) => () => void;
  };
  agents: {
    fleet: () => Promise<FleetPayload>;
    sessions: (workspaceId: string) => Promise<AgentSessionSlim[]>;
  };
  // Per-workspace docs-validator state across the fleet (FEAT-0028).
  // One clipboard path (FEAT-0054 / TASK-0261) — main-process backed,
  // so it needs neither document focus nor a permission, and both calls
  // RESOLVE with a result so a failure cannot be silently dropped.
  clipboard: {
    write: (text: string) => Promise<{ ok: boolean; error?: string }>;
    read: () => Promise<{ ok: boolean; text?: string; error?: string }>;
  };
  // Push, and only ever from a person clicking (FEAT-0055 / TASK-0266).
  git: {
    push: (workspaceId: string) => Promise<{ ok: boolean; error?: string }>;
  };
  fleetHealth: {
    get: () => Promise<{ rows: FleetHealthRow[]; generatedAt: number }>;
    recheck: () => Promise<{ rows: FleetHealthRow[]; generatedAt: number }>;
    onChange: (cb: (payload: unknown) => void) => () => void;
  };
  app: {
    openExternal: (url: string) => Promise<{ ok: boolean; error?: string }>;
    revealInFinder: (abs: string) => Promise<{ ok: boolean; error?: string }>;
    showContextMenu: (type: string, payload: Record<string, unknown>) => Promise<void>;
    onMenuDispatch: (
      cb: (ev: { action: string } & Record<string, unknown>) => void,
    ) => () => void;
    pathForFile: (file: File) => string;
    captureScreenshot: (workspaceId: string) => Promise<{
      ok: boolean; name?: string; cancelled?: boolean; error?: string;
    }>;
    resolveDroppedFile: (absPath: string) => Promise<{
      action: 'navigate' | 'offer-add-workspace' | 'ignored';
      workspaceId?: string;
      rel?: string;
      root?: string;
      reason?: string;
    }>;
  };
  deeplink: {
    onUrl: (cb: (url: string) => void) => () => void;
  };
  settings: {
    get: () => Promise<{ externalHook: boolean }>;
    set: (patch: Record<string, unknown>) => Promise<{ ok: boolean; error?: string; settings: { externalHook: boolean } }>;
  };
  dispatch: {
    execute: (workspaceId: string, item: unknown) => Promise<{ queued: boolean; delivered?: string; warning?: string; error?: string }>;
    list: (workspaceId: string) => Promise<QueuedDispatch[]>;
    remove: (workspaceId: string, index: number) => Promise<QueuedDispatch[]>;
    clear: (workspaceId: string) => Promise<QueuedDispatch[]>;
    poke: (workspaceId: string, state: string) => void;
    onQueueChanged: (cb: (ev: { workspaceId: string; items: QueuedDispatch[] }) => void) => () => void;
    onDelivered: (cb: (ev: { workspaceId: string; item: QueuedDispatch; mode: string; warning?: string }) => void) => () => void;
  };
  terminal: {
    spawn: (opts: { workspaceId: string; cwd?: string; cols?: number; rows?: number }) => Promise<{ ok: boolean; error?: string }>;
    attach: (workspaceId: string) => Promise<{ ok: boolean; error?: string; backlog: string }>;
    write: (workspaceId: string, data: string) => void;
    resize: (workspaceId: string, cols: number, rows: number) => void;
    dispose: (workspaceId: string) => Promise<{ ok: boolean }>;
    onData: (cb: (ev: { workspaceId: string; data: string }) => void) => () => void;
    onExit: (cb: (info: { workspaceId: string; exitCode: number; signal?: number }) => void) => () => void;
  };
}

// Ambient declarations for the UMD-loaded xterm + addon-fit globals.
// (Renderer is a non-module script, so we can't `import` them — they're
// loaded via `<script>` tags in index.html.)
//
// xterm UMD assigns each named export directly to `window`, so the
// `Terminal` class is reachable as a global. addon-fit's UMD assigns
// the whole module object to `window.FitAddon`, so the class itself
// lives at `FitAddon.FitAddon`. Different shapes, hence the asymmetric
// declarations below.
declare const Terminal: new (options?: Record<string, unknown>) => XtermTerminal;
declare const FitAddon: { FitAddon: new () => XtermFitAddon };

interface XtermTerminal {
  open(elem: HTMLElement): void;
  write(data: string | Uint8Array): void;
  loadAddon(addon: unknown): void;
  onData(cb: (data: string) => void): void;
  onResize(cb: (size: { cols: number; rows: number }) => void): void;
  resize(cols: number, rows: number): void;
  readonly cols: number;
  readonly rows: number;
  /** xterm.js public mode state — `mouseTrackingMode` is 'none' | 'x10' |
   *  'vt200' | 'drag' | 'any'. Wiped by reset(); we snapshot + restore it
   *  per workspace so wheel forwarding survives a switch (ISS-0016). */
  readonly modes: { mouseTrackingMode?: string };
  dispose(): void;
  focus(): void;
  reset(): void;
  clear(): void;
  getSelection(): string;
  hasSelection(): boolean;
  selectAll(): void;
  onSelectionChange(cb: () => void): void;
  /** xterm.js: mutating `options.theme` re-paints the visible buffer. */
  options: { theme?: Record<string, string> };
}

interface XtermFitAddon {
  fit(): void;
  proposeDimensions(): { cols: number; rows: number } | undefined;
}

// Pull the API off `window` via a single typed cast so the rest of the
// file is plain typed code.
const cockpitApi = (window as unknown as { cockpit: CockpitApi }).cockpit;

// Bridge: base.css uses `[data-theme="dark"]` to activate the dark
// palette (mode-1 cockpit.js toggles this from a UI control). Until
// FEAT-0009 wires a proper theme picker, mirror the OS preference
// straight onto <html> so the metadata-strip + body content match
// the native chrome.
// Theme picker (FEAT-0009 / TASK-0095). Override `prefers-color-scheme`
// when the user picks an explicit theme via the status-bar buttons.
type ThemePref = 'system' | 'light' | 'dark';

function loadStoredTheme(): ThemePref {
  try {
    const v = localStorage.getItem('cockpit:theme');
    if (v === 'light' || v === 'dark' || v === 'system') return v;
  } catch { /* localStorage unavailable */ }
  return 'system';
}

let themePref: ThemePref = loadStoredTheme();

function applyTheme(): void {
  const dark = themePref === 'dark'
    || (themePref === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
  // Repaint the xterm if one's been spawned — its palette is JS-driven,
  // not CSS-driven (FEAT-0015 user feedback). Guarded against the
  // temporal-dead-zone: applyTheme() runs at module init before `term`
  // is declared, so reading it would throw a ReferenceError.
  try {
    if (term) term.options.theme = currentTerminalTheme();
  } catch { /* term not yet declared */ }
}

function setThemePref(pref: ThemePref): void {
  themePref = pref;
  try { localStorage.setItem('cockpit:theme', pref); } catch { /* ignore */ }
  applyTheme();
  // After DOM is ready (and DOM lookups have run) the theme buttons
  // exist — keep this guarded so the initial call doesn't crash if
  // it fires before the listeners are wired.
  refreshThemeButtons();
}

function refreshThemeButtons(): void {
  document.querySelectorAll<HTMLButtonElement>('.sf-theme-btn').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.theme === themePref);
  });
}

applyTheme();
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyTheme);

function $<T extends Element>(sel: string): T {
  const el = document.querySelector(sel);
  if (!el) throw new Error(`missing element: ${sel}`);
  return el as T;
}

const listEl       = $<HTMLUListElement>('#workspace-list');
const wsRailAdd    = $<HTMLButtonElement>('#ws-rail-add');
const leftPaneCollapseBtn = $<HTMLButtonElement>('#left-pane-collapse');
const hideCompletedBtn    = $<HTMLButtonElement>('#hide-completed-toggle');
const followBtn           = document.getElementById('follow-toggle') as HTMLButtonElement | null;
const platformBarEl       = $<HTMLDivElement>('#platform-bar');
const platformCombo       = $<HTMLDivElement>('#platform-combo');
const platformLabel       = $<HTMLSpanElement>('#platform-label');
const platformMenu        = $<HTMLUListElement>('#platform-menu');
const wsNavProject        = $<HTMLElement>('#ws-nav-project');
const wsNavProjectIcon    = $<HTMLSpanElement>('#ws-nav-project-icon');
const wsNavProjectName    = $<HTMLSpanElement>('#ws-nav-project-name');
const projectSettingsBtn  = $<HTMLButtonElement>('#project-settings-btn');
const projectSettingsMenu = $<HTMLDivElement>('#project-settings-menu');
const psmName             = $<HTMLInputElement>('#psm-name');
const psmPickIcon         = $<HTMLButtonElement>('#psm-pick-icon');
const psmEmoji            = $<HTMLInputElement>('#psm-emoji');
const psmSwatches         = $<HTMLDivElement>('#psm-swatches');
const psmResetIcon        = $<HTMLButtonElement>('#psm-reset-icon');
const psmReveal           = $<HTMLButtonElement>('#psm-reveal');
const psmRemove           = $<HTMLButtonElement>('#psm-remove');
const placeholder  = $<HTMLDivElement>('#placeholder');
const docView      = $<HTMLElement>('#doc-view');
const statusBar    = $<HTMLDivElement>('#status-bar');
const terminalBtn  = $<HTMLButtonElement>('#terminal-toggle');
const terminalPane = $<HTMLDivElement>('#terminal-pane');
const terminalMount = $<HTMLDivElement>('#terminal-mount');
const terminalDivider = $<HTMLDivElement>('#terminal-divider');
const wsNavPlaceholder = $<HTMLDivElement>('#ws-nav-placeholder');
const wsNavContent = $<HTMLDivElement>('#ws-nav-content');
const appEl = $<HTMLDivElement>('#app');
const rightPaneToggle = $<HTMLButtonElement>('#right-pane-toggle');
const rightPaneContent = $<HTMLDivElement>('#right-pane-content');
const quickSwitchEl = $<HTMLDivElement>('#quick-switch');
const quickSwitchInput = $<HTMLInputElement>('#quick-switch-input');
const quickSwitchResults = $<HTMLUListElement>('#quick-switch-results');
const findBar = $<HTMLDivElement>('#find-bar');
const findInput = $<HTMLInputElement>('#find-input');
const findCount = $<HTMLSpanElement>('#find-count');
const findPrevBtn = $<HTMLButtonElement>('#find-prev');
const findNextBtn = $<HTMLButtonElement>('#find-next');
const findCloseBtn = $<HTMLButtonElement>('#find-close');
const sfSidecar = $<HTMLSpanElement>('#sf-sidecar');
const sfPath = $<HTMLSpanElement>('#sf-path');

let workspaces: Workspace[] = [];
let activeId: string | null = null;
// Per-workspace agent-state (FEAT-0010 / TASK-0082). The poller in
// main fans diffs from `.cockpit/agent-state.json` files via the
// `workspaces:agent-state` IPC; we paint a colored dot per pill.
const agentStates = new Map<string, AgentStatePayload>();
// The Electron sidecar exposes a per-workspace HTTP endpoint at this
// URL once `sidecar:event` 'ready' fires. The centre pane fetches
// /api/render against this base; null between workspaces.
let sidecarBaseUrl: string | null = null;
// Current docs-rel path mounted in the centre pane. Null when the
// placeholder is showing.
let currentRel: string | null = null;

// One shared auto-hide timer so a newer toast always cancels an older
// toast's pending hide (TASK-0158 — overlapping toasts used to hide
// each other early). Callers use scheduleHide() rather than their own
// setTimeout(hideStatus, …).
let statusHideTimer: number | null = null;

//: How long a toast stays before it dismisses itself. Errors dwell longer
//: because an error that vanishes in two seconds is one the reader misses —
//: but "longer" is not "forever", which is what they were (ISS-0144).
const STATUS_DWELL_MS = 4000;
const STATUS_ERROR_DWELL_MS = 12000;

function showStatus(text: string, kind: 'info' | 'error' = 'info'): void {
  if (statusHideTimer != null) { clearTimeout(statusHideTimer); statusHideTimer = null; }
  statusBar.replaceChildren(document.createTextNode(text));
  statusBar.classList.toggle('error', kind === 'error');
  statusBar.classList.remove('is-actionable');
  // Click anywhere on the bar dismisses it. It is an absolutely-positioned
  // panel over the pane, and a panel with no exit is a modal nobody chose.
  statusBar.onclick = () => hideStatus();
  statusBar.hidden = false;
  // **The default is that it goes away** (ISS-0144). It used to be that it
  // stayed, with dismissal delegated to each caller through `scheduleHide` —
  // and 78 of 110 call sites did not make that call, so the app's normal
  // behaviour was a permanent overlay and the 32 that remembered were the
  // exception. A caller wanting a different dwell still overrides: this
  // schedules, and `scheduleHide` clears and replaces the pending timer.
  scheduleHide(kind === 'error' ? STATUS_ERROR_DWELL_MS : STATUS_DWELL_MS);
}

function scheduleHide(ms: number): void {
  if (statusHideTimer != null) clearTimeout(statusHideTimer);
  statusHideTimer = window.setTimeout(hideStatus, ms);
}

// A status toast with a click action — used for suppressed agent-focus
// jumps (TASK-0158): "Agent focus → TARGET · open".
function showActionStatus(text: string, action: string, onClick: () => void): void {
  if (statusHideTimer != null) { clearTimeout(statusHideTimer); statusHideTimer = null; }
  statusBar.replaceChildren(document.createTextNode(`${text} · `));
  const link = document.createElement('button');
  link.type = 'button';
  link.className = 'status-bar-action';
  link.textContent = action;
  link.addEventListener('click', (e) => { e.stopPropagation(); hideStatus(); onClick(); });
  statusBar.appendChild(link);
  statusBar.classList.remove('error');
  statusBar.classList.add('is-actionable');
  // Dismissible, but NOT self-dismissing (ISS-0144): this one is an offer, and
  // an offer that expires before it can be taken is worse than one that waits.
  // The link stops propagation, so taking the action never doubles as a
  // dismissal of something the reader has not read.
  statusBar.onclick = () => hideStatus();
  statusBar.hidden = false;
}

/** Copy through the main process, and SAY SO when it fails
 *  (FEAT-0054 / TASK-0261).
 *
 *  `navigator.clipboard.writeText` throws `NotAllowedError` unless the
 *  document is focused, and every call site here used to `void` the
 *  promise or swallow it — so a copy that did not happen looked exactly
 *  like one that did. That is how this survived to be reported by a
 *  user rather than noticed.
 */
async function copyText(text: string, label = 'Copied'): Promise<boolean> {
  if (!text) { showStatus('Nothing to copy', 'error'); return false; }
  try {
    const res = await cockpitApi.clipboard.write(text);
    if (!res.ok) {
      showStatus(`Copy failed: ${res.error ?? 'unknown error'}`, 'error');
      return false;
    }
    showStatus(label);
    scheduleHide(1200);
    return true;
  } catch (err) {
    showStatus(`Copy failed: ${String(err)}`, 'error');
    return false;
  }
}

function hideStatus(): void {
  if (statusHideTimer != null) { clearTimeout(statusHideTimer); statusHideTimer = null; }
  statusBar.hidden = true;
  statusBar.onclick = null;
  statusBar.classList.remove('is-actionable');
}

function renderWorkspaceRail(): void {
  // FEAT-0015 / TASK-0100: each workspace is a square. Renders the
  // project icon (data URI sourced from `findWorkspaceIcon` in main)
  // when available, otherwise a colored letter fallback.
  listEl.innerHTML = '';
  if (workspaces.length === 0) {
    const li = document.createElement('li');
    li.className = 'empty';
    // TASK-0318's pattern, split across two carriers because the rail is a
    // column of ~40px squares and a sentence cannot render in it. The visible
    // label stays the path; the title carries what the rail shows.
    li.textContent = '+ to add';
    li.title = 'No workspaces yet — + adds a repo with a SNAPSHOT.yaml.';
    listEl.appendChild(li);
    return;
  }
  for (const ws of workspaces) {
    const li = document.createElement('li');
    li.className = 'ws-square';
    li.dataset.id = ws.id;
    if (ws.id === activeId) li.classList.add('active');

    paintWorkspaceVisual(li, ws, 32);

    li.addEventListener('click', () => { void openWorkspace(ws.id); });
    li.addEventListener('mousedown', (e) => {
      // Middle-click closes the workspace (Chrome / VS Code convention).
      if (e.button === 1) {
        e.preventDefault();
        closeWorkspace(ws.id);
      }
    });
    applyAgentStateToSquare(li, ws); // also paints the validator badge
    listEl.appendChild(li);
  }
}

function colorFromName(name: string): string {
  // Deterministic hue (0-360) from the workspace name. Saturation +
  // lightness picked so all variants read on both light and dark bg.
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = (hash * 31 + name.charCodeAt(i)) | 0;
  }
  const hue = Math.abs(hash) % 360;
  return `hsl(${hue} 55% 45%)`;
}

// ---- fleet validator health (FEAT-0028 / TASK-0250) ----------------

// `healthMarks` comes from `health-marks.ts`, loaded as a separate <script>
// before this one. Neither file is a module, so tsc already sees it in the
// global scope — no import, and no `declare` (which would collide with the
// real signature).

interface FleetHealthRow {
  workspaceId: string;
  name: string;
  root: string;
  state: 'ok' | 'failing' | 'unavailable' | 'unknown';
  errors: number;
  warnings: number;
  checkedAt: string | null;
  source: 'live' | 'cold' | null;
  detail?: string;
  stale?: boolean;
  validator?: 'repo' | 'bundled';
  ahead?: number | null;
  remoteKind?: 'backup' | 'deploy' | 'none';
  remote?: string | null;
}

const fleetHealth = new Map<string, FleetHealthRow>();

/** Paint the validator badge on one rail square.
 *
 *  Deliberately separate from `applyAgentStateToSquare`: the two
 *  signals are independent, arrive on different channels, and one
 *  repainting must not wipe the other. Folding them into one function
 *  is how they would end up sharing a `classList` reset.
 */
function applyHealthToSquare(li: HTMLLIElement, ws: Workspace): void {
  for (const cls of ['health-ok', 'health-failing', 'health-unavailable', 'health-stale']) {
    li.classList.remove(cls);
  }
  const existing = li.querySelector('.ws-health');
  if (existing) existing.remove();

  const base = li.dataset.baseTitle ?? li.title;
  li.title = base;

  const row = fleetHealth.get(ws.id);
  // The decision lives in `health-marks.ts` as a pure function so it can be
  // tested without a DOM (ISS-0074). `unknown` yields no classes and no
  // badge — nothing at all, not a reassuring grey.
  const marks = healthMarks(row);
  for (const cls of marks.classes) li.classList.add(cls);
  if (marks.badge !== null) {
    const badge = document.createElement('span');
    badge.className = 'ws-health';
    badge.textContent = marks.badge;
    badge.setAttribute('aria-hidden', 'true');
    li.appendChild(badge);
  }
  if (!row || row.state === 'unknown') return;
  li.title = `${base}\n${healthSummary(row)}`;
}

/** One line of prose for the tooltip — state, count, and how old. */
function healthSummary(row: FleetHealthRow): string {
  const when = row.checkedAt ? relativeTime(row.checkedAt) : 'never';
  const how = row.source === 'cold' ? 'not open' : row.source === 'live' ? 'open' : '';
  // Which validator ran, for cold rows only. The per-repo choice
  // (TASK-0249) is only defensible if the reader can see it was made —
  // a fleet of mixed template versions must not look uniform. A live
  // row's sidecar is by construction running its own repo's copy.
  const by = row.validator === 'bundled' ? ", cockpit's bundled validator"
    : row.validator === 'repo' ? ", this repo's own validator" : '';
  // How far behind its remote (FEAT-0055). Reported here because the
  // push does not fail for being hard — it fails for being invisible:
  // 312 commits across eight repos on 2026-07-30, nothing mentioning it.
  const behind = row.remoteKind === 'none'
    ? '\nno remote — nothing is backed up'
    : typeof row.ahead === 'number' && row.ahead > 0
      ? `\n${row.ahead} commit${row.ahead === 1 ? '' : 's'} not pushed`
        + (row.remoteKind === 'deploy' ? ' (remote is a deploy target)' : '')
      : '';
  const suffix = `${how ? `${how}, ` : ''}checked ${when}${by}${row.stale ? ' — stale' : ''}`;
  if (row.state === 'failing') {
    return `docs: ${row.errors} validator error${row.errors === 1 ? '' : 's'} (${suffix})${behind}`;
  }
  if (row.state === 'unavailable') {
    return `docs: could not validate — ${row.detail || 'no reason given'} (${suffix})${behind}`;
  }
  return `docs: clean (${suffix})${behind}`;
}

function relativeTime(iso: string): string {
  const ms = Date.now() - Date.parse(iso);
  if (!Number.isFinite(ms)) return iso;
  const mins = Math.round(ms / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.round(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.round(hrs / 24)}d ago`;
}

function applyFleetHealthPayload(payload: unknown): void {
  const rows = (payload as { rows?: FleetHealthRow[] } | null)?.rows;
  if (!Array.isArray(rows)) return;
  fleetHealth.clear();
  for (const row of rows) fleetHealth.set(row.workspaceId, row);
  for (const li of Array.from(listEl.querySelectorAll<HTMLLIElement>('li.ws-square'))) {
    const ws = workspaces.find((w) => w.id === li.dataset.id);
    if (ws) applyHealthToSquare(li, ws);
  }
}

// Declared by cache-temperature.js, loaded as a plain script before this
// one (same arrangement as healthMarks).
declare function cacheTemperature(
  input: { ts?: string | null; state?: string | null } | null | undefined,
  now: number,
  ttlMs?: number,
): 'warm' | 'cold' | 'unknown';
declare function railKey(
  state: AgentStatePayload | null | undefined, now: number, ttlMs?: number,
): string | null;
declare function attentionIds(
  states: Iterable<[string, AgentStatePayload]>, now: number, ttlMs?: number,
): string[];

/** True when this workspace's session has passed the cache TTL.
 *
 *  ISS-0105: a session waiting 211 hours pulsed exactly like one waiting
 *  two minutes. Cold demotes to the grey dot and leaves the NEEDS YOU
 *  list, so amber-pulse means "waiting AND still cheap to resume".
 */
function isColdWorkspace(state: AgentStatePayload | undefined, now = Date.now()): boolean {
  return cacheTemperature(state, now) === 'cold';
}

function applyAgentStateToSquare(li: HTMLLIElement, ws: Workspace): void {
  const state = agentStates.get(ws.id);
  const cold = isColdWorkspace(state);
  const stateLine = state
    ? `\nagent: ${state.state}${state.message ? ` — ${state.message}` : ''}`
      + (cold ? `\ncold — last turn ${fmtDuration(state.ts || null, null)} ago;`
        + ' resuming re-writes the cached prefix' : '')
    : '';
  // The base tooltip. Health appends to THIS rather than to whatever
  // `title` currently holds — otherwise two independent repaint paths
  // append to each other's output and the tooltip grows without bound.
  li.dataset.baseTitle = `${effectiveName(ws)}\n${ws.root}${stateLine}`;
  li.title = li.dataset.baseTitle;
  for (const cls of ['state-busy', 'state-waiting', 'state-needs-input', 'state-done', 'state-idle', 'state-error']) {
    li.classList.remove(cls);
  }
  const existingDot = li.querySelector('.ws-dot');
  if (existingDot) existingDot.remove();
  if (!state) { applyHealthToSquare(li, ws); return; }
  // Cold takes the same branch decay already took (ISS-0105). The
  // judgment is railKey's, in the module the node suite can reach
  // (ISS-0110); this line only applies it.
  const key = railKey(state, Date.now()) || state.state;
  li.classList.add(`state-${key}`);
  // Acknowledged alerts go static (pulse off, colour kept) — TASK-0157.
  li.classList.toggle('acked', isAlertAcked(ws.id, state.ts || ''));
  const dot = document.createElement('span');
  dot.className = 'ws-dot';
  dot.setAttribute('aria-hidden', 'true');
  li.appendChild(dot);
  // Agent state arrives far more often than validator state; without
  // this the health badge survives (classes are untouched) but its
  // tooltip line is lost on the next poll.
  applyHealthToSquare(li, ws);
}

function closeWorkspace(id: string): void {
  // Soft close: just drop from the active list in the UI. The real
  // sidecar lifecycle is owned by main; the user re-opens via the +.
  const idx = workspaces.findIndex((w) => w.id === id);
  if (idx < 0) return;
  workspaces.splice(idx, 1);
  agentStates.delete(id);
  if (activeId === id) {
    // Pick the next-best tab to land on; fall back to placeholder.
    activeId = null;
    if (workspaces.length > 0) {
      const fallback = workspaces[Math.min(idx, workspaces.length - 1)];
      void openWorkspace(fallback.id);
    } else {
      placeholder.hidden = false;
      docView.hidden = true;
    }
  }
  renderWorkspaceRail();
}

async function loadWorkspaces(): Promise<void> {
  try {
    console.log('[renderer] requesting workspace list…');
    workspaces = await cockpitApi.workspaces.list();
    console.log(`[renderer] got ${workspaces.length} workspaces`);
    renderWorkspaceRail();
  } catch (err) {
    console.error('[renderer] workspaces.list failed:', err);
    showStatus(`Failed to load workspaces: ${String(err)}`, 'error');
  }
}

async function rescanWorkspaces(): Promise<void> {
  wsRailAdd.disabled = true;
  showStatus('Scanning for workspaces…');
  try {
    workspaces = await cockpitApi.workspaces.rescan();
    renderWorkspaceRail();
    showStatus(`Found ${workspaces.length} workspace${workspaces.length === 1 ? '' : 's'}.`);
    scheduleHide(1500);
  } catch (err) {
    showStatus(`Rescan failed: ${String(err)}`, 'error');
  } finally {
    wsRailAdd.disabled = false;
  }
}

function setProjectHeader(ws: Workspace | null): void {
  if (!ws) {
    wsNavProject.hidden = true;
    return;
  }
  wsNavProject.hidden = false;
  const displayName = effectiveName(ws);
  wsNavProjectName.textContent = displayName || '?';
  wsNavProjectName.title = `${displayName}\n${ws.root}`;
  paintWorkspaceVisual(wsNavProjectIcon, ws, 22);
}

// ----- Workspace visual painter --------------------------------------
// Priority (most specific wins):
//   1. userIcon  → uploaded image
//   2. userEmoji → emoji character
//   3. icon      → auto-probed favicon / logo in the project dir
//   4. identicon → 5×5 symmetric SVG derived from ws.id (with userColor
//                  or a hash-derived hue)

function paintWorkspaceVisual(target: HTMLElement, ws: Workspace, sizePx: number): void {
  target.replaceChildren();
  target.classList.remove('ws-has-emoji');
  target.style.backgroundColor = '';
  if (ws.userIcon) {
    const img = document.createElement('img');
    img.className = 'ws-icon';
    img.alt = '';
    img.src = ws.userIcon;
    target.appendChild(img);
    return;
  }
  if (ws.userEmoji) {
    target.classList.add('ws-has-emoji');
    target.textContent = ws.userEmoji;
    target.style.fontSize = `${Math.round(sizePx * 0.6)}px`;
    return;
  }
  if (ws.icon) {
    const img = document.createElement('img');
    img.className = 'ws-icon';
    img.alt = '';
    img.src = ws.icon;
    target.appendChild(img);
    return;
  }
  // Identicon fallback.
  target.appendChild(buildIdenticon(ws.id, ws.userColor));
  target.style.backgroundColor = ws.userColor
    ? withAlpha(ws.userColor, 0.12)
    : identiconTint(ws.id);
}

const IDENTICON_SVG_NS = 'http://www.w3.org/2000/svg';

function buildIdenticon(seed: string, colorOverride?: string): SVGElement {
  // 32-bit FNV-like hash from the workspace id; the first 15 bits drive
  // the cell pattern (3 cols × 5 rows, mirrored), the remaining bits
  // pick a hue.
  let hash = 2166136261 >>> 0;
  for (let i = 0; i < seed.length; i++) {
    hash = (hash ^ seed.charCodeAt(i)) >>> 0;
    hash = Math.imul(hash, 16777619) >>> 0;
  }
  const fill = colorOverride ?? `hsl(${hash % 360} 55% 42%)`;
  const svg = document.createElementNS(IDENTICON_SVG_NS, 'svg');
  svg.setAttribute('class', 'ws-identicon');
  svg.setAttribute('viewBox', '0 0 30 30');
  svg.setAttribute('aria-hidden', 'true');
  svg.setAttribute('fill', fill);
  const CELL = 6;
  for (let r = 0; r < 5; r++) {
    for (let c = 0; c < 3; c++) {
      const bit = (hash >>> (r * 3 + c)) & 1;
      if (!bit) continue;
      for (const col of c === 2 ? [2] : [c, 4 - c]) {
        const rect = document.createElementNS(IDENTICON_SVG_NS, 'rect');
        rect.setAttribute('x', String(col * CELL));
        rect.setAttribute('y', String(r * CELL));
        rect.setAttribute('width', String(CELL));
        rect.setAttribute('height', String(CELL));
        svg.appendChild(rect);
      }
    }
  }
  return svg;
}

function identiconTint(seed: string): string {
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) | 0;
  return `hsl(${Math.abs(h) % 360} 50% 92%)`;
}

function withAlpha(color: string, alpha: number): string {
  // Best-effort tint for the square background. hsl() → keep, just
  // mix toward elevated bg via CSS opacity isn't possible here; instead
  // return an hsla approximation when input is hsl(...), or a fallback.
  const m = color.match(/^hsl\(\s*(-?\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)%\s+(\d+(?:\.\d+)?)%\s*\)$/);
  if (m) {
    return `hsl(${m[1]} ${m[2]}% 92%)`;
  }
  return color + Math.round(alpha * 255).toString(16).padStart(2, '0');
}

// ---- Following a cross-repo link (FEAT-0093 / TASK-0392) ---------------
//
// `[[project-os-dev#ADR-0011]]` renders as an anchor carrying the two parts
// as data rather than an href (ADR-0024): a sidecar serves ONE repo and
// cannot resolve another, so it must not emit a URL it cannot honour. The
// shell can — it discovers every SNAPSHOT-bearing repo and runs a sidecar per
// workspace — so the lookup happens here.
//
// The jump is two-legged and the legs are in different processes: switch the
// workspace, then ask the ARRIVING sidecar where that id lives. Neither half
// can answer the other's, which is why this is deferred through
// `pendingCrossRepoJump` and consumed when the sidecar reports ready.

let pendingCrossRepoJump: { project: string; noteId: string } | null = null;

// A cross-repo jump has to beat the arriving workspace's own landing, and it
// cannot win by being fast: both are async, and the landing has a head start.
// So it does not race — it suppresses, once.
//
// This is the third time this exact shape has been got wrong here. ISS-0040:
// the README fetch raced a virtual landing and won, so you selected Design,
// restarted, and got README with the Design button lit. Then the guard named
// only `overview` and Review and Design inherited it. Now a jump arrives into
// a workspace whose landing overwrites the note that was clicked — measured
// live: the workspace switched to project-os-dev and the centre pane read
// "Features (by phase) — Nothing owed on features."
let suppressLandingOnce = false;

/** True once per arm, so a suppression can never outlive the jump that set it
 *  and silently swallow the next legitimate landing. */
function consumeLandingSuppression(): boolean {
  if (!suppressLandingOnce) return false;
  suppressLandingOnce = false;
  return true;
}

async function jumpToCrossRepoNote(project: string, noteId: string): Promise<void> {
  const target = workspaces.find((w) => w.projectId === project);
  if (!target) {
    // Said out loud, never a dead click. A reference to a project that is not
    // on this machine is a real answer — the note may exist and simply not be
    // here — and it must not look identical to one that resolves.
    showStatus(`No project “${project}” on this machine — ${noteId} is not reachable from here.`, 'error');
    return;
  }
  if (target.id === activeId) {
    // Already here: no switch, no wait, just locate.
    void locateAndOpen(noteId, project);
    return;
  }
  pendingCrossRepoJump = { project, noteId };
  suppressLandingOnce = true;
  await openWorkspace(target.id);
}

async function locateAndOpen(noteId: string, project: string): Promise<void> {
  if (!sidecarBaseUrl) return;
  try {
    const resp = await fetch(
      `${sidecarBaseUrl}/api/cockpit/locate?id=${encodeURIComponent(noteId)}`,
    );
    if (!resp.ok) { showStatus(`Could not look up ${noteId}`, 'error'); return; }
    const found = await resp.json() as { found?: boolean; rel?: string };
    if (!found.found || !found.rel) {
      showStatus(`${project} has no ${noteId}`, 'error');
      return;
    }
    void navigateTo(found.rel);
  } catch (err) {
    showStatus(`Could not open ${noteId}: ${String(err)}`, 'error');
  }
}

// One delegated listener on the document: cross-repo links appear in the note
// body, in the frontmatter strip and in the context pane, and three listeners
// would be three places to forget one.
document.addEventListener('click', (ev) => {
  const el = (ev.target as HTMLElement | null)?.closest?.('a.cross-repo-link');
  if (!el) return;
  ev.preventDefault();
  ev.stopPropagation();
  const project = el.getAttribute('data-project') || '';
  const noteId = el.getAttribute('data-note-id') || '';
  if (project && noteId) void jumpToCrossRepoNote(project, noteId);
});

async function openWorkspace(id: string): Promise<void> {
  if (id === activeId) return;
  activeId = id;
  // Tell main which workspace is active so the agent-state poller
  // can suppress notifications about the one the user is on (TASK-0087).
  cockpitApi.workspaces.notifyActiveChanged(id);
  const ws = workspaces.find((w) => w.id === id);
  if (ws) setProjectHeader(ws);
  // If the terminal pane is open, swap the xterm to the new
  // workspace's PTY (FEAT-0015 / TASK-0104).
  if (!terminalPane.hidden) void attachTerminalTo(id);
  renderWorkspaceRail();
  refreshFollowButton();  // reflect the new workspace's follow mode
  scheduleAck();  // looking at this workspace may acknowledge its alert
  placeholder.hidden = true;
  docView.hidden = true;
  sidecarBaseUrl = null;
  clearValidation();  // the report belongs to a repo no longer on screen
  // Same reason as the agent strip below: the tray is per-workspace, and
  // leaving the old project's items up while the new sidecar starts would
  // invite triaging a file into the wrong repo.
  void renderInboxPanel();
  // Drop the previous workspace's snapshot so a waiting row for the
  // newly-active workspace doesn't briefly show the old workspace's
  // cost before the new sidecar's /api/cockpit/state resolves (review
  // finding, FEAT-0030). Clear the agent strip too so it can't keep
  // rendering the previous workspace's session if the new sidecar
  // fails to spawn (review finding F3).
  lastAgentSnap = null;
  showAgentStrip(null, null);
  // `stripLastPrompt` and `workTransitions` are sticky *within* a
  // workspace (the strip keeps showing the last prompt / touched notes
  // between runs), but must not survive a switch — otherwise a project
  // whose current session has no prompt of its own renders the previous
  // workspace's prompt (ISS-0015). Clear them so the strip starts clean.
  stripLastPrompt = '';
  workTransitions.clear();
  // Centre tabs are per-workspace context — reset on switch (TASK-0159).
  agentsTabOpen = false;
  lastDocRel = null;
  docTabChanged = false;
  // Overview scope is per-project — a phase from the previous workspace
  // won't exist here (a phase-less project would 404 on ~overview/PHASE-…).
  // Reset so a new workspace starts at the unscoped project overview (TASK-0177).
  overviewScope = null;
  scopePhaseList = null;
  renderCenterTabs();
  currentRel = null;
  setSidecarStatus('spawning');
  refreshFooterPath();
  refreshFooterAgent();
  showStatus('Starting cockpit…');
  const res = await cockpitApi.workspaces.open(id);
  if (!res.ok) {
    showStatus(`Failed to open workspace: ${res.error ?? 'unknown error'}`, 'error');
    placeholder.hidden = false;
    activeId = null;
    renderWorkspaceRail();
  }
  // The sidecar:ready event handler below loads the URL into the iframe.
}

cockpitApi.sidecar.onEvent((ev) => {
  switch (ev.kind) {
    case 'ready': {
      const p = ev.payload as SidecarReadyPayload;
      // Every workspace's sidecar URL is kept, not only the active one's
      // (TASK-0313). The shell spawns one per workspace and announces each;
      // discarding the rest here is why "one line per workspace" looked
      // impossible — the data was arriving and being thrown away.
      sidecarUrls.set(p.workspaceId, p.url);
      if (p.workspaceId !== activeId) { void refreshAttention(); return; }
      sidecarBaseUrl = p.url;
      setSidecarStatus('ready');
      hideStatus();
      // SSE soft-reload + heartbeat (TASK-0086) — subscribe to this
      // sidecar's event stream now that we know its URL.
      attachSidecarEventStream(p.url);
      startTabStateHeartbeat();
      // In-workspace nav populates as soon as the sidecar is up
      // (TASK-0083). Default landing for the centre pane: README.md
      // — UNLESS the user is in Overview mode, where loadWsNav() will
      // route to loadOverview() and mount the dashboard. Without this
      // guard a workspace switch would race the README fetch against
      // the stats fetch and overwrite the dashboard.
      void loadWsNav();
      // Every mode whose `loadWsNav()` lands on a VIRTUAL page must be
      // excluded here, or the README fetch races that navigation and wins —
      // you select Design, restart, and land on README with the Design button
      // still lit. The guard named only `overview` because it was written
      // when overview was the only such mode; Review and Design inherited the
      // bug on the days they were added (ISS-0040).
      if (!MODES_WITH_VIRTUAL_LANDING.has(currentNavMode) && !pendingCrossRepoJump) void navigateTo('README.md');
      // A cross-repo jump parked here while the workspace switched
      // (FEAT-0093). Consumed before the default landing so the reader ends
      // up at the note they clicked rather than on this workspace's overview.
      if (pendingCrossRepoJump) {
        const jump = pendingCrossRepoJump;
        pendingCrossRepoJump = null;
        void locateAndOpen(jump.noteId, jump.project);
      }
      void renderInboxPanel();
      // ISS-0149: the badges' own refresh bails on `!sidecarBaseUrl`, and on a
      // fresh window `setNavMode` runs from stored state before any sidecar
      // exists — so without this call every view button stays bare until the
      // first mode click. Since FEAT-0092 the badge is the way INTO each
      // view's landing page, which makes a blank one the entry point to the
      // list of what you owe, missing exactly when you open the app to ask.
      void refreshObligationBadges();
      void refreshAgentSnapshot();
      void loadAgentActions();
      void loadAgentRegistry();
      void refreshQueueItems();
      void drainDispatchRequests();
      // Reopen the console if it was open when the app last closed.
      restoreTerminalPanel();
      break;
    }
    case 'failed': {
      const p = ev.payload as SidecarFailedPayload;
      if (p.workspaceId !== activeId) return;
      const tail = p.stderrTail ? `\n${p.stderrTail}` : '';
      showStatus(`Sidecar failed: ${p.reason}${tail}`, 'error');
      setSidecarStatus('failed', `sidecar: failed (${p.reason})`);
      placeholder.hidden = false;
      docView.hidden = true;
      sidecarBaseUrl = null;
      clearValidation();  // the report belongs to a repo no longer on screen
      currentRel = null;
      activeId = null;
      refreshFooterPath();
      refreshFooterAgent();
      renderWorkspaceRail();
      break;
    }
    case 'exited': {
      const p = ev.payload as SidecarExitedPayload;
      if (p.workspaceId !== activeId) return;
      const detail = p.code === 0 ? 'cleanly' : `code ${p.code ?? 'null'}, signal ${p.signal ?? 'null'}`;
      showStatus(`Sidecar exited ${detail}.`);
      setSidecarStatus('exited', `sidecar: exited (${detail})`);
      placeholder.hidden = false;
      docView.hidden = true;
      sidecarBaseUrl = null;
      clearValidation();  // the report belongs to a repo no longer on screen
      currentRel = null;
      activeId = null;
      refreshFooterPath();
      refreshFooterAgent();
      renderWorkspaceRail();
      break;
    }
  }
});

// ----------------------------------------------------------------------
// Centre pane (TASK-0070) — fetch /api/render and mount the HTML.
// ----------------------------------------------------------------------

interface RenderResponse {
  schema_version: number;
  rel_path: string;
  title: string;
  frontmatter: Record<string, unknown>;
  metadata_html: string;
  html: string;
  linked: unknown[];
  backlinks: unknown[];
  produced_by?: {
    session_id: string;
    agent?: string | null;
    started?: string | null;
    total_cost_usd?: number;
  };
  dispatch_history?: Array<{
    id: string; verb?: string; agent?: string; ts: string;
    session_id: string | null; live: boolean; pending?: boolean;
    total_cost_usd?: number;
  }>;
}

// Provenance of the currently open note (FEAT-0025 / TASK-0135) —
// feeds the re-dispatch guard and the provenance line.
let currentNoteId = '';
let currentDispatchHistory: RenderResponse['dispatch_history'] | null = null;
let currentNoteStatus: string | null = null;

// History stack for the centre pane (TASK-0072). Entries are normalised
// docs-rel paths (no leading "docs/", no query). Hash anchors are part
// of the entry — back/forward to the same path with a different anchor
// is intentional.
const HISTORY_LIMIT = 100;
const historyStack: string[] = [];
let historyCursor = -1;

// Per-note scroll preservation (TASK-0073). Keyed by rel-without-frag
// so #anchor jumps inside the same doc don't pollute the saved
// position. Updated on every nav-away.
const scrollPositions = new Map<string, number>();

function stripFragment(rel: string): string {
  const idx = rel.indexOf('#');
  return idx >= 0 ? rel.slice(0, idx) : rel;
}

function noteTypeFromFrontmatter(fm: Record<string, unknown>): string | null {
  const raw = fm.type;
  if (typeof raw !== 'string') return null;
  return raw.replace(/[[\]"]/g, '').trim().toLowerCase() || null;
}

function buildDocHeader(data: RenderResponse, rel: string): HTMLElement {
  const bar = document.createElement('div');
  bar.className = 'doc-header';

  // One row: type icon + ID + path on the left; verb buttons
  // right-aligned with the status chip at the very end.
  const row = document.createElement('div');
  row.className = 'doc-header-row';

  const identity = document.createElement('div');
  identity.className = 'doc-header-identity';
  const noteType = noteTypeFromFrontmatter(data.frontmatter || {});
  appendIf(identity, typeIcon(noteType || undefined, 15));
  const fmId = typeof data.frontmatter?.id === 'string'
    ? (data.frontmatter.id as string) : '';
  if (fmId) {
    const idEl = document.createElement('span');
    idEl.className = 'doc-header-id';
    idEl.textContent = fmId;
    identity.appendChild(idEl);
  }
  const pathEl = document.createElement('button');
  pathEl.type = 'button';
  pathEl.className = 'doc-header-path';
  pathEl.textContent = `docs/${rel}`;
  pathEl.title = 'Click to copy path';
  pathEl.addEventListener('click', () => {
    void copyText(`docs/${rel}`, 'Path copied');
    const orig = pathEl.textContent;
    pathEl.textContent = 'copied';
    setTimeout(() => { pathEl.textContent = orig; }, 800);
  });
  identity.appendChild(pathEl);
  row.appendChild(identity);

  const right = document.createElement('div');
  right.className = 'doc-header-right';
  const dispatchId = fmId && isDispatchableId(fmId) ? fmId.toUpperCase() : null;
  if (dispatchId) {
    const verbs = verbsForId(dispatchId, {
      type: noteType, status: currentNoteStatus,
    });
    for (const verb of verbs) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'doc-header-verb' + (verb.default ? ' is-default' : '');
      btn.textContent = verb.default ? `▶ ${verb.label}` : verb.label;
      btn.title = `${verb.label} ${dispatchId} with the agent`;
      btn.addEventListener('click', () => {
        void dispatchToAgent(dispatchId, rel, undefined, verb.key);
      });
      right.appendChild(btn);
    }
  }
  // `Start acceptance run` — DES-0006's second entry point, on the feature
  // note itself, "for accepting anything on demand, opted-in or not". The
  // queue entry is the other one (TASK-0290).
  if (noteType === 'feature' && fmId) {
    const run = document.createElement('button');
    run.type = 'button';
    run.className = 'doc-header-verb';
    const requested =
      String((data.frontmatter as Record<string, unknown> | undefined)?.acceptance ?? '')
        .trim().toLowerCase() === 'requested';
    run.textContent = requested ? '▶ Accept…' : 'Accept…';
    run.title = requested
      ? `${fmId} has requested acceptance — walk its criteria`
      : `Walk ${fmId}'s acceptance criteria (it has not requested acceptance)`;
    run.addEventListener('click', () => {
      void navigateTo(`~accept/${fmId.toUpperCase()}`);
    });
    right.appendChild(run);
  }
  appendIf(right, statusChip(currentNoteStatus || undefined));
  if (right.childElementCount > 0) row.appendChild(right);
  bar.appendChild(row);
  return bar;
}

async function navigateTo(
  rel: string,
  opts: { replace?: boolean; fromHistory?: boolean } = {},
): Promise<void> {
  await navigateToInner(rel, opts);
  renderCenterTabs();
}

async function navigateToInner(
  rel: string,
  opts: { replace?: boolean; fromHistory?: boolean } = {},
): Promise<void> {
  if (!sidecarBaseUrl) return;
  // Capture the current scroll position before we replace innerHTML;
  // back / forward restore from this map.
  if (currentRel) {
    scrollPositions.set(stripFragment(currentRel), docView.scrollTop);
  }
  // Strip any leading "/docs/" — the API accepts both forms but
  // keeping `currentRel` canonical simplifies history.
  let normalised = rel.replace(/^\/+/, '');
  if (normalised.startsWith('docs/')) normalised = normalised.slice('docs/'.length);
  normalised = normalised.split('?')[0];
  // Virtual pages (TASK-0127/0130): `~overview[/PHASE-…]` and
  // `~session/<id>` render synthesized pages instead of fetching
  // /api/render — with real history entries so back/forward work.
  if (normalised === '~overview' || normalised.startsWith('~overview/')) {
    const scopeId = normalised.startsWith('~overview/')
      ? normalised.slice('~overview/'.length).toUpperCase()
      : null;
    const target = scopeId ? `~overview/${scopeId}` : '~overview';
    const ok = await renderOverviewPage(scopeId);
    if (ok) {
      currentRel = target;
      currentDispatchHistory = null;
      currentNoteStatus = null;
      pushHistory(target, opts.replace ?? false);
      refreshFooterPath();
    }
    return;
  }
  // ~history — the full timeline (FEAT-0052 / TASK-0257). The overview
  // tile is the short version; this is the same grammar, further back.
  if (normalised === '~history' || normalised.startsWith('~history/')) {
    const at = normalised === '~history'
      ? null : normalised.slice('~history/'.length);
    const ok = await renderHistoryPage(at);
    if (ok) {
      currentRel = normalised;
      currentDispatchHistory = null;
      currentNoteStatus = null;
      pushHistory(normalised, opts.replace ?? false);
      refreshFooterPath();
    }
    return;
  }
  // ~tests/<TST>/run — the manual test runner (TASK-0372). It moved off the
  // desk with the register it belongs to; what it WRITES is untouched, and
  // deliberately so — every guard on `/api/notes/test-run` (allow-list, mtime
  // precondition, loopback check) lives server-side, so a renderer change that
  // needed to edit `note_writes.py` would mean this move had gone wrong.
  // Bare `~tests` USED to have no page of its own — "the navigator IS the
  // view" — and selected the mode instead. FEAT-0092 gave it one, and the two
  // could not coexist: `setNavMode('tests')` calls `loadWsNav`, which now
  // navigates to `~tests`, which reached this branch and called `setNavMode`
  // again. **An infinite loop that froze the renderer**, found by clicking the
  // button in the harness — the landing branch below is a hundred lines
  // further down, so it never ran and Tests silently kept the previous view's
  // page. A route claimed twice does not error; it takes whichever claim is
  // written first.
  // ~accept/<FEAT-id> — the acceptance runner (TASK-0288, DES-0006). One
  // criterion at a time, deliberately not a checklist page: a list invites
  // skimming, and the runner's whole value is that each criterion was
  // actually tried.
  if (normalised.startsWith('~accept/')) {
    const featureId = normalised.slice('~accept/'.length).toUpperCase();
    const ok = await renderAcceptanceRun(featureId);
    if (ok) {
      currentRel = normalised;
      currentDispatchHistory = null;
      currentNoteStatus = null;
      pushHistory(normalised, opts.replace ?? false);
      refreshFooterPath();
    }
    return;
  }

  if (normalised.startsWith('~tests/') && normalised.endsWith('/run')) {
    const id = normalised.slice('~tests/'.length, -'/run'.length);
    const ok = await renderTestRunPage(id);
    if (ok) {
      currentRel = normalised;
      currentDispatchHistory = null;
      currentNoteStatus = null;
      pushHistory(normalised, opts.replace ?? false);
      refreshFooterPath();
    }
    return;
  }
  // ~review — the desk (FEAT-0041). `~review` is the queue with nothing
  // selected; `~review/<id>` a proposal/decision; `~review/<TST>/run` a
  // manual test run in progress — that last one now REDIRECTS, because the
  // run route moved and a deep link in someone's history is exactly what a
  // migration is for (the `RETIRED_NAV_MODES` lesson, applied to a route).
  if (normalised.startsWith('~review/') && normalised.endsWith('/run')) {
    const id = normalised.slice('~review/'.length, -'/run'.length);
    await navigateTo(`~tests/${id}/run`, { replace: true });
    return;
  }
  if (normalised === '~review' || normalised.startsWith('~review/')) {
    // No `/run` handling left here — the branch above intercepts it. Keeping
    // the old one as a fallback would leave a second, unreachable copy of the
    // runner's entry point, which is how a "moved" surface stays in two places.
    const target = normalised === '~review'
      ? '' : normalised.slice('~review/'.length);
    const ok = await renderReviewPage(target);
    if (ok) {
      currentRel = normalised;
      currentDispatchHistory = null;
      currentNoteStatus = null;
      pushHistory(normalised, opts.replace ?? false);
      refreshFooterPath();
    }
    return;
  }
  // ~design — the design bench (FEAT-0042 / TASK-0215). `~design` lists the
  // register; `~design/<DES-id>` frames one artifact.
  // ~inbox/<name> frames one item full-size (TASK-0234). Bare ~inbox has no
  // page any more — the left-pane tray is the index — so it just refreshes
  // the tray and leaves the stage alone.
  if (normalised === '~inbox') {
    void renderInboxPanel();
    return;
  }
  if (normalised.startsWith('~inbox/')) {
    const name = decodeURIComponent(normalised.slice('~inbox/'.length));
    currentRel = normalised;
    pushHistory(normalised, opts.replace ?? false);
    await renderInboxItemView(name);
    void renderInboxPanel();
    return;
  }
  // The view landings (FEAT-0092). `~features`, `~issues`, `~tests` — three
  // views that changed the navigator and left the centre pane on whatever you
  // were reading, while their badges counted things the view never gathered.
  if (VIEW_LANDING_RELS.has(normalised)) {
    const ok = await renderViewLanding(normalised.slice(1));
    if (ok) {
      currentRel = normalised;
      currentDispatchHistory = null;
      currentNoteStatus = null;
      pushHistory(normalised, opts.replace ?? false);
      refreshFooterPath();
    }
    return;
  }
  if (normalised === '~design' || normalised.startsWith('~design/')) {
    const target = normalised === '~design'
      ? '' : normalised.slice('~design/'.length);
    const ok = await renderDesignPage(target);
    if (ok) {
      currentRel = normalised;
      currentDispatchHistory = null;
      currentNoteStatus = null;
      pushHistory(normalised, opts.replace ?? false);
      refreshFooterPath();
    }
    return;
  }
  if (normalised.startsWith('~session/')) {
    const ok = await renderSessionDetailPage(normalised.slice('~session/'.length));
    if (ok) {
      currentRel = normalised;
      pushHistory(normalised, opts.replace ?? false);
      refreshFooterPath();
    }
    return;
  }
  if (normalised === '~agents') {
    const ok = await renderAgentsPage();
    if (ok) {
      currentRel = '~agents';
      currentDispatchHistory = null;
      currentNoteStatus = null;
      agentsTabOpen = true;   // pin the fleet tab (TASK-0159)
      docTabChanged = false;  // switching to agents clears the doc dot
      pushHistory('~agents', opts.replace ?? false);
      refreshFooterPath();
    }
    return;
  }
  const fragmentIndex = normalised.indexOf('#');
  const pathOnly = fragmentIndex >= 0 ? normalised.slice(0, fragmentIndex) : normalised;
  const frag = fragmentIndex >= 0 ? normalised.slice(fragmentIndex + 1) : null;

  // `~root/README.md` is a top-level PROJECT file, not the docs note of the
  // same name. It renders through this ordinary path — only the request the
  // server sees differs, because `root/` is what tells it which file is meant
  // (ISS-0037). Handled here rather than as its own virtual-page branch: it
  // really is just a markdown render, and a separate branch would have to
  // duplicate the fragment, history, 404 and error handling below.
  const renderPath = pathOnly.startsWith('~root/')
    ? pathOnly.slice(1)                     // '~root/README.md' -> 'root/README.md'
    : pathOnly;

  let resp: Response;
  try {
    resp = await fetch(
      `${sidecarBaseUrl}/api/render?path=${encodeURIComponent(renderPath)}`,
    );
  } catch (err) {
    showStatus(`Render fetch failed: ${String(err)}`, 'error');
    return;
  }
  if (resp.status === 404) {
    mountPlaceholder(pathOnly);
    pushHistory(normalised, opts.replace ?? false);
    return;
  }
  if (!resp.ok) {
    showStatus(`Render failed: HTTP ${resp.status}`, 'error');
    return;
  }
  const data = (await resp.json()) as RenderResponse;
  // Server-side resolution: `metadata_html` is the pre-resolved
  // metadata strip (TASK-0075). `html` is the rendered body with
  // wikilinks already turned into `<a>` tags. The click handler on
  // #doc-view intercepts links in either section identically.
  docView.innerHTML = (data.metadata_html || '') + data.html;
  docView.classList.remove('overview-pane', 'agents-page',
    'design-page', 'is-design-shell');
  docView.hidden = false;
  placeholder.hidden = true;
  currentRel = normalised;
  lastDocRel = normalised;   // the doc tab points here (TASK-0159)

  // The actuator row (TASK-0281) — drawn from the server's answer for this
  // note's current status, absent when nothing is owed.
  currentNoteId =
    typeof data.frontmatter?.id === 'string' ? (data.frontmatter.id as string) : '';
  void mountActuatorRow(
    typeof data.frontmatter?.id === 'string' ? (data.frontmatter.id as string) : '',
  );
  // The run affordance for a manual test (TASK-0372). Deliberately NOT an
  // entry in the actuator row: that row is `/api/notes/actions`, which is the
  // human-owned STATUS transitions and nothing else (REQ-0026). Starting a run
  // sets no status — the run does, afterwards — so putting it there would put
  // a non-transition in the one place whose whole meaning is transitions.
  void mountTestRunButton(currentNoteId, data.frontmatter || {});

  currentDispatchHistory = data.dispatch_history ?? null;
  currentNoteStatus = typeof data.frontmatter?.status === 'string'
    ? (data.frontmatter.status as string) : null;
  // Design input (TASK-0212): dossiers, mockups and research that shaped
  // this note, linked via the `design:` frontmatter field. Placed above
  // the metadata strip because the question it answers — "why does this
  // look the way it does?" — is asked before the frontmatter's, and
  // because design input is otherwise reachable only by knowing it exists.
  const designStrip = buildDesignStrip(data.frontmatter || {});
  if (designStrip) docView.prepend(designStrip);
  // A design NOTE offers its own artifact. Opening the note and seeing only
  // prose is correct for Markdown and wrong for a design — and without this
  // the render surface had no door into it at all: the only link to
  // ~design/<id> lived inside the register, which nothing pointed to.
  if (noteTypeFromFrontmatter(data.frontmatter || {}) === 'design') {
    if (!designRegister.length) await fetchDesignRegister();
    const banner = buildDesignNoteBanner(normalised);
    if (banner) docView.prepend(banner);
  }
  // Verification panel (TASK-0211) on the scopes that get validated.
  // Appended, not prepended: the note's own words come first, then the
  // evidence that it works.
  const scopeType = noteTypeFromFrontmatter(data.frontmatter || {}) || '';
  const scopeId = typeof data.frontmatter?.id === 'string'
    ? (data.frontmatter.id as string) : '';
  if (scopeId && ['feature', 'phase', 'release'].includes(scopeType)) {
    docView.appendChild(buildVerificationPanel(scopeId));
  }
  // The release gate (TASK-0373). Prepended, unlike the verification panel:
  // "this release is blocked" is not evidence to read after the prose, it is
  // the first thing a release note has to say about itself.
  if (scopeType === 'release') void mountReleaseGate();
  // Doc header bar (FEAT-0026 / TASK-0140): identity + path + verbs.
  docView.prepend(buildDocHeader(data, pathOnly));
  // Dispatch provenance (FEAT-0025 / TASK-0135).
  if (data.dispatch_history && data.dispatch_history.length > 0) {
    const d = data.dispatch_history[0];
    const prov = document.createElement('div');
    prov.className = 'chg-provenance dispatch-provenance';
    const when = d.ts ? new Date(d.ts).toLocaleString() : '';
    const sess = d.pending
      ? 'pending delivery'
      : d.session_id
        ? `session ${d.session_id.slice(0, 8)}${d.live ? ' (live)' : ''}${typeof d.total_cost_usd === 'number' ? ` · $${d.total_cost_usd.toFixed(2)}` : ''}`
        : '';
    prov.textContent = `dispatched ${d.verb ?? 'default'} · ${d.agent ?? 'agent'}${when ? ` · ${when}` : ''}${sess ? ` → ${sess}` : ''}`;
    docView.prepend(prov);
  }
  // CHG provenance (FEAT-0022 / TASK-0126): cockpit-side enrichment,
  // the note file itself is untouched.
  if (data.produced_by) {
    const prov = document.createElement('div');
    prov.className = 'chg-provenance';
    const cost = typeof data.produced_by.total_cost_usd === 'number'
      ? ` · $${data.produced_by.total_cost_usd.toFixed(2)}` : '';
    prov.textContent = `produced by ${data.produced_by.agent || 'agent'} session ${data.produced_by.session_id.slice(0, 8)}${cost}`;
    docView.prepend(prov);
  }
  wireInteractiveCheckboxes();
  wireMetadataStripPersistence();
  applyScrollTarget(pathOnly, frag, opts.fromHistory ?? false);
  pushHistory(normalised, opts.replace ?? false);
  // Highlight the nav row matching the new doc (TASK-0083).
  refreshActiveNavRow();
  // Refresh the right pane against the new doc (TASK-0085).
  void loadRightPane(normalised);
  // Heartbeat the new URL so the cockpit's state snapshot stays
  // accurate (TASK-0086).
  void sendTabState();
  // Update the status footer (TASK-0094).
  refreshFooterPath();
  // Repaint the star — its filled state depends on currentRel.
  paintStar();
}

// ----------------------------------------------------------------------
// Interactive task-list checkboxes (TASK-0074)
// ----------------------------------------------------------------------

// Persist the frontmatter strip's open/collapsed state across navigation
// (FEAT-0015 user request). The server emits `<details class="metadata-strip" open>`
// every render; localStorage remembers the user's last choice so a
// collapse on one note stays collapsed when they navigate to the next.
const METADATA_STRIP_KEY = 'cockpit:metadata-strip-open';

// ----- The actuator row (FEAT-0060 / TASK-0281) -------------------------
//
// DES-0005: an actuator belongs on the thing being actuated. The left pane is
// a selection list and the right a description, so the row sits under the
// note's own metadata strip.
//
// **No vocabulary here.** The server answers `GET /api/notes/actions` with the
// legal moves for this note's *current* status, and this draws what it is
// sent. Removing a transition from `note_writes.HUMAN_TRANSITIONS` removes the
// button with no change to this file — which is the ISS-0023 rule, and what
// makes REQ-0026 enforceable rather than a convention.

interface NoteAction {
  verb: string;
  to: string;
  confirm: boolean;
  disabled: boolean;
  reason: string;
  /** Empty for the generic transition path; a name when this type's verdict
   *  belongs somewhere else (TASK-0375). The renderer reads the FIELD, never
   *  the note type — the one place that knows designs are special is
   *  `note_writes.VERDICT_ENDPOINTS`, and a `type === 'design'` test here
   *  would be that knowledge in a second place. */
  endpoint?: string;
  /** Set only on verdict-routed actions: what this button means to the
   *  endpoint that serves it. Sent by `note_writes.VERDICT_SEMANTICS` rather
   *  than inferred here — deriving `accept` from the verb's name, or from the
   *  tone `confirm` carries, is the status vocabulary leaking into TypeScript
   *  one field at a time. */
  verdict?: string;
  accept?: boolean;
}

// ----- The release gate (TASK-0373) ------------------------------------
//
// `tools/instructions/TESTING.md` has carried the rule since it was written:
// *a release is blocked while any Tier 1/Tier 2 test is unchecked*. Nothing
// had ever rendered it, because no repo had ever instantiated the suite the
// rule reads — 92 test notes across twelve repos, zero tier classification.
//
// The band states the rule in the CONTRACT's words, sent by the server rather
// than written here. A surface that paraphrased the rule would be a second
// statement of it, and the two would drift the first time either was edited.

interface GateItem {
  tier: number; number: string; section: string; area: string; name: string;
}
interface GatePayload {
  exists: boolean; blocked: boolean; rule: string; rel: string;
  blocking: GateItem[];
  counts: Record<string, { total: number; unchecked: number; reconciled?: number }>;
  local_rule?: string;
}

async function mountReleaseGate(): Promise<void> {
  docView.querySelector('.release-gate')?.remove();
  if (!sidecarBaseUrl) return;
  let gate: GatePayload | null = null;
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/acceptance`);
    if (!resp.ok) return;
    gate = ((await resp.json()) as { gate?: GatePayload }).gate ?? null;
  } catch { return; }
  if (!gate) return;

  const band = document.createElement('section');
  band.className = 'release-gate';

  // Three states, and the third is the one that matters. "No suite" must not
  // render as "nothing blocking": that was every repo's situation before this
  // existed, and a gate that reports clear because it has nothing to read is
  // worse than no gate — it is a green light nobody earned.
  if (!gate.exists) {
    band.classList.add('is-unknown');
    band.append(
      gateLine('No acceptance suite in this repo — the gate cannot be evaluated.'),
      gateNote(`Scaffold ${'docs/tests/ACCEPTANCE_TESTS.md'} from `
        + 'docs/__templates__/acceptance-tests.md to turn it on.'),
    );
    docView.prepend(band);
    return;
  }

  const t1 = gate.counts.tier1, t2 = gate.counts.tier2;
  if (!gate.blocked) {
    band.classList.add('is-clear');
    // "every test is checked" is false when one was reconciled instead of
    // walked, and a clear gate is exactly where an overstatement costs most
    // (ISS-0141). Say which kind of settled, or say nothing about kinds.
    const reconciled = (t1?.reconciled ?? 0) + (t2?.reconciled ?? 0);
    band.append(
      gateLine(reconciled
        ? `Release gate clear — every Tier 1 and Tier 2 test is settled, ${reconciled} by reconciliation rather than by being walked.`
        : 'Release gate clear — every Tier 1 and Tier 2 test is checked.'),
      gateNote(`${t1?.total ?? 0} Tier 1 · ${t2?.total ?? 0} Tier 2`),
    );
    docView.prepend(band);
    return;
  }

  band.classList.add('is-blocked');
  const unchecked = (t1?.unchecked ?? 0) + (t2?.unchecked ?? 0);
  band.appendChild(gateLine(
    `Release blocked — ${unchecked} Tier 1/2 test${unchecked === 1 ? '' : 's'} unchecked.`,
  ));
  band.appendChild(gateNote(gate.rule));
  // The contract's sentence blocks on *unchecked*; this repo also settles a
  // check by reconciliation, and the blocked band is exactly where a reader
  // asks why some `[~]` item below is not in the list. Stated beside the rule,
  // never folded into it — found by re-review, which noted the payload carried
  // this and no surface said it.
  if (gate.local_rule) band.appendChild(gateNote(gate.local_rule));

  const list = document.createElement('ul');
  list.className = 'release-gate-list';
  for (const item of gate.blocking) {
    const li = document.createElement('li');
    const tier = document.createElement('span');
    tier.className = 'release-gate-tier mono';
    tier.textContent = `T${item.tier} ${item.number}`;
    const name = document.createElement('span');
    name.textContent = item.name;
    const area = document.createElement('span');
    area.className = 'release-gate-area';
    area.textContent = item.area;
    li.append(tier, name, area);
    li.style.cursor = 'pointer';
    li.addEventListener('click', () => void navigateTo(gate!.rel));
    list.appendChild(li);
  }
  band.appendChild(list);
  docView.prepend(band);
}

function gateLine(text: string): HTMLElement {
  const el = document.createElement('p');
  el.className = 'release-gate-line';
  el.textContent = text;
  return el;
}

function gateNote(text: string): HTMLElement {
  const el = document.createElement('p');
  el.className = 'release-gate-note';
  el.textContent = text;
  return el;
}

/** A `Run ▸` button on a manual test note (TASK-0372).
 *
 *  This is how the stepper starts from the Tests view: the navigator lists the
 *  tests, clicking one opens the note, and the run begins where the test is
 *  written. It replaces the desk row that used to be the only way in.
 *
 *  Shown only when the server says there are steps to walk — the same
 *  `manual_test_steps` parse the runner itself uses, so a button can never
 *  open a stepper with nothing in it. Reading `kind: manual` from the
 *  frontmatter instead would be a second answer to "who runs this", which is
 *  the defect TASK-0371 removed one of.
 */
async function mountTestRunButton(
  noteId: string, frontmatter: Record<string, unknown>,
): Promise<void> {
  docView.querySelector('.note-run')?.remove();
  if (!sidecarBaseUrl || !noteId) return;
  if (String(frontmatter.type || '').toLowerCase().indexOf('test') === -1) return;

  let detail: ReviewDetail | null = null;
  try {
    const resp = await fetch(
      `${sidecarBaseUrl}/api/cockpit/review/${encodeURIComponent(noteId)}`,
    );
    if (!resp.ok) return;
    detail = (await resp.json()) as ReviewDetail;
  } catch { return; }
  const steps = detail?.steps?.length ?? 0;
  if (steps === 0) return;

  const row = document.createElement('div');
  row.className = 'note-actions note-run';
  const label = document.createElement('span');
  label.className = 'note-actions-label';
  label.textContent = 'Verify';
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'note-action-btn is-good';
  btn.textContent = `Run ▸ ${steps} steps`;
  btn.title = detail?.last_run
    ? `last run ${detail.last_run}` : 'never run from here';
  btn.addEventListener('click', () => void navigateTo(`~tests/${noteId}/run`));
  row.append(label, btn);

  const strip = docView.querySelector('details.metadata-strip');
  if (strip && strip.parentElement) {
    strip.parentElement.insertBefore(row, strip.nextSibling);
  } else {
    docView.insertBefore(row, docView.firstChild);
  }
}

async function mountActuatorRow(noteId: string): Promise<void> {
  docView.querySelector('.note-actions')?.remove();
  if (!sidecarBaseUrl || !noteId) return;

  let actions: NoteAction[] = [];
  try {
    const resp = await fetch(
      `${sidecarBaseUrl}/api/notes/actions?id=${encodeURIComponent(noteId)}`,
    );
    if (!resp.ok) return;
    actions = ((await resp.json()) as { actions?: NoteAction[] }).actions ?? [];
  } catch { return; }

  // Hidden entirely when nothing is owed — which is most notes, most of the
  // time. An empty row would be a permanent reminder that there is nothing
  // to do, on every note in the corpus.
  if (actions.length === 0) return;

  const row = document.createElement('div');
  row.className = 'note-actions';
  const label = document.createElement('span');
  label.className = 'note-actions-label';
  label.textContent = 'Owed';
  row.appendChild(label);

  for (const action of actions) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'note-action-btn';
    // Tone comes from `confirm`, not from the verb's name. A forward move
    // reads affirmative; a terminal one reads as something to pause over.
    // Reading the verb string here would put the vocabulary back in the
    // renderer by the back door, one class name at a time.
    btn.classList.add(action.confirm ? 'is-terminal' : 'is-good');
    btn.textContent = action.verb;
    // A button that explains beats a button that vanishes (DES-0005).
    if (action.disabled) {
      btn.disabled = true;
      btn.title = action.reason || 'not available for this note right now';
    } else {
      btn.title = `Sets status: ${action.to}`;
    }
    btn.addEventListener('click', () => {
      void performNoteAction(noteId, action, btn);
    });
    row.appendChild(btn);
  }

  const strip = docView.querySelector('details.metadata-strip');
  if (strip && strip.parentElement) {
    strip.parentElement.insertBefore(row, strip.nextSibling);
  } else {
    docView.insertBefore(row, docView.firstChild);
  }
}

async function performNoteAction(
  noteId: string, action: NoteAction, btn: HTMLButtonElement,
): Promise<void> {
  // One confirmation for terminal moves, none for forward ones: reversing an
  // approve is itself a recorded action, so the cost of a slip is an extra
  // line of history rather than lost work.
  if (action.confirm) {
    const ok = window.confirm(
      `${action.verb} ${noteId}? This sets status: ${action.to}.`,
    );
    if (!ok) return;
  }
  btn.disabled = true;
  if (action.endpoint === '/api/design/verdict') {
    await performDesignVerdict(noteId, action, btn);
    return;
  }
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/notes/transition`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: noteId, to: action.to, actor: 'user:edwin' }),
    });
    const data = (await resp.json()) as { ok?: boolean; error?: string };
    if (!resp.ok || !data.ok) {
      showStatus(data.error || `Transition failed: HTTP ${resp.status}`, 'error');
      btn.disabled = false;
      return;
    }
    showStatus(`${noteId} → ${action.to}`);
    void refreshObligationBadges();
    // No optimistic mutation. The file is the truth: the write lands, the
    // watcher emits, and the note re-renders from disk.
    if (currentRel) void navigateTo(currentRel, { replace: true });
  } catch (err) {
    showStatus(`Transition failed: ${String(err)}`, 'error');
    btn.disabled = false;
  }
}

/** A design's verdict, named to the revision it judged (TASK-0375 / ISS-0056).
 *
 *  The button is the same button, on the same note, from the same table. What
 *  differs is where it posts: `/api/design/verdict` requires a revision and
 *  validates it against the artifact's real git history, so an approval given
 *  to revision 3 cannot silently cover revision 6. The generic transition path
 *  refuses this type outright, so a client that skipped this branch would get
 *  a 403 rather than an unrevisioned accept.
 *
 *  The revision is the artifact's newest, fetched here rather than assumed —
 *  and a **dirty** artifact is refused, because the frame is showing a working
 *  copy no revision covers. That is the same distinction
 *  `design_revisions_payload` exists to report.
 */
async function performDesignVerdict(
  noteId: string, action: NoteAction, btn: HTMLButtonElement,
): Promise<void> {
  try {
    const resp = await fetch(
      `${sidecarBaseUrl}/api/cockpit/design-revisions/${encodeURIComponent(noteId)}`,
    );
    const revs = (await resp.json()) as
      { available?: boolean; dirty?: boolean; revisions?: Array<{ sha: string }> };
    const newest = revs.revisions?.[0]?.sha;
    if (!newest) {
      showStatus(
        'No committed revision of this design to judge — capture one first.',
        'error',
      );
      btn.disabled = false;
      return;
    }
    if (revs.dirty) {
      showStatus(
        'This artifact has uncommitted edits; a verdict would name a revision '
        + 'that is not what you are looking at.',
        'error',
      );
      btn.disabled = false;
      return;
    }
    await postJson(action.endpoint!, {
      id: noteId,
      reviewer: 'user:edwin',
      verdict: action.verdict,
      revision: newest,
      accept: action.accept,
    });
    showStatus(`${noteId} → ${action.to} at ${newest.slice(0, 7)}`);
    void refreshObligationBadges();
    if (currentRel) void navigateTo(currentRel, { replace: true });
  } catch (err) {
    showStatus(`Verdict failed: ${String(err)}`, 'error');
    btn.disabled = false;
  }
}

function wireMetadataStripPersistence(): void {
  const det = docView.querySelector<HTMLDetailsElement>('details.metadata-strip');
  if (!det) return;
  let storedOpen = true;
  try {
    const v = localStorage.getItem(METADATA_STRIP_KEY);
    if (v === '0') storedOpen = false;
  } catch { /* ignore */ }
  det.open = storedOpen;
  det.addEventListener('toggle', () => {
    try { localStorage.setItem(METADATA_STRIP_KEY, det.open ? '1' : '0'); }
    catch { /* ignore */ }
  });
}

/** Headings whose checkboxes are *criteria*, not a planning checklist.
 *
 *  The same distinction the validator draws: REQ-BOXES reads "Acceptance",
 *  PHASE-BOXES reads "Exit Criteria", and PHASE-BOXES deliberately requires
 *  the heading because a phase note carries unrelated checklists elsewhere.
 *  Getting this wrong in the other direction would demand evidence for a
 *  step in someone's Steps list. */
const CRITERIA_HEADINGS = /^(acceptance|exit criteria|acceptance criteria)\b/i;

/** True when this checkbox sits under a criteria heading (TASK-0282). */
function isCriterionBox(box: HTMLInputElement): boolean {
  let node: Element | null = box.closest('ul, ol');
  while (node) {
    const prev: Element | null = node.previousElementSibling;
    if (prev && /^H[1-6]$/.test(prev.tagName)) {
      return CRITERIA_HEADINGS.test((prev.textContent || '').trim());
    }
    node = prev ?? node.parentElement;
    if (node === docView) break;
  }
  return false;
}

/** The criterion's own prose, as it reads **in the source**.
 *
 *  `data-raw` is put here by `renderer._annotate_checkbox_source`, and it is
 *  the only correct answer (ISS-0137). This function used to read the
 *  rendered `textContent`, and the comment above it claimed to mirror
 *  `note_writes._criterion_text` — it mirrored the *rendered* text instead.
 *  Markdown has already eaten the markup by then: `` `x` `` arrives as
 *  `<code>x</code>` whose textContent has no backticks, `[[y]]` as an anchor
 *  with no brackets. The server matches the source line exactly, so every
 *  criterion carrying inline markup was untickable — measured at **26 of
 *  this corpus's 53 open criteria**, each failing only *after* the reader
 *  had typed their evidence.
 *
 *  The textContent path stays as a fallback for a page served by an older
 *  sidecar that does not send the attribute: wrong for marked-up criteria,
 *  which is what it always was, and right for plain ones. */
function criterionTextOf(box: HTMLInputElement): string {
  const raw = box.dataset.raw;
  if (typeof raw === 'string' && raw.trim()) return raw.trim();
  const li = box.closest('li');
  if (!li) return '';
  const clone = li.cloneNode(true) as HTMLElement;
  clone.querySelectorAll('input[type=checkbox], ul, ol').forEach((n) => n.remove());
  return (clone.textContent || '').trim();
}

function wireInteractiveCheckboxes(): void {
  // pymdownx.tasklist with `clickable_checkbox: False` renders the
  // boxes as `disabled` — mode-1 browser view stays read-only. Mode 3
  // enables them by stripping the attribute; the change handler
  // delegates from #doc-view and writes back through the new endpoint.
  const boxes = docView.querySelectorAll<HTMLInputElement>('input[type=checkbox]');
  boxes.forEach((box) => {
    box.removeAttribute('disabled');
    // A criterion is not a to-do (TASK-0282). Ticking one is a claim that
    // something is true, so it takes evidence — REQ-0028's witness, and the
    // shape REQ-BOXES actually reads. Plain checkboxes keep the FEAT-0011
    // toggle; only criteria are intercepted.
    if (box.checked || !isCriterionBox(box)) return;
    box.dataset.criterion = 'true';
    box.addEventListener('click', (ev) => {
      ev.preventDefault();
      ev.stopPropagation();
      openTickPrompt(box);
    });
  });
}

/** Inline evidence field for one criterion (TASK-0282). */
function openTickPrompt(box: HTMLInputElement): void {
  const li = box.closest('li');
  if (!li || li.querySelector('.tick-prompt')) return;
  const criterion = criterionTextOf(box);
  if (!criterion) return;

  const wrap = document.createElement('div');
  wrap.className = 'tick-prompt';
  const field = document.createElement('input');
  field.type = 'text';
  field.className = 'tick-prompt-field';
  field.placeholder = 'what shows this is met?';
  const tick = document.createElement('button');
  tick.type = 'button';
  tick.className = 'note-action-btn is-good';
  tick.textContent = 'Tick';
  const reconcile = document.createElement('button');
  reconcile.type = 'button';
  reconcile.className = 'note-action-btn';
  reconcile.textContent = 'Reconcile…';
  reconcile.title = 'Record why this was not delivered as written';
  const cancel = document.createElement('button');
  cancel.type = 'button';
  cancel.className = 'note-action-btn';
  cancel.textContent = 'Cancel';

  const send = (form: 'tick' | 'reconcile'): void => {
    const text = field.value.trim();
    if (!text) {
      field.placeholder = form === 'tick'
        ? 'evidence is required — what shows this is met?'
        : 'a reason is required — why was this not delivered?';
      field.focus();
      return;
    }
    void submitTick(criterion, form, text, wrap);
  };
  tick.addEventListener('click', () => send('tick'));
  reconcile.addEventListener('click', () => {
    field.placeholder = 'why was this not delivered as written?';
    if (field.value.trim()) send('reconcile'); else field.focus();
  });
  cancel.addEventListener('click', () => wrap.remove());
  field.addEventListener('keydown', (ev) => {
    if (ev.key === 'Enter') send('tick');
    if (ev.key === 'Escape') wrap.remove();
  });

  wrap.append(field, tick, reconcile, cancel);
  li.appendChild(wrap);
  field.focus();
}

async function submitTick(
  criterion: string, form: 'tick' | 'reconcile', text: string, wrap: HTMLElement,
): Promise<void> {
  const noteId = currentNoteId;
  if (!sidecarBaseUrl || !noteId) return;
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/notes/tick`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: noteId,
        criterion,
        evidence: form === 'tick' ? text : '',
        reason: form === 'reconcile' ? text : '',
        actor: 'user:edwin',
      }),
    });
    const data = (await resp.json()) as { ok?: boolean; error?: string };
    if (!resp.ok || !data.ok) {
      // A refusal is never silence (TASK-0282 DoD). A stale mtime in
      // particular means somebody else's edit is on disk, so say so and
      // re-read rather than leaving a field that looks like it worked.
      const stale = (data.error || '').toLowerCase().includes('changed');
      showStatus(
        stale ? 'note changed — reloaded' : (data.error || 'Tick failed'),
        'error',
      );
      wrap.remove();
      if (currentRel) void navigateTo(currentRel, { replace: true });
      return;
    }
    wrap.remove();
    if (currentRel) void navigateTo(currentRel, { replace: true });
  } catch (err) {
    showStatus(`Tick failed: ${String(err)}`, 'error');
    wrap.remove();
  }
}

docView.addEventListener('change', async (e) => {
  const tgt = e.target;
  if (!(tgt instanceof HTMLInputElement)) return;
  if (tgt.type !== 'checkbox') return;
  if (!sidecarBaseUrl || !currentRel) return;

  const all = docView.querySelectorAll('input[type=checkbox]');
  const idx = Array.from(all).indexOf(tgt);
  if (idx < 0) return;

  const pathOnly = stripFragment(currentRel);
  const desired = tgt.checked;
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/notes/check-toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: pathOnly, index: idx, checked: desired }),
    });
    if (!resp.ok) {
      tgt.checked = !desired; // revert optimistic update
      const reason = await resp.text();
      showStatus(`Checkbox toggle failed: ${reason}`, 'error');
      scheduleHide(2500);
    }
  } catch (err) {
    tgt.checked = !desired;
    showStatus(`Checkbox toggle failed: ${String(err)}`, 'error');
    scheduleHide(2500);
  }
});

function applyScrollTarget(
  pathOnly: string,
  frag: string | null,
  fromHistory: boolean,
): void {
  // The browser would scroll to the anchor synchronously after parsing,
  // but we just injected innerHTML — layout hasn't happened yet. Defer
  // to next frame so getBoundingClientRect / scrollIntoView see the
  // laid-out DOM.
  requestAnimationFrame(() => {
    if (frag) {
      try {
        const el = docView.querySelector(`#${CSS.escape(frag)}`);
        if (el) {
          (el as HTMLElement).scrollIntoView({ block: 'start' });
          return;
        }
      } catch {
        /* invalid id — fall through to top */
      }
    }
    if (fromHistory) {
      docView.scrollTop = scrollPositions.get(pathOnly) ?? 0;
    } else {
      docView.scrollTop = 0;
    }
  });
}

function pushHistory(entry: string, replace: boolean): void {
  try { queueMicrotask(refreshHistoryButtons); } catch { /* TDZ on early renders */ }
  if (replace && historyCursor >= 0) {
    historyStack[historyCursor] = entry;
    return;
  }
  // Drop any forward history that's now stale.
  if (historyCursor < historyStack.length - 1) {
    historyStack.length = historyCursor + 1;
  }
  // No-op if the user just clicked the same link.
  if (historyStack[historyCursor] === entry) return;
  historyStack.push(entry);
  // Trim oldest entries if we blow the cap.
  if (historyStack.length > HISTORY_LIMIT) {
    const drop = historyStack.length - HISTORY_LIMIT;
    historyStack.splice(0, drop);
  }
  historyCursor = historyStack.length - 1;
}

function back(): void {
  if (historyCursor <= 0) return;
  historyCursor -= 1;
  // Re-render without pushing onto history; restore scroll from the
  // per-note map.
  const entry = historyStack[historyCursor];
  void navigateTo(entry, { replace: true, fromHistory: true });
}

function forward(): void {
  if (historyCursor >= historyStack.length - 1) return;
  historyCursor += 1;
  const entry = historyStack[historyCursor];
  void navigateTo(entry, { replace: true, fromHistory: true });
}

// Top-bar back / forward / search button wiring + disabled-state sync.
// Imperative ids — these elements live in the window-wide top bar.
const topBarBack   = $<HTMLButtonElement>('#top-bar-back');
const topBarFwd    = $<HTMLButtonElement>('#top-bar-fwd');
const topBarSearch = $<HTMLButtonElement>('#top-bar-search');

function refreshHistoryButtons(): void {
  topBarBack.disabled = historyCursor <= 0;
  topBarFwd.disabled  = historyCursor >= historyStack.length - 1;
}

topBarBack.addEventListener('click',   () => back());
topBarFwd.addEventListener('click',    () => forward());
topBarSearch.addEventListener('click', () => {
  if (quickSwitchEl.hidden) openQuickSwitch();
  else closeQuickSwitch();
});

refreshHistoryButtons();

// ----- Pin / star the current doc (per-workspace localStorage) -------
// Browser cockpit mode 1 uses the same storage shape under
// `project-os-cockpit.cockpit.pinned-paths`; the native shell keys
// per workspace so pins don't leak across projects.

const topBarStar = $<HTMLButtonElement>('#top-bar-star');

function pinnedStorageKey(workspaceId: string): string {
  return `cockpit:pinned:${workspaceId}`;
}

function loadPinned(workspaceId: string): string[] {
  try {
    const raw = localStorage.getItem(pinnedStorageKey(workspaceId));
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed.filter((s) => typeof s === 'string') : [];
  } catch { return []; }
}

function savePinned(workspaceId: string, paths: string[]): void {
  try {
    localStorage.setItem(pinnedStorageKey(workspaceId), JSON.stringify(paths));
  } catch { /* ignore */ }
}

function isPinnedHere(rel: string): boolean {
  if (!activeId) return false;
  return loadPinned(activeId).indexOf(rel) >= 0;
}

function togglePinned(rel: string): boolean {
  if (!activeId) return false;
  const list = loadPinned(activeId);
  const idx = list.indexOf(rel);
  if (idx >= 0) list.splice(idx, 1);
  else list.push(rel);
  savePinned(activeId, list);
  return idx < 0;
}

const STAR_OUTLINE = '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>';

function paintStar(): void {
  const rel = currentRel ? stripFragment(currentRel) : null;
  topBarStar.disabled = !rel;
  if (!rel) {
    topBarStar.setAttribute('aria-pressed', 'false');
    topBarStar.title = 'Pin to Library';
    topBarStar.replaceChildren(makeSvg(STAR_OUTLINE, 14, {}));
    return;
  }
  const pinned = isPinnedHere(rel);
  topBarStar.setAttribute('aria-pressed', pinned ? 'true' : 'false');
  topBarStar.title = pinned ? 'Unpin from Library' : 'Pin to Library';
  topBarStar.replaceChildren(makeSvg(STAR_OUTLINE, 14, {}));
}

topBarStar.addEventListener('click', () => {
  const rel = currentRel ? stripFragment(currentRel) : null;
  if (!rel || !activeId) return;
  togglePinned(rel);
  paintStar();
  // Refresh Library nav if it's currently the active mode — the
  // server returns a Pinned group when we send ?pinned=…
  if (currentNavMode === 'library' && sidecarBaseUrl) void loadWsNav();
});

// Schedule the initial paint after PANEL_LEFT_* constants + makeSvg
// are declared further down the file.
queueMicrotask(paintStar);

// Mouse button 3 (back) / 4 (forward) — common on 5-button mice.
// `mousedown` is more reliable than `auxclick` for these buttons.
document.addEventListener('mousedown', (e) => {
  if (e.button === 3) {
    e.preventDefault();
    back();
  } else if (e.button === 4) {
    e.preventDefault();
    forward();
  }
});

cockpitApi.menu.onBack(() => back());
cockpitApi.menu.onForward(() => forward());

function mountPlaceholder(missing: string): void {
  docView.innerHTML =
    `<h1>No note here</h1>` +
    `<p class="meta">${escapeHtml(missing)} did not resolve to a Markdown file in this workspace.</p>` +
    `<p class="meta">Pick another note (left nav lands in <code>FEAT-0010</code>) or open one from a parent doc.</p>`;
  docView.hidden = false;
  placeholder.hidden = true;
  currentRel = null;
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

// ----------------------------------------------------------------------
// Link interception (TASK-0071)
// ----------------------------------------------------------------------

type LinkClass =
  | { kind: 'docs'; rel: string }
  | { kind: 'fragment'; frag: string }
  | { kind: 'external'; url: string }
  | { kind: 'unknown' };

function classifyLink(href: string): LinkClass {
  if (!href) return { kind: 'unknown' };
  if (href.startsWith('#')) {
    return { kind: 'fragment', frag: href.slice(1) };
  }
  // Resolve relative URLs against the docs root of the active
  // sidecar; the cockpit's wikilink renderer emits anchors like
  // `<a href="/docs/features/foo.md">`.
  const base = sidecarBaseUrl ? sidecarBaseUrl + '/docs/' : 'http://placeholder/';
  let parsed: URL;
  try {
    parsed = new URL(href, base);
  } catch {
    return { kind: 'unknown' };
  }

  if (sidecarBaseUrl) {
    const sidecar = new URL(sidecarBaseUrl);
    if (parsed.host === sidecar.host) {
      // Same origin — only `/docs/*` paths are renderable.
      if (parsed.pathname.startsWith('/docs/')) {
        const rel = parsed.pathname.slice('/docs/'.length) + (parsed.hash || '');
        return { kind: 'docs', rel };
      }
      // Same-origin but a non-renderable route (e.g. /_static/) —
      // let it fall through to external so the user can decide.
    }
  }

  if (parsed.protocol === 'http:' || parsed.protocol === 'https:') {
    return { kind: 'external', url: parsed.href };
  }
  return { kind: 'unknown' };
}

docView.addEventListener('click', (e) => {
  const target = e.target as HTMLElement | null;
  if (!target) return;
  const anchor = target.closest('a') as HTMLAnchorElement | null;
  if (!anchor) return;
  const href = anchor.getAttribute('href');
  if (!href) return;

  const cls = classifyLink(href);

  // Cmd/Ctrl-click forces the system browser even for docs-internal
  // links (the "open in new tab" escape hatch).
  if ((e.metaKey || e.ctrlKey) && cls.kind === 'docs' && sidecarBaseUrl) {
    e.preventDefault();
    const absolute = `${sidecarBaseUrl}/docs/${cls.rel}`;
    void cockpitApi.app.openExternal(absolute);
    return;
  }

  switch (cls.kind) {
    case 'docs':
      e.preventDefault();
      void navigateTo(cls.rel);
      break;
    case 'external':
      e.preventDefault();
      void cockpitApi.app.openExternal(cls.url);
      break;
    case 'fragment': {
      e.preventDefault();
      try {
        const el = docView.querySelector(`#${CSS.escape(cls.frag)}`);
        if (el) (el as HTMLElement).scrollIntoView({ behavior: 'smooth', block: 'start' });
      } catch {
        /* CSS.escape unavailable / invalid id — best-effort skip */
      }
      break;
    }
    case 'unknown':
      e.preventDefault();
      break;
  }
});

// Rescan binding moved to the rail's + button (wsRailAdd). The menu
// item still triggers rescan via `cockpitApi.menu.onRescan` below.

cockpitApi.workspaces.onSwitchTo((ev) => {
  // Notification click (TASK-0087) — switch to the named workspace.
  void openWorkspace(ev.workspaceId);
});

// Fleet validator health (FEAT-0028). Pushed by main whenever any
// workspace's state changes; the initial read primes the rail.
cockpitApi.fleetHealth.onChange((payload) => { applyFleetHealthPayload(payload); });
void cockpitApi.fleetHealth.get()
  .then((payload) => applyFleetHealthPayload(payload))
  .catch(() => { /* older main process — the rail simply shows nothing */ });

cockpitApi.workspaces.onAgentState((ev) => {
  const prev = agentStates.get(ev.workspaceId)?.state;
  noteFinish(ev.workspaceId, prev, ev.payload);
  if (ev.payload) {
    agentStates.set(ev.workspaceId, ev.payload);
  } else {
    agentStates.delete(ev.workspaceId);
  }
  // Repaint only the affected tab so a state change on one
  // workspace doesn't disturb the rest of the strip.
  const li = listEl.querySelector<HTMLLIElement>(`li[data-id="${ev.workspaceId}"]`);
  if (li) {
    const ws = workspaces.find((w) => w.id === ev.workspaceId);
    if (ws) applyAgentStateToSquare(li, ws);
  }
  if (ev.workspaceId === activeId) {
    refreshFooterAgent();
    void refreshAgentSnapshot();
    scheduleAck();  // new alert on the workspace you're looking at
  }
  refreshAttention();
  if (currentRel === '~agents') void renderAgentsPage(true);
});

// ----------------------------------------------------------------------
// Terminal pane (TASK-0063)
// ----------------------------------------------------------------------

// Per-workspace terminal sessions (FEAT-0015 / TASK-0104):
// PTYs live in main, keyed by workspaceId. The xterm in the renderer
// is a single shared instance; switching workspaces re-attaches it
// to the new workspace's PTY (rewriting the buffer with the backlog).
// PTYs persist across switches — they only die on explicit dispose
// or app shutdown, so REPLs / dev servers survive when you flip tabs.

let term: XtermTerminal | null = null;
let fitAddon: XtermFitAddon | null = null;
let attachedTerminalId: string | null = null;
const liveTerminals = new Set<string>();
let terminalListenersWired = false;

const TERMINAL_THEME_DARK = {
  background: '#1b1d1f',
  foreground: '#d6d6d6',
  cursor: '#7da6ff',
  cursorAccent: '#1b1d1f',
  selectionBackground: '#33373b',
  black: '#1b1d1f',  red: '#cc6f6f', green: '#8ab886', yellow: '#d5b878',
  blue: '#7da6ff',  magenta: '#b48ead', cyan: '#86c1b9', white: '#c5c8c6',
  brightBlack: '#5c5f63', brightRed: '#d68a8a', brightGreen: '#a6c898',
  brightYellow: '#e0c895', brightBlue: '#9bb8ff', brightMagenta: '#c8a4c6',
  brightCyan: '#a5d3cc', brightWhite: '#f0f0f0',
};

const TERMINAL_THEME_LIGHT = {
  background: '#ffffff',
  foreground: '#1c1d1f',
  cursor: '#3b6ea8',
  cursorAccent: '#ffffff',
  selectionBackground: '#dfe6ee',
  black: '#1c1d1f',  red: '#b54a4a', green: '#3f7a44', yellow: '#a06c1a',
  blue: '#3b6ea8',  magenta: '#86458a', cyan: '#347a72', white: '#3a3d41',
  brightBlack: '#6b6e73', brightRed: '#c45656', brightGreen: '#4f9656',
  brightYellow: '#b97f2e', brightBlue: '#4d83c2', brightMagenta: '#9a5c9e',
  brightCyan: '#479287', brightWhite: '#1c1d1f',
};

function currentTerminalTheme(): Record<string, string> {
  return document.documentElement.dataset.theme === 'dark'
    ? TERMINAL_THEME_DARK
    : TERMINAL_THEME_LIGHT;
}

function activeWorkspaceCwd(): string | undefined {
  if (!activeId) return undefined;
  const ws = workspaces.find((w) => w.id === activeId);
  return ws?.root;
}

// Wire IPC listeners once. data/exit events come in tagged with
// workspaceId; we filter to the currently-attached one so other
// workspaces' bytes don't leak into the visible xterm.
function wireTerminalListenersOnce(): void {
  if (terminalListenersWired) return;
  terminalListenersWired = true;
  cockpitApi.terminal.onData((ev) => {
    if (!term) return;
    if (ev.workspaceId !== attachedTerminalId) return;
    term.write(ev.data);
  });
  cockpitApi.terminal.onExit((info) => {
    liveTerminals.delete(info.workspaceId);
    if (info.workspaceId !== attachedTerminalId || !term) return;
    term.write(`\r\n\x1b[90m[terminal exited code=${info.exitCode}${info.signal ? ` signal=${info.signal}` : ''}]\x1b[0m\r\n`);
  });
}

// Lazily build the xterm shell. Bytes typed in are routed to whichever
// PTY is currently attached.
function ensureXterm(): void {
  if (term) return;
  term = new Terminal({
    fontFamily: 'ui-monospace, "SF Mono", Menlo, Monaco, Consolas, monospace',
    fontSize: 13,
    theme: currentTerminalTheme(),
    cursorBlink: true,
    scrollback: 5000,
    allowProposedApi: true,
    // xterm selects the word under the cursor on right-click, and on
    // macOS that defaults to ON. With copy-on-select now unconditional
    // (ISS-0080) the two combine badly: right-click selects a word,
    // copy-on-select copies it, and the clipboard you were about to
    // paste is gone — so right-click "copies the current word" and then
    // pastes it back. Reported immediately after ISS-0080 landed.
    //
    // Right-click is the PASTE gesture here. It must not touch the
    // selection at all.
    rightClickSelectsWord: false,
  });
  fitAddon = new FitAddon.FitAddon();
  term.loadAddon(fitAddon);
  term.open(terminalMount);
  fitAddon.fit();

  // Keep xterm's geometry in sync with its container (ISS-0016). Toggling
  // the pane visible (hidden→shown on a view switch), a window/monitor
  // resize, or a divider drag all change the mount's size; without a
  // re-fit xterm keeps a stale row count (the prompt and lines below it
  // clip off-screen under the mount's overflow:hidden) and a stale scroll
  // viewport (mouse-wheel dead until a manual resize). A ResizeObserver
  // catches every case — including the hidden→visible transition, which
  // reports a 0→real size change. rAF-debounced; fit() only resizes xterm
  // *within* the mount, so it can't re-trigger the observer into a loop.
  let fitPending = false;
  const refit = (): void => {
    if (fitPending) return;
    fitPending = true;
    requestAnimationFrame(() => {
      fitPending = false;
      if (terminalPane.hidden) return;
      try { fitAddon?.fit(); } catch { /* xterm not ready yet */ }
    });
  };
  new ResizeObserver(refit).observe(terminalMount);

  term.onData((data) => {
    if (attachedTerminalId) cockpitApi.terminal.write(attachedTerminalId, data);
  });
  term.onResize(({ cols, rows }) => {
    if (attachedTerminalId) cockpitApi.terminal.resize(attachedTerminalId, cols, rows);
  });
  // Copy-on-select (TASK-0167, opt-in) — PuTTY convention for the
  // terminally-inclined.
  term.onSelectionChange(() => {
    if (!copyOnSelect || !term?.hasSelection()) return;
    const s = term.getSelection();
    // Quiet on success — copy-on-select fires constantly and a status
    // line per drag would be noise. A FAILURE still speaks.
    if (s) void cockpitApi.clipboard.write(s).then((r: { ok: boolean; error?: string }) => {
      if (!r.ok) showStatus(`Copy failed: ${r.error ?? 'unknown error'}`, 'error');
    });
  });
  // Terminal context menu (TASK-0167) — xterm's selection isn't a DOM
  // selection, so the native menu can't see it; build our own.
  // Right-click PASTES. The terminal convention (PuTTY, mintty), and it
  // replaces a context menu that did not work for the user across three
  // attempts while ⌘C/⌘V did (ISS-0080). Instrumentation said the menu
  // path wrote to the PTY and held focus — it was measuring a dispatched
  // event, not a real right-click — so this removes the mechanism rather
  // than repairing what could not be reproduced.
  //
  // Always pastes, with no selection-aware mode: a gesture that
  // sometimes copies and sometimes pastes is worse than either, and if
  // you have a selection you have already copied it, because selecting
  // IS the copy.
  terminalMount.addEventListener('contextmenu', (e) => {
    e.preventDefault();
    e.stopPropagation();
    void pasteIntoTerminal();
  });
  wireTerminalListenersOnce();
}

// ----- Terminal context menu + clipboard (TASK-0167) -------------------
// Selecting copies. Formerly an opt-in preference defaulting to OFF,
// which meant "select to copy" was not the behaviour at all unless you
// had found the toggle — half of why the console's clipboard felt
// broken (ISS-0080). It is the convention now, not a setting.
const copyOnSelect = true;

// Multi-line pastes are wrapped in bracketed-paste markers so a shell /
// REPL treats them as one block instead of running each line.
function bracketedPaste(text: string): string {
  return text.includes('\n') ? `\x1b[200~${text}\x1b[201~` : text;
}

async function pasteIntoTerminal(): Promise<void> {
  if (!attachedTerminalId) { showStatus('No console to paste into', 'error'); return; }
  const res = await cockpitApi.clipboard.read();
  if (!res.ok) { showStatus(`Paste failed: ${res.error ?? 'unknown error'}`, 'error'); return; }
  const text = res.text ?? '';
  if (!text) { showStatus('Clipboard is empty', 'error'); return; }
  cockpitApi.terminal.write(attachedTerminalId, bracketedPaste(text));
  // Say so. A paste into a full-screen TUI can be visually ambiguous —
  // the app decides where the text lands — and silence was reported as
  // "paste does not work" when the write had in fact succeeded.
  showStatus(`Pasted ${text.length} character${text.length === 1 ? '' : 's'} into the console`);
  scheduleHide(1200);
}

function copyTerminalSelection(): void {
  const s = term?.hasSelection() ? (term.getSelection() || '') : '';
  void copyText(s, 'Copied from console');
}


// Attach the xterm to a workspace's PTY: spawn it if not yet alive,
// otherwise replay the backlog so the screen resumes in-place.
// Per-workspace mouse-tracking mode (ISS-0016). One xterm is shared across
// workspaces; switching calls term.reset(), which wipes the app's mouse-
// tracking mode, and the raw backlog can't restore it (the enable sequence
// predates the ring buffer). We snapshot the mode when leaving a workspace
// and re-assert it on return so wheel forwarding to a TUI (e.g. Claude Code)
// resumes immediately instead of waiting — maybe forever — for the app to
// redraw. A plain shell stays 'none', so its native scrollback still works.
const workspaceMouseMode = new Map<string, string>();
const MOUSE_TRACK_DECSET: Record<string, string> = {
  x10: '9', vt200: '1000', drag: '1002', any: '1003',
};

async function attachTerminalTo(workspaceId: string): Promise<void> {
  ensureXterm();
  if (!term) return;
  if (attachedTerminalId === workspaceId) return;
  // Snapshot the mouse-tracking mode of the workspace we're leaving, before
  // reset() wipes it, so we can restore it when the user comes back.
  if (attachedTerminalId) {
    workspaceMouseMode.set(attachedTerminalId, term.modes?.mouseTrackingMode || 'none');
  }
  attachedTerminalId = workspaceId;
  term.reset();
  const cwd = workspaces.find((w) => w.id === workspaceId)?.root;
  if (!liveTerminals.has(workspaceId)) {
    const res = await cockpitApi.terminal.spawn({
      workspaceId, cwd, cols: term.cols, rows: term.rows,
    });
    if (!res.ok) {
      term.write(`\x1b[31m[failed to spawn terminal: ${res.error ?? 'unknown'}]\x1b[0m\r\n`);
      return;
    }
    liveTerminals.add(workspaceId);
    return;
  }
  // PTY already running for this workspace — re-attach and replay
  // the captured backlog so the user sees the previous screen.
  const res = await cockpitApi.terminal.attach(workspaceId);
  if (res.ok && res.backlog) term.write(res.backlog);
  // Restore this workspace's mouse-tracking mode (ISS-0016). reset() above
  // wiped it; re-assert it (with SGR encoding, which modern TUIs use) so
  // xterm resumes forwarding wheel events to the app and scrolling works
  // immediately. Written to xterm only — it changes xterm's mode, not the
  // PTY. Skipped for 'none' (plain shells keep native scrollback scroll).
  // Known limitation: if the app exited to a plain shell in this same PTY
  // while we were detached, we'll briefly re-assert the stale tracking mode
  // until the next redraw disables it — recoverable, and rare.
  const savedMode = workspaceMouseMode.get(workspaceId);
  const decset = savedMode ? MOUSE_TRACK_DECSET[savedMode] : undefined;
  if (decset) term.write(`\x1b[?${decset}h\x1b[?1006h`);
  // Re-send our current geometry; main may have lost track if the
  // window resized while detached.
  cockpitApi.terminal.resize(workspaceId, term.cols, term.rows);
}

// Force a genuine terminal resize so the PTY gets a real SIGWINCH and the
// running app (e.g. Claude Code) fully redraws. A workspace switch calls
// `term.reset()` (see attachTerminalTo), which wipes xterm's mode state —
// including mouse-tracking mode — and the replayed backlog does NOT restore
// it (the app's enable sequence predates the backlog window). Until the app
// redraws and re-enables mouse tracking, xterm won't forward wheel events,
// so scrolling is dead — the exact repair a divider drag performs. A
// same-size fit() no-ops (xterm's resize early-returns on identical
// cols/rows), so round-trip rows-1 → true rows to guarantee a real resize
// (ISS-0016). Also rebuilds the scroll viewport / fixes clip on show.
function forceRefitTerminal(): void {
  if (!term || !fitAddon || terminalPane.hidden) return;
  try {
    if (term.rows > 2) term.resize(term.cols, term.rows - 1);
    fitAddon.fit();
  } catch { /* xterm not ready yet */ }
}

// Recover a wedged console (ISS-0017 / TASK-0187): dispose the active
// workspace's PTY — killPty also kills its backing tmux session, so a stuck
// TUI can't survive — clear our per-workspace state, then re-attach, which
// spawns a fresh shell because the workspace is no longer live.
async function restartTerminal(): Promise<void> {
  const wsId = attachedTerminalId ?? activeId;
  if (!wsId || !term) return;
  if (!window.confirm(
    'Restart this console? The current shell (and any process running in it, '
    + 'including a Claude/codex session) will be killed and a fresh shell started.',
  )) return;
  await cockpitApi.terminal.dispose(wsId);
  liveTerminals.delete(wsId);
  workspaceMouseMode.delete(wsId);
  attachedTerminalId = null;
  term.reset();
  await attachTerminalTo(wsId);
  requestAnimationFrame(() => { forceRefitTerminal(); term?.focus(); });
  // attachTerminalTo only adds to liveTerminals on a successful spawn, so
  // it's our signal for whether the fresh shell actually came up.
  if (liveTerminals.has(wsId)) {
    showStatus('Console restarted');
    scheduleHide(2000);
  } else {
    showStatus('Failed to restart console', 'error');
  }
}

// Console panel persistence. The panel is part of how the window is set
// up, not a transient view — reopening it and re-dragging it after every
// restart is the kind of small tax that makes a restart feel expensive.
const TERMINAL_OPEN_KEY = 'cockpit:terminal-open';
const TERMINAL_HEIGHT_KEY = 'cockpit:terminal-height';

function rememberTerminalOpen(open: boolean): void {
  try { localStorage.setItem(TERMINAL_OPEN_KEY, open ? '1' : '0'); }
  catch { /* localStorage unavailable — the panel just won't persist */ }
}

function rememberTerminalHeight(px: number): void {
  try { localStorage.setItem(TERMINAL_HEIGHT_KEY, String(Math.round(px))); }
  catch { /* ignore */ }
}

function storedTerminalHeight(): number | null {
  try {
    const raw = localStorage.getItem(TERMINAL_HEIGHT_KEY);
    if (!raw) return null;
    const px = Number(raw);
    if (!Number.isFinite(px)) return null;
    // Re-clamp on read: the stored height may come from a larger display.
    return Math.min(window.innerHeight - 120, Math.max(80, px));
  } catch { return null; }
}

// Restore once a workspace is live — showTerminal attaches to activeId,
// so restoring before the sidecar is ready would attach to nothing.
let terminalRestored = false;

function restoreTerminalPanel(): void {
  if (terminalRestored) return;
  terminalRestored = true;
  const height = storedTerminalHeight();
  if (height !== null) terminalPane.style.height = `${height}px`;
  let wanted = false;
  try { wanted = localStorage.getItem(TERMINAL_OPEN_KEY) === '1'; }
  catch { /* default closed */ }
  if (wanted && terminalPane.hidden) void showTerminal();
}

async function showTerminal(): Promise<void> {
  terminalPane.hidden = false;
  terminalBtn.classList.add('active');
  // Attach FIRST (a workspace switch resets xterm + replays the backlog),
  // and only THEN force the real resize — otherwise the resize's SIGWINCH
  // races ahead of the reset and the app never gets prompted to re-enable
  // mouse tracking, leaving the wheel dead until a manual drag (ISS-0016).
  if (activeId) await attachTerminalTo(activeId);
  requestAnimationFrame(() => {
    forceRefitTerminal();
    term?.focus();
  });
  scheduleAck();  // terminal now visible — start the seen-timer (TASK-0157)
  rememberTerminalOpen(true);
}

function hideTerminal(): void {
  terminalPane.hidden = true;
  terminalBtn.classList.remove('active');
  rememberTerminalOpen(false);
}

function toggleTerminal(): void {
  if (terminalPane.hidden) showTerminal();
  else hideTerminal();
}

terminalBtn.addEventListener('click', toggleTerminal);
// Cmd+` triggers via the View → Toggle Terminal menu accelerator now;
// kept this listener as a fallback so Cmd+` works even when the
// renderer has focus on a child element that swallowed the accelerator.
document.addEventListener('keydown', (e) => {
  if (e.metaKey && e.key === '`') {
    e.preventDefault();
    toggleTerminal();
  }
  // ⌘C / ⌘V are owned by the Edit menu's accelerators now (TASK-0263).
  // Handling them here as well raced the menu — on macOS the accelerator
  // fires first — which made ⌘V paste twice and ⌘C copy the wrong thing.
});

/** True when the console has focus and should own Copy/Paste. */
function terminalHasFocus(): boolean {
  return !terminalPane.hidden && terminalMount.contains(document.activeElement);
}

// The Edit menu asks; the renderer decides which pane it meant
// (FEAT-0054 / TASK-0263).
cockpitApi.menu.onEdit((ev) => {
  if (ev.action === 'copy') {
    if (terminalHasFocus()) { copyTerminalSelection(); return; }
    const sel = window.getSelection()?.toString() ?? '';
    if (sel) void copyText(sel);
    else showStatus('Nothing selected to copy', 'error');
    return;
  }
  if (ev.action === 'paste') {
    if (terminalHasFocus()) { void pasteIntoTerminal(); return; }
    // A focused input is the document's own business — let the platform
    // insert, which preserves undo history and caret position.
    const el = document.activeElement as HTMLElement | null;
    const editable = el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA'
      || el.isContentEditable);
    if (editable) { document.execCommand('paste'); return; }
    showStatus('Nothing here accepts a paste', 'error');
  }
});

cockpitApi.menu.onRescan(() => { void rescanWorkspaces(); });
cockpitApi.menu.onToggleTerminal(() => { toggleTerminal(); });
cockpitApi.menu.onRestartTerminal(() => { void restartTerminal(); });

cockpitApi.agent.onFocus((payload) => {
  if (!payload || typeof payload !== 'object') return;
  const p = payload as { url?: unknown; target?: unknown };
  const target = typeof p.target === 'string' ? p.target : '?';
  // The URL the server resolves is shaped like `/docs/features/…md`
  // (or `/README.md` for top-level support files); only the former
  // is renderable here.
  const url = typeof p.url === 'string' ? p.url : '';
  const rel = url.startsWith('/docs/') ? url.slice('/docs/'.length) : null;
  // Follow gate (TASK-0158 / REQ-0020): navigate only when this
  // workspace is in Following mode AND the user isn't parked on a
  // virtual page they opened deliberately. Otherwise the jump is
  // offered, never forced.
  // While the fleet is pinned and visible AND this workspace is
  // following, a follow updates the doc tab in the background rather
  // than evicting the fleet (TASK-0159). In Manual mode the focus is
  // ignored (falls through to the actionable toast) — the Manual
  // contract wins over the tab convenience.
  if (rel && isFollowing(activeId) && maybeBackgroundDocNav(rel)) {
    return;
  }
  const onVirtual = !!currentRel && currentRel.startsWith('~');
  const mayFollow = isFollowing(activeId) && !onVirtual;
  if (rel && mayFollow) {
    showStatus(`Agent focus → ${target}`);
    scheduleHide(1500);
    void navigateTo(rel);
  } else if (rel) {
    showActionStatus(`Agent focus → ${target}`, 'open', () => { void navigateTo(rel); });
    scheduleHide(6000);
  } else {
    showStatus(`Agent focus → ${target}`);
    scheduleHide(1500);
  }
});

// Dispatch a doc-pane text selection as an agent prompt (TASK-0168).
cockpitApi.agent.onDispatchSelection((text) => { void dispatchSelectionAsPrompt(text); });

async function dispatchSelectionAsPrompt(text: string): Promise<void> {
  const wsId = activeId;
  const trimmed = (text || '').trim();
  if (!wsId || !trimmed) return;
  const chosen = loadDispatchAgent();
  const preview = trimmed.length > 140 ? `${trimmed.slice(0, 140)}…` : trimmed;
  if (!window.confirm(`Dispatch the selected text to ${chosen}?\n\n${preview}`)) return;
  const item: QueuedDispatch = {
    id: currentFrontmatterId() || 'selection',
    rel: currentRel && !currentRel.startsWith('~') ? currentRel : '',
    agent: chosen,
    prompt: trimmed,
    ts: new Date().toISOString(),
  };
  const freshPty = !liveTerminals.has(wsId);
  showTerminal();
  await new Promise((r) => setTimeout(r, freshPty ? 600 : 150));
  const res = await cockpitApi.dispatch.execute(wsId, item);
  if ('error' in res && res.error) { showStatus(`Dispatch failed: ${res.error}`, 'error'); return; }
  showStatus(res.queued ? 'Queued selection' : `Dispatched selection (${res.delivered})`);
  scheduleHide(2000);
}

cockpitApi.deeplink.onUrl((url) => {
  // cockpit://<workspace-id>/<target>
  showStatus(`Deeplink received: ${url}`);
  scheduleHide(2000);
  try {
    const u = new URL(url);
    const wsId = u.host;
    if (wsId) void openWorkspace(wsId);
  } catch {
    /* malformed URL — already surfaced via showStatus */
  }
});

// Vertical resize via divider drag.
terminalDivider.addEventListener('mousedown', (downEv) => {
  downEv.preventDefault();
  const startY = downEv.clientY;
  const startHeight = terminalPane.getBoundingClientRect().height;
  const onMove = (moveEv: MouseEvent) => {
    const delta = startY - moveEv.clientY;
    const next = Math.min(window.innerHeight - 120, Math.max(80, startHeight + delta));
    terminalPane.style.height = `${next}px`;
  };
  const onUp = () => {
    document.removeEventListener('mousemove', onMove);
    document.removeEventListener('mouseup', onUp);
    try { fitAddon?.fit(); } catch { /* ignore */ }
    rememberTerminalHeight(terminalPane.getBoundingClientRect().height);
  };
  document.addEventListener('mousemove', onMove);
  document.addEventListener('mouseup', onUp);
});

// Window resize → re-clamp a dragged-tall pane so it can't exceed a
// now-smaller window (moving to a smaller screen would otherwise push the
// prompt off the bottom — ISS-0016), then re-fit. The ResizeObserver also
// catches the fit, but the height clamp is a policy the observer can't do.
window.addEventListener('resize', () => {
  if (terminalPane.hidden) return;
  if (terminalPane.style.height) {
    const h = terminalPane.getBoundingClientRect().height;
    terminalPane.style.height =
      `${Math.min(window.innerHeight - 120, Math.max(80, h))}px`;
  }
  try { fitAddon?.fit(); } catch { /* ignore */ }
});

void loadWorkspaces();

// + button on the workspace rail rescans + adds (FEAT-0015 / TASK-0100).
// A full picker overlay is a future follow-up.
// FEAT-0016: rail `+` opens a native directory picker. If the picked
// dir is a project, add it; if it's a parent of projects, scan and
// add all SNAPSHOT-bearing descendants. Auto-discovery is gone.
wsRailAdd.addEventListener('click', () => { void addWorkspaceFlow(); });

// ---- Project settings popover (FEAT-0016 / TASK-0107) ----------------

function openProjectSettings(): void {
  if (!activeId) return;
  const ws = workspaces.find((w) => w.id === activeId);
  if (!ws) return;
  psmName.value = effectiveName(ws);
  psmEmoji.value = ws.userEmoji ?? '';
  refreshSwatchSelection(ws.userColor ?? '');
  projectSettingsMenu.hidden = false;
  projectSettingsBtn.setAttribute('aria-expanded', 'true');
  // Defer focus so the click that opened the menu doesn't blur the
  // input via the document-level click-outside listener.
  setTimeout(() => psmName.focus(), 0);
}

function refreshSwatchSelection(currentColor: string): void {
  psmSwatches.querySelectorAll<HTMLButtonElement>('.psm-swatch').forEach((btn) => {
    btn.classList.toggle('is-active', (btn.dataset.color ?? '') === currentColor);
  });
}

function closeProjectSettings(): void {
  projectSettingsMenu.hidden = true;
  projectSettingsBtn.setAttribute('aria-expanded', 'false');
}

projectSettingsBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  if (projectSettingsMenu.hidden) openProjectSettings();
  else closeProjectSettings();
});

document.addEventListener('click', (e) => {
  if (projectSettingsMenu.hidden) return;
  const t = e.target as Node;
  if (!projectSettingsMenu.contains(t) && t !== projectSettingsBtn) {
    closeProjectSettings();
  }
});

document.addEventListener('keydown', (e) => {
  if (!projectSettingsMenu.hidden && e.key === 'Escape') {
    closeProjectSettings();
    projectSettingsBtn.focus();
  }
});

async function refreshActiveWorkspaceFromMain(): Promise<void> {
  workspaces = await cockpitApi.workspaces.list();
  renderWorkspaceRail();
  const ws = activeId ? workspaces.find((w) => w.id === activeId) : null;
  if (ws) setProjectHeader(ws);
}

// Save the rename on blur or Enter; revert on Escape.
async function commitRename(): Promise<void> {
  if (!activeId) return;
  const ws = workspaces.find((w) => w.id === activeId);
  if (!ws) return;
  const next = psmName.value.trim();
  // If the user cleared the field or typed the auto-derived name back,
  // drop the override so future SNAPSHOT renames take effect again.
  const userName = (next === '' || next === ws.name) ? null : next;
  if ((ws.userName ?? null) === userName) return;
  await cockpitApi.workspaces.update({ id: activeId, userName });
  await refreshActiveWorkspaceFromMain();
}

psmName.addEventListener('blur', () => { void commitRename(); });
psmName.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') { e.preventDefault(); void commitRename().then(closeProjectSettings); }
  else if (e.key === 'Escape') {
    e.preventDefault();
    // Revert to current effective name + close.
    const ws = activeId ? workspaces.find((w) => w.id === activeId) : null;
    if (ws) psmName.value = effectiveName(ws);
    closeProjectSettings();
  }
});

psmPickIcon.addEventListener('click', async () => {
  if (!activeId) return;
  const pick = await cockpitApi.workspaces.pickIcon(activeId);
  if (!pick.ok) {
    if (pick.error && pick.error !== 'cancelled') {
      showStatus(`Icon: ${pick.error}`, 'error');
      scheduleHide(3000);
    }
    return;
  }
  await cockpitApi.workspaces.update({ id: activeId, userIcon: pick.dataUri ?? null });
  await refreshActiveWorkspaceFromMain();
  closeProjectSettings();
});

// Commit the emoji input on blur or Enter. Cleared = revert to icon
// chain. Apply on each input change so the user sees the rail update
// immediately as they type.
async function commitEmoji(): Promise<void> {
  if (!activeId) return;
  const ws = workspaces.find((w) => w.id === activeId);
  if (!ws) return;
  const next = psmEmoji.value.trim();
  const userEmoji = next === '' ? null : next;
  if ((ws.userEmoji ?? null) === userEmoji) return;
  await cockpitApi.workspaces.update({ id: activeId, userEmoji });
  await refreshActiveWorkspaceFromMain();
}

psmEmoji.addEventListener('change', () => { void commitEmoji(); });
psmEmoji.addEventListener('blur',   () => { void commitEmoji(); });
psmEmoji.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') { e.preventDefault(); void commitEmoji(); }
});

// Color swatches.
psmSwatches.addEventListener('click', async (e) => {
  if (!activeId) return;
  const btn = (e.target as HTMLElement).closest<HTMLButtonElement>('.psm-swatch');
  if (!btn) return;
  const next = btn.dataset.color ?? '';
  await cockpitApi.workspaces.update({ id: activeId, userColor: next === '' ? null : next });
  await refreshActiveWorkspaceFromMain();
  refreshSwatchSelection(next);
});

// Reset clears all three overrides (uploaded icon, emoji, colour).
// Display reverts to: auto-probed favicon → identicon (hash colour).
psmResetIcon.addEventListener('click', async () => {
  if (!activeId) return;
  await cockpitApi.workspaces.update({
    id: activeId, userIcon: null, userEmoji: null, userColor: null,
  });
  await refreshActiveWorkspaceFromMain();
  closeProjectSettings();
});

psmReveal.addEventListener('click', () => {
  if (!activeId) return;
  const ws = workspaces.find((w) => w.id === activeId);
  if (!ws) return;
  void cockpitApi.app.revealInFinder(ws.root);
  closeProjectSettings();
});

psmRemove.addEventListener('click', async () => {
  if (!activeId) return;
  const ws = workspaces.find((w) => w.id === activeId);
  if (!ws) return;
  // eslint-disable-next-line no-alert
  const ok = window.confirm(
    `Remove "${effectiveName(ws)}" from the workspace list?\n\nThe project's files are not deleted.`,
  );
  if (!ok) return;
  const idToRemove = activeId;
  await cockpitApi.workspaces.remove(idToRemove);
  // Drop from local state + switch off if it was active.
  workspaces = workspaces.filter((w) => w.id !== idToRemove);
  closeProjectSettings();
  if (workspaces.length > 0) {
    activeId = null;
    void openWorkspace(workspaces[0].id);
  } else {
    activeId = null;
    placeholder.hidden = false;
    docView.hidden = true;
    setProjectHeader(null);
  }
  renderWorkspaceRail();
});

async function addWorkspaceFlow(): Promise<void> {
  wsRailAdd.disabled = true;
  showStatus('Choose a project folder…');
  try {
    const res = await cockpitApi.workspaces.pickAndAdd();
    if (res.cancelled) { hideStatus(); return; }
    if (res.error) {
      showStatus(res.error, 'error');
      scheduleHide(3000);
      return;
    }
    workspaces = res.workspaces;
    renderWorkspaceRail();
    const msg = res.skipped > 0
      ? `Added ${res.added}; skipped ${res.skipped} duplicate${res.skipped === 1 ? '' : 's'}.`
      : `Added ${res.added} project${res.added === 1 ? '' : 's'}.`;
    showStatus(msg);
    scheduleHide(2000);
  } catch (err) {
    showStatus(`Add failed: ${String(err)}`, 'error');
  } finally {
    wsRailAdd.disabled = false;
  }
}

// Tab keyboard shortcuts (FEAT-0014 / TASK-0097): Cmd/Ctrl+1..9 jumps
// to the Nth tab, Cmd+W closes the active tab.
document.addEventListener('keydown', (e) => {
  const meta = e.metaKey || e.ctrlKey;
  if (!meta) return;
  if (e.key >= '1' && e.key <= '9') {
    const idx = parseInt(e.key, 10) - 1;
    const ws = workspaces[idx];
    if (ws) {
      e.preventDefault();
      void openWorkspace(ws.id);
    }
    return;
  }
  if (e.key === 'w' || e.key === 'W') {
    if (activeId) {
      e.preventDefault();
      closeWorkspace(activeId);
    }
  }
});

// ----------------------------------------------------------------------
// In-workspace nav (FEAT-0010 / TASK-0083)
// ----------------------------------------------------------------------

interface NavItem {
  id?: string;
  title?: string;
  status?: string;
  url?: string;
  subtitle?: string;
  type?: string;
  children?: NavItem[];
  /** Set by the group when every item shares one status, so the head can
   *  say it once instead of every row repeating it (TASK-0272). Client
   *  state, never sent by the server. */
  chipSuppressed?: boolean;
}

interface NavGroupData {
  key?: string;
  label?: string;
  url?: string;
  status?: string;
  items?: NavItem[];
  item_layout?: string;          // 'stacked' | 'compact' | default
  subgroups?: NavGroupData[];
  default_open?: boolean;
}

interface NavPayload {
  schema_version: number;
  mode: string;
  platform: string;
  available_platforms?: string[];
  groups?: NavGroupData[];
}

// Order matters and is asserted. The strip encodes KINDS of thing —
// state · design · structure ×3 · queue · record — and design sits upstream
// of structure: what it should be, before what is being built. This reverses
// a two-day-old decision that six modes was the ceiling (taken when Active and
// Recent were retired for Review); reversing it deliberately is fine, drifting
// past it would not be.
// TASK-0371 inserts `tests` after `issues`: it is the third structural view —
// what we build, what is wrong with it, what proves it — and it must sit
// before `review`, because the desk is what it is taking the register from.
const NAV_MODES = ['overview', 'intent', 'features', 'tasks', 'issues', 'tests', 'review', 'active', 'library', 'recent'] as const;
type NavMode = typeof NAV_MODES[number];

// Statuses that count as "completed" for the hide-completed filter.
// Mirror of cockpit.js COMPLETED_STATUSES (itself derived from
// statuses.py COMPLETED_STATUSES) so the desktop renderer matches the
// browser cockpit's idea of "done".
//
// `implemented` is terminal since ADR-0007 (it is the requirement's final
// status; `verified` was retired). The non-terminal delivered band —
// `staged`, `monitoring` — is deliberately absent: that work is shipped but
// not signed off and must stay visible when completed items are hidden.
const COMPLETED_STATUSES = new Set([
  'done', 'merged', 'fixed', 'resolved', 'fulfilled', 'met', 'complete',
  'implemented', 'verified', 'passing', 'published', 'released', 'closed',
  'obsolete', 'retired', 'cancelled', 'superseded',
  'declined', 'reverted', 'deprecated', 'reconciled',
]);

let hideCompleted = false;
try { hideCompleted = localStorage.getItem('cockpit:hide-completed') === '1'; }
catch { /* ignore */ }

// ----- Follow mode (FEAT-0034 / TASK-0158) -----------------------------
// Per-workspace: whether the centre pane follows agent `cockpit focus`
// events. Default following (matches mode-1). Even when following, a
// deliberately-opened virtual page (~agents/~overview/~session) is never
// evicted (REQ-0020) — the suppressed jump stays available via a
// clickable toast.
function followKey(wsId: string): string { return `cockpit:follow:${wsId}`; }
function isFollowing(wsId: string | null): boolean {
  if (!wsId) return true;
  try { return localStorage.getItem(followKey(wsId)) !== 'manual'; }
  catch { return true; }
}
function setFollowing(wsId: string, following: boolean): void {
  try { localStorage.setItem(followKey(wsId), following ? 'following' : 'manual'); }
  catch { /* storage unavailable — mode resets next launch */ }
}
function refreshFollowButton(): void {
  if (!followBtn) return;
  const following = isFollowing(activeId);
  followBtn.setAttribute('aria-pressed', following ? 'true' : 'false');
  followBtn.title = following
    ? 'Following agent navigation (click for Manual)'
    : 'Manual — ignoring agent navigation (click to Follow)';
}

// Ids of docs notes the active session is touching — drives the nav
// "agent" chip (TASK-0164). Derived from the session's docs_notes.
const sessionTouchedIds = new Set<string>();
// Numbered types stop at the numeric id (FEAT-0034, not the slug that
// follows); CHG ids are the full dated slug.
const ID_RE = /((?:TASK|ISS|FEAT|REQ|PHASE|RISK|TST|ADR)-\d+|CHG-[0-9A-Za-z-]+)/;
function refreshSessionTouched(): void {
  sessionTouchedIds.clear();
  const s = lastAgentSnap?.session ?? lastAgentSnap?.last_session;
  const notes = s?.work_notes ?? s?.docs_notes ?? [];
  for (const n of notes) {
    const m = String(n).match(ID_RE);
    if (m) sessionTouchedIds.add(m[1]);
  }
}

// Live-migrate the Active nav mode on a status transition (TASK-0164):
// reload the mode so the row moves to its new group, then flash it.
function handleStatusChange(c: { id?: string; to?: string; from?: string; ts?: string; title?: string; type?: string }): void {
  if (currentNavMode === 'active' && sidecarBaseUrl) {
    void loadWsNav().then(() => { if (c.id) flashNavItem(c.id); });
  }
  // Phase-less Now board live-migration (TASK-0165).
  const board = docView.querySelector<HTMLElement>('.now-board');
  if (board && currentRel && currentRel.startsWith('~overview')) {
    void fillNowBoard(board).then(() => {
      if (!c.id) return;
      const card = board.querySelector<HTMLElement>(`.now-card-item[data-id="${CSS.escape(c.id)}"]`);
      if (card) {
        card.classList.add('now-card-flash');
        window.setTimeout(() => card.classList.remove('now-card-flash'), 1600);
      }
    });
  }
  noteWorkTransition(c);  // session "work" tab (TASK-0163)
}

function flashNavItem(id: string): void {
  const li = wsNavContent.querySelector<HTMLElement>(`li[data-id="${CSS.escape(id)}"]`);
  if (!li) return;
  li.classList.add('nav-status-flash');
  window.setTimeout(() => li.classList.remove('nav-status-flash'), 1600);
}

// ----- Centre tabs: doc + pinned Agents (FEAT-0034 / TASK-0159) --------
// A two-tab strip appears only while the Agents fleet is pinned open.
// The doc tab holds the last real note; follow/agent navigation updates
// it in the background (a dot) without leaving the fleet view.
const centerTabs = document.getElementById('center-tabs') as HTMLDivElement | null;
let agentsTabOpen = false;
let lastDocRel: string | null = null;
let docTabChanged = false;

function docTabLabel(): string {
  if (!lastDocRel) return 'Doc';
  const m = lastDocRel.match(/(?:^|\/)((?:TASK|ISS|FEAT|REQ|PHASE|RISK|CHG|ADR|TST)-[0-9A-Za-z-]+)/);
  if (m) return m[1].split('-').slice(0, 2).join('-');
  const base = lastDocRel.split('/').pop() || lastDocRel;
  return base.replace(/\.md$/, '');
}

function renderCenterTabs(): void {
  if (!centerTabs) return;
  if (!agentsTabOpen) { centerTabs.hidden = true; centerTabs.replaceChildren(); return; }
  centerTabs.hidden = false;
  centerTabs.replaceChildren();
  const onAgents = currentRel === '~agents';

  const docTab = document.createElement('button');
  docTab.type = 'button';
  docTab.className = 'center-tab' + (onAgents ? '' : ' on');
  docTab.setAttribute('role', 'tab');
  docTab.setAttribute('aria-selected', onAgents ? 'false' : 'true');
  docTab.textContent = docTabLabel();
  if (docTabChanged && onAgents) {
    const dot = document.createElement('span');
    dot.className = 'center-tab-dot';
    dot.title = 'updated in the background';
    docTab.appendChild(dot);
  }
  docTab.addEventListener('click', () => {
    docTabChanged = false;
    if (lastDocRel) void navigateTo(lastDocRel);
    else void navigateTo('~overview');
  });

  const agentsTab = document.createElement('button');
  agentsTab.type = 'button';
  agentsTab.className = 'center-tab' + (onAgents ? ' on' : '');
  agentsTab.setAttribute('role', 'tab');
  agentsTab.setAttribute('aria-selected', onAgents ? 'true' : 'false');
  const label = document.createElement('span');
  label.textContent = 'Agents';
  agentsTab.appendChild(label);
  const close = document.createElement('span');
  close.className = 'center-tab-close';
  close.textContent = '×';
  close.title = 'Close Agents tab';
  close.setAttribute('role', 'button');
  close.addEventListener('click', (e) => { e.stopPropagation(); closeAgentsTab(); });
  agentsTab.appendChild(close);
  agentsTab.addEventListener('click', () => { if (currentRel !== '~agents') void navigateTo('~agents'); });

  centerTabs.append(docTab, agentsTab);
}

function closeAgentsTab(): void {
  agentsTabOpen = false;
  renderCenterTabs();
  if (currentRel === '~agents') {
    if (lastDocRel) void navigateTo(lastDocRel);
    else void navigateTo('~overview');
  }
}

// Follow/agent navigation targeting a doc while the fleet is pinned and
// visible updates the doc tab in the background instead of evicting the
// fleet (TASK-0159). Returns true if it consumed the navigation.
function maybeBackgroundDocNav(rel: string): boolean {
  if (agentsTabOpen && currentRel === '~agents') {
    lastDocRel = rel;
    docTabChanged = true;
    renderCenterTabs();
    return true;
  }
  return false;
}

function isCompletedStatus(status: string | undefined): boolean {
  if (!status) return false;
  return COMPLETED_STATUSES.has(String(status).toLowerCase());
}

// `isItemHidden` lived here until TASK-0270. Nothing removes an item by
// status any more: the switch collapses, and `foldGroup` is the only
// thing that decides how much of a group renders.

/** How many rows a nav group shows before folding — VOLUME, not status.
 *
 *  Chosen from the measured distribution rather than guessed. Group sizes
 *  in this corpus:
 *
 *    tasks       261, 3, 2, 2, 2
 *    issues       52, 18, 11, 2, 1, 1, 1
 *    features     19, 10, 5, 3, 2, 2, 2, 2, 2, then nine 1s
 *
 *  There is a clean cliff. Twelve folds the four groups that are
 *  genuinely unreadable (261, 52, 19, 18) and leaves the other twenty-six
 *  whole.
 *
 *  An earlier version justified it as "just above 11, the largest context
 *  group anywhere" — that was 11 measured on ONE note. Swept across the
 *  corpus, 11 of 3192 context groups exceed 12 and the largest real one
 *  is 79. The number survives; the reasoning for it did not. */
const NAV_GROUP_FOLD_LIMIT = 12;

/** The same rule in the context pane, and the same number.
 *
 *  One constant rather than two that can disagree: "how many rows is too
 *  many to read" does not depend on which pane you are reading. Swept
 *  across the corpus, 11 of 3192 context groups exceed it — the fold is
 *  rare here, which is what a length threshold should be. */
const CONTEXT_GROUP_FOLD_LIMIT = NAV_GROUP_FOLD_LIMIT;

// Modes with a button in the top bar. `active` and `recent` stay in
// NAV_MODES — the server still serves them and the Now board and strip
// still consume `mode=active` — but they lost their buttons in
// TASK-0204, so a stored preference pointing at one must migrate or the
// user lands in a mode they cannot see is selected and cannot leave by
// clicking the (now absent) button.
// Modes whose `loadWsNav()` routes to a virtual page rather than a note.
// Anything listed here must NOT be sent to README.md on workspace open.
// `review` left this set with its button (TASK-0378). The route is still
// served — the record column links to it while the agent ledger has open
// entries — but nobody LANDS there any more, so it must not claim a
// workspace-open landing.
const MODES_WITH_VIRTUAL_LANDING: ReadonlySet<string> = new Set([
  // FEAT-0092 widened this from `{overview, intent}`. Those two had a landing
  // because FEAT-0071 and FEAT-0087 each built one for their own reasons; the
  // other four sent the reader to README.md and left their badges pointing at
  // nothing a view gathered. The Library keeps no landing deliberately — it
  // owes nothing and is a file browser, and a summary in front of a tree is
  // the thing people open the tree to avoid.
  'overview', 'intent', 'features', 'issues', 'tests',
]);

const RETIRED_NAV_MODES: readonly string[] = ['active', 'recent', 'inbox', 'tasks', 'review', 'design'];
const RETIRED_MODE_FALLBACK: Record<string, NavMode> = {
  active: 'overview',   // in-flight work is ambient on the overview now
  recent: 'overview',   // "what changed" is the commits panel
  // TASK-0234: the inbox became a left-pane tray. Anyone whose stored mode
  // still says 'inbox' would otherwise land in a mode with no button and no
  // way out, which is exactly the trap RETIRED_NAV_MODES exists to prevent.
  inbox: 'overview',
  // TASK-0368: tasks now hang under the feature they serve (TASK-0366), so
  // the flat status list has nothing left to show that Features does not.
  // The server mode stays served — see `_tasks_groups` — but nobody lands here.
  tasks: 'features',
  // TASK-0378: the desk dissolved (ADR-0020). Every register and queue group
  // re-homed to the view that owns its subject, and the "am I done" count
  // became the badges on the view buttons — so `overview` is where somebody
  // whose stored mode says `review` actually wanted to be.
  review: 'overview',
  // TASK-0385: the view is called Intent — the name Edwin agreed, which the
  // obligation registry has used since FEAT-0089 while the nav kept the
  // inherited `design`. Anyone whose stored preference still says `design`
  // is migrated here rather than dropped into the features fallback.
  design: 'intent',
};

function loadStoredNavMode(): NavMode {
  try {
    const v = localStorage.getItem('cockpit:nav-mode');
    if (v && RETIRED_NAV_MODES.includes(v)) {
      const fallback = RETIRED_MODE_FALLBACK[v] ?? 'features';
      try { localStorage.setItem('cockpit:nav-mode', fallback); } catch { /* ignore */ }
      return fallback;
    }
    if (v && (NAV_MODES as readonly string[]).includes(v)) return v as NavMode;
  } catch { /* localStorage unavailable */ }
  return 'features';
}

let currentNavMode: NavMode = loadStoredNavMode();

function setNavMode(mode: NavMode): void {
  currentNavMode = mode;
  try { localStorage.setItem('cockpit:nav-mode', mode); } catch { /* ignore */ }
  refreshNavModeButtons();
  void refreshObligationBadges();
  if (sidecarBaseUrl) void loadWsNav();
}

// ----- Obligation badges (FEAT-0089 / TASK-0370) -----------------------
//
// ADR-0020 decision 3: the count lives on the view button, and the badges
// together must cover **every** obligation kind. That replaces the desk's one
// number with something continuous — you learn what is owed without visiting
// a page to ask.
//
// Absent, never zero. A permanent `0` is the shape of thing a reader learns to
// stop seeing, and this surface has been taught that lesson twice already.

async function refreshObligationBadges(): Promise<void> {
  if (!sidecarBaseUrl) return;
  let views: Record<string, number> = {};
  let breakdown: Record<string, Record<string, number>> = {};
  let verbs: Record<string, string> = {};
  let nouns: Record<string, string[]> = {};
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/obligations`);
    if (!resp.ok) return;
    const payload = (await resp.json()) as {
      views?: Record<string, number>;
      breakdown?: Record<string, Record<string, number>>;
      verbs?: Record<string, string>;
      nouns?: Record<string, string[]>;
    };
    views = payload.views ?? {};
    breakdown = payload.breakdown ?? {};
    verbs = payload.verbs ?? {};
    nouns = payload.nouns ?? {};
  } catch { return; }

  // The registry's view names are the server's; the buttons' `data-mode`
  // values are this renderer's. One mapping, here, rather than the server
  // learning about `design` or the renderer learning about obligations.
  const MODE_FOR_VIEW: Record<string, string> = {
    overview: 'overview',
    intent: 'intent',     // TASK-0385: it answers to its own name now
    features: 'features',
    issues: 'issues',
    tests: 'tests',
  };

  document.querySelectorAll<HTMLElement>('.top-bar-btn[data-mode]').forEach((btn) => {
    btn.querySelector('.mode-badge')?.remove();
    const mode = btn.getAttribute('data-mode') || '';
    const view = Object.keys(MODE_FOR_VIEW).find((v) => MODE_FOR_VIEW[v] === mode);
    // The button's own description, kept once so repeated refreshes compose
    // against the original rather than against last refresh's sentence.
    if (btn.dataset.baseTitle === undefined) btn.dataset.baseTitle = btn.title || '';
    const base = btn.dataset.baseTitle || '';
    // Reset before the early return, so a view whose count has just dropped to
    // zero loses last refresh's sentence instead of keeping it as a tooltip
    // describing work that is no longer owed.
    btn.title = base;
    btn.removeAttribute('aria-label');
    const n = view ? (views[view] ?? 0) : 0;
    if (n <= 0) return;

    // ISS-0133: say WHAT is owed, not that something is. The old string was
    // `N items here need a person` under every view — the same sentence for
    // requirements to approve, changes to review and issues to triage, which
    // told the reader only that the number was not decoration. The kinds and
    // their verbs are registry data (ADR-0020 decision 3 made them so), and
    // the badge was the one surface not using them.
    const kinds = (view && breakdown[view]) || {};
    const parts = Object.entries(kinds)
      .sort((a, b) => b[1] - a[1])
      .map(([kind, count]) => {
        const verb = (verbs[kind] || '').toLowerCase();
        // The noun ships from the registry (TASK-0357). Falling back to the
        // bare kind keeps a new kind readable on an old renderer rather than
        // reintroducing a plural rule here to cover it.
        const pair = nouns[kind] || [];
        const noun = (count === 1 ? pair[0] : pair[1]) || kind;
        return verb ? `${count} ${noun} to ${verb}` : `${count} ${noun}`;
      });
    const owed = parts.length ? parts.join(', ') : `${n} waiting on you`;

    const badge = document.createElement('span');
    badge.className = 'mode-badge';
    badge.textContent = String(n);
    btn.appendChild(badge);
    // On the BUTTON, not the badge (ISS-0133): the badge is ~14px and was the
    // only hover target, while the review badge already titled its button —
    // two hover behaviours for one control. Hovering anywhere on the button
    // now answers the question the number raises.
    btn.title = base ? `${base}\n${owed}` : owed;
    btn.setAttribute('aria-label', base ? `${base} — ${owed}` : owed);
  });
}

function refreshNavModeButtons(): void {
  // Mode icons live in the window-wide top bar (FEAT-0015 it. 2).
  document.querySelectorAll<HTMLButtonElement>('.top-bar-btn[data-mode]').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.mode === currentNavMode);
  });
}

// ----- Overview dashboard (FEAT-0017 / TASK-0110) --------------------

interface StatsHero {
  features: { total: number; done: number };
  tasks:    { total: number; done: number };
  issues:   { total: number; open: number };
  tests:    { total: number; passing: number };
  risks:    { total: number; open: number };
  requirements?: { total: number; done: number };
  last_change?: { id?: string; title: string; rel: string; date: string } | null;
}
interface PhaseItem {
  id?: string; title: string; rel?: string;
  status: string; bucket: 'done' | 'in_progress' | 'backlog';
  type: string;
  severity?: string;              // issues only (TASK-0199)
  // DES-0004. `state` is the square's encoding; `bucket` stays because the
  // mix bars and progress fractions read it. `attn` composes with any state,
  // because STATUSES.md allows blocked-while-doing.
  state?: 'delivered' | 'dropped' | 'deferred' | 'doing' | 'unproven' | null;
  attn?: boolean;
}
interface PhaseFeature extends PhaseItem { children: PhaseItem[] }
interface StatsPhase {
  key: string; title: string; status: string | null; rel?: string | null;
  tasks: { done: number; in_progress: number; backlog: number };
  // Phase-header markers (DES-0004): what no square can carry.
  waiting?: number;               // items here needing a human — count, not ids
  unclosed?: boolean;             // every item resolved, phase not closed
  features: PhaseFeature[];
  loose: PhaseItem[];
}
interface StatsRecent { id?: string; title: string; rel: string; date: string; type?: string; features?: string[] }

// SNAPSHOT focus block (TASK-0199). Slots resolve against the index; a
// slot pointing at a deleted note degrades to `{id}` alone.
interface FocusItem {
  id: string; title?: string; status?: string; type?: string;
  rel?: string; done?: boolean;
}
interface FocusBlock {
  items: Partial<Record<'task' | 'feature' | 'phase' | 'issue' | 'requirement', FocusItem>>;
  note: string;
  note_date: string;
}

// One commit as a documentation event (TASK-0199).
interface CommitItem {
  id: string; title: string; rel: string; type: string;
  status: string; done: boolean;
}
interface CommitRow {
  sha: string; full_sha: string; date: string; subject: string;
  author: string; items: CommitItem[]; undocumented: boolean;
}
interface CommitsPayload {
  schema_version: number; available: boolean; commits: CommitRow[];
}

interface StatsPayload {
  schema_version: number;
  scope?: { id: string; title: string; status: string; rel: string } | null;
  exit_criteria?: Array<{ text: string; done: boolean }> | null;
  focus?: FocusBlock | null;
  hero: StatsHero;
  phases: StatsPhase[];
  status_mix: Record<string, Record<string, number>>;
  status_buckets?: Record<string, MixBuckets>;
  activity: {
    weekly: Array<{ week_iso: string; start_date: string; count: number }>;
    recent: StatsRecent[];
  };
}

// Current Overview scope (FEAT-0023): null = whole project, else a
// PHASE-#### id. The scope list for the left pane is cached from the
// last unscoped payload (server-side stats cache makes refetch cheap).
let overviewScope: string | null = null;
// Completed band starts closed — finished phases are history until asked for,
// the same default the centre-pane accordion uses.
let scopeCompletedOpen = (() => {
  try { return localStorage.getItem('cockpit:scope-completed-open') === '1'; }
  catch { return false; }
})();
let scopePhaseList: StatsPhase[] | null = null;

async function renderOverviewPage(scope: string | null): Promise<boolean> {
  if (!sidecarBaseUrl) return false;
  const q = scope ? `?scope=${encodeURIComponent(scope)}` : '';
  let resp: Response;
  try {
    resp = await fetch(`${sidecarBaseUrl}/api/cockpit/stats${q}`);
  } catch (err) {
    showStatus(`Stats fetch failed: ${String(err)}`, 'error');
    return false;
  }
  if (resp.status === 404) {
    // The requested scope doesn't exist in this project (a remembered
    // phase from another workspace, a phase-less project, or a stale
    // deep link). Degrade to the unscoped project overview instead of
    // erroring (TASK-0177).
    if (scope !== null) {
      overviewScope = null;
      scopePhaseList = null;
      return renderOverviewPage(null);
    }
    showStatus(`Unknown phase: ${scope}`, 'error');
    return false;
  }
  if (!resp.ok) {
    showStatus(`Stats fetch failed: HTTP ${resp.status}`, 'error');
    return false;
  }
  const data = (await resp.json()) as StatsPayload;
  overviewScope = scope;
  if (!scope) {
    scopePhaseList = data.phases;
  } else if (!scopePhaseList) {
    // Entered a scope directly (deep link / history) — fetch the full
    // phase list for the scope pane; the server cache absorbs it.
    void (async () => {
      try {
        const r = await fetch(`${sidecarBaseUrl}/api/cockpit/stats`);
        if (r.ok) {
          scopePhaseList = ((await r.json()) as StatsPayload).phases;
          renderOverviewScopePane();
        }
      } catch { /* pane fills on next project-scope visit */ }
    })();
  }
  renderOverviewScopePane();
  if (scope && data.scope) renderScopedOverview(data);
  else renderProjectOverview(data);
  void renderOverviewRightPane(scope && data.scope ? data.scope.rel : null, data);
  return true;
}

function renderProjectOverview(data: StatsPayload): void {
  docView.classList.add('overview-pane');
  docView.classList.remove('agents-page');
  // Phase-less projects get a live Now board instead of an empty phase
  // grid (TASK-0165) — the same in-flight data as the Active nav mode.
  const middle = data.phases.length === 0
    ? buildNowBoard()
    : buildPhaseSection(data.phases);
  // State above the fold, history below it (REQ-0022): focus → counts →
  // phases → what's waiting on a human; activity and commits last.
  const parts: HTMLElement[] = [];
  const focus = data.focus ? buildFocusBand(data.focus) : null;
  if (focus) parts.push(focus);
  parts.push(
    buildStatTiles(data),
    middle,
    // One History surface (FEAT-0052). It replaced three tiles that
    // answered the same question three ways — a weekly edit count, the
    // change notes, and the git log with notes as chips — all of which
    // read git or the filesystem as the subject. Here the row is a
    // note's status transition and the commit is a divider.
    buildHistoryTile(data),
  );
  docView.replaceChildren(...parts);
  docView.hidden = false;
  placeholder.hidden = true;
  refreshFooterPath();
  // The digest band goes at the TOP, above the focus band, when the watermark
  // is behind (TASK-0314). Mounted after the paint because it needs a fetch,
  // and prepended rather than inserted into `parts` so a slow sidecar delays
  // the band and never the overview.
  void mountDigestBand();
}

// ----- Since you looked: the digest band (FEAT-0071 / TASK-0314) --------
//
// DES-0008: *"a band atop the overview when the watermark is behind: the
// transitions grouped exactly as History groups them, newest first, with the
// needs-you items lifted above the merely-informational. `Caught up` sits at
// its end — reading to the bottom is what being caught up means."*
//
// The button is at the bottom for that reason and no other. In the header it
// would be a dismiss control, and a dismiss control on a digest is a way to
// mark unread things read.

interface DigestPayload {
  available?: boolean;
  seen_at?: string;
  computed_at?: string;
  transitions?: Array<{
    id?: string; title?: string; rel?: string; type?: string;
    from?: string; to?: string; sha?: string; date?: string;
  }>;
  needs_you?: Array<{
    id?: string; title?: string; rel?: string; type?: string;
    status?: string; owed_verb?: string;
  }>;
  transition_count?: number;
  needs_you_count?: number;
}

async function mountDigestBand(): Promise<void> {
  docView.querySelector('.digest-band')?.remove();
  if (!sidecarBaseUrl) return;
  let d: DigestPayload | null = null;
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/digest`);
    if (!resp.ok) return;
    d = (await resp.json()) as DigestPayload;
  } catch { return; }
  // Absent when there is nothing behind the watermark. A band reading
  // "nothing happened" on every visit is the permanent zero this surface has
  // been taught about twice.
  //
  // **`needs_you` no longer keeps it open** (ISS-0145). The band's subject is
  // *since you looked*; an obligation is not news, did not happen while you
  // were away, and now has a view of its own to live on (FEAT-0092). Counting
  // it here is what made `Caught up` a button that could not clear the thing
  // it sat under.
  if (!d || !d.transition_count) return;

  const band = document.createElement('section');
  band.className = 'digest-band';

  const head = document.createElement('div');
  head.className = 'digest-head';
  // The INSTANT, not `.slice(0, 10)` (ISS-0150). Truncating to the date made
  // `relativeTime` measure from midnight, so catching up at 08:52 reported
  // *8 hours ago* — a clock reading wearing an elapsed time's clothes. The
  // payload has always carried the instant and a test asserts it does; the
  // precision was thrown away one line before it was used.
  const seen = d.seen_at && !d.seen_at.startsWith('1970') ? d.seen_at : '';
  head.textContent = seen
    ? `Since you looked — ${relativeTime(seen)}`
    : 'Since this cockpit first ran';
  band.appendChild(head);

  // **The needs-you half is gone from this band** (ISS-0145). It was here
  // because the digest was the only surface gathering obligations; the badges
  // and the view landings are that surface now, so this one is news and only
  // news. The caption explaining that `Caught up` did not cover the other half
  // went with it — it was a caption for a design that no longer exists.
  //
  // ISS-0134's answer (re-render rather than remove, because the obligations
  // came straight back) was right about its own design and is retired with it.
  const moved = d.transitions ?? [];
  if (moved.length) {
    band.appendChild(digestSubhead(
      `${moved.length} transition${moved.length === 1 ? '' : 's'}`, false,
    ));
    const list = document.createElement('ul');
    list.className = 'digest-list';
    for (const item of moved.slice(0, DIGEST_ROW_LIMIT)) {
      list.appendChild(digestRow(
        item.id ?? '', item.title ?? '', item.rel ?? '',
        item.from && item.to ? `${item.from} → ${item.to}` : (item.to ?? ''),
      ));
    }
    band.appendChild(list);
    band.appendChild(digestMore(moved.length));
  }

  // `Caught up` last. It sends `computed_at`, not the moment of the click:
  // anything that landed while this was on screen must not be marked seen.
  const foot = document.createElement('div');
  foot.className = 'digest-foot';
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'review-btn is-primary digest-caught-up';
  btn.textContent = 'Caught up';
  btn.title = 'Move the watermark to the moment this digest was computed';
  btn.addEventListener('click', () => {
    btn.disabled = true;
    void postJson('/api/cockpit/caught-up', { at: d!.computed_at })
      .then(() => {
        // **Remove the band** (ISS-0145). ISS-0134 answered this by
        // re-rendering, because the obligations half came back on the next
        // paint and removal would have shown a dismissal that had not
        // happened. That half is gone, so removal is now the honest answer:
        // the band's whole subject is what changed since you looked, and you
        // have just said you looked.
        band.remove();
        showStatus('Caught up.');
        void refreshDigests(true).then(() => refreshAttention());
      })
      .catch((err) => {
        btn.disabled = false;
        showStatus(`Could not record: ${String(err)}`, 'error');
      });
  });
  foot.appendChild(btn);
  band.appendChild(foot);

  docView.prepend(band);
}

/** How many rows of each half the band shows before saying how many more.
 *
 *  Not a fold with a toggle: the band is a summary and History is the place
 *  that holds everything. Measured on this repo — an epoch watermark yields
 *  440 transitions and 93 owed items, which is a page nobody reads. */
const DIGEST_ROW_LIMIT = 8;

function digestSubhead(text: string, owed: boolean): HTMLElement {
  const el = document.createElement('div');
  el.className = `digest-subhead${owed ? ' is-owed' : ''}`;
  el.textContent = text;
  return el;
}

function digestMore(total: number): HTMLElement {
  const el = document.createElement('div');
  el.className = 'digest-more';
  el.textContent = total > DIGEST_ROW_LIMIT
    ? `+ ${total - DIGEST_ROW_LIMIT} more — open History for the rest` : '';
  el.hidden = total <= DIGEST_ROW_LIMIT;
  return el;
}

function digestRow(
  id: string, title: string, rel: string, tail: string,
): HTMLElement {
  const li = document.createElement('li');
  const idEl = document.createElement('span');
  idEl.className = 'digest-id mono ov-typed';
  idEl.textContent = shortNoteId(id);
  idEl.title = id;
  const titleEl = document.createElement('span');
  titleEl.className = 'digest-title';
  titleEl.textContent = title;
  const tailEl = document.createElement('span');
  tailEl.className = 'digest-tail';
  tailEl.textContent = tail;
  li.append(idEl, titleEl, tailEl);
  if (rel) {
    li.style.cursor = 'pointer';
    li.addEventListener('click', () => void navigateTo(rel));
  }
  return li;
}

// ----- Verification panel (TASK-0211) -----------------------------------
// The durable counterpart to the desk's queue. It lives on the scope
// being validated — a feature note, a phase page, a release — and reads
// only note data (status, last_run, the `## Runs` log), never the queue.
// The queue's "run" row is a reminder; this panel is the record, and it
// is still here after the reminder is gone.
//
// FEAT-0018 coordination: that feature owns validator/waiver health at
// *project* scope (its badges live in the record column). This panel is
// deliberately per-scope and test-centric so the two compose rather than
// overlap — same surface family, different question.

interface ScopeTest {
  id: string; title: string; rel: string; status: string;
  last_run: string; manual: boolean; steps: number; stale?: boolean;
}

// `MANUAL_TEST_STALE_DAYS = 60` used to live here — a second staleness rule,
// and a disagreeing one (TASK-0371). The project's threshold is
// `DEFAULT_STALENESS_DAYS = 90`, overridable per repo by `SNAPSHOT.yaml`
// `verification.staleness_days`, and both the validator and the cockpit's own
// `unproven` marker already used it against `last_verified`. This constant
// used 60 days against `last_run`, and only for manual tests.
//
// Measured across this corpus on 2026-08-10: the project's rule calls 2 tests
// stale (TST-0001/TST-0002, 94 days); this one called 0, because both are
// automated. A panel reading "all fresh" beside a validator saying otherwise
// is the parallel vocabulary ISS-0024 and ISS-0069 are both about.
//
// The server now ships `stale` on every test row, computed once. Nothing here
// decides it.

async function fetchScopeTests(noteId: string): Promise<ScopeTest[]> {
  if (!sidecarBaseUrl) return [];
  try {
    const resp = await fetch(
      `${sidecarBaseUrl}/api/cockpit/scope-tests?id=${encodeURIComponent(noteId)}`,
    );
    if (!resp.ok) return [];
    const data = (await resp.json()) as { tests?: ScopeTest[] };
    return data.tests ?? [];
  } catch { return []; }
}

function buildVerificationPanel(noteId: string): HTMLElement {
  const wrap = document.createElement('section');
  wrap.className = 'ov-section ov-tile verification-panel';
  const head = document.createElement('div');
  head.className = 'scoped-exit-head';
  const h = document.createElement('h3');
  h.textContent = 'Verification';
  head.appendChild(h);
  wrap.appendChild(head);
  const body = document.createElement('div');
  wrap.appendChild(body);
  void fillVerificationPanel(noteId, head, body);
  return wrap;
}

async function fillVerificationPanel(
  noteId: string, head: HTMLElement, body: HTMLElement,
): Promise<void> {
  const tests = await fetchScopeTests(noteId);
  if (tests.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'meta';
    empty.textContent = 'No acceptance tests link to this scope yet — a test joins it by naming it in `scope:`.';
    body.replaceChildren(empty);
    return;
  }
  const passing = tests.filter(
    (t) => (t.status || '').toLowerCase() === 'passing',
  ).length;

  const frac = document.createElement('span');
  frac.className = 'scoped-exit-frac num';
  frac.textContent = `${passing}/${tests.length}`;
  const bar = document.createElement('span');
  bar.className = 'scoped-exit-bar';
  const fill = document.createElement('i');
  fill.style.width = `${Math.round((passing / tests.length) * 100)}%`;
  bar.appendChild(fill);
  head.append(frac, bar);

  const runnable = tests.filter((t) => t.manual && t.steps > 0);
  if (runnable.length > 0) {
    const all = document.createElement('button');
    all.type = 'button';
    all.className = 'review-btn is-primary verification-runall';
    all.textContent = `Validate this scope · ${runnable.length} manual`;
    all.title = runnable.map((t) => `${t.id} ${t.title}`).join('\n');
    // Sequential by construction: the runner is a stepper, so "run all"
    // means "start the first and come back", not a parallel fan-out.
    all.addEventListener('click', () => {
      void navigateTo(`~tests/${runnable[0].id}/run`);
    });
    head.appendChild(all);
  }

  const list = document.createElement('ul');
  list.className = 'scoped-rowlist verification-list';
  for (const test of tests) {
    const li = document.createElement('li');
    const id = document.createElement('span');
    id.className = 'scoped-row-id mono ov-typed';
    id.dataset.type = 'test';
    id.textContent = shortNoteId(test.id);
    id.title = test.id;
    const title = document.createElement('span');
    title.className = 'scoped-row-title';
    title.textContent = test.title;
    li.append(id, title);

    const meta = document.createElement('span');
    meta.className = 'verification-meta';
    const stale = isStaleRun(test);
    meta.textContent = test.last_run
      ? `${test.manual ? 'manual' : 'auto'} · ran ${test.last_run}`
      : `${test.manual ? 'manual' : 'auto'} · never run`;
    if (stale) {
      meta.classList.add('is-stale');
      meta.title = "Last verified longer ago than this project's staleness "
        + 'threshold (SNAPSHOT.yaml verification.staleness_days)';
    }
    li.appendChild(meta);

    if (test.manual && test.steps > 0) {
      const run = document.createElement('button');
      run.type = 'button';
      run.className = 'verification-run';
      run.textContent = 'Run ▸';
      run.title = `${test.steps} steps`;
      run.addEventListener('click', (e) => {
        e.stopPropagation();
        void navigateTo(`~tests/${test.id}/run`);
      });
      li.appendChild(run);
    }
    appendIf(li, statusChip(test.status));
    li.style.cursor = 'pointer';
    li.addEventListener('click', () => void navigateTo(test.rel));
    list.appendChild(li);
  }
  body.replaceChildren(list);
}

function isStaleRun(test: ScopeTest): boolean {
  return test.stale === true;
}

// ----------------------------------------------------------------------
// Review desk — ~review (FEAT-0041)
// ----------------------------------------------------------------------
// The desk is a *queue*: proposals to accept, questions to answer, tests
// to run. Queues empty, so nothing durable lives here — accepting stamps
// the note's review fields, a run writes its log into the test note, and
// the record surfaces (verification panel, design references) are where
// those outcomes are read afterwards.

interface ReviewQueueItem {
  id?: string; request_id?: string; title?: string; body?: string;
  rel?: string; type?: string; status?: string; kind?: string;
  ts?: string; steps?: number; agent?: string; session_id?: string;
  items?: Array<{ id: string; title?: string; rel?: string; type?: string; status?: string }>;
  // A request ABOUT one note rather than a set (TASK-0229): a design offered
  // for review. `subject_missing` says the note is gone.
  subject?: string;
  subject_missing?: boolean;
  subject_type?: string;
  at_revision?: string;
  dirty_at_offer?: boolean;
}
interface ReviewQueueGroup { key: string; label: string; items: ReviewQueueItem[] }
interface ReviewRegisterTest {
  id: string; title: string; rel: string; status: string;
  last_verified?: string; manual?: boolean; command?: string;
  adequacy?: boolean; waived?: boolean;
}
interface ReviewRegisterReviewed {
  id: string; title: string; rel: string; type: string;
  verdict: string; reviewed_by?: string; review_date?: string;
  // Server-computed (ISS-0121). NOT derivable from `verdict` alone: the
  // field is sticky, so a `changes-requested` note that has since reached
  // a terminal status owes nothing. The predicate lives in `cockpit.py`
  // beside the statuses it reads — see `_verdict_is_owed`.
  owed?: boolean;
}
interface ReviewQueuePayload {
  schema_version: number; total: number; groups: ReviewQueueGroup[];
  outcomes?: Record<string, number>;
  reviewed?: number;
  // The durable half (FEAT-0049). The queue empties; these do not.
  registers?: {
    tests?: ReviewRegisterTest[];
    reviewed?: ReviewRegisterReviewed[];
  };
}
interface ReviewDetail {
  kind: string;
  request?: ReviewQueueItem;
  items?: Array<{ id: string; title?: string; rel?: string; type?: string; status?: string }>;
  note?: { id: string; title: string; rel: string; type: string; status: string };
  steps?: Array<{ n: number; text: string; expected?: string }>;
  mtime?: number;
  last_run?: string;
  verifies?: string[];
  // Staleness for a design-subject request, computed when the entry is
  // opened rather than in the queue payload — it costs a git call and only
  // matters once someone is looking at it.
  subject_type?: string;
  at_revision?: string;
  head_revision?: string;
  revision_moved?: boolean;
  dirty?: boolean;
}

let reviewQueue: ReviewQueuePayload | null = null;
let reviewSelection = '';

const KIND_LABEL: Record<string, string> = {
  decide: 'decide', review: 'review', answer: 'answer', run: 'run',
};

async function fetchReviewQueue(): Promise<ReviewQueuePayload | null> {
  if (!sidecarBaseUrl) return null;
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/review-queue`);
    if (!resp.ok) return null;
    return (await resp.json()) as ReviewQueuePayload;
  } catch { return null; }
}

// The badge is the desk's only claim on the user's attention, so it
// counts only things a human must act on, and it never decays (REQ-0018).
async function refreshReviewBadge(): Promise<void> {
  const payload = await fetchReviewQueue();
  reviewQueue = payload;
  const btn = document.querySelector<HTMLButtonElement>('.top-bar-btn[data-mode="review"]');
  if (!btn) return;
  btn.querySelector('.mode-badge')?.remove();
  const total = payload?.total ?? 0;
  if (total <= 0) return;
  const badge = document.createElement('span');
  badge.className = 'mode-badge';
  badge.textContent = String(total);
  btn.appendChild(badge);
  btn.title = `Review — ${total} waiting on you`;
}

/** How many items are waiting in the inbox, on the Inbox mode button.
 *
 *  Not decoration. The inbox's success condition is being EMPTY, so the count
 *  is the entire mechanism by which anyone notices there is triage to do — and
 *  on this surface specifically, four separate defects this month were "a thing
 *  existed and nothing pointed at it".
 */
interface InboxItem { name: string; bytes: number; mtime: number; suffix: string }
interface InboxPayload { schema_version: number; items: InboxItem[] }

const INBOX_PREVIEWABLE = new Set(['.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif', '.svg']);
/** Types the stage can render as text rather than punting to Finder. */
const INBOX_READABLE = new Set(['.md', '.txt', '.log', '.csv', '.tsv', '.json',
  '.yaml', '.yml', '.html', '.css', '.js', '.ts', '.py', '.sh']);

// Lucide file-type icons, keyed by suffix. Same idiom and same builder as
// TYPE_ICONS below — an inbox row should look like it belongs to this app.
const ICON_FILE_TAIL = '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v6h6"/>';
const INBOX_ICONS: ReadonlyArray<[ReadonlySet<string>, string]> = [
  [new Set(['.pdf']),
    `${ICON_FILE_TAIL}<path d="M9 13v5"/><path d="M9 13h1.5a1.5 1.5 0 0 1 0 3H9"/>`],
  [new Set(['.md', '.txt', '.log', '.rtf', '.doc', '.docx', '.pages']),
    `${ICON_FILE_TAIL}<path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/>`],
  [new Set(['.csv', '.tsv', '.json', '.yaml', '.yml', '.xlsx', '.numbers']),
    `${ICON_FILE_TAIL}<path d="M8 13h2"/><path d="M14 13h2"/><path d="M8 17h2"/><path d="M14 17h2"/>`],
  [new Set(['.zip', '.tar', '.gz', '.tgz', '.7z']),
    `${ICON_FILE_TAIL}<path d="M10 7V6"/><path d="M10 12v-1"/><circle cx="10" cy="18" r="2"/>`],
  [new Set(['.mov', '.mp4', '.m4v', '.webm', '.avi']),
    '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M7 3v18"/><path d="M3 7.5h4"/>'
    + '<path d="M3 12h18"/><path d="M3 16.5h4"/><path d="M17 3v18"/><path d="M17 7.5h4"/><path d="M17 16.5h4"/>'],
  // An image whose thumbnail failed to load still reads as an image here,
  // rather than falling through to "unknown file".
  [INBOX_PREVIEWABLE,
    '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/>'
    + '<path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>'],
];
const ICON_CAMERA = '<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/>';

function inboxIconFor(suffix: string): SVGElement {
  for (const [suffixes, paths] of INBOX_ICONS) {
    if (suffixes.has(suffix)) return makeSvg(paths, 15, { class: 'inbox-icon' });
  }
  return makeSvg(ICON_FILE_TAIL, 15, { class: 'inbox-icon' });
}

function inboxItemUrl(name: string): string {
  return `${sidecarBaseUrl}/_inbox/${encodeURIComponent(name)}`;
}

async function fetchInboxItems(): Promise<InboxItem[]> {
  if (!sidecarBaseUrl) return [];
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/inbox`);
    if (resp.ok) return ((await resp.json()) as InboxPayload).items;
  } catch { /* an unreachable sidecar is not an inbox problem */ }
  return [];
}

/**
 * Hand one inbox item to the agent to triage.
 *
 * Reuses the dispatch path rather than growing a second one, so this inherits
 * the agent preference, the terminal and the ledger. The prompt names the one
 * file and the skill: the convention's whole point is that the inbox empties,
 * and until now the UI could only *discard* an item, never triage it.
 */
async function triageInboxItem(item: InboxItem): Promise<void> {
  const wsId = activeId;
  if (!wsId) return;
  const chosen = loadDispatchAgent();
  const prompt = `Triage inbox/${item.name} in this project. Read `
    + `tools/skills/inbox-triage/SKILL.md and follow it for this one item: read `
    + `it, decide where it belongs, then file it, split it across the right `
    + `notes, or discard it — and remove it from inbox/ either way. Nothing `
    + `should be left in the inbox afterwards.`;
  const queued: QueuedDispatch = {
    id: 'inbox', rel: '', agent: chosen, prompt, ts: new Date().toISOString(),
  };
  const freshPty = !liveTerminals.has(wsId);
  showTerminal();
  await new Promise((r) => setTimeout(r, freshPty ? 600 : 150));
  const res = await cockpitApi.dispatch.execute(wsId, queued);
  if ('error' in res && res.error) {
    showStatus(`Triage dispatch failed: ${res.error}`, 'error');
    return;
  }
  showStatus(res.queued ? `Queued triage of ${item.name}` : `Triaging ${item.name}`);
  scheduleHide(2500);
}

async function discardInboxItem(name: string): Promise<void> {
  await postJson('/api/inbox/discard', { name });
  showStatus(`Discarded ${name}.`, 'info');
  void renderInboxPanel();
}

/**
 * Open one item full-size in the centre stage.
 *
 * The pane is the tray and the stage is the viewer (TASK-0234). A left pane
 * is narrow and a screenshot is the thing most often dropped into it, so
 * shrinking images to fit the tray would trade away the feature's point.
 */
async function renderInboxItemView(name: string): Promise<boolean> {
  if (!sidecarBaseUrl) return false;
  const items = await fetchInboxItems();
  const item = items.find((i) => i.name === name);
  docView.classList.remove('overview-pane', 'agents-page', 'review-page',
    'design-page', 'is-design-shell');
  docView.classList.add('inbox-page');

  const root = document.createElement('div');
  const h = document.createElement('h1');
  h.textContent = name;
  root.append(h);

  if (!item) {
    // Triaged out from under us — the resolved state, not an error.
    const gone = document.createElement('p');
    gone.className = 'inbox-empty';
    gone.textContent = 'No longer in the inbox — it has been filed or discarded.';
    root.append(gone);
    docView.replaceChildren(root);
    docView.hidden = false;
    placeholder.hidden = true;
    return true;
  }

  const meta = document.createElement('p');
  meta.className = 'meta';
  meta.textContent = `${Math.max(1, Math.round(item.bytes / 1024))} KB · inbox/${item.name}`;
  root.append(meta);

  const actions = document.createElement('div');
  actions.className = 'inbox-actions';
  const triage = document.createElement('button');
  triage.type = 'button';
  triage.className = 'review-btn is-primary';
  triage.textContent = 'Triage this item';
  triage.addEventListener('click', () => { void triageInboxItem(item); });
  const discard = document.createElement('button');
  discard.type = 'button';
  discard.className = 'review-btn is-bad';
  discard.textContent = 'Discard';
  discard.addEventListener('click', () => {
    void (async () => { await discardInboxItem(item.name); await navigateTo('~inbox'); })();
  });
  actions.append(triage, discard);
  root.append(actions);

  if (INBOX_PREVIEWABLE.has(item.suffix)) {
    const img = document.createElement('img');
    img.className = 'inbox-full';
    img.src = inboxItemUrl(item.name);
    img.alt = item.name;
    root.append(img);
  } else if (INBOX_READABLE.has(item.suffix)) {
    const pre = document.createElement('pre');
    pre.className = 'inbox-text';
    try {
      const resp = await fetch(inboxItemUrl(item.name));
      // textContent, never innerHTML: this is unreviewed external material.
      pre.textContent = resp.ok ? await resp.text() : 'Could not read this item.';
    } catch { pre.textContent = 'Could not read this item.'; }
    root.append(pre);
  } else {
    const hint = document.createElement('p');
    hint.className = 'meta';
    hint.textContent = 'No in-app preview for this type — open it in Finder.';
    root.append(hint);
    const reveal = document.createElement('button');
    reveal.type = 'button';
    reveal.className = 'review-btn';
    reveal.textContent = 'Reveal in Finder';
    reveal.addEventListener('click', () => {
      const wsRoot = workspaces.find((w) => w.id === activeId)?.root || '';
      if (wsRoot) void cockpitApi.app.revealInFinder(`${wsRoot}/inbox/${item.name}`);
    });
    root.append(reveal);
  }

  docView.replaceChildren(root);
  docView.hidden = false;
  placeholder.hidden = true;
  return true;
}

/**
 * The inbox tray, docked in the left pane above the agent attention panel.
 *
 * It sits here rather than in the top bar because every mode up there is a
 * view over the committed record in `docs/`, and the inbox is deliberately
 * none of that — it is gitignored staging whose success condition is being
 * empty (LIFECYCLE). The header stays even when empty: it is one row, it
 * carries the screenshot action, and "empty" is a state worth stating.
 */
async function renderInboxPanel(): Promise<void> {
  const panel = document.getElementById('ws-inbox');
  if (!panel) return;
  if (!activeId || !sidecarBaseUrl) { panel.hidden = true; return; }
  const items = await fetchInboxItems();
  panel.hidden = false;

  const head = document.createElement('div');
  head.className = 'ws-inbox-head';
  const label = document.createElement('span');
  label.className = 'ws-inbox-label';
  label.textContent = 'Inbox';
  head.append(label);
  if (items.length) {
    const count = document.createElement('span');
    count.className = 'ws-inbox-count';
    count.textContent = String(items.length);
    head.append(count);
  }
  const shoot = document.createElement('button');
  shoot.type = 'button';
  shoot.className = 'ws-inbox-shoot';
  shoot.title = 'Take a screenshot into this project\u2019s inbox';
  shoot.setAttribute('aria-label', 'Take a screenshot');
  shoot.append(makeSvg(ICON_CAMERA, 14, { class: 'ws-inbox-shoot-icon' }));
  shoot.addEventListener('click', (ev) => {
    ev.stopPropagation();
    void (async () => {
      if (!activeId) return;
      shoot.disabled = true;
      try {
        const res = await cockpitApi.app.captureScreenshot(activeId);
        if (res.cancelled) showStatus('Screenshot cancelled.', 'info');
        else if (!res.ok) showStatus(`Screenshot failed: ${res.error}`, 'error');
        else { showStatus(`Captured ${res.name}`, 'info'); void renderInboxPanel(); }
      } finally { shoot.disabled = false; }
    })();
  });
  head.append(shoot);

  const body = document.createElement('div');
  body.className = 'ws-inbox-body';
  if (!items.length) {
    // An empty inbox is the RESOLVED state, not a blank pane. Saying so is the
    // difference between "nothing to do" and "something is broken".
    const done = document.createElement('p');
    done.className = 'ws-inbox-empty';
    done.textContent = 'Empty \u2014 nothing to triage.';
    body.append(done);
  }
  for (const item of items) {
    const row = document.createElement('div');
    row.className = 'ws-inbox-row';
    row.tabIndex = 0;
    row.setAttribute('role', 'button');
    row.title = `${item.name} \u2014 ${Math.max(1, Math.round(item.bytes / 1024))} KB`;
    if (INBOX_PREVIEWABLE.has(item.suffix)) {
      const img = document.createElement('img');
      img.className = 'ws-inbox-thumb';
      img.src = inboxItemUrl(item.name);
      img.alt = '';
      row.append(img);
    } else {
      row.append(inboxIconFor(item.suffix));
    }
    const name = document.createElement('span');
    name.className = 'ws-inbox-name';
    name.textContent = item.name;
    row.append(name);
    const open = (): void => { void navigateTo(`~inbox/${item.name}`); };
    row.addEventListener('click', open);
    row.addEventListener('keydown', (ev) => {
      if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); open(); }
    });
    row.addEventListener('contextmenu', (ev) => {
      ev.preventDefault();
      void cockpitApi.app.showContextMenu('inbox-item', {
        name: item.name,
        workspaceId: activeId || '',
        root: workspaces.find((w) => w.id === activeId)?.root || '',
      });
    });
    body.append(row);
  }

  panel.replaceChildren(head, body);
}

interface DesignRecord {
  id: string; title: string; rel: string; status: string;
  role: string; asset: string; has_asset: boolean;
  viewport: number | null; implements: string[];
  rationale: DesignRationale[];
  stylesheets?: string[];
  variants?: DesignVariant[];
  variant_scripts?: boolean;
  chosen_variant?: string;
}

/** An ADR this design links. `missing` = the link resolves to nothing, which
 *  is shown rather than dropped — omitting it would hide a typo in the note's
 *  own frontmatter, and the point of resolving by link is that links are
 *  checkable. */
interface DesignRationale {
  id: string; title: string; decision: string;
  url: string; status: string; missing: boolean;
}

let designRegister: DesignRecord[] = [];

/** Viewport presets. 900 is not a breakpoint — it is the height REQ-0022
 *  asserts every state section fits within, so a design reviewed at another
 *  size is reviewed against the wrong question. */
const DESIGN_VIEWPORTS: Array<{ key: string; label: string; w: number | null; h: number | null }> = [
  { key: 'declared', label: 'Declared', w: null, h: 900 },
  { key: 'w1240', label: '1240 × 900', w: 1240, h: 900 },
  { key: 'w900', label: '900 × 900', w: 900, h: 900 },
  { key: 'w420', label: '420 × 900', w: 420, h: 900 },
  { key: 'fill', label: 'Fill', w: null, h: null },
];
let designViewport = 'declared';

// The sidebar costs the artifact 260px of width. Measured against the real
// renderer: a 1356px pane leaves the frame 1036px, and DES-0001's dossier is
// authored at 1240px — so the design scrolled sideways inside its own frame,
// which is what "the frame is not the right size" looked like on screen. The
// sidebar therefore collapses, and the choice persists.
let designSideOpen = (() => {
  try { return localStorage.getItem('cockpit:design-side') !== 'closed'; }
  catch { return true; }
})();
function setDesignSideOpen(open: boolean): void {
  designSideOpen = open;
  try { localStorage.setItem('cockpit:design-side', open ? 'open' : 'closed'); }
  catch { /* localStorage unavailable */ }
}

async function fetchDesignRegister(): Promise<DesignRecord[]> {
  if (!sidecarBaseUrl) return [];
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/designs`);
    if (!resp.ok) return [];
    const data = await resp.json() as { designs?: DesignRecord[] };
    designRegister = Array.isArray(data.designs) ? data.designs : [];
  } catch { /* keep the last good register */ }
  return designRegister;
}

function buildDesignFrame(d: DesignRecord, atSha?: string): HTMLElement {
  const wrap = document.createElement('div');
  wrap.className = 'design-stage';
  if (atSha) {
    const tag = document.createElement('span');
    tag.className = 'design-stage-tag';
    const rev = designRevisions.find((r) => r.sha === atSha);
    tag.textContent = rev ? `${rev.date} · ${rev.sha}` : atSha;
    wrap.append(tag);
  }

  if (!d.asset) {
    // Not a frame: the stage stretches its children so an iframe can fill it,
    // which turned a one-line button into a full-height slab (Edwin,
    // 2026-07-28). An empty stage is a message, not a surface.
    wrap.classList.add('is-empty');
    const empty = document.createElement('p');
    empty.className = 'design-empty';
    empty.textContent = `${d.id} declares no artifact yet — nothing to render.`;
    wrap.append(empty);
    // An empty stage must still lead somewhere. DES-0002 is the design SYSTEM
    // and its whole content is prose; landing on "nothing to render" with no
    // way through made the system unreadable inside the tool that exists to
    // show it (ISS-0041).
    const toNote = document.createElement('button');
    toNote.type = 'button';
    toNote.className = 'design-note-open';
    toNote.textContent = `Read ${d.id} as a note`;
    toNote.addEventListener('click', () => { void navigateTo(d.rel); });
    wrap.append(toNote);
    return wrap;
  }
  if (!d.has_asset && !atSha) {
    // `has_asset` is an `is_file()` on the WORKING COPY, so it must not gate a
    // HISTORICAL render: `design-asset-at` reads from git and serves an
    // artifact deleted after it was committed. The outer caller was relaxed
    // for this in round 2 and this inner return still refused, so only the
    // message changed (independent review round 3).
    //
    // Distinguish "none declared" from "declared but missing". A blank pane
    // for either would hide a typo committed weeks earlier.
    wrap.classList.add('is-empty');
    const missing = document.createElement('p');
    missing.className = 'design-empty design-missing';
    missing.textContent = `Artifact not found: ${d.asset}`;
    wrap.append(missing);
    return wrap;
  }

  const frame = document.createElement('iframe');
  frame.className = 'design-frame';
  // allow-scripts is required: DES-0001 carries a theme toggle, so a
  // script-free sandbox would break the acceptance subject. Everything else
  // stays denied — no same-origin, no top navigation, no forms. The real
  // protection against an artifact reaching a mutation endpoint is
  // server-side (the asset route is GET-only and gated on the register);
  // a sandbox attribute does not restrict network.
  frame.setAttribute('sandbox', 'allow-scripts');
  frame.setAttribute('referrerpolicy', 'no-referrer');
  // The artifact cannot read the app's theme: it is sandboxed with an opaque
  // origin and can reach neither the parent nor localStorage. So the theme
  // travels in the URL, and an artifact may honour it or ignore it — a design
  // mock that is deliberately light stays light, while the style guide (which
  // documents both schemes) follows the app.
  // Theme, plus the stylesheets the note declares (TASK-0231). The frame is
  // sandboxed with an opaque origin, so it cannot fetch the designs API to
  // discover them — the URL is the only channel. Passing them makes ONE
  // style-guide page work for every project: everything project-specific
  // arrives at runtime, so six repos share one artifact rather than six that
  // drift.
  const cssQ = (d.stylesheets || []).length
    ? `&css=${encodeURIComponent((d.stylesheets || []).join(','))}` : '';
  const themeQ = `?theme=${document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light'}${cssQ}`;
  frame.src = atSha
    ? `${sidecarBaseUrl}/design-asset-at/${encodeURIComponent(d.id)}/${encodeURIComponent(atSha)}${themeQ}`
    : `${sidecarBaseUrl}/design-asset/${d.asset.split('/').map(encodeURIComponent).join('/')}${themeQ}`;

  const preset = DESIGN_VIEWPORTS.find((v) => v.key === designViewport)
    ?? DESIGN_VIEWPORTS[0];
  // `declared` means: use the note's viewport if it declared one, otherwise
  // let the artifact scroll. Absence is meaningful — a dossier framed at a
  // device width demonstrates nothing.
  const width = preset.key === 'declared' ? d.viewport : preset.w;
  if (width) {
    frame.style.width = `${width}px`;
    wrap.classList.add('is-framed');
  } else {
    frame.style.width = '100%';
  }
  // Height follows the SAME absence rule as width, which it did not before
  // (ISS-0039): `declared` carried h: 900 unconditionally, so a design that
  // declared no viewport — a document, the case that should scroll freely —
  // was forced into a 900px window inside a scrolling page. DES-0001 is that
  // case and is the only design in the repo with an artifact, so the one
  // thing that could be opened was the one thing framed wrongly.
  //
  // A declared viewport keeps its fixed height: the framing IS the point,
  // and a phone-width design stretched to the window height demonstrates
  // nothing. Everything else fills the stage, which the shell has already
  // sized, and the artifact scrolls inside it — once.
  const framedHeight = preset.key === 'declared' ? (d.viewport ? preset.h : null) : preset.h;
  if (framedHeight) frame.style.height = `${framedHeight}px`;
  else frame.style.height = '100%';

  if (width && framedHeight) {
    // Fit the declared viewport into the stage rather than letting the stage
    // scroll (ISS-0044). A 900px frame in a ~767px stage made the stage a
    // second scroller, and — centred in a wide pane — left a broad dead zone
    // either side of the design where the wheel scrolled that stage by a few
    // pixels instead of scrolling the artifact. "No way to scroll down the
    // document" was pointing at exactly that.
    //
    // Scaling preserves what framing is FOR: the artifact still lays out at
    // its declared width, so a 420px design is still a 420px design. Only the
    // presentation shrinks, and only when it must.
    const fit = () => {
      const box = wrap.getBoundingClientRect();
      if (!box.height || !box.width) return;
      const scale = Math.min(1, box.height / framedHeight, box.width / width);
      frame.style.transformOrigin = 'top center';
      frame.style.transform = scale < 1 ? `scale(${scale})` : '';
      // A scaled element still occupies its UNSCALED size in layout, so the
      // negative bottom margin below is what actually reclaims the
      // difference. (ISS-0055 §2: a `--design-fit` custom property used to
      // be set here with a comment claiming it did this. It appeared in no
      // stylesheet — the clipping comes from
      // `.design-stage.is-framed { overflow: hidden }`. A comment naming a
      // mechanism that does not exist is worse than none, because it gets
      // believed.)
      frame.style.marginBottom = scale < 1
        ? `${-(framedHeight * (1 - scale))}px` : '';
    };
    requestAnimationFrame(fit);
    // ISS-0055 §3: one observer per frame, and a frame is rebuilt on every
    // viewport change, revision selection and compare toggle. Disconnect the
    // previous one rather than leaking it per repaint.
    designFitObserver?.disconnect();
    designFitObserver = new ResizeObserver(fit);
    designFitObserver.observe(wrap);
  }
  wrap.append(frame);
  return wrap;
}

// The design stage has at most one framed artifact at a time, so at most
// one fit observer should exist (ISS-0055 §3).
let designFitObserver: ResizeObserver | null = null;

function buildDesignHeader(d: DesignRecord, onViewport: () => void): HTMLElement {
  const head = document.createElement('header');
  head.className = 'design-head';

  const h = document.createElement('h1');
  h.textContent = d.title || d.id;
  head.append(h);

  const meta = document.createElement('div');
  meta.className = 'design-meta';
  const chip = (text: string, cls = '') => {
    const el = document.createElement('span');
    el.className = `design-chip ${cls}`.trim();
    el.textContent = text;
    return el;
  };
  // A design with no artifact renders an empty stage, and until now there was
  // no way from here to the prose that explains it — the note banner points at
  // the bench and nothing pointed back, so DES-0002 (asset: "") was readable
  // only outside the app. The id chip is the link (ISS-0041).
  const idChip = chip(d.id, 'design-chip-link');
  idChip.setAttribute('role', 'link');
  idChip.setAttribute('tabindex', '0');
  idChip.title = `Open ${d.rel}`;
  const openNote = () => { void navigateTo(d.rel); };
  idChip.addEventListener('click', openNote);
  idChip.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openNote(); }
  });
  meta.append(idChip);
  if (d.status) meta.append(chip(d.status, `status-${d.status}`));
  meta.append(chip(d.role === 'system' ? 'design system' : 'proposal'));
  if (d.viewport) meta.append(chip(`${d.viewport}px surface`));
  else if (d.asset) meta.append(chip('document'));
  for (const id of d.implements) meta.append(chip(id, 'design-implements'));
  head.append(meta);

  // The viewport chooser appears ONLY for a design that declares a viewport —
  // that is, one that IS a surface (ISS-0045).
  //
  // Edwin: "why do we have these options on top if all we show is just a page
  // with artefacts ... the page should always just show the page". Correct for
  // a document, and both designs in this corpus are documents: the bar was
  // five controls of which four were disabled, framing a page that has no
  // device width. `viewport:` absence already means "this is a document, let
  // it flow" everywhere else; the chrome had not been told.
  if (d.viewport) {
    const bar = document.createElement('div');
    bar.className = 'design-viewports';
    for (const v of DESIGN_VIEWPORTS) {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'design-vp' + (v.key === designViewport ? ' is-active' : '');
      b.textContent = v.label;
      b.addEventListener('click', () => { designViewport = v.key; onViewport(); });
      bar.append(b);
    }
    head.append(bar);
  }
  return head;
}

/** The decisions behind this design — the ADRs it links, and no others.
 *
 *  Returns null when there are none, so a design with no linked ADRs shows
 *  nothing at all. An empty "Rationale" heading would read as "no decisions
 *  were made here", which is a claim; absence is not.
 */
function buildDesignRationale(d: DesignRecord): HTMLElement | null {
  const entries = d.rationale || [];
  if (!entries.length) return null;

  const sec = document.createElement('section');
  sec.className = 'design-rationale';
  const h = document.createElement('h2');
  h.textContent = 'Decisions behind this design';
  sec.append(h);

  for (const r of entries) {
    const row = document.createElement('div');
    row.className = 'design-rationale-row' + (r.missing ? ' is-missing' : '');

    const id = document.createElement('span');
    id.className = 'design-rationale-id';
    id.textContent = shortNoteId(r.id);
    id.title = r.id;
    row.append(id);

    const text = document.createElement('div');
    text.className = 'design-rationale-text';
    if (r.missing) {
      // Named, not summarised. The link is broken and the surface says so.
      text.textContent = `${r.id} is linked but no such note exists.`;
    } else {
      // The ADR's own `decision:` line — the sentence its author wrote to be
      // quoted. Its title when that is absent, and never a paraphrase: a
      // generated summary of a decision is the kind of confident restatement
      // that misleads precisely where accuracy matters.
      text.textContent = r.decision || r.title || r.id;
    }
    row.append(text);

    if (!r.missing && r.url) {
      const open = document.createElement('button');
      open.type = 'button';
      open.className = 'design-rationale-open';
      open.textContent = 'Open';
      open.addEventListener('click', () => { void navigateTo(r.url); });
      row.append(open);
    }
    sec.append(row);
  }
  return sec;
}

function buildDesignRegisterList(designs: DesignRecord[]): HTMLElement {
  const wrap = document.createElement('div');
  wrap.className = 'design-register';
  const h = document.createElement('h1');
  h.textContent = 'Designs';
  wrap.append(h);
  if (!designs.length) {
    const p = document.createElement('p');
    p.className = 'design-empty';
    p.textContent = 'No design notes yet. A design is a note with type: [[design]].';
    wrap.append(p);
    return wrap;
  }
  for (const d of designs) {
    const row = document.createElement('a');
    row.className = 'design-row';
    row.href = '#';
    row.addEventListener('click', (e) => {
      e.preventDefault();
      void navigateTo(`~design/${d.id}`);
    });
    const t = document.createElement('span');
    t.className = 'design-row-title';
    t.textContent = `${d.id} — ${d.title}`;
    const s2 = document.createElement('span');
    s2.className = 'design-row-meta';
    s2.textContent = [
      d.role === 'system' ? 'system' : 'proposal',
      d.status,
      d.has_asset ? (d.viewport ? `${d.viewport}px` : 'document') : 'no artifact',
    ].filter(Boolean).join(' · ');
    row.append(t, s2);
    wrap.append(row);
  }
  return wrap;
}

interface DesignRevision {
  sha: string; full_sha: string; date: string;
  subject: string; reason: string; author: string;
}
let designRevisions: DesignRevision[] = [];
let designDirty = false;
let designCompareSha: string | null = null;   // null = working copy

async function fetchDesignRevisions(id: string): Promise<void> {
  designRevisions = [];
  designDirty = false;
  if (!sidecarBaseUrl) return;
  try {
    const resp = await fetch(
      `${sidecarBaseUrl}/api/cockpit/design-revisions/${encodeURIComponent(id)}`);
    if (!resp.ok) return;
    const data = await resp.json() as
      { revisions?: DesignRevision[]; dirty?: boolean };
    designRevisions = Array.isArray(data.revisions) ? data.revisions : [];
    designDirty = Boolean(data.dirty);
  } catch { /* the surface still renders the working copy */ }
}

function buildDesignRevisionRail(d: DesignRecord, repaint: () => void): HTMLElement {
  const rail = document.createElement('aside');
  rail.className = 'design-revisions';

  const h = document.createElement('h2');
  h.textContent = 'Revisions';
  rail.append(h);

  if (designDirty) {
    // An uncaptured edit is a revision the compare view cannot see and the
    // note does not record. Saying so is the difference between "three
    // revisions" and "three revisions plus whatever you have not committed".
    const warn = document.createElement('p');
    warn.className = 'design-dirty';
    warn.textContent = 'Uncommitted changes — capture them or they are not history.';
    rail.append(warn);
  }

  const mk = (label: string, meta: string, sha: string | null) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'design-rev' + (designCompareSha === sha ? ' is-active' : '');
    const t = document.createElement('span');
    t.className = 'design-rev-label';
    t.textContent = label;
    const m = document.createElement('span');
    m.className = 'design-rev-meta';
    m.textContent = meta;
    b.append(t, m);
    b.addEventListener('click', () => {
      designCompareSha = designCompareSha === sha ? null : sha;
      repaint();
    });
    return b;
  };

  rail.append(mk('Working copy', designDirty ? 'uncommitted' : 'current', null));
  for (const r of designRevisions) {
    rail.append(mk(r.reason || r.subject, `${r.date} · ${r.sha}`, r.sha));
  }
  if (!designRevisions.length) {
    const p2 = document.createElement('p');
    p2.className = 'design-empty';
    p2.textContent = 'No committed revisions yet — a revision is recorded when this design is accepted.';
    rail.append(p2);
  }
  return rail;
}

/** A banner on a design NOTE offering the artifact.
 *
 *  The note is prose *about* a design; the artifact is the design. Opening
 *  the note and seeing only text is the correct behaviour for Markdown and
 *  the wrong experience for a design — so the note says where the design is.
 */
function buildDesignNoteBanner(rel: string): HTMLElement | null {
  const d = designRegister.find((x) => x.rel === rel);
  if (!d) return null;
  const bar = document.createElement('div');
  bar.className = 'design-note-banner';
  const label = document.createElement('span');
  label.textContent = d.has_asset
    ? 'This note describes a design.'
    : 'This design has no artifact yet.';
  bar.append(label);
  if (d.has_asset) {
    const open = document.createElement('button');
    open.type = 'button';
    open.className = 'design-note-open';
    open.textContent = `Open ${d.id} in the design bench`;
    open.addEventListener('click', () => { void navigateTo(`~design/${d.id}`); });
    bar.append(open);
  }
  return bar;
}

interface BriefPayload {
  state: 'absent' | 'unfilled' | 'filled';
  name: string; purpose: string; placeholders: number; rel: string;
  // `body_html` is the section rendered by the sidecar (ISS-0151); optional
  // so an older sidecar degrades to an empty band rather than to raw
  // markdown printed as text, which is the defect it replaces.
  sections: Array<{ heading: string; body: string; body_html?: string }>;
}
let briefCache: BriefPayload | null = null;

async function fetchBrief(): Promise<BriefPayload | null> {
  if (!sidecarBaseUrl) return null;
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/brief`);
    if (!resp.ok) return null;
    briefCache = await resp.json() as BriefPayload;
  } catch { /* keep the last good brief */ }
  return briefCache;
}

/** The identity band: what this is, who for, its shape.
 *
 *  Three states are rendered differently on purpose. `unfilled` shows a
 *  prompt and NEVER the placeholder text — a surface leading with
 *  "Purpose: REPLACE ME" every session is worse than one that says the brief
 *  needs writing. `absent` degrades quietly: not every project adopts the
 *  convention, and nagging one that never did is noise.
 */
function buildIdentityBand(brief: BriefPayload | null): HTMLElement | null {
  if (!brief || brief.state === 'absent') return null;

  const band = document.createElement('section');
  band.className = 'design-identity';

  if (brief.state === 'unfilled') {
    band.classList.add('is-unfilled');
    const h = document.createElement('h1');
    // Say what IS known. A brief with a real name and a missing purpose is a
    // project that has half-answered, and headlining "has not said what it
    // is" over a name the payload just parsed calls the file a liar
    // (ISS-0035). `name` is already placeholder-scrubbed, so a non-empty
    // value here is always real.
    h.textContent = brief.name
      ? `${brief.name} — the brief is unfinished`
      : 'This project has not said what it is';
    const p = document.createElement('p');
    // A brief can be incomplete WITHOUT carrying placeholders — someone
    // deleted the template lines instead of filling them. Reporting "0
    // template placeholder(s)" there would be nonsense, so the sentence is
    // built from what is actually true of this file.
    p.textContent = (brief.placeholders
      ? `LLM_BRIEF.md carries ${brief.placeholders} template placeholder(s). `
      : 'LLM_BRIEF.md does not say what this project is or what it is for. ')
      + 'It is what an agent reads to learn what this project is for — an '
      + 'unfinished one teaches it nothing.';
    const a = document.createElement('a');
    a.className = 'design-identity-edit';
    a.href = '#';
    a.textContent = 'Open LLM_BRIEF.md';
    a.addEventListener('click', (e) => {
      e.preventDefault();
      void navigateTo(brief.rel);
    });
    band.append(h, p, a);
    return band;
  }

  const h = document.createElement('h1');
  h.textContent = brief.name || 'This project';
  band.append(h);
  if (brief.purpose) {
    const p = document.createElement('p');
    p.className = 'design-identity-purpose';
    p.textContent = brief.purpose;
    band.append(p);
  }
  // "What it is for" is the section worth surfacing inline — it answers the
  // question the band exists to answer. The rest stay one click away rather
  // than turning the band into the whole file.
  const forSection = brief.sections.find(
    (s) => /what it is for/i.test(s.heading));
  if (forSection) {
    const det = document.createElement('div');
    det.className = 'design-identity-for';
    // Rendered by the sidecar, inserted as markup (ISS-0151). This printed
    // `forSection.body` — raw markdown — as `textContent` under a `pre-wrap`
    // rule, so the file's own newlines showed as hard breaks and its syntax
    // showed as syntax. It reads exactly like a wrapped source file, and the
    // file was never wrapped: measured across twelve repos, zero.
    det.innerHTML = forSection.body_html || '';
    band.append(det);
  }
  // A filled identity with placeholders still in the file used to render as
  // simply complete. The surface being the feedback loop is this feature's
  // whole thesis — a brief nobody is told about is the state that left 10 of
  // 11 fleet repos unfilled — so say it, quietly, without retracting the
  // identity that IS stated.
  if (brief.placeholders) {
    const note = document.createElement('p');
    note.className = 'design-identity-residual';
    note.textContent = `${brief.placeholders} section(s) of the brief are `
      + 'still template placeholders.';
    band.append(note);
  }
  const a = document.createElement('a');
  a.className = 'design-identity-edit';
  a.href = '#';
  a.textContent = 'Read the full brief';
  a.addEventListener('click', (e) => {
    e.preventDefault();
    void navigateTo(brief.rel);
  });
  band.append(a);
  return band;
}

// ---- The view landings (FEAT-0092 / TASK-0388) --------------------------
//
// Two of Edwin's observations with one cause: four of the six view buttons
// left the centre pane on whatever you were last reading, and the badges —
// honest and complete since FEAT-0089 — counted things the view then never
// gathered. Issues appeared to work only because its NAVIGATOR happens to
// open on `Needs triage`.
//
// So each of these views gets the thing Overview and Intent already had: a
// page, leading with what its badge counts, named with the registry's own
// verb. The count comes from the same walk as the badge (`landing_payload`),
// because a page disagreeing with the button that opened it is the failure
// FEAT-0089 exists to prevent.

const VIEW_LANDING_RELS: ReadonlySet<string> = new Set([
  '~features', '~issues', '~tests',
]);

//: The heading each landing carries. Read from the top bar's own `title`
//: attributes rather than restated, so the page and the button that opens it
//: cannot come to call the same view two different things.
const VIEW_LABELS: Record<string, string> = Object.fromEntries(
  Array.from(document.querySelectorAll<HTMLElement>('.top-bar-btn[data-mode]'))
    .map((b) => [b.dataset.mode ?? '', b.title || b.dataset.mode || ''])
    .filter(([mode]) => mode),
);

interface LandingPayload {
  view: string;
  known: boolean;
  total: number;
  groups: Array<{
    kind: string; count: number; verb: string; noun: string; label: string;
    items: Array<{ id: string; title: string; rel: string; type: string; status: string; verb: string }>;
  }>;
}

//: What each landing says when it owes nothing. Never a `0` and never an
//: empty panel — this project's standing rule about zero, and FEAT-0073's
//: about empty states saying what the pane is FOR.
const LANDING_QUIET: Record<string, { head: string; note: string }> = {
  features: {
    head: 'Nothing owed on features.',
    note: 'Requirements awaiting approval and features awaiting acceptance appear here. The tree on the left is the whole structure.',
  },
  issues: {
    head: 'Nothing owed on issues.',
    note: 'Issues at triage appear here, with the verb that settles them. Everything filed is on the left, by severity.',
  },
  tests: {
    head: 'Nothing owed on tests.',
    note: 'Manual tests waiting for a run appear here. The register and the acceptance tiers are on the left.',
  },
};

async function renderViewLanding(view: string): Promise<boolean> {
  if (!sidecarBaseUrl) return false;
  let data: LandingPayload | null = null;
  try {
    const resp = await fetch(
      `${sidecarBaseUrl}/api/cockpit/landing?view=${encodeURIComponent(view)}`,
    );
    if (!resp.ok) return false;
    data = (await resp.json()) as LandingPayload;
  } catch { return false; }
  if (!data || !data.known) return false;

  // `hidden = false` + `placeholder.hidden = true`, exactly as every other
  // virtual page does. Without the pair the section renders into a doc view
  // the stage is still hiding: the DOM is right, `.view-landing` is present
  // and correct, and the pane is **blank**. Found by taking a screenshot after
  // a run of DOM assertions had all passed — which is the argument for looking
  // at a surface rather than querying it.
  docView.replaceChildren();
  docView.hidden = false;
  placeholder.hidden = true;
  const page = document.createElement('section');
  page.className = 'view-landing';
  page.dataset.view = view;

  const head = document.createElement('h1');
  head.className = 'view-landing-head';
  head.textContent = VIEW_LABELS[view] ?? view;
  page.appendChild(head);

  if (data.total === 0) {
    const quiet = LANDING_QUIET[view] ?? {
      head: 'Nothing owed here.', note: '',
    };
    const line = document.createElement('p');
    line.className = 'view-landing-quiet';
    line.textContent = quiet.head;
    page.appendChild(line);
    if (quiet.note) {
      const note = document.createElement('p');
      note.className = 'meta';
      note.textContent = quiet.note;
      page.appendChild(note);
    }
    docView.appendChild(page);
    return true;
  }

  const lead = document.createElement('p');
  lead.className = 'view-landing-lead';
  lead.textContent = `${data.total} need${data.total === 1 ? 's' : ''} you here.`;
  page.appendChild(lead);

  for (const group of data.groups) {
    if (!group.count) continue;
    const section = document.createElement('div');
    section.className = 'view-landing-group';
    const gh = document.createElement('div');
    gh.className = 'view-landing-group-head';
    // The registry's verb and noun, never "items" (ISS-0133's rule, applied
    // to the page the badge opens rather than only to the tooltip).
    gh.textContent = group.label;
    section.appendChild(gh);

    if (group.items.length === 0) {
      // A counted group with no rows: the standing-document obligation, whose
      // subject is a manifest entry rather than a note. Say where it lives
      // instead of rendering an empty list under a number.
      const where = document.createElement('p');
      where.className = 'meta';
      where.textContent = 'Listed under “What this project is” on the left.';
      section.appendChild(where);
      page.appendChild(section);
      continue;
    }

    const list = document.createElement('ul');
    list.className = 'view-landing-list';
    for (const item of group.items) {
      const li = document.createElement('li');
      const row = document.createElement('button');
      row.type = 'button';
      row.className = 'view-landing-row';
      const id = document.createElement('span');
      id.className = 'view-landing-id mono';
      id.textContent = shortNoteId(item.id);
      id.title = item.id;
      row.appendChild(id);
      const title = document.createElement('span');
      title.className = 'view-landing-title';
      title.textContent = item.title;
      title.title = item.title;
      row.appendChild(title);
      appendIf(row, statusChip(item.status));
      // Straight to the note that carries the actuator, so the verb named
      // above is the verb available when you arrive.
      row.addEventListener('click', () => void navigateTo(item.rel));
      li.appendChild(row);
      list.appendChild(li);
    }
    section.appendChild(list);
    page.appendChild(section);
  }

  docView.appendChild(page);
  return true;
}

async function renderDesignPage(target: string): Promise<boolean> {
  if (!sidecarBaseUrl) return false;
  const designs = await fetchDesignRegister();
  docView.classList.remove('overview-pane', 'agents-page', 'review-page',
    'is-design-shell');
  docView.classList.add('design-page');
  rightPaneContent.replaceChildren();
  // A design note has real links — DES-0002 names DES-0001, TST-0019,
  // ISS-0023 and REQ-0022 — and clearing the pane without refilling it made
  // every one of them invisible on the surface built to show the design
  // (Edwin, 2026-07-28). The context endpoint already answers this for any
  // note; the design page simply never asked.

  if (!target) {
    // Identity first: what this is, before what it should look like.
    const brief = await fetchBrief();
    const parts: HTMLElement[] = [];
    const band = buildIdentityBand(brief);
    if (band) parts.push(band);
    parts.push(buildDesignRegisterList(designs));
    docView.replaceChildren(...parts);
    docView.hidden = false;
    placeholder.hidden = true;
    return true;
  }
  const d = designs.find((x) => x.id === target);
  if (!d) {
    docView.classList.remove('is-design-shell');
    docView.replaceChildren(buildDesignRegisterList(designs));
    showStatus(`No design ${target}`, 'error');
    docView.hidden = false;
    placeholder.hidden = true;
    return true;
  }
  await fetchDesignRevisions(d.id);
  void loadRightPane(d.rel);
  designCompareSha = null;
  const paint = () => {
    // App-shell, not a document (ISS-0039). The page itself does not scroll:
    // the head pins, the stage takes the rest of the height, and the artifact
    // frame is the only scroller for the artifact. Revisions and rationale go
    // in a sidebar that scrolls on its own, so nothing ever ends up inside
    // the artifact's scroller.
    const root = document.createElement('div');
    root.className = 'design-view is-shell';
    const body = document.createElement('div');
    body.className = 'design-body';
    if (designCompareSha) {
      // Side by side: the working copy against the chosen revision, both at
      // the same viewport — comparing two renders at different sizes would
      // show the layout changing rather than the design.
      body.classList.add('is-compare');
      body.append(buildDesignFrame(d), buildDesignFrame(d, designCompareSha));
    } else if ((d.variants ?? []).length && !d.has_asset) {
      // A note with variants and no artifact IS its variants — the strip is
      // the stage rather than an addition to it (TASK-0301). With an artifact
      // present the artifact stays the subject and the strip goes beneath.
      const strip = buildVariantStrip(
        d.variants ?? [], d.stylesheets ?? [], d.variant_scripts === true,
        d.id, d.chosen_variant ?? '',
      );
      if (strip) body.append(strip);
      else body.append(buildDesignFrame(d));
    } else {
      body.append(buildDesignFrame(d));
      const strip = buildVariantStrip(
        d.variants ?? [], d.stylesheets ?? [], d.variant_scripts === true,
        d.id, d.chosen_variant ?? '',
      );
      if (strip) body.append(strip);
    }
    // `Annotate` — FEAT-0069. On the design page rather than a global verb:
    // an annotation is always about a design, and offering it elsewhere would
    // invite anchors to things that have no revisions to be lost across.
    const annotate = document.createElement('button');
    annotate.type = 'button';
    annotate.className = 'review-btn';
    annotate.textContent = 'Annotate selection';
    annotate.title = 'Comment on the selected text, anchored to the quote';
    annotate.addEventListener('click', () => annotationFromSelection(d.id));
    body.appendChild(annotate);

    const side = document.createElement('aside');
    side.className = 'design-side';
    side.hidden = !designSideOpen;
    side.append(buildDesignRevisionRail(d, paint));
    const rationale = buildDesignRationale(d);
    if (rationale) side.append(rationale);

    const stage = document.createElement('div');
    stage.className = 'design-shell-body';
    stage.append(body, side);

    const head = buildDesignHeader(d, paint);
    // Offer this design for review WITHOUT touching its status (TASK-0229).
    // The desk had two doors and designs could only use the status one, so a
    // design that was genuinely `implemented` could never be put in front of a
    // human without changing its status to something untrue.
    const ask = document.createElement('button');
    ask.type = 'button';
    ask.className = 'design-ask-review';
    ask.textContent = 'Ask for review';
    ask.addEventListener('click', () => {
      ask.disabled = true;
      void (async () => {
        try {
          const resp = await fetch(`${sidecarBaseUrl}/api/design/offer-review`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: d.id }),
          });
          const data = await resp.json();
          if (!resp.ok || data.ok === false) {
            showStatus(`Could not offer ${d.id}: ${data.error || resp.status}`, 'error');
            ask.disabled = false;
            return;
          }
          // Idempotent server-side; say which happened rather than pretending
          // a second press did something.
          showStatus(data.already_open
            ? `${d.id} is already waiting in Review`
            : `${d.id} sent to Review`, 'info');
          ask.textContent = 'Waiting in Review';
          void refreshReviewBadge();
        } catch (err) {
          showStatus(`Could not offer ${d.id}: ${String(err)}`, 'error');
          ask.disabled = false;
        }
      })();
    });
    head.append(ask);
    // The toggle lives in the head so it is reachable whether or not the
    // sidebar is showing — a control that disappears with the thing it
    // controls cannot bring it back.
    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'design-side-toggle';
    const labelToggle = () => {
      toggle.textContent = designSideOpen ? 'Hide details ›' : '‹ Show details';
      toggle.setAttribute('aria-expanded', String(designSideOpen));
    };
    labelToggle();
    toggle.addEventListener('click', () => {
      setDesignSideOpen(!designSideOpen);
      side.hidden = !designSideOpen;
      labelToggle();
    });
    head.append(toggle);

    root.append(head, stage);
    docView.replaceChildren(root);
    // The register scrolls; a stage does not. Toggled per render because the
    // same element carries both.
    docView.classList.add('is-design-shell');
  };
  paint();
  docView.hidden = false;
  placeholder.hidden = true;
  return true;
}

async function renderReviewPage(target: string): Promise<boolean> {
  if (!sidecarBaseUrl) return false;
  const payload = await fetchReviewQueue();
  if (!payload) {
    showStatus('Review queue unavailable', 'error');
    return false;
  }
  reviewQueue = payload;
  reviewSelection = target;
  renderReviewQueuePane(payload);
  void refreshReviewBadge();

  docView.classList.remove('overview-pane', 'agents-page',
    'design-page', 'is-design-shell');
  docView.classList.add('review-page');
  rightPaneContent.replaceChildren();

  if (!target) {
    docView.replaceChildren(buildReviewEmpty(payload));
    docView.hidden = false;
    placeholder.hidden = true;
    return true;
  }

  let detail: ReviewDetail | null = null;
  try {
    const resp = await fetch(
      `${sidecarBaseUrl}/api/cockpit/review/${encodeURIComponent(target)}`,
    );
    if (resp.ok) detail = (await resp.json()) as ReviewDetail;
  } catch { /* handled below */ }
  if (!detail) {
    docView.replaceChildren(buildReviewEmpty(payload, `Nothing found for ${target}.`));
    docView.hidden = false;
    placeholder.hidden = true;
    return true;
  }

  if (detail.kind === 'question') {
    docView.replaceChildren(buildQuestionView(detail));
  } else if (detail.request && detail.request.subject_missing) {
    // The design was deleted or renamed after being offered. Accept and
    // Reject both post to /api/notes/review for an id that no longer
    // resolves, 404, and never reach review-resolve — so the row was
    // unclearable except by hand-editing the ledger (ISS-0056). Offer the
    // one action that can honestly be taken.
    docView.replaceChildren(buildOrphanedRequestView(detail));
  } else if (detail.request && detail.subject_type === 'design') {
    // A design must NOT go through the proposal path: that stamps
    // `plan-accepted` with no revision, and rejects by writing
    // `status: cancelled` onto a design that may be `implemented`.
    // TASK-0218 built /api/design/verdict precisely so a verdict names the
    // revision it judged; this is what calls it (ISS-0056).
    docView.replaceChildren(buildDesignReviewView(detail));
  } else if (detail.request) {
    docView.replaceChildren(buildProposalView(detail));
  } else if (detail.note) {
    docView.replaceChildren(buildSingleNoteReview(detail));
  }
  docView.hidden = false;
  placeholder.hidden = true;
  return true;
}

function buildReviewEmpty(
  payload: ReviewQueuePayload, message?: string,
): HTMLElement {
  const wrap = document.createElement('section');
  wrap.className = 'review-empty';
  const h = document.createElement('h2');
  h.textContent = payload.total > 0
    ? 'Pick something from the queue' : 'Nothing waiting on you';
  const p = document.createElement('p');
  p.className = 'meta';
  p.textContent = message ?? (payload.total > 0
    // 'item needs' / 'items need' — the noun was pluralised and the verb was not.
    ? `${payload.total} item${payload.total === 1 ? ' needs' : 's need'} a human.`
    : 'Proposals, questions and pending test runs appear here as they arrive.');
  wrap.append(h, p);
  return wrap;
}

function renderReviewQueuePane(payload: ReviewQueuePayload): void {
  wsNavPlaceholder.hidden = true;
  wsNavContent.hidden = false;
  const wrap = document.createElement('div');
  wrap.className = 'scope-pane review-queue';

  const head = document.createElement('h4');
  head.className = 'scope-heading';
  head.textContent = payload.total > 0 ? `Queue · ${payload.total}` : 'Queue';
  wrap.appendChild(head);

  for (const group of payload.groups) {
    if (group.items.length === 0) continue;
    const label = document.createElement('h4');
    label.className = 'scope-heading';
    label.textContent = `${group.label} · ${group.items.length}`;
    wrap.appendChild(label);
    for (const item of group.items) {
      wrap.appendChild(buildQueueRow(item, group.key));
    }
  }
  if (payload.total === 0) {
    const empty = document.createElement('p');
    empty.className = 'meta review-queue-empty';
    empty.textContent = 'Nothing is waiting on you — proposals, questions and manual test runs appear here.';
    wrap.appendChild(empty);
  }

  // The ADR-0007 advisory-phase tally used to render here, between the
  // queue and the registers. Removed by TASK-0247: the ADR is settled
  // (stay advisory, permanently), so the instrument it fed has no
  // consumer, and it was the only non-interactive block in a pane of
  // clickable rows — which is how Edwin came to ask what it was for
  // (ISS-0064).
  //
  // The store still records outcomes on resolve() and the payload still
  // carries `outcomes`/`reviewed`. That is the ledger's own record of
  // what the desk did, and what a reopened gating question would read;
  // what was retired is the obligation to watch it, not the data.

  // The registers (FEAT-0049). The queue is what is waiting; these are
  // what exists. A desk with an empty queue used to say nothing at all.
  //
  // Order is Queue → Reviewed → Tests, and it is load-bearing (asserted
  // by TST-0022) because both are appended at the tail of this function:
  // positional, so the next append in the obvious place would reshuffle
  // the pane with nothing failing. Tests goes last — it is the least
  // time-sensitive thing here, a browsable list of what gets verified
  // rather than a record of what happened (Edwin's call).
  // Owed work first, then the tests register, then finished work last —
  // "completed at the bottom" is the same ordering the other three
  // navigators use, and `buildReviewedRegister` emits both halves.
  const reviewed = buildReviewedRegister(payload.registers?.reviewed ?? []);
  const owed = reviewed?.querySelector('.review-completed')
    ? (() => {
        const band = reviewed.querySelector('.review-completed')!;
        band.remove();
        return { top: reviewed, bottom: band };
      })()
    : { top: reviewed, bottom: null };
  appendIf(wrap, owed.top && owed.top.childElementCount > 0 ? owed.top : null);
  appendIf(wrap, buildTestsRegister(payload.registers?.tests ?? []));
  appendIf(wrap, owed.bottom as HTMLElement | null);
  wsNavContent.replaceChildren(wrap);
}

// Every acceptance test, not the `runs` queue slice above — that one is
// gated to manual tests at `ready` (about one row of twenty-two here).
// "What is waiting on me" and "what do we verify" are different
// questions and both belong on the desk.
function buildTestsRegister(tests: ReviewRegisterTest[]): HTMLElement | null {
  if (tests.length === 0) return null;
  const passing = tests.filter(
    (t) => (t.status || '').toLowerCase() === 'passing',
  ).length;
  const section = document.createElement('div');
  section.className = 'review-register';
  const head = document.createElement('div');
  head.className = 'scope-heading';
  head.textContent = `Tests · ${passing}/${tests.length}`;
  section.appendChild(head);
  // Non-passing first: those are the ones worth reading, the rest are
  // the denominator.
  const ordered = [...tests].sort((a, b) => {
    const ap = (a.status || '').toLowerCase() === 'passing' ? 1 : 0;
    const bp = (b.status || '').toLowerCase() === 'passing' ? 1 : 0;
    return ap - bp || a.id.localeCompare(b.id);
  });
  for (const t of ordered) {
    const row = document.createElement('button');
    row.type = 'button';
    row.className = 'queue-row register-row';
    const id = document.createElement('span');
    id.className = 'mono ov-typed';
    id.dataset.type = 'test';
    // Display handle only (ISS-0084). The review desk was the one
    // surface the shortening had not reached — the third time in this
    // phase a change landed in some renderers and not all of them.
    id.textContent = shortNoteId(t.id);
    id.title = t.id;
    const title = document.createElement('span');
    title.className = 'queue-title';
    title.textContent = t.title;
    title.title = t.title;
    row.append(id, title);
    appendIf(row, statusChip(t.status));
    if (t.manual) {
      const m = document.createElement('span');
      m.className = 'queue-age';
      m.textContent = 'manual';
      m.title = 'Run from the desk; no automated command';
      row.appendChild(m);
    }
    row.addEventListener('click', () => void navigateTo(`/docs/${t.rel}`));
    section.appendChild(row);
  }
  return section;
}

/** True when a verdict leaves work owed (TASK-0277).
 *
 *  `changes-requested` means a reviewer asked for something and nothing
 *  has recorded it happening. Counting it as finished is a
 *  terminal-looking label on an open obligation — the error this whole
 *  phase exists to have removed.
 *
 *  `accepted` and `approved` both appear in this corpus and are both read
 *  as finished; reconciling them is ISS-0069's problem, not this one's.
 */
/** Whether a register row still owes work.
 *
 *  Reads the server's `owed` flag rather than re-deriving it. The verdict
 *  alone was the ISS-0121 defect: `review_verdict` is sticky, so all ten
 *  rows the desk headed `Changes requested` were terminal and none was
 *  owed. The discriminator is the subject's current status, and it lives
 *  in one module (`cockpit.py:_verdict_is_owed`) rather than here — the
 *  ISS-0023 rule.
 *
 *  Falls back to `false` when the field is absent: an older sidecar that
 *  does not send it should under-report rather than resurrect ten false
 *  obligations. */
function isOwedVerdict(item: ReviewRegisterReviewed): boolean {
  return item.owed === true;
}

// Sourced from note frontmatter, not the store — `_MAX_REQUESTS` trims
// the store's tail, so a store-backed register would quietly forget.
function buildReviewedRegister(
  items: ReviewRegisterReviewed[],
): HTMLElement | null {
  if (items.length === 0) return null;
  const section = document.createElement('div');
  section.className = 'review-register';

  // TASK-0277. `Reviewed · 82` already WAS this desk's completed section;
  // it only lacked the shape. But 10 of the 82 are `changes-requested` —
  // a reviewer asked for work and nothing records it having happened.
  //
  // Filing those under "reviewed" is the same error the old
  // Hide-completed switch made: a terminal-looking label on something
  // still owed. They are promoted to sit with the live work; the rest
  // collapse into one card per verdict.
  const owed = items.filter(isOwedVerdict);
  const settled = items.filter((i) => !isOwedVerdict(i));

  const renderRow = (item: ReviewRegisterReviewed): HTMLElement => {
    const row = document.createElement('button');
    row.type = 'button';
    row.className = 'queue-row register-row';
    const id = document.createElement('span');
    id.className = 'mono ov-typed';
    id.dataset.type = item.type;
    // Display handle only (ISS-0084).
    id.textContent = shortNoteId(item.id);
    id.title = item.id;
    const title = document.createElement('span');
    title.className = 'queue-title';
    title.textContent = item.title;
    title.title = item.reviewed_by
      ? `${item.title}\nreviewed by ${item.reviewed_by}` : item.title;
    row.append(id, title);
    const date = document.createElement('span');
    date.className = 'queue-age';
    date.textContent = item.review_date || '';
    row.appendChild(date);
    row.addEventListener('click', () => void navigateTo(`/docs/${item.rel}`));
    return row;
  };

  if (owed.length > 0) {
    const head = document.createElement('div');
    head.className = 'scope-heading';
    head.textContent = `Changes requested · ${owed.length}`;
    section.appendChild(head);
    for (const item of owed) section.appendChild(renderRow(item));
  }

  if (settled.length > 0) {
    // One card per verdict, all shut — the same shape the other three
    // navigators use for finished work.
    const byVerdict = new Map<string, ReviewRegisterReviewed[]>();
    for (const item of settled) {
      const key = (item.verdict || 'unrecorded').toLowerCase();
      const list = byVerdict.get(key);
      if (list) list.push(item); else byVerdict.set(key, [item]);
    }
    const band = document.createElement('div');
    band.className = 'review-completed';
    const head = document.createElement('div');
    head.className = 'scope-heading';
    head.textContent = `Completed · ${byVerdict.size}`;
    band.appendChild(head);
    for (const [verdict, list] of [...byVerdict].sort((a, b) => b[1].length - a[1].length)) {
      const card = document.createElement('details');
      card.className = 'right-pane-group ctx-card';
      const summary = document.createElement('summary');
      summary.className = 'ctx-card-head';
      const chev = document.createElement('span');
      chev.className = 'ov-chev';
      chev.setAttribute('aria-hidden', 'true');
      const name = document.createElement('span');
      name.textContent = verdict;
      const count = document.createElement('span');
      count.className = 'ctx-card-right';
      count.textContent = String(list.length);
      summary.append(chev, name, count);
      card.appendChild(summary);
      const body = document.createElement('div');
      for (const item of list) body.appendChild(renderRow(item));
      card.appendChild(body);
      band.appendChild(card);
    }
    section.appendChild(band);
  }
  return section;
}

function buildQueueRow(item: ReviewQueueItem, groupKey: string): HTMLElement {
  const key = item.request_id || item.id || '';
  const row = document.createElement('button');
  row.type = 'button';
  row.className = 'queue-row' + (key === reviewSelection ? ' current' : '');

  const kind = document.createElement('span');
  const kindKey = item.kind || (groupKey === 'runs' ? 'run' : 'review');
  kind.className = `queue-kind is-${kindKey}`;
  kind.textContent = KIND_LABEL[kindKey] || kindKey;
  row.appendChild(kind);

  const title = document.createElement('span');
  title.className = 'queue-title';
  title.textContent = item.id
    ? `${shortNoteId(item.id)} ${item.title ?? ''}`.trim()
    : (item.title || '(untitled)');
  if (item.id) title.title = item.id;
  row.appendChild(title);

  const age = document.createElement('span');
  age.className = 'queue-age';
  age.textContent = item.ts ? relativeAge(item.ts) : (item.status || '');
  row.appendChild(age);

  row.addEventListener('click', () => {
    // A `run` row leaves the desk for the Tests view (TASK-0372). The desk's
    // own queue is the last caller pointed at the new route rather than
    // through the redirect: the redirect exists for links already in
    // somebody's history, not as an indirection every click goes through.
    void navigateTo(kindKey === 'run' ? `~tests/${key}/run` : `~review/${key}`);
  });
  return row;
}

function relativeAge(iso: string): string {
  const then = Date.parse(iso);
  if (Number.isNaN(then)) return '';
  const mins = Math.max(0, Math.round((Date.now() - then) / 60000));
  if (mins < 60) return `${mins}m`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `${hours}h`;
  return `${Math.round(hours / 24)}d`;
}

// ----- Proposal set review (TASK-0207) ----------------------------------

function buildReviewHeader(
  kind: string, title: string, status: string | undefined,
  actions: HTMLElement | null, sub?: string,
): HTMLElement {
  const head = document.createElement('header');
  head.className = 'review-head';
  const kindEl = document.createElement('span');
  kindEl.className = `queue-kind is-${kind}`;
  kindEl.textContent = KIND_LABEL[kind] || kind;
  const h = document.createElement('h2');
  h.textContent = title;
  head.append(kindEl, h);
  appendIf(head, statusChip(status));
  if (actions) head.appendChild(actions);
  const wrap = document.createElement('div');
  wrap.appendChild(head);
  if (sub) {
    const p = document.createElement('p');
    p.className = 'review-sub';
    p.textContent = sub;
    wrap.appendChild(p);
  }
  return wrap;
}

function buildProposalView(detail: ReviewDetail): HTMLElement {
  const request = detail.request!;
  const items = detail.items ?? [];
  const wrap = document.createElement('div');
  wrap.className = 'review-body';

  const ticks = new Map<string, boolean>();
  for (const item of items) ticks.set(item.id, true);

  const actions = document.createElement('div');
  actions.className = 'review-actions';
  const accept = document.createElement('button');
  accept.type = 'button';
  accept.className = 'review-btn is-good';
  accept.textContent = 'Accept set';
  const changes = document.createElement('button');
  changes.type = 'button';
  changes.className = 'review-btn is-primary';
  changes.textContent = 'Request changes';
  const reject = document.createElement('button');
  reject.type = 'button';
  reject.className = 'review-btn is-bad';
  reject.textContent = 'Reject';
  actions.append(accept, changes, reject);

  const provenance = [
    request.agent ? `proposed by ${request.agent}` : '',
    request.session_id ? `session ${String(request.session_id).slice(0, 8)}` : '',
    request.ts ? `${relativeAge(request.ts)} ago` : '',
    'review requested via the dispatch ledger',
  ].filter(Boolean).join(' · ');

  wrap.appendChild(buildReviewHeader(
    'review', request.title || 'Proposal set', undefined, actions, provenance,
  ));

  if (request.body) {
    const blurb = document.createElement('p');
    blurb.className = 'review-blurb';
    blurb.textContent = request.body;
    wrap.appendChild(blurb);
  }

  const list = document.createElement('section');
  list.className = 'review-set';
  const listHead = document.createElement('h3');
  listHead.className = 'review-set-head';
  const listLabel = document.createElement('span');
  listLabel.textContent = `Proposed set · ${items.length} item${items.length === 1 ? '' : 's'}`;
  listHead.appendChild(listLabel);
  list.appendChild(listHead);

  for (const item of items) {
    const row = document.createElement('div');
    row.className = 'review-set-row';
    const box = document.createElement('button');
    box.type = 'button';
    box.className = 'review-tick is-on';
    box.setAttribute('aria-pressed', 'true');
    box.textContent = '✓';
    box.addEventListener('click', () => {
      const next = !ticks.get(item.id);
      ticks.set(item.id, next);
      box.classList.toggle('is-on', next);
      box.setAttribute('aria-pressed', String(next));
      row.classList.toggle('is-off', !next);
    });
    const id = document.createElement('span');
    id.className = 'mono ov-typed';
    if (item.type) id.dataset.type = item.type;
    // Display handle only (ISS-0084). The review desk was the one
    // surface the shortening had not reached — the third time in this
    // phase a change landed in some renderers and not all of them.
    id.textContent = shortNoteId(item.id);
    id.title = item.id;
    const title = document.createElement('span');
    title.className = 'review-set-title';
    title.textContent = item.title || '';
    row.append(box, id, title);
    appendIf(row, statusChip(item.status));

    // Every row expands to the note it proposes. Accepting a set of five
    // tasks means reading five task notes; the first cut showed titles
    // and tick-boxes only, so a set was approved as blind as a lone note
    // was (reported 2026-07-26).
    const peek = document.createElement('button');
    peek.type = 'button';
    peek.className = 'review-peek';
    peek.setAttribute('aria-expanded', 'false');
    peek.title = 'Show this note';
    const noteBody = document.createElement('div');
    noteBody.className = 'review-note review-note-inline';
    noteBody.hidden = true;
    let loaded = false;
    peek.addEventListener('click', () => {
      const opening = noteBody.hidden;
      noteBody.hidden = !opening;
      peek.classList.toggle('is-open', opening);
      peek.setAttribute('aria-expanded', String(opening));
      if (opening && !loaded && item.rel) {
        loaded = true;
        void fillReviewNoteBody(noteBody, item.rel);
      }
    });
    row.appendChild(peek);
    if (item.rel) {
      title.style.cursor = 'pointer';
      title.addEventListener('click', () => void navigateTo(item.rel!));
    }
    list.append(row, noteBody);
  }

  // Reading five notes one click at a time is worse than reading five
  // notes; offer the whole set at once.
  const expandAll = document.createElement('button');
  expandAll.type = 'button';
  expandAll.className = 'review-expand-all';
  expandAll.textContent = 'Show all notes';
  expandAll.addEventListener('click', () => {
    const opening = expandAll.textContent === 'Show all notes';
    list.querySelectorAll<HTMLButtonElement>('.review-peek').forEach((btn) => {
      if (btn.classList.contains('is-open') !== opening) btn.click();
    });
    expandAll.textContent = opening ? 'Hide all notes' : 'Show all notes';
  });
  listHead.appendChild(expandAll);
  wrap.appendChild(list);

  const comment = document.createElement('textarea');
  comment.className = 'review-comment';
  comment.rows = 2;
  comment.placeholder =
    'Optional note back to the agent — sent with Request changes, recorded with Accept.';
  wrap.appendChild(comment);

  const feedback = document.createElement('p');
  feedback.className = 'review-feedback';
  feedback.hidden = true;
  wrap.appendChild(feedback);

  const setBusy = (busy: boolean): void => {
    for (const btn of [accept, changes, reject]) btn.disabled = busy;
  };
  const say = (text: string, error = false): void => {
    feedback.textContent = text;
    feedback.hidden = false;
    feedback.classList.toggle('is-error', error);
  };

  accept.addEventListener('click', () => {
    const ticked = items.filter((i) => ticks.get(i.id));
    if (ticked.length === 0) { say('Nothing ticked to accept.', true); return; }
    setBusy(true);
    void acceptProposalSet(request, ticked, comment.value, items.length)
      .then((msg) => { say(msg); void refreshReviewBadge(); })
      .catch((err: Error) => { say(err.message, true); setBusy(false); });
  });
  reject.addEventListener('click', () => {
    setBusy(true);
    void rejectProposalSet(request, items, comment.value)
      .then((msg) => { say(msg); void refreshReviewBadge(); })
      .catch((err: Error) => { say(err.message, true); setBusy(false); });
  });
  changes.addEventListener('click', () => {
    const unticked = items.filter((i) => !ticks.get(i.id));
    setBusy(true);
    void requestChanges(request, unticked, comment.value)
      .then((msg) => { say(msg); void refreshReviewBadge(); })
      .catch((err: Error) => { say(err.message, true); setBusy(false); });
  });
  return wrap;
}

async function postJson(path: string, body: unknown): Promise<Record<string, unknown>> {
  const resp = await fetch(`${sidecarBaseUrl}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = (await resp.json().catch(() => ({}))) as Record<string, unknown>;
  if (!resp.ok || data.ok === false) {
    throw new Error(String(data.error || `HTTP ${resp.status}`));
  }
  return data;
}

/** A design offered for review, judged through the design verdict path.
 *
 *  Follows the shape every other review entry already has, rather than
 *  inventing one beside it: `buildReviewHeader` with the actions **in the
 *  header**, a `.review-comment` box for the note back, and the content
 *  itself on the page. Three separate corrections got it here, and the first
 *  two were both mistakes this file had already made and written down —
 *  `buildSingleNoteReview` carries the comment "the first cut rendered a
 *  header, buttons and nothing else — asking for approval of content it never
 *  showed (reported 2026-07-26)", which is precisely what my first cut did.
 *
 *  What is genuinely different: the verdict names the revision it judged, the
 *  frame renders THAT revision rather than the working copy, and rejecting
 *  goes through the design endpoint so a built design is not cancelled by a
 *  status posted from the client.
 */
function buildDesignReviewView(detail: ReviewDetail): HTMLElement {
  const request = detail.request as ReviewQueueItem;
  const wrap = document.createElement('div');
  wrap.className = 'review-body design-review';

  const note: { id: string; title?: string; rel?: string; status?: string } =
    (detail.items && detail.items[0]) || { id: request.subject || '' };
  const comment = document.createElement('textarea');
  comment.className = 'review-comment';
  comment.rows = 2;
  comment.placeholder =
    'Optional note for the record — sent with Request changes, recorded with Accept.';

  const act = async (
    verdict: string, accept: boolean | null, outcome: string | null, said: string,
  ) => {
    try {
      const res = await postJson('/api/design/verdict', {
        id: note.id, reviewer: 'user:edwin', verdict,
        revision: detail.at_revision, accept,
      });
      if (res && (res as { ok?: boolean }).ok === false) {
        showStatus(`Could not record: ${(res as { error?: string }).error}`, 'error');
        return;
      }
      // `outcome: null` = Request changes, which leaves the request open,
      // exactly as the proposal path does.
      if (outcome && request.request_id) {
        await postJson('/api/cockpit/review-resolve', {
          request_id: request.request_id, outcome, note: comment.value,
        });
      }
      showStatus(said, 'info');
      void navigateTo('~review');
    } catch (err) {
      showStatus(`Could not record: ${String(err)}`, 'error');
    }
  };

  const actions = document.createElement('div');
  actions.className = 'review-actions';
  const btn = (label: string, cls: string, run: () => void) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = cls;
    b.textContent = label;
    b.addEventListener('click', run);
    actions.append(b);
    return b;
  };
  btn('Accept this revision', 'review-btn is-good', () => {
    void act('accepted', true, 'accepted',
             `${note.id} accepted at ${detail.at_revision}.`);
  });
  btn('Request changes', 'review-btn is-primary', () => {
    void (async () => {
      // The comment is the whole point of requesting changes, and the
      // placeholder promises it is sent. The first cut recorded a verdict and
      // silently dropped the text (ISS-0056 round 2). It goes on the note as a
      // document-level design comment, which is where TASK-0217 puts review
      // prose so it survives without the tool.
      const text = comment.value.trim();
      if (text) {
        try {
          await postJson('/api/design/comment', {
            id: note.id, region: '', text, author: 'user:edwin',
          });
        } catch (err) {
          showStatus(`Comment not saved: ${String(err)}`, 'error');
          return;
        }
      }
      await act('changes-requested', null, null,
                `Changes requested on ${note.id}; it stays in the queue.`);
    })();
  });
  btn('Reject', 'review-btn is-bad', () => {
    void act('rejected', false, 'rejected',
             `${note.id} rejected at ${detail.at_revision}.`);
  });

  const provenance = [
    `revision ${detail.at_revision || '(none)'}`,
    request.ts ? `${relativeAge(request.ts)} ago` : '',
    'offered for review from the design surface',
  ].filter(Boolean).join(' · ');
  wrap.appendChild(buildReviewHeader(
    'review', note.title ? `${note.id} — ${note.title}` : String(note.id),
    note.status, actions, provenance,
  ));

  if (detail.revision_moved) {
    const warn = document.createElement('p');
    warn.className = 'review-stale';
    warn.textContent = `The artifact has moved since you were asked: head is now `
      + `${detail.head_revision}. A verdict here judges ${detail.at_revision}.`;
    wrap.append(warn);
  }
  if (request.dirty_at_offer) {
    const d0 = document.createElement('p');
    d0.className = 'review-stale';
    d0.textContent = 'This design had uncommitted changes when it was offered, '
      + 'so the person who offered it may have been looking at edits that '
      + `${detail.at_revision} does not contain.`;
    wrap.append(d0);
  } else if (detail.dirty) {
    const d1 = document.createElement('p');
    d1.className = 'review-stale';
    d1.textContent = 'The working copy has uncommitted changes now. They are '
      + 'not part of what you are reviewing here.';
    wrap.append(d1);
  }

  // The artifact, at the revision under review — not the working copy.
  const stage = document.createElement('div');
  stage.className = 'review-design-stage';
  const pending = document.createElement('p');
  pending.className = 'meta';
  pending.textContent = 'Loading the reviewed revision…';
  stage.append(pending);
  wrap.append(stage);
  void (async () => {
    const designs = await fetchDesignRegister();
    const d = designs.find((x) => x.id === note.id);
    if (!d) {
      pending.textContent = `${note.id} is no longer in the design register.`;
      return;
    }
    // `has_asset` is an `is_file()` on the WORKING COPY, so it must not gate a
    // historical render: an artifact deleted after being offered still renders
    // fine at the revision under review (ISS-0056 round 2). Without a revision
    // there is nothing but the working copy to fall back on.
    if (!d.has_asset && !detail.at_revision) {
      pending.textContent = `${note.id} declares no artifact — there is nothing to show.`;
      return;
    }
    stage.replaceChildren(buildDesignFrame(d, detail.at_revision || undefined));
  })();

  // The note's prose as well: the artifact is what it looks like, the note is
  // why. `buildSingleNoteReview` mounts the body inline for the same reason.
  if (note.rel) {
    const body = document.createElement('section');
    body.className = 'review-note';
    wrap.appendChild(body);
    void fillReviewNoteBody(body, note.rel);
  }

  wrap.append(comment);
  return wrap;
}

/** A request whose subject no longer exists. */
function buildOrphanedRequestView(detail: ReviewDetail): HTMLElement {
  const request = detail.request as ReviewQueueItem;
  const root = document.createElement('div');
  root.className = 'review-body';
  const h = document.createElement('h2');
  h.textContent = String(request.subject || 'Unknown subject');
  root.append(h);
  const p = document.createElement('p');
  p.className = 'review-stale';
  p.textContent = `${request.subject} no longer exists — it was deleted or `
    + `renamed after being offered for review. There is nothing left to judge, `
    + `so the only honest action is to clear the request.`;
  root.append(p);
  const actions = document.createElement('div');
  actions.className = 'review-actions';
  const dismiss = document.createElement('button');
  dismiss.type = 'button';
  dismiss.className = 'review-btn is-bad';
  dismiss.textContent = 'Clear this request';
  dismiss.addEventListener('click', () => {
    void (async () => {
      // Resolves the LEDGER only. No note is written, because there is no
      // note — the previous behaviour posted to /api/notes/review, got 404,
      // and never reached this call, wedging the row forever.
      await postJson('/api/cockpit/review-resolve', {
        request_id: request.request_id, outcome: 'rejected',
        note: 'subject no longer exists',
      });
      showStatus('Request cleared.', 'info');
      void navigateTo('~review');
    })();
  });
  actions.append(dismiss);
  root.append(actions);
  return root;
}

async function acceptProposalSet(
  request: ReviewQueueItem,
  ticked: Array<{ id: string }>,
  note: string,
  total: number,
): Promise<string> {
  for (const item of ticked) {
    await postJson('/api/notes/review', {
      id: item.id,
      reviewer: 'user:edwin',
      // Deliberately NOT `approved`: that is close-out's verdict, and a
      // plan acceptance must never satisfy the verification gate.
      verdict: 'plan-accepted',
    });
  }
  const amended = ticked.length < total;
  if (request.request_id) {
    await postJson('/api/cockpit/review-resolve', {
      request_id: request.request_id,
      outcome: amended ? 'accepted-amended' : 'accepted',
      note,
    });
  }
  return amended
    ? `Accepted ${ticked.length} of ${total} — the rest were left untouched.`
    : `Accepted all ${total} items.`;
}

async function rejectProposalSet(
  request: ReviewQueueItem,
  items: Array<{ id: string }>,
  note: string,
): Promise<string> {
  for (const item of items) {
    await postJson('/api/notes/review', {
      id: item.id, reviewer: 'user:edwin',
      // A rejection records a rejection. An earlier cut stamped
      // `plan-accepted` alongside `cancelled` because the endpoint took
      // only one verdict, which left the durable record reading as an
      // acceptance (independent review, 2026-07-26).
      verdict: 'plan-rejected', status: 'cancelled',
    });
  }
  if (request.request_id) {
    await postJson('/api/cockpit/review-resolve', {
      request_id: request.request_id, outcome: 'rejected', note,
    });
  }
  return `Rejected — ${items.length} item${items.length === 1 ? '' : 's'} cancelled.`;
}

async function requestChanges(
  request: ReviewQueueItem,
  unticked: Array<{ id: string; title?: string }>,
  note: string,
): Promise<string> {
  // The round-trip is the dispatch queue (TASK-0208): the comment plus
  // the rows that were not accepted go back to the session as a prompt.
  const lines = [
    `Review of "${request.title || 'proposal set'}": changes requested.`,
    note.trim(),
    unticked.length
      ? `Not accepted: ${unticked.map((i) => i.id).join(', ')}`
      : '',
  ].filter(Boolean);
  await cockpitApi.dispatch.execute(activeId || '', {
    id: request.items?.[0]?.id || request.request_id || '',
    verb: 'revise',
    prompt: lines.join('\n\n'),
    agent: loadDispatchAgent(),
  }).catch(() => undefined);
  return 'Sent back to the agent — the request stays open until it returns.';
}

function buildQuestionView(detail: ReviewDetail): HTMLElement {
  const request = detail.request!;
  const wrap = document.createElement('div');
  wrap.className = 'review-body';

  const actions = document.createElement('div');
  actions.className = 'review-actions';
  const send = document.createElement('button');
  send.type = 'button';
  send.className = 'review-btn is-primary';
  send.textContent = 'Send answer';
  actions.appendChild(send);

  wrap.appendChild(buildReviewHeader(
    'answer', request.title || 'Question', undefined, actions,
    [request.agent ? `asked by ${request.agent}` : '',
     request.ts ? `${relativeAge(request.ts)} ago` : ''].filter(Boolean).join(' · '),
  ));

  if (request.body) {
    const body = document.createElement('p');
    body.className = 'review-blurb';
    body.textContent = request.body;
    wrap.appendChild(body);
  }
  const answer = document.createElement('textarea');
  answer.className = 'review-comment';
  answer.rows = 3;
  answer.placeholder = 'Your answer — dispatched back to the asking session.';
  wrap.appendChild(answer);

  const feedback = document.createElement('p');
  feedback.className = 'review-feedback';
  feedback.hidden = true;
  wrap.appendChild(feedback);

  send.addEventListener('click', () => {
    if (!answer.value.trim()) {
      feedback.textContent = 'Write an answer first.';
      feedback.hidden = false;
      feedback.classList.add('is-error');
      return;
    }
    send.disabled = true;
    void cockpitApi.dispatch.execute(activeId || '', {
      id: request.items?.[0]?.id || '',
      verb: 'answer',
      prompt: `Answer to "${request.title}":\n\n${answer.value.trim()}`,
      agent: loadDispatchAgent(),
    }).catch(() => undefined);
    void postJson('/api/cockpit/review-resolve', {
      request_id: request.request_id, outcome: 'answered',
      note: answer.value.slice(0, 400),
    }).then(() => {
      feedback.textContent = 'Answer dispatched.';
      feedback.hidden = false;
      void refreshReviewBadge();
    }).catch((err: Error) => {
      feedback.textContent = err.message;
      feedback.classList.add('is-error');
      feedback.hidden = false;
      send.disabled = false;
    });
  });
  return wrap;
}

// A proposed ADR / draft requirement: one note, same accept vocabulary.
// Accept/decline wording per type — the vocabulary STATUSES.md defines,
// not a generic yes/no. Types absent here are not decided from the desk.
const DECIDE_LABELS: Record<string, { accept: string; decline: string }> = {
  adr:         { accept: 'Accept decision', decline: 'Supersede' },
  decision:    { accept: 'Accept decision', decline: 'Supersede' },
  requirement: { accept: 'Approve', decline: 'Cancel' },
};

function buildSingleNoteReview(detail: ReviewDetail): HTMLElement {
  const note = detail.note!;
  const wrap = document.createElement('div');
  wrap.className = 'review-body';
  const isTest = note.type === 'test';

  const actions = document.createElement('div');
  actions.className = 'review-actions';
  if (isTest) {
    const run = document.createElement('button');
    run.type = 'button';
    run.className = 'review-btn is-primary';
    run.textContent = `Run ▸ ${detail.steps?.length ?? 0} steps`;
    run.addEventListener('click', () => void navigateTo(`~tests/${note.id}/run`));
    actions.appendChild(run);
  }

  // Decide buttons. Their absence is why a proposed ADR or draft
  // requirement could be opened from the queue but never acted on — the
  // set-review path had actions, the single-note path had none
  // (reported 2026-07-26). Labels come from the type's own vocabulary:
  // an ADR is accepted or superseded, never "rejected" (STATUSES.md).
  const decide = DECIDE_LABELS[note.type];
  let feedback: HTMLElement | null = null;
  if (decide) {
    const accept = document.createElement('button');
    accept.type = 'button';
    accept.className = 'review-btn is-good';
    accept.textContent = decide.accept;
    const decline = document.createElement('button');
    decline.type = 'button';
    decline.className = 'review-btn is-bad';
    decline.textContent = decide.decline;

    const run = (isAccept: boolean, btn: HTMLButtonElement): void => {
      accept.disabled = true;
      decline.disabled = true;
      void postJson('/api/notes/decide', {
        id: note.id, reviewer: 'user:edwin', accept: isAccept,
      }).then((res) => {
        const status = (res.result as { status?: string } | undefined)?.status;
        if (feedback) {
          feedback.textContent = `${note.id} is now ${status ?? 'updated'}.`;
          feedback.hidden = false;
        }
        void refreshReviewBadge();
        void navigateTo(note.rel);
      }).catch((err: Error) => {
        if (feedback) {
          feedback.textContent = err.message;
          feedback.classList.add('is-error');
          feedback.hidden = false;
        }
        accept.disabled = false;
        decline.disabled = false;
        void btn;
      });
    };
    accept.addEventListener('click', () => run(true, accept));
    decline.addEventListener('click', () => run(false, decline));
    actions.append(accept, decline);
  }

  const open = document.createElement('button');
  open.type = 'button';
  open.className = 'review-btn';
  open.textContent = 'Open note ↗';
  open.addEventListener('click', () => void navigateTo(note.rel));
  actions.appendChild(open);

  wrap.appendChild(buildReviewHeader(
    isTest ? 'run' : 'decide', `${note.id} · ${note.title}`, note.status, actions,
    isTest && detail.last_run ? `last run ${detail.last_run}`
      : isTest ? 'defined, never executed' : 'awaiting a decision',
  ));

  feedback = document.createElement('p');
  feedback.className = 'review-feedback';
  feedback.hidden = true;
  wrap.appendChild(feedback);

  // The note itself. Deciding an ADR means reading its decision, context
  // and alternatives; approving a requirement means reading its
  // acceptance criteria. The first cut rendered a header, buttons and
  // nothing else — asking for approval of content it never showed
  // (reported 2026-07-26). Mounted inline rather than linked out so the
  // decision and the evidence stay on one screen.
  const body = document.createElement('section');
  body.className = 'review-note';
  wrap.appendChild(body);
  void fillReviewNoteBody(body, note.rel);

  if (isTest && detail.steps?.length) {
    const preview = document.createElement('section');
    preview.className = 'review-set';
    const h = document.createElement('h3');
    h.textContent = 'Steps';
    preview.appendChild(h);
    for (const step of detail.steps) {
      const row = document.createElement('div');
      row.className = 'run-step';
      const n = document.createElement('span');
      n.className = 'run-step-n';
      n.textContent = String(step.n);
      const text = document.createElement('span');
      text.textContent = step.text;
      row.append(n, text);
      preview.appendChild(row);
    }
    wrap.appendChild(preview);
  }
  return wrap;
}

// Render the queued note into the review page. Reuses `/api/render`, so
// wikilinks, checkboxes and the metadata strip behave exactly as they do
// in the centre pane — a reviewer reads the real note, not a summary of it.
async function fillReviewNoteBody(target: HTMLElement, rel: string): Promise<void> {
  if (!sidecarBaseUrl || !rel) return;
  try {
    const resp = await fetch(
      `${sidecarBaseUrl}/api/render?path=${encodeURIComponent(rel)}`,
    );
    if (!resp.ok) {
      target.innerHTML = '<p class="meta">Could not load the note — open it to review.</p>';
      return;
    }
    const data = (await resp.json()) as RenderResponse;
    // Same mount as the centre pane: metadata strip then body.
    target.innerHTML = (data.metadata_html || '') + data.html;
    // Links inside a reviewed note stay navigable; the doc-view click
    // handler only covers #doc-view, so wire this subtree explicitly.
    target.querySelectorAll<HTMLAnchorElement>('a[href]').forEach((a) => {
      const href = a.getAttribute('href') || '';
      if (!href.startsWith('/docs/')) return;
      a.addEventListener('click', (e) => {
        e.preventDefault();
        void navigateTo(href.slice('/docs/'.length));
      });
    });
  } catch {
    target.innerHTML = '<p class="meta">Could not load the note — open it to review.</p>';
  }
}

/** The server's shaping of a failing step into an issue (TASK-0209's
 *  `draft_issue_body`, finally wired up by TASK-0372). */
interface IssueDraft { title: string; body: string; test_id: string }

// ----- Manual test runner (TASK-0209; moved to Tests by TASK-0372) ------
//
// `~tests/<TST>/run`. The stepper below is unchanged — it is the desk's one
// piece of genuine machinery, and moving it means moving it, not rewriting it.
// What changed is where you arrive from and what the left pane shows while you
// are running: the Tests navigator, so the run happens inside the view that
// owns the subject (ADR-0020).

async function renderTestRunPage(noteId: string): Promise<boolean> {
  if (!sidecarBaseUrl || !noteId) return false;
  let detail: ReviewDetail | null = null;
  try {
    // `/api/cockpit/review/<id>` still serves this. The endpoint is not the
    // desk: it resolves any note id and adds the test fields, and FEAT-0008's
    // API-stability rule is explicit that a retired UI route does not retire
    // an endpoint. TASK-0378 takes the route; this survives it.
    const resp = await fetch(
      `${sidecarBaseUrl}/api/cockpit/review/${encodeURIComponent(noteId)}`,
    );
    if (resp.ok) detail = (await resp.json()) as ReviewDetail;
  } catch { /* handled below */ }
  if (!detail || !detail.note) {
    showStatus(`No test found for ${noteId}`, 'error');
    return false;
  }

  // The left pane stays the Tests navigator rather than becoming a queue.
  // A run is one row of that list being walked, not a separate place.
  if (currentNavMode !== 'tests') setNavMode('tests');

  docView.classList.remove('overview-pane', 'agents-page',
    'design-page', 'is-design-shell', 'review-page');
  rightPaneContent.replaceChildren();
  docView.replaceChildren(buildTestRunner(detail));
  docView.hidden = false;
  placeholder.hidden = true;
  return true;
}

function buildTestRunner(detail: ReviewDetail): HTMLElement {
  const note = detail.note!;
  const steps = detail.steps ?? [];
  const results = steps.map((s) => ({
    n: s.n, text: s.text, expected: s.expected,
    result: '' as '' | 'pass' | 'fail' | 'skip', evidence: '',
  }));
  let current = 0;

  const wrap = document.createElement('div');
  wrap.className = 'review-body run-view';
  const stage = document.createElement('div');

  const rerender = (): void => {
    stage.replaceChildren();

    const actions = document.createElement('div');
    actions.className = 'review-actions';
    const counter = document.createElement('span');
    counter.className = 'run-counter';
    counter.textContent = current < steps.length
      ? `step ${current + 1} of ${steps.length}` : 'all steps recorded';
    const abort = document.createElement('button');
    abort.type = 'button';
    abort.className = 'review-btn';
    abort.textContent = 'Abort run';
    abort.addEventListener('click', () => void finish(true));
    actions.append(counter, abort);

    stage.appendChild(buildReviewHeader(
      'run', `${note.id} · ${note.title}`, note.status, actions,
      [detail.verifies?.length ? `verifies ${detail.verifies.join(', ')}` : '',
       detail.last_run ? `last run ${detail.last_run}` : 'first execution',
      ].filter(Boolean).join(' · '),
    ));

    const bar = document.createElement('div');
    bar.className = 'run-progress';
    const fill = document.createElement('i');
    fill.style.width = `${steps.length ? (current / steps.length) * 100 : 0}%`;
    bar.appendChild(fill);
    stage.appendChild(bar);

    results.forEach((step, i) => {
      if (i < current) {
        const row = document.createElement('div');
        row.className = `run-step is-done is-${step.result || 'skip'}`;
        const n = document.createElement('span');
        n.className = 'run-step-n';
        n.textContent = step.result === 'pass' ? '✓' : step.result === 'fail' ? '✕' : '–';
        const text = document.createElement('span');
        text.textContent = step.text;
        const ev = document.createElement('span');
        ev.className = 'run-step-ev';
        ev.textContent = step.evidence;
        row.append(n, text, ev);
        stage.appendChild(row);
        return;
      }
      if (i === current) {
        stage.appendChild(buildCurrentStep(step, i));
        return;
      }
      const row = document.createElement('div');
      row.className = 'run-step';
      const n = document.createElement('span');
      n.className = 'run-step-n';
      n.textContent = String(step.n);
      const text = document.createElement('span');
      text.textContent = step.text;
      row.append(n, text);
      stage.appendChild(row);
    });

    if (current >= steps.length && steps.length > 0) {
      stage.appendChild(buildRunSummary());
    }
    if (steps.length === 0) {
      const empty = document.createElement('p');
      empty.className = 'meta';
      empty.textContent =
        'This test has no parsable ## Steps section — add numbered steps to run it here.';
      stage.appendChild(empty);
    }
  };

  const buildCurrentStep = (
    step: typeof results[number], index: number,
  ): HTMLElement => {
    const card = document.createElement('div');
    card.className = 'run-step-current';
    const title = document.createElement('div');
    title.className = 'run-step-title';
    const n = document.createElement('span');
    n.className = 'run-step-n is-current';
    n.textContent = String(step.n);
    const text = document.createElement('span');
    text.textContent = step.text;
    title.append(n, text);
    card.appendChild(title);

    if (step.expected) {
      const exp = document.createElement('p');
      exp.className = 'run-expected';
      exp.textContent = `Expected: ${step.expected}`;
      card.appendChild(exp);
    }
    const row = document.createElement('div');
    row.className = 'run-controls';
    const evidence = document.createElement('input');
    evidence.type = 'text';
    evidence.className = 'run-evidence';
    evidence.placeholder = 'evidence — what you observed…';

    const advance = (result: 'pass' | 'fail' | 'skip'): void => {
      results[index].result = result;
      results[index].evidence = evidence.value.trim();
      current = index + 1;
      rerender();
    };
    for (const [label, kind] of [
      ['Pass', 'pass'], ['Fail', 'fail'], ['Skip', 'skip'],
    ] as const) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = `review-btn is-${kind === 'pass' ? 'good' : kind === 'fail' ? 'bad' : ''}`;
      btn.textContent = label;
      btn.addEventListener('click', () => advance(kind));
      row.appendChild(btn);
    }
    row.appendChild(evidence);
    card.appendChild(row);
    return card;
  };

  const buildRunSummary = (): HTMLElement => {
    const failed = results.filter((r) => r.result === 'fail');
    const outcome = failed.length > 0 ? 'failing' : 'passing';
    const box = document.createElement('div');
    box.className = 'run-summary';
    const line = document.createElement('p');
    line.className = 'run-summary-line';
    line.textContent = failed.length > 0
      ? `${failed.length} step${failed.length === 1 ? '' : 's'} failed — the test will be recorded as failing.`
      : 'Every step passed — the test will be recorded as passing.';
    box.appendChild(line);

    const actions = document.createElement('div');
    actions.className = 'review-actions';
    const save = document.createElement('button');
    save.type = 'button';
    save.className = `review-btn ${outcome === 'passing' ? 'is-good' : 'is-bad'}`;
    save.textContent = `Record run (${outcome})`;
    save.addEventListener('click', () => void finish(false));
    actions.appendChild(save);
    box.appendChild(actions);

    if (failed.length > 0) {
      // This sentence promised a draft that did not exist. Written for
      // TASK-0209 in the future tense — "an issue draft **will be** offered" —
      // and nothing ever offered one: `stamp_test_run` wrote the status, the
      // `last_run` and the `## Runs` entry, and stopped. `draft_issue_body`
      // was there the whole time with no caller outside its unit test, while
      // TST-0021 recorded that a failing step "produces an issue draft".
      // Measured while moving the runner (TASK-0372) — which is when a
      // sentence describing behaviour finally got read beside the behaviour.
      //
      // True now, and with no new write path: the server returns the draft in
      // its result and `buildRunOffer` hands it to FEAT-0059's capture box.
      // Still never filed automatically — allocating an id is a documentation
      // decision, which is why it is offered rather than done.
      const draft = document.createElement('p');
      draft.className = 'run-draft';
      draft.textContent =
        'Recording the run offers an issue draft for the first failing step — filing it stays your call.';
      box.appendChild(draft);
    }
    const feedback = document.createElement('p');
    feedback.className = 'review-feedback';
    feedback.hidden = true;
    feedback.id = 'run-feedback';
    box.appendChild(feedback);
    return box;
  };

  const finish = async (aborted: boolean): Promise<void> => {
    const recorded = results.filter((r) => r.result);
    const failed = results.filter((r) => r.result === 'fail');
    const outcome = failed.length > 0 ? 'failing' : 'passing';
    const feedback = stage.querySelector<HTMLElement>('#run-feedback');
    let draft: IssueDraft | null = null;
    try {
      const posted = await postJson('/api/notes/test-run', {
        id: note.id,
        outcome: aborted ? '' : outcome,
        aborted,
        runner: 'user:edwin',
        mtime: detail.mtime,
        steps: recorded.map((r) => ({
          // `expected` travels so the draft can quote it: the server shapes
          // the issue and only the stepper knows what the note promised.
          n: r.n, text: r.text, expected: r.expected,
          result: r.result, evidence: r.evidence,
        })),
      });
      draft = ((posted.result || {}) as { issue_draft?: IssueDraft })
        .issue_draft ?? null;
    } catch (err) {
      const message = (err as Error).message;
      if (feedback) {
        feedback.textContent = message;
        feedback.classList.add('is-error');
        feedback.hidden = false;
      } else {
        showStatus(`Run not recorded: ${message}`, 'error');
      }
      return;
    }
    void refreshReviewBadge();
    showStatus(
      aborted ? 'Run aborted — partial log kept in the note.'
        : `Run recorded: ${note.id} is ${outcome}.`,
    );
    // A failing run stops here and offers the draft. Navigating straight to
    // the note would carry the one moment the offer is worth anything off the
    // screen — and the run is already written, so nothing is at risk in
    // pausing. Everything else goes to the note as before.
    if (draft) {
      stage.replaceChildren(buildRunOffer(draft));
      return;
    }
    void navigateTo(note.rel);
  };

  /** What a recorded failing run leaves you with: the outcome, and the offer.
   *
   *  The draft's text is the SERVER'S (`draft_issue_body`) — title, the step,
   *  what the note expected and what was observed. Shaping it here would be a
   *  second issue-drafting vocabulary a few hundred lines from the first, and
   *  only one of them would ever be tested.
   */
  const buildRunOffer = (issue: IssueDraft): HTMLElement => {
    const box = document.createElement('div');
    box.className = 'run-summary';
    const line = document.createElement('p');
    line.className = 'run-summary-line';
    line.textContent = `Recorded — ${note.id} is failing.`;
    const preview = document.createElement('p');
    preview.className = 'run-draft';
    preview.textContent = issue.title;

    const actions = document.createElement('div');
    actions.className = 'review-actions';
    const file = document.createElement('button');
    file.type = 'button';
    file.className = 'review-btn is-primary';
    file.textContent = 'Draft an issue ▸';
    file.addEventListener('click', () => openCapture({
      title: issue.title, body: issue.body, related: [note.id],
    }));
    const open = document.createElement('button');
    open.type = 'button';
    open.className = 'review-btn';
    open.textContent = `Open ${note.id}`;
    open.addEventListener('click', () => void navigateTo(note.rel));
    actions.append(file, open);

    box.append(line, preview, actions);
    return box;
  };

  wrap.appendChild(stage);
  rerender();
  return wrap;
}

// ----- Design input strip (TASK-0212) -----------------------------------
// `design:` holds wikilinks to reference notes wrapping committed
// dossiers under docs/references/design/. Existing machinery throughout:
// an existing note type, an indexed link field, the normal resolver.

const WIKILINK_TARGET_RE = /\[\[([^\]|]+?)(?:\|[^\]]*)?\]\]/g;

function designLinksFrom(frontmatter: Record<string, unknown>): string[] {
  const raw = frontmatter.design;
  if (!raw) return [];
  const values = Array.isArray(raw) ? raw : [raw];
  const out: string[] = [];
  for (const value of values) {
    const text = String(value);
    let matched = false;
    for (const m of text.matchAll(WIKILINK_TARGET_RE)) {
      out.push(m[1].trim());
      matched = true;
    }
    if (!matched && text.trim()) out.push(text.trim());
  }
  return out;
}

function buildDesignStrip(
  frontmatter: Record<string, unknown>,
): HTMLElement | null {
  const targets = designLinksFrom(frontmatter);
  if (targets.length === 0) return null;

  const strip = document.createElement('div');
  strip.className = 'doc-design-strip';
  const label = document.createElement('span');
  label.className = 'doc-design-label';
  label.textContent = targets.length === 1 ? 'Design input' : `Design input · ${targets.length}`;
  strip.appendChild(label);

  for (const target of targets) {
    const link = document.createElement('button');
    link.type = 'button';
    link.className = 'doc-design-item';
    const icon = document.createElement('span');
    icon.className = 'doc-design-icon';
    icon.textContent = '▣';
    const name = document.createElement('span');
    name.textContent = target.replace(/^REF-\d+-/, '').replace(/-/g, ' ');
    link.append(icon, name);
    link.title = target;
    // Resolution goes through the sidecar so a renamed note still opens
    // — the same path a [[wikilink]] in the body takes.
    link.addEventListener('click', () => void navigateToId(target));
    strip.appendChild(link);
  }
  return strip;
}

async function navigateToId(target: string): Promise<void> {
  if (!sidecarBaseUrl) return;
  try {
    const resp = await fetch(
      `${sidecarBaseUrl}/api/cockpit/context?this=${encodeURIComponent(target)}`,
    );
    if (resp.ok) {
      const data = (await resp.json()) as ContextPayload;
      const rel = extractRel(data.active?.url);
      if (rel) { void navigateTo(rel); return; }
    }
  } catch { /* fall through to the literal form */ }
  void navigateTo(target.endsWith('.md') ? target : `${target}.md`);
}

// ----- Focus band (TASK-0200) -------------------------------------------
// The SNAPSHOT focus chain. It is always set but usually terminal — work
// here is bursty (an agent sets `doing` and clears it at close-out), so
// the resting state reads "what just finished" rather than pretending
// something is live. The note's age is shown because a stale focus note
// is itself worth seeing.

const FOCUS_ORDER: Array<'phase' | 'feature' | 'requirement' | 'issue' | 'task'> =
  ['phase', 'feature', 'requirement', 'issue', 'task'];

function buildFocusBand(focus: FocusBlock): HTMLElement | null {
  const slots = FOCUS_ORDER
    .map((k) => focus.items?.[k])
    .filter((it): it is FocusItem => !!it && !!it.id);
  if (slots.length === 0 && !focus.note) return null;

  const band = document.createElement('section');
  band.className = 'ov-focus';
  const label = document.createElement('span');
  label.className = 'ov-focus-label';
  const live = slots.some((s) => isActiveStatus(s.status));
  band.classList.toggle('is-live', live);
  label.textContent = live ? 'NOW' : 'FOCUS';
  band.appendChild(label);

  slots.forEach((slot, i) => {
    if (i > 0) {
      const sep = document.createElement('span');
      sep.className = 'ov-focus-sep';
      sep.textContent = '▸';
      band.appendChild(sep);
    }
    band.appendChild(buildFocusChip(slot));
  });

  if (focus.note_date) {
    const age = document.createElement('span');
    age.className = 'ov-focus-age';
    const days = daysSince(focus.note_date);
    age.textContent = days === null ? focus.note_date
      : days <= 0 ? 'note today'
      : `note ${days}d old`;
    age.title = focus.note;
    if (days !== null && days >= 7) age.classList.add('is-stale');
    band.appendChild(age);
  }
  return band;
}

function buildFocusChip(slot: FocusItem): HTMLElement {
  const chip = document.createElement('button');
  chip.type = 'button';
  chip.className = 'ov-focus-chip';
  if (isActiveStatus(slot.status)) {
    const pulse = document.createElement('span');
    pulse.className = 'ov-focus-pulse';
    chip.appendChild(pulse);
  }
  const id = document.createElement('span');
  id.className = 'ov-focus-id mono ov-typed';
  id.textContent = shortNoteId(slot.id);
  id.title = slot.id;
  if (slot.type) id.dataset.type = slot.type;
  chip.appendChild(id);
  if (slot.title) {
    const title = document.createElement('span');
    title.className = 'ov-focus-title';
    title.textContent = slot.title;
    chip.appendChild(title);
  }
  appendIf(chip, statusChip(slot.status));
  if (slot.rel) {
    chip.addEventListener('click', () => void navigateTo(slot.rel!));
  } else {
    chip.classList.add('is-dangling');
    chip.title = `${slot.id} — no note resolves for this id`;
    chip.disabled = true;
  }
  return chip;
}

function isActiveStatus(status?: string): boolean {
  const s = (status || '').toLowerCase().trim();
  return s === 'doing' || s === 'in-progress' || s === 'in_progress'
    || s === 'active' || s === 'review';
}

function daysSince(isoDate: string): number | null {
  const then = Date.parse(`${isoDate}T00:00:00`);
  if (Number.isNaN(then)) return null;
  const today = new Date();
  const midnight = new Date(
    today.getFullYear(), today.getMonth(), today.getDate(),
  ).getTime();
  return Math.round((midnight - then) / 86_400_000);
}

// Now board (TASK-0165): Doing / Next / Done-today columns rendered
// from the Active-mode data, live-migrating on status transitions.
function buildNowBoard(): HTMLElement {
  const wrap = document.createElement('section');
  wrap.className = 'ov-section ov-now-board';
  const h = document.createElement('h3');
  h.textContent = 'Now — work in flight';
  wrap.appendChild(h);
  const board = document.createElement('div');
  board.className = 'now-board';
  wrap.appendChild(board);
  void fillNowBoard(board);
  return wrap;
}

async function fillNowBoard(board: HTMLElement): Promise<void> {
  if (!sidecarBaseUrl) return;
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/nav?mode=active`);
    if (!resp.ok) return;
    const data = await resp.json() as { groups: NavGroupData[] };
    board.replaceChildren();
    if (data.groups.length === 0) {
      const empty = document.createElement('p');
      empty.className = 'meta';
      empty.textContent = 'Nothing in flight right now — work appears here while its status is doing.';
      board.appendChild(empty);
      return;
    }
    for (const g of data.groups) {
      const items = g.items ?? [];
      const col = document.createElement('div');
      col.className = 'now-col';
      const head = document.createElement('div');
      head.className = 'now-col-head';
      head.textContent = `${g.label} · ${items.length}`;
      col.appendChild(head);
      for (const it of items) {
        const card = document.createElement('button');
        card.type = 'button';
        card.className = 'now-card-item';
        if (it.id) card.dataset.id = String(it.id);
        appendIf(card, typeIcon(it.type));
        const idl = document.createElement('span');
        idl.className = 'now-card-id mono';
        // Found by the enumerating guard, not by looking (ISS-0099): the
        // FIFTH surface rendering a raw id, and one nobody had reported.
        idl.textContent = shortNoteId(it.id || '');
        if (it.id) idl.title = String(it.id);
        card.appendChild(idl);
        if (it.id && sessionTouchedIds.has(it.id)) {
          const chip = document.createElement('span');
          chip.className = 'nav-agent-chip';
          chip.textContent = 'agent';
          card.appendChild(chip);
        }
        appendIf(card, statusChip(it.status));
        const rel = extractRel(it.url);
        if (rel) card.addEventListener('click', () => void navigateTo(rel));
        col.appendChild(card);
      }
      board.appendChild(col);
    }
  } catch { /* transient — ignore */ }
}

// ----- Stat tiles (TASK-0200) -------------------------------------------
// Six counts, each with the status composition inline. This is what
// retires the donut row: the mix a donut drew without labels is stated
// here in situ, next to the number it decomposes, at a third the height.

// Mix segments in reading order. The *bucketing* is deliberately not done
// here: which bucket a status belongs to is a vocabulary question, and
// ISS-0023 is what happens when a surface answers that locally. The
// sidecar sends `status_buckets` (computed from statuses.py) and this
// draws the widths. Colours resolve to existing status tokens — no new
// palette, no new vocabulary (ADR-0006 / TST-0019).
type MixKey = 'done' | 'doing' | 'attention' | 'backlog';
const MIX_KEYS: MixKey[] = ['done', 'doing', 'attention', 'backlog'];

const MIX_LABEL: Record<MixKey, string> = {
  done: 'done', doing: 'in flight', attention: 'attention', backlog: 'backlog',
};

type MixBuckets = Partial<Record<MixKey, number>>;

function buildMixBar(
  buckets: MixBuckets | undefined,
  raw?: Record<string, number>,
): HTMLElement {
  const bar = document.createElement('div');
  bar.className = 'ov-mixbar';
  const total = MIX_KEYS.reduce((n, k) => n + (buckets?.[k] ?? 0), 0);
  if (total === 0) {
    bar.classList.add('is-empty');
    return bar;
  }
  for (const key of MIX_KEYS) {
    const count = buckets?.[key] ?? 0;
    if (count === 0) continue;
    const seg = document.createElement('i');
    seg.dataset.seg = key;
    seg.style.flex = String(count);
    bar.appendChild(seg);
  }
  // The tooltip keeps the raw per-status detail the buckets summarise.
  const detail = Object.entries(raw || {})
    .sort((a, b) => b[1] - a[1])
    .map(([status, count]) => `${count} ${status}`)
    .join(' · ');
  bar.title = detail || MIX_KEYS
    .filter((k) => (buckets?.[k] ?? 0) > 0)
    .map((k) => `${buckets?.[k]} ${MIX_LABEL[k]}`)
    .join(' · ');
  return bar;
}

function buildStatTile(
  label: string, value: string, sub: string,
  buckets: MixBuckets | undefined, raw: Record<string, number> | undefined,
  navMode?: NavMode,
): HTMLElement {
  const tile = document.createElement(navMode ? 'button' : 'div');
  tile.className = 'ov-stat';
  if (navMode) {
    (tile as HTMLButtonElement).type = 'button';
    tile.addEventListener('click', () => setNavMode(navMode));
  }
  const head = document.createElement('div');
  head.className = 'ov-stat-label';
  head.textContent = label;
  const val = document.createElement('div');
  val.className = 'ov-stat-value num';
  val.textContent = value;
  if (sub) {
    const small = document.createElement('small');
    small.textContent = ` ${sub}`;
    val.appendChild(small);
  }
  tile.append(head, val, buildMixBar(buckets, raw));
  return tile;
}

function buildStatTiles(data: StatsPayload): HTMLElement {
  const wrap = document.createElement('section');
  wrap.className = 'ov-section ov-stats';
  const strip = document.createElement('div');
  strip.className = 'ov-stat-strip';
  const hero = data.hero;
  const mix = data.status_mix || {};
  const buckets = data.status_buckets || {};

  strip.append(
    buildStatTile('Features', String(hero.features.done),
      `/${hero.features.total}`, buckets.features, mix.features, 'features'),
    buildStatTile('Tasks', String(hero.tasks.done),
      // TASK-0368: was 'tasks'. Retiring a mode is exactly how a live tile
      // becomes a dead click (ISS-0063), and tasks live under Features now.
      `/${hero.tasks.total}`, buckets.tasks, mix.tasks, 'features'),
  );
  // Requirements were computed by the sidecar all along and never
  // rendered — the tile strip is where they finally show (TASK-0200).
  if (hero.requirements) {
    strip.appendChild(buildStatTile(
      'Reqs', String(hero.requirements.done),
      `/${hero.requirements.total}`, buckets.requirements, mix.requirements,
    ));
  }
  // Tests and Risks were passed no navMode until PHASE-010, so they
  // rendered as divs: a count that looks like a control and does nothing
  // (ISS-0063). They were dead because the types had no page. Both have one
  // now — Tests its own view (FEAT-0086), risks the constraints view.
  //
  // Reqs stays deliberately dead: requirements nest under features, so
  // the tile has no single destination. Recorded as a decision in
  // PHASE-010's Out of Scope, and asserted by TST-0022 so it does not
  // read as an oversight.
  // TASK-0371 repointed two of these, and both were dead clicks by the time
  // it looked. Tests went to `review` because the desk register was the only
  // list of tests anywhere; there is a Tests view now. Risks went to `issues`
  // — and risks left that navigator earlier the same day for the constraints
  // view (ISS-0128), so the tile had spent a commit sending people to a pane
  // with no risks in it. That is ISS-0063 verbatim, re-created by moving a
  // type without re-checking who pointed at it, which is why
  // `test_every_stat_tile_lands_where_its_type_lives` now asserts the
  // PROPERTY — the destination contains the type — against the real corpus,
  // rather than the mode string a reader has to verify by hand.
  strip.append(
    buildStatTile('Tests', String(hero.tests.passing),
      `/${hero.tests.total}`, buckets.tests, mix.tests, 'tests'),
    buildStatTile('Issues', String(hero.issues.open),
      `open /${hero.issues.total}`, buckets.issues, mix.issues, 'issues'),
    buildStatTile('Risks', String(hero.risks.open),
      // The Risks tile lands on Intent, where ISS-0128 moved risks. The
      // argument is a nav MODE, so it moved with the rename (TASK-0385).
      `open /${hero.risks.total}`, buckets.risks, mix.risks, 'intent'),
  );
  wrap.appendChild(strip);

  const key = document.createElement('div');
  key.className = 'ov-mix-key';
  for (const k of ['done', 'doing', 'attention', 'backlog'] as MixKey[]) {
    const item = document.createElement('span');
    const swatch = document.createElement('i');
    swatch.dataset.seg = k;
    item.append(swatch, document.createTextNode(MIX_LABEL[k]));
    key.appendChild(item);
  }
  wrap.appendChild(key);
  return wrap;
}

function buildHero(hero: StatsHero): HTMLElement {
  const wrap = document.createElement('section');
  wrap.className = 'ov-hero';
  const fmt = (n: number, total: number): string => total ? `${n} / ${total}` : '—';
  const cell = (label: string, value: string, sub?: string): HTMLElement => {
    const el = document.createElement('div');
    el.className = 'ov-hero-cell';
    el.innerHTML = `<div class="ov-hero-value">${value}</div>`
      + `<div class="ov-hero-label">${label}</div>`
      + (sub ? `<div class="ov-hero-sub">${sub}</div>` : '');
    return el;
  };
  wrap.append(
    cell('Features', fmt(hero.features.done, hero.features.total)),
    cell('Tasks',    fmt(hero.tasks.done,    hero.tasks.total)),
    cell('Issues',   String(hero.issues.open), `${hero.issues.total} total`),
    cell('Tests',    `${hero.tests.passing} / ${hero.tests.total}`),
    cell('Risks',    String(hero.risks.open), `${hero.risks.total} total`),
  );
  if (hero.last_change) {
    const last = document.createElement('div');
    last.className = 'ov-hero-cell ov-hero-last';
    last.innerHTML = `<div class="ov-hero-value ov-hero-last-title">${escapeHtml(hero.last_change.title)}</div>`
      + `<div class="ov-hero-label">Last change</div>`
      + `<div class="ov-hero-sub">${escapeHtml(hero.last_change.date)}</div>`;
    last.style.cursor = 'pointer';
    last.title = hero.last_change.rel;
    last.addEventListener('click', () => {
      if (hero.last_change?.rel) void navigateTo(hero.last_change.rel);
    });
    wrap.appendChild(last);
  }
  return wrap;
}

// ----- Phase section (TASK-0201) ----------------------------------------
// Live phases lead and carry their metadata on the row; finished phases
// group under a "Completed" band. Every row is an accordion — expanded
// state is per-phase and remembered for the session, so opening a
// delivered phase to inspect it is one click and stays put across the
// SSE-driven re-renders.
//
// "Completed" is a *view* over done phases, never a status: ADR-0006
// retired the `delivered` band after measuring zero writes of its
// members, and `test_delivered_band_is_retired` guards its return.

const phaseOpenState = new Map<string, boolean>();

function phaseIsComplete(p: StatsPhase): boolean {
  // The phase's own status wins when it is terminal. `superseded` is the case
  // that made this necessary: your-trainer's PHASE-012 (iOS Launch) was
  // superseded by PHASE-019 (iOS Parity), and a purely count-based predicate
  // would call it live again the moment any child was reopened — the authored
  // decision "this phase was replaced" outranks arithmetic over its tasks.
  //
  // COMPLETED_STATUSES is the shared vocabulary (statuses.py -> cockpit.js ->
  // here), so `done`, `superseded` and `cancelled` all resolve without this
  // function keeping its own list. `deferred` is deliberately NOT in it: parked
  // work is still wanted (ADR-0005).
  if (isCompletedStatus(p.status ?? undefined)) return true;
  const t = p.tasks;
  const total = t.done + t.in_progress + t.backlog;
  return total > 0 && t.done === total;
}

// Live phases sort active-first: an `active` phase is where work is happening,
// and burying it under `planned` ones ordered by `order:` is the same "shouting
// as loudly as the live one" problem the Completed band fixed, one level down.
//
// Rank 0 comes from `phaseIsActiveStatus` rather than from this table: the
// same question — is anyone in this phase — now also decides which phases
// expand on first paint (ISS-0103), and two tables answering it would drift.
const PHASE_LIVE_RANK: Record<string, number> = {
  planned: 1, backlog: 1, draft: 1,
};

function phaseLiveRank(p: StatsPhase): number {
  if (phaseIsActiveStatus(p.status)) return 0;
  return PHASE_LIVE_RANK[(p.status ?? '').toLowerCase()] ?? 2;
}

function sortLivePhases(phases: StatsPhase[]): StatsPhase[] {
  return phases
    .map((p, i) => ({ p, i }))                    // keep `order:` as the tiebreak
    .sort((a, b) => {
      const ra = phaseLiveRank(a.p);
      const rb = phaseLiveRank(b.p);
      return ra !== rb ? ra - rb : a.i - b.i;
    })
    .map((x) => x.p);
}

function phaseIsOpen(p: StatsPhase, complete: boolean): boolean {
  const stored = phaseOpenState.get(p.key);
  // A stored value always wins: the default describes the FIRST render, and
  // an SSE re-render must never re-collapse a phase the reader opened.
  //
  // The rule itself lives in `completed-work.ts` (ISS-0103) so it can be
  // tested as a truth table rather than grepped out of a DOM function.
  // `countInFlight(p)` is what the row prints as `16 in flight`, so the
  // number you can see is the number that decides — reading
  // `p.tasks.in_progress` here would be a second definition of in-flight.
  return stored === undefined
    ? phaseOpensByDefault(p.status, countInFlight(p), complete)
    : stored;
}

function buildPhaseSection(phases: StatsPhase[]): HTMLElement {
  const wrap = document.createElement('section');
  wrap.className = 'ov-section';
  const heading = document.createElement('h3');
  heading.textContent = 'Phases';
  wrap.appendChild(heading);

  const live = sortLivePhases(phases.filter((p) => !phaseIsComplete(p)));
  const complete = phases.filter((p) => phaseIsComplete(p));

  for (const p of live) wrap.appendChild(buildPhaseRow(p, false));

  if (complete.length > 0) {
    const items = complete.reduce(
      (n, p) => n + p.tasks.done + p.tasks.in_progress + p.tasks.backlog, 0,
    );
    const band = document.createElement('div');
    band.className = 'ov-completed-head';
    const chev = document.createElement('span');
    chev.className = 'ov-chev';
    const label = document.createElement('span');
    label.textContent = `Completed · ${complete.length} phase${complete.length === 1 ? '' : 's'} · ${items} items`;
    const rule = document.createElement('span');
    rule.className = 'ov-rule';
    band.append(chev, label, rule);

    const body = document.createElement('div');
    body.className = 'ov-completed-body';
    for (const p of complete) body.appendChild(buildPhaseRow(p, true));

    const open = completedBandOpen;
    band.classList.toggle('is-open', open);
    body.hidden = !open;
    band.addEventListener('click', () => {
      completedBandOpen = !completedBandOpen;
      band.classList.toggle('is-open', completedBandOpen);
      body.hidden = !completedBandOpen;
    });
    wrap.append(band, body);
  }
  return wrap;
}

let completedBandOpen = false;

function buildPhaseRow(p: StatsPhase, complete: boolean): HTMLElement {
  const t = p.tasks;
  const total = t.done + t.in_progress + t.backlog;
  const pct = total > 0 ? Math.round((t.done / total) * 100) : 0;
  const open = phaseIsOpen(p, complete);

  const row = document.createElement('div');
  row.className = 'ov-phase' + (complete ? ' is-complete' : '');
  row.classList.toggle('is-open', open);

  const head = document.createElement('div');
  head.className = 'ov-phase-head';

  const chev = document.createElement('button');
  chev.type = 'button';
  chev.className = 'ov-chev';
  chev.setAttribute('aria-expanded', String(open));
  chev.setAttribute('aria-label', `${open ? 'Collapse' : 'Expand'} ${p.title}`);

  const title = document.createElement('span');
  title.className = 'ov-phase-title';
  title.textContent = p.title;

  head.append(chev);
  // The ID, beside the title (ISS-0076). `p.key` was already here — it
  // routes the title click to `~overview/<key>` — and was never shown.
  //
  // It matters more than a label usually would: everything that refers
  // to a phase refers to it by ID (`focus.phase`, every note's
  // frontmatter, docs/PHASES.md), so this section is the one surface
  // listing every phase and the only one that could not be matched
  // against any of them. The focus band above already shows it.
  //
  // Guarded on the same shape the drill-in guards on: a non-`PHASE-*`
  // key is a bucket, not a phase, and has nothing to name.
  if (/^PHASE-/i.test(p.key)) {
    const id = document.createElement('span');
    id.className = 'ov-phase-id mono';
    id.textContent = p.key;
    head.appendChild(id);
  }
  head.appendChild(title);
  appendIf(head, statusChip(p.status || undefined));

  // ISS-0101: progress is ONE field. `24/51`, `47%` and `10 in flight` are
  // three readings of the same fact — how far this phase has got — and they
  // sat in three columns with an unrelated pill between them.
  const inFlight = countInFlight(p);
  const frac = document.createElement('span');
  frac.className = 'ov-phase-count num';
  frac.textContent = total > 0
    ? `${t.done}/${total} · ${pct}%${inFlight > 0 ? ` · ${inFlight} in flight` : ''}`
    : '(no items)';
  if (inFlight > 0) frac.title = `${inFlight} item${inFlight === 1 ? '' : 's'} being worked now`;
  // ISS-0102: attention sits INLINE, right after `in flight`, in the same
  // font and a different colour.
  //
  // It was a right-aligned pill until Edwin asked where it took him. The
  // honest answer was nowhere — and making it navigate would only have
  // repeated what clicking the row already does. A number that leads
  // nowhere should not be dressed as a control; it is one more reading of
  // the same phase, so it reads on the same line as the others.
  if (p.waiting && p.waiting > 0) {
    const attn = document.createElement('span');
    attn.className = 'ov-phase-attn-inline';
    attn.textContent = ` · ${p.waiting} attention`;
    attn.title = attentionBreakdown(p)
      || `${p.waiting} item${p.waiting === 1 ? '' : 's'} here need a decision or a run`;
    frac.appendChild(attn);
  }
  head.appendChild(frac);

  // DES-0004's phase-header markers: the two things no square can carry.
  //
  // `unclosed` is a property of the phase, so nothing with a square can hold
  // it — and it is the only row in the retired Waiting-on-you list that
  // nothing else on the page could tell you.
  if (p.unclosed) {
    const pill = document.createElement('span');
    pill.className = 'ov-phase-pill is-unclosed';
    pill.textContent = 'close out';
    pill.title = 'Every item here is resolved and the phase is not closed';
    head.appendChild(pill);
  }
  // ISS-0101: ONE attention field, and named for what it means.
  //
  // It read `15 waiting`, and three columns later the row itemised part of
  // the SAME set as `2 triage · 1 in review` — the aggregate and a subset of
  // its own members, on one line. Edwin could not say what `waiting` meant,
  // which is the correct response to a number that is partly repeated
  // beside itself under a different name.
  //
  const meta = buildPhaseMeta(p, complete);
  if (meta) head.appendChild(meta);
  row.appendChild(head);

  if (!complete && total > 0) {
    const under = document.createElement('div');
    under.className = 'ov-phase-under';
    const fill = document.createElement('i');
    fill.style.width = `${pct}%`;
    under.appendChild(fill);
    row.appendChild(under);
  }

  const bar = document.createElement('div');
  bar.className = 'ov-phase-bar';
  bar.title = `${t.done} done · ${t.in_progress} in progress · ${t.backlog} backlog`;
  for (const feat of p.features) bar.appendChild(buildPhaseFeatureGroup(feat));
  if (p.loose.length > 0) bar.appendChild(buildPhaseLooseGroup(p.loose));
  if (p.features.length === 0 && p.loose.length === 0) {
    const empty = document.createElement('span');
    empty.className = 'ov-phase-empty';
    empty.textContent = 'No features or issues in this phase yet — add one with a `phase:` naming it.';
    bar.appendChild(empty);
  }
  bar.hidden = !open;
  row.appendChild(bar);

  const toggle = (): void => {
    const next = !row.classList.contains('is-open');
    phaseOpenState.set(p.key, next);
    row.classList.toggle('is-open', next);
    bar.hidden = !next;
    chev.setAttribute('aria-expanded', String(next));
  };
  chev.addEventListener('click', (e) => { e.stopPropagation(); toggle(); });

  // The title drills into the scoped dashboard (FEAT-0023); the chevron
  // expands in place. Two affordances, two outcomes, both discoverable.
  if (/^PHASE-/i.test(p.key)) {
    title.classList.add('is-link');
    title.addEventListener('click', (e) => {
      e.stopPropagation();
      void navigateTo(`~overview/${p.key}`);
    });
    head.addEventListener('click', toggle);
    head.style.cursor = 'pointer';
  }
  return row;
}

// Row-level metadata: what is live here, and what wants a human. Both
// derived from the children the payload already carries.
function buildPhaseMeta(p: StatsPhase, complete: boolean): HTMLElement | null {
  const children: PhaseItem[] = [];
  for (const feature of p.features) children.push(feature, ...feature.children);
  children.push(...p.loose);

  // ISS-0101: this used to carry `N in flight` and an itemised attention
  // list. Both moved: in-flight into the progress field it belongs to, and
  // the itemisation into the `needs you` tooltip, because it was a subset
  // of that pill's own count sitting three columns away from it.
  //
  // What is left is the one thing neither field can say — that a phase is
  // finished and nobody closed it.
  const t = p.tasks;
  const total = t.done + t.in_progress + t.backlog;
  const unclosed = total > 0 && t.done === total
    && (p.status || '').toLowerCase() !== 'done';
  if (!unclosed || complete) return null;

  const meta = document.createElement('span');
  meta.className = 'ov-phase-rowmeta';
  const el = document.createElement('span');
  el.className = 'ov-phase-attention';
  el.textContent = 'awaiting close-out';
  meta.appendChild(el);
  return meta;
}

/** Items being worked right now, across a phase's features and loose items. */
function countInFlight(p: StatsPhase): number {
  const children: PhaseItem[] = [];
  for (const feature of p.features) children.push(feature, ...feature.children);
  children.push(...p.loose);
  return children.filter((c) => isActiveStatus(c.status)).length;
}

/** What the `needs you` count is made of — for its tooltip, not the row.
 *
 *  A total that wants explaining explains itself on hover; itemising it in
 *  a column beside itself was the double-count ISS-0101 removed. */
function attentionBreakdown(p: StatsPhase): string {
  const children: PhaseItem[] = [];
  for (const feature of p.features) children.push(feature, ...feature.children);
  children.push(...p.loose);
  const n = (pred: (c: PhaseItem) => boolean): number => children.filter(pred).length;
  const st = (c: PhaseItem): string => (c.status || '').toLowerCase();
  const parts: string[] = [];
  const triage = n((c) => st(c) === 'triage');
  const review = n((c) => st(c) === 'review');
  const ready = n((c) => c.type === 'test' && st(c) === 'ready');
  const failing = n((c) => c.type === 'test' && st(c) === 'failing');
  if (failing) parts.push(`${failing} failing test${failing === 1 ? '' : 's'}`);
  if (triage) parts.push(`${triage} awaiting triage`);
  if (review) parts.push(`${review} awaiting review`);
  if (ready) parts.push(`${ready} test${ready === 1 ? '' : 's'} never run`);
  return parts.length ? `Needs a decision or a run:\n· ${parts.join('\n· ')}` : '';
}

function makePhaseSquare(item: PhaseItem, isFeature: boolean): HTMLElement {
  const sq = document.createElement('span');
  sq.className = 'ov-phase-sq' + (isFeature ? ' is-feature' : '');
  sq.dataset.bucket = item.bucket;
  sq.dataset.type = item.type;
  // DES-0004: six marks, colour still carrying type. `data-state` drives the
  // fill (solid / slit / strike / inverted / inverted-pulsing) and `data-attn`
  // the corner dot, which layers over any of them.
  //
  // This is what replaced the Waiting-on-you list rather than duplicating it:
  // every row that list showed was already a square here, rendering as plain
  // hollow because the encoding could not say otherwise (ISS-0068).
  if (item.state) sq.dataset.state = item.state;
  if (item.attn) sq.dataset.attn = '';
  const marks = [
    item.state === 'unproven' ? 'complete, not proven' : null,
    item.state === 'dropped' ? 'resolved, nothing delivered' : null,
    item.state === 'deferred' ? 'parked' : null,
    item.state === 'doing' ? 'in progress' : null,
    item.attn ? 'needs you' : null,
  ].filter(Boolean);
  sq.title = `${item.id ?? ''} ${item.title} (${item.status || '—'})`.trim()
    + (marks.length ? ` — ${marks.join(', ')}` : '');
  if (item.rel) {
    sq.style.cursor = 'pointer';
    sq.addEventListener('click', () => {
      setNavMode('features');
      void navigateTo(item.rel!);
    });
  }
  return sq;
}

function buildPhaseFeatureGroup(feat: PhaseFeature): HTMLElement {
  const g = document.createElement('span');
  g.className = 'ov-phase-group';
  g.title = `${feat.id ?? ''} ${feat.title}`.trim();
  g.appendChild(makePhaseSquare(feat, true));
  for (const c of feat.children) g.appendChild(makePhaseSquare(c, false));
  return g;
}

function buildPhaseLooseGroup(loose: PhaseItem[]): HTMLElement {
  const g = document.createElement('span');
  g.className = 'ov-phase-group ov-phase-group-loose';
  g.title = `${loose.length} item${loose.length === 1 ? '' : 's'} without a parent feature`;
  for (const c of loose) g.appendChild(makePhaseSquare(c, false));
  return g;
}

const STATUS_COLOR_BY_KEY: Record<string, string> = {
  // Done family (`implemented` is terminal since ADR-0007)
  done: 'var(--status-done)', merged: 'var(--status-done)', verified: 'var(--status-done)',
  closed: 'var(--status-done)', fixed: 'var(--status-done)', complete: 'var(--status-done)',
  passing: 'var(--status-done)',
  implemented: 'var(--status-done)', resolved: 'var(--status-done)',
  released: 'var(--status-done)',
  // Active family
  active: 'var(--status-active)', doing: 'var(--status-active)',
  accepted: 'var(--status-active)', approved: 'var(--status-active)',
  // Pending family — matches base.css and statuses.py (not 'active')
  proposed: 'var(--status-pending)', draft: 'var(--status-pending)',
  // Blocked / negative
  blocked: 'var(--severity-high)', failed: 'var(--severity-critical)',
  cancelled: 'var(--text-faint)', superseded: 'var(--text-faint)',
  retired: 'var(--text-faint)', obsolete: 'var(--text-faint)',
  // Backlog / planned
  backlog: 'var(--text-faint)', planned: 'var(--text-faint)',
  triage: 'var(--severity-medium)', open: 'var(--severity-medium)',
};

function donutGradient(mix: Record<string, number>): string {
  const total = Object.values(mix).reduce((a, b) => a + b, 0);
  if (total === 0) return `var(--text-faint)`;
  // Sort entries so the donut has a stable arc order.
  const entries = Object.entries(mix).sort((a, b) => b[1] - a[1]);
  const parts: string[] = [];
  let acc = 0;
  for (const [status, count] of entries) {
    const start = (acc / total) * 100;
    acc += count;
    const end = (acc / total) * 100;
    const color = STATUS_COLOR_BY_KEY[status] || 'var(--text-muted)';
    parts.push(`${color} ${start}% ${end}%`);
  }
  return `conic-gradient(${parts.join(', ')})`;
}

// ----- Waiting on you (TASK-0200) ---------------------------------------
// Only states the corpus actually holds and holds *durably*. The states
// audit behind FEAT-0040 found `doing`/`triage` empty between sessions
// (they clear at close-out), while these persist until a human acts:
// open issues, review stalls, defined-but-never-executed tests, parked
// work, open risks, and phases finished but never closed out.

// AttentionRow went with the Waiting-on-you list (ISS-0068) — it described
// that section's rows and had no other caller.

// SEVERITY_RANK went too: its only caller was collectAttention's rank, and the
// squares carry no severity ordering — the dot is one signal regardless.

// buildWaitingOnYou / collectAttention / appendAsyncWaitingRows /
// buildWaitingRow lived here until PHASE-012 (ISS-0068).
//
// The section they built re-listed, in prose, items that were already on the
// page as phase squares — measured 2026-07-30: all 9 rows it showed had a
// square, 8 of them visible, every one rendering plain hollow because the
// encoding could not say otherwise. It was a workaround for an
// under-expressive square, not a second view, so DES-0004 gave the square the
// states and this went.
//
// Deleted rather than emptied, and TASK-0200 / TASK-0210 are marked
// `superseded` rather than left claiming a live surface: retiring this reverses
// a design decision (DES-0001's plate 5 specified it by name), and a reversal
// should read as one.
//
// Gone with it: the dedup pass that existed only because a `ready` manual test
// was both a durable state and a queue entry and two independent appenders
// listed it twice; and the `status === 'blocked'` branch, which could never
// fire — STATUSES.md says blocked-ness is `depends:`, and no note carries that
// status. Blocked is now computed from the link graph, server-side.

// ----- Activity + commits (TASK-0200) -----------------------------------

// ----- Changes tile (FEAT-0048 / TASK-0240) -----------------------------
// The history band's missing middle grain. Activity counts note churn by
// week, Commits shows what git saw; a CHG note is the only one of the
// three carrying a written reason for the change.
//
// Recent renders expanded, the pre-existing week/month buckets collapse
// beneath it. That shape is the owner's call (2026-07-29) over routing
// the archive through the Docs tree: the archive travels with the recent
// items rather than being left behind on a surface that no longer lists
// them.

interface ChangesPayload {
  total: number;
  recent: NavItem[];
  buckets: NavGroupData[];
}

async function fillChanges(
  wrap: HTMLElement, body: HTMLElement,
): Promise<void> {
  if (!sidecarBaseUrl) return;
  let data: ChangesPayload;
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/changes`);
    // An older sidecar has no such endpoint. Drop the tile rather than
    // leaving an empty box on the overview.
    if (!resp.ok) { wrap.remove(); return; }
    data = (await resp.json()) as ChangesPayload;
  } catch { wrap.remove(); return; }

  if (data.total === 0) {
    const p = document.createElement('p');
    p.className = 'meta';
    p.textContent = 'No change notes yet.';
    body.replaceChildren(p);
    return;
  }

  const head = wrap.querySelector('h3');
  if (head) {
    const count = document.createElement('span');
    count.className = 'ctx-card-right';
    count.textContent = String(data.total);
    head.appendChild(count);
  }

  const parts: HTMLElement[] = [];
  for (const item of data.recent) parts.push(buildChangeRow(item));
  if (data.recent.length === 0) {
    const p = document.createElement('p');
    p.className = 'meta';
    p.textContent = 'Nothing this week.';
    parts.push(p);
  }
  for (const bucket of data.buckets) parts.push(buildChangeBucket(bucket));
  body.replaceChildren(...parts);
}

// ----- History (FEAT-0052 / TASK-0256) ---------------------------------
//
// Replaced Activity, Changes and Commits. Those answered "what happened"
// three ways and every one of them made git or the filesystem the
// subject: a weekly edit count that never said *what*, the change notes
// which only cover work someone wrote a note for, and the git log with
// documents reduced to chips inside it.
//
// Here the row is a note's STATUS TRANSITION and the commit is a
// DIVIDER — "everything above this is not saved yet; this commit
// contained these". That is the ordering the whole system implies:
// documents are the record, git is where they are kept.
//
// Deleting the three was the point rather than a side effect. Landing
// beside them would have left the overview with four history surfaces,
// which is the shape PHASE-010 and PHASE-012 each closed by undoing.

interface HistoryTransition {
  id: string | null;
  type: string | null;
  title: string | null;
  rel: string | null;
  path: string;
  from: string | null;
  to: string;
  created: boolean;
}

interface HistoryCommit {
  sha: string;
  full_sha: string;
  date: string;
  author: string;
  subject: string;
  transitions: HistoryTransition[];
  undocumented: boolean;
}

interface HistoryPayload {
  available: boolean;
  commits: HistoryCommit[];
  uncommitted: Array<{
    id: string | null; type: string | null; title: string | null;
    rel: string | null; path: string; status: string | null; code: string;
  }>;
}

/** How many commits the overview's short version shows. The full view
 *  (`~history`) shows the rest — this is the "what happened lately"
 *  answer, not the archive. */
const HISTORY_TILE_COMMITS = 6;

/** The full history view (TASK-0257).
 *
 *  Same rows and dividers as the overview tile, further back — one
 *  grammar, not two. Grouped by day so a month is scannable rather than
 *  a wall, and it states its horizon: a view that stops at N commits
 *  without saying so reads as "this is everything".
 */
const HISTORY_PAGE_COMMITS = 60;

async function renderHistoryPage(at: string | null = null): Promise<boolean> {
  if (!sidecarBaseUrl) return false;
  docView.classList.remove('overview-pane', 'agents-page', 'design-page',
    'is-design-shell');
  docView.classList.add('history-page');
  docView.replaceChildren();

  const head = document.createElement('header');
  head.className = 'agents-head';
  const h1 = document.createElement('h1');
  h1.textContent = 'History';
  const sub = document.createElement('span');
  sub.className = 'agents-head-sub';
  sub.textContent = at
    ? `what changed state on or before ${at}`
    : 'what changed state, and which commit carried it';
  head.append(h1, sub);
  docView.appendChild(head);

  const gridMount = document.createElement('div');
  gridMount.className = 'ov-grid-mount is-page';
  docView.appendChild(gridMount);
  void fillContributionGrid(gridMount);

  const wrap = document.createElement('section');
  wrap.className = 'ov-section ov-history is-page';
  const body = document.createElement('div');
  body.className = 'ov-history-body';
  wrap.appendChild(body);
  docView.appendChild(wrap);
  await fillHistory(wrap, body, HISTORY_PAGE_COMMITS, false, at);

  // Say the horizon. Without this a truncated view reads as complete —
  // the same failure the fleet roll-up avoids by naming how many repos
  // it checked.
  const foot = document.createElement('p');
  foot.className = 'meta ov-history-horizon';
  foot.textContent = at
    ? `${HISTORY_PAGE_COMMITS} commits up to ${at}, touching docs/ or SNAPSHOT.yaml.`
    : `Last ${HISTORY_PAGE_COMMITS} commits touching docs/ or SNAPSHOT.yaml.`;
  docView.appendChild(foot);

  docView.hidden = false;
  placeholder.hidden = true;
  docView.scrollTop = 0;
  return true;
}

// ----- the contribution grid (TASK-0259) -------------------------------

interface ActivityPayload {
  available: boolean;
  days: Record<string, { transitions: number; commits: number }>;
  first_commit: string | null;
  last_commit: string | null;
  buckets: number[];
}

async function fillContributionGrid(mount: HTMLElement): Promise<void> {
  if (!sidecarBaseUrl) return;
  let data: ActivityPayload;
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/activity`);
    if (!resp.ok) { mount.remove(); return; }   // older sidecar
    data = (await resp.json()) as ActivityPayload;
  } catch { mount.remove(); return; }
  if (!data.available || !data.first_commit) { mount.remove(); return; }

  const weeks = buildGridWeeks(
    data.days, data.first_commit, data.buckets, new Date());
  mount.replaceChildren(buildGridElement(weeks, data));
}

function buildGridElement(
  weeks: ReturnType<typeof buildGridWeeks>, data: ActivityPayload,
): HTMLElement {
  const wrap = document.createElement('div');
  wrap.className = 'ov-grid';

  const months = document.createElement('div');
  months.className = 'ov-grid-months';
  // A cell should be locatable without hovering it.
  for (const { col, label } of gridMonthLabels(weeks)) {
    const el = document.createElement('span');
    el.textContent = label;
    el.style.gridColumn = String(col + 1);
    months.appendChild(el);
  }
  wrap.appendChild(months);

  const body = document.createElement('div');
  body.className = 'ov-grid-body';
  for (const column of weeks) {
    const col = document.createElement('div');
    col.className = 'ov-grid-col';
    for (const cell of column) {
      const el = document.createElement('button');
      el.type = 'button';
      el.className = 'ov-grid-cell';
      el.dataset.state = String(cell.state);
      if (cell.state === 'absent') {
        // Not a day with no activity — a day the project did not exist.
        el.disabled = true;
        el.setAttribute('aria-hidden', 'true');
      } else if (cell.state === 'empty') {
        el.disabled = true;
        el.title = `${cell.date} · nothing`;
      } else {
        el.title = `${cell.date} · ${cell.transitions} state change`
          + `${cell.transitions === 1 ? '' : 's'}, ${cell.commits} commit`
          + `${cell.commits === 1 ? '' : 's'}`;
        el.addEventListener('click', () => { void goToHistoryDate(cell.date); });
      }
      col.appendChild(el);
    }
    body.appendChild(col);
  }
  wrap.appendChild(body);

  const foot = document.createElement('div');
  foot.className = 'ov-grid-foot';
  const since = document.createElement('span');
  since.textContent = `since ${data.first_commit}`;
  foot.appendChild(since);

  // Year controls only once there is a second year to go to. On a
  // twelve-week repo a selector offers navigation to nothing.
  const years = gridYears(data.first_commit, data.last_commit);
  if (years.length > 1) {
    const picker = document.createElement('span');
    picker.className = 'ov-grid-years';
    for (const year of years) {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'ov-grid-year';
      b.textContent = String(year);
      b.addEventListener('click', () => { void goToHistoryDate(`${year}-12-31`); });
      picker.appendChild(b);
    }
    foot.appendChild(picker);
  }

  const legend = document.createElement('span');
  legend.className = 'ov-grid-legend';
  legend.textContent = 'less';
  for (const step of [1, 2, 3, 4]) {
    const s = document.createElement('i');
    s.dataset.state = String(step);
    legend.appendChild(s);
  }
  const more = document.createElement('span');
  more.textContent = 'more';
  legend.appendChild(more);
  legend.title = `steps: ≤${data.buckets[0]}, ≤${data.buckets[1]}, `
    + `≤${data.buckets[2]}, more — scaled to this project's own busiest days`;
  foot.appendChild(legend);
  wrap.appendChild(foot);
  return wrap;
}

/** Go to History with the window ANCHORED at a date.
 *
 *  The whole point of a cell: a destination, not a decoration.
 *
 *  The first cut navigated to `~history` and scrolled — which worked
 *  only for dates inside the loaded window. The grid spans the whole
 *  history and a page shows 60 commits, so clicking 2026-05-07 landed
 *  on 2026-07-28: the oldest commit that happened to be loaded, with no
 *  indication anything had gone wrong. Found in TASK-0259's live pass.
 *
 *  Anchoring the window at the date makes the day loaded by
 *  construction, so the scroll cannot miss.
 */
async function goToHistoryDate(date: string): Promise<void> {
  await navigateTo(`~history/${date}`);
  window.setTimeout(() => {
    const dividers = Array.from(
      docView.querySelectorAll<HTMLElement>('.ov-history-divider[data-date]'));
    const target = dividers.find((d) => d.dataset.date === date) ?? dividers[0];
    if (!target) return;
    target.scrollIntoView({ block: 'center' });
    target.classList.add('is-landed');
    window.setTimeout(() => target.classList.remove('is-landed'), 2000);
  }, 300);
}

function buildHistoryTile(_data: StatsPayload): HTMLElement {
  const wrap = document.createElement('section');
  wrap.className = 'ov-section ov-tile ov-history';
  const h = document.createElement('h3');
  h.textContent = 'History';

  wrap.appendChild(h);

  // The contribution grid replaces the 13-week sparkline (FEAT-0053).
  // Same question at far higher resolution, and — unlike the sparkline
  // — every cell is a destination. A cell that does not navigate is the
  // ornament this replaced, at higher resolution.
  const grid = document.createElement('div');
  grid.className = 'ov-grid-mount';
  wrap.appendChild(grid);
  void fillContributionGrid(grid);

  const body = document.createElement('div');
  body.className = 'ov-history-body';
  wrap.appendChild(body);
  void fillHistory(wrap, body, HISTORY_TILE_COMMITS, true);
  return wrap;
}

async function fillHistory(
  wrap: HTMLElement, body: HTMLElement, limit: number, short: boolean,
  until: string | null = null,
): Promise<void> {
  if (!sidecarBaseUrl) return;
  let data: HistoryPayload;
  try {
    const q = `limit=${limit}` + (until ? `&until=${encodeURIComponent(until)}` : '');
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/history?${q}`);
    // An older sidecar has no such endpoint. Drop the tile rather than
    // leaving an empty box on the overview.
    if (!resp.ok) { wrap.remove(); return; }
    data = (await resp.json()) as HistoryPayload;
  } catch { wrap.remove(); return; }

  const parts: HTMLElement[] = [];

  if (!data.available) {
    const p = document.createElement('p');
    p.className = 'meta';
    p.textContent = 'No git history for this workspace.';
    body.replaceChildren(p);
    return;
  }

  // Not saved yet — above the first divider, because that is where it
  // is in time. This is the half git history cannot answer.
  if (data.uncommitted.length > 0) {
    parts.push(buildUncommittedBand(data.uncommitted));
  }

  for (const commit of data.commits) {
    parts.push(buildCommitDivider(commit));
    for (const tr of commit.transitions) parts.push(buildTransitionRow(tr));
  }

  if (parts.length === 0) {
    const p = document.createElement('p');
    p.className = 'meta';
    p.textContent = 'Nothing recorded yet.';
    parts.push(p);
  }

  if (short) {
    const more = document.createElement('button');
    more.type = 'button';
    more.className = 'ov-history-more';
    more.textContent = 'Full history ›';
    more.addEventListener('click', () => { void navigateTo('~history'); });
    parts.push(more);
  }
  body.replaceChildren(...parts);
}

/** The uncommitted band. Says what is in flight, and says plainly that
 *  it is not saved — the question "is this written down yet" should not
 *  require leaving the page. */
function buildUncommittedBand(
  rows: HistoryPayload['uncommitted'],
): HTMLElement {
  const wrap = document.createElement('div');
  wrap.className = 'ov-history-uncommitted';
  const head = document.createElement('div');
  head.className = 'ov-history-divider is-uncommitted';
  head.textContent = `not committed yet · ${rows.length} file${rows.length === 1 ? '' : 's'}`;
  wrap.appendChild(head);
  for (const row of rows) {
    const el = document.createElement('button');
    el.type = 'button';
    el.className = 'ov-history-row is-uncommitted';
    if (row.id) el.dataset.noteId = row.id;
    if (row.rel) el.dataset.noteRel = row.rel;
    const sq = document.createElement('span');
    sq.className = 'ov-phase-sq';
    if (row.type) sq.dataset.type = row.type;
    const id = document.createElement('span');
    id.className = 'ov-history-id mono';
    id.textContent = row.id || row.path.split('/').pop() || row.path;
    const title = document.createElement('span');
    title.className = 'ov-history-title';
    // Empty rather than repeating the path already shown to its left —
    // `SNAPSHOT.yaml | SNAPSHOT.yaml` is noise, and an untracked
    // directory (git reports those as one entry) has no title at all.
    title.textContent = row.title || '';
    el.append(sq, id, title);
    if (row.status) {
      const st = document.createElement('span');
      st.className = 'ov-history-to';
      st.textContent = row.status;
      el.appendChild(st);
    }
    el.title = `${row.path} — ${row.code}`;
    if (row.rel) {
      el.addEventListener('click', () => { void navigateTo(row.rel as string); });
    } else {
      el.disabled = true;
    }
    wrap.appendChild(el);
  }
  return wrap;
}

/** A commit, as a divider rather than a row.
 *
 *  Subordinate on purpose: it is the boundary between in-flight and
 *  durable, not the unit of meaning. But NOT hidden — a commit that
 *  moved code with nothing recording why is the one worth seeing, and
 *  under a transition-based list it has no rows at all, so the flag has
 *  to live here or it disappears entirely (FEAT-0022's guardrail).
 */
function buildCommitDivider(commit: HistoryCommit): HTMLElement {
  const el = document.createElement('div');
  el.className = 'ov-history-divider';
  el.dataset.date = commit.date;   // the anchor a grid cell lands on
  if (commit.undocumented) el.classList.add('is-undocumented');

  const date = document.createElement('span');
  date.className = 'ov-history-date mono';
  date.textContent = commit.date.slice(5);

  const sha = document.createElement('span');
  sha.className = 'ov-history-sha mono';
  sha.textContent = commit.sha;

  const subject = document.createElement('span');
  subject.className = 'ov-history-subject';
  subject.textContent = commit.subject;

  el.append(date, sha, subject);
  if (commit.undocumented) {
    const flag = document.createElement('span');
    flag.className = 'ov-history-flag';
    flag.textContent = 'nothing documented';
    el.appendChild(flag);
  }
  el.title = `${commit.full_sha}\n${commit.author} · ${commit.date}`;
  return el;
}

/** One row: a note's state change. */
function buildTransitionRow(tr: HistoryTransition): HTMLElement {
  const el = document.createElement('button');
  el.type = 'button';
  el.className = 'ov-history-row';
  // Identity for the context menu (ISS-0079). These rows are BUTTONS,
  // not anchors, so the doc-link menu — which keyed off `closest('a')` —
  // never fired for them and a right-click fell through to the word
  // menu. Reported: "cannot copy a link, tried a feature link in the
  // history".
  if (tr.id) el.dataset.noteId = tr.id;
  if (tr.rel) el.dataset.noteRel = tr.rel;

  const sq = document.createElement('span');
  sq.className = 'ov-phase-sq';
  if (tr.type) sq.dataset.type = tr.type;
  if (isCompletedStatus(tr.to)) sq.dataset.bucket = 'done';

  const id = document.createElement('span');
  id.className = 'ov-history-id mono';
  id.textContent = tr.id || tr.path.split('/').pop() || tr.path;

  const title = document.createElement('span');
  title.className = 'ov-history-title';
  title.textContent = tr.title || '';

  const state = document.createElement('span');
  state.className = 'ov-history-to';
  // `created` renders as "new · done" rather than "→ done": most notes
  // in a busy commit are written and closed in one pass, and an arrow
  // would imply a journey the note never took.
  state.textContent = tr.created ? `new · ${tr.to}` : `${tr.from} → ${tr.to}`;

  el.append(sq, id, title, state);
  el.title = tr.rel || tr.path;
  const dest = tr.rel;
  if (dest) {
    el.addEventListener('click', () => { void navigateTo(dest); });
  } else {
    el.disabled = true;   // the note has since been deleted or renamed
  }
  return el;
}

function buildChangeRow(item: NavItem): HTMLElement {
  const rel = extractRel(item.url);
  const row = document.createElement('div');
  row.className = 'ov-change-row';
  const id = document.createElement('span');
  id.className = 'mono ov-typed';
  id.dataset.type = 'change';
  id.textContent = String(item.id || '');
  const title = document.createElement('span');
  title.className = 'ov-change-title';
  title.textContent = item.title || '';
  title.title = item.title || '';
  row.append(id, title);
  if (rel) {
    row.style.cursor = 'pointer';
    row.addEventListener('click', () => void navigateTo(rel));
  }
  return row;
}

// A bucket and its optional week sub-buckets, as nested disclosures —
// the same `ov-chev` affordance the record column's "N older" uses.
function buildChangeBucket(group: NavGroupData): HTMLElement {
  const wrap = document.createElement('div');
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'ctx-disclosure';
  const chev = document.createElement('span');
  chev.className = 'ov-chev';
  const label = document.createElement('span');
  const subs = group.subgroups ?? [];
  const count = (group.items ?? []).length
    + subs.reduce((n, s) => n + (s.items ?? []).length, 0);
  label.textContent = `${group.label} · ${count}`;
  btn.append(chev, label);
  const inner = document.createElement('div');
  inner.hidden = true;
  for (const item of group.items ?? []) inner.appendChild(buildChangeRow(item));
  for (const sub of subs) inner.appendChild(buildChangeBucket(sub));
  btn.addEventListener('click', () => {
    inner.hidden = !inner.hidden;
    btn.classList.toggle('is-open', !inner.hidden);
  });
  wrap.append(btn, inner);
  return wrap;
}

function buildCommitRow(commit: CommitRow): HTMLLIElement {
  const li = document.createElement('li');
  if (commit.undocumented) li.classList.add('is-undocumented');

  const sha = document.createElement('span');
  sha.className = 'ov-commit-sha mono';
  sha.textContent = commit.sha;
  sha.title = commit.full_sha;
  const date = document.createElement('span');
  date.className = 'ov-commit-date mono';
  date.textContent = commit.date.slice(5);      // MM-DD
  date.title = `${commit.date} · ${commit.author}`;
  const subject = document.createElement('span');
  subject.className = 'ov-commit-subject';
  subject.textContent = commit.subject;
  subject.title = commit.subject;
  li.append(sha, date, subject);

  const chips = document.createElement('span');
  chips.className = 'ov-commit-items';
  if (commit.undocumented) {
    // FEAT-0022's traceability guardrail, per commit: code moved and no
    // note recorded it.
    const flag = document.createElement('span');
    flag.className = 'ov-commit-flag';
    flag.textContent = 'no doc items';
    flag.title = 'This commit touched no project-os notes';
    chips.appendChild(flag);
  }
  for (const item of commit.items.slice(0, 4)) {
    const chip = document.createElement('button');
    chip.type = 'button';
    chip.className = 'ov-commit-chip';
    const id = document.createElement('span');
    id.className = 'mono ov-typed';
    id.dataset.type = item.type;
    // Display handle only (ISS-0084). The review desk was the one
    // surface the shortening had not reached — the third time in this
    // phase a change landed in some renderers and not all of them.
    id.textContent = shortNoteId(item.id);
    id.title = item.id;
    chip.appendChild(id);
    if (item.done) {
      const tick = document.createElement('span');
      tick.className = 'ov-commit-tick';
      tick.textContent = '✓';
      chip.appendChild(tick);
    }
    chip.title = `${item.id} ${item.title} (${item.status || '—'})`;
    chip.addEventListener('click', (e) => {
      e.stopPropagation();
      void navigateTo(item.rel);
    });
    chips.appendChild(chip);
  }
  if (commit.items.length > 4) {
    const more = document.createElement('span');
    more.className = 'ov-commit-more mono';
    more.textContent = `+${commit.items.length - 4}`;
    more.title = commit.items.slice(4).map((i) => `${i.id} ${i.title}`).join('\n');
    chips.appendChild(more);
  }
  li.appendChild(chips);
  return li;
}

function buildBottomGrid(data: StatsPayload): HTMLElement {
  const wrap = document.createElement('section');
  wrap.className = 'ov-section ov-bottom';

  // Activity histogram on the left.
  const activity = document.createElement('div');
  activity.className = 'ov-tile ov-activity';
  const maxCount = Math.max(1, ...data.activity.weekly.map((w) => w.count));
  const bars = data.activity.weekly.map((w) => {
    const pct = (w.count / maxCount) * 100;
    return `<span class="ov-act-bar" title="${w.week_iso} · ${w.count} change${w.count === 1 ? '' : 's'}" style="height:${pct}%"></span>`;
  }).join('');
  activity.innerHTML = `
    <h3>Activity (last 13 weeks)</h3>
    <div class="ov-act-chart">${bars}</div>
    <div class="ov-act-axis"><span>13w</span><span>now</span></div>`;
  wrap.appendChild(activity);

  // Donuts on the right.
  const donuts = document.createElement('div');
  donuts.className = 'ov-tile ov-donuts';
  donuts.innerHTML = '<h3>Status mix</h3>';
  const grid = document.createElement('div');
  grid.className = 'ov-donut-grid';
  for (const key of ['features', 'tasks', 'issues', 'requirements']) {
    const mix = data.status_mix[key] || {};
    const total = Object.values(mix).reduce((a, b) => a + b, 0);
    const d = document.createElement('div');
    d.className = 'ov-donut-cell';
    d.innerHTML = `
      <div class="ov-donut" style="background: ${donutGradient(mix)}">
        <div class="ov-donut-hole">${total}</div>
      </div>
      <div class="ov-donut-label">${key}</div>`;
    grid.appendChild(d);
  }
  donuts.appendChild(grid);
  wrap.appendChild(donuts);
  return wrap;
}

function buildRecentFeed(recent: StatsRecent[]): HTMLElement {
  const wrap = document.createElement('section');
  wrap.className = 'ov-section ov-feed';
  wrap.innerHTML = '<h3>Recent activity</h3>';
  if (recent.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'meta';
    empty.textContent = 'No changes recorded yet.';
    wrap.appendChild(empty);
    return wrap;
  }
  const ul = document.createElement('ul');
  ul.className = 'ov-feed-list';
  for (const r of recent) {
    const li = document.createElement('li');
    const typeTag = r.type
      ? `<span class="ov-feed-type ov-feed-type-${escapeHtml(r.type)}">${escapeHtml(r.type)}</span>`
      : '';
    // Display handle only (ISS-0084, reaching this surface at ISS-0099 —
    // the fourth straggler). `title` keeps the full value.
    const idTag = r.id
      ? `<span class="ov-feed-id" title="${escapeHtml(r.id)}">${escapeHtml(shortNoteId(r.id))}</span>`
      : '';
    const featTag = r.features && r.features.length
      ? `<span class="ov-feed-tag">${escapeHtml(r.features.join(', '))}</span>`
      : '';
    li.innerHTML = `
      <span class="ov-feed-date">${escapeHtml(r.date)}</span>
      ${typeTag}
      ${idTag}
      <span class="ov-feed-title">${escapeHtml(r.title)}</span>
      ${featTag}`;
    li.style.cursor = 'pointer';
    li.title = r.rel;
    li.addEventListener('click', () => {
      if (r.rel) {
        setNavMode('features');
        void navigateTo(r.rel);
      }
    });
    ul.appendChild(li);
  }
  wrap.appendChild(ul);
  return wrap;
}

// Wire the top-bar + rail-tools controls (FEAT-0015 iteration 2):
// mode icons + collapse buttons in the top bar; hide-completed +
// terminal + settings on the workspace rail. Runs once at startup
// after TYPE_ICONS / GROUP_ICONS are declared.
function initNavToolbar(): void {
  const modeIconMap: Record<string, string> = {
    // Lucide bar-chart: bars of varying heights — reads as "stats".
    overview: '<line x1="12" x2="12" y1="20" y2="10"/><line x1="18" x2="18" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="16"/>',
    features: TYPE_ICONS.feature,
    tasks:    TYPE_ICONS.task,
    issues:   TYPE_ICONS.issue,
    tests:    TYPE_ICONS.test,
    // Active: a "pulse/activity" line — work in motion. Retired from the
    // strip in TASK-0204; the entry stays so a stored preference or a
    // deep link still resolves an icon.
    active:   '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    // Review: a clipboard with a tick — the desk's queue (FEAT-0041).
    review:   '<rect x="8" y="2" width="8" height="4" rx="1"/>'
      + '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>'
      + '<path d="m9 14 2 2 4-4"/>',
    // Intent: a drafting compass — the instrument you set a shape with
    // before you build it, which is what this mode is for. Deliberately
    // not a paintbrush: the mode carries the project's identity and its
    // rules, not decoration.
    //
    // Keyed by `data-mode` (TASK-0385): when the mode id became `intent`
    // and this key did not, the lookup fell through to `TYPE_ICONS._default`
    // and the button silently lost its compass.
    intent:   '<circle cx="12" cy="5" r="2"/><path d="M12 7v3"/>'
      + '<path d="m10.5 10-5 10"/><path d="m13.5 10 5 10"/>',
    // Inbox: a tray. The one place things arrive before anyone has decided
    // what they are.
    inbox:    '<path d="M22 12h-6l-2 3h-4l-2-3H2"/>'
      + '<path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89'
      + 'A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/>',
    library:  TYPE_ICONS.reference,
    recent:   GROUP_ICONS.history,
  };
  document.querySelectorAll<HTMLButtonElement>('.top-bar-btn[data-mode]').forEach((btn) => {
    const mode = btn.dataset.mode as NavMode;
    const paths = modeIconMap[mode] || TYPE_ICONS._default;
    btn.replaceChildren(makeSvg(paths, 16, {}));
    btn.addEventListener('click', () => {
      if ((NAV_MODES as readonly string[]).includes(mode)) setNavMode(mode);
    });
  });

  // Collapse-completed: eye-strikethrough icon. Flips `hideCompleted`
  // and re-renders the nav.
  //
  // The name is historical and the behaviour is not: since TASK-0270 this
  // FOLDS each group at its first completed item rather than removing
  // items. It can shorten a view; it can no longer empty one, which is
  // what it did to three of them.
  const eyeOff = '<path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" x2="22" y1="2" y2="22"/>';
  hideCompletedBtn.replaceChildren(makeSvg(eyeOff, 16, {}));
  hideCompletedBtn.setAttribute('aria-pressed', hideCompleted ? 'true' : 'false');
  hideCompletedBtn.addEventListener('click', () => {
    hideCompleted = !hideCompleted;
    hideCompletedBtn.setAttribute('aria-pressed', hideCompleted ? 'true' : 'false');
    try { localStorage.setItem('cockpit:hide-completed', hideCompleted ? '1' : '0'); } catch { /* ignore */ }
    if (sidecarBaseUrl) void loadWsNav();
    // The right pane is NOT re-rendered: it no longer reads this state at
    // all (TASK-0269). It is a description of the open note, and a note's
    // completed children are what the note is made of — collapsing them
    // emptied FEAT-0051's context pane entirely.
  });

  // Terminal toggle (existing click handler registered later in the
  // file). Search opens the quick-switch palette; Pinned + Settings
  // are disabled placeholders. All SVGs injected here.
  terminalBtn.replaceChildren(makeSvg(GROUP_ICONS.terminal, 18, {}));
  const agentsBtn = document.getElementById('agents-toggle');
  if (agentsBtn) {
    agentsBtn.replaceChildren(makeSvg(GROUP_ICONS.agents, 18, {}));
    agentsBtn.addEventListener('click', () => {
      if (!sidecarBaseUrl) return;  // need a workspace open to host the page
      void navigateTo('~agents');
    });
  }
  // History from the rail (TASK-0260): reachable from any page, rather
  // than only by visiting the overview and finding a link at the bottom
  // of a tile. Same shape as the Agents button beside it — both are
  // pages, and neither is a left-pane nav mode.
  const historyBtn = document.getElementById('history-toggle');
  if (historyBtn) {
    historyBtn.replaceChildren(makeSvg(GROUP_ICONS.history, 18, {}));
    historyBtn.addEventListener('click', () => {
      if (!sidecarBaseUrl) return;  // need a workspace open to host the page
      void navigateTo('~history');
    });
  }
  if (followBtn) {
    followBtn.replaceChildren(makeSvg(GROUP_ICONS.follow, 18, {}));
    refreshFollowButton();
    followBtn.addEventListener('click', () => {
      if (!activeId) return;
      const next = !isFollowing(activeId);
      setFollowing(activeId, next);
      refreshFollowButton();
      showStatus(next ? 'Following agent navigation' : 'Manual — agent navigation ignored');
      scheduleHide(1500);
    });
  }
  const settingsBtn = document.getElementById('settings-toggle');
  if (settingsBtn) settingsBtn.replaceChildren(makeSvg(GROUP_ICONS.settings, 18, {}));
  const searchBtn = document.getElementById('search-toggle') as HTMLButtonElement | null;
  if (searchBtn) {
    searchBtn.replaceChildren(makeSvg(GROUP_ICONS.search, 18, {}));
    searchBtn.addEventListener('click', () => {
      if (quickSwitchEl.hidden) openQuickSwitch();
      else closeQuickSwitch();
    });
  }
  // Rail star removed — the per-doc pin now lives in the top bar
  // (right of the search field). Library mode shows the Pinned group.

  // Left-pane collapse — toggles .app.left-collapsed + syncs CSS
  // variables so the top-bar's left zone and the grid's nav column
  // both shrink to button-width.
  leftPaneCollapseBtn.addEventListener('click', () => {
    applyLeftPaneState(!appEl.classList.contains('left-collapsed'));
  });
  // Hydrate persisted state.
  let leftCollapsedInit = false;
  try {
    leftCollapsedInit = localStorage.getItem(LEFT_PANE_STORAGE_KEY) === '1';
  } catch { /* ignore */ }
  applyLeftPaneState(leftCollapsedInit);

  // Right-pane: paint icon now that PANEL_RIGHT_* paths exist.
  paintRightCollapse();

  refreshNavModeButtons();
}

// initModeRibbon() is invoked LATER — after TYPE_ICONS / GROUP_ICONS
// are declared (temporal-dead-zone). See the call near the bottom of
// the item-render port section.

// Platform filter (FEAT-0015 / TASK-0102). Persisted per-workspace
// because each project has its own platform vocabulary.

function platformStorageKey(): string {
  return `cockpit:platform:${activeId || '_'}`;
}

function loadStoredPlatform(): string {
  try {
    const v = localStorage.getItem(platformStorageKey());
    if (v) return v;
  } catch { /* ignore */ }
  return 'all';
}

function setPlatform(p: string): void {
  try { localStorage.setItem(platformStorageKey(), p); } catch { /* ignore */ }
  if (sidecarBaseUrl) void loadWsNav();
}

function renderPlatformBar(available: string[] | undefined): void {
  const list = available || [];
  if (list.length <= 1) {
    platformBarEl.hidden = true;
    return;
  }
  platformBarEl.hidden = false;
  const current = loadStoredPlatform();
  platformLabel.textContent = current;
  platformMenu.replaceChildren();
  for (const p of ['all', ...list]) {
    const li = document.createElement('li');
    li.textContent = p;
    li.dataset.value = p;
    li.setAttribute('role', 'option');
    if (p === current) li.classList.add('is-active');
    li.addEventListener('click', () => {
      closePlatformMenu();
      setPlatform(p);
    });
    platformMenu.appendChild(li);
  }
}

function openPlatformMenu(): void {
  platformMenu.hidden = false;
  platformCombo.setAttribute('aria-expanded', 'true');
}

function closePlatformMenu(): void {
  platformMenu.hidden = true;
  platformCombo.setAttribute('aria-expanded', 'false');
}

platformCombo.addEventListener('click', (e) => {
  e.stopPropagation();
  if (platformMenu.hidden) openPlatformMenu();
  else closePlatformMenu();
});

document.addEventListener('click', (e) => {
  if (platformMenu.hidden) return;
  const t = e.target as Node;
  if (!platformBarEl.contains(t)) closePlatformMenu();
});

document.addEventListener('keydown', (e) => {
  if (!platformMenu.hidden && e.key === 'Escape') closePlatformMenu();
});

async function loadWsNav(): Promise<void> {
  if (!sidecarBaseUrl) return;
  // Checked once at the top: exactly one landing branch runs per call, and
  // reading it per-branch would clear it in whichever happened to be first.
  const skipLanding = consumeLandingSuppression();
  if (currentNavMode === 'overview') {
    // Overview is a virtual page (FEAT-0023 / TASK-0130): route through
    // navigateTo so it lands in history and back/forward can reach it.
    const target = overviewScope ? `~overview/${overviewScope}` : '~overview';
    if (!skipLanding) void navigateTo(target, { replace: currentRel === target });
    return;
  }
  if (currentNavMode === 'review') {
    // Same virtual-page treatment for the desk (FEAT-0041 / TASK-0206).
    const target = currentRel && currentRel.startsWith('~review')
      ? currentRel : '~review';
    if (!skipLanding) void navigateTo(target, { replace: currentRel === target });
    return;
  }
  // FEAT-0092: land the three views that had no page, the same way Intent
  // does — the nav list still loads beneath, so this does NOT return early.
  // `startsWith` and not equality for the same reason Intent gives:
  // reselecting a mode while a note is open is not a request to lose your
  // place, so the landing is only claimed when nothing else is.
  if (VIEW_LANDING_RELS.has(`~${currentNavMode}`)) {
    const target = `~${currentNavMode}`;
    // Mirrors Intent's shape: land unless you are already on THIS view's
    // page. The first draft guarded on `startsWith('~')`, which read every
    // other view's landing as "somewhere you already are" — so arriving from
    // Overview left the reader on the overview with the Issues nav beside it.
    // Caught in the harness, not by a test, which is the argument for driving
    // a surface before calling it done.
    if (currentRel !== target && !skipLanding) {
      void navigateTo(target, { replace: false });
    }
  }
  if (currentNavMode === 'intent') {
    // Unlike Overview and Review, Design has BOTH a nav list and a page:
    // the left pane lists the design system and the proposals, the main
    // pane frames whichever is open. So this does not return early — it
    // lands on the register and then falls through to the nav fetch.
    //
    // `startsWith('~design')` and not an equality check: switching back
    // to Design while a specific artifact is open must keep that artifact
    // open. Reselecting a mode is not a request to lose your place.
    if ((!currentRel || !currentRel.startsWith('~design')) && !skipLanding) {
      void navigateTo('~design', { replace: false });
    }
  }
  const platform = loadStoredPlatform();
  const platformQ = platform && platform !== 'all'
    ? `&platform=${encodeURIComponent(platform)}` : '';
  // The server's Library mode emits a "Pinned" group when we hand it
  // the list of pinned rel-paths. Mode-1 cockpit uses the same query.
  const pins = activeId ? loadPinned(activeId) : [];
  const pinnedQ = pins.length > 0
    ? `&pinned=${encodeURIComponent(pins.join(','))}` : '';
  try {
    const resp = await fetch(
      `${sidecarBaseUrl}/api/cockpit/nav?mode=${encodeURIComponent(currentNavMode)}${platformQ}${pinnedQ}`,
    );
    if (!resp.ok) {
      showStatus(`Nav fetch failed: HTTP ${resp.status}`, 'error');
      return;
    }
    const data = (await resp.json()) as NavPayload;
    renderPlatformBar(data.available_platforms);
    renderWsNav(data);
  } catch (err) {
    showStatus(`Nav fetch failed: ${String(err)}`, 'error');
  }
}

function renderWsNav(data: NavPayload): void {
  wsNavPlaceholder.hidden = true;
  wsNavContent.hidden = false;
  wsNavContent.innerHTML = '';
  const groups = data.groups || [];
  if (groups.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'meta';
    empty.style.padding = '24px 16px';
    empty.textContent = `(no items for mode "${data.mode}")`;
    wsNavContent.appendChild(empty);
    return;
  }
  // TASK-0273: groups still holding open work render normally; everything
  // finished goes below a divider as ONE expandable line.
  //
  // FEAT-0056 made a finished group cost a 53px header plus a 25px fold
  // row. Eighteen of those is 1400px of chrome describing work nobody is
  // doing — the folding worked and the headers became the noise. Here 16
  // finished phases cost one line.
  //
  // Nothing is unreachable: two clicks (roll-up, then group) reach any
  // note, and `openGroupsContaining` opens both automatically when the
  // active note is inside — which at 99% completion is the normal path,
  // not an edge.
  // `Needs you` is lifted OUT of the live/settled split before it happens
  // (FEAT-0094). It was landing under the `Open · N` heading, which is a
  // heading about work in flight — and what needs a person is not a kind of
  // open work, it is the reason to be looking at the pane at all. Under that
  // heading it read as one more phase.
  const owedGroup = groups.find((g) => g.key === 'needs-you') || null;
  const rest = owedGroup ? groups.filter((g) => g !== owedGroup) : groups;

  const live: NavGroupData[] = [];
  const settled: NavGroupData[] = [];
  for (const group of rest) {
    (groupIsSettled(group.items || []) ? settled : live).push(group);
  }

  let any = false;
  if (owedGroup) {
    const section = document.createElement('div');
    section.className = 'nav-needs-you';
    const head = document.createElement('div');
    head.className = 'nav-needs-you-head';
    const label = document.createElement('span');
    label.textContent = 'Needs you';
    head.appendChild(label);
    // The same number, in the same shape as the button that carries it —
    // Edwin: *"it could do with a way to indicate that these are the issues
    // identified in the badge"*. A count rendered as a count would leave the
    // reader to notice the coincidence; rendered as the badge, it says so.
    const count = document.createElement('span');
    count.className = 'mode-badge nav-needs-you-count';
    count.textContent = String((owedGroup.items || []).length);
    head.appendChild(count);
    section.appendChild(head);
    // No caption. The count is rendered in the badge's own shape, which says
    // these are the items the button counts; a line saying so as well is the
    // surface explaining its own notation.
    const node = renderNavGroup(owedGroup, currentNavMode);
    if (node) { section.appendChild(node); }
    wsNavContent.appendChild(section);
    any = true;
  }
  // ISS-0089: where a divider names the finished set, the live set gets a
  // heading too. An unlabelled block above a labelled one reads as "and
  // these" rather than as its own half — Edwin asked for two SETS of
  // cards, and a set with no name is not one.
  if (live.length > 0 && settled.length > 0
      && !groupNamesStateThemselves(currentNavMode)) {
    const head = document.createElement('div');
    head.className = 'nav-set-heading';
    head.textContent = `Open · ${live.length}`;
    wsNavContent.appendChild(head);
  }
  for (const group of live) {
    const node = renderNavGroup(group, currentNavMode);
    if (node) {
      wsNavContent.appendChild(node);
      any = true;
    }
  }
  if (settled.length) {
    if (groupNamesStateThemselves(currentNavMode)) {
      // No divider: `Done`, `Cancelled` and `Superseded` name their own
      // state, so each simply sits in place as a collapsed card.
      for (const group of settled) {
        const node = renderNavGroup(group, currentNavMode);
        if (node) { wsNavContent.appendChild(node); any = true; }
      }
    } else {
      const node = renderSettledRollup(settled, currentNavMode);
      if (node) { wsNavContent.appendChild(node); any = true; }
    }
  }
  if (!any) {
    const empty = document.createElement('p');
    empty.className = 'meta';
    empty.style.padding = '24px 16px';
    // No hide-completed branch any more: since TASK-0270 a group folds
    // but never disappears, so an empty pane means the mode genuinely
    // has nothing in it.
    empty.textContent = `(no items for mode "${data.mode}")`;
    wsNavContent.appendChild(empty);
  }
  refreshActiveNavRow();
}

// ----------------------------------------------------------------------
// Item renderers (FEAT-0014 / TASK-0099) — ported from cockpit.js so the
// native renderer emits the same DOM as the browser cockpit. cockpit.css
// styles every selector below; no new CSS needed.
// ----------------------------------------------------------------------

const SVG_NS = 'http://www.w3.org/2000/svg';

// Lucide-style monochrome paths keyed by note type. Stroke uses
// currentColor so the per-type CSS tokens (cockpit.css) drive the hue.
const TYPE_ICONS: Record<string, string> = {
  feature:     '<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><path d="M4 22V15"/>',
  task:        '<path d="m9 11 3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
  issue:       '<polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/>',
  requirement: '<rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M12 11h4"/><path d="M12 16h4"/><path d="M8 11h.01"/><path d="M8 16h.01"/>',
  phase:       '<path d="M3 9h18"/><path d="M3 15h18"/><path d="M5 4v16"/><path d="M19 4v16"/><path d="M9 9v6"/><path d="M15 9v6"/>',
  change:      '<line x1="3" x2="9" y1="12" y2="12"/><line x1="15" x2="21" y1="12" y2="12"/><circle cx="12" cy="12" r="3"/>',
  adr:         '<path d="m16 16 3-8 3 8c-2 1-4 1-6 0z"/><path d="m2 16 3-8 3 8c-2 1-4 1-6 0z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>',
  decision:    '<path d="m16 16 3-8 3 8c-2 1-4 1-6 0z"/><path d="m2 16 3-8 3 8c-2 1-4 1-6 0z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>',
  risk:        '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="M12 8v4"/><path d="M12 16h.01"/>',
  test:        '<path d="M10 2v7.527a2 2 0 0 1-.211.896L4.72 20.55a1 1 0 0 0 .9 1.45h12.76a1 1 0 0 0 .9-1.45l-5.069-10.127A2 2 0 0 1 14 9.527V2"/><path d="M8.5 2h7"/><path d="M7 16h10"/>',
  workflow:    '<rect width="8" height="8" x="3" y="3" rx="2"/><path d="M7 11v4a2 2 0 0 0 2 2h4"/><rect width="8" height="8" x="13" y="13" rx="2"/>',
  release:     '<path d="M11 21.73a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73z"/><path d="M12 22V12"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="m7.5 4.27 9 5.15"/>',
  reference:   '<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>',
  plan:        '<path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3z"/><path d="M9 3v15"/><path d="M15 6v15"/>',
  _default:    '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/>',
};

const GROUP_ICONS: Record<string, string> = {
  agents:        '<rect width="16" height="10" x="4" y="10" rx="2"/><path d="M12 6v4"/><circle cx="12" cy="4" r="1.5"/><path d="M9 14h.01"/><path d="M15 14h.01"/><path d="M2 14h2"/><path d="M20 14h2"/>',
  follow:        '<circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="2.5"/><path d="M12 2v3"/><path d="M12 19v3"/><path d="M2 12h3"/><path d="M19 12h3"/>',
  star:          '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
  folder_tree:   '<path d="M20 10a1 1 0 0 0 1-1V6a1 1 0 0 0-1-1h-2.5a1 1 0 0 1-.8-.4l-.9-1.2A1 1 0 0 0 15 3h-2a1 1 0 0 0-1 1v5a1 1 0 0 0 1 1Z"/><path d="M20 21a1 1 0 0 0 1-1v-3a1 1 0 0 0-1-1h-2.9a1 1 0 0 1-.88-.55l-.42-.85a1 1 0 0 0-.92-.6H13a1 1 0 0 0-1 1v5a1 1 0 0 0 1 1Z"/><path d="M3 5a2 2 0 0 0 2 2h3"/><path d="M3 3v13a2 2 0 0 0 2 2h3"/>',
  layers:        '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 12.18-9.43 4.27a2 2 0 0 1-1.66 0L2 12.18"/><path d="m22 17.18-9.43 4.27a2 2 0 0 1-1.66 0L2 17.18"/>',
  list_checks:   '<path d="m3 17 2 2 4-4"/><path d="m3 7 2 2 4-4"/><path d="M13 6h8"/><path d="M13 12h8"/><path d="M13 18h8"/>',
  alert_octagon: '<polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/>',
  sun:           '<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>',
  moon:          '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
  calendar_days: '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/><path d="M8 14h.01"/><path d="M12 14h.01"/><path d="M16 14h.01"/><path d="M8 18h.01"/><path d="M12 18h.01"/><path d="M16 18h.01"/>',
  calendar:      '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/>',
  history:       '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/>',
  search:        '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
  graph:         '<circle cx="12" cy="5" r="3"/><circle cx="5" cy="19" r="3"/><circle cx="19" cy="19" r="3"/><path d="M10.6 7.4 6.4 16.6"/><path d="m13.4 7.4 4.2 9.2"/>',
  settings:      '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.5a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/>',
  terminal:      '<path d="m7 11 2-2-2-2"/><path d="M11 13h4"/><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>',
};

function typeIcon(type: string | undefined, size = 14): SVGElement | null {
  if (!type) return null;
  const key = String(type).toLowerCase();
  const paths = TYPE_ICONS[key] || TYPE_ICONS._default;
  return makeSvg(paths, size, { class: 'type-icon', 'data-type': key });
}

function makeSvg(
  paths: string,
  size: number,
  attrs: Record<string, string>,
): SVGElement {
  const svg = document.createElementNS(SVG_NS, 'svg');
  for (const [k, v] of Object.entries(attrs)) svg.setAttribute(k, v);
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('width', String(size));
  svg.setAttribute('height', String(size));
  svg.setAttribute('fill', 'none');
  svg.setAttribute('stroke', 'currentColor');
  svg.setAttribute('stroke-width', '2');
  svg.setAttribute('stroke-linecap', 'round');
  svg.setAttribute('stroke-linejoin', 'round');
  svg.setAttribute('aria-hidden', 'true');
  svg.innerHTML = paths;
  return svg;
}

// Lucide panel-left / panel-right SVGs — the shapes the HTML cockpit
// uses for its sidebar toggles (matches cockpit.js). Chevron points
// inward when the pane is open ("click to close") and outward when
// collapsed ("click to open").
const PANEL_LEFT_CLOSE =
  '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>'
  + '<line x1="9" x2="9" y1="3" y2="21"/>'
  + '<path d="m16 15-3-3 3-3"/>';
const PANEL_LEFT_OPEN =
  '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>'
  + '<line x1="9" x2="9" y1="3" y2="21"/>'
  + '<path d="m13 15 3-3-3-3"/>';
const PANEL_RIGHT_CLOSE =
  '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>'
  + '<line x1="15" x2="15" y1="3" y2="21"/>'
  + '<path d="m8 9 3 3-3 3"/>';
const PANEL_RIGHT_OPEN =
  '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>'
  + '<line x1="15" x2="15" y1="3" y2="21"/>'
  + '<path d="m11 9-3 3 3 3"/>';

const RECENT_BUCKET_ICONS: Record<string, string> = {
  today:     GROUP_ICONS.sun,
  yesterday: GROUP_ICONS.moon,
  week:      GROUP_ICONS.calendar_days,
  month:     GROUP_ICONS.calendar,
  earlier:   GROUP_ICONS.history,
};

function groupIcon(mode: NavMode, group: NavGroupData): SVGElement | null {
  const key = String(group.key || '');
  if (key === 'pinned')    return makeSvg(GROUP_ICONS.star, 13, { class: 'group-icon' });
  if (key === 'docs-tree') return makeSvg(GROUP_ICONS.folder_tree, 13, { class: 'group-icon' });
  if (key.indexOf('rare:') === 0) return typeIcon(key.slice(5), 13);
  if (mode === 'features') return makeSvg(GROUP_ICONS.layers, 13, { class: 'group-icon' });
  if (mode === 'tasks')    return makeSvg(GROUP_ICONS.list_checks, 13, { class: 'group-icon', 'data-status': key });
  if (mode === 'issues')   return makeSvg(GROUP_ICONS.alert_octagon, 13, { class: 'group-icon', 'data-severity': key });
  if (mode === 'recent')   return makeSvg(RECENT_BUCKET_ICONS[key] || GROUP_ICONS.history, 13, { class: 'group-icon' });
  return null;
}

function statusChip(status: string | undefined): HTMLSpanElement | null {
  if (!status) return null;
  const span = document.createElement('span');
  span.className = 'status-chip';
  span.dataset.status = status.toLowerCase().replace(/\s+/g, '-');
  span.textContent = status;
  return span;
}

function navLineSpacer(): HTMLSpanElement {
  const s = document.createElement('span');
  s.className = 'nav-line-spacer';
  return s;
}

function appendIf<T extends Node>(parent: Node, child: T | null): void {
  if (child) parent.appendChild(child);
}

// ----- Item layout dispatcher

type ItemRenderer = (item: NavItem) => HTMLLIElement;

function pickItemRenderer(layout: string | undefined): ItemRenderer {
  if (layout === 'stacked') return navItemStacked;
  if (layout === 'compact') return navItemCompact;
  return navItem;
}

// ----- Default layout (Features / Tasks / Issues / Recent)
// row 1: [icon] [id] [spacer] [status]
// row 2: [title]
// row 3: [subtitle] (when present)

/** The one row every lifecycle list uses (ISS-0085).
 *
 *  There were four renderers and TASK-0271 rewrote one of them, so risks
 *  and designs (`stacked`) and requirements and plans (`nested`) kept the
 *  old two-line card — 90px at worst, against the 27px the record column
 *  sets. `pickItemRenderer` sits three lines from `navItem` and I never
 *  followed it; the guard was written from the same reading, so it agreed.
 *
 *  One builder now, differing only by an indent class. A row that renders
 *  differently per group is a decision, and there was no decision here —
 *  only three copies that drifted apart.
 *
 *  `item.subtitle` is deliberately NOT rendered. It is the second line,
 *  and the server sends one for every feature (`goal`), design and risk
 *  (first body paragraph) — 50 rows in the pilot workspace. The left pane
 *  is a selection list; a summary belongs in the note, not in the list of
 *  things you might open.
 */
function buildNavRow(item: NavItem, extraClass?: string): HTMLLIElement {
  const li = document.createElement('li');
  const rel = extractRel(item.url);
  if (rel) li.dataset.rel = rel;
  if (item.id) li.dataset.id = String(item.id);
  if (item.type) li.dataset.type = String(item.type);
  if (item.status) li.dataset.status = String(item.status);

  const card = document.createElement('div');
  // `nav-item-line`, NOT `nav-item-compact`: that class is already taken
  // by the Library's file rows in `cockpit.css`, where it paints a file
  // icon via ::before.
  card.className = `nav-item nav-item-line${extraClass ? ` ${extraClass}` : ''}`;

  const line = document.createElement('div');
  line.className = 'nav-line';
  // The id column is a COLUMN: an absent value has to occupy it, not skip
  // it. A plan child carries `id: ""` deliberately (an untyped plan still
  // gets a row), and without this its title took the id's place and sat
  // 78px left of its sibling requirements (ISS-0090).
  //
  // The type is the handle in that case — `PLAN` — which is what an id is
  // for a note that has no number of its own.
  const handle = item.id || (item.type ? item.type.toUpperCase() : '');
  if (handle) {
    const idSpan = document.createElement('span');
    idSpan.className = 'nav-id mono ov-typed' + (item.id ? '' : ' is-typeless');
    if (item.type) idSpan.dataset.type = String(item.type);
    // Display handle only — `data-id` on the `li` keeps the full value,
    // and every lookup goes through that (ISS-0084).
    idSpan.textContent = item.id ? shortNoteId(item.id) : handle;
    idSpan.title = item.id || handle;
    line.appendChild(idSpan);
  }
  if (item.title) {
    const titleEl = document.createElement('span');
    titleEl.className = 'nav-title';
    titleEl.textContent = item.title;
    titleEl.title = item.title;
    line.appendChild(titleEl);
  } else {
    line.appendChild(navLineSpacer());
  }
  // Agent chip (TASK-0164): a live session is touching this note. Kept
  // through the compaction deliberately — it is the one thing on the row
  // that is not derivable from the note, and the reason to be looking at
  // the pane at all.
  if (item.id && sessionTouchedIds.has(item.id)) {
    const chip = document.createElement('span');
    chip.className = 'nav-agent-chip';
    chip.textContent = 'agent';
    chip.title = 'A live agent session is working on this';
    line.appendChild(chip);
  }
  // Suppressed when the whole group shares one status — the head says it
  // once instead (TASK-0272).
  if (!item.chipSuppressed) appendIf(line, statusChip(item.status));
  card.appendChild(line);

  if (rel) {
    card.addEventListener('click', (e) => {
      e.stopPropagation();
      void navigateTo(rel);
    });
  }
  li.appendChild(card);
  return li;
}

/** What the children toggle says a feature carries (TASK-0367).
 *
 *  Counts by type. Before tasks joined the child list (TASK-0366) this was
 *  "everything that is not a plan is a requirement", which a feature with 3
 *  requirements, a plan and 14 tasks would have reported as
 *  "17 requirements · plan". */
function childrenSummary(kids: NavItem[]): string {
  const n = (type: string): number => kids.filter((k) => k.type === type).length;
  const reqs = n('requirement');
  const plans = n('plan');
  const tasks = n('task');
  const other = kids.length - reqs - plans - tasks;
  const parts: string[] = [];
  if (reqs) parts.push(`${reqs} requirement${reqs === 1 ? '' : 's'}`);
  if (plans) parts.push(plans === 1 ? 'plan' : `${plans} plans`);
  if (tasks) parts.push(`${tasks} task${tasks === 1 ? '' : 's'}`);
  if (other) parts.push(`${other} other`);
  return parts.join(' · ');
}

function navItem(item: NavItem): HTMLLIElement {
  const li = buildNavRow(item);
  // ISS-0088: the expand affordance goes ON the row's line, not on a line
  // of its own. It used to be a `<details><summary>2 requirements · plan`
  // beneath the feature — a second row describing the first.
  //
  // The button's PRESENCE is the signal that a feature has requirements
  // or a plan, which is what the label was spending a whole row saying.
  const kids = openFirst(item.children || []);
  if (kids.length) {
    const list = document.createElement('ul');
    list.className = 'nav-item-children-list';
    list.hidden = true;
    // Fold on VOLUME (TASK-0367). Tasks joined this list in TASK-0366 and
    // the largest feature carries 48 of them; the median carries 3. The
    // same limit and the same helper the nav groups use — folding at the
    // first completed item when Hide-completed is on, on length always.
    const foldedKids = foldGroup(kids, NAV_GROUP_FOLD_LIMIT, hideCompleted);
    for (const child of foldedKids.head) list.appendChild(navItemNested(child));
    if (foldedKids.hidden > 0) {
      // The same row the groups use, for the same reason: the count is
      // never optional, and revealing happens in place rather than by
      // flipping a preference that governs every other list on screen.
      const li = document.createElement('li');
      li.className = 'nav-item nav-more';
      const moreBtn = document.createElement('button');
      moreBtn.type = 'button';
      moreBtn.className = 'nav-more-btn';
      moreBtn.textContent = `… ${foldedKids.hidden} more`;
      moreBtn.title = 'Show the rest of this feature\u2019s children';
      moreBtn.addEventListener('click', (ev) => {
        ev.stopPropagation();
        ev.preventDefault();
        list.replaceChildren(...kids.map((c) => navItemNested(c)));
      });
      li.appendChild(moreBtn);
      list.appendChild(li);
    }

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'nav-children-toggle';
    btn.setAttribute('aria-expanded', 'false');
    btn.title = childrenSummary(kids);
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      e.preventDefault();
      list.hidden = !list.hidden;
      btn.classList.toggle('is-open', !list.hidden);
      btn.setAttribute('aria-expanded', list.hidden ? 'false' : 'true');
    });
    const line = li.querySelector('.nav-line');
    if (line) line.insertBefore(btn, line.firstChild);
    li.appendChild(list);
  }
  return li;
}

// Risks and designs. Identical to the default now — the "stacked" layout
// existed to give a rare type more room, and more room is the thing being
// removed. Kept as a distinct function only because the server still
// sends `item_layout: "stacked"` and the picker still routes on it.
function navItemStacked(item: NavItem): HTMLLIElement {
  return buildNavRow(item);
}

// ----- Compact layout (Library Docs tree)

function navItemCompact(item: NavItem): HTMLLIElement {
  const li = document.createElement('li');
  const rel = extractRel(item.url);
  if (rel) li.dataset.rel = rel;
  if (item.id) li.dataset.id = String(item.id);
  if (item.type) li.dataset.type = String(item.type);
  if (item.status) li.dataset.status = String(item.status);

  const card = document.createElement('div');
  card.className = 'nav-item nav-item-compact' + (item.type ? ' has-type-icon' : '');
  appendIf(card, item.type ? typeIcon(item.type, 12) : null);
  const titleSpan = document.createElement('span');
  titleSpan.className = 'nav-title-compact';
  titleSpan.textContent = item.title || '';
  titleSpan.title = item.title || '';
  card.appendChild(titleSpan);

  if (rel) {
    card.addEventListener('click', (e) => { e.stopPropagation(); void navigateTo(rel); });
  }
  li.appendChild(card);
  return li;
}

// ----- Nested layout (requirements and plans under features)

// The same row, indented. It carried its own two-line card until
// ISS-0085 — 103 rows of it in the pilot workspace.
function navItemNested(item: NavItem): HTMLLIElement {
  return buildNavRow(item, 'nav-item-nested');
}

function renderItemChildren(item: NavItem): HTMLDetailsElement | null {
  // Children order open-first like every other list (TASK-0267). Mode 1
  // did this from the start and mode 3 did not — the review caught the
  // two surfaces disagreeing, which is the failure mode a hand-written
  // twin has by construction.
  const kids = openFirst(item.children || []);
  if (!kids.length) return null;
  const details = document.createElement('details');
  details.className = 'nav-item-children';
  const summary = document.createElement('summary');
  summary.className = 'nav-item-children-toggle';
  const chevron = document.createElement('span');
  chevron.className = 'nav-children-chevron';
  chevron.setAttribute('aria-hidden', 'true');
  summary.appendChild(chevron);
  const label = document.createElement('span');
  // Requirements were the only child type until FEAT-0046 nested the
  // delivery plan here too, so a hardcoded "N requirements" would have
  // counted the plan as one — the kind of quietly wrong label nobody
  // reads twice.
  const plans = kids.filter((k) => k.type === 'plan').length;
  const rest = kids.length - plans;
  const parts: string[] = [];
  if (rest) parts.push(`${rest} requirement${rest === 1 ? '' : 's'}`);
  if (plans) parts.push(plans === 1 ? 'plan' : `${plans} plans`);
  label.textContent = parts.join(' · ');
  summary.appendChild(label);
  details.appendChild(summary);
  const list = document.createElement('ul');
  list.className = 'nav-item-children-list';
  for (const child of kids) list.appendChild(navItemNested(child));
  details.appendChild(list);
  return details;
}

// ----- Group + left-pane assembly

/** Modes whose group names already say a group is finished, so a
 *  `Completed` divider would only repeat them (TASK-0276).
 *
 *  The tasks navigator groups BY status: `Done`, `Cancelled`,
 *  `Superseded`. Three collapsed cards under a heading reading "Completed"
 *  would be the word four times over.
 *
 *  Everywhere else the group name is on some other axis — a phase title, a
 *  severity, a verdict — and says nothing about state, so the divider is
 *  the only thing that can.
 *
 *  Named for WHY it holds rather than listed as "modes that want one":
 *  the next navigator added should be able to answer the question rather
 *  than look for itself in a list.
 */
/** True when a group's LABEL names a category rather than a thing
 *  (ISS-0089).
 *
 *  `Done`, `Critical`, `Designs` are categories: scaffolding you read past
 *  to reach the rows, so the faint uppercase label treatment the context
 *  pane uses is exactly right, and a frame around each reads as structure.
 *
 *  `PHASE-007 · Agent instrumentation` is a THING. It is the content, and
 *  rendering it faint hides what the pane was opened to find — while
 *  eighteen frames around eighteen things read as clutter rather than
 *  structure.
 *
 *  Four rounds of this phase were spent making the two heads match. They
 *  should not.
 */
function groupLabelIsCategory(mode: NavMode): boolean {
  return mode !== 'features';
}

function groupNamesStateThemselves(mode: NavMode): boolean {
  // `tests` joins `tasks` here (TASK-0371) for the same reason and with more
  // force: its groups are `Needs a run` / `Failing` / `Stale` / `Verified`,
  // which ARE the states. Rolling them under a "settled" divider would file
  // `Verified` — the answer the view exists to give, and today all 23 of
  // them — behind a line that says nothing about tests at all.
  return mode === 'tasks' || mode === 'tests';
}

/** Nouns for the roll-up line, per mode.
 *
 *  "16 finished phases · 53 features" reads; "16 finished groups · 53
 *  items" does not, and the whole value of one line is that it says what
 *  is behind it. */
const ROLLUP_NOUNS: Record<string, { group: [string, string]; item: [string, string] }> = {
  features: { group: ['phase', 'phases'], item: ['feature', 'features'] },
  tasks:    { group: ['bucket', 'buckets'], item: ['task', 'tasks'] },
  issues:   { group: ['bucket', 'buckets'], item: ['issue', 'issues'] },
  // Present for completeness, not because it renders: `tests` groups name
  // their own state (`groupNamesStateThemselves`), so the settled roll-up is
  // never built for this mode. Leaving the entry out would make that a
  // coincidence of two functions agreeing rather than a stated fact.
  tests:    { group: ['group', 'groups'], item: ['test', 'tests'] },
  intent:   { group: ['group', 'groups'], item: ['design', 'designs'] },
  library:  { group: ['group', 'groups'], item: ['note', 'notes'] },
  review:   { group: ['verdict', 'verdicts'], item: ['note', 'notes'] },
  active:   { group: ['group', 'groups'], item: ['item', 'items'] },
  recent:   { group: ['group', 'groups'], item: ['note', 'notes'] },
};

function plural(n: number, pair: [string, string]): string {
  return `${n} ${n === 1 ? pair[0] : pair[1]}`;
}

/** Whether the `Completed · N` band is open, per nav mode.
 *
 *  Persisted, and defaulting to OPEN — both to match the overview's scope
 *  pane, which has worked this way since FEAT-0043 and is the surface
 *  Edwin actually reads.
 *
 *  The first version was a bare `<details>`: closed by default and with
 *  no persistence, so it re-closed on every navigation. That hid *which
 *  phases exist* (ISS-0086), and a phase list is a taxonomy rather than a
 *  backlog. Collapsing a group's BODY hides items nobody is working on;
 *  collapsing its HEAD hides the shape of the project.
 *
 *  Quantity lives in the bodies, structure lives in the heads. The
 *  roll-up applied one rule to both.
 */
function navCompletedBandOpen(mode: NavMode): boolean {
  try {
    const v = localStorage.getItem(`cockpit:nav-completed-open:${mode}`);
    return v === null ? true : v === '1';
  } catch { return true; }
}

/** Everything finished, under a heading rather than behind a door
 *  (TASK-0273, corrected by ISS-0086). */
function renderSettledRollup(
  groups: NavGroupData[], mode: NavMode,
): HTMLElement | null {
  if (!groups.length) return null;
  const items = groups.reduce((n, g) => n + (g.items || []).length, 0);
  const nouns = ROLLUP_NOUNS[mode]
    || { group: ['group', 'groups'] as [string, string], item: ['item', 'items'] as [string, string] };

  const details = document.createElement('details');
  details.className = 'nav-group nav-rollup';
  details.open = navCompletedBandOpen(mode);
  const summary = document.createElement('summary');
  summary.className = 'nav-group-header nav-rollup-header';
  const chevron = document.createElement('span');
  chevron.className = 'group-chevron';
  chevron.setAttribute('aria-hidden', 'true');
  summary.appendChild(chevron);
  const label = document.createElement('span');
  label.className = 'nav-rollup-label';
  // `Completed · N` — the overview's exact wording, so one idea does not
  // wear two names across two panes. The count is never optional: a band
  // that does not say how much is behind it is indistinguishable from an
  // empty pane, which is the failure FEAT-0056 exists to have fixed.
  label.textContent = `Completed · ${groups.length}`;
  const sub = document.createElement('span');
  sub.className = 'nav-rollup-sub';
  sub.textContent = plural(items, nouns.item);
  summary.append(label, sub);
  details.appendChild(summary);

  details.addEventListener('toggle', () => {
    try {
      localStorage.setItem(
        `cockpit:nav-completed-open:${mode}`, details.open ? '1' : '0',
      );
    } catch { /* ignore */ }
  });

  const body = document.createElement('div');
  body.className = 'nav-rollup-body';
  for (const g of groups) {
    const node = renderNavGroup(g, mode);
    if (node) body.appendChild(node);
  }
  details.appendChild(body);
  return details;
}

function renderNavGroup(group: NavGroupData, mode: NavMode): HTMLElement | null {
  // TASK-0270: the switch COLLAPSES rather than hides.
  //
  // It used to filter, and at 99% lifecycle completion that is not a
  // filter. Measured with it on: 1 of 18 feature groups survived, 0 of the
  // 4 issue severity buckets, and 5 item rows of 270 tasks. Turning it on
  // to reduce noise deleted the view.
  //
  // Now the group always renders and `foldGroup` decides how much of it
  // does. Two independent reasons to fold, and the distinction is the
  // whole point:
  //
  //   collapse (the switch)  fold at the first completed item — MEANING
  //   NAV_GROUP_FOLD_LIMIT   fold at a length nobody reads past — VOLUME
  //
  // Neither empties the VIEW: a fully collapsed group cuts to zero rows
  // and stays visible through its header and its `… N more` count, which
  // is where visibility belongs. (An earlier draft kept one sample row
  // for this and said so here; showing the first item by ID reads as if
  // that item were the notable one.)
  // The tasks pane is where volume actually bites (270 rows across five
  // status buckets, 261 of them in one); the switch is where meaning does.
  const folded = foldGroup(group.items || [], NAV_GROUP_FOLD_LIMIT, hideCompleted);
  // When the head says the status, the rows must not repeat it.
  const chipSuppressed = uniformStatus(group.items || []) !== null;
  const visibleItems = folded.head.map(
    (it) => (chipSuppressed ? { ...it, chipSuppressed: true } : it),
  );
  const visibleSubgroups: HTMLElement[] = [];
  for (const sub of group.subgroups || []) {
    const node = renderNavGroup(sub, mode);
    if (node) visibleSubgroups.push(node);
  }
  // A collapsed group cuts to zero rows and is still a group: the header
  // and the count are what keep it visible. Only a genuinely empty group
  // renders nothing.
  if (visibleItems.length === 0 && visibleSubgroups.length === 0
      && folded.hidden === 0) {
    return null;
  }

  const details = document.createElement('details');
  const layoutClass = group.item_layout ? ` nav-group-${group.item_layout}` : '';
  details.className = `nav-group${layoutClass}`;
  // TASK-0275: a settled group opens SHUT — exactly `renderContextGroup`'s
  // rule, which is why the right pane reads the way it does. A shut card
  // still carries its name and count, so nothing is hidden that the head
  // did not already say.
  //
  // The server's `default_open: false` still wins: this adds a reason to
  // close, never a reason to open.
  const settledGroup = groupIsSettled(group.items || []);
  (details as HTMLDetailsElement).open =
    group.default_open !== false && !settledGroup;

  const summary = document.createElement('summary');
  summary.className = 'nav-group-header';
  const chevron = document.createElement('span');
  chevron.className = 'group-chevron';
  chevron.setAttribute('aria-hidden', 'true');
  summary.appendChild(chevron);
  const inner = document.createElement('span');
  inner.className = 'group-header-inner';
  // ISS-0088: the head uses the ROW's grammar — a type-coloured ID and a
  // name — rather than an icon and one flat string. The icon was a third
  // encoding of a fact the ID already carries in colour, and the ID
  // itself was buried inside the label so it could not be coloured at all.
  const rawLabel = group.label || group.key || '';
  if (!groupLabelIsCategory(mode)) summary.classList.add('is-thing');
  const split = /^([A-Z]+-\d+)\s*·\s*(.*)$/.exec(rawLabel);
  if (split) {
    const idSpan = document.createElement('span');
    idSpan.className = 'nav-id mono ov-typed';
    idSpan.dataset.type = 'phase';
    idSpan.textContent = split[1];
    const nameSpan = document.createElement('span');
    nameSpan.className = 'group-header-name';
    nameSpan.textContent = split[2];
    nameSpan.title = split[2];
    inner.append(idSpan, nameSpan);
  } else {
    const labelSpan = document.createElement('span');
    labelSpan.className = 'group-header-name';
    labelSpan.textContent = rawLabel;
    labelSpan.title = rawLabel;
    inner.appendChild(labelSpan);
  }
  // ISS-0132: the head OPENS the thing it names. The server has always sent
  // `url` on a group that names a note -- every phase group carries
  // `/docs/phases/PHASE-...md`, and `NavGroupData.url` was declared here --
  // and nothing ever read it, so the navigator organised entirely around
  // phases could not reach one. Sharper since REL-0001 was re-scoped to be
  // defined by phase exit criteria: the release's own definition lived in a
  // note this view listed and could not open.
  //
  // The label navigates, the chevron folds. Binding the whole `summary`
  // would take the fold away, which is the one thing the head already did.
  const groupRel = extractRel(group.url);
  if (groupRel) {
    // `data-rel` on the summary, so `refreshActiveNavRow` finds the head the
    // same way it finds a row and the selected phase highlights like the
    // selected feature (Edwin, 2026-08-11 -- it did not, because that sweep
    // walks `li[data-rel]` and a group head is a `<summary>`).
    summary.dataset.rel = groupRel;
    summary.classList.add('is-navigable');
    summary.title = `Open ${group.key || 'this note'}`;
    summary.addEventListener('click', (ev) => {
      // THE WHOLE HEAD OPENS THE NOTE, and the chevron alone folds -- one
      // grammar with the feature row, which selects from anywhere on the card
      // and keeps a separate control for its children. Binding only the label
      // (the first cut) meant a click an inch to the right folded the group
      // instead of opening it: the same row doing two things depending on
      // which pixel was hit.
      if ((ev.target as HTMLElement | null)?.closest('.group-chevron')) return;
      // `summary` toggles `<details>` by default; this click navigates
      // instead, so the default has to go or the group collapses underneath
      // the reader as the note opens.
      ev.preventDefault();
      void navigateTo(groupRel);
    });
  }
  summary.appendChild(inner);
  const sp = document.createElement('span');
  sp.className = 'nav-group-spacer';
  summary.appendChild(sp);
  // TASK-0272: the head carries the count, and the status when every item
  // shares one — `PHASE-007 · Agent instrumentation · 19 · done`. This is
  // the record column's own move: its DECISIONS card says "7 · all
  // accepted" once rather than printing "accepted" on seven rows.
  // Where the group name IS the status, the summary is the count alone —
  // `Done · 265`, not `Done · 265 · done`. Same fact as the divider rule
  // one function up: these names already state themselves.
  // A head that names a THING takes the overview scope row's trailing
  // form — `✓ 8` for a finished phase, a plain count for a live one
  // (ISS-0090). It said `2 · done` beside a `done` pill, inside a band
  // headed `Completed`: the same word three times.
  const items = group.items || [];
  let summaryText: string;
  if (!groupLabelIsCategory(mode)) {
    summaryText = items.length ? (settledGroup ? `✓ ${items.length}` : String(items.length)) : '';
  } else if (groupNamesStateThemselves(mode)) {
    summaryText = String(items.length || '');
  } else {
    summaryText = groupHeadSummary(items);
  }
  if (summaryText) {
    const cnt = document.createElement('span');
    cnt.className = 'nav-group-summary'
      + (!groupLabelIsCategory(mode) && settledGroup ? ' is-done' : '');
    cnt.textContent = summaryText;
    summary.appendChild(cnt);
  }
  // The pill is shown unless the group's own NAME already says it.
  //
  // Two wrong answers preceded this one. First it was suppressed when the
  // item summary happened to end in the same word — defensible, and the
  // output looked random (PHASE-001 bare, PHASE-002 pilled). Then
  // ISS-0088 made it unconditional, which put a `done` pill on a card
  // called `Done`.
  //
  // Neither "always" nor "never" was right: the question is whether the
  // LABEL is already the status, which is the same question the divider
  // and the head summary ask. One rule, three uses.
  // …and no pill where the head names a thing: the overview's scope rows
  // never had one, and inside a band headed `Completed` it is the word a
  // third time.
  if (group.status && !groupNamesStateThemselves(mode) && groupLabelIsCategory(mode)) {
    appendIf(summary, statusChip(group.status));
  }
  details.appendChild(summary);

  const body = document.createElement('div');
  body.className = 'group-body';
  const renderItem = pickItemRenderer(group.item_layout);
  const ul = document.createElement('ul');
  ul.className = 'nav-items';
  for (const item of visibleItems) ul.appendChild(renderItem(item));
  if (folded.hidden > 0) {
    // The count is never optional. A fold that hides the fact that it hid
    // something is indistinguishable from having nothing there — which is
    // precisely how the old switch managed to empty three views without
    // ever looking broken.
    const li = document.createElement('li');
    li.className = 'nav-item nav-more';
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'nav-more-btn';
    btn.textContent = `… ${folded.hidden} more`;
    btn.title = 'Show the rest of this group';
    btn.addEventListener('click', (ev) => {
      ev.stopPropagation();
      // Reveal in place. Deliberately NOT a state change on
      // `hideCompleted`: expanding one group must not silently flip a
      // preference that governs every other group on the surface.
      const all = openFirst(group.items || []).map(
        (it) => (chipSuppressed ? { ...it, chipSuppressed: true } : it),
      );
      ul.replaceChildren(...all.map((item) => renderItem(item)));
    });
    li.appendChild(btn);
    ul.appendChild(li);
  }
  body.appendChild(ul);
  for (const sub of visibleSubgroups) body.appendChild(sub);
  details.appendChild(body);
  return details;
}

function extractRel(url: string | undefined): string | null {
  if (!url) return null;
  if (url.startsWith('/docs/')) return url.slice('/docs/'.length);
  // A virtual page (`~design/DES-0001`, `~review/...`) is a legitimate nav
  // target and `navigateTo` already routes it. Returning null here made a
  // Library row that pointed at one a dead click: the row got no data-rel,
  // and the delegated handler keys entirely off data-rel (found by Edwin,
  // 2026-07-28 — the second reachability bug in this surface).
  if (url.startsWith('~')) return url;
  // NOT routed here: `/README.md` and the other top-level project files the
  // Library emits. Routing them looked like a free bonus fix while closing
  // ISS-0033 and was not — `/docs/README.md` and `/README.md` both reduce to
  // `README.md`, so two distinct Library rows collapsed onto one fetch and
  // whichever file the server preferred won. Those rows stay dead clicks
  // (ISS-0037) until the rel carries the disambiguator the url has.
  //
  // The identity band is unaffected: it calls `navigateTo(brief.rel)`
  // directly and never passes through here.
  return null;
}

// Initialise the in-workspace toolbar now that TYPE_ICONS / GROUP_ICONS
// are declared (avoids the temporal-dead-zone error that bit us once).
initNavToolbar();

// ----------------------------------------------------------------------
// Right pane (FEAT-0010 / TASK-0085)
// ----------------------------------------------------------------------

interface ContextItem {
  id?: string;
  title?: string;
  status?: string;
  url?: string;
  type?: string;
}

interface ContextGroup {
  type?: string;
  items?: ContextItem[];
}

interface ContextPayload {
  schema_version: number;
  platform: string;
  active?: { id?: string; title?: string; url?: string } | null;
  linked?: ContextGroup[];
  backlinks?: ContextGroup[];
}

const RIGHT_PANE_STORAGE_KEY = 'cockpit:right-pane-collapsed';

function loadStoredRightPane(): boolean {
  try {
    return localStorage.getItem(RIGHT_PANE_STORAGE_KEY) === '1';
  } catch {
    return false;
  }
}

function applyRightPaneState(collapsed: boolean, paint = true): void {
  appEl.classList.toggle('right-collapsed', collapsed);
  try { localStorage.setItem(RIGHT_PANE_STORAGE_KEY, collapsed ? '1' : '0'); }
  catch { /* ignore */ }
  // Sync the CSS variable so the top-bar's right zone tracks the
  // actual column width (collapsed = 28 px, otherwise the stored
  // splitter width).
  if (collapsed) {
    // Pane fully hidden; the top-bar-right's min-width keeps the
    // toggle button visible at the right edge of the toolbar.
    appEl.style.setProperty('--right-width', '0px');
  } else {
    const stored = loadStoredWidth('cockpit:right-width', 280);
    appEl.style.setProperty('--right-width', `${stored}px`);
  }
  if (paint) paintRightCollapse();
}

const LEFT_PANE_STORAGE_KEY = 'cockpit:left-collapsed';

function applyLeftPaneState(collapsed: boolean, paint = true): void {
  appEl.classList.toggle('left-collapsed', collapsed);
  try { localStorage.setItem(LEFT_PANE_STORAGE_KEY, collapsed ? '1' : '0'); }
  catch { /* ignore */ }
  if (collapsed) {
    appEl.style.setProperty('--nav-width', '0px');
  } else {
    const stored = loadStoredWidth('cockpit:nav-width', 240);
    appEl.style.setProperty('--nav-width', `${stored}px`);
  }
  if (paint) paintLeftCollapse();
}

function paintLeftCollapse(): void {
  const collapsed = appEl.classList.contains('left-collapsed');
  const paths = collapsed ? PANEL_LEFT_OPEN : PANEL_LEFT_CLOSE;
  leftPaneCollapseBtn.replaceChildren(makeSvg(paths, 16, { class: 'panel-left-icon' }));
  leftPaneCollapseBtn.title = collapsed ? 'Show navigator pane' : 'Hide navigator pane';
}

function paintRightCollapse(): void {
  const collapsed = appEl.classList.contains('right-collapsed');
  const paths = collapsed ? PANEL_RIGHT_OPEN : PANEL_RIGHT_CLOSE;
  rightPaneToggle.replaceChildren(makeSvg(paths, 16, { class: 'panel-right-icon' }));
  rightPaneToggle.title = collapsed ? 'Show context pane' : 'Hide context pane';
}

// Hydrate persisted state on launch (paint*Collapse repaint after
// TYPE_ICONS / PANEL_* are declared — those are below in source
// order, so the *_INITIAL paint happens inside initNavToolbar()).
applyRightPaneState(loadStoredRightPane(), /* paint */ false);

rightPaneToggle.addEventListener('click', () => {
  applyRightPaneState(!appEl.classList.contains('right-collapsed'));
});

// ----------------------------------------------------------------------
// Resizable splitters (FEAT-0009 / TASK-0096)
// ----------------------------------------------------------------------

const NAV_WIDTH_MIN = 180;
const NAV_WIDTH_MAX = 480;
const RIGHT_WIDTH_MIN = 200;
const RIGHT_WIDTH_MAX = 520;

function loadStoredWidth(key: string, fallback: number): number {
  try {
    const v = localStorage.getItem(key);
    if (v) {
      const n = parseInt(v, 10);
      if (Number.isFinite(n) && n > 0) return n;
    }
  } catch { /* ignore */ }
  return fallback;
}

function setNavWidth(px: number): void {
  const clamped = Math.max(NAV_WIDTH_MIN, Math.min(NAV_WIDTH_MAX, px));
  appEl.style.setProperty('--nav-width', `${clamped}px`);
  try { localStorage.setItem('cockpit:nav-width', String(clamped)); } catch { /* ignore */ }
}

function setRightWidth(px: number): void {
  const clamped = Math.max(RIGHT_WIDTH_MIN, Math.min(RIGHT_WIDTH_MAX, px));
  appEl.style.setProperty('--right-width', `${clamped}px`);
  try { localStorage.setItem('cockpit:right-width', String(clamped)); } catch { /* ignore */ }
}

// Apply persisted widths on launch.
setNavWidth(loadStoredWidth('cockpit:nav-width', 240));
setRightWidth(loadStoredWidth('cockpit:right-width', 280));

function attachSplitter(el: HTMLElement, axis: 'nav' | 'right'): void {
  el.addEventListener('mousedown', (downEv) => {
    downEv.preventDefault();
    el.classList.add('is-dragging');
    // Capture starting widths so the drag delta is stable even if the
    // cursor moves outside the splitter element during the drag.
    const navStart = parseInt(getComputedStyle(appEl).getPropertyValue('--nav-width'), 10) || 240;
    const rightStart = parseInt(getComputedStyle(appEl).getPropertyValue('--right-width'), 10) || 280;
    const startX = downEv.clientX;
    const onMove = (moveEv: MouseEvent): void => {
      const dx = moveEv.clientX - startX;
      if (axis === 'nav') setNavWidth(navStart + dx);
      else setRightWidth(rightStart - dx); // dragging RIGHT shrinks the right pane
    };
    const onUp = (): void => {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
      el.classList.remove('is-dragging');
    };
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  });
}

attachSplitter($<HTMLDivElement>('#splitter-nav'), 'nav');
attachSplitter($<HTMLDivElement>('#splitter-right'), 'right');

async function loadRightPane(rel: string): Promise<void> {
  if (!sidecarBaseUrl) return;
  try {
    const resp = await fetch(
      `${sidecarBaseUrl}/api/cockpit/context?this=${encodeURIComponent(rel)}`,
    );
    if (!resp.ok) {
      rightPaneContent.innerHTML = `<p class="meta">Context fetch failed: HTTP ${resp.status}</p>`;
      return;
    }
    const data = (await resp.json()) as ContextPayload;
    renderRightPane(data);
  } catch (err) {
    rightPaneContent.innerHTML = `<p class="meta">Context fetch failed: ${escapeHtml(String(err))}</p>`;
  }
}

// Stash the most recent payload so we can re-render when the hide-
// completed filter toggles without re-fetching.
let lastContextPayload: ContextPayload | null = null;

function renderRightPane(data: ContextPayload): void {
  lastContextPayload = data;
  const linked = data.linked || [];
  const backlinks = data.backlinks || [];
  rightPaneContent.innerHTML = '';
  const linkedNode = linked.length > 0 ? renderContextSection('Links from this note', linked) : null;
  const backlinksNode = backlinks.length > 0 ? renderContextSection('Backlinks', backlinks) : null;
  if (!linkedNode && !backlinksNode) {
    const msg = (linked.length === 0 && backlinks.length === 0)
      ? 'No links from or to this note.'
      : 'Everything linked here is completed (toggle the eye icon to show).';
    rightPaneContent.innerHTML = `<p class="meta">${msg}</p>`;
    void fillChangeShapeCard(currentFrontmatterId() ?? '');
    return;
  }
  if (linkedNode) rightPaneContent.appendChild(linkedNode);
  if (backlinksNode) rightPaneContent.appendChild(backlinksNode);
  // The shape of what this note's commits touched (ISS-0096). Last, and
  // absent when git has nothing — it is context for a judgment, not a claim
  // the note makes about itself.
  void fillChangeShapeCard(currentFrontmatterId() ?? '');
}

function renderContextSection(heading: string, groups: ContextGroup[]): HTMLElement | null {
  const sectionChildren: HTMLElement[] = [];
  for (const group of groups) {
    const node = renderContextGroup(group);
    if (node) sectionChildren.push(node);
  }
  if (sectionChildren.length === 0) return null;
  const wrap = document.createElement('div');
  wrap.className = 'right-pane-section';
  const h = document.createElement('h3');
  h.textContent = heading;
  h.style.cssText = 'margin: 0 0 8px; font-size: 11px; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; color: var(--text-faint);';
  wrap.appendChild(h);
  for (const node of sectionChildren) wrap.appendChild(node);
  return wrap;
}

function renderContextGroup(group: ContextGroup): HTMLElement | null {
  // FEAT-0014 / TASK-0099: right pane uses the same nav-item renderers
  // as the in-workspace nav.
  //
  // FEAT-0015 made it obey hide-completed too, "so the right pane stays
  // in sync with the left". TASK-0269 undoes that: the two panes are not
  // the same kind of thing. The left pane is a SELECTION LIST, where a
  // completed item is one you are not going to click. The right pane is a
  // DESCRIPTION — a note's completed children are what the note is made
  // of, and FEAT-0051's five done tasks ARE FEAT-0051.
  //
  // Measured with the switch on: FEAT-0051 and ISS-0080 rendered an
  // ENTIRELY EMPTY context pane, PHASE-016 kept 1 group of 7, FEAT-0028
  // 3 of 11. At 91% complete the emptied pane was the normal case.
  //
  // The pressure that justifies folding elsewhere is also absent here:
  // everything shown is already scoped to one note, and the largest group
  // measured anywhere in the corpus is 11 items. There is no wall to
  // scroll past. The group types settle it — `change` is 100% complete
  // and `test` 96%, so a state filter here does not thin those groups, it
  // forbids them.
  //
  // State still ORDERS (TASK-0267): one open task among nine done sits at
  // the top. It just never removes — `collapse` is passed as false.
  //
  // LENGTH still folds, though. My first pass skipped the fold here on
  // the grounds that "the largest group measured anywhere is 11 items";
  // the review caught that as a measurement of ONE note. Swept across the
  // whole corpus, 11 of 3192 context groups exceed it and PHASE-007 renders
  // a 79-item backlinks group. The wall is real, so the length rule
  // applies here exactly as it does on the left — which is the point of
  // its being a length rule.
  const folded = contextGroupRows(group.items || [], CONTEXT_GROUP_FOLD_LIMIT);
  const visible = folded.head;
  if (visible.length === 0 && folded.hidden === 0) return null;
  // TASK-0274: a record card — a head naming the type with its count and
  // status, and a body that is CLOSED when every item in it is terminal.
  //
  // Closing a body is not filtering, and the distinction is the whole
  // reason this is allowed where TASK-0269's filter was not: a closed
  // card still says the relationship exists, what type it is, and how
  // many. The filter said nothing at all — FEAT-0051's pane rendered
  // empty. The structural guarantee is unchanged above: `contextGroupRows`
  // has no parameter with which to filter, so a disclosure default cannot
  // quietly become one.
  const items = group.items || [];
  const settled = groupIsSettled(items);
  const div = document.createElement('details');
  div.className = 'right-pane-group ctx-card';
  div.open = !settled;
  const h = document.createElement('summary');
  h.className = 'ctx-card-head';
  const chev = document.createElement('span');
  chev.className = 'ov-chev';
  chev.setAttribute('aria-hidden', 'true');
  const name = document.createElement('span');
  name.textContent = pluralizeType(group.type) || '';
  h.append(chev, name);
  const summaryText = groupHeadSummary(items);
  if (summaryText) {
    const cnt = document.createElement('span');
    cnt.className = 'ctx-card-right';
    // `5 · done` when uniform, `6 · 5 done` when mixed — the record
    // column's own `7 · all accepted` move (TASK-0272).
    cnt.textContent = summaryText;
    h.appendChild(cnt);
  }
  div.appendChild(h);
  const chipSuppressed = uniformStatus(items) !== null;
  const ul = document.createElement('ul');
  ul.className = 'nav-items';
  for (const item of visible) {
    // Inject type from the group so the ID's type colour resolves even
    // when the server didn't echo it onto each item.
    const enriched: NavItem = {
      ...item, type: item.type || group.type, chipSuppressed,
    };
    ul.appendChild(navItem(enriched));
  }
  if (folded.hidden > 0) {
    const li = document.createElement('li');
    li.className = 'nav-item nav-more';
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'nav-more-btn';
    btn.textContent = `… ${folded.hidden} more`;
    btn.title = 'Show the rest of this group';
    btn.addEventListener('click', (ev) => {
      ev.stopPropagation();
      const all = openFirst(group.items || []);
      ul.replaceChildren(...all.map(
        (it) => navItem({ ...it, type: it.type || group.type, chipSuppressed })));
    });
    li.appendChild(btn);
    ul.appendChild(li);
  }
  div.appendChild(ul);
  return div;
}

function pluralizeType(t: string | undefined): string {
  if (!t) return '';
  // Mirror the cockpit's plural mapping (server.py INDEX_TYPE_PLURALS,
  // inverted).
  const map: Record<string, string> = {
    feature: 'Features', task: 'Tasks', requirement: 'Requirements',
    issue: 'Issues', risk: 'Risks', adr: 'Decisions', change: 'Changes',
    release: 'Releases', workflow: 'Workflows', test: 'Tests',
    phase: 'Phases', reference: 'References',
  };
  return map[t] || t.charAt(0).toUpperCase() + t.slice(1);
}

/** Open every collapsed ancestor of the active row (TASK-0273).
 *
 *  `refreshActiveNavRow` sets `is-active` on whichever `li` matches
 *  `data-rel`. A row inside a closed `<details>` is in the DOM and
 *  matches — so without this the pane would highlight a row nobody can
 *  see, and show no selection at all while claiming one.
 *
 *  Navigating to a finished note is not the rare case: 99% of the corpus
 *  is finished, so this is the normal path.
 */
function openGroupsContaining(li: Element): void {
  let node: Element | null = li.parentElement;
  while (node && node !== wsNavContent) {
    if (node instanceof HTMLDetailsElement) node.open = true;
    node = node.parentElement;
  }
}

function refreshActiveNavRow(): void {
  // Drop any prior is-active, then add it to the row matching
  // `currentRel`. Stripping the fragment so #anchor nav doesn't
  // de-highlight the parent doc.
  const rel = currentRel ? stripFragment(currentRel) : null;
  // ISS-0083: this selected `li.nav-item`, but `navItem` puts that class
  // on the DIV inside the `li` — so it matched no navigable row and the
  // highlight never appeared. Measured at f5e6637: 112 rows carrying
  // `data-rel`, `is-active` on zero of them after navigating to one.
  //
  // The stylesheet was right all along (`.nav-item.is-active` targets the
  // div); only the selector was wrong. The `li` stays the handle for
  // walking up to the enclosing `<details>`.
  wsNavContent.querySelectorAll<HTMLLIElement>('li[data-rel]').forEach((li) => {
    const isActive = !!rel && li.dataset.rel === rel;
    const card = li.querySelector('.nav-item');
    if (card) card.classList.toggle('is-active', isActive);
    if (isActive) openGroupsContaining(li);
  });
  // Group heads that name a note highlight on the same rule (ISS-0132). They
  // are `<summary>` rather than `li`, so the sweep above cannot see them and
  // an open phase showed no selection at all -- the one row on the surface
  // that could be current and never looked it.
  wsNavContent.querySelectorAll<HTMLElement>('summary[data-rel]').forEach((summary) => {
    summary.classList.toggle('is-active', !!rel && summary.dataset.rel === rel);
  });
}

// ----------------------------------------------------------------------
// Find in document (FEAT-0012 / TASK-0089)
// ----------------------------------------------------------------------

let findMarks: HTMLElement[] = [];
let findCurrentIndex = 0;

function clearFindMarks(): void {
  for (const mark of findMarks) {
    const parent = mark.parentNode;
    if (!parent) continue;
    while (mark.firstChild) parent.insertBefore(mark.firstChild, mark);
    parent.removeChild(mark);
    parent.normalize();
  }
  findMarks = [];
}

function runFind(query: string): void {
  clearFindMarks();
  findCurrentIndex = 0;
  if (!query) {
    findCount.textContent = '0 / 0';
    return;
  }
  const q = query.toLowerCase();
  // TreeWalker over docView's text nodes; skip empty / pure-whitespace.
  const walker = document.createTreeWalker(
    docView, NodeFilter.SHOW_TEXT,
    {
      acceptNode: (node) => {
        const text = node.nodeValue || '';
        if (!text || !text.toLowerCase().includes(q)) return NodeFilter.FILTER_REJECT;
        // Don't re-walk into an existing find-mark.
        let p: Node | null = node.parentNode;
        while (p && p !== docView) {
          if (p instanceof HTMLElement && p.classList.contains('find-match')) {
            return NodeFilter.FILTER_REJECT;
          }
          p = p.parentNode;
        }
        return NodeFilter.FILTER_ACCEPT;
      },
    },
  );
  const matches: Text[] = [];
  let n: Node | null;
  while ((n = walker.nextNode())) matches.push(n as Text);
  // Split + wrap each match. Iterate in reverse on each text node so
  // earlier matches don't invalidate the index of later ones inside the
  // same node.
  for (const textNode of matches) {
    const text = textNode.nodeValue || '';
    const lower = text.toLowerCase();
    const positions: number[] = [];
    let idx = lower.indexOf(q);
    while (idx >= 0) {
      positions.push(idx);
      idx = lower.indexOf(q, idx + q.length);
    }
    if (positions.length === 0) continue;
    // Walk positions backwards: splitText returns the trailing
    // fragment; we wrap the leading fragment of the trailing piece.
    let remaining = textNode;
    for (let i = positions.length - 1; i >= 0; i--) {
      const at = positions[i];
      const after = remaining.splitText(at + q.length);
      const matchNode = remaining.splitText(at);
      const mark = document.createElement('mark');
      mark.className = 'find-match';
      mark.textContent = matchNode.nodeValue || '';
      matchNode.parentNode?.replaceChild(mark, matchNode);
      findMarks.unshift(mark);
      // `after` becomes our `remaining` for the previous (earlier)
      // match within this same text node — but only `remaining` (the
      // surviving prefix) needs further splitting. We continue with
      // `remaining` which is now the prefix before this match.
      void after; // suppress unused-var
    }
  }
  if (findMarks.length === 0) {
    findCount.textContent = '0 / 0';
    return;
  }
  setFindCurrent(0);
}

function setFindCurrent(idx: number): void {
  for (const mark of findMarks) mark.classList.remove('is-current');
  findCurrentIndex = ((idx % findMarks.length) + findMarks.length) % findMarks.length;
  const cur = findMarks[findCurrentIndex];
  cur.classList.add('is-current');
  cur.scrollIntoView({ block: 'center', behavior: 'smooth' });
  findCount.textContent = `${findCurrentIndex + 1} / ${findMarks.length}`;
}

function openFindBar(): void {
  findBar.hidden = false;
  findInput.value = '';
  clearFindMarks();
  findCount.textContent = '0 / 0';
  findInput.focus();
}

function closeFindBar(): void {
  clearFindMarks();
  findBar.hidden = true;
  findInput.value = '';
}

findInput.addEventListener('input', () => {
  runFind(findInput.value.trim());
});

findInput.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') { e.preventDefault(); closeFindBar(); }
  else if (e.key === 'Enter') {
    e.preventDefault();
    if (findMarks.length > 0) {
      setFindCurrent(findCurrentIndex + (e.shiftKey ? -1 : 1));
    }
  }
});
findPrevBtn.addEventListener('click', () => {
  if (findMarks.length > 0) setFindCurrent(findCurrentIndex - 1);
});
findNextBtn.addEventListener('click', () => {
  if (findMarks.length > 0) setFindCurrent(findCurrentIndex + 1);
});
findCloseBtn.addEventListener('click', closeFindBar);

// Global ⌘F / Ctrl+F opens. Clears stale marks when the centre
// doc is re-mounted via navigateTo (already calls clearFindMarks
// implicitly via the DOM replacement, but we belt-and-brace below).
document.addEventListener('keydown', (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'f') {
    e.preventDefault();
    if (findBar.hidden) openFindBar();
    else closeFindBar();
  }
});

// ----------------------------------------------------------------------
// Native context menus (FEAT-0012 / TASK-0090)
// ----------------------------------------------------------------------

listEl.addEventListener('contextmenu', (e) => {
  const target = e.target as HTMLElement | null;
  const li = target?.closest('li.ws-square[data-id]') as HTMLLIElement | null;
  if (!li || !li.dataset.id) return;
  e.preventDefault();
  const ws = workspaces.find((w) => w.id === li.dataset.id);
  if (!ws) return;
  void cockpitApi.app.showContextMenu('rail', {
    workspaceId: ws.id,
    root: ws.root,
  });
});

// Shared row context menu: nav rows AND the right pane's linked /
// backlinks cards use the same nav-item markup, so both get the same
// menu (Open / Copy ID / Copy path / Reveal / Agent verbs).
function navRowContextMenu(e: MouseEvent): void {
  const target = e.target as HTMLElement | null;
  // The `nav-item` class is on the inner card div, not the <li> —
  // the li carries the data attributes (ISS-0005).
  const li = target?.closest('li[data-rel]') as HTMLLIElement | null;
  if (!li || !li.dataset.rel) return;
  e.preventDefault();
  const rel = li.dataset.rel;
  const id = li.querySelector('.nav-id')?.textContent || '';
  const activeWs = workspaces.find((w) => w.id === activeId);
  void cockpitApi.app.showContextMenu('nav-row', {
    id, rel,
    workspaceId: activeId || '',
    root: activeWs?.root || '',
    verbs: verbsForId(id, { type: li.dataset.type, status: li.dataset.status })
      .map((v) => ({ key: v.key, label: v.label })),
    currentAgent: loadDispatchAgent(),
    agents: agentRegistry,
  });
}

wsNavContent.addEventListener('contextmenu', navRowContextMenu);
rightPaneContent.addEventListener('contextmenu', navRowContextMenu);

docView.addEventListener('contextmenu', (e) => {
  const target = e.target as HTMLElement | null;

  // Anchors in rendered markdown, OR any element that carries a note's
  // identity (ISS-0079). The History rows, the uncommitted band and the
  // fleet roll-up are BUTTONS, so keying only off `closest('a')` meant a
  // right-click on a feature in History got the word menu and no way to
  // copy anything about it.
  const carrier = target?.closest('[data-note-rel]') as HTMLElement | null;
  const anchor = target?.closest('a') as HTMLAnchorElement | null;
  if (!carrier && !anchor) return;

  let rel: string;
  let linkId: string;
  let href: string;
  if (carrier) {
    rel = carrier.dataset.noteRel || '';
    linkId = (carrier.dataset.noteId || '').toUpperCase();
    href = `/docs/${rel}`;
  } else {
    href = anchor!.getAttribute('href') || '';
    const cls = classifyLink(href);
    if (cls.kind !== 'docs') return;
    rel = cls.rel;
    linkId = (anchor!.textContent || '').match(/^((TASK|ISS|FEAT|REQ|PHASE|RISK)-\d+)/i)?.[1]?.toUpperCase()
      || (cls.rel.split('/').pop() || '').match(/^((TASK|ISS|FEAT|REQ|PHASE|RISK)-\d+)/i)?.[1]?.toUpperCase()
      || '';
    href = anchor!.href || href;
  }
  if (!rel) return;
  e.preventDefault();
  const activeWs = workspaces.find((w) => w.id === activeId);
  const cls = { rel };
  void cockpitApi.app.showContextMenu('doc-link', {
    id: linkId,
    rel: cls.rel,
    url: href,
    workspaceId: activeId || '',
    root: activeWs?.root || '',
    verbs: linkId ? verbsForId(linkId).map((v) => ({ key: v.key, label: v.label })) : [],
    currentAgent: loadDispatchAgent(),
    agents: agentRegistry,
  });
});

// ----------------------------------------------------------------------
// Drag-and-drop note (FEAT-0012 / TASK-0091)
// ----------------------------------------------------------------------

const dragOverlay = document.createElement('div');
dragOverlay.className = 'drop-overlay';
dragOverlay.hidden = true;
dragOverlay.textContent = 'Drop a .md note to navigate';
document.body.appendChild(dragOverlay);

let dragEnterDepth = 0;

document.addEventListener('dragenter', (e) => {
  if (e.dataTransfer && Array.from(e.dataTransfer.items).some((i) => i.kind === 'file')) {
    dragEnterDepth += 1;
    dragOverlay.hidden = false;
  }
});

document.addEventListener('dragleave', () => {
  dragEnterDepth -= 1;
  if (dragEnterDepth <= 0) {
    dragEnterDepth = 0;
    dragOverlay.hidden = true;
  }
});

// Paste an image straight from the clipboard (FEAT-0045). `⌘⇧⌃ 4` puts a
// screenshot on the macOS clipboard, so this needs NO file on disk — strictly
// fewer steps than saving and dragging, which is the point of the feature.
// Same destination and same code path as drop, so neither becomes the good one
// and the other a trap.
document.addEventListener('paste', (e) => {
  const items = e.clipboardData?.items;
  if (!items) return;
  for (const item of Array.from(items)) {
    if (item.kind !== 'file') continue;
    const file = item.getAsFile();
    if (!file) continue;
    e.preventDefault();
    void storeInInbox(file);
    return;
  }
});

/** Store a dropped or pasted file in the active project's inbox. */
async function storeInInbox(file: File): Promise<void> {
  if (!sidecarBaseUrl) {
    showStatus('Open a workspace first — an inbox belongs to a project.', 'error');
    return;
  }
  try {
    const buf = await file.arrayBuffer();
    // Chunked rather than String.fromCharCode(...bytes): a screenshot is ~1MB
    // and spreading a million arguments overflows the call stack.
    let binary = '';
    const bytes = new Uint8Array(buf);
    for (let i = 0; i < bytes.length; i += 0x8000) {
      binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
    }
    // A pasted screenshot often has no name at all.
    const name = file.name || `pasted.${(file.type.split('/')[1] || 'png')}`;
    const res = (await postJson('/api/inbox/store',
      { name, data: btoa(binary) })) as
        { ok?: boolean; name?: string; error?: string };
    if (res.ok === false) {
      showStatus(`Not stored: ${res.error}`, 'error');
      return;
    }
    showStatus(`Stored in the inbox: ${res.name}`, 'info');
    void renderInboxPanel();
  } catch (err) {
    showStatus(`Not stored: ${String(err)}`, 'error');
  }
}

document.addEventListener('dragover', (e) => {
  // Required to let the browser fire `drop`.
  if (e.dataTransfer?.items && Array.from(e.dataTransfer.items).some((i) => i.kind === 'file')) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
  }
});

document.addEventListener('drop', async (e) => {
  dragEnterDepth = 0;
  dragOverlay.hidden = true;
  if (!e.dataTransfer || e.dataTransfer.files.length === 0) return;
  e.preventDefault();
  const file = e.dataTransfer.files[0];
  // Electron 32 REMOVED `File.path`. This used to read it and return early
  // when it was undefined — so after that upgrade, dropping a note silently
  // stopped navigating and dropping a screenshot did nothing at all, with no
  // error anywhere. `webUtils.getPathForFile` is the replacement and lives in
  // the preload, because it is not exposed to the renderer.
  //
  // And the path is now OPTIONAL: filing into the inbox needs the file's
  // bytes, not its location, so a drag from an app that supplies no path
  // still works. Requiring a path to do something that never needed one is
  // what made this fail closed and silent.
  const absPath = cockpitApi.app.pathForFile(file)
    || (file as File & { path?: string }).path || '';
  if (!absPath) {
    void storeInInbox(file);
    return;
  }
  const result = await cockpitApi.app.resolveDroppedFile(absPath);
  switch (result.action) {
    case 'navigate': {
      if (result.workspaceId && result.workspaceId !== activeId) {
        await openWorkspace(result.workspaceId);
      }
      if (result.rel) void navigateTo(result.rel);
      break;
    }
    case 'offer-add-workspace': {
      showStatus(`That file is in ${result.root} — add it as a workspace? (Use Rescan to discover.)`);
      scheduleHide(4000);
      break;
    }
    case 'ignored':
    default: {
      // Not a note — so it is external material, which is exactly what the
      // inbox is for (FEAT-0045). Refusing it was the old behaviour and it
      // threw away the easiest way to hand the project a screenshot.
      void storeInInbox(file);
      break;
    }
  }
});

// ----------------------------------------------------------------------
// Status footer (FEAT-0009 / TASK-0094 + 0095)
// ----------------------------------------------------------------------

type SidecarStatus = 'idle' | 'spawning' | 'ready' | 'failed' | 'exited';

function setSidecarStatus(state: SidecarStatus, label?: string): void {
  sfSidecar.dataset.state = state;
  const text = label || `sidecar: ${state}`;
  sfSidecar.querySelector('.sf-label')!.textContent = text;
}

function refreshFooterPath(): void {
  sfPath.textContent = currentRel ? currentRel : '';
}

// The footer no longer carries an agent dot (FEAT-0031 / TASK-0148):
// agent state already reads from the rail dots, the agent strip, and
// the attention panel — one surface per scope. The footer keeps only
// sidecar-process health (#sf-sidecar). This shim keeps the former
// call sites cheap no-ops.
function refreshFooterAgent(): void { /* removed — see TASK-0148 */ }

sfPath.addEventListener('click', () => {
  if (!sfPath.textContent) return;
  void copyText(sfPath.textContent, 'Path copied');
  const orig = sfPath.textContent;
  sfPath.textContent = 'copied';
  setTimeout(() => { sfPath.textContent = orig; refreshFooterPath(); }, 800);
});

document.querySelectorAll<HTMLButtonElement>('.sf-theme-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    const v = btn.dataset.theme as ThemePref | undefined;
    if (v === 'system' || v === 'light' || v === 'dark') setThemePref(v);
  });
});
refreshThemeButtons();

cockpitApi.app.onMenuDispatch((ev) => {
  switch (ev.action) {
    case 'navigate': {
      const rel = ev.rel as string | undefined;
      if (rel) void navigateTo(rel);
      break;
    }
    case 'switch-workspace': {
      const id = ev.workspaceId as string | undefined;
      if (id) void openWorkspace(id);
      break;
    }
    case 'agent-dispatch': {
      const id = (ev.id as string | undefined) || '';
      const rel = (ev.rel as string | undefined) || '';
      const verb = (ev.verb as string | undefined) || undefined;
      const wsId = (ev.workspaceId as string | undefined) || undefined;
      const agent = ev.agent === 'codex' ? 'codex' as const
        : ev.agent === 'claude' ? 'claude' as const : undefined;
      if (id || rel) void dispatchToAgent(id, rel, agent, verb, wsId);
      break;
    }
    case 'inbox-triage': {
      const name = (ev.name as string | undefined) || '';
      if (!name) break;
      void (async () => {
        const item = (await fetchInboxItems()).find((i) => i.name === name);
        // Gone between the right-click and the click: triaging a file that is
        // no longer there would send the agent after nothing.
        if (!item) { showStatus(`${name} is no longer in the inbox.`, 'info'); return; }
        await triageInboxItem(item);
      })();
      break;
    }
    case 'inbox-open': {
      const name = (ev.name as string | undefined) || '';
      if (name) void navigateTo(`~inbox/${name}`);
      break;
    }
    case 'inbox-discard': {
      const name = (ev.name as string | undefined) || '';
      if (name) void discardInboxItem(name);
      break;
    }
    case 'agent-set': {
      // Reject an agent the registry does not know, rather than saving it as
      // `claude` (ISS-0032). Coercing here meant a third agent could never be
      // selected: the menu would set it and the preference would come back as
      // Claude, with nothing reporting that the choice had been discarded.
      const agent = resolveDispatchAgent(ev.agent);
      if (agent) saveDispatchAgent(agent);
      showStatus(`Dispatch agent: ${agent}`);
      break;
    }
  }
});

// ----------------------------------------------------------------------
// Quick-switch palette (FEAT-0012 / TASK-0088)
// ----------------------------------------------------------------------

interface QuickItem { id: string; title: string; rel: string; type: string; }

let quickCorpus: QuickItem[] = [];
let quickResults: QuickItem[] = [];
let quickSelectedIndex = 0;
// Verb mode (FEAT-0026 / TASK-0138): "refine TASK-0115" — a leading
// verb token filters to items whose type carries that verb and Enter
// dispatches instead of navigating.
let quickVerb: { key: string; label: string; types: string[] } | null = null;

function parseQuickVerb(query: string): { verb: typeof quickVerb; rest: string } {
  const m = query.match(/^(\S+)\s+(.*)$/);
  if (!m) return { verb: null, rest: query };
  const token = m[1].toLowerCase();
  const types: string[] = [];
  let label = '';
  let key = '';
  for (const [t, verbs] of Object.entries(agentActions)) {
    for (const v of verbs) {
      if (v.key.toLowerCase() === token || v.label.toLowerCase() === token) {
        types.push(t);
        key = v.key;
        label = v.label;
      }
    }
  }
  if (types.length === 0) return { verb: null, rest: query };
  return { verb: { key, label, types }, rest: m[2] };
}

function flattenNavItems(groups: NavGroupData[] | undefined, out: QuickItem[]): void {
  if (!groups) return;
  for (const group of groups) {
    for (const item of group.items || []) {
      const rel = extractRel(item.url) || '';
      if (rel) {
        // Items without an id (Docs-tree entries, references, plain
        // .md files) are still navigable — keep them in the corpus
        // so pasting a rel-path matches.
        out.push({
          id: item.id || rel,
          title: item.title || item.id || rel,
          rel,
          type: item.type || group.key || '',
        });
      }
      if (item.children) flattenNavItems([{ items: item.children }], out);
    }
    // Library mode (and any future grouped mode) nests deeply via
    // subgroups; walk those too so the corpus matches the whole tree.
    if (group.subgroups) flattenNavItems(group.subgroups, out);
  }
}

// Modes whose union covers every note type in a project-os corpus.
//
// This used to be a single `mode=library` fetch, on the reasonable
// assumption that Library was "the broadest one" — it carried a by-type
// group for every canonical type. PHASE-010 removed those groups, which
// would have silently reduced Cmd+P to pins and loose files: still a
// populated palette, so nothing would look broken, and half the corpus
// would simply stop being findable.
//
// That is the same reachability failure REQ-0025 gates the nav against,
// reached through search instead. Enumerating the modes keeps the corpus
// honest and makes the coverage claim checkable rather than incidental.
const QUICK_CORPUS_MODES = [
  // TASK-0368: `features` now carries every task too — `flattenNavItems`
  // descends into `children`, and TASK-0366 put tasks there plus an
  // `unattached-tasks` group for the rest. Listing `tasks` as well would
  // add all 384 a second time.
  'features',   // features + their requirements, plans and tasks
  'issues',     // issues + risks (FEAT-0047)
  'intent',     // designs, decisions, risks, references (TASK-0385: was `design`)
  'library',    // pins + the Docs tree, incl. references and workflows
] as const;

async function buildQuickCorpus(): Promise<void> {
  if (!sidecarBaseUrl) return;
  const out: QuickItem[] = [];
  const results = await Promise.all(QUICK_CORPUS_MODES.map(async (mode) => {
    try {
      const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/nav?mode=${mode}`);
      if (!resp.ok) return null;
      return (await resp.json()) as NavPayload;
    } catch { return null; }
  }));
  if (results.every((r) => r === null)) return;  // keep the previous corpus
  for (const data of results) {
    if (data) flattenNavItems(data.groups, out);
  }
  // Changes and tests have no nav mode — they live on the overview and
  // the review desk. Both are still worth finding by name.
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/review-queue`);
    if (resp.ok) {
      const queue = (await resp.json()) as {
        registers?: { tests?: Array<{ id?: string; title?: string; rel?: string }> };
      };
      for (const t of queue.registers?.tests ?? []) {
        if (t.rel) {
          out.push({
            id: t.id || '', title: t.title || '',
            rel: `/docs/${t.rel}`, type: 'test',
          });
        }
      }
    }
  } catch { /* best-effort */ }
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/changes`);
    if (resp.ok) {
      const changes = (await resp.json()) as ChangesPayload;
      const push = (it: NavItem): void => {
        const rel = extractRel(it.url);
        if (rel) {
          out.push({
            id: String(it.id || ''), title: it.title || '',
            rel, type: 'change',
          });
        }
      };
      const walk = (groups: NavGroupData[]): void => {
        for (const g of groups) {
          for (const it of g.items ?? []) push(it);
          if (g.subgroups) walk(g.subgroups);
        }
      };
      for (const it of changes.recent ?? []) push(it);
      walk(changes.buckets ?? []);
    }
  } catch { /* best-effort */ }
  // Several modes reach the same note (a requirement nests under its
  // feature and may also stand alone); dedupe by rel-path.
  const seen = new Set<string>();
  quickCorpus = out.filter((it) => seen.has(it.rel) ? false : (seen.add(it.rel), true));
}

function fuzzyScore(item: QuickItem, query: string): number {
  if (!query) return 1;
  const q = query.toLowerCase();
  const id = item.id.toLowerCase();
  const title = item.title.toLowerCase();
  const rel = item.rel.toLowerCase();
  if (id === q) return 1000;
  if (id.startsWith(q)) return 500;
  if (id.includes(q)) return 200;
  if (title.startsWith(q)) return 300;
  if (title.includes(q)) return 100;
  if (rel.includes(q)) return 50;
  return 0;
}

function refreshQuickResults(): void {
  const query = quickSwitchInput.value.trim();
  const parsed = parseQuickVerb(query);
  quickVerb = parsed.verb;
  const effectiveQuery = quickVerb ? parsed.rest : query;
  const pool = quickVerb
    ? quickCorpus.filter((it) => quickVerb!.types.includes((it.type || '').toLowerCase()))
    : quickCorpus;
  const scored = pool
    .map((it) => ({ it, score: fuzzyScore(it, effectiveQuery) }))
    .filter((s) => s.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 30);
  quickResults = scored.map((s) => s.it);
  quickSelectedIndex = 0;
  renderQuickResults();
}

function renderQuickResults(): void {
  quickSwitchResults.innerHTML = '';
  if (quickResults.length === 0) {
    const li = document.createElement('li');
    li.className = 'qs-empty';
    li.textContent = quickCorpus.length === 0
      ? '(corpus empty — pick a workspace first)'
      : 'No matches.';
    quickSwitchResults.appendChild(li);
    return;
  }
  quickResults.forEach((item, idx) => {
    const li = document.createElement('li');
    if (idx === quickSelectedIndex) li.classList.add('is-selected');
    if (quickVerb) {
      li.classList.add('is-action');
      const badge = document.createElement('span');
      badge.className = 'qs-action-badge';
      badge.textContent = `▶ ${quickVerb.label}`;
      li.prepend(badge);
    }
    const line1 = document.createElement('div');
    line1.className = 'qs-line-1';
    const idSpan = document.createElement('span');
    idSpan.className = 'qs-id';
    // Display handle only — `data-id` on the `li` keeps the full
    // value, and every lookup goes through that (ISS-0084).
    idSpan.textContent = shortNoteId(item.id);
    idSpan.title = item.id;
    line1.appendChild(idSpan);
    const titleSpan = document.createElement('span');
    titleSpan.className = 'qs-title';
    titleSpan.textContent = item.title;
    line1.appendChild(titleSpan);
    li.appendChild(line1);
    const path = document.createElement('div');
    path.className = 'qs-path';
    path.textContent = item.rel;
    li.appendChild(path);
    li.addEventListener('click', () => { quickSelectedIndex = idx; acceptQuickSwitch(); });
    li.addEventListener('mouseenter', () => {
      // TASK-0105: do NOT re-render the list here — that destroys
      // every <li> and breaks the click event (browsers only fire
      // 'click' when mousedown and mouseup hit the same node).
      // Toggle the highlight class in place instead.
      quickSelectedIndex = idx;
      quickSwitchResults.querySelectorAll<HTMLLIElement>('li').forEach((node, j) => {
        node.classList.toggle('is-selected', j === idx);
      });
    });
    quickSwitchResults.appendChild(li);
  });
}

function openQuickSwitch(): void {
  void buildQuickCorpus().then(() => {
    quickSwitchEl.hidden = false;
    quickSwitchInput.value = '';
    refreshQuickResults();
    quickSwitchInput.focus();
  });
}

function closeQuickSwitch(): void {
  quickSwitchEl.hidden = true;
}

function acceptQuickSwitch(): void {
  const item = quickResults[quickSelectedIndex];
  if (!item) return;
  const verb = quickVerb;
  closeQuickSwitch();
  if (verb && item.id) {
    void dispatchToAgent(item.id, item.rel, undefined, verb.key);
    return;
  }
  void navigateTo(item.rel);
}

quickSwitchInput.addEventListener('input', refreshQuickResults);
quickSwitchInput.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') { e.preventDefault(); closeQuickSwitch(); }
  else if (e.key === 'Enter') { e.preventDefault(); acceptQuickSwitch(); }
  else if (e.key === 'ArrowDown') {
    e.preventDefault();
    if (!quickResults.length) return;
    quickSelectedIndex = (quickSelectedIndex + 1) % quickResults.length;
    renderQuickResults();
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    if (!quickResults.length) return;
    quickSelectedIndex = (quickSelectedIndex - 1 + quickResults.length) % quickResults.length;
    renderQuickResults();
  }
});
quickSwitchEl.addEventListener('click', (e) => {
  if (e.target === quickSwitchEl) closeQuickSwitch();
});
// ----------------------------------------------------------------------
// Quick capture (FEAT-0061 / TASK-0283)
// ----------------------------------------------------------------------
//
// A thought becomes a record without composing a prompt. Deliberately dumber
// than the ad-hoc-intake skill: a title now beats a paragraph never, and an
// agent can be dispatched from the triage row when investigation is worth it.
//
// It lands at `triage` rather than `open` — capture records that something was
// noticed; deciding what it is, is the judgment the triage tray exists for.

function openCapture(opts: { title?: string; body?: string; related?: string[] } = {}): void {
  if (!sidecarBaseUrl) {
    showStatus('Open a workspace first', 'error');
    return;
  }
  if (document.getElementById('capture-overlay')) return;
  // A caller may seed the text and the link — the failing-step draft
  // (TASK-0372) is the first. It seeds rather than files: the box opens with
  // the sentence already written and the cursor in it, because what the
  // stepper knows is which step failed, and what the person knows is why.
  const seedRelated = opts.related?.length
    ? opts.related : (currentNoteId ? [currentNoteId] : []);

  const overlay = document.createElement('div');
  overlay.id = 'capture-overlay';
  overlay.className = 'capture-overlay';
  const box = document.createElement('div');
  box.className = 'capture-box';

  const label = document.createElement('div');
  label.className = 'capture-label';
  label.textContent = seedRelated.length
    ? `Capture an issue · linked to ${seedRelated.join(', ')}`
    : 'Capture an issue';

  const field = document.createElement('input');
  field.type = 'text';
  field.className = 'capture-field';
  field.placeholder = 'what did you notice?';
  if (opts.title) field.value = opts.title;

  const hint = document.createElement('div');
  hint.className = 'capture-hint';
  hint.textContent = 'Enter files it at triage · Esc closes';

  box.append(label, field, hint);
  overlay.appendChild(box);
  document.body.appendChild(overlay);
  field.focus();

  const close = (): void => { overlay.remove(); };
  overlay.addEventListener('click', (ev) => {
    if (ev.target === overlay) close();
  });
  field.addEventListener('keydown', (ev) => {
    ev.stopPropagation();
    if (ev.key === 'Escape') { close(); return; }
    if (ev.key !== 'Enter') return;
    const title = field.value.trim();
    if (!title) { close(); return; }
    field.disabled = true;
    hint.textContent = 'filing…';
    void (async () => {
      try {
        const resp = await fetch(`${sidecarBaseUrl}/api/notes/create`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            type: 'issue',
            title,
            body: opts.body || '',
            related: seedRelated.map((id) => `[[${id}]]`),
            actor: 'user:edwin',
          }),
        });
        const data = (await resp.json()) as
          { ok?: boolean; error?: string; result?: { id?: string } };
        if (!resp.ok || !data.ok) {
          // Never lose the text. A capture that eats a thought on a failed
          // request is worse than no capture — the whole point is that it
          // costs nothing to use.
          field.disabled = false;
          hint.textContent = data.error || `failed: HTTP ${resp.status}`;
          hint.classList.add('is-error');
          field.focus();
          return;
        }
        showStatus(`${data.result?.id ?? 'issue'} captured at triage`);
        close();
        // No reload: the watcher sees the new file and the pane refreshes.
      } catch (err) {
        field.disabled = false;
        hint.textContent = String(err);
        hint.classList.add('is-error');
        field.focus();
      }
    })();
  });
}

document.addEventListener('keydown', (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'n') {
    e.preventDefault();
    openCapture();
  }
});

document.addEventListener('keydown', (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'p') {
    e.preventDefault();
    if (quickSwitchEl.hidden) openQuickSwitch();
    else closeQuickSwitch();
  }
});

// ----------------------------------------------------------------------
// SSE soft-reload + tab-state heartbeat (FEAT-0010 / TASK-0086)
// ----------------------------------------------------------------------

let activeEventSource: EventSource | null = null;
let softReloadTimer: number | null = null;
let heartbeatTimer: number | null = null;
let tabId: string | null = null;

function getTabId(): string {
  if (tabId) return tabId;
  try {
    const stored = localStorage.getItem('cockpit:tab-id');
    if (stored) { tabId = stored; return stored; }
  } catch { /* ignore */ }
  // RFC4122-ish — sufficient for tab identity, not a security primitive.
  const generated = 'desktop-' + Math.random().toString(36).slice(2, 12) +
                    '-' + Date.now().toString(36);
  tabId = generated;
  try { localStorage.setItem('cockpit:tab-id', generated); } catch { /* ignore */ }
  return generated;
}

function attachSidecarEventStream(baseUrl: string): void {
  if (activeEventSource) {
    activeEventSource.close();
    activeEventSource = null;
  }
  // EventSource is the browser-standard SSE consumer. Available in
  // Electron renderers without any extra polyfill.
  const es = new EventSource(`${baseUrl}/_events`);
  es.addEventListener('file-changed', () => {
    scheduleSoftReload();
  });
  // Status transitions (FEAT-0036 / TASK-0162): live-migrate rows in the
  // Active nav mode and flash the changed item.
  es.addEventListener('cockpit:status-change', (e) => {
    try {
      const c = JSON.parse((e as MessageEvent).data) as {
        id?: string; to?: string; from?: string; ts?: string; title?: string; type?: string;
      };
      handleStatusChange(c);
    } catch { /* malformed — ignore */ }
  });
  // Hook-fed activity feed (FEAT-0019/0020): live strip + nav trail.
  es.addEventListener('cockpit:agent-activity', (e) => {
    try {
      handleAgentActivity(JSON.parse((e as MessageEvent).data) as AgentActivity);
    } catch { /* malformed activity event — ignore */ }
  });
  // Instant agent-state for the ACTIVE workspace (the cross-workspace
  // poller still covers the rest of the rail at 5s cadence).
  es.addEventListener('cockpit:agent-state', (e) => {
    try {
      const payload = JSON.parse((e as MessageEvent).data) as AgentStatePayload;
      if (activeId) {
        noteFinish(activeId, agentStates.get(activeId)?.state, payload);
        agentStates.set(activeId, payload);
        const li = listEl.querySelector<HTMLLIElement>(`li[data-id="${activeId}"]`);
        const ws = workspaces.find((w) => w.id === activeId);
        if (li && ws) applyAgentStateToSquare(li, ws);
        refreshFooterAgent();
        refreshAttention();
        void refreshAgentSnapshot();
        scheduleAck();  // seen-timer for the active workspace (TASK-0157)
        if (payload.state) cockpitApi.dispatch.poke(activeId, payload.state);
      }
    } catch { /* ignore */ }
  });
  // CLI `cockpit dispatch` requests (FEAT-0025 / TASK-0136).
  es.addEventListener('cockpit:dispatch-request', (e) => {
    try {
      handleDispatchRequest(JSON.parse((e as MessageEvent).data));
    } catch { /* ignore malformed */ }
  });
  // Docs-validator health for THIS repo (FEAT-0051 / TASK-0252). Fires
  // only when the observable state changes, which is why `primeValidation`
  // runs once on attach — a repo that has been quietly failing since
  // before we connected would otherwise never report.
  es.addEventListener('cockpit:validation', (e) => {
    try {
      applyValidationReport(JSON.parse((e as MessageEvent).data) as ValidationReport);
    } catch { /* malformed frame — keep the last good report */ }
  });
  // `cockpit:focus` stays on the main process's agent-focus bridge.
  es.onerror = () => {
    // EventSource auto-reconnects; nothing to do here. Closing the
    // stream on every transient error would loop.
  };
  activeEventSource = es;
  void primeValidation(baseUrl);
}

function scheduleSoftReload(): void {
  if (softReloadTimer != null) window.clearTimeout(softReloadTimer);
  softReloadTimer = window.setTimeout(() => {
    softReloadTimer = null;
    // Re-fetch nav + right pane + centre. Centre uses {replace: true}
    // so the file-changed reload doesn't pollute history with a copy
    // of the same path.
    if (sidecarBaseUrl) {
      if (currentRel && currentRel.startsWith('~overview')) {
        // Overview refreshes in place — scroll survives, no history
        // churn, and the server-side stats cache makes it cheap
        // (FEAT-0023 / TASK-0130).
        void refreshOverviewInPlace();
        return;
      }
      void loadWsNav();
      if (currentRel && !currentRel.startsWith('~')) {
        void loadRightPane(currentRel);
        void navigateTo(currentRel, { replace: true });
      }
    }
  }, 150);
}

function startTabStateHeartbeat(): void {
  if (heartbeatTimer != null) window.clearInterval(heartbeatTimer);
  // Fire once immediately so the cockpit's state snapshot reflects
  // this tab right away.
  sendTabState();
  heartbeatTimer = window.setInterval(sendTabState, 15_000);
}

async function sendTabState(): Promise<void> {
  if (!sidecarBaseUrl || !currentRel) return;
  if (currentRel.startsWith('~')) return; // virtual pages have no docs URL
  const url = `/docs/${stripFragment(currentRel)}`;
  try {
    await fetch(`${sidecarBaseUrl}/api/cockpit/tab-state`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tab_id: getTabId(),
        url,
        following: isFollowing(activeId),
      }),
    });
  } catch {
    /* heartbeat is best-effort */
  }
}

// ----------------------------------------------------------------------
// Agent instrumentation surfaces (PHASE-007)
//   FEAT-0020: activity strip, needs-input inbox, live nav trail
//   FEAT-0021: task dispatch
//   FEAT-0022: session insight (overview section + CHG provenance)
// ----------------------------------------------------------------------

interface AgentActivity {
  event: string;
  session_id: string;
  agent: string;
  ts: string;
  state?: string;
  prompt?: string;
  tool?: string;
  file?: string;
  rel?: string;
  undocumented?: boolean;
  cost?: AgentCostSnapshot;
}

interface AgentCostSnapshot {
  total_cost_usd?: number;
  total_lines_added?: number;
  total_lines_removed?: number;
  used_percentage?: number;
  rate_limits?: Record<string, { used_percentage: number; resets_at?: string }>;
  captured_at?: string;
}

interface AgentSessionSlim {
  session_id: string;
  agent: string | null;
  started: string | null;
  ended: string | null;
  live: boolean;
  prompt_count: number;
  last_prompt: string | null;
  files: string[];
  docs_notes: string[];
  work_notes?: string[];
  // Index-enriched work items for the current session (TASK-0191).
  work_items?: WorkItem[];
  cost: AgentCostSnapshot | null;
  chg_ids: string[];
  undocumented: boolean;
  transcript_path?: string | null;
  prompts?: { ts: string; text: string }[];
}

const agentStrip = $<HTMLDivElement>('#agent-strip');
const agentStripDot = $<HTMLSpanElement>('#agent-strip-dot');
const agentStripAgent = $<HTMLSpanElement>('#agent-strip-agent');
const agentStripText = $<HTMLSpanElement>('#agent-strip-text');
const agentStripUndoc = $<HTMLSpanElement>('#agent-strip-undoc');
const agentStripCtx = $<HTMLSpanElement>('#agent-strip-ctx');
const agentStripWeight = $<HTMLSpanElement>('#agent-strip-weight');
const agentStripCache = $<HTMLSpanElement>('#agent-strip-cache');
const agentStripCost = $<HTMLSpanElement>('#agent-strip-cost');
const agentStripExpand = $<HTMLButtonElement>('#agent-strip-expand');
const agentStripDetail = $<HTMLDivElement>('#agent-strip-detail');
const agentStripInflight = $<HTMLSpanElement>('#agent-strip-inflight');
const attentionPanel = $<HTMLDivElement>('#ws-attention');

let stripSession: AgentSessionSlim | null = null;
let stripLastPrompt = '';

// ----- Activity strip (TASK-0118) -------------------------------------

function agentStateLabel(state: string | undefined): string {
  switch (state) {
    case 'busy': return 'working';
    case 'needs-input': return 'needs you';
    case 'waiting': return 'waiting for you';
    case 'idle': return 'idle';
    case 'done': return 'done';
    case 'error': return 'error';
    default: return state || '';
  }
}

// Prompt-cache standing for the shown session (FEAT-0081 / TASK-0344).
// Served on the agent snapshot, read from the transcript by the sidecar.
interface AgentCacheState {
  prefix_tokens: number;
  last_turn_at: string;
  age_seconds: number;
  ttl_seconds: number;
  model?: string | null;
  state: 'warm' | 'cooling' | 'cold';
  resume_cost_usd: number;
  warm_cost_usd: number;
  cooling_minutes_left?: number;
  model_switch?: {
    from: string; to: string; discarded_tokens: number; cost_usd: number;
  };
}



// Declared by cache-temperature.js. The judgment lives there so the node
// suite can reach it (ISS-0110); this is the adapter that paints it.
declare function cacheBadge(cache: AgentCacheState | null | undefined): {
  weight: string; label: string; title: string; tone: string; switch: boolean;
} | null;

function renderAgentStripCache(cache: AgentCacheState | null | undefined): void {
  const badge = cacheBadge(cache);
  if (!badge) {
    agentStripWeight.hidden = true;
    agentStripCache.hidden = true;
    return;
  }
  agentStripWeight.textContent = badge.weight;
  agentStripWeight.hidden = false;
  agentStripCache.textContent = badge.label;
  agentStripCache.title = badge.title;
  agentStripCache.dataset.cache = badge.tone;
  agentStripCache.toggleAttribute('data-switch', badge.switch);
  agentStripCache.hidden = false;
}

function renderAgentStripCost(cost: AgentCostSnapshot | null | undefined): void {
  if (cost && typeof cost.used_percentage === 'number') {
    agentStripCtx.textContent = `ctx ${Math.round(cost.used_percentage)}%`;
    agentStripCtx.hidden = false;
    agentStripCtx.classList.toggle('meter-hot', cost.used_percentage >= 80);
  } else {
    agentStripCtx.hidden = true;
  }
  // Rate-limit budgets moved out of the session strip to the account
  // budget block in the left pane (FEAT-0035/TASK-0160) — the strip is
  // session-scoped only. Capture the freshest sample for that block.
  if (cost?.rate_limits) noteRateLimits(cost.rate_limits, cost.captured_at);
  if (cost && typeof cost.total_cost_usd === 'number') {
    agentStripCost.textContent = `$${cost.total_cost_usd.toFixed(2)}`;
    agentStripCost.hidden = false;
  } else {
    agentStripCost.hidden = true;
  }
}

function showAgentStrip(activity: AgentActivity | null, session: AgentSessionSlim | null): void {
  stripSession = session;
  // `session` may be live (session.live) or the most-recent ended one
  // (the snapshot's last_session fallback) so the files view persists
  // between runs. Only truly hide when there's no session to show and
  // nothing queued.
  if (!session) {
    // Keep the strip up while dispatches are queued — the chip is the
    // only visible handle on the queue (FEAT-0024 / TASK-0133).
    agentStrip.hidden = activeQueueItems.length === 0;
    agentStripDetail.hidden = true;
    agentStripExpand.setAttribute('aria-expanded', 'false');
    renderAgentStripCache(null);
    renderInflightBoxes();  // hides the boxes when there is no session
    return;
  }
  const live = session.live;
  agentStrip.hidden = false;
  agentStrip.classList.toggle('is-ended', !live);
  const state = live
    ? (activity?.state || agentStates.get(activeId || '')?.state || 'busy')
    : 'idle';
  agentStripDot.dataset.state = state;
  // Prefer the live hook agent over a stale last_session agent so the
  // strip and rail dot never disagree (ISS-0012) — a one-off codex run
  // must not relabel a live claude workspace.
  agentStripAgent.textContent =
    activity?.agent || agentStates.get(activeId || '')?.agent || session.agent || 'agent';
  if (live && activity?.prompt) stripLastPrompt = activity.prompt;
  else if (session.last_prompt) stripLastPrompt = session.last_prompt;
  let detail = '';
  if (live && activity?.tool && activity?.file) {
    const short = (activity.rel || activity.file).split('/').pop() || activity.file;
    detail = `${activity.tool} · ${short}`;
  } else if (live && activity?.tool) {
    detail = activity.tool;
  }
  const label = live ? agentStateLabel(state) : 'last session';
  agentStripText.textContent = detail
    ? `${label} — ${detail}`
    : stripLastPrompt
      ? `${label} — ${stripLastPrompt}`
      : label;
  agentStripText.title = stripLastPrompt;
  agentStripUndoc.hidden = !((live && activity?.undocumented) || session.undocumented);
  renderAgentStripCost(session.cost || (live ? activity?.cost : undefined));
  renderAgentStripCache(lastAgentSnap?.cache);
  renderInflightBoxes();  // inline in-flight boxes before ctx (FEAT-0038)
}

// Session progress views (FEAT-0036 / FEAT-0038): the block notation per
// docs item worked, filling live as the agent completes them.
// Terminal statuses for the session progress views. Kept in step with
// COMPLETED_STATUSES above; `implemented` is terminal since ADR-0007.
const DONE_STATUSES = new Set(['done', 'merged', 'fixed', 'fulfilled', 'met', 'complete', 'implemented', 'verified', 'closed', 'passing', 'published', 'released', 'resolved']);

// Index-enriched work item served by the sidecar (TASK-0191).
interface WorkItem {
  id: string; rel: string; title: string; status: string; type: string;
  done: boolean; ts?: string | null; current_prompt: boolean;
}
// A status transition seen this session — the cockpit:status-change payload,
// keyed by note id. Overlays instant fill/transition text onto work_items.
interface WorkTransition { from?: string; to: string; ts?: string; title?: string; }
const workTransitions = new Map<string, WorkTransition>();
let stripDetailTab: 'work' | 'files' = 'work';

// Note type from an id prefix — fallback when a work_item lacks a type.
function typeForId(id: string): string {
  const prefix = id.split('-')[0];
  return ({
    TASK: 'task', ISS: 'issue', FEAT: 'feature', REQ: 'requirement',
    RISK: 'risk', TST: 'test', ADR: 'adr', CHG: 'change', PHASE: 'plan',
  } as Record<string, string>)[prefix] ?? 'task';
}

// Compact relative time ("now", "4m", "2h", "3d") from an ISO string.
function relTime(iso: string | null | undefined): string {
  if (!iso) return '';
  const t = Date.parse(iso);
  if (Number.isNaN(t)) return '';
  const s = Math.max(0, (Date.now() - t) / 1000);
  if (s < 45) return 'now';
  if (s < 3600) return `${Math.round(s / 60)}m`;
  if (s < 86400) return `${Math.round(s / 3600)}h`;
  return `${Math.round(s / 86400)}d`;
}

function navToWorkItem(it: WorkItem): void {
  if (it.rel) void navigateTo(it.rel);
}

// The session's enriched work items, or [] when the sidecar predates them.
function sessionWorkItems(): WorkItem[] {
  return stripSession?.work_items ?? [];
}

// Done state: the server's per-type `done`, plus an instant overlay from a
// status-change we may have seen before the next snapshot lands.
function itemDone(it: WorkItem): boolean {
  if (it.done) return true;
  const to = workTransitions.get(it.id)?.to?.toLowerCase();
  return !!to && DONE_STATUSES.has(to);
}

// The item being worked on right now: the newest-touched, not-yet-done item
// in the current prompt while the session is live (pulsed).
function activeWorkItemId(items: WorkItem[]): string | null {
  if (!stripSession?.live) return null;
  let best: WorkItem | null = null;
  for (const it of items) {
    if (!it.current_prompt || itemDone(it) || !it.ts) continue;
    if (!best || (best.ts && it.ts > best.ts)) best = it;
  }
  return best?.id ?? null;
}

// In-flight boxes: the CURRENT prompt's work items, inline before ctx,
// filling as they complete (TASK-0192, replaces the second rail).
function renderInflightBoxes(): void {
  const items = stripSession && !agentStrip.hidden
    ? sessionWorkItems().filter((it) => it.current_prompt) : [];
  if (items.length === 0) {
    agentStripInflight.hidden = true; agentStripInflight.replaceChildren(); return;
  }
  agentStripInflight.replaceChildren();
  const activeId = activeWorkItemId(items);
  const CAP = 12;
  for (const it of items.slice(0, CAP)) {
    const sq = document.createElement('span');
    sq.className = 'ov-phase-sq';
    sq.dataset.type = it.type || typeForId(it.id);
    if (itemDone(it)) sq.dataset.bucket = 'done';
    else if (it.id === activeId) sq.classList.add('is-active');
    sq.title = `${it.id}${it.title ? ` ${it.title}` : ''}${it.status ? ` (${it.status})` : ''}`;
    sq.addEventListener('click', () => navToWorkItem(it));
    agentStripInflight.appendChild(sq);
  }
  if (items.length > CAP) {
    const more = document.createElement('span');
    more.className = 'prog-more';
    more.textContent = `+${items.length - CAP}`;
    agentStripInflight.appendChild(more);
  }
  agentStripInflight.hidden = false;
}

function noteWorkTransition(c: { id?: string; to?: string; from?: string; ts?: string; title?: string; type?: string }): void {
  if (c.id && typeof c.to === 'string') {
    const prev = workTransitions.get(c.id);
    workTransitions.set(c.id, {
      from: prev?.from ?? c.from,  // earliest from across moves this session
      to: c.to,
      ts: c.ts,
      title: c.title ?? prev?.title,
    });
  }
  renderInflightBoxes();
  if (!agentStripDetail.hidden && stripDetailTab === 'work') renderAgentStripDetail();
}

// ---- validator errors for the ACTIVE repo (FEAT-0051 / TASK-0252) ----
//
// FEAT-0018 built `GET /api/cockpit/validation` and the
// `cockpit:validation` SSE event, and the renderer has held an
// EventSource on the sidecar since FEAT-0036 — it simply never
// subscribed to this one. That is why the desktop shell has had no way
// to see its own repo's violations while the browser client has had a
// drift panel for weeks.
//
// The FLEET map (FEAT-0028) stays counts-only on purpose: that is ten
// repos over an IPC boundary. This is one repo, live, on a connection
// that is already open, so it carries the whole report.

/** The active workspace's validator report, or null when unknown. */
let activeValidation: ValidationReport | null = null;

function currentValidationErrors(): ValidationEntry[] {
  return activeValidation?.errors ?? [];
}

function applyValidationReport(report: ValidationReport | null): void {
  activeValidation = report;
  noteValidationChange(report, Date.now());
  if (!agentStripDetail.hidden) renderAgentStripDetail();
}

/** Drop everything on a workspace switch or a dead sidecar.
 *
 *  Not "keep the last report": it belongs to a repo that is no longer
 *  on screen, and showing one repo's violations under another's session
 *  is the mistake FEAT-0028's identity check exists to prevent, one
 *  scope down. */
function clearValidation(): void {
  activeValidation = null;
  resetValidationRows();
  if (!agentStripDetail.hidden) renderAgentStripDetail();
}

async function primeValidation(baseUrl: string): Promise<void> {
  try {
    const resp = await fetch(`${baseUrl}/api/cockpit/validation`);
    if (!resp.ok) return;
    applyValidationReport((await resp.json()) as ValidationReport);
  } catch { /* best-effort; the SSE event will bring the next one */ }
}

/** The validator-error block in the session summary (TASK-0253).
 *
 *  One row per error, in the same grammar as the work rows below it —
 *  a square that fills when the thing completes. The eye should not
 *  have to learn a second pattern six inches from the first.
 *
 *  It carries code, message and a destination; it does NOT restate the
 *  rail badge's count. The badge answers *which project*, this answers
 *  *what* — and a surface that re-listed what another already drew is
 *  exactly what ISS-0068 deleted.
 */
function buildValidationBlock(rows: ValidationRow[]): HTMLElement {
  const wrap = document.createElement('div');
  wrap.className = 'agent-detail-validation';

  const head = document.createElement('div');
  head.className = 'agent-detail-validation-head';
  const openCount = rows.filter((r) => !r.done).length;
  head.textContent = openCount === 0
    ? 'Docs checks — all cleared'
    : `Docs checks — ${openCount} to fix`;
  wrap.appendChild(head);

  for (const { entry, done } of rows) {
    const row = document.createElement('button');
    row.type = 'button';
    row.className = 'agent-detail-work-row agent-detail-validation-row'
      + (done ? ' is-done' : '');

    const sq = document.createElement('span');
    sq.className = 'ov-phase-sq';
    sq.dataset.type = 'issue';
    if (done) sq.dataset.bucket = 'done';

    const code = document.createElement('span');
    code.className = 'work-id mono';
    code.textContent = entry.code;

    const label = document.createElement('span');
    label.className = 'work-title';
    label.textContent = validationLabel(entry);

    row.append(sq, code, label);

    // The subject: the note the error is about, when it names one.
    const subject = entry.id || (entry.rel ? entry.rel.split('/').pop() : '');
    if (subject) {
      const subj = document.createElement('span');
      subj.className = 'work-status';
      subj.textContent = subject;
      row.appendChild(subj);
    }

    const state = document.createElement('span');
    state.className = 'work-time';
    state.textContent = done ? 'fixed' : 'open';
    row.appendChild(state);

    // Full message on hover — the label is a summary, and a summary
    // that cannot be expanded is where "what is this related to" came
    // from in the first place.
    row.title = entry.message;

    const target = entry.url || (entry.rel && entry.rel.startsWith('docs/') ? `/${entry.rel}` : '');
    if (target) {
      row.addEventListener('click', () => { void navigateTo(target); });
    } else {
      // Snapshot-level errors name no note. Say so rather than offering
      // a click that goes nowhere — ISS-0037 was exactly that.
      row.disabled = true;
      row.title = `${entry.message}\n\n(no single note to open — this is about SNAPSHOT.yaml)`;
    }
    wrap.appendChild(row);
  }
  return wrap;
}

function renderAgentStripDetail(): void {
  if (!stripSession) { agentStripDetail.hidden = true; return; }
  agentStripDetail.replaceChildren();
  const head = document.createElement('div');
  head.className = 'agent-detail-head';
  head.textContent = `session ${stripSession.session_id.slice(0, 8)} · ${stripSession.prompt_count} prompt${stripSession.prompt_count === 1 ? '' : 's'}`;
  agentStripDetail.appendChild(head);

  // Validator errors, above the tabs and above the work rows
  // (FEAT-0051 / TASK-0253). Deliberately outside the tab bar: this is
  // not a third view of the session, it is a condition of the repo that
  // the session is currently causing or clearing, and burying it behind
  // a tab would reproduce the problem it exists to fix — a signal you
  // have to go looking for.
  const errRows = validationRows(currentValidationErrors(), Date.now());
  if (errRows.length > 0) agentStripDetail.appendChild(buildValidationBlock(errRows));

  const items = sessionWorkItems();
  // Tab bar: progress | files (TASK-0190 renamed 'work' → 'progress').
  const tabs = document.createElement('div');
  tabs.className = 'agent-detail-tabs';
  for (const [key, label] of [['work', 'progress'], ['files', 'files']] as const) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'agent-detail-tab' + (stripDetailTab === key ? ' on' : '');
    b.textContent = label;
    b.addEventListener('click', () => { stripDetailTab = key; renderAgentStripDetail(); });
    tabs.appendChild(b);
  }
  agentStripDetail.appendChild(tabs);

  if (stripDetailTab === 'work') {
    const list = document.createElement('div');
    list.className = 'agent-detail-work';
    if (items.length === 0) {
      const e = document.createElement('div');
      e.className = 'agent-detail-empty';
      e.textContent = 'No documented work yet — items appear as this session touches notes.';
      list.appendChild(e);
    }
    // Rich rows from the enriched work_items (TASK-0192): current-prompt
    // items first, then the rest by most-recent touch; the active item
    // pinned to the very top.
    const activeId = activeWorkItemId(items);
    const rank = (it: WorkItem): number => {
      if (it.id === activeId) return Number.POSITIVE_INFINITY;
      const parsed = it.ts ? Date.parse(it.ts) : 0;
      const base = Number.isNaN(parsed) ? 0 : parsed;
      return it.current_prompt ? base + 1e13 : base;  // current prompt sorts above the rest
    };
    const ordered = [...items].sort((a, b) => rank(b) - rank(a));
    for (const it of ordered) {
      const done = itemDone(it);
      const isActive = it.id === activeId;
      const row = document.createElement('button');
      row.type = 'button';
      row.className = 'agent-detail-work-row' + (isActive ? ' is-active' : '');
      const sq = document.createElement('span');
      sq.className = 'ov-phase-sq';
      sq.dataset.type = it.type || typeForId(it.id);
      if (done) sq.dataset.bucket = 'done';
      const idEl = document.createElement('span');
      idEl.className = 'work-id mono';
      idEl.textContent = shortNoteId(it.id);
      idEl.title = it.id;
      row.append(sq, idEl);
      if (it.title) {
        const titleEl = document.createElement('span');
        titleEl.className = 'work-title';
        titleEl.textContent = it.title;
        row.appendChild(titleEl);
      }
      // Status: the observed from→to transition when we saw one, else the
      // note's current status. Active items get a "· working" marker.
      const t = workTransitions.get(it.id);
      const statusEl = document.createElement('span');
      statusEl.className = 'work-status';
      if (t?.from && t.from !== t.to) statusEl.textContent = `${t.from} → ${t.to}`;
      else statusEl.textContent = it.status || t?.to || '';
      if (isActive) statusEl.textContent += ' · working';
      row.appendChild(statusEl);
      const time = document.createElement('span');
      time.className = 'work-time';
      time.textContent = relTime(it.ts ?? t?.ts);
      row.appendChild(time);
      row.addEventListener('click', () => navToWorkItem(it));
      list.appendChild(row);
    }
    agentStripDetail.appendChild(list);
  } else {
    const list = document.createElement('ul');
    list.className = 'agent-detail-files';
    const files = stripSession.files.slice(-20).reverse();
    if (files.length === 0) {
      const li = document.createElement('li');
      li.className = 'agent-detail-empty';
      li.textContent = 'No files touched yet — paths appear as this session edits them.';
      list.appendChild(li);
    }
    for (const f of files) {
      const li = document.createElement('li');
      const isDocs = !f.startsWith('/');
      if (isDocs) {
        const a = document.createElement('a');
        a.href = '#';
        a.textContent = f;
        a.addEventListener('click', (e) => { e.preventDefault(); void navigateTo(f); });
        li.appendChild(a);
      } else {
        li.textContent = f;
      }
      list.appendChild(li);
    }
    agentStripDetail.appendChild(list);
  }
  agentStripDetail.hidden = false;
}

// One shared fetch per hook-event burst feeds every agent surface —
// strip, Now card, sessions feed (TASK-0130 fix: was three fetches).
interface AgentSnap {
  activity?: AgentActivity | null;
  session?: AgentSessionSlim | null;
  last_session?: AgentSessionSlim | null;
  agent_state?: { state?: string } | null;
  // Freshest account-global usage across all sessions (TASK-0171).
  rate_limits?: Record<string, { used_percentage: number; resets_at?: string }>;
  rate_limits_at?: string;
  // Prompt-cache standing of the shown session (FEAT-0081 / TASK-0344).
  cache?: AgentCacheState | null;
}
let lastAgentSnap: AgentSnap | null = null;
let agentSnapTimer: number | null = null;

async function refreshAgentSnapshot(): Promise<void> {
  if (!sidecarBaseUrl) return;
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/state`);
    if (!resp.ok) return;
    lastAgentSnap = await resp.json() as AgentSnap;
    // Account-global usage: adopt the freshest reading across all of
    // this workspace's sessions (TASK-0171), through the adopt-if-newer
    // gate — so the real reading isn't masked by a later session that
    // lacked one.
    if (lastAgentSnap.rate_limits && lastAgentSnap.rate_limits_at) {
      noteRateLimits(lastAgentSnap.rate_limits, lastAgentSnap.rate_limits_at);
    }
    refreshSessionTouched();
    // Fall back to the most-recent (ended) session so the strip — and
    // its files view — persists between runs instead of vanishing.
    showAgentStrip(
      lastAgentSnap.activity ?? null,
      lastAgentSnap.session ?? lastAgentSnap.last_session ?? null,
    );
    if (!agentStripDetail.hidden) renderAgentStripDetail();
  } catch { /* agent surfaces are best-effort */ }
}

function scheduleAgentSnapshotRefresh(): void {
  if (agentSnapTimer != null) window.clearTimeout(agentSnapTimer);
  agentSnapTimer = window.setTimeout(() => {
    agentSnapTimer = null;
    void refreshAgentSnapshot();
  }, 300);
}

function handleAgentActivity(activity: AgentActivity): void {
  scheduleAgentSnapshotRefresh();
  if (activity.rel) flashAgentTouch(activity.rel);
}

// ----- Live nav trail (TASK-0120) --------------------------------------

const AGENT_TOUCH_DECAY_MS = 8_000;

function flashAgentTouch(rel: string): void {
  const roots: ParentNode[] = [wsNavContent, rightPaneContent];
  for (const root of roots) {
    root.querySelectorAll<HTMLElement>('li[data-rel]').forEach((li) => {
      if (li.dataset.rel !== rel) return;
      li.classList.add('agent-touched');
      const existing = li.querySelector('.agent-touched-chip');
      if (!existing) {
        const chip = document.createElement('span');
        chip.className = 'agent-touched-chip';
        chip.textContent = 'agent';
        li.appendChild(chip);
      }
      window.setTimeout(() => {
        li.classList.remove('agent-touched');
        li.querySelector('.agent-touched-chip')?.remove();
      }, AGENT_TOUCH_DECAY_MS);
    });
  }
}

// ----- Agent attention panel (FEAT-0030 / TASK-0147) -------------------
// Docked at the bottom of the nav pane. Answers "what needs me?" across
// all workspaces: needs-input (act now) then waiting (turn finished,
// review) rows, plus a one-line finished-today tally. Replaces the old
// top-bar bell + popover. Zero-height (hidden) when there's nothing.

interface AttentionEntry {
  workspaceId: string;
  name: string;
  /** `record` is TASK-0313's widening: DES-0008's complaint was that these
   *  cards "know only about waiting terminals", so a workspace whose RECORD
   *  owes something now earns a card too, agent or no agent. */
  kind: 'needs-input' | 'waiting' | 'record';
  message: string;
  ts: string;
  cost?: number;   // only known for the active workspace (live session)
  /** The since-line: `since Thu · 14 transitions · 2 need you`. Present when
   *  that workspace's sidecar has answered; absent, never zero. */
  since?: string;
}

// ----- Since you looked (FEAT-0071 / TASK-0313) ------------------------
//
// One digest per workspace, from that workspace's own sidecar. Polled on
// arrival rather than pushed — DES-0008's Out of Scope is explicit that
// nothing here notifies, and presence is not attention: only `Caught up`
// moves the watermark.

const sidecarUrls = new Map<string, string>();

interface DigestSummary {
  transitions: number;
  needsYou: number;
  seenAt: string;
  computedAt: string;
}

const digests = new Map<string, DigestSummary>();
let digestFetchAt = 0;
const DIGEST_MIN_INTERVAL_MS = 30_000;

async function refreshDigests(force = false): Promise<void> {
  const now = Date.now();
  if (!force && now - digestFetchAt < DIGEST_MIN_INTERVAL_MS) return;
  digestFetchAt = now;
  await Promise.all(Array.from(sidecarUrls.entries()).map(async ([wsId, url]) => {
    try {
      const resp = await fetch(`${url}/api/cockpit/digest`);
      if (!resp.ok) return;
      const d = (await resp.json()) as {
        available?: boolean; transition_count?: number; needs_you_count?: number;
        seen_at?: string; computed_at?: string;
      };
      digests.set(wsId, {
        transitions: d.transition_count ?? 0,
        needsYou: d.needs_you_count ?? 0,
        seenAt: d.seen_at ?? '',
        computedAt: d.computed_at ?? '',
      });
    } catch { /* a sidecar that is down simply has no line */ }
  }));
}

/** `since Thu · 14 transitions · 2 need you`, or nothing at all.
 *
 *  **Absent rather than zero.** A permanent `0 transitions · 0 need you` under
 *  every workspace is the shape of thing a reader learns to stop seeing, and
 *  this surface has been taught that twice.
 *
 *  An unset watermark reads `since first run` rather than `since 1 Jan 1970` —
 *  the epoch is the payload's way of saying "show everything", not a date
 *  anybody wants to read. */
function sinceLine(d: DigestSummary | undefined): string {
  if (!d || (d.transitions === 0 && d.needsYou === 0)) return '';
  const bits: string[] = [];
  const seen = d.seenAt && !d.seenAt.startsWith('1970') ? d.seenAt.slice(0, 10) : '';
  bits.push(seen ? `since ${relativeTime(seen)}` : 'since first run');
  if (d.transitions > 0) {
    bits.push(`${d.transitions} transition${d.transitions === 1 ? '' : 's'}`);
  }
  if (d.needsYou > 0) bits.push(`${d.needsYou} need you`);
  return bits.join(' · ');
}

// Per-alert dismissal, keyed by (workspace, state-ts): a new state
// transition mints a fresh ts, so a dismissed alert reappears only when
// something genuinely new happens. Persisted, pruned after 24h.
const ATTENTION_DISMISS_KEY = 'cockpit.attention.dismissed';
let dismissedAlerts: Record<string, number> = loadDismissedAlerts();

function loadDismissedAlerts(): Record<string, number> {
  try {
    const raw = localStorage.getItem(ATTENTION_DISMISS_KEY);
    const obj = raw ? JSON.parse(raw) : {};
    const cutoff = Date.now() - 24 * 3600_000;
    const pruned: Record<string, number> = {};
    for (const [k, v] of Object.entries(obj)) {
      if (typeof v === 'number' && v > cutoff) pruned[k] = v;
    }
    return pruned;
  } catch { return {}; }
}

function alertKey(wsId: string, ts: string): string { return `${wsId}::${ts}`; }
function isAlertDismissed(wsId: string, ts: string): boolean {
  return alertKey(wsId, ts) in dismissedAlerts;
}
function dismissAlert(wsId: string, ts: string): void {
  dismissedAlerts[alertKey(wsId, ts)] = Date.now();
  try { localStorage.setItem(ATTENTION_DISMISS_KEY, JSON.stringify(dismissedAlerts)); }
  catch { /* storage full/unavailable — dismissal is best-effort */ }
  refreshAttention();
}

// Ephemeral "finished today" tally (interim until the ~agents fleet log,
// FEAT-0032): counts observed SessionEnd transitions (a real idle, not a
// decay timeout). Resets across a day boundary; rebuilt live, not
// persisted.
const finishedToday: number[] = []; // finish timestamps (ms)

function noteFinish(wsId: string, prev: string | undefined, next: AgentStatePayload | null): void {
  const wasActive = prev === 'busy' || prev === 'waiting' || prev === 'needs-input';
  const nowIdle = next?.state === 'idle' && !next.decayed_from;
  if (wasActive && nowIdle) finishedToday.push(Date.now());
}

function finishedTodayCount(): number {
  const start = new Date(); start.setHours(0, 0, 0, 0);
  const cutoff = start.getTime();
  while (finishedToday.length && finishedToday[0] < cutoff) finishedToday.shift();
  return finishedToday.length;
}

function attentionEntries(): AttentionEntry[] {
  const out: AttentionEntry[] = [];
  const activeCost = lastAgentSnap?.session?.cost?.total_cost_usd;
  // Membership is attentionIds' answer (ISS-0110): blocked on you AND
  // still cheap to pick up. A cold entry leaves; its obligation lives on
  // the grey square instead (ISS-0105, scope note).
  const eligible = new Set(attentionIds(agentStates, Date.now()));
  for (const [wsId, state] of agentStates) {
    if (!eligible.has(wsId)) continue;
    if (isAlertDismissed(wsId, state.ts || '')) continue;
    // `attentionIds` already guarantees this; repeated only to narrow the
    // type, since the policy now lives in a plain-script module TypeScript
    // cannot see through. A cast would hide a real mismatch here.
    const kind = state.state;
    if (kind !== 'needs-input' && kind !== 'waiting') continue;
    const ws = workspaces.find((w) => w.id === wsId);
    out.push({
      workspaceId: wsId,
      name: ws ? effectiveName(ws) : wsId,
      kind,
      message: state.message
        || (state.state === 'needs-input' ? 'needs your input' : 'turn finished — review'),
      ts: state.ts || '',
      cost: wsId === activeId && typeof activeCost === 'number' ? activeCost : undefined,
    });
  }
  // The since-line rides on the card that already exists (TASK-0313). A
  // second row for the same workspace would be one thing as two rows on one
  // screen — the failure ISS-0068 names — so an agent-waiting workspace gets
  // its record line appended, not a card of its own.
  const carded = new Set(out.map((e) => e.workspaceId));
  for (const e of out) e.since = sinceLine(digests.get(e.workspaceId));

  // And a workspace whose RECORD owes something earns a card even with no
  // agent anywhere near it. That is the whole of DES-0008's complaint: these
  // cards knew only about waiting terminals, so a repo with eleven things
  // needing a human and a quiet terminal looked exactly like a repo with
  // nothing to do.
  for (const [wsId, d] of digests) {
    if (carded.has(wsId) || d.needsYou === 0) continue;
    if (isAlertDismissed(wsId, d.computedAt)) continue;
    const ws = workspaces.find((w) => w.id === wsId);
    out.push({
      workspaceId: wsId,
      name: ws ? effectiveName(ws) : wsId,
      kind: 'record',
      message: `${d.needsYou} item${d.needsYou === 1 ? '' : 's'} need a person`,
      ts: d.computedAt,
      since: sinceLine(d),
    });
  }

  // needs-input above waiting above record: act now, then review, then read.
  // A record card is never urgent — nothing in it arrived while you watched.
  const rank = (k: string) => (k === 'needs-input' ? 0 : k === 'waiting' ? 1 : 2);
  out.sort((a, b) => rank(a.kind) - rank(b.kind) || (a.ts < b.ts ? 1 : -1));
  return out;
}

function buildAttentionRow(entry: AttentionEntry): HTMLElement {
  const row = document.createElement('div');
  row.className = `ws-attention-row kind-${entry.kind}`;
  // Read back by tickTemperatures to compare wanted rows against shown
  // rows — the panel's own DOM is the truth, not a cached decision.
  row.dataset.wsId = entry.workspaceId;
  if (isAlertAcked(entry.workspaceId, entry.ts)) row.classList.add('acked');
  const main = document.createElement('button');
  main.type = 'button';
  main.className = 'ws-attention-main';
  main.title = entry.kind === 'needs-input' ? 'Respond' : 'Review';
  const dot = document.createElement('span');
  dot.className = 'ws-attention-dot';
  const body = document.createElement('span');
  body.className = 'ws-attention-body';
  const name = document.createElement('span');
  name.className = 'ws-attention-name';
  name.textContent = entry.name;
  const msg = document.createElement('span');
  msg.className = 'ws-attention-msg';
  msg.textContent = entry.message;
  const metaBits = [fmtDuration(entry.ts || null, null)];
  if (typeof entry.cost === 'number') metaBits.push(`$${entry.cost.toFixed(2)}`);
  const meta = document.createElement('span');
  meta.className = 'ws-attention-meta';
  meta.textContent = metaBits.filter(Boolean).join(' · ');
  body.append(name, msg, meta);
  if (entry.since) {
    const since = document.createElement('span');
    since.className = 'ws-attention-since';
    since.textContent = entry.since;
    body.appendChild(since);
  }
  main.append(dot, body);
  main.addEventListener('click', () => {
    void (async () => {
      if (activeId !== entry.workspaceId) await openWorkspace(entry.workspaceId);
      // A record card opens the overview, where the digest band is; an agent
      // card opens the terminal, where the agent is. Sending both to the
      // terminal is what made these cards "know only about waiting
      // terminals" in the first place.
      if (entry.kind === 'record') void navigateTo('~overview');
      else showTerminal();
    })();
  });
  const dismiss = document.createElement('button');
  dismiss.type = 'button';
  dismiss.className = 'ws-attention-dismiss';
  dismiss.textContent = '✕';
  dismiss.title = 'Dismiss';
  dismiss.setAttribute('aria-label', `Dismiss ${entry.name}`);
  dismiss.addEventListener('click', (e) => {
    e.stopPropagation();
    dismissAlert(entry.workspaceId, entry.ts);
  });
  row.append(main, dismiss);
  return row;
}

// ----- Account budget block (FEAT-0035 / TASK-0160) --------------------
// The 5h/7d rate limits are account-scoped, so they live at the foot of
// the attention panel (left pane), not in the session strip. The
// freshest sample from any live session is authoritative.
interface RateWindow { used_percentage: number; resets_at?: string }
let latestRateLimits: Record<string, RateWindow> | null = null;
// Epoch ms of the currently-displayed reading. Rate limits are
// account-global, so we keep the FRESHEST reading from any source /
// workspace and never downgrade — switching projects can't change the
// number (TASK-0169).
let rateLimitsAsOf = 0;

// Persist the freshest account-global reading so the Usage block is
// visible immediately on launch and across workspace switches — it's an
// account fact, not a per-session one (TASK-0170).
const USAGE_KEY = 'cockpit:usage';
function persistUsage(): void {
  try {
    if (latestRateLimits) {
      localStorage.setItem(USAGE_KEY, JSON.stringify({ rl: latestRateLimits, at: rateLimitsAsOf }));
    }
  } catch { /* storage unavailable — in-memory only */ }
}
function loadPersistedUsage(): void {
  try {
    const raw = localStorage.getItem(USAGE_KEY);
    if (!raw) return;
    const obj = JSON.parse(raw) as { rl?: Record<string, RateWindow>; at?: number };
    if (obj.rl && typeof obj.at === 'number' && Number.isFinite(obj.at)) {
      latestRateLimits = obj.rl;
      rateLimitsAsOf = obj.at;
    }
  } catch { /* corrupt — ignore */ }
}

// Burn-rate samples per window (TASK-0161): a short ring of (ts, pct)
// so the block can project time-to-cap from the recent slope.
const BUDGET_SAMPLE_WINDOW_MS = 15 * 60_000;
const budgetSamples: Record<string, Array<[number, number]>> = {};

function recordBudgetSample(key: string, pct: number): void {
  const arr = budgetSamples[key] ?? (budgetSamples[key] = []);
  const now = Date.now();
  // Skip duplicate timestamps/values so a resent statusline doesn't
  // skew the slope.
  if (arr.length && arr[arr.length - 1][1] === pct && now - arr[arr.length - 1][0] < 1000) return;
  arr.push([now, pct]);
  const cutoff = now - BUDGET_SAMPLE_WINDOW_MS;
  while (arr.length && arr[0][0] < cutoff) arr.shift();
  if (arr.length > 60) arr.shift();
}

function adoptRateLimits(rl: Record<string, RateWindow>, capturedAtMs: number): void {
  // Only strictly-newer readings adopt: never downgrade, and don't
  // re-push identical-timestamp samples that would dilute the burn slope
  // while idle (review F1); NaN never poisons rateLimitsAsOf (F3).
  if (!Number.isFinite(capturedAtMs) || capturedAtMs <= rateLimitsAsOf) return;
  latestRateLimits = rl;
  rateLimitsAsOf = capturedAtMs;
  for (const key of ['five_hour', 'seven_day']) {
    const w = rl[key];
    if (w && typeof w.used_percentage === 'number') recordBudgetSample(key, w.used_percentage);
  }
  persistUsage();
  refreshAttention();
}

// Live statusline path (active workspace). A missing captured_at means
// "just arrived", so stamp it now.
function noteRateLimits(rl: Record<string, RateWindow>, capturedAt?: string): void {
  // A reading with no captured_at (only pre-change on-disk snapshots) is
  // of unknown freshness — treat it as oldest (0) so it can't downgrade
  // or falsely-freshen the account-global reading (review F2).
  const ms = capturedAt ? Date.parse(capturedAt) : 0;
  adoptRateLimits(rl, Number.isFinite(ms) ? ms : 0);
}

// Poll the fleet for the freshest account-global reading across all
// workspaces (TASK-0171) — a silent backstop; there is no on-demand
// refresh because the statusline is the only usage source (TASK-0172).
async function pollUsage(): Promise<void> {
  try {
    const payload = await cockpitApi.agents.fleet();
    let best: { rl: Record<string, RateWindow>; at: number } | null = null;
    for (const row of payload.rows) {
      if (!row.rateLimits) continue;
      const at = row.rateLimitsAt ? Date.parse(row.rateLimitsAt) : 0;
      if (!best || at > best.at) best = { rl: row.rateLimits, at };
    }
    if (best && best.at > 0) adoptRateLimits(best.rl, best.at);
  } catch { /* transient — keep the last reading */ }
  finally {
    // Always repaint so the "as of" age ticks even without new data.
    refreshAttention();
  }
}
// Show the last-known usage immediately on launch, then refresh from any
// live sidecar shortly after (TASK-0170).
loadPersistedUsage();
refreshAttention();
window.setInterval(() => { void pollUsage(); }, 120_000);
window.setTimeout(() => { void pollUsage(); }, 3_000);

function fmtMsShort(ms: number): string {
  const mins = Math.max(1, Math.round(ms / 60_000));
  if (mins < 60) return `${mins}m`;
  return `${Math.floor(mins / 60)}h ${mins % 60}m`;
}

function budgetRow(label: string, w: RateWindow): HTMLElement {
  const pct = Math.max(0, Math.min(100, w.used_percentage));
  const tier = pct >= 85 ? 'crit' : pct >= 60 ? 'warn' : '';
  const row = document.createElement('div');
  row.className = 'ws-budget-row';
  const lab = document.createElement('span');
  lab.className = 'ws-budget-label';
  lab.textContent = label;
  const track = document.createElement('span');
  track.className = 'ws-budget-track';
  const fill = document.createElement('span');
  fill.className = 'ws-budget-fill' + (tier ? ` ${tier}` : '');
  fill.style.width = `${pct}%`;
  track.appendChild(fill);
  const val = document.createElement('span');
  val.className = 'ws-budget-val' + (tier ? ` ${tier}` : '');
  val.textContent = `${Math.round(pct)}%`;
  row.append(lab, track, val);
  if (w.resets_at) {
    const d = new Date(w.resets_at);
    if (!Number.isNaN(d.getTime())) row.title = `resets ${d.toLocaleTimeString()}`;
  }
  return row;
}

function buildBudgetBlock(): HTMLElement | null {
  const rl = latestRateLimits;
  if (!rl) return null;
  const rows: HTMLElement[] = [];
  const five = rl.five_hour;
  const seven = rl.seven_day;
  if (five && typeof five.used_percentage === 'number') rows.push(budgetRow('5h', five));
  if (seven && typeof seven.used_percentage === 'number') rows.push(budgetRow('7d', seven));
  if (rows.length === 0) return null;
  const block = document.createElement('div');
  block.className = 'ws-budget';
  // Header: "Usage" + as-of freshness (TASK-0169; refresh button removed in TASK-0172).
  const head = document.createElement('div');
  head.className = 'ws-budget-head';
  const title = document.createElement('span');
  title.textContent = 'Usage';
  head.appendChild(title);
  const asOf = document.createElement('span');
  asOf.className = 'ws-budget-asof';
  if (rateLimitsAsOf > 0) {
    const ageMin = Math.floor((Date.now() - rateLimitsAsOf) / 60_000);
    asOf.textContent = ageMin < 1 ? 'just now' : `${ageMin}m ago`;
    if (ageMin >= 10) asOf.classList.add('stale');
    asOf.title = `Reading captured ${new Date(rateLimitsAsOf).toLocaleTimeString()}`;
  }
  head.appendChild(asOf);
  block.appendChild(head);
  for (const r of rows) block.appendChild(r);
  // Reset caption for the binding (5h) window.
  if (five?.resets_at) {
    const d = new Date(five.resets_at);
    if (!Number.isNaN(d.getTime())) {
      const cap = document.createElement('div');
      cap.className = 'ws-budget-reset';
      cap.textContent = `5h resets ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
      const proj = budgetProjection('five_hour', five);
      if (proj) {
        const p = document.createElement('span');
        p.className = 'ws-budget-proj';
        p.textContent = ` · ${proj}`;
        cap.appendChild(p);
      }
      block.appendChild(cap);
    }
  }
  return block;
}

// Project time-to-cap from the recent burn slope (TASK-0161). Returns
// null when there's too little data, the slope is flat/negative, or the
// window resets before you'd hit the cap (the reset caption wins).
function budgetProjection(key: string, w: RateWindow): string | null {
  const arr = budgetSamples[key];
  if (!arr || arr.length < 3) return null;
  const first = arr[0];
  const last = arr[arr.length - 1];
  const dtMs = last[0] - first[0];
  const dPct = last[1] - first[1];
  if (dtMs < 60_000 || dPct <= 0.5) return null;   // too little data / flat
  const slope = dPct / dtMs;                         // % per ms
  const remaining = 100 - last[1];
  if (remaining <= 0) return null;
  const msToFull = remaining / slope;
  let resetMs = Infinity;
  if (w.resets_at) {
    const r = new Date(w.resets_at).getTime();
    if (!Number.isNaN(r)) resetMs = r - Date.now();
  }
  if (resetMs <= msToFull) return null;              // resets first — no alarm
  return `~${fmtMsShort(msToFull)} left at this rate`;
}

/** Repaint the attention panel, and pull fresh digests behind it.
 *
 *  Synchronous on purpose: a dozen call sites treat this as a redraw, and a
 *  redraw that awaits the network is a redraw that stutters. The digest fetch
 *  is fire-and-forget and repaints when it lands — which is also why it calls
 *  `paintAttention` rather than itself, so a slow sidecar cannot start a loop.
 *
 *  Pulled on arrival, never pushed: DES-0008's Out of Scope rules out
 *  notifications, and `refreshDigests` will not go to the network more than
 *  once every 30 seconds however often this is called. */
function refreshAttention(): void {
  paintAttention(attentionEntries());
  void refreshDigests().then(() => paintAttention(attentionEntries()));
}

function paintAttention(entries: AttentionEntry[]): void {
  const finished = finishedTodayCount();
  const budget = buildBudgetBlock();
  if (entries.length === 0 && finished === 0 && !budget) {
    attentionPanel.hidden = true;
    attentionPanel.replaceChildren();
    return;
  }
  attentionPanel.replaceChildren();
  if (entries.length > 0) {
    const head = document.createElement('div');
    head.className = 'ws-attention-head';
    head.textContent = 'Needs you';
    attentionPanel.appendChild(head);
    for (const entry of entries) attentionPanel.appendChild(buildAttentionRow(entry));
  }
  if (finished > 0) {
    const foot = document.createElement('button');
    foot.type = 'button';
    foot.className = 'ws-attention-finished';
    foot.textContent = `${finished} finished today`;
    const arrow = document.createElement('span');
    arrow.className = 'ws-attention-arrow';
    arrow.textContent = 'sessions ›';
    foot.appendChild(arrow);
    foot.addEventListener('click', () => { void navigateTo('~agents'); });
    attentionPanel.appendChild(foot);
  }
  if (budget) attentionPanel.appendChild(budget);
  attentionPanel.hidden = false;
}

// ----- Seen-acknowledgement (TASK-0157) --------------------------------
// Pulse means "unseen"; static (colour kept) means "seen, still
// pending". Looking at a workspace — active tab, window focused,
// terminal visible for ACK_DELAY_MS — acknowledges its current alert
// without touching any state data. A new state transition mints a new
// ts, so the pulse resumes for genuinely new alerts.

const ACK_DELAY_MS = 2000;
const ackedAlerts = new Set<string>();
let ackTimer: number | null = null;

function isAlertAcked(wsId: string, ts: string): boolean {
  return ackedAlerts.has(alertKey(wsId, ts));
}

function pruneAckedAlerts(): void {
  // An acked key only matters while that exact (wsId, ts) is still the
  // live state — once the state moves on (new ts) the key is dead
  // weight. Keeps the set bounded to ~one entry per workspace.
  const live = new Set<string>();
  for (const [wsId, st] of agentStates) live.add(alertKey(wsId, st.ts || ''));
  for (const k of ackedAlerts) if (!live.has(k)) ackedAlerts.delete(k);
}

function attentionStateForAck(wsId: string): AgentStatePayload | null {
  const st = agentStates.get(wsId);
  if (!st || st.decayed_from) return null;
  if (st.state !== 'needs-input' && st.state !== 'waiting') return null;
  return st;
}

function repaintAckedActive(): void {
  if (!activeId) return;
  const li = listEl.querySelector<HTMLLIElement>(`li[data-id="${activeId}"]`);
  const ws = workspaces.find((w) => w.id === activeId);
  if (li && ws) applyAgentStateToSquare(li, ws);
  refreshAttention();
}

function scheduleAck(): void {
  if (ackTimer !== null) { clearTimeout(ackTimer); ackTimer = null; }
  if (!activeId || !document.hasFocus() || terminalPane.hidden) return;
  const st = attentionStateForAck(activeId);
  if (!st) return;
  const wsId = activeId;
  const key = alertKey(wsId, st.ts || '');
  if (ackedAlerts.has(key)) return;
  ackTimer = window.setTimeout(() => {
    ackTimer = null;
    // Re-check at fire time — focus/terminal/state may have changed.
    if (activeId !== wsId || !document.hasFocus() || terminalPane.hidden) return;
    const now = attentionStateForAck(wsId);
    if (!now || alertKey(wsId, now.ts || '') !== key) return;
    ackedAlerts.add(key);
    pruneAckedAlerts();
    repaintAckedActive();
  }, ACK_DELAY_MS);
}

window.addEventListener('focus', scheduleAck);
window.addEventListener('blur', () => {
  if (ackTimer !== null) { clearTimeout(ackTimer); ackTimer = null; }
});

document.getElementById('agent-strip-queue')?.addEventListener('click', (e) => {
  if (activeQueueItems.length === 0) return;
  if (!queuePopover.hidden) { queuePopover.hidden = true; return; }
  renderQueuePopover();
  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
  queuePopover.style.left = `${Math.max(8, rect.right - 240)}px`;
  queuePopover.style.top = `${rect.top - 8}px`;
  queuePopover.style.transform = 'translateY(-100%)';
  queuePopover.hidden = false;
});

document.addEventListener('click', (e) => {
  if (queuePopover.hidden) return;
  const target = e.target as HTMLElement | null;
  const chip = document.getElementById('agent-strip-queue');
  if (target && !queuePopover.contains(target) && !(chip && chip.contains(target))) {
    queuePopover.hidden = true;
  }
});

agentStripExpand.addEventListener('click', () => {
  if (agentStripDetail.hidden) {
    renderAgentStripDetail();
    agentStripExpand.setAttribute('aria-expanded', 'true');
  } else {
    agentStripDetail.hidden = true;
    agentStripExpand.setAttribute('aria-expanded', 'false');
  }
});

// ----- Task dispatch (FEAT-0021 + FEAT-0024) -----------------------------

// Agent ids come from the served registry (`/api/cockpit/agents`, ISS-0032).
// This is a string, not a union: a closed union here is a second declaration
// of membership, which is what drifted.
type DispatchAgent = string;

interface AgentSpec { id: string; label: string; command: string; instrumented: boolean }
let agentRegistry: AgentSpec[] = [];
let defaultAgent = 'claude';

async function loadAgentRegistry(): Promise<void> {
  if (!sidecarBaseUrl) return;
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/agents`);
    if (!resp.ok) return;
    const data = await resp.json() as { agents?: AgentSpec[]; default?: string };
    if (Array.isArray(data.agents) && data.agents.length) agentRegistry = data.agents;
    if (typeof data.default === 'string' && data.default) defaultAgent = data.default;
  } catch { /* keep whatever the last successful load gave us */ }
}

/** Normalise a dispatch target, or null when the registry does not know it.
 *  Never substitutes a sibling — that substitution was ISS-0032. */
function resolveDispatchAgent(v: unknown): DispatchAgent | null {
  if (typeof v !== 'string' || !v) return null;
  const id = v.trim().toLowerCase();
  if (agentRegistry.length === 0) return id;   // registry not loaded yet
  return agentRegistry.some((a) => a.id === id) ? id : null;
}

/** Display label for any agent, dispatchable or merely recorded. An agent the
 *  cockpit cannot launch still appears in records; showing it under another
 *  agent's name would misattribute the work. */
function agentLabel(id: string | null | undefined): string {
  if (!id) return 'unknown';
  return agentRegistry.find((a) => a.id === id)?.label ?? id;
}

interface AgentAction { key: string; label: string; prompt: string; default?: boolean; when?: string[] }
let agentActions: Record<string, AgentAction[]> = {};

async function loadAgentActions(): Promise<void> {
  if (!sidecarBaseUrl) return;
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/actions`);
    if (!resp.ok) return;
    const data = await resp.json() as { actions?: Record<string, AgentAction[]> };
    agentActions = data.actions || {};
  } catch { /* verbs fall back to the built-in implement/fix prompt */ }
}

const NOTE_TYPE_BY_PREFIX: Record<string, string> = {
  TASK: 'task', ISS: 'issue', FEAT: 'feature',
  REQ: 'requirement', PHASE: 'phase', RISK: 'risk',
};

function noteTypeOfId(id: string): string | null {
  const m = id.match(/^([A-Z]+)-\d/i);
  return m ? NOTE_TYPE_BY_PREFIX[m[1].toUpperCase()] ?? null : null;
}

function verbsForId(
  id: string, opts: { type?: string | null; status?: string | null } = {},
): AgentAction[] {
  // Prefer the row's own type (works for custom actions.yaml types);
  // the ID-prefix guess is the fallback (TASK-0139).
  const t = opts.type || noteTypeOfId(id);
  const verbs = t ? agentActions[t] || [] : [];
  const status = (opts.status || '').toLowerCase();
  if (!status) return verbs;
  // `when:` lists filter by lifecycle status (TASK-0137); entries
  // without one always show.
  return verbs.filter((v) => !v.when || v.when.includes(status));
}

function resolveVerb(id: string, verbKey?: string): AgentAction | null {
  const verbs = verbsForId(id);
  if (verbs.length === 0) return null;
  if (verbKey) return verbs.find((v) => v.key === verbKey) ?? null;
  return verbs.find((v) => v.default) ?? verbs[0];
}

function dispatchAgentKey(): string {
  return `cockpit:dispatch-agent:${activeId || 'default'}`;
}

function loadDispatchAgent(): DispatchAgent {
  try {
    const stored = resolveDispatchAgent(localStorage.getItem(dispatchAgentKey()));
    if (stored) return stored;
  } catch { /* ignore */ }
  return defaultAgent;
}

function saveDispatchAgent(agent: DispatchAgent): void {
  try { localStorage.setItem(dispatchAgentKey(), agent); } catch { /* ignore */ }
}

function dispatchPrompt(id: string, rel: string): string {
  const noteRef = rel ? `docs/${rel}` : id;
  const isIssue = /^ISS-/i.test(id);
  const verb = isIssue ? `Fix ${id}` : `Work on ${id}`;
  return `${verb}. Read ${noteRef} first — the note is the spec — and follow the project-os lifecycle (preflight, implement, close-out).`;
}

// Dispatch runtime client (FEAT-0025 / TASK-0134). The queue and its
// delivery state machine live in the MAIN process (persisted,
// workspace-independent); this side builds prompts, invokes
// dispatch:execute, and renders queue state.

let activeQueueItems: QueuedDispatch[] = [];

function updateQueueChip(): void {
  const chip = document.getElementById('agent-strip-queue');
  if (!chip) return;
  chip.hidden = activeQueueItems.length === 0;
  chip.textContent = `queued ${activeQueueItems.length}`;
  chip.title = activeQueueItems
    .map((d) => `${d.verb ?? 'default'} ${d.id}`).join('\n') + '\n(click to manage)';
  if (activeQueueItems.length > 0) agentStrip.hidden = false;
  if (!queuePopover.hidden) renderQueuePopover();
}

async function refreshQueueItems(): Promise<void> {
  if (!activeId) { activeQueueItems = []; updateQueueChip(); return; }
  try {
    activeQueueItems = await cockpitApi.dispatch.list(activeId);
  } catch { activeQueueItems = []; }
  updateQueueChip();
}

cockpitApi.dispatch.onQueueChanged((ev) => {
  if (ev.workspaceId !== activeId) return;
  activeQueueItems = ev.items;
  updateQueueChip();
});

cockpitApi.dispatch.onDelivered((ev) => {
  const label = `${ev.item.verb ?? 'default'} ${ev.item.id}`;
  const suffix = ev.warning ? ` — ${ev.warning}` : '';
  if (ev.workspaceId === activeId) {
    showStatus(`Delivered ${label} (${ev.mode})${suffix}`);
    void refreshAgentSnapshot();
  }
});

function resolvedPrompt(id: string, rel: string, verbKey?: string): string {
  const verb = resolveVerb(id, verbKey);
  if (!verb) return dispatchPrompt(id, rel);
  return verb.prompt.replaceAll('{id}', id).replaceAll('{rel}', rel);
}

async function dispatchToAgent(
  id: string, rel: string, agent?: DispatchAgent, verbKey?: string,
  workspaceId?: string,
): Promise<void> {
  const wsId = workspaceId || activeId;
  if (!wsId) return;
  const chosen = agent || loadDispatchAgent();
  saveDispatchAgent(chosen);
  // Re-dispatch guard (TASK-0135): warn when this note's most recent
  // dispatch is still attached to a live session.
  const lastDispatch = currentDispatchHistory?.[0];
  if (
    lastDispatch && lastDispatch.live
    && currentFrontmatterId() === id
    && !window.confirm(
      `${id} was already dispatched (${lastDispatch.verb ?? 'default'}) to a live session. Dispatch again?`,
    )
  ) return;
  const item: QueuedDispatch = {
    id, rel, verb: verbKey, agent: chosen,
    prompt: resolvedPrompt(id, rel, verbKey),
    ts: new Date().toISOString(),
  };
  // For the on-screen workspace, make sure a terminal exists and has
  // had time to source the shell before main types into it.
  if (wsId === activeId) {
    const freshPty = !liveTerminals.has(wsId);
    showTerminal();
    await new Promise((r) => setTimeout(r, freshPty ? 600 : 150));
  }
  const res = await cockpitApi.dispatch.execute(wsId, item);
  if ('error' in res && res.error) {
    showStatus(`Dispatch failed: ${res.error}`, 'error');
    return;
  }
  const label = `${item.verb ?? 'default'} ${id}`;
  if (res.queued) {
    showStatus(`Queued ${label}${res.warning ? ` — ${res.warning}` : ''}`);
  } else {
    showStatus(`Dispatched ${label} (${res.delivered})${res.warning ? ` — ${res.warning}` : ''}`);
  }
}

// ---- queue popover ----

const queuePopover = document.createElement('div');
queuePopover.id = 'queue-popover';
queuePopover.className = 'queue-popover';
queuePopover.hidden = true;
document.body.appendChild(queuePopover);

function renderQueuePopover(): void {
  queuePopover.replaceChildren();
  if (activeQueueItems.length === 0) { queuePopover.hidden = true; return; }
  activeQueueItems.forEach((d, idx) => {
    const row = document.createElement('div');
    row.className = 'queue-row';
    const label = document.createElement('span');
    label.className = 'queue-row-label';
    label.textContent = `${d.verb ?? 'default'} · ${d.id}`;
    label.title = d.prompt;
    const remove = document.createElement('button');
    remove.type = 'button';
    remove.className = 'queue-row-remove';
    remove.textContent = '×';
    remove.title = 'Remove from queue';
    remove.addEventListener('click', () => {
      if (!activeId) return;
      void cockpitApi.dispatch.remove(activeId, idx).then((items) => {
        activeQueueItems = items;
        updateQueueChip();
        renderQueuePopover();
      });
    });
    row.append(label, remove);
    queuePopover.appendChild(row);
  });
  const clear = document.createElement('button');
  clear.type = 'button';
  clear.className = 'queue-clear';
  clear.textContent = 'Clear all';
  clear.addEventListener('click', () => {
    if (!activeId) return;
    void cockpitApi.dispatch.clear(activeId).then(() => {
      activeQueueItems = [];
      updateQueueChip();
      queuePopover.hidden = true;
    });
  });
  queuePopover.appendChild(clear);
}

// ---- CLI dispatch-requests (FEAT-0025 / TASK-0136) ----

function handleDispatchRequest(rec: { id?: string; verb?: string; agent?: string }): void {
  if (!rec || typeof rec.id !== 'string' || !rec.id) return;
  const agent = rec.agent === 'codex' ? 'codex' as const
    : rec.agent === 'claude' ? 'claude' as const : undefined;
  // Resolve the note's rel via the quick-switch corpus when possible;
  // the prompt template tolerates a missing rel (falls back to the ID).
  const hit = quickCorpus.find((q) => q.id.toUpperCase() === rec.id!.toUpperCase());
  void dispatchToAgent(rec.id.toUpperCase(), hit?.rel || '', agent, rec.verb);
}

async function drainDispatchRequests(): Promise<void> {
  if (!sidecarBaseUrl) return;
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/dispatch-requests`);
    if (!resp.ok) return;
    const data = await resp.json() as { requests?: Array<{ id?: string; verb?: string; agent?: string }> };
    for (const rec of data.requests || []) handleDispatchRequest(rec);
  } catch { /* requests retry on next attach */ }
}

function isDispatchableId(id: string | undefined): boolean {
  return !!id && noteTypeOfId(id) !== null;
}

function currentFrontmatterId(): string | undefined {
  if (!currentRel || currentRel.startsWith('~')) return undefined;
  const name = currentRel.split('/').pop() || '';
  const m = name.match(/^((TASK|ISS|FEAT|REQ|PHASE|RISK)-\d+)/i);
  return m ? m[1].toUpperCase() : undefined;
}

// The top-bar ▶ was replaced by the doc header's verb buttons
// (FEAT-0026 / TASK-0140).

// ----- Session history in Overview (FEAT-0022 / TASK-0124 + TASK-0127) --

function fmtDuration(started: string | null, ended: string | null): string {
  if (!started) return '';
  const a = Date.parse(started);
  const b = ended ? Date.parse(ended) : Date.now();
  if (!Number.isFinite(a) || !Number.isFinite(b) || b < a) return '';
  const mins = Math.round((b - a) / 60_000);
  if (mins < 1) return '<1 min';
  if (mins < 60) return `${mins} min`;
  return `${Math.floor(mins / 60)}h ${mins % 60}m`;
}

function fmtSessionDate(ts: string | null): string {
  if (!ts) return '';
  const d = new Date(ts);
  if (Number.isNaN(d.getTime())) return '';
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${mm}-${dd}`;
}

async function fetchSessions(): Promise<AgentSessionSlim[]> {
  if (!sidecarBaseUrl) return [];
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/sessions`);
    if (!resp.ok) return [];
    const data = await resp.json() as { sessions?: AgentSessionSlim[] };
    return data.sessions || [];
  } catch {
    return [];
  }
}

// ----- Recent activity feed (TASK-0127; sessions moved to ~agents in
// TASK-0178 — the overview is project-focused). --------------------------

function buildFeedsGrid(data: StatsPayload): HTMLElement {
  const grid = document.createElement('section');
  grid.className = 'ov-feeds ov-feeds-single';
  grid.append(buildRecentFeed(data.activity.recent));
  return grid;
}

// Per-project session history on the ~agents screen (TASK-0180 / ISS-0013):
// driven by the selected fleet row, sourced from that workspace's sidecar
// or its persisted .cockpit/sessions.json (via the agents:sessions IPC).
function buildAgentsSessionSection(workspaceId: string | null, name: string): HTMLElement {
  const wrap = document.createElement('section');
  wrap.className = 'ov-section ov-feed ov-sessions-feed agents-sessions';
  const h = document.createElement('h3');
  h.textContent = name ? `Recent sessions — ${name}` : 'Recent sessions';
  wrap.appendChild(h);
  const body = document.createElement('div');
  body.className = 'ov-sessions-body';
  wrap.appendChild(body);
  if (workspaceId) void fillAgentsSessions(body, workspaceId);
  return wrap;
}

async function fillAgentsSessions(body: HTMLElement, workspaceId: string): Promise<void> {
  let sessions: AgentSessionSlim[] = [];
  try { sessions = await cockpitApi.agents.sessions(workspaceId); } catch { /* empty */ }
  sessions = [...sessions].sort((a, b) => (b.started || '').localeCompare(a.started || ''));
  if (sessions.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'meta';
    empty.textContent = 'No sessions recorded for this project yet.';
    body.replaceChildren(empty);
    return;
  }
  // The ~session detail page reads the ACTIVE sidecar, so rows only
  // deep-link when the selected project is the active one.
  const navigable = workspaceId === activeId;
  const ul = document.createElement('ul');
  ul.className = 'ov-feed-list';
  for (const s of sessions.slice(0, 20)) ul.appendChild(buildSessionFeedRow(s, navigable));
  body.replaceChildren(ul);
}

function buildSessionFeedRow(s: AgentSessionSlim, navigable = true): HTMLLIElement {
  const li = document.createElement('li');
  const date = document.createElement('span');
  date.className = 'ov-feed-date';
  date.textContent = fmtSessionDate(s.started);
  const pill = document.createElement('span');
  pill.className = `ov-feed-type ov-agent-pill ov-agent-${(s.agent || 'agent').replace(/[^a-z0-9]/gi, '')}`;
  pill.textContent = s.agent || 'agent';
  const title = document.createElement('span');
  title.className = 'ov-feed-title';
  title.textContent = s.last_prompt || '(no prompt)';
  li.append(date, pill, title);
  const disp = (s as unknown as { dispatches?: Array<{ verb?: string; id: string }> }).dispatches;
  if (disp && disp.length > 0) {
    const chip = document.createElement('span');
    chip.className = 'ov-feed-tag ov-session-dispatch';
    chip.textContent = `← ${disp[0].verb ?? 'dispatch'} ${disp[0].id}`;
    li.appendChild(chip);
  }
  if (s.live) {
    const live = document.createElement('span');
    live.className = 'ov-session-live';
    live.textContent = 'live';
    li.appendChild(live);
  }
  const meta = document.createElement('span');
  meta.className = 'ov-feed-tag ov-session-row-meta';
  const dur = fmtDuration(s.started, s.ended);
  const cost = s.cost && typeof s.cost.total_cost_usd === 'number'
    ? `$${s.cost.total_cost_usd.toFixed(2)}` : '';
  meta.textContent = [dur, cost].filter(Boolean).join(' · ');
  if (s.live && s.started) meta.dataset.durStart = s.started;
  if (meta.textContent) li.appendChild(meta);
  if (s.undocumented) {
    const undoc = document.createElement('span');
    undoc.className = 'ov-session-undoc';
    undoc.textContent = 'undocumented';
    li.appendChild(undoc);
  }
  if (navigable) {
    li.style.cursor = 'pointer';
    li.title = `session ${s.session_id}`;
    li.addEventListener('click', () => {
      void navigateTo(`~session/${s.session_id}`);
    });
  } else {
    li.title = `session ${s.session_id} — open this project to view detail`;
  }
  return li;
}

// ----- Session detail virtual page (TASK-0127) --------------------------

async function renderSessionDetailPage(sessionId: string): Promise<boolean> {
  const sessions = await fetchSessions();
  const s = sessions.find((x) => x.session_id === sessionId);
  if (!s) {
    mountPlaceholder(`session ${sessionId}`);
    return false;
  }
  docView.classList.remove('overview-pane', 'agents-page',
    'design-page', 'is-design-shell');
  docView.replaceChildren();

  const head = document.createElement('header');
  head.className = 'session-page-head';
  const h1 = document.createElement('h1');
  h1.textContent = `${s.agent || 'agent'} session`;
  if (s.live) {
    const live = document.createElement('span');
    live.className = 'ov-session-live';
    live.textContent = 'live';
    h1.appendChild(live);
  }
  const meta = document.createElement('p');
  meta.className = 'session-page-meta';
  const parts = [
    s.session_id,
    s.started ? new Date(s.started).toLocaleString() : '',
    fmtDuration(s.started, s.ended),
    s.cost && typeof s.cost.total_cost_usd === 'number'
      ? `$${s.cost.total_cost_usd.toFixed(2)}` : '',
  ].filter(Boolean);
  meta.textContent = parts.join(' · ');
  head.append(h1, meta);
  if (s.undocumented) {
    const warn = document.createElement('p');
    warn.className = 'session-page-undoc';
    warn.textContent = 'Source files were edited this session without touching a TASK/ISS/CHG note.';
    head.appendChild(warn);
  }
  docView.appendChild(head);

  const section = (title: string): HTMLElement => {
    const sec = document.createElement('section');
    sec.className = 'session-page-section';
    const h = document.createElement('h2');
    h.textContent = title;
    sec.appendChild(h);
    docView.appendChild(sec);
    return sec;
  };

  if (s.prompts && s.prompts.length > 0) {
    const sec = section(`Prompts (${s.prompts.length})`);
    const ol = document.createElement('ol');
    for (const pr of s.prompts) {
      const li = document.createElement('li');
      li.textContent = pr.text;
      ol.appendChild(li);
    }
    sec.appendChild(ol);
  }

  if (s.files.length > 0) {
    const sec = section(`Files touched (${s.files.length})`);
    const ul = document.createElement('ul');
    for (const f of s.files) {
      const li = document.createElement('li');
      if (!f.startsWith('/')) {
        const a = document.createElement('a');
        a.href = '#';
        a.textContent = f;
        a.addEventListener('click', (e) => { e.preventDefault(); void navigateTo(f); });
        li.appendChild(a);
      } else {
        li.textContent = f;
      }
      ul.appendChild(li);
    }
    sec.appendChild(ul);
  }

  const detailDispatches = (s as unknown as { dispatches?: Array<{ verb?: string; id: string }> }).dispatches;
  if (detailDispatches && detailDispatches.length > 0) {
    const sec = section('Dispatched from');
    const pd = document.createElement('p');
    pd.className = 'meta';
    pd.textContent = detailDispatches
      .map((d) => `${d.verb ?? 'default'} ${d.id}`).join(', ');
    sec.appendChild(pd);
  }

  if (s.chg_ids.length > 0) {
    const sec = section('Produced changes');
    const ul = document.createElement('ul');
    for (const chg of s.chg_ids) {
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = '#';
      a.textContent = chg;
      a.addEventListener('click', (e) => {
        e.preventDefault();
        void navigateTo(`changes/${chg}.md`);
      });
      li.appendChild(a);
      ul.appendChild(li);
    }
    sec.appendChild(ul);
  }

  if (s.transcript_path) {
    const sec = section('Transcript');
    const path = s.transcript_path;
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'session-transcript-link';
    btn.textContent = path;
    btn.title = 'Reveal in Finder';
    btn.addEventListener('click', () => { void cockpitApi.app.revealInFinder(path); });
    sec.appendChild(btn);
  }

  docView.hidden = false;
  placeholder.hidden = true;
  docView.scrollTop = 0;
  return true;
}


// ----------------------------------------------------------------------
// Agents fleet screen (FEAT-0032 / TASK-0151) — cross-workspace mission
// control: one row per workspace, live state + session + cost + queue,
// with jump actions. Data comes from the main-process fleet proxy.
// ----------------------------------------------------------------------

interface FleetRow {
  workspaceId: string;
  name: string;
  root: string;
  state: string | null;
  message?: string;
  stateTs?: string;
  live: boolean;
  agent?: string;
  lastPrompt?: string;
  lastFile?: string;
  undocumented?: boolean;
  cost?: number;
  ctx?: number;
  fiveHourPct?: number;
  fiveHourResetsAt?: string;
  rateLimits?: Record<string, { used_percentage: number; resets_at?: string }>;
  rateLimitsAt?: string;
  dispatchOrigin?: string;
  queueDepth: number;
  sessionId?: string;
}
interface FleetPayload { rows: FleetRow[]; generatedAt: number; }

const FLEET_ATTENTION = new Set(['needs-input', 'waiting', 'busy']);

function fleetRank(r: FleetRow): number {
  const order: Record<string, number> = {
    'needs-input': 0, 'waiting': 1, 'busy': 2, 'error': 3,
    'done': 4, 'idle': 5,
  };
  return order[r.state ?? 'idle'] ?? 6;
}

// Selected project on the ~agents screen — drives the session-history
// section (TASK-0180). Persists across live rebuilds.
let agentsSelectedWs: string | null = null;

async function renderAgentsPage(preserveScroll = false): Promise<boolean> {
  let payload: FleetPayload;
  try {
    payload = await cockpitApi.agents.fleet();
  } catch {
    mountPlaceholder('agents');
    return false;
  }
  // Live-refresh rebuilds the whole list; keep the viewport where the
  // user left it so a peer workspace's state change doesn't yank the
  // headline fleet screen back to the top (review finding F1).
  const prevScroll = docView.scrollTop;
  docView.classList.remove('overview-pane', 'agents-page',
    'design-page', 'is-design-shell');
  docView.classList.add('agents-page');
  docView.replaceChildren();

  const rows = [...payload.rows].sort((a, b) =>
    fleetRank(a) - fleetRank(b) || a.name.localeCompare(b.name));
  const active = rows.filter((r) => r.state && FLEET_ATTENTION.has(r.state));
  const totalCost = rows.reduce((s, r) => s + (r.cost ?? 0), 0);
  const totalQueued = rows.reduce((s, r) => s + r.queueDepth, 0);
  const fiveHour = rows.map((r) => r.fiveHourPct).filter((p): p is number => typeof p === 'number');
  const budget = fiveHour.length ? Math.max(...fiveHour) : null;

  const head = document.createElement('header');
  head.className = 'agents-head';
  const h1 = document.createElement('h1');
  h1.textContent = 'Agents';
  const sub = document.createElement('span');
  sub.className = 'agents-head-sub';
  const bits = [
    `${active.length} active`,
    `${totalQueued} queued`,
    totalCost > 0 ? `$${totalCost.toFixed(2)} today` : null,
  ].filter(Boolean) as string[];
  sub.textContent = bits.join(' · ');
  head.append(h1, sub);
  if (budget !== null) {
    const rl = document.createElement('span');
    rl.className = 'agents-head-budget';
    if (budget >= 80) rl.classList.add('meter-hot');
    const reset = rows.find((r) => typeof r.fiveHourResetsAt === 'string')?.fiveHourResetsAt;
    rl.textContent = `5h limit ${Math.round(budget)}%`;
    if (reset) rl.title = `resets ${new Date(reset).toLocaleTimeString()}`;
    head.appendChild(rl);
  }
  docView.appendChild(head);

  // Which project's session history to show below (TASK-0180): the
  // selected fleet row, else the active workspace, else the top row.
  const has = (id: string | null): boolean => !!id && rows.some((r) => r.workspaceId === id);
  const selected = has(agentsSelectedWs) ? agentsSelectedWs
    : has(activeId) ? activeId
    : rows[0]?.workspaceId ?? null;

  const list = document.createElement('div');
  list.className = 'agents-list';
  for (const r of rows) {
    const el = buildFleetRow(r);
    if (r.workspaceId === selected) el.classList.add('is-selected');
    // Click the name to select this project's session history below
    // (the action buttons keep their own behaviour).
    const idcol = el.querySelector<HTMLElement>('.agents-row-id');
    if (idcol) {
      idcol.style.cursor = 'pointer';
      idcol.title = "Show this project's session history";
      idcol.addEventListener('click', () => {
        if (agentsSelectedWs === r.workspaceId) return;
        agentsSelectedWs = r.workspaceId;
        void renderAgentsPage(true);
      });
    }
    list.appendChild(el);
  }
  docView.appendChild(list);

  // Docs health across the fleet (FEAT-0028 / TASK-0251).
  docView.appendChild(buildFleetHealthSection());

  // Session history for the selected project (TASK-0180 / ISS-0013).
  const selName = rows.find((r) => r.workspaceId === selected)?.name ?? '';
  docView.appendChild(buildAgentsSessionSection(selected, selName));

  docView.hidden = false;
  placeholder.hidden = true;
  docView.scrollTop = preserveScroll ? prevScroll : 0;
  return true;
}

/** The fleet docs-health roll-up (FEAT-0028 / TASK-0251).
 *
 *  Answers one question the rail badges cannot: *is anything wrong
 *  anywhere*. It deliberately does NOT restate what a badge already
 *  says per repo — PHASE-010 and PHASE-012 each ended by deleting a
 *  surface that re-listed what another surface already drew, and this
 *  is the same shape of mistake waiting to be made.
 *
 *  Lives on the ~agents screen rather than in a new one: that screen
 *  already aggregates per-workspace state across the fleet, and a
 *  second fleet screen would split the answer in two.
 */
function buildFleetHealthSection(): HTMLElement {
  const wrap = document.createElement('section');
  wrap.className = 'agents-health';

  const head = document.createElement('div');
  head.className = 'agents-health-head';
  const title = document.createElement('h2');
  title.textContent = 'Docs health';
  head.appendChild(title);

  const rows = Array.from(fleetHealth.values());
  const drifting = rows.filter((r) => r.state === 'failing')
    .sort((a, b) => b.errors - a.errors || a.name.localeCompare(b.name));
  const unknown = rows.filter((r) => r.state === 'unknown' || r.state === 'unavailable')
    .sort((a, b) => a.name.localeCompare(b.name));
  const clean = rows.filter((r) => r.state === 'ok');

  const recheck = document.createElement('button');
  recheck.type = 'button';
  recheck.className = 'agents-health-recheck';
  recheck.textContent = 'Re-check';
  recheck.title = 'Run the validator for workspaces that are not open';
  recheck.addEventListener('click', () => {
    recheck.disabled = true;
    recheck.textContent = 'Checking…';
    void cockpitApi.fleetHealth.recheck()
      .then((payload) => { applyFleetHealthPayload(payload); void renderAgentsPage(true); })
      .catch(() => { recheck.disabled = false; recheck.textContent = 'Re-check'; });
  });
  head.appendChild(recheck);
  wrap.appendChild(head);

  // The all-clear says how many and how recently. A blank panel is
  // indistinguishable from a broken one, and this is the common state.
  if (!rows.length) {
    const p = document.createElement('p');
    p.className = 'agents-health-empty';
    p.textContent = 'No workspaces discovered — the shell looks for SNAPSHOT.yaml under ~/Dev/repos.';
    wrap.appendChild(p);
    return wrap;
  }
  if (!drifting.length) {
    const p = document.createElement('p');
    p.className = 'agents-health-empty';
    const newest = clean.map((r) => r.checkedAt).filter(Boolean).sort().pop();
    p.textContent = clean.length
      ? `${clean.length} of ${rows.length} repos clean${newest ? `, newest check ${relativeTime(newest)}` : ''}.`
      : 'Nothing checked yet.';
    wrap.appendChild(p);
  }

  for (const r of drifting) wrap.appendChild(buildHealthRow(r));

  // Behind the remote — a DIFFERENT problem from failing, so a separate
  // group (FEAT-0055). A repo can be perfectly clean and six days
  // unpushed, and that is the failure nobody could see.
  const behind = rows.filter((r) => typeof r.ahead === 'number' && r.ahead > 0)
    .sort((a, b) => (b.ahead ?? 0) - (a.ahead ?? 0));
  const noRemote = rows.filter((r) => r.remoteKind === 'none');
  if (behind.length) {
    const head2 = document.createElement('p');
    head2.className = 'agents-health-subhead';
    const total = behind.reduce((s, r) => s + (r.ahead ?? 0), 0);
    head2.textContent = `Not pushed — ${total} commit${total === 1 ? '' : 's'} across `
      + `${behind.length} repo${behind.length === 1 ? '' : 's'}`;
    wrap.appendChild(head2);
    for (const r of behind) wrap.appendChild(buildBehindRow(r));
  }
  if (noRemote.length) {
    const p = document.createElement('p');
    p.className = 'agents-health-unknown';
    // Not "up to date". Nothing is backed up at all.
    p.textContent = `${noRemote.length} with no remote: `
      + noRemote.map((r) => r.name).join(', ');
    wrap.appendChild(p);
  }

  // Unknown is listed SEPARATELY, never folded into "fine". A repo
  // nobody checked is not a repo that passed.
  if (unknown.length) {
    const sub = document.createElement('p');
    sub.className = 'agents-health-unknown';
    sub.textContent = `${unknown.length} not checked: ${unknown.map((r) => r.name).join(', ')}`;
    sub.title = unknown.map((r) => `${r.name}: ${r.detail || 'no sidecar, not yet validated'}`).join('\n');
    wrap.appendChild(sub);
  }
  return wrap;
}

/** One repo that is ahead of its remote, with the push (FEAT-0055). */
function buildBehindRow(r: FleetHealthRow): HTMLElement {
  const row = document.createElement('div');
  row.className = 'agents-health-row is-behind';

  const count = document.createElement('span');
  count.className = 'agents-health-count is-behind';
  count.textContent = String(r.ahead ?? 0);

  const name = document.createElement('span');
  name.className = 'agents-health-name';
  name.textContent = r.name;

  const act = document.createElement('button');
  act.type = 'button';
  act.className = 'agents-health-push';

  if (r.remoteKind === 'deploy') {
    // The refusal is the feature. One fleet repo's only remote is a
    // server path; pushing it deploys a live website.
    act.textContent = 'deploy remote';
    act.disabled = true;
    act.title = 'This repo\u2019s remote is a deployment target, not a backup. '
      + 'Pushing it would publish a running site, so it is never offered here.';
  } else {
    act.textContent = `Push ${r.ahead}`;
    act.title = `Publish ${r.ahead} commit${r.ahead === 1 ? '' : 's'} from ${r.name}`;
    act.addEventListener('click', () => {
      // Say what will be published BEFORE doing it: these counts are
      // large and surprising — 117 commits and six days for one repo.
      act.disabled = true;
      act.textContent = 'Pushing…';
      void cockpitApi.git.push(r.workspaceId).then((res) => {
        if (res.ok) {
          showStatus(`Pushed ${r.name}`);
          act.textContent = 'Pushed';
        } else {
          showStatus(`Push failed: ${res.error ?? 'unknown error'}`, 'error');
          act.disabled = false;
          act.textContent = `Push ${r.ahead}`;
        }
      });
    });
  }

  row.append(count, name, act);
  row.title = `${r.remote ?? 'no remote'}`;
  return row;
}

function buildHealthRow(r: FleetHealthRow): HTMLElement {
  const row = document.createElement('div');
  row.className = 'agents-health-row';

  const count = document.createElement('span');
  count.className = 'agents-health-count';
  count.textContent = String(r.errors);

  const name = document.createElement('span');
  name.className = 'agents-health-name';
  name.textContent = r.name;

  const when = document.createElement('span');
  when.className = 'agents-health-when';
  when.textContent = `${r.checkedAt ? relativeTime(r.checkedAt) : 'never'}${r.stale ? ' · stale' : ''}`;

  row.append(count, name, when);
  row.title = healthSummary(r);
  // Not a note, so no `data-note-rel` — but the workspace name is worth
  // copying, and the fleet rows are the other button-shaped surface
  // ISS-0079 covers. Left without a menu deliberately: there is no
  // single note behind a repo's health row.
  // Deep-link into that workspace's own drift panel (TASK-0112), which
  // holds the actual violations — this row only carries the number.
  row.addEventListener('click', () => { void openWorkspace(r.workspaceId); });
  return row;
}

function buildFleetRow(r: FleetRow): HTMLElement {
  const row = document.createElement('div');
  row.className = 'agents-row';
  if (!r.state || r.state === 'idle') row.classList.add('is-dormant');

  const dot = document.createElement('span');
  dot.className = 'agents-row-dot';
  dot.dataset.state = r.state ?? 'idle';

  const idcol = document.createElement('div');
  idcol.className = 'agents-row-id';
  const name = document.createElement('span');
  name.className = 'agents-row-name';
  name.textContent = r.name;
  idcol.append(dot, name);

  const sess = document.createElement('div');
  sess.className = 'agents-row-sess';
  const line1 = document.createElement('span');
  line1.className = 'agents-row-line1';
  const stateLabel = r.state ? agentStateLabel(r.state) : 'idle';
  const elapsed = r.stateTs ? fmtDuration(r.stateTs, null) : '';
  const summary = r.live && r.lastPrompt ? ` — ${r.lastPrompt}`
    : r.message ? ` — ${r.message}`
    : r.lastPrompt ? ` — ${r.lastPrompt}` : '';
  line1.textContent = `${r.agent || 'agent'} · ${stateLabel}${elapsed ? ' ' + elapsed : ''}${summary}`;
  const line2 = document.createElement('span');
  line2.className = 'agents-row-line2';
  const l2 = [];
  if (r.lastFile) l2.push(`last: ${r.lastFile}`);
  if (r.dispatchOrigin) l2.push(`from ${r.dispatchOrigin}`);
  if (r.queueDepth > 0) l2.push(`queue ${r.queueDepth}`);
  line2.textContent = l2.join(' · ');
  if (r.undocumented) {
    const u = document.createElement('span');
    u.className = 'agents-row-undoc';
    u.textContent = 'undocumented';
    line2.append(' ', u);
  }
  sess.append(line1, line2);

  const meters = document.createElement('div');
  meters.className = 'agents-row-meters';
  const mbits = [];
  if (typeof r.ctx === 'number') mbits.push(`ctx ${Math.round(r.ctx)}%`);
  if (typeof r.cost === 'number') mbits.push(`$${r.cost.toFixed(2)}`);
  meters.textContent = mbits.join(' · ');

  const acts = document.createElement('div');
  acts.className = 'agents-row-acts';
  const primaryLabel = r.state === 'needs-input' ? 'respond'
    : r.state === 'waiting' ? 'review' : 'terminal';
  const termBtn = document.createElement('button');
  termBtn.type = 'button';
  termBtn.className = 'agents-btn primary';
  termBtn.textContent = primaryLabel;
  termBtn.addEventListener('click', () => {
    void (async () => {
      if (activeId !== r.workspaceId) await openWorkspace(r.workspaceId);
      showTerminal();
    })();
  });
  acts.appendChild(termBtn);
  if (r.sessionId) {
    const sessBtn = document.createElement('button');
    sessBtn.type = 'button';
    sessBtn.className = 'agents-btn';
    sessBtn.textContent = 'session';
    sessBtn.addEventListener('click', () => {
      void (async () => {
        if (activeId !== r.workspaceId) await openWorkspace(r.workspaceId);
        void navigateTo(`~session/${r.sessionId}`);
      })();
    });
    acts.appendChild(sessBtn);
  }

  row.append(idcol, sess, meters, acts);
  return row;
}


// ----------------------------------------------------------------------
// Overview scopes (FEAT-0023 / TASK-0129 + TASK-0130)
// ----------------------------------------------------------------------

// ----- Left pane: scope list -------------------------------------------

function buildScopeRow(
  label: string, target: string, current: boolean,
  pct: number | null, doneCount?: number, id?: string | null,
): HTMLElement {
  const row = document.createElement('button');
  row.type = 'button';
  row.className = 'scope-row' + (current ? ' current' : '');
  // The scope pane was the one surface with no IDs on it — 24 phase rows
  // reading `MVP`, `Downstream pilot`, and nothing to tie them to the
  // PHASE-nnn everything else names them by (Edwin, 2026-08-02). Same
  // `nav-id mono ov-typed` grammar as every other row, so the type colour
  // and the ISS-0084 shortening come along for free.
  if (id) {
    const idEl = document.createElement('span');
    idEl.className = 'nav-id mono ov-typed scope-id';
    idEl.dataset.type = 'phase';
    idEl.textContent = shortNoteId(id);
    idEl.title = id;
    row.appendChild(idEl);
  }
  const name = document.createElement('span');
  name.className = 'scope-name';
  name.textContent = label;
  name.title = label;
  row.appendChild(name);
  // Completed phases carry a tick + item count instead of a 100% bar (dossier
  // plate C, pin 9): a full progress bar on five finished phases is exactly the
  // "shouting as loudly as the live one" the redesign set out to stop.
  if (doneCount != null) {
    const tick = document.createElement('span');
    tick.className = 'scope-done';
    tick.textContent = `✓ ${doneCount}`;
    row.appendChild(tick);
  } else if (pct != null) {
    const bar = document.createElement('span');
    bar.className = 'scope-bar';
    const fill = document.createElement('span');
    fill.style.width = `${Math.round(pct)}%`;
    bar.appendChild(fill);
    const pctEl = document.createElement('span');
    pctEl.className = 'scope-pct';
    pctEl.textContent = `${Math.round(pct)}%`;
    row.append(bar, pctEl);
  }
  row.addEventListener('click', () => {
    if (currentRel === target) return;
    void navigateTo(target);
  });
  return row;
}

function renderOverviewScopePane(): void {
  if (currentNavMode !== 'overview') return;
  wsNavPlaceholder.hidden = true;
  wsNavContent.hidden = false;
  const wrap = document.createElement('div');
  wrap.className = 'scope-pane';
  const h = document.createElement('h4');
  h.className = 'scope-heading';
  h.textContent = 'Scope';
  wrap.appendChild(h);
  wrap.appendChild(buildScopeRow('⌂ Project', '~overview', overviewScope === null, null));

  // Plate C, pin 9: live phases lead under "In flight"; finished ones collapse
  // into a "Completed · N" band. `phaseIsComplete` is shared with the centre
  // pane's accordion deliberately — two panes disagreeing about which phase is
  // finished is the drift this codebase keeps paying for.
  const phases = (scopePhaseList || []).filter((p) => /^PHASE-/i.test(p.key));
  const live = sortLivePhases(phases.filter((p) => !phaseIsComplete(p)));
  const complete = phases.filter((p) => phaseIsComplete(p));

  if (live.length > 0) {
    const ph = document.createElement('h4');
    ph.className = 'scope-heading';
    ph.textContent = 'In flight';
    wrap.appendChild(ph);
    for (const p of live) {
      const total = p.tasks.done + p.tasks.in_progress + p.tasks.backlog;
      const pct = total > 0 ? (p.tasks.done / total) * 100 : 0;
      wrap.appendChild(buildScopeRow(
        p.title, `~overview/${p.key}`, overviewScope === p.key, pct,
        undefined, p.key,
      ));
    }
  }

  if (complete.length > 0) {
    const head = document.createElement('button');
    head.type = 'button';
    head.className = 'scope-heading scope-band'
      + (scopeCompletedOpen ? ' is-open' : '');
    const chev = document.createElement('span');
    chev.className = 'scope-chev';
    const label = document.createElement('span');
    label.textContent = `Completed · ${complete.length}`;
    head.append(chev, label);
    const body = document.createElement('div');
    body.className = 'scope-band-body';
    body.hidden = !scopeCompletedOpen;
    for (const p of complete) {
      const items = p.tasks.done + p.tasks.in_progress + p.tasks.backlog;
      body.appendChild(buildScopeRow(
        p.title, `~overview/${p.key}`, overviewScope === p.key, null, items,
        p.key,
      ));
    }
    head.addEventListener('click', () => {
      scopeCompletedOpen = !scopeCompletedOpen;
      try { localStorage.setItem('cockpit:scope-completed-open', scopeCompletedOpen ? '1' : '0'); }
      catch { /* ignore */ }
      head.classList.toggle('is-open', scopeCompletedOpen);
      body.hidden = !scopeCompletedOpen;
    });
    // ISS-0089: the card contains its rows. The frame used to sit on the
    // heading button alone, with the 22 phase rows as a sibling outside
    // it — so the card counted phases it did not enclose.
    const card = document.createElement('div');
    card.className = 'scope-band-card';
    card.append(head, body);
    wrap.appendChild(card);
  }
  wsNavContent.replaceChildren(wrap);
}

// ----- Centre: scoped dashboard ----------------------------------------

function buildScopedHeader(data: StatsPayload): HTMLElement {
  const scope = data.scope!;
  const head = document.createElement('header');
  head.className = 'scoped-head';
  const crumb = document.createElement('a');
  crumb.href = '#';
  crumb.className = 'scoped-crumb';
  crumb.textContent = 'Overview';
  crumb.addEventListener('click', (e) => {
    e.preventDefault();
    void navigateTo('~overview');
  });
  const sep = document.createElement('span');
  sep.className = 'scoped-sep';
  sep.textContent = '▸';
  const title = document.createElement('h2');
  title.className = 'scoped-title';
  title.textContent = `${scope.id} · ${scope.title}`;
  head.append(crumb, sep, title);
  appendIf(head, statusChip(scope.status));

  // How far, and what gates it — the two questions a phase page should
  // answer before anything else (TASK-0202). No extra row spent.
  const stats = document.createElement('span');
  stats.className = 'scoped-head-stats';
  const p = data.phases[0];
  if (p) {
    const t = p.tasks;
    const total = t.done + t.in_progress + t.backlog;
    if (total > 0) {
      const frac = document.createElement('span');
      frac.className = 'scoped-frac num';
      frac.textContent = `${t.done}/${total} · ${Math.round((t.done / total) * 100)}%`;
      stats.appendChild(frac);
    }
  }
  const criteria = data.exit_criteria || [];
  if (criteria.length > 0) {
    const met = criteria.filter((c) => c.done).length;
    const gates = document.createElement('a');
    gates.href = '#exit-criteria';
    gates.className = 'scoped-gates mono';
    gates.textContent = `gates ${met}/${criteria.length}`;
    gates.title = `${met} of ${criteria.length} exit criteria met`;
    if (met < criteria.length) gates.classList.add('is-open');
    gates.addEventListener('click', (e) => {
      e.preventDefault();
      docView.querySelector('#exit-criteria')?.scrollIntoView({
        behavior: 'smooth', block: 'start',
      });
    });
    stats.appendChild(gates);
  }
  const open = document.createElement('a');
  open.href = '#';
  open.className = 'scoped-open-note';
  open.textContent = 'open note ↗';
  open.addEventListener('click', (e) => {
    e.preventDefault();
    void navigateTo(scope.rel);
  });
  stats.appendChild(open);
  head.appendChild(stats);
  return head;
}

// ----- Scoped health band (TASK-0202) -----------------------------------
// One line of scoped counts with inline mix-bars, replacing the repeated
// six-tile hero. Same facts, ~40 px instead of ~230 px, and it doesn't
// make a phase page look like a second project dashboard.

function buildScopedHealthBand(data: StatsPayload): HTMLElement {
  const band = document.createElement('section');
  band.className = 'ov-health';
  const hero = data.hero;
  const mix = data.status_mix || {};
  const buckets = data.status_buckets || {};

  const cell = (
    value: string, label: string,
    buckets?: MixBuckets, raw?: Record<string, number>,
  ): HTMLElement => {
    const el = document.createElement('span');
    el.className = 'ov-health-cell';
    const v = document.createElement('b');
    v.className = 'num';
    v.textContent = value;
    el.append(v, document.createTextNode(label));
    if (buckets) el.appendChild(buildMixBar(buckets, raw));
    return el;
  };
  const divider = (): HTMLElement => {
    const d = document.createElement('span');
    d.className = 'ov-health-div';
    return d;
  };

  band.append(
    cell(`${hero.features.done}/${hero.features.total}`, 'features', buckets.features, mix.features),
    divider(),
    cell(`${hero.tasks.done}/${hero.tasks.total}`, 'features', buckets.tasks, mix.tasks),
    divider(),
    cell(`${hero.tests.passing}/${hero.tests.total}`, 'tests'),
    divider(),
    cell(String(hero.issues.open), hero.issues.open === 1 ? 'issue open' : 'issues open'),
  );
  if (hero.requirements && hero.requirements.total > 0) {
    band.append(
      divider(),
      cell(`${hero.requirements.done}/${hero.requirements.total}`, 'reqs'),
    );
  }

  // Live/attention flags, computed from the same children the rows use.
  const p = data.phases[0];
  if (p) {
    const children: PhaseItem[] = [];
    for (const f of p.features) children.push(f, ...f.children);
    children.push(...p.loose);
    const inFlight = children.filter((c) => isActiveStatus(c.status)).length;
    const triage = children.filter((c) => (c.status || '').toLowerCase() === 'triage').length;
    if (inFlight > 0) {
      const el = document.createElement('span');
      el.className = 'ov-health-flag is-live';
      el.textContent = `${inFlight} in flight`;
      band.appendChild(el);
    }
    if (triage > 0) {
      const el = document.createElement('span');
      el.className = 'ov-health-flag is-attention';
      el.textContent = `${triage} triage`;
      band.appendChild(el);
    }
  }
  return band;
}

// ----- Scoped feature rows (TASK-0202) ----------------------------------
// Every row states its fraction; rows with live work name the item that
// is moving and the one queued behind it; a row containing an open issue
// flags it. Answering "what's left in this feature?" no longer requires
// hovering squares one at a time.

function isDoneItem(item: PhaseItem): boolean {
  return item.bucket === 'done';
}

function buildFeatureNextLine(children: PhaseItem[]): HTMLElement | null {
  const doing = children.find((c) => isActiveStatus(c.status));
  const triage = children.find(
    (c) => c.type === 'issue'
      && ['triage', 'open'].includes((c.status || '').toLowerCase()),
  );
  const failing = children.find(
    (c) => c.type === 'test' && (c.status || '').toLowerCase() === 'failing',
  );
  const next = children.find(
    (c) => !isDoneItem(c) && !isActiveStatus(c.status) && c !== triage && c !== failing,
  );
  if (!doing && !triage && !failing) return null;

  const line = document.createElement('div');
  line.className = 'scoped-feat-next';
  const add = (
    lead: string, leadClass: string, item: PhaseItem,
  ): void => {
    const l = document.createElement('span');
    l.className = `scoped-next-lead ${leadClass}`;
    l.textContent = lead;
    const id = document.createElement('span');
    id.className = 'mono ov-typed';
    id.dataset.type = item.type;
    id.textContent = item.id || '';
    const title = document.createElement('span');
    title.className = 'scoped-next-title';
    title.textContent = item.title;
    const group = document.createElement('span');
    group.className = 'scoped-next-item';
    group.append(l, id, title);
    if (item.rel) {
      group.style.cursor = 'pointer';
      group.addEventListener('click', (e) => {
        e.stopPropagation();
        void navigateTo(item.rel!);
      });
    }
    line.appendChild(group);
  };
  // ISS-0098: at most ONE annotation on the row, in priority order, with a
  // `+N` for the rest. Three of them stacked into a column 78px tall
  // against neighbouring rows of 32 — and a row whose height depends on how
  // much is wrong with it is not a row.
  //
  // Priority is the order below: a failing test outranks live work, which
  // outranks something waiting on triage, which outranks what is next.
  const candidates: Array<[string, string, PhaseItem]> = [];
  if (failing) candidates.push(['▸ failing', 'is-fail', failing]);
  if (doing) candidates.push(['▸ doing', 'is-live', doing]);
  if (triage) candidates.push([`▸ ${(triage.status || '').toLowerCase()}`, 'is-attention', triage]);
  if (doing && next) candidates.push(['next', 'is-next', next]);
  if (!candidates.length) return null;

  const [lead, cls, item] = candidates[0];
  add(lead, cls, item);
  if (candidates.length > 1) {
    const more = document.createElement('span');
    more.className = 'scoped-next-more';
    more.textContent = `+${candidates.length - 1}`;
    more.title = candidates.slice(1)
      .map(([l, , it]) => `${l} ${it.id || ''} ${it.title}`.trim())
      .join('\n');
    line.appendChild(more);
  }
  return line;
}

function buildScopedFeatureRow(
  feat: PhaseFeature | { id?: string; title: string; rel?: string; status: string; children: PhaseItem[] },
  opts: { loose?: boolean } = {},
): HTMLElement {
  const children = feat.children;
  const done = children.filter(isDoneItem).length;
  const row = document.createElement('div');
  row.className = 'scoped-feat' + (opts.loose ? ' scoped-loose' : '');
  if (children.length > 0 && done === children.length) row.classList.add('is-done');

  const top = document.createElement('div');
  top.className = 'scoped-feat-top';

  const name = document.createElement(feat.rel ? 'a' : 'span');
  name.className = 'scoped-feat-name';
  name.textContent = `${feat.id ?? ''} ${feat.title}`.trim();
  if (feat.rel) {
    (name as HTMLAnchorElement).href = '#';
    name.addEventListener('click', (e) => {
      e.preventDefault();
      void navigateTo(feat.rel!);
    });
    name.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      e.stopPropagation();
      const fid = feat.id || '';
      void cockpitApi.app.showContextMenu('nav-row', {
        id: fid, rel: feat.rel || '',
        workspaceId: activeId || '', root: '',
        verbs: verbsForId(fid, { type: 'feature', status: feat.status })
          .map((v) => ({ key: v.key, label: v.label })),
        currentAgent: loadDispatchAgent(),
    agents: agentRegistry,
      });
    });
  }
  top.appendChild(name);

  // ISS-0101: the chip goes with the NAME, ahead of everything describing
  // the feature's CHILDREN. It is the feature's own state; the fraction and
  // the squares are its children's. Rendered last, `planned` read as though
  // it belonged to the squares beside it.
  if (!opts.loose) appendIf(top, statusChip(feat.status));

  if (children.length > 0) {
    const frac = document.createElement('span');
    frac.className = 'scoped-feat-frac num';
    frac.textContent = `${done}/${children.length}`;
    top.appendChild(frac);
  }

  const sqs = document.createElement('span');
  sqs.className = 'scoped-feat-sqs';
  // ISS-0098: a capped run, then `+N`. The strip used to render every child
  // and wrap, which turned FEAT-0071's nine squares into a 9px-wide,
  // 105px-tall column beside 32px neighbours — the row had no column model,
  // so the most compressible child absorbed every shortfall, and a 3px
  // square is the most compressible thing on the row.
  //
  // Capping is the honest fix rather than shrinking: squares are a
  // per-item signal (DES-0004), and forty of them in a strip communicate
  // no more than twelve plus a number.
  const shown = children.slice(0, FEATURE_SQUARE_LIMIT);
  for (const c of shown) sqs.appendChild(makePhaseSquare(c, false));
  if (children.length > shown.length) {
    const more = document.createElement('span');
    more.className = 'scoped-feat-more';
    more.textContent = `+${children.length - shown.length}`;
    more.title = `${children.length} children in total`;
    sqs.appendChild(more);
  }
  if (children.length === 0) {
    const none = document.createElement('span');
    none.className = 'ov-phase-empty';
    none.textContent = 'Nothing names this phase yet — a note joins it by setting `phase:`.';
    sqs.appendChild(none);
  }
  top.appendChild(sqs);
  row.appendChild(top);

  const next = buildFeatureNextLine(children);
  if (next) row.appendChild(next);
  return row;
}

function buildScopedFeatures(p: StatsPhase): HTMLElement {
  const wrap = document.createElement('section');
  wrap.className = 'ov-section';
  const h = document.createElement('h3');
  h.textContent = `Features · ${p.features.length}`;
  wrap.appendChild(h);

  if (p.features.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'meta';
    empty.textContent = 'No features assigned to this phase yet.';
    wrap.appendChild(empty);
  }

  // Live features first; finished ones fold behind a disclosure so a
  // long-delivered phase doesn't bury the two rows that still move.
  const isFeatureDone = (f: PhaseFeature): boolean =>
    isDoneItem(f) && f.children.every(isDoneItem);
  const live = p.features.filter((f) => !isFeatureDone(f));
  const finished = p.features.filter(isFeatureDone);

  for (const feat of live) wrap.appendChild(buildScopedFeatureRow(feat));

  if (p.loose.length > 0) {
    wrap.appendChild(buildScopedFeatureRow(
      { title: 'Loose items', status: '', children: p.loose }, { loose: true },
    ));
  }

  if (finished.length > 0) {
    const disc = document.createElement('button');
    disc.type = 'button';
    disc.className = 'scoped-disclosure';
    const chev = document.createElement('span');
    chev.className = 'ov-chev';
    const label = document.createElement('span');
    label.textContent = `${finished.length} delivered feature${finished.length === 1 ? '' : 's'}`;
    disc.append(chev, label);
    const body = document.createElement('div');
    body.hidden = true;
    for (const feat of finished) body.appendChild(buildScopedFeatureRow(feat));
    disc.addEventListener('click', () => {
      body.hidden = !body.hidden;
      disc.classList.toggle('is-open', !body.hidden);
    });
    wrap.append(disc, body);
  }
  return wrap;
}

/** How many task squares a feature row shows before counting the rest.
 *
 *  Twelve is the widest run that fits beside a 260px name, a fraction, a
 *  chip and the next-line trail at the narrowest pane width the layout
 *  supports — measured, not chosen. Beyond it the strip says `+N`, because
 *  a row whose height depends on its child count is not a row (ISS-0098). */
const FEATURE_SQUARE_LIMIT = 12;

// ----- Remaining work (TASK-0202) ---------------------------------------
// What would finish this phase, spelled out. Previously only obtainable
// by hovering each unfilled square in turn.

const REMAINING_RANK: Record<string, number> = {
  failing: 0, blocked: 1, doing: 2, review: 3,
  triage: 4, open: 5, draft: 6, ready: 6, backlog: 7, planned: 7,
  deferred: 9, parked: 9,
};

function buildRemainingList(p: StatsPhase): HTMLElement {
  const items: PhaseItem[] = [];
  for (const feature of p.features) {
    if (!isDoneItem(feature)) items.push(feature);
    items.push(...feature.children.filter((c) => !isDoneItem(c)));
  }
  items.push(...p.loose.filter((c) => !isDoneItem(c)));

  const wrap = document.createElement('section');
  wrap.className = 'ov-section ov-tile';
  const h = document.createElement('h3');
  h.textContent = items.length ? `Remaining · ${items.length}` : 'Remaining';
  wrap.appendChild(h);

  if (items.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'meta scoped-row-clear';
    empty.textContent = 'Nothing left — every item in this phase is done.';
    wrap.appendChild(empty);
    return wrap;
  }

  items.sort((a, b) => {
    const ra = REMAINING_RANK[(a.status || '').toLowerCase()] ?? 8;
    const rb = REMAINING_RANK[(b.status || '').toLowerCase()] ?? 8;
    return ra - rb || (a.id || '').localeCompare(b.id || '');
  });

  const list = document.createElement('ul');
  list.className = 'scoped-rowlist';
  for (const item of items) {
    const li = document.createElement('li');
    const id = document.createElement('span');
    id.className = 'scoped-row-id mono ov-typed';
    id.dataset.type = item.type;
    id.textContent = item.id || '';
    const title = document.createElement('span');
    title.className = 'scoped-row-title';
    title.textContent = item.title;
    li.append(id, title);
    appendIf(li, statusChip(item.status));
    if (item.rel) {
      li.style.cursor = 'pointer';
      li.addEventListener('click', () => void navigateTo(item.rel!));
    }
    list.appendChild(li);
  }
  wrap.appendChild(list);
  return wrap;
}

// Criteria frequently name their evidence inline ("… verified by
// TST-0010"). Lifting that id out and joining it to the live index turns
// a flat checklist into a gate with proof attached. Client-side regex is
// the cheap form; parsing it in `_exit_criteria_from_body` would make the
// link durable (recorded as a FEAT-0040 open question).
const EVIDENCE_ID_RE = /\b((?:TST|TASK|ISS|CHG|ADR|REQ)-\d+)\b/g;

function buildExitCriteria(data: StatsPayload, p?: StatsPhase): HTMLElement {
  const exit = document.createElement('section');
  exit.className = 'ov-section ov-tile';
  exit.id = 'exit-criteria';
  const criteria = data.exit_criteria || [];

  const head = document.createElement('div');
  head.className = 'scoped-exit-head';
  const h = document.createElement('h3');
  h.textContent = 'Exit criteria';
  head.appendChild(h);

  if (criteria.length === 0) {
    exit.appendChild(head);
    const empty = document.createElement('p');
    empty.className = 'meta';
    empty.textContent = 'No exit criteria recorded in the phase note.';
    exit.appendChild(empty);
    return exit;
  }

  const met = criteria.filter((c) => c.done).length;
  const frac = document.createElement('span');
  frac.className = 'scoped-exit-frac num';
  frac.textContent = `${met}/${criteria.length}`;
  const bar = document.createElement('span');
  bar.className = 'scoped-exit-bar';
  const fill = document.createElement('i');
  fill.style.width = `${Math.round((met / criteria.length) * 100)}%`;
  bar.appendChild(fill);
  head.append(frac, bar);
  exit.appendChild(head);

  // Index the scope's items so an id mentioned in a criterion can carry
  // that item's *live* status rather than a restated one.
  const byId = new Map<string, PhaseItem>();
  if (p) {
    for (const feature of p.features) {
      if (feature.id) byId.set(feature.id, feature);
      for (const child of feature.children) {
        if (child.id) byId.set(child.id, child);
      }
    }
    for (const item of p.loose) if (item.id) byId.set(item.id, item);
  }

  const ul = document.createElement('ul');
  ul.className = 'scoped-exit-list';
  for (const c of criteria) {
    const li = document.createElement('li');
    if (c.done) li.classList.add('done');
    const box = document.createElement('span');
    box.className = 'scoped-exit-box';
    box.textContent = c.done ? '☑' : '☐';
    const text = document.createElement('span');
    text.className = 'scoped-exit-text';
    text.textContent = c.text;
    li.append(box, text);

    const seen = new Set<string>();
    for (const match of c.text.matchAll(EVIDENCE_ID_RE)) {
      const id = match[1];
      if (seen.has(id)) continue;
      seen.add(id);
      const item = byId.get(id);
      if (!item) continue;
      const chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'scoped-exit-evidence';
      const idEl = document.createElement('span');
      idEl.className = 'mono ov-typed';
      idEl.dataset.type = item.type;
      idEl.textContent = id;
      chip.appendChild(idEl);
      appendIf(chip, statusChip(item.status));
      chip.title = `${id} ${item.title} (${item.status || '—'})`;
      if (item.rel) {
        chip.addEventListener('click', (e) => {
          e.stopPropagation();
          void navigateTo(item.rel!);
        });
      }
      li.appendChild(chip);
    }
    ul.appendChild(li);
  }
  exit.appendChild(ul);
  return exit;
}

function buildScopedActivity(data: StatsPayload): HTMLElement {
  const act = document.createElement('section');
  act.className = 'ov-section ov-feed ov-tile';
  const h = document.createElement('h3');
  h.textContent = 'Activity in this phase';
  act.appendChild(h);

  const recent = data.activity.recent;
  if (recent.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'meta';
    empty.textContent = 'No recorded activity yet.';
    act.appendChild(empty);
    return act;
  }
  const ul = document.createElement('ul');
  // Scoped rows regain the id column the 3-column template dropped in
  // TASK-0173 — without it two rows from the same day and type are
  // indistinguishable. The template below matches the project feed.
  ul.className = 'ov-feed-list';
  for (const r of recent.slice(0, 8)) {
    const li = document.createElement('li');
    const typeTag = r.type
      ? `<span class="ov-feed-type ov-feed-type-${escapeHtml(r.type)}">${escapeHtml(r.type)}</span>`
      : '<span class="ov-feed-type ov-feed-type-empty"></span>';
    li.innerHTML = `<span class="ov-feed-date">${escapeHtml(r.date)}</span>`
      + typeTag
      + `<span class="ov-feed-id" title="${escapeHtml(r.id || '')}">`
      + `${escapeHtml(shortNoteId(r.id || ''))}</span>`
      + `<span class="ov-feed-title">${escapeHtml(r.title)}</span>`;
    li.style.cursor = 'pointer';
    li.addEventListener('click', () => { if (r.rel) void navigateTo(r.rel); });
    ul.appendChild(li);
  }
  act.appendChild(ul);
  return act;
}

function renderScopedOverview(data: StatsPayload): void {
  docView.classList.add('overview-pane');
  const p = data.phases[0];
  const parts: HTMLElement[] = [
    buildScopedHeader(data),
    buildScopedHealthBand(data),
  ];
  if (p) parts.push(buildScopedFeatures(p));
  const grid = document.createElement('section');
  grid.className = 'ov-feeds';
  grid.appendChild(buildExitCriteria(data, p));
  if (p) grid.appendChild(buildRemainingList(p));
  parts.push(grid);
  if (data.scope?.id) parts.push(buildVerificationPanel(data.scope.id));
  parts.push(buildScopedActivity(data));
  docView.replaceChildren(...parts);
  docView.hidden = false;
  placeholder.hidden = true;
  refreshFooterPath();
}

// ----- Right pane: Now column + scope context ---------------------------


// ----- Record column (TASK-0203) ----------------------------------------
// The overview right pane had no job: pinned-or-nothing at project scope,
// a raw link-graph dump at phase scope. It becomes the *record* column —
// decisions, verification, library — because those are populated by
// construction and never go stale, unlike the live state a "meanwhile"
// column would have shown (which the FEAT-0040 states audit found empty
// most of the time). It is also the only surface where ADRs and
// acceptance tests are reachable without browsing the Library tree.

function buildRecordCard(heading: string, right?: string): {
  card: HTMLElement; body: HTMLElement;
} {
  const card = document.createElement('div');
  card.className = 'ctx-card';
  const head = document.createElement('div');
  head.className = 'ctx-card-head';
  const h = document.createElement('span');
  h.textContent = heading;
  head.appendChild(h);
  if (right) {
    const r = document.createElement('span');
    r.className = 'ctx-card-right';
    r.textContent = right;
    head.appendChild(r);
  }
  const body = document.createElement('div');
  card.append(head, body);
  return { card, body };
}

function buildRecordRow(
  id: string, title: string, rel?: string, type?: string,
  status?: string,
): HTMLElement {
  const row = document.createElement('div');
  row.className = 'ctx-kv';
  if (id) {
    const idEl = document.createElement('span');
    idEl.className = 'mono ctx-kv-id ov-typed';
    if (type) idEl.dataset.type = type;
    idEl.textContent = id;
    row.appendChild(idEl);
  }
  const titleEl = document.createElement('span');
  titleEl.className = 'ctx-kv-title';
  titleEl.textContent = title;
  titleEl.title = title;
  row.appendChild(titleEl);
  appendIf(row, statusChip(status));
  if (rel) {
    row.style.cursor = 'pointer';
    row.addEventListener('click', () => void navigateTo(rel));
  }
  return row;
}

interface RecordNote {
  id: string; title: string; rel: string; status: string; type: string;
}

// Which decisions reach a scope is a link-graph question, so the sidecar
// answers it (`scope-tests` returns `decisions` resolved through the same
// frontmatter link fields the graph uses). An earlier cut matched ids
// inside ADR titles here; it happened to work on this corpus and would
// have silently missed any ADR whose title didn't name its subject.
async function fetchScopeDecisions(noteId: string): Promise<RecordNote[]> {
  if (!sidecarBaseUrl || !noteId) return [];
  try {
    const resp = await fetch(
      `${sidecarBaseUrl}/api/cockpit/scope-tests?id=${encodeURIComponent(noteId)}`,
    );
    if (!resp.ok) return [];
    const data = (await resp.json()) as {
      decisions?: Array<{ id: string; title: string; rel: string; status: string }>;
    };
    return (data.decisions ?? []).map((d) => ({ ...d, type: 'adr' }));
  } catch { return []; }
}

// ADRs from the sidecar's own answer, not scraped out of a nav mode
// (ISS-0065). `/api/cockpit/decisions` exists so that "what decisions
// exist" has a source that does not change shape when a nav mode does.
async function fetchDecisions(): Promise<RecordNote[]> {
  if (!sidecarBaseUrl) return [];
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/decisions`);
    if (!resp.ok) return [];
    const data = (await resp.json()) as {
      decisions?: Array<{
        id?: string; title?: string; rel?: string; status?: string; type?: string;
      }>;
    };
    return (data.decisions ?? [])
      .filter((d) => d.id && d.rel)
      .map((d) => ({
        id: String(d.id), title: d.title || String(d.id),
        rel: `/docs/${d.rel}`, status: d.status || '',
        type: (d.type || 'adr').toLowerCase(),
      }));
  } catch { return []; }
}

// The desk's test register in RecordNote shape. Split out from the fetch
// so a caller that already holds the queue payload can use it without a
// second identical GET (ISS-0065 re-review).
function testsFromQueue(data: ReviewQueuePayload | null): RecordNote[] {
  return (data?.registers?.tests ?? [])
    .filter((t) => t.id && t.rel)
    .map((t) => ({
      id: t.id, title: t.title || t.id, rel: `/docs/${t.rel}`,
      status: t.status || '', type: 'test',
    }));
}

// The desk's test register, reused as the record column's source for the
// same reason (ISS-0065): it answers "what do we verify" directly.
async function fetchTestsRegister(): Promise<RecordNote[]> {
  return testsFromQueue(await fetchReviewQueue());
}

// `fetchRecordNotes(mode)` lived here: walk any nav payload, keep every
// item carrying an id, and let the caller filter by type. Deleted with
// ISS-0065 — it had no callers left once the record column and the
// attention rows moved to purpose payloads.
//
// It is the abstraction that caused the bug, not just a casualty of it. A
// helper that turns "a navigation surface" into "a list of notes" invites
// callers to depend on a nav mode's *contents*, which is a UI decision
// and free to change. It did change, three consumers broke, and two of
// them stayed broken through a full review of the phase that broke them.

async function renderOverviewRightPane(
  scopeRel: string | null, data?: StatsPayload,
): Promise<void> {
  // Agent state deliberately stays out of here (TASK-0178): the rail,
  // strip, attention inbox, and ~agents screen already own it.
  rightPaneContent.replaceChildren();
  const scoped = Boolean(scopeRel);

  // Transient cards first — in-flight and attention *here*. They are
  // often empty (the states audit found `doing` clears within a session),
  // which is why the durable record sits underneath rather than beside.
  if (scoped && data) {
    const transient = buildScopedTransientCards(data);
    for (const card of transient) rightPaneContent.appendChild(card);
  }
  void fillRecordColumn(scoped, data);
  if (scoped && sidecarBaseUrl) void fillScopedContext(scopeRel!);
}

// In-flight / attention for the scoped phase — the two questions a
// reviewer asks on arrival, answered before the durable record.
function buildScopedTransientCards(data: StatsPayload): HTMLElement[] {
  const p = data.phases[0];
  if (!p) return [];
  const children: PhaseItem[] = [];
  for (const feature of p.features) children.push(feature, ...feature.children);
  children.push(...p.loose);

  const out: HTMLElement[] = [];
  const inFlight = children.filter((c) => isActiveStatus(c.status));
  if (inFlight.length > 0) {
    const { card, body } = buildRecordCard('In flight');
    for (const item of inFlight.slice(0, 5)) {
      body.appendChild(buildRecordRow(
        item.id || '', item.title, item.rel, item.type, item.status,
      ));
    }
    out.push(card);
  }
  const attention = children.filter((c) => {
    const s = (c.status || '').toLowerCase();
    return s === 'triage' || s === 'blocked' || s === 'failing'
      || (c.type === 'issue' && s === 'open');
  });
  if (attention.length > 0) {
    const { card, body } = buildRecordCard('Attention');
    for (const item of attention.slice(0, 5)) {
      body.appendChild(buildRecordRow(
        item.id || '', item.title, item.rel, item.type, item.status,
      ));
    }
    out.push(card);
  }
  return out;
}

async function fillRecordColumn(
  scoped: boolean, data?: StatsPayload,
): Promise<void> {
  // Purpose payloads, not a nav-mode harvest (ISS-0065). This used to be
  // `fetchRecordNotes('library')` for all three lists, which meant the
  // record column's contents were whatever the Library *nav mode*
  // happened to emit. PHASE-010 reduced that mode to the Docs tree, whose
  // items carry no `id`, so the harvest went 149 → 0 and the Decisions
  // and Verification cards stopped being built — silently, because every
  // card sits behind a `length > 0` guard.
  //
  // Worse, the reduction was justified by this column: "Library's
  // Decisions group duplicates the record column" was true only because
  // the column *was* that group, reshaped. Asking the sidecar what
  // decisions and tests exist cannot fail that way.
  const [adrs, tests] = await Promise.all([
    fetchDecisions(),
    fetchTestsRegister(),
  ]);
  if (!currentRel || !currentRel.startsWith('~overview')) return;

  // On a phase, narrow the record to what reaches *this* phase: ADRs the
  // scope's items reference, and the phase's own acceptance tests. On the
  // project scope everything is in scope by definition.
  const scopeIds = new Set<string>();
  if (scoped && data) {
    const p = data.phases[0];
    if (p) {
      for (const f of p.features) {
        if (f.id) scopeIds.add(f.id);
        for (const c of f.children) if (c.id) scopeIds.add(c.id);
      }
      for (const l of p.loose) if (l.id) scopeIds.add(l.id);
      if (data.scope?.id) scopeIds.add(data.scope.id);
    }
  }
  // Tests reach a scope through their own link fields, which the sidecar
  // resolves — they are never children of a feature in the phase payload,
  // so filtering the library list against `scopeIds` produced an always
  // empty card (independent review, 2026-07-26).
  const scopedAdrs = scoped
    ? await fetchScopeDecisions(data?.scope?.id || '')
    : adrs;
  const scopedTests = scoped
    ? (await fetchScopeTests(data?.scope?.id || '')).map((t) => ({
        id: t.id, title: t.title, rel: t.rel, status: t.status, type: 'test',
      }))
    : tests;

  if (scopedAdrs.length > 0) {
    const accepted = scopedAdrs.filter(
      (a) => ['accepted', 'approved'].includes((a.status || '').toLowerCase()),
    ).length;
    const { card, body } = buildRecordCard(
      'Decisions',
      accepted === scopedAdrs.length ? `${scopedAdrs.length} · all accepted`
        : `${accepted}/${scopedAdrs.length} accepted`,
    );
    const sorted = [...scopedAdrs].sort((a, b) => b.id.localeCompare(a.id));
    for (const adr of sorted.slice(0, 4)) {
      const proposed = (adr.status || '').toLowerCase() === 'proposed';
      body.appendChild(buildRecordRow(
        adr.id, adr.title, adr.rel, 'adr', proposed ? adr.status : undefined,
      ));
    }
    if (sorted.length > 4) {
      body.appendChild(buildRecordDisclosure(
        `${sorted.length - 4} older`, sorted.slice(4), 'adr',
      ));
    }
    rightPaneContent.appendChild(card);
  }

  if (scopedTests.length > 0) {
    const passing = scopedTests.filter(
      (t) => (t.status || '').toLowerCase() === 'passing',
    ).length;
    const { card, body } = buildRecordCard(
      'Verification',
      `${passing}/${scopedTests.length}`,
    );
    const mix: Record<string, number> = {};
    const testBuckets: MixBuckets = { done: passing, backlog: 0, attention: 0 };
    for (const t of scopedTests) {
      const key = (t.status || 'unknown').toLowerCase();
      mix[key] = (mix[key] || 0) + 1;
      if (key === 'passing') continue;
      if (key === 'failing') testBuckets.attention = (testBuckets.attention ?? 0) + 1;
      else testBuckets.backlog = (testBuckets.backlog ?? 0) + 1;
    }
    body.appendChild(buildMixBar(testBuckets, mix));
    // Only the tests that aren't passing are worth naming here; the
    // rest are the denominator.
    const attention = scopedTests.filter(
      (t) => (t.status || '').toLowerCase() !== 'passing',
    );
    for (const t of attention.slice(0, 4)) {
      body.appendChild(buildRecordRow(t.id, t.title, t.rel, 'test', t.status));
    }
    if (attention.length === 0) {
      const p = document.createElement('p');
      p.className = 'ctx-note';
      p.textContent = 'Every recorded test is passing.';
      body.appendChild(p);
    }
    // Waivers and validator state complete the verification picture: a
    // green test count means little if the corpus is failing validation
    // or the coverage was waived rather than earned (FEAT-0018's data).
    const health = document.createElement('p');
    health.className = 'ctx-note';
    body.appendChild(health);
    void fillVerificationHealth(health);
  void fillRuntimeFreshness(health);
    rightPaneContent.appendChild(card);
  }

  // Reviewed — the desk's register, re-homed (TASK-0377). 103 verdicts, and
  // it belongs beside the ADRs and the tests for the reason ADR-0020 gives:
  // a verdict is part of the RECORD, not a queue, and it was on the desk only
  // because the desk was where registers went.
  //
  // Project scope only. A per-phase verdict list would need every note's
  // verdict filtered against the scope's items, which the payload does not
  // carry — and a card that silently showed the project's verdicts on a phase
  // page would be worse than no card.
  if (!scoped) void fillReviewedCard();

  // Unreleased — done-but-unshipped (TASK-0315). Project scope only, for the
  // reason the Reviewed card gives one comment up: the payload carries no
  // per-phase slice, and a card silently showing the project's number on a
  // phase page would be worse than no card.
  if (!scoped) void fillUnreleasedCard();

  // Acceptance debt (TASK-0295) — what is claimed against what is shown.
  if (!scoped) void fillAcceptanceDebtCard();

  // A third card, headed "Library", used to be built here from
  // `library.filter(n => n.type === 'reference')`. It never rendered, and
  // not because of PHASE-010: `fetchRecordNotes` keeps only items with an
  // `id`, and reference notes inline in the Docs tree are emitted with
  // `id: ""` by design (TASK-0036 — filename in the id slot, no project-os
  // ID). Measured against the pre-PHASE-010 payload, the harvest carried
  // design/change/adr/risk/test/workflow/plan items and **zero**
  // references, so the filter was always empty.
  //
  // Removed rather than repaired: design inputs are reachable from the
  // Design mode (FEAT-0043) and references browse in the Docs tree, so
  // the card has no content of its own to show. Found while fixing
  // ISS-0065 — it is the same defect class, aged, and worth recording
  // because a `length > 0` guard hid it for as long as it existed.

  if (data && !scoped) {
    // Corpus size, in the ID vocabulary the notes themselves use.
    const h = data.hero;
    const counts = document.createElement('div');
    counts.className = 'ctx-counters mono';
    const parts = [
      `FEAT ${h.features.total}`, `TASK ${h.tasks.total}`,
      `ISS ${h.issues.total}`, `TST ${h.tests.total}`,
    ];
    if (h.requirements) parts.push(`REQ ${h.requirements.total}`);
    parts.push(`RISK ${h.risks.total}`);
    counts.textContent = parts.join(' · ');
    counts.title = 'Notes of each type in this corpus';
    rightPaneContent.appendChild(counts);
  }

  if (!scoped) {
    const pins = activeId ? loadPinned(activeId) : [];
    if (pins.length > 0) {
      const { card, body } = buildRecordCard('Pinned');
      for (const rel of pins) {
        body.appendChild(buildRecordRow(
          '', rel.split('/').pop() || rel, rel,
        ));
      }
      rightPaneContent.appendChild(card);
    }
  }
}

/** The reviewed register, on the record surfaces (TASK-0377).
 *
 *  **Owed and settled are the server's answer, not this function's.** ISS-0121
 *  was ten rows headed *Changes requested* of which zero were genuinely owed,
 *  because the renderer read `review_verdict` alone and the field is sticky —
 *  a reviewer writes it, the work is done, the note reaches `fixed`, and
 *  nothing clears the stamp. `_verdict_is_owed` compares against the subject's
 *  current status, and moving the register was the moment to make sure the
 *  defect did not move with it.
 *
 *  The inverse case is deliberately preserved and is the one that would be
 *  missed: a verdict written AFTER its subject went terminal is a genuine
 *  re-review request. Filtering on "subject is terminal" alone would hide it,
 *  which is why the predicate lives in one server-side function with its
 *  limitation written down rather than as a renderer-side `filter`.
 */
interface UnreleasedPayload {
  count?: number;
  since?: { id?: string; title?: string; rel?: string; date?: string } | null;
  items?: Array<{ id?: string; title?: string; rel?: string }>;
}

interface DesignVariant { name?: string; html?: string; }

/** `## Variant <name>` fenced html, side by side (TASK-0300 / TASK-0301).
 *
 *  **Convention over machinery**: a variant is a markdown section, so it is
 *  authored with what an agent or a human already has. Rendered into
 *  `srcdoc` iframes so a mockup is a live fragment rather than a picture of
 *  one — and sandboxed **without** `allow-scripts` unless the note opts in,
 *  because a mockup that can run code is a mockup that can reach the cockpit.
 *  The artifact frame allows scripts (DES-0001 carries a theme toggle); a
 *  variant fenced inside a note has not earned that by default.
 */
function buildVariantStrip(
  variants: DesignVariant[], stylesheets: string[], allowScripts: boolean,
  designId = '', chosen = '',
): HTMLElement | null {
  if (!variants.length) return null;
  const strip = document.createElement('div');
  strip.className = 'variant-strip';
  for (const variant of variants) {
    const cell = document.createElement('figure');
    cell.className = 'variant-cell';
    const cap = document.createElement('figcaption');
    cap.className = 'variant-name';
    cap.textContent = variant.name || 'unnamed';
    if (chosen && variant.name === chosen) {
      const mark = document.createElement('span');
      mark.className = 'variant-chosen';
      mark.textContent = 'chosen';
      cap.appendChild(mark);
    } else if (designId) {
      // `Choose` records the shape and NOTHING else (TASK-0302). It does not
      // accept the design: choosing a shape and accepting a design are two
      // judgments, and a click on a thumbnail must not carry an acceptance
      // nobody made. The ADR it offers arrives `proposed`, like any proposal.
      const pick = document.createElement('button');
      pick.type = 'button';
      pick.className = 'variant-choose';
      pick.textContent = 'Choose';
      pick.title = `Record ${variant.name} as the chosen shape — this does not accept the design`;
      pick.addEventListener('click', () => {
        void postJson('/api/notes/choose-variant', {
          id: designId, variant: variant.name, actor: loadDispatchActor(),
        }).then(() => {
          showStatus(`Chose ${variant.name} — the design is not accepted by this.`);
          scheduleHide(3000);
          offerVariantAdr(designId, variant.name ?? '', variants);
          void navigateTo(`~design/${designId}`);
        }).catch((err) => showStatus(`Could not record: ${String(err)}`, 'error'));
      });
      cap.appendChild(pick);
    }
    cell.appendChild(cap);

    const frame = document.createElement('iframe');
    frame.className = 'variant-frame';
    frame.setAttribute('sandbox', allowScripts ? 'allow-scripts' : '');
    frame.setAttribute('referrerpolicy', 'no-referrer');
    // The design-system stylesheets are injected so a mockup wears real
    // tokens. A variant whose note declares none renders unstyled rather
    // than failing — an unstyled shape still answers "which arrangement",
    // which is what a variant is for.
    const links = stylesheets
      .map((href) => `<link rel="stylesheet" href="${sidecarBaseUrl}/design-asset/${href}">`)
      .join('');
    frame.srcdoc =
      `<!doctype html><html><head><meta charset="utf-8">${links}`
      + `<style>body{margin:0;padding:12px;font:13px/1.5 system-ui}</style>`
      + `</head><body>${variant.html ?? ''}</body></html>`;
    cell.appendChild(frame);
    strip.appendChild(cell);
  }
  return strip;
}

/** Offer the ADR that records WHY a shape was chosen (TASK-0302).
 *
 *  Dispatched, never written: the options-considered are prefilled from the
 *  variants, but the reasoning is the part that matters and the cockpit does
 *  not have it. `status: proposed` — nothing is auto-accepted, and the ADR
 *  waits for the actuator row like any other proposal.
 */
function offerVariantAdr(designId: string, chosen: string, variants: DesignVariant[]): void {
  const others = variants.map((v) => v.name).filter((n) => n && n !== chosen);
  showActionStatus(`Chose ${chosen}`, 'record why (ADR)', () => {
    const prompt =
      `Author an ADR for the shape chosen on ${designId}: read docs/designs/, `
      + `record the decision as \`status: proposed\` (never accepted — that is `
      + `the actuator row's), with options considered = ${chosen} (chosen)`
      + (others.length ? `, ${others.join(', ')}` : '')
      + `. The variants are in the design note; the REASONING is not, and it is `
      + `the only part worth writing down.`;
    void dispatchToAgent(designId, '', prompt);
  });
  scheduleHide(8000);
}

interface ShapePayload {
  id?: string;
  available?: boolean;
  commits?: Array<{ sha?: string; date?: string; subject?: string; files?: number }>;
  kinds?: Record<string, number>;
  files?: number;
}

/** CHANGED — the shape of what a note's commits touched (ISS-0096).
 *
 *  History answers *what moved*; this answers *what was touched*. The question
 *  it serves is the acceptance-time one: did this touch what it claims to?
 *  A task promising a CSS fix that rewrote the validator is one line here and
 *  invisible in prose.
 *
 *  Counts, never contents — the cockpit is not an editor and the persona is
 *  not reading implementations.
 */
async function fillChangeShapeCard(noteId: string): Promise<void> {
  if (!sidecarBaseUrl || !noteId) return;
  let data: ShapePayload;
  try {
    const resp = await fetch(
      `${sidecarBaseUrl}/api/notes/shape?id=${encodeURIComponent(noteId)}`,
    );
    if (!resp.ok) return;
    data = (await resp.json()) as ShapePayload;
  } catch { return; }
  if (!data.available || !(data.files ?? 0)) return;   // absent when nothing touched it

  const { card, body } = buildRecordCard('Changed', String(data.files ?? 0));
  const kinds = Object.entries(data.kinds ?? {})
    .sort((a, b) => b[1] - a[1])
    .map(([kind, n]) => `${n} ${kind}`);
  const line = document.createElement('p');
  line.className = 'ctx-note';
  line.textContent = kinds.join(' · ');
  body.appendChild(line);

  for (const commit of (data.commits ?? []).slice(0, 4)) {
    const row = document.createElement('p');
    row.className = 'ctx-note';
    row.textContent = `${commit.sha} · ${commit.date} · ${commit.files} files`;
    row.title = commit.subject ?? '';
    body.appendChild(row);
  }
  const total = (data.commits ?? []).length;
  if (total > 4) {
    const more = document.createElement('p');
    more.className = 'ctx-note';
    more.textContent = `…and ${total - 4} more commits.`;
    body.appendChild(more);
  }
  rightPaneContent.appendChild(card);
}

/** UNRELEASED · N — done features no shipped release names (TASK-0315).
 *
 *  "Done" and "shipped" are different facts and the cockpit knew only one.
 *  This card is the second, and it is deliberately a RECORD card rather than
 *  an obligation: nothing here is owed to anybody. Shipping is a person's
 *  deliberate act (FEAT-0055's line), so this reports a state and offers no
 *  verb — which is also why it carries no badge.
 */
async function fillUnreleasedCard(): Promise<void> {
  if (!sidecarBaseUrl) return;
  let data: UnreleasedPayload;
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/unreleased`);
    if (!resp.ok) return;
    data = (await resp.json()) as UnreleasedPayload;
  } catch { return; }
  // The fetch is async, so the reader may have navigated away while it was in
  // flight — the same guard `fillReviewedCard` carries, for the same reason.
  if (!currentRel || !currentRel.startsWith('~overview')) return;

  const items = data.items ?? [];
  const count = data.count ?? items.length;
  // Absent when zero, per the task: a card reading `UNRELEASED · 0` is a row
  // of furniture asserting nothing. Silence already says everything shipped.
  if (count <= 0) return;

  const { card, body } = buildRecordCard('Unreleased', String(count));
  for (const item of items.slice(0, 8)) {
    body.appendChild(buildRecordRow(item.id ?? '', item.title ?? '', item.rel ?? ''));
  }
  const line = document.createElement('p');
  line.className = 'ctx-note';
  const since = data.since;
  line.textContent = since && since.id
    ? `${count} done since ${since.id}${since.date ? ` (${since.date})` : ''}`
    // No shipped release at all is this project's actual state, and saying
    // "since the last release" would name something that does not exist.
    : `${count} features done, none in a shipped release yet`;
  body.appendChild(line);
  if (items.length > 8) {
    const more = document.createElement('p');
    more.className = 'ctx-note';
    more.textContent = `Showing 8 of ${items.length}.`;
    body.appendChild(more);
  }

  // `Draft release note` (TASK-0316). The one verb on this card, and it is
  // deliberately the weakest one available: it allocates an id and writes a
  // file with `status: draft`. It does not ship, tag, push or deploy —
  // FEAT-0055's line, that a commit is local and reversible while publishing
  // is a person's deliberate act, and REL-0001's own note that pushing a
  // fleet repo can deploy a live website.
  const draft = document.createElement('button');
  draft.type = 'button';
  draft.className = 'review-btn';
  draft.textContent = 'Draft release note';
  draft.title = `Scaffold a REL note listing these ${count} features, as a draft`;
  draft.addEventListener('click', () => {
    const title = window.prompt(
      `Title for the release note?\n\n${count} unshipped feature(s) will be listed. `
      + 'This writes one file as a draft — it ships nothing.',
    );
    if (title === null) return;                     // cancelled, not confirmed
    if (!title.trim()) { showStatus('A release needs a title', 'error'); return; }
    draft.disabled = true;
    void postJson('/api/notes/create', { type: 'release', title: title.trim() })
      .then((res) => {
        const created = (res as { result?: { id?: string; rel?: string } }).result;
        if (!created?.rel) { showStatus('Drafted, but no path came back', 'error'); return; }
        showStatus(`Drafted ${created.id}`);
        scheduleHide(2500);
        void navigateTo(created.rel);
      })
      .catch((err) => {
        draft.disabled = false;
        showStatus(`Could not draft: ${String(err)}`, 'error');
      });
  });
  const foot = document.createElement('div');
  foot.className = 'digest-foot';
  foot.appendChild(draft);
  body.appendChild(foot);

  rightPaneContent.appendChild(card);
}

interface DebtRow { id?: string; title?: string; rel?: string; count?: number; open?: number; }
interface DebtPayload {
  unverified?: DebtRow[];
  unresolved?: DebtRow[];
  evidence_free?: DebtRow[];
  counts?: Record<string, number>;
  total?: number;
}

/** ACCEPTANCE DEBT — three numbers that existed nowhere (TASK-0295).
 *
 *  A record card rather than an obligation badge, deliberately: none of this
 *  is owed to a person on a deadline. It is the gap between what the record
 *  CLAIMS and what it SHOWS, and the point of surfacing it is that the gap
 *  was previously invisible — not that somebody must close it today.
 */
async function fillAcceptanceDebtCard(): Promise<void> {
  if (!sidecarBaseUrl) return;
  let data: DebtPayload;
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/acceptance-debt`);
    if (!resp.ok) return;
    data = (await resp.json()) as DebtPayload;
  } catch { return; }
  if (!currentRel || !currentRel.startsWith('~overview')) return;
  const total = data.total ?? 0;
  if (total <= 0) return;                       // absent at zero, like the rest

  const { card, body } = buildRecordCard('Acceptance debt', String(total));
  const sections: Array<[string, DebtRow[], string]> = [
    ['unverified', data.unverified ?? [], 'no test names them in `verifies:`'],
    ['unresolved', data.unresolved ?? [], 'open criteria on live notes'],
    ['evidence-free ticks', data.evidence_free ?? [], 'ticked with nothing behind it'],
  ];
  for (const [label, rows, why] of sections) {
    if (!rows.length) continue;                 // an empty band says nothing
    const head = document.createElement('p');
    head.className = 'ctx-note';
    head.textContent = `${rows.length} ${label} — ${why}`;
    body.appendChild(head);
    for (const row of rows.slice(0, 4)) {
      body.appendChild(buildRecordRow(row.id ?? '', row.title ?? '', row.rel ?? ''));
    }
    if (rows.length > 4) {
      const more = document.createElement('p');
      more.className = 'ctx-note';
      more.textContent = `…and ${rows.length - 4} more.`;
      body.appendChild(more);
    }
  }
  rightPaneContent.appendChild(card);
}

async function fillReviewedCard(): Promise<void> {
  if (!sidecarBaseUrl) return;
  let items: ReviewRegisterReviewed[] = [];
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/reviewed`);
    if (!resp.ok) return;
    items = ((await resp.json()) as { reviewed?: ReviewRegisterReviewed[] })
      .reviewed ?? [];
  } catch { return; }
  if (!currentRel || !currentRel.startsWith('~overview')) return;
  if (items.length === 0) return;

  const owed = items.filter(isOwedVerdict);
  const { card, body } = buildRecordCard(
    'Reviewed', owed.length ? `${owed.length} owed` : `${items.length}`,
  );
  // Owed first and only — the settled 93 are the denominator, and the card
  // says how many there are rather than listing them. The desk listed both
  // halves because it was a queue; the record column is not.
  for (const item of owed.slice(0, 8)) {
    body.appendChild(buildRecordRow(
      item.id ?? '', item.title ?? '', item.rel ?? '',
    ));
  }
  const line = document.createElement('p');
  line.className = 'ctx-note';
  line.textContent = owed.length
    ? `${items.length} verdicts recorded · ${owed.length} still owed`
    : `${items.length} verdicts recorded, none owed`;
  body.appendChild(line);

  // The one door left to the desk (TASK-0378). Its button and mode are gone,
  // but the review LEDGER is runtime state agents still write — proposals,
  // questions, offered designs — and this repo has an open entry today.
  // Retiring the route with a live request behind it would strand it, which
  // is the trap RETIRED_NAV_MODES exists to prevent, one level up.
  //
  // Where those flows finally land is ISS-0126, which is Edwin's decision and
  // deliberately not guessed at here. Until then the link appears only when
  // there is something behind it, and never otherwise.
  void (async () => {
    const open = await openReviewRequestCount();
    if (open <= 0) return;
    if (!currentRel || !currentRel.startsWith('~overview')) return;
    const link = document.createElement('button');
    link.type = 'button';
    link.className = 'ctx-note ctx-link';
    link.textContent =
      `${open} agent request${open === 1 ? '' : 's'} waiting — open the ledger`;
    link.addEventListener('click', () => void navigateTo('~review'));
    body.appendChild(link);
  })();

  rightPaneContent.appendChild(card);
}

/** Open entries in the review ledger — proposals, questions, offered designs.
 *
 *  Runtime state, not note state (ADR-0007), and untouched by the desk's
 *  retirement: agents still write it and the store still resolves it. */
async function openReviewRequestCount(): Promise<number> {
  if (!sidecarBaseUrl) return 0;
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/review-queue`);
    if (!resp.ok) return 0;
    const q = (await resp.json()) as ReviewQueuePayload;
    return (q.groups ?? [])
      .filter((g) => g.key === 'proposals' || g.key === 'questions')
      .reduce((n, g) => n + (g.items?.length ?? 0), 0);
  } catch { return 0; }
}

/** How many failing notes the card names before it folds.
 *
 *  Four, matching the failing-tests list directly above it: the card is a
 *  240px rail column, and the point is *which* notes, not all of them.
 *  Anything beyond is counted, never dropped silently. */
const VALIDATOR_NAMED_LIMIT = 4;

// Waiver count + validator state for the Verification card. Waivers come
// from the corpus (`verification_waiver` frontmatter, surfaced by the
// context payload's `waived` flag); validator state from FEAT-0018's
// endpoint. Best-effort: an older sidecar simply leaves the line off.
//
// **The card names the notes, not just the count** (acceptance check
// 1.11.1). It used to render `validator: 4 errors` and stop, which agrees
// with a terminal run on the number and tells the reader nothing they can
// act on — and the check asks for *same error count, same notes named*.
// That gap was invisible for as long as the corpus was clean: zero errors
// on both sides looks like agreement. It only showed up when the surface
// was driven against a repo with real errors in it.
//
// The payload has carried `id`, `rel` and `url` per error since FEAT-0018;
// nothing new is needed from the server, which is the other half of why
// this sat unnoticed.
/** One validator error, as FEAT-0018's endpoint has always sent it. */
interface ValidatorError {
  code?: string;
  message?: string;
  id?: string;
  rel?: string;
  url?: string;
}

async function fillVerificationHealth(target: HTMLElement): Promise<void> {
  if (!sidecarBaseUrl) return;
  let validator = '';
  let errorRows: ValidatorError[] = [];
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/validation`);
    if (resp.ok) {
      const v = (await resp.json()) as {
        state?: string; errors?: ValidatorError[]; warnings?: unknown[];
      };
      errorRows = Array.isArray(v.errors) ? v.errors : [];
      const errors = errorRows.length;
      validator = v.state === 'ok' ? 'validator clean'
        : v.state === 'unavailable' ? 'validator unavailable'
        : `validator: ${errors} error${errors === 1 ? '' : 's'}`;
    }
  } catch { /* best-effort */ }
  if (!currentRel || !currentRel.startsWith('~overview')) return;
  target.textContent = validator;
  const failing = validator.startsWith('validator:');
  target.classList.toggle('is-warn', failing);

  // Rows go AFTER the line, as siblings, so the summary keeps its own
  // shape and an older sidecar's payload simply produces none.
  target.parentElement?.querySelectorAll('.ctx-validator-row')
    .forEach((n) => n.remove());
  if (!failing || !errorRows.length) return;

  const named = errorRows.slice(0, VALIDATOR_NAMED_LIMIT);
  for (const err of named) {
    // The validator's message opens with the note's own id, which the id
    // column is already showing. Saying it twice in a 240px rail spends the
    // width that would otherwise carry what is actually wrong.
    let msg = err.message || err.code || '';
    if (err.id && msg.startsWith(err.id)) {
      msg = msg.slice(err.id.length).replace(/^[\s:—-]+/, '') || msg;
    }
    const row = buildRecordRow(err.id || '', msg, err.rel, 'issue');
    row.classList.add('ctx-validator-row');
    if (err.code) row.title = `[${err.code}] ${err.message || ''}`.trim();
    target.parentElement?.appendChild(row);
  }
  if (errorRows.length > named.length) {
    const more = document.createElement('p');
    more.className = 'ctx-note ctx-validator-row';
    // Never a silent truncation: the reader is told the list is short.
    more.textContent = `+${errorRows.length - named.length} more`;
    target.parentElement?.appendChild(more);
  }
}

/** Say so when the running code is older than the code on disk (ISS-0140).
 *
 *  Two long-running processes, the same trap. A sidecar never re-imports;
 *  a renderer bundle is read once at window creation. Neither notices a
 *  rebuild, and nothing on screen said so — which cost a false bug report
 *  on 2026-08-10 (a stale sidecar rendering the Tests view as Features)
 *  and a false observation on 2026-08-11 (a shell running 1 day 23 hours,
 *  showing agent chips for notes nobody had touched).
 *
 *  **Reports, never reloads.** Reloading a window under someone mid-session
 *  is worse than the staleness. This is an obligation the reader
 *  discharges, in the voice the surface already uses for `validator: N`.
 *
 *  The window's own age is `performance.timeOrigin` — when *this* document
 *  began, which is when the bundle was read. Comparing it to the newest
 *  asset mtime is the whole check.
 */
async function fillRuntimeFreshness(target: HTMLElement): Promise<void> {
  if (!sidecarBaseUrl) return;
  let stale: string[] = [];
  try {
    const resp = await fetch(`${sidecarBaseUrl}/api/cockpit/runtime`);
    if (!resp.ok) return;                       // older sidecar: no line
    const r = (await resp.json()) as {
      sidecar_stale?: boolean; assets_newest?: number;
    };
    if (r.sidecar_stale) stale.push('sidecar');
    const built = (r.assets_newest ?? 0) * 1000;
    if (built && built > performance.timeOrigin) stale.push('window');
  } catch { return; }
  if (!currentRel || !currentRel.startsWith('~overview')) return;
  target.parentElement?.querySelectorAll('.ctx-stale-row').forEach((n) => n.remove());
  if (!stale.length) return;

  const p = document.createElement('p');
  p.className = 'ctx-note is-warn ctx-stale-row';
  // Names WHICH one, because the two need different actions: a sidecar
  // restarts itself on reopen, a window needs relaunching.
  p.textContent = stale.length === 2
    ? 'sidecar and window are older than the code — restart to trust this'
    : `${stale[0]} is older than the code — restart to trust this`;
  target.parentElement?.appendChild(p);
}

function buildRecordDisclosure(
  label: string, notes: RecordNote[], type: string,
): HTMLElement {
  const wrap = document.createElement('div');
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'ctx-disclosure';
  const chev = document.createElement('span');
  chev.className = 'ov-chev';
  const text = document.createElement('span');
  text.textContent = label;
  btn.append(chev, text);
  const body = document.createElement('div');
  body.hidden = true;
  for (const note of notes) {
    body.appendChild(buildRecordRow(note.id, note.title, note.rel, type));
  }
  btn.addEventListener('click', () => {
    body.hidden = !body.hidden;
    btn.classList.toggle('is-open', !body.hidden);
  });
  wrap.append(btn, body);
  return wrap;
}

// Phase scope keeps its link graph, demoted to disclosures so it informs
// without dominating (FEAT-0023's pane contract is preserved, not dropped).
async function fillScopedContext(scopeRel: string): Promise<void> {
  try {
    const resp = await fetch(
      `${sidecarBaseUrl}/api/cockpit/context?this=${encodeURIComponent(scopeRel)}`,
    );
    if (!resp.ok) return;
    const data = (await resp.json()) as ContextPayload;
    if (!currentRel || !currentRel.startsWith('~overview/')) return;
    const wrap = document.createElement('div');
    wrap.className = 'ctx-graph';
    const linked = renderContextSection('Linked', data.linked || []);
    const back = renderContextSection('Backlinks', data.backlinks || []);
    for (const [label, node] of [['Linked', linked], ['Backlinks', back]] as const) {
      if (!node) continue;
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'ctx-disclosure';
      const chev = document.createElement('span');
      chev.className = 'ov-chev';
      const count = node.querySelectorAll('.ctx-row, li').length;
      const text = document.createElement('span');
      text.textContent = count ? `${label} · ${count}` : label;
      btn.append(chev, text);
      node.hidden = true;
      btn.addEventListener('click', () => {
        node.hidden = !node.hidden;
        btn.classList.toggle('is-open', !node.hidden);
      });
      wrap.append(btn, node);
    }
    if (wrap.childElementCount > 0) rightPaneContent.appendChild(wrap);
  } catch { /* context is best-effort */ }
}

// ----- Lifecycle: in-place refresh + live-duration tick (TASK-0130) -----

async function refreshOverviewInPlace(): Promise<void> {
  if (!currentRel || !currentRel.startsWith('~overview')) return;
  const scroll = docView.scrollTop;
  const ok = await renderOverviewPage(overviewScope);
  if (ok) docView.scrollTop = scroll;
}

function updateLiveDurations(): void {
  const session = lastAgentSnap?.session;
  document.querySelectorAll<HTMLElement>('[data-dur-start]').forEach((el) => {
    const start = el.dataset.durStart;
    if (!start) return;
    const dur = fmtDuration(start, null);
    if (!dur) return;
    // Session feed rows carry "dur · $cost" — preserve the cost part.
    const cost = el.textContent?.includes('$')
      ? el.textContent.slice(el.textContent.indexOf('$')) : '';
    el.textContent = cost ? `${dur} · ${cost}` : dur;
  });
}

window.setInterval(updateLiveDurations, 30_000);

// ----- Temperature tick (FEAT-0081 / TASK-0346, ISS-0105) --------------
//
// The rail and the NEEDS YOU list are painted from `agentStates`, which
// is fed by SSE. Cold is the one transition with no event behind it —
// the premise is a session where NOTHING is happening — so without a
// clock a dot would sit amber forever and the list would never shed the
// entry. That is the defect ISS-0105 records, and this is the part that
// fixes it.
//
// Compares against what is PAINTED, not against a remembered decision.
//
// An earlier version cached the last temperature per workspace and
// repainted only on a change. That is wrong, and wrong in exactly the
// case this feature exists for: the DOM is also repainted by inbound SSE
// events, so after cold → warm (event) → cold (time), the cache still
// read `cold`, the tick saw no change, and the dot stayed amber forever.
// Reading the DOM makes the tick self-healing — it cannot disagree with
// the screen about what is on the screen.
function tickTemperatures(): void {
  const now = Date.now();
  let listStale = false;
  for (const [wsId, state] of agentStates) {
    const li = listEl.querySelector<HTMLLIElement>(`li.ws-square[data-id="${CSS.escape(wsId)}"]`);
    const ws = workspaces.find((w) => w.id === wsId);
    if (!li || !ws) continue;
    // ISS-0115: this used to restate railKey's rule inline, so the cold
    // decision had two implementations and only one was tested. Ask the
    // tested one what it wants painted, and compare that to what is.
    const painted = li.classList.contains('state-idle');
    const shouldBeIdle = railKey(state, now) === 'idle';
    if (shouldBeIdle !== painted) {
      applyAgentStateToSquare(li, ws);
      listStale = true;
    }
  }
  // The panel is compared the same way: the ids it should be showing
  // against the ids it is showing.
  const want = attentionEntries().map((e) => e.workspaceId).join(',');
  const have = Array.from(
    attentionPanel.querySelectorAll<HTMLElement>('.ws-attention-row'),
  ).map((r) => r.dataset.wsId || '').join(',');
  if (listStale || want !== have) refreshAttention();
}

window.setInterval(tickTemperatures, 30_000);


// ----------------------------------------------------------------------
// Settings popover (FEAT-0027 / TASK-0142)
// ----------------------------------------------------------------------

const settingsBtn = $<HTMLButtonElement>('#settings-toggle');
const settingsPopover = $<HTMLDivElement>('#settings-popover');
const settingExternalHook = $<HTMLInputElement>('#setting-external-hook');
const settingsStatus = $<HTMLParagraphElement>('#settings-status');

function settingsFeedback(text: string, isError = false): void {
  settingsStatus.textContent = text;
  settingsStatus.hidden = !text;
  settingsStatus.classList.toggle('is-error', isError);
}

async function openSettingsPopover(): Promise<void> {
  try {
    const s = await cockpitApi.settings.get();
    settingExternalHook.checked = s.externalHook === true;
  } catch { /* leave unchecked */ }
  settingsFeedback('');
  const rect = settingsBtn.getBoundingClientRect();
  settingsPopover.style.left = `${rect.right + 8}px`;
  settingsPopover.style.bottom = `${Math.max(8, window.innerHeight - rect.bottom)}px`;
  settingsPopover.hidden = false;
  settingsBtn.setAttribute('aria-expanded', 'true');
}

function closeSettingsPopover(): void {
  settingsPopover.hidden = true;
  settingsBtn.setAttribute('aria-expanded', 'false');
}

settingsBtn.addEventListener('click', () => {
  if (settingsPopover.hidden) void openSettingsPopover();
  else closeSettingsPopover();
});

document.addEventListener('click', (e) => {
  if (settingsPopover.hidden) return;
  const target = e.target as HTMLElement | null;
  if (target && !settingsPopover.contains(target) && !settingsBtn.contains(target)) {
    closeSettingsPopover();
  }
});

settingExternalHook.addEventListener('change', () => {
  const want = settingExternalHook.checked;
  settingExternalHook.disabled = true;
  void cockpitApi.settings.set({ externalHook: want }).then((res) => {
    settingExternalHook.disabled = false;
    if (!res.ok) {
      settingExternalHook.checked = res.settings.externalHook;
      settingsFeedback(res.error || 'Failed to update setting', true);
      return;
    }
    settingsFeedback(want
      ? 'Hook installed in ~/.claude/settings.json — new Claude sessions will signal state.'
      : 'Hook removed from ~/.claude/settings.json.');
  });
});


// ----------------------------------------------------------------------
// The acceptance runner (FEAT-0063 / TASK-0288, DES-0006)
// ----------------------------------------------------------------------

interface AcceptanceCriterion {
  index?: number;
  text?: string;
  raw?: string;
  state?: string;
  evidence?: string;
  witness?: string;
  witness_date?: string;
}

interface AcceptanceRequirement {
  id?: string;
  title?: string;
  rel?: string;
  status?: string;
  declared?: number;
  criteria?: AcceptanceCriterion[];
}

interface AcceptancePayload {
  id?: string;
  title?: string;
  rel?: string;
  requirements?: AcceptanceRequirement[];
  totals?: Record<string, number>;
  total?: number;
  nothing_to_accept?: boolean;
  error?: string;
}

/** One criterion, flattened with the requirement that owns it. */
interface RunStep { req: string; reqRel: string; criterion: AcceptanceCriterion; }

/** A run in progress. Held in memory only — an abandoned run leaves the
 *  record exactly as it found it, which is what makes `esc` safe. */
interface RunState {
  featureId: string;
  steps: RunStep[];
  at: number;
  passed: number;
  failed: number;
  skipped: number;
  issues: string[];
}

let activeRun: RunState | null = null;

/** A capture taken but not yet spent. Held until the next verdict, so the
 *  picture is filed as evidence FOR a criterion rather than as a loose file —
 *  DES-0006: "attach a capture to whatever the next verdict is". */
let pendingCapture: string | null = null;

async function captureForVerdict(): Promise<void> {
  if (!activeId) return;
  try {
    const shot = await cockpitApi.app.captureScreenshot(activeId);
    if (!shot?.ok) {
      if (!shot?.cancelled) showStatus(`Capture failed: ${shot?.error ?? 'unknown'}`, 'error');
      return;
    }
    // The bridge writes to `inbox/` and hands back a name. The runner does not
    // want it there — `inbox/` is gitignored staging — so the attach endpoint
    // re-files it under `docs/attachments/` when the verdict lands.
    pendingCapture = shot.name ?? null;
    showStatus('Capture attached to the next verdict.');
    scheduleHide(2000);
    void renderAcceptanceRun(activeRun?.featureId ?? '');
  } catch (err) {
    showStatus(`Capture failed: ${String(err)}`, 'error');
  }
}

/** `accepted in cockpit run, user:edwin, 2026-08-03` — REQ-0028's witness,
 *  by construction. Composed here and never typed: the requirement's first
 *  criterion is that it is "machine-composed — never typed, never omitted". */
function acceptanceEvidence(): string {
  const who = loadDispatchActor();
  const when = new Date().toISOString().slice(0, 10);
  return `accepted in cockpit run, ${who}, ${when}`;
}

function loadDispatchActor(): string {
  try { return localStorage.getItem('cockpit:actor') || 'user:edwin'; }
  catch { return 'user:edwin'; }
}

async function renderAcceptanceRun(featureId: string): Promise<boolean> {
  if (!sidecarBaseUrl) return false;
  let data: AcceptancePayload;
  try {
    const resp = await fetch(
      `${sidecarBaseUrl}/api/notes/acceptance?id=${encodeURIComponent(featureId)}`,
    );
    data = (await resp.json()) as AcceptancePayload;
  } catch (err) {
    showStatus(`Could not load criteria: ${String(err)}`, 'error');
    return false;
  }
  if (data.error) { showStatus(data.error, 'error'); return false; }

  // Resume rather than restart when the run is already open on this feature —
  // reselecting the route is not a request to lose your place, the same rule
  // the Intent mode follows for an open artifact.
  if (!activeRun || activeRun.featureId !== featureId) {
    const steps: RunStep[] = [];
    for (const req of data.requirements ?? []) {
      for (const criterion of req.criteria ?? []) {
        // Settled criteria are shown in the summary but not walked: re-asking
        // about something already ticked with a witness invites re-ticking it
        // without re-trying it.
        if (criterion.state === 'open') {
          steps.push({ req: req.id ?? '', reqRel: req.rel ?? '', criterion });
        }
      }
    }
    activeRun = {
      featureId, steps, at: 0, passed: 0, failed: 0, skipped: 0, issues: [],
    };
  }
  paintAcceptanceRun(data);
  return true;
}

function paintAcceptanceRun(data: AcceptancePayload): void {
  const run = activeRun;
  if (!run) return;
  const wrap = document.createElement('div');
  wrap.className = 'accept-run';

  const head = document.createElement('div');
  head.className = 'accept-head';
  const title = document.createElement('span');
  title.textContent = `${data.id} · Acceptance run`;
  const progress = document.createElement('span');
  progress.className = 'accept-progress';
  const total = run.steps.length;
  progress.textContent = total ? `${Math.min(run.at + 1, total)} of ${total}` : '—';
  head.append(title, progress);
  wrap.appendChild(head);

  if (data.nothing_to_accept) {
    const none = document.createElement('p');
    none.className = 'accept-empty';
    none.textContent =
      'No acceptance criteria on this feature — a criterion arrives when a '
      + 'requirement names it in `acceptance:`.';
    wrap.appendChild(none);
    docView.replaceChildren(wrap);
    docView.hidden = false;
    placeholder.hidden = true;
    return;
  }

  if (run.at >= total) {
    wrap.appendChild(buildRunSummary(run, data));
    docView.replaceChildren(wrap);
    docView.hidden = false;
    placeholder.hidden = true;
    return;
  }

  const step = run.steps[run.at];
  const where = document.createElement('div');
  where.className = 'accept-where';
  where.textContent = `${step.req} · criterion ${(step.criterion.index ?? 0) + 1}`;
  wrap.appendChild(where);

  const text = document.createElement('blockquote');
  text.className = 'accept-criterion';
  text.textContent = step.criterion.text || '(no text)';
  wrap.appendChild(text);

  const actions = document.createElement('div');
  actions.className = 'accept-actions';
  actions.append(
    acceptButton('Pass', 'is-primary', () => void verdict('pass')),
    acceptButton('Fail…', '', () => void verdict('fail')),
    acceptButton('Skip / reconcile…', '', () => void verdict('skip')),
    // 📷 — capture at the moment of the verdict (TASK-0298, DES-0006). It
    // attaches to whatever the NEXT verdict is rather than writing on its own,
    // so a picture is always evidence FOR something rather than a loose file.
    acceptButton(pendingCapture ? '📷 attached' : '📷', '', () => void captureForVerdict()),
  );
  wrap.appendChild(actions);

  const hint = document.createElement('p');
  hint.className = 'accept-hint';
  hint.textContent = 'enter passes · f fails · s reconciles · esc leaves the run resumable';
  wrap.appendChild(hint);

  docView.replaceChildren(wrap);
  docView.hidden = false;
  placeholder.hidden = true;
}

function acceptButton(label: string, cls: string, onClick: () => void): HTMLButtonElement {
  const b = document.createElement('button');
  b.type = 'button';
  b.className = `review-btn ${cls}`.trim();
  b.textContent = label;
  b.addEventListener('click', onClick);
  return b;
}

function buildRunSummary(run: RunState, data: AcceptancePayload): HTMLElement {
  const box = document.createElement('div');
  box.className = 'accept-summary';
  const line = document.createElement('p');
  line.textContent =
    `${run.passed} passed · ${run.failed} failed`
    + (run.issues.length ? ` → ${run.issues.join(', ')}` : '')
    + ` · ${run.skipped} skipped`;
  box.appendChild(line);

  const note = document.createElement('p');
  note.className = 'accept-hint';
  note.textContent = run.failed
    ? 'Recording this run stamps the feature only if nothing failed — a fail is a datum, not an acceptance.'
    : 'Recording this run stamps the feature with your name and today.';
  box.appendChild(note);

  const foot = document.createElement('div');
  foot.className = 'digest-foot';
  foot.appendChild(acceptButton('Record run', 'is-primary', () => {
    void postJson('/api/notes/acceptance-run', {
      id: run.featureId,
      passed: run.passed,
      failed: run.failed,
      skipped: run.skipped,
      issues: run.issues,
      // A run with a failure is COMPLETE as a walk but must not stamp
      // acceptance — DES-0006: "a fail is a datum, not an abort", and
      // REQ-0028: accepted_by only on a run where everything resolved.
      complete: run.failed === 0,
      actor: loadDispatchActor(),
    }).then(() => {
      showStatus(`Run recorded on ${run.featureId}`);
      scheduleHide(2500);
      activeRun = null;
      void navigateTo(data.rel || '');
    }).catch((err) => showStatus(`Could not record: ${String(err)}`, 'error'));
  }));
  foot.appendChild(acceptButton('Discard', '', () => {
    activeRun = null;
    showStatus('Run discarded — nothing was written for the unrecorded steps.');
    scheduleHide(2500);
    void navigateTo(data.rel || '');
  }));
  box.appendChild(foot);
  return box;
}

/** Apply one verdict, then advance. Each verdict writes IMMEDIATELY through
 *  the guarded verbs, so an abandoned run keeps the work already done rather
 *  than discarding it — the record is the ledger, not this object. */
async function verdict(kind: 'pass' | 'fail' | 'skip'): Promise<void> {
  const run = activeRun;
  if (!run || run.at >= run.steps.length) return;
  const step = run.steps[run.at];
  const criterion = step.criterion.text || '';
  // Spend any pending capture on THIS verdict, before it is recorded, so the
  // evidence string can cite the picture (TASK-0298). Filing it first also
  // means a failed attach does not silently drop the only proof.
  let shot = '';
  if (pendingCapture) {
    try {
      const filed = await postJson('/api/notes/attach', {
        id: step.req, inbox_name: pendingCapture,
        caption: criterion.slice(0, 80), actor: loadDispatchActor(),
      });
      shot = String((filed.result as { markdown?: string } | undefined)?.markdown ?? '');
      pendingCapture = null;
    } catch (err) {
      showStatus(`Could not file the capture: ${String(err)}`, 'error');
      return;                       // the verdict waits; the picture is not lost
    }
  }
  try {
    if (kind === 'pass') {
      await postJson('/api/notes/tick', {
        id: step.req, criterion,
        evidence: acceptanceEvidence() + (shot ? ` ${shot}` : ''),
        actor: loadDispatchActor(),
      });
      run.passed += 1;
    } else if (kind === 'skip') {
      const reason = window.prompt(
        `Why is this criterion reconciled rather than met?\n\n${criterion}`,
      );
      if (reason === null) return;                    // cancelled, not skipped
      if (!reason.trim()) { showStatus('A reconcile needs a reason', 'error'); return; }
      await postJson('/api/notes/tick', {
        id: step.req, criterion, reason: reason.trim(), actor: loadDispatchActor(),
      });
      run.skipped += 1;
    } else {
      const what = window.prompt(
        `What failed?\n\n${criterion}\n\n(files an issue, pre-linked; the run continues)`,
      );
      if (what === null) return;
      const created = await postJson('/api/notes/create', {
        type: 'issue',
        title: `Acceptance failed: ${criterion}`.slice(0, 120),
        body: (what.trim() || 'Failed during an acceptance run.')
          + `\n\nFound accepting ${run.featureId}, criterion of ${step.req}.`
          + (shot ? `\n\n${shot}` : ''),
        related: [`[[${run.featureId}]]`, `[[${step.req}]]`],
        actor: loadDispatchActor(),
      });
      const issue = (created.result as { id?: string } | undefined)?.id;
      if (issue) run.issues.push(issue);
      run.failed += 1;
    }
  } catch (err) {
    showStatus(`Could not record: ${String(err)}`, 'error');
    return;
  }
  run.at += 1;
  void renderAcceptanceRun(run.featureId);
}

document.addEventListener('keydown', (ev) => {
  if (!activeRun || !currentRel || !currentRel.startsWith('~accept/')) return;
  if (ev.metaKey || ev.ctrlKey || ev.altKey) return;
  const target = ev.target as HTMLElement | null;
  if (target && /^(INPUT|TEXTAREA)$/.test(target.tagName)) return;
  if (ev.key === 'Enter') { ev.preventDefault(); void verdict('pass'); }
  else if (ev.key === 'f') { ev.preventDefault(); void verdict('fail'); }
  else if (ev.key === 's') { ev.preventDefault(); void verdict('skip'); }
  else if (ev.key === 'Escape') {
    // Resumable, not discarded: the steps already recorded are in the notes,
    // and `activeRun` survives so returning to the route continues the walk.
    ev.preventDefault();
    showStatus('Run paused — reopen it to continue where you left off.');
    scheduleHide(2500);
  }
});

// ----------------------------------------------------------------------
// The measure view (FEAT-0068 / TASK-0303-0305)
// ----------------------------------------------------------------------
//
// **The cockpit measures itself.** That is TASK-0304's path and it is the one
// that actually works: variant frames are sandboxed with an opaque origin, so
// a parent cannot reach into them by construction — the same property that
// makes them safe makes them unmeasurable from outside. Same-origin artefact
// frames remain measurable and go through the identical probe.
//
// Scoped to self and artefacts, per the feature's out-of-scope line. Pointing
// this at an external app is its own phase with its own risk scan.

// `measure.js` is loaded as a plain script before this one, exactly as
// `completed-work.js` is, so its functions are already in scope. No `declare`
// block: TypeScript sees the sibling's own declarations, and re-declaring them
// here collides with them (caught at build).

interface MeasureMetrics { label: string; selector: string; values: Record<string, string>; }
interface MeasureRow { group: string; property: string; a: string; b: string; differs: boolean; }

let measurePicking: 'A' | 'B' | null = null;
let measureA: MeasureMetrics | null = null;
let measureB: MeasureMetrics | null = null;

/** Arm the picker. The next click anywhere in the app harvests that element.
 *
 *  A click rather than a hover-commit: hovering commits by accident, and the
 *  thing being measured is usually under the pointer on the way to somewhere
 *  else. Escape disarms.
 */
function armMeasure(slot: 'A' | 'B'): void {
  measurePicking = slot;
  document.body.classList.add('is-measuring');
  showStatus(`Click the element for pane ${slot} — esc cancels.`);
}

function disarmMeasure(): void {
  measurePicking = null;
  document.body.classList.remove('is-measuring');
}

document.addEventListener('click', (ev) => {
  if (!measurePicking) return;
  const target = ev.target as Element | null;
  if (!target || !(target instanceof Element)) return;
  // The picker's own chrome is not a measurement subject.
  if (target.closest('.measure-panel')) return;
  ev.preventDefault();
  ev.stopPropagation();
  const slot = measurePicking;
  const metrics = harvest(target, `pane ${slot}`);
  if (slot === 'A') measureA = metrics; else measureB = metrics;
  disarmMeasure();
  renderMeasurePanel();
}, true);

document.addEventListener('keydown', (ev) => {
  if (measurePicking && ev.key === 'Escape') {
    ev.preventDefault();
    disarmMeasure();
    showStatus('Measure cancelled.');
    scheduleHide(1500);
  }
});

function renderMeasurePanel(): void {
  document.querySelector('.measure-panel')?.remove();
  const panel = document.createElement('section');
  panel.className = 'measure-panel';

  const head = document.createElement('div');
  head.className = 'measure-head';
  head.textContent = 'Measure';
  const close = document.createElement('button');
  close.type = 'button';
  close.className = 'measure-close';
  close.textContent = '✕';
  close.title = 'Close the measure panel';
  close.addEventListener('click', () => {
    measureA = measureB = null;
    disarmMeasure();
    document.querySelector('.measure-panel')?.remove();
  });
  head.appendChild(close);
  panel.appendChild(head);

  const picks = document.createElement('div');
  picks.className = 'measure-picks';
  for (const slot of ['A', 'B'] as const) {
    const held = slot === 'A' ? measureA : measureB;
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'review-btn';
    btn.textContent = held ? `${slot}: ${held.selector}` : `Pick ${slot}…`;
    btn.addEventListener('click', () => armMeasure(slot));
    picks.appendChild(btn);
  }
  panel.appendChild(picks);

  if (measureA && measureB) {
    const rows = diff(measureA, measureB);
    const table = document.createElement('table');
    table.className = 'measure-table';
    let lastGroup = '';
    for (const row of rows) {
      if (row.group !== lastGroup) {
        lastGroup = row.group;
        const gr = table.insertRow();
        const gc = gr.insertCell();
        gc.colSpan = 3;
        gc.className = 'measure-group';
        gc.textContent = row.group;
      }
      const tr = table.insertRow();
      if (row.differs) tr.className = 'differs';
      tr.insertCell().textContent = row.property;
      tr.insertCell().textContent = row.a || '—';
      tr.insertCell().textContent = row.b || '—';
    }
    panel.appendChild(table);

    const foot = document.createElement('div');
    foot.className = 'digest-foot';
    const copy = document.createElement('button');
    copy.type = 'button';
    copy.className = 'review-btn is-primary';
    copy.textContent = 'Copy differences as markdown';
    copy.addEventListener('click', () => {
      void copyText(toMarkdown(measureA!, measureB!, rows), 'Copied the table');
    });
    foot.appendChild(copy);
    panel.appendChild(foot);
  } else {
    const hint = document.createElement('p');
    hint.className = 'measure-hint';
    hint.textContent =
      'Pick two elements to compare — the cockpit measures its own surfaces and '
      + 'same-origin artefacts.';
    panel.appendChild(hint);
  }
  document.body.appendChild(panel);
}

// ----------------------------------------------------------------------
// Annotations on a design (FEAT-0069 / TASK-0307)
// ----------------------------------------------------------------------
//
// **Selection, not a pixel pin.** `append_design_comment` learned this once:
// *"the anchor is a region id, never a coordinate. Pixel pins die on the next
// revision, and the founding artifact went through six in one session."* A
// quoted selection is the richer version of that lesson — it survives a
// reflow, and when it does not survive an edit it can SAY SO rather than
// float to whatever is now at those coordinates.
//
// esc costs nothing: the selection is read at click time, so dismissing the
// prompt leaves the record untouched.

/** Offer `Annotate` when text is selected inside a design note. */
function annotationFromSelection(designId: string): void {
  const sel = window.getSelection();
  const quote = (sel?.toString() ?? '').trim();
  if (!quote) {
    showStatus('Select the text the comment is about first.', 'error');
    return;
  }
  const text = window.prompt(`Comment on:\n\n“${quote.slice(0, 160)}”`);
  if (text === null) return;                       // esc costs nothing
  if (!text.trim()) { showStatus('An annotation needs a comment', 'error'); return; }

  // The variant it sits in, when the selection is inside one — read from the
  // nearest variant cell rather than guessed from position.
  const node = sel?.anchorNode as Element | null;
  const cell = (node?.nodeType === 1 ? node : node?.parentElement)?.closest('.variant-cell');
  const variant = cell?.querySelector('.variant-name')?.firstChild?.textContent?.trim() ?? '';

  void postJson('/api/cockpit/review-request', {
    kind: 'annotation',
    title: text.trim().slice(0, 120),
    body: text.trim(),
    items: [designId],
    subject: designId,
    // Quote first: it is what lets a moved anchor be re-found and a lost one
    // admit it. No coordinates — the store's allow-list would drop them anyway.
    anchor: { quote: quote.slice(0, 300), variant },
  }).then(() => {
    showStatus('Annotation recorded against the selection.');
    scheduleHide(2500);
  }).catch((err) => showStatus(`Could not record: ${String(err)}`, 'error'));
}
