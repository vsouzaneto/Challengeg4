"use client";

// `meta` da API, buscado uma vez por sessão do navegador para o cabeçalho ("Dados até …").
import { useCallback, useEffect, useState } from "react";

import { api } from "@/lib/api";
import type { Meta } from "@/lib/contract";
import { errorMessage } from "@/lib/use-api";

let cached: Promise<Meta> | null = null;

/** Uma nova tentativa automática, logo depois da falha (a API pode estar subindo); depois, só a pedido. */
const AUTO_RETRY_MS = 3000;

export function useMeta(): { meta: Meta | null; error: string | null; retry: () => void } {
  const [meta, setMeta] = useState<Meta | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    let timer: ReturnType<typeof setTimeout> | undefined;
    cached ??= api.meta();
    cached.then(
      (value) => {
        if (!active) return;
        setError(null);
        setMeta(value);
      },
      (e: unknown) => {
        cached = null;
        if (!active) return;
        setError(errorMessage(e));
        if (attempt === 0) timer = setTimeout(() => setAttempt(1), AUTO_RETRY_MS);
      },
    );
    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [attempt]);

  const retry = useCallback(() => {
    setError(null);
    setAttempt((n) => n + 1);
  }, []);

  return { meta, error, retry };
}
