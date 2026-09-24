const productAliases = new Map([
  ["gtxpro", "GTX Pro"],
]);

const sectorAliases = new Map([
  ["technolgy", "technology"],
]);

function normalizedKey(value: string): string {
  return value.trim().replace(/\s+/gu, "").toLocaleLowerCase("pt-BR");
}

export function normalizeProduct(value: string | null | undefined): string | null {
  const normalized = value?.trim().replace(/\s+/gu, " ") ?? "";
  if (!normalized) {
    return null;
  }
  return productAliases.get(normalizedKey(normalized)) ?? normalized;
}

export function normalizeSector(value: string | null | undefined): string | null {
  const normalized = value?.trim().replace(/\s+/gu, " ") ?? "";
  if (!normalized) {
    return null;
  }
  return sectorAliases.get(normalizedKey(normalized)) ?? normalized;
}
