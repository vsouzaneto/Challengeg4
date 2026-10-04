"use client";
import { useMemo, useState } from "react";

type Defaults = {
  annual_tickets: number; aht_minutes: Record<string, number>; channel_share: Record<string, number>; triage_minutes: number;
  hour_cost_brl: number; auto_containment: number; assist_aht_reduction: number; human_prep_reduction: number;
  ai_cost_per_ticket_brl: number; platform_cost_month_brl: number; human_review_minutes_auto: number;
};

const brl = (v: number) => v.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });
const n0 = (v: number) => v.toLocaleString("pt-BR", { maximumFractionDigits: 0 });

function Slider({ label, value, set, min, max, step, fmt }: { label: string; value: number; set: (v: number) => void; min: number; max: number; step: number; fmt: (v: number) => string }) {
  return (
    <label className="block">
      <div className="flex justify-between text-xs"><span className="text-muted">{label}</span><b className="text-navy">{fmt(value)}</b></div>
      <input type="range" min={min} max={max} step={step} value={value} onChange={(e) => set(Number(e.target.value))} className="mt-1 w-full accent-[#c08e51]" />
    </label>
  );
}

export function RoiCalculator({ d, modeShare, classifierAccuracy }: { d: Defaults; modeShare: Record<string, number>; classifierAccuracy: number }) {
  const [tickets, setTickets] = useState(d.annual_tickets);
  const [hourCost, setHourCost] = useState(d.hour_cost_brl);
  const [triage, setTriage] = useState(d.triage_minutes);
  const [auto, setAuto] = useState(modeShare["Automática"] / 100);
  const [assist, setAssist] = useState(modeShare["Assistida"] / 100);
  const [containment, setContainment] = useState(d.auto_containment);
  const [assistRed, setAssistRed] = useState(d.assist_aht_reduction);
  const [aht, setAht] = useState(d.aht_minutes);

  const r = useMemo(() => {
    const human = Math.max(0, 1 - auto - assist);
    const wAht = Object.entries(d.channel_share).reduce((s, [c, sh]) => s + sh * (aht[c] ?? 10), 0);
    const baselineH = (tickets * (wAht + triage)) / 60;
    const repetitiveH = (tickets * (auto + assist) * (wAht + triage)) / 60;
    const triageH = (tickets * triage * classifierAccuracy) / 60;
    const autoH = (tickets * auto * (containment * wAht - d.human_review_minutes_auto)) / 60;
    const assistH = (tickets * assist * wAht * assistRed) / 60;
    const humanH = (tickets * human * wAht * d.human_prep_reduction) / 60;
    const saved = triageH + autoH + assistH + humanH;
    const benefit = saved * hourCost;
    const cost = tickets * d.ai_cost_per_ticket_brl + d.platform_cost_month_brl * 12;
    return { human, wAht, baselineH, repetitiveH, triageH, autoH, assistH, humanH, saved, benefit, cost, roi: (benefit - cost) / cost, fte: saved / 1760 };
  }, [tickets, hourCost, triage, auto, assist, containment, assistRed, aht, d, classifierAccuracy]);

  return (
    <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
      <div className="space-y-3 rounded-xl bg-offwhite p-4">
        <div className="text-xs font-bold uppercase tracking-wide text-navy">Premissas (ajuste ao vivo)</div>
        <Slider label="Tickets por ano" value={tickets} set={setTickets} min={5000} max={100000} step={1000} fmt={n0} />
        <Slider label="Custo/hora do agente (carregado)" value={hourCost} set={setHourCost} min={20} max={150} step={1} fmt={brl} />
        <Slider label="Minutos de triagem manual / ticket" value={triage} set={setTriage} min={0} max={8} step={0.5} fmt={(v) => `${v} min`} />
        {Object.keys(aht).map((c) => (
          <Slider key={c} label={`AHT ${c}`} value={aht[c]} set={(v) => setAht({ ...aht, [c]: v })} min={3} max={30} step={1} fmt={(v) => `${v} min`} />
        ))}
        <Slider label="% tickets em modo AUTO" value={auto} set={setAuto} min={0} max={0.6} step={0.01} fmt={(v) => `${(v * 100).toFixed(0)}%`} />
        <Slider label="% tickets em modo ASSISTIDO" value={assist} set={setAssist} min={0} max={0.7} step={0.01} fmt={(v) => `${(v * 100).toFixed(0)}%`} />
        <Slider label="Contenção real do AUTO (resolve sem humano)" value={containment} set={setContainment} min={0.2} max={0.9} step={0.05} fmt={(v) => `${(v * 100).toFixed(0)}%`} />
        <Slider label="Redução de AHT com resposta sugerida" value={assistRed} set={setAssistRed} min={0.1} max={0.6} step={0.05} fmt={(v) => `${(v * 100).toFixed(0)}%`} />
      </div>
      <div>
        <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">
          <div className="rounded-xl bg-navy p-4 text-offwhite"><div className="text-[11px] uppercase tracking-wide text-offwhite/60">Horas/ano hoje</div><div className="h-display text-2xl font-extrabold">{n0(r.baselineH)}h</div><div className="text-xs text-offwhite/60">{(r.baselineH / 1760).toFixed(1)} FTE · AHT médio {r.wAht.toFixed(1)} min</div></div>
          <div className="rounded-xl bg-navy p-4 text-offwhite"><div className="text-[11px] uppercase tracking-wide text-offwhite/60">Em trabalho repetitivo</div><div className="h-display text-2xl font-extrabold text-gold">{n0(r.repetitiveH)}h</div><div className="text-xs text-offwhite/60">{brl(r.repetitiveH * hourCost)}/ano</div></div>
          <div className="rounded-xl border-2 border-gold bg-white p-4"><div className="text-[11px] uppercase tracking-wide text-muted">Horas recuperáveis</div><div className="h-display text-2xl font-extrabold text-navy">{n0(r.saved)}h</div><div className="text-xs text-muted">{r.fte.toFixed(1)} FTE · {n0(r.saved / 12)}h/mês</div></div>
          <div className="rounded-xl border-2 border-gold bg-white p-4"><div className="text-[11px] uppercase tracking-wide text-muted">Benefício líquido / ROI</div><div className="h-display text-2xl font-extrabold text-emerald-700">{brl(r.benefit - r.cost)}</div><div className="text-xs text-muted">ROI {(r.roi * 100).toFixed(0)}% · custo IA+infra {brl(r.cost)}</div></div>
        </div>
        <table className="mt-5 w-full text-sm">
          <thead><tr className="text-left text-xs uppercase tracking-wide text-muted"><th className="pb-2">Alavanca</th><th className="pb-2">Como</th><th className="pb-2 text-right">Horas/ano</th><th className="pb-2 text-right">R$/ano</th></tr></thead>
          <tbody>
            {[
              ["Triagem automática", `classificador (${(classifierAccuracy * 100).toFixed(1)}% acurácia) elimina a triagem manual`, r.triageH],
              ["Resposta automática", `${(auto * 100).toFixed(0)}% dos tickets × contenção ${(containment * 100).toFixed(0)}% − revisão amostral`, r.autoH],
              ["Resposta sugerida", `${(assist * 100).toFixed(0)}% dos tickets × −${(assistRed * 100).toFixed(0)}% de AHT`, r.assistH],
              ["Preparação p/ humano", `${(r.human * 100).toFixed(0)}% dos tickets: resumo, contexto e artigo prontos (−${d.human_prep_reduction * 100}% AHT)`, r.humanH],
            ].map(([a, b, h]) => (
              <tr key={a as string} className="border-t border-line">
                <td className="py-2 font-medium">{a}</td><td className="text-xs text-muted">{b}</td>
                <td className="text-right font-semibold">{n0(h as number)}</td><td className="text-right">{brl((h as number) * hourCost)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="mt-3 text-xs text-muted">
          O que é dado e o que é premissa: volume e mix de modos vêm dos dados (Opportunity Matrix aplicada aos 8.469 tickets; volume do brief).
          AHT, custo/hora e taxas de contenção são premissas de mercado — o Dataset 1 não tem tempo de manuseio. Por isso a calculadora é editável:
          a conversa com o Diretor passa a ser sobre premissas, não sobre um número mágico.
        </p>
      </div>
    </div>
  );
}
