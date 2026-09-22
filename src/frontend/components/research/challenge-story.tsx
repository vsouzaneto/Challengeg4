"use client";

import { useEffect, useRef, useState } from "react";
import { BookOpen, ChartLine, Check, Sparkles, X } from "lucide-react";
import type { ResearchStory } from "@/lib/research/stories";

const LENS_ICONS = [Sparkles, ChartLine, BookOpen] as const;

export function ChallengeStory({ story }: { story: ResearchStory }) {
  const [visible, setVisible] = useState(false);
  const [focus, setFocus] = useState(story.cards[0]?.id ?? "");
  const [lens, setLens] = useState(story.lenses[0]?.id ?? "");
  const ref = useRef<HTMLDivElement>(null);
  const activeCard = story.cards.find((card) => card.id === focus) ?? story.cards[0];
  const activeLens = story.lenses.find((item) => item.id === lens) ?? story.lenses[0];

  useEffect(() => {
    const obs = new IntersectionObserver(([entry]) => entry.isIntersecting && setVisible(true), {
      threshold: 0.15,
    });
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);

  return (
    <>
      <section id="background" ref={ref} className="space-y-12 lg:space-y-16">
        <div>
          <span className="inline-flex items-center gap-3 text-sm font-mono text-muted-foreground mb-6">
            <span className="w-8 h-px bg-foreground/30" />
            Contexto · {story.menuLabel}
          </span>
          <h1
            className={`text-4xl lg:text-6xl font-display tracking-tight max-w-4xl transition-all duration-700 ${
              visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
            }`}
          >
            {story.headline} <br />
            <span className="text-muted-foreground">{story.headlineMuted}</span>
          </h1>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 lg:gap-20">
          <div className="space-y-5 text-lg leading-relaxed text-foreground/85">
            {story.paragraphs.map((paragraph) => (
              <p key={paragraph}>{paragraph}</p>
            ))}
          </div>

          <div
            className={`transition-all duration-700 delay-200 ${
              visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"
            }`}
          >
            <h2 className="font-display text-xl mb-6">O caso em números</h2>
            <div className="grid grid-cols-2 gap-px bg-foreground/10 border border-foreground/10">
              {story.stats.map((stat) => (
                <div key={stat.label} className="bg-background p-6">
                  <div className="text-3xl lg:text-4xl font-display tracking-tight">{stat.value}</div>
                  <div className="text-sm text-foreground/80 mt-1">{stat.label}</div>
                  <div className="text-xs font-mono text-muted-foreground mt-1">{stat.hint}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section id="eda" className="space-y-12">
        <div>
          <span className="inline-flex items-center gap-3 text-sm font-mono text-muted-foreground mb-6">
            <span className="w-8 h-px bg-foreground/30" />
            Análise exploratória de dados
          </span>
          <h2 className="text-3xl lg:text-5xl font-display tracking-tight max-w-3xl">
            {story.signalTitle}
          </h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-3xl leading-relaxed">
            {story.signalBody}
          </p>
        </div>

        <div className="grid lg:grid-cols-[1.2fr_1fr] gap-px bg-foreground/10 border border-foreground/10">
          <div className="bg-background p-4 lg:p-6">
            <div className="grid sm:grid-cols-2 gap-3">
              {story.cards.map((card) => (
                <button
                  key={card.id}
                  type="button"
                  onMouseEnter={() => setFocus(card.id)}
                  onFocus={() => setFocus(card.id)}
                  onClick={() => setFocus(card.id)}
                  className={`text-left p-4 border rounded-md transition-all ${
                    focus === card.id
                      ? "border-foreground/40 bg-foreground/[0.03]"
                      : "border-foreground/10 hover:border-foreground/25"
                  }`}
                >
                  <div className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground mb-2">
                    {card.short}
                  </div>
                  <div className="font-display text-xl">{card.title}</div>
                  <div className="text-xs font-mono text-muted-foreground mt-2">{card.metric}</div>
                </button>
              ))}
            </div>
          </div>

          {activeCard && (
            <div className="bg-background p-6 lg:p-8 flex flex-col">
              <span className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
                {activeCard.short}
              </span>
              <h3 className="font-display text-3xl mt-2">{activeCard.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed mt-4 flex-1">
                {activeCard.body}
              </p>
              <div className="mt-6 border border-foreground/10 p-4">
                <div className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
                  Leitura
                </div>
                <div className="font-display text-2xl mt-1">{activeCard.metric}</div>
              </div>
            </div>
          )}
        </div>
      </section>

      <section id="feature-selection" className="space-y-10">
        <div>
          <span className="inline-flex items-center gap-3 text-sm font-mono text-muted-foreground mb-6">
            <span className="w-8 h-px bg-foreground/30" />
            Corte
          </span>
          <h2 className="text-3xl lg:text-5xl font-display tracking-tight max-w-3xl">
            {story.cutTitle}
          </h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-3xl leading-relaxed">
            {story.cutBody}
          </p>
        </div>

        <div className="border border-foreground/10">
          {story.rows.map((row, index) => (
            <div
              key={row.id}
              className="grid grid-cols-[40px_1fr_auto] items-center gap-4 px-6 py-4 border-t first:border-t-0 border-foreground/10"
            >
              <div className="font-mono text-xs text-muted-foreground tabular-nums">
                {String(index + 1).padStart(2, "0")}
              </div>
              <div className="min-w-0">
                <div className="font-display text-base">{row.label}</div>
                <div className="font-mono text-[11px] text-muted-foreground">{row.detail}</div>
              </div>
              {row.keep ? (
                <span className="inline-flex items-center gap-1 text-[11px] font-mono uppercase tracking-wider px-2 py-1 rounded-full bg-foreground text-background">
                  <Check className="w-3 h-3" /> manter
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 text-[11px] font-mono uppercase tracking-wider px-2 py-1 rounded-full bg-foreground/5 text-muted-foreground">
                  <X className="w-3 h-3" /> descartar
                </span>
              )}
            </div>
          ))}
        </div>
      </section>

      <section id="analysis" className="space-y-10">
        <div>
          <span className="inline-flex items-center gap-3 text-sm font-mono text-muted-foreground mb-6">
            <span className="w-8 h-px bg-foreground/30" />
            Análise
          </span>
          <h2 className="text-3xl lg:text-5xl font-display tracking-tight max-w-3xl">
            Escolha uma lente. <br />
            <span className="text-muted-foreground">{story.analysisMuted}</span>
          </h2>
        </div>

        <div className="grid sm:grid-cols-3 gap-px bg-foreground/10 border border-foreground/10">
          {story.lenses.map((item, index) => {
            const Icon = LENS_ICONS[index] ?? Sparkles;
            const isActive = item.id === lens;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => setLens(item.id)}
                className={`text-left p-6 transition-colors relative ${
                  isActive ? "bg-foreground text-background" : "bg-background hover:bg-foreground/[0.03]"
                }`}
              >
                <div className="flex items-center gap-3 mb-3">
                  <Icon className={`w-4 h-4 ${isActive ? "text-background" : "text-foreground/70"}`} />
                  <span
                    className={`font-mono text-[11px] uppercase tracking-wider ${
                      isActive ? "text-background/70" : "text-muted-foreground"
                    }`}
                  >
                    perspectiva
                  </span>
                </div>
                <div className="font-display text-2xl">{item.label}</div>
                <div
                  className={`text-xs font-mono mt-1 ${
                    isActive ? "text-background/70" : "text-muted-foreground"
                  }`}
                >
                  {item.subtitle}
                </div>
              </button>
            );
          })}
        </div>

        {activeLens && (
          <div className="border border-foreground/10 p-6 lg:p-10 space-y-6">
            <p className="text-lg leading-relaxed text-foreground/85 max-w-3xl">{activeLens.lead}</p>
            <ul className="space-y-3">
              {activeLens.points.map((point) => (
                <li key={point} className="flex gap-3 text-sm leading-relaxed">
                  <span className="font-mono text-xs text-muted-foreground mt-0.5">—</span>
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>
    </>
  );
}
