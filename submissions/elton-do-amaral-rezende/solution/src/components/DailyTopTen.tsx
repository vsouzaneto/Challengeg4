import { opportunityById } from '../data/dataset';
import { statusOf, type DayState } from '../domain/missions/queue';
import { MissionCard } from './MissionCard';
import { CompactMission } from './CompactMission';
export function DailyTopTen({ day, onSelect, onResolve, onCopy }: { day: DayState; onSelect: (id: string) => void; onResolve: (id: string, status: 'completed' | 'deferred') => void; onCopy: (id: string) => void }) {
  const activePosition = day.active ? day.batch.indexOf(day.active) : -1;
  return <section className="daily-missions" aria-label="Missões do lote">
    {day.batch.map((id, index) => {
      if (statusOf(day, id) !== 'pending') return null;
      const opportunity = opportunityById.get(id); if (!opportunity) return null;
      return <div key={id} className={index < activePosition ? 'mission-above' : index > activePosition ? 'mission-below' : 'mission-current'}>{id === day.active
        ? <MissionCard opportunity={opportunity} position={index + 1} onComplete={() => onResolve(id, 'completed')} onDefer={() => onResolve(id, 'deferred')} onCopy={() => onCopy(id)} />
        : <CompactMission opportunity={opportunity} position={index + 1} onSelect={() => onSelect(id)} />}</div>;
    })}
  </section>;
}
