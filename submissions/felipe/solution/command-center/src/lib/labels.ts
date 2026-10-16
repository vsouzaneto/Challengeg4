/** Rótulos de filtro — sempre iniciar com maiúscula na UI. */
export function displayLabel(value: string): string {
  if (!value) return value;
  const trimmed = value.trim();
  if (/^[A-Z]/.test(trimmed) && trimmed.includes(" ")) return trimmed;
  if (/^[A-Z]/.test(trimmed)) return trimmed;
  return trimmed.charAt(0).toUpperCase() + trimmed.slice(1);
}
