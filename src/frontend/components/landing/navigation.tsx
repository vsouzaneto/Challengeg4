"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ChevronDown, Menu, X } from "lucide-react";

import { G4Mark } from "@/components/brand/g4-mark";
import { CHALLENGES } from "@/lib/research/stories";

type NavLink = {
  kind: "link";
  name: string;
  href: string;
};

type NavMenu = {
  kind: "menu";
  name: string;
  target: "about" | "research" | "model" | "images";
  hash?: "background" | "analysis";
};

type NavItem = NavLink | NavMenu;

const navItems: NavItem[] = [
  { kind: "menu", name: "Sobre", target: "about" },
  { kind: "menu", name: "Contexto", target: "research", hash: "background" },
  { kind: "menu", name: "Análise", target: "research", hash: "analysis" },
  { kind: "menu", name: "Modelo", target: "model" },
  { kind: "link", name: "Chatbot", href: "/sdk/chatbot" },
  { kind: "link", name: "Dashboards", href: "/sdk/dashboards" },
  { kind: "menu", name: "Estatísticas do modelo", target: "images" },
];

function menuPath(item: NavMenu, challenge: (typeof CHALLENGES)[number]) {
  if (item.target === "about") return challenge.aboutPath;
  if (item.target === "model") return challenge.modelPath;
  if (item.target === "images") return challenge.imagePath;
  return challenge.path;
}

function menuHref(item: NavMenu, challenge: (typeof CHALLENGES)[number]) {
  if (item.target === "research") return `${challenge.path}#${item.hash}`;
  return menuPath(item, challenge);
}

function menuMatchesPath(item: NavMenu, pathname: string) {
  return CHALLENGES.some((challenge) => menuPath(item, challenge) === pathname);
}

export function Navigation() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const [mobileSection, setMobileSection] = useState<string | null>(null);
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    setOpenMenu(null);
    setMobileSection(null);
  }, [pathname]);

  const handleNavigate = (e: React.MouseEvent, href: string) => {
    setIsMobileMenuOpen(false);
    setOpenMenu(null);
    setMobileSection(null);

    const [path, hash] = href.split("#");
    const targetPath = path || "/";

    if (targetPath === pathname && hash) {
      e.preventDefault();
      const el = document.getElementById(hash);
      if (el) {
        el.scrollIntoView({ behavior: "smooth" });
        window.history.replaceState(null, "", href);
      }
      return;
    }

    if (!hash) {
      return;
    }

    e.preventDefault();
    router.push(href);
  };

  const linkClass =
    "text-sm text-primary-foreground/70 hover:text-primary-foreground transition-colors duration-300 relative group";

  return (
    <header
      className={`fixed z-50 transition-all duration-500 ${
        isScrolled ? "top-4 left-4 right-4" : "top-0 left-0 right-0"
      }`}
    >
      <nav
        className={`mx-auto transition-all duration-500 bg-primary text-primary-foreground ${
          isScrolled || isMobileMenuOpen
            ? "backdrop-blur-xl rounded-2xl shadow-[var(--g4s-shadow-card)] max-w-[1200px]"
            : "max-w-[1400px]"
        }`}
      >
        <div
          className={`flex items-center justify-between transition-all duration-500 px-6 lg:px-8 ${
            isScrolled ? "h-14" : "h-20"
          }`}
        >
          <G4Mark scrolled={isScrolled} />

          <div className="hidden md:flex items-center gap-8 lg:gap-12">
            {navItems.map((item) => {
              if (item.kind === "link") {
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    prefetch={!item.href.startsWith("/sdk")}
                    onClick={(e) => handleNavigate(e, item.href)}
                    className={linkClass}
                  >
                    {item.name}
                    <span className="absolute -bottom-1 left-0 w-0 h-px bg-primary-foreground transition-all duration-300 group-hover:w-full" />
                  </Link>
                );
              }

              const isOpen = openMenu === item.name;
              const onChallenge = menuMatchesPath(item, pathname);

              return (
                <div
                  key={item.name}
                  className="relative"
                  onMouseEnter={() => setOpenMenu(item.name)}
                  onMouseLeave={() => setOpenMenu(null)}
                >
                  <button
                    type="button"
                    className={`${linkClass} inline-flex items-center gap-1 ${
                      onChallenge ? "text-primary-foreground" : ""
                    }`}
                    aria-expanded={isOpen}
                    aria-haspopup="menu"
                    onClick={() => setOpenMenu(isOpen ? null : item.name)}
                  >
                    {item.name}
                    <ChevronDown
                      className={`w-3.5 h-3.5 transition-transform duration-300 ${
                        isOpen ? "rotate-180" : ""
                      }`}
                    />
                    <span className="absolute -bottom-1 left-0 w-0 h-px bg-primary-foreground transition-all duration-300 group-hover:w-full" />
                  </button>
                  <div
                    role="menu"
                    aria-label={item.name}
                    className={`absolute left-0 top-full pt-3 ${isOpen ? "block" : "hidden"}`}
                  >
                    <div className="min-w-[200px] rounded-xl bg-primary text-primary-foreground shadow-[var(--g4s-shadow-card)] border border-primary-foreground/10 py-2">
                      {CHALLENGES.map((challenge) => {
                        const href = menuHref(item, challenge);
                        const isCurrent = pathname === menuPath(item, challenge);
                        return (
                          <Link
                            key={href}
                            href={href}
                            role="menuitem"
                            onClick={(e) => handleNavigate(e, href)}
                            className={`block px-4 py-2 text-sm transition-colors ${
                              isCurrent
                                ? "text-primary-foreground"
                                : "text-primary-foreground/70 hover:text-primary-foreground"
                            }`}
                          >
                            <span className="font-mono text-xs mr-2">{challenge.code}</span>
                            {challenge.slug}
                          </Link>
                        );
                      })}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 text-primary-foreground"
            aria-label="Abrir ou fechar o menu"
          >
            {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </nav>

      <div
        className={`md:hidden fixed inset-0 bg-primary text-primary-foreground z-40 transition-all duration-500 ${
          isMobileMenuOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
        }`}
        style={{ top: 0 }}
      >
        <div className="flex flex-col h-full px-8 pt-28 pb-8 overflow-y-auto">
          <div className="flex-1 flex flex-col justify-center gap-6">
            {navItems.map((item, i) => {
              if (item.kind === "link") {
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    prefetch={!item.href.startsWith("/sdk")}
                    onClick={(e) => handleNavigate(e, item.href)}
                    className={`text-4xl font-display text-primary-foreground hover:text-primary-foreground/70 transition-all duration-500 ${
                      isMobileMenuOpen ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
                    }`}
                    style={{ transitionDelay: isMobileMenuOpen ? `${i * 75}ms` : "0ms" }}
                  >
                    {item.name}
                  </Link>
                );
              }

              const expanded = mobileSection === item.name;
              return (
                <div key={item.name}>
                  <button
                    type="button"
                    aria-expanded={expanded}
                    onClick={() => setMobileSection(expanded ? null : item.name)}
                    className={`inline-flex items-center gap-3 text-4xl font-display text-primary-foreground hover:text-primary-foreground/70 transition-all duration-500 ${
                      isMobileMenuOpen ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
                    }`}
                    style={{ transitionDelay: isMobileMenuOpen ? `${i * 75}ms` : "0ms" }}
                  >
                    {item.name}
                    <ChevronDown
                      className={`w-6 h-6 transition-transform duration-300 ${
                        expanded ? "rotate-180" : ""
                      }`}
                    />
                  </button>
                  {expanded && (
                    <div className="mt-3 flex flex-col gap-2 pl-1">
                      {CHALLENGES.map((challenge) => {
                        const href = menuHref(item, challenge);
                        return (
                          <Link
                            key={href}
                            href={href}
                            onClick={(e) => handleNavigate(e, href)}
                            className="text-xl font-mono text-primary-foreground/80 hover:text-primary-foreground"
                          >
                            {challenge.menuLabel}
                          </Link>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </header>
  );
}
