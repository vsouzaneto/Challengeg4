"use client";

// Carrega uma resposta da API e guarda carregando/erro; a última chamada vence.
import { useEffect, useState } from "react";

import { ApiError } from "@/lib/api";

export const errorMessage = (error: unknown): string => (error instanceof ApiError ? error.message : String(error));

export type ApiState<T> = { data: T | null; error: string | null; loading: boolean };

/** `load` nulo não busca nada (ex.: nenhum vendedor escolhido). `key` diz quando buscar de novo. */
export function useApi<T>(load: (() => Promise<T>) | null, key: string): ApiState<T> {
  const [state, setState] = useState<ApiState<T>>({ data: null, error: null, loading: Boolean(load) });

  useEffect(() => {
    if (!load) {
      setState({ data: null, error: null, loading: false });
      return undefined;
    }
    let active = true;
    setState({ data: null, error: null, loading: true });
    load()
      .then((data) => active && setState({ data, error: null, loading: false }))
      .catch((e: unknown) => active && setState({ data: null, error: errorMessage(e), loading: false }));
    return () => {
      active = false;
    };
    // `key` resume os parâmetros de `load`, que é uma função nova a cada render.
  }, [key]);

  return state;
}
