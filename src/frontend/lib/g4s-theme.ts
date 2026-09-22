/** Hex for canvas / SVG / Recharts. Same values as `--g4s-*` in tokens.css. */
export const g4s = {
  navy: "#32445A",
  steel: "#466381",
  slate: "#9CA5AC",
  ice: "#E3EAF2",
  mist: "#EFF2FB",
  canvas: "#FFFFFF",
  ok: "#3D5A4C",
  warn: "#8A7348",
  danger: "#7A3E44",
} as const;

export const CLASS_BENIGN = g4s.steel;
export const CLASS_MALIGNANT = g4s.navy;
export const CLASS_CANCER = g4s.navy;
export const CLASS_NO_CANCER = g4s.steel;
