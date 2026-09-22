"use client";

import { useMemo } from "react";
import { FileText, Quote, Sparkles } from "lucide-react";
import { FEATURES } from "@/lib/breast-cancer/features";
import type { SVMModel, SVMPrediction } from "@/lib/breast-cancer/models";

interface ExplanationPanelProps {
  model: SVMModel;
  prediction: SVMPrediction;
  values: number[];
}

// Mock "ground truth" research excerpts. The RAG retrieval is mocked here —
// in production this would be an API call to a vector store backed by clinical
// reference documents.
const GROUND_TRUTH_SNIPPETS = [
  {
    id: "wdbc-1995",
    title: "Wolberg & Mangasarian (1990): Multi-surface method for breast tumor diagnosis",
    quote:
      "Em 569 punções aspirativas, raio médio, perímetro e pontos côncavos foram as features mais discriminativas — juntas passam de 97% de acurácia em validação cruzada com um classificador linear.",
    tags: ["radius_mean", "perimeter_mean", "concave_points_mean"],
  },
  {
    id: "rfe-ucsd-2024",
    title: "DS3 interno — Relatório de eliminação recursiva de features (primavera 2026)",
    quote:
      "Depois do RFE, só seis features de média passam o corte de significância 0,05; suavidade e dimensão fractal caem de forma consistente como redundantes.",
    tags: ["smoothness_mean", "fractal_dimension_mean"],
  },
  {
    id: "rbf-vs-linear",
    title: "Estudo de comparação de kernels, benchmark UCI-WDBC",
    quote:
      "O kernel RBF estreita a fronteira na região de alta concavidade, onde o linear tende a classificar demais os casos limítrofes como benignos.",
    tags: ["concavity_mean", "concave_points_mean"],
  },
  {
    id: "case-A",
    title: "Caso A-123 — predição positiva histórica (match de 91%)",
    quote:
      "Entradas nesta vizinhança (raio ≈ 17, concavidade ≈ 0,15) resolveram como maligno em 41 de 44 casos retrospectivos.",
    tags: ["radius_mean", "concavity_mean"],
  },
  {
    id: "case-B",
    title: "Caso B-002 — cluster benigno histórico (match de 87%)",
    quote:
      "Perfis com raio < 13 e pontos côncavos < 0,04 agrupam com força na região benigna de todos os kernels avaliados.",
    tags: ["radius_mean", "concave_points_mean"],
  },
];

const RECOMMENDED_FEATURES = new Set([
  "radius_mean",
  "perimeter_mean",
  "concave_points_mean",
  "concavity_mean",
  "area_mean",
  "texture_mean",
]);

interface ExplainerLine {
  text: string;
  weight: "high" | "medium" | "low";
}

function buildSummary(model: SVMModel, prediction: SVMPrediction, values: number[]): ExplainerLine[] {
  const lines: ExplainerLine[] = [];
  const isMalignant = prediction.label === "malignant";
  const confidence = prediction.confidence;

  lines.push({
    text: `Com o ${model.name.toLowerCase()}, sua entrada cai na região ${
      isMalignant ? "maligna" : "benigna"
    } do espaço de features com ${(confidence * 100).toFixed(1)}% de confiança (decisão com sinal ${prediction.decision.toFixed(
      3
    )}).`,
    weight: "high",
  });

  // Closest reference cluster.
  const radius = values[0];
  const concavity = values[6];
  const concavePoints = values[7];
  if (isMalignant && radius > 15 && concavity > 0.1) {
    lines.push({
      text: `Esta vizinhança (raio ≈ ${radius.toFixed(1)}, concavidade ≈ ${concavity.toFixed(
        3
      )}) se aproxima do Caso A-123 — cluster maligno histórico com 91% de match.`,
      weight: "medium",
    });
  } else if (!isMalignant && radius < 13 && concavePoints < 0.04) {
    lines.push({
      text: `Seu raio (${radius.toFixed(
        1
      )}) e pontos côncavos (${concavePoints.toFixed(
        3
      )}) ficam no cluster benigno de referência B-002 (match de 87%).`,
      weight: "medium",
    });
  } else {
    lines.push({
      text: `Esta entrada fica perto da fronteira — pequenos movimentos em concavidade ou raio podem inverter a predição. Revise o painel de viés/variância abaixo.`,
      weight: "medium",
    });
  }

  // Feature-choice critique. A feature counts as "active" if the user has moved
  // it meaningfully away from the midpoint between the two class means.
  const ACTIVE_TOLERANCE = 0.02; // fraction of the feature range
  const chosen = FEATURES.filter((f, i) => {
    const midpoint = (f.benignMean + f.malignantMean) / 2;
    const range = f.max - f.min;
    return Math.abs(values[i] - midpoint) / range > ACTIVE_TOLERANCE;
  });
  if (chosen.length === 0) {
    lines.push({
      text: `Sua entrada está no ponto médio neutro de todas as features. Ajuste raio, perímetro, área ou pontos côncavos para ver a predição responder.`,
      weight: "low",
    });
  } else {
    const overlap = chosen.filter((c) => RECOMMENDED_FEATURES.has(c.id)).length;
    const ratio = overlap / chosen.length;
    if (ratio >= 0.6) {
      lines.push({
        text: `${(ratio * 100).toFixed(0)}% das ${chosen.length} feature${
          chosen.length === 1 ? "" : "s"
        } que você ajusta coincidem com o conjunto RFE — o modelo opera no sinal mais forte.`,
        weight: "low",
      });
    } else {
      lines.push({
        text: `Só ${(ratio * 100).toFixed(0)}% das ${chosen.length} feature${
          chosen.length === 1 ? "" : "s"
        } ativas estão no conjunto RFE; foque em raio, perímetro, área e pontos côncavos para predições mais nítidas.`,
        weight: "low",
      });
    }
  }

  return lines;
}

export function ExplanationPanel({ model, prediction, values }: ExplanationPanelProps) {
  const summary = useMemo(() => buildSummary(model, prediction, values), [model, prediction, values]);

  // Retrieve the snippets most relevant to the prediction.
  const retrieved = useMemo(() => {
    const importantFeatureIds = new Set<string>();
    if (Math.abs(prediction.decision) > 0.4) {
      importantFeatureIds.add("radius_mean");
      importantFeatureIds.add("perimeter_mean");
      importantFeatureIds.add("concave_points_mean");
    } else {
      importantFeatureIds.add("concavity_mean");
      importantFeatureIds.add("smoothness_mean");
    }
    return GROUND_TRUTH_SNIPPETS.filter((s) =>
      s.tags.some((t) => importantFeatureIds.has(t))
    ).slice(0, 3);
  }, [prediction.decision]);

  return (
    <div className="grid lg:grid-cols-[1.1fr_1fr] gap-px bg-foreground/10 border border-foreground/10">
      {/* AI summary */}
      <div className="bg-background p-6">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-4 h-4" />
          <h4 className="font-display text-xl">Por que esta predição?</h4>
          <span className="ml-auto text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded-full bg-foreground/5 text-muted-foreground">
            RAG · mock
          </span>
        </div>
        <ul className="space-y-3">
          {summary.map((s, i) => (
            <li
              key={i}
              className={`text-sm leading-relaxed ${
                s.weight === "high"
                  ? "text-foreground"
                  : s.weight === "medium"
                  ? "text-foreground/80"
                  : "text-muted-foreground"
              }`}
            >
              {s.text}
            </li>
          ))}
        </ul>
        <div className="mt-5 pt-5 border-t border-foreground/10 text-xs text-muted-foreground font-mono">
          As predições são consultivas e exigem validação clínica antes de qualquer ação.
        </div>
      </div>

      {/* Retrieved snippets */}
      <div className="bg-background p-6">
        <div className="flex items-center gap-2 mb-4">
          <FileText className="w-4 h-4" />
          <h4 className="font-display text-xl">Trechos de referência recuperados</h4>
        </div>
        <div className="space-y-4">
          {retrieved.map((r) => (
            <div key={r.id} className="border border-foreground/10 p-4 rounded-md">
              <div className="text-xs font-mono text-muted-foreground mb-2">{r.id}</div>
              <div className="font-display text-base leading-snug mb-2">{r.title}</div>
              <div className="text-sm text-foreground/80 leading-relaxed flex gap-2">
                <Quote className="w-3.5 h-3.5 shrink-0 mt-1 text-foreground/40" />
                <span>{r.quote}</span>
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                {r.tags.map((t) => (
                  <span
                    key={t}
                    className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-foreground/5 text-muted-foreground"
                  >
                    {t}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
