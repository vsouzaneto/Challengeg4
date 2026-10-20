"use client";

// Produtos com poucas vendas fechadas no histórico. Só informa: não entra na classificação nem na ordem.
import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import { emptyFilter } from "@/lib/intelligence";

/** Abaixo disto o histórico do produto é pouco para servir de comparação. Com os dados de hoje só o GTK 500 (25
 * fechadas) fica abaixo; os outros produtos têm de 745 a 1.436. */
export const MIN_CLOSED_PER_PRODUCT = 100;

export type ProductSample = { closed: number; won: number };

let samples: Promise<Map<string, ProductSample>> | null = null;

/** Uma só leitura da Inteligência (histórico por produto), repartida entre todas as análises abertas. */
function loadSamples(): Promise<Map<string, ProductSample>> {
  if (samples) return samples;
  const request = api.intelligence(emptyFilter()).then((payload) => {
    const byProduct = new Map<string, ProductSample>();
    const product = payload.breakdowns.find((breakdown) => breakdown.dimension === "product");
    for (const segment of product?.segments ?? []) {
      if (segment.key !== null) byProduct.set(segment.key, { closed: segment.history.closed, won: segment.history.won });
    }
    return byProduct;
  });
  samples = request;
  request.catch(() => {
    if (samples === request) samples = null; // falhou: a próxima análise aberta tenta de novo
  });
  return request;
}

/** O histórico do produto, só quando é pequeno; `null` se o produto tem base suficiente, se não há produto ou se a
 * leitura falhou (a análise segue sem o aviso). */
export function useSmallProductSample(product: string | null): ProductSample | null {
  const [sample, setSample] = useState<ProductSample | null>(null);
  useEffect(() => {
    let active = true;
    setSample(null);
    if (product) {
      loadSamples().then((byProduct) => {
        const found = byProduct.get(product);
        if (active && found && found.closed < MIN_CLOSED_PER_PRODUCT) setSample(found);
      }, () => undefined);
    }
    return () => {
      active = false;
    };
  }, [product]);
  return sample;
}

/** Só para os testes: esquece a leitura guardada. */
export function resetProductSamples(): void {
  samples = null;
}
