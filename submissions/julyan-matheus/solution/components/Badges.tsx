import type { Tier, Tone } from "@/lib/types";

const TIER_STYLE: Record<Tier, string> = {
  Top: "bg-emerald-100 text-emerald-800 ring-emerald-200",
  Meio: "bg-amber-100 text-amber-800 ring-amber-200",
  Fundo: "bg-neutral-200 text-neutral-700 ring-neutral-300",
};

export function TierBadge({ tier }: { tier: Tier | null }) {
  if (!tier) return <span className="text-xs text-neutral-400">—</span>;
  return (
    <span
      className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${TIER_STYLE[tier]}`}
      title="Posição entre os deals do seu Focar"
    >
      {tier} do seu Focar
    </span>
  );
}

const TONE_STYLE: Record<Tone, string> = {
  positivo: "bg-emerald-500",
  neutro: "bg-neutral-400",
  alerta: "bg-red-500",
};

export function ToneDot({ tone }: { tone: Tone }) {
  return <span aria-label={tone} className={`mt-1.5 inline-block h-2 w-2 shrink-0 rounded-full ${TONE_STYLE[tone]}`} />;
}

export function ScorePill({ score }: { score: number }) {
  return (
    <span className="inline-flex min-w-10 items-center justify-center rounded-md bg-neutral-900 px-2 py-0.5 font-mono text-sm font-semibold text-white">
      {score}
    </span>
  );
}
