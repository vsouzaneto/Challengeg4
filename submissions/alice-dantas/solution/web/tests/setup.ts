// Ambiente dos testes de tela: polyfills que o Radix e o cmdk usam e o jsdom não tem, e o roteador simulado.
import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";

import { navigation } from "./navigation";

vi.mock("next/navigation", () => import("./navigation"));

class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}
globalThis.ResizeObserver ??= ResizeObserverStub as unknown as typeof ResizeObserver;
Element.prototype.hasPointerCapture ??= () => false;
Element.prototype.setPointerCapture ??= () => {};
Element.prototype.releasePointerCapture ??= () => {};
Element.prototype.scrollIntoView ??= () => {};
window.matchMedia ??= (query: string) =>
  ({
    matches: false, media: query, onchange: null, addListener: () => {}, removeListener: () => {},
    addEventListener: () => {}, removeEventListener: () => {}, dispatchEvent: () => false,
  }) as MediaQueryList;

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  window.localStorage.clear();
  navigation.go("/carteira");
});
