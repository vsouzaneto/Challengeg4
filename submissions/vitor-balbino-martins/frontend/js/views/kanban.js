import { api, ApiError } from "../api.js";
import { $, el, render, toast } from "../dom.js";
import * as fmt from "../format.js";

const STAGES = [["new", "Novo"], ["triage", "Em triagem"], ["progress", "Em atendimento"], ["done", "Resolvido"]];
let tickets = [];

function card(ticket) {
  const node = el("article", { class: "kanban-ticket", draggable: "true" }, [el("div", { class: "kanban-ticket-top" }, [el("span", { class: "eyebrow", text: `#${ticket.ticket_id}` }), el("span", { class: `priority-badge priority-${String(ticket.priority ?? "low").toLowerCase()}`, text: fmt.label(ticket.priority ?? "low") })]), el("h4", { text: ticket.subject || "Ticket sem assunto" }), el("p", { text: ticket.description || "Sem descrição disponível." }), el("div", { class: "kanban-ticket-foot" }, [el("span", { text: `${fmt.label(ticket.channel)} · ${fmt.label(ticket.ticket_type)}` }), el("span", { text: ticket.satisfaction == null ? "—" : `★ ${fmt.rating(ticket.satisfaction)}` })])]);
  node.addEventListener("dragstart", (event) => event.dataTransfer.setData("text/ticket-id", ticket.ticket_id));
  return node;
}

function paint() {
  const grouped = Object.fromEntries(STAGES.map(([stage]) => [stage, []]));
  tickets.forEach((ticket) => (grouped[ticket.stage] ??= []).push(ticket));
  render($("#kanban-body"), STAGES.map(([stage, label]) => {
    const column = el("section", { class: "kanban-column" }, [el("div", { class: "kanban-column-head" }, [el("h3", { text: label }), el("span", { class: "pill-tag", text: fmt.num(grouped[stage].length) })]), el("div", { class: "kanban-dropzone" }, grouped[stage].map(card))]);
    const zone = column.querySelector(".kanban-dropzone");
    zone.addEventListener("dragover", (event) => { event.preventDefault(); zone.classList.add("is-over"); });
    zone.addEventListener("dragleave", () => zone.classList.remove("is-over"));
    zone.addEventListener("drop", async (event) => { event.preventDefault(); zone.classList.remove("is-over"); const id = event.dataTransfer.getData("text/ticket-id"); const ticket = tickets.find((item) => item.ticket_id === id); if (!ticket || ticket.stage === stage) return; try { await api.moveTicket(id, stage); ticket.stage = stage; paint(); toast(`Ticket #${id} movido para ${label}.`); } catch (error) { toast(error instanceof ApiError ? error.message : "Não foi possível mover o ticket.", "error"); } });
    return column;
  }));
  $("#kanban-hint").textContent = `${fmt.num(tickets.length)} tickets persistidos · arraste para mover e salvar a etapa.`;
}

export function initKanban() {
  const load = async () => { try { tickets = await api.tickets(); paint(); } catch (error) { $("#kanban-hint").textContent = error instanceof ApiError ? error.message : "Sincronize o Dashboard antes de abrir o Kanban."; render($("#kanban-body"), el("div", { class: "state state-center" }, [el("h3", { text: "Nenhum ticket persistido" }), el("p", { text: "Execute a sincronização no Dashboard para carregar a base." })])); } };
  $("#kanban-refresh")?.addEventListener("click", load); load(); return {};
}
