"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { Controller, useForm } from "react-hook-form"
import * as z from "zod"

import { Field, FieldDescription, FieldError, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { statusItems } from "./data"

const schema = z.object({
  nome: z.string().trim().min(3, "Informe o nome completo (mínimo 3 caracteres)."),
  email: z.email("Informe um e-mail válido, ex.: nome@empresa.com."),
  status: z.enum(["ativo", "pendente", "inativo"], "Selecione um status."),
})

export type ItemValues = z.infer<typeof schema>

// Padrão de formulário: RHF + Zod + Field. Label sempre visível, erro específico por campo.
// O botão de submit fica fora (SheetFooter/DialogFooter) e aponta para o form via `id`.
export function ItemForm({
  id,
  defaultValues,
  onSubmit,
  onPendingChange,
}: {
  id: string
  defaultValues?: Partial<ItemValues>
  onSubmit: (values: ItemValues) => Promise<void>
  onPendingChange: (pending: boolean) => void
}) {
  const form = useForm<ItemValues>({
    resolver: zodResolver(schema),
    defaultValues: { nome: "", email: "", status: "ativo", ...defaultValues },
  })

  async function submit(values: ItemValues) {
    onPendingChange(true)
    try {
      await onSubmit(values)
    } finally {
      onPendingChange(false)
    }
  }

  return (
    <form id={id} onSubmit={form.handleSubmit(submit)} noValidate>
      <FieldGroup>
        <Controller
          name="nome"
          control={form.control}
          render={({ field, fieldState }) => (
            <Field data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor={field.name}>Nome</FieldLabel>
              <Input {...field} id={field.name} aria-invalid={fieldState.invalid} autoComplete="name" />
              {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
            </Field>
          )}
        />
        <Controller
          name="email"
          control={form.control}
          render={({ field, fieldState }) => (
            <Field data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor={field.name}>E-mail</FieldLabel>
              <Input
                {...field}
                id={field.name}
                type="email"
                aria-invalid={fieldState.invalid}
                autoComplete="email"
              />
              <FieldDescription>Usado para notificações. Use @erro.com para simular falha.</FieldDescription>
              {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
            </Field>
          )}
        />
        <Controller
          name="status"
          control={form.control}
          render={({ field, fieldState }) => (
            <Field data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor={field.name}>Status</FieldLabel>
              <Select items={statusItems} value={field.value} onValueChange={field.onChange}>
                <SelectTrigger id={field.name} aria-invalid={fieldState.invalid} className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    {statusItems.map((s) => (
                      <SelectItem key={s.value} value={s.value}>
                        {s.label}
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
              {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
            </Field>
          )}
        />
      </FieldGroup>
    </form>
  )
}
