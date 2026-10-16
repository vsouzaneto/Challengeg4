// Capturas reais do Lead Kanban para o vídeo, em 2× (3840×2160), com a posição dos elementos destacados.
//
//   1) em solution/: python server.py
//   2) aqui:          npm run capturas [-- --url http://localhost:8000]
//
// Grava public/capturas/<tela>.jpg e src/capturas.json ({tela: {elemento: [x, y, largura, altura]}}),
// com coordenadas no quadro de 1920×1080. Usa o Microsoft Edge instalado (playwright-core, sem baixar navegador).
import {mkdirSync, writeFileSync} from 'node:fs';
import {dirname, join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright-core';

const raiz = join(dirname(fileURLToPath(import.meta.url)), '..');
const i = process.argv.indexOf('--url');
const url = i > 0 ? process.argv[i + 1] : 'http://localhost:8000';
const pasta = join(raiz, 'public', 'capturas');
mkdirSync(pasta, {recursive: true});

const browser = await chromium.launch({channel: 'msedge'});
const context = await browser.newContext({viewport: {width: 1920, height: 1080}, deviceScaleFactor: 2, locale: 'pt-BR'});
const page = await context.newPage();
const erros = [];
page.on('pageerror', (e) => erros.push(String(e)));

await page.goto(`${url}/#/pipeline`);
await page.evaluate(() => {
  localStorage.clear();
  localStorage.setItem('lead-kanban-guide-dismissed', 'true');
});
await page.reload();
await page.waitForSelector('.card');

const caixas = {};
const pausa = (ms) => page.waitForTimeout(ms);
async function medir(tela, alvos) {
  caixas[tela] = await page.evaluate((alvos) => {
    const out = {};
    for (const [nome, seletor, indice = 0] of alvos) {
      const el = document.querySelectorAll(seletor)[indice];
      if (!el) continue;
      const r = el.getBoundingClientRect();
      out[nome] = [r.x, r.y, r.width, r.height].map((v) => Math.round(v));
    }
    return out;
  }, alvos);
}
async function capturar(tela, alvos) {
  await pausa(500);
  await medir(tela, alvos);
  await page.screenshot({path: join(pasta, `${tela}.jpg`), type: 'jpeg', quality: 88});
  console.log(`${tela}: ${Object.keys(caixas[tela]).join(', ')}`);
}

await capturar('pipeline', [
  ['negociar', '.lane', 0], ['qualificar', '.lane', 1], ['encerrar', '.lane', 2],
  ['cabecaNegociar', '.lane-head', 0], ['cabecaQualificar', '.lane-head', 1], ['cabecaEncerrar', '.lane-head', 2],
  ['cartao', '.lane .card', 0], ['prazo', '.lane .card .deadline', 0],
  ['vendedor', '#f-agent'], ['ajuda', '#open-help'], ['dashboardTab', 'a[href="#/dashboard"]'],
]);

// Carteira de uma vendedora com negócios nas três colunas.
await page.selectOption('#f-agent', 'Anna Snelling');
await page.dispatchEvent('#f-agent', 'change');
await capturar('filtrado', [['vendedor', '#f-agent'], ['negociar', '.lane', 0], ['qualificar', '.lane', 1], ['encerrar', '.lane', 2]]);
await page.selectOption('#f-agent', '');
await page.dispatchEvent('#f-agent', 'change');
await pausa(300);

await page.click('.lane .card');
await page.waitForSelector('#deal-modal[open]');
await capturar('detalhe', [
  ['modal', '#deal-content'], ['acoes', '.detail-grid .panel', 0], ['motivo', '.detail-grid .panel', 1],
  ['tempo', '.detail-grid .panel', 2],
]);
await page.keyboard.press('Escape');

await page.goto(`${url}/#/dashboard`);
await page.waitForSelector('.kpis');
await capturar('dashboard', [['kpis', '.kpis'], ['composicao', '.stack-chart'], ['rankings', '.rank-grid']]);
await page.evaluate(() => {
  const grade = document.querySelector('.facts-grid');
  const bloco = grade.closest('section') || grade.parentElement;
  window.scrollBy(0, bloco.getBoundingClientRect().top - 84);
});
await capturar('evidencias', [['fatos', '.facts-grid']]);

await page.goto(`${url}/#/pipeline`);
await page.waitForSelector('.card');
await pausa(600); // a troca de rota fecha diálogos abertos; espera ela terminar antes do clique
await page.evaluate(() => document.getElementById('open-help').click());
await page.waitForFunction(() => document.getElementById('help-modal').open, null, {timeout: 5000});
await capturar('ajuda', [['modal', '#help-content'], ['botao', '#open-help']]);

writeFileSync(join(raiz, 'src', 'capturas.json'), JSON.stringify(caixas, null, 1));
await browser.close();
if (erros.length) {
  console.error('Erros na página:', erros);
  process.exit(1);
}
