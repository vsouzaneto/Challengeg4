// Priority Score = Severity + Urgency + Customer Sentiment + Topic Risk (PRD §17).
// O dataset mostrou 25% dos tickets como "Critical" e prioridade sem relação com o texto:
// aqui a prioridade é derivada de sinais observáveis e explicada componente a componente.
import type { RiskLevel } from "./risk";

export type Priority = "Low" | "Medium" | "High" | "Critical";
export type PriorityResult = { priority: Priority; score: number; breakdown: Record<string, number>; reasons: string[] };

const SEVERITY: [RegExp, number, string][] = [
  [/\b(all (users|employees)|everyone|entire (team|company)|production|outage|down for|todos (os )?(usuários|usuarios)|fora do ar|parado)/i, 30, "impacto amplo"],
  [/\b(lawyer|legal action|lawsuit|procon|advogad|processar|reclame aqui)/i, 35, "ameaça jurídica"],
  [/\b(lost|data loss|security|hacked|fraud|perdi|perda|invadid|fraude)/i, 25, "impacto irreversível/segurança"],
  [/\b(can'?t|cannot|unable|not working|doesn'?t work|won'?t|blocked|locked|não consigo|nao consigo|não funciona|nao funciona|bloquead)/i, 15, "bloqueio de uso"],
  [/\b(slow|sometimes|intermittent|minor|lento|às vezes|as vezes|intermitente)/i, 5, "degradação parcial"],
];
const URGENCY: [RegExp, number, string][] = [
  [/\b(urgent|asap|immediately|right now|emergency|urgente|imediatamente|agora|emergência|emergencia)/i, 15, "urgência explícita"],
  [/\b(\d+|three|two|several|três|tres|dois|vários|varios) (days|weeks|dias|semanas)\b/i, 12, "esperando há dias"],
  [/\b(again|already contacted|second time|third time|de novo|novamente|já entrei em contato|ja entrei em contato|segunda vez|terceira vez)/i, 12, "contato repetido"],
  [/\b(deadline|today|tomorrow|prazo|hoje|amanhã|amanha)\b/i, 8, "prazo"],
];

export function scorePriority(text: string, sentimentScore: number, risk: RiskLevel): PriorityResult {
  const reasons: string[] = [];
  let severity = 0, urgency = 0;
  for (const [re, pts, why] of SEVERITY) if (re.test(text)) { severity = Math.max(severity, pts); reasons.push(why); }
  for (const [re, pts, why] of URGENCY) if (re.test(text)) { urgency += pts; reasons.push(why); }
  urgency = Math.min(urgency, 25);
  const sentiment = Math.round(Math.max(0, 60 - sentimentScore) / 3); // 0..20
  const topic = risk === "HIGH" ? 20 : risk === "MEDIUM" ? 10 : 0;
  const score = severity + urgency + sentiment + topic;
  const priority: Priority = score >= 60 ? "Critical" : score >= 40 ? "High" : score >= 20 ? "Medium" : "Low";
  return { priority, score, breakdown: { severity, urgency, sentiment, topic }, reasons };
}
