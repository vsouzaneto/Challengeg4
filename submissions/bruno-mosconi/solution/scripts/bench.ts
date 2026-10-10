// npm run bench (CA10, CA15): mede o núcleo com os dados multiplicados por 1, 10 e 100, no Node e
// no Chromium (o mesmo código, empacotado pelo Vite). Grava analysis/saidas/bench.md.

import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { cpus, tmpdir } from "node:os";
import { join } from "node:path";
import { gzipSync } from "node:zlib";
import { chromium } from "@playwright/test";
import { build } from "vite";
import { parseDataset } from "../src/core/data.ts";
import { readRaw } from "../src/node/load.ts";
import { type BenchRow, bench, multiply } from "./bench-run.ts";

const raw = readRaw();
const node = bench(raw);

// O mesmo bench-run.ts, num arquivo só, para o navegador.
const out = mkdtempSync(join(tmpdir(), "bench-"));
await build({
	logLevel: "silent",
	configFile: false,
	build: {
		outDir: out,
		lib: {
			entry: new URL("./bench-run.ts", import.meta.url).pathname,
			name: "Bench",
			formats: ["iife"],
			fileName: () => "bench.js",
		},
	},
});
const browser = await chromium.launch();
const page = await browser.newPage();
await page.addScriptTag({
	content: readFileSync(join(out, "bench.js"), "utf8"),
});
const web = (await page.evaluate(
	(r) =>
		(globalThis as unknown as { Bench: { bench: typeof bench } }).Bench.bench(
			r,
		),
	raw,
)) as BenchRow[];
const version = browser.version();
await browser.close();

const gz = Object.fromEntries(
	[1, 10, 100].map((k) => [
		k,
		gzipSync(JSON.stringify(multiply(parseDataset(raw), k).deals)).length,
	]),
);
const n = (v: number) => Math.round(v).toLocaleString("pt-BR");
const mb = (b: number) =>
	(b / 1e6).toLocaleString("pt-BR", {
		maximumFractionDigits: 1,
		minimumFractionDigits: 1,
	});
let md = `# npm run bench\n\nNúcleo (\`src/core\`) na data padrão, com os negócios multiplicados por k (cópias com ID novo; mesmos 35 vendedores e 7 produtos). Mediana de 5 rodadas depois de 1 de aquecimento, em milissegundos. Máquina: ${cpus()[0]?.model ?? "?"}, ${cpus().length} núcleos; Node ${process.version}; Chromium ${version}.\n\n`;
md +=
	"- **Tela:** o que o app calcula ao abrir a semana de um vendedor: curva, score de todos, a lista dele e a equipe do gestor.\n";
md +=
	"- **Job:** o que um job diário calcularia: curva, score de todos e as listas dos 35 vendedores.\n";
md += "- **Foto:** os negócios em JSON, sem e com gzip.\n\n";
md +=
	"| k | Negócios | Em andamento (com data) | Curva (Node) | Tela (Node) | Tela (Chromium) | Job (Node) | Job (Chromium) | Foto JSON | Foto gzip |\n|---|---|---|---|---|---|---|---|---|---|\n";
node.forEach((r, i) => {
	const w = web[i] as BenchRow;
	md += `| ${r.scale} | ${n(r.deals)} | ${n(r.open)} | ${n(r.curveMs)} | ${n(r.screenMs)} | ${n(w.screenMs)} | ${n(r.jobMs)} | ${n(w.jobMs)} | ${mb(r.jsonBytes)} MB | ${mb(gz[r.scale] as number)} MB |\n`;
});
writeFileSync(new URL("../analysis/saidas/bench.md", import.meta.url), md);
console.log(md);
