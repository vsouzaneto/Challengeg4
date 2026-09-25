// Política do chat de atendimento: o que a IA faz sozinha (🤖), o que sugere para o atendente aprovar (🤝) e o que passa
// direto para uma pessoa (🧑). É a mesma política da seção 5 e do fluxo da revisão, aplicada a uma conversa.
// Função pura, sem tela nem rede: tests/chat.mjs testa os cenários em Node.

// Regras de risco, avaliadas no texto original (português) e na tradução (inglês). Um alarme falso só manda o ticket
// para uma pessoa, então as listas preferem pegar demais a pegar de menos.
export const RISK_RULES = [
  { id: 'financeiro', motivo: 'pedido financeiro (reembolso, cancelamento ou cobrança)',
    re: /\b(reembols\w*|estorn\w*|cancel\w*|cobran[çc]\w*|cobrad\w*|fatura\w*|pagament\w*|refund\w*|chargeback|billing|invoice\w*|charged)\b/i },
  { id: 'perda_dados', motivo: 'possível perda de dados',
    re: /\b(perdi|apaguei|apagad[oa]s?|perda de dados|sumiram|deletei|data loss|deleted|lost (?:all |my )?(?:data|files))\b/i },
  { id: 'invasao', motivo: 'suspeita de invasão ou roubo',
    re: /\b(hackead\w*|invadi\w*|invas[aã]o|roubad\w*|fraude|golpe|hacked|stolen|breach|phishing)\b/i },
  { id: 'emocao_juridico', motivo: 'insatisfação forte ou menção jurídica',
    re: /\b(advogad\w*|processar|procon|reclame aqui|absurdo|frustrad\w*|irritad\w*|inaceit[aá]vel|lawyers?|attorney|lawsuit|sue|frustrated|angry|unacceptable)\b/i },
  { id: 'sensivel', motivo: 'tema sensível (saúde, remuneração ou desligamento)',
    re: /\b(licen[çc]a[- ]maternidade|maternidade|paternidade|atestado|sal[aá]rio|demiss[aã]o|desligament\w*|doen[çc]a|acidente|luto|falecimento)\b/i },
];

export const QUEUE_PT = {
  Access: 'Acessos e contas',
  'Administrative rights': 'Software (Outlook, Windows)',
  'HR Support': 'Pessoas (RH)',
  Hardware: 'Equipamentos',
  'Internal Project': 'Projetos internos',
  Miscellaneous: 'Aprovações e diversos',
  Purchase: 'Compras',
  Storage: 'Pastas e armazenamento',
};

const pct = (v) => `${Math.round(100 * v)}%`;

// Palavras de conteúdo: sem stopwords, saudações e números (mesmo critério da regra de cobertura do modelo)
export function contentWords(model, text) {
  return model.tokenize(text).filter((t) => !model.generic.has(t) && !model.stopwords.has(t) && !/^\d+$/.test(t));
}

// Precisa traduzir antes de classificar? Só quando o modelo reconhece pouco do texto (outro idioma).
export function needsTranslation(model, text) {
  const words = contentWords(model, text);
  if (words.length < 2) return false;
  return words.filter((t) => model.index.has(t)).length / words.length < 0.8;
}

/**
 * Decide a faixa de um ticket.
 * @param model     TriageModel (js/model.js)
 * @param original  texto do cliente como veio (pode ser português)
 * @param english   tradução para inglês, ou null se não houve
 * @returns {lane: 'auto'|'assistido'|'humano'|'detalhes', motivo, riscos, r, vago}
 */
export function decide(model, original, english = null) {
  const text = english ?? original;
  const r = model.predict(text);
  const riscos = RISK_RULES.filter((rule) => rule.re.test(original) || (english && rule.re.test(english)));
  if (r.flags.sensitive && !riscos.some((x) => x.id === 'sensivel')) riscos.push(RISK_RULES.find((x) => x.id === 'sensivel'));
  const words = contentWords(model, text);
  const vago = words.length < 3;
  let lane;
  let motivo;
  if (riscos.length) {
    lane = 'humano';
    motivo = `Regra de risco: ${riscos.map((x) => x.motivo).join('; ')}.`;
  } else if (vago) {
    lane = 'detalhes';
    motivo = `O texto não diz qual é o problema: ${words.length} palavra(s) de conteúdo.`;
  } else if (r.flags.ood) {
    lane = 'humano';
    motivo = `O modelo conhece só ${pct(r.flags.coverage)} das palavras de conteúdo${english ? ' mesmo depois da tradução' : ' (outro idioma, sem tradução disponível)'}: a confiança não vale aqui.`;
  } else if (r.conf >= model.tauAuto) {
    lane = 'auto';
    motivo = `Confiança ${pct(r.conf)} ≥ ${pct(model.tauAuto)}: acima do limiar em que o modelo acertou ≥ 97% no teste.`;
  } else if (r.conf >= model.tauAssist) {
    lane = 'assistido';
    motivo = `Confiança ${pct(r.conf)}, entre ${pct(model.tauAssist)} e ${pct(model.tauAuto)}: o atendente escolhe entre as 2 primeiras filas.`;
  } else {
    lane = 'humano';
    motivo = `Confiança ${pct(r.conf)}, abaixo de ${pct(model.tauAssist)}: nem as 2 primeiras filas são confiáveis.`;
  }
  return { lane, motivo, riscos, r, vago };
}
