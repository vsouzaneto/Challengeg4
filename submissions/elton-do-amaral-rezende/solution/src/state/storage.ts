import { STORAGE_SCHEMA_VERSION } from '../domain/config';

export function storageKey(datasetVersion: string, salesAgent: string): string {
  return `lead-scorer:v${STORAGE_SCHEMA_VERSION}:${encodeURIComponent(datasetVersion)}:${encodeURIComponent(salesAgent)}`;
}

export interface StorageAdapter {
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
}

/** Instância por sessão; o chamador exibe aviso quando persistent for false. */
export function createStorage(getStorage: () => StorageAdapter = () => window.localStorage) {
  const session = new Map<string, string>();
  let persistent = true;
  return {
    get persistent() { return persistent; },
    read<T>(key: string, isValid: (value: unknown) => value is T): T | null {
      try {
        let raw = session.get(key) ?? null;
        if (persistent) {
          try { raw = getStorage().getItem(key) ?? raw; }
          catch { persistent = false; }
        }
        if (raw === null) return null;
        const value: unknown = JSON.parse(raw);
        if (!isValid(value)) { persistent = false; return null; }
        session.set(key, raw);
        return value;
      } catch {
        persistent = false;
        return null;
      }
    },
    write<T>(key: string, value: T): void {
      const raw = JSON.stringify(value);
      session.set(key, raw);
      if (persistent) {
        try { getStorage().setItem(key, raw); }
        catch { persistent = false; }
      }
    },
  };
}
