export function isEmbeddedInHost(
  search: string = typeof window === "undefined" ? "" : window.location.search,
  framed: boolean = typeof window !== "undefined" && window.self !== window.top,
): boolean {
  const embed = new URLSearchParams(search).get("embed");
  return framed || embed === "1";
}
