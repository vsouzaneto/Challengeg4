"use client";

import { useEffect, useRef, useState } from "react";

const stats = [
  { value: "569", label: "Amostras de pacientes", hint: "Wisconsin Diagnostic" },
  { value: "30", label: "Features de origem", hint: "10 média · 10 EP · 10 pior" },
  { value: "62.7%", label: "Prevalência benigna", hint: "split 357 / 212" },
  { value: "1990", label: "Publicação original", hint: "Wolberg & Mangasarian" },
];

export function BackgroundSection() {
  const [visible, setVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => e.isIntersecting && setVisible(true), {
      threshold: 0.15,
    });
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);

  return (
    <section id="background" ref={ref} className="space-y-12 lg:space-y-16">
      <div>
        <span className="inline-flex items-center gap-3 text-sm font-mono text-muted-foreground mb-6">
          <span className="w-8 h-px bg-foreground/30" />
          Contexto
        </span>
        <h1
          className={`text-4xl lg:text-6xl font-display tracking-tight max-w-4xl transition-all duration-700 ${
            visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
          }`}
        >
          Ler núcleos <br />
          <span className="text-muted-foreground">como evidência.</span>
        </h1>
      </div>

      <div className="grid lg:grid-cols-2 gap-12 lg:gap-20">
        <div className="space-y-5 text-lg leading-relaxed text-foreground/85">
          <p>
            O câncer de mama é o mais diagnosticado no mundo; a triagem
            citológica precoce por imagens de punção aspirativa por agulha fina
            (PAAF / FNA) é linha de frente desde o início dos anos 1990.
            O dataset Wisconsin Diagnostic Breast Cancer (WDBC), coletado na
            UW-Madison, codifica 30 features morfométricas extraídas de imagens
            FNA digitalizadas em forma tabular.
          </p>
          <p>
            O projeto reexamina esse dataset pela lente das machines de vetores
            de suporte. Comparamos quatro kernels — linear, polinomial, RBF e
            sigmoide — num pipeline unificado de seleção de features e
            validação, e expomos o comportamento do modelo de forma interativa
            para clínicos e estudantes construírem intuição.
          </p>
          <p>
            O modelo <em className="text-foreground">não</em> é ferramenta diagnóstica.
            É uma leitura estruturada de um dataset clássico e um veículo para
            experimentar IA explicável.
          </p>
        </div>

        <div
          className={`transition-all duration-700 delay-200 ${
            visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"
          }`}
        >
          <h3 className="font-display text-xl mb-6">Motivação em números</h3>
          <div className="grid grid-cols-2 gap-px bg-foreground/10 border border-foreground/10">
            {stats.map((s) => (
              <div key={s.label} className="bg-background p-6">
                <div className="text-3xl lg:text-4xl font-display tracking-tight">{s.value}</div>
                <div className="text-sm text-foreground/80 mt-1">{s.label}</div>
                <div className="text-xs font-mono text-muted-foreground mt-1">{s.hint}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
