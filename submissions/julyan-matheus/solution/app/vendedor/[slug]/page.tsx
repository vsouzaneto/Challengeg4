import { notFound } from "next/navigation";
import { AgentSelect } from "@/components/AgentSelect";
import { BucketTabs } from "@/components/BucketTabs";
import { ScorePill, TierBadge } from "@/components/Badges";
import { formatRefDate, usd } from "@/lib/format";
import { getAgent, getPipeline } from "@/lib/pipeline";

export const dynamicParams = false;

export function generateStaticParams() {
  return getPipeline().agents.map((a) => ({ slug: a.slug }));
}

export default async function VendedorPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const agent = getAgent(slug);
  if (!agent) notFound();
  const { ref, agents } = getPipeline();
  const c = agent.counts;

  const cards = [
    { label: "Total aberto", value: agent.total, hint: "Prospecting + Engaging" },
    { label: "Focar", value: c.Focar, hint: "recebem score" },
    { label: "Requalificar", value: c.Requalificar, hint: "sem conta" },
    { label: "Iniciar", value: c.Iniciar, hint: "sem primeiro contato" },
    { label: "Limpar", value: c.Limpar, hint: "> 138 dias" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Meu pipeline</h1>
          <p className="text-sm text-neutral-500">
            {agent.name} · gerente {agent.manager} · {agent.regional_office} · dados até {formatRefDate(ref)}
          </p>
        </div>
        <AgentSelect options={agents} value={agent.slug} basePath="/vendedor" />
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
        {cards.map((k) => (
          <div key={k.label} className="rounded-lg border border-neutral-200 bg-white px-4 py-3">
            <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">{k.label}</p>
            <p className="mt-1 text-2xl font-semibold tabular-nums">{k.value}</p>
            <p className="text-xs text-neutral-400">{k.hint}</p>
          </div>
        ))}
      </div>

      <section className="rounded-lg border border-neutral-900 bg-neutral-900 p-4 text-white">
        <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
          <h2 className="text-lg font-semibold">Hoje</h2>
          {agent.today.length > 0 && (
            <p className="text-xs text-neutral-300">Se só der tempo pra 3: maior valor esperado no seu Focar</p>
          )}
        </div>
        {agent.today.length === 0 ? (
          <p className="mt-3 text-sm text-neutral-300">
            Nada em Focar. Você tem {c.Requalificar} {c.Requalificar === 1 ? "deal" : "deals"} sem conta — vincular
            conta é a ação de hoje.
          </p>
        ) : (
          <ol className="mt-3 grid gap-3 sm:grid-cols-3">
            {agent.today.map((t, i) => (
              <li key={t.deal.opportunity_id} className="rounded-md bg-white p-3 text-neutral-900">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-neutral-500">#{i + 1}</span>
                  <ScorePill score={t.score} />
                </div>
                <p className="mt-2 font-semibold">{t.deal.account}</p>
                <p className="text-sm text-neutral-600">
                  {t.deal.product} · {t.daysOpen} dias · <span className="font-mono text-xs">{t.deal.opportunity_id}</span>
                </p>
                <p className="mt-2 text-lg font-semibold tabular-nums">{usd(t.expectedValue)}</p>
                <div className="mt-1">
                  <TierBadge tier={t.tier} />
                </div>
              </li>
            ))}
          </ol>
        )}
      </section>

      <BucketTabs rows={agent.rows} counts={agent.counts} focar={agent.focar} />
    </div>
  );
}
