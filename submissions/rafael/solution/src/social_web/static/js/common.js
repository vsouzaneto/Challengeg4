/* Shared helpers: pt-BR formatting, lazy charts in collapsed sections, labels, evidence chips and theme-aware Chart.js setup (charts re-render on theme change). */
const LBL = window.SITE_LABELS || {};
const VAL = window.SITE_VALUES || {};
const label = k => LBL[k] || k;
const val = v => VAL[String(v)] ?? String(v);
const nf = (x, d = 0) => x == null || Number.isNaN(x) ? "—" : Number(x).toLocaleString("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d });
const pct = (x, d = 1) => x == null ? "—" : nf(x, d) + "%";
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const css = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const PALETTE = ["--c1", "--c2", "--c3", "--c4", "--c5"];

/* Evidence levels in plain words. */
function chip(evidence) {
  const e = String(evidence);
  if (e.startsWith("robusta") || e === "confirmado") return '<span class="chip confirmado">confirmado</span>';
  if (e.startsWith("replicada") || e.startsWith("se repetiu")) return '<span class="chip repetiu">se repetiu nos 2 anos</span>';
  if (e.startsWith("explor") || e === "pista") return '<span class="chip pista">pista</span>';
  return '<span class="chip nada">sem diferença</span>';
}

/* Describe a discovered pocket in words: "Tema: beauty · Idioma: espanhol". */
function describeConditions(cond) {
  return Object.entries(cond).map(([k, v]) => Array.isArray(v) ? `${label(k)} entre ${nf(v[0])} e ${nf(v[1])}` : `${label(k)}: ${val(v)}`).join(" · ");
}

/* Each chart is an entry {canvasId, build, chart}; build() reads the theme tokens, so redraws pick up theme changes. */
const CHARTS = [];
function makeChart(canvasId, build) {
  const el = $(canvasId);
  if (!el) return null;
  if (!window.Chart) { el.closest(".chart").innerHTML = '<p class="caption">Não foi possível carregar o gráfico.</p>'; return null; }
  const entry = { canvasId, build, chart: new Chart(el, build()) };
  CHARTS.push(entry);
  requestAnimationFrame(() => entry.chart.resize());  // re-measure once the surrounding layout has settled
  return entry;
}
/* Charts inside a closed <details> have no size: draw them the first time their section opens. */
function lazyChart(canvasId, build) {
  const el = $(canvasId), box = el && el.closest("details");
  if (!box || box.open) return makeChart(canvasId, build);
  box.addEventListener("toggle", () => { if (box.open && !CHARTS.some(c => c.canvasId === canvasId)) makeChart(canvasId, build); });
  return null;
}
/* Replace the content of an existing chart entry (or create it on first use). */
function setChart(entry, canvasId, build) {
  if (!entry) return makeChart(canvasId, build);
  entry.chart.destroy();
  entry.build = build;
  entry.chart = new Chart($(canvasId), build());
  requestAnimationFrame(() => entry.chart.resize());
  return entry;
}
function redrawCharts() { CHARTS.forEach(e => { e.chart.destroy(); e.chart = new Chart($(e.canvasId), e.build()); }); }
function chartOptions(extra = {}) {
  const ink = css("--muted"), rule = css("--rule");
  const base = { responsive: true, maintainAspectRatio: false, animation: false,
    plugins: { legend: { labels: { color: ink, boxWidth: 12, font: { family: "Manrope" } } },
               tooltip: { backgroundColor: css("--ink"), titleColor: css("--paper"), bodyColor: css("--paper") } },
    scales: { x: { ticks: { color: ink }, grid: { color: rule } }, y: { ticks: { color: ink }, grid: { color: rule } } } };
  return deepMerge(base, extra);
}
function deepMerge(a, b) {
  for (const [k, v] of Object.entries(b)) a[k] = v && typeof v === "object" && !Array.isArray(v) && typeof a[k] === "object" ? deepMerge({ ...a[k] }, v) : v;
  return a;
}
window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", redrawCharts);
new MutationObserver(redrawCharts).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
/* Close the "Aprofundar" menu when clicking anywhere else. */
document.addEventListener("click", e => document.querySelectorAll("details.menu[open]").forEach(m => { if (!m.contains(e.target)) m.open = false; }));
/* Charts drawn while their section was closed have no size: re-measure them when the section opens. */
document.addEventListener("toggle", e => {
  if (e.target.open) CHARTS.filter(c => e.target.contains($(c.canvasId))).forEach(c => c.chart.resize());
}, true);
/* A link to a section (e.g. /perguntas#patrocinio) opens that section's details, after the page's charts are registered. */
function openHashSection() {
  if (/^#[\w-]+$/.test(location.hash)) document.querySelector(location.hash + " details.more")?.setAttribute("open", "");
}
window.addEventListener("load", openHashSection);
window.addEventListener("hashchange", openHashSection);
