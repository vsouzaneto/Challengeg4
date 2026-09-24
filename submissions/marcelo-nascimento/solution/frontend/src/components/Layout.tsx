import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.js";

const navigation = [
  { to: "/dashboard", label: "Dashboard", icon: "fa-gauge-high" },
  { to: "/leads", label: "Listagem", icon: "fa-list" },
  { to: "/reports", label: "Relatórios", icon: "fa-chart-line" },
  { to: "/users", label: "Usuários", icon: "fa-users" },
];

const pageTitles: Record<string, { title: string; subtitle: string }> = {
  "/dashboard": { title: "Dashboard", subtitle: "Priorize as oportunidades com maior aderência." },
  "/leads": { title: "Oportunidades", subtitle: "Pesquise, filtre eCompare o pipeline comercial." },
  "/reports": { title: "Relatórios", subtitle: "Analise a distribuição dos scores e o funil." },
  "/users": { title: "Usuários", subtitle: "Gerencie os acessos à aplicação." },
};

export default function Layout() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);
  const [logoutError, setLogoutError] = useState("");
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const page = location.pathname.startsWith("/leads/")
    ? { title: "Detalhe da oportunidade", subtitle: "Revise o score e suas evidências." }
    : pageTitles[location.pathname] ?? pageTitles["/dashboard"];

  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  async function handleLogout(): Promise<void> {
    setLoggingOut(true);
    setLogoutError("");
    try {
      await logout();
      navigate("/login", { replace: true });
    } catch (logoutRequestError) {
      setLogoutError(logoutRequestError instanceof Error ? logoutRequestError.message : "Não foi possível encerrar a sessão.");
    } finally {
      setLoggingOut(false);
    }
  }

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">Ir para o conteúdo</a>
      {menuOpen ? <button className="sidebar-overlay" aria-label="Fechar menu" onClick={() => setMenuOpen(false)} /> : null}
      <aside id="application-sidebar" className={`sidebar ${menuOpen ? "sidebar-open" : ""}`} onKeyDown={(event) => {
        if (event.key === "Escape") {
          setMenuOpen(false);
        }
      }}>
        <div className="brand">
          <span className="brand-mark"><i className="fa-solid fa-crosshairs" aria-hidden="true" /></span>
          <div><strong>Lead Scorer</strong><small>Inteligência comercial</small></div>
        </div>
        <nav className="sidebar-nav" aria-label="Navegação principal">
          {navigation.map((item) => (
            <NavLink key={item.to} to={item.to} onClick={() => setMenuOpen(false)}>
              <i className={`fa-solid ${item.icon}`} aria-hidden="true" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-user">
          <span className="user-avatar">{user?.name.charAt(0).toUpperCase()}</span>
          <div><strong>{user?.name}</strong><small>{user?.email}</small></div>
          <button type="button" className="icon-button" onClick={() => void handleLogout()} aria-label="Sair" title="Sair" disabled={loggingOut}>
            {loggingOut ? <span className="spinner-border spinner-border-sm" aria-hidden="true" /> : <i className="fa-solid fa-arrow-right-from-bracket" aria-hidden="true" />}
          </button>
        </div>
      </aside>
      <div className="app-main">
        <header className="topbar">
          <button className="menu-button" type="button" onClick={() => setMenuOpen(true)} aria-label="Abrir menu" aria-controls="application-sidebar" aria-expanded={menuOpen}>
            <i className="fa-solid fa-bars" aria-hidden="true" />
          </button>
          <div>
            <h1>{page?.title}</h1>
            <p>{page?.subtitle}</p>
          </div>
          <span className="topbar-badge"><i className="fa-solid fa-shield-halved" aria-hidden="true" /> Backend auditável</span>
        </header>
        <main id="main-content" className="content">
          {logoutError ? <div className="alert alert-danger" role="alert">{logoutError}</div> : null}
          <Outlet />
        </main>
      </div>
    </div>
  );
}
