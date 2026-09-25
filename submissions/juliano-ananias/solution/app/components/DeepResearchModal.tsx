'use client';

import React from 'react';
import { BrainIcon, SparklesIcon, CloseIcon, CheckCircleIcon } from './Icons';

interface DeepResearchModalProps {
  sliceData: any;
  aiReport: string | null;
  isLoading: boolean;
  onClose: () => void;
  onRefresh: () => void;
}

export default function DeepResearchModal({
  sliceData,
  aiReport,
  isLoading,
  onClose,
  onRefresh,
}: DeepResearchModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-md p-4 overflow-y-auto">
      <div className="w-full max-w-4xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden my-6 text-slate-800 animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-6 bg-gradient-to-r from-slate-950 via-slate-900 to-indigo-950 text-white flex justify-between items-start">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-500/20 text-indigo-300 rounded-full text-xs font-semibold border border-indigo-500/40 mb-2">
              <SparklesIcon className="w-4 h-4" />
              G4 DeepResearch™ Engine (Gemini 2.5)
            </div>
            <h2 className="text-xl font-bold text-white">
              Relatório Executivo & Análise Estratégica do Slice
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Recorte selecionado: {sliceData?.total_filtered} oportunidades · Potencial em Pipeline: $
              {sliceData?.total_pipeline_val?.toLocaleString()}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
          >
            <CloseIcon className="w-5 h-5" />
          </button>
        </div>

        {/* Resumo do Recorte */}
        <div className="p-4 bg-slate-50 border-b border-slate-200 grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          <div className="p-2.5 bg-white rounded-lg border border-slate-200">
            <span className="text-slate-500 block">Deals no Recorte</span>
            <span className="text-base font-bold text-slate-900">{sliceData?.total_filtered}</span>
          </div>
          <div className="p-2.5 bg-white rounded-lg border border-slate-200">
            <span className="text-slate-500 block">Win Rate Histórico</span>
            <span className="text-base font-bold text-indigo-600">
              {sliceData?.avg_win_rate ? (sliceData.avg_win_rate * 100).toFixed(1) + '%' : '63.2%'}
            </span>
          </div>
          <div className="p-2.5 bg-white rounded-lg border border-slate-200">
            <span className="text-slate-500 block">Ticket Médio Estimado</span>
            <span className="text-base font-bold text-slate-900">
              ${sliceData?.avg_ticket?.toLocaleString() || '2,360'}
            </span>
          </div>
          <div className="p-2.5 bg-white rounded-lg border border-slate-200">
            <span className="text-slate-500 block">Deals &gt; 2x Ciclo Mediano</span>
            <span className="text-base font-bold text-rose-600">
              {sliceData?.over_cycle_count || 0} em revisão
            </span>
          </div>
        </div>

        {/* Conteúdo do Relatório */}
        <div className="p-6 max-h-[60vh] overflow-y-auto">
          {isLoading ? (
            <div className="py-16 text-center">
              <div className="inline-block animate-spin rounded-full h-9 w-9 border-4 border-indigo-600 border-t-transparent mb-3" />
              <p className="text-sm font-semibold text-slate-800">
                A IA está cruzando dimensões, calculando ofensores e gerando o parecer de RevOps...
              </p>
              <p className="text-xs text-slate-400 mt-1">Conectando ao modelo Gemini 2.5 Flash</p>
            </div>
          ) : aiReport ? (
            <div className="prose prose-sm max-w-none text-slate-700 leading-relaxed whitespace-pre-line bg-slate-50/50 p-6 rounded-2xl border border-slate-200">
              {aiReport}
            </div>
          ) : (
            <div className="text-center py-10">
              <BrainIcon className="w-10 h-10 text-slate-400 mx-auto mb-2" />
              <p className="text-sm text-slate-600 font-medium">Nenhum relatório gerado ainda.</p>
              <button
                onClick={onRefresh}
                className="mt-3 px-4 py-2 bg-indigo-600 text-white text-xs font-semibold rounded-xl hover:bg-indigo-700 transition"
              >
                Gerar Análise Agora
              </button>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-50 border-t border-slate-200 flex justify-between items-center">
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="px-4 py-2 text-xs font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 rounded-xl transition flex items-center gap-1.5 disabled:opacity-50"
          >
            <SparklesIcon className="w-4 h-4" />
            Recalcular com Novos Filtros
          </button>

          <button
            onClick={onClose}
            className="px-5 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-xl transition shadow-sm"
          >
            Concluir & Voltar ao Pipeline
          </button>
        </div>
      </div>
    </div>
  );
}
