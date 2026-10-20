"use client";

import { useCallback, useEffect, useState } from "react";

import { emptyAssessment, type Assessment } from "./model";
import { readStore, setKey, writeStore, type Store } from "./storage";

export type Assessments = {
  /** As avaliações do vendedor, por oportunidade. */
  byId: Record<string, Assessment>;
  /** Muda a avaliação de uma oportunidade a partir do que já está guardado (várias respostas seguidas não se perdem). */
  update: (id: string, change: (current: Assessment) => Assessment) => void;
  /** Apaga as respostas de uma oportunidade e as ordens escolhidas que a incluíam. */
  remove: (id: string) => void;
  orderFor: (ids: string[]) => string[] | null;
  saveOrder: (ids: string[], order: string[]) => void;
  /** O navegador não guardou a última gravação (as respostas valem até fechar a página). */
  unsaved: boolean;
};

/** As avaliações de um vendedor. Lê o navegador depois de montar (sem divergir do servidor) e regrava a cada mudança. */
export function useAssessments(seller: string): Assessments {
  const [store, setStore] = useState<Store>({ assessments: {}, orders: {} });
  const [unsaved, setUnsaved] = useState(false);

  useEffect(() => setStore(readStore()), [seller]);

  const commit = useCallback((change: (current: Store) => Store) => {
    setStore((current) => {
      const next = change(current);
      setUnsaved(!writeStore(next));
      return next;
    });
  }, []);

  const update = useCallback((id: string, change: (current: Assessment) => Assessment) => commit((current) => ({
    ...current,
    assessments: {
      ...current.assessments,
      [seller]: { ...current.assessments[seller], [id]: change(current.assessments[seller]?.[id] ?? emptyAssessment(id)) },
    },
  })), [commit, seller]);

  const remove = useCallback((id: string) => commit((current) => ({
    ...current,
    assessments: {
      ...current.assessments,
      [seller]: Object.fromEntries(Object.entries(current.assessments[seller] ?? {}).filter(([other]) => other !== id)),
    },
    orders: {
      ...current.orders,
      [seller]: Object.fromEntries(
        Object.entries(current.orders[seller] ?? {}).filter(([key]) => !key.split("|").includes(id)),
      ),
    },
  })), [commit, seller]);

  const saveOrder = useCallback((ids: string[], order: string[]) => commit((current) => ({
    ...current,
    orders: { ...current.orders, [seller]: { ...current.orders[seller], [setKey(ids)]: order } },
  })), [commit, seller]);

  return {
    byId: store.assessments[seller] ?? {},
    update,
    remove,
    saveOrder,
    orderFor: (ids) => store.orders[seller]?.[setKey(ids)] ?? null,
    unsaved,
  };
}
