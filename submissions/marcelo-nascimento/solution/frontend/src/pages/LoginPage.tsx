import { useState, type FormEvent } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.js";

export default function LoginPage() {
  const { user, login } = useAuth();
  const [email, setEmail] = useState("admin@leadscore.local");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(email, password);
      const destination = (location.state as { from?: string } | null)?.from ?? "/dashboard";
      navigate(destination, { replace: true });
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Não foi possível entrar.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-visual" aria-label="Apresentação do Lead Scorer">
        <div className="login-brand"><i className="fa-solid fa-crosshairs" aria-hidden="true" /> Lead Scorer</div>
        <div className="login-message">
          <span className="eyebrow">Prioridade comercial com contexto</span>
          <h1>Encontre onde focar agora.</h1>
          <p>Scores determinísticos, fatores auditáveis e justificativas que explicam cada prioridade.</p>
        </div>
        <div className="login-feature"><i className="fa-solid fa-layer-group" aria-hidden="true" /><span><strong>Quatro fatores</strong><small>Contribuições separadas e rastreáveis</small></span></div>
        <div className="login-feature"><i className="fa-solid fa-chart-pie" aria-hidden="true" /><span><strong>Pipeline visual</strong><small>Prioridade orientada por evidências</small></span></div>
      </section>
      <section className="login-panel">
        <form className="login-card" onSubmit={(event) => void handleSubmit(event)}>
          <span className="login-icon"><i className="fa-solid fa-right-to-bracket" aria-hidden="true" /></span>
          <h2>Acesse sua conta</h2>
          <p>Use suas credenciais para visualizar o pipeline.</p>
          {error ? <div className="alert alert-danger" role="alert"><i className="fa-solid fa-circle-exclamation" aria-hidden="true" /> {error}</div> : null}
          <label htmlFor="email">E-mail</label>
          <div className="input-shell">
            <i className="fa-regular fa-envelope" aria-hidden="true" />
            <input id="email" type="email" autoComplete="username" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </div>
          <label htmlFor="password">Senha</label>
          <div className="input-shell">
            <i className="fa-solid fa-lock" aria-hidden="true" />
            <input id="password" type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} required />
          </div>
          <button className="btn btn-primary w-100 login-submit" type="submit" disabled={submitting}>
            {submitting ? <><span className="spinner-border spinner-border-sm" aria-hidden="true" /> Entrando...</> : <>Entrar <i className="fa-solid fa-arrow-right" aria-hidden="true" /></>}
          </button>
          <small className="login-security"><i className="fa-solid fa-shield-halved" aria-hidden="true" /> Acesso protegido e sem papéis diferenciados.</small>
        </form>
      </section>
    </main>
  );
}
