"use client";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

// Paleta categórica validada (lightness band, chroma, CVD, normal-vision) — derivada das cores G4.
export const SERIES = { auto: "#1867a8", suggest: "#c4893f", human: "#b0405a" } as const;
const AXIS = { fontSize: 11, fill: "#5b6b7a" };
const GRID = "#ebe8e4";
const tooltipStyle = { borderRadius: 10, border: "1px solid #e3e0dc", fontSize: 12, boxShadow: "0 6px 20px rgba(0,32,55,.08)" };

export function DecisionVolume({ data, hourly }: { data: { t: number; auto: number; suggest: number; human: number }[]; hourly: boolean }) {
  const fmt = (t: number) => new Date(t).toLocaleString("pt-BR", hourly ? { hour: "2-digit" } : { day: "2-digit", month: "2-digit" });
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} margin={{ left: -18, right: 8, top: 4 }} barCategoryGap={2}>
        <CartesianGrid vertical={false} stroke={GRID} />
        <XAxis dataKey="t" tickFormatter={fmt} tick={AXIS} tickLine={false} axisLine={{ stroke: GRID }} minTickGap={24} />
        <YAxis tick={AXIS} tickLine={false} axisLine={false} allowDecimals={false} />
        <Tooltip contentStyle={tooltipStyle} labelFormatter={(t) => fmt(Number(t))} cursor={{ fill: "rgba(0,32,55,.04)" }} />
        <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 12 }} />
        <Bar dataKey="auto" name="AUTO (IA responde)" stackId="a" fill={SERIES.auto} stroke="#fff" strokeWidth={1} />
        <Bar dataKey="suggest" name="SUGESTÃO (humano aprova)" stackId="a" fill={SERIES.suggest} stroke="#fff" strokeWidth={1} />
        <Bar dataKey="human" name="HUMANO" stackId="a" fill={SERIES.human} stroke="#fff" strokeWidth={1} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function HBars({ data, color = "#002037", unit = "", height }: { data: { label: string; value: number }[]; color?: string; unit?: string; height?: number }) {
  return (
    <ResponsiveContainer width="100%" height={height ?? Math.max(120, data.length * 30)}>
      <BarChart data={data} layout="vertical" margin={{ left: 8, right: 36 }}>
        <XAxis type="number" hide />
        <YAxis type="category" dataKey="label" width={170} tick={{ ...AXIS, fill: "#0f1b26" }} tickLine={false} axisLine={false} />
        <Tooltip contentStyle={tooltipStyle} formatter={(v) => [`${Number(v).toLocaleString("pt-BR", { maximumFractionDigits: 2 })}${unit}`, ""]} cursor={{ fill: "rgba(0,32,55,.04)" }} />
        <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={14} label={{ position: "right", fontSize: 11, fill: "#5b6b7a", formatter: (v: unknown) => `${Number(v).toLocaleString("pt-BR", { maximumFractionDigits: 1 })}${unit}` }}>
          {data.map((d) => <Cell key={d.label} fill={color} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export function CalibrationCurve({ data, auto, suggest }: { data: { threshold: number; coverage: number; accuracy: number | null }[]; auto: number; suggest: number }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data} margin={{ left: -12, right: 12, top: 8 }}>
        <CartesianGrid stroke={GRID} vertical={false} />
        <XAxis dataKey="threshold" tick={AXIS} tickLine={false} axisLine={{ stroke: GRID }} />
        <YAxis domain={[40, 100]} tick={AXIS} tickLine={false} axisLine={false} unit="%" />
        <Tooltip contentStyle={tooltipStyle} labelFormatter={(t) => `threshold ≥ ${t}`} formatter={(v, n) => [`${v}%`, n]} />
        <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 12 }} />
        <Line dataKey="accuracy" name="Acurácia nos tickets acima do threshold" stroke={SERIES.auto} strokeWidth={2} dot={{ r: 3 }} />
        <Line dataKey="coverage" name="Cobertura (% de tickets acima)" stroke={SERIES.suggest} strokeWidth={2} dot={{ r: 3 }} />
        <ReferenceLine x={suggest} stroke="#b0405a" strokeDasharray="4 4" label={{ value: "SUGESTÃO", fontSize: 10, fill: "#5b6b7a", position: "insideTopLeft" }} />
        <ReferenceLine x={auto} stroke="#1867a8" strokeDasharray="4 4" label={{ value: "AUTO", fontSize: 10, fill: "#5b6b7a", position: "insideTopLeft" }} />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function Sparkline({ data }: { data: number[] }) {
  return (
    <ResponsiveContainer width="100%" height={40}>
      <AreaChart data={data.map((v, i) => ({ i, v }))} margin={{ top: 2, bottom: 2, left: 0, right: 0 }}>
        <Area dataKey="v" stroke="#c08e51" fill="#c08e51" fillOpacity={0.15} strokeWidth={2} />
      </AreaChart>
    </ResponsiveContainer>
  );
}
