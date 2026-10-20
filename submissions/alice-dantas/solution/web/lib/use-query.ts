"use client";

// Estado da página na URL (vendedor, aba, filtros): dá para voltar, recarregar e guardar nos favoritos.
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback } from "react";

export function useQuery(): [URLSearchParams, (changes: Record<string, string | null>) => void] {
  const params = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const update = useCallback(
    (changes: Record<string, string | null>) => {
      const next = new URLSearchParams(params.toString());
      for (const [key, value] of Object.entries(changes)) {
        if (value) next.set(key, value);
        else next.delete(key);
      }
      const query = next.toString();
      router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
    },
    [params, router, pathname],
  );

  return [new URLSearchParams(params.toString()), update];
}
