"use client";
import { useMemo, useState, useTransition } from "react";
import { FlaskConical, RotateCcw, Save } from "lucide-react";
import { computeScore, decide, kbConfidenceOf, GATE_LIMITS, type GateConfig, type GateDecision } from "@/lib/ai/gate";
import { saveGateAction, testGateAction } from "@/app/(app)/confianca/actions";
import { SERIES } from "@/components/charts";

/** [confiança classificador, score KB, peso KB, frustrado, risco (0 baixo,1 médio,2 alto), bloqueado] */
export type Row = [number, number, number, number, number, number];
type Calib = { threshold: number; coverage: number; accuracy: number | null }[];
type Metrics = Awaited<ReturnType<typeof testGateAction>>;

const RISK = ["LOW", "MEDIUM", "HIGH"];
const LABEL: Record<GateDecision, string> = { auto: "AUTO", suggest: "SUGESTÃO", human: "HUMANO" };
const pct = (v: number, d = 0) => `${(v * 100).toLocaleString("pt-BR", { maximumFractionDigits: d, minimumFractionDigits: d })}%`;

function simulate(cfg: GateConfig, rows: Row[]) {
  const counts = { auto: 0, suggest: 0, human: 0 };
  const bins = Array.from({ length: 20 }, () => 0);
  const decisions: GateDecision[] = [];
  for (const [c, k, w, f, r, b] of rows) {
    const s = computeScore(cfg, c, kbConfidenceOf(cfg, k, w), f ? "Frustrated" : "Neutral").score;
    const d = decide(cfg, { score: s, riskLevel: RISK[r], mandatoryHuman: r === 2, inputAllowed: !b });
    counts[d]++;
    decisions.push(d);
    if (r !== 2 && !b) bins[Math.min(19, Math.floor(s * 20))]++;
  }
  return { counts, bins, decisions };
}

function nearest(cal: Calib, t: number) {
  return cal.reduce((best, x) => (Math.abs(x.threshold - t) < Math.abs(best.threshold - t) ? x : best), cal[0]);
}

export function GateTuner({ saved, defaults, rows, calibration, canEdit }: { saved: GateConfig; defaults: GateConfig; rows: Row[]; calibration: Calib; canEdit: boolean }) {
  const [cfg, setCfg] = useState<GateConfig>(saved);
  const [example, setExample] = useState({ cls: 0.9, kb: 0.8, frustrated: false, risk: "LOW" });
  const [test, setTest] = useState<Metrics | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [pending, start] = useTransition();

  const base = useMemo(() => simulate(saved, rows), [saved, rows]);
  const sim = useMemo(() => simulate(cfg, rows), [cfg, rows]);
  const changed = useMemo(() => sim.decisions.reduce((n, d, i) => n + (d !== base.decisions[i] ? 1 : 0), 0), [sim, base]);
  const dirty = JSON.stringify(cfg) !== JSON.stringify(saved);
  const total = rows.length || 1;
  const maxBin = Math.max(...sim.bins, 1);

  const ex = computeScore(cfg, example.cls, example.kb, example.frustrated ? "Frustrated" : "Neutral");
  const exDecision = decide(cfg, { score: ex.score, riskLevel: example.risk, mandatoryHuman: example.risk === "HIGH", inputAllowed: true });
  const autoCal = nearest(calibration, cfg.autoThreshold), sugCal = nearest(calibration, cfg.suggestThreshold);

  const set = (k: keyof GateConfig, v: number) => setCfg((c) => {
    const n = { ...c, [k]: v };
    if (k === "suggestThreshold" && v > n.autoThreshold) n.autoThreshold = v;
    if (k === "autoThreshold" && v < n.suggestThreshold) n.suggestThreshold = v;
    return n;
  });

  return (
    <div className="space-y-5">
      {/* 1. Fórmula + exemplo */}
      <div className="grid gap-5 xl:grid-cols-[1.2fr_1fr]">
        <section className="card p-5">
          <div className="kicker">Como o score é calculado</div>
          <div className="mt-3 rounded-xl bg-navy p-4 font-mono text-sm text-offwhite">
            score = <span className="text-gold">{cfg.wClassifier.toFixed(2)}</span> × confiança do classificador
            {" "}+ <span className="text-gold">{(1 - cfg.wClassifier).toFixed(2)}</span> × confiança da KB
            {" "}− <span className="text-gold">{cfg.frustrationPenalty.toFixed(2)}</span> se o cliente está frustrado
          </div>
          <ul className="mt-3 space-y-1.5 text-sm text-muted">
            <li><b className="text-ink">Confiança do classificador</b>: probabilidade da categoria (modelo treinado em 48k tickets; calibrado — ver abaixo).</li>
            <li><b className="text-ink">Confiança da KB</b>: similaridade × cobertura do melhor artigo ÷ {cfg.kbStrong} (limitada a 1). Sem artigo bom, não há resposta para dar.</li>
            <li><b className="text-ink">Antes do score</b>, regras de risco têm prioridade: risco alto (reembolso, cancelamento, jurídico, fraude…) ou guardrail → sempre HUMANO; risco médio (cobrança) → no máximo SUGESTÃO.</li>
          </ul>
          <div className="mt-4 grid grid-cols-3 gap-2 text-center text-xs">
            <div className="rounded-lg p-2 text-white" style={{ background: SERIES.human }}><b>HUMANO</b><div>score &lt; {pct(cfg.suggestThreshold)}</div></div>
            <div className="rounded-lg p-2 text-white" style={{ background: SERIES.suggest }}><b>SUGESTÃO</b><div>{pct(cfg.suggestThreshold)} – {pct(cfg.autoThreshold)}</div></div>
            <div className="rounded-lg p-2 text-white" style={{ background: SERIES.auto }}><b>AUTO</b><div>≥ {pct(cfg.autoThreshold)} e risco baixo</div></div>
          </div>
        </section>
        <section className="card p-5">
          <div className="kicker">Calculadora de um ticket</div>
          <div className="mt-3 space-y-3 text-sm">
            {([["cls", "Confiança do classificador"], ["kb", "Confiança da KB"]] as const).map(([k, l]) => (
              <label key={k} className="block">
                <div className="flex justify-between text-xs"><span className="text-muted">{l}</span><b>{pct(example[k])}</b></div>
                <input type="range" min={0} max={1} step={0.01} value={example[k]} onChange={(e) => setExample({ ...example, [k]: Number(e.target.value) })} className="w-full accent-[#c08e51]" />
              </label>
            ))}
            <div className="flex items-center gap-4 text-xs">
              <label className="flex items-center gap-1.5"><input type="checkbox" checked={example.frustrated} onChange={(e) => setExample({ ...example, frustrated: e.target.checked })} /> cliente frustrado</label>
              <select value={example.risk} onChange={(e) => setExample({ ...example, risk: e.target.value })} className="input w-40 py-1 text-xs">
                <option value="LOW">risco baixo</option><option value="MEDIUM">risco médio</option><option value="HIGH">risco alto</option>
              </select>
            </div>
            <div className="rounded-lg bg-offwhite p-3 font-mono text-xs">
              {ex.classifier.toFixed(2)} + {ex.kb.toFixed(2)}{ex.penalty ? ` − ${ex.penalty.toFixed(2)}` : ""} = <b className="text-navy">{ex.score.toFixed(2)}</b>
              <span className="ml-2 rounded px-2 py-0.5 font-sans font-bold text-white" style={{ background: SERIES[exDecision] }}>{LABEL[exDecision]}</span>
              {example.risk === "HIGH" && <div className="mt-1 font-sans text-muted">Risco alto ignora o score: sempre humano.</div>}
              {example.risk === "MEDIUM" && exDecision === "suggest" && ex.score >= cfg.autoThreshold && <div className="mt-1 font-sans text-muted">Score alto, mas risco médio limita a SUGESTÃO.</div>}
            </div>
          </div>
        </section>
      </div>

      {/* 2. Ajustes + impacto */}
      <div className="grid gap-5 xl:grid-cols-[360px_1fr]">
        <section className="card space-y-4 p-5">
          <div className="flex items-center justify-between">
            <div className="kicker">Ajustes</div>
            {dirty && <span className="rounded-full bg-gold-100 px-2 py-0.5 text-[11px] font-semibold text-navy">não salvo</span>}
          </div>
          {(Object.keys(GATE_LIMITS) as (keyof GateConfig)[]).map((k) => {
            const l = GATE_LIMITS[k];
            return (
              <label key={k} className="block">
                <div className="flex justify-between text-xs">
                  <span className="font-semibold text-ink">{l.label}</span>
                  <span><b className="text-navy">{cfg[k].toFixed(2)}</b>{cfg[k] !== defaults[k] && <span className="ml-1 text-muted">(padrão {defaults[k]})</span>}</span>
                </div>
                <input type="range" min={l.min} max={l.max} step={l.step} value={cfg[k]} onChange={(e) => set(k, Number(e.target.value))} className="mt-1 w-full accent-[#c08e51]" />
                <div className="text-[11px] text-muted">{l.help}</div>
              </label>
            );
          })}
          <div className="flex flex-wrap gap-2 border-t border-line pt-4">
            <button disabled={pending} onClick={() => start(async () => { setMsg(null); setTest(await testGateAction(cfg)); })} className="btn btn-navy"><FlaskConical size={14} />Testar no golden set</button>
            <button disabled={pending || !canEdit || !dirty} onClick={() => start(async () => {
              const r = await saveGateAction(cfg);
              if ("error" in r) setMsg(r.error ?? null);
              else { setTest(r.metrics); setMsg(`Salvo. ${r.reprocessed.toLocaleString("pt-BR")} tickets reprocessados e evals registrados no histórico.`); }
            })} className="btn btn-gold"><Save size={14} />Salvar e aplicar</button>
            <button disabled={pending} onClick={() => setCfg(defaults)} className="btn btn-ghost"><RotateCcw size={14} />Padrão</button>
          </div>
          {!canEdit && <p className="text-[11px] text-muted">Você pode simular e testar; salvar é restrito a gestores.</p>}
          {pending && <p className="text-xs text-muted">Processando…</p>}
          {msg && <p className="rounded-lg bg-emerald-50 px-3 py-2 text-xs text-emerald-800">{msg}</p>}
        </section>

        <div className="space-y-5">
          <section className="card p-5">
            <div className="kicker">Impacto simulado nos {rows.length.toLocaleString("pt-BR")} tickets reais</div>
            <div className="mt-3 grid grid-cols-3 gap-3">
              {(["auto", "suggest", "human"] as const).map((d) => {
                const delta = (sim.counts[d] - base.counts[d]) / total;
                return (
                  <div key={d} className="rounded-xl border border-line p-3">
                    <div className="text-[11px] font-bold" style={{ color: SERIES[d] }}>{LABEL[d]}</div>
                    <div className="h-display text-2xl font-extrabold text-navy">{pct(sim.counts[d] / total, 1)}</div>
                    <div className="text-xs text-muted">{sim.counts[d].toLocaleString("pt-BR")} tickets{Math.abs(delta) > 0.0005 && <b className={delta > 0 ? " text-navy" : " text-muted"}> · {delta > 0 ? "+" : ""}{pct(delta, 1)} vs salvo</b>}</div>
                  </div>
                );
              })}
            </div>
            <p className="mt-2 text-xs text-muted">{changed ? `${changed.toLocaleString("pt-BR")} tickets mudariam de decisão com esta configuração.` : "Nenhuma mudança em relação à configuração salva."}</p>

            <div className="mt-5 text-xs font-semibold uppercase tracking-wide text-muted">Distribuição do score (tickets elegíveis: sem risco alto)</div>
            <div className="relative mt-2 flex h-36 items-end gap-[2px]">
              {sim.bins.map((n, i) => {
                const mid = (i + 0.5) / 20;
                const zone: GateDecision = mid < cfg.suggestThreshold ? "human" : mid < cfg.autoThreshold ? "suggest" : "auto";
                return <div key={i} title={`${(i / 20).toFixed(2)}–${((i + 1) / 20).toFixed(2)}: ${n} tickets`} className="flex-1 rounded-t" style={{ height: `${Math.max(2, (n / maxBin) * 100)}%`, background: SERIES[zone], opacity: n ? 1 : 0.25 }} />;
              })}
              {[cfg.suggestThreshold, cfg.autoThreshold].map((t, i) => (
                <div key={i} className="absolute bottom-0 top-0 border-l-2 border-dashed border-navy" style={{ left: `${t * 100}%` }}>
                  <span className="absolute -top-1 left-1 whitespace-nowrap rounded bg-navy px-1 text-[10px] text-white">{i ? "máx" : "mín"} {t.toFixed(2)}</span>
                </div>
              ))}
            </div>
            <div className="mt-1 flex justify-between text-[10px] text-muted"><span>0</span><span>0,5</span><span>1</span></div>
            <p className="mt-2 text-xs text-muted">Nos tickets do Dataset 1 o texto é sintético, então a KB só é encontrada pelo assunto (peso 0,8) e o score raramente passa de 0,85 — por isso quase não há AUTO no histórico. Tickets reais do portal, com texto coerente, chegam a 0,9–1,0.</p>
          </section>

          <div className="grid gap-5 lg:grid-cols-2">
            <section className="card p-5">
              <div className="kicker">Quanto confiar em cada faixa</div>
              <p className="mt-1 text-xs text-muted">Evidência do classificador no conjunto de validação do Dataset 2 (7.176 tickets nunca vistos no treino).</p>
              <table className="mt-3 w-full text-sm">
                <tbody>
                  <tr className="border-b border-line"><td className="py-1.5">Confiança ≥ máximo ({autoCal.threshold})</td><td className="text-right"><b>{autoCal.accuracy}%</b> de acerto</td><td className="text-right text-muted">{autoCal.coverage}% dos tickets</td></tr>
                  <tr><td className="py-1.5">Confiança ≥ mínimo ({sugCal.threshold})</td><td className="text-right"><b>{sugCal.accuracy}%</b> de acerto</td><td className="text-right text-muted">{sugCal.coverage}% dos tickets</td></tr>
                </tbody>
              </table>
              <p className="mt-2 text-xs text-muted">Leitura: subir o máximo aumenta o acerto do que é automatizado, mas reduz o volume automatizado. A regra prática é só promover para AUTO faixas com ≥ 95% de acerto e 0 automações inseguras no golden set.</p>
            </section>
            <section className="card p-5">
              <div className="kicker">Golden set com esta configuração</div>
              {test ? (
                <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
                  {[
                    ["Automação insegura", String(test.escalation.unsafeAuto), test.escalation.unsafeAuto ? "text-rose-700" : "text-emerald-700"],
                    ["Escalation recall", pct(test.escalation.recall, 1), ""],
                    ["RAG retrieval hit", pct(test.rag.retrievalHit, 1), ""],
                    ["Casos aprovados", `${test.behavioral.pass}/${test.behavioral.n}`, ""],
                  ].map(([l, v, c]) => (
                    <div key={l} className="rounded-lg bg-offwhite p-2"><div className="text-[11px] text-muted">{l}</div><div className={`h-display text-xl font-extrabold text-navy ${c}`}>{v}</div></div>
                  ))}
                  {test.escalation.unsafeAuto > 0 && <p className="col-span-2 text-xs font-semibold text-rose-700">Esta configuração automatiza casos que deveriam ir para humano. Não aplique.</p>}
                </div>
              ) : <p className="mt-3 text-sm text-muted">Clique em “Testar no golden set” para rodar os 58 casos rotulados (segurança, escalonamento, RAG, gaps, prioridade) com estes valores — nada é salvo.</p>}
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
