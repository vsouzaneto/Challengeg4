// Paginação das tabelas: tamanho da página e quais números de página mostrar.

export const PAGE_SIZE = 25;

export const pageCount = (total: number, size: number = PAGE_SIZE): number => Math.max(1, Math.ceil(total / size));

/** A página (1, 2, …) em que está o item de posição `index` (0, 1, …). */
export const pageOf = (index: number, size: number = PAGE_SIZE): number => Math.floor(index / size) + 1;

/** Números de página a mostrar: a primeira, a última e as vizinhas da atual; `null` marca um salto (…). */
export function pageWindow(page: number, count: number): (number | null)[] {
  const wanted = new Set([1, count, page - 1, page, page + 1].filter((n) => n >= 1 && n <= count));
  const sorted = [...wanted].sort((a, b) => a - b);
  return sorted.flatMap((n, i) => (i > 0 && n - sorted[i - 1] > 1 ? [null, n] : [n]));
}
