export default function Loading() {
  return (
    <div
      className="panel loading-layout"
      role="status"
      aria-label="Carregando conteúdo"
    >
      <div className="skeleton" />
      <div className="skeleton" style={{ width: "40%" }} />
      <div className="skeleton large" />
      <p className="small-copy muted">Carregando a análise…</p>
    </div>
  );
}
