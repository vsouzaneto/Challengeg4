// Inferência do classificador de triagem no navegador.
// Espelho do pipeline Python (TfidfVectorizer + LogisticRegression do sklearn): mesmos tokens, mesmo tf-idf, mesma
// softmax. A equivalência é verificada por tests/parity.mjs contra probabilidades geradas pelo sklearn.

const LANES = {
  auto: { nome: 'Roteamento automático', acao: 'Vai direto para a fila, sem triagem humana.' },
  assistido: { nome: 'Assistido', acao: 'O atendente confirma entre as 2 sugestões com um clique.' },
  humano: { nome: 'Triagem humana', acao: 'Um atendente lê e decide do zero.' },
  detalhes: { nome: 'Pedir detalhes', acao: 'Resposta automática pedindo o que falta antes de qualquer triagem.' },
};

export class TriageModel {
  constructor(m) {
    this.classes = m.classes;
    this.queueInfo = m.queue_info;
    this.index = new Map(m.vocab.map((t, i) => [t, i]));
    this.vocab = m.vocab;
    this.idf = m.idf;
    this.coef = m.coef;
    this.intercept = m.intercept;
    this.tokenRe = new RegExp(m.tokenizer.pattern, 'gu');
    this.generic = new Set(m.policy.generic_words);
    this.stopwords = new Set(m.policy.stopwords);
    this.minContent = m.policy.min_content_words;
    this.minCoverage = m.policy.min_coverage;
    this.minCoverageTokens = m.policy.min_coverage_tokens;
    this.rx = {
      thread: new RegExp(m.policy.thread, 'g'),
      sensitive: new RegExp(m.policy.sensitive),
      urgent: new RegExp(m.policy.urgent),
      selfService: new RegExp(m.policy.self_service),
    };
    this.tauAuto = m.limiar_auto;
    this.tauAssist = m.limiar_assistido;
  }

  tokenize(text) {
    return text.toLowerCase().match(this.tokenRe) || [];
  }

  // tf sublinear (1 + ln tf) × idf, normalizado em L2 — como o sklearn.
  vectorize(tokens) {
    const counts = new Map();
    for (const t of tokens) {
      const j = this.index.get(t);
      if (j !== undefined) counts.set(j, (counts.get(j) || 0) + 1);
    }
    const x = new Map();
    let norm = 0;
    for (const [j, c] of counts) {
      const v = (1 + Math.log(c)) * this.idf[j];
      x.set(j, v);
      norm += v * v;
    }
    norm = Math.sqrt(norm) || 1;
    for (const [j, v] of x) x.set(j, v / norm);
    return x;
  }

  probabilities(x) {
    const logits = this.intercept.map((b, k) => {
      let z = b;
      for (const [j, v] of x) z += v * this.coef[k][j];
      return z;
    });
    const max = Math.max(...logits);
    const exp = logits.map((z) => Math.exp(z - max));
    const sum = exp.reduce((a, b) => a + b, 0);
    return exp.map((e) => e / sum);
  }

  // Explicação contrastiva: quais palavras empurraram para a 1ª fila em vez da 2ª.
  explain(x, top, second, n = 6) {
    const terms = [];
    for (const [j, v] of x) {
      const w = v * (this.coef[top][j] - this.coef[second][j]);
      terms.push({ termo: this.vocab[j], peso: w });
    }
    terms.sort((a, b) => b.peso - a.peso);
    return {
      favor: terms.filter((t) => t.peso > 0).slice(0, n),
      contra: terms.filter((t) => t.peso < 0).slice(-3).reverse(),
    };
  }

  flags(text, tokens) {
    const lower = text.toLowerCase();
    const content = tokens.filter((t) => !this.generic.has(t) && !/^\d+$/.test(t)).length;
    // Cobertura: das palavras de conteúdo (sem stopwords), quantas o modelo conhece. Baixa = outro idioma ou assunto novo.
    const covTokens = tokens.filter((t) => !this.generic.has(t) && !this.stopwords.has(t) && !/^\d+$/.test(t));
    const coverage = covTokens.length ? covTokens.filter((t) => this.index.has(t)).length / covTokens.length : 1;
    return {
      sensitive: this.rx.sensitive.test(lower),
      urgent: this.rx.urgent.test(lower),
      selfService: this.rx.selfService.test(lower),
      messages: 1 + (lower.match(this.rx.thread) || []).length,
      infoPoor: content < this.minContent,
      contentWords: content,
      coverage,
      ood: covTokens.length >= this.minCoverageTokens && coverage < this.minCoverage,
    };
  }

  lane(conf, flags, tauAuto = this.tauAuto, tauAssist = this.tauAssist) {
    if (flags.infoPoor) return { id: 'detalhes', motivo: 'O texto não diz qual é o problema: faltam palavras de conteúdo.' };
    if (flags.ood) return { id: 'humano', motivo: `O modelo conhece só ${pct(flags.coverage)} das palavras de conteúdo (outro idioma ou assunto fora do treino): aqui a confiança não vale nada.` };
    if (flags.sensitive) return { id: 'humano', motivo: 'Tema sensível (saúde, remuneração ou desligamento): sempre com uma pessoa.' };
    if (conf >= tauAuto) return { id: 'auto', motivo: `Confiança ${pct(conf)} ≥ limiar automático de ${pct(tauAuto)}.` };
    if (conf >= tauAssist) return { id: 'assistido', motivo: `Confiança ${pct(conf)}: acima de ${pct(tauAssist)}, as 2 primeiras sugestões acertam ≥ 90% das vezes.` };
    return { id: 'humano', motivo: `Confiança ${pct(conf)} abaixo de ${pct(tauAssist)}: nem as 2 primeiras sugestões são confiáveis.` };
  }

  predict(text) {
    const tokens = this.tokenize(text);
    const x = this.vectorize(tokens);
    const proba = this.probabilities(x);
    const order = proba.map((p, k) => k).sort((a, b) => proba[b] - proba[a]);
    const known = tokens.filter((t) => this.index.has(t)).length;
    const flags = this.flags(text, tokens);
    const conf = proba[order[0]];
    const lane = this.lane(conf, flags);
    return {
      proba, order, conf, flags, lane: { ...lane, ...LANES[lane.id] },
      top: this.classes[order[0]], second: this.classes[order[1]],
      explicacao: this.explain(x, order[0], order[1]),
      cobertura: { tokens: tokens.length, conhecidos: known },
    };
  }
}

export const pct = (v, d = 0) => `${(100 * v).toFixed(d).replace('.', ',')}%`;
export { LANES };
