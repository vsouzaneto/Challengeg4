import type { Metadata } from "next";
import { Navigation } from "@/components/landing/navigation";
import { FooterSection } from "@/components/landing/footer-section";
import { AboutChallenge } from "@/components/about/about-challenge";
import { getAboutStory } from "@/lib/about/stories";

const story = getAboutStory("004");

export const metadata: Metadata = {
  title: story.metaTitle,
  description: story.metaDescription,
};

export default function AboutChallenge004Page() {
  return (
    <main className="relative min-h-screen overflow-x-hidden noise-overlay">
      <Navigation />
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12 pt-32 pb-24 lg:pt-40 lg:pb-32">
        <AboutChallenge story={story} />
      </div>
      <FooterSection />
    </main>
  );
}
