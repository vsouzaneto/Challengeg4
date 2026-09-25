'use client';

import React, { useState, useEffect, useMemo } from 'react';
import {
  SparklesIcon,
  BrainIcon,
  FlameIcon,
  RocketIcon,
  SearchIcon,
  ClockIcon,
  BuildingIcon,
  RefreshIcon,
  TrendingUpIcon,
  DollarSignIcon,
  FilterIcon,
  CompassIcon,
  TargetIcon,
} from '../components/Icons';
import LoginModal from '../components/LoginModal';
import DealDetailModal from '../components/DealDetailModal';
import DeepResearchModal from '../components/DeepResearchModal';
import SyncSharepointModal from '../components/SyncSharepointModal';
import ImmersiveConducao from '../components/ImmersiveConducao';
import SliceAnalysisCards from '../components/SliceAnalysisCards';

export default function LeadScorerDashboard() {
  // Estado de Autenticação
  const [currentUser, setCurrentUser] = useState<{ name: string; role: string; email: string } | null>(null);
  const [isDataLoaded, setIsDataLoaded] = useState(false);
  const [rawDeals, setRawDeals] = useState<any[]>([]);
  const [metadata, setMetadata] = useState<any>(null);

  // Modo de visualização: 'conducao' (Telas Primárias Vítricas) ou 'dashboard'
  const [viewMode, setViewMode] = useState<'conducao' | 'dashboard'>('conducao');

  // Modais
  const [selectedDeal, setSelectedDeal] = useState<any | null>(null);
  const [showDeepResearch, setShowDeepResearch] = useState(false);
  const [showSyncModal, setShowSyncModal] = useState(false);
  const [updatedCount, setUpdatedCount] = useState(0);

  // Estado de IA para DeepResearch
  const [aiReport, setAiReport] = useState<string | null>(null);
  const [isLoadingAi, setIsLoadingAi] = useState(false);
  const [quickAiSummary, setQuickAiSummary] = useState<string | null>(null);

  // Filtros Globais
  const [activeQueue, setActiveQueue] = useState<string>('TODAS');
  const [selectedAgent, setSelectedAgent] = useState<string>('ALL');
  const [selectedManager, setSelectedManager] = useState<string>('ALL');
  const [selectedOffice, setSelectedOffice] = useState<string>('ALL');
  const [selectedProduct, setSelectedProduct] = useState<string>('ALL');
  const [selectedSector, setSelectedSector] = useState<string>('ALL');
  const [selectedTier, setSelectedTier] = useState<string>('ALL');
  const [minScore, setMinScore] = useState<number>(0);
  const [selectedYearEstRange, setSelectedYearEstRange] = useState<string>('ALL');
  const [selectedPriceRange, setSelectedPriceRange] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Paginação
  const [currentPage, setCurrentPage] = useState<number>(1);
  const itemsPerPage = 15;

  // Carregar dados brutos
  useEffect(() => {
    fetch('/data/pipeline_processed.json')
      .then((res) => res.json())
      .then((data) => {
        setRawDeals(data.deals || []);
        setMetadata(data.metadata || {});
        setIsDataLoaded(true);
      })
      .catch((err) => {
        console.error('Erro ao carregar dados:', err);
      });
  }, []);

  // Lista única de filtros
  const filterOptions = useMemo(() => {
    if (!rawDeals.length) return { agents: [], managers: [], offices: [], products: [], sectors: [] };
    const agents = Array.from(new Set(rawDeals.map((d) => d.agent))).filter(Boolean).sort();
    const managers = Array.from(new Set(rawDeals.map((d) => d.manager))).filter(Boolean).sort();
    const offices = Array.from(new Set(rawDeals.map((d) => d.office))).filter(Boolean).sort();
    const products = Array.from(new Set(rawDeals.map((d) => d.product))).filter(Boolean).sort();
    const sectors = Array.from(new Set(rawDeals.map((d) => d.sector))).filter(Boolean).sort();
    return { agents, managers, offices, products, sectors };
  }, [rawDeals]);

  // Função Global de Reset Completo
  const handleResetAllFilters = () => {
    setActiveQueue('TODAS');
    setSelectedAgent('ALL');
    setSelectedManager('ALL');
    setSelectedOffice('ALL');
    setSelectedProduct('ALL');
    setSelectedSector('ALL');
    setSelectedTier('ALL');
    setMinScore(0);
    setSelectedYearEstRange('ALL');
    setSelectedPriceRange('ALL');
    setSearchQuery('');
    setCurrentPage(1);
    setViewMode('conducao');
  };

  // Contadores globais das 4 filas
  const queueCounts = useMemo(() => {
    const counts = {
      'Agir Hoje': 0,
      'Avançar Negociação': 0,
      'Qualificar': 0,
      'Revisar Continuidade': 0,
      total: 0,
    };
    rawDeals.forEach((d) => {
      if (d.is_active) {
        counts.total++;
        if (counts[d.action_queue as keyof typeof counts] !== undefined) {
          counts[d.action_queue as keyof typeof counts]++;
        }
      }
    });
    return counts;
  }, [rawDeals]);

  // Filtragem dos deals ativos
  const filteredDeals = useMemo(() => {
    return rawDeals.filter((d) => {
      if (!d.is_active) return false;

      // Fila de Ação
      if (activeQueue !== 'TODAS' && d.action_queue !== activeQueue) return false;

      // Filtros dropdown
      if (selectedAgent !== 'ALL' && d.agent !== selectedAgent) return false;
      if (selectedManager !== 'ALL' && d.manager !== selectedManager) return false;
      if (selectedOffice !== 'ALL' && d.office !== selectedOffice) return false;
      if (selectedProduct !== 'ALL' && d.product !== selectedProduct) return false;
      if (selectedSector !== 'ALL' && d.sector !== selectedSector) return false;
      if (selectedTier !== 'ALL' && d.tier !== selectedTier) return false;

      // Score mínimo
      if (d.score < minScore) return false;

      // Range de Fundação da Empresa
      if (selectedYearEstRange !== 'ALL') {
        const y = d.year_est;
        if (!y) return false;
        if (selectedYearEstRange === 'old' && y >= 2000) return false;
        if (selectedYearEstRange === 'modern' && (y < 2000 || y > 2012)) return false;
        if (selectedYearEstRange === 'recent' && y <= 2012) return false;
      }

      // Range de Close Value (Ticket)
      if (selectedPriceRange !== 'ALL') {
        const p = d.sales_price || 0;
        if (selectedPriceRange === 'enterprise' && p < 20000) return false;
        if (selectedPriceRange === 'premium' && (p < 4000 || p >= 20000)) return false;
        if (selectedPriceRange === 'mid' && (p < 1000 || p >= 4000)) return false;
        if (selectedPriceRange === 'entry' && p >= 1000) return false;
      }

      // Busca por texto
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const accMatch = (d.account || '').toLowerCase().includes(q);
        const idMatch = (d.id || '').toLowerCase().includes(q);
        const agentMatch = (d.agent || '').toLowerCase().includes(q);
        const prodMatch = (d.product || '').toLowerCase().includes(q);
        if (!accMatch && !idMatch && !agentMatch && !prodMatch) return false;
      }

      return true;
    });
  }, [
    rawDeals,
    activeQueue,
    selectedAgent,
    selectedManager,
    selectedOffice,
    selectedProduct,
    selectedSector,
    selectedTier,
    minScore,
    selectedYearEstRange,
    selectedPriceRange,
    searchQuery,
  ]);

  // Ordenação prioritária: Score decrescente
  const sortedDeals = useMemo(() => {
    return [...filteredDeals].sort((a, b) => b.score - a.score);
  }, [filteredDeals]);

  // Métricas do Slice Ativo
  const sliceStats = useMemo(() => {
    const total = sortedDeals.length;
    if (total === 0) {
      return {
        total_filtered: 0,
        total_pipeline_val: 0,
        avg_score: 0,
        over_cycle_count: 0,
        unidentified_count: 0,
        top_product: 'N/A',
        top_agent: 'N/A',
        avg_ticket: 0,
      };
    }
    const totalVal = sortedDeals.reduce((acc, d) => acc + (d.sales_price || 0), 0);
    const avgScore = Math.round(sortedDeals.reduce((acc, d) => acc + d.score, 0) / total);
    const overCycle = sortedDeals.filter((d) => d.relative_age >= 2.0).length;
    const unidentified = sortedDeals.filter((d) => !d.has_account).length;

    const prodCounts: Record<string, number> = {};
    sortedDeals.forEach((d) => {
      prodCounts[d.product] = (prodCounts[d.product] || 0) + 1;
    });
    const topProd = Object.entries(prodCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A';

    return {
      total_filtered: total,
      total_pipeline_val: totalVal,
      avg_score: avgScore,
      over_cycle_count: overCycle,
      unidentified_count: unidentified,
      top_product: topProd,
      avg_ticket: Math.round(totalVal / total),
    };
  }, [sortedDeals]);

  // Atualizar deal localmente após ação no modal
  const handleUpdateDeal = (updated: any) => {
    setRawDeals((prev) => prev.map((d) => (d.id === updated.id ? updated : d)));
    setUpdatedCount((c) => c + 1);
  };

  // Handler da Condução Imersiva (Avança diretamente para o Dashboard já filtrado)
  const handleApplySliceFromImmersive = (filters: {
    queue: string;
    office: string;
    priceRange: string;
    yearEstRange: string;
    sector: string;
  }) => {
    setActiveQueue(filters.queue);
    setSelectedOffice(filters.office);
    setSelectedPriceRange(filters.priceRange);
    setSelectedYearEstRange(filters.yearEstRange);
    setSelectedSector(filters.sector);
    setViewMode('dashboard');
    setCurrentPage(1);
  };

  // Disparar DeepResearch
  const handleTriggerDeepResearch = async () => {
    setShowDeepResearch(true);
    setIsLoadingAi(true);
    try {
      const res = await fetch('/api/ai-research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sliceContext: {
            filtros_ativos: {
              fila: activeQueue,
              vendedor: selectedAgent,
              gerente: selectedManager,
              regiao: selectedOffice,
              produto: selectedProduct,
              setor: selectedSector,
              ticket_range: selectedPriceRange,
              fundacao_range: selectedYearEstRange,
            },
            metricas: sliceStats,
            amostra_deals: sortedDeals.slice(0, 10).map((d) => ({
              id: d.id,
              conta: d.account || 'SEM CONTA',
              produto: d.product,
              score: d.score,
              tier: d.tier,
              idade_relativa: d.relative_age + 'x',
              ticket: '$' + d.sales_price,
            })),
          },
          mode: 'deep-research',
        }),
      });
      const data = await res.json();
      if (data?.result) {
        setAiReport(data.result);
      } else {
        setAiReport(data?.error || 'Erro na resposta do modelo Gemini.');
      }
    } catch (e: any) {
      setAiReport('Erro ao comunicar com a IA: ' + e?.message);
    } finally {
      setIsLoadingAi(false);
    }
  };

  // Resumo rápido de IA para o slice ao mudar filtro chave
  useEffect(() => {
    if (!isDataLoaded || sortedDeals.length === 0) return;
    const overPct = ((sliceStats.over_cycle_count / sliceStats.total_filtered) * 100).toFixed(1);
    const unIdPct = ((sliceStats.unidentified_count / sliceStats.total_filtered) * 100).toFixed(1);

    setQuickAiSummary(
      `Slice com ${sliceStats.total_filtered} oportunidades ativas ($${sliceStats.total_pipeline_val.toLocaleString()} em pipeline). ` +
        `Fila: ${activeQueue !== 'TODAS' ? activeQueue : 'Global'}. ` +
        `${unIdPct}% não possuem conta mapeada. ` +
        `${overPct}% estão acima de 2x o ciclo mediano (revisar continuidade).`
    );
  }, [activeQueue, selectedOffice, selectedProduct, selectedSector, sliceStats]);

  // Paginação
  const totalPages = Math.ceil(sortedDeals.length / itemsPerPage) || 1;
  const paginatedDeals = sortedDeals.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const topTargetDeal = sortedDeals[0] || null;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-blue-600 selection:text-white">
      {/* Login Modal se não estiver autenticado */}
      {!currentUser && (
        <LoginModal
          onLogin={(user) => {
            setCurrentUser(user);
            if (user.role.includes('Vendedor')) {
              setSelectedAgent('Darcel Schlecht');
            }
          }}
        />
      )}

      {/* SE O USUÁRIO ESTÁ NO MODO CONDUÇÃO GUIADA: TELAS PRIMÁRIAS IMERSIVAS */}
      {viewMode === 'conducao' && (
        <ImmersiveConducao
          onApplySlice={handleApplySliceFromImmersive}
          queueCounts={queueCounts}
          onSkipToDashboard={() => setViewMode('dashboard')}
        />
      )}

      {/* SE O USUÁRIO ESTÁ NO MODO DASHBOARD: DASHBOARD VÍTRICO ULTRA-PREMIUM */}
      {viewMode === 'dashboard' && (
        <>
          {/* Header Vítrico com Logo Oficial do G4 */}
          <header className="border-b border-white/[0.08] bg-slate-950/70 backdrop-blur-2xl sticky top-0 z-30">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 p-1.5 bg-white/[0.03] rounded-xl border border-white/[0.08] shadow-sm">
                  <img
                    src="/logo-g4-completa-branca.svg"
                    alt="G4 Educação"
                    className="h-8 w-auto object-contain"
                  />
                </div>

                <div className="border-l border-white/[0.1] pl-3">
                  <h1 className="text-sm font-bold text-white flex items-center gap-2">
                    AI Master — Lead Scorer Pro
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30 font-medium">
                      RevOps Glass Engine
                    </span>
                  </h1>
                  <p className="text-[11px] text-slate-400">
                    Priorização Algorítmica & Análise do Slice
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                {/* Botão Reiniciar Prospecção & Zerar Filtros */}
                <button
                  onClick={handleResetAllFilters}
                  title="Limpar todos os filtros e abrir as perguntas primárias de condução"
                  className="px-3.5 py-1.5 bg-rose-500/[0.12] hover:bg-rose-500/[0.2] text-rose-300 hover:text-white border border-rose-500/30 text-xs font-bold rounded-xl transition flex items-center gap-1.5 shadow-sm"
                >
                  <RefreshIcon className="w-3.5 h-3.5 text-rose-400" />
                  <span>Reiniciar Prospecção</span>
                </button>

                {/* Botão de Condução Guiada */}
                <button
                  onClick={() => setViewMode('conducao')}
                  className="px-3 py-1.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold rounded-xl transition flex items-center gap-1.5 shadow-md shadow-blue-500/20"
                >
                  <CompassIcon className="w-3.5 h-3.5" />
                  <span>Condução Guiada</span>
                </button>

                {/* Sincronizar CRM */}
                <button
                  onClick={() => setShowSyncModal(true)}
                  className="px-3 py-1.5 bg-white/[0.04] hover:bg-white/[0.08] text-slate-200 text-xs font-semibold rounded-xl border border-white/[0.08] transition flex items-center gap-1.5 shadow-sm"
                >
                  <RefreshIcon className="w-3.5 h-3.5 text-blue-400" />
                  <span className="hidden sm:inline">Sincronizar CRM</span>
                </button>

                {/* Perfil */}
                {currentUser && (
                  <div className="flex items-center gap-2 pl-3 border-l border-white/[0.1]">
                    <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center font-bold text-xs text-white">
                      {currentUser.name.charAt(0)}
                    </div>
                    <div className="hidden md:block text-left">
                      <div className="text-xs font-semibold text-white">{currentUser.name}</div>
                      <div className="text-[10px] text-slate-400">{currentUser.role}</div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </header>

          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
            {/* ALVO #1 RECOMENDADO EM DESTAQUE COM SCORE MÁXIMO (VÍTRICO) */}
            {topTargetDeal && (
              <div className="p-5 rounded-3xl backdrop-blur-2xl bg-white/[0.03] border border-blue-500/40 shadow-[0_16px_40px_rgba(59,130,246,0.15)] relative overflow-hidden">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex items-start gap-4">
                    <div className="p-3.5 rounded-2xl bg-blue-500/10 border border-blue-500/30 text-center flex-shrink-0">
                      <span className="text-[10px] font-bold uppercase tracking-wider block text-blue-300">
                        Lead Score
                      </span>
                      <span className="text-3xl font-black text-white">{topTargetDeal.score}</span>
                      <span className="text-[10px] font-bold px-2 py-0.5 bg-rose-500/20 text-rose-300 rounded block mt-0.5">
                        Tier {topTargetDeal.tier}
                      </span>
                    </div>

                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-blue-400 uppercase tracking-wider flex items-center gap-1">
                          <TargetIcon className="w-3.5 h-3.5" />
                          Alvo Prioritário #1 Recomendado para Atacar Agora
                        </span>
                        <span className="text-xs px-2.5 py-0.5 rounded-full bg-white/[0.05] text-slate-300 border border-white/[0.08]">
                          Fila: {topTargetDeal.action_queue}
                        </span>
                      </div>
                      <h3 className="text-lg font-bold text-white mt-1">
                        {topTargetDeal.account || 'Empresa em Qualificação (Mapear Decisor)'}
                      </h3>
                      <p className="text-xs text-slate-300 mt-0.5">
                        Produto: <strong className="text-white">{topTargetDeal.product}</strong> · Ticket:{' '}
                        <strong className="text-white">${topTargetDeal.sales_price?.toLocaleString()}</strong> · Vendedor:{' '}
                        <strong>{topTargetDeal.agent}</strong> ({topTargetDeal.office}) · Ano Est.:{' '}
                        {topTargetDeal.year_est || 'N/A'}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setSelectedDeal(topTargetDeal)}
                      className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-blue-600/30 transition"
                    >
                      Abrir Roteiro de Abordagem & Ações
                    </button>
                    <button
                      onClick={() => setViewMode('conducao')}
                      className="px-3.5 py-2.5 bg-white/[0.05] hover:bg-white/[0.1] text-slate-300 text-xs font-semibold rounded-xl border border-white/[0.08] transition"
                    >
                      Refazer Condução
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* PAINÉIS DE ANÁLISE PROFUNDA DO SLICE (CARDS DE CORRELAÇÃO, GANHO VS PERDIDO E OFENSORES) */}
            <SliceAnalysisCards
              sliceData={sliceStats}
              selectedOffice={selectedOffice}
              selectedSector={selectedSector}
              selectedYearRange={selectedYearEstRange}
            />

            {/* Banner de Briefing de IA & Botão DeepResearch */}
            <div className="p-5 rounded-2xl backdrop-blur-2xl bg-white/[0.02] border border-white/[0.08] relative overflow-hidden shadow-xl">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
                <div className="space-y-1">
                  <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 text-xs font-medium border border-blue-500/30">
                    <SparklesIcon className="w-3.5 h-3.5" />
                    Copiloto de IA em Tempo Real (Gemini 2.5 Flash)
                  </div>
                  <h2 className="text-base font-bold text-white">
                    Briefing Estratégico do Slice Filtrado
                  </h2>
                  <p className="text-xs text-slate-300 max-w-3xl leading-relaxed">
                    {quickAiSummary ||
                      'Carregando dados das 8.800 oportunidades e calculando métricas de RevOps...'}
                  </p>
                </div>

                <button
                  onClick={handleTriggerDeepResearch}
                  className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-indigo-600/30 transition flex items-center justify-center gap-2 flex-shrink-0"
                >
                  <BrainIcon className="w-4 h-4" />
                  Executar DeepResearch do Slice
                </button>
              </div>
            </div>

            {/* As 4 Filas de Ação RevOps do Briefing */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                  <FilterIcon className="w-3.5 h-3.5 text-blue-400" />
                  Filas de Ação Comercial (Foco de Segunda-Feira)
                </h3>
                <span className="text-xs text-slate-500">
                  Total de Ativos: <strong className="text-slate-300">{queueCounts.total}</strong>
                </span>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {/* Fila 1: Agir Hoje */}
                <button
                  onClick={() => {
                    setActiveQueue(activeQueue === 'Agir Hoje' ? 'TODAS' : 'Agir Hoje');
                    setCurrentPage(1);
                  }}
                  className={`p-4 rounded-2xl text-left border transition-all duration-200 relative overflow-hidden group ${
                    activeQueue === 'Agir Hoje'
                      ? 'bg-rose-500/[0.12] border-rose-500/60 shadow-[0_0_24px_rgba(244,63,94,0.2)]'
                      : 'bg-white/[0.02] border-white/[0.06] hover:bg-white/[0.04]'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <span className="p-2 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
                      <FlameIcon className="w-4 h-4" />
                    </span>
                    <span className="text-2xl font-black text-white">{queueCounts['Agir Hoje']}</span>
                  </div>
                  <div className="mt-3">
                    <div className="text-xs font-bold text-white group-hover:text-rose-400 transition">
                      1. Agir Hoje
                    </div>
                    <div className="text-[11px] text-slate-400 mt-0.5">
                      Deals quentes / ticket alto no momento de fechamento
                    </div>
                  </div>
                </button>

                {/* Fila 2: Avançar Negociação */}
                <button
                  onClick={() => {
                    setActiveQueue(activeQueue === 'Avançar Negociação' ? 'TODAS' : 'Avançar Negociação');
                    setCurrentPage(1);
                  }}
                  className={`p-4 rounded-2xl text-left border transition-all duration-200 relative overflow-hidden group ${
                    activeQueue === 'Avançar Negociação'
                      ? 'bg-blue-500/[0.12] border-blue-500/60 shadow-[0_0_24px_rgba(59,130,246,0.2)]'
                      : 'bg-white/[0.02] border-white/[0.06] hover:bg-white/[0.04]'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <span className="p-2 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
                      <RocketIcon className="w-4 h-4" />
                    </span>
                    <span className="text-2xl font-black text-white">
                      {queueCounts['Avançar Negociação']}
                    </span>
                  </div>
                  <div className="mt-3">
                    <div className="text-xs font-bold text-white group-hover:text-blue-400 transition">
                      2. Avançar Negociação
                    </div>
                    <div className="text-[11px] text-slate-400 mt-0.5">
                      Conta qualificada com próximo passo viável
                    </div>
                  </div>
                </button>

                {/* Fila 3: Qualificar */}
                <button
                  onClick={() => {
                    setActiveQueue(activeQueue === 'Qualificar' ? 'TODAS' : 'Qualificar');
                    setCurrentPage(1);
                  }}
                  className={`p-4 rounded-2xl text-left border transition-all duration-200 relative overflow-hidden group ${
                    activeQueue === 'Qualificar'
                      ? 'bg-amber-500/[0.12] border-amber-500/60 shadow-[0_0_24px_rgba(245,158,11,0.2)]'
                      : 'bg-white/[0.02] border-white/[0.06] hover:bg-white/[0.04]'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <span className="p-2 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      <BuildingIcon className="w-4 h-4" />
                    </span>
                    <span className="text-2xl font-black text-amber-400">
                      {queueCounts['Qualificar']}
                    </span>
                  </div>
                  <div className="mt-3">
                    <div className="text-xs font-bold text-white group-hover:text-amber-400 transition">
                      3. Qualificar (68,2%)
                    </div>
                    <div className="text-[11px] text-slate-400 mt-0.5">
                      1.425 ativos sem conta identificada (mapear empresa)
                    </div>
                  </div>
                </button>

                {/* Fila 4: Revisar Continuidade */}
                <button
                  onClick={() => {
                    setActiveQueue(
                      activeQueue === 'Revisar Continuidade' ? 'TODAS' : 'Revisar Continuidade'
                    );
                    setCurrentPage(1);
                  }}
                  className={`p-4 rounded-2xl text-left border transition-all duration-200 relative overflow-hidden group ${
                    activeQueue === 'Revisar Continuidade'
                      ? 'bg-purple-500/[0.12] border-purple-500/60 shadow-[0_0_24px_rgba(168,85,247,0.2)]'
                      : 'bg-white/[0.02] border-white/[0.06] hover:bg-white/[0.04]'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <span className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
                      <ClockIcon className="w-4 h-4" />
                    </span>
                    <span className="text-2xl font-black text-purple-400">
                      {queueCounts['Revisar Continuidade']}
                    </span>
                  </div>
                  <div className="mt-3">
                    <div className="text-xs font-bold text-white group-hover:text-purple-400 transition">
                      4. Revisar Continuidade
                    </div>
                    <div className="text-[11px] text-slate-400 mt-0.5">
                      Deals &gt; 2x ciclo mediano (desocupar ou reengajar)
                    </div>
                  </div>
                </button>
              </div>
            </div>

            {/* Barra de Filtros Finos em Vidro (com Range de Fundação e Range de Ticket) */}
            <div className="p-4.5 backdrop-blur-xl bg-white/[0.02] border border-white/[0.08] rounded-2xl space-y-3 shadow-lg">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="relative flex-1 min-w-[240px]">
                  <SearchIcon className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    placeholder="Buscar por conta, vendedor, produto ou ID..."
                    value={searchQuery}
                    onChange={(e) => {
                      setSearchQuery(e.target.value);
                      setCurrentPage(1);
                    }}
                    className="w-full pl-9 pr-3 py-2 bg-white/[0.03] border border-white/[0.08] rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>

                <button
                  onClick={handleResetAllFilters}
                  className="px-3.5 py-2 text-xs font-semibold text-rose-300 hover:text-white bg-rose-500/[0.1] hover:bg-rose-500/[0.2] border border-rose-500/30 rounded-xl transition flex items-center gap-1.5 shadow-sm"
                >
                  <RefreshIcon className="w-3.5 h-3.5" />
                  Zerar Todos os Filtros
                </button>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2 text-xs">
                {/* Vendedor */}
                <div>
                  <label className="text-[10px] text-slate-400 font-semibold block mb-1">VENDEDOR</label>
                  <select
                    value={selectedAgent}
                    onChange={(e) => {
                      setSelectedAgent(e.target.value);
                      setCurrentPage(1);
                    }}
                    className="w-full p-2 bg-slate-900 border border-white/[0.08] rounded-xl text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <option value="ALL">Todos os Vendedores</option>
                    {filterOptions.agents.map((ag) => (
                      <option key={ag} value={ag}>
                        {ag}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Região */}
                <div>
                  <label className="text-[10px] text-slate-400 font-semibold block mb-1">REGIÃO</label>
                  <select
                    value={selectedOffice}
                    onChange={(e) => {
                      setSelectedOffice(e.target.value);
                      setCurrentPage(1);
                    }}
                    className="w-full p-2 bg-slate-900 border border-white/[0.08] rounded-xl text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <option value="ALL">Todas as Regiões</option>
                    {filterOptions.offices.map((o) => (
                      <option key={o} value={o}>
                        {o}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Produto */}
                <div>
                  <label className="text-[10px] text-slate-400 font-semibold block mb-1">PRODUTO</label>
                  <select
                    value={selectedProduct}
                    onChange={(e) => {
                      setSelectedProduct(e.target.value);
                      setCurrentPage(1);
                    }}
                    className="w-full p-2 bg-slate-900 border border-white/[0.08] rounded-xl text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <option value="ALL">Todos os Produtos</option>
                    {filterOptions.products.map((p) => (
                      <option key={p} value={p}>
                        {p}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Setor */}
                <div>
                  <label className="text-[10px] text-slate-400 font-semibold block mb-1">SETOR CONTA</label>
                  <select
                    value={selectedSector}
                    onChange={(e) => {
                      setSelectedSector(e.target.value);
                      setCurrentPage(1);
                    }}
                    className="w-full p-2 bg-slate-900 border border-white/[0.08] rounded-xl text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <option value="ALL">Todos os Setores</option>
                    {filterOptions.sectors.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Range de Close Value */}
                <div>
                  <label className="text-[10px] text-slate-400 font-semibold block mb-1">FAIXA DE TICKET</label>
                  <select
                    value={selectedPriceRange}
                    onChange={(e) => {
                      setSelectedPriceRange(e.target.value);
                      setCurrentPage(1);
                    }}
                    className="w-full p-2 bg-slate-900 border border-white/[0.08] rounded-xl text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <option value="ALL">Todos os Valores</option>
                    <option value="enterprise">Enterprise ($20k+)</option>
                    <option value="premium">Premium ($4k-$20k)</option>
                    <option value="mid">Mid-Range ($1k-$4k)</option>
                    <option value="entry">Entry (&lt; $1k)</option>
                  </select>
                </div>

                {/* Range de Fundação da Empresa */}
                <div>
                  <label className="text-[10px] text-slate-400 font-semibold block mb-1">ANO FUNDAÇÃO</label>
                  <select
                    value={selectedYearEstRange}
                    onChange={(e) => {
                      setSelectedYearEstRange(e.target.value);
                      setCurrentPage(1);
                    }}
                    className="w-full p-2 bg-slate-900 border border-white/[0.08] rounded-xl text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <option value="ALL">Qualquer Idade</option>
                    <option value="old">Tradicionais (&lt; 2000)</option>
                    <option value="modern">Consolidadas (2000-12)</option>
                    <option value="recent">Modernas (&gt; 2012)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Tabela Vítrica de Oportunidades Priorizadas */}
            <div className="backdrop-blur-2xl bg-white/[0.02] border border-white/[0.08] rounded-2xl overflow-hidden shadow-xl">
              <div className="p-4 border-b border-white/[0.06] flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    Oportunidades Ranqueadas por Lead Score
                    <span className="text-xs px-2 py-0.5 rounded-full bg-white/[0.05] text-slate-400 font-normal">
                      {sortedDeals.length} deals encontrados
                    </span>
                  </h3>
                  <p className="text-[11px] text-slate-400">
                    Priorize contatos no topo da lista. Clique na linha para abrir o diagnóstico completo.
                  </p>
                </div>

                <div className="flex items-center gap-2 text-xs">
                  <button
                    onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                    className="px-2.5 py-1 rounded bg-white/[0.05] text-slate-300 hover:bg-white/[0.1] disabled:opacity-40"
                  >
                    Anterior
                  </button>
                  <span className="text-slate-400">
                    Pág. <strong className="text-white">{currentPage}</strong> de {totalPages}
                  </span>
                  <button
                    onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                    className="px-2.5 py-1 rounded bg-white/[0.05] text-slate-300 hover:bg-white/[0.1] disabled:opacity-40"
                  >
                    Próxima
                  </button>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-white/[0.02] text-slate-400 uppercase text-[10px] tracking-wider border-b border-white/[0.06]">
                    <tr>
                      <th className="py-3 px-4">Score & Tier</th>
                      <th className="py-3 px-4">Fila de Ação</th>
                      <th className="py-3 px-4">Conta / Empresa</th>
                      <th className="py-3 px-4">Produto</th>
                      <th className="py-3 px-4">Ticket Ref.</th>
                      <th className="py-3 px-4">Idade Relativa</th>
                      <th className="py-3 px-4">Vendedor</th>
                      <th className="py-3 px-4 text-right">Ação</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/[0.04]">
                    {paginatedDeals.map((d) => (
                      <tr
                        key={d.id}
                        onClick={() => setSelectedDeal(d)}
                        className="hover:bg-white/[0.04] cursor-pointer transition group"
                      >
                        {/* Score com Destaque */}
                        <td className="py-3 px-4 whitespace-nowrap">
                          <div className="flex items-center gap-2">
                            <span
                              className={`font-black text-sm px-2.5 py-1 rounded-lg shadow-sm ${
                                d.tier === 'Hot'
                                  ? 'bg-rose-500 text-white shadow-rose-500/20'
                                  : d.tier === 'Warm'
                                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                                  : 'bg-white/[0.05] text-slate-400'
                              }`}
                            >
                              {d.score}
                            </span>
                            <span className="text-[11px] font-semibold text-slate-300">{d.tier}</span>
                          </div>
                        </td>

                        {/* Fila */}
                        <td className="py-3 px-4 whitespace-nowrap">
                          <span
                            className={`inline-block px-2.5 py-0.5 rounded-full text-[10px] font-medium ${
                              d.action_queue === 'Agir Hoje'
                                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                                : d.action_queue === 'Qualificar'
                                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                                : d.action_queue === 'Revisar Continuidade'
                                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                                : 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                            }`}
                          >
                            {d.action_queue}
                          </span>
                        </td>

                        {/* Conta */}
                        <td className="py-3 px-4">
                          {d.account ? (
                            <div>
                              <div className="font-semibold text-white group-hover:text-blue-400 transition">
                                {d.account}
                              </div>
                              <div className="text-[10px] text-slate-400">
                                {d.sector || 'Geral'} · {d.year_est ? `Est. ${d.year_est}` : ''}
                              </div>
                            </div>
                          ) : (
                            <div className="text-amber-400 flex items-center gap-1 italic text-[11px]">
                              Sem conta identificada
                            </div>
                          )}
                        </td>

                        {/* Produto */}
                        <td className="py-3 px-4 whitespace-nowrap">
                          <div className="text-slate-200 font-medium">{d.product}</div>
                          <div className="text-[10px] text-slate-500">{d.series}</div>
                        </td>

                        {/* Ticket */}
                        <td className="py-3 px-4 whitespace-nowrap">
                          <div className="font-semibold text-white">
                            ${d.sales_price?.toLocaleString()}
                          </div>
                          <div className="text-[10px] text-slate-500">
                            Esp: ${d.expected_ref_val?.toLocaleString()}
                          </div>
                        </td>

                        {/* Idade Relativa */}
                        <td className="py-3 px-4 whitespace-nowrap">
                          <div
                            className={`font-semibold ${
                              d.relative_age >= 2.0
                                ? 'text-rose-400'
                                : d.relative_age >= 1.0
                                ? 'text-amber-400'
                                : 'text-emerald-400'
                            }`}
                          >
                            {d.relative_age}x ciclo
                          </div>
                          <div className="text-[10px] text-slate-500">{d.days_engage} dias</div>
                        </td>

                        {/* Vendedor */}
                        <td className="py-3 px-4 whitespace-nowrap">
                          <div className="text-slate-200">{d.agent}</div>
                          <div className="text-[10px] text-slate-500">{d.office}</div>
                        </td>

                        {/* Ação */}
                        <td className="py-3 px-4 text-right whitespace-nowrap">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedDeal(d);
                            }}
                            className="px-2.5 py-1 bg-white/[0.05] hover:bg-blue-600 hover:text-white rounded-lg text-[11px] font-semibold text-slate-300 transition"
                          >
                            Ver Detalhes
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </main>
        </>
      )}

      {/* Modal de Detalhe do Deal */}
      {selectedDeal && (
        <DealDetailModal
          deal={selectedDeal}
          onClose={() => setSelectedDeal(null)}
          onUpdateDeal={handleUpdateDeal}
        />
      )}

      {/* Modal DeepResearch do Slice */}
      {showDeepResearch && (
        <DeepResearchModal
          sliceData={{ ...sliceStats, activeQueue }}
          aiReport={aiReport}
          isLoading={isLoadingAi}
          onClose={() => setShowDeepResearch(false)}
          onRefresh={handleTriggerDeepResearch}
        />
      )}

      {/* Modal Sincronização CRM */}
      {showSyncModal && (
        <SyncSharepointModal
          updatedCount={updatedCount}
          onClose={() => setShowSyncModal(false)}
        />
      )}
    </div>
  );
}
