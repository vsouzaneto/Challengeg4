/**
 * Catálogo de apresentação por código: ícone e classes de cor de cada grupo e os ícones dos conceitos recorrentes.
 *
 * Fica em `copy/` pelo mesmo motivo do `GROUP_LABELS`: os componentes recebem `state` da API e leem daqui, sem
 * escrever chave de grupo à mão (`tests/policy.test.ts`). O `Record<GroupKey, …>` obriga a ter ícone e cor para
 * todo grupo novo do contrato. Nenhum ícone de relógio, ampulheta ou alvo (ADR-008): a idade não ordena.
 */
import {
  Binoculars, Building2, CalendarCheck, CalendarPlus, ListChecks, ListTodo, MessageCircleQuestion, RefreshCw, Search,
  Signpost, CalendarDays, CalendarRange, CircleDashed, ClipboardCheck, Database, Layers, EyeOff, FileSearch,
  FlaskConical, Focus, Info, ListOrdered, NotebookPen, Package, PencilLine, Scale, Sprout, Tag, TriangleAlert, UserRound,
  UsersRound, type LucideIcon,
} from "lucide-react";

import type { CategoryCode } from "@/lib/assisted/model";

import type { GroupKey } from "./pt-BR";

export type GroupVisual = {
  icon: LucideIcon;
  /** Preenchimento de gráfico (SVG): `var(--status-<g>-fill)`. */
  fill: string;
  /** Quadrado do ícone e linhas de fundo suave: fundo do grupo + texto do grupo (AA). */
  tile: string;
  /** Texto ou ícone na cor do grupo. */
  text: string;
  /** Fundo suave, sem cor de texto, que se mantém no hover de um botão fantasma. */
  soft: string;
};

export const GROUP_VISUAL: Record<GroupKey, GroupVisual> = {
  focar: {
    icon: Focus, fill: "var(--status-focar-fill)", tile: "bg-status-focar-bg text-status-focar",
    text: "text-status-focar", soft: "bg-status-focar-bg hover:bg-status-focar-bg dark:hover:bg-status-focar-bg",
  },
  qualificar: {
    icon: Sprout, fill: "var(--status-qualificar-fill)", tile: "bg-status-qualificar-bg text-status-qualificar",
    text: "text-status-qualificar", soft: "bg-status-qualificar-bg hover:bg-status-qualificar-bg dark:hover:bg-status-qualificar-bg",
  },
  acompanhar: {
    icon: Binoculars, fill: "var(--status-acompanhar-fill)", tile: "bg-status-acompanhar-bg text-status-acompanhar",
    text: "text-status-acompanhar", soft: "bg-status-acompanhar-bg hover:bg-status-acompanhar-bg dark:hover:bg-status-acompanhar-bg",
  },
  revisar: {
    icon: ClipboardCheck, fill: "var(--status-revisar-fill)", tile: "bg-status-revisar-bg text-status-revisar",
    text: "text-status-revisar", soft: "bg-status-revisar-bg hover:bg-status-revisar-bg dark:hover:bg-status-revisar-bg",
  },
  nao_pontuavel: {
    icon: PencilLine, fill: "var(--status-nao-pontuavel-fill)",
    tile: "bg-status-nao-pontuavel-bg text-status-nao-pontuavel", text: "text-status-nao-pontuavel",
    soft: "bg-status-nao-pontuavel-bg hover:bg-status-nao-pontuavel-bg dark:hover:bg-status-nao-pontuavel-bg",
  },
};

export const CONCEPT_ICONS = {
  listPrice: Tag,
  age: CalendarRange,
  engaged: CalendarDays,
  account: Building2,
  noAccount: CircleDashed,
  product: Package,
  seller: UserRound,
  people: UsersRound,
  blindSpot: EyeOff,
  verify: FileSearch,
  evidence: FlaskConical,
  warning: TriangleAlert,
  info: Info,
  tie: Layers,
  assisted: NotebookPen,
  order: ListOrdered,
  data: Database,
  qualify: Sprout,
  compare: Scale,
} as const satisfies Record<string, LucideIcon>;

export type Concept = keyof typeof CONCEPT_ICONS;

/** Ícone de cada categoria da priorização assistida (o nome sempre acompanha). */
export const CATEGORY_ICONS: Record<CategoryCode, LucideIcon> = {
  review_answers: ListChecks,
  commitment_due: CalendarCheck,
  commitment_to_organize: CalendarPlus,
  define_continuity: Signpost,
  advance_qualification: ListTodo,
  resume_or_reassess: RefreshCw,
  investigate_first: Search,
  qualify_need: MessageCircleQuestion,
};
