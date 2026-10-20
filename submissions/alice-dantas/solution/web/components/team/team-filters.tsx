"use client";

import { X } from "lucide-react";

import { FilterSelect } from "@/components/app/filter-select";
import { Button } from "@/components/ui/button";
import { UI, officeLabel } from "@/copy/pt-BR";

type Props = {
  managers: string[];
  offices: string[];
  manager: string | null;
  office: string | null;
  onChange: (changes: { gerente?: string | null; escritorio?: string | null }) => void;
};

/** Filtros de gerente e escritório (os que a API aceita), com as opções do cadastro de vendedores. */
export function TeamFilters({ managers, offices, manager, office, onChange }: Props) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
      <FilterSelect label={UI.filters.manager} options={managers} value={manager}
                    onChange={(value) => onChange({ gerente: value })} />
      <FilterSelect label={UI.filters.office} options={offices} value={office}
                    onChange={(value) => onChange({ escritorio: value })} optionLabel={officeLabel} />
      {(manager || office) && (
        <Button variant="ghost" className="w-fit" onClick={() => onChange({ gerente: null, escritorio: null })}>
          <X aria-hidden />
          {UI.filters.clear}
        </Button>
      )}
    </div>
  );
}
