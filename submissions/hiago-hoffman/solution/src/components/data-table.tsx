import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { ErrorState } from "@/components/error-state"

export type Column<T> = {
  key: string
  header: React.ReactNode
  cell: (row: T) => React.ReactNode
  className?: string
}

// Tabela com os estados obrigatórios: loading, error, empty e dados.
// ponytail: sem ordenação/paginação/seleção; adote @tanstack/react-table quando o produto precisar.
export function DataTable<T>({
  columns,
  rows,
  getRowId,
  loading,
  error,
  onRetry,
  empty,
}: {
  columns: Column<T>[]
  rows: T[]
  getRowId: (row: T) => string
  loading?: boolean
  error?: boolean
  onRetry?: () => void
  empty: React.ReactNode
}) {
  if (error) return <ErrorState onRetry={onRetry} />
  if (!loading && rows.length === 0) return empty

  return (
    <div className="overflow-hidden rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map((col) => (
              <TableHead key={col.key} className={col.className}>
                {col.header}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {loading
            ? Array.from({ length: 5 }, (_, i) => (
                <TableRow key={i}>
                  {columns.map((col) => (
                    <TableCell key={col.key}>
                      <Skeleton className="h-4 w-full max-w-32" />
                    </TableCell>
                  ))}
                </TableRow>
              ))
            : rows.map((row) => (
                <TableRow key={getRowId(row)}>
                  {columns.map((col) => (
                    <TableCell key={col.key} className={col.className}>
                      {col.cell(row)}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
        </TableBody>
      </Table>
    </div>
  )
}
