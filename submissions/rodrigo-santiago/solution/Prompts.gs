/**
 * ===========================================================================
 * Deals Priorizados — Prompts do Gemini
 * Prompts consultivos estilo executivo.
 * Edite aqui para ajustar tom, estrutura ou profundidade das análises.
 * ===========================================================================
 */

/**
 * Explicação de um deal específico.
 * Chamado quando o vendedor clica em "Explicar este deal" no modal.
 */
function promptExplicarDeal(d) {
  const conta = d.account || 'sem nome';
  const produto = d.product || 'sem produto';
  const stage = d.deal_stage || '—';
  const vendedor = d.sales_agent || '—';
  const score = d.probability_score || 0;
  const quadrante = d.priority_quadrant || '—';
  const expectedValue = d.expected_value || 0;
  const dias = d.days_since_engage || 0;
  const winRateAgentProduto = pct(d.agent_win_rate_product);
  const winRateProduto = pct(d.product_base_win_rate);
  const winRateSetor = pct(d.sector_win_rate);
  const recorrente = d.is_repeat_customer === 'sim' ? 'sim' : 'não';
  const cicloProduto = d.product_avg_cycle ? Math.round(d.product_avg_cycle) : '—';
  
  return [
    'Você é consultor sênior de RevOps. Tom executivo, direto, sem enrolação.',
    '',
    'DEAL: ' + conta + ' | ' + produto + ' | ' + stage + ' | vendedor: ' + vendedor,
    'Score: ' + score + '/100 | Quadrante: ' + quadrante + ' | Valor esperado: USD ' + expectedValue,
    'Dias em aberto: ' + dias + ' | Ciclo médio produto: ' + cicloProduto + ' dias',
    'Win rate agente×produto: ' + winRateAgentProduto + ' | produto: ' + winRateProduto + ' | setor: ' + winRateSetor,
    'Cliente recorrente: ' + recorrente,
    '',
    'ENTREGUE EXATAMENTE 3 FRASES CURTAS, prosa direta:',
    '1. Por que o score é este (1 frase, ancorado nos números).',
    '2. Status do ciclo: no prazo, atrasado ou estourado, comparando dias com ciclo do produto (1 frase).',
    '3. Próxima ação tática concreta (1 frase, verbo no imperativo).',
    '',
    'Máximo 80 palavras no total. Sem bullets, sem títulos, sem saudação. Só as 3 frases numeradas.'
  ].join('\n');
}

/**
 * Análise agregada do pipeline filtrado.
 * Chamado quando o vendedor/manager clica em "Analisar meu pipeline" no painel.
 */
function promptAnalisarPipeline(r) {
  return [
    'Você é consultor sênior de RevOps. Tom executivo, direto, sem enrolação.',
    '',
    'PIPELINE (deals em aberto, filtro aplicado):',
    'Total: ' + (r.totalAbertos || 0) + ' deals | Valor esperado: USD ' + (r.valorEsperadoTotal || 0) + ' | Ticket médio: USD ' + (r.ticketMedio || 0),
    'Quadrantes: A=' + (r.quadranteA || 0) + ' | B=' + (r.quadranteB || 0) + ' | C=' + (r.quadranteC || 0) + ' | D=' + (r.quadranteD || 0),
    'Estágios: Prospecting=' + (r.prospecting || 0) + ' | Engaging=' + (r.engaging || 0),
    '',
    'TOP DEALS DO QUADRANTE A:',
    formatarTopDeals(r.topA || []),
    '',
    'DEALS MAIS ANTIGOS:',
    formatarTopDeals(r.topEstagnados || []),
    '',
    'ENTREGUE EXATAMENTE 3 FRASES CURTAS, prosa direta:',
    '1. Diagnóstico do pipeline em uma frase (formato saudável ou desequilibrado, e por quê).',
    '2. Onde focar esta semana, citando 1 ou 2 contas específicas do quadrante A por nome.',
    '3. Um alerta concreto (deal estagnado por nome, ou risco de concentração).',
    '',
    'Máximo 100 palavras no total. Sem bullets, sem títulos, sem saudação. Só as 3 frases numeradas.'
  ].join('\n');
}

/**
 * Auxiliares de formatação para os prompts.
 */
function pct(v) {
  if (v == null || v === '' || isNaN(v)) return '—';
  return Math.round(Number(v) * 100) + '%';
}

function formatarTopDeals(lista) {
  if (!lista || lista.length === 0) return '- (nenhum)';
  return lista.map(function(d) {
    return '- ' + (d.account || 'sem conta') + 
           ' | ' + (d.product || 'sem produto') + 
           ' | valor esperado USD ' + (d.expected_value || 0) + 
           ' | score ' + (d.probability_score || 0) + 
           ' | ' + (d.days_since_engage || 0) + ' dias em aberto';
  }).join('\n');
}
