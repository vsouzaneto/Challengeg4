import Link from "next/link";
import diag from "../../../../data/generated/diagnostico.json";
import metrics from "../../../../data/generated/classifier_metrics.json";
import { PageHeader, Section, Pill } from "@/components/ui";
import { RoiCalculator } from "@/components/RoiCalculator";
import { HBars, SERIES } from "@/components/charts";

type Row = { n: number; median: number; p90: number };
const D = diag as unknown as {
  data_quality: Record<string, number> & { resolution_examples: string[] };
  bottlenecks: Record<string, { rows: Record<string, Row>; kruskal_p: number }> & {
    critical_vs_low: { critical_median: number; low_median: number; mannwhitney_p_critical_faster: number };
    worst_combo_permutation_p: number;
  };
  backlog: Record<string, number>;
  csat: Record<string, { kruskal_p: number; means: Record<string, number> | null }> & {
    spearman_resolution_hours: { rho: number; p: number }; model: { rf_accuracy_cv: number; majority_baseline: number };
  };
  opportunity: { subject: string; n: number; mode: string; why: string }[];
  mode_share: Record<string, number>;
  waste_defaults: Parameters<typeof RoiCalculator>[0]["d"];
};

const TABS = [
  { key: "gargalos", label: "Onde trava" },
  { key: "satisfacao", label: "Satisfação" },
  { key: "automacao", label: "O que automatizar" },
  { key: "roi", label: "Desperdício & ROI" },
  { key: "dados", label: "Limites dos dados" },
] as const;

const fmtPct = (v: number) => `${v.toLocaleString("pt-BR", { maximumFractionDigits: 0 })}%`;

function Headline({ value, label, tone }: { value: string; label: string; tone: string }) {
  return (
    <div className="card p-5">
      <div className={`h-display text-4xl font-extrabold ${tone}`}>{value}</div>
      <div className="mt-1 text-sm text-muted">{label}</div>
    </div>
  );
}

function Takeaway({ children }: { children: React.ReactNode }) {
  return <p className="mt-4 rounded-lg border-l-4 border-gold bg-gold-100/50 px-4 py-3 text-sm text-navy">{children}</p>;
}

export default async function DiagnosticoPage({ searchParams }: { searchParams: Promise<Record<string, string | undefined>> }) {
  const sp = await searchParams;
  const tab = TABS.find((t) => t.key === sp.tab)?.key ?? "gargalos";
  const bl = D.backlog;
  const pr = D.bottlenecks.priority.rows;
  const docShare = D.mode_share["Automática"] + D.mode_share["Assistida"];

  return (
    <>
      <PageHeader kicker="Para o Diretor de Operações" title="Diagnóstico operacional">
        8.469 tickets reais (Dataset 1). Cada afirmação tem teste estatístico por trás — detalhes em <code>analysis/diagnostico.py</code>.
      </PageHeader>
      <div className="space-y-5 p-8">
        <div className="grid grid-cols-2 gap-4 xl:grid-cols-4">
          <Headline value={fmtPct(bl.open_pct)} label="dos tickets estão sem nenhuma primeira resposta" tone="text-rose-700" />
          <Headline value={fmtPct(bl.critical_or_high_pct)} label="marcados como High/Critical — prioridade não prioriza" tone="text-navy" />
          <Headline value={fmtPct(docShare)} label="em assuntos que a IA pode resolver ou sugerir" tone="text-gold" />
          <Headline value="~2.600 h" label="por ano recuperáveis (≈ 1,5 pessoa em tempo integral)" tone="text-emerald-700" />
        </div>

        <nav className="flex flex-wrap gap-1 border-b border-line">
          {TABS.map((t) => (
            <Link key={t.key} href={`/diagnostico?tab=${t.key}`}
              className={`-mb-px border-b-2 px-4 py-2 text-sm font-semibold ${t.key === tab ? "border-gold text-navy" : "border-transparent text-muted hover:text-navy"}`}>
              {t.label}
            </Link>
          ))}
        </nav>

        {tab === "gargalos" && (
          <div className="grid gap-5 xl:grid-cols-2">
            <Section title="O gargalo é a fila, não um canal">
              <HBars height={140} unit="%" color={SERIES.human} data={[
                { label: "Sem 1ª resposta", value: bl.open_pct },
                { label: "Aguardando cliente", value: bl.pending_pct },
                { label: "Fechados", value: 100 - bl.open_pct - bl.pending_pct },
              ]} />
              <Takeaway>{bl.open_without_first_response.toLocaleString("pt-BR")} tickets nunca receberam resposta — {bl.open_critical} deles “Critical”. A IA responde 100% na hora e zera essa fila.</Takeaway>
            </Section>
            <Section title="Tempo de resolução por prioridade (mediana)">
              <HBars height={170} unit="h" color="#002037" data={["Critical", "High", "Medium", "Low"].map((p) => ({ label: p, value: pr[p].median }))} />
              <Takeaway>Critical resolve só ~1h mais rápido que Low. Canal e tipo de ticket também não fazem diferença (p &gt; 0,1). Quando metade é “urgente”, a fila vira ordem de chegada.</Takeaway>
            </Section>
          </div>
        )}

        {tab === "satisfacao" && (
          <div className="grid gap-5 xl:grid-cols-2">
            <Section title="CSAT médio por canal (1–5)">
              <HBars height={160} color="#002037" data={Object.entries(D.csat.channel.means ?? {}).map(([k, v]) => ({ label: k, value: v }))} />
              <Takeaway>Todos ≈ 3,0. A diferença não é estatisticamente significativa — o mesmo vale para tipo, prioridade, produto e tempo de resolução.</Takeaway>
            </Section>
            <Section title="Dá para prever a satisfação com esses dados?">
              <div className="grid grid-cols-2 gap-3 text-center">
                <div className="rounded-xl bg-offwhite p-4"><div className="h-display text-3xl font-extrabold text-navy">{D.csat.model.rf_accuracy_cv}%</div><div className="text-xs text-muted">acerto do modelo</div></div>
                <div className="rounded-xl bg-offwhite p-4"><div className="h-display text-3xl font-extrabold text-muted">{D.csat.model.majority_baseline}%</div><div className="text-xs text-muted">chutar sempre a mesma nota</div></div>
              </div>
              <Takeaway>O modelo é pior que o chute: o CSAT atual não explica nada. Recomendação: coletar CSAT por ticket com contexto (automação, categoria, sentimento) — o produto já faz isso.</Takeaway>
            </Section>
          </div>
        )}

        {tab === "automacao" && (
          <Section title="Modo recomendado por assunto">
            <div className="mb-4 grid grid-cols-3 gap-3">
              {([["Automática", "auto"], ["Assistida", "suggest"], ["Humano", "human"]] as const).map(([m, k]) => (
                <div key={m} className="rounded-xl border border-line p-3">
                  <div className="text-[11px] font-bold uppercase" style={{ color: SERIES[k] }}>{m}</div>
                  <div className="h-display text-2xl font-extrabold text-navy">{D.mode_share[m]}%</div>
                </div>
              ))}
            </div>
            <table className="w-full text-sm">
              <tbody>{D.opportunity.map((o) => (
                <tr key={o.subject} className="border-t border-line">
                  <td className="py-1.5 font-medium">{o.subject}</td>
                  <td><Pill v={o.mode === "Automática" ? "auto" : o.mode === "Assistida" ? "suggest" : "human"}>{o.mode}</Pill></td>
                  <td className="text-xs text-muted">{o.why}</td>
                </tr>
              ))}</tbody>
            </table>
            <Takeaway>Reembolso, cancelamento, pagamento e perda de dados ficam com humanos — a IA só prepara o caso. O pipeline chegou ao mesmo número de forma independente (55,7% humano).</Takeaway>
          </Section>
        )}

        {tab === "roi" && (
          <Section title="Horas e custo recuperáveis — ajuste as premissas">
            <RoiCalculator d={D.waste_defaults} modeShare={D.mode_share} classifierAccuracy={metrics.test.accuracy / 100} />
          </Section>
        )}

        {tab === "dados" && (
          <Section title="Por que algumas perguntas não têm resposta nestes dados">
            <ul className="grid gap-3 text-sm md:grid-cols-2">
              {[
                ["Amostra menor que o brief", `${D.data_quality.rows.toLocaleString("pt-BR")} tickets, não ~30 mil. O volume anual entra como premissa no ROI.`],
                ["Tempos inconsistentes", `${D.data_quality.closed_negative_resolution_pct}% dos fechados “resolvidos antes da 1ª resposta”. Sem horário de criação.`],
                ["CSAT aleatório", "Notas 1 a 5 com ~20% cada — padrão de dado gerado, não de cliente real."],
                ["Texto sem sinal", `Prever o tipo pelo texto acerta ${D.data_quality.text_to_type_accuracy}% — igual ao acaso (${D.data_quality.text_to_type_chance}%).`],
              ].map(([t, d]) => (
                <li key={t} className="rounded-lg border border-line p-3"><b className="text-navy">{t}</b><div className="mt-0.5 text-muted">{d}</div></li>
              ))}
            </ul>
            <Takeaway>Por isso o diagnóstico separa o que os dados sustentam (fila, prioridade, mix de assuntos) do que não sustentam (drivers de tempo e satisfação). Recomendação nº 1: instrumentar a operação para medir certo.</Takeaway>
          </Section>
        )}
      </div>
    </>
  );
}
