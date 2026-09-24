import { useState } from 'react';
import { t } from '../i18n/pt-BR';

export interface HBarDatum {
  key: string;
  label: string;
  value: number; // 0..max
  ci?: [number, number];
  highlight?: boolean;
}

interface Props {
  data: HBarDatum[];
  max: number;
  formatValue: (v: number) => string;
  formatCi?: (lo: number, hi: number) => string;
  ariaLabel: string;
}

/**
 * Horizontal bars with a 95% CI band, values printed beside each bar, plus a table toggle.
 * Small inline SVG — no chart library. One series (highlight = ours), so no legend box.
 */
export function HBarChart({ data, max, formatValue, formatCi, ariaLabel }: Props) {
  const [table, setTable] = useState(false);
  const rowH = 36;
  const labelW = 180;
  const valueW = 150;
  const width = 640;
  const plotW = width - labelW - valueW;
  const height = data.length * rowH;
  const x = (v: number) => labelW + (Math.min(Math.max(v, 0), max) / max) * plotW;
  const summary = data.map((d) => `${d.label} ${formatValue(d.value)}`).join('; ');

  return (
    <div>
      <div className="flex justify-end">
        <button
          type="button"
          className="btn-secondary h-8 text-xs"
          aria-pressed={table}
          onClick={() => setTable((v) => !v)}
        >
          {table ? t.quality.showChart : t.quality.showTable}
        </button>
      </div>
      {table ? (
        <table className="mt-3 w-full text-sm tabular-nums">
          <thead>
            <tr className="text-left text-xs font-semibold text-g4-muted">
              <th scope="col" className="py-1">
                {t.quality.columns.method}
              </th>
              <th scope="col" className="py-1 text-right">
                {t.quality.columns.hits}
              </th>
              <th scope="col" className="py-1 text-right">
                {t.quality.columns.ci}
              </th>
            </tr>
          </thead>
          <tbody>
            {data.map((d) => (
              <tr key={d.key} className="border-t border-g4line">
                <th scope="row" className="py-1 text-left font-semibold">
                  {d.label}
                </th>
                <td className="py-1 text-right">{formatValue(d.value)}</td>
                <td className="py-1 text-right">
                  {d.ci && formatCi ? formatCi(d.ci[0], d.ci[1]) : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <svg
          role="img"
          aria-label={`${ariaLabel}: ${summary}`}
          viewBox={`0 0 ${width} ${height}`}
          className="mt-3 w-full font-sans"
        >
          {data.map((d, i) => {
            const y = i * rowH;
            const barY = y + 10;
            return (
              <g key={d.key}>
                <text x={0} y={y + rowH / 2 + 4} fontSize="13" fontWeight="600" fill="#031A26">
                  {d.label}
                </text>
                <rect x={labelW} y={barY} width={plotW} height={16} rx={4} fill="#F5F4F3" />
                <rect
                  x={labelW}
                  y={barY}
                  width={Math.max(x(d.value) - labelW, 0)}
                  height={16}
                  rx={4}
                  fill={d.highlight ? '#001F35' : '#9AA3AE'}
                />
                {d.ci && (
                  <rect
                    x={x(d.ci[0])}
                    y={barY + 4}
                    width={Math.max(x(d.ci[1]) - x(d.ci[0]), 2)}
                    height={8}
                    rx={2}
                    fill="#6B7A8C"
                    opacity={0.6}
                  />
                )}
                <text
                  x={labelW + plotW + 8}
                  y={y + rowH / 2 + 4}
                  fontSize="13"
                  fontWeight="700"
                  fill="#031A26"
                >
                  {formatValue(d.value)}
                  {d.ci && formatCi && (
                    <tspan fontWeight="500" fill="#5B6673">
                      {' '}
                      {formatCi(d.ci[0], d.ci[1])}
                    </tspan>
                  )}
                </text>
              </g>
            );
          })}
        </svg>
      )}
    </div>
  );
}
