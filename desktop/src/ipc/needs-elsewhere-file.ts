// The file that tells a cockpit terminal's Claude plugin what needs the
// person in the other projects (FEAT-0157 / TASK-0671).
//
// A sidecar knows only its own project, so the shell, which knows every
// project, writes `needs-elsewhere.json` into each workspace's instrument
// folder beside `hook-env`. The plugin adds the counts up for the project
// line. This module builds the file and writes it; it imports nothing from
// Electron, so the node suite runs it as built.

import * as fs from 'node:fs';
import * as path from 'node:path';

import { NeedsCount } from './needs-count';

export const NEEDS_ELSEWHERE_FILE = 'needs-elsewhere.json';

export interface ElsewhereProject {
  project: string;
  workspace_id: string;
  /** null when it could not be read; never 0 for "not read". */
  count: number | null;
  as_of: string | null;
  source: NeedsCount['source'];
}

export interface NeedsElsewhere {
  schema_version: 1;
  written_at: string;
  /** The folder's own workspace, which the plugin uses to build its link. */
  workspace_id: string;
  /** Every other workspace, never this one. */
  projects: ElsewhereProject[];
}

/** The file for one workspace's folder, from every workspace's count. */
export function elsewherePayload(
  selfId: string,
  rows: { id: string; name: string; count: NeedsCount }[],
  now: number,
): NeedsElsewhere {
  return {
    schema_version: 1,
    written_at: new Date(now).toISOString(),
    workspace_id: selfId,
    projects: rows.filter((r) => r.id !== selfId).map((r) => ({
      project: r.name,
      workspace_id: r.id,
      count: r.count.count,
      as_of: r.count.asOf,
      source: r.count.source,
    })),
  };
}

/** Writes `name` in `dir` through a temporary file and a rename, so a reader
 *  sees the old file or the new one, never half of one. Throws on failure,
 *  leaving the previous file in place. */
export function writeAtomic(dir: string, name: string, text: string): void {
  const target = path.join(dir, name);
  const temp = path.join(dir, `.${name}.${process.pid}.tmp`);
  try {
    fs.writeFileSync(temp, text, 'utf-8');
    fs.renameSync(temp, target);
  } catch (err) {
    try { fs.rmSync(temp, { force: true }); } catch { /* nothing to clean */ }
    throw err;
  }
}
