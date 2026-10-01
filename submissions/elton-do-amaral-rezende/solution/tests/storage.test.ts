import { describe, expect, it } from 'vitest';
import { createStorage, storageKey } from '../src/state/storage';

const isString = (value: unknown): value is string => typeof value === 'string';

describe('persistência local', () => {
  it('isola vendedores e versões mesmo com separadores nos nomes', () => {
    expect(storageKey('v1', 'A:B')).not.toBe(storageKey('v1:A', 'B'));
    expect(storageKey('v1', 'A')).not.toBe(storageKey('v2', 'A'));
    expect(storageKey('v1', 'A')).not.toBe(storageKey('v1', 'B'));
  });
  it('preserva ações na sessão quando o navegador bloqueia o armazenamento', () => {
    const storage = createStorage(() => { throw new Error('Bloqueado'); });
    storage.write('key', 'ação');
    expect(storage.persistent).toBe(false);
    expect(storage.read('key', isString)).toBe('ação');
  });
  it('recupera de JSON corrompido e permite novos registros em sessão', () => {
    const storage = createStorage(() => ({ getItem: () => '{broken', setItem: () => {} }));
    expect(storage.read('key', isString)).toBeNull();
    expect(storage.persistent).toBe(false);
    storage.write('key', 'recuperado');
    expect(storage.read('key', isString)).toBe('recuperado');
  });
  it('rejeita conteúdo que não corresponde ao contrato solicitado', () => {
    const storage = createStorage(() => ({ getItem: () => '42', setItem: () => {} }));
    expect(storage.read('key', isString)).toBeNull();
    expect(storage.persistent).toBe(false);
  });
});
