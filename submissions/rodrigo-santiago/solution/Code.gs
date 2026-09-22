/**
 * ===========================================================================
 * Deals Priorizados — Backend
 * Webapp em Apps Script para priorização de deals do pipeline comercial.
 * Desafio G4 AI Master — Lead Scorer.
 * ===========================================================================
 */

const SHEET_NAME = 'main';
const REF_DATE_STR = '2017-12-31';
const GEMINI_MODEL = 'gemini-3.5-flash-lite';
const CACHE_SHEET_NAME = '_cache_gemini';

/**
 * Ponto de entrada do webapp.
 */
function doGet() {
  return HtmlService
    .createHtmlOutputFromFile('Index')
    .setTitle('Deals Priorizados')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

/**
 * Lê todo o pipeline da planilha e devolve para o frontend.
 * Envia apenas as colunas usadas pelo webapp. Datas viram string ISO.
 */
function getPipeline() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  if (!sheet) throw new Error('Aba "' + SHEET_NAME + '" não encontrada.');
  
  const values = sheet.getDataRange().getValues();
  if (values.length < 2) return { headers: [], rows: [] };
  
  const allHeaders = values[0];
  const colunas = [
    'opportunity_id', 'deal_stage', 'engage_date', 'close_date', 'close_value',
    'sales_agent', 'manager', 'regional_office', 'product', 'sales_price',
    'account', 'sector', 'days_since_engage',
    'agent_win_rate_product', 'product_base_win_rate', 'sector_win_rate',
    'account_prior_win_rate', 'is_repeat_customer',
    'agent_avg_cycle', 'product_avg_cycle',
    'probability_score', 'expected_value', 'priority_quadrant'
  ];
  
  const indices = {};
  colunas.forEach(nome => {
    const idx = allHeaders.indexOf(nome);
    if (idx !== -1) indices[nome] = idx;
  });
  
  const headers = Object.keys(indices);
  const rows = values.slice(1).map(row => {
    const obj = {};
    headers.forEach(h => {
      var val = row[indices[h]];
      if (val instanceof Date) {
        val = Utilities.formatDate(val, 'GMT', 'yyyy-MM-dd');
      }
      obj[h] = val;
    });
    return obj;
  });
  
  return { headers: headers, rows: rows };
}

/**
 * Atualiza o stage de um deal (mover no kanban).
 * Se novo stage for Won ou Lost, preenche close_date com 31/12/2017.
 * Se Won, também preenche close_value.
 */
function atualizarDeal(opportunityId, novoStage, closeValue) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  if (!sheet) throw new Error('Aba não encontrada.');
  
  const values = sheet.getDataRange().getValues();
  const headers = values[0];
  
  const idxId = headers.indexOf('opportunity_id');
  const idxStage = headers.indexOf('deal_stage');
  const idxCloseDate = headers.indexOf('close_date');
  const idxCloseValue = headers.indexOf('close_value');
  
  if (idxId === -1) throw new Error('Coluna opportunity_id não encontrada.');
  
  // Busca a linha
  var linhaEncontrada = -1;
  for (var i = 1; i < values.length; i++) {
    if (values[i][idxId] === opportunityId) {
      linhaEncontrada = i + 1; // +1 porque Sheet é 1-indexado
      break;
    }
  }
  
  if (linhaEncontrada === -1) {
    throw new Error('Deal ' + opportunityId + ' não encontrado.');
  }
  
  // Atualiza stage
  sheet.getRange(linhaEncontrada, idxStage + 1).setValue(novoStage);
  
  // Se for Won ou Lost, preenche close_date
  if (novoStage === 'Won' || novoStage === 'Lost') {
    const refDate = new Date(2017, 11, 31);
    if (idxCloseDate !== -1) {
      sheet.getRange(linhaEncontrada, idxCloseDate + 1).setValue(refDate);
    }
    // Se Won, preenche close_value; se Lost, zera
    if (idxCloseValue !== -1) {
      const valor = novoStage === 'Won' ? (Number(closeValue) || 0) : 0;
      sheet.getRange(linhaEncontrada, idxCloseValue + 1).setValue(valor);
    }
  }
  
  return { success: true, opportunityId: opportunityId, novoStage: novoStage };
}

/**
 * Chama o Gemini para explicar um deal específico.
 * Usa cache em aba oculta para não repetir chamadas.
 */
function explicarDeal(dealData) {
  const cacheKey = 'deal_' + dealData.opportunity_id;
  const cached = lerCache(cacheKey);
  if (cached) return { texto: cached, fromCache: true };
  
  const prompt = promptExplicarDeal(dealData);
  const resposta = chamarGemini(prompt);
  
  gravarCache(cacheKey, resposta);
  return { texto: resposta, fromCache: false };
}

/**
 * Chama o Gemini para analisar o pipeline agregado.
 * Sem cache (muda a cada estado do pipeline).
 */
function analisarPipeline(resumo) {
  const prompt = promptAnalisarPipeline(resumo);
  const resposta = chamarGemini(prompt);
  return { texto: resposta };
}

/**
 * Chamada base ao Gemini.
 */
function chamarGemini(prompt) {
  const apiKey = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY');
  if (!apiKey) throw new Error('Chave GEMINI_API_KEY não configurada em Script Properties.');
  
  const url = 'https://generativelanguage.googleapis.com/v1beta/models/' + GEMINI_MODEL + ':generateContent?key=' + apiKey;
  const payload = {
    contents: [{ parts: [{ text: prompt }] }],
    generationConfig: {
      temperature: 0.4,
      maxOutputTokens: 250,
      topP: 0.8
    }
  };
  
  const response = UrlFetchApp.fetch(url, {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  });
  
  const status = response.getResponseCode();
  const body = response.getContentText();
  
  if (status !== 200) {
    throw new Error('Gemini retornou status ' + status + ': ' + body);
  }
  
  const parsed = JSON.parse(body);
  return parsed.candidates[0].content.parts[0].text;
}

/**
 * Cache simples em aba oculta.
 */
function lerCache(key) {
  const sheet = obterCacheSheet();
  const values = sheet.getDataRange().getValues();
  for (var i = 1; i < values.length; i++) {
    if (values[i][0] === key) return values[i][1];
  }
  return null;
}

function gravarCache(key, valor) {
  const sheet = obterCacheSheet();
  sheet.appendRow([key, valor, new Date()]);
}

function obterCacheSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(CACHE_SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(CACHE_SHEET_NAME);
    sheet.appendRow(['key', 'valor', 'timestamp']);
    sheet.hideSheet();
  }
  return sheet;
}

/**
 * Teste de sanidade para rodar no editor.
 */
function testarLeitura() {
  const data = getPipeline();
  Logger.log('Linhas: ' + data.rows.length + ' | Colunas: ' + data.headers.length);
  Logger.log('Amostra: ' + JSON.stringify(data.rows[0]));
}

function analisarPrioridades() {
  const data = getPipeline();
  const abertos = data.rows.filter(function(d){
    return d.deal_stage === 'Prospecting' || d.deal_stage === 'Engaging';
  });
  
  var quadA = 0, quadB = 0, quadC = 0, quadD = 0, semQuad = 0;
  var scoreAlto = 0, scoreMedio = 0, scoreBaixo = 0;
  
  abertos.forEach(function(d){
    var q = String(d.priority_quadrant || '').charAt(0);
    if(q === 'A') quadA++;
    else if(q === 'B') quadB++;
    else if(q === 'C') quadC++;
    else if(q === 'D') quadD++;
    else semQuad++;
    
    var s = Number(d.probability_score) || 0;
    if(s >= 70) scoreAlto++;
    else if(s >= 40) scoreMedio++;
    else scoreBaixo++;
  });
  
  Logger.log('Total de deals abertos: ' + abertos.length);
  Logger.log('--- Por quadrante ---');
  Logger.log('A (Foco Máximo): ' + quadA + ' (' + Math.round(quadA/abertos.length*100) + '%)');
  Logger.log('B (Quick Win): ' + quadB + ' (' + Math.round(quadB/abertos.length*100) + '%)');
  Logger.log('C (Estratégico): ' + quadC + ' (' + Math.round(quadC/abertos.length*100) + '%)');
  Logger.log('D (Baixa): ' + quadD + ' (' + Math.round(quadD/abertos.length*100) + '%)');
  Logger.log('Sem quadrante: ' + semQuad);
  Logger.log('--- Por score ---');
  Logger.log('Alto (>=70): ' + scoreAlto + ' (' + Math.round(scoreAlto/abertos.length*100) + '%)');
  Logger.log('Médio (40-69): ' + scoreMedio + ' (' + Math.round(scoreMedio/abertos.length*100) + '%)');
  Logger.log('Baixo (<40): ' + scoreBaixo + ' (' + Math.round(scoreBaixo/abertos.length*100) + '%)');
}
