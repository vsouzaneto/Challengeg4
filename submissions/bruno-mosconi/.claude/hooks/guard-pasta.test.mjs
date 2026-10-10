// Testes do hook guard-pasta. Rodar com: node --test .claude/hooks/
// Monta um repositório falso numa pasta temporária, copia o hook para dentro dele e simula
// as chamadas que o Claude Code faria.

import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { copyFileSync, mkdirSync, mkdtempSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { after, before, test } from "node:test";
import { fileURLToPath } from "node:url";

const HOOK_SRC = path.join(path.dirname(fileURLToPath(import.meta.url)), "guard-pasta.mjs");
let tmp, repo, sub, hook;

before(() => {
  tmp = mkdtempSync(path.join(os.tmpdir(), "guard-"));
  repo = path.join(tmp, "repo");
  sub = path.join(repo, "submissions", "bruno-mosconi");
  mkdirSync(path.join(repo, ".git"), { recursive: true });
  mkdirSync(path.join(sub, ".claude", "hooks"), { recursive: true });
  mkdirSync(path.join(sub, "solution"), { recursive: true });
  writeFileSync(path.join(repo, "README.md"), "raiz");
  hook = path.join(sub, ".claude", "hooks", "guard-pasta.mjs");
  copyFileSync(HOOK_SRC, hook);
  symlinkSync(path.join(repo, "README.md"), path.join(sub, "atalho-readme.md"));
});

after(() => rmSync(tmp, { recursive: true, force: true }));

function run(payload, raw) {
  const r = spawnSync(process.execPath, [hook], { input: raw ?? JSON.stringify(payload), encoding: "utf8" });
  return { code: r.status, err: r.stderr };
}

const write = (file_path, cwd = sub) => ({ tool_name: "Write", tool_input: { file_path }, cwd });

test("permite arquivo dentro da pasta (absoluto)", () => {
  assert.equal(run(write(path.join(sub, "solution", "a.ts"))).code, 0);
});

test("permite caminho relativo dentro da pasta", () => {
  assert.equal(run(write("solution/src/novo/b.ts")).code, 0);
});

test("bloqueia README da raiz do repositório", () => {
  const r = run(write("../../README.md"));
  assert.equal(r.code, 2);
  assert.match(r.err, /fora de submissions/);
});

test("bloqueia pasta de outro candidato", () => {
  assert.equal(run(write(path.join(repo, "submissions", "outra-pessoa", "x.md"))).code, 2);
});

test("bloqueia escrita por symlink que aponta para fora", () => {
  assert.equal(run(write(path.join(sub, "atalho-readme.md"))).code, 2);
});

test("bloqueia .git da raiz", () => {
  assert.equal(run(write(path.join(repo, ".git", "config"))).code, 2);
});

test("bloqueia NotebookEdit fora da pasta", () => {
  const r = run({ tool_name: "NotebookEdit", tool_input: { notebook_path: path.join(repo, "n.ipynb") }, cwd: sub });
  assert.equal(r.code, 2);
});

test("permite arquivo fora do repositório (não afeta o PR)", () => {
  assert.equal(run(write(path.join(tmp, "fora-do-repo.txt"))).code, 0);
});

test("bloqueia quando a entrada é ilegível", () => {
  assert.equal(run(null, "isto não é json").code, 2);
});

test("bloqueia quando falta o caminho", () => {
  assert.equal(run({ tool_name: "Edit", tool_input: {}, cwd: sub }).code, 2);
});

