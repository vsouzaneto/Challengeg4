// Guardrails de entrada e saída. Princípio do PRD: "Disclaimer não substitui guardrail".

export type GuardrailFlag = { kind: string; severity: "block" | "warn" | "info"; detail: string };
export type InputCheck = { allowed: boolean; sanitized: string; flags: GuardrailFlag[] };

const INJECTION: [RegExp, string][] = [
  [/ignore (all |any )?(the )?(previous|prior|above) (instructions|prompts?|rules)/i, "override de instruções"],
  [/ignor(e|a|ar) (todas )?(as )?(instruç(õ|o)es|regras) (anteriores|acima)/i, "override de instruções (PT)"],
  [/(reveal|show|print|repeat|leak).{0,30}(system prompt|internal prompt|instructions|hidden prompt)/i, "exfiltração de system prompt"],
  [/(mostre|revele|imprima|repita).{0,30}(prompt|instruç(õ|o)es)( do sistema| internas)?/i, "exfiltração de system prompt (PT)"],
  [/you are now|act as (an? )?(unrestricted|jailbroken|dan)|developer mode|\bDAN\b|jailbreak/i, "jailbreak / troca de persona"],
  [/(agora você é|finja que (você )?é|modo desenvolvedor)/i, "jailbreak / troca de persona (PT)"],
  [/<\s*script|javascript:|onerror\s*=|\{\{.*\}\}|\$\{.*\}/i, "payload de código"],
  [/(drop|delete|truncate)\s+table|union\s+select|;\s*--/i, "payload SQL"],
  [/(approve|issue|process|aprove|faça|faca|libere).{0,20}(refund|reembolso|estorno).{0,40}(without|sem).{0,20}(approval|aprovação|aprovacao|checking|verificar)/i, "tentativa de ação não autorizada"],
];

const OUT_OF_SCOPE: [RegExp, string][] = [
  [/(other|another) (customer|user)'?s? (data|email|address|phone|password)/i, "dados de terceiros"],
  [/(dados|email|endereço|telefone|senha) de (outro|outra) (cliente|usuário|usuario|pessoa)/i, "dados de terceiros"],
  [/(write|escreva).{0,20}(poem|poema|code|código|essay|redação)/i, "fora do escopo de suporte"],
];

// Mascaramento de PII antes de qualquer LLM/log.
const PII: [RegExp, string, string][] = [
  [/\b(?:\d[ -]?){13,19}\b/g, "[CARTÃO]", "número de cartão"],
  [/\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b/g, "[CPF]", "CPF"],
  [/[\w.+-]+@[\w-]+\.[\w.]+/g, "[EMAIL]", "e-mail"],
  [/(\+?55\s?)?\(?\d{2}\)?\s?9?\d{4}-?\d{4}\b/g, "[TELEFONE]", "telefone"],
  [/\b(password|senha)\s*[:=]\s*\S+/gi, "$1: [REDACTED]", "senha em texto"],
];

export function checkInput(text: string): InputCheck {
  const flags: GuardrailFlag[] = [];
  if (text.length > 4000) flags.push({ kind: "length", severity: "warn", detail: "mensagem truncada em 4000 caracteres" });
  let sanitized = text.slice(0, 4000);
  for (const [re, detail] of INJECTION) if (re.test(sanitized)) flags.push({ kind: "prompt_injection", severity: "block", detail });
  for (const [re, detail] of OUT_OF_SCOPE) if (re.test(sanitized)) flags.push({ kind: "out_of_scope", severity: "block", detail });
  for (const [re, repl, detail] of PII) {
    if (sanitized.match(re)) {
      sanitized = sanitized.replace(re, repl);
      flags.push({ kind: "pii_masked", severity: "info", detail });
    }
  }
  return { allowed: !flags.some((f) => f.severity === "block"), sanitized, flags };
}

// ---------------------------------------------------------------------------
// Output
// ---------------------------------------------------------------------------
const UNAUTHORIZED_COMMITMENTS: [RegExp, string][] = [
  [/(your|o seu|seu) (refund|reembolso|estorno) (has been|was|foi) (approved|processed|aprovado|processado)/i, "promessa de reembolso"],
  [/(i|we) (have )?(approved|processed|cancelled|canceled) (your|the)/i, "ação financeira/contratual executada"],
  [/(aprovei|processei|cancelei|estornei)/i, "ação financeira/contratual executada (PT)"],
  [/(guarantee|garantimos|garanto|100% (certo|sure))/i, "garantia absoluta"],
  [/(r\$|us\$|\$)\s?\d+/i, "valor monetário não verificado"],
];

const SENSITIVE_TOPICS = /(refund|reembolso|estorno|charge|cobran|payment|pagamento|invoice|fatura|cancel|legal|lawyer|advogado|procon|dados pessoais|lgpd)/i;

export const DISCLAIMER_PT =
  "ℹ️ Resposta gerada por assistente de IA com base na nossa base de conhecimento. Decisões financeiras ou contratuais são sempre confirmadas por um especialista.";
export const DISCLAIMER_EN =
  "ℹ️ AI-generated answer based on our knowledge base. Financial or contractual decisions are always confirmed by a specialist.";

export type OutputCheck = { ok: boolean; text: string; flags: GuardrailFlag[]; groundedness: number };

/**
 * Valida a resposta antes de chegar ao cliente:
 * - groundedness: % dos termos de conteúdo da resposta que existem no artigo-fonte;
 * - compromissos não autorizados; PII; disclaimer em temas sensíveis.
 */
export function checkOutput(reply: string, source: string, lang: "pt" | "en", context: string): OutputCheck {
  const flags: GuardrailFlag[] = [];
  for (const [re, detail] of UNAUTHORIZED_COMMITMENTS) if (re.test(reply)) flags.push({ kind: "unauthorized_claim", severity: "block", detail });
  for (const [re, , detail] of PII) if (reply.match(re) && !source.match(re)) flags.push({ kind: "pii_leak", severity: "block", detail });

  const content = (s: string) => new Set((s.toLowerCase().match(/[\p{L}]{5,}/gu) ?? []));
  const r = content(reply), s = content(source);
  const supported = [...r].filter((w) => s.has(w)).length;
  const groundedness = r.size ? supported / r.size : 1;
  if (groundedness < 0.35) flags.push({ kind: "low_groundedness", severity: "block", detail: `apenas ${(groundedness * 100).toFixed(0)}% dos termos suportados pela KB` });

  let text = reply.trim();
  if (SENSITIVE_TOPICS.test(context + " " + reply)) {
    text += `\n\n${lang === "pt" ? DISCLAIMER_PT : DISCLAIMER_EN}`;
    flags.push({ kind: "disclaimer_added", severity: "info", detail: "tema sensível" });
  }
  return { ok: !flags.some((f) => f.severity === "block"), text, flags, groundedness };
}

export const SAFE_FALLBACK_PT =
  "Não encontrei informação suficiente para responder isso com segurança. Vou encaminhar para um especialista do nosso time, que vai continuar daqui — você não vai precisar repetir nada.";
export const SAFE_FALLBACK_EN =
  "I couldn't find enough information to answer this safely. I'm handing this over to a specialist on our team, who will continue from here — you won't need to repeat anything.";
