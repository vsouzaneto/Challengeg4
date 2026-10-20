// Filtros da Equipe: cada um restringe o outro, a partir do cadastro de vendedores.
import { expect, test } from "vitest";

import { filterOptions } from "@/lib/team";
import { pageCount, pageOf, pageWindow } from "@/lib/pagination";

import { sellers } from "./fixtures";

const all = sellers().sellers;

test("sem filtro: todos os gerentes e escritórios, em ordem alfabética", () => {
  expect(filterOptions(all, null, null)).toEqual({ managers: ["Mara Um", "Nina Dois"], offices: ["Central", "East"] });
});

test("gerente escolhido: só os escritórios dele; escritório escolhido: só os gerentes dele", () => {
  expect(filterOptions(all, "Mara Um", null).offices).toEqual(["Central"]);
  expect(filterOptions(all, null, "East").managers).toEqual(["Nina Dois"]);
});

test("combinação vinda de um link que não existe: o valor escolhido continua visível", () => {
  expect(filterOptions(all, "Mara Um", "East")).toEqual({ managers: ["Mara Um", "Nina Dois"], offices: ["Central", "East"] });
});

test("paginação: páginas, posição e números com saltos", () => {
  expect([pageCount(0, 25), pageCount(25, 25), pageCount(1291, 25)]).toEqual([1, 1, 52]);
  expect([pageOf(0, 25), pageOf(24, 25), pageOf(25, 25)]).toEqual([1, 1, 2]);
  expect(pageWindow(1, 1)).toEqual([1]);
  expect(pageWindow(1, 7)).toEqual([1, 2, null, 7]);
  expect(pageWindow(4, 7)).toEqual([1, null, 3, 4, 5, null, 7]);
  expect(pageWindow(3, 4)).toEqual([1, 2, 3, 4]);
});
