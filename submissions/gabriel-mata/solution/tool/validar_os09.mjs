/* OS-09 item 0.5 - roda o engine.js no Node e compara com o recalculo
   independente do os09_validacao.py.
   Uso: node validar_os09.mjs  (a partir de solution/tool/) */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const OUT09 = path.join(AQUI, "..", "outputs", "os09");

const srcEngine = fs.readFileSync(path.join(AQUI, "src", "engine.js"), "utf8");
const ENG = new Function(srcEngine + "; return ENGINE;")();

// ---------------------------------------------------------------- utilidades

/* CSV simples: sem aspas com virgula dentro e sem quebra de linha nos campos.
   Os dois arquivos lidos aqui sao gerados pelo proprio os09_validacao.py. */
function lerCSV(arquivo) {
  const txt = fs.readFileSync(arquivo, "utf8").replace(/\r/g, "").trim();
  const linhas = txt.split("\n");
  const cab = linhas[0].split(",");
  return linhas.slice(1).map((l) => {
    const campos = [];
    let atual = "", dentro = false;
    for (const ch of l) {
      if (ch === '"') dentro = !dentro;
      else if (ch === "," && !dentro) { campos.push(atual); atual = ""; }
      else atual += ch;
    }
    campos.push(atual);
    return Object.fromEntries(cab.map((h, i) => [h, campos[i]]));
  });
}

function lerBaseEmbutida() {
  const html = fs.readFileSync(path.join(AQUI, "decisor.html"), "utf8");
  const ini = html.indexOf('<script id="dados-embutidos" type="application/json">');
  if (ini < 0) throw new Error("decisor.html sem o bloco de dados embutidos");
  const abre = html.indexOf(">", ini) + 1;
  const fecha = html.indexOf("</script>", abre);
  return JSON.parse(html.slice(abre, fecha));
}

let falhas = 0;
const resumo = [];

function checar(item, dif, tolerancia) {
  const ok = dif <= tolerancia;
  if (!ok) falhas++;
  resumo.push({ item, dif, tolerancia, ok });
  return ok;
}

function tabela(titulo, linhas, colunas) {
  console.log("\n" + titulo);
  const larg = colunas.map((c) =>
    Math.max(c.rotulo.length, ...linhas.map((l) => String(c.valor(l)).length)));
  const linha = (cels) => "| " + cels.map((c, i) => String(c).padEnd(larg[i])).join(" | ") + " |";
  console.log(linha(colunas.map((c) => c.rotulo)));
  console.log("|" + larg.map((w) => "-".repeat(w + 2)).join("|") + "|");
  linhas.forEach((l) => console.log(linha(colunas.map((c) => c.valor(l)))));
}

/* Segmentos simples (um valor de uma variavel) de um resultado do engine. */
function simples(r) {
  const m = new Map();
  for (const bloco of [r.desempenho, r.publico]) {
    if (!bloco) continue;
    for (const s of bloco.segmentos) {
      if (s.vars.length !== 1) continue;
      m.set(s.vars[0] + "|" + s.valores[0], s);
    }
  }
  return m;
}

// ------------------------------------------------------- 0.5.1 base completa

const base = ENG.montarBase(lerBaseEmbutida());
const r = ENG.analisar(base, { margem: 0.10 });
console.log(`Base embutida: ${base.n} posts. Analise: ${r.n} posts, k desempenho = ${r.desempenho.k}, k publico = ${r.publico.k}`);

const refA = lerCSV(path.join(OUT09, "a_referencia_lift_ep.csv"));
const segs = simples(r);
let maxLift = 0, maxEp = 0, comparadas = 0, faltantes = [];
const piores = [];
for (const o of refA) {
  const s = segs.get(o.variavel + "|" + o.segmento);
  if (!s) { faltantes.push(o.variavel + "|" + o.segmento); continue; }
  const v = s.metricas[o.metrica];
  const dl = Math.abs(v.lift - Number(o.lift)), de = Math.abs(v.ep - Number(o.ep));
  if (Number(o.n) !== s.n) { falhas++; console.log(`  n diferente em ${o.variavel}|${o.segmento}: ${s.n} vs ${o.n}`); }
  maxLift = Math.max(maxLift, dl); maxEp = Math.max(maxEp, de);
  comparadas++;
  piores.push({ ...o, lift: v.lift, ep: v.ep, dl, de });
}
piores.sort((a, b) => Math.max(b.dl, b.de) - Math.max(a.dl, a.de));

tabela(`0.5.1 - maiores diferencas entre engine e Python (${comparadas} linhas comparadas)`,
  piores.slice(0, 8), [
    { rotulo: "metrica", valor: (l) => l.metrica },
    { rotulo: "variavel", valor: (l) => l.variavel },
    { rotulo: "segmento", valor: (l) => l.segmento },
    { rotulo: "n", valor: (l) => l.n },
    { rotulo: "lift engine", valor: (l) => l.lift.toFixed(9) },
    { rotulo: "lift python", valor: (l) => Number(l.lift_py ?? l.lift).toFixed(9) },
    { rotulo: "dif lift", valor: (l) => l.dl.toExponential(2) },
    { rotulo: "dif ep", valor: (l) => l.de.toExponential(2) },
  ]);

if (faltantes.length) { falhas++; console.log("  segmentos ausentes no engine: " + faltantes.join(", ")); }
if (comparadas !== refA.length) { falhas++; console.log(`  comparadas ${comparadas} de ${refA.length}`); }
checar("0.5.1 lift (segmentos simples, base completa)", maxLift, 1e-6);
checar("0.5.1 erro padrao (segmentos simples, base completa)", maxEp, 1e-6);

// ------------------------------------------------- 0.5.2 efeito conhecido

const linhasB = lerCSV(path.join(OUT09, "fixtures", "base_efeito_conhecido.csv"));
const baseB = ENG.carregarLinhas(linhasB);
if (baseB.erro) throw new Error("fixture do 0.5.2 nao carregou: " + baseB.erro);
const rB = ENG.analisar(baseB, { margem: 0.10 });
console.log(`\n0.5.2 - base com efeito conhecido: ${baseB.n} posts carregados, ${baseB.descartadas} descartados, k = ${rB.desempenho.k}`);

const ESPERADO_B = {
  video: { lift: 0.196, tipo: "funciona" }, image: { lift: -0.147, tipo: "nao_funciona" },
  text: { lift: -0.133, tipo: "nao_funciona" }, mixed: { lift: -0.133, tipo: "nao_funciona" },
};
const refB = new Map(lerCSV(path.join(OUT09, "b_referencia_efeito_conhecido.csv"))
  .filter((o) => o.metrica === "taxa").map((o) => [o.segmento, o]));
const segsB = simples(rB);
const linhasTabB = [];
for (const nome of Object.keys(ESPERADO_B)) {
  const s = segsB.get("formato|" + nome);
  const v = s.metricas.taxa;
  const py = refB.get(nome);
  const dl = Math.abs(v.lift - Number(py.lift)), de = Math.abs(v.ep - Number(py.ep));
  maxLift = Math.max(maxLift, dl); maxEp = Math.max(maxEp, de);
  const pctEngine = (v.lift - 1) * 100;
  linhasTabB.push({
    segmento: nome, n: s.n, pct: pctEngine, pctEsperado: ESPERADO_B[nome].lift * 100,
    tipo: v.tipo, tipoEsperado: ESPERADO_B[nome].tipo, dl, de,
  });
  // tabela da OS: lift arredondado a 1 decimal e veredito
  if (Math.abs(pctEngine - ESPERADO_B[nome].lift * 100) > 0.05) {
    falhas++; console.log(`  FORA DO ESPERADO: lift de ${nome} = ${pctEngine.toFixed(2)}%`);
  }
  if (v.tipo !== ESPERADO_B[nome].tipo) {
    falhas++; console.log(`  FORA DO ESPERADO: veredito de ${nome} = ${v.tipo}`);
  }
}

tabela("0.5.2 - formato na base com efeito conhecido (margem 10%)", linhasTabB, [
  { rotulo: "formato", valor: (l) => l.segmento },
  { rotulo: "n", valor: (l) => l.n },
  { rotulo: "lift engine", valor: (l) => (l.pct >= 0 ? "+" : "") + l.pct.toFixed(2) + "%" },
  { rotulo: "lift da OS", valor: (l) => (l.pctEsperado >= 0 ? "+" : "") + l.pctEsperado.toFixed(1) + "%" },
  { rotulo: "veredito", valor: (l) => l.tipo },
  { rotulo: "esperado", valor: (l) => l.tipoEsperado },
  { rotulo: "dif lift vs Python", valor: (l) => l.dl.toExponential(2) },
  { rotulo: "dif ep vs Python", valor: (l) => l.de.toExponential(2) },
]);
checar("0.5.2 lift e ep contra o Python", Math.max(...linhasTabB.map((l) => Math.max(l.dl, l.de))), 1e-6);

// ------------------------------------------------- 0.5.3 base do desafio

function contarTipos(blocos, met) {
  const c = { funciona: 0, nao_funciona: 0, sem_efeito: 0, inconclusivo: 0 };
  for (const b of [].concat(blocos)) {
    if (!b) continue;
    for (const s of b.segmentos) c[s.metricas[met].tipo]++;
  }
  return c;
}

const tipos = contarTipos([r.desempenho, r.publico], "taxa");
const tiposPublico = contarTipos(r.publico, "taxa");
const vPat = r.patrocinio.metricas.taxa;
const VEREDITO_PAT = { funciona: "Aprovado", nao_funciona: "Barrado", sem_efeito: "Barrado", inconclusivo: "Inconclusivo" };

const checks = [
  { item: "patrocinio", esperado: "Barrado", obtido: VEREDITO_PAT[vPat.tipo],
    detalhe: `efeito ${vPat.efeito.toFixed(6)}, IC equiv. [${vPat.eqLo.toFixed(5)}; ${vPat.eqHi.toFixed(5)}]` },
  { item: "nenhum positivo", esperado: "0", obtido: String(tipos.funciona),
    detalhe: `${tipos.sem_efeito} sem efeito comprovado` },
  { item: "nenhum negativo", esperado: "0", obtido: String(tipos.nao_funciona),
    detalhe: `${tipos.inconclusivo} inconclusivos` },
  { item: "publico", esperado: "nenhum comprovado",
    obtido: tiposPublico.funciona === 0 ? "nenhum comprovado" : `${tiposPublico.funciona} positivos`,
    detalhe: `${r.publico.segmentos.length} segmentos de publico` },
];

tabela("0.5.3 - vereditos na base do desafio (precisam ficar inalterados)", checks, [
  { rotulo: "item", valor: (l) => l.item },
  { rotulo: "esperado", valor: (l) => l.esperado },
  { rotulo: "obtido", valor: (l) => l.obtido },
  { rotulo: "ok", valor: (l) => (l.obtido === l.esperado ? "sim" : "NAO") },
  { rotulo: "detalhe", valor: (l) => l.detalhe },
]);
for (const c of checks) if (c.obtido !== c.esperado) { falhas++; console.log(`  FORA DO ESPERADO: ${c.item} -> ${c.obtido}`); }

// ------------------------------------------------- A/B com piso de 30

console.log(`\n0.3 - teste A/B: dp do indice ${r.ab.dp.toFixed(6)}, calculado ${r.ab.calculado} posts por versao, usado ${r.ab.posts} (piso 30)`);
if (r.ab.posts < 30) { falhas++; console.log("  FORA DO ESPERADO: menos de 30 posts por versao"); }

tabela("Resumo das tolerancias", resumo, [
  { rotulo: "item", valor: (l) => l.item },
  { rotulo: "dif", valor: (l) => l.dif.toExponential(2) },
  { rotulo: "tolerancia", valor: (l) => l.tolerancia },
  { rotulo: "ok", valor: (l) => (l.ok ? "sim" : "NAO") },
]);

console.log(falhas === 0 ? "\nTodas as checagens passaram." : `\n${falhas} checagem(ns) fora do esperado.`);
process.exit(falhas === 0 ? 0 : 1);
