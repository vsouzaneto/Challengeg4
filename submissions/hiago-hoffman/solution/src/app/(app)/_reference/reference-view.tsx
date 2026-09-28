"use client"

import { useState } from "react"
import { CircleAlertIcon, InboxIcon, MoreHorizontalIcon, PlusIcon, RotateCwIcon, SearchXIcon } from "lucide-react"
import { cn } from "@/lib/utils"

import { DataTable, type Column } from "@/components/data-table"
import { PageHeader } from "@/components/page-header"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Spinner } from "@/components/ui/spinner"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { toast } from "@/components/ui/toast"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { seed, statusMeta, type Item, type Status } from "./data"
import { ItemForm, type ItemValues } from "./item-form"

// Simula latência de API. Troque por chamadas reais (server actions, fetch).
const wait = (ms: number) => new Promise((r) => setTimeout(r, ms))
const dateFmt = new Intl.DateTimeFormat("pt-BR", { dateStyle: "medium", timeZone: "UTC" })

const simItems = [
  { value: "dados", label: "Com dados" },
  { value: "carregando", label: "Carregando" },
  { value: "vazio", label: "Vazio" },
  { value: "erro", label: "Erro" },
]

export function ReferenceView() {
  const [items, setItems] = useState(seed)
  const [tab, setTab] = useState<Status | "todos">("todos")
  const [query, setQuery] = useState("")
  const [sim, setSim] = useState("dados")
  const [refreshing, setRefreshing] = useState(false)
  const [sheetOpen, setSheetOpen] = useState(false)
  const [editing, setEditing] = useState<Item | null>(null)
  const [pending, setPending] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [deleting, setDeleting] = useState<Item | null>(null)

  const source = sim === "vazio" ? [] : items
  const q = query.trim().toLowerCase()
  const rows = source.filter(
    (i) =>
      (tab === "todos" || i.status === tab) &&
      (!q || i.nome.toLowerCase().includes(q) || i.email.toLowerCase().includes(q))
  )

  async function refresh() {
    setRefreshing(true)
    await wait(800)
    setRefreshing(false)
  }

  function openForm(item: Item | null) {
    setEditing(item)
    setSaveError(null)
    setSheetOpen(true)
  }

  async function save(values: ItemValues) {
    setSaveError(null)
    await wait(800)
    // Falha dentro de overlay aparece no próprio overlay (Alert), não em toast.
    if (values.email.endsWith("@erro.com")) {
      setSaveError("O servidor recusou a operação. Seus dados continuam no formulário.")
      return
    }
    const atualizadoEm = new Date().toISOString().slice(0, 10)
    setItems((prev) =>
      editing
        ? prev.map((i) => (i.id === editing.id ? { ...i, ...values, atualizadoEm } : i))
        : [{ id: crypto.randomUUID(), ...values, atualizadoEm }, ...prev]
    )
    setSheetOpen(false)
    toast.add({ type: "success", title: editing ? "Registro atualizado" : "Registro criado" })
  }

  function remove(item: Item) {
    const index = items.indexOf(item)
    setItems((prev) => prev.filter((i) => i.id !== item.id))
    setDeleting(null)
    toast.add({
      type: "success",
      title: "Registro excluído",
      description: item.nome,
      timeout: 10000,
      actionProps: {
        children: "Desfazer",
        onClick: () => setItems((prev) => prev.toSpliced(index, 0, item)),
      },
    })
  }

  const columns: Column<Item>[] = [
    {
      key: "nome",
      header: "Nome",
      className: "w-full max-w-0",
      cell: (i) => (
        <div className="flex min-w-0 flex-col">
          <span className="truncate font-medium">{i.nome}</span>
          <span className="truncate text-muted-foreground">{i.email}</span>
        </div>
      ),
    },
    {
      key: "status",
      header: "Status",
      cell: (i) => (
        <Badge variant="outline">
          <span className={cn("size-1.5 rounded-full", statusMeta[i.status].dot)} aria-hidden />
          {statusMeta[i.status].label}
        </Badge>
      ),
    },
    {
      key: "atualizado",
      header: "Atualizado em",
      className: "hidden md:table-cell",
      cell: (i) => (
        <span className="text-muted-foreground">{dateFmt.format(new Date(i.atualizadoEm))}</span>
      ),
    },
    {
      key: "acoes",
      header: <span className="sr-only">Ações</span>,
      className: "w-0 text-right",
      cell: (i) => (
        <DropdownMenu>
          <DropdownMenuTrigger
            render={<Button variant="ghost" size="icon-sm" aria-label={`Ações para ${i.nome}`} />}
          >
            <MoreHorizontalIcon />
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuGroup>
              <DropdownMenuItem onClick={() => openForm(i)}>Editar</DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            <DropdownMenuGroup>
              <DropdownMenuItem variant="destructive" onClick={() => setDeleting(i)}>
                Excluir
              </DropdownMenuItem>
            </DropdownMenuGroup>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    },
  ]

  // Dois vazios distintos: "ainda não há nada" (CTA de criação) vs "filtro sem resultado".
  const empty =
    source.length === 0 ? (
      <Empty className="border">
        <EmptyHeader>
          <EmptyMedia variant="icon">
            <InboxIcon />
          </EmptyMedia>
          <EmptyTitle>Nenhum registro ainda</EmptyTitle>
          <EmptyDescription>Crie o primeiro registro para começar.</EmptyDescription>
        </EmptyHeader>
        <EmptyContent>
          <Button onClick={() => openForm(null)}>
            <PlusIcon data-icon="inline-start" />
            Novo registro
          </Button>
        </EmptyContent>
      </Empty>
    ) : (
      <Empty className="border">
        <EmptyHeader>
          <EmptyMedia variant="icon">
            <SearchXIcon />
          </EmptyMedia>
          <EmptyTitle>Nenhum resultado</EmptyTitle>
          <EmptyDescription>Nada corresponde aos filtros atuais.</EmptyDescription>
        </EmptyHeader>
        <EmptyContent>
          <Button
            variant="outline"
            onClick={() => {
              setQuery("")
              setTab("todos")
            }}
          >
            Limpar filtros
          </Button>
        </EmptyContent>
      </Empty>
    )

  const tabs = [
    { value: "todos", label: "Todos", count: source.length },
    ...(Object.keys(statusMeta) as Status[]).map((s) => ({
      value: s,
      label: statusMeta[s].label,
      count: source.filter((i) => i.status === s).length,
    })),
  ]

  return (
    <>
      <PageHeader
        title="Referência"
        description="Padrões da fundação: tabela, filtros, formulário, overlays e estados."
        actions={
          <Button onClick={() => openForm(null)}>
            <PlusIcon data-icon="inline-start" />
            Novo registro
          </Button>
        }
      />

      <Tabs value={tab} onValueChange={(v) => setTab(v as Status | "todos")} className="gap-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <TabsList>
            {tabs.map((t) => (
              <TabsTrigger key={t.value} value={t.value}>
                {t.label}
                <span className="text-muted-foreground tabular-nums">{t.count}</span>
              </TabsTrigger>
            ))}
          </TabsList>
          <div className="flex w-full items-center gap-2 sm:w-auto">
            <Input
              type="search"
              aria-label="Buscar por nome ou e-mail"
              placeholder="Buscar"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="min-w-0 flex-1 sm:w-64 sm:flex-none"
            />
            <Select items={simItems} value={sim} onValueChange={(v) => setSim(v ?? "dados")}>
              <SelectTrigger aria-label="Simular estado" className="w-36 shrink-0">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  {simItems.map((s) => (
                    <SelectItem key={s.value} value={s.value}>
                      {s.label}
                    </SelectItem>
                  ))}
                </SelectGroup>
              </SelectContent>
            </Select>
            <Tooltip>
              <TooltipTrigger
                render={
                  <Button
                    variant="outline"
                    size="icon"
                    aria-label="Recarregar"
                    onClick={refresh}
                    disabled={refreshing}
                  />
                }
              >
                <RotateCwIcon />
              </TooltipTrigger>
              <TooltipContent>Recarregar</TooltipContent>
            </Tooltip>
          </div>
        </div>
        {tabs.map((t) => (
          <TabsContent key={t.value} value={t.value}>
            <DataTable
              columns={columns}
              rows={rows}
              getRowId={(i) => i.id}
              loading={sim === "carregando" || refreshing}
              error={sim === "erro"}
              onRetry={() => setSim("dados")}
              empty={empty}
            />
          </TabsContent>
        ))}
      </Tabs>

      <Sheet open={sheetOpen} onOpenChange={(open) => !pending && setSheetOpen(open)}>
        <SheetContent>
          <SheetHeader>
            <SheetTitle>{editing ? "Editar registro" : "Novo registro"}</SheetTitle>
            <SheetDescription>Campos obrigatórios são validados ao salvar.</SheetDescription>
          </SheetHeader>
          <div className="flex flex-1 flex-col gap-4 overflow-y-auto px-4">
            {saveError && (
              <Alert variant="destructive">
                <CircleAlertIcon />
                <AlertTitle>Não foi possível salvar</AlertTitle>
                <AlertDescription>{saveError}</AlertDescription>
              </Alert>
            )}
            <ItemForm
              key={editing?.id ?? "new"}
              id="item-form"
              defaultValues={editing ?? undefined}
              onSubmit={save}
              onPendingChange={setPending}
            />
          </div>
          <SheetFooter>
            <Button type="submit" form="item-form" disabled={pending}>
              {pending && <Spinner data-icon="inline-start" />}
              {pending ? "Salvando…" : "Salvar"}
            </Button>
          </SheetFooter>
        </SheetContent>
      </Sheet>

      <Dialog open={deleting !== null} onOpenChange={(open) => !open && setDeleting(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Excluir registro?</DialogTitle>
            <DialogDescription>
              {deleting?.nome} será removido. Você pode desfazer logo em seguida.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <DialogClose render={<Button variant="outline" />}>Cancelar</DialogClose>
            <Button variant="destructive" onClick={() => deleting && remove(deleting)}>
              Excluir
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
