export type Status = "ativo" | "pendente" | "inativo"

export type Item = {
  id: string
  nome: string
  email: string
  status: Status
  atualizadoEm: string
}

export const statusMeta: Record<Status, { label: string; dot: string }> = {
  ativo: { label: "Ativo", dot: "bg-success" },
  pendente: { label: "Pendente", dot: "bg-warning" },
  inativo: { label: "Inativo", dot: "bg-muted-foreground" },
}

export const statusItems = Object.entries(statusMeta).map(([value, m]) => ({
  value: value as Status,
  label: m.label,
}))

export const seed: Item[] = [
  { id: "1", nome: "Ana Souza", email: "ana@exemplo.com", status: "ativo", atualizadoEm: "2026-09-24" },
  { id: "2", nome: "Bruno Lima", email: "bruno@exemplo.com", status: "pendente", atualizadoEm: "2026-09-22" },
  { id: "3", nome: "Carla Mendes de Albuquerque Figueiredo Nascimento", email: "carla.mendes.albuquerque@exemplo-empresa-longa.com.br", status: "ativo", atualizadoEm: "2026-09-20" },
  { id: "4", nome: "Diego Rocha", email: "diego@exemplo.com", status: "inativo", atualizadoEm: "2026-09-18" },
  { id: "5", nome: "Elisa Prado", email: "elisa@exemplo.com", status: "pendente", atualizadoEm: "2026-09-15" },
]
