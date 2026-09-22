"use client";

import { useEffect, useRef, useState } from "react";
import { AnimatedVisual } from "@/components/landing/features-section";
import type { AboutBeat, AboutStory } from "@/lib/about/stories";

function Beat({ beat, index }: { beat: AboutBeat; index: number }) {
  const [isVisible, setIsVisible] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setIsVisible(true);
      },
      { threshold: 0.2 }
    );
    if (cardRef.current) observer.observe(cardRef.current);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={cardRef}
      className={`group relative transition-all duration-700 ${
        isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-12"
      }`}
      style={{ transitionDelay: `${index * 100}ms` }}
    >
      <div className="flex flex-col lg:flex-row gap-8 lg:gap-16 py-12 lg:py-20 border-b border-foreground/10">
        <div className="shrink-0">
          <span className="font-mono text-sm text-muted-foreground">{beat.number}</span>
        </div>
        <div className="flex-1 grid lg:grid-cols-2 gap-8 items-center">
          <div>
            <h2 className="text-3xl lg:text-4xl font-display mb-4 group-hover:translate-x-2 transition-transform duration-500">
              {beat.title}
            </h2>
            <p className="text-lg text-muted-foreground leading-relaxed">{beat.description}</p>
          </div>
          <div className="flex justify-center lg:justify-end">
            <div className="w-48 h-40 text-foreground">
              <AnimatedVisual type={beat.visual} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function AboutChallenge({ story }: { story: AboutStory }) {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setIsVisible(true);
      },
      { threshold: 0.1 }
    );
    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  return (
    <section id="about" ref={sectionRef} className="relative">
      <div className="mb-16 lg:mb-24">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-muted-foreground mb-6">
          <span className="w-8 h-px bg-foreground/30" />
          Sobre · {story.code}
        </span>
        <h1
          className={`text-4xl lg:text-6xl font-display tracking-tight transition-all duration-700 ${
            isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
          }`}
        >
          {story.headline}
          <br />
          <span className="text-muted-foreground">{story.headlineMuted}</span>
        </h1>
        <p className="mt-8 text-lg text-muted-foreground leading-relaxed max-w-3xl">{story.lede}</p>
      </div>
      <div>
        {story.beats.map((beat, index) => (
          <Beat key={beat.number} beat={beat} index={index} />
        ))}
      </div>
    </section>
  );
}
