"use client";

import { useEffect, useState, useRef } from "react";

const integrations = [
  { name: "GitHub", category: "Controle de versão" },
  { name: "Slack", category: "Comunicação" },
  { name: "Stripe", category: "Pagamentos" },
  { name: "PostgreSQL", category: "Banco de dados" },
  { name: "Redis", category: "Cache" },
  { name: "AWS", category: "Cloud" },
  { name: "MongoDB", category: "Banco de dados" },
  { name: "Vercel", category: "Hospedagem" },
  { name: "Figma", category: "Design" },
  { name: "Linear", category: "Gestão de projetos" },
  { name: "Notion", category: "Documentação" },
  { name: "OpenAI", category: "IA/ML" },
];

export function IntegrationsSection() {
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
    <section id="integrations" ref={sectionRef} className="relative py-24 lg:py-32 overflow-hidden">
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12">
        {/* Header */}
        <div
          className={`text-center max-w-3xl mx-auto mb-16 lg:mb-24 transition-all duration-700 ${
            isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
          }`}
        >
          <span className="inline-flex items-center gap-3 text-sm font-mono text-muted-foreground mb-6">
            <span className="w-8 h-px bg-foreground/30" />
            Resultados
            <span className="w-8 h-px bg-foreground/30" />
          </span>
          <h2 className="text-4xl lg:text-6xl font-display tracking-tight mb-6">
            Funciona com tudo
            <br />
            que você já usa.
          </h2>
          <p className="text-xl text-muted-foreground">
            Mais de 200 integrações prontas. Conecte a stack inteira em minutos.
          </p>
        </div>

      </div>
    </section>
  );
}
