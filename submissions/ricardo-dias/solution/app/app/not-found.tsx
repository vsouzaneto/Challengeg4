import Link from "next/link";
export default function NotFound() {
  return (
    <div className="panel empty-state">
      <p className="eyebrow">Página não encontrada</p>
      <h1 style={{ fontSize: 28 }}>Vamos voltar ao diagnóstico?</h1>
      <p style={{ margin: "14px 0 24px" }}>
        Este endereço não faz parte da ferramenta.
      </p>
      <Link href="/" className="button">
        Abrir diagnóstico
      </Link>
    </div>
  );
}
