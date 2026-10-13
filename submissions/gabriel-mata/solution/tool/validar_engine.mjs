/* OS-08 item 10 - roda o engine.js no Node sobre a base embutida no decisor.html
   e compara com as saidas do Python das OS anteriores.
   Uso: node validar_engine.mjs  (a partir de solution/tool/) */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const OUTPUTS = path.join(AQUI, "..", "outputs");

// o engine.js e um script de navegador (sem import/export): carregamos o texto
const srcEngine = fs.readFileSync(path.join(AQUI, "src", "engine.js"), "utf8");
const ENG = new Function(srcEngine + "; return ENGINE;")();

// ---------------------------------------------------------------- utilidades

function lerCSV(rel) {
  const txt = fs.readFileSync(path.join(OUTPUTS, rel), "utf8").trim();
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

/* Extrai o JSON dos dados embutidos no decisor.html. */
function lerBaseEmbutida() {
  const html = fs.readFileSync(path.join(AQUI, "decisor.html"), "utf8");
  const ini = html.indexOf('<script id="dados-embutidos" type="application/json">');
  if (ini < 0) throw new Error("decisor.html sem o bloco de dados embutidos");
  const abre = html.indexOf(">", ini) + 1;
  const fecha = html.indexOf("</script>", abre);
  return JSON.parse(html.slice(abre, fecha));
}

const linhasRelatorio = [];
let falhas = 0;

function checar(item, obtido, esperado, tolerancia, unidade = "") {
  const dif = Math.abs(obtido - esperado);
  const ok = dif <= tolerancia;
  if (!ok) falhas++;
  linhasRelatorio.push({
    item, obtido, esperado, dif, tolerancia, ok, unidade,
  });
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

// ---------------------------------------------------------------- base e analise

const compacto = lerBaseEmbutida();
const base = ENG.montarBase(compacto);
console.log(`Base embutida: ${base.n} posts, de ${new Date(base.dataMin).toISOString().slice(0, 10)} a ${new Date(base.dataMax).toISOString().slice(0, 10)}`);

// base completa, sem filtros, margem padrao de 10%
const r = ENG.analisar(base, { margem: 0.10 });
console.log(`Analise: ${r.n} posts, margem ${r.margem * 100}%, k desempenho=${r.desempenho.k}, k publico=${r.publico.k}`);

// ---------------------------------------------------------------- 10a - lift e IC

const MAPVAR = {
  plataforma: "platform", formato: "content_type", categoria: "content_category",
  faixa: "faixa_seguidores", idade: "audience_age_distribution",
  genero: "audience_gender_distribution", pais: "audience_location",
};
// o engine usa os rotulos da OS-08; as OS anteriores gravaram sem acento
const MAPFAIXA = {
  "até 50K": "ate 50K", "50–100K": "50-100K", "100–500K": "100-500K", "500K–1M": "500K-1M",
};

// referencia de lift/IC: os02 nivel1 (+ os02/plataforma.csv para a variavel platform)
// e os03c/bloco1_equivalencia.csv (mesmos numeros, com IC 95% e 90% bootstrap)
const refEquiv = new Map();
for (const o of lerCSV("os03c/bloco1_equivalencia.csv")) {
  if (o.metrica !== "taxa_engajamento") continue;
  refEquiv.set(o.variavel + "|" + o.segmento, o);
}
const refNivel1 = new Map();
for (const o of lerCSV("os02/nivel1.csv")) {
  if (o.metrica !== "taxa_engajamento" || o.nivel !== "1") continue;
  refNivel1.set(o.variaveis + "|" + o.segmento, o);
}
const refPlataforma = new Map();
for (const o of lerCSV("os02/plataforma.csv")) {
  if (o.metrica !== "taxa_engajamento") continue;
  refPlataforma.set(o.platform, o);
}

const compLift = [];
for (const bloco of [r.desempenho, r.publico]) {
  for (const s of bloco.segmentos) {
    if (s.vars.length !== 1) continue;            // nivel 1: um valor de uma variavel
    const varPy = MAPVAR[s.vars[0]];
    const segPy = s.vars[0] === "faixa" ? (MAPFAIXA[s.valores[0]] || s.valores[0]) : s.valores[0];
    const m = s.metricas.taxa;

    // lift: os02 (nivel1 ou plataforma.csv)
    const refL = s.vars[0] === "plataforma"
      ? Number(refPlataforma.get(segPy).razao_vs_media_geral)
      : Number(refNivel1.get(varPy + "|" + segPy).lift);
    // IC 95% sem correcao: bootstrap do os03c
    const eq = refEquiv.get(varPy + "|" + segPy);

    const lo = m.lift - 1.96 * m.ep, hi = m.lift + 1.96 * m.ep;
    compLift.push({
      variavel: s.vars[0], segmento: s.valores[0], n: s.n,
      lift: m.lift, liftPy: refL, difLift: Math.abs(m.lift - refL),
      icLo: lo, icLoPy: Number(eq.ic95_inferior), icHi: hi, icHiPy: Number(eq.ic95_superior),
      difIC: Math.max(Math.abs(lo - Number(eq.ic95_inferior)), Math.abs(hi - Number(eq.ic95_superior))),
    });
  }
}

const maxDifLift = Math.max(...compLift.map((c) => c.difLift));
const maxDifIC = Math.max(...compLift.map((c) => c.difIC));

tabela("10a.1 - Lift e IC 95% por valor de variavel (metrica taxa)", compLift, [
  { rotulo: "variavel", valor: (l) => l.variavel },
  { rotulo: "segmento", valor: (l) => l.segmento },
  { rotulo: "n", valor: (l) => l.n },
  { rotulo: "lift engine", valor: (l) => l.lift.toFixed(6) },
  { rotulo: "lift python", valor: (l) => l.liftPy.toFixed(6) },
  { rotulo: "dif lift", valor: (l) => l.difLift.toExponential(2) },
  { rotulo: "dif IC95", valor: (l) => l.difIC.toExponential(2) },
]);

// desde a OS-09 o lift é segmento vs. resto; validado em validar_os09.mjs
// checar("Lift por valor de variavel (taxa)", maxDifLift, 0, 1e-6);
checar("Limites do IC 95% sem correcao", maxDifIC, 0, 0.001);

// ---------------------------------------------------------------- 10a - patrocinio

const pat03 = lerCSV("os03/bloco1_comparacao_estratificada.csv");
const pat06 = lerCSV("os06/1b_comparacao_estratificada.csv");
const refTaxa = Number(pat03.find((o) => o.metrica === "taxa_engajamento").efeito_geral);
const refViews = Number(pat06.find((o) => o.metrica === "views").efeito_geral);
const refEstratos = pat03.find((o) => o.metrica === "taxa_engajamento");

const compPat = [
  { item: "efeito patrocinio - taxa", engine: r.patrocinio.metricas.taxa.efeito, python: refTaxa, fonte: "os03 bloco1" },
  { item: "efeito patrocinio - views", engine: r.patrocinio.metricas.views.efeito, python: refViews, fonte: "os06 item 1b" },
  { item: "estratos existentes", engine: r.patrocinio.estratosExistentes, python: Number(refEstratos.estratos_existentes), fonte: "os03 bloco1" },
  { item: "estratos usados", engine: r.patrocinio.estratosUsados, python: Number(refEstratos.estratos_usados), fonte: "os03 bloco1" },
  { item: "posts usados", engine: r.patrocinio.postsUsados, python: Number(refEstratos.posts_usados), fonte: "os03 bloco1" },
  { item: "patrocinados usados", engine: r.patrocinio.nPatrocinado, python: Number(refEstratos.n_patrocinado_usado), fonte: "os03 bloco1" },
  { item: "organicos usados", engine: r.patrocinio.nOrganico, python: Number(refEstratos.n_organico_usado), fonte: "os03 bloco1" },
];

tabela("10a.2 - Patrocinio (comparacao estratificada)", compPat, [
  { rotulo: "item", valor: (l) => l.item },
  { rotulo: "engine", valor: (l) => (Number.isInteger(l.python) ? l.engine : l.engine.toFixed(6)) },
  { rotulo: "python", valor: (l) => (Number.isInteger(l.python) ? l.python : l.python.toFixed(6)) },
  { rotulo: "dif", valor: (l) => Math.abs(l.engine - l.python).toExponential(2) },
  { rotulo: "fonte", valor: (l) => l.fonte },
]);

checar("Efeito do patrocinio em taxa", r.patrocinio.metricas.taxa.efeito, refTaxa, 0.001);
checar("Efeito do patrocinio em views", r.patrocinio.metricas.views.efeito, refViews, 0.001);
for (const c of compPat.slice(2)) checar(c.item, c.engine, c.python, 0);

// ---------------------------------------------------------------- 10b - vereditos

function contarTipos(blocos) {
  const c = { funciona: 0, nao_funciona: 0, sem_efeito: 0, inconclusivo: 0 };
  for (const b of [].concat(blocos)) {
    if (!b) continue;
    for (const s of b.segmentos) c[s.metricas.taxa.tipo]++;
  }
  return c;
}

const tiposTudo = contarTipos([r.desempenho, r.publico]);
const tiposPublico = contarTipos(r.publico);
const vPat = r.patrocinio.metricas.taxa;
const VEREDITO_PAT = { funciona: "Aprovado", nao_funciona: "Barrado", sem_efeito: "Barrado", inconclusivo: "Inconclusivo" };

const checks10b = [
  {
    item: "patrocinio", esperado: "Barrado", obtido: VEREDITO_PAT[vPat.tipo],
    detalhe: `efeito ${vPat.efeito.toFixed(6)}, IC equivalencia [${vPat.eqLo.toFixed(5)}; ${vPat.eqHi.toFixed(5)}] dentro de [0,90; 1,10]`,
  },
  {
    item: "nenhum positivo", esperado: "0", obtido: String(tiposTudo.funciona),
    detalhe: `${tiposTudo.sem_efeito} segmentos sem efeito comprovado`,
  },
  {
    item: "nenhum negativo", esperado: "0", obtido: String(tiposTudo.nao_funciona),
    detalhe: `${tiposTudo.inconclusivo} inconclusivos`,
  },
  {
    item: "publico", esperado: "Nenhum publico comprovado",
    obtido: tiposPublico.funciona === 0 ? "Nenhum publico comprovado" : `${tiposPublico.funciona} positivos`,
    detalhe: `${r.publico.segmentos.length} segmentos de publico avaliados`,
  },
  {
    item: "saude da base", esperado: "com alertas",
    obtido: r.saude.alertas > 0 ? "com alertas" : "sem alertas",
    detalhe: r.saude.testes.filter((t) => t.alerta).map((t) => t.nome).join("; "),
  },
];

tabela("10b - Vereditos esperados nesta base", checks10b, [
  { rotulo: "item", valor: (l) => l.item },
  { rotulo: "esperado", valor: (l) => l.esperado },
  { rotulo: "obtido", valor: (l) => l.obtido },
  { rotulo: "ok", valor: (l) => (l.obtido === l.esperado ? "sim" : "NAO") },
  { rotulo: "detalhe", valor: (l) => l.detalhe },
]);

for (const c of checks10b) {
  if (c.obtido !== c.esperado) {
    falhas++;
    console.log(`  FORA DO ESPERADO: ${c.item} -> ${c.obtido}`);
  }
}

// ---------------------------------------------------------------- 10d - filtro

const j90 = ENG.janelaUltimosDias(base, 90);
const r90 = ENG.analisar(base, { margem: 0.10, de: j90.de, ate: j90.ate });
const tipos90 = contarTipos([r90.desempenho, r90.publico]);

tabela("10d - Filtro 'Ultimos 90 dias'", [
  {
    recorte: "Toda a base", n: r.n, k: r.desempenho.k,
    estratos: r.patrocinio.estratosUsados,
    pat: r.patrocinio.metricas.taxa.efeito.toFixed(6),
    tipos: `${tiposTudo.funciona}/${tiposTudo.nao_funciona}/${tiposTudo.sem_efeito}/${tiposTudo.inconclusivo}`,
  },
  {
    recorte: "Ultimos 90 dias", n: r90.n, k: r90.desempenho.k,
    estratos: r90.patrocinio.estratosUsados,
    pat: Number.isFinite(r90.patrocinio.metricas.taxa.efeito) ? r90.patrocinio.metricas.taxa.efeito.toFixed(6) : "sem estratos",
    tipos: `${tipos90.funciona}/${tipos90.nao_funciona}/${tipos90.sem_efeito}/${tipos90.inconclusivo}`,
  },
], [
  { rotulo: "recorte", valor: (l) => l.recorte },
  { rotulo: "posts", valor: (l) => l.n },
  { rotulo: "k", valor: (l) => l.k },
  { rotulo: "estratos", valor: (l) => l.estratos },
  { rotulo: "efeito patroc.", valor: (l) => l.pat },
  { rotulo: "func/nao/sem/inconcl", valor: (l) => l.tipos },
]);

console.log(`\nJanela: ${new Date(j90.de).toISOString().slice(0, 10)} a ${new Date(j90.ate).toISOString().slice(0, 10)}`);
if (r90.n >= r.n) { falhas++; console.log("  FORA DO ESPERADO: o filtro de 90 dias nao reduziu o numero de posts"); }

// ---------------------------------------------------------------- resumo

tabela("Resumo das tolerancias", linhasRelatorio, [
  { rotulo: "item", valor: (l) => l.item },
  { rotulo: "dif", valor: (l) => l.dif.toExponential(2) },
  { rotulo: "tolerancia", valor: (l) => l.tolerancia },
  { rotulo: "ok", valor: (l) => (l.ok ? "sim" : "NAO") },
]);

console.log(falhas === 0
  ? "\nTodas as checagens passaram."
  : `\n${falhas} checagem(ns) fora do esperado.`);
process.exit(falhas === 0 ? 0 : 1);
