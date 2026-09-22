"use client";

import { useMemo } from "react";
import { FEATURES } from "@/lib/breast-cancer/features";
import { MODEL_INDEX } from "@/lib/breast-cancer/models";

import { CLASS_BENIGN as BENIGN_COLOR, CLASS_MALIGNANT as MALIGNANT_COLOR } from "@/lib/g4s-theme";

interface Case {
  id: string;
  age: number;
  region: string;
  groundTruth: "benign" | "malignant";
  narrative: string;
  outcome: string;
  features: Partial<Record<string, number>>;
}

const CASES: Case[] = [
  {
    id: "WD-042",
    age: 56,
    region: "Meio-oeste dos EUA, acompanhamento 1992",
    groundTruth: "malignant",
    narrative:
      "Paciente de 56 anos com massa assimétrica no rastreio de rotina. A PAAF mostrou núcleos com muitos pontos côncavos e raio elevado — features que o modelo agora marca com força.",
    outcome:
      "Carcinoma ductal invasivo confirmado na biópsia. Cirurgia conservadora e terapia adjuvante; livre de doença aos 5 anos.",
    features: {
      radius_mean: 17.6,
      perimeter_mean: 117.5,
      area_mean: 982.0,
      concavity_mean: 0.162,
      concave_points_mean: 0.094,
      texture_mean: 21.7,
    },
  },
  {
    id: "WD-137",
    age: 42,
    region: "Coorte de Madison, 1991",
    groundTruth: "benign",
    narrative:
      "Paciente de 42 anos com nódulo palpável optou por PAAF antes da excisão. Compacidade e pontos côncavos abaixo da média populacional ancoraram o caso no cluster benigno.",
    outcome:
      "Fibroadenoma confirmado na histologia. Vigilância ativa; sem progressão em 2 anos.",
    features: {
      radius_mean: 11.9,
      perimeter_mean: 76.4,
      area_mean: 451.0,
      concavity_mean: 0.041,
      concave_points_mean: 0.023,
      texture_mean: 17.2,
    },
  },
  {
    id: "WD-204",
    age: 49,
    region: "Caso limítrofe · 1993",
    groundTruth: "malignant",
    narrative:
      "Achados limítrofes de PAAF ficaram perto da fronteira em todos os kernels. O RBF classificou como maligno, mas com confiança abaixo de 60% — sinal claro de que o caso pedia mais imagem.",
    outcome:
      "Biópsia com agulha grossa revelou carcinoma ductal in situ. O caso integra o conjunto de teste de explicabilidade da região de fronteira.",
    features: {
      radius_mean: 14.6,
      perimeter_mean: 94.8,
      area_mean: 670.5,
      concavity_mean: 0.084,
      concave_points_mean: 0.052,
      texture_mean: 19.4,
    },
  },
];

function buildVector(c: Case): number[] {
  return FEATURES.map((f) => {
    const v = c.features[f.id];
    if (v != null) return v;
    return c.groundTruth === "benign" ? f.benignMean : f.malignantMean;
  });
}

export function CaseStudyView() {
  const enriched = useMemo(() => {
    const rbf = MODEL_INDEX.rbf;
    return CASES.map((c) => {
      const vector = buildVector(c);
      const pred = rbf.predict(vector);
      return { case: c, pred };
    });
  }, []);

  return (
    <div className="space-y-12">
      {enriched.map(({ case: c, pred }, idx) => {
        const truthColor = c.groundTruth === "malignant" ? MALIGNANT_COLOR : BENIGN_COLOR;
        const predColor = pred.label === "malignant" ? MALIGNANT_COLOR : BENIGN_COLOR;
        const matches = c.groundTruth === pred.label;
        return (
          <article
            key={c.id}
            className="grid lg:grid-cols-[1fr_1.2fr] gap-px bg-foreground/10 border border-foreground/10"
          >
            <div className="bg-background p-6 lg:p-8">
              <div className="flex items-baseline justify-between mb-4">
                <span className="font-mono text-xs text-muted-foreground">
                  Caso {String(idx + 1).padStart(2, "0")} · {c.id}
                </span>
                <span
                  className="text-[11px] font-mono uppercase tracking-wider px-2 py-0.5 rounded-full"
                  style={{ background: `${truthColor}1f`, color: truthColor }}
                >
                  verdade · {c.groundTruth === "malignant" ? "maligno" : "benigno"}
                </span>
              </div>
              <h3 className="font-display text-2xl lg:text-3xl">
                {c.age} anos — {c.region}
              </h3>
              <p className="text-sm text-muted-foreground mt-4 leading-relaxed">{c.narrative}</p>
              <p className="text-sm text-foreground/85 mt-4 leading-relaxed">
                <span className="font-display text-base mr-1">Desfecho.</span>
                {c.outcome}
              </p>
            </div>

            <div className="bg-background p-6 lg:p-8 space-y-5">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-xs font-mono text-muted-foreground">Predição RBF</div>
                  <div
                    className="font-display text-2xl mt-1"
                    style={{ color: predColor }}
                  >
                    {pred.label === "malignant" ? "maligno" : "benigno"}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs font-mono text-muted-foreground">confiança</div>
                  <div className="font-display text-2xl">{(pred.confidence * 100).toFixed(1)}%</div>
                </div>
                <div className="text-right">
                  <div className="text-xs font-mono text-muted-foreground">match</div>
                  <div
                    className={`font-display text-2xl ${
                      matches ? "text-foreground" : "text-primary"
                    }`}
                  >
                    {matches ? "✓" : "≠"}
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                {Object.entries(c.features).map(([fid, val]) => {
                  const f = FEATURES.find((x) => x.id === fid);
                  if (!f || val == null) return null;
                  const range = f.max - f.min;
                  const pct = ((val - f.min) / range) * 100;
                  const benignPct = ((f.benignMean - f.min) / range) * 100;
                  const malignantPct = ((f.malignantMean - f.min) / range) * 100;
                  return (
                    <div key={fid} className="text-xs font-mono">
                      <div className="flex items-baseline justify-between mb-1">
                        <span className="text-muted-foreground">{f.short}</span>
                        <span className="tabular-nums">{val.toFixed(f.step < 0.01 ? 3 : 1)}</span>
                      </div>
                      <div className="relative h-1.5 rounded-full bg-foreground/5">
                        <span
                          className="absolute top-0 bottom-0 w-px"
                          style={{ left: `${benignPct}%`, background: BENIGN_COLOR }}
                        />
                        <span
                          className="absolute top-0 bottom-0 w-px"
                          style={{ left: `${malignantPct}%`, background: MALIGNANT_COLOR }}
                        />
                        <span
                          className="absolute -top-1 w-2 h-3.5 rounded-sm"
                          style={{
                            left: `calc(${pct}% - 4px)`,
                            background: predColor,
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </article>
        );
      })}
    </div>
  );
}
