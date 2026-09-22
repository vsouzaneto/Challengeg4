"use client";

import { FEATURES, FeatureId, type FeatureMeta } from "@/lib/breast-cancer/features";
import { CLASS_BENIGN, CLASS_MALIGNANT } from "@/lib/g4s-theme";
import { Slider } from "@/components/ui/slider";

function formatValue(value: number, feature: FeatureMeta): string {
  if (feature.step >= 1) return value.toFixed(0);
  if (feature.step >= 0.1) return value.toFixed(1);
  if (feature.step >= 0.01) return value.toFixed(2);
  if (feature.step >= 0.001) return value.toFixed(3);
  return value.toFixed(4);
}

interface FeatureSlidersProps {
  values: number[];
  onChange: (idx: number, value: number) => void;
  xFeature: FeatureId;
  yFeature: FeatureId;
  onReset: () => void;
  onRandomize: () => void;
  onUseBenignMean: () => void;
  onUseMalignantMean: () => void;
}

export function FeatureSliders({
  values,
  onChange,
  xFeature,
  yFeature,
  onReset,
  onRandomize,
  onUseBenignMean,
  onUseMalignantMean,
}: FeatureSlidersProps) {
  return (
    <div className="space-y-5">
      {/* Quick actions */}
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={onReset}
          className="text-xs font-mono px-3 py-1.5 border border-foreground/15 hover:border-foreground/30 rounded-md transition-colors"
        >
          neutro
        </button>
        <button
          type="button"
          onClick={onUseBenignMean}
          className="text-xs font-mono px-3 py-1.5 border border-foreground/15 hover:border-foreground/30 rounded-md transition-colors"
        >
          média benigna
        </button>
        <button
          type="button"
          onClick={onUseMalignantMean}
          className="text-xs font-mono px-3 py-1.5 border border-foreground/15 hover:border-foreground/30 rounded-md transition-colors"
        >
          média maligna
        </button>
        <button
          type="button"
          onClick={onRandomize}
          className="text-xs font-mono px-3 py-1.5 border border-foreground/15 hover:border-foreground/30 rounded-md transition-colors ml-auto"
        >
          aleatorizar
        </button>
      </div>

      <div className="space-y-5">
        {FEATURES.map((feature, idx) => {
          const isXAxis = feature.id === xFeature;
          const isYAxis = feature.id === yFeature;
          const value = values[idx];
          const valuePct = ((value - feature.min) / (feature.max - feature.min)) * 100;
          const benignPct =
            ((feature.benignMean - feature.min) / (feature.max - feature.min)) * 100;
          const malignantPct =
            ((feature.malignantMean - feature.min) / (feature.max - feature.min)) * 100;

          return (
            <div key={feature.id} className="space-y-1.5">
              <div className="flex items-baseline justify-between gap-2">
                <div className="flex items-baseline gap-2 min-w-0">
                  <span className="font-display text-sm truncate">{feature.label}</span>
                  {(isXAxis || isYAxis) && (
                    <span className="text-[10px] font-mono uppercase tracking-wider text-foreground/50 shrink-0">
                      eixo {isXAxis ? "X" : "Y"}
                    </span>
                  )}
                </div>
                <span className="font-mono text-sm tabular-nums shrink-0">
                  {formatValue(value, feature)}
                  {feature.unit ? (
                    <span className="text-muted-foreground"> {feature.unit}</span>
                  ) : null}
                </span>
              </div>

              <div className="relative">
                {/* Class-mean markers */}
                <div className="absolute -top-1 left-0 right-0 h-3 pointer-events-none">
                  <span
                    className="absolute -translate-x-1/2 w-px h-2 bg-secondary"
                    style={{ left: `${benignPct}%` }}
                    title={`Média benigna ${formatValue(feature.benignMean, feature)}`}
                  />
                  <span
                    className="absolute -translate-x-1/2 w-px h-2 bg-primary"
                    style={{ left: `${malignantPct}%` }}
                    title={`Média maligna ${formatValue(feature.malignantMean, feature)}`}
                  />
                </div>

                <Slider
                  value={[value]}
                  min={feature.min}
                  max={feature.max}
                  step={feature.step}
                  onValueChange={(v) => onChange(idx, v[0])}
                />
              </div>

              <div className="flex items-center justify-between text-[10px] font-mono text-muted-foreground tabular-nums">
                <span>{formatValue(feature.min, feature)}</span>
                <span
                  className="opacity-60"
                  style={{
                    color:
                      valuePct < (benignPct + malignantPct) / 2
                        ? CLASS_BENIGN
                        : CLASS_MALIGNANT,
                  }}
                >
                  rank RFE {feature.rfeRank} · importância {(feature.importance * 100).toFixed(0)}%
                </span>
                <span>{formatValue(feature.max, feature)}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
