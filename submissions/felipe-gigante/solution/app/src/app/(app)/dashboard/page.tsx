import { dashboard, PERIODS } from "@/lib/analytics";
import { PageHeader, Section, Stat, Bar, Pill, fmt } from "@/components/ui";
import { PeriodTabs } from "@/components/PeriodTabs";
import { DecisionVolume, HBars, SERIES } from "@/components/charts";

export const dynamic = "force-dynamic";
const SENT_ORDER = ["Positive", "Neutral", "Frustrated", "Angry"];
const SENT_PT: Record<string, string> = { Positive: "Positivo", Neutral: "Neutro", Frustrated: "Frustrado", Angry: "Irritado" };

export default async function DashboardPage({ searchParams }: { searchParams: Promise<Record<string, string | undefined>> }) {
  const sp = await searchParams;
  const p = Number(sp.p);
  const days = (PERIODS as readonly number[]).includes(p) ? p : 30;
  const d = await dashboard(days);
  const sentTotal = d.sentiment.reduce((s, x) => s + x.n, 0);
  const decl = Object.fromEntries(d.declared.map((x) => [x.priority, x.n]));
  const declTotal = d.declared.reduce((s, x) => s + x.n, 0);
  const prTotal = d.priority.reduce((s, x) => s + x.n, 0);

  return (
    <>
      <PageHeader kicker="Visão do gestor" title="Dashboard operacional" actions={<PeriodTabs current={days} base="/dashboard" />}>
        Tickets reais do Dataset 1 (redistribuídos nos últimos 90 dias) + tickets criados ao vivo no portal. Toda decisão abaixo vem do pipeline de IA.
      </PageHeader>
      <div className="space-y-5 p-8">
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4 xl:grid-cols-6">
          <Stat label="Tickets recebidos" value={fmt.n(d.total)} sub={fmt.delta(d.total, d.totalPrev)} />
          <Stat label="Backlog aberto" value={fmt.n(d.backlog)} sub="novos + abertos + escalados + aguardando" />
          <Stat label="CSAT médio" value={d.csat ? d.csat.toFixed(2) : "—"} sub={`${fmt.n(d.csatN)} avaliações (1–5)`} />
          <Stat label="TTR mediano" value={Number.isNaN(d.ttrMedianH) ? "—" : `${d.ttrMedianH.toFixed(1)}h`} sub={`${fmt.n(d.ttrN)} tickets com duração válida`} hint="O Dataset 1 só tem duração válida em 1.402 tickets (49% têm TTR < FRT)." />
          <Stat label="FRT mediano" value={Number.isNaN(d.frtMedianS) ? "—" : d.frtMedianS < 60 ? `${d.frtMedianS.toFixed(0)}s` : `${(d.frtMedianS / 60).toFixed(0)} min`} sub={`${fmt.n(d.frtN)} tickets do portal (IA responde 1º)`} tone="good" hint="O Dataset 1 não tem timestamp de criação: FRT só é medido nos tickets do app." />
          <Stat label="Safe Resolution Rate" value={d.automated ? fmt.pct(d.safeResolutionRate) : "—"} sub={`North Star · ${d.automated} tickets automatizados`} tone="gold" hint="Resolvidos pela IA com CSAT ≥ 4 / tickets automatizados." />
        </div>

        <div className="grid gap-5 xl:grid-cols-3">
          <Section className="xl:col-span-2" kicker="Confidence gate" title="Volume por decisão da IA"
            right={<div className="flex gap-4 text-right text-xs">
              {(["auto", "suggest", "human"] as const).map((k) => (
                <div key={k}><div className="h-display text-lg font-extrabold" style={{ color: SERIES[k] }}>{fmt.pct(d.decision[k], 1)}</div><Pill v={k} /></div>
              ))}
            </div>}>
            <DecisionVolume data={d.series} hourly={d.bucket < 86_400_000} />
            <p className="mt-2 text-xs text-muted">
              Elegíveis para automação (risco ≠ alto): <b>{fmt.pct(d.eligible, 1)}</b>. Os {fmt.pct(d.decision.human, 0)} em HUMANO são majoritariamente reembolso, cancelamento e cobrança —
              a IA não decide; ela prepara o caso (categoria, resumo, artigo) e o humano assume.
            </p>
          </Section>
          <Section kicker="Human in the loop" title="Qualidade da IA">
            <div className="space-y-3 text-sm">
              {[
                ["AI Acceptance Rate", d.acceptance === null ? "—" : fmt.pct(d.acceptance), `${d.feedback.accepted} aceitas · ${d.feedback.edited} editadas · ${d.feedback.rejected} rejeitadas`],
                ["Confiança média", fmt.pct(d.avgConfidence), "score combinado classificador + KB"],
                ["KB Coverage", fmt.pct(d.kbCoverage), "tickets com artigo relevante na KB"],
                ["Guardrail trigger rate", fmt.pct(d.guardrailRate, 2), `${d.guardrailBlocks} bloqueios (injeção / fora de escopo)`],
                ["Knowledge Gaps pendentes", fmt.n(d.gaps.pending), `${d.gaps.occ} ocorrências agrupadas`],
                ["Devoluções downstream", fmt.n(d.feedback.downstream), "humano → IA conclui e pede CSAT"],
                ["Frustração detectada", fmt.n(d.feedback.frustration), "queda de sentimento na conversa"],
              ].map(([l, v, s]) => (
                <div key={l} className="flex items-baseline justify-between gap-3 border-b border-line pb-2 last:border-0">
                  <div><div className="font-medium text-ink">{l}</div><div className="text-xs text-muted">{s}</div></div>
                  <div className="h-display text-lg font-extrabold text-navy">{v}</div>
                </div>
              ))}
            </div>
          </Section>
        </div>

        <div className="grid gap-5 xl:grid-cols-3">
          <Section kicker="Top customer questions" title="Principais assuntos" className="xl:col-span-1">
            <div className="space-y-2.5">
              {d.topics.slice(0, 10).map((t) => (
                <div key={t.topic}>
                  <div className="flex justify-between text-sm"><span className="font-medium">{t.topic}</span>
                    <span className="text-muted">{fmt.n(t.n)} · {fmt.pct(t.share, 1)}{" "}
                      {t.trend !== null && Math.abs(t.trend) >= 1 && <span className={t.trend > 0 ? "text-rose-700" : "text-emerald-700"}>{t.trend > 0 ? "▲" : "▼"}{Math.abs(t.trend).toFixed(0)}%</span>}
                    </span>
                  </div>
                  <Bar value={t.share} max={d.topics[0]?.share || 1} color="bg-navy" />
                </div>
              ))}
            </div>
            <p className="mt-3 text-xs text-muted">Tendência vs período anterior. No dataset sintético os assuntos são uniformes (~6% cada) — por isso as variações são pequenas; em operação real, um pico aqui é sinal de bug ou incidente.</p>
          </Section>
          <Section kicker="Escalonamento upstream" title="Por que a IA passou para humano">
            <HBars data={d.escalationReasons.map((r) => ({ label: r.reason, value: r.n }))} color={SERIES.human} />
            <p className="mt-2 text-xs text-muted">Motivos normalizados numa taxonomia única (formulário + texto + sentimento). Um ticket conta uma vez por motivo; pode ter mais de um.</p>
          </Section>
          <Section kicker="Sinal em tempo real" title="Sentimento">
            <div className="space-y-3">
              {SENT_ORDER.map((s) => {
                const n = d.sentiment.find((x) => x.sentiment === s)?.n ?? 0;
                return (
                  <div key={s}>
                    <div className="flex justify-between text-sm"><span>{SENT_PT[s]}</span><span className="text-muted">{fmt.pct((n / (sentTotal || 1)) * 100, 1)} · {fmt.n(n)}</span></div>
                    <Bar value={n} max={sentTotal || 1} color={s === "Positive" ? "bg-emerald-600" : s === "Neutral" ? "bg-slate-400" : s === "Frustrated" ? "bg-amber-500" : "bg-rose-600"} />
                  </div>
                );
              })}
            </div>
            <div className="mt-5 border-t border-line pt-4">
              <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">Prioridade: declarada no dataset × calculada pela IA</div>
              <table className="w-full text-sm">
                <thead><tr className="text-left text-xs text-muted"><th className="font-medium">Prioridade</th><th className="font-medium">Dataset</th><th className="font-medium">IA</th></tr></thead>
                <tbody>
                  {["Critical", "High", "Medium", "Low"].map((pr) => (
                    <tr key={pr} className="border-t border-line">
                      <td className="py-1"><Pill v={pr} /></td>
                      <td>{fmt.pct(((decl[pr] ?? 0) / (declTotal || 1)) * 100, 0)}</td>
                      <td className="font-semibold">{fmt.pct(((d.priority.find((x) => x.priority === pr)?.n ?? 0) / (prTotal || 1)) * 100, 0)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="mt-2 text-xs text-muted">25% “Critical” no dataset = prioridade inflacionada (se tudo é crítico, nada é). A IA prioriza por sinais observáveis.</p>
            </div>
          </Section>
        </div>

        <div className="grid gap-5 xl:grid-cols-2">
          <Section kicker="Roteamento (classificador treinado no Dataset 2)" title="Categoria → time responsável">
            <table className="w-full text-sm">
              <thead><tr className="text-left text-xs uppercase tracking-wide text-muted"><th className="pb-2">Categoria</th><th className="pb-2">Time</th><th className="pb-2 text-right">Tickets</th><th className="pb-2 text-right">Confiança</th></tr></thead>
              <tbody>
                {d.categories.map((c) => (
                  <tr key={c.category} className="border-t border-line">
                    <td className="py-1.5 font-medium">{c.category}</td><td className="text-muted">{c.team}</td>
                    <td className="text-right">{fmt.n(c.n)}</td><td className="text-right">{fmt.pct(c.conf * 100)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="mt-3 text-xs text-muted">Cruzamento dos datasets: o modelo treinado em tickets de TI interna (D2) classifica ~88% dos tickets B2C de eletrônicos (D1) como Hardware. Taxonomia não transfere 1:1 → recomendação: re-treinar com labels da própria operação (o feedback do agente na Inbox gera esses labels).</p>
          </Section>
          <Section kicker="Automação está melhorando a experiência?" title="CSAT por decisão e por canal">
            <div className="grid grid-cols-2 gap-6">
              <div>
                <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">Por decisão do gate</div>
                {d.csatByDecision.map((c) => (
                  <div key={c.decision} className="mb-2 flex items-center justify-between text-sm"><Pill v={c.decision} /><span><b>{c.csat.toFixed(2)}</b> <span className="text-xs text-muted">n={c.n}</span></span></div>
                ))}
              </div>
              <div>
                <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">Por canal</div>
                {d.csatByChannel.map((c) => (
                  <div key={c.channel} className="mb-2 flex items-center justify-between text-sm"><span>{c.channel}</span><span><b>{c.csat.toFixed(2)}</b> <span className="text-xs text-muted">n={c.n}</span></span></div>
                ))}
              </div>
            </div>
            <p className="mt-2 text-xs text-muted">No histórico do dataset, nenhuma diferença de CSAT é estatisticamente significativa (ver Diagnóstico). A partir de agora, cada CSAT do portal registra se houve automação — é assim que se responde “automação × CSAT” com dados reais.</p>
          </Section>
        </div>
      </div>
    </>
  );
}
