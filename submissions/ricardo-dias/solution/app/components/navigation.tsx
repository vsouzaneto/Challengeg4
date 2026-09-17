"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Icon, type IconName } from "./icons";

const links: { href: string; label: string; icon: IconName }[] = [
  { href: "/", label: "Diagnóstico", icon: "chart" },
  { href: "/triagem", label: "Triagem", icon: "ticket" },
  { href: "/modelo", label: "Modelo", icon: "model" },
  { href: "/proposta", label: "Proposta", icon: "flow" },
];

export function Navigation() {
  const pathname = usePathname();
  return (
    <header className="app-header">
      <div className="header-inner">
        <Link
          href="/"
          className="brand"
          aria-label="Suporte Inteligente — início"
        >
          <span className="brand-symbol">
            <Icon name="grid" width={21} height={21} />
          </span>
          <span>
            Suporte<span className="brand-secondary">Inteligente</span>
          </span>
        </Link>
        <nav className="main-nav" aria-label="Navegação principal">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`nav-link${pathname === link.href ? " active" : ""}`}
              aria-current={pathname === link.href ? "page" : undefined}
            >
              <Icon name={link.icon} width={17} height={17} />
              <span>{link.label}</span>
            </Link>
          ))}
        </nav>
        <span className="header-label">
          <span className="status-dot" />
          Challenge 002
        </span>
      </div>
    </header>
  );
}
