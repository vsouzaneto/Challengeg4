// Ordenação das tabelas: três cliques, vazios no fim e texto em pt-BR.
import { expect, test } from "vitest";

import { nextSort, sortRows, type SortState } from "@/lib/sort";

type Row = { name: string; n: number | null };
const rows: Row[] = [{ name: "Zé", n: 2 }, { name: "Ágata", n: null }, { name: "Bia", n: 10 }, { name: "Caio", n: 1 }];
const accessors = { name: (r: Row) => r.name, n: (r: Row) => r.n };

test("clicar na mesma coluna alterna crescente, decrescente e volta à ordem original", () => {
  let state: SortState<"name" | "n"> = null;
  state = nextSort(state, "n");
  expect(state).toEqual({ key: "n", dir: "asc" });
  state = nextSort(state, "n");
  expect(state).toEqual({ key: "n", dir: "desc" });
  expect(nextSort(state, "n")).toBeNull();
  expect(nextSort(state, "name")).toEqual({ key: "name", dir: "asc" });
});

test("sem ordenação, devolve a ordem recebida (a da API) sem alterar a lista original", () => {
  expect(sortRows(rows, null, accessors)).toEqual(rows);
  sortRows(rows, { key: "n", dir: "asc" }, accessors);
  expect(rows.map((r) => r.name)).toEqual(["Zé", "Ágata", "Bia", "Caio"]);
});

test("números pelo valor e vazios sempre no fim, nos dois sentidos", () => {
  expect(sortRows(rows, { key: "n", dir: "asc" }, accessors).map((r) => r.n)).toEqual([1, 2, 10, null]);
  expect(sortRows(rows, { key: "n", dir: "desc" }, accessors).map((r) => r.n)).toEqual([10, 2, 1, null]);
});

test("texto com a ordem do português (Á junto do A)", () => {
  expect(sortRows(rows, { key: "name", dir: "asc" }, accessors).map((r) => r.name)).toEqual(["Ágata", "Bia", "Caio", "Zé"]);
});
