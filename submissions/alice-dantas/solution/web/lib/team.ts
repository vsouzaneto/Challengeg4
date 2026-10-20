// Opções dos filtros da Equipe a partir do cadastro de vendedores (/api/sellers).
import type { Seller } from "@/lib/contract";

const sorted = (values: string[]): string[] => [...new Set(values)].sort((a, b) => a.localeCompare(b, "pt-BR"));

/** Cada filtro restringe o outro: com um gerente escolhido, só os escritórios em que ele tem vendedores;
 * com um escritório, só os gerentes dele. O valor escolhido sempre aparece, mesmo vindo de um link
 * com uma combinação que não existe (a API então responde a carteira vazia). */
export function filterOptions(sellers: Seller[], manager: string | null, office: string | null) {
  const managers = sorted(sellers.filter((s) => !office || s.office === office).map((s) => s.manager));
  const offices = sorted(sellers.filter((s) => !manager || s.manager === manager).map((s) => s.office));
  return {
    managers: manager && !managers.includes(manager) ? sorted([...managers, manager]) : managers,
    offices: office && !offices.includes(office) ? sorted([...offices, office]) : offices,
  };
}
