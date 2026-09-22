/**
 * ===========================================================================
 * criar-legend.gs — Apps Script TEMPORÁRIO de documentação dos dados
 * ===========================================================================
 * 
 * Este script foi usado UMA VEZ para criar a aba 'legend' do Google Sheets,
 * que funciona como dicionário de dados descrevendo cada campo em linguagem
 * acessível para leigos.
 * 
 * Não faz parte do webapp em execução. É evidência do processo de documentação
 * dos dados, gerado com apoio do Google Gemini durante a Fase 1.5 do desafio.
 * 
 * A aba 'legend' foi posteriormente expandida manualmente para incluir também
 * a descrição de todas as colunas calculadas (Bloco 1, Bloco 2 e Bloco 3),
 * com indicação de origem (Dataset ou Calculado) e heurística de cálculo.
 * 
 * ===========================================================================
 */

function criarAbaLegend() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheetLegend = ss.getSheetByName('legend');
  
  // Se a aba já existir, limpa. Se não, cria.
  if (sheetLegend) {
    sheetLegend.clear();
  } else {
    sheetLegend = ss.insertSheet('legend');
  }

  // Tabela com as legendas (Dicionário de Dados) — colunas originais do dataset
  const legendData = [
    ["Nome da Coluna", "Descrição (O que significa)"],
    ["opportunity_id", "O código único de identificação de cada negociação (protocolo)."],
    ["deal_stage", "O status da venda: Ganha (Won), Perdida (Lost), Em andamento (Engaging) ou Prospecção (Prospecting)."],
    ["engage_date", "A data do primeiro contato ou início das tratativas com o cliente."],
    ["close_date", "A data em que o negócio foi finalizado (vencido ou perdido)."],
    ["close_value", "O valor financeiro real (em USD) fechado ao final da negociação."],
    ["sales_agent", "O nome do vendedor ou executivo de contas responsável pelo negócio."],
    ["manager", "O nome do gerente de vendas responsável pela equipe do vendedor."],
    ["regional_office", "A região geográfica ou sede do time de vendas."],
    ["product", "O nome específico do produto sendo negociado."],
    ["series", "A linha, modelo ou categoria de catálogo daquele produto."],
    ["sales_price", "O preço base 'de tabela' daquele produto (em USD)."],
    ["account", "O nome da empresa cliente com quem estamos negociando."],
    ["sector", "O setor de mercado ou indústria da empresa cliente (ex: tecnologia, saúde)."],
    ["year_established", "O ano em que a empresa cliente foi fundada."],
    ["revenue", "O faturamento anual da empresa cliente (em USD), indicando seu porte financeiro."],
    ["employees", "O número de funcionários do cliente, indicando o tamanho da empresa."],
    ["office_location", "O país onde fica a sede principal do cliente."],
    ["subsidiary_of", "Se o cliente pertencer a um grupo corporativo maior, indica o nome da matriz/dona."]
  ];

  // Inserir dados na planilha
  let range = sheetLegend.getRange(1, 1, legendData.length, legendData[0].length);
  range.setValues(legendData);

  // Formatação visual
  sheetLegend.setFrozenRows(1);
  
  let headerRange = sheetLegend.getRange(1, 1, 1, 2);
  headerRange.setFontWeight("bold");
  headerRange.setBackground("#1B3A47"); // Petróleo Garô
  headerRange.setFontColor("#ffffff");
  
  sheetLegend.autoResizeColumn(1);
  sheetLegend.autoResizeColumn(2);

  SpreadsheetApp.getUi().alert("Aba 'legend' (Dicionário de Dados) gerada com sucesso!");
}
