// Marca G4 (wordmark nas cores oficiais). Para usar a logo oficial, coloque o arquivo em
// public/g4-logo.svg e troque este componente por <img src="/g4-logo.svg" />.
export function G4Mark({ size = 36 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" aria-label="G4">
      <rect width="40" height="40" rx="9" fill="#002037" />
      <rect x="1" y="1" width="38" height="38" rx="8" fill="none" stroke="#C08E51" strokeOpacity=".55" />
      <text x="20" y="26.5" textAnchor="middle" fontFamily="var(--font-manrope), sans-serif" fontWeight="800" fontSize="17" fill="#F3F2F1">
        G<tspan fill="#C08E51">4</tspan>
      </text>
    </svg>
  );
}

export function Logo({ light = false }: { light?: boolean }) {
  return (
    <div className="flex items-center gap-2.5">
      <G4Mark />
      <div className="leading-tight">
        <div className={`h-display text-[15px] font-extrabold ${light ? "text-offwhite" : "text-navy"}`}>AI Support OS</div>
        <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-gold">G4 · AI Master</div>
      </div>
    </div>
  );
}
