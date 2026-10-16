import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { Conta } from "../types";
import { usageSeries } from "../lib/filters";
import type { Bundle } from "../types";
import { G4_CHART } from "../theme/g4";

const tooltipStyle = {
  contentStyle: {
    background: "#121f2a",
    border: "1px solid rgba(184, 142, 94, 0.32)",
    borderRadius: 8,
  },
  labelStyle: { color: "#ffffff" },
};

const STATUS_COLOR: Record<string, string> = {
  "Ativa (revolving)": G4_CHART.primary,
  "Ativa estável": G4_CHART.secondary,
  "Churn líquido": G4_CHART.danger,
};

type PickHandlers = {
  onPickStatus?: (status: string) => void;
  onPickIndustry?: (industry: string) => void;
};

export function StatusChart({ rows, onPickStatus }: { rows: Conta[] } & PickHandlers) {
  const counts: Record<string, number> = {};
  rows.forEach((r) => {
    counts[r.status_conta] = (counts[r.status_conta] ?? 0) + 1;
  });
  const total = rows.length || 1;
  const data = Object.entries(counts).map(([name, value]) => ({
    name,
    value,
    pct: Math.round((value / total) * 100),
  }));

  if (!rows.length) {
    return <p className="chart-empty">Nenhuma conta no recorte. Ajuste os filtros.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={260} className="chart-interactive">
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          innerRadius={62}
          outerRadius={92}
          paddingAngle={3}
          cursor="pointer"
          onClick={(_, index) => {
            const name = data[index]?.name;
            if (name && onPickStatus) onPickStatus(name);
          }}
          label={(props) => {
            const pct = (props as { payload?: { pct?: number } }).payload?.pct;
            return pct != null ? `${pct}%` : "";
          }}
          labelLine={false}
        >
          {data.map((d) => (
            <Cell key={d.name} fill={STATUS_COLOR[d.name] ?? "#737373"} stroke="none" />
          ))}
        </Pie>
        <Tooltip
          {...tooltipStyle}
          formatter={(v, _n, p) => {
            const n = typeof v === "number" ? v : Number(v);
            const pct = (p?.payload as { pct?: number })?.pct;
            return [`${n} contas${pct != null ? ` (${pct}%)` : ""}`, "Status"];
          }}
        />
        <Legend wrapperStyle={{ fontSize: 12, color: "#a3a3a3" }} />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function IndustryChurnChart({ rows, onPickIndustry }: { rows: Conta[] } & PickHandlers) {
  const inds = [...new Set(rows.map((r) => r.industria))].sort();
  const data = inds
    .map((ind) => {
      const g = rows.filter((r) => r.industria === ind);
      const rate = g.length ? g.filter((r) => r.churn_liquido).length / g.length : 0;
      return { industria: ind, taxa: Math.round(rate * 1000) / 10, n: g.length };
    })
    .sort((a, b) => b.taxa - a.taxa);

  if (!rows.length) {
    return <p className="chart-empty">Nenhuma conta no recorte.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={260} className="chart-interactive">
      <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" vertical={false} />
        <XAxis dataKey="industria" tick={{ fill: "#a3a3a3", fontSize: 11 }} axisLine={false} tickLine={false} />
        <YAxis
          tick={{ fill: "#a3a3a3", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          unit="%"
          domain={[0, "auto"]}
        />
        <Tooltip
          {...tooltipStyle}
          cursor={{ fill: "rgba(184, 142, 94, 0.1)", className: "soft-bar-cursor" }}
          formatter={(v, _n, p) => {
            const pct = typeof v === "number" ? v : Number(v);
            const n = (p?.payload as { n?: number })?.n;
            return [`${pct}%${n != null ? ` · ${n} contas` : ""}`, "Churn líquido"];
          }}
        />
        <Bar
          dataKey="taxa"
          fill={G4_CHART.primary}
          radius={[6, 6, 0, 0]}
          maxBarSize={52}
          cursor="pointer"
          onClick={(entry) => {
            const ind = (entry as { industria?: string }).industria;
            if (ind && onPickIndustry) onPickIndustry(ind);
          }}
        >
          {data.map((d) => (
            <Cell key={d.industria} fill={d.taxa >= 25 ? G4_CHART.danger : G4_CHART.primary} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export function UsageTrendChart({
  bundle,
  industries,
  periodoInicio,
  periodoFim,
  onPickIndustry,
}: {
  bundle: Bundle;
  industries: string[];
  periodoInicio?: string;
  periodoFim?: string;
  onPickIndustry?: (industry: string) => void;
}) {
  const series = usageSeries(bundle, industries, periodoInicio ?? "", periodoFim ?? "");
  const data = series.months.map((label, i) => {
    const row: Record<string, string | number> = { mes: label };
    series.datasets.forEach((d) => {
      row[d.name] = d.values[i];
    });
    return row;
  });

  return (
    <ResponsiveContainer width="100%" height={280} className="chart-interactive">
      <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
        <XAxis dataKey="mes" tick={{ fill: "#a3a3a3", fontSize: 11 }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fill: "#a3a3a3", fontSize: 11 }} axisLine={false} tickLine={false} />
        <Tooltip {...tooltipStyle} />
        <Legend
          wrapperStyle={{ fontSize: 12, color: "#a3a3a3", cursor: "pointer" }}
          onClick={(e) => {
            const name = String(e.value ?? "");
            if (name && onPickIndustry) onPickIndustry(name);
          }}
        />
        {series.datasets.map((d) => (
          <Line
            key={d.name}
            type="monotone"
            dataKey={d.name}
            stroke={d.color}
            strokeWidth={2}
            dot={{ r: 3, fill: d.color, cursor: "pointer" }}
            activeDot={{
              r: 6,
              cursor: "pointer",
              onClick: (_e, payload) => {
                const name = (payload as { dataKey?: string }).dataKey;
                if (name && onPickIndustry) onPickIndustry(String(name));
              },
            }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
