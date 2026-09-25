// Paridade Python × navegador: o modelo em JS precisa reproduzir as probabilidades do sklearn.
// Uso: node tests/parity.mjs   (a partir de solution/app)
import { readFileSync } from 'node:fs';
import { TriageModel } from '../js/model.js';

const load = (f) => JSON.parse(readFileSync(new URL(`../data/${f}`, import.meta.url), 'utf8'));
const model = new TriageModel(load('model.json'));
const { docs, proba, faixas } = load('paridade.json');

let maxDiff = 0;
let sameTop = 0;
const laneMismatch = [];
docs.forEach((doc, i) => {
  const r = model.predict(doc);
  const p = r.proba;
  if (r.lane.id !== faixas[i]) laneMismatch.push(`${faixas[i]} → ${r.lane.id}: ${doc.slice(0, 60)}`);
  p.forEach((v, k) => { maxDiff = Math.max(maxDiff, Math.abs(v - proba[i][k])); });
  const top = (arr) => arr.indexOf(Math.max(...arr));
  if (top(p) === top(proba[i])) sameTop += 1;
});

console.log(`${docs.length} textos | mesma fila: ${sameTop}/${docs.length} | mesma faixa: ${docs.length - laneMismatch.length}/${docs.length} | maior diferença de probabilidade: ${maxDiff.toExponential(2)}`);
laneMismatch.forEach((m) => console.error(`  faixa diferente: ${m}`));
// Pesos e idf são exportados com 4 casas decimais; diferenças até ~1e-3 são arredondamento, não divergência de lógica.
if (sameTop !== docs.length || laneMismatch.length || maxDiff > 2e-3) {
  console.error('FALHOU: o modelo do navegador diverge do sklearn');
  process.exit(1);
}
console.log('OK');
