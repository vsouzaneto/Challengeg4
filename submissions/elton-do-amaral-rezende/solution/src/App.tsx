import { useEffect, useState } from 'react';
import { EmptyDailyQueue } from './components/EmptyDailyQueue';
import { DailyTopTen } from './components/DailyTopTen';
import { DailyProgress } from './components/DailyProgress';
import { Icon } from './components/Icon';
import { dataset, opportunityById, evaluationSummary } from './data/dataset';
import { OPERATIONAL_TIME_ZONE } from './domain/config';
import { greeting } from './domain/dates';
import { completedCount, currentStreak, pendingIds, resolveMission, statusOf } from './domain/missions/queue';
import type { DayKey } from './domain/types';
import { useDailyQueue } from './state/useDailyQueue';

type Toast = { text: string; undo?: { day: DayKey; id: string } };
const dateLabel = (date: string) => new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeZone: 'UTC' }).format(new Date(`${date}T12:00:00Z`));
const percent = (n: number | null) => n === null ? '—' : `${(n * 100).toFixed(1).replace('.', ',')}%`;
const methodLabel: Record<string, string> = { priority: 'Score de prioridade', 'without-value': 'Score sem preço', 'without-age': 'Score sem idade', 'catalog-price': 'Preço de catálogo', 'recent-engagement': 'Engajamento recente', random: 'Aleatório (seed fixa)' };

export function App() {
  const queue = useDailyQueue();
  const { now, dayKey, seller, state, day } = queue;
  const [toast, setToast] = useState<Toast | null>(null);
  const [manager, setManager] = useState(''), [region, setRegion] = useState('');
  const availableAgents = dataset.agents.filter((a) => (!manager || a.manager === manager) && (!region || a.region === region));
  const completed = day ? completedCount(day) : 0;
  const batchDone = day?.batch.filter((id) => statusOf(day, id) === 'completed').length ?? 0;
  const deferred = day ? Object.values(day.actions).filter((a) => a.status === 'deferred').length : 0;
  const streak = state ? currentStreak(state, dayKey) : 0;
  useEffect(() => {
    if (seller && day?.batch.length === 0) document.getElementById('finished-title')?.focus();
  }, [seller, day?.batch.length]);
  useEffect(() => {
    if (!toast) return;
    const timer = window.setTimeout(() => setToast(null), 9000);
    return () => window.clearTimeout(timer);
  }, [toast]);
  function chooseSeller(name: string) { queue.chooseSeller(name); setToast(null); }
  function onResolve(id: string, status: 'completed' | 'deferred') {
    if (!day || !state || statusOf(day, id) !== 'pending') return;
    const preview = resolveMission(state, dayKey, id, status, new Date().toISOString()).days[dayKey];
    let text = status === 'completed' ? 'Ação concluída.' : 'Missão adiada para amanhã.';
    if (status === 'completed' && completed < day.goal && completedCount(preview) >= day.goal) text = 'Meta do dia cumprida!';
    if (pendingIds(day).length === 1) {
      const allCompleted = day.batch.every((item) => item === id ? status === 'completed' : statusOf(day, item) === 'completed');
      if (allCompleted && preview.batch.length) text += ' Lote concluído!';
      text += preview.batch.length ? ` Próximas ${preview.batch.length} prioridades carregadas.` : ' Você revisou todas as prioridades disponíveis.';
    }
    if (!queue.resolve(id, status)) { setToast({ text: 'O dia mudou. Sua fila foi atualizada; escolha uma missão para continuar.' }); return; }
    setToast({ text, undo: { day: dayKey, id } });
  }
  function undo(actionDay: DayKey, id: string) {
    queue.undo(actionDay, id); setToast({ text: 'Registro desfeito. A missão volta ao lote ou à fila elegível.' });
  }
  async function copy(id: string) {
    const opportunity = opportunityById.get(id); if (!opportunity) return;
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard indisponível');
      await navigator.clipboard.writeText(opportunity.nextAction);
      setToast({ text: 'Orientação copiada. A missão continua pendente.' });
    } catch { setToast({ text: 'Não foi possível copiar automaticamente. Selecione o texto da próxima ação para copiá-lo.' }); }
  }
  function exportCsv() {
    if (!seller) return;
    const rows = dataset.opportunities.filter((o) => o.salesAgent === seller);
    const cell = (v: unknown) => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const csv = '\uFEFF' + [['opportunity_id', 'sales_agent', 'account', 'product', 'stage', 'catalog_price_usd', 'priority_score', 'as_of_date', 'next_action'], ...rows.map((o) => [o.opportunityId, o.salesAgent, o.account, o.product, o.stage, o.catalogPriceUsd, o.priorityScore, o.asOfDate, o.nextAction])].map((r) => r.map(cell).join(',')).join('\r\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    const anchor = document.createElement('a'); anchor.href = url; anchor.download = 'lead-scorer-carteira.csv'; anchor.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  const historyDays = state ? Object.keys(state.days).filter((d) => Object.keys(state.days[d].actions).length).sort().reverse() : [];
  return <main className="app-shell">
    <nav className="topbar" aria-label="Carteira de trabalho">
      <div className="brand"><span className="brand-mark" aria-hidden="true"><Icon name="arrow" /></span>Lead Scorer<span className="brand-caption">Prioridades do dia</span></div>
      <div className="seller-field"><label htmlFor="seller">Sua carteira</label><select id="seller" value={seller} onChange={(e) => chooseSeller(e.target.value)}><option value="" disabled>Escolha seu nome</option>{seller && !availableAgents.some((a) => a.name === seller) && <option value={seller}>{seller}</option>}{availableAgents.map((a) => <option key={a.name} value={a.name}>{a.name}</option>)}</select></div>
    </nav>
    {queue.persistenceWarning && <p className="persistence-warning" role="status">O armazenamento está indisponível ou precisou ser recuperado. Seus registros serão mantidos apenas nesta sessão.</p>}
    <header className="daily-header"><div><p className="date-label">{new Intl.DateTimeFormat('pt-BR', { timeZone: OPERATIONAL_TIME_ZONE, weekday: 'long', day: 'numeric', month: 'long' }).format(now)}</p><h1>{greeting(now)}{seller ? `, ${seller.split(' ')[0]}` : ''}.<br />{day && day.batch.length > 0 && day.batchNumber > 1 ? `Mais ${day.batch.length} prioridades · lote ${day.batchNumber}` : day && day.ranking.length > 0 && day.batch.length === 0 ? 'Sua rotina de hoje.' : 'Seu Top 10 de hoje.'}</h1></div>{day && <div className="daily-counter"><strong>{day.batch.length ? batchDone : '✓'}</strong>{day.batch.length > 0 && <span>/{day.batch.length}</span>}<p>{streak ? `${streak} ${streak === 1 ? 'dia' : 'dias'} com a meta cumprida` : 'Uma ação de cada vez'}</p></div>}</header>
    {day && day.batch.length > 0 && <DailyProgress day={day} />}
    {day && <div className="daily-summary"><Icon name="check" size={19} /><span><strong>{completed} {completed === 1 ? 'concluída' : 'concluídas'} hoje</strong>{deferred > 0 && ` · ${deferred} ${deferred === 1 ? 'adiada' : 'adiadas'} para amanhã`}{day.batchNumber > 1 && ` · lote ${day.batchNumber}`}</span></div>}
    {!seller ? <EmptyDailyQueue /> : day && day.batch.length ? <DailyTopTen day={day} onSelect={queue.select} onResolve={onResolve} onCopy={copy} /> : <section className="finished" aria-labelledby="finished-title"><span className="finished-icon"><Icon name="check" size={28} /></span><h2 id="finished-title" tabIndex={-1}>Você revisou todas as prioridades disponíveis.</h2><p>{day?.ranking.length ? `${completed} ações concluídas e ${deferred} adiamentos hoje.` : 'Esta carteira não tem oportunidades abertas disponíveis hoje.'}</p><p>{day?.goal ? `Meta diária: ${day.goal} ações únicas. ${completed >= day.goal ? 'Meta cumprida.' : 'Adiamentos não contam como conclusão.'}` : 'Sem oportunidades, não há conquista de meta neste dia.'}</p></section>}
    {state && <details className="history-panel"><summary>Histórico de ações{historyDays.length ? ` · ${completed} ${completed === 1 ? 'concluída' : 'concluídas'} hoje` : ''}</summary>{!historyDays.length && <p>Seu histórico começa aqui. Conclua ou adie uma missão para registrar a ação.</p>}{historyDays.map((d) => <section key={d} className="history-day"><h3>{dateLabel(d)} · {completedCount(state.days[d])}/{state.days[d].goal} ações da meta</h3>{Object.values(state.days[d].actions).map((a) => <div className="history-row" key={a.opportunityId}><Icon name={a.status === 'completed' ? 'check' : 'clock'} size={17} /><div><strong>{opportunityById.get(a.opportunityId)?.account ?? `Oportunidade #${a.opportunityId}`}</strong><span>{a.status === 'completed' ? 'Ação concluída' : `Adiada para ${dateLabel(a.deferredUntil!)}`}</span></div><button className="text-button" onClick={() => undo(d as DayKey, a.opportunityId)} aria-label={`Desfazer ${a.status === 'completed' ? 'conclusão' : 'adiamento'} da oportunidade ${a.opportunityId} em ${dateLabel(d)}`}><Icon name="undo" size={16} />Desfazer</button></div>)}</section>)}</details>}
    <div className="secondary-panels"><details className="method"><summary>Como priorizamos</summary><div className="method-content"><h2>Prioridade com contexto</h2><p>O índice combina evidência histórica (65%), idade desde o engajamento (25%) e preço unitário de catálogo (10%). As contribuições em pontos aparecem em cada missão. Não é probabilidade de fechamento ou receita esperada.</p><p>As taxas por produto, setor e conta são suavizadas com 20 negócios de referência global. Cadastro ausente usa fallback; não é tratado como desinteresse. Idade é o tempo desde a entrada em engajamento, nunca desde o último contato.</p><h3>Dados e limites</h3><p>{dataset.quality.rows.pipeline.toLocaleString('pt-BR')} oportunidades do dataset público de demonstração do Kaggle, com empresas fictícias. {dataset.opportunities.length.toLocaleString('pt-BR')} abertas; {dataset.quality.aliases.toLocaleString('pt-BR')} vínculos corrigidos de GTXPro para GTX Pro. Conta não informada em {dataset.quality.missingAccounts.toLocaleString('pt-BR')} registros. Valores em USD; preço de catálogo não é valor negociado.</p><h3>Avaliação histórica · Top 10 por vendedor</h3><p>Histórico até {dateLabel(evaluationSummary.cutoff)}, resultados até {dateLabel(evaluationSummary.horizon)}. {evaluationSummary.eligible.toLocaleString('pt-BR')} candidatos: {evaluationSummary.outcomes.wins} ganhos, {evaluationSummary.outcomes.losses} perdidos e {evaluationSummary.outcomes.censored.toLocaleString('pt-BR')} sem resultado conhecido.</p><div className="table-scroll"><table><caption>Resumo agregado do Top 10 de cada vendedor com candidatos</caption><thead><tr><th>Método</th><th>Won</th><th>Lost</th><th>Sem resultado</th><th>Vitória entre resolvidos</th></tr></thead><tbody>{evaluationSummary.summary.map((r) => <tr key={r.method}><th scope="row">{methodLabel[r.method]}</th><td>{r.wins}</td><td>{r.losses}</td><td>{r.censored}</td><td>{percent(r.resolvedWinRate)}</td></tr>)}</tbody></table></div><p className="evaluation-warning">A regra não superou a referência aleatória na taxa de vitória entre resolvidos. Os grupos têm coberturas diferentes. Esta avaliação não comprova aumento de conversão.</p><ul>{evaluationSummary.limitations.map((text) => <li key={text}>{text}</li>)}</ul><p>As ações feitas e a sequência são registros locais da sua rotina. Não confirmam contatos, vendas ou alterações no CRM; não sincronizam dispositivos.</p><a href="https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics" target="_blank" rel="noreferrer">Ver fonte dos dados ↗</a></div></details>
    <details className="team-options"><summary>Opções da equipe</summary><div className="team-fields"><label>Gestor<select value={manager} onChange={(e) => setManager(e.target.value)}><option value="">Todos</option>{[...new Set(dataset.agents.map((a) => a.manager))].sort().map((name) => <option key={name}>{name}</option>)}</select></label><label>Região<select value={region} onChange={(e) => setRegion(e.target.value)}><option value="">Todas</option>{[...new Set(dataset.agents.map((a) => a.region))].sort().map((name) => <option key={name}>{name}</option>)}</select></label><p>Os filtros alteram as opções do seletor de carteira. A rotina continua sendo de um vendedor por vez.</p><button className="button secondary" disabled={!seller} onClick={exportCsv}>Exportar carteira selecionada</button></div></details></div>
    <footer><span>Score na referência histórica: <time dateTime={dataset.asOfDate}>{dateLabel(dataset.asOfDate)}</time></span><span>Calendário das ações: America/Sao_Paulo</span></footer>
    <div className="toast-region" role="status" aria-live="polite" aria-atomic="true">{toast && <div className="toast"><span>{toast.text}</span>{toast.undo && <button onClick={() => undo(toast.undo!.day, toast.undo!.id)}>Desfazer</button>}<button onClick={() => setToast(null)} aria-label="Fechar aviso">×</button></div>}</div>
  </main>;
}


