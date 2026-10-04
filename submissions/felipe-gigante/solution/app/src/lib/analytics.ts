// Consultas do dashboard operacional (PRD §28–30). Sempre comparam com o período anterior.
import { all, one } from "./db";
import { escalationCategories } from "./ai/risk";

export const PERIODS = [1, 7, 30, 60, 90] as const;
const DAY = 86_400_000;

function median(xs: number[]) {
  if (!xs.length) return null;
  const s = [...xs].sort((a, b) => a - b);
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}
const pct = (a: number, b: number) => (b ? (a / b) * 100 : 0);

export async function dashboard(days: number) {
  const now = Date.now();
  const from = now - days * DAY, prevFrom = from - days * DAY;
  const W = "created_at >= ? AND created_at < ?";
  const cur = [from, now], prev = [prevFrom, from];

  const kpi = async (range: number[]) => one<Record<string, number>>(
    `SELECT COUNT(*) total,
      SUM(status IN ('new','open','escalated','pending')) backlog,
      SUM(decision='auto') auto, SUM(decision='suggest') suggest, SUM(decision='human') human,
      AVG(csat) csat, COUNT(csat) csat_n,
      AVG(ai_confidence) conf,
      SUM(kb_score >= 0.27) kb_covered,
      SUM(guardrail_flags LIKE '%"severity":"block"%') guardrail_block,
      SUM(guardrail_flags LIKE '%pii_masked%') pii,
      SUM(sentiment IN ('Frustrated','Angry')) negative,
      SUM(automated=1) automated,
      SUM(automated=1 AND status IN ('resolved','closed')) ai_resolved,
      SUM(automated=1 AND csat >= 4) safe_resolved,
      SUM(risk_level != 'HIGH') eligible
     FROM tickets WHERE ${W}`, range);
  const [k, kp] = await Promise.all([kpi(cur), kpi(prev)]);

  const ttrRows = await all<{ d: number }>(`SELECT resolved_at - created_at d FROM tickets WHERE ${W} AND resolved_at IS NOT NULL`, cur);
  const frtRows = await all<{ d: number }>(`SELECT first_response_at - created_at d FROM tickets WHERE ${W} AND first_response_at IS NOT NULL`, cur);

  const feedback = await one<Record<string, number>>(
    `SELECT SUM(type='reply_accepted') accepted, SUM(type='reply_edited') edited, SUM(type='reply_rejected') rejected,
            SUM(type='escalated') escalated, SUM(type='returned_to_ai') downstream, SUM(type='frustration_detected') frustration
     FROM events WHERE ${W}`, cur);
  const gaps = await one<{ pending: number; occ: number }>("SELECT COUNT(*) pending, COALESCE(SUM(occurrences),0) occ FROM kb_gaps WHERE status='pending'");

  // Volume diário por decisão do gate
  const bucket = days <= 1 ? 3_600_000 : DAY;
  const series = await all<{ b: number; auto: number; suggest: number; human: number }>(
    `SELECT (created_at / ${bucket}) b, SUM(decision='auto') auto, SUM(decision='suggest') suggest, SUM(decision='human') human
     FROM tickets WHERE ${W} GROUP BY b ORDER BY b`, cur);

  // Top topics + tendência vs período anterior
  const topicsCur = await all<{ topic: string; n: number }>(`SELECT topic, COUNT(*) n FROM tickets WHERE ${W} GROUP BY topic ORDER BY n DESC`, cur);
  const topicsPrev = new Map((await all<{ topic: string; n: number }>(`SELECT topic, COUNT(*) n FROM tickets WHERE ${W} GROUP BY topic`, prev)).map((r) => [r.topic, r.n]));
  const topics = topicsCur.map((t) => {
    const p = topicsPrev.get(t.topic) ?? 0;
    return { topic: t.topic, n: t.n, share: pct(t.n, k?.total ?? 0), trend: p ? ((t.n - p) / p) * 100 : null };
  });

  const sentiment = await all<{ sentiment: string; n: number }>(`SELECT sentiment, COUNT(*) n FROM tickets WHERE ${W} GROUP BY sentiment`, cur);
  const categories = await all<{ category: string; team: string; n: number; conf: number }>(
    `SELECT category, team, COUNT(*) n, AVG(category_conf) conf FROM tickets WHERE ${W} GROUP BY category ORDER BY n DESC`, cur);
  const csatByDecision = await all<{ decision: string; csat: number; n: number }>(
    `SELECT decision, AVG(csat) csat, COUNT(csat) n FROM tickets WHERE ${W} AND csat IS NOT NULL GROUP BY decision`, cur);
  const csatByChannel = await all<{ channel: string; csat: number; n: number }>(
    `SELECT channel, AVG(csat) csat, COUNT(csat) n FROM tickets WHERE ${W} AND csat IS NOT NULL GROUP BY channel ORDER BY csat DESC`, cur);
  const priority = await all<{ priority: string; n: number; declared: number }>(
    `SELECT priority, COUNT(*) n, 0 declared FROM tickets WHERE ${W} GROUP BY priority`, cur);
  const declared = await all<{ priority: string; n: number }>(
    `SELECT dataset_priority priority, COUNT(*) n FROM tickets WHERE ${W} AND dataset_priority IS NOT NULL GROUP BY dataset_priority`, cur);

  const reasonsRows = await all<{ risk_reasons: string; risk_level: string; blocked: number }>(
    `SELECT risk_reasons, risk_level, guardrail_flags LIKE '%"severity":"block"%' blocked FROM tickets WHERE ${W} AND decision='human'`, cur);
  const reasonCount = new Map<string, number>();
  for (const r of reasonsRows) {
    for (const c of escalationCategories(r.risk_level, JSON.parse(r.risk_reasons || "[]"), !!r.blocked)) reasonCount.set(c, (reasonCount.get(c) ?? 0) + 1);
  }
  const escalationReasons = [...reasonCount].map(([reason, n]) => ({ reason, n })).sort((a, b) => b.n - a.n).slice(0, 7);

  const fb = feedback ?? {};
  const reviewed = (fb.accepted ?? 0) + (fb.edited ?? 0) + (fb.rejected ?? 0);
  const total = k?.total ?? 0;
  return {
    days,
    total,
    totalPrev: kp?.total ?? 0,
    backlog: k?.backlog ?? 0,
    csat: k?.csat ?? null,
    csatPrev: kp?.csat ?? null,
    csatN: k?.csat_n ?? 0,
    ttrMedianH: (median(ttrRows.map((r) => r.d)) ?? NaN) / 3_600_000,
    ttrN: ttrRows.length,
    frtMedianS: (median(frtRows.map((r) => r.d)) ?? NaN) / 1000,
    frtN: frtRows.length,
    decision: { auto: pct(k?.auto ?? 0, total), suggest: pct(k?.suggest ?? 0, total), human: pct(k?.human ?? 0, total) },
    decisionPrev: { auto: pct(kp?.auto ?? 0, kp?.total ?? 0), human: pct(kp?.human ?? 0, kp?.total ?? 0) },
    automated: k?.automated ?? 0,
    aiResolved: k?.ai_resolved ?? 0,
    safeResolutionRate: pct(k?.safe_resolved ?? 0, k?.automated ?? 0),
    eligible: pct(k?.eligible ?? 0, total),
    acceptance: reviewed ? pct(fb.accepted ?? 0, reviewed) : null,
    feedback: { accepted: fb.accepted ?? 0, edited: fb.edited ?? 0, rejected: fb.rejected ?? 0, downstream: fb.downstream ?? 0, frustration: fb.frustration ?? 0 },
    avgConfidence: (k?.conf ?? 0) * 100,
    kbCoverage: pct(k?.kb_covered ?? 0, total),
    guardrailRate: pct((k?.guardrail_block ?? 0) + (k?.pii ?? 0), total),
    guardrailBlocks: k?.guardrail_block ?? 0,
    negativeShare: pct(k?.negative ?? 0, total),
    gaps: gaps ?? { pending: 0, occ: 0 },
    series: series.map((s) => ({ t: s.b * bucket, auto: s.auto, suggest: s.suggest, human: s.human })),
    bucket,
    topics,
    sentiment,
    categories,
    csatByDecision,
    csatByChannel,
    priority,
    declared,
    escalationReasons,
  };
}

export type Dashboard = Awaited<ReturnType<typeof dashboard>>;
