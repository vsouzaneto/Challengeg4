export function EmptyDailyQueue() {
  return (
    <section aria-labelledby="queue-title" className="mission-shell">
      <span className="eyebrow">Seu próximo passo</span>
      <h2 id="queue-title">Uma boa rotina começa com prioridades claras.</h2>
      <p>Escolha seu nome no seletor de carteira para receber as prioridades do dia.</p>
      <div className="routine" aria-label="Como funciona sua rotina">
        <div><span className="step">01</span><h3>Escolha sua carteira</h3><p>Receba até dez oportunidades por vez.</p></div>
        <div><span className="step">02</span><h3>Entenda a prioridade</h3><p>Veja os motivos e a próxima ação.</p></div>
        <div><span className="step">03</span><h3>Avance na rotina</h3><p>Conclua uma ação ou adie para amanhã.</p></div>
      </div>
    </section>
  );
}
