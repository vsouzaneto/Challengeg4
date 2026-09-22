import type { Metadata } from "next";
import { Navigation } from "@/components/landing/navigation";
import { FooterSection } from "@/components/landing/footer-section";
import { ImageChallenge } from "@/components/model-2/image-challenge";
import { getImageWorkshop } from "@/lib/model-2/stories";

const story = getImageWorkshop("003");

export const metadata: Metadata = {
  title: story.metaTitle,
  description: story.metaDescription,
};

export default function Model2Challenge003Page() {
  return (
    <main className="relative min-h-screen overflow-x-hidden noise-overlay">
      <Navigation />
      <div className="pt-32 pb-24">
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          <ImageChallenge story={story} />
        </div>
      </div>
      <FooterSection />
    </main>
  );
}
