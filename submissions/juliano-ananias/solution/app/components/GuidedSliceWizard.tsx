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
} from './Icons';

interface WizardProps {
  onApplySlice: (filters: {
    queue: string;
    office: string;
    priceRange: string;
    product: string;
  }) => void;
  queueCounts: {
    'Agir Hoje': number;
    'Avançar Negociação': number;
    'Qualificar': number;
    'Revisar Continuidade': number;
    total: number;
  };
  onDismiss: () => void;
  onResetAll: () => void;
}

export default function GuidedSliceWizard({
  onApplySlice,
  queueCounts,
  onDismiss,
  onResetAll,
}: WizardProps) {
  const [step, setStep] = useState<number>(1);
  const [selectedMission, setSelectedMission] = useState<string>('Agir Hoje');
  const [selectedOffice, setSelectedOffice] = useState<string>('ALL');
  const [selectedTicket, setSelectedTicket] = useState<string>('ALL');

  // Insights dinâmicos da IA para o Passo 1
  const missionAiInsights: Record<string, string> = {
    'Agir Hoje':
      '🎯 Parecer da IA: 38 oportunidades quentes totalizando $260k em pipeline. Deals no sweet-spot de timing (idade relativa entre 0.8x e 1.2x do ciclo mediano) convertem até 2.4x mais rápido se contatados hoje.',
    'Avançar Negociação':
      '🚀 Parecer da IA: 178 deals ativos onde a empresa já possui histórico mapeado. O foco do vendedor aqui é avançar alinhamento técnico para envio imediato de proposta comercial.',
    'Qualificar':
      '🔍 Parecer da IA: 1.425 registros (68,2% de todo o pipeline ativo) estão sem razão social identificada. O vendedor deve mapear decisor e porte antes de queimar tempo em ligação fria.',
    'Revisar Continuidade':
      '⏳ Parecer da IA: 448 negociações ultrapassam duas vezes o ciclo mediano do produto. Estatisticamente, a taxa de vitória cai para menos de 12% sem uma repactuação de escopo imediata (regra: avançar ou dar lost).',
  };

  // Insights dinâmicos da IA para o Passo 2
  const officeAiInsights: Record<string, string> = {
    ALL: '🌍 Parecer da IA: Visão nacional equilibrada com representatividade dos 35 executivos de vendas.',
    West: '📈 Parecer da IA: A praça West lidera a taxa de vitória geral da companhia (63.9%), com alta tração em empresas de tecnologia e marketing.',
    East: '💼 Parecer da IA: Região East apresenta maior concentração de contas corporativas de médio e grande porte, com ticket médio superior.',
    Central:
      '🏢 Parecer da IA: Mercado mais maduro (62.6% win rate), com ciclos de negociação mais longos porém alta fidelidade e recorrência de compra.',
  };

  // Insights dinâmicos da IA para o Passo 3
  const ticketAiInsights: Record<string, string> = {
    ALL: '📦 Parecer da IA: Portfólio amplo dos 7 produtos, do MG Special ($55) ao enterprise GTK 500 ($26k).',
    enterprise:
      '💎 Parecer da IA: Foco exclusivo no "unicórnio" GTK 500 ($26.707). Cada vitória compensa quase 50 deals básicos. Recomenda-se acompanhamento direto do gerente.',
    premium:
      '🚀 Parecer da IA: Carro-chefe de faturamento corporativo (GTX Plus Pro e GTXPro), combinando ticket expressivo com ciclo médio saudável de 57 dias.',
    mid: '⚡ Parecer da IA: Produtos de entrada com ciclo de fechamento mais ágil, ideais para bater meta de volume e abrir portas em novas contas.',
  };

  const handleFinish = () => {
    onApplySlice({
      queue: selectedMission,
      office: selectedOffice,
      priceRange: selectedTicket,
      product: 'ALL',
    });
  };

  const handleResetWizard = () => {
    setStep(1);
    setSelectedMission('Agir Hoje');
    setSelectedOffice('ALL');
    setSelectedTicket('ALL');
    onResetAll();
  };

  return (
    <div className="bg-gradient-to-br from-slate-900 via-slate-950 to-indigo-950 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header do Wizard */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <img
            src="/logo-g4-completa-branca.svg"
            alt="G4 Educação"
            className="h-8 w-auto object-contain"
          />
          <div className="border-l border-slate-700 pl-3">
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-blue-400">
                Condução Guiada de Prospecção
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 font-medium">
                Passo {step} de 3
              </span>
            </div>
            <h2 className="text-xl sm:text-2xl font-black text-white mt-0.5">
              Por onde começaremos a prospectar hoje?
            </h2>
          </div>
        </div>

        {/* Controles de Progresso & Reset */}
        <div className="flex items-center gap-3">
          {/* Botão Zerar Tudo */}
          <button
            onClick={handleResetWizard}
            title="Zerar todos os filtros e reiniciar prospecção"
            className="px-3 py-1.5 bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-semibold rounded-xl border border-slate-700 transition flex items-center gap-1.5 shadow-sm"
          >
            <RefreshIcon className="w-3.5 h-3.5 text-rose-400" />
            <span>Zerar Tudo</span>
          </button>

          <div className="flex gap-1.5 ml-2">
            <div
              className={`h-2 rounded-full transition-all ${
                step >= 1 ? 'w-8 bg-blue-500' : 'w-4 bg-slate-800'
              }`}
            />
            <div
              className={`h-2 rounded-full transition-all ${
                step >= 2 ? 'w-8 bg-blue-500' : 'w-4 bg-slate-800'
              }`}
            />
            <div
              className={`h-2 rounded-full transition-all ${
                step >= 3 ? 'w-8 bg-blue-500' : 'w-4 bg-slate-800'
              }`}
            />
          </div>

          <button
            onClick={onDismiss}
            className="text-xs text-slate-400 hover:text-white px-2.5 py-1 rounded-lg hover:bg-slate-800/60 transition ml-2"
          >
            Pular Condução
          </button>
        </div>
      </div>

      {/* PASSO 1: A MISSÃO DO DIA */}
      {step === 1 && (
        <div className="py-6 space-y-4 animate-in fade-in slide-in-from-right-4 duration-200">
          <div>
            <h3 className="text-sm font-bold text-slate-200">
              1. Selecione o objetivo comercial da sua ação agora:
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              O motor de IA filtra os alvos ideais de acordo com a urgência da esteira.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-2">
            {/* Missão 1 */}
            <div
              onClick={() => setSelectedMission('Agir Hoje')}
              className={`p-4 rounded-2xl border cursor-pointer transition relative group ${
                selectedMission === 'Agir Hoje'
                  ? 'bg-rose-950/40 border-rose-500 ring-2 ring-rose-500/30'
                  : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="flex items-start justify-between">
                <span className="p-2 rounded-xl bg-rose-500/20 text-rose-400 border border-rose-500/30">
                  <FlameIcon className="w-5 h-5" />
                </span>
                <span className="text-xs font-black px-2 py-0.5 bg-rose-500/20 text-rose-300 rounded-full">
                  {queueCounts['Agir Hoje']} alvos
                </span>
              </div>
              <h4 className="text-sm font-bold text-white mt-3 group-hover:text-rose-400 transition">
                Fechar Receita Rápida (Agir Hoje)
              </h4>
              <p className="text-xs text-slate-400 mt-1">
                Deals de alto ticket no momento crítico de conversão e decisor aquecido.
              </p>
            </div>

            {/* Missão 2 */}
            <div
              onClick={() => setSelectedMission('Avançar Negociação')}
              className={`p-4 rounded-2xl border cursor-pointer transition relative group ${
                selectedMission === 'Avançar Negociação'
                  ? 'bg-blue-950/40 border-blue-500 ring-2 ring-blue-500/30'
                  : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="flex items-start justify-between">
                <span className="p-2 rounded-xl bg-blue-500/20 text-blue-400 border border-blue-500/30">
                  <RocketIcon className="w-5 h-5" />
                </span>
                <span className="text-xs font-black px-2 py-0.5 bg-blue-500/20 text-blue-300 rounded-full">
                  {queueCounts['Avançar Negociação']} alvos
                </span>
              </div>
              <h4 className="text-sm font-bold text-white mt-3 group-hover:text-blue-400 transition">
                Destravar Negociações em Andamento
              </h4>
              <p className="text-xs text-slate-400 mt-1">
                Oportunidades com empresa mapeada, ciclo saudável e próximo passo viável.
              </p>
            </div>

            {/* Missão 3 */}
            <div
              onClick={() => setSelectedMission('Qualificar')}
              className={`p-4 rounded-2xl border cursor-pointer transition relative group ${
                selectedMission === 'Qualificar'
                  ? 'bg-amber-950/40 border-amber-500 ring-2 ring-amber-500/30'
                  : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="flex items-start justify-between">
                <span className="p-2 rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30">
                  <BuildingIcon className="w-5 h-5" />
                </span>
                <span className="text-xs font-black px-2 py-0.5 bg-amber-500/20 text-amber-300 rounded-full">
                  {queueCounts['Qualificar']} alvos (68,2%)
                </span>
              </div>
              <h4 className="text-sm font-bold text-white mt-3 group-hover:text-amber-400 transition">
                Qualificar Pipeline Frio (Mapear Contas)
              </h4>
              <p className="text-xs text-slate-400 mt-1">
                Identificar a empresa, porte e decisor antes de despender tempo em ligações.
              </p>
            </div>

            {/* Missão 4 */}
            <div
              onClick={() => setSelectedMission('Revisar Continuidade')}
              className={`p-4 rounded-2xl border cursor-pointer transition relative group ${
                selectedMission === 'Revisar Continuidade'
                  ? 'bg-purple-950/40 border-purple-500 ring-2 ring-purple-500/30'
                  : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="flex items-start justify-between">
                <span className="p-2 rounded-xl bg-purple-500/20 text-purple-400 border border-purple-500/30">
                  <ClockIcon className="w-5 h-5" />
                </span>
                <span className="text-xs font-black px-2 py-0.5 bg-purple-500/20 text-purple-300 rounded-full">
                  {queueCounts['Revisar Continuidade']} alvos
                </span>
              </div>
              <h4 className="text-sm font-bold text-white mt-3 group-hover:text-purple-400 transition">
                Limpeza & Decisão Crítica (&gt; 2x Ciclo)
              </h4>
              <p className="text-xs text-slate-400 mt-1">
                Deals estagnados. Regra de ouro: reengajar com proposta final ou dar Lost.
              </p>
            </div>
          </div>

          {/* Card de Auxílio da IA em Tempo Real para a Missão Escolhida */}
          <div className="p-4 rounded-2xl bg-blue-950/40 border border-blue-500/30 flex items-start gap-3 mt-3 animate-in fade-in">
            <span className="p-2 rounded-xl bg-blue-500/20 text-blue-300 flex-shrink-0">
              <BrainIcon className="w-4 h-4" />
            </span>
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-blue-300 block">
                Auxílio da IA — Insight da Missão Selecionada
              </span>
              <p className="text-xs text-slate-200 mt-0.5 leading-relaxed font-medium">
                {missionAiInsights[selectedMission]}
              </p>
            </div>
          </div>

          <div className="flex justify-end pt-4">
            <button
              onClick={() => setStep(2)}
              className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded-xl transition flex items-center gap-2 shadow-lg shadow-blue-600/30"
            >
              Avançar para Região
              <ChevronRightIcon className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* PASSO 2: REGIÃO & PRAÇA */}
      {step === 2 && (
        <div className="py-6 space-y-4 animate-in fade-in slide-in-from-right-4 duration-200">
          <div>
            <h3 className="text-sm font-bold text-slate-200">
              2. Deseja afunilar por Escritório Regional?
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Veja a taxa histórica de fechamento comprovada em cada praça comercial.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 pt-2">
            <div
              onClick={() => setSelectedOffice('ALL')}
              className={`p-4 rounded-2xl border cursor-pointer transition ${
                selectedOffice === 'ALL'
                  ? 'bg-blue-950/40 border-blue-500 ring-2 ring-blue-500/30'
                  : 'bg-slate-900/60 border-slate-800'
              }`}
            >
              <h4 className="text-xs font-bold text-white">Todas as Regiões</h4>
              <p className="text-[11px] text-slate-400 mt-1">Visão nacional consolidada</p>
            </div>

            <div
              onClick={() => setSelectedOffice('West')}
              className={`p-4 rounded-2xl border cursor-pointer transition ${
                selectedOffice === 'West'
                  ? 'bg-blue-950/40 border-blue-500 ring-2 ring-blue-500/30'
                  : 'bg-slate-900/60 border-slate-800'
              }`}
            >
              <div className="flex justify-between items-center">
                <h4 className="text-xs font-bold text-white">Região West</h4>
                <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded">
                  63.9% win
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mt-1">Maior taxa de conversão</p>
            </div>

            <div
              onClick={() => setSelectedOffice('East')}
              className={`p-4 rounded-2xl border cursor-pointer transition ${
                selectedOffice === 'East'
                  ? 'bg-blue-950/40 border-blue-500 ring-2 ring-blue-500/30'
                  : 'bg-slate-900/60 border-slate-800'
              }`}
            >
              <div className="flex justify-between items-center">
                <h4 className="text-xs font-bold text-white">Região East</h4>
                <span className="text-[10px] font-bold text-blue-400 bg-blue-500/10 px-1.5 py-0.5 rounded">
                  63.0% win
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mt-1">Alto volume de contas enterprise</p>
            </div>

            <div
              onClick={() => setSelectedOffice('Central')}
              className={`p-4 rounded-2xl border cursor-pointer transition ${
                selectedOffice === 'Central'
                  ? 'bg-blue-950/40 border-blue-500 ring-2 ring-blue-500/30'
                  : 'bg-slate-900/60 border-slate-800'
              }`}
            >
              <div className="flex justify-between items-center">
                <h4 className="text-xs font-bold text-white">Região Central</h4>
                <span className="text-[10px] font-bold text-amber-400 bg-amber-500/10 px-1.5 py-0.5 rounded">
                  62.6% win
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mt-1">Mercado maduro</p>
            </div>
          </div>

          {/* Card de Auxílio da IA em Tempo Real para a Região */}
          <div className="p-4 rounded-2xl bg-blue-950/40 border border-blue-500/30 flex items-start gap-3 mt-3 animate-in fade-in">
            <span className="p-2 rounded-xl bg-blue-500/20 text-blue-300 flex-shrink-0">
              <BrainIcon className="w-4 h-4" />
            </span>
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-blue-300 block">
                Auxílio da IA — Insight da Região Selecionada
              </span>
              <p className="text-xs text-slate-200 mt-0.5 leading-relaxed font-medium">
                {officeAiInsights[selectedOffice]}
              </p>
            </div>
          </div>

          <div className="flex justify-between pt-4">
            <button
              onClick={() => setStep(1)}
              className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-white"
            >
              ← Voltar
            </button>
            <button
              onClick={() => setStep(3)}
              className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded-xl transition flex items-center gap-2 shadow-lg shadow-blue-600/30"
            >
              Avançar para Ticket
              <ChevronRightIcon className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* PASSO 3: FAIXA DE TICKET & CONCLUSÃO */}
      {step === 3 && (
        <div className="py-6 space-y-4 animate-in fade-in slide-in-from-right-4 duration-200">
          <div>
            <h3 className="text-sm font-bold text-slate-200">
              3. Escolha a faixa de ticket desejada:
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Conclua o slice para entregar os alvos com Score em destaque.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 pt-2">
            <div
              onClick={() => setSelectedTicket('ALL')}
              className={`p-4 rounded-2xl border cursor-pointer transition ${
                selectedTicket === 'ALL'
                  ? 'bg-blue-950/40 border-blue-500 ring-2 ring-blue-500/30'
                  : 'bg-slate-900/60 border-slate-800'
              }`}
            >
              <h4 className="text-xs font-bold text-white">Todos os Tickets</h4>
              <p className="text-[11px] text-slate-400 mt-1">Portfólio amplo</p>
            </div>

            <div
              onClick={() => setSelectedTicket('enterprise')}
              className={`p-4 rounded-2xl border cursor-pointer transition ${
                selectedTicket === 'enterprise'
                  ? 'bg-rose-950/40 border-rose-500 ring-2 ring-rose-500/30'
                  : 'bg-slate-900/60 border-slate-800'
              }`}
            >
              <h4 className="text-xs font-bold text-white">Enterprise ($20k+)</h4>
              <p className="text-[11px] text-slate-400 mt-1">GTK 500 (Impacto máximo em faturamento)</p>
            </div>

            <div
              onClick={() => setSelectedTicket('premium')}
              className={`p-4 rounded-2xl border cursor-pointer transition ${
                selectedTicket === 'premium'
                  ? 'bg-blue-950/40 border-blue-500 ring-2 ring-blue-500/30'
                  : 'bg-slate-900/60 border-slate-800'
              }`}
            >
              <h4 className="text-xs font-bold text-white">Premium ($4k - $20k)</h4>
              <p className="text-[11px] text-slate-400 mt-1">GTX Plus Pro & GTXPro</p>
            </div>

            <div
              onClick={() => setSelectedTicket('mid')}
              className={`p-4 rounded-2xl border cursor-pointer transition ${
                selectedTicket === 'mid'
                  ? 'bg-indigo-950/40 border-indigo-500 ring-2 ring-indigo-500/30'
                  : 'bg-slate-900/60 border-slate-800'
              }`}
            >
              <h4 className="text-xs font-bold text-white">Mid & Entry (&lt; $4k)</h4>
              <p className="text-[11px] text-slate-400 mt-1">MG Advanced & GTX Basic</p>
            </div>
          </div>

          {/* Card de Auxílio da IA em Tempo Real para o Ticket */}
          <div className="p-4 rounded-2xl bg-blue-950/40 border border-blue-500/30 flex items-start gap-3 mt-3 animate-in fade-in">
            <span className="p-2 rounded-xl bg-blue-500/20 text-blue-300 flex-shrink-0">
              <BrainIcon className="w-4 h-4" />
            </span>
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-blue-300 block">
                Auxílio da IA — Insight do Ticket Selecionado
              </span>
              <p className="text-xs text-slate-200 mt-0.5 leading-relaxed font-medium">
                {ticketAiInsights[selectedTicket]}
              </p>
            </div>
          </div>

          {/* Card de Resumo do Slice Pronto */}
          <div className="p-4 bg-slate-900/80 rounded-2xl border border-blue-500/40 flex flex-col sm:flex-row items-center justify-between gap-4 mt-3">
            <div className="flex items-center gap-3">
              <span className="p-2.5 rounded-xl bg-blue-500/20 text-blue-400">
                <TargetIcon className="w-6 h-6" />
              </span>
              <div>
                <div className="text-xs font-bold text-white">
                  Slice Configurado com Sucesso!
                </div>
                <div className="text-[11px] text-slate-400">
                  Fila: <strong>{selectedMission}</strong> · Região: <strong>{selectedOffice}</strong> · Ticket: <strong>{selectedTicket}</strong>
                </div>
              </div>
            </div>

            <button
              onClick={handleFinish}
              className="w-full sm:w-auto px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-black text-xs rounded-xl shadow-xl shadow-blue-500/25 transition flex items-center justify-center gap-2"
            >
              <SparklesIcon className="w-4 h-4" />
              Atacar Este Slice & Ver Alvos com Score
            </button>
          </div>

          <div className="flex justify-start pt-2">
            <button
              onClick={() => setStep(2)}
              className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-white"
            >
              ← Voltar
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
