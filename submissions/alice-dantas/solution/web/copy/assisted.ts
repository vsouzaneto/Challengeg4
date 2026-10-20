/**
 * Textos da priorização assistida (ADR-010), montados a partir dos códigos de `lib/assisted`.
 *
 * É uma camada declarada pelo vendedor, separada do scoring: aqui nada afirma probabilidade, previsão de fechamento
 * nem "melhor oportunidade". `tests/copy.test.ts` varre este catálogo com o mesmo vocabulário do resto da tela.
 */
import {
  DIMENSIONS, WEIGHTS, WINDOW_DAYS, type AnswerOf, type CategoryCode, type ConflictCode, type Dimension, type Note,
} from "@/lib/assisted/model";
import type { Evaluation, Ranked } from "@/lib/assisted/policy";
import type { Item } from "@/lib/contract";
import { formatDate } from "@/lib/format";

import { clientText } from "./pt-BR";

const TOTAL = DIMENSIONS.reduce((sum, d) => sum + WEIGHTS[d], 0);

export const CRITERIA_LABELS: Record<Dimension, string> = {
  interest: "Interesse e reciprocidade",
  timing: "Momento de compra",
  need: "Necessidade",
  urgency: "Urgência de compra",
  budget: "Orçamento",
  authority: "Decisão",
  progress: "Próxima ação",
};

export const QUESTIONS: Record<Dimension, string> = {
  interest: "O cliente demonstrou interesse ou respondeu recentemente?",
  timing: "O cliente informou quando pretende decidir a compra?",
  need: "O cliente confirmou qual problema ou necessidade quer resolver?",
  urgency: "Existe uma razão concreta para o cliente comprar em breve?",
  budget: "O cliente indicou orçamento ou aprovação para a compra?",
  authority: "Você sabe quem participa da decisão de compra?",
  progress: "Existe uma próxima ação combinada com o cliente?",
};

type Labels = { [D in Dimension]: Record<AnswerOf<D>, string> };

export const ANSWER_LABELS: Labels = {
  interest: {
    replied: "Sim, respondeu ou participou de uma conversa recente",
    no_reply: "Houve contato, mas não respondeu recentemente",
    no_contact: "Ainda não houve contato",
    unknown: "Não sei",
  },
  timing: {
    within_30: "Sim, pretende decidir em até 30 dias",
    within_90: "Sim, entre 31 e 90 dias",
    later: "Sim, em mais de 90 dias",
    no_forecast: "Disse que ainda não tem previsão",
    not_discussed: "Não conversamos sobre isso",
    unknown: "Não sei",
  },
  need: {
    confirmed: "Sim, necessidade confirmada",
    investigating: "Estamos investigando",
    none: "Não foi identificada uma necessidade",
    unknown: "Não sei",
  },
  urgency: {
    concrete: "Sim, o cliente informou uma razão concreta",
    possible: "Possível, mas ainda não confirmada",
    none: "Não há razão para comprar em breve",
    unknown: "Não sei",
  },
  budget: {
    confirmed: "Sim, orçamento ou aprovação confirmados",
    needs_approval: "Depende de uma aprovação",
    none: "Não há orçamento por ora",
    unknown: "Não sei",
  },
  authority: {
    access: "Sim, e tenho acesso a essa pessoa",
    no_access: "Sei quem decide, mas ainda não tenho acesso",
    not_identified: "Ainda não identifiquei",
    unknown: "Não sei",
  },
  progress: {
    within_7: "Sim, para os próximos 7 dias",
    within_30: "Sim, para o próximo mês (de 8 a 30 dias)",
    later: "Sim, para daqui a mais de 30 dias",
    undated: "Sim, mas sem período combinado",
    none: "Não existe uma próxima ação combinada",
    unknown: "Não sei",
  },
};

/** Versão curta, para o comparativo lado a lado. */
export const ANSWER_SHORT: Labels = {
  interest: { replied: "Respondeu", no_reply: "Sem resposta", no_contact: "Sem contato", unknown: "Não sei" },
  timing: {
    within_30: "Até 30 dias", within_90: "31 a 90 dias", later: "Mais de 90 dias", no_forecast: "Sem previsão",
    not_discussed: "Não conversamos", unknown: "Não sei",
  },
  need: { confirmed: "Confirmada", investigating: "Investigando", none: "Não identificada", unknown: "Não sei" },
  urgency: { concrete: "Razão concreta", possible: "Possível", none: "Sem razão", unknown: "Não sei" },
  budget: { confirmed: "Confirmado", needs_approval: "Depende de aprovação", none: "Sem orçamento", unknown: "Não sei" },
  authority: { access: "Com acesso", no_access: "Sem acesso", not_identified: "Não identificado", unknown: "Não sei" },
  progress: {
    within_7: "Até 7 dias", within_30: "8 a 30 dias", later: "Mais de 30 dias", undated: "Sem período", none: "Não existe",
    unknown: "Não sei",
  },
};

export const answerLabel = (dimension: Dimension, answer: string | null, short = false): string =>
  answer === null ? "—" : ((short ? ANSWER_SHORT : ANSWER_LABELS)[dimension] as Record<string, string>)[answer];

export const CATEGORY_LABELS: Record<CategoryCode, string> = {
  review_answers: "Revisar respostas",
  commitment_due: "Compromisso a cumprir",
  commitment_to_organize: "Compromisso a organizar",
  define_continuity: "Definir continuidade",
  advance_qualification: "Avançar qualificação",
  resume_or_reassess: "Retomar ou reavaliar",
  investigate_first: "Investigar primeiro",
  qualify_need: "Qualificar necessidade",
};

/** O que fazer agora: orientação de trabalho, não previsão. */
export const CATEGORY_ACTIONS: Record<CategoryCode, string> = {
  review_answers: "Confirme ou corrija as respostas que se contradizem.",
  commitment_due: "Verifique ou execute a ação combinada com o cliente.",
  commitment_to_organize: "Confirme com o cliente quando e como a ação combinada vai acontecer.",
  define_continuity: "Acorde o próximo passo com o cliente.",
  advance_qualification: "Esclareça o que ainda não está confirmado antes de investir mais esforço.",
  resume_or_reassess: "Consulte o histórico e decida se vale um novo contato.",
  investigate_first: "Consulte o CRM ou quem atendeu a conta antes de decidir quanto esforço investir.",
  qualify_need: "Entenda se existe um problema que a oferta resolve.",
};

export const CONFLICT_TEXTS: Record<ConflictCode, string> = {
  no_contact_with_action:
    "Você respondeu que ainda não houve contato, mas também que existe uma ação combinada com o cliente.",
  no_contact_with_need:
    "Você respondeu que ainda não houve contato, mas também que a necessidade do cliente está confirmada.",
};

const list = (items: string[]): string => items.join(", ");

/** Por que a oportunidade recebeu esta orientação: só o que o vendedor respondeu. */
export function whyText(evaluation: Evaluation): string {
  switch (evaluation.category) {
    case "commitment_due":
      return `Você informou uma ação combinada para os próximos ${WINDOW_DAYS} dias.`;
    case "commitment_to_organize":
      return "Você informou uma ação combinada, mas sem período definido.";
    case "define_continuity":
      return "O cliente respondeu recentemente e confirmou a necessidade, mas não há próxima ação combinada.";
    case "advance_qualification": {
      const answerOf = (dimension: string) => evaluation.breakdown.find((row) => row.dimension === dimension)?.answer;
      if (answerOf("need") === "confirmed") {
        const authority = answerOf("authority");
        if (authority === "no_access" || authority === "not_identified") {
          return "A necessidade está confirmada, mas ainda não há acesso à pessoa que decide.";
        }
        // Necessidade confirmada e decisor ao alcance: o que falta é a ação para os próximos dias.
        if (authority === "access") {
          return `A necessidade está confirmada e há acesso a quem decide, mas não há ação combinada para os próximos ${WINDOW_DAYS} dias.`;
        }
      }
      return "Há diálogo ou necessidade em andamento, mas ainda nem tudo está confirmado.";
    }
    case "resume_or_reassess":
      return "Não houve resposta recente do cliente e não há ação combinada.";
    case "investigate_first":
      return "Muitas respostas foram “Não sei”: ainda não há informação para comparar.";
    case "qualify_need":
      return "Não foi identificada uma necessidade do cliente.";
    case "review_answers":
      return "Há respostas que se contradizem.";
    default:
      return "";
  }
}

export function noteText(note: Note): string {
  switch (note.code) {
    case "future_commitment":
      return `Há uma ação combinada, mas para além dos próximos ${WINDOW_DAYS} dias.`;
    case "authority_gap":
      return "Ainda não há acesso à pessoa que decide.";
  }
}

/** O que ainda não se sabe: as perguntas respondidas com "Não sei". */
export const unknownText = (evaluation: Evaluation): string | null =>
  evaluation.unknown.length ? list(evaluation.unknown.map((d) => CRITERIA_LABELS[d])) : null;

/** Quebra por dimensão: "Interesse e reciprocidade 20/20". */
export const breakdownText = (row: Evaluation["breakdown"][number]): string =>
  `${CRITERIA_LABELS[row.dimension]} ${row.points}/${row.weight}`;

export const ASSISTED = {
  title: "Priorização assistida",
  pointsLabel: "Pontos de qualificação declarada",
  points: (confirmed: number) => `${confirmed} de ${TOTAL} pontos`,
  potential: (potential: number) => `até ${potential} se o que você não sabe se confirmar`,
  disclaimer: "Pesos iniciais, a validar. Baseado nas suas respostas, mas não é previsão de fechamento.",
  localNote:
    "As respostas ficam só neste navegador: não vão ao servidor nem ao CRM e somem se você limpar os dados do navegador.",
  unsaved: "Este navegador não guardou as respostas: elas valem até você fechar a página.",
  close: "Fechar",
  card: {
    hint: "Compare as empatadas com o que você sabe.",
    button: "Avaliar empatadas",
    note: "Não muda a ordem oficial da Carteira.",
    orderedBy: "Ordem pela sua avaliação",
  },
  single: {
    title: "Priorização assistida",
    hint: "Responda 7 perguntas sobre o que você sabe desta negociação. O resultado fica só neste navegador e não " +
      "muda a ordem da Carteira.",
    button: "Avaliar com o que você sabe",
    edit: "Rever avaliação",
  },
  dialog: {
    step: (step: number, total: number) => `Etapa ${step} de ${total}`,
  },
  sheet: {
    setDescription: "Compare oportunidades empatadas com o que você sabe sobre cada negociação.",
    pickedDescription: "Compare as oportunidades que você marcou com o que sabe sobre cada negociação.",
    singleDescription: "O que você sabe sobre esta negociação.",
  },
  select: {
    title: "Escolha de 2 a 5 oportunidades",
    counter: (n: number) => `${n} de 5 escolhidas`,
    needMore: "Escolha ao menos 2 para comparar.",
    full: "Você já escolheu 5. Desmarque uma para trocar.",
    assessed: "Já avaliada",
    next: "Continuar",
    listLabel: "Oportunidades empatadas",
  },
  selection: {
    head: "Selecionar",
    row: (id: string) => `Selecionar ${id} para priorizar`,
    barLabel: "Oportunidades selecionadas para priorizar",
    counter: (n: number) => (n === 1 ? "1 selecionada" : `${n} selecionadas`),
    needMore: "Marque ao menos 2 para comparar.",
    full: "Máximo de 5 por vez.",
    ready: "Priorize a ordem entre elas.",
    action: "Priorizar",
    clear: "Limpar",
  },
  ask: {
    progress: (index: number, total: number) => `Oportunidade ${index} de ${total}`,
    answered: (n: number) => `${n} de ${DIMENSIONS.length} respondidas`,
    back: "Voltar",
    skip: "Pular por agora",
    next: "Salvar e seguir",
    finish: "Ver resultado",
    form: (id: string) => `Perguntas sobre ${id}`,
    questionTag: (n: number) => `Pergunta ${String(n).padStart(2, "0")}`,
    chooseOne: "Escolha só uma resposta",
  },
  conflict: {
    title: "Respostas que se contradizem",
    question: "Houve um equívoco?",
    keep: "Está correto",
    hint: "Se foi um equívoco, corrija as respostas acima.",
  },
  result: {
    title: "Ordem sugerida de trabalho",
    intro: "Baseada nas suas respostas. A ordem oficial da Carteira não mudou.",
    single: "Resultado desta avaliação",
    partialTitle: "Comparação parcial",
    partialBody: (ids: string[]) => `Ainda sem respostas completas: ${list(ids)}. Elas entram na ordem quando você concluir.`,
    incompleteTitle: "Avaliação incompleta",
    incompleteBody: "Responda as perguntas que ainda estão em aberto para ver o resultado.",
    answer: "Responder",
    pending: "Fora da ordem por enquanto",
    asideTitle: "Investigar primeiro: informações em aberto",
    asideNote: "Sem posição: com tantas respostas “Não sei”, ainda não há como comparar. Isso não é um juízo sobre a oportunidade.",
    position: (n: number, tied: boolean) => (tied ? `${n}º, empate` : `${n}º`),
    tied: "Mesma pontuação que outra oportunidade da lista.",
    manual: "Posição escolhida por você",
    why: "Por que",
    unknown: "O que ainda não sabemos",
    unknownBody: (names: string) => `Você respondeu “Não sei” em: ${names}.`,
    todo: "O que fazer agora",
    breakdown: "Pontos por pergunta",
    pointsOf: (points: number, weight: number) => `${points} de ${weight}`,
    localNoteLabel: "Onde ficam as respostas",
    assessedOn: (date: string) => `Avaliada em ${date}`,
    recalculated: "Recalculada com a política atual.",
    edit: "Editar respostas",
    up: (id: string) => `Subir ${id}`,
    down: (id: string) => `Descer ${id}`,
    compare: "Ver comparativo lado a lado",
    hideCompare: "Ocultar comparativo",
    compareTitle: "Respostas lado a lado",
    compareLabel: "Respostas de cada oportunidade",
    copy: "Copiar resumo e plano",
    copied: "Resumo copiado",
  },
  remove: {
    button: "Remover avaliação",
    label: (id: string) => `Remover avaliação de ${id}`,
    title: "Remover esta avaliação?",
    body: "As respostas desta oportunidade serão apagadas deste navegador e o selo some da Carteira.",
    confirm: "Remover",
    cancel: "Cancelar",
  },
  mark: {
    // A3 (decisão da dona): o selo na lista não leva os pontos, para não parecer nota por oportunidade; os pontos
    // ficam só no painel da assistida.
    done: (label: string) => `Avaliada · ${label}`,
    aside: "Avaliada · investigar primeiro",
    pending: "Avaliação incompleta",
    conflict: "Revisar respostas",
  },
} as const;

/** O selo de uma oportunidade avaliada na Carteira. */
export function markText(evaluation: Evaluation): string {
  if (evaluation.status === "conflict") return ASSISTED.mark.conflict;
  if (evaluation.status === "incomplete") return ASSISTED.mark.pending;
  if (evaluation.aside) return ASSISTED.mark.aside;
  return ASSISTED.mark.done(CATEGORY_LABELS[evaluation.category!]);
}

type SummaryInput = {
  seller: string;
  asOf: string;
  items: Record<string, Item>;
  ranked: Ranked[];
  aside: Evaluation[];
  pending: Evaluation[];
};

/** O resumo e o plano para colar fora do Rankio. Mesmas frases da tela, sem nada a mais. */
export function summaryText({ seller, asOf, items, ranked, aside, pending }: SummaryInput): string {
  const who = (id: string) => {
    const item = items[id];
    return item ? `${id} (${[item.product, clientText(item)].filter(Boolean).join(", ")})` : id;
  };
  const lines = [
    `${ASSISTED.title} · ${seller}`,
    `Dados até ${formatDate(asOf)}. ${ASSISTED.disclaimer}`,
    "",
  ];
  for (const { evaluation, position, tied } of ranked) {
    const category = CATEGORY_LABELS[evaluation.category!];
    const potential = evaluation.potential > evaluation.confirmed ? ` (${ASSISTED.potential(evaluation.potential)})` : "";
    lines.push(`${ASSISTED.result.position(position, tied)} ${who(evaluation.opportunityId)} · ` +
      `${ASSISTED.points(evaluation.confirmed)}${potential} · ${category}`);
    lines.push(`   ${ASSISTED.result.todo}: ${CATEGORY_ACTIONS[evaluation.category!]}`);
    const unknown = unknownText(evaluation);
    if (unknown) lines.push(`   ${ASSISTED.result.unknown}: ${unknown}`);
  }
  if (aside.length) {
    lines.push("", `${ASSISTED.result.asideTitle}:`);
    for (const evaluation of aside) lines.push(`   ${who(evaluation.opportunityId)}`);
  }
  if (pending.length) {
    lines.push("", `${ASSISTED.result.pending}:`);
    for (const evaluation of pending) lines.push(`   ${who(evaluation.opportunityId)} · ${markText(evaluation)}`);
  }
  return lines.join("\n");
}
