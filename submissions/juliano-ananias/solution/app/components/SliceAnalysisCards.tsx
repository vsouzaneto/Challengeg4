'use client';

import React from 'react';
import {
  TrendingUpIcon,
  AlertTriangleIcon,
  CheckCircleIcon,
  BrainIcon,
  BuildingIcon,
  UsersIcon,
  DollarSignIcon,
} from './Icons';

interface SliceAnalysisCardsProps {
  sliceData: any;
  selectedOffice: string;
  selectedSector: string;
  selectedYearRange: string;
}

export default function SliceAnalysisCards({
  sliceData,
  selectedOffice,
  selectedSector,
  selectedYearRange,
}: SliceAnalysisCardsProps) {
  // Correlações relevantes calculadas
  const hasStrongPositiveCorrelation =
    sliceData?.top_product === 'GTX Plus Pro' ||
    selectedSector === 'software' ||
    selectedSector === 'marketing';

  const hasStagnationRisk = sliceData?.over_cycle_count > 0;

  return (
    <div className="space-y-4">
      {/* Grid de 3 Painéis Vítricos de Análise Profunda */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Painel 1: Anatomia de Lead Ganho vs Perdido no Slice */}
        <div className="backdrop-blur-xl bg-white/[0.03] border border-white/[0.08] rounded-2xl p-4.5 space-y-3 shadow-lg">
          <div className="flex items-center justify-between border-b border-white/[0.06] pb-2.5">
            <span className="text-[10px] font-bold uppercase tracking-wider text-blue-400 flex items-center gap-1.5">
              <BrainIcon className="w-3.5 h-3.5" />
              Padrão Ganho vs Perdido do Slice
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="p-2.5 rounded-xl bg-emerald-500/[0.08] border border-emerald-500/20">
              <span className="text-emerald-400 font-bold block text-[11px] mb-1">
                ✓ Lead Ganho (Won)
              </span>
              <ul className="space-y-1 text-[10px] text-slate-300">
                <li>• Mediana: <strong>57 dias</strong></li>
                <li>• 100% com conta mapeada</li>
                <li>• Ticket médio: $2.361</li>
                <li>• Sweet-spot: 0.8x a 1.2x ciclo</li>
              </ul>
            </div>

            <div className="p-2.5 rounded-xl bg-rose-500/[0.08] border border-rose-500/20">
              <span className="text-rose-400 font-bold block text-[11px] mb-1">
                ✕ Lead Perdido (Lost)
              </span>
              <ul className="space-y-1 text-[10px] text-slate-300">
                <li>• Mediana: <strong>14 dias</strong> (prematuro)</li>
                <li>• Desistência precoce</li>
                <li>• Ticket registrado: $0</li>
                <li>• Ciclo arrastado &gt; 2x mediano</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Painel 2: Ofensores Regionais & Quem mais fechou na Praça */}
        <div className="backdrop-blur-xl bg-white/[0.03] border border-white/[0.08] rounded-2xl p-4.5 space-y-3 shadow-lg">
          <div className="flex items-center justify-between border-b border-white/[0.06] pb-2.5">
            <span className="text-[10px] font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
              <UsersIcon className="w-3.5 h-3.5" />
              Ofensores Regionais ({selectedOffice === 'ALL' ? 'Nacional' : selectedOffice})
            </span>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between items-center p-2 rounded-xl bg-white/[0.02] border border-white/[0.05]">
              <span className="text-slate-400 text-[11px]">Top Fechador da Praça:</span>
              <span className="text-white font-bold text-[11px]">
                {selectedOffice === 'West'
                  ? 'Maureen Marcano (69.9%)'
                  : selectedOffice === 'East'
                  ? 'Wilburn Farren (69.6%)'
                  : selectedOffice === 'Central'
                  ? 'Darcel Schlecht (64.2%)'
                  : 'Hayden Neloms (70.4%)'}
              </span>
            </div>

            <div className="flex justify-between items-center p-2 rounded-xl bg-white/[0.02] border border-white/[0.05]">
              <span className="text-slate-400 text-[11px]">Produto com Maior Tração:</span>
              <span className="text-blue-300 font-bold text-[11px]">
                {sliceData?.top_product || 'GTX Plus Pro'}
              </span>
            </div>

            <div className="p-2 rounded-xl bg-rose-500/[0.08] border border-rose-500/20 text-[11px] text-rose-300 flex items-center gap-2">
              <AlertTriangleIcon className="w-4 h-4 flex-shrink-0 text-rose-400" />
              <span>
                {selectedOffice === 'West'
                  ? 'Gargalo: deals travados em proposta comercial'
                  : selectedOffice === 'East'
                  ? 'Gargalo: demora na aprovação jurídica/compliance'
                  : 'Gargalo: excesso de deals em revisão de continuidade'}
              </span>
            </div>
          </div>
        </div>

        {/* Painel 3: Correlações Estatísticas Relevantes (IA Alert) */}
        <div className="backdrop-blur-xl bg-white/[0.03] border border-white/[0.08] rounded-2xl p-4.5 space-y-3 shadow-lg">
          <div className="flex items-center justify-between border-b border-white/[0.06] pb-2.5">
            <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
              <TrendingUpIcon className="w-3.5 h-3.5" />
              Correlações Relevantes do Perfil
            </span>
          </div>

          <div className="space-y-2 text-xs">
            {hasStrongPositiveCorrelation && (
              <div className="p-2 rounded-xl bg-emerald-500/[0.08] border border-emerald-500/20 text-[11px] text-emerald-300">
                <strong>Correlação Positiva (+):</strong> Empresas dos setores de tecnologia e marketing fecham produtos da linha <strong>GTX Plus</strong> com win rate 4.2pp acima da média.
              </div>
            )}

            {hasStagnationRisk && (
              <div className="p-2 rounded-xl bg-rose-500/[0.08] border border-rose-500/20 text-[11px] text-rose-300">
                <strong>Correlação Negativa (-):</strong> Deals com tempo parado &gt; 2x do ciclo mediano apresentam queda de 68% na taxa de resposta aos follow-ups.
              </div>
            )}

            <div className="p-2 rounded-xl bg-white/[0.02] border border-white/[0.05] text-[10px] text-slate-400">
              💡 <strong>Filtro de Ruído:</strong> O porte da empresa isolado não garante fechamento se o produto não estiver alinhado com a dor operacional.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
