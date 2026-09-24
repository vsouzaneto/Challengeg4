// Captures the three screens (plus states) for process-log/screenshots.
// Usage: npm run screenshots        -> mock mode (`vite --mode mock`, MSW fixtures, yellow demo banner)
//        npm run screenshots:real   -> real mode (`vite` proxying /api to the API on :8000; needs `docker compose up`)
// Both start Vite on :5199 and need Playwright chromium. Real mode skips the "artifacts missing"
// state, which only exists as a mock (`?mock=missing`).
import { spawn } from 'node:child_process';
import { mkdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { chromium } from 'playwright';

const PORT = 5199;
const REAL = process.env.SHOTS_MODE === 'real';
const OUT = resolve(process.argv[2] ?? '../../process-log/screenshots');
mkdirSync(OUT, { recursive: true });

const viteArgs = ['vite', '--port', String(PORT), '--strictPort'];
if (!REAL) viteArgs.splice(1, 0, '--mode', 'mock');
const vite = spawn('npx', viteArgs, { stdio: 'ignore' });
const base = `http://localhost:${PORT}`;

async function waitForServer() {
  for (let i = 0; i < 60; i++) {
    try {
      const res = await fetch(base);
      if (res.ok) return;
    } catch {
      /* not up yet */
    }
    await new Promise((r) => setTimeout(r, 500));
  }
  throw new Error('vite did not start');
}

const shots = [
  [
    'web-fila.png',
    '/?as_of=2017-12-31&region=Central&manager=Melvin+Marxen&agent=Darcel+Schlecht',
    null,
  ],
  [
    'web-fila-drawer.png',
    // Z063OYW0 is an MSW fixture; 28EJ0L9T is Darcel Schlecht's top deal in the real gold partition.
    `/?as_of=2017-12-31&agent=Darcel+Schlecht&deal=${REAL ? '28EJ0L9T' : 'Z063OYW0'}`,
    '[role=dialog]',
  ],
  [
    'web-fila-confirmar.png',
    '/?as_of=2017-12-31&manager=Melvin+Marxen&queue=confirm',
    '[role=progressbar]',
  ],
  ['web-time.png', '/time?as_of=2017-12-31&manager=Melvin+Marxen', 'table'],
  ['web-qualidade.png', '/qualidade?as_of=2017-12-31', 'svg[role=img]'],
  ['web-estado-artefatos.png', '/?as_of=2017-12-31&mock=missing', 'pre'],
  ['web-estado-vazio.png', '/?as_of=2017-12-31&agent=Ninguem', '[role=status]'],
].filter(([file]) => !(REAL && file === 'web-estado-artefatos.png'));

try {
  await waitForServer();
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1000 },
    deviceScaleFactor: 1,
  });
  for (const [file, path, waitFor] of shots) {
    await page.goto(base + path, { waitUntil: 'networkidle' });
    if (waitFor) await page.waitForSelector(waitFor, { timeout: 30000, state: 'attached' });
    await page.waitForTimeout(400);
    await page.screenshot({ path: resolve(OUT, file), fullPage: true });
    console.log('saved', file);
  }
  await browser.close();
} finally {
  vite.kill();
}
