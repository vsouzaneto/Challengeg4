// Captures the three screens (plus states) in mock mode for process-log/screenshots.
// Usage: npm run screenshots  (starts `vite --mode mock` on :5199, needs Playwright chromium).
import { spawn } from 'node:child_process';
import { mkdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { chromium } from 'playwright';

const PORT = 5199;
const OUT = resolve(process.argv[2] ?? '../../process-log/screenshots');
mkdirSync(OUT, { recursive: true });

const vite = spawn('npx', ['vite', '--mode', 'mock', '--port', String(PORT), '--strictPort'], {
  stdio: 'ignore',
});
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
    '/?as_of=2017-12-31&agent=Darcel+Schlecht&deal=Z063OYW0',
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
];

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
