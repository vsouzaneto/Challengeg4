export const usd = (n: number) => `$${Math.round(n).toLocaleString("en-US")}`;

export const pct = (x: number) => `${Math.round(x * 100)}%`;

export function formatRefDate(iso: string): string {
  const [y, m, d] = iso.split("-");
  return `${d}/${m}/${y}`;
}
