import type { Conta, InvestigacaoConta } from "../types";

type Props = {
  conta: Conta | null;
  investigacao: InvestigacaoConta | null;
  onClose: () => void;
};

function fmtUsd(n: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);
}

export function AccountDrawer({ conta, investigacao, onClose }: Props) {
  if (!conta) return null;
  const contaId = conta.conta_id;

  async function copyId() {
    try {
      await navigator.clipboard.writeText(contaId);
    } catch {
      /* ignore */
    }
  }

  return (
    <div className="drawer-backdrop" role="presentation" onClick={onClose}>
      <aside
        className="drawer-panel"
        role="dialog"
        aria-label="Investigação da conta"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="drawer-head">
          <div>
            <h3>{conta.nome_conta}</h3>
            <button type="button" className="link-btn" onClick={copyId}>
              {conta.conta_id} · copiar ID
            </button>
          </div>
          <button type="button" className="drawer-close" onClick={onClose} aria-label="Fechar">
            ×
          </button>
        </header>

        <div className="drawer-body">
          <p>
            <strong>{conta.industria}</strong> · {conta.status_conta} · MRR {fmtUsd(conta.mrr_usd)}
          </p>
          {conta.motivo_risco && (
            <p className="drawer-muted">
              <strong>Risco:</strong> {conta.motivo_risco}
            </p>
          )}

          {investigacao?.alertas?.length ? (
            <ul className="drawer-alerts">
              {investigacao.alertas.map((a) => (
                <li key={a}>{a}</li>
              ))}
            </ul>
          ) : null}

          <h4>Eventos de churn</h4>
          {investigacao?.eventos_churn?.length ? (
            <ul className="drawer-list">
              {investigacao.eventos_churn.map((e) => (
                <li key={`${e.data}-${e.motivo}`}>
                  {e.data} — {e.motivo}
                  {e.reativacao ? " (reativação)" : ""}
                </li>
              ))}
            </ul>
          ) : (
            <p className="drawer-muted">Nenhum evento registrado.</p>
          )}

          <h4>Uso mensal (últimos meses)</h4>
          {investigacao?.uso_mensal?.length ? (
            <ul className="drawer-list compact">
              {investigacao.uso_mensal.map((u) => (
                <li key={u.mes}>
                  {u.mes}: {u.total.toLocaleString()} usos
                </li>
              ))}
            </ul>
          ) : (
            <p className="drawer-muted">Sem telemetria agregada.</p>
          )}

          <h4>Suporte</h4>
          {investigacao?.suporte ? (
            <p className="drawer-muted">
              {investigacao.suporte.tickets} tickets · escalacao{" "}
              {investigacao.suporte.taxa_escalacao_pct}%
              {investigacao.suporte.csat_medio != null
                ? ` · CSAT ${investigacao.suporte.csat_medio}`
                : ""}
            </p>
          ) : null}
        </div>
      </aside>
    </div>
  );
}
