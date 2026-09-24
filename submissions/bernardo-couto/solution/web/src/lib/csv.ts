import type { ScoredDeal } from '../api/client';

const HEADER = [
  'opportunity_id',
  'tier',
  'priority_score',
  'account',
  'product',
  'sales_agent',
  'manager',
  'regional_office',
  'deal_stage',
  'days_in_engaging',
  'expected_value',
  'sales_price',
  'p_win',
  'confidence',
  'main_reason',
  'next_action',
  'as_of',
  'model_version',
];

function cell(v: unknown): string {
  if (v === null || v === undefined) return '';
  const s = String(v);
  return /[";\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

/** Semicolon-separated (Excel pt-BR opens it directly), UTF-8 with BOM. */
export function dealsToCsv(deals: ScoredDeal[]): string {
  const rows = deals.map((d) =>
    [
      d.opportunity_id,
      d.tier,
      d.priority_score,
      d.account,
      d.product,
      d.sales_agent,
      d.manager,
      d.regional_office,
      d.deal_stage,
      d.days_in_engaging,
      d.expected_value,
      d.sales_price,
      d.p_win,
      d.confidence,
      d.reasons[0]?.text_pt,
      d.next_action,
      d.as_of,
      d.model_version,
    ]
      .map(cell)
      .join(';'),
  );
  return '﻿' + [HEADER.join(';'), ...rows].join('\r\n');
}

export function downloadCsv(filename: string, content: string) {
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.rel = 'noopener';
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
