"use client";
import { Icon } from "@/components/icons";

export default function ErrorPage({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="panel empty-state" role="alert">
      <span className="empty-icon">
        <Icon name="alert" />
      </span>
      <h1 style={{ fontSize: 26 }}>Não foi possível carregar esta página.</h1>
      <p style={{ margin: "14px 0 24px" }}>
        A análise pode estar sendo atualizada. Tente carregar o conteúdo
        novamente.
      </p>
      <button className="button" onClick={() => reset()}>
        <Icon name="refresh" width={16} />
        Tentar novamente
      </button>
    </div>
  );
}
