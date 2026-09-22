import type { Metadata } from "next";
import { Navigation } from "@/components/landing/navigation";
import { FooterSection } from "@/components/landing/footer-section";
import { Model2WorkshopClient } from "@/components/model-2/model2-workshop-client";

export const metadata: Metadata = {
  title: "Oficina de imagens · Tumor Sense",
  description:
    "Oficina interativa de classificação de imagens de câncer de mama. Compare CNNs, ResNets, MobileNets e ViTs em patches histológicos; percorra o forward pass; inspecione Grad-CAM, eigen-breasts e o espaço de embeddings.",
};

export default function ModelTwoPage() {
  return (
    <main className="relative min-h-screen overflow-x-hidden noise-overlay">
      <Navigation />
      <div className="pt-32 pb-24">
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          <Model2WorkshopClient />
        </div>
      </div>
      <FooterSection />
    </main>
  );
}
