// Persistência da configuração do gate (tabela meta). Cache curto: com várias instâncias
// serverless, uma mudança propaga em até 10s.
import { one, run } from "../db";
import { DEFAULT_GATE, sanitizeGate, type GateConfig } from "./gate";

let cache: { at: number; cfg: GateConfig } | null = null;

export async function getGateConfig(): Promise<GateConfig> {
  if (cache && Date.now() - cache.at < 10_000) return cache.cfg;
  const r = await one<{ value: string }>("SELECT value FROM meta WHERE key='gate_config'");
  const cfg = r ? sanitizeGate(JSON.parse(r.value)) : DEFAULT_GATE;
  cache = { at: Date.now(), cfg };
  return cfg;
}

export async function saveGateConfig(input: Partial<GateConfig>): Promise<GateConfig> {
  const cfg = sanitizeGate(input);
  await run("INSERT INTO meta (key, value) VALUES ('gate_config', ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", [JSON.stringify(cfg)]);
  cache = { at: Date.now(), cfg };
  return cfg;
}
