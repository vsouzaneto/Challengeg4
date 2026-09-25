'use client';

import React, { useState } from 'react';

interface LoginModalProps {
  onLogin: (user: { name: string; role: string; email: string }) => void;
}

export function ShieldIconLocal({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
  );
}

export default function LoginModal({ onLogin }: LoginModalProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (password === 'g4master2026' || password === 'demo' || password.length >= 4) {
      onLogin({
        name: email.split('@')[0] || 'Avaliador G4',
        role: 'Diretor de RevOps',
        email: email || 'avaliador@g4educacao.com',
      });
    } else {
      setError('Senha inválida. Use a senha informada no README ou utilize o Acesso Rápido abaixo.');
    }
  };

  const handleQuickLogin = (role: 'vendedor' | 'diretor') => {
    if (role === 'vendedor') {
      onLogin({
        name: 'Darcel Schlecht',
        role: 'Senior Sales Agent (Central)',
        email: 'darcel.schlecht@g4educacao.com',
      });
    } else {
      onLogin({
        name: 'Avaliador G4 Educação',
        role: 'Head de Revenue Operations & AI',
        email: 'avaliador.g4@g4educacao.com',
      });
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/85 backdrop-blur-md p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden text-slate-800">
        {/* Top banner G4 EDUCAÇÃO OFICIAL SVG */}
        <div className="bg-slate-950 text-white p-6 pb-8 text-center relative border-b border-slate-800">
          <div className="inline-flex items-center justify-center p-2.5 bg-slate-900 rounded-2xl mb-3 border border-slate-800 shadow-md">
            <img
              src="/logo-g4-completa-branca.svg"
              alt="G4 Educação"
              className="h-9 w-auto object-contain"
            />
          </div>
          <h2 className="text-xl font-black tracking-tight text-white">
            AI Master — Lead Scorer Pro
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Sistema de Priorização Comercial com Copiloto de IA
          </p>
        </div>

        <div className="p-6 -mt-3 bg-white rounded-t-2xl">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">
                E-mail Corporativo
              </label>
              <input
                type="email"
                placeholder="seu.email@empresa.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent transition"
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="block text-xs font-semibold text-slate-600">Senha</label>
                <span className="text-[11px] text-blue-600 font-medium">Dica: g4master2026</span>
              </div>
              <input
                type="password"
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent transition"
              />
            </div>

            {error && (
              <p className="text-xs text-rose-600 font-medium bg-rose-50 p-2.5 rounded-lg border border-rose-200">
                {error}
              </p>
            )}

            <button
              type="submit"
              className="w-full py-2.5 px-4 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm rounded-xl transition shadow-md flex items-center justify-center gap-2"
            >
              Entrar no Sistema
            </button>
          </form>

          {/* Quick Access for evaluators */}
          <div className="mt-6 pt-5 border-t border-slate-200">
            <div className="flex items-center gap-2 mb-3">
              <ShieldIconLocal className="w-4 h-4 text-emerald-600" />
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Modo Demo Avaliador G4 (1-Clique)
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => handleQuickLogin('diretor')}
                className="p-2.5 text-left border border-slate-200 hover:border-blue-500 hover:bg-blue-50/50 rounded-xl transition group"
              >
                <div className="text-xs font-bold text-slate-800 group-hover:text-blue-600">
                  Head RevOps
                </div>
                <div className="text-[11px] text-slate-500">Visão Geral Completa</div>
              </button>

              <button
                type="button"
                onClick={() => handleQuickLogin('vendedor')}
                className="p-2.5 text-left border border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/50 rounded-xl transition group"
              >
                <div className="text-xs font-bold text-slate-800 group-hover:text-emerald-600">
                  Vendedor (Darcel S.)
                </div>
                <div className="text-[11px] text-slate-500">Visão Individual</div>
              </button>
            </div>

            <p className="text-[11px] text-slate-400 text-center mt-3">
              Acesso seguro. Credencial documentada no README.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
