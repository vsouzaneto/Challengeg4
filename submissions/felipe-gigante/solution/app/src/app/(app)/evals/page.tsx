import metrics from "../../../../data/generated/classifier_metrics.json";
import { evalHistory, pipelineVersion } from "@/lib/evals";
import { PageHeader, Section, Stat, Pill, fmt } from "@/components/ui";
import { RunEvalsButton } from "@/components/RunEvalsButton";
import { CalibrationCurve } from "@/components/charts";
import { getGateConfig } from "@/lib/ai/gate-store";

export const dynamic = "force-dynamic";
type M = {
  classification: { n: number; accuracy: number; parityWithPython: number; macroF1: number };
  escalation: { recall: number; precision: number; unsafeAuto: number; n: number };
  safety: { detection: number; falsePositiveRate: number; n: number };
  rag: { retrievalHit: number; groundedness: number | null; n: number };
  gaps: { detection: number; n: number };
  priority: { exact: number; withinOne: number; n: number };
  behavioral: { pass: number; n: number };
  ms: number; llm: boolean;
};
type Det = { rows: { suite: string; input: string; pass: boolean; got: string; expected: string }[]; clsErrors: { text: string; expected: string; predicted: string; confidence: number }[] };
const p = (v: number) => fmt.pct(v * 100, 1);

export default async function EvalsPage() {
  const hist = await evalHistory();
  const gate = await getGateConfig();
  const last = hist[0];
  const m = last ? (JSON.parse(last.metrics) as M) : null;
  const det = last ? (JSON.parse(last.details) as Det) : null;
  const labels = metrics.dataset.labels;
  const cm = metrics.test.confusion_matrix;
  const maxCell = Math.max(...cm.flat());

  return (
    <>
      <PageHeader kicker="Qualidade da IA" title="Evals & regression testing" actions={<RunEvalsButton />}>
        Não são “3 exemplos manuais”: 7.176 tickets de teste do Dataset 2 (offline, Python) + 480 tickets de teste reexecutados no pipeline TypeScript + 58 casos comportamentais rotulados à mão.
        Versão atual: <code className="text-xs">{pipelineVersion(gate)}</code>
      </PageHeader>
      <div className="space-y-5 p-8">
        {m && (
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4 xl:grid-cols-7">
            <Stat label="Classificação" value={p(m.classification.accuracy)} sub={`macro-F1 ${p(m.classification.macroF1)} · n=${m.classification.n}`} />
            <Stat label="Paridade TS × Python" value={p(m.classification.parityWithPython)} sub="mesmas predições" tone="good" />
            <Stat label="Escalation recall" value={p(m.escalation.recall)} sub={`precisão ${p(m.escalation.precision)}`} />
            <Stat label="Automação insegura" value={m.escalation.unsafeAuto} sub="deveria escalar e foi AUTO" tone={m.escalation.unsafeAuto ? "bad" : "good"} hint="Métrica que bloqueia deploy" />
            <Stat label="Safety (injeção)" value={p(m.safety.detection)} sub={`falso positivo ${p(m.safety.falsePositiveRate)}`} />
            <Stat label="RAG retrieval hit" value={p(m.rag.retrievalHit)} sub={`groundedness ${m.rag.groundedness === null ? "—" : p(m.rag.groundedness)}`} />
            <Stat label="Prioridade (±1 nível)" value={p(m.priority.withinOne)} sub={`exata ${p(m.priority.exact)} · gaps ${p(m.gaps.detection)}`} />
          </div>
        )}

        <div className="grid gap-5 xl:grid-cols-2">
          <Section kicker="Dataset 2 · offline (analysis/train_classifier.py)" title="Comparação de approaches (validação)">
            <table className="w-full text-sm">
              <thead><tr className="text-left text-[11px] uppercase tracking-wide text-muted"><th className="pb-1 font-medium">Modelo</th><th className="text-right font-medium">Acurácia</th><th className="text-right font-medium">Macro-F1</th><th className="text-right font-medium">Treino</th></tr></thead>
              <tbody>{metrics.comparison.map((c) => (
                <tr key={c.model} className={`border-t border-line ${c.model === metrics.winner ? "font-semibold text-navy" : ""}`}>
                  <td className="py-1.5">{c.model}{c.model === metrics.winner && " ✓"}</td><td className="text-right">{c.val_accuracy}%</td><td className="text-right">{c.val_macro_f1}%</td><td className="text-right text-muted">{c.train_seconds ?? "—"}s</td>
                </tr>
              ))}</tbody>
            </table>
            <p className="mt-3 text-xs text-muted">
              Escolha: Logistic Regression — o SVM é 0,6 p.p. melhor, mas a LR dá probabilidades nativas (o gate depende delas), é trivial de portar para TypeScript
              (inferência local em ~0,04ms, custo zero) e explica a decisão pelos termos. Teste final (7.176 tickets nunca vistos): <b>{metrics.test.accuracy}%</b> acurácia, macro-F1 <b>{metrics.test.macro_f1}%</b>.
            </p>
            <table className="mt-4 w-full text-sm">
              <thead><tr className="text-right text-[11px] uppercase tracking-wide text-muted"><th className="text-left font-medium">Classe (teste)</th><th className="font-medium">Precisão</th><th className="font-medium">Recall</th><th className="font-medium">F1</th><th className="font-medium">Suporte</th></tr></thead>
              <tbody>{metrics.test.per_class.map((c) => (
                <tr key={c.label} className="border-t border-line text-right"><td className="py-1 text-left">{c.label}</td><td>{c.precision}%</td><td className={c.recall < 80 ? "font-semibold text-rose-700" : ""}>{c.recall}%</td><td>{c.f1}%</td><td className="text-muted">{c.support}</td></tr>
              ))}</tbody>
            </table>
            <p className="mt-2 text-xs text-muted">Por que não só acurácia: “Administrative rights” tem 90% de precisão mas <b>70% de recall</b> — 3 em 10 pedidos de admin são roteados errado (geralmente para Access/Hardware). Acurácia geral esconde isso.</p>
          </Section>

          <Section kicker="Calibração do Confidence Gate (validação)" title="Quanto confiar no modelo em cada faixa">
            <CalibrationCurve data={metrics.calibration_val} auto={gate.autoThreshold} suggest={gate.suggestThreshold} />
            <div className="mt-3 grid grid-cols-3 gap-3 text-center text-sm">
              {Object.entries(metrics.test.bands).map(([k, v]) => (
                <div key={k} className="rounded-lg bg-offwhite p-2"><div className="text-xs text-muted">{k}</div><div className="h-display text-lg font-extrabold text-navy">{v.accuracy}%</div><div className="text-[11px] text-muted">acurácia · {v.coverage}% dos tickets</div></div>
              ))}
            </div>
            <p className="mt-2 text-xs text-muted">Os thresholds do PRD (0,60 / 0,85) foram <b>validados</b>, não chutados: acima de 0,85 o classificador erra 2,7% (60% dos tickets); abaixo de 0,60 erra 44% — por isso vai para humano.</p>
          </Section>
        </div>

        <Section kicker="Dataset 2 · teste" title="Matriz de confusão (linhas = real, colunas = previsto)">
          <div className="overflow-x-auto">
            <table className="text-xs">
              <thead><tr><th />{labels.map((l) => <th key={l} className="w-20 px-1 pb-1 text-center font-medium text-muted">{l}</th>)}</tr></thead>
              <tbody>{cm.map((row, i) => (
                <tr key={labels[i]}><th className="pr-2 text-right font-medium text-muted">{labels[i]}</th>
                  {row.map((v, j) => (
                    <td key={j} className="h-9 w-20 border border-white text-center" title={`${labels[i]} → ${labels[j]}: ${v}`}
                      style={{ background: i === j ? `rgba(24,103,168,${0.15 + 0.85 * (v / maxCell)})` : v ? `rgba(176,64,90,${Math.min(0.85, 0.08 + v / 120)})` : "#f3f2f1", color: i === j && v / maxCell > 0.4 ? "#fff" : "#0f1b26" }}>{v}</td>
                  ))}
                </tr>
              ))}</tbody>
            </table>
          </div>
        </Section>

        {det && (
          <div className="grid gap-5 xl:grid-cols-[1.4fr_1fr]">
            <Section kicker="Golden set comportamental" title={`Casos (${m?.behavioral.pass}/${m?.behavioral.n} passaram)`}>
              <div className="max-h-[480px] overflow-y-auto">
                <table className="w-full text-xs">
                  <thead className="sticky top-0 bg-white"><tr className="text-left text-[11px] uppercase tracking-wide text-muted"><th className="pb-1" /><th className="font-medium">Suite</th><th className="font-medium">Entrada</th><th className="font-medium">Resultado</th></tr></thead>
                  <tbody>{det.rows.map((r, i) => (
                    <tr key={i} className="border-t border-line align-top">
                      <td className="py-1.5 pr-2">{r.pass ? "✅" : "❌"}</td><td className="pr-2"><Pill v={r.suite === "safety" ? "HIGH" : r.suite === "escalation" ? "human" : r.suite === "rag" ? "auto" : "MEDIUM"}>{r.suite}</Pill></td>
                      <td className="pr-2">{r.input}</td><td className="text-muted">{r.got}{!r.pass && <div className="text-rose-700">esperado: {r.expected}</div>}</td>
                    </tr>
                  ))}</tbody>
                </table>
              </div>
            </Section>
            <Section kicker="Regression testing" title="Histórico de execuções">
              <table className="w-full text-xs">
                <thead><tr className="text-left text-[11px] uppercase tracking-wide text-muted"><th className="font-medium">Quando</th><th className="font-medium">Versão</th><th className="text-right font-medium">Comport.</th><th className="text-right font-medium">Esc. recall</th><th className="text-right font-medium">Inseguro</th></tr></thead>
                <tbody>{hist.map((h) => {
                  const x = JSON.parse(h.metrics) as M;
                  return (
                    <tr key={h.id} className="border-t border-line">
                      <td className="py-1.5">{new Date(h.created_at).toLocaleString("pt-BR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" })}</td>
                      <td className="max-w-[180px] truncate text-muted" title={h.version}>{h.version}{x.llm ? " · LLM" : ""}</td>
                      <td className="text-right">{x.behavioral.pass}/{x.behavioral.n}</td><td className="text-right">{p(x.escalation.recall)}</td>
                      <td className={`text-right font-semibold ${x.escalation.unsafeAuto ? "text-rose-700" : "text-emerald-700"}`}>{x.escalation.unsafeAuto}</td>
                    </tr>
                  );
                })}</tbody>
              </table>
              <p className="mt-3 text-xs text-muted">
                A v2 deixou passar “Quero meu dinheiro de volta” como resposta AUTOMÁTICA (o regex de risco só conhecia “money back”). O eval pegou; a correção virou v3.
                <code className="ml-1">npm run eval</code> falha o build se houver qualquer automação insegura.
              </p>
            </Section>
          </div>
        )}
      </div>
    </>
  );
}
