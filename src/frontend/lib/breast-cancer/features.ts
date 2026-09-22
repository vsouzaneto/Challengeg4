// Feature definitions for the Wisconsin Diagnostic Breast Cancer (WDBC) dataset.
// The min / max / step values approximate the empirical ranges in the public dataset.
// Each feature stores both class means so we can generate realistic mock data and
// compute interpretable decision boundaries without a live backend.

export type FeatureId =
  | "radius_mean"
  | "texture_mean"
  | "perimeter_mean"
  | "area_mean"
  | "smoothness_mean"
  | "compactness_mean"
  | "concavity_mean"
  | "concave_points_mean"
  | "symmetry_mean"
  | "fractal_dimension_mean";

export interface FeatureMeta {
  id: FeatureId;
  label: string;
  short: string;
  unit?: string;
  min: number;
  max: number;
  step: number;
  benignMean: number;
  benignSd: number;
  malignantMean: number;
  malignantSd: number;
  rfeRank: number; // 1 = strongest selected, higher = less informative
  importance: number; // 0..1 SHAP-style importance score
  description: string;
}

export const FEATURES: FeatureMeta[] = [
  {
    id: "radius_mean",
    label: "Raio (média)",
    short: "Raio",
    unit: "mm",
    min: 6,
    max: 30,
    step: 0.1,
    benignMean: 12.2,
    benignSd: 1.8,
    malignantMean: 17.5,
    malignantSd: 3.2,
    rfeRank: 1,
    importance: 0.92,
    description: "Distância média do centro do núcleo celular ao perímetro.",
  },
  {
    id: "texture_mean",
    label: "Textura (média)",
    short: "Textura",
    min: 9,
    max: 40,
    step: 0.1,
    benignMean: 17.9,
    benignSd: 4,
    malignantMean: 21.6,
    malignantSd: 4,
    rfeRank: 6,
    importance: 0.41,
    description: "Desvio-padrão dos valores de cinza no núcleo celular.",
  },
  {
    id: "perimeter_mean",
    label: "Perímetro (média)",
    short: "Perímetro",
    unit: "px",
    min: 40,
    max: 200,
    step: 0.5,
    benignMean: 78.1,
    benignSd: 11.8,
    malignantMean: 115.4,
    malignantSd: 21.9,
    rfeRank: 2,
    importance: 0.9,
    description: "Perímetro médio do núcleo celular.",
  },
  {
    id: "area_mean",
    label: "Área (média)",
    short: "Área",
    unit: "px²",
    min: 140,
    max: 2500,
    step: 1,
    benignMean: 462.8,
    benignSd: 134,
    malignantMean: 978.4,
    malignantSd: 367,
    rfeRank: 3,
    importance: 0.88,
    description: "Área média do núcleo celular.",
  },
  {
    id: "smoothness_mean",
    label: "Suavidade (média)",
    short: "Suavidade",
    min: 0.05,
    max: 0.17,
    step: 0.001,
    benignMean: 0.0925,
    benignSd: 0.0134,
    malignantMean: 0.1029,
    malignantSd: 0.0125,
    rfeRank: 9,
    importance: 0.23,
    description: "Variação local dos comprimentos de raio.",
  },
  {
    id: "compactness_mean",
    label: "Compacidade (média)",
    short: "Compacidade",
    min: 0.02,
    max: 0.36,
    step: 0.001,
    benignMean: 0.0801,
    benignSd: 0.0337,
    malignantMean: 0.1452,
    malignantSd: 0.054,
    rfeRank: 7,
    importance: 0.38,
    description: "Perímetro² / área − 1,0 — mede o quão compacto é o núcleo.",
  },
  {
    id: "concavity_mean",
    label: "Concavidade (média)",
    short: "Concavidade",
    min: 0,
    max: 0.43,
    step: 0.001,
    benignMean: 0.0461,
    benignSd: 0.0436,
    malignantMean: 0.16,
    malignantSd: 0.075,
    rfeRank: 4,
    importance: 0.81,
    description: "Severidade das porções côncavas do contorno do núcleo.",
  },
  {
    id: "concave_points_mean",
    label: "Pontos côncavos (média)",
    short: "Pts. côncavos",
    min: 0,
    max: 0.21,
    step: 0.001,
    benignMean: 0.0258,
    benignSd: 0.0159,
    malignantMean: 0.0879,
    malignantSd: 0.0345,
    rfeRank: 5,
    importance: 0.78,
    description: "Número de porções côncavas do contorno.",
  },
  {
    id: "symmetry_mean",
    label: "Simetria (média)",
    short: "Simetria",
    min: 0.1,
    max: 0.31,
    step: 0.001,
    benignMean: 0.1742,
    benignSd: 0.0248,
    malignantMean: 0.1928,
    malignantSd: 0.0276,
    rfeRank: 8,
    importance: 0.27,
    description: "Simetria da forma do núcleo celular.",
  },
  {
    id: "fractal_dimension_mean",
    label: "Dim. fractal (média)",
    short: "Dim. fractal",
    min: 0.045,
    max: 0.1,
    step: 0.0005,
    benignMean: 0.0629,
    benignSd: 0.0067,
    malignantMean: 0.0627,
    malignantSd: 0.0076,
    rfeRank: 10,
    importance: 0.09,
    description: "Aproximação de costa − 1,0 (complexidade do contorno).",
  },
];

export const FEATURE_INDEX = Object.fromEntries(
  FEATURES.map((f, i) => [f.id, i])
) as Record<FeatureId, number>;

export const FEATURE_IDS = FEATURES.map((f) => f.id);

// Normalize a value to 0..1 based on its feature range.
export function normalize(value: number, feature: FeatureMeta): number {
  return (value - feature.min) / (feature.max - feature.min);
}

export function denormalize(value: number, feature: FeatureMeta): number {
  return feature.min + value * (feature.max - feature.min);
}

// Convert a full feature vector (in original units, ordered like FEATURES) into
// a normalized [0,1] vector — what most of the SVM math operates on.
export function normalizeVector(values: number[]): number[] {
  return values.map((v, i) => normalize(v, FEATURES[i]));
}
