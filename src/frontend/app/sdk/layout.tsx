import { Navigation } from "@/components/landing/navigation";
import { SingleSpaRoot } from "@/components/spa/single-spa-root";

export default function SdkLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <main className="relative flex h-svh flex-col overflow-hidden bg-background">
      <Navigation />
      {children}
      <SingleSpaRoot />
    </main>
  );
}
