// ROI da revisão — mesma fórmula de pipeline/05_revisao_csv.py (a paridade é checada por tests/roi.mjs).
//   horas por automação = volume elegível × minutos poupados ÷ 60 × taxa de acerto
//   benefício/mês = Σ horas × custo/hora
//   custo/mês = manutenção + API + revisão humana dos rascunhos
//   ROI 12m = (12 × benefício − (implantação + 12 × custo/mês)) ÷ (implantação + 12 × custo/mês)
//   payback = implantação ÷ (benefício/mês − custo/mês)

export function scenario(roi, i, { vol = roi.volume_mes, over = {} } = {}) {
  const g = (k) => (k in over ? over[k] : roi.premissas[k][i]);
  const horas = {};
  let revisaoH = 0;
  let api = 0;
  for (const [k, a] of Object.entries(roi.automacoes)) {
    const v = vol * roi.elegivel[k];
    const min = `${k}.min` in over ? over[`${k}.min`] : a.min[i];
    const acerto = `${k}.acerto` in over ? over[`${k}.acerto`] : a.acerto[i];
    horas[k] = (v * min) / 60 * acerto;
    revisaoH += (v * a.revisao[i]) / 60;
    if (a.llm) api += v * g('api_reais_por_rascunho');
  }
  const horasTotal = Object.values(horas).reduce((s, h) => s + h, 0);
  const beneficio = horasTotal * g('custo_hora');
  const manutencao = g('manut_horas_mes') * g('impl_custo_hora');
  const custoMes = manutencao + api + revisaoH * g('custo_hora');
  const impl = g('impl_horas') * g('impl_custo_hora');
  const custo12 = impl + 12 * custoMes;
  const liquido = beneficio - custoMes;
  return {
    horas, horas_total: horasTotal, beneficio_mes: beneficio, manutencao_mes: manutencao, revisao_mes: revisaoH * g('custo_hora'),
    api_mes: api, custo_mes: custoMes, implantacao: impl, roi_12m: (12 * beneficio - custo12) / custo12,
    payback_meses: liquido > 0 ? impl / liquido : null,
  };
}

// Volume mensal a partir do qual o ROI de 12 meses fica ≥ 0
export function breakeven(roi, i, over = {}) {
  let lo = 1;
  let hi = 1e6;
  for (let k = 0; k < 100; k += 1) {
    const mid = (lo + hi) / 2;
    if (scenario(roi, i, { vol: mid, over }).roi_12m >= 0) hi = mid; else lo = mid;
  }
  return hi;
}
