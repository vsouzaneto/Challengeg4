"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { ArrowUpRight, ChevronDown, Check, X } from "lucide-react";
import type { ModelWorkshopStory } from "@/lib/model/workshops";

export function ModelChallenge({ story }: { story: ModelWorkshopStory }) {
  const [variantId, setVariantId] = useState(story.variants[0]?.id ?? "");
  const [pickerOpen, setPickerOpen] = useState(false);
  const variant = story.variants.find((item) => item.id === variantId) ?? story.variants[0];

  const snapshot = useMemo(() => {
    if (!variant) return "";
    return JSON.stringify(
      {
        challenge: story.code,
        variant: variant.id,
        notebook: story.notebook,
        sees: variant.sees,
        ignores: variant.ignores,
        output: variant.output,
      },
      null,
      2
    );
  }, [story.code, story.notebook, variant]);

  if (!variant) return null;

  return (
    <div className="space-y-12 lg:space-y-16">
      <div className="space-y-6">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <span className="inline-flex items-center gap-3 text-sm font-mono text-muted-foreground">
            <span className="w-8 h-px bg-foreground/30" />
            {story.kicker}
          </span>
          <Link
            href={story.researchHref}
            className="group inline-flex items-center gap-2 rounded-full border border-foreground/15 hover:border-foreground/40 bg-background/40 px-4 py-1.5 text-xs font-mono text-muted-foreground hover:text-foreground transition-colors"
          >
            <span className="uppercase tracking-wider">Ir à análise</span>
            <ArrowUpRight className="w-3.5 h-3.5 -translate-x-0.5 group-hover:translate-x-0 transition-transform" />
          </Link>
        </div>

        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <h1 className="text-4xl lg:text-6xl font-display tracking-tight max-w-3xl">
            {story.headline} <br />
            <span className="text-muted-foreground">{story.headlineMuted}</span>
          </h1>

          <div className="relative">
            <button
              type="button"
              onClick={() => setPickerOpen((open) => !open)}
              className="flex items-center gap-3 border border-foreground/15 rounded-full px-5 py-3 text-sm hover:border-foreground/40 transition-colors"
              aria-expanded={pickerOpen}
            >
              <span className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
                variante
              </span>
              <span className="font-display text-lg">{variant.name}</span>
              <ChevronDown className={`w-4 h-4 transition-transform ${pickerOpen ? "rotate-180" : ""}`} />
            </button>
            {pickerOpen && (
              <div className="absolute right-0 top-full mt-2 z-30 w-80 bg-background border border-foreground/15 rounded-2xl shadow-lg overflow-hidden">
                {story.variants.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => {
                      setVariantId(item.id);
                      setPickerOpen(false);
                    }}
                    className={`w-full text-left px-5 py-4 border-b border-foreground/10 last:border-b-0 transition-colors ${
                      item.id === variant.id ? "bg-foreground/[0.04]" : "hover:bg-foreground/[0.02]"
                    }`}
                  >
                    <div className="flex items-baseline justify-between gap-3">
                      <span className="font-display text-base">{item.name}</span>
                      <span className="text-xs font-mono text-muted-foreground">{item.metric}</span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1 leading-relaxed">{item.summary}</p>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        <p className="text-lg text-muted-foreground max-w-3xl leading-relaxed">{story.lede}</p>
      </div>

      <div className="grid lg:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)] gap-10 lg:gap-14">
        <div className="space-y-6">
          <div className="flex items-baseline justify-between">
            <h2 className="font-display text-2xl">O que entra</h2>
            <span className="text-xs font-mono text-muted-foreground">{variant.sees.length} sinais</span>
          </div>
          <div className="border border-foreground/10">
            {variant.sees.map((item) => (
              <div key={item} className="flex items-start gap-3 px-5 py-3 border-t first:border-t-0 border-foreground/10">
                <Check className="w-3.5 h-3.5 mt-1 shrink-0" />
                <span className="text-sm leading-relaxed">{item}</span>
              </div>
            ))}
            {variant.ignores.map((item) => (
              <div key={item} className="flex items-start gap-3 px-5 py-3 border-t border-foreground/10 text-muted-foreground">
                <X className="w-3.5 h-3.5 mt-1 shrink-0" />
                <span className="text-sm leading-relaxed">{item}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-8">
          <div className="space-y-2">
            <h2 className="font-display text-2xl">O que devolve</h2>
            <p className="text-sm text-muted-foreground">{variant.summary}</p>
          </div>
          <div className="border border-foreground/10 p-6 lg:p-8 space-y-4">
            <div className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
              {variant.name}
            </div>
            <p className="font-display text-3xl lg:text-4xl tracking-tight leading-tight">{variant.output}</p>
            <div className="font-mono text-xs text-muted-foreground">{variant.metric}</div>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <div className="flex items-baseline justify-between gap-4 flex-wrap">
          <h2 className="font-display text-3xl lg:text-5xl tracking-tight">Estatísticas do modelo</h2>
          <span className="text-sm font-mono text-muted-foreground">
            {variant.name} · {variant.metric}
          </span>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-px bg-foreground/10 border border-foreground/10">
          {variant.stats.map((stat) => (
            <div key={stat.label} className="bg-background p-6">
              <div className="text-3xl lg:text-4xl font-display tracking-tight">{stat.value}</div>
              <div className="text-sm text-foreground/80 mt-1">{stat.label}</div>
              <div className="text-xs font-mono text-muted-foreground mt-1">{stat.hint}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-6">
        <div className="flex items-baseline justify-between gap-4 flex-wrap">
          <h2 className="font-display text-3xl lg:text-5xl tracking-tight">Explicabilidade</h2>
          <span className="text-sm font-mono text-muted-foreground">{variant.name}</span>
        </div>
        <div className="border border-foreground/10 p-6 lg:p-8 space-y-5">
          <p className="text-lg leading-relaxed text-foreground/85">{variant.explain}</p>
          <ul className="space-y-3">
            {variant.limits.map((limit) => (
              <li key={limit} className="flex gap-3 text-sm leading-relaxed">
                <span className="font-mono text-xs text-muted-foreground mt-0.5">—</span>
                <span>{limit}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="border border-foreground/10 p-6 lg:p-8">
        <div className="flex items-baseline justify-between mb-6">
          <h3 className="font-display text-2xl">Snapshot da variante</h3>
          <span className="text-xs font-mono text-muted-foreground">Lab 04 · contrato lido no notebook</span>
        </div>
        <pre className="text-xs font-mono overflow-x-auto leading-relaxed text-foreground/80">{snapshot}</pre>
      </div>
    </div>
  );
}
