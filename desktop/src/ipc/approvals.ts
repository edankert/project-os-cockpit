// Permission prompts answered from the cockpit (FEAT-0159 / TASK-0666).
//
// A Claude session's plugin offers a permission ask to its workspace's
// sidecar and waits a few seconds for a click. The Needs you panel has to
// show that ask within those seconds whichever project is on screen, so the
// main process keeps one event stream per running sidecar, not only the
// active one, and forwards each `cockpit:approval` to every window.
//
// The answer goes through here too. The renderer asks for "approve this";
// the main process posts it with the sidecar's secret and the person's own
// account as the actor. The renderer never holds the secret and never
// chooses the actor, so a script in a framed page cannot answer for anyone.

import { BrowserWindow, ipcMain } from 'electron';
import * as http from 'node:http';
import * as os from 'node:os';

import { sidecarSecretFor, sidecarUrlFor } from './sidecar';

/** What the panel draws for one approval; the sidecar's record, trimmed. */
export interface ApprovalView {
  approval_id: string;
  session_id: string;
  agent?: string;
  agent_id?: string;
  tool: string;
  prompt: string;
  status: string;
  ts?: string;
  wait_ms?: number;
}

/** The statuses a card is drawn for, as `approvals.LIVE` in the sidecar. */
const LIVE = new Set(['open', 'handed-to-terminal']);

/** How long to wait before reconnecting a stream that dropped. */
const RECONNECT_MS = 2000;

const live = new Map<string, Map<string, ApprovalView>>();
const streams = new Map<string, { url: string; request: http.ClientRequest | null; timer: NodeJS.Timeout | null }>();

/** Every live approval, by workspace. */
export function liveApprovals(): Record<string, ApprovalView[]> {
  const out: Record<string, ApprovalView[]> = {};
  for (const [ws, byId] of live) {
    if (byId.size) out[ws] = [...byId.values()];
  }
  return out;
}

function broadcast(workspaceId: string): void {
  const approvals = [...(live.get(workspaceId)?.values() ?? [])];
  for (const w of BrowserWindow.getAllWindows()) {
    if (!w.isDestroyed()) w.webContents.send('approval:changed', { workspaceId, approvals });
  }
}

/** Apply one record from the sidecar: keep it while live, drop it otherwise. */
export function applyApproval(workspaceId: string, record: unknown): boolean {
  const r = record as Partial<ApprovalView> | null;
  if (!r || typeof r.approval_id !== 'string') return false;
  let byId = live.get(workspaceId);
  if (!byId) { byId = new Map(); live.set(workspaceId, byId); }
  if (typeof r.status === 'string' && LIVE.has(r.status)) byId.set(r.approval_id, r as ApprovalView);
  else if (!byId.delete(r.approval_id)) return false;
  return true;
}

function getJson(url: string): Promise<unknown> {
  return new Promise((resolve) => {
    const req = http.get(url, { timeout: 2000 }, (res) => {
      let text = '';
      res.setEncoding('utf-8');
      res.on('data', (c: string) => { text += c; });
      res.on('end', () => { try { resolve(JSON.parse(text)); } catch { resolve(null); } });
    });
    req.on('error', () => resolve(null));
    req.on('timeout', () => { req.destroy(); resolve(null); });
  });
}

/** Read the sidecar's live approvals afresh: on connect and on reconnect,
 *  so nothing that changed while the stream was down is missed. */
async function seed(workspaceId: string, url: string): Promise<void> {
  const body = await getJson(`${url}/api/cockpit/approvals`) as { approvals?: unknown[] } | null;
  if (!body || !Array.isArray(body.approvals)) return;
  const byId = new Map<string, ApprovalView>();
  for (const r of body.approvals) {
    const a = r as Partial<ApprovalView>;
    if (typeof a.approval_id === 'string' && typeof a.status === 'string' && LIVE.has(a.status)) {
      byId.set(a.approval_id, a as ApprovalView);
    }
  }
  live.set(workspaceId, byId);
  broadcast(workspaceId);
}

function connect(workspaceId: string): void {
  const s = streams.get(workspaceId);
  if (!s) return;
  const u = new URL(s.url);
  const req = http.get({
    host: u.hostname, port: Number(u.port), path: '/_events',
    headers: { Accept: 'text/event-stream' },
  }, (res) => {
    if (res.statusCode !== 200) { res.resume(); return; }
    void seed(workspaceId, s.url);
    res.setEncoding('utf-8');
    let buffer = '';
    let event = '';
    let data = '';
    res.on('data', (chunk: string) => {
      buffer += chunk;
      let nl: number;
      while ((nl = buffer.indexOf('\n')) >= 0) {
        const line = buffer.slice(0, nl);
        buffer = buffer.slice(nl + 1);
        if (line === '') {
          if (event === 'cockpit:approval') {
            try { if (applyApproval(workspaceId, JSON.parse(data))) broadcast(workspaceId); } catch { /* malformed */ }
          }
          event = ''; data = '';
        } else if (line.startsWith('event: ')) {
          event = line.slice(7).trim();
        } else if (line.startsWith('data: ')) {
          data = data ? `${data}\n${line.slice(6)}` : line.slice(6);
        }
      }
    });
    res.on('end', () => retry(workspaceId, req));
    res.on('error', () => retry(workspaceId, req));
  });
  req.on('error', () => retry(workspaceId, req));
  s.request = req;
}

function retry(workspaceId: string, req: http.ClientRequest): void {
  const s = streams.get(workspaceId);
  if (!s || s.request !== req || s.timer) return;
  s.request = null;
  s.timer = setTimeout(() => {
    s.timer = null;
    // Only while that same sidecar is still the workspace's.
    if (streams.get(workspaceId) === s && sidecarUrlFor(workspaceId) === s.url) connect(workspaceId);
  }, RECONNECT_MS);
  // A retry alone never keeps the process alive.
  s.timer.unref?.();
}

/** Start following a sidecar's approvals; called once it is healthy. */
export function watchApprovals(workspaceId: string, url: string): void {
  const existing = streams.get(workspaceId);
  if (existing?.url === url && (existing.request || existing.timer)) return;
  unwatchApprovals(workspaceId);
  streams.set(workspaceId, { url, request: null, timer: null });
  connect(workspaceId);
}

/** Stop, when the sidecar exits: its approvals are gone with it. */
export function unwatchApprovals(workspaceId: string): void {
  const s = streams.get(workspaceId);
  if (s) {
    streams.delete(workspaceId);
    if (s.timer) clearTimeout(s.timer);
    try { s.request?.destroy(); } catch { /* already closed */ }
  }
  if (live.delete(workspaceId)) broadcast(workspaceId);
}

/** The person answering, as the sidecar records it. Never the renderer's choice. */
export function personActor(): string {
  let name = '';
  try { name = os.userInfo().username; } catch { /* no account name */ }
  return `user:${name || 'unknown'}`;
}

export interface AnswerResult {
  ok: boolean;
  status: number;
  error?: string;
  approval?: ApprovalView;
}

/** Post one answer with the sidecar's secret. */
export function postAnswer(
  url: string, secret: string, approvalId: string, decision: 'granted' | 'denied',
): Promise<AnswerResult> {
  const data = Buffer.from(JSON.stringify({ approval_id: approvalId, decision, actor: personActor() }));
  const u = new URL(`${url}/api/cockpit/approve`);
  return new Promise((resolve) => {
    const req = http.request({
      hostname: u.hostname, port: u.port, path: u.pathname, method: 'POST', timeout: 3000,
      headers: { 'Content-Type': 'application/json', 'Content-Length': data.length, 'X-Cockpit-Secret': secret },
    }, (res) => {
      let text = '';
      res.setEncoding('utf-8');
      res.on('data', (c: string) => { text += c; });
      res.on('end', () => {
        let body: { ok?: boolean; error?: string; result?: ApprovalView; approval?: ApprovalView } = {};
        try { body = JSON.parse(text); } catch { /* not JSON */ }
        resolve({
          ok: res.statusCode === 200 && body.ok === true,
          status: res.statusCode ?? 0,
          error: body.error,
          approval: body.result ?? body.approval,
        });
      });
    });
    req.on('error', () => resolve({ ok: false, status: 0, error: "the cockpit's server did not answer" }));
    req.on('timeout', () => { req.destroy(); resolve({ ok: false, status: 0, error: "the cockpit's server did not answer" }); });
    req.end(data);
  });
}

export function registerApprovalIpc(): void {
  ipcMain.handle('approval:list', () => liveApprovals());
  ipcMain.handle('approval:answer', async (_evt, workspaceId: unknown, approvalId: unknown, decision: unknown): Promise<AnswerResult> => {
    if (typeof workspaceId !== 'string' || typeof approvalId !== 'string'
        || (decision !== 'granted' && decision !== 'denied')) {
      return { ok: false, status: 0, error: 'an answer is granted or denied, for one approval' };
    }
    const url = sidecarUrlFor(workspaceId);
    const secret = sidecarSecretFor(workspaceId);
    if (!url || !secret) return { ok: false, status: 0, error: "this project's cockpit server is not running" };
    const result = await postAnswer(url, secret, approvalId, decision);
    if (result.approval && applyApproval(workspaceId, result.approval)) broadcast(workspaceId);
    return result;
  });
}
