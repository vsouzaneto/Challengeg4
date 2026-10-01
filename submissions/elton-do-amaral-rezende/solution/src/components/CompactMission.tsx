import type { RankedOpportunity } from '../domain/types';
import { Icon } from './Icon';
import { usd } from './MissionCard';
export function CompactMission({ opportunity: o, position, onSelect }: { opportunity: RankedOpportunity; position: number; onSelect: () => void }) {
  return <button className="compact-mission" data-opportunity-id={o.opportunityId} onClick={onSelect} aria-label={`Abrir missão ${position}: ${o.account ?? 'Conta não informada'}, ${o.product}, prioridade ${o.priorityScore}`} aria-expanded={false}>
    <span className="position">{position}</span><span className="compact-company"><strong>{o.account ?? `Oportunidade #${o.opportunityId}`}</strong><span>{o.product}</span></span>
    <span className="compact-reason">{o.stage === 'Prospecting' ? 'Qualificar necessidade' : 'Confirmar situação atual'}{!o.account ? ' · conta não informada' : ''}</span>
    <span className="compact-value">{o.catalogPriceUsd === null ? '—' : usd(o.catalogPriceUsd)}<small>catálogo</small></span><span className="compact-score" title="Score de prioridade">{o.priorityScore}</span><span className="expand-icon"><Icon name="arrow" /></span>
  </button>;
}
