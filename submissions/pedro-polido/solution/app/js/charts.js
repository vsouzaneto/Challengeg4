// Gráficos SVG mínimos, sem dependências. As cores são variáveis CSS, então funcionam nos temas claro e escuro.

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

function frame(h, m, w = 600) {
  return { w, h, m, iw: w - m.l - m.r, ih: h - m.t - m.b };
}

function scale(d0, d1, r0, r1) {
  return (v) => r0 + ((v - d0) / (d1 - d0)) * (r1 - r0);
}

function yAxis(f, y, ticks, fmt) {
  return ticks.map((t) => `
    <line class="grid" x1="${f.m.l}" x2="${f.m.l + f.iw}" y1="${y(t)}" y2="${y(t)}"/>
    <text x="${f.m.l - 8}" y="${y(t) + 4}" text-anchor="end">${fmt(t)}</text>`).join('');
}

// Histograma com barras coloridas por uma regra (ex.: valores negativos em vermelho)
export function histogram(el, { counts, edges, color = () => 'var(--faint)', xFmt = (v) => v, annotate, width }) {
  const f = frame(240, { t: 22, r: 10, b: 34, l: 48 }, width);
  const max = Math.max(...counts);
  const x = scale(edges[0], edges[edges.length - 1], f.m.l, f.m.l + f.iw);
  const y = scale(0, max * 1.15, f.m.t + f.ih, f.m.t);
  const ticks = [0, Math.round(max / 2), max];
  const bars = counts.map((c, i) => {
    const x0 = x(edges[i]) + 1;
    const x1 = x(edges[i + 1]) - 1;
    return `<rect x="${x0}" y="${y(c)}" width="${Math.max(0, x1 - x0)}" height="${y(0) - y(c)}" rx="2" fill="${color(edges[i], edges[i + 1])}"><title>${xFmt(edges[i])} a ${xFmt(edges[i + 1])}: ${c}</title></rect>`;
  }).join('');
  const xt = edges.filter((_, i) => i % 3 === 0).map((e) => `<text x="${x(e)}" y="${f.m.t + f.ih + 18}" text-anchor="middle">${xFmt(e)}</text>`).join('');
  const zero = edges[0] < 0 && edges[edges.length - 1] > 0
    ? `<line x1="${x(0)}" x2="${x(0)}" y1="${f.m.t}" y2="${f.m.t + f.ih}" stroke="var(--text)" stroke-width="1.5" stroke-dasharray="4 3"/>` : '';
  const note = annotate ? `<text x="${annotate.x === 'left' ? f.m.l + 6 : f.m.l + f.iw - 6}" y="${f.m.t + 10}" text-anchor="${annotate.x === 'left' ? 'start' : 'end'}" style="fill:${annotate.color};font-weight:700;font-size:12px">${esc(annotate.text)}</text>` : '';
  el.innerHTML = `<svg viewBox="0 0 ${f.w} ${f.h}" role="img">${yAxis(f, y, ticks, (v) => v)}${bars}${zero}${xt}${note}</svg>`;
}

// Linhas (ex.: curva de poder, cobertura × acerto). series: [{points: [[x, y]], color, label, dash}]
export function lineChart(el, { series, x, y, marker, height = 250, xLabel, width }) {
  const f = frame(height, { t: 18, r: 18, b: xLabel ? 48 : 30, l: 52 }, width);
  const sx = scale(x.min, x.max, f.m.l, f.m.l + f.iw);
  const sy = scale(y.min, y.max, f.m.t + f.ih, f.m.t);
  const xt = x.ticks.map((t) => `<text x="${sx(t)}" y="${f.m.t + f.ih + 18}" text-anchor="middle">${x.fmt(t)}</text>`).join('');
  const lines = series.map((s) => {
    const d = s.points.filter((p) => p[1] !== null).map((p, i) => `${i ? 'L' : 'M'}${sx(p[0]).toFixed(1)},${sy(p[1]).toFixed(1)}`).join('');
    const dots = s.dots ? s.points.map((p) => `<circle cx="${sx(p[0])}" cy="${sy(p[1])}" r="3.5" fill="${s.color}"><title>${esc(s.label || '')}: ${x.fmt(p[0])} → ${y.fmt(p[1])}</title></circle>`).join('') : '';
    return `<path d="${d}" fill="none" stroke="${s.color}" stroke-width="2.5" ${s.dash ? 'stroke-dasharray="5 4"' : ''} stroke-linejoin="round"/>${dots}`;
  }).join('');
  let mk = '';
  if (marker) {
    mk = `<line x1="${sx(marker.x)}" x2="${sx(marker.x)}" y1="${f.m.t}" y2="${f.m.t + f.ih}" stroke="var(--text)" stroke-width="1.2" stroke-dasharray="3 3"/>`;
    (marker.points || []).forEach((p) => {
      mk += `<circle cx="${sx(marker.x)}" cy="${sy(p.y)}" r="5" fill="var(--surface)" stroke="${p.color}" stroke-width="2.5"/>
             <text x="${sx(marker.x) + (marker.x > (x.min + x.max) / 2 ? -9 : 9)}" y="${sy(p.y) - 8}" text-anchor="${marker.x > (x.min + x.max) / 2 ? 'end' : 'start'}" style="fill:${p.color};font-weight:700;font-size:12px">${esc(p.label)}</text>`;
    });
  }
  const xl = xLabel ? `<text x="${f.m.l + f.iw / 2}" y="${f.h - 6}" text-anchor="middle">${esc(xLabel)}</text>` : '';
  el.innerHTML = `<svg viewBox="0 0 ${f.w} ${f.h}" role="img">${yAxis(f, sy, y.ticks, y.fmt)}${lines}${mk}${xt}${xl}</svg>`;
}

// Barras agrupadas com faixas de fundo (ex.: acerto por faixa de confiança, com as faixas da política)
export function groupedBars(el, { groups, series, y, bands = [], height = 250, width }) {
  const f = frame(height, { t: 30, r: 10, b: 32, l: 52 }, width);
  const gw = f.iw / groups.length;
  const sy = scale(y.min, y.max, f.m.t + f.ih, f.m.t);
  const bw = Math.min(26, (gw - 12) / series.length);
  const bg = bands.map((b) => `<rect x="${f.m.l + b.from * gw}" y="${f.m.t - 22}" width="${(b.to - b.from) * gw}" height="${f.ih + 22}" fill="${b.color}" opacity=".12"/>
    <text x="${f.m.l + (b.from + (b.to - b.from) / 2) * gw}" y="${f.m.t - 8}" text-anchor="middle" style="fill:${b.color};font-weight:700;font-size:14px">${esc(b.label)}</text>`).join('');
  const bars = groups.map((g, i) => series.map((s, k) => {
    const v = s.values[i];
    const x0 = f.m.l + i * gw + (gw - bw * series.length) / 2 + k * bw;
    return `<rect x="${x0}" y="${sy(v)}" width="${bw - 2}" height="${sy(y.min) - sy(v)}" rx="2" fill="${s.color}"><title>${esc(g)} · ${esc(s.label)}: ${y.fmt(v)}</title></rect>`;
  }).join('') + `<text x="${f.m.l + i * gw + gw / 2}" y="${f.m.t + f.ih + 18}" text-anchor="middle">${esc(g)}</text>`).join('');
  el.innerHTML = `<svg viewBox="0 0 ${f.w} ${f.h}" role="img">${bg}${yAxis(f, sy, y.ticks, y.fmt)}${bars}</svg>`;
}

// Médias com intervalo de confiança (ex.: CSAT por canal)
export function dotsCI(el, { items, x, fmt, width }) {
  const rowH = 40;
  const f = frame(items.length * rowH + 40, { t: 10, r: 20, b: 32, l: 120 }, width);
  const sx = scale(x.min, x.max, f.m.l, f.m.l + f.iw);
  const grid = x.ticks.map((t) => `<line class="grid" x1="${sx(t)}" x2="${sx(t)}" y1="${f.m.t}" y2="${f.m.t + f.ih}"/><text x="${sx(t)}" y="${f.m.t + f.ih + 18}" text-anchor="middle">${fmt(t)}</text>`).join('');
  const rows = items.map((it, i) => {
    const cy = f.m.t + i * rowH + rowH / 2;
    return `<text x="${f.m.l - 10}" y="${cy + 4}" text-anchor="end" style="fill:var(--text)">${esc(it.label)}</text>
      <line x1="${sx(it.mean - it.ci)}" x2="${sx(it.mean + it.ci)}" y1="${cy}" y2="${cy}" stroke="var(--accent)" stroke-width="3" stroke-linecap="round" opacity=".45"/>
      <circle cx="${sx(it.mean)}" cy="${cy}" r="6" fill="var(--accent)"><title>${esc(it.label)}: ${fmt(it.mean)} ± ${fmt(it.ci)}</title></circle>`;
  }).join('');
  el.innerHTML = `<svg viewBox="0 0 ${f.w} ${f.h}" role="img">${grid}${rows}</svg>`;
}
