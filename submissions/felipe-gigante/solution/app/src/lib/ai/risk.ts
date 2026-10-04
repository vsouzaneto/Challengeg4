// Intenção + risco. Decide o que NÃO automatizar (PRD §23 e §52).
// Intenções usam o mesmo vocabulário de "Ticket Subject" do Dataset 1, para unificar os dashboards.
import { normalizeToEnglish } from "./text";

export type RiskLevel = "LOW" | "MEDIUM" | "HIGH";
export type Intent = { topic: string; matched: string | null };
export type Risk = { level: RiskLevel; reasons: string[]; mandatoryHuman: boolean };

const INTENTS: [string, RegExp][] = [
  ["Refund request", /\b(refund|money back|return (it|the product|my)|chargeback|reembolso|estorno|devolu|dinheiro de volta|ressarc)/i],
  ["Cancellation request", /\b(cancel|unsubscribe|close my account|terminate|cancelar|cancelamento|encerrar (minha )?conta)/i],
  ["Payment issue", /\b(payment|charged|charge|invoice|billing|card declined|double charge|paid|pagamento|cobran|cobrad|fatura|boleto|nota fiscal)/i],
  ["Account access", /\b(password|login|log in|sign in|locked out|account access|2fa|two.factor|reset|senha|acess(o|ar) (a |à )?(minha )?conta|bloquead)/i],
  ["Delivery problem", /\b(delivery|shipping|shipment|tracking|package|arriv|late order|entrega|rastreio|pedido (não|nao) chegou|atrasad)/i],
  ["Data loss", /\b(lost (all )?(my )?(data|files|photos)|data loss|deleted (my )?files|perdi (meus |os )?(dados|arquivos|fotos))/i],
  ["Battery life", /\b(battery|charging|drains?|bateria|carrega)/i],
  ["Network problem", /\b(wifi|wi-fi|network|internet|connect(ion)?|vpn|bluetooth|rede|conex)/i],
  ["Display issue", /\b(screen|display|flicker|pixels?|tela|imagem)/i],
  ["Software bug", /\b(crash|bug|freez|error message|update broke|app closes|erro|travando|trava)/i],
  ["Installation support", /\b(install|installation|instal)/i],
  ["Product setup", /\b(set ?up|configure|pair|configurar|configura)/i],
  ["Product compatibility", /\b(compatib|work with|works with|funciona com)/i],
  ["Peripheral compatibility", /\b(keyboard|mouse|printer|adapter|cable|teclado|impressora|adaptador|cabo)/i],
  ["Hardware issue", /\b(broken|hardware|won't turn on|doesn't turn on|overheat|quebr|não liga|nao liga|esquent)/i],
  ["Product recommendation", /\b(recommend|which (model|one) should|best (option|model)|recomend|qual (modelo|devo))/i],
];

export function detectIntent(text: string): Intent {
  for (const [topic, re] of INTENTS) {
    const m = text.match(re) ?? normalizeToEnglish(text).match(re);
    if (m) return { topic, matched: m[0] };
  }
  return { topic: "Other", matched: null };
}

const HIGH: [RegExp, string][] = [
  [/\b(refund|chargeback|money back|reembolso|estorno|charged twice|double charge|cobrado duas vezes|cobrança indevida|cobranca indevida|dinheiro de volta|devolver (o|meu) dinheiro|ressarcimento)/i, "Financeiro: reembolso/chargeback"],
  [/\b(cancel|close my account|switch(ing)? to (a )?competitor|cancelar|cancelamento|encerrar (minha )?conta|vou trocar de)/i, "Churn: cancelamento"],
  [/\b(lawyer|lawsuit|sue|legal action|procon|advogad|processar|processo judicial|reclame aqui|anpd|lgpd)/i, "Jurídico: ameaça legal/regulatória"],
  [/\b(hacked|fraud|unauthori[sz]ed|stolen|someone (else )?(logged|accessed)|invadid|fraude|roubad|não reconheço|nao reconheco|golpe)/i, "Segurança: fraude/conta comprometida"],
  [/\b(lost (all )?(my )?(data|files|photos)|data loss|perdi (todos )?(os )?(meus )?(dados|arquivos|fotos))/i, "Impacto irreversível: perda de dados"],
  [/\b(delete my (data|personal)|apagar meus dados|meus dados pessoais|personal data request)/i, "Dados pessoais (LGPD)"],
];
const MEDIUM: [RegExp, string][] = [
  [/\b(payment|invoice|billing|pagamento|fatura|boleto|nota fiscal|cobran)/i, "Financeiro: dúvida de cobrança"],
  [/\b(warranty|rma|replacement|garantia|troca)/i, "Garantia / troca"],
  [/\b(enterprise|contract|contrato|SLA)\b/i, "Conta estratégica / contrato"],
];

const DECLARED: Record<string, [RiskLevel, string]> = {
  "Refund request": ["HIGH", "Formulário: pedido de reembolso"],
  "Cancellation request": ["HIGH", "Formulário: pedido de cancelamento (churn)"],
  "Billing inquiry": ["MEDIUM", "Formulário: dúvida de cobrança"],
};

export function assessRisk(text: string, sentimentScore: number, frustrationDetected: boolean, declaredType?: string): Risk {
  const reasons: string[] = [];
  let level: RiskLevel = "LOW";
  const declared = declaredType ? DECLARED[declaredType] : undefined;
  if (declared) { level = declared[0]; reasons.push(declared[1]); }
  for (const [re, why] of HIGH) if (re.test(text)) { reasons.push(why); level = "HIGH"; }
  if (level !== "HIGH") for (const [re, why] of MEDIUM) if (re.test(text)) { reasons.push(why); level = "MEDIUM"; }
  if (level === "LOW" && declared) level = declared[0];
  if (sentimentScore < 22) { reasons.push("Situação emocional severa (sentimento < 22)"); level = "HIGH"; }
  if (frustrationDetected) { reasons.push("Frustração crescente na conversa"); level = "HIGH"; }
  return { level, reasons, mandatoryHuman: level === "HIGH" };
}

// ---------------------------------------------------------------------------
// Normalização de motivos de escalonamento (taxonomia canônica).
// Vários detectores podem apontar o mesmo motivo (ex.: tipo do formulário "Refund request"
// e o regex "estorno" no texto). Para dashboards, cada ticket conta uma vez por categoria.
// ---------------------------------------------------------------------------
export const ESCALATION_CATEGORIES = [
  [/reembolso|chargeback/i, "Reembolso / chargeback"],
  [/cancelamento|churn/i, "Cancelamento (churn)"],
  [/jurídico|legal|regulat/i, "Jurídico / regulatório"],
  [/fraude|comprometida|segurança/i, "Fraude / conta comprometida"],
  [/perda de dados/i, "Perda de dados"],
  [/lgpd|dados pessoais/i, "Dados pessoais (LGPD)"],
  [/emocional|frustração/i, "Cliente irritado / frustração"],
  [/cobrança/i, "Cobrança"],
  [/garantia|troca/i, "Garantia / troca"],
  [/contrato|estratégica/i, "Conta estratégica"],
] as const;

export const LOW_CONFIDENCE = "Baixa confiança / sem cobertura na KB";
export const GUARDRAIL = "Bloqueado pelo guardrail";

export function canonicalReason(reason: string): string {
  for (const [re, label] of ESCALATION_CATEGORIES) if (re.test(reason)) return label;
  return reason;
}

/** Motivos canônicos (sem duplicatas) pelos quais um ticket HUMANO foi escalado. */
export function escalationCategories(riskLevel: string, reasons: string[], guardrailBlocked: boolean): string[] {
  if (guardrailBlocked) return [GUARDRAIL];
  // Risco médio não escala sozinho: se foi para humano, o motivo real foi confiança baixa.
  if (riskLevel !== "HIGH" || !reasons.length) return [LOW_CONFIDENCE];
  return [...new Set(reasons.map(canonicalReason))];
}
