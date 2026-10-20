// Ordenação de tabelas pelo cabeçalho: crescente, decrescente e de volta à ordem original (a da API).
import { useCallback, useMemo, useState } from "react";

export type SortDir = "asc" | "desc";
export type SortState<K extends string> = { key: K; dir: SortDir } | null;
export type SortValue = string | number | null | undefined;

/** O próximo estado ao clicar na coluna `key`: crescente, decrescente e, no terceiro clique, sem ordenação. */
export function nextSort<K extends string>(current: SortState<K>, key: K): SortState<K> {
  if (current?.key !== key) return { key, dir: "asc" };
  return current.dir === "asc" ? { key, dir: "desc" } : null;
}

const collator = new Intl.Collator("pt-BR", { numeric: true, sensitivity: "base" });

/** Cópia ordenada por uma coluna (estável; vazios sempre no fim, em qualquer sentido). Sem estado, devolve a ordem
 * recebida. */
export function sortRows<T, K extends string>(
  rows: readonly T[], state: SortState<K>, accessors: Record<K, (row: T) => SortValue>,
): T[] {
  if (!state) return [...rows];
  const read = accessors[state.key];
  const sign = state.dir === "asc" ? 1 : -1;
  return [...rows].sort((a, b) => {
    const x = read(a);
    const y = read(b);
    const emptyX = x === null || x === undefined;
    const emptyY = y === null || y === undefined;
    if (emptyX || emptyY) return emptyX === emptyY ? 0 : emptyX ? 1 : -1;
    if (typeof x === "number" && typeof y === "number") return (x - y) * sign;
    return collator.compare(String(x), String(y)) * sign;
  });
}

/** Estado de ordenação de uma tabela: as linhas ordenadas, a coluna atual e o clique do cabeçalho. */
export function useSort<T, K extends string>(
  rows: readonly T[], accessors: Record<K, (row: T) => SortValue>, onChange?: () => void,
) {
  const [state, setState] = useState<SortState<K>>(null);
  const sorted = useMemo(() => sortRows(rows, state, accessors), [rows, state, accessors]);
  const toggle = useCallback((key: K) => {
    setState((current) => nextSort(current, key));
    onChange?.();
  }, [onChange]);
  return { sorted, state, toggle };
}
