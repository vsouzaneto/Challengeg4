'use client';

import React, { useState } from 'react';
import {
  SparklesIcon,
  BrainIcon,
  ClockIcon,
  BuildingIcon,
  DollarSignIcon,
  CheckCircleIcon,
  AlertTriangleIcon,
  CloseIcon,
} from './Icons';

interface DealDetailModalProps {
  deal: any;
  onClose: () => void;
  onUpdateDeal: (updatedDeal: any) => void;
}

export default function DealDetailModal({ deal, onClose, onUpdateDeal }: DealDetailModalProps) {
  const [currentDeal, setCurrentDeal] = useState(deal);
  const [aiInsight, setAiInsight] = useState<string | null>(null);
  const [isLoadingAi, setIsLoadingAi] = useState(false);
  const [newAccountInput, setNewAccountInput] = useState('');
  const [showAccountInput, setShowAccountInput] = useState(false);
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);

  // Ação 1: Apontar prospecção hoje
  const handleProspectToday = () => {
    const today = new Date().toISOString().split('T')[0];
    const updated = {
      ...currentDeal,
      engage_date: today,
      stage: currentDeal.stage === 'Prospecting' ? 'Engaging' : currentDeal.stage,
      days_engage: 0,
      relative_age: 0.05,
      action_queue: currentDeal.has_account ? 'Avançar Negociação' : 'Qualificar',
      last_activity: `Prospecção ativa realizada hoje (${today})`,
    };
    setCurrentDeal(updated);
    onUpdateDeal(updated);
    setActionFeedback('✅ Prospecção apontada com sucesso para hoje! Etapa e datas atualizadas.');
    setTimeout(() => setActionFeedback(null), 4000);
  };

  // Ação 2: Atualizar Etapa
  const handleStageChange = (newStage: string) => {
    const updated = {
      ...currentDeal,
      stage: newStage,
      is_active: newStage === 'Prospecting' || newStage === 'Engaging',
      action_queue: newStage === 'Won' || newStage === 'Lost' ? 'Fechado' : currentDeal.action_queue,
    };
    setCurrentDeal(updated);
    onUpdateDeal(updated);
    setActionFeedback(`Status do deal atualizado para "${newStage}".`);
    setTimeout(() => setActionFeedback(null), 3000);
  };

  // Ação 3: Atribuir Conta
  const handleAssignAccount = () => {
    if (!newAccountInput.trim()) return;
    const updated = {
      ...currentDeal,
      account: newAccountInput.trim(),
      has_account: true,
      action_queue: currentDeal.stage === 'Engaging' ? 'Avançar Negociação' : 'Agir Hoje',
      score: Math.min(100, currentDeal.score + 20),
    };
    setCurrentDeal(updated);
    onUpdateDeal(updated);
    setShowAccountInput(false);
    setActionFeedback(`Conta "${newAccountInput}" associada com sucesso! Fila e score recalculados.`);
    setTimeout(() => setActionFeedback(null), 4000);
  };

  // Chamada de IA para análise do Lead
  const handleRequestAiInsight = async () => {
    setIsLoadingAi(true);
    setAiInsight(null);
    try {
      const res = await fetch('/api/ai-research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dealContext: currentDeal,
          mode: 'deal-insight',
        }),
      });
      const data = await res.json();
      if (data?.result) {
        setAiInsight(data.result);
      } else {
        setAiInsight(data?.error || 'Não foi possível gerar análise no momento.');
      }
    } catch (e: any) {
      setAiInsight('Falha na comunicação com o serviço de IA: ' + e?.message);
    } finally {
      setIsLoadingAi(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/75 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="w-full max-w-3xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden my-6 text-slate-800 animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-6 bg-slate-900 text-white flex justify-between items-start">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono px-2 py-0.5 bg-slate-800 text-blue-300 rounded border border-slate-700">
                #{currentDeal.id}
              </span>
              <span
                className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${
                  currentDeal.tier === 'Hot'
                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                    : currentDeal.tier === 'Warm'
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                    : 'bg-slate-700 text-slate-300'
                }`}
              >
                Tier {currentDeal.tier} ({currentDeal.score} pts)
              </span>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/40 font-medium">
                Fila: {currentDeal.action_queue}
              </span>
            </div>
            <h2 className="text-xl font-bold mt-2 text-white flex items-center gap-2">
              {currentDeal.account || (
                <span className="text-amber-400 italic font-normal text-base flex items-center gap-1.5">
                  <AlertTriangleIcon className="w-4 h-4 text-amber-400" />
                  Conta Não Identificada (68,2% dos ativos)
                </span>
              )}
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Produto: <strong className="text-slate-200">{currentDeal.product}</strong> ({currentDeal.series}) · Vendedor: <strong className="text-slate-200">{currentDeal.agent}</strong> · Região: {currentDeal.office}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
          >
            <CloseIcon className="w-5 h-5" />
          </button>
        </div>

        {/* Feedback Alert */}
        {actionFeedback && (
          <div className="bg-emerald-50 border-b border-emerald-200 p-3 text-emerald-800 text-xs font-medium flex items-center gap-2 animate-in fade-in">
            <CheckCircleIcon className="w-4 h-4 text-emerald-600 flex-shrink-0" />
            {actionFeedback}
          </div>
        )}

        {/* Action Bar do Vendedor */}
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <button
              onClick={handleProspectToday}
              className="px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-xl transition shadow-sm flex items-center gap-1.5"
            >
              <ClockIcon className="w-4 h-4" />
              Apontar Prospecção Hoje
            </button>

            {!currentDeal.has_account && !showAccountInput && (
              <button
                onClick={() => setShowAccountInput(true)}
                className="px-3 py-2 bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold rounded-xl transition shadow-sm flex items-center gap-1.5"
              >
                <BuildingIcon className="w-4 h-4" />
                Qualificar / Atribuir Conta
              </button>
            )}
          </div>

          {/* Seletor de Etapa */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 font-medium">Etapa:</span>
            <select
              value={currentDeal.stage}
              onChange={(e) => handleStageChange(e.target.value)}
              className="px-3 py-1.5 text-xs font-semibold bg-white border border-slate-300 rounded-lg text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="Prospecting">Prospecting</option>
              <option value="Engaging">Engaging</option>
              <option value="Won">Won (Ganho)</option>
              <option value="Lost">Lost (Perdido)</option>
            </select>
          </div>
        </div>

        {/* Input Atribuir Conta */}
        {showAccountInput && (
          <div className="p-4 bg-amber-50 border-b border-amber-200 flex items-center gap-2">
            <input
              type="text"
              placeholder="Digite o nome da empresa cliente..."
              value={newAccountInput}
              onChange={(e) => setNewAccountInput(e.target.value)}
              className="flex-1 px-3 py-1.5 text-xs border border-amber-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500 bg-white"
            />
            <button
              onClick={handleAssignAccount}
              className="px-3 py-1.5 bg-emerald-600 text-white text-xs font-semibold rounded-lg hover:bg-emerald-700"
            >
              Salvar Conta
            </button>
            <button
              onClick={() => setShowAccountInput(false)}
              className="px-3 py-1.5 text-slate-600 text-xs hover:bg-slate-200 rounded-lg"
            >
              Cancelar
            </button>
          </div>
        )}

        <div className="p-6 space-y-6 max-h-[60vh] overflow-y-auto">
          {/* Grid de 4 Métricas de Negócio Chave */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-[11px] text-slate-500 font-medium block">1. Valor Referência</span>
              <span className="text-base font-bold text-slate-900">
                ${currentDeal.expected_ref_val?.toLocaleString() || currentDeal.sales_price?.toLocaleString()}
              </span>
              <span className="text-[10px] text-slate-400 block mt-0.5">Ticket médio x Win Rate</span>
            </div>

            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-[11px] text-slate-500 font-medium block">2. Idade Relativa</span>
              <span
                className={`text-base font-bold ${
                  currentDeal.relative_age >= 2.0
                    ? 'text-rose-600'
                    : currentDeal.relative_age >= 1.0
                    ? 'text-amber-600'
                    : 'text-emerald-600'
                }`}
              >
                {currentDeal.relative_age}x ciclo
              </span>
              <span className="text-[10px] text-slate-400 block mt-0.5">
                {currentDeal.days_engage}d (mediana: {currentDeal.median_cycle_days}d)
              </span>
            </div>

            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-[11px] text-slate-500 font-medium block">3. Relacionamento</span>
              <span className="text-sm font-bold text-slate-900 block truncate">
                {currentDeal.relationship?.repurchase_type || 'Novo'}
              </span>
              <span className="text-[10px] text-slate-400 block mt-0.5">
                {currentDeal.relationship?.previous_wins || 0} compras anteriores
              </span>
            </div>

            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-[11px] text-slate-500 font-medium block">4. Preço Catálogo</span>
              <span className="text-base font-bold text-slate-900">
                ${currentDeal.sales_price?.toLocaleString()}
              </span>
              <span className="text-[10px] text-slate-400 block mt-0.5">Base de fechamento</span>
            </div>
          </div>

          {/* Breakdown do Score */}
          <div className="p-4 bg-slate-50/70 rounded-xl border border-slate-200">
            <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
              Composição Explicável do Lead Score ({currentDeal.score}/100)
            </h4>
            <div className="space-y-2.5">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-600">Potencial Financeiro (25%)</span>
                  <span className="font-semibold text-slate-800">{currentDeal.score_breakdown?.value || 50}/100</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-blue-600 h-1.5 rounded-full"
                    style={{ width: `${currentDeal.score_breakdown?.value || 50}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-600">Qualidade da Conta & Setor (20%)</span>
                  <span className="font-semibold text-slate-800">{currentDeal.score_breakdown?.account || 20}/100</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-indigo-600 h-1.5 rounded-full"
                    style={{ width: `${currentDeal.score_breakdown?.account || 20}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-600">Timing & Sweet Spot de Ciclo (25%)</span>
                  <span className="font-semibold text-slate-800">{currentDeal.score_breakdown?.timing || 50}/100</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-amber-600 h-1.5 rounded-full"
                    style={{ width: `${currentDeal.score_breakdown?.timing || 50}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-600">Taxa Histórica do Vendedor (15%)</span>
                  <span className="font-semibold text-slate-800">{currentDeal.score_breakdown?.agent || 63}/100</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-emerald-600 h-1.5 rounded-full"
                    style={{ width: `${currentDeal.score_breakdown?.agent || 63}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-600">Força do Relacionamento / Recompra (15%)</span>
                  <span className="font-semibold text-slate-800">{currentDeal.score_breakdown?.relationship || 20}/100</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-purple-600 h-1.5 rounded-full"
                    style={{ width: `${currentDeal.score_breakdown?.relationship || 20}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Análise de IA do Lead */}
          <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <BrainIcon className="w-5 h-5 text-blue-600" />
                <h4 className="text-xs font-bold text-blue-900 uppercase tracking-wider">
                  Copiloto de IA — Orientação Tática do Lead
                </h4>
              </div>
              <button
                onClick={handleRequestAiInsight}
                disabled={isLoadingAi}
                className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg transition flex items-center gap-1.5 disabled:opacity-50"
              >
                <SparklesIcon className="w-3.5 h-3.5" />
                {isLoadingAi ? 'Analisando com Gemini...' : 'Gerar Roteiro de Abordagem'}
              </button>
            </div>

            {aiInsight ? (
              <div className="mt-3 p-3 bg-white rounded-lg border border-blue-100 text-xs text-slate-700 whitespace-pre-line leading-relaxed">
                {aiInsight}
              </div>
            ) : (
              <p className="text-xs text-blue-700/80 mt-1">
                Clique no botão acima para o Gemini avaliar o perfil deste lead, antecipar objeções e sugerir a ação mais rápida para fechamento.
              </p>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-50 border-t border-slate-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold rounded-xl transition"
          >
            Fechar Janela
          </button>
        </div>
      </div>
    </div>
  );
}
