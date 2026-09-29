"use client"

import { useActionState, useEffect } from "react"
import { CircleAlertIcon, CircleCheckIcon, RotateCcwIcon, UploadIcon } from "lucide-react"

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Field, FieldDescription, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { Spinner } from "@/components/ui/spinner"
import { toast } from "@/components/ui/toast"
import { atualizarBase, restaurarBase, type UploadResult } from "./actions"

const FILES = [
  { name: "sales_pipeline", hint: "opportunity_id, sales_agent, product, account, deal_stage, engage_date, close_date, close_value" },
  { name: "sales_teams", hint: "sales_agent, manager, regional_office" },
  { name: "products", hint: "product, series, sales_price" },
  { name: "accounts", hint: "account, sector, employees, revenue, office_location…" },
]

function useResultToast(result: UploadResult) {
  useEffect(() => {
    if (result?.ok) toast.add({ type: "success", title: "Modelo reaprendido", description: result.message })
  }, [result])
}

export function UploadForm({ needsToken, usingUpload }: { needsToken: boolean; usingUpload: boolean }) {
  const [result, submit, pending] = useActionState(atualizarBase, null)
  const [restoreResult, restore, restoring] = useActionState(restaurarBase, null)
  useResultToast(result)
  useResultToast(restoreResult)
  const shown = restoreResult ?? result

  return (
    <div className="flex flex-col gap-4">
      <form action={submit} className="flex flex-col gap-4">
        <FieldGroup className="grid gap-4 sm:grid-cols-2">
          {FILES.map((f) => (
            <Field key={f.name}>
              <FieldLabel htmlFor={f.name}>{f.name}.csv</FieldLabel>
              <Input id={f.name} name={f.name} type="file" accept=".csv,text/csv" required disabled={pending} />
              <FieldDescription>Colunas: {f.hint}</FieldDescription>
            </Field>
          ))}
          {needsToken && (
            <Field>
              <FieldLabel htmlFor="token">Token de administrador</FieldLabel>
              <Input id="token" name="token" type="password" required disabled={pending} autoComplete="off" />
            </Field>
          )}
        </FieldGroup>
        <div className="flex flex-wrap gap-2">
          <Button type="submit" disabled={pending}>
            {pending ? <Spinner data-icon="inline-start" /> : <UploadIcon data-icon="inline-start" />}
            {pending ? "Validando e reaprendendo…" : "Enviar e reaprender"}
          </Button>
        </div>
      </form>

      {usingUpload && (
        <form action={restore} className="flex flex-wrap items-end gap-2">
          {needsToken && (
            <Input name="token" type="password" required aria-label="Token de administrador" placeholder="Token" className="w-48" />
          )}
          <Button type="submit" variant="outline" disabled={restoring || pending}>
            {restoring ? <Spinner data-icon="inline-start" /> : <RotateCcwIcon data-icon="inline-start" />}
            Voltar para a base padrão
          </Button>
        </form>
      )}

      {shown && !shown.ok && (
        <Alert variant="destructive">
          <CircleAlertIcon />
          <AlertTitle>A base não foi trocada</AlertTitle>
          <AlertDescription>{shown.error}</AlertDescription>
        </Alert>
      )}
      {shown?.ok && (
        <Alert>
          <CircleCheckIcon />
          <AlertTitle>Base atualizada</AlertTitle>
          <AlertDescription>{shown.message}</AlertDescription>
        </Alert>
      )}
    </div>
  )
}
