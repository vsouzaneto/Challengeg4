// Paridade do ROI: o cálculo em JS (js/roi.js) precisa reproduzir o do Python (pipeline/05_revisao_csv.py).
// Uso: node tests/roi.mjs   (a partir de solution/app)
import { readFileSync } from 'node:fs';
import { scenario, breakeven } from '../js/roi.js';

const { roi } = JSON.parse(readFileSync(new URL('../data/revisao.json', import.meta.url), 'utf8'));
const close = (a, b) => (a === null || b === null ? a === b : Math.abs(a - b) <= 1e-6 * Math.max(1, Math.abs(b)));
let fails = 0;
['conservador', 'provável', 'otimista'].forEach((name, i) => {
  const js = scenario(roi, i);
  const py = roi.cenarios[name];
  for (const k of ['horas_total', 'beneficio_mes', 'custo_mes', 'implantacao', 'roi_12m', 'payback_meses']) {
    if (!close(js[k], py[k])) { fails += 1; console.error(`${name}.${k}: js=${js[k]} py=${py[k]}`); }
  }
  if (Math.abs(breakeven(roi, i) - py.equilibrio) > 0.01) { fails += 1; console.error(`${name}.equilibrio difere`); }
  const r2500 = scenario(roi, i, { vol: 2500 });
  if (!close(r2500.roi_12m, py.com_2500.roi_12m)) { fails += 1; console.error(`${name}.com_2500 difere`); }
  console.log(`${name}: ROI 12m ${(100 * js.roi_12m).toFixed(1)}% (Python ${(100 * py.roi_12m).toFixed(1)}%)`);
});
if (fails) { console.error(`FALHOU: ${fails} divergência(s)`); process.exit(1); }
console.log('OK');
