/* Formatação e utilidades sem estado. */

const num = new Intl.NumberFormat("pt-BR");
const compactFmt = new Intl.NumberFormat("pt-BR", { notation: "compact", maximumFractionDigits: 1 });

export const fmt = (value) => num.format(Math.round(value));
export const compact = (value) => compactFmt.format(value);
export const pct = (part, total) => (total ? `${Math.round((part / total) * 100)}%` : "—");

export function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}

export function fmtDate(iso) {
  if (!iso) return "—";
  const [y, m, d] = iso.split("-");
  return `${d}/${m}/${y}`;
}

export const initials = (name) => name.split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0]).join("").toUpperCase();
export const firstName = (name) => name.split(/\s+/)[0];

export function median(values) {
  if (!values.length) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.floor(sorted.length / 2)];
}

export function readStore(key, fallback) {
  try { const raw = localStorage.getItem(key); return raw ? JSON.parse(raw) : fallback; } catch { return fallback; }
}
export function writeStore(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* armazenamento indisponível */ }
}

export function downloadCsv(filename, header, rows) {
  const cell = (v) => {
    const s = String(v ?? "");
    return /[";\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const text = [header, ...rows].map((r) => r.map(cell).join(";")).join("\n");
  const blob = new Blob(["﻿" + text], { type: "text/csv;charset=utf-8" });
  const link = Object.assign(document.createElement("a"), { href: URL.createObjectURL(blob), download: filename });
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(link.href), 1000);
}

/* Tooltip único: conteúdo sempre via textContent (rótulos são dados). */
const tip = () => document.getElementById("tooltip");

function placeTooltip(x, y) {
  const node = tip();
  node.hidden = false;
  const box = node.getBoundingClientRect();
  node.style.left = `${Math.max(8, Math.min(x + 14, window.innerWidth - box.width - 8))}px`;
  node.style.top = `${y - box.height - 12 < 8 ? y + 20 : y - box.height - 12}px`;
}

export function hideTooltip() { tip().hidden = true; }

/* Ícones ⓘ em qualquer tela: hover, foco ou toque mostram a definição. */
export function bindInfo() {
  const show = (button) => {
    const node = tip();
    node.replaceChildren();
    node.classList.add("is-text");
    node.textContent = button.dataset.info;
    const r = button.getBoundingClientRect();
    placeTooltip(r.left, r.top);
  };
  document.addEventListener("pointerover", (e) => { const b = e.target.closest("[data-info]"); if (b) show(b); });
  document.addEventListener("pointerout", (e) => { if (e.target.closest("[data-info]")) hideTooltip(); });
  document.addEventListener("focusin", (e) => { const b = e.target.closest("[data-info]"); if (b) show(b); });
  document.addEventListener("focusout", (e) => { if (e.target.closest("[data-info]")) hideTooltip(); });
  document.addEventListener("click", (e) => {
    const b = e.target.closest("[data-info]");
    if (b) { e.preventDefault(); e.stopPropagation(); show(b); }
  }, true);
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") hideTooltip(); });
  window.addEventListener("scroll", hideTooltip, true);
}

/* Tooltip de gráficos: título + linhas (valor em destaque, rótulo secundário). */
export function bindTooltip(root, describe) {
  const show = (target, x, y) => {
    const info = describe(target);
    if (!info) return;
    const node = tip();
    node.classList.remove("is-text");
    node.replaceChildren();
    const title = document.createElement("div");
    title.className = "tt-title";
    title.textContent = info.title;
    node.append(title);
    for (const row of info.rows) {
      const line = document.createElement("div");
      line.className = "tt-row";
      const key = document.createElement("i");
      key.style.background = row.color || "transparent";
      const value = document.createElement("strong");
      value.textContent = row.value;
      const label = document.createElement("span");
      label.textContent = row.label;
      line.append(key, value, label);
      node.append(line);
    }
    placeTooltip(x, y);
  };
  const hide = hideTooltip;
  root.addEventListener("pointermove", (e) => {
    if (e.target.closest("[data-info]")) return; // o ⓘ tem tooltip próprio
    const target = e.target.closest("[data-tip]");
    target ? show(target, e.clientX, e.clientY) : hide();
  });
  root.addEventListener("pointerleave", hide);
  root.addEventListener("focusin", (e) => {
    const target = e.target.closest("[data-tip]");
    if (!target) return;
    const r = target.getBoundingClientRect();
    show(target, r.left + r.width / 2, r.top);
  });
  root.addEventListener("focusout", hide);
}
