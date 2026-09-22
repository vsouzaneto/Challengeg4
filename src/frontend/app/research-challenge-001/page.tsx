import type { Metadata } from "next";
import { Navigation } from "@/components/landing/navigation";
import { FooterSection } from "@/components/landing/footer-section";
import { ChallengeStory } from "@/components/research/challenge-story";
import { getStory } from "@/lib/research/stories";

const story = getStory("001");

export const metadata: Metadata = {
  title: story.metaTitle,
  description: story.metaDescription,
};

export default function ResearchChallenge001Page() {
  return (
    <main className="relative min-h-screen overflow-x-hidden noise-overlay">
      <Navigation />
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12 pt-32 pb-24 lg:pt-40 lg:pb-32 space-y-24 lg:space-y-32">
        <ChallengeStory story={story} />
      </div>
      <FooterSection />
    </main>
  );
}
