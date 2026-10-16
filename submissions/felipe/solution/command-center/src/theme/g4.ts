/** G4 Gestão e Estratégia — tonalidades da marca (logo / site). */
export const G4 = {
  navy: "#0d161e",
  navyDeep: "#0a1218",
  navyCard: "#121f2a",
  navyElevated: "#162b45",
  gold: "#b88e5e",
  goldMuted: "#a68966",
  goldLight: "#c9a876",
  goldSoft: "rgba(184, 142, 94, 0.18)",
  goldBorder: "rgba(184, 142, 94, 0.32)",
  white: "#ffffff",
  muted: "#8a9aab",
  inkOnGold: "#0d161e",
  danger: "#d48484",
  success: "#7aafa0",
} as const;

export const G4_CHART = {
  primary: G4.gold,
  secondary: "#e8eaed",
  tertiary: "#5a7088",
  quaternary: G4.goldMuted,
  danger: G4.danger,
  success: G4.success,
  grid: "rgba(184, 142, 94, 0.1)",
} as const;
