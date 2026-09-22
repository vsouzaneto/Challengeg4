'use strict';
const form = document.querySelector('#economics-form');
const statusText = document.querySelector('#economics-status');
const output = document.querySelector('#economics-result');
const presets = JSON.parse(document.querySelector('#economics-presets').textContent);
const number = new Intl.NumberFormat('pt-BR', {maximumFractionDigits: 2});
const money = new Intl.NumberFormat('pt-BR', {style: 'currency', currency: 'BRL'});
let revision = 0;
form.addEventListener('input', () => {
  revision++; output.hidden = true;
  statusText.textContent = 'Premissas alteradas. Calcule para atualizar o resultado.';
});
async function calculate() {
  if (!form.reportValidity()) return;
  const current = ++revision;
  output.hidden = true;
  statusText.textContent = 'Calculando…';
  const values = Object.fromEntries([...new FormData(form)].map(([key, value]) => [key, Number(value)]));
  try {
    const response = await fetch('/api/economics', {method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(values)});
    if (!response.ok) throw new Error('Não foi possível calcular. Confira as premissas e tente novamente.');
    const {result} = await response.json();
    if (current !== revision) return;
    for (const [key, value] of Object.entries(result)) {
      const target = document.getElementById(key);
      if (!target) continue;
      const monetary = ['capacity_value_month','avoided_expense_month','net_cash_month','first_year_net_cash'].includes(key);
      let text = value === null ? 'Não se aplica' : monetary ? money.format(value) : number.format(value);
      if (value !== null) {
        if (key === 'hours_month') text += ' h';
        if (key === 'fte_capacity') text += ' pessoa';
        if (key === 'roi_12m_pct') text += '%';
        if (key === 'payback_months') text += ' meses';
        if (key === 'break_even_minutes_12m') text += ' min';
      }
      target.textContent = text;
    }
    const extra = document.querySelector('#additional-work');
    extra.hidden = result.additional_work_value_month <= 0;
    extra.textContent = 'Este cenário acrescenta trabalho: ' + money.format(result.additional_work_value_month) + '/mês em capacidade consumida. Esse custo de oportunidade é adicional ao saldo financeiro exibido.';
    output.hidden = false;
    statusText.textContent = 'Cenário calculado. Valores estimados, sem economia observada.';
  } catch (error) {
    if (current === revision) statusText.textContent = error.message;
  }
}
form.addEventListener('submit', event => {event.preventDefault(); calculate();});
document.querySelector('#scenario').addEventListener('change', event => {
  for (const [key, value] of Object.entries(presets[event.target.value])) form.elements[key].value = value;
  calculate();
});
calculate();
