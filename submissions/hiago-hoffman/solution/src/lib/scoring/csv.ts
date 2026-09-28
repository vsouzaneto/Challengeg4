// Parser CSV (RFC 4180): aspas, vírgulas e quebras de linha dentro de campos, BOM.
export function parseCsv(text: string): Record<string, string>[] {
  const rows: string[][] = []
  let row: string[] = []
  let field = ""
  let quoted = false

  const endRow = () => {
    row.push(field)
    field = ""
    if (row.some((c) => c !== "")) rows.push(row)
    row = []
  }

  for (let i = 0; i < text.length; i++) {
    const ch = text[i]
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') {
        field += '"'
        i++
      } else if (ch === '"') quoted = false
      else field += ch
    } else if (ch === '"') quoted = true
    else if (ch === ",") {
      row.push(field)
      field = ""
    } else if (ch === "\n" || ch === "\r") {
      if (ch === "\r" && text[i + 1] === "\n") i++
      endRow()
    } else field += ch
  }
  if (field !== "" || row.length) endRow()

  const [header, ...body] = rows
  if (!header) return []
  const keys = header.map((h) => h.replace(/^﻿/, "").trim())
  return body.map((r) => Object.fromEntries(keys.map((k, j) => [k, (r[j] ?? "").trim()])))
}
