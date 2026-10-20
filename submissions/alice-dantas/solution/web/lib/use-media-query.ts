"use client";

import { useSyncExternalStore } from "react";

/** Se a media query casa agora. No servidor (e no jsdom, sem `matchMedia` real) responde `false`: quem usa escolhe a
 * query para que `false` seja a versão de mesa, e só uma das duas versões fica no DOM. */
export function useMediaQuery(query: string): boolean {
  return useSyncExternalStore(
    (notify) => {
      const list = window.matchMedia(query);
      list.addEventListener("change", notify);
      return () => list.removeEventListener("change", notify);
    },
    () => window.matchMedia(query).matches,
    () => false,
  );
}

/** Abaixo do `md` do Tailwind (768 px). */
export const MOBILE_QUERY = "(max-width: 767px)";
