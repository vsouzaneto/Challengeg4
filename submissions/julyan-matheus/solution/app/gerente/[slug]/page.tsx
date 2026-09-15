import Link from "next/link";
import { notFound } from "next/navigation";
import { AgentSelect } from "@/components/AgentSelect";
import { formatRefDate, pct, usd } from "@/lib/format";
import { agentSlug, getPipeline, type AgentView } from "@/lib/pipeline";

export const dynamicParams = false;

export function generateStaticParams() {
  return getPipeline().managers.map((m) => ({ slug: agentSlug(m) }));
}

/** Alert thresholds from spec §8 (Tela 2). */
const ALERT_REQUALIFICAR = 0.6;
const ALERT_LIMPAR = 0.8;

interface Row {
  agent: AgentView;
  total: number;
  focar: number;
  requalificar: number;
  iniciar: number;
  limpar: number;
  alive: number;
  ev: number;
  alerts: string[];
  noFocar: boolean;
}

function toRow(agent: AgentView): Row {
  const { Focar, Requalificar, Iniciar, Limpar } = agent.counts;
  const total = agent.total;
  const alerts: string[] = [];
  if (total > 0 && Requalificar / total > ALERT_REQUALIFICAR) alerts.push(`${pct(Requalificar / total)} sem conta`);
  if (total > 0 && Limpar / total > ALERT_LIMPAR) alerts.push(`${pct(Limpar / total)} passou de 138 dias`);
  return {
    agent,
    total,
    focar: Focar,
    requalificar: Requalificar,
    iniciar: Iniciar,
    limpar: Limpar,
    alive: total > 0 ? Focar / total : 0,
    ev: agent.focar.reduce((s, d) => s + d.expectedValue, 0),
    alerts,
    noFocar: Focar === 0,
  };
}

export default async function GerentePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const { ref, managers, agents } = getPipeline();
  const manager = managers.find((m) => agentSlug(m) === slug);
  if (!manager) notFound();

  const rows = agents
    .filter((a) => a.manager === manager)
    .map(toRow)
    .sort((a, b) => b.alive - a.alive || b.ev - a.ev);

  const team = rows.reduce(
    (t, r) => ({
      total: t.total + r.total,
      focar: t.focar + r.focar,
      requalificar: t.requalificar + r.requalificar,
      iniciar: t.iniciar + r.iniciar,
      limpar: t.limpar + r.limpar,
      ev: t.ev + r.ev,
    }),
    { total: 0, focar: 0, requalificar: 0, iniciar: 0, limpar: 0, ev: 0 },
  );
  const teamAlive = team.total > 0 ? team.focar / team.total : 0;
  const withoutFocar = rows.filter((r) => r.noFocar).length;
  const withAlert = rows.filter((r) => r.alerts.length > 0).length;
  const region = rows[0]?.agent.regional_office ?? "—";

  const cards = [
    { label: "Vendedores", value: String(rows.length), hint: `${withoutFocar} sem nada em Focar` },
    { label: "Total aberto", value: String(team.total), hint: "Prospecting + Engaging" },
    { label: "Pipeline vivo", value: pct(teamAlive), hint: `${team.focar} em Focar` },
    { label: "Valor esperado", value: usd(team.ev), hint: "soma do Focar" },
    { label: "Em alerta", value: String(withAlert), hint: "> 60% sem conta ou > 80% vencido" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Visão do gerente</h1>
          <p className="text-sm text-neutral-500">
            {manager} · {region} · dados até {formatRefDate(ref)}
          </p>
        </div>
        <AgentSelect
          options={managers.map((m) => ({ slug: agentSlug(m), name: m }))}
          value={slug}
          basePath="/gerente"
        />
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

      <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white">
        <table className="w-full text-sm">
          <thead className="bg-neutral-50">
            <tr>
              <th className={`${th} min-w-44`}>Vendedor</th>
              <th className={`${th} text-right`}>Total aberto</th>
              <th className={`${th} text-right`}>Focar</th>
              <th className={`${th} text-right`}>Requalificar</th>
              <th className={`${th} text-right`}>Iniciar</th>
              <th className={`${th} text-right`}>Limpar</th>
              <th className={`${th} text-right`}>% vivo</th>
              <th className={`${th} text-right`}>Valor esperado</th>
              <th className={th}>Alerta</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr
                key={r.agent.slug}
                className={`border-t border-neutral-100 ${
                  r.noFocar ? "bg-red-50/70" : r.alerts.length ? "bg-amber-50/60" : ""
                }`}
              >
                <td className={td}>
                  <Link href={`/vendedor/${r.agent.slug}`} className="font-medium hover:underline">
                    {r.agent.name}
                  </Link>
                  {r.noFocar && (
                    <span className="ml-2 inline-block rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800 ring-1 ring-inset ring-red-200">
                      0 em Focar
                    </span>
                  )}
                </td>
                <td className={num}>{r.total}</td>
                <td className={`${num} ${r.noFocar ? "font-semibold text-red-700" : "font-semibold"}`}>{r.focar}</td>
                <td className={num}>{r.requalificar}</td>
                <td className={num}>{r.iniciar}</td>
                <td className={num}>{r.limpar}</td>
                <td className={num}>
                  <AliveBar value={r.alive} muted={r.noFocar} />
                </td>
                <td className={num}>{usd(r.ev)}</td>
                <td className={`${td} text-xs text-amber-800`}>
                  {r.alerts.length ? r.alerts.join(" · ") : <span className="text-neutral-300">—</span>}
                </td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr className="border-t-2 border-neutral-300 bg-neutral-50 font-semibold">
              <td className={td}>Total do time</td>
              <td className={num}>{team.total}</td>
              <td className={num}>{team.focar}</td>
              <td className={num}>{team.requalificar}</td>
              <td className={num}>{team.iniciar}</td>
              <td className={num}>{team.limpar}</td>
              <td className={num}>
                <AliveBar value={teamAlive} />
              </td>
              <td className={num}>{usd(team.ev)}</td>
              <td className={td}></td>
            </tr>
          </tfoot>
        </table>
      </div>

      <p className="text-xs text-neutral-500">
        % vivo = Focar ÷ total aberto. Alerta quando mais de 60% do pipeline está sem conta ou mais de 80% passou de
        138 dias. Linha em vermelho: vendedor sem nenhum deal em Focar.
      </p>
    </div>
  );
}

const th = "px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500";
const td = "px-3 py-2 align-middle";
const num = `${td} text-right tabular-nums`;

function AliveBar({ value, muted = false }: { value: number; muted?: boolean }) {
  return (
    <span className="inline-flex items-center justify-end gap-2">
      <span className="hidden h-1.5 w-16 overflow-hidden rounded-full bg-neutral-200 sm:inline-block">
        <span
          className={`block h-full rounded-full ${muted ? "bg-red-400" : "bg-emerald-500"}`}
          style={{ width: `${Math.round(value * 100)}%` }}
        />
      </span>
      <span>{pct(value)}</span>
    </span>
  );
}
