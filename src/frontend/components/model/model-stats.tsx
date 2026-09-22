"use client";

import { useMemo } from "react";
import {
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { SVMModel, SVMPrediction } from "@/lib/breast-cancer/models";
import { CLASS_BENIGN, CLASS_MALIGNANT } from "@/lib/g4s-theme";

interface ModelStatsProps {
  model: SVMModel;
  prediction: SVMPrediction;
}

function Stat({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint?: string;
}) {
  return (
    <div>
      <div className="text-3xl lg:text-4xl font-display tracking-tight tabular-nums">{value}</div>
      <div className="mt-1 text-sm text-muted-foreground">{label}</div>
      {hint && <div className="text-xs text-muted-foreground/70 font-mono mt-0.5">{hint}</div>}
    </div>
  );
}

export function ModelStats({ model, prediction }: ModelStatsProps) {
  const distance = Math.abs(prediction.decision);

  const charts = useMemo(() => {
    return {
      learning: model.learningCurve.map((p) => ({
        epoch: p.epoch,
        train: +(p.train * 100).toFixed(2),
        test: +(p.test * 100).toFixed(2),
      })),
      bv: model.biasVariance.map((p) => ({
        complexity: p.complexity,
        train: +(p.train * 100).toFixed(2),
        test: +(p.test * 100).toFixed(2),
      })),
    };
  }, [model]);

  return (
    <div className="space-y-12">
      {/* Performance metrics grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-foreground/10 border border-foreground/10">
        <div className="bg-background p-6">
          <Stat
            label="Acurácia"
            value={`${(model.accuracy * 100).toFixed(1)}%`}
            hint="split de teste hold-out"
          />
        </div>
        <div className="bg-background p-6">
          <Stat
            label="ROC-AUC"
            value={(model.rocAuc * 100).toFixed(1) + "%"}
            hint="área sob a curva ROC"
          />
        </div>
        <div className="bg-background p-6">
          <Stat
            label="Score F1"
            value={(model.f1 * 100).toFixed(1) + "%"}
            hint="média harmônica precisão / recall"
          />
        </div>
        <div className="bg-background p-6">
          <Stat
            label="Latência da predição"
            value={`${model.latencyMs.toFixed(1)} ms`}
            hint="inferência de uma amostra"
          />
        </div>
        <div className="bg-background p-6">
          <Stat
            label="Precisão"
            value={(model.precision * 100).toFixed(1) + "%"}
            hint="TP / (TP+FP)"
          />
        </div>
        <div className="bg-background p-6">
          <Stat
            label="Recall"
            value={(model.recall * 100).toFixed(1) + "%"}
            hint="VP / (VP+FN)"
          />
        </div>
        <div className="bg-background p-6">
          <Stat
            label="Vetores de suporte"
            value={model.supportVectors.toString()}
            hint={`treinado em ${model.trainingTimeMs} ms`}
          />
        </div>
        <div className="bg-background p-6">
          <Stat
            label="Distância à fronteira"
            value={distance.toFixed(3)}
            hint={`prob. maligno ${(prediction.probability * 100).toFixed(1)}%`}
          />
        </div>
      </div>

      {/* Learning curve + bias-variance side by side */}
      <div className="grid lg:grid-cols-2 gap-px bg-foreground/10 border border-foreground/10">
        <div className="bg-background p-6">
          <div className="flex items-baseline justify-between mb-5">
            <h4 className="font-display text-xl">Curva de aprendizado</h4>
            <span className="text-xs font-mono text-muted-foreground">acurácia vs. época</span>
          </div>
          <div className="h-60">
            <ResponsiveContainer>
              <LineChart data={charts.learning} margin={{ top: 8, right: 12, left: -20, bottom: 0 }}>
                <XAxis
                  dataKey="epoch"
                  tickLine={false}
                  axisLine={{ stroke: "rgba(20,20,20,0.18)" }}
                  fontSize={10}
                  className="font-mono"
                />
                <YAxis
                  domain={[80, 100]}
                  tickLine={false}
                  axisLine={false}
                  fontSize={10}
                  className="font-mono"
                  tickFormatter={(v) => `${v}%`}
                />
                <Tooltip
                  contentStyle={{
                    background: "rgba(255,255,255,0.95)",
                    border: "1px solid rgba(20,20,20,0.1)",
                    borderRadius: 6,
                    fontFamily: "monospace",
                    fontSize: 12,
                  }}
                  formatter={(v: number) => `${v.toFixed(2)}%`}
                />
                <Line
                  type="monotone"
                  dataKey="train"
                  stroke="#111"
                  strokeWidth={1.6}
                  dot={false}
                  name="train"
                />
                <Line
                  type="monotone"
                  dataKey="test"
                  stroke={CLASS_MALIGNANT}
                  strokeWidth={1.6}
                  dot={false}
                  name="test"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="flex items-center gap-5 mt-4 text-xs font-mono text-muted-foreground">
            <span className="flex items-center gap-2">
              <span className="w-4 h-px bg-foreground" />
              treino
            </span>
            <span className="flex items-center gap-2">
              <span className="w-4 h-px bg-primary" />
              teste
            </span>
          </div>
        </div>

        <div className="bg-background p-6">
          <div className="flex items-baseline justify-between mb-5">
            <h4 className="font-display text-xl">Diagnóstico viés / variância</h4>
            <span className="text-xs font-mono text-muted-foreground">error vs. complexity (C)</span>
          </div>
          <div className="h-60">
            <ResponsiveContainer>
              <LineChart data={charts.bv} margin={{ top: 8, right: 12, left: -20, bottom: 0 }}>
                <XAxis
                  dataKey="complexity"
                  tickLine={false}
                  axisLine={{ stroke: "rgba(20,20,20,0.18)" }}
                  fontSize={10}
                  className="font-mono"
                />
                <YAxis
                  domain={[0, 12]}
                  tickLine={false}
                  axisLine={false}
                  fontSize={10}
                  className="font-mono"
                  tickFormatter={(v) => `${v}%`}
                />
                <Tooltip
                  contentStyle={{
                    background: "rgba(255,255,255,0.95)",
                    border: "1px solid rgba(20,20,20,0.1)",
                    borderRadius: 6,
                    fontFamily: "monospace",
                    fontSize: 12,
                  }}
                  formatter={(v: number) => `${v.toFixed(2)}%`}
                />
                <ReferenceLine
                  y={3}
                  stroke="rgba(20,20,20,0.2)"
                  strokeDasharray="2 4"
                  label={{
                    value: "target err.",
                    position: "right",
                    fontSize: 10,
                    fill: "rgba(20,20,20,0.45)",
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="train"
                  stroke={CLASS_BENIGN}
                  strokeWidth={1.6}
                  dot={false}
                  name="bias (train err.)"
                />
                <Line
                  type="monotone"
                  dataKey="test"
                  stroke={CLASS_MALIGNANT}
                  strokeWidth={1.6}
                  dot={false}
                  name="variance proxy (cv err.)"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="flex items-center gap-5 mt-4 text-xs font-mono text-muted-foreground">
            <span className="flex items-center gap-2">
              <span className="w-4 h-px bg-secondary" />
              viés (erro de treino)
            </span>
            <span className="flex items-center gap-2">
              <span className="w-4 h-px bg-primary" />
              variância (erro CV)
            </span>
          </div>
        </div>
      </div>

      {/* Hyperparameter card */}
      <div className="border border-foreground/10 p-6">
        <div className="flex items-baseline justify-between mb-4">
          <h4 className="font-display text-xl">Hiperparâmetros</h4>
          <span className="text-xs font-mono text-muted-foreground">{model.formula}</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          {model.hyperparameters.map((h) => (
            <div key={h.name} className="font-mono text-sm">
              <div className="text-muted-foreground">{h.name}</div>
              <div className="text-foreground">{h.value}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
