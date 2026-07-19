// Download python-build-standalone for the current platform/arch and
// install project_os_cockpit (+ its deps) into the bundled interpreter.
//
//   node scripts/fetch-python.mjs
//
// Result: desktop/python-runtime/<platform-arch>/python/ contains a
// self-contained Python interpreter with the package installed. The
// Electron main process (src/ipc/sidecar.ts → pythonExecutable())
// resolves this path first, so launching the shell works without any
// system Python.
//
// This is the dev-time bundling step (TASK-0062). The packaged-app
// flow (TASK-0065) reuses the same layout but copies it into the
// .app's Resources directory at make time.

import { execFileSync, spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, rmSync } from 'node:fs';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const desktopRoot = path.resolve(here, '..');
const repoRoot = path.resolve(desktopRoot, '..');
const runtimeRoot = path.join(desktopRoot, 'python-runtime');

// Pinned python-build-standalone release. Bump deliberately — newer
// releases occasionally rename tarballs or drop arches. Verify the
// URL resolves before bumping in CI.
const PYTHON_VERSION = '3.13.1';
const RELEASE_DATE = '20250115';

const triples = {
  'darwin-arm64': 'aarch64-apple-darwin',
  'darwin-x64':   'x86_64-apple-darwin',
  'linux-x64':    'x86_64-unknown-linux-gnu',
  'win32-x64':    'x86_64-pc-windows-msvc',
};

const key = `${process.platform}-${process.arch}`;
const triple = triples[key];
if (!triple) {
  console.error(`fetch-python: unsupported platform ${key}`);
  process.exit(1);
}

const archDir = path.join(runtimeRoot, key);
const pythonHome = path.join(archDir, 'python');
const pythonBin = process.platform === 'win32'
  ? path.join(pythonHome, 'python.exe')
  : path.join(pythonHome, 'bin', 'python3');

if (existsSync(pythonBin)) {
  console.log(`fetch-python: already present at ${pythonBin}`);
  // Still try to refresh the install of the project package so dev
  // changes to src/ are reflected.
  reinstallProjectPackage(pythonBin);
  process.exit(0);
}

const tarball = `cpython-${PYTHON_VERSION}+${RELEASE_DATE}-${triple}-install_only.tar.gz`;
const url = `https://github.com/astral-sh/python-build-standalone/releases/download/${RELEASE_DATE}/${tarball}`;
const tarballPath = path.join(runtimeRoot, tarball);

mkdirSync(runtimeRoot, { recursive: true });
rmSync(archDir, { recursive: true, force: true });
mkdirSync(archDir, { recursive: true });

console.log(`fetch-python: downloading ${url}`);
execFileSync('curl', ['-fLo', tarballPath, url], { stdio: 'inherit' });

console.log(`fetch-python: extracting to ${archDir}`);
execFileSync('tar', ['-xzf', tarballPath, '-C', archDir], { stdio: 'inherit' });

if (!existsSync(pythonBin)) {
  console.error(`fetch-python: bundled python binary not found at ${pythonBin}`);
  process.exit(1);
}

reinstallProjectPackage(pythonBin);

rmSync(tarballPath, { force: true });
console.log(`fetch-python: ✓ bundled python ready at ${pythonBin}`);

function reinstallProjectPackage(py) {
  console.log(`fetch-python: pip install -e ${repoRoot}`);
  const res = spawnSync(
    py,
    ['-m', 'pip', 'install', '-e', repoRoot, '--quiet', '--disable-pip-version-check'],
    { stdio: 'inherit' },
  );
  if (res.status !== 0) {
    console.error(`fetch-python: pip install failed (exit ${res.status})`);
    process.exit(res.status ?? 1);
  }
  const verify = spawnSync(
    py,
    ['-c', 'import project_os_cockpit; print("bundled python:", project_os_cockpit.__version__)'],
    { stdio: 'inherit' },
  );
  if (verify.status !== 0) {
    console.error('fetch-python: verification failed');
    process.exit(verify.status ?? 1);
  }
}
