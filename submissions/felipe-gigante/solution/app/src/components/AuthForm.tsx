"use client";
import Link from "next/link";
import { useActionState } from "react";
import type { AuthState } from "@/app/(auth)/actions";

export function AuthForm({ mode, action }: { mode: "login" | "signup"; action: (s: AuthState, f: FormData) => Promise<AuthState> }) {
  const [state, formAction, pending] = useActionState(action, undefined);
  const login = mode === "login";
  return (
    <form action={formAction} className="space-y-4">
      <div>
        <h2 className="h-display text-2xl font-extrabold text-navy">{login ? "Entrar" : "Criar conta"}</h2>
        <p className="mt-1 text-sm text-muted">{login ? "Acesse o console de operação do suporte." : "Cadastre-se como agente, gestor ou knowledge manager."}</p>
      </div>
      {!login && (
        <div><label className="label" htmlFor="name">Nome</label><input id="name" name="name" className="input" required autoComplete="name" /></div>
      )}
      <div><label className="label" htmlFor="email">E-mail</label><input id="email" name="email" type="email" className="input" required autoComplete="email" defaultValue={login ? "demo@g4.com.br" : ""} /></div>
      <div><label className="label" htmlFor="password">Senha</label><input id="password" name="password" type="password" className="input" required autoComplete={login ? "current-password" : "new-password"} defaultValue={login ? "g4demo2026" : ""} /></div>
      {!login && (
        <div>
          <label className="label" htmlFor="role">Perfil</label>
          <select id="role" name="role" className="input" defaultValue="agent">
            <option value="agent">Agente de suporte</option>
            <option value="manager">Gestor de suporte</option>
            <option value="knowledge">Knowledge Manager</option>
          </select>
        </div>
      )}
      {state?.error && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{state.error}</p>}
      <button className="btn btn-gold w-full" disabled={pending}>{pending ? "Aguarde…" : login ? "Entrar" : "Criar conta"}</button>
      {login && <p className="rounded-lg bg-gold-100 px-3 py-2 text-xs text-navy">Acesso demo já preenchido: <b>demo@g4.com.br</b> / <b>g4demo2026</b></p>}
      <p className="text-center text-sm text-muted">
        {login ? <>Não tem conta? <Link href="/signup" className="font-semibold text-gold hover:underline">Cadastre-se</Link></> : <>Já tem conta? <Link href="/login" className="font-semibold text-gold hover:underline">Entrar</Link></>}
      </p>
    </form>
  );
}
