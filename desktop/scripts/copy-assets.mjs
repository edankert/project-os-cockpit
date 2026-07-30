// Copy renderer HTML + CSS + third-party UMD bundles into dist/.
//
// tsc only emits JavaScript for our own .ts sources. The renderer needs
// HTML / CSS / xterm.js (UMD) / addon-fit.js (UMD) / xterm.css alongside
// the compiled renderer.js, so this script copies them after tsc finishes.
//
// We use the UMD builds of xterm + addon-fit (not their ES modules)
// because the renderer is loaded as a plain `<script>` rather than an
// ES module — see the explanatory note at the top of renderer.ts.

import { cp, mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const repoRoot = path.resolve(root, '..');
const rendererSrc = path.join(root, 'src', 'renderer');
const rendererDst = path.join(root, 'dist', 'renderer');
const nodeModules = path.join(root, 'node_modules');

await mkdir(rendererDst, { recursive: true });

// Our own renderer assets.
for (const file of ['index.html', 'renderer.css']) {
  await cp(path.join(rendererSrc, file), path.join(rendererDst, file));
}

// Cockpit's content + shell CSS — single source of truth in the
// Python package, copied here at build time so the mounted Markdown
// HTML inherits the same styling mode 1 uses. `base.css` holds the
// `--surface`, `--text`, status / severity, font, and metadata-strip
// styles; `cockpit.css` layers cockpit-specific chrome on top.
// (FEAT-0009 may later split this further; for now we ship both.)
const staticDir = path.join(repoRoot, 'src', 'project_os_cockpit', 'static');
for (const file of ['base.css', 'cockpit.css']) {
  await cp(path.join(staticDir, file), path.join(rendererDst, file));
}

// Third-party UMD bundles (loaded via `<script>` tags in index.html).
const vendored = [
  ['@xterm/xterm/lib/xterm.js',         'xterm.js'],
  ['@xterm/xterm/css/xterm.css',        'xterm.css'],
  ['@xterm/addon-fit/lib/addon-fit.js', 'addon-fit.js'],
];
for (const [src, dst] of vendored) {
  await cp(path.join(nodeModules, src), path.join(rendererDst, dst));
}

// Stamp what this build was produced FROM (ISS-0055 §4). The staleness
// guard used to compare mtimes, which fired on a no-op touch — restoring
// renderer.ts byte-identical after a mutation run moved its mtime past
// the build's and turned the suite red with nothing stale. A content
// hash answers the question mtime was only approximating.
//
// Every .ts under src/, not just renderer.ts (PHASE-013 review, F8):
// `fleet-health.test.mjs` runs against `dist/ipc/fleet-health.js`, so a
// hash covering only the renderer let the one BEHAVIOURAL suite in the
// repo test a stale artifact and stay green.
async function tsFiles(dir) {
  const out = [];
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const abs = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...await tsFiles(abs));
    else if (entry.name.endsWith('.ts')) out.push(abs);
  }
  return out;
}
const sources = (await tsFiles(path.join(root, 'src'))).sort();
const digest = createHash('sha256');
for (const file of sources) {
  digest.update(path.relative(root, file));       // renames count as changes
  digest.update(await readFile(file));
}
await writeFile(
  path.join(rendererDst, '.source-hash'),
  digest.digest('hex') + '\n',
  'utf-8',
);

console.log(`copy-assets: ${rendererSrc} (+ vendored xterm) → ${rendererDst}`);
