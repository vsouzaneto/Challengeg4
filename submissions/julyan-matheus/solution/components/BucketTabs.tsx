"use client";

import { useState } from "react";
import type { Bucket, PipelineRow, ScoredDeal, TriagedDeal } from "@/lib/types";
import { usd } from "@/lib/format";
import { ScorePill, TierBadge, ToneDot } from "./Badges";

const ORDER: Bucket[] = ["Focar", "Requalificar", "Iniciar", "Limpar"];

const HINT: Record<Bucket, string> = {
  Focar: "Vivos, com conta e dentro do prazo. Só estes recebem score.",
  Requalificar: "Sem conta vinculada. Nenhum deal sem conta fechou no histórico.",
  Iniciar: "Prospecting com conta. Ainda sem primeiro contato.",
  Limpar: "Mais de 138 dias abertos. Nenhum deal fechou depois disso.",
};

export function BucketTabs({
  rows,
  counts,
  focar,
}: {
  rows: PipelineRow[];
  counts: Record<Bucket, number>;
  focar: ScoredDeal[];
}) {
  const [tab, setTab] = useState<Bucket>("Focar");

  return (
    <section>
      <div role="tablist" className="flex flex-wrap gap-1 border-b border-neutral-200">
        {ORDER.map((b) => (
          <button
            key={b}
            role="tab"
            aria-selected={tab === b}
            onClick={() => setTab(b)}
            className={`-mb-px rounded-t-md border-b-2 px-4 py-2 text-sm ${
              tab === b
                ? "border-neutral-900 font-semibold text-neutral-900"
                : "border-transparent text-neutral-500 hover:text-neutral-800"
            }`}
          >
            {b} <span className="ml-1 rounded-full bg-neutral-100 px-2 py-0.5 text-xs text-neutral-600">{counts[b]}</span>
          </button>
        ))}
      </div>
      <p className="mt-3 text-sm text-neutral-500">{HINT[tab]}</p>
      <div className="mt-3 overflow-x-auto rounded-lg border border-neutral-200 bg-white">
        {tab === "Focar" ? <FocarTable rows={focar} /> : <TriagedTable bucket={tab} rows={rows} />}
      </div>
    </section>
  );
}

const th = "px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500";
const td = "px-3 py-2 align-top";

function FocarTable({ rows }: { rows: ScoredDeal[] }) {
  const [open, setOpen] = useState<string | null>(null);
  if (rows.length === 0) return <Empty text="Nenhum deal em Focar." />;
  return (
    <table className="w-full text-sm">
      <thead className="bg-neutral-50">
        <tr>
          <th className={th}>Deal</th>
          <th className={th}>Conta</th>
          <th className={th}>Produto</th>
          <th className={`${th} text-right`}>Dias aberto</th>
          <th className={`${th} text-right`}>Score</th>
          <th className={th}>Etiqueta</th>
          <th className={`${th} text-right`}>Valor esperado</th>
          <th className={th}></th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r) => {
          const id = r.deal.opportunity_id;
          const expanded = open === id;
          return (
            <FocarRow key={id} row={r} expanded={expanded} onToggle={() => setOpen(expanded ? null : id)} />
          );
        })}
      </tbody>
    </table>
  );
}

function FocarRow({ row: r, expanded, onToggle }: { row: ScoredDeal; expanded: boolean; onToggle: () => void }) {
  return (
    <>
      <tr
        className="cursor-pointer border-t border-neutral-100 hover:bg-neutral-50"
        onClick={onToggle}
        aria-expanded={expanded}
      >
        <td className={`${td} font-mono text-xs`}>{r.deal.opportunity_id}</td>
        <td className={td}>{r.deal.account}</td>
        <td className={td}>{r.deal.product}</td>
        <td className={`${td} text-right tabular-nums`}>{r.daysOpen}</td>
        <td className={`${td} text-right`}>
          <ScorePill score={r.score} />
        </td>
        <td className={td}>
          <TierBadge tier={r.tier} />
        </td>
        <td className={`${td} text-right tabular-nums`}>{usd(r.expectedValue)}</td>
        <td className={`${td} text-right text-neutral-400`}>{expanded ? "▾" : "▸"}</td>
      </tr>
      {expanded && (
        <tr className="border-t border-neutral-100 bg-neutral-50/60">
          <td colSpan={8} className="px-4 py-3">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">Por quê</p>
            <ul className="space-y-1.5">
              {r.why.map((w) => (
                <li key={w.factor} className="flex items-start gap-2">
                  <ToneDot tone={w.tone} />
                  <span>
                    <span className="font-medium capitalize">{w.factor}:</span> {w.text}
                  </span>
                </li>
              ))}
            </ul>
          </td>
        </tr>
      )}
    </>
  );
}

function TriagedTable({ bucket, rows }: { bucket: Exclude<Bucket, "Focar">; rows: PipelineRow[] }) {
  const list = rows.filter((r): r is TriagedDeal => r.bucket === bucket);
  if (bucket === "Requalificar") {
    // Engaging primeiro (dias aberto crescente), Prospecting depois.
    list.sort((a, b) => {
      const aEng = a.deal.deal_stage === "Engaging" ? 0 : 1;
      const bEng = b.deal.deal_stage === "Engaging" ? 0 : 1;
      return aEng - bEng || (a.daysOpen ?? 0) - (b.daysOpen ?? 0);
    });
  }
  if (bucket === "Limpar") list.sort((a, b) => (b.daysOpen ?? 0) - (a.daysOpen ?? 0));
  if (list.length === 0) return <Empty text={`Nenhum deal em ${bucket}.`} />;
  const showAccount = bucket !== "Requalificar";
  const showDays = bucket !== "Iniciar";
  return (
    <table className="w-full text-sm">
      <thead className="bg-neutral-50">
        <tr>
          <th className={th}>Deal</th>
          {showAccount && <th className={th}>Conta</th>}
          <th className={th}>Produto</th>
          {showDays && <th className={`${th} text-right`}>Dias aberto</th>}
          <th className={th}>Ação</th>
        </tr>
      </thead>
      <tbody>
        {list.map((r) => (
          <tr key={r.deal.opportunity_id} className="border-t border-neutral-100">
            <td className={`${td} font-mono text-xs`}>{r.deal.opportunity_id}</td>
            {showAccount && <td className={td}>{r.deal.account ?? <span className="text-neutral-400">—</span>}</td>}
            <td className={td}>{r.deal.product}</td>
            {showDays && (
              <td className={`${td} text-right tabular-nums`}>
                {r.daysOpen ?? <span className="text-neutral-400">—</span>}
              </td>
            )}
            <td className={`${td} text-neutral-700`}>{r.action}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function Empty({ text }: { text: string }) {
  return <p className="px-4 py-6 text-sm text-neutral-500">{text}</p>;
}
