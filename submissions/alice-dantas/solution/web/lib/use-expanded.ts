// As linhas da lista com a análise aberta: várias ao mesmo tempo, para comparar uma com a de baixo.
import { useCallback, useState } from "react";

export function useExpanded() {
  const [expanded, setExpanded] = useState<string[]>([]);
  const [reveal, setReveal] = useState<{ id: string } | null>(null);
  const toggle = useCallback((id: string) => {
    setExpanded((current) => (current.includes(id) ? current.filter((other) => other !== id) : [...current, id]));
  }, []);
  /** Abre a análise de uma oportunidade que o vendedor escolheu fora da lista (o cartão do topo). */
  const open = useCallback((id: string) => {
    setExpanded((current) => (current.includes(id) ? current : [...current, id]));
    setReveal({ id });
  }, []);
  const close = useCallback((id: string) => setExpanded((current) => current.filter((other) => other !== id)), []);
  const reset = useCallback(() => {
    setExpanded([]);
    setReveal(null);
  }, []);
  return { expanded, reveal, toggle, open, close, reset };
}
