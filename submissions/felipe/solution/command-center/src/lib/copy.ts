/** Remove travessões tipográficos do texto exibido. */
export function noDash(text: string): string {
  return text.replace(/\s*[—–−]\s*/g, ". ").replace(/\s*\.\s*\./g, ".").trim();
}
