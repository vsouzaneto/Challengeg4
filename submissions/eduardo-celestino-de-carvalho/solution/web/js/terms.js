/* Vocabulário e cores do Lead Kanban: fonte única para todas as telas.
   As cores das colunas passaram no validador de paleta (CVD e normal-vision);
   o âmbar tem contraste < 3:1, por isso todo gráfico tem legenda, rótulos e tabela. */

export const LANE = {
  negociar: { title: "Negociar", color: "#2E6DA4", pitch: "Chance real de fechar agora. Comece por aqui." },
  qualificar: { title: "Qualificar", color: "#C99436", pitch: "Ainda em prospecção: confirmar se vale negociar." },
  encerrar: { title: "Confirmar ou encerrar", color: "#B5452F", pitch: "Parados há mais tempo do que qualquer venda já levou." },
};
export const LANE_ORDER = ["negociar", "qualificar", "encerrar"];

/* Etapas do CRM em linguagem simples (o nome técnico aparece só como apoio). */
export const STAGE = { Engaging: "Negociação", Prospecting: "Prospecção" };

export const PHASE = {
  "Início": { tag: "tag-amber", hint: "Até 14 dias em negociação. É quando a maioria das perdas acontece." },
  "Em andamento": { tag: "tag-blue", hint: "De 15 a 89 dias em negociação. Já passou da fase de maior risco." },
  "Perto do limite": { tag: "tag-brick", hint: "De 90 dias até o prazo máximo. Nesta fase os negócios costumam travar." },
  "Prazo excedido": { tag: "tag-dark", hint: "Em negociação há mais tempo do que qualquer venda já levou para fechar." },
  "Sem data": { tag: "tag-slate", hint: "Em prospecção: o CRM não registra quando começou." },
};
export const NEGOTIATION_PHASES = ["Início", "Em andamento", "Perto do limite"];

/* Definições curtas usadas nos ícones ⓘ. */
export const GLOSSARY = {
  valorPotencial: "Preço de tabela do produto. Mostra o tamanho do negócio; não é o valor fechado nem uma previsão.",
  prazoMaximo: (days) => `O maior tempo que uma venda já levou para fechar, contado desde o início da negociação: ${days} dias.`,
  saude: "Do valor que está em negociação, quanto ainda está dentro do prazo máximo. Quanto maior, mais realista é o pipeline.",
  negociar: (days) => `Negócios em negociação há até ${days} dias. Ordem: maior valor primeiro; no empate, o mais recente.`,
  qualificar: "Oportunidades em prospecção, sem negociação iniciada. Ordem: maior valor primeiro.",
  encerrar: (days) => `Negócios em negociação há mais de ${days} dias. No histórico, nenhuma venda fechou depois disso.`,
  taxaGanho: "Das vendas já concluídas, a parte que foi ganha.",
  contaPendente: "A oportunidade não tem empresa cadastrada no CRM. Cadastrar é uma tarefa extra; não muda a ordem.",
};

export const SECTORS = {
  technology: "Tecnologia", medical: "Saúde", retail: "Varejo", software: "Software",
  finance: "Finanças", marketing: "Marketing", entertainment: "Entretenimento",
  telecommunications: "Telecom", services: "Serviços", employment: "Recrutamento",
};

export const GROUPS = {
  region: { label: "Regional", plural: "regionais", key: (i) => i.region },
  manager: { label: "Manager", plural: "managers", key: (i) => i.manager },
  agent: { label: "Vendedor", plural: "vendedores", key: (i) => i.agent },
};

/* Ícone ⓘ acessível: o texto aparece no tooltip global (hover, foco ou toque). */
export function info(text) {
  const safe = String(text).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
  return `<button type="button" class="info" data-info="${safe}" aria-label="${safe}">i</button>`;
}
