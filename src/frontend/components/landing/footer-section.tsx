"use client";

import dynamic from "next/dynamic";
import { ArrowUpRight } from "lucide-react";
import { CHALLENGES } from "@/lib/research/stories";

const AnimatedWave = dynamic(
  () => import("./animated-wave").then((module) => module.AnimatedWave),
  { ssr: false },
);

const footerLinks = {
  Navegação: [
    ...CHALLENGES.map((challenge) => ({
      name: `Sobre · ${challenge.menuLabel}`,
      href: challenge.aboutPath,
    })),
    ...CHALLENGES.map((challenge) => ({
      name: `Contexto · ${challenge.menuLabel}`,
      href: `${challenge.path}#background`,
    })),
    ...CHALLENGES.map((challenge) => ({
      name: `Análise · ${challenge.menuLabel}`,
      href: `${challenge.path}#analysis`,
    })),
    ...CHALLENGES.map((challenge) => ({
      name: `Modelo · ${challenge.menuLabel}`,
      href: challenge.modelPath,
    })),
    ...CHALLENGES.map((challenge) => ({
      name: `Estatísticas do modelo · ${challenge.menuLabel}`,
      href: challenge.imagePath,
    })),
  ],
  LinkedIn: [
    { name: "Adriano Aguiar", href: "https://linkedin.com/in/adrianoaguiar" },
  ],
  "Páginas Institucionais": [
    { name: "Site", href: "https://g4business.com/" },
    { name: "G4 Ai Master", href: "https://ats.g4business.com/application/8889da8b-b1b2-46bb-b81f-e825477a3f5b" },
    { name: "Instagram", href: "https://www.instagram.com/g4.business/" },
  ],
  "Podcast G4": [
    { name: "Spotify", href: "https://open.spotify.com/show/0uNjUO4oP1UDaV0JHRAhXJ" },
  ],
};

const socialLinks = [
  { name: "GitHub", href: "https://github.com/adrianoaguiar/ai-master-challenge" },
];

export function FooterSection() {
  return (
    <footer className="relative border-t border-foreground/10 [content-visibility:auto] [contain-intrinsic-size:1px_640px]">
      {/* Animated wave background */}
      <div className="absolute inset-0 h-64 opacity-20 pointer-events-none overflow-hidden">
        <AnimatedWave />
      </div>

      <div className="relative z-10 max-w-[1400px] mx-auto px-6 lg:px-12">
        {/* Main Footer */}
        <div className="py-16 lg:py-24">
          <div className="grid grid-cols-2 md:grid-cols-6 gap-12 lg:gap-8">
            {/* Brand Column */}
            <div className="col-span-2">
              <a href="/" className="flex items-center gap-2 group mb-6">
                <img
                  src="/brand/logo-g4-completa-branca.svg"
                  alt="G4"
                  className="h-8 w-auto g4s-logo-on-light"
                />
              </a>

              <p className="text-muted-foreground leading-relaxed mb-8 max-w-xs">
                O G4 está construindo um novo tipo de profissional: o AI Master. Uma pessoa capaz de entrar em qualquer área — vendas, suporte, marketing, operações — e usar IA generativa para resolver problemas reais de forma transformacional.
              </p>

              {/* Social Links */}
              <div className="flex gap-6">
                {socialLinks.map((link) => (
                  <a
                    key={link.name}
                    href={link.href}
                    className="text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1 group"
                  >
                    {link.name}
                    <ArrowUpRight className="w-3 h-3 opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                  </a>
                ))}
              </div>
            </div>

            {/* Link Columns */}
            {Object.entries(footerLinks).map(([title, links]) => (
              <div key={title}>
                <h3 className="text-sm font-medium mb-6">{title}</h3>
                <ul className="space-y-4">
                  {links.map((link) => (
                    <li key={link.name}>
                      <a
                        href={link.href}
                        className="text-sm text-muted-foreground hover:text-foreground transition-colors inline-flex items-center gap-2"
                      >
                        {link.name}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="py-8 border-t border-foreground/10 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-muted-foreground">
            G4 2026. Todos os direitos reservados.
          </p>

          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[var(--g4s-feedback-ok)]" />
              Todos os sistemas operacionais
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}
