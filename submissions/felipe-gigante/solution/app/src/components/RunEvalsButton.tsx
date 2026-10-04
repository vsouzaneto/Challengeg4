"use client";
import { useTransition } from "react";
import { Play } from "lucide-react";
import { runEvalsAction } from "@/app/(app)/evals/actions";
export function RunEvalsButton() {
  const [pending, start] = useTransition();
  return <button disabled={pending} onClick={() => start(() => runEvalsAction())} className="btn btn-gold"><Play size={14} />{pending ? "Rodando 538 casos…" : "Rodar evals agora"}</button>;
}
