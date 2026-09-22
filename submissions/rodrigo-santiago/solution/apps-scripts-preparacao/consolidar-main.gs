/**
 * ===========================================================================
 * consolidar-main.gs — Apps Script TEMPORÁRIO de preparação dos dados
 * ===========================================================================
 * 
 * Este script foi usado UMA VEZ para consolidar os 4 CSVs originais 
 * (accounts, products, sales_pipeline, sales_teams) em uma aba única 'main'
 * do Google Sheets, aplicando todas as correções e padronizações.
 * 
 * Não faz parte do webapp em execução. É evidência do processo de preparação
 * dos dados, gerado com apoio do Google Gemini durante a Fase 1 do desafio.
 * 
 * Correções aplicadas:
 * - "technolgy" → "technology" no campo sector
 * - Unificação de "GTXPro" e "GTX Pro" (remove espaços e case)
 * - Conversão forçada de números com problema de locale brasileiro
 * - Padronização de vazios: "-" para texto, vazio para número e data
 * - Formatação de colunas monetárias como USD
 * 
 * ===========================================================================
 */

function criarBaseMain() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  const sheetPipeline = ss.getSheetByName('sales_pipeline');
  const sheetAccounts = ss.getSheetByName('accounts');
  const sheetProducts = ss.getSheetByName('products');
  const sheetTeams = ss.getSheetByName('sales_teams');
  
  if (!sheetPipeline || !sheetAccounts || !sheetProducts || !sheetTeams) {
    SpreadsheetApp.getUi().alert("Erro: Verifique se as 4 abas originais estão com os nomes corretos.");
    return;
  }

  const dataAccounts = sheetAccounts.getDataRange().getValues();
  const dataProducts = sheetProducts.getDataRange().getValues();
  const dataTeams = sheetTeams.getDataRange().getValues();
  const dataPipeline = sheetPipeline.getDataRange().getValues();

  // --- FUNÇÕES DE PADRONIZAÇÃO ---
  // 1. Textos: Se vazio, vira "-"
  function formatText(val) {
    if (val === "" || val == null || String(val).trim() === "") return "-";
    return String(val).trim();
  }

  // 2. Números: Converte formato e mantém vazio se não houver dados
  function formatNumber(val) {
    if (val === "" || val == null || String(val).trim() === "") return "";
    let num = parseFloat(String(val).replace(',', '.'));
    return isNaN(num) ? "" : num;
  }

  // 3. Datas: Mantém vazio
  function formatDate(val) {
    if (val === "" || val == null || String(val).trim() === "") return "";
    return val;
  }

  const mapAccounts = {};
  for (let i = 1; i < dataAccounts.length; i++) {
    let row = dataAccounts[i];
    let accountName = formatText(row[0]);
    
    let sector = formatText(row[1]);
    if (sector === "technolgy") sector = "technology";
    
    mapAccounts[accountName] = {
      sector: sector,
      year_established: formatNumber(row[2]),
      revenue: formatNumber(row[3]),
      employees: formatNumber(row[4]),
      office_location: formatText(row[5]),
      subsidiary_of: formatText(row[6])
    };
  }

  const mapProducts = {};
  for (let i = 1; i < dataProducts.length; i++) {
    let row = dataProducts[i];
    // Unifica GTXPro e GTX Pro: remove espaços e lowercase
    let productNameClean = String(row[0]).replace(/\s+/g, '').toLowerCase(); 
    mapProducts[productNameClean] = {
      series: formatText(row[1]),
      sales_price: formatNumber(row[2])
    };
  }

  const mapTeams = {};
  for (let i = 1; i < dataTeams.length; i++) {
    let row = dataTeams[i];
    let agentName = formatText(row[0]);
    mapTeams[agentName] = {
      manager: formatText(row[1]),
      regional_office: formatText(row[2])
    };
  }

  const newData = [];
  
  const header = [
    "opportunity_id", "deal_stage", "engage_date", "close_date", "close_value", 
    "sales_agent", "manager", "regional_office",                                
    "product", "series", "sales_price",                                         
    "account", "sector", "year_established", "revenue", "employees", "office_location", "subsidiary_of" 
  ];
  newData.push(header);

  for (let i = 1; i < dataPipeline.length; i++) {
    let row = dataPipeline[i];
    
    let opp_id = formatText(row[0]);
    let agent = formatText(row[1]);
    let productOriginal = formatText(row[2]);
    let productClean = productOriginal !== "-" ? productOriginal.replace(/\s+/g, '').toLowerCase() : "";
    let account = formatText(row[3]);
    let stage = formatText(row[4]);
    let engage_date = formatDate(row[5]);
    let close_date = formatDate(row[6]);
    let close_value = formatNumber(row[7]);

    let teamData = mapTeams[agent] || {manager: "-", regional_office: "-"};
    let prodData = mapProducts[productClean] || {series: "-", sales_price: ""};
    let accData = mapAccounts[account] || {sector: "-", year_established: "", revenue: "", employees: "", office_location: "-", subsidiary_of: "-"};

    newData.push([
      opp_id, stage, engage_date, close_date, close_value,
      agent, teamData.manager, teamData.regional_office,
      productOriginal, prodData.series, prodData.sales_price,
      account, accData.sector, accData.year_established, accData.revenue, accData.employees, accData.office_location, accData.subsidiary_of
    ]);
  }

  let sheetMain = ss.getSheetByName('main');
  if (sheetMain) {
    sheetMain.clear();
  } else {
    sheetMain = ss.insertSheet('main');
  }

  let range = sheetMain.getRange(1, 1, newData.length, newData[0].length);
  range.setValues(newData);

  sheetMain.setFrozenRows(1);
  sheetMain.getRange(1, 1, 1, newData[0].length).setFontWeight("bold");

  // Formata colunas monetárias como USD
  sheetMain.getRange(2, 5, sheetMain.getLastRow() - 1, 1).setNumberFormat('[$$-409]#,##0.00'); // close_value
  sheetMain.getRange(2, 11, sheetMain.getLastRow() - 1, 1).setNumberFormat('[$$-409]#,##0.00'); // sales_price
  sheetMain.getRange(2, 15, sheetMain.getLastRow() - 1, 1).setNumberFormat('[$$-409]#,##0.00'); // revenue

  SpreadsheetApp.getUi().alert("Base 'main' consolidada com sucesso! As regras de campos vazios foram aplicadas.");
}
