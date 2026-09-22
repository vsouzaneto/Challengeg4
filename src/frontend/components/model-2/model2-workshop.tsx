"use client";

import { useEffect, useMemo, useState } from "react";
import { Lightbulb, ScanLine, ImageDown, Cpu, Layers } from "lucide-react";
import { getDefaultImage, type PatchImage } from "@/lib/breast-cancer/image-dataset";
import { NETWORK_INDEX, NETWORKS, type Network } from "@/lib/breast-cancer/networks";
import { NetworkPicker } from "./network-picker";
import { Leaderboard } from "./leaderboard";
import { ImageGallery, SelectedImagePreview } from "./image-gallery";
import { Architecture3D } from "./architecture-3d";
import { ForwardPassViz } from "./forward-pass-viz";
import { SaliencyView } from "./saliency-view";
import { EmbeddingExplorer } from "./embedding-explorer";
import { EigenBreasts } from "./eigen-breasts";
import { SegmentationView } from "./segmentation-view";
import { NetworkStats } from "./network-stats";

type Mode = "classification" | "segmentation";

export function Model2Workshop() {
  const [image, setImage] = useState<PatchImage>(() => getDefaultImage());
  const [network, setNetwork] = useState<Network>(() => NETWORK_INDEX.resnet18);
  const [mode, setMode] = useState<Mode>("classification");
  const [activeLayerIndex, setActiveLayerIndex] = useState<number>(network.layers.length - 1);

  // Reset layer index when the network changes.
  useEffect(() => {
    setActiveLayerIndex(network.layers.length - 1);
  }, [network.id, network.layers.length]);

  // When switching into segmentation mode, prefer the U-Net.
  useEffect(() => {
    if (mode === "segmentation" && network.family !== "unet") {
      setNetwork(NETWORK_INDEX.unet);
    }
  }, [mode, network.family]);

  const classificationNetworks = useMemo(
    () => NETWORKS.filter((n) => n.family !== "unet") as Network[],
    []
  );

  return (
    <div className="space-y-16 lg:space-y-24">
      {/* ── Hero ─────────────────────────────────────────────────────────── */}
      <section className="space-y-6">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-muted-foreground">
          <span className="w-8 h-px bg-foreground/30" />
          Oficina de imagens · protótipo
        </span>
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <h1 className="text-4xl lg:text-6xl font-display tracking-tight max-w-3xl">
            Veja a rede <br />
            <span className="text-muted-foreground">enxergar o tecido.</span>
          </h1>
          <NetworkPicker network={network} onChange={setNetwork} />
        </div>
        <p className="text-lg text-muted-foreground max-w-3xl leading-relaxed">
          Escolha um patch histológico, uma arquitetura e percorra o
          forward pass. Passe o mouse em qualquer camada da pilha 3D — ou arraste a faixa abaixo —
          para ver o que a rede calcula até a decisão.
        </p>
      </section>

      {/* ── Brainstorm callout (temporarily hidden) ──────────────────────── */}
      {/* <BrainstormCallout /> */}

      {/* ── Leaderboard ──────────────────────────────────────────────────── */}
      <Leaderboard selectedId={network.id} onSelect={setNetwork} />

      {/* ── Image picker ─────────────────────────────────────────────────── */}
      <section className="space-y-6">
        <div className="flex items-baseline justify-between gap-4 flex-wrap">
          <h2 className="font-display text-2xl lg:text-3xl tracking-tight">Galeria de entrada</h2>
          <span className="text-xs font-mono text-muted-foreground">
            36 patches histológicos IDC · 50×50 RGB · classes balanceadas
          </span>
        </div>
        <ImageGallery selected={image} onSelect={setImage} />
        <SelectedImagePreview image={image} />
      </section>

      {/* ── Mode tabs (classification / segmentation) ────────────────────── */}
      <section className="space-y-8">
        <div className="grid sm:grid-cols-2 gap-px bg-foreground/10 border border-foreground/10">
          {([
            {
              id: "classification" as Mode,
              label: "Classificação",
              sub: "prediz o rótulo do patch · benigno vs maligno",
              icon: Cpu,
            },
            {
              id: "segmentation" as Mode,
              label: "Segmentação",
              sub: "máscara de tumor por pixel via U-Net",
              icon: ScanLine,
            },
          ]).map((tab) => {
            const Icon = tab.icon;
            const isActive = tab.id === mode;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setMode(tab.id)}
                className={`p-6 text-left transition-colors relative ${
                  isActive
                    ? "bg-foreground text-background"
                    : "bg-background hover:bg-foreground/[0.03]"
                }`}
              >
                <div className="flex items-center gap-3 mb-3">
                  <Icon
                    className={`w-4 h-4 ${
                      isActive ? "text-background" : "text-foreground/70"
                    }`}
                  />
                  <span
                    className={`font-mono text-[11px] uppercase tracking-wider ${
                      isActive ? "text-background/70" : "text-muted-foreground"
                    }`}
                  >
                    tarefa
                  </span>
                </div>
                <div className="font-display text-2xl">{tab.label}</div>
                <div
                  className={`text-xs font-mono mt-1 ${
                    isActive ? "text-background/70" : "text-muted-foreground"
                  }`}
                >
                  {tab.sub}
                </div>
                {isActive && (
                  <span className="absolute -bottom-px left-0 right-0 h-0.5 bg-background" />
                )}
              </button>
            );
          })}
        </div>

        {mode === "classification" ? (
          <ClassificationPanels
            network={network}
            image={image}
            activeLayerIndex={activeLayerIndex}
            onActiveLayerChange={setActiveLayerIndex}
            networksForFamily={classificationNetworks}
          />
        ) : (
          <SegmentationPanels image={image} />
        )}
      </section>

      {/* ── Network stats ────────────────────────────────────────────────── */}
      <section className="space-y-6">
        <div className="flex items-baseline justify-between gap-4 flex-wrap">
          <h2 className="font-display text-3xl lg:text-5xl tracking-tight">Estatísticas do modelo</h2>
          <span className="text-sm font-mono text-muted-foreground">
            {network.name} · {network.layers.length} layers · {network.paramsM.toFixed(2)} M params
          </span>
        </div>
        <NetworkStats network={network} />
      </section>

      {/* ── Brainstormed extras: clearly labelled section ───────────────── */}
      {mode === "classification" && (
        <section className="space-y-10">
          <div>
            <span className="inline-flex items-center gap-3 text-sm font-mono text-muted-foreground mb-4">
              <span className="w-8 h-px bg-foreground/30" />
              Extras — painéis XAI de brainstorm
            </span>
            <h2 className="text-3xl lg:text-5xl font-display tracking-tight max-w-3xl">
              Onde o modelo olha. <br />
              <span className="text-muted-foreground">Como o espaço se curva.</span>
            </h2>
          </div>
          <SaliencyView network={network} image={image} />
          <div className="border-t border-foreground/10 pt-10">
            <EmbeddingExplorer network={network} selected={image} onSelect={setImage} />
          </div>
          <div className="border-t border-foreground/10 pt-10">
            <EigenBreasts image={image} />
          </div>
        </section>
      )}
    </div>
  );
}

function ClassificationPanels({
  network,
  image,
  activeLayerIndex,
  onActiveLayerChange,
  networksForFamily,
}: {
  network: Network;
  image: PatchImage;
  activeLayerIndex: number;
  onActiveLayerChange: (i: number) => void;
  networksForFamily: Network[];
}) {
  return (
    <div className="space-y-10">
      {/* 3D architecture */}
      <div className="space-y-5">
        <div className="flex items-baseline justify-between gap-3 flex-wrap">
          <div className="flex items-center gap-3">
            <Layers className="w-4 h-4 text-muted-foreground" />
            <h3 className="font-display text-2xl lg:text-3xl tracking-tight">
              Arquitetura em 3D
            </h3>
          </div>
          <span className="text-xs font-mono text-muted-foreground">
            área da fatia = resolução espacial · profundidade = canais
          </span>
        </div>
        <Architecture3D
          network={network}
          activeIndex={activeLayerIndex}
          onActiveChange={onActiveLayerChange}
        />
      </div>

      {/* Forward pass */}
      <div className="space-y-5 pt-2">
        <div className="flex items-baseline justify-between gap-3 flex-wrap">
          <div className="flex items-center gap-3">
            <ImageDown className="w-4 h-4 text-muted-foreground" />
            <h3 className="font-display text-2xl lg:text-3xl tracking-tight">
              Forward pass · mapas de features
            </h3>
          </div>
          <span className="text-xs font-mono text-muted-foreground">
            filtros conv reais aplicados ao patch selecionado
          </span>
        </div>
        <ForwardPassViz network={network} image={image} />
      </div>

      {/* Subtle note about which networks are in scope */}
      <div className="text-xs font-mono text-muted-foreground border-t border-foreground/10 pt-4">
        Escopo de classificação · {networksForFamily.length} redes (CNN, ResNet, VGG, MobileNet, ViT).
        A U-Net fica na aba de segmentação acima.
      </div>
    </div>
  );
}

function SegmentationPanels({ image }: { image: PatchImage }) {
  return (
    <div className="space-y-10">
      <SegmentationView image={image} />
      <p className="text-xs font-mono text-muted-foreground border-t border-foreground/10 pt-4">
        Saída mock da U-Net. Máscaras reais viriam de uma cabeça de segmentação treinada
        nos datasets BACH / BreastPathQ — a ligação fica para o backend.
      </p>
    </div>
  );
}

function BrainstormCallout() {
  return (
    <section className="border border-foreground/10 rounded-xl p-6 lg:p-8 bg-foreground/[0.02]">
      <div className="flex items-start gap-4">
        <div className="shrink-0 w-10 h-10 rounded-full bg-foreground text-background flex items-center justify-center">
          <Lightbulb className="w-4 h-4" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-[11px] font-mono uppercase tracking-wider text-muted-foreground">
            Extras de brainstorm
          </div>
          <h3 className="font-display text-xl lg:text-2xl mt-1">
            Duas ideias extras de XAI nesta página
          </h3>
          <div className="grid sm:grid-cols-2 gap-6 mt-5">
            <BrainstormItem
              title="Overlay de saliência Grad-CAM"
              desc="Heatmap ao vivo de onde a rede escolhida estava 'olhando' ao pontuar o patch. Alterne entre resolução em pixel e 10×10 grosseira para imitar o upscaling do mapa de ativação do Grad-CAM real."
            />
            <BrainstormItem
              title="Explorador do espaço de embeddings"
              desc="Projeta a ativação da penúltima camada de cada patch em 2D (UMAP / PCA). Passe o mouse para pré-visualizar, clique para usar como entrada — e veja o cluster maligno se afastar do benigno ao trocar de rede."
            />
            <BrainstormItem
              title="Eigen-breasts (PCA)"
              desc="PCA real sobre os 36 patches. Os componentes principais aparecem como eixos bipolares 'rosa ↔ azul' — uma lente de representation learning que combina com os embeddings da rede."
            />
            <BrainstormItem
              title="Visão alternativa de segmentação"
              desc="Aba opcional de U-Net que gera máscaras de tumor por pixel com métricas Dice / IoU. Fácil de remover ou estender depois."
            />
          </div>
        </div>
      </div>
    </section>
  );
}

function BrainstormItem({ title, desc }: { title: string; desc: string }) {
  return (
    <div>
      <div className="font-display text-base">{title}</div>
      <p className="text-sm text-muted-foreground mt-1 leading-relaxed">{desc}</p>
    </div>
  );
}
