import { ArrowUpRight } from 'lucide-react';
import { AnimatedWave } from './animated-wave';

const footerLinks = {
  Navegação: [
    { name: 'Sobre · 001 churn', href: '/about-challenge-001' },
    { name: 'Sobre · 002 support', href: '/about-challenge-002' },
    { name: 'Sobre · 003 lead', href: '/about-challenge-003' },
    { name: 'Sobre · 004 social', href: '/about-challenge-004' },
    { name: 'Contexto · 001 churn', href: '/research-challenge-001#background' },
    { name: 'Contexto · 002 support', href: '/research-challenge-002#background' },
    { name: 'Contexto · 003 lead', href: '/research-challenge-003#background' },
    { name: 'Contexto · 004 social', href: '/research-challenge-004#background' },
    { name: 'Análise · 001 churn', href: '/research-challenge-001#analysis' },
    { name: 'Análise · 002 support', href: '/research-challenge-002#analysis' },
    { name: 'Análise · 003 lead', href: '/research-challenge-003#analysis' },
    { name: 'Análise · 004 social', href: '/research-challenge-004#analysis' },
    { name: 'Modelo · 001 churn', href: '/model-challenge-001' },
    { name: 'Modelo · 002 support', href: '/model-challenge-002' },
    { name: 'Modelo · 003 lead', href: '/model-challenge-003' },
    { name: 'Modelo · 004 social', href: '/model-challenge-004' },
    { name: 'Imagens', href: '/model-2' },
    { name: 'Resultados', href: '/#results' },
  ],
  LinkedIn: [
    { name: 'Adriano Aguiar', href: 'https://linkedin.com/in/adrianoaguiar' },
  ],
  DS3: [
    { name: 'Site', href: 'https://www.ds3atucsd.com' },
    { name: 'Projetos de primavera', href: 'https://www.ds3atucsd.com/projects' },
    { name: 'Instagram', href: 'https://www.instagram.com/ds3atucsd/' },
  ],
  HDSI: [{ name: 'Site', href: 'https://datascience.ucsd.edu' }],
};

const socialLinks = [
  { name: 'GitHub', href: 'https://github.com/adrianoaguiar/ai-master-challenge' },
];

export function SiteFooter() {
  return (
    <footer className="g4-chrome relative border-t border-foreground/10 bg-background">
      <div className="absolute inset-0 h-64 opacity-20 pointer-events-none overflow-hidden">
        <AnimatedWave />
      </div>

      <div className="relative z-10 max-w-[1400px] mx-auto px-6 lg:px-12">
        <div className="py-16 lg:py-24">
          <div className="grid grid-cols-2 md:grid-cols-6 gap-12 lg:gap-8">
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
