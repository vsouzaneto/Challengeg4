// Cenários da política do chat (sem LLM: textos em inglês, ou português sem tradução).
// Uso: node tests/chat.mjs   (a partir de solution/app)
import { readFileSync } from 'node:fs';
import { TriageModel } from '../js/model.js';
import { decide, needsTranslation } from '../js/chat-policy.js';

const model = new TriageModel(JSON.parse(readFileSync(new URL('../data/model.json', import.meta.url), 'utf8')));
const CASES = [
  ['my laptop screen is flickering and the docking station does not detect the external monitor', 'auto'],
  ['Hi team, I cannot log into Confluence since this morning, my account seems locked. Can you help?', 'auto'],
  ['Please create a new purchase order for two monitors and a keyboard for the new hire starting Monday', 'assistido'],
  ['please help, it does not work', 'detalhes'],
  ['I want a refund, I was charged twice for the same license', 'humano'],
  ['I accidentally deleted the project folder, can you recover it?', 'humano'],
  ['I will be on maternity leave from next month, how do I log my hours?', 'humano'],
  ['my account was hacked and someone changed my password', 'humano'],
  ['Minha senha expirou e não consigo entrar no Outlook', 'humano'], // português sem tradução: fora do padrão
  ['Quero o reembolso, fui cobrado duas vezes', 'humano'], // regra de risco vale no texto original
  ['Estou de licença-maternidade a partir de dezembro', 'humano'],
  ['não funciona, me ajuda', 'humano'], // sem tradução: português fica fora do padrão e vai para uma pessoa
  ['it does not work, help me please', 'detalhes'], // a mesma frase depois da tradução: pedido vago
];
let fails = 0;
for (const [text, expected] of CASES) {
  const d = decide(model, text);
  const ok = d.lane === expected;
  if (!ok) fails += 1;
  console.log(`${ok ? 'ok ' : 'ERRO'} ${d.lane.padEnd(9)} (esperado ${expected.padEnd(9)}) ${Math.round(100 * d.r.conf)}% ${d.r.top.padEnd(20)} | ${text.slice(0, 60)}`);
}
const t1 = needsTranslation(model, 'Minha senha expirou e não consigo entrar no Outlook');
const t2 = needsTranslation(model, 'my laptop screen is flickering');
console.log(`traduzir português: ${t1} | traduzir inglês: ${t2}`);
if (!t1 || t2) fails += 1;
if (fails) { console.error(`FALHOU: ${fails}`); process.exit(1); }
console.log('OK');
