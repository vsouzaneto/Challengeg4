"use client";

import { useState } from "react";
import type { ImageWorkshop } from "@/lib/model-2/stories";

export function ImageChallenge({ story }: { story: ImageWorkshop }) {
  const [lens, setLens] = useState(0);
  const active = story.classification?.[lens];

  return (
    <div className="space-y-16 lg:space-y-24">
      <section className="space-y-6">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-muted-foreground">
          <span className="w-8 h-px bg-foreground/30" />
          {story.kicker}
        </span>
        <h1 className="text-4xl lg:text-6xl font-display tracking-tight max-w-3xl">
          {story.headline} <br />
          <span className="text-muted-foreground">{story.headlineMuted}</span>
        </h1>
        <p className="text-lg text-muted-foreground max-w-3xl leading-relaxed">{story.lede}</p>
      </section>

      <section className="space-y-6">
        <div className="flex items-baseline justify-between gap-4 flex-wrap">
          <h2 className="font-display text-2xl lg:text-3xl tracking-tight">{story.rankingTitle}</h2>
          <span className="text-xs font-mono text-muted-foreground">{story.rankingHint}</span>
        </div>
        <div className="border border-foreground/10">
          {story.ranking.map((row, index) => (
            <div
              key={row.name}
              className="grid grid-cols-[40px_1fr_auto] gap-4 items-baseline px-6 py-4 border-t first:border-t-0 border-foreground/10"
            >
              <div className="font-mono text-xs text-muted-foreground tabular-nums">
                {String(index + 1).padStart(2, "0")}
              </div>
              <div className="min-w-0">
                <div className="font-display text-lg">{row.name}</div>
                <div className="text-xs font-mono text-muted-foreground mt-1">{row.note}</div>
              </div>
              <div className="font-display text-lg tabular-nums">{row.metric}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="space-y-6">
        <h2 className="font-display text-2xl lg:text-3xl tracking-tight">{story.entranceTitle}</h2>
        <div className="grid sm:grid-cols-2 gap-px bg-foreground/10 border border-foreground/10">
          {story.entrance.map((item) => (
            <div key={item.name} className="bg-background p-6">
              <div className="font-display text-xl">{item.name}</div>
              <p className="text-sm text-muted-foreground mt-2 leading-relaxed">{item.detail}</p>
            </div>
          ))}
        </div>
      </section>

      {story.classification && active && (
        <section className="space-y-8">
          <h2 className="font-display text-2xl lg:text-3xl tracking-tight">Classificação</h2>
          <div className={`grid gap-px bg-foreground/10 border border-foreground/10 ${story.classification.length > 1 ? "sm:grid-cols-2" : ""}`}>
            {story.classification.map((item, index) => {
              const isActive = index === lens;
              return (
                <button
                  key={item.label}
                  type="button"
                  onClick={() => setLens(index)}
                  className={`p-6 text-left ${isActive ? "bg-foreground text-background" : "bg-background"}`}
                >
                  <div className="font-display text-2xl">{item.label}</div>
                  <div className={`text-xs font-mono mt-1 ${isActive ? "text-background/70" : "text-muted-foreground"}`}>
                    {item.subtitle}
                  </div>
                </button>
              );
            })}
          </div>
          <p className="text-lg leading-relaxed text-foreground/85 max-w-3xl">{active.body}</p>
        </section>
      )}

      <section className="space-y-6">
        <h2 className="font-display text-3xl lg:text-5xl tracking-tight">Estatísticas do modelo</h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-px bg-foreground/10 border border-foreground/10">
          {story.stats.map((stat) => (
            <div key={stat.label} className="bg-background p-6">
              <div className="text-2xl lg:text-3xl font-display tracking-tight tabular-nums">{stat.value}</div>
              <div className="mt-1 text-sm text-muted-foreground">{stat.label}</div>
              <div className="text-xs font-mono text-muted-foreground/70 mt-0.5">{stat.hint}</div>
            </div>
          ))}
        </div>
      </section>

      {story.bias && (
        <section className="space-y-4">
          <h2 className="font-display text-3xl lg:text-5xl tracking-tight">{story.bias.title}</h2>
          <p className="text-lg text-muted-foreground leading-relaxed max-w-3xl">{story.bias.body}</p>
        </section>
      )}

      <section className="space-y-6 border-t border-foreground/10 pt-12">
        <h2 className="font-display text-2xl tracking-tight">Fora desta oficina</h2>
        <ul className="space-y-3">
          {story.omitted.map((item) => (
            <li key={item.section} className="grid sm:grid-cols-[240px_1fr] gap-2 sm:gap-6 text-sm">
              <span className="font-mono text-xs text-muted-foreground uppercase tracking-wider">{item.section}</span>
              <span className="text-foreground/80 leading-relaxed">{item.reason}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
