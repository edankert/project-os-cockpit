// The latest test run and CI runs on the Tests page ([[FEAT-0161]], [[TASK-0681]]).
//
// Drawn from `GET /api/cockpit/test-run`, which reads the two files
// project-os's `run-tests.py` and `ci-status.py` write under `.project-os/`
// (the template's `tools/instructions/TEST-RUNS.md`). **The page works nothing
// out itself**: the header, each command's symbol, duration and tooltip, which
// commands get a row, and each workflow's state all arrive in the payload
// (`test_runs.py`), so the rules are tested in the Python suite and this file
// only places them.
//
// Declares no imports and no exports: `renderer.ts` is loaded as a plain
// <script>, so this is loaded the same way, before it, and these are globals.

interface TrCommand {
  index: number; tests: string[]; command: string; state: string;
  symbol: string; label: string; took: string; reason: string;
  progress: string; log_url: string; listed: boolean; tip: string;
}
interface TrRun {
  header: string; state: string; state_line: string; live: boolean;
  commit: string; branch: string; commands: TrCommand[];
}
interface TrRunReading {
  state: string; message?: string; file?: string; run?: TrRun;
}
interface TrCiRun {
  state: string; symbol: string; commit: string; event: string; ago: string;
  url: string; failing_tests: string[]; failing_jobs: string[];
}
interface TrWorkflow extends TrCiRun { name: string; red: boolean; previous: TrCiRun | null }
interface TrCiReading {
  state: string; message?: string; branch?: string; fetched_ago?: string;
  error?: string; workflows?: TrWorkflow[];
}
interface TrPayload { run: TrRunReading; ci: TrCiReading }

/** What a click does. The renderer supplies both, because only it holds the
 *  sidecar's address and the shell bridge. */
interface TrOpeners {
  log: (route: string) => void;
  external: (url: string) => void;
}

function trEl(tag: string, cls: string, text?: string): HTMLElement {
  const el = document.createElement(tag);
  if (cls) el.className = cls;
  if (text !== undefined) el.textContent = text;
  return el;
}

/** A section with the landing's own group head, so it reads as part of the
 *  page rather than as a panel bolted onto it. */
function trSection(title: string, aside: string): HTMLElement {
  const section = trEl('section', 'view-landing-group tr-section');
  const head = trEl('div', 'view-landing-group-head', title);
  if (aside) head.appendChild(trEl('span', 'tr-head-aside', aside));
  section.appendChild(head);
  return section;
}

/** One line in place of a section: no file, or a file that cannot be read. */
function trQuiet(text: string, unreadable: boolean): HTMLElement {
  return trEl('p', unreadable ? 'tr-quiet tr-unreadable' : 'tr-quiet', text);
}

/** The text of one command's row, after its symbol. */
function trRowText(c: TrCommand): string {
  const who = c.tests.length ? c.tests.join(' ') : (c.command || `command ${c.index}`);
  const parts = [who, c.label];
  if (c.took) parts.push(c.took);
  //: A running command's progress line is the news; its reason is empty
  //: until it ends.
  if (c.state === 'running' && c.progress) parts.push(c.progress);
  else if (c.reason) parts.push(c.reason);
  return parts.join(' · ');
}

function trBuildRun(reading: TrRunReading, open: TrOpeners): HTMLElement {
  const run = reading.run;
  const section = trSection('Latest test run', run && run.commit
    ? `${run.branch ? `${run.branch} · ` : ''}${run.commit}` : '');
  if (reading.state !== 'ok' || !run) {
    section.appendChild(trQuiet(reading.message || 'No test run yet.',
      reading.state === 'unreadable'));
    return section;
  }
  const head = trEl('p', 'tr-run-head');
  head.appendChild(trEl('span', 'tr-run-header', run.header));
  head.appendChild(trEl('span', `tr-run-state tr-run-${run.state}`, run.state_line));
  section.appendChild(head);

  //: The grid: one block per command, in the file's order, which is the
  //: order the runner runs them. A block with a log opens it; a waiting
  //: command has none yet and is not a button.
  const grid = trEl('div', 'tr-grid');
  grid.setAttribute('role', 'list');
  for (const c of run.commands) {
    const block = trEl(c.log_url ? 'button' : 'span',
      `tr-block tr-${c.state}`, c.symbol);
    block.setAttribute('role', 'listitem');
    block.title = c.tip;
    if (c.log_url && block instanceof HTMLButtonElement) {
      block.type = 'button';
      block.addEventListener('click', () => open.log(c.log_url));
    }
    grid.appendChild(block);
  }
  section.appendChild(grid);

  const listed = run.commands.filter((c) => c.listed);
  if (listed.length) {
    const list = trEl('ul', 'view-landing-list tr-rows');
    for (const c of listed) {
      const li = document.createElement('li');
      const row = trEl(c.log_url ? 'button' : 'div', 'view-landing-row tr-row');
      row.appendChild(trEl('span', `tr-row-symbol tr-${c.state}`, c.symbol));
      const text = trEl('span', 'view-landing-title tr-row-text', trRowText(c));
      text.title = c.command || text.textContent || '';
      row.appendChild(text);
      if (c.log_url && row instanceof HTMLButtonElement) {
        row.type = 'button';
        row.appendChild(trEl('span', 'view-landing-note', 'log'));
        row.addEventListener('click', () => open.log(c.log_url));
      }
      li.appendChild(row);
      list.appendChild(li);
    }
    section.appendChild(list);
  }
  return section;
}

/** `TST-0022 TST-0023`, or `jobs: android`, or `` for a run that passed. */
function trCiFailing(r: TrCiRun): string {
  if (r.failing_tests.length) return r.failing_tests.join(' ');
  if (r.failing_jobs.length) return `jobs: ${r.failing_jobs.join(', ')}`;
  return '';
}

function trBuildCi(reading: TrCiReading, open: TrOpeners): HTMLElement {
  const section = trSection('CI', reading.state === 'ok'
    ? [reading.branch || '', reading.fetched_ago ? `fetched ${reading.fetched_ago}` : '']
      .filter(Boolean).join(' · ')
    : '');
  if (reading.state !== 'ok') {
    section.appendChild(trQuiet(reading.message || 'No CI result yet.',
      reading.state === 'unreadable'));
    return section;
  }
  if (reading.error) section.appendChild(trQuiet(reading.error, true));
  const workflows = reading.workflows || [];
  if (!workflows.length) {
    section.appendChild(trQuiet('No workflow runs on this branch.', false));
    return section;
  }
  const list = trEl('ul', 'view-landing-list tr-rows');
  for (const w of workflows) {
    const li = document.createElement('li');
    const row = trEl(w.url ? 'button' : 'div', 'view-landing-row tr-row');
    row.appendChild(trEl('span', `tr-row-symbol tr-ci-${w.state}`, w.symbol));
    const parts = [w.name, w.state];
    if (w.commit) parts.push(w.commit);
    if (w.ago) parts.push(w.ago);
    const failing = trCiFailing(w);
    if (failing) parts.push(failing);
    //: Still running after a failure: say the failure, or the row reads as
    //: recovered while the workflow is still red (TEST-RUNS.md).
    if (w.previous) {
      const before = trCiFailing(w.previous);
      parts.push(`last finished run failed${w.previous.commit ? ` on ${w.previous.commit}` : ''}`
        + (before ? `: ${before}` : ''));
    }
    row.appendChild(trEl('span', 'view-landing-title tr-row-text', parts.join(' · ')));
    if (w.url && row instanceof HTMLButtonElement) {
      row.type = 'button';
      row.title = w.url;
      row.appendChild(trEl('span', 'view-landing-note', 'open run'));
      row.addEventListener('click', () => open.external(w.url));
    }
    li.appendChild(row);
    list.appendChild(li);
  }
  section.appendChild(list);
  return section;
}

/** Both sections, for the top of the Tests page. */
function trBuildSections(data: TrPayload, open: TrOpeners): HTMLElement {
  const wrap = trEl('div', 'tr-panel');
  wrap.appendChild(trBuildRun(data.run || { state: 'absent' }, open));
  wrap.appendChild(trBuildCi(data.ci || { state: 'absent' }, open));
  return wrap;
}
