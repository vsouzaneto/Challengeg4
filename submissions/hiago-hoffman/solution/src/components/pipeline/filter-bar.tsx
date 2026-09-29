"use client"

import { useTransition } from "react"
import { usePathname, useRouter } from "next/navigation"
import { XIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Combobox,
  ComboboxContent,
  ComboboxEmpty,
  ComboboxInput,
  ComboboxItem,
  ComboboxList,
} from "@/components/ui/combobox"
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Spinner } from "@/components/ui/spinner"
import type { BoardDTO, Filters } from "@/lib/server/view"

const ALL = "__todos"

// Filtros em cascata (região → manager → vendedor), guardados na URL para poder compartilhar a visão.
export function FilterBar({ options, filters }: { options: BoardDTO["options"]; filters: Filters }) {
  const router = useRouter()
  const pathname = usePathname()
  const [pending, startTransition] = useTransition()

  const apply = (next: Filters) => {
    const qs = new URLSearchParams()
    if (next.regiao) qs.set("regiao", next.regiao)
    if (next.manager) qs.set("manager", next.manager)
    if (next.vendedor) qs.set("vendedor", next.vendedor)
    startTransition(() => router.push(qs.size ? `${pathname}?${qs}` : pathname, { scroll: false }))
  }

  const managers = options.managers.filter((m) => !filters.regiao || m.region === filters.regiao)
  const agents = options.agents.filter(
    (a) => (!filters.regiao || a.region === filters.regiao) && (!filters.manager || a.manager === filters.manager),
  )
  const regionItems = [{ value: ALL, label: "Todas as regiões" }, ...options.regions.map((r) => ({ value: r, label: r }))]
  const managerItems = [{ value: ALL, label: "Todos os managers" }, ...managers.map((m) => ({ value: m.name, label: m.name }))]
  const active = !!(filters.regiao || filters.manager || filters.vendedor)

  return (
    <div className="flex flex-wrap items-center gap-2" role="search" aria-label="Filtrar oportunidades">
      <Select
        items={regionItems}
        value={filters.regiao ?? ALL}
        onValueChange={(v) => {
          const regiao = !v || v === ALL ? undefined : v
          apply({
            regiao,
            manager: managers.find((m) => m.name === filters.manager && (!regiao || m.region === regiao))?.name,
            vendedor: options.agents.find((a) => a.name === filters.vendedor && (!regiao || a.region === regiao))?.name,
          })
        }}
      >
        <SelectTrigger aria-label="Região" className="w-44">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            {regionItems.map((r) => (
              <SelectItem key={r.value} value={r.value}>
                {r.label}
              </SelectItem>
            ))}
          </SelectGroup>
        </SelectContent>
      </Select>

      <Select
        items={managerItems}
        value={filters.manager ?? ALL}
        onValueChange={(v) => {
          const manager = !v || v === ALL ? undefined : v
          apply({
            regiao: filters.regiao,
            manager,
            vendedor: options.agents.find((a) => a.name === filters.vendedor && (!manager || a.manager === manager))?.name,
          })
        }}
      >
        <SelectTrigger aria-label="Manager" className="w-48">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            {managerItems.map((m) => (
              <SelectItem key={m.value} value={m.value}>
                {m.label}
              </SelectItem>
            ))}
          </SelectGroup>
        </SelectContent>
      </Select>

      <div className="w-60">
        {/* key: recria a lista quando região/manager mudam, para nunca mostrar vendedores de fora do filtro */}
        <Combobox
          key={`${filters.regiao ?? ""}|${filters.manager ?? ""}`}
          items={agents.map((a) => a.name)}
          value={filters.vendedor ?? null}
          onValueChange={(v) => apply({ ...filters, vendedor: (v as string | null) ?? undefined })}
        >
          <ComboboxInput placeholder="Todos os vendedores" aria-label="Vendedor" showClear />
          <ComboboxContent>
            <ComboboxEmpty>Nenhum vendedor encontrado.</ComboboxEmpty>
            <ComboboxList>
              {(name: string) => (
                <ComboboxItem key={name} value={name}>
                  {name}
                </ComboboxItem>
              )}
            </ComboboxList>
          </ComboboxContent>
        </Combobox>
      </div>

      {active && (
        <Button variant="ghost" onClick={() => apply({})}>
          <XIcon data-icon="inline-start" />
          Limpar filtros
        </Button>
      )}
      {pending && <Spinner aria-label="Atualizando" />}
    </div>
  )
}
