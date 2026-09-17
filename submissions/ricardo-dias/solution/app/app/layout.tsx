import type { Metadata } from "next";
import { Inter, Manrope } from "next/font/google";
import { Navigation } from "@/components/navigation";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const manrope = Manrope({
  variable: "--font-manrope",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "Suporte Inteligente | Challenge 002",
    template: "%s | Suporte Inteligente",
  },
  description:
    "Diagnóstico operacional, triagem de tickets e uma proposta de automação com supervisão humana.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="pt-BR" className={`${inter.variable} ${manrope.variable}`}>
      <body>
        <a className="skip-link" href="#main-content">
          Pular para o conteúdo
        </a>
        <Navigation />
        <main id="main-content" className="main-content" tabIndex={-1}>
          {children}
        </main>
        <footer className="app-footer">
          <span>
            Ricardo Barão <span className="footer-separator">/</span> AI Master
            Challenge
          </span>
          <span>Dados, decisões e supervisão humana.</span>
        </footer>
      </body>
    </html>
  );
}
