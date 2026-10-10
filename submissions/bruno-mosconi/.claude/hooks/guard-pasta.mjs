#!/usr/bin/env node
// Hook PreToolUse (Edit, Write, NotebookEdit): bloqueia edição de arquivos do repositório fora desta
// pasta de submissão. Motivo: CONTRIBUTING.md do desafio — "PRs que alteram outros arquivos serão rejeitados".
// Não cobre comandos de shell (Bash): esses não passam por este hook.
//
// Entrada (stdin, JSON do Claude Code): { tool_name, tool_input: { file_path | notebook_path }, cwd, ... }
// Saída: exit 0 = segue o fluxo normal de permissões; exit 2 + stderr = bloqueia e explica ao Claude.
// Falha fechada: se não der para entender a entrada, bloqueia.
//
// A raiz da submissão vem da posição deste arquivo (<submissão>/.claude/hooks/), não de variável de
// ambiente, para não depender de como o Claude Code define CLAUDE_PROJECT_DIR em subpastas.

import { existsSync, readFileSync, realpathSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SUBMISSION_ROOT = canonical(path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", ".."));
const CASE_INSENSITIVE = process.platform === "darwin" || process.platform === "win32";

function block(reason) {
  process.stderr.write(`[guard-pasta] ${reason}\n`);
  process.exit(2);
}

// Resolve symlinks no maior trecho existente do caminho e mantém o resto como está.
function canonical(p) {
  let head = path.resolve(p);
  const tail = [];
  while (!existsSync(head)) {
    const parent = path.dirname(head);
    if (parent === head) break;
    tail.unshift(path.basename(head));
    head = parent;
  }
  const real = existsSync(head) ? realpathSync.native(head) : head;
  return path.join(real, ...tail);
}

function norm(p) {
  return CASE_INSENSITIVE ? p.toLowerCase() : p;
}

function isInside(child, parent) {
  const rel = path.relative(norm(parent), norm(child));
  return rel === "" || (!rel.startsWith("..") && !path.isAbsolute(rel));
}

function findRepoRoot(start) {
  let dir = start;
  for (;;) {
    if (existsSync(path.join(dir, ".git"))) return dir;
    const parent = path.dirname(dir);
    if (parent === dir) return null;
    dir = parent;
  }
}

let input;
try {
  input = JSON.parse(readFileSync(0, "utf8"));
} catch {
  block("Entrada do hook ilegível; bloqueado por segurança.");
}

const toolInput = input?.tool_input ?? {};
const target = toolInput.file_path ?? toolInput.notebook_path;
if (typeof target !== "string" || target.length === 0) {
  block(`Não encontrei o caminho do arquivo em ${input?.tool_name ?? "ferramenta desconhecida"}; bloqueado por segurança.`);
}

const base = typeof input.cwd === "string" && input.cwd ? input.cwd : process.cwd();
const resolved = canonical(path.isAbsolute(target) ? target : path.resolve(base, target));
// Se a pasta ainda não estiver num repositório git, assume o layout <repo>/submissions/<nome>.
const repoRoot = canonical(findRepoRoot(SUBMISSION_ROOT) ?? path.resolve(SUBMISSION_ROOT, "..", ".."));

if (isInside(resolved, path.join(SUBMISSION_ROOT, ".git"))) {
  block(`Edição dentro de .git não é permitida: ${resolved}`);
}
if (isInside(resolved, SUBMISSION_ROOT)) process.exit(0);
if (isInside(resolved, repoRoot)) {
  block(
    `Arquivo fora de ${path.relative(repoRoot, SUBMISSION_ROOT)}/: ${path.relative(repoRoot, resolved)}. ` +
      "A regra do desafio rejeita PRs que alteram arquivos fora da pasta da submissão. " +
      "Se precisar mesmo, peça ao usuário para fazer à mão.",
  );
}
// Fora do repositório (ex.: memória do Claude em ~/.claude): não afeta o PR; segue as permissões normais.
process.exit(0);
