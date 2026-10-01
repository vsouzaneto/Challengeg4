import { completedCount, statusOf, type DayState } from '../domain/missions/queue';
import { Icon } from './Icon';
export function DailyProgress({ day }: { day: DayState }) {
  const done = day.batch.filter((id) => statusOf(day, id) === 'completed').length;
  return <section className="progress-section" aria-label="Progresso da rotina">
    <div className="progress-caption"><span>Lote {day.batchNumber || 1} · {done}/{day.batch.length} concluídas</span><span>Meta diária: {completedCount(day)}/{day.goal} ações</span></div>
    <div className="segments">{day.batch.map((id, i) => {
      const status = statusOf(day, id), selected = day.active === id;
      const label = status === 'completed' ? 'concluída' : status === 'deferred' ? 'adiada' : selected ? 'selecionada, pendente' : 'pendente';
      return <span key={id} className={`segment ${status} ${selected ? 'selected' : ''}`} aria-label={`Missão ${i + 1}: ${label}`} title={`Missão ${i + 1}: ${label}`}>{status === 'completed' ? <Icon name="check" size={14} /> : status === 'deferred' ? <Icon name="clock" size={14} /> : selected ? <span className="selected-dot" /> : null}</span>;
    })}</div>
    <div className="progress-legend"><span><i className="legend-blue" />Concluída</span><span><i className="legend-orange" />Selecionada</span><span><i className="legend-gray" />Pendente</span><span><Icon name="clock" size={13} />Adiada</span></div>
  </section>;
}
