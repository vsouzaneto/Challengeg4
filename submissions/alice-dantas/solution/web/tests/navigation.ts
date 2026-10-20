// Roteador do Next para os testes: a URL fica em memória e os componentes re-renderizam quando ela muda.
import { useSyncExternalStore } from "react";

let url = new URL("http://localhost/carteira");
let params = new URLSearchParams();
const listeners = new Set<() => void>();

const subscribe = (listener: () => void) => {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
};

function go(href: string) {
  url = new URL(href, url);
  params = new URLSearchParams(url.search);
  listeners.forEach((listener) => listener());
}

export const navigation = {
  go,
  get pathname() {
    return url.pathname;
  },
  get params() {
    return params;
  },
};

const router = { push: go, replace: go, prefetch: () => {}, back: () => {}, forward: () => {}, refresh: () => {} };

export const useRouter = () => router;
export const usePathname = () => useSyncExternalStore(subscribe, () => url.pathname);
export const useSearchParams = () => useSyncExternalStore(subscribe, () => params);
export function redirect(href: string): never {
  throw new Error(`redirect:${href}`);
}
