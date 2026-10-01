import { useEffect, useRef } from 'react';
import type { RankedOpportunity } from '../domain/types';
import { Icon } from './Icon';
export const usd = (value: number) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);
const factorLabels = { history: 'Histórico de vendas', engagementAge: 'Tempo desde o engajamento', catalogValue: 'Preço de catálogo' };
export function MissionCard({ opportunity: o, position, onComplete, onDefer, onCopy }: { opportunity: RankedOpportunity; position: number; onComplete: () => void; onDefer: () => void; onCopy: () => void }) {
  const titleRef = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    titleRef.current?.focus({ preventScroll: true });
    const rect = titleRef.current?.getBoundingClientRect();
    if (rect && (rect.top < 0 || rect.bottom > window.innerHeight)) titleRef.current?.scrollIntoView({ block: 'center', behavior: window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  }, [o.opportunityId]);
  return <article className="mission-card" data-opportunity-id={o.opportunityId} aria-labelledby={`mission-${o.opportunityId}`} data-testid="expanded-mission">
    <div className="mission-top"><div>
      <span className="eyebrow"><Icon name="target" size={17} />Agora · missão {position}</span>
      <h2 id={`mission-${o.opportunityId}`} ref={titleRef} tabIndex={-1}>{o.account ?? 'Conta não informada'}</h2>
      <p className="mission-meta">{o.product}<span>·</span>{o.stage === 'Prospecting' ? 'Prospecção' : 'Em engajamento'}<span>·</span><span className="id-label">#{o.opportunityId}</span></p>
      <p className="catalog-label">Preço de catálogo: <strong>{o.catalogPriceUsd === null ? 'não informado' : usd(o.catalogPriceUsd)}</strong></p>
    </div><div className="score-box"><div className="score-ring" style={{ '--score': `${o.priorityScore}%` } as React.CSSProperties}><span>{o.priorityScore}</span></div><span>prioridade / 100</span></div></div>
    <section className="why-panel" aria-label="Contribuições ao score">
      <h3>Por que está nesta posição</h3>
      {o.factors.map((f) => <div key={f.key} className="factor-row"><span>{factorLabels[f.key]}</span><div className="factor-track"><span style={{ width: `${f.contributionPoints}%` }} /></div><strong>{f.contributionPoints.toFixed(1).replace('.', ',')} pts</strong></div>)}
      <p className="factor-note">As barras mostram quantos pontos cada critério soma à prioridade. Essa pontuação não é a chance de fechar a venda.</p>
      <details className="calculation"><summary>Entender esta prioridade</summary>{o.factors.map((f) => <p key={f.key}><strong>{factorLabels[f.key]}.</strong> {f.explanation}{f.fallback && <span className="fallback"> {f.fallback}</span>}</p>)}<p>Prioridade total: {o.priorityScore} de 100 pontos. Dados analisados até {o.asOfDate.split('-').reverse().join('/')}.</p></details>
    </section>
    {o.missingData.length > 0 && <p className="data-warning"><Icon name="info" size={17} /><span>{o.missingData.join(' · ')}</span></p>}
    <div className="next-action"><span className="action-label">Próxima ação</span><p>{o.nextAction}</p></div>
    <div className="mission-actions"><button className="button orange" onClick={onCopy}><Icon name="copy" />Copiar orientação</button><button className="button success" onClick={onComplete}><Icon name="check" />Feito</button><button className="button quiet" onClick={onDefer}><Icon name="clock" />Adiar para amanhã</button></div>
    <p className="manual-note">Feito registra a ação que você realizou. Não muda o estágio da oportunidade.</p>
  </article>;
}
