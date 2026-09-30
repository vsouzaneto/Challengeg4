import { api, ApiError } from "../api.js";
import { $, el, render, toast } from "../dom.js";
import * as fmt from "../format.js";

const lanes = ["alta", "media", "baixa"];
const laneLabels = { alta: "Agora", media: "Próximo ciclo", baixa: "Monitorar" };

function card(item) {
  const priority = String(item.prioridade ?? "media").toLowerCase();
  return el("article", { class: `improvement-card priority-${priority}` }, [
    el("div", { class: "improvement-card-top" }, [el("span", { class: "pill-tag", text: item.categoria || "Operação" }), el("span", { class: "improvement-priority", text: priority })]),
    el("h3", { text: item.problema || "Ponto de melhoria" }),
    el("div", { class: "improvement-evidence" }, [el("b", { text: "Evidência" }), evidenceView(item.evidencia)]),
    el("div", { class: "improvement-impact" }, [el("b", { text: "Impacto" }), el("span", { text: item.impacto || "Impacto operacional identificado" })]),
    el("div", { class: "improvement-action" }, [el("b", { text: "Ação recomendada" }), el("span", { text: item.acao || "Definir responsável e próxima ação." })]),
    item.ganho_estimado ? el("small", { class: "improvement-gain", text: `✦ Ganho estimado: ${item.ganho_estimado}` }) : null,
    item.fontes ? el("small", { class: "improvement-source", text: `Fonte: ${Array.isArray(item.fontes) ? item.fontes.map((source) => source.file).join(", ") : item.fontes}` }) : null,
  ]);
}

function evidenceView(value) {
  if (!value) return el("span", { text: "Evidência consolidada na base." });
  if (typeof value === "string") return el("span", { text: value });
  const values = Array.isArray(value) ? value : Object.entries(value).map(([key, val]) => ({ metric: key, value: val }));
  const rows = values.slice(0, 5).map((row) => {
    if (row.dimensions) return el("div", { class: "evidence-row" }, [el("span", { class: "evidence-main", text: Object.values(row.dimensions).map(fmt.label).join(" · ") }), el("span", { class: "evidence-value", text: `${row.avg ?? "—"} h · ${row.tickets ?? 0} tickets` })]);
    return el("div", { class: "evidence-row" }, [el("span", { class: "evidence-main", text: fmt.label(row.metric || row.title || "Métrica") }), el("span", { class: "evidence-value", text: typeof row.value === "object" ? JSON.stringify(row.value) : String(row.value) })]);
  });
  return el("div", { class: "evidence-structured" }, [el("div", {}, rows), el("details", {}, [el("summary", { text: "Ver dados brutos" }), el("pre", { text: JSON.stringify(value, null, 2) })])]);
}

function paint(payload) {
  const result = payload.improvement || {};
  const items = Array.isArray(result.esteira) ? result.esteira : [];
  const groups = Object.fromEntries(lanes.map((lane) => [lane, items.filter((item) => String(item.prioridade ?? "media").toLowerCase() === lane)]));
  render($("#improvements-body"), [result.resumo ? el("article", { class: "improvement-summary" }, [el("span", { class: "eyebrow", text: "SÍNTESE DO AGENTE" }), el("p", { text: result.resumo })]) : null, el("div", { class: "improvement-legend" }, [el("span", { text: `${fmt.num(items.length)} pontos consolidados` }), el("span", { text: "Agora = maior impacto e urgência" })]), el("div", { class: "improvement-board" }, lanes.map((lane) => el("section", { class: "improvement-lane" }, [el("div", { class: "improvement-lane-head" }, [el("div", {}, [el("span", { class: "lane-dot" }), el("h3", { text: laneLabels[lane] })]), el("span", { class: "pill-tag", text: fmt.num(groups[lane].length) })]), ...(groups[lane].length ? groups[lane].map(card) : [el("p", { class: "card-note", text: "Nenhuma ação nesta prioridade." })])]))) ]);
}

export function initImprovements() {
  const button = $("#improvements-run");
  button?.addEventListener("click", async () => { button.disabled = true; button.textContent = "Consolidando..."; try { paint(await api.improvements({ dataset: "customer_support_tickets.csv", chunk_size: 250 })); toast("Esteira de melhorias atualizada."); } catch (error) { toast(error instanceof ApiError ? error.message : "Não foi possível consolidar a base.", "error"); } finally { button.disabled = false; button.textContent = "Consolidar base"; } });
  return {};
}
