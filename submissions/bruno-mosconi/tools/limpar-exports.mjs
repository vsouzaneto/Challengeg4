#!/usr/bin/env node
// Limpa os exports de chat (/export do Claude Code) antes de versionar. Reutilizável: rode de novo
// a cada export novo.
//
//   node tools/limpar-exports.mjs [--saida <pasta>] [--termo <texto>]... <arquivo.txt>...
//
// Sem --saida, reescreve os arquivos no lugar. Com --saida, grava as cópias limpas lá e não toca nos
// originais (para conferir com `diff -u original limpo` antes).
//
// Substitui:
//   - o conteúdo mostrado de um arquivo de configuração pessoal do Claude Code (~/.claude/settings*.json,
//     ~/.claude.json): a linha da ferramenta fica, o bloco abaixo dela vira [configuração pessoal removida]
//   - caminhos temporários do Claude (/private/tmp/claude-N/..., com o ID da sessão) → [removido]
//   - a pasta do ai-memory → [removido]
//   - IDs de sessão (UUID) → [removido]
//   - /Users/<usuário>/ → ~/  (e o mesmo caminho codificado, -Users-<usuário>-)
//   - e-mails (menos os de exceção, como o noreply do Co-Authored-By) → [removido]
//   - nome da organização e outros termos privados → [removido]. Eles vêm de --termo, do domínio do
//     `git config user.email` (se não for de e-mail pessoal) e de tools/.termos-privados (um termo
//     por linha). Esse arquivo fica no .gitignore: o nome da organização não entra no repositório.
//
// O export quebra linhas longas (cerca de 80 colunas, com recuo na linha seguinte); os padrões
// aceitam essa quebra no meio de um caminho ou de um UUID. No fim, lista o que sobrou para conferir.

import { execFileSync } from "node:child_process";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { userInfo } from "node:os";
import { basename, join } from "node:path";

const R = "[removido]";
const EMAIL_OK = new Set(["noreply@anthropic.com"]);

const args = process.argv.slice(2);
let out = null;
const terms = [];
const files = [];
for (let i = 0; i < args.length; i++) {
	if (args[i] === "--saida") out = args[++i];
	else if (args[i] === "--termo") terms.push(args[++i]);
	else files.push(args[i]);
}
if (!files.length) {
	console.error("Uso: node tools/limpar-exports.mjs [--saida <pasta>] [--termo <texto>]... <arquivo.txt>...");
	process.exit(1);
}

const user = userInfo().username;
let email = "";
try {
	email = execFileSync("git", ["config", "user.email"], { encoding: "utf8" }).trim();
} catch {}
const domain = email.split("@")[1]?.split(".")[0];
if (domain && !["gmail", "hotmail", "outlook", "icloud", "yahoo"].includes(domain)) terms.push(domain);

try {
	const local = readFileSync(new URL("./.termos-privados", import.meta.url), "utf8");
	terms.push(...local.split("\n").map((l) => l.trim()).filter((l) => l && !l.startsWith("#")));
} catch {}

const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
// A quebra de linha do export: fim de linha e recuo de 2 a 8 espaços.
const gap = String.raw`(?:\n[ ]{2,8})?`;
const wrapped = (s) => [...s].map(esc).join(gap);
const hex = (n) => Array(n).fill("[0-9a-f]").join(gap);
const home = `(?:/Users/${wrapped(user)}|~)`;

const RULES = [
	[
		"configuração pessoal",
		/(⏺ \w+\((?:~|\/Users\/[^/\s)]+)\/\.claude(?:\/settings[\w.-]*\.json|\.json)\)\n)(?! {2}⎿ {2}\[configuração pessoal removida\])(?:[^\n]+\n)+/g,
		(m, header) => `${header}  ⎿  [configuração pessoal removida]\n`,
	],
	[
		"caminho temporário do Claude",
		new RegExp(String.raw`/private/tmp/claude-\d+/(?:[A-Za-z0-9._/-]|\n[ ]{2,8}(?=[A-Za-z0-9._/-]))+`, "g"),
		R,
	],
	["pasta do ai-memory", new RegExp(`${home}/Library/Application Support/ai-memory`, "g"), R],
	["pasta do ai-memory", new RegExp(String.raw`${home}/\S*?ai-memory(?:/ai-memory)?`, "g"), R],
	["ID de sessão", new RegExp([hex(8), hex(4), hex(4), hex(4), hex(12)].join(`${gap}-${gap}`), "gi"), R],
	["/Users/<usuário>", new RegExp(`/Users/${wrapped(user)}`, "g"), "~"],
	["-Users-<usuário>-", new RegExp(`-Users-${wrapped(user)}-`, "g"), "-~-"],
	[
		"e-mail",
		/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g,
		(m) => (EMAIL_OK.has(m.toLowerCase()) ? m : R),
	],
	...terms.map((t) => ["organização ou termo", new RegExp(wrapped(t), "gi"), R]),
];

// O que ainda pode identificar alguém depois da limpeza (para conferir à mão).
const LEFT = [
	["usuário", new RegExp(esc(user), "i")],
	["/private/tmp/claude", /\/private\/tmp\/claude/],
	["UUID", /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i],
	["e-mail", /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/],
	...terms.map((t) => [t, new RegExp(esc(t), "i")]),
];

if (out) mkdirSync(out, { recursive: true });
let leftovers = 0;
for (const file of files) {
	let text = readFileSync(file, "utf8");
	const counts = {};
	for (const [name, re, to] of RULES)
		text = text.replace(re, (...m) => {
			counts[name] = (counts[name] ?? 0) + 1;
			return typeof to === "function" ? to(...m) : to;
		});
	writeFileSync(out ? join(out, basename(file)) : file, text);
	console.log(`\n${basename(file)}`);
	for (const [name, n] of Object.entries(counts)) console.log(`  ${name}: ${n}`);
	text.split("\n").forEach((line, i) => {
		for (const [name, re] of LEFT)
			if (re.test(line) && !(name === "e-mail" && [...line.matchAll(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g)].every((m) => EMAIL_OK.has(m[0].toLowerCase())))) {
				leftovers++;
				console.log(`  SOBROU (${name}) linha ${i + 1}: ${line.trim().slice(0, 100)}`);
			}
	});
}
console.log(leftovers ? `\n${leftovers} linha(s) para conferir à mão.` : "\nNada sobrou dos padrões conferidos.");
