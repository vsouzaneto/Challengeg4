'use client';

import React, { useState } from 'react';
import {
  FlameIcon,
  RocketIcon,
  BuildingIcon,
  ClockIcon,
  ChevronRightIcon,
  SparklesIcon,
  TargetIcon,
  BrainIcon,
  RefreshIcon,
  TrendingUpIcon,
  AlertTriangleIcon,
} from './Icons';

interface ImmersiveConducaoProps {
  onApplySlice: (filters: {
    queue: string;
    office: string;
    priceRange: string;
    yearEstRange: string;
    sector: string;
  }) => void;
  queueCounts: {
    'Agir Hoje': number;
    'Avançar Negociação': number;
    'Qualificar': number;
    'Revisar Continuidade': number;
    total: number;
  };
  onSkipToDashboard: () => void;
}

export default function ImmersiveConducao({
  onApplySlice,
  queueCounts,
  onSkipToDashboard,
}: ImmersiveConducaoProps) {
  const [step, setStep] = useState<number>(1);

  // Seleções do usuário
  const [selectedMission, setSelectedMission] = useState<string>('Agir Hoje');
  const [selectedOffice, setSelectedOffice] = useState<string>('ALL');
  const [selectedPriceRange, setSelectedPriceRange] = useState<string>('ALL');
  const [selectedYearRange, setSelectedYearRange] = useState<string>('ALL');
  const [selectedSector, setSelectedSector] = useState<string>('ALL');

  // Insights de IA ultra-específicos e dinâmicos para cada escolha
  const missionInsights: Record<string, { title: string; text: string; alert?: string }> = {
    'Agir Hoje': {
      title: 'Fila 1 — Fechamento Imediato & Alto Potencial',
      text: 'Concentra 38 oportunidades no sweet-spot de negociação (ciclo relativo entre 0.8x e 1.2x). Deals trabalhados nesta janela temporal fecham até 2.4x mais rápido do que em fases prematuras.',
      alert: 'Alerta da IA: 4 deals com produto GTK 500 ($26k) demandam contato direto do gestor hoje.',
    },
    'Avançar Negociação': {
      title: 'Fila 2 — Negociações Qualificadas em Andamento',
      text: '178 oportunidades ativas onde a conta já é cliente ou possui dados cadastrais completos. O objetivo do vendedor é apresentar proposta comercial formal e acordar data de validação com decisor.',
      alert: 'Recomendação: priorize contas com histórico de recompra para aumentar a taxa em até 18pp.',
    },
    'Qualificar': {
      title: 'Fila 3 — Saneamento de Pipeline Frio (68,2% dos Ativos)',
      text: '1.425 registros ativos sem razão social associada no CRM. Ligar sem mapear a empresa derruba a produtividade comercial em mais de 40%.',
      alert: 'Ação Mandatória: identificar empresa e decisor no LinkedIn/Receita antes de efetuar a ligação.',
    },
    'Revisar Continuidade': {
      title: 'Fila 4 — Limpeza Crítica & Repactuação (> 2x Ciclo)',
      text: '448 deals ultrapassam duas vezes o ciclo mediano do produto. A probabilidade histórica de fechamento cai para 11.4% quando o deal fica estagnado sem atualização de proposta.',
      alert: 'Regra de RevOps: aplicar critério de "avançar ou dar lost definitivo" para liberar a agenda do vendedor.',
    },
  };

  const officeInsights: Record<string, { title: string; text: string; topAgent: string; ofensor: string }> = {
    ALL: {
      title: 'Território Nacional Unificado',
      text: 'Visão consolidada com atuação dos 35 executivos nos três escritórios regionais.',
      topAgent: 'Hayden Neloms (70.4% win rate)',
      ofensor: 'Deals órfãos sem contato nos últimos 30 dias',
    },
    West: {
      title: 'Escritório Regional West — Maior Eficiência',
      text: 'Líder em conversão geral (63.9%), com destaque nos setores de Software e Serviços.',
      topAgent: 'Maureen Marcano (69.9% win rate)',
      ofensor: 'Retenção de tickets na fase de minuta técnica',
    },
    East: {
      title: 'Escritório Regional East — Maior Volume Enterprise',
      text: 'Concentra as maiores receitas corporativas e maior taxa de deals do produto GTX Plus Pro.',
      topAgent: 'Wilburn Farren (69.6% win rate)',
      ofensor: 'Ciclo de aprovação financeira mais longo (mediana 64 dias)',
    },
    Central: {
      title: 'Escritório Regional Central — Mercado Consolidado',
      text: 'Base madura (62.6% win rate), caracterizada por relações de longo prazo e alta taxa de recompra.',
      topAgent: 'Darcel Schlecht (64.2% win rate)',
      ofensor: 'Deals de entrada com margem de desconto excessiva',
    },
  };

  const handleComplete = () => {
    onApplySlice({
      queue: selectedMission,
      office: selectedOffice,
      priceRange: selectedPriceRange,
      yearEstRange: selectedYearRange,
      sector: selectedSector,
    });
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 sm:p-6 lg:p-8 relative overflow-hidden font-sans">
      {/* Luzes difusas em vidro / Aurora Glass Effect */}
      <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-blue-600/15 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-[450px] h-[450px] bg-indigo-600/15 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute top-10 right-1/3 w-[300px] h-[300px] bg-[#B9915B]/10 rounded-full blur-[120px] pointer-events-none" />

      {/* Container Principal Vítrico Flutuante */}
      <div className="w-full max-w-4xl backdrop-blur-2xl bg-white/[0.03] border border-white/[0.08] shadow-[0_16px_48px_0_rgba(0,0,0,0.45)] rounded-3xl p-6 sm:p-10 relative z-10 transition-all duration-300">
        {/* Top Header Vítrico com Logo G4 Oficial */}
        <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-white/[0.07]">
          <div className="flex items-center gap-3.5">
            <div className="p-2 rounded-2xl bg-white/[0.04] border border-white/[0.1] shadow-inner">
              <img
                src="/logo-g4-completa-branca.svg"
                alt="G4 Educação"
                className="h-8 w-auto object-contain"
              />
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold tracking-[0.2em] text-blue-400 block">
                Condução Guiada & Inteligência de RevOps
              </span>
              <h1 className="text-xl sm:text-2xl font-black text-white tracking-tight">
                Por onde começaremos a prospectar hoje?
              </h1>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Indicador de Passos Minimalista */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/[0.04] border border-white/[0.08] text-xs font-semibold text-slate-300">
              <span className="text-blue-400 font-bold">Passo {step}</span> de 3
            </div>

            <button
              onClick={onSkipToDashboard}
              className="text-xs text-slate-400 hover:text-white px-3 py-1.5 rounded-xl hover:bg-white/[0.05] transition"
            >
              Pular Direto ao Dashboard
            </button>
          </div>
        </div>

        {/* TELA 1: A MISSÃO PRIORITÁRIA */}
        {step === 1 && (
          <div className="py-6 space-y-6 animate-in fade-in duration-300">
            <div>
              <span className="text-[11px] font-semibold text-blue-400 uppercase tracking-wider block">
                Etapa 1 de 3 · Direcionamento Comercial
              </span>
              <h2 className="text-lg font-bold text-white mt-0.5">
                Selecione o objetivo da prospecção de hoje:
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                O Lead Scorer ajusta os pesos algorítmicos e entrega a fatia ideal de oportunidades.
              </p>
            </div>

            {/* Grid dos 4 Cards de Missão em Vidro */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              {/* Missão 1: Agir Hoje */}
              <div
                onClick={() => setSelectedMission('Agir Hoje')}
                className={`p-4 rounded-2xl cursor-pointer transition-all duration-200 border relative group ${
                  selectedMission === 'Agir Hoje'
                    ? 'bg-rose-500/[0.12] border-rose-500/60 shadow-[0_0_24px_rgba(244,63,94,0.2)]'
                    : 'bg-white/[0.02] border-white/[0.06] hover:bg-white/[0.05] hover:border-white/[0.12]'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="p-2.5 rounded-xl bg-rose-500/20 text-rose-400 border border-rose-500/30">
                    <FlameIcon className="w-5 h-5" />
                  </div>
                  <span className="text-xs font-black px-2.5 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30">
                    {queueCounts['Agir Hoje']} alvos quentes
                  </span>
                </div>
                <h3 className="text-sm font-bold text-white mt-3 group-hover:text-rose-400 transition">
                  1. Fechar Receita Rápida (Agir Hoje)
                </h3>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                  Deals de alto valor no sweet-spot de ciclo com maior probabilidade de conversão nas próximas 72h.
                </p>
              </div>

              {/* Missão 2: Avançar Negociação */}
              <div
                onClick={() => setSelectedMission('Avançar Negociação')}
                className={`p-4 rounded-2xl cursor-pointer transition-all duration-200 border relative group ${
                  selectedMission === 'Avançar Negociação'
                    ? 'bg-blue-500/[0.12] border-blue-500/60 shadow-[0_0_24px_rgba(59,130,246,0.2)]'
                    : 'bg-white/[0.02] border-white/[0.06] hover:bg-white/[0.05] hover:border-white/[0.12]'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="p-2.5 rounded-xl bg-blue-500/20 text-blue-400 border border-blue-500/30">
                    <RocketIcon className="w-5 h-5" />
                  </div>
                  <span className="text-xs font-black px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30">
                    {queueCounts['Avançar Negociação']} alvos
                  </span>
                </div>
                <h3 className="text-sm font-bold text-white mt-3 group-hover:text-blue-400 transition">
                  2. Destravar Negociações em Andamento
                </h3>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                  Empresas qualificadas com ciclo saudável. O foco é obter próximo passo e minuta de proposta.
                </p>
              </div>

              {/* Missão 3: Qualificar */}
              <div
                onClick={() => setSelectedMission('Qualificar')}
                className={`p-4 rounded-2xl cursor-pointer transition-all duration-200 border relative group ${
                  selectedMission === 'Qualificar'
                    ? 'bg-amber-500/[0.12] border-amber-500/60 shadow-[0_0_24px_rgba(245,158,11,0.2)]'
                    : 'bg-white/[0.02] border-white/[0.06] hover:bg-white/[0.05] hover:border-white/[0.12]'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="p-2.5 rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30">
                    <BuildingIcon className="w-5 h-5" />
                  </div>
                  <span className="text-xs font-black px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
                    {queueCounts['Qualificar']} alvos (68,2%)
                  </span>
                </div>
                <h3 className="text-sm font-bold text-white mt-3 group-hover:text-amber-400 transition">
                  3. Qualificar Pipeline Frio (Mapear Contas)
                </h3>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                  1.425 negócios sem conta mapeada. Identificar decisor antes de ligar para não queimar lead.
                </p>
              </div>

              {/* Missão 4: Revisar Continuidade */}
              <div
                onClick={() => setSelectedMission('Revisar Continuidade')}
                className={`p-4 rounded-2xl cursor-pointer transition-all duration-200 border relative group ${
                  selectedMission === 'Revisar Continuidade'
                    ? 'bg-purple-500/[0.12] border-purple-500/60 shadow-[0_0_24px_rgba(168,85,247,0.2)]'
                    : 'bg-white/[0.02] border-white/[0.06] hover:bg-white/[0.05] hover:border-white/[0.12]'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="p-2.5 rounded-xl bg-purple-500/20 text-purple-400 border border-purple-500/30">
                    <ClockIcon className="w-5 h-5" />
                  </div>
                  <span className="text-xs font-black px-2.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                    {queueCounts['Revisar Continuidade']} alvos
                  </span>
                </div>
                <h3 className="text-sm font-bold text-white mt-3 group-hover:text-purple-400 transition">
                  4. Limpeza Crítica & Decisão (&gt; 2x Ciclo)
                </h3>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                  Oportunidades estagnadas. Regra cirúrgica: reengajar com nova condição ou dar Lost definitivo.
                </p>
              </div>
            </div>

            {/* Caixa de Auxílio da IA em Tempo Real (Glass Box) */}
            <div className="p-4 rounded-2xl backdrop-blur-xl bg-blue-950/30 border border-blue-500/30 flex items-start gap-3.5 shadow-lg">
              <div className="p-2 rounded-xl bg-blue-500/20 text-blue-300 flex-shrink-0">
                <BrainIcon className="w-5 h-5" />
              </div>
              <div className="space-y-1">
                <span className="text-[11px] font-bold uppercase tracking-wider text-blue-300 block">
                  {missionInsights[selectedMission]?.title}
                </span>
                <p className="text-xs text-slate-200 leading-relaxed font-medium">
                  {missionInsights[selectedMission]?.text}
                </p>
                {missionInsights[selectedMission]?.alert && (
                  <p className="text-[11px] text-amber-300/90 font-semibold pt-0.5">
                    {missionInsights[selectedMission]?.alert}
                  </p>
                )}
              </div>
            </div>

            <div className="flex justify-end pt-4">
              <button
                onClick={() => setStep(2)}
                className="px-7 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-xs rounded-xl transition flex items-center gap-2 shadow-lg shadow-blue-500/25"
              >
                Avançar para Praça & Ofensores
                <ChevronRightIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* TELA 2: PRAÇA & OFENSORES REGIONAIS */}
        {step === 2 && (
          <div className="py-6 space-y-6 animate-in fade-in duration-300">
            <div>
              <span className="text-[11px] font-semibold text-blue-400 uppercase tracking-wider block">
                Etapa 2 de 3 · Praça Comercial & Ofensores
              </span>
              <h2 className="text-lg font-bold text-white mt-0.5">
                Em qual Escritório Regional concentrar o esforço?
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                A IA analisa a taxa de vitória e aponta o principal gargalo de cada região.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-4 gap-3.5">
              {/* Todas */}
              <div
                onClick={() => setSelectedOffice('ALL')}
                className={`p-4 rounded-2xl cursor-pointer transition-all border ${
                  selectedOffice === 'ALL'
                    ? 'bg-blue-500/[0.12] border-blue-500/60 shadow-[0_0_24px_rgba(59,130,246,0.2)]'
                    : 'bg-white/[0.02] border-white/[0.06] hover:bg-white/[0.05]'
                }`}
              >
                <div className="text-xs font-bold text-white">Todas as Regiões</div>
                <div className="text-[11px] text-slate-400 mt-1">Nacional consolidado</div>
                <div className="text-[10px] text-blue-300 font-semibold mt-3">63.2% win global</div>
              </div>

              {/* West */}
              <div
                onClick={() => setSelectedOffice('West')}
                className={`p-4 rounded-2xl cursor-pointer transition-all border ${
                  selectedOffice === 'West'
                    ? 'bg-blue-500/[0.12] border-blue-500/60 shadow-[0_0_24px_rgba(59,130,246,0.2)]'
                    : 'bg-white/[0.02] border-white/[0.06] hover:bg-white/[0.05]'
                }`}
              >
                <div className="flex justify-between items-center">
                  <span className="text-xs font-bold text-white">Região West</span>
                  <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded">
                    63.9% win
                  </span>
                </div>
                <div className="text-[11px] text-slate-400 mt-1">Líder em conversão</div>
                <div className="text-[10px] text-emerald-300 font-semibold mt-3">Top: Maureen M.</div>
              </div>

              {/* East */}
              <div
                onClick={() => setSelectedOffice('East')}
                className={`p-4 rounded-2xl cursor-pointer transition-all border ${
                  selectedOffice === 'East'
                    ? 'bg-blue-500/[0.12] border-blue-500/60 shadow-[0_0_24px_rgba(59,130,246,0.2)]'
                    : 'bg-white/[0.02] border-white/[0.06] hover:bg-white/[0.05]'
                }`}
              >
                <div className="flex justify-between items-center">
                  <span className="text-xs font-bold text-white">Região East</span>
                  <span className="text-[10px] font-bold text-blue-400 bg-blue-500/10 px-1.5 py-0.5 rounded">
                    63.0% win
                  </span>
                </div>
                <div className="text-[11px] text-slate-400 mt-1">Maior ticket médio</div>
                <div className="text-[10px] text-blue-300 font-semibold mt-3">Top: Wilburn F.</div>
              </div>

              {/* Central */}
              <div
                onClick={() => setSelectedOffice('Central')}
                className={`p-4 rounded-2xl cursor-pointer transition-all border ${
                  selectedOffice === 'Central'
                    ? 'bg-blue-500/[0.12] border-blue-500/60 shadow-[0_0_24px_rgba(59,130,246,0.2)]'
                    : 'bg-white/[0.02] border-white/[0.06] hover:bg-white/[0.05]'
                }`}
              >
                <div className="flex justify-between items-center">
                  <span className="text-xs font-bold text-white">Região Central</span>
                  <span className="text-[10px] font-bold text-amber-400 bg-amber-500/10 px-1.5 py-0.5 rounded">
                    62.6% win
                  </span>
                </div>
                <div className="text-[11px] text-slate-400 mt-1">Alta recorrência</div>
                <div className="text-[10px] text-amber-300 font-semibold mt-3">Top: Darcel S.</div>
              </div>
            </div>

            {/* Painel de Ofensores Regionais Identificados pela IA */}
            <div className="p-4 rounded-2xl backdrop-blur-xl bg-indigo-950/30 border border-indigo-500/30 flex items-start gap-3.5 shadow-lg">
              <div className="p-2 rounded-xl bg-indigo-500/20 text-indigo-300 flex-shrink-0">
                <BrainIcon className="w-5 h-5" />
              </div>
              <div className="space-y-1">
                <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-300 block">
                  {officeInsights[selectedOffice]?.title} · Análise de Desempenho
                </span>
                <p className="text-xs text-slate-200 leading-relaxed font-medium">
                  {officeInsights[selectedOffice]?.text}
                </p>
                <div className="pt-1 flex flex-wrap gap-4 text-[11px]">
                  <span className="text-slate-300">
                    🏆 Maior Fechador: <strong className="text-white">{officeInsights[selectedOffice]?.topAgent}</strong>
                  </span>
                  <span className="text-rose-300">
                    ⚠️ Ofensor Crítico: <strong className="text-rose-200">{officeInsights[selectedOffice]?.ofensor}</strong>
                  </span>
                </div>
              </div>
            </div>

            <div className="flex justify-between pt-4">
              <button
                onClick={() => setStep(1)}
                className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-white"
              >
                ← Voltar para Missão
              </button>
              <button
                onClick={() => setStep(3)}
                className="px-7 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-xs rounded-xl transition flex items-center gap-2 shadow-lg shadow-blue-500/25"
              >
                Avançar para Ranges & Perfil
                <ChevronRightIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* TELA 3: RANGES DE TICKET, FUNDAÇÃO & ENTREGÁVEL FINAL */}
        {step === 3 && (
          <div className="py-6 space-y-6 animate-in fade-in duration-300">
            <div>
              <span className="text-[11px] font-semibold text-blue-400 uppercase tracking-wider block">
                Etapa 3 de 3 · Ranges & Segmentação Fina
              </span>
              <h2 className="text-lg font-bold text-white mt-0.5">
                Defina os Ranges de Ticket e Tempo de Fundação da Empresa:
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Cruzamento entre maturidade da conta e potencial financeiro para calcular o Score ideal.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Range de Close Value */}
              <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06] space-y-3">
                <span className="text-xs font-bold text-slate-200 uppercase tracking-wider block">
                  1. Range de Close Value (Ticket)
                </span>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <button
                    type="button"
                    onClick={() => setSelectedPriceRange('ALL')}
                    className={`p-2 rounded-xl border text-left transition ${
                      selectedPriceRange === 'ALL'
                        ? 'bg-blue-500/20 border-blue-500 text-white'
                        : 'bg-white/[0.03] border-white/[0.06] text-slate-400'
                    }`}
                  >
                    Todos os Tickets
                  </button>
                  <button
                    type="button"
                    onClick={() => setSelectedPriceRange('enterprise')}
                    className={`p-2 rounded-xl border text-left transition ${
                      selectedPriceRange === 'enterprise'
                        ? 'bg-rose-500/20 border-rose-500 text-white font-bold'
                        : 'bg-white/[0.03] border-white/[0.06] text-slate-400'
                    }`}
                  >
                    Enterprise ($20k+)
                  </button>
                  <button
                    type="button"
                    onClick={() => setSelectedPriceRange('premium')}
                    className={`p-2 rounded-xl border text-left transition ${
                      selectedPriceRange === 'premium'
                        ? 'bg-blue-500/20 border-blue-500 text-white font-bold'
                        : 'bg-white/[0.03] border-white/[0.06] text-slate-400'
                    }`}
                  >
                    Premium ($4k - $20k)
                  </button>
                  <button
                    type="button"
                    onClick={() => setSelectedPriceRange('mid')}
                    className={`p-2 rounded-xl border text-left transition ${
                      selectedPriceRange === 'mid'
                        ? 'bg-indigo-500/20 border-indigo-500 text-white font-bold'
                        : 'bg-white/[0.03] border-white/[0.06] text-slate-400'
                    }`}
                  >
                    Mid & Entry (&lt; $4k)
                  </button>
                </div>
              </div>

              {/* Range de Fundação da Empresa */}
              <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06] space-y-3">
                <span className="text-xs font-bold text-slate-200 uppercase tracking-wider block">
                  2. Tempo de Fundação da Empresa (Ano Est.)
                </span>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <button
                    type="button"
                    onClick={() => setSelectedYearRange('ALL')}
                    className={`p-2 rounded-xl border text-left transition ${
                      selectedYearRange === 'ALL'
                        ? 'bg-blue-500/20 border-blue-500 text-white'
                        : 'bg-white/[0.03] border-white/[0.06] text-slate-400'
                    }`}
                  >
                    Qualquer Idade
                  </button>
                  <button
                    type="button"
                    onClick={() => setSelectedYearRange('old')}
                    className={`p-2 rounded-xl border text-left transition ${
                      selectedYearRange === 'old'
                        ? 'bg-purple-500/20 border-purple-500 text-white font-bold'
                        : 'bg-white/[0.03] border-white/[0.06] text-slate-400'
                    }`}
                  >
                    Tradicionais (&lt; 2000)
                  </button>
                  <button
                    type="button"
                    onClick={() => setSelectedYearRange('modern')}
                    className={`p-2 rounded-xl border text-left transition ${
                      selectedYearRange === 'modern'
                        ? 'bg-purple-500/20 border-purple-500 text-white font-bold'
                        : 'bg-white/[0.03] border-white/[0.06] text-slate-400'
                    }`}
                  >
                    Consolidadas (2000-2012)
                  </button>
                  <button
                    type="button"
                    onClick={() => setSelectedYearRange('recent')}
                    className={`p-2 rounded-xl border text-left transition ${
                      selectedYearRange === 'recent'
                        ? 'bg-purple-500/20 border-purple-500 text-white font-bold'
                        : 'bg-white/[0.03] border-white/[0.06] text-slate-400'
                    }`}
                  >
                    Modernas (&gt; 2012)
                  </button>
                </div>
              </div>
            </div>

            {/* Insight de Sazonalidade / Dia da Semana da Utilização */}
            <div className="p-4 rounded-2xl backdrop-blur-xl bg-emerald-950/20 border border-emerald-500/30 flex items-start gap-3.5 shadow-lg">
              <div className="p-2 rounded-xl bg-emerald-500/20 text-emerald-300 flex-shrink-0">
                <TrendingUpIcon className="w-5 h-5" />
              </div>
              <div className="space-y-1">
                <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-300 block">
                  Inteligência Sazonal · Padrão de Fechamento por Dia da Semana
                </span>
                <p className="text-xs text-slate-200 leading-relaxed font-medium">
                  Análise nos 4.238 deals ganhos revela que oportunidades do produto <strong>GTX Plus Pro</strong> e empresas com mais de 10 anos de fundação apresentam maior prontidão para fechamento às sextas-feiras e fechamento de mês.
                </p>
              </div>
            </div>

            {/* Botão de Finalização da Condução */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-white/[0.07]">
              <button
                onClick={() => setStep(2)}
                className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-white"
              >
                ← Voltar para Praça
              </button>

              <button
                onClick={handleComplete}
                className="w-full sm:w-auto px-8 py-3.5 bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-500 hover:opacity-95 text-white font-black text-xs rounded-xl shadow-[0_0_30px_rgba(59,130,246,0.35)] transition flex items-center justify-center gap-2.5 uppercase tracking-wider"
              >
                <TargetIcon className="w-4 h-4" />
                Gerar Slice & Abrir Dashboard Filtrado
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
